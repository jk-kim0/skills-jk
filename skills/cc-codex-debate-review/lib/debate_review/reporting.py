from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

_STEP_ORDER = [
    "step0_sync",
    "step1_lead_review",
    "step2_cross_review",
    "step3_lead_apply",
    "step4_settle",
]


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _to_iso(dt: datetime | None) -> str | None:
    return dt.isoformat() if dt is not None else None


def _seconds(start: datetime | None, end: datetime | None) -> float | None:
    if start is None or end is None:
        return None
    return round(max((end - start).total_seconds(), 0.0), 1)


def _iter_state_files(state_dir: Path):
    for path in sorted(state_dir.iterdir()):
        if not path.is_file():
            continue
        if not (path.name.endswith(".json") or path.name.endswith(".archived")):
            continue
        yield path


def _step_order_key(step_name: str) -> tuple[int, str]:
    try:
        return (_STEP_ORDER.index(step_name), step_name)
    except ValueError:
        return (len(_STEP_ORDER), step_name)


def _classify_bash_command(command: str) -> str:
    stripped = command.strip()
    if re.search(r"(^|\s)gh\b", stripped):
        return "github_api_seconds"
    if re.search(r"(^|\s)git\b", stripped):
        return "local_git_seconds"
    if re.search(r"(^|\s)(cat|sed|rg|ls|find|awk|head|tail|wc|sort|stat|nl|fd)\b", stripped):
        return "local_file_seconds"
    return "other_tool_seconds"


def _classify_cc_tool(name: str, input_payload: dict) -> str:
    if name in {"Read", "Grep", "Glob", "LS"}:
        return "local_file_seconds"
    if name == "Bash":
        command = str(input_payload.get("command") or input_payload.get("cmd") or "")
        return _classify_bash_command(command)
    return "other_tool_seconds"


def _parse_cc_subagent_log(path: Path) -> dict:
    tool_uses = {}
    prompt_chunks = []
    first_ts = None
    last_ts = None
    breakdown = defaultdict(float)

    with path.open() as f:
        for raw_line in f:
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            event = json.loads(raw_line)
            timestamp = _parse_iso(event.get("timestamp"))
            if timestamp is not None:
                if first_ts is None or timestamp < first_ts:
                    first_ts = timestamp
                if last_ts is None or timestamp > last_ts:
                    last_ts = timestamp

            message = event.get("message", {})
            for item in message.get("content", []):
                if isinstance(item, str):
                    prompt_chunks.append(item)
                    continue
                if not isinstance(item, dict):
                    continue
                item_type = item.get("type")
                if item_type == "text":
                    prompt_chunks.append(str(item.get("text", "")))
                elif item_type == "tool_use":
                    tool_uses[item.get("id")] = {
                        "timestamp": timestamp,
                        "name": item.get("name"),
                        "input": item.get("input", {}),
                    }
                elif item_type == "tool_result":
                    tool_use_id = item.get("tool_use_id")
                    tool_use = tool_uses.get(tool_use_id)
                    if not tool_use or timestamp is None or tool_use.get("timestamp") is None:
                        continue
                    bucket = _classify_cc_tool(str(tool_use.get("name")), tool_use.get("input", {}))
                    breakdown[bucket] += max((timestamp - tool_use["timestamp"]).total_seconds(), 0.0)

    prompt_text = "\n".join(chunk for chunk in prompt_chunks if chunk)
    match = re.search(r"([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)#(\d+)", prompt_text)
    round_match = re.search(r"round\s+(\d+)", prompt_text, re.IGNORECASE)

    step_name = None
    lower_text = prompt_text.lower()
    if "lead response + code application" in lower_text:
        step_name = "step3_lead_apply"
    elif "cross-verification" in lower_text or "cross-verifier" in lower_text:
        step_name = "step2_cross_review"
    elif "lead review" in lower_text or "lead reviewer" in lower_text:
        step_name = "step1_lead_review"

    active_seconds = _seconds(first_ts, last_ts) or 0.0
    used_seconds = sum(breakdown.values())
    breakdown["reasoning_seconds"] = round(max(active_seconds - used_seconds, 0.0), 1)
    breakdown["active_seconds"] = round(active_seconds, 1)
    for key in ("local_file_seconds", "local_git_seconds", "github_api_seconds", "other_tool_seconds"):
        breakdown[key] = round(breakdown.get(key, 0.0), 1)

    return {
        "path": str(path),
        "repo": match.group(1) if match else None,
        "pr_number": int(match.group(2)) if match else None,
        "round": int(round_match.group(1)) if round_match else None,
        "step_name": step_name,
        "started_at": _to_iso(first_ts),
        "completed_at": _to_iso(last_ts),
        "agent_breakdown": dict(breakdown),
    }


def _scan_cc_subagent_logs(claude_projects_root: Path) -> dict[tuple[str, int, int, str], list[dict]]:
    index: dict[tuple[str, int, int, str], list[dict]] = defaultdict(list)
    for path in claude_projects_root.rglob("subagents/*.jsonl"):
        try:
            parsed = _parse_cc_subagent_log(path)
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            continue
        key = (parsed.get("repo"), parsed.get("pr_number"), parsed.get("round"), parsed.get("step_name"))
        if None in key:
            continue
        index[key].append(parsed)
    return index


def _round_end(round_data: dict, session_end: datetime | None) -> datetime | None:
    return _parse_iso(round_data.get("completed_at")) or session_end


def _fallback_steps(state: dict, round_data: dict, session_end: datetime | None) -> dict:
    timings = round_data.get("step_timings") or {}
    if not timings and state.get("current_round") == round_data.get("round"):
        timings = state.get("journal", {}).get("step_timings", {})
    entries = []
    for step_name, ts in timings.items():
        parsed = _parse_iso(ts)
        if parsed is not None:
            entries.append((step_name, parsed))
    entries.sort(key=lambda item: (item[1], _step_order_key(item[0])))

    steps = {}
    for idx, (step_name, started_at) in enumerate(entries):
        next_started = entries[idx + 1][1] if idx + 1 < len(entries) else _round_end(round_data, session_end)
        steps[step_name] = {
            "started_at": _to_iso(started_at),
            "completed_at": _to_iso(next_started),
            "duration_seconds": _seconds(started_at, next_started),
        }
    return steps


def _match_cc_trace(index: dict, *, repo: str, pr_number: int, round_num: int, step_name: str, subagent_log_path: str | None):
    if subagent_log_path:
        for entries in index.values():
            for entry in entries:
                if entry["path"] == subagent_log_path:
                    return entry
    candidates = index.get((repo, pr_number, round_num, step_name), [])
    return candidates[0] if candidates else None


def _expected_cc_steps(round_data: dict) -> list[str]:
    lead_agent = round_data.get("lead_agent")
    if lead_agent == "cc":
        return ["step1_lead_review", "step3_lead_apply"]
    if lead_agent == "codex":
        return ["step2_cross_review"]
    return []


def _summarize_round_steps(state: dict, session: dict, round_data: dict, cc_index: dict, session_end: datetime | None) -> dict:
    traces = round_data.get("step_traces", {})
    steps = _fallback_steps(state, round_data, session_end)

    for step_name in sorted(traces, key=_step_order_key):
        trace = traces[step_name]
        started_at = _parse_iso(trace.get("started_at")) or _parse_iso(round_data.get("step_timings", {}).get(step_name))
        completed_at = _parse_iso(trace.get("completed_at")) or _round_end(round_data, session_end)
        step_summary = steps.get(step_name, {})
        step_summary.update({
            "agent": trace.get("agent"),
            "started_at": _to_iso(started_at),
            "completed_at": _to_iso(completed_at),
            "duration_seconds": _seconds(started_at, completed_at),
            "command_spans": trace.get("command_spans", []),
        })
        subagent_log_path = (
            trace.get("runtime_artifacts", {}).get("subagent_log_path")
            or trace.get("dispatch", {}).get("subagent_log_path")
        )
        if trace.get("agent") == "cc":
            matched = _match_cc_trace(
                cc_index,
                repo=session["repo"],
                pr_number=session["pr_number"],
                round_num=round_data["round"],
                step_name=step_name,
                subagent_log_path=subagent_log_path,
            )
            if matched:
                step_summary["agent_breakdown"] = matched["agent_breakdown"]
                step_summary["subagent_log_path"] = matched["path"]
        steps[step_name] = step_summary

    for step_name in _expected_cc_steps(round_data):
        if step_name in steps and "agent_breakdown" in steps[step_name]:
            continue
        matched = _match_cc_trace(
            cc_index,
            repo=session["repo"],
            pr_number=session["pr_number"],
            round_num=round_data["round"],
            step_name=step_name,
            subagent_log_path=None,
        )
        if not matched:
            continue
        step_summary = steps.get(step_name, {})
        started_at = _parse_iso(step_summary.get("started_at")) or _parse_iso(matched.get("started_at"))
        completed_at = _parse_iso(step_summary.get("completed_at")) or _parse_iso(matched.get("completed_at"))
        step_summary.update({
            "agent": step_summary.get("agent") or "cc",
            "started_at": _to_iso(started_at),
            "completed_at": _to_iso(completed_at),
            "duration_seconds": step_summary.get("duration_seconds") or _seconds(started_at, completed_at),
            "agent_breakdown": matched["agent_breakdown"],
            "subagent_log_path": matched["path"],
        })
        steps[step_name] = step_summary

    return steps


def generate_sessions_report(
    *,
    state_dir: str | Path,
    claude_projects_root: str | Path | None = None,
    codex_sessions_root: str | Path | None = None,
) -> dict:
    state_root = Path(state_dir).expanduser()
    claude_root = Path(claude_projects_root).expanduser() if claude_projects_root else Path.home() / ".claude" / "projects"
    _ = Path(codex_sessions_root).expanduser() if codex_sessions_root else Path.home() / ".codex" / "sessions"

    cc_index = _scan_cc_subagent_logs(claude_root) if claude_root.exists() else {}
    sessions = []
    now = datetime.now(timezone.utc)

    for state_path in _iter_state_files(state_root):
        try:
            with state_path.open() as f:
                state = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(state, dict) or "repo" not in state or "pr_number" not in state:
            continue

        started_at = _parse_iso(state.get("started_at"))
        finished_at = _parse_iso(state.get("finished_at")) or now
        rounds = []
        for round_data in sorted(state.get("rounds", []), key=lambda item: item.get("round", 0)):
            round_started = _parse_iso(round_data.get("started_at"))
            round_completed = _parse_iso(round_data.get("completed_at")) or finished_at
            rounds.append({
                "round": round_data["round"],
                "lead_agent": round_data.get("lead_agent"),
                "started_at": _to_iso(round_started),
                "completed_at": _to_iso(round_completed),
                "duration_seconds": _seconds(round_started, round_completed),
                "steps": _summarize_round_steps(state, state, round_data, cc_index, finished_at),
            })

        sessions.append({
            "state_file": str(state_path),
            "repo": state["repo"],
            "pr_number": state["pr_number"],
            "status": state.get("status"),
            "final_outcome": state.get("final_outcome"),
            "started_at": _to_iso(started_at),
            "finished_at": _to_iso(_parse_iso(state.get("finished_at"))),
            "duration_seconds": _seconds(started_at, finished_at),
            "rounds": rounds,
        })

    sessions.sort(key=lambda item: item.get("started_at") or "", reverse=True)
    return {
        "generated_at": _to_iso(now),
        "totals": {
            "sessions": len(sessions),
            "completed": sum(1 for session in sessions if session.get("finished_at")),
            "in_progress": sum(1 for session in sessions if not session.get("finished_at")),
        },
        "sessions": sessions,
    }


def render_sessions_report_markdown(report: dict) -> str:
    lines = [
        "# Debate Review Session Report",
        "",
        f"- Generated at: {report['generated_at']}",
        f"- Sessions: {report['totals']['sessions']}",
        f"- Completed: {report['totals']['completed']}",
        f"- In progress: {report['totals']['in_progress']}",
        "",
    ]
    for session in report.get("sessions", []):
        lines.extend(
            [
                f"## {session['repo']}#{session['pr_number']}",
                "",
                f"- Status: {session.get('status')}",
                f"- Outcome: {session.get('final_outcome')}",
                f"- Duration: {session.get('duration_seconds')}s",
                "",
            ]
        )
        for round_data in session.get("rounds", []):
            lines.extend(
                [
                    f"### Round {round_data['round']}",
                    "",
                    f"- Lead agent: {round_data.get('lead_agent')}",
                    f"- Duration: {round_data.get('duration_seconds')}s",
                    "",
                    "| Step | Duration (s) | Agent | Local File | Local Git | GitHub/API | Reasoning |",
                    "| --- | ---: | --- | ---: | ---: | ---: | ---: |",
                ]
            )
            for step_name, step in round_data.get("steps", {}).items():
                breakdown = step.get("agent_breakdown", {})
                lines.append(
                    "| "
                    f"{step_name} | {step.get('duration_seconds')} | {step.get('agent', '')} | "
                    f"{breakdown.get('local_file_seconds', '')} | "
                    f"{breakdown.get('local_git_seconds', '')} | "
                    f"{breakdown.get('github_api_seconds', '')} | "
                    f"{breakdown.get('reasoning_seconds', '')} |"
                )
            lines.append("")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"

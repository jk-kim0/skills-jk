from __future__ import annotations

import json
import math
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median

from debate_review.issue_ops import latest_report_message

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
    if not state_dir.exists() or not state_dir.is_dir():
        return
    for path in sorted(state_dir.iterdir()):
        if not path.is_file():
            continue
        if not path.name.endswith(".json"):
            continue
        yield path


def _step_order_key(step_name: str) -> tuple[int, str]:
    try:
        return (_STEP_ORDER.index(step_name), step_name)
    except ValueError:
        return (len(_STEP_ORDER), step_name)


def _percentile(values: list[float], percent: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return round(ordered[0], 1)

    position = (len(ordered) - 1) * percent
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return round(ordered[lower], 1)

    lower_value = ordered[lower]
    upper_value = ordered[upper]
    interpolated = lower_value + (upper_value - lower_value) * (position - lower)
    return round(interpolated, 1)


def _stats(values: list[float]) -> dict:
    if not values:
        return {
            "count": 0,
            "min": None,
            "p25": None,
            "median": None,
            "p75": None,
            "max": None,
            "average": None,
        }
    return {
        "count": len(values),
        "min": round(min(values), 1),
        "p25": _percentile(values, 0.25),
        "median": round(median(values), 1),
        "p75": _percentile(values, 0.75),
        "max": round(max(values), 1),
        "average": round(mean(values), 1),
    }


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


def _classify_codex_tool(name: str, arguments_payload) -> str:
    if name == "exec_command":
        if isinstance(arguments_payload, str):
            try:
                arguments_payload = json.loads(arguments_payload)
            except json.JSONDecodeError:
                arguments_payload = {}
        if not isinstance(arguments_payload, dict):
            arguments_payload = {}
        return _classify_bash_command(str(arguments_payload.get("cmd") or ""))
    return "other_tool_seconds"


def _parse_repo_pr(text: str) -> tuple[str | None, int | None]:
    match = re.search(r"([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)\s*#(\d+)", text)
    if not match:
        return None, None
    return match.group(1), int(match.group(2))


def _parse_round_step(text: str) -> tuple[int | None, str | None]:
    round_match = re.search(r"Round\s+(\d+)", text, re.IGNORECASE)
    round_num = int(round_match.group(1)) if round_match else None
    lower_text = text.lower()
    if "lead response + code application" in lower_text:
        return round_num, "step3_lead_apply"
    if "cross-verification" in lower_text or "cross-verifier" in lower_text:
        return round_num, "step2_cross_review"
    if "lead review" in lower_text or "lead reviewer" in lower_text:
        return round_num, "step1_lead_review"
    return round_num, None


def _finalize_breakdown(breakdown: defaultdict[str, float], *, active_seconds: float) -> dict:
    used_seconds = sum(breakdown.values())
    breakdown["unattributed_seconds"] = max(active_seconds - used_seconds, 0.0)
    breakdown["active_seconds"] = active_seconds
    for key in (
        "local_file_seconds",
        "local_git_seconds",
        "github_api_seconds",
        "other_tool_seconds",
        "unattributed_seconds",
        "active_seconds",
    ):
        breakdown[key] = round(breakdown.get(key, 0.0), 1)
    return dict(breakdown)


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
    repo, pr_number = _parse_repo_pr(prompt_text)
    round_num, step_name = _parse_round_step(prompt_text)
    active_seconds = _seconds(first_ts, last_ts) or 0.0

    return {
        "path": str(path),
        "repo": repo,
        "pr_number": pr_number,
        "round": round_num,
        "step_name": step_name,
        "agent": "cc",
        "started_at": _to_iso(first_ts),
        "completed_at": _to_iso(last_ts),
        "agent_breakdown": _finalize_breakdown(breakdown, active_seconds=active_seconds),
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


def _parse_codex_rollout(path: Path) -> tuple[str | None, list[dict]]:
    session_id = None
    session_repo = None
    session_pr = None
    current_turn = None
    turns: dict[str, dict] = {}

    def ensure_turn(turn_id: str) -> dict:
        turn = turns.setdefault(
            turn_id,
            {
                "turn_id": turn_id,
                "started_at": None,
                "completed_at": None,
                "repo": None,
                "pr_number": None,
                "round": None,
                "step_name": None,
                "user_texts": [],
                "calls": {},
                "breakdown": defaultdict(float),
                "last_ts": None,
            },
        )
        return turn

    with path.open() as f:
        for raw_line in f:
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            event = json.loads(raw_line)
            ts = _parse_iso(event.get("timestamp"))
            event_type = event.get("type")
            payload = event.get("payload", {})

            if event_type == "session_meta":
                session_id = payload.get("id")
                continue

            if event_type == "event_msg" and payload.get("type") == "task_started":
                current_turn = payload.get("turn_id")
                ensure_turn(current_turn)["started_at"] = ts
                continue

            if event_type == "turn_context":
                current_turn = payload.get("turn_id")
                ensure_turn(current_turn)
                continue

            if event_type == "event_msg" and payload.get("type") == "task_complete":
                turn_id = payload.get("turn_id")
                turn = ensure_turn(turn_id)
                turn["completed_at"] = ts
                turn["last_ts"] = ts or turn["last_ts"]
                current_turn = None
                continue

            if event_type != "response_item":
                continue

            payload_type = payload.get("type")
            if payload_type == "message" and payload.get("role") == "user":
                texts = []
                for item in payload.get("content", []):
                    if not isinstance(item, dict):
                        continue
                    if item.get("type") == "input_text":
                        texts.append(str(item.get("text", "")))
                joined = "\n".join(texts)
                repo, pr_number = _parse_repo_pr(joined)
                if repo and pr_number:
                    session_repo = repo
                    session_pr = pr_number
                if current_turn:
                    turn = ensure_turn(current_turn)
                    turn["user_texts"].extend(texts)
                    turn["repo"] = turn["repo"] or session_repo
                    turn["pr_number"] = turn["pr_number"] or session_pr
                    round_num, step_name = _parse_round_step(joined)
                    if round_num is not None:
                        turn["round"] = round_num
                    if step_name is not None:
                        turn["step_name"] = step_name
                    turn["last_ts"] = ts or turn["last_ts"]
                continue

            if not current_turn:
                continue

            turn = ensure_turn(current_turn)
            turn["repo"] = turn["repo"] or session_repo
            turn["pr_number"] = turn["pr_number"] or session_pr
            turn["last_ts"] = ts or turn["last_ts"]

            if payload_type == "function_call":
                call_id = payload.get("call_id")
                if call_id:
                    turn["calls"][call_id] = {
                        "timestamp": ts,
                        "name": payload.get("name"),
                        "arguments": payload.get("arguments"),
                    }
                continue

            if payload_type == "function_call_output":
                call_id = payload.get("call_id")
                call = turn["calls"].get(call_id)
                if not call or ts is None or call.get("timestamp") is None:
                    continue
                bucket = _classify_codex_tool(str(call.get("name")), call.get("arguments"))
                turn["breakdown"][bucket] += max((ts - call["timestamp"]).total_seconds(), 0.0)

    parsed_turns = []
    for turn in turns.values():
        if not turn.get("repo") or not turn.get("pr_number") or not turn.get("round") or not turn.get("step_name"):
            continue
        start = turn.get("started_at")
        end = turn.get("completed_at") or turn.get("last_ts")
        active_seconds = _seconds(start, end) or 0.0
        parsed_turns.append(
            {
                "path": str(path),
                "session_id": session_id,
                "repo": turn["repo"],
                "pr_number": turn["pr_number"],
                "round": turn["round"],
                "step_name": turn["step_name"],
                "agent": "codex",
                "started_at": _to_iso(start),
                "completed_at": _to_iso(end),
                "agent_breakdown": _finalize_breakdown(turn["breakdown"], active_seconds=active_seconds),
            }
        )
    return session_id, parsed_turns


def _scan_codex_rollouts(codex_sessions_root: Path) -> dict:
    by_key: dict[tuple[str, int, int, str], list[dict]] = defaultdict(list)
    by_session: dict[str, list[dict]] = defaultdict(list)
    for path in codex_sessions_root.rglob("*.jsonl"):
        try:
            session_id, turns = _parse_codex_rollout(path)
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            continue
        for turn in turns:
            key = (turn["repo"], turn["pr_number"], turn["round"], turn["step_name"])
            by_key[key].append(turn)
            if session_id:
                by_session[session_id].append(turn)
    return {"by_key": by_key, "by_session": by_session}


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
        wall_clock_seconds = _seconds(started_at, next_started)
        steps[step_name] = {
            "started_at": _to_iso(started_at),
            "completed_at": _to_iso(next_started),
            "wall_clock_seconds": wall_clock_seconds,
            # Deprecated alias retained for downstream consumers that still read duration_seconds.
            "duration_seconds": wall_clock_seconds,
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


def _match_codex_trace(index: dict, *, session_id: str | None, repo: str, pr_number: int, round_num: int, step_name: str):
    if session_id:
        for entry in index.get("by_session", {}).get(session_id, []):
            if entry["round"] == round_num and entry["step_name"] == step_name:
                return entry
    candidates = index.get("by_key", {}).get((repo, pr_number, round_num, step_name), [])
    return candidates[0] if candidates else None


def _expected_step_agents(round_data: dict) -> dict[str, str]:
    lead_agent = round_data.get("lead_agent")
    cross_verifier = "cc" if lead_agent == "codex" else "codex"
    return {
        "step1_lead_review": lead_agent,
        "step2_cross_review": cross_verifier,
        "step3_lead_apply": lead_agent,
    }


def _apply_matched_step(step_summary: dict, matched: dict, default_agent: str) -> dict:
    started_at = _parse_iso(step_summary.get("started_at")) or _parse_iso(matched.get("started_at"))
    completed_at = _parse_iso(step_summary.get("completed_at")) or _parse_iso(matched.get("completed_at"))
    wall_clock_seconds = (
        step_summary.get("wall_clock_seconds")
        or step_summary.get("duration_seconds")
        or _seconds(started_at, completed_at)
    )
    step_summary.update(
        {
            "agent": step_summary.get("agent") or matched.get("agent") or default_agent,
            "started_at": _to_iso(started_at),
            "completed_at": _to_iso(completed_at),
            "wall_clock_seconds": wall_clock_seconds,
            "agent_active_seconds": matched["agent_breakdown"].get("active_seconds"),
            # Deprecated alias retained for downstream consumers that still read duration_seconds.
            "duration_seconds": wall_clock_seconds,
            "agent_breakdown": matched["agent_breakdown"],
        }
    )
    if matched.get("path"):
        step_summary["artifact_path"] = matched["path"]
    return step_summary


def _summarize_round_steps(
    state: dict,
    session: dict,
    round_data: dict,
    cc_index: dict,
    codex_index: dict,
    session_end: datetime | None,
) -> dict:
    traces = round_data.get("step_traces", {})
    steps = _fallback_steps(state, round_data, session_end)

    for step_name in sorted(traces, key=_step_order_key):
        trace = traces[step_name]
        started_at = _parse_iso(trace.get("started_at")) or _parse_iso(round_data.get("step_timings", {}).get(step_name))
        completed_at = _parse_iso(trace.get("completed_at")) or _round_end(round_data, session_end)
        wall_clock_seconds = _seconds(started_at, completed_at)
        step_summary = steps.get(step_name, {})
        step_summary.update(
            {
                "agent": trace.get("agent"),
                "started_at": _to_iso(started_at),
                "completed_at": _to_iso(completed_at),
                "wall_clock_seconds": wall_clock_seconds,
                # Deprecated alias retained for downstream consumers that still read duration_seconds.
                "duration_seconds": wall_clock_seconds,
                "command_spans": trace.get("command_spans", []),
            }
        )
        if trace.get("agent") == "cc":
            subagent_log_path = (
                trace.get("runtime_artifacts", {}).get("subagent_log_path")
                or trace.get("dispatch", {}).get("subagent_log_path")
            )
            matched = _match_cc_trace(
                cc_index,
                repo=session["repo"],
                pr_number=session["pr_number"],
                round_num=round_data["round"],
                step_name=step_name,
                subagent_log_path=subagent_log_path,
            )
            if matched:
                _apply_matched_step(step_summary, matched, "cc")
        elif trace.get("agent") == "codex":
            trace_session_id = trace.get("persistent_session", {}).get("handle")
            matched = _match_codex_trace(
                codex_index,
                session_id=trace_session_id or state.get("persistent_agents", {}).get("codex_session_id"),
                repo=session["repo"],
                pr_number=session["pr_number"],
                round_num=round_data["round"],
                step_name=step_name,
            )
            if matched:
                _apply_matched_step(step_summary, matched, "codex")
        steps[step_name] = step_summary

    for step_name, agent_name in _expected_step_agents(round_data).items():
        step_summary = steps.get(step_name, {})
        if "agent_breakdown" in step_summary:
            continue
        matched = None
        if agent_name == "cc":
            matched = _match_cc_trace(
                cc_index,
                repo=session["repo"],
                pr_number=session["pr_number"],
                round_num=round_data["round"],
                step_name=step_name,
                subagent_log_path=None,
            )
        else:
            matched = _match_codex_trace(
                codex_index,
                session_id=state.get("persistent_agents", {}).get("codex_session_id"),
                repo=session["repo"],
                pr_number=session["pr_number"],
                round_num=round_data["round"],
                step_name=step_name,
            )
        if matched:
            _apply_matched_step(step_summary, matched, agent_name)
        elif step_summary:
            step_summary["agent"] = step_summary.get("agent") or agent_name
        if step_summary:
            steps[step_name] = step_summary

    return dict(sorted(steps.items(), key=lambda item: _step_order_key(item[0])))


def _step_agent_label(step_name: str, agent: str) -> str:
    return f"{step_name} / {agent}"


def _sum_active_seconds(items: list[dict]) -> float | None:
    active_values = [item.get("agent_active_seconds") for item in items if item.get("agent_active_seconds") is not None]
    if not active_values:
        return None
    return round(sum(active_values), 1)


def _classify_cc_invocation(state: dict) -> str:
    """Classify CC invocation type from persistent_agents handle format.

    - 'agent-tool': legacy mode sessions (old API-based Agent tool subagent)
    - 'subprocess': UUID-format handle (claude -p --resume), after PR #178
    - 'agent-tool': persistent session with old API-based Agent tool handle
    - 'unknown': no persistent agent or unrecognizable format
    """
    if state.get("agent_mode", "legacy") == "legacy":
        return "agent-tool"

    pa = state.get("persistent_agents", {})
    handle = pa.get("cc_agent_id") or pa.get("cc_session_id") or ""
    handle = str(handle)
    if not handle or handle == "None":
        return "unknown"
    # UUID format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx (subprocess)
    import re
    if re.match(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]", handle):
        return "subprocess"
    return "agent-tool"


def _mark_stats_eligibility(
    *,
    dry_run: bool,
    in_progress: bool,
    missing_completed_at: bool = False,
) -> tuple[bool, list[str]]:
    reasons = []
    if dry_run:
        reasons.append("dry_run")
    if in_progress:
        reasons.append("in_progress")
    if missing_completed_at:
        reasons.append("missing_completed_at")
    return not reasons, reasons


def _build_stats(sessions: list[dict]) -> dict:
    session_wall_clock = []
    session_active = []
    round_wall_clock = []
    round_active = []
    step_wall_clock: dict[str, list[float]] = defaultdict(list)
    step_wall_clock_by_agent: dict[str, list[float]] = defaultdict(list)
    step_active: dict[str, list[float]] = defaultdict(list)
    step_active_by_agent: dict[str, list[float]] = defaultdict(list)
    lead_agent_round_wall_clock: dict[str, list[float]] = defaultdict(list)

    for session in sessions:
        if session.get("include_in_wall_clock_stats") and session.get("wall_clock_seconds") is not None:
            session_wall_clock.append(session["wall_clock_seconds"])
        if session.get("include_in_active_stats") and session.get("agent_active_seconds") is not None:
            session_active.append(session["agent_active_seconds"])

        for round_data in session.get("rounds", []):
            if round_data.get("include_in_wall_clock_stats") and round_data.get("wall_clock_seconds") is not None:
                round_wall_clock.append(round_data["wall_clock_seconds"])
                lead_agent = round_data.get("lead_agent")
                if lead_agent:
                    lead_agent_round_wall_clock[lead_agent].append(round_data["wall_clock_seconds"])
            if round_data.get("include_in_active_stats") and round_data.get("agent_active_seconds") is not None:
                round_active.append(round_data["agent_active_seconds"])

            for step_name, step in round_data.get("steps", {}).items():
                if step.get("include_in_wall_clock_stats") and step.get("wall_clock_seconds") is not None:
                    step_wall_clock[step_name].append(step["wall_clock_seconds"])
                    if step.get("agent"):
                        step_wall_clock_by_agent[_step_agent_label(step_name, step["agent"])].append(step["wall_clock_seconds"])
                if step.get("include_in_active_stats") and step.get("agent_active_seconds") is not None:
                    step_active[step_name].append(step["agent_active_seconds"])
                    if step.get("agent"):
                        step_active_by_agent[_step_agent_label(step_name, step["agent"])].append(step["agent_active_seconds"])

    return {
        "session_wall_clock_seconds": _stats(session_wall_clock),
        "session_active_seconds": _stats(session_active),
        "round_wall_clock_seconds": _stats(round_wall_clock),
        "round_active_seconds": _stats(round_active),
        "step_wall_clock_seconds": {step: _stats(values) for step, values in sorted(step_wall_clock.items(), key=lambda item: _step_order_key(item[0]))},
        "step_wall_clock_seconds_by_agent": {step: _stats(values) for step, values in sorted(step_wall_clock_by_agent.items())},
        "step_active_seconds": {step: _stats(values) for step, values in sorted(step_active.items(), key=lambda item: _step_order_key(item[0]))},
        "step_active_seconds_by_agent": {step: _stats(values) for step, values in sorted(step_active_by_agent.items())},
        "lead_agent_round_wall_clock_seconds": {agent: _stats(values) for agent, values in sorted(lead_agent_round_wall_clock.items())},
    }


def _build_populations(sessions: list[dict]) -> dict:
    populations = {
        "sessions": {
            "total": 0,
            "included_in_wall_clock_stats": 0,
            "excluded_dry_run": 0,
            "excluded_in_progress": 0,
        },
        "rounds": {
            "total": 0,
            "included_in_wall_clock_stats": 0,
            "excluded_dry_run": 0,
            "excluded_in_progress": 0,
            "excluded_missing_completed_at": 0,
        },
        "steps": {
            "total": 0,
            "included_in_wall_clock_stats": 0,
            "included_in_active_stats": 0,
            "excluded_dry_run": 0,
            "excluded_in_progress": 0,
            "excluded_missing_completed_at": 0,
        },
    }

    for session in sessions:
        populations["sessions"]["total"] += 1
        if session.get("include_in_wall_clock_stats"):
            populations["sessions"]["included_in_wall_clock_stats"] += 1
        for reason in session.get("exclusion_reasons", []):
            key = f"excluded_{reason}"
            if key in populations["sessions"]:
                populations["sessions"][key] += 1

        for round_data in session.get("rounds", []):
            populations["rounds"]["total"] += 1
            if round_data.get("include_in_wall_clock_stats"):
                populations["rounds"]["included_in_wall_clock_stats"] += 1
            for reason in round_data.get("exclusion_reasons", []):
                key = f"excluded_{reason}"
                if key in populations["rounds"]:
                    populations["rounds"][key] += 1

            for step in round_data.get("steps", {}).values():
                populations["steps"]["total"] += 1
                if step.get("include_in_wall_clock_stats"):
                    populations["steps"]["included_in_wall_clock_stats"] += 1
                if step.get("include_in_active_stats"):
                    populations["steps"]["included_in_active_stats"] += 1
                for reason in step.get("exclusion_reasons", []):
                    key = f"excluded_{reason}"
                    if key in populations["steps"]:
                        populations["steps"][key] += 1

    return populations


def _build_coverage(sessions: list[dict]) -> dict:
    rounds_total = 0
    rounds_with_any_steps = 0
    rounds_with_any_breakdown = 0
    steps_total = 0
    steps_with_breakdown = 0

    for session in sessions:
        for round_data in session.get("rounds", []):
            if not round_data.get("include_in_wall_clock_stats"):
                continue
            rounds_total += 1
            eligible_steps = [step for step in round_data.get("steps", {}).values() if step.get("include_in_wall_clock_stats")]
            if eligible_steps:
                rounds_with_any_steps += 1
            has_breakdown = False
            for step in eligible_steps:
                steps_total += 1
                if step.get("agent_breakdown"):
                    steps_with_breakdown += 1
                    has_breakdown = True
            if has_breakdown:
                rounds_with_any_breakdown += 1

    return {
        "rounds_total": rounds_total,
        "rounds_with_any_steps": rounds_with_any_steps,
        "rounds_with_any_breakdown": rounds_with_any_breakdown,
        "steps_total": steps_total,
        "steps_with_breakdown": steps_with_breakdown,
        "step_coverage_ratio": round(rounds_with_any_steps / rounds_total, 3) if rounds_total else 0.0,
        "breakdown_coverage_ratio": round(rounds_with_any_breakdown / rounds_total, 3) if rounds_total else 0.0,
    }


def _build_findings(sessions: list[dict], stats: dict, coverage: dict, populations: dict) -> list[dict]:
    findings = [
        {
            "title": "Excluded Population",
            "detail": (
                f"session 통계에서는 dry-run {populations['sessions']['excluded_dry_run']}개, "
                f"in-progress {populations['sessions']['excluded_in_progress']}개를 제외했습니다. "
                f"round 통계에서는 completed_at 누락 {populations['rounds']['excluded_missing_completed_at']}개를 제외했습니다."
            ),
        },
        {
            "title": "Step-Level Coverage",
            "detail": (
                f"통계 대상 completed round {coverage['rounds_total']}개 중 step 정보가 있는 round는 "
                f"{coverage['rounds_with_any_steps']}개, agent breakdown이 있는 round는 "
                f"{coverage['rounds_with_any_breakdown']}개입니다."
            ),
        },
    ]

    step_stats = stats.get("step_wall_clock_seconds", {})
    if step_stats:
        slowest_step, slowest_stat = max(step_stats.items(), key=lambda item: item[1]["median"] or -1)
        findings.append(
            {
                "title": "Slowest Median Step",
                "detail": f"{slowest_step}의 median은 {slowest_stat['median']}초로, 집계된 step 중 가장 깁니다.",
            }
        )

    split_stats = stats.get("step_wall_clock_seconds_by_agent", {})
    cc_cross = split_stats.get("step2_cross_review / cc", {})
    codex_cross = split_stats.get("step2_cross_review / codex", {})
    if cc_cross.get("median") is not None and codex_cross.get("median") is not None:
        findings.append(
            {
                "title": "Cross-Reviewer Split",
                "detail": (
                    f"step2_cross_review median은 CC {cc_cross['median']}초, Codex {codex_cross['median']}초로 "
                    f"cross-review 분포가 agent별로 크게 갈립니다."
                ),
            }
        )

    lead_stats = stats.get("lead_agent_round_wall_clock_seconds", {})
    if lead_stats.get("cc", {}).get("median") is not None and lead_stats.get("codex", {}).get("median") is not None:
        cc_median = lead_stats["cc"]["median"]
        codex_median = lead_stats["codex"]["median"]
        slower = "CC" if cc_median > codex_median else "Codex"
        findings.append(
            {
                "title": "Lead Agent Comparison",
                "detail": f"Lead round median은 CC {cc_median}초, Codex {codex_median}초이며 {slower} 쪽이 더 느립니다.",
            }
        )

    longest_session = None
    for session in sessions:
        if not session.get("include_in_wall_clock_stats"):
            continue
        duration = session.get("wall_clock_seconds")
        if duration is None:
            continue
        if longest_session is None or duration > longest_session["wall_clock_seconds"]:
            longest_session = session
    if longest_session:
        findings.append(
            {
                "title": "Longest Session",
                "detail": (
                    f"{longest_session['repo']}#{longest_session['pr_number']} 세션이 "
                    f"{longest_session['wall_clock_seconds']}초로 가장 길었습니다."
                ),
            }
        )

    return findings


def generate_sessions_report(
    *,
    state_dir: str | Path,
    claude_projects_root: str | Path | None = None,
    codex_sessions_root: str | Path | None = None,
) -> dict:
    state_root = Path(state_dir).expanduser()
    claude_root = Path(claude_projects_root).expanduser() if claude_projects_root else Path.home() / ".claude" / "projects"
    codex_root = Path(codex_sessions_root).expanduser() if codex_sessions_root else Path.home() / ".codex" / "sessions"

    cc_index = _scan_cc_subagent_logs(claude_root) if claude_root.exists() else {}
    codex_index = _scan_codex_rollouts(codex_root) if codex_root.exists() else {"by_key": {}, "by_session": {}}
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

        dry_run = bool(state.get("dry_run"))
        started_at = _parse_iso(state.get("started_at"))
        explicit_finished_at = _parse_iso(state.get("finished_at"))
        finished_at = explicit_finished_at or now
        session_finished = explicit_finished_at is not None
        session_include, session_reasons = _mark_stats_eligibility(dry_run=dry_run, in_progress=not session_finished)

        agent_mode = state.get("agent_mode", "legacy")
        cc_invocation_type = _classify_cc_invocation(state)

        session_wall_clock = _seconds(started_at, finished_at)
        session_summary = {
            "state_file": str(state_path),
            "repo": state["repo"],
            "pr_number": state["pr_number"],
            "status": state.get("status"),
            "final_outcome": state.get("final_outcome"),
            "dry_run": dry_run,
            "agent_mode": agent_mode,
            "cc_invocation_type": cc_invocation_type,
            "started_at": _to_iso(started_at),
            "finished_at": _to_iso(explicit_finished_at),
            "wall_clock_seconds": session_wall_clock,
            # Deprecated alias retained for downstream consumers that still read duration_seconds.
            "duration_seconds": session_wall_clock,
            "agent_active_seconds": None,
            "include_in_wall_clock_stats": session_include,
            "include_in_active_stats": False,
            "exclusion_reasons": session_reasons,
            "rounds": [],
        }

        for round_data in sorted(state.get("rounds", []), key=lambda item: item.get("round", 0)):
            round_started = _parse_iso(round_data.get("started_at"))
            explicit_round_completed = _parse_iso(round_data.get("completed_at"))
            round_include, round_reasons = _mark_stats_eligibility(
                dry_run=dry_run,
                in_progress=not session_finished,
                missing_completed_at=explicit_round_completed is None,
            )

            steps = _summarize_round_steps(
                state,
                session_summary,
                round_data,
                cc_index,
                codex_index,
                finished_at,
            )
            for step in steps.values():
                explicit_step_completed = step.get("completed_at") is not None
                step_include, step_reasons = _mark_stats_eligibility(
                    dry_run=dry_run,
                    in_progress=not session_finished,
                    missing_completed_at=not explicit_step_completed,
                )
                step["include_in_wall_clock_stats"] = step_include
                step["include_in_active_stats"] = step_include and step.get("agent_active_seconds") is not None
                step["exclusion_reasons"] = step_reasons

            round_wall_clock = _seconds(round_started, explicit_round_completed) if explicit_round_completed else None
            round_active = _sum_active_seconds(list(steps.values()))
            round_summary = {
                "round": round_data["round"],
                "lead_agent": round_data.get("lead_agent"),
                "clean_pass": round_data.get("clean_pass"),
                "started_at": _to_iso(round_started),
                "completed_at": _to_iso(explicit_round_completed),
                "wall_clock_seconds": round_wall_clock,
                # Deprecated alias retained for downstream consumers that still read duration_seconds.
                "duration_seconds": round_wall_clock,
                "agent_active_seconds": round_active,
                "include_in_wall_clock_stats": round_include,
                "include_in_active_stats": round_include and round_active is not None,
                "exclusion_reasons": round_reasons,
                "steps": steps,
            }
            session_summary["rounds"].append(round_summary)

        session_summary["agent_active_seconds"] = _sum_active_seconds(session_summary["rounds"])
        session_summary["include_in_active_stats"] = (
            session_summary["include_in_wall_clock_stats"] and session_summary["agent_active_seconds"] is not None
        )
        sessions.append(session_summary)

    sessions.sort(key=lambda item: item.get("started_at") or "", reverse=True)
    populations = _build_populations(sessions)
    coverage = _build_coverage(sessions)
    stats = _build_stats(sessions)
    findings = _build_findings(sessions, stats, coverage, populations)

    # Build per-invocation-type stats
    stats_by_invocation: dict[str, dict] = {}
    for inv_type in ("subprocess", "agent-tool"):
        filtered = [s for s in sessions if s.get("cc_invocation_type") == inv_type]
        if filtered:
            stats_by_invocation[inv_type] = {
                "session_count": len(filtered),
                "completed": sum(1 for s in filtered if s.get("finished_at")),
                "stats": _build_stats(filtered),
                "populations": _build_populations(filtered),
            }

    return {
        "generated_at": _to_iso(now),
        "totals": {
            "sessions": len(sessions),
            "completed": sum(1 for session in sessions if session.get("finished_at")),
            "in_progress": sum(1 for session in sessions if not session.get("finished_at")),
        },
        "populations": populations,
        "coverage": coverage,
        "stats": stats,
        "stats_by_invocation": stats_by_invocation,
        "findings": findings,
        "sessions": sessions,
    }


def _render_stats_rows(title: str, stats_dict: dict) -> list[str]:
    lines = [
        f"### {title}",
        "",
        "| Metric | Count | Min | 25% | Median | 75% | Max | Average |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for label, value in stats_dict.items():
        lines.append(
            f"| {label} | {value['count']} | {value['min']} | {value['p25']} | {value['median']} | "
            f"{value['p75']} | {value['max']} | {value['average']} |"
        )
    lines.append("")
    return lines


def render_sessions_report_markdown(report: dict) -> str:
    lines = [
        "# Debate Review Session Report",
        "",
        f"- Generated at: {report['generated_at']}",
        f"- Sessions: {report['totals']['sessions']}",
        f"- Completed: {report['totals']['completed']}",
        f"- In progress: {report['totals']['in_progress']}",
        "",
        "## Findings",
        "",
    ]
    for finding in report.get("findings", []):
        lines.append(f"- **{finding['title']}**: {finding['detail']}")

    lines.extend(
        [
            "",
            "## Population",
            "",
            "| Population | Total | Included | Excluded Dry Run | Excluded In Progress | Excluded Missing Completed At |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
            (
                f"| Sessions | {report['populations']['sessions']['total']} | "
                f"{report['populations']['sessions']['included_in_wall_clock_stats']} | "
                f"{report['populations']['sessions']['excluded_dry_run']} | "
                f"{report['populations']['sessions']['excluded_in_progress']} | - |"
            ),
            (
                f"| Rounds | {report['populations']['rounds']['total']} | "
                f"{report['populations']['rounds']['included_in_wall_clock_stats']} | "
                f"{report['populations']['rounds']['excluded_dry_run']} | "
                f"{report['populations']['rounds']['excluded_in_progress']} | "
                f"{report['populations']['rounds']['excluded_missing_completed_at']} |"
            ),
            (
                f"| Steps | {report['populations']['steps']['total']} | "
                f"{report['populations']['steps']['included_in_wall_clock_stats']} | "
                f"{report['populations']['steps']['excluded_dry_run']} | "
                f"{report['populations']['steps']['excluded_in_progress']} | "
                f"{report['populations']['steps']['excluded_missing_completed_at']} |"
            ),
            "",
            "_Sessions do not use the Excluded Missing Completed At column; session inclusion is based on `finished_at`._",
            "",
            "## Statistics",
            "",
            f"- Coverage (rounds with steps): {report['coverage']['rounds_with_any_steps']} / {report['coverage']['rounds_total']}",
            f"- Coverage (rounds with breakdown): {report['coverage']['rounds_with_any_breakdown']} / {report['coverage']['rounds_total']}",
            "",
        ]
    )
    lines.extend(
        _render_stats_rows(
            "Completed Session And Round Wall-Clock Durations",
            {
                "Sessions": report["stats"]["session_wall_clock_seconds"],
                "Rounds": report["stats"]["round_wall_clock_seconds"],
            },
        )
    )
    if report["stats"].get("step_wall_clock_seconds"):
        lines.extend(_render_stats_rows("Completed Step Wall-Clock Durations", report["stats"]["step_wall_clock_seconds"]))
    if report["stats"].get("step_wall_clock_seconds_by_agent"):
        lines.extend(_render_stats_rows("Completed Step Wall-Clock Durations By Agent", report["stats"]["step_wall_clock_seconds_by_agent"]))
    if report["stats"].get("step_active_seconds"):
        lines.extend(_render_stats_rows("Completed Step Active Durations", report["stats"]["step_active_seconds"]))
    if report["stats"].get("step_active_seconds_by_agent"):
        lines.extend(_render_stats_rows("Completed Step Active Durations By Agent", report["stats"]["step_active_seconds_by_agent"]))
    if report["stats"].get("lead_agent_round_wall_clock_seconds"):
        lines.extend(
            _render_stats_rows(
                "Completed Lead Agent Round Wall-Clock Durations",
                {agent.capitalize(): stats for agent, stats in report["stats"]["lead_agent_round_wall_clock_seconds"].items()},
            )
        )

    # Per-invocation-type stats
    stats_by_inv = report.get("stats_by_invocation", {})
    if stats_by_inv:
        lines.extend(["## Statistics By CC Invocation Type", ""])
        for inv_type, inv_data in stats_by_inv.items():
            inv_stats = inv_data["stats"]
            inv_pops = inv_data["populations"]
            label = "Subprocess (`claude -p`)" if inv_type == "subprocess" else "Agent Tool (old API)"
            lines.extend([
                f"### {label}",
                "",
                f"- Sessions: {inv_data['session_count']} (completed: {inv_data['completed']})",
                f"- Rounds included: {inv_pops['rounds']['included_in_wall_clock_stats']}",
                "",
            ])
            lines.extend(
                _render_stats_rows(
                    f"{label} — Session And Round Durations",
                    {
                        "Sessions": inv_stats["session_wall_clock_seconds"],
                        "Rounds": inv_stats["round_wall_clock_seconds"],
                    },
                )
            )
            if inv_stats.get("step_wall_clock_seconds_by_agent"):
                lines.extend(_render_stats_rows(f"{label} — Step Durations By Agent", inv_stats["step_wall_clock_seconds_by_agent"]))
            if inv_stats.get("lead_agent_round_wall_clock_seconds"):
                lines.extend(
                    _render_stats_rows(
                        f"{label} — Lead Agent Round Durations",
                        {agent.capitalize(): s for agent, s in inv_stats["lead_agent_round_wall_clock_seconds"].items()},
                    )
                )

    lines.extend(["## Appendix", ""])
    for session in report.get("sessions", []):
        session_stats_line = "yes"
        if session.get("exclusion_reasons"):
            session_stats_line = f"no (excluded from stats: {', '.join(session['exclusion_reasons'])})"
        lines.extend(
            [
                f"### {session['repo']}#{session['pr_number']}",
                "",
                f"- Status: {session.get('status')}",
                f"- Outcome: {session.get('final_outcome')}",
                f"- Dry run: {session.get('dry_run')}",
                f"- Agent mode: {session.get('agent_mode', 'legacy')}",
                f"- CC invocation: {session.get('cc_invocation_type', 'unknown')}",
                f"- Stats eligibility: {session_stats_line}",
                f"- Wall clock: {session.get('wall_clock_seconds')}s",
                f"- Active: {session.get('agent_active_seconds')}s",
                "",
            ]
        )
        lines.extend(_render_round_step_table(session.get("rounds", [])))
        for round_data in session.get("rounds", []):
            round_stats_line = "yes"
            if round_data.get("exclusion_reasons"):
                round_stats_line = f"no (excluded from stats: {', '.join(round_data['exclusion_reasons'])})"
            lines.extend(
                [
                    f"#### Round {round_data['round']}",
                    "",
                    f"- Lead agent: {round_data.get('lead_agent')}",
                    f"- Stats eligibility: {round_stats_line}",
                    f"- Wall clock: {round_data.get('wall_clock_seconds')}s",
                    f"- Active: {round_data.get('agent_active_seconds')}s",
                    "",
                    "| Step | Wall Clock (s) | Active (s) | Agent | Local File | Local Git | GitHub/API | Unattributed |",
                    "| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |",
                ]
            )
            for step_name, step in round_data.get("steps", {}).items():
                breakdown = step.get("agent_breakdown", {})
                lines.append(
                    "| "
                    f"{step_name} | {step.get('wall_clock_seconds')} | {step.get('agent_active_seconds')} | {step.get('agent', '')} | "
                    f"{breakdown.get('local_file_seconds', '')} | "
                    f"{breakdown.get('local_git_seconds', '')} | "
                    f"{breakdown.get('github_api_seconds', '')} | "
                    f"{breakdown.get('unattributed_seconds', '')} |"
                )
            if not round_data.get("steps"):
                lines.append("| (no step-level data) |  |  |  |  |  |  |  |")
            lines.append("")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _render_round_step_table(rounds: list[dict]) -> list[str]:
    """Render a single table: round=row, step=column."""
    lines = [
        "| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for round_data in rounds:
        lead = round_data.get("lead_agent", "?")
        total = round_data.get("duration_seconds")
        total_str = f"{total}s" if total is not None else "-"
        steps = round_data.get("steps", {})
        cells = []
        for step_key in _STEP_ORDER:
            step = steps.get(step_key)
            if step is None:
                cells.append("skip")
            else:
                dur = step.get("duration_seconds")
                cells.append(f"{dur}s" if dur is not None else "-")
        lines.append(
            f"| {round_data.get('round', '?')} | {lead} | "
            + " | ".join(cells)
            + f" | {total_str} |"
        )
    if not rounds:
        lines.append("| (no rounds) | | | | | | | |")
    return lines


def _format_duration(seconds: float | None) -> str:
    """Format seconds as 'Xm Ys' string."""
    if seconds is None:
        return "-"
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    if minutes > 0:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def build_final_summary(state: dict) -> dict:
    """Build a final summary dict from session state for user-facing report.

    Returns dict with:
    - pr_url: GitHub PR URL
    - outcome: final outcome string
    - total_rounds: number of rounds completed
    - total_duration: formatted total duration
    - round_timings: list of {round, lead_agent, duration} dicts
    - prompt_files: dict of agent -> prompt file path
    - state_file: state file path (added by caller)
    """
    repo = state.get("repo", "")
    pr_number = state.get("pr_number", "")
    pr_url = f"https://github.com/{repo}/pull/{pr_number}" if repo and pr_number else None

    started = _parse_iso(state.get("started_at"))
    finished = _parse_iso(state.get("finished_at"))
    total_secs = _seconds(started, finished)

    round_timings = []
    for round_ in state.get("rounds", []):
        r_started = _parse_iso(round_.get("started_at"))
        r_completed = _parse_iso(round_.get("completed_at"))
        r_secs = _seconds(r_started, r_completed)
        round_timings.append({
            "round": round_.get("round"),
            "lead_agent": round_.get("lead_agent", "unknown"),
            "duration_seconds": r_secs,
            "duration": _format_duration(r_secs),
        })

    return {
        "pr_url": pr_url,
        "outcome": state.get("final_outcome", "unknown"),
        "total_rounds": state.get("current_round", 0),
        "total_duration": _format_duration(total_secs),
        "total_duration_seconds": total_secs,
        "round_timings": round_timings,
    }


def export_debate_markdown(state: dict, output_path: str) -> str:
    """Export the full debate review session as a markdown file.

    Returns the output file path.
    """
    repo = state.get("repo", "")
    pr_number = state.get("pr_number", "")
    pr_url = f"https://github.com/{repo}/pull/{pr_number}" if repo and pr_number else ""

    lines = [
        f"# Debate Review: {repo}#{pr_number}",
        "",
        f"- **PR**: {pr_url}",
        f"- **Outcome**: {state.get('final_outcome', 'unknown')}",
        f"- **Rounds**: {state.get('current_round', 0)}",
    ]

    started = _parse_iso(state.get("started_at"))
    finished = _parse_iso(state.get("finished_at"))
    total_secs = _seconds(started, finished)
    if started:
        lines.append(f"- **Started**: {state.get('started_at', '')}")
    if finished:
        lines.append(f"- **Finished**: {state.get('finished_at', '')}")
    if total_secs is not None:
        lines.append(f"- **Total Duration**: {_format_duration(total_secs)}")

    # Round timing summary (round=row, step=column)
    lines.extend(["", "## Round Summary", ""])
    lines.append("| Round | Lead | Step0 | Step1 | Step2 | Step3 | Step4 | Total |")
    lines.append("| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for round_ in state.get("rounds", []):
        r_started = _parse_iso(round_.get("started_at"))
        r_completed = _parse_iso(round_.get("completed_at"))
        r_secs = _seconds(r_started, r_completed)
        step_traces = round_.get("step_traces", {})
        cells = []
        clean_pass = round_.get("clean_pass", False)
        for step_key in _STEP_ORDER:
            trace = step_traces.get(step_key)
            if trace is not None:
                s_start = _parse_iso(trace.get("started_at"))
                s_end = _parse_iso(trace.get("completed_at"))
                s_secs = _seconds(s_start, s_end)
                cells.append(_format_duration(s_secs))
            elif clean_pass and step_key in ("step2_cross_review", "step3_lead_apply"):
                cells.append("skip")
            else:
                cells.append("-")
        lines.append(
            f"| {round_.get('round', '?')} | {round_.get('lead_agent', '?')} | "
            + " | ".join(cells)
            + f" | {_format_duration(r_secs)} |"
        )

    # Debate ledger
    ledger = state.get("debate_ledger", [])
    if ledger:
        lines.extend(["", "## Debate Ledger", ""])
        for entry in ledger:
            status = entry.get("status", "unknown")
            summary = entry.get("summary", "")
            issue_id = entry.get("issue_id", "")
            lines.append(f"- **{issue_id}** [{status}] {summary}")

    # Issues
    issues = state.get("issues", {})
    if issues:
        applied = [i for i in issues.values() if i.get("application_status") == "applied"]
        recommended = [i for i in issues.values() if i.get("application_status") == "recommended"]
        withdrawn = [i for i in issues.values() if i.get("consensus_status") == "withdrawn"]
        open_issues = [i for i in issues.values()
                       if i.get("consensus_status") == "open"
                       or (i.get("consensus_status") == "accepted"
                           and i.get("application_status") not in ("applied", "recommended"))]

        if applied:
            lines.extend(["", "## Applied Fixes", ""])
            for issue in applied:
                msg = latest_report_message(issue)
                lines.append(f"- `{issue.get('file', '?')}:{issue.get('line', '?')}` — {msg}")

        if recommended:
            lines.extend(["", "## Recommended Fixes", ""])
            for issue in recommended:
                msg = latest_report_message(issue)
                lines.append(f"- `{issue.get('file', '?')}:{issue.get('line', '?')}` — {msg}")

        if withdrawn:
            lines.extend(["", "## Withdrawn Findings", ""])
            for issue in withdrawn:
                msg = latest_report_message(issue)
                reason = issue.get("consensus_reason", "")
                lines.append(f"- `{issue.get('file', '?')}:{issue.get('line', '?')}` — {msg}")
                if reason:
                    lines.append(f"  - Reason: {reason}")

        if open_issues:
            lines.extend(["", "## Unresolved Issues", ""])
            for issue in open_issues:
                msg = latest_report_message(issue)
                lines.append(f"- `{issue.get('file', '?')}:{issue.get('line', '?')}` — {msg}")

    # Round details
    for round_ in state.get("rounds", []):
        round_num = round_.get("round", "?")
        lines.extend(["", f"## Round {round_num} Details", ""])
        lines.append(f"- **Lead**: {round_.get('lead_agent', '?')}")
        lines.append(f"- **Status**: {round_.get('status', '?')}")
        lines.append(f"- **Clean pass**: {round_.get('clean_pass', '?')}")

    lines.append("")
    content = "\n".join(lines)

    with open(output_path, "w") as f:
        f.write(content)

    return output_path

from __future__ import annotations

import json
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


def _stats(values: list[float]) -> dict:
    if not values:
        return {"count": 0, "min": None, "max": None, "average": None, "median": None}
    return {
        "count": len(values),
        "min": round(min(values), 1),
        "max": round(max(values), 1),
        "average": round(mean(values), 1),
        "median": round(median(values), 1),
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
    breakdown["reasoning_seconds"] = max(active_seconds - used_seconds, 0.0)
    breakdown["active_seconds"] = active_seconds
    for key in (
        "local_file_seconds",
        "local_git_seconds",
        "github_api_seconds",
        "other_tool_seconds",
        "reasoning_seconds",
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
    step_summary.update(
        {
            "agent": step_summary.get("agent") or matched.get("agent") or default_agent,
            "started_at": _to_iso(started_at),
            "completed_at": _to_iso(completed_at),
            "duration_seconds": step_summary.get("duration_seconds") or _seconds(started_at, completed_at),
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
        step_summary = steps.get(step_name, {})
        step_summary.update(
            {
                "agent": trace.get("agent"),
                "started_at": _to_iso(started_at),
                "completed_at": _to_iso(completed_at),
                "duration_seconds": _seconds(started_at, completed_at),
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


def _build_stats(sessions: list[dict]) -> dict:
    session_durations = []
    round_durations = []
    step_durations: dict[str, list[float]] = defaultdict(list)
    lead_agent_round_durations: dict[str, list[float]] = defaultdict(list)

    for session in sessions:
        if session.get("duration_seconds") is not None:
            session_durations.append(session["duration_seconds"])
        for round_data in session.get("rounds", []):
            if round_data.get("duration_seconds") is not None:
                round_durations.append(round_data["duration_seconds"])
                lead_agent_round_durations[round_data.get("lead_agent")].append(round_data["duration_seconds"])
            for step_name, step in round_data.get("steps", {}).items():
                if step.get("duration_seconds") is not None:
                    step_durations[step_name].append(step["duration_seconds"])

    return {
        "session_duration_seconds": _stats(session_durations),
        "round_duration_seconds": _stats(round_durations),
        "step_duration_seconds": {step: _stats(values) for step, values in sorted(step_durations.items(), key=lambda item: _step_order_key(item[0]))},
        "lead_agent_round_duration_seconds": {agent: _stats(values) for agent, values in sorted(lead_agent_round_durations.items()) if agent},
    }


def _build_coverage(sessions: list[dict]) -> dict:
    rounds_total = 0
    rounds_with_any_steps = 0
    rounds_with_any_breakdown = 0
    steps_total = 0
    steps_with_breakdown = 0

    for session in sessions:
        for round_data in session.get("rounds", []):
            rounds_total += 1
            if round_data.get("steps"):
                rounds_with_any_steps += 1
            has_breakdown = False
            for step in round_data.get("steps", {}).values():
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


def _build_findings(sessions: list[dict], stats: dict, coverage: dict) -> list[dict]:
    findings = []
    findings.append(
        {
            "title": "Step-Level Coverage",
            "detail": (
                f"{coverage['rounds_total']}개 round 중 step 정보가 있는 round는 "
                f"{coverage['rounds_with_any_steps']}개, agent breakdown이 있는 round는 "
                f"{coverage['rounds_with_any_breakdown']}개입니다."
            ),
        }
    )

    step_stats = stats.get("step_duration_seconds", {})
    if step_stats:
        slowest_step, slowest_stat = max(
            step_stats.items(),
            key=lambda item: item[1]["median"] or -1,
        )
        findings.append(
            {
                "title": "Slowest Median Step",
                "detail": f"{slowest_step}의 median은 {slowest_stat['median']}초로, 집계된 step 중 가장 깁니다.",
            }
        )

    lead_stats = stats.get("lead_agent_round_duration_seconds", {})
    if lead_stats.get("cc", {}).get("median") is not None and lead_stats.get("codex", {}).get("median") is not None:
        cc_median = lead_stats["cc"]["median"]
        codex_median = lead_stats["codex"]["median"]
        slower = "CC" if cc_median > codex_median else "Codex"
        findings.append(
            {
                "title": "Lead Agent Comparison",
                "detail": (
                    f"Lead round median은 CC {cc_median}초, Codex {codex_median}초이며 "
                    f"{slower} 쪽이 더 느립니다."
                ),
            }
        )

    longest_session = None
    for session in sessions:
        duration = session.get("duration_seconds")
        if duration is None:
            continue
        if longest_session is None or duration > longest_session["duration_seconds"]:
            longest_session = session
    if longest_session:
        findings.append(
            {
                "title": "Longest Session",
                "detail": (
                    f"{longest_session['repo']}#{longest_session['pr_number']} 세션이 "
                    f"{longest_session['duration_seconds']}초로 가장 길었습니다."
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

        started_at = _parse_iso(state.get("started_at"))
        finished_at = _parse_iso(state.get("finished_at")) or now
        session_summary = {
            "state_file": str(state_path),
            "repo": state["repo"],
            "pr_number": state["pr_number"],
            "status": state.get("status"),
            "final_outcome": state.get("final_outcome"),
            "started_at": _to_iso(started_at),
            "finished_at": _to_iso(_parse_iso(state.get("finished_at"))),
            "duration_seconds": _seconds(started_at, finished_at),
            "rounds": [],
        }

        for round_data in sorted(state.get("rounds", []), key=lambda item: item.get("round", 0)):
            round_started = _parse_iso(round_data.get("started_at"))
            round_completed = _parse_iso(round_data.get("completed_at")) or finished_at
            session_summary["rounds"].append(
                {
                    "round": round_data["round"],
                    "lead_agent": round_data.get("lead_agent"),
                    "clean_pass": round_data.get("clean_pass"),
                    "started_at": _to_iso(round_started),
                    "completed_at": _to_iso(round_completed),
                    "duration_seconds": _seconds(round_started, round_completed),
                    "steps": _summarize_round_steps(
                        state,
                        session_summary,
                        round_data,
                        cc_index,
                        codex_index,
                        finished_at,
                    ),
                }
            )

        sessions.append(session_summary)

    sessions.sort(key=lambda item: item.get("started_at") or "", reverse=True)
    coverage = _build_coverage(sessions)
    stats = _build_stats(sessions)
    findings = _build_findings(sessions, stats, coverage)

    return {
        "generated_at": _to_iso(now),
        "totals": {
            "sessions": len(sessions),
            "completed": sum(1 for session in sessions if session.get("finished_at")),
            "in_progress": sum(1 for session in sessions if not session.get("finished_at")),
        },
        "coverage": coverage,
        "stats": stats,
        "findings": findings,
        "sessions": sessions,
    }


def _render_stats_rows(title: str, stats_dict: dict) -> list[str]:
    lines = [f"### {title}", "", "| Metric | Count | Min | Max | Average | Median |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for label, value in stats_dict.items():
        lines.append(
            f"| {label} | {value['count']} | {value['min']} | {value['max']} | {value['average']} | {value['median']} |"
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
            "## Statistics",
            "",
            f"- Coverage (rounds with steps): {report['coverage']['rounds_with_any_steps']} / {report['coverage']['rounds_total']}",
            f"- Coverage (rounds with breakdown): {report['coverage']['rounds_with_any_breakdown']} / {report['coverage']['rounds_total']}",
            "",
        ]
    )
    lines.extend(_render_stats_rows("Durations", {
        "Sessions": report["stats"]["session_duration_seconds"],
        "Rounds": report["stats"]["round_duration_seconds"],
    }))
    if report["stats"].get("step_duration_seconds"):
        lines.extend(_render_stats_rows("Step Durations", report["stats"]["step_duration_seconds"]))
    if report["stats"].get("lead_agent_round_duration_seconds"):
        lines.extend(_render_stats_rows(
            "Lead Agent Round Durations",
            {agent.capitalize(): stats for agent, stats in report["stats"]["lead_agent_round_duration_seconds"].items()},
        ))

    lines.extend(["## Appendix", ""])
    for session in report.get("sessions", []):
        lines.extend(
            [
                f"### {session['repo']}#{session['pr_number']}",
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
                    f"#### Round {round_data['round']}",
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
            if not round_data.get("steps"):
                lines.append("| (no step-level data) |  |  |  |  |  |  |")
            lines.append("")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


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

    # Round timing summary
    lines.extend(["", "## Round Summary", ""])
    lines.append("| Round | Lead Agent | Duration |")
    lines.append("| ---: | --- | --- |")
    for round_ in state.get("rounds", []):
        r_started = _parse_iso(round_.get("started_at"))
        r_completed = _parse_iso(round_.get("completed_at"))
        r_secs = _seconds(r_started, r_completed)
        lines.append(
            f"| {round_.get('round', '?')} | {round_.get('lead_agent', '?')} | {_format_duration(r_secs)} |"
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

        r_started = _parse_iso(round_.get("started_at"))
        r_completed = _parse_iso(round_.get("completed_at"))
        r_secs = _seconds(r_started, r_completed)
        lines.append(f"- **Duration**: {_format_duration(r_secs)}")

        # Step timings
        step_traces = round_.get("step_traces", {})
        if step_traces:
            lines.extend(["", "| Step | Agent | Duration |", "| --- | --- | --- |"])
            for step_name in sorted(step_traces.keys(), key=_step_order_key):
                trace = step_traces[step_name]
                s_start = _parse_iso(trace.get("started_at"))
                s_end = _parse_iso(trace.get("completed_at"))
                s_secs = _seconds(s_start, s_end)
                lines.append(f"| {step_name} | {trace.get('agent', '?')} | {_format_duration(s_secs)} |")

    lines.append("")
    content = "\n".join(lines)

    with open(output_path, "w") as f:
        f.write(content)

    return output_path

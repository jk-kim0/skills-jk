"""Step-level timing and trace instrumentation for debate-review sessions."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_journal_fields(state: dict) -> dict:
    journal = state.setdefault("journal", {})
    journal.setdefault("step_timings", {})
    journal.setdefault("current_step_trace", None)
    return journal


def _find_round(state: dict, round_num: int | None) -> dict | None:
    if round_num is None:
        return None
    for round_ in state.get("rounds", []):
        if round_.get("round") == round_num:
            return round_
    return None


def _infer_round_num(state: dict, round_num: int | None = None) -> int | None:
    if round_num is not None:
        return round_num
    journal = _ensure_journal_fields(state)
    inferred = journal.get("round", state.get("current_round"))
    return inferred if _find_round(state, inferred) is not None else None


def _ensure_round_fields(round_: dict) -> dict:
    round_.setdefault("step_timings", {})
    round_.setdefault("step_traces", {})
    return round_


def ensure_timing_fields(state: dict) -> None:
    _ensure_journal_fields(state)
    for round_ in state.get("rounds", []):
        _ensure_round_fields(round_)


def reset_step_timings(state):
    """Start a fresh step-timing map for a new round."""
    journal = _ensure_journal_fields(state)
    journal["step_timings"] = {}
    journal["current_step_trace"] = None


def record_step_timing(state, step_name, *, round_num: int | None = None, timestamp: str | None = None):
    """Record current UTC time for a step transition (first-write-wins)."""
    ensure_timing_fields(state)
    ts = timestamp or utc_now_iso()
    journal = state["journal"]
    timings = journal.setdefault("step_timings", {})
    timings.setdefault(step_name, ts)

    current_round = _find_round(state, _infer_round_num(state, round_num))
    if current_round is not None:
        _ensure_round_fields(current_round)
        current_round["step_timings"].setdefault(step_name, timings[step_name])

    return timings[step_name]


def _ensure_step_trace(state: dict, *, round_num: int, step_name: str) -> dict:
    ensure_timing_fields(state)
    round_ = _find_round(state, round_num)
    if round_ is None:
        raise ValueError(f"Round {round_num} not found")
    traces = _ensure_round_fields(round_)["step_traces"]
    trace = traces.setdefault(step_name, {"step": step_name, "command_spans": []})
    trace.setdefault("command_spans", [])
    return trace


def _merge_trace(trace: dict, patch: dict) -> dict:
    for key, value in patch.items():
        if value is None:
            continue
        if key == "command_spans":
            trace.setdefault("command_spans", [])
            trace["command_spans"].extend(deepcopy(value))
            continue
        existing = trace.get(key)
        if isinstance(existing, dict) and isinstance(value, dict):
            _merge_trace(existing, value)
            continue
        trace[key] = deepcopy(value)
    return trace


def start_step_trace(
    state: dict,
    *,
    round_num: int,
    step_name: str,
    agent: str,
    started_at: str | None = None,
    patch: dict | None = None,
) -> dict:
    started = record_step_timing(state, step_name, round_num=round_num, timestamp=started_at)
    trace = _ensure_step_trace(state, round_num=round_num, step_name=step_name)
    trace.setdefault("agent", agent)
    trace.setdefault("started_at", started)
    if patch:
        _merge_trace(trace, patch)
    state["journal"]["current_step_trace"] = {
        "round": round_num,
        "step": step_name,
        "agent": trace.get("agent"),
        "started_at": trace["started_at"],
    }
    return trace


def update_step_trace(
    state: dict,
    *,
    round_num: int,
    step_name: str,
    patch: dict,
) -> dict:
    trace = _ensure_step_trace(state, round_num=round_num, step_name=step_name)
    _merge_trace(trace, patch)
    return trace


def complete_step_trace(
    state: dict,
    *,
    round_num: int,
    step_name: str,
    completed_at: str | None = None,
    patch: dict | None = None,
) -> dict:
    trace = _ensure_step_trace(state, round_num=round_num, step_name=step_name)
    if "started_at" not in trace:
        trace["started_at"] = record_step_timing(state, step_name, round_num=round_num)
    if patch:
        _merge_trace(trace, patch)
    trace["completed_at"] = completed_at or utc_now_iso()
    current = state["journal"].get("current_step_trace")
    if current and current.get("round") == round_num and current.get("step") == step_name:
        state["journal"]["current_step_trace"] = None
    return trace

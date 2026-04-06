"""Tests for runtime heartbeat and stall supervision."""

from datetime import datetime, timedelta, timezone

from debate_review.runtime_events import normalize_event
from debate_review.runtime_supervision import StepSupervisor


def _plus(base: str, seconds: int) -> str:
    dt = datetime.fromisoformat(base)
    return (dt + timedelta(seconds=seconds)).isoformat()


def test_supervisor_transitions_from_awaiting_to_thinking():
    base = "2026-04-07T00:00:00+00:00"
    supervisor = StepSupervisor(agent="cc", started_at=base)

    supervisor.mark_process_started(observed_at=base)
    first = supervisor.snapshot(now=base)
    assert first["status"] == "awaiting_first_event"

    supervisor.on_event(
        normalize_event(
            "cc",
            {"type": "stream_event.message_start"},
            observed_at=_plus(base, 5),
        )
    )
    snapshot = supervisor.snapshot(now=_plus(base, 5))

    assert snapshot["status"] == "thinking"
    assert snapshot["last_event_kind"] == "turn_started"
    assert snapshot["stall_level"] == "none"


def test_supervisor_marks_codex_suspected_stall_after_90s():
    base = "2026-04-07T00:00:00+00:00"
    supervisor = StepSupervisor(agent="codex", started_at=base)
    supervisor.mark_process_started(observed_at=base)
    supervisor.on_event(
        normalize_event(
            "codex",
            {"type": "turn.started"},
            observed_at=_plus(base, 1),
        )
    )

    supervisor.evaluate(now=_plus(base, 92))
    snapshot = supervisor.snapshot(now=_plus(base, 92))

    assert snapshot["status"] == "suspected_stall"
    assert snapshot["stall_level"] == "suspected"
    assert snapshot["last_event_kind"] == "turn_started"


def test_supervisor_records_recovery_attempt():
    base = "2026-04-07T00:00:00+00:00"
    supervisor = StepSupervisor(agent="cc", started_at=base)

    supervisor.begin_recovery(
        "session_recreate",
        observed_at=_plus(base, 130),
        result="started",
        reconcile_summary="existing commit missing",
    )
    snapshot = supervisor.snapshot(now=_plus(base, 130))

    assert snapshot["status"] == "recovering"
    assert snapshot["recovery_attempts"][0]["kind"] == "session_recreate"
    assert snapshot["recovery_attempts"][0]["reconcile_summary"] == "existing commit missing"


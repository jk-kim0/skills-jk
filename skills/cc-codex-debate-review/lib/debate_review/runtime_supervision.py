"""Heartbeat and stall supervision for streaming debate-review steps."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _seconds_between(started_at: str | None, completed_at: str | None) -> int | None:
    start = _parse_iso(started_at)
    end = _parse_iso(completed_at)
    if start is None or end is None:
        return None
    return max(0, int((end - start).total_seconds()))


@dataclass(frozen=True)
class Thresholds:
    suspected: int
    hard: int


_THRESHOLDS = {
    "cc": Thresholds(suspected=45, hard=120),
    "codex": Thresholds(suspected=90, hard=180),
}


class StepSupervisor:
    """Tracks the runtime health of a single persistent-agent step."""

    def __init__(self, *, agent: str, started_at: str):
        self.agent = agent
        self.started_at = started_at
        self.status = "dispatching"
        self.last_event_at: str | None = None
        self.last_event_kind: str | None = None
        self.last_heartbeat_at: str | None = None
        self.last_strong_heartbeat_at: str | None = None
        self.heartbeat_source: str | None = None
        self.stall_level = "none"
        self.strong_heartbeat_count = 0
        self.weak_heartbeat_count = 0
        self.recovery_attempts: list[dict] = []

    def mark_process_started(self, *, observed_at: str) -> dict:
        self.status = "awaiting_first_event"
        self.last_heartbeat_at = observed_at
        self.heartbeat_source = "process_alive"
        self.weak_heartbeat_count += 1
        return self.snapshot(now=observed_at)

    def on_event(self, event: dict) -> dict:
        observed_at = event["ts"]
        self.last_event_at = observed_at
        self.last_event_kind = event["kind"]
        if event.get("heartbeat") == "strong":
            self.last_strong_heartbeat_at = observed_at
            self.last_heartbeat_at = observed_at
            self.heartbeat_source = "stdout_event"
            self.strong_heartbeat_count += 1
            self.stall_level = "none"
        display_status = event.get("display_status")
        if display_status:
            self.status = display_status
        return self.snapshot(now=observed_at)

    def on_stderr(self, line: str, *, observed_at: str) -> dict:
        if line:
            self.last_heartbeat_at = observed_at
            self.heartbeat_source = "stderr_line"
            self.weak_heartbeat_count += 1
            if self.status == "dispatching":
                self.status = "awaiting_first_event"
        return self.snapshot(now=observed_at)

    def on_process_alive(self, *, observed_at: str) -> dict:
        self.last_heartbeat_at = observed_at
        self.heartbeat_source = "process_alive"
        self.weak_heartbeat_count += 1
        return self.snapshot(now=observed_at)

    def evaluate(self, *, now: str) -> dict:
        if self.status in {"completed", "recovering", "failed"}:
            return self.snapshot(now=now)

        thresholds = _THRESHOLDS.get(self.agent, _THRESHOLDS["codex"])
        reference = self.last_strong_heartbeat_at or self.started_at
        gap = _seconds_between(reference, now) or 0

        if gap > thresholds.hard:
            self.status = "suspected_stall"
            self.stall_level = "hard"
        elif gap > thresholds.suspected:
            self.status = "suspected_stall"
            self.stall_level = "suspected"
        elif self.last_strong_heartbeat_at is None:
            self.status = "awaiting_first_event"
            self.stall_level = "none"
        elif gap > 10:
            self.status = "idle_but_alive"
            self.stall_level = "none"
        else:
            self.stall_level = "none"
        return self.snapshot(now=now)

    def begin_recovery(
        self,
        kind: str,
        *,
        observed_at: str,
        result: str,
        reconcile_summary: str | None = None,
    ) -> dict:
        self.status = "recovering"
        self.recovery_attempts.append(
            {
                "kind": kind,
                "started_at": observed_at,
                "completed_at": observed_at,
                "result": result,
                "reconcile_summary": reconcile_summary,
            }
        )
        return self.snapshot(now=observed_at)

    def snapshot(self, *, now: str | None = None) -> dict:
        now = now or self.last_event_at or self.last_heartbeat_at or self.started_at
        snapshot = {
            "status": self.status,
            "last_event_at": self.last_event_at,
            "last_event_kind": self.last_event_kind,
            "last_event_age_seconds": _seconds_between(self.last_event_at, now),
            "last_heartbeat_at": self.last_heartbeat_at,
            "heartbeat_source": self.heartbeat_source,
            "stall_level": self.stall_level,
            "strong_heartbeat_count": self.strong_heartbeat_count,
            "weak_heartbeat_count": self.weak_heartbeat_count,
            "recovery_attempts": deepcopy(self.recovery_attempts),
        }
        return snapshot


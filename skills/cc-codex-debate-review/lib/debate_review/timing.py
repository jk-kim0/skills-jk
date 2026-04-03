"""Step-level timing instrumentation for debate-review sessions."""

from datetime import datetime, timezone


def reset_step_timings(state):
    """Start a fresh step-timing map for a new round."""
    state["journal"]["step_timings"] = {}


def record_step_timing(state, step_name):
    """Record current UTC time for a step transition (first-write-wins)."""
    timings = state["journal"].setdefault("step_timings", {})
    if step_name not in timings:
        timings[step_name] = datetime.now(timezone.utc).isoformat()

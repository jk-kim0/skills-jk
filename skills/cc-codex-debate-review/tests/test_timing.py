"""Tests for round-level and step-level timing instrumentation."""

from datetime import datetime, timezone

from debate_review.round_ops import init_round, record_verdict, settle_round
from debate_review.timing import record_step_timing


def _is_iso_utc(value):
    """Check that value is a valid ISO 8601 UTC timestamp."""
    assert isinstance(value, str)
    dt = datetime.fromisoformat(value)
    assert dt.tzinfo is not None
    return True


# --- record_step_timing helper ---

def test_record_step_timing_writes_to_journal(sample_state):
    record_step_timing(sample_state, "step0_sync")
    timings = sample_state["journal"]["step_timings"]
    assert "step0_sync" in timings
    assert _is_iso_utc(timings["step0_sync"])


def test_record_step_timing_does_not_overwrite(sample_state):
    record_step_timing(sample_state, "step0_sync")
    first = sample_state["journal"]["step_timings"]["step0_sync"]
    record_step_timing(sample_state, "step0_sync")
    assert sample_state["journal"]["step_timings"]["step0_sync"] == first


def test_record_step_timing_initializes_missing_key(sample_state):
    # Simulate legacy state without step_timings
    del sample_state["journal"]["step_timings"]
    record_step_timing(sample_state, "step1_lead_review")
    assert "step1_lead_review" in sample_state["journal"]["step_timings"]


# --- Round-level timing ---

def test_init_round_sets_started_at(sample_state):
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    r = sample_state["rounds"][0]
    assert "started_at" in r
    assert _is_iso_utc(r["started_at"])


def test_init_round_idempotent_preserves_started_at(sample_state):
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    ts = sample_state["rounds"][0]["started_at"]
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    assert sample_state["rounds"][0]["started_at"] == ts


def test_settle_round_sets_completed_at(sample_state):
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    record_verdict(sample_state, round_num=1, verdict="has_findings")
    settle_round(sample_state, round_num=1)
    r = sample_state["rounds"][0]
    assert "completed_at" in r
    assert _is_iso_utc(r["completed_at"])


# --- Step timing via CLI commands ---

def test_step_timings_in_initial_state(sample_state):
    """create_initial_state should include step_timings in journal."""
    assert "step_timings" in sample_state["journal"]
    assert isinstance(sample_state["journal"]["step_timings"], dict)

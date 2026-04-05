"""Tests for debate_review.progress module."""

from __future__ import annotations

import io
import time
from unittest.mock import patch

from debate_review.progress import (
    ProgressReporter,
    _format_elapsed,
    format_step1,
    format_step2,
    format_step3,
)


# ── _format_elapsed ──


def test_format_elapsed_seconds_only():
    assert _format_elapsed(45) == "45s"


def test_format_elapsed_zero():
    assert _format_elapsed(0) == "0s"


def test_format_elapsed_minutes_and_seconds():
    assert _format_elapsed(125) == "2m 5s"


# ── ProgressReporter output ──


def test_round_start():
    buf = io.StringIO()
    pr = ProgressReporter(file=buf)
    pr.round_start(1, "codex", "cc")
    output = buf.getvalue()
    assert "Round 1" in output
    assert "lead: codex" in output


def test_step_start_and_done():
    buf = io.StringIO()
    pr = ProgressReporter(file=buf)
    pr.step_start("Step1", "codex", "lead review")
    pr.step_done("Step1", "codex", "lead review", 154.0, "2 findings")
    output = buf.getvalue()
    assert "[Step1] codex lead review..." in output
    assert "✓" in output
    assert "2m 34s" in output
    assert "2 findings" in output


def test_step_skip():
    buf = io.StringIO()
    pr = ProgressReporter(file=buf)
    pr.step_skip("Step2", "clean pass")
    assert "[Step2] skip (clean pass)" in buf.getvalue()


def test_debate_content():
    buf = io.StringIO()
    pr = ProgressReporter(file=buf)
    pr.debate_content(["finding 1", "finding 2"])
    output = buf.getvalue()
    assert "  finding 1" in output
    assert "  finding 2" in output


def test_settle():
    buf = io.StringIO()
    pr = ProgressReporter(file=buf)
    pr.settle("continue", next_round=2, settled=["isu_001"], unresolved=["isu_002"])
    output = buf.getvalue()
    assert "settle ✓ continue → round 2" in output
    assert "settled: isu_001" in output
    assert "unresolved: isu_002" in output


def test_final_result():
    buf = io.StringIO()
    pr = ProgressReporter(file=buf)
    pr.final_result("consensus", 3, "4m 43s", applied=1, withdrawn=2, unresolved=0)
    output = buf.getvalue()
    assert "consensus after 3 rounds" in output
    assert "applied: 1" in output


# ── timer ──


def test_timer_ticks(monkeypatch):
    buf = io.StringIO()
    pr = ProgressReporter(file=buf)
    monkeypatch.setattr(pr, "TICK_INTERVAL", 0.1)
    pr.step_start("Step1", "codex", "lead review")
    time.sleep(0.35)
    pr._stop_timer()
    output = buf.getvalue()
    # Should have at least 2 tick lines
    tick_lines = [l for l in output.splitlines() if "..." in l and "(" in l]
    assert len(tick_lines) >= 2


def test_step_done_stops_timer():
    buf = io.StringIO()
    pr = ProgressReporter(file=buf)
    pr.step_start("Step1", "codex", "review")
    pr.step_done("Step1", "codex", "review", 5.0)
    assert pr._timer is None


def test_step_done_during_tick_does_not_reschedule(monkeypatch):
    buf = io.StringIO()
    pr = ProgressReporter(file=buf)
    pr._step_label = "[Step1] codex lead review"
    pr._step_start = time.monotonic()
    pr._running = True
    pr._token = 1

    wrote_tick = {"seen": False}
    original_write = pr._write

    def write_and_stop(text):
        original_write(text)
        if "..." in text and "(" in text and not wrote_tick["seen"]:
            wrote_tick["seen"] = True
            pr.step_done("Step1", "codex", "lead review", 5.0)

    monkeypatch.setattr(pr, "_write", write_and_stop)

    try:
        pr._tick()
        assert pr._timer is None
    finally:
        if pr._timer is not None:
            pr._timer.cancel()


# ── format_step1 ──


def test_format_step1_findings():
    response = {
        "findings": [
            {"severity": "warning", "file": "foo.py", "line": 10, "anchor": "bar", "message": "bad code"},
        ],
        "rebuttal_responses": [],
        "verdict": "has_findings",
    }
    lines = format_step1(response)
    assert any("[warning] foo.py:10 (bar)" in l for l in lines)
    assert any("bad code" in l for l in lines)
    assert any("verdict: has_findings" in l for l in lines)


def test_format_step1_withdrawals():
    response = {
        "findings": [],
        "withdrawals": [{"issue_id": "isu_001", "reason": "duplicate"}],
        "verdict": "has_findings",
    }
    lines = format_step1(response)
    assert any("isu_001 WITHDRAW" in l for l in lines)
    assert any("duplicate" in l for l in lines)


def test_format_step1_rebuttals():
    response = {
        "findings": [],
        "rebuttal_responses": [
            {"issue_id": "isu_001", "decision": "withdraw", "reason": "accepted rebuttal"},
        ],
        "verdict": "no_findings_mergeable",
    }
    lines = format_step1(response)
    assert any("isu_001 WITHDRAW" in l for l in lines)
    assert any("verdict: no_findings_mergeable" in l for l in lines)


# ── format_step2 ──


def test_format_step2_verifications_and_findings():
    response = {
        "cross_verifications": [
            {"issue_id": "isu_001", "verdict": "rebut", "reason": "out of scope"},
            {"issue_id": "isu_002", "verdict": "accept", "reason": "agreed"},
        ],
        "findings": [
            {"severity": "warning", "file": "bar.py", "line": 5, "anchor": "baz", "message": "new issue"},
        ],
    }
    lines = format_step2(response)
    assert any("isu_001 REBUT" in l for l in lines)
    assert any("out of scope" in l for l in lines)
    assert any("isu_002 ACCEPT" in l for l in lines)
    assert any("[warning] bar.py:5 (baz)" in l for l in lines)
    assert any("1 new finding" in l for l in lines)


# ── format_step3 ──


def test_format_step3_decisions_and_application():
    response = {
        "rebuttal_decisions": [
            {"report_id": "rpt_001", "decision": "maintain", "reason": "still valid"},
        ],
        "cross_finding_evaluations": [
            {"report_id": "rpt_003", "decision": "accept", "reason": "good point"},
        ],
        "application_result": {
            "applied_issues": ["isu_002"],
            "failed_issues": [],
            "commit_sha": "abc1234567890",
        },
    }
    lines = format_step3(response)
    assert any("rpt_001 MAINTAIN" in l for l in lines)
    assert any("rpt_003 ACCEPT" in l for l in lines)
    assert any("CODE APPLIED: isu_002 → commit abc1234" in l for l in lines)


def test_format_step3_failed_issues():
    response = {
        "rebuttal_decisions": [],
        "cross_finding_evaluations": [],
        "application_result": {
            "applied_issues": [],
            "failed_issues": [{"issue_id": "isu_003", "reason": "conflict"}],
            "commit_sha": "",
        },
    }
    lines = format_step3(response)
    assert any("CODE FAILED: isu_003" in l for l in lines)

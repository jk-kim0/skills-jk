import pytest
from debate_review.round_ops import init_round
from debate_review.state import create_initial_state
from debate_review.issue_ops import (
    CANONICAL_KINDS,
    generate_issue_key,
    normalize_message,
    upsert_issue,
)


def test_issue_key_canonical_kind():
    key = generate_issue_key(criterion=3, file="src/foo.py", anchor="L42", message="loop never ends")
    assert "kind:unbounded_loop" in key
    assert "criterion:3" in key
    assert "file:src/foo.py" in key
    assert "anchor:L42" in key


def test_issue_key_fallback_sha1():
    key = generate_issue_key(criterion=99, file="src/bar.py", anchor="L10", message="some weird issue")
    assert "criterion:99" in key
    assert "msg:" in key
    # 12-char hex
    msg_part = [p for p in key.split("|") if p.startswith("msg:")][0]
    hex_val = msg_part[len("msg:"):]
    assert len(hex_val) == 12
    assert all(c in "0123456789abcdef" for c in hex_val)


def test_upsert_creates_new_issue(sample_state):
    result = upsert_issue(
        sample_state,
        agent="cc",
        round_num=1,
        severity="critical",
        criterion=3,
        file="src/foo.py",
        line=42,
        anchor="L42",
        message="loop never ends",
    )
    assert result["action"] == "created"
    assert result["issue_id"] == "isu_001"
    assert result["report_id"] == "rpt_001"
    assert result["issue_key"] is not None

    issue = sample_state["issues"]["isu_001"]
    assert issue["severity"] == "critical"
    assert issue["criterion"] == 3
    assert issue["file"] == "src/foo.py"
    assert issue["line"] == 42
    assert issue["anchor"] == "L42"
    assert issue["opened_by"] == "cc"
    assert issue["introduced_in_round"] == 1
    assert issue["consensus_status"] == "open"
    assert issue["application_status"] == "pending"
    assert "cc" in issue["accepted_by"]
    assert len(issue["reports"]) == 1


def test_upsert_appends_report_to_existing(sample_state):
    upsert_issue(
        sample_state,
        agent="cc",
        round_num=1,
        severity="critical",
        criterion=3,
        file="src/foo.py",
        line=42,
        anchor="L42",
        message="loop never ends",
    )
    result = upsert_issue(
        sample_state,
        agent="codex",
        round_num=1,
        severity="critical",
        criterion=3,
        file="src/foo.py",
        line=42,
        anchor="L42",
        message="loop never ends",
    )
    assert result["action"] == "appended"
    assert result["issue_id"] == "isu_001"

    issue = sample_state["issues"]["isu_001"]
    assert "cc" in issue["accepted_by"]
    assert "codex" in issue["accepted_by"]
    assert len(issue["reports"]) == 2


def test_upsert_reopens_withdrawn_issue(sample_state):
    upsert_issue(
        sample_state,
        agent="cc",
        round_num=1,
        severity="warning",
        criterion=5,
        file="src/bar.py",
        line=10,
        anchor="L10",
        message="stale state",
    )
    # Manually withdraw the issue
    issue_id = list(sample_state["issues"].keys())[0]
    sample_state["issues"][issue_id]["consensus_status"] = "withdrawn"

    result = upsert_issue(
        sample_state,
        agent="codex",
        round_num=2,
        severity="warning",
        criterion=5,
        file="src/bar.py",
        line=10,
        anchor="L10",
        message="stale state",
    )
    assert result["action"] == "appended"
    issue = sample_state["issues"][issue_id]
    assert issue["consensus_status"] == "open"
    assert issue["application_status"] == "pending"
    assert "codex" in issue["accepted_by"]


def test_upsert_sets_report_status_open(sample_state):
    """upsert_issue should set report status to 'open' explicitly."""
    result = upsert_issue(
        sample_state, agent="cc", round_num=1, severity="critical",
        criterion=1, file="src/a.py", line=1, anchor="x", message="test",
    )
    issue = sample_state["issues"][result["issue_id"]]
    assert issue["reports"][0]["status"] == "open"


def test_upsert_resets_applied_issue(sample_state):
    upsert_issue(
        sample_state,
        agent="cc",
        round_num=1,
        severity="suggestion",
        criterion=6,
        file="src/baz.py",
        line=99,
        anchor="L99",
        message="unused variable x",
    )
    issue_id = list(sample_state["issues"].keys())[0]
    # Simulate applied state
    sample_state["issues"][issue_id]["consensus_status"] = "accepted"
    sample_state["issues"][issue_id]["application_status"] = "applied"
    sample_state["issues"][issue_id]["applied_by"] = "codex"
    sample_state["issues"][issue_id]["application_commit_sha"] = "deadbeef"

    result = upsert_issue(
        sample_state,
        agent="codex",
        round_num=2,
        severity="suggestion",
        criterion=6,
        file="src/baz.py",
        line=99,
        anchor="L99",
        message="unused variable x",
    )
    assert result["action"] == "appended"
    issue = sample_state["issues"][issue_id]
    assert issue["consensus_status"] == "open"
    assert issue["application_status"] == "pending"
    assert issue["applied_by"] is None
    assert issue["application_commit_sha"] is None
    assert issue["accepted_by"] == ["codex"]  # reset to reporting agent only


def test_upsert_tracks_cross_verifier_reports_in_step2():
    state = create_initial_state(
        repo="owner/repo",
        repo_root="/tmp/repo",
        pr_number=123,
        is_fork=False,
        head_sha="abc1234def5678",
        pr_branch_name="feat/test",
        max_rounds=10,
    )
    init_round(state, round_num=1, lead_agent="codex", synced_head_sha="abc1234def5678")

    result = upsert_issue(
        state,
        agent="cc",
        round_num=1,
        severity="warning",
        criterion=7,
        file="src/c.py",
        line=12,
        anchor="MAX_TIMEOUT",
        message="hardcoded timeout value",
    )

    round_ = state["rounds"][0]
    assert round_["step1"]["report_ids"] == []
    assert round_["step1"]["issue_ids_touched"] == []
    assert round_["step2"]["report_ids"] == [result["report_id"]]
    assert round_["step2"]["issue_ids_touched"] == [result["issue_id"]]

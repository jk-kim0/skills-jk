from debate_review.state import create_initial_state
from debate_review.round_ops import init_round
from debate_review.application import (
    record_application_phase1,
    record_application_phase2,
    record_application_phase3,
)


def _state_with_accepted_issues():
    """State with round 1, lead=codex, two accepted issues ready for application."""
    state = create_initial_state(
        repo="owner/repo", repo_root="/tmp/repo", pr_number=123,
        is_fork=False, head_sha="abc123", pr_branch_name="feat/test",
    )
    init_round(state, round_num=1, lead_agent="codex", synced_head_sha="abc123")
    state["issues"]["isu_001"] = {
        "issue_id": "isu_001", "issue_key": "k1",
        "criterion": 1, "file": "src/a.py", "line": 10, "anchor": "foo",
        "severity": "critical", "consensus_status": "accepted",
        "application_status": "pending", "accepted_by": ["codex", "cc"],
        "rejected_by": [], "applied_by": None, "application_commit_sha": None,
        "reports": [{"report_id": "rpt_001", "agent": "codex", "round": 1,
                     "severity": "critical", "message": "Missing validation",
                     "reported_at": "2026-03-30T00:00:00+00:00", "status": "open"}],
        "created_at": "2026-03-30T00:00:00+00:00", "updated_at": "2026-03-30T00:00:00+00:00",
    }
    state["issues"]["isu_002"] = {
        "issue_id": "isu_002", "issue_key": "k2",
        "criterion": 8, "file": "src/b.py", "line": 20, "anchor": "bar",
        "severity": "warning", "consensus_status": "accepted",
        "application_status": "pending", "accepted_by": ["codex", "cc"],
        "rejected_by": [], "applied_by": None, "application_commit_sha": None,
        "reports": [{"report_id": "rpt_002", "agent": "codex", "round": 1,
                     "severity": "warning", "message": "Duplicate logic",
                     "reported_at": "2026-03-30T00:00:00+00:00", "status": "open"}],
        "created_at": "2026-03-30T00:00:00+00:00", "updated_at": "2026-03-30T00:00:00+00:00",
    }
    return state


def test_phase1_records_applied_and_failed():
    state = _state_with_accepted_issues()
    result = record_application_phase1(
        state, round_num=1,
        applied_issue_ids=["isu_001"], failed_issue_ids=["isu_002"],
    )
    assert result["phase"] == 1
    assert state["issues"]["isu_001"]["application_status"] == "applied"
    assert state["issues"]["isu_002"]["application_status"] == "failed"
    assert state["journal"]["applied_issue_ids"] == ["isu_001"]
    assert state["journal"]["failed_application_issue_ids"] == ["isu_002"]
    assert state["journal"]["step"] == "step3_lead_apply"
    assert state["journal"]["commit_sha"] is None
    assert state["journal"]["push_verified"] is False


def test_phase1_idempotent():
    state = _state_with_accepted_issues()
    record_application_phase1(state, round_num=1, applied_issue_ids=["isu_001"], failed_issue_ids=[])
    record_application_phase1(state, round_num=1, applied_issue_ids=["isu_001"], failed_issue_ids=[])
    assert state["issues"]["isu_001"]["application_status"] == "applied"
    assert state["journal"]["applied_issue_ids"] == ["isu_001"]


def test_phase2_records_commit_sha():
    state = _state_with_accepted_issues()
    record_application_phase1(state, round_num=1, applied_issue_ids=["isu_001"], failed_issue_ids=[])
    result = record_application_phase2(state, round_num=1, commit_sha="deadbeef123")
    assert result["phase"] == 2
    assert state["journal"]["commit_sha"] == "deadbeef123"


def test_phase2_idempotent():
    state = _state_with_accepted_issues()
    record_application_phase1(state, round_num=1, applied_issue_ids=["isu_001"], failed_issue_ids=[])
    record_application_phase2(state, round_num=1, commit_sha="deadbeef123")
    record_application_phase2(state, round_num=1, commit_sha="deadbeef123")
    assert state["journal"]["commit_sha"] == "deadbeef123"


def test_phase3_finalizes():
    state = _state_with_accepted_issues()
    record_application_phase1(state, round_num=1, applied_issue_ids=["isu_001"], failed_issue_ids=["isu_002"])
    record_application_phase2(state, round_num=1, commit_sha="deadbeef123")
    result = record_application_phase3(state, round_num=1)
    assert result["phase"] == 3
    assert result["push_verified"] is True
    # Journal
    assert state["journal"]["push_verified"] is True
    assert state["journal"]["state_persisted"] is True
    # Issue-level
    assert state["issues"]["isu_001"]["applied_by"] == "codex"
    assert state["issues"]["isu_001"]["application_commit_sha"] == "deadbeef123"
    # Failed issue should NOT have applied_by/commit_sha
    assert state["issues"]["isu_002"]["applied_by"] is None
    # Round step3
    round_ = state["rounds"][0]
    assert round_["step3"]["applied_issue_ids"] == ["isu_001"]
    assert round_["step3"]["failed_application_issue_ids"] == ["isu_002"]
    assert round_["step3"]["commit_sha"] == "deadbeef123"
    assert round_["step3"]["push_verified"] is True


def test_phase3_idempotent():
    state = _state_with_accepted_issues()
    record_application_phase1(state, round_num=1, applied_issue_ids=["isu_001"], failed_issue_ids=[])
    record_application_phase2(state, round_num=1, commit_sha="deadbeef123")
    record_application_phase3(state, round_num=1)
    record_application_phase3(state, round_num=1)
    assert state["journal"]["push_verified"] is True
    assert state["issues"]["isu_001"]["applied_by"] == "codex"


def test_full_3phase_flow():
    state = _state_with_accepted_issues()
    record_application_phase1(state, round_num=1, applied_issue_ids=["isu_001", "isu_002"], failed_issue_ids=[])
    assert state["journal"]["step"] == "step3_lead_apply"
    record_application_phase2(state, round_num=1, commit_sha="abc123def")
    assert state["journal"]["commit_sha"] == "abc123def"
    record_application_phase3(state, round_num=1)
    assert state["journal"]["push_verified"] is True
    assert state["journal"]["state_persisted"] is True
    for isu_id in ["isu_001", "isu_002"]:
        assert state["issues"][isu_id]["applied_by"] == "codex"
        assert state["issues"][isu_id]["application_commit_sha"] == "abc123def"

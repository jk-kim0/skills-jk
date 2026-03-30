import pytest
from debate_review.state import create_initial_state
from debate_review.round_ops import init_round
from debate_review.cross_verification import record_cross_verification, resolve_rebuttals


def _state_with_round_and_issues():
    """Create a state with round 1 (lead=codex), and two issues with reports."""
    state = create_initial_state(
        repo="owner/repo", repo_root="/tmp/repo", pr_number=123,
        is_fork=False, head_sha="abc123", pr_branch_name="feat/test",
    )
    init_round(state, round_num=1, lead_agent="codex", synced_head_sha="abc123")
    # Issue 1 reported by codex (lead)
    state["issues"]["isu_001"] = {
        "issue_id": "isu_001", "issue_key": "criterion:1|file:src/a.py|anchor:foo|kind:missing_validation",
        "criterion": 1, "file": "src/a.py", "line": 10, "anchor": "foo",
        "severity": "critical", "consensus_status": "open", "application_status": "pending",
        "accepted_by": ["codex"], "rejected_by": [], "applied_by": None,
        "application_commit_sha": None,
        "reports": [{"report_id": "rpt_001", "agent": "codex", "round": 1, "severity": "critical", "message": "Missing validation", "reported_at": "2026-03-30T00:00:00+00:00", "status": "open"}],
        "created_at": "2026-03-30T00:00:00+00:00", "updated_at": "2026-03-30T00:00:00+00:00",
    }
    # Issue 2 reported by codex (lead)
    state["issues"]["isu_002"] = {
        "issue_id": "isu_002", "issue_key": "criterion:8|file:src/b.py|anchor:bar|kind:duplicate_logic",
        "criterion": 8, "file": "src/b.py", "line": 20, "anchor": "bar",
        "severity": "warning", "consensus_status": "open", "application_status": "pending",
        "accepted_by": ["codex"], "rejected_by": [], "applied_by": None,
        "application_commit_sha": None,
        "reports": [{"report_id": "rpt_002", "agent": "codex", "round": 1, "severity": "warning", "message": "Duplicate logic", "reported_at": "2026-03-30T00:00:00+00:00", "status": "open"}],
        "created_at": "2026-03-30T00:00:00+00:00", "updated_at": "2026-03-30T00:00:00+00:00",
    }
    return state


# Test 1: record_cross_verification — accept adds cross-verifier to accepted_by, sets consensus
def test_record_cross_verification_accept():
    state = _state_with_round_and_issues()
    verifications = [{"report_id": "rpt_001", "decision": "accept", "reason": "Valid finding"}]
    result = record_cross_verification(state, round_num=1, verifications=verifications)
    issue = state["issues"]["isu_001"]
    assert "cc" in issue["accepted_by"]  # cross-verifier (cc) added
    assert issue["consensus_status"] == "accepted"
    round_ = state["rounds"][0]
    assert "rpt_001" in round_["step2"]["accepted_report_ids"]


# Test 2: record_cross_verification — rebut records in step2.rebuttals
def test_record_cross_verification_rebut():
    state = _state_with_round_and_issues()
    verifications = [{"report_id": "rpt_002", "decision": "rebut", "reason": "Intentional duplication"}]
    result = record_cross_verification(state, round_num=1, verifications=verifications)
    round_ = state["rounds"][0]
    assert len(round_["step2"]["rebuttals"]) == 1
    assert round_["step2"]["rebuttals"][0]["report_id"] == "rpt_002"
    assert round_["step2"]["rebuttals"][0]["issue_id"] == "isu_002"


# Test 3: record_cross_verification — accept on fork PR sets application_status=recommended
def test_record_cross_verification_accept_fork():
    state = _state_with_round_and_issues()
    state["is_fork"] = True
    verifications = [{"report_id": "rpt_001", "decision": "accept", "reason": "Valid"}]
    record_cross_verification(state, round_num=1, verifications=verifications)
    assert state["issues"]["isu_001"]["application_status"] == "recommended"


# Test 4: resolve_rebuttals step=1a — withdraw recalculates accepted_by
def test_resolve_rebuttals_step1a_withdraw():
    state = _state_with_round_and_issues()
    # Setup: issue has only one report from codex, accepted_by=["codex"]
    decisions = [{"report_id": "rpt_001", "decision": "withdraw", "reason": "Fair point"}]
    result = resolve_rebuttals(state, round_num=1, step="1a", decisions=decisions)
    issue = state["issues"]["isu_001"]
    assert issue["consensus_status"] == "withdrawn"
    assert issue["consensus_reason"] == "Fair point"
    assert issue["accepted_by"] == []
    assert issue["application_status"] == "not_applicable"
    # Check report status
    assert issue["reports"][0].get("status") == "withdrawn"
    # Check step1.rebuttal_responses
    round_ = state["rounds"][0]
    assert len(round_["step1"]["rebuttal_responses"]) == 1


# Test 5: resolve_rebuttals step=1a — maintain returns re-report targets
def test_resolve_rebuttals_step1a_maintain():
    state = _state_with_round_and_issues()
    decisions = [{"report_id": "rpt_001", "decision": "maintain", "reason": "Still valid"}]
    result = resolve_rebuttals(state, round_num=1, step="1a", decisions=decisions)
    assert "rpt_001" in result.get("re_report_ids", [])


# Test 6: resolve_rebuttals step=3 — withdraw adds to step3.withdrawn_report_ids
def test_resolve_rebuttals_step3_withdraw():
    state = _state_with_round_and_issues()
    decisions = [{"report_id": "rpt_002", "decision": "withdraw", "reason": "Accepted rebuttal"}]
    result = resolve_rebuttals(state, round_num=1, step="3", decisions=decisions)
    round_ = state["rounds"][0]
    assert "rpt_002" in round_["step3"]["withdrawn_report_ids"]
    issue = state["issues"]["isu_002"]
    assert issue["consensus_status"] == "withdrawn"


# Test 7: resolve_rebuttals step=3 — accept adds lead to accepted_by
def test_resolve_rebuttals_step3_accept():
    state = _state_with_round_and_issues()
    # isu_002 reported by codex (lead), cross-verifier (cc) reported new finding
    # Simulate: isu_002 was reported by cc (cross-verifier), accepted_by=["cc"]
    state["issues"]["isu_002"]["accepted_by"] = ["cc"]
    state["issues"]["isu_002"]["reports"][0]["agent"] = "cc"
    decisions = [{"report_id": "rpt_002", "decision": "accept", "reason": "Good catch"}]
    result = resolve_rebuttals(state, round_num=1, step="3", decisions=decisions)
    issue = state["issues"]["isu_002"]
    assert "codex" in issue["accepted_by"]  # lead (codex) added
    assert issue["consensus_status"] == "accepted"
    round_ = state["rounds"][0]
    assert "rpt_002" in round_["step3"]["accepted_report_ids"]


# Test 8: resolve_rebuttals step=3 — maintain records in step3.rebuttals
def test_resolve_rebuttals_step3_maintain():
    state = _state_with_round_and_issues()
    decisions = [{"report_id": "rpt_002", "decision": "maintain", "reason": "Disagree with rebuttal"}]
    result = resolve_rebuttals(state, round_num=1, step="3", decisions=decisions)
    round_ = state["rounds"][0]
    assert len(round_["step3"]["rebuttals"]) == 1
    assert round_["step3"]["rebuttals"][0]["report_id"] == "rpt_002"


# Test 9: withdraw with remaining open reports — accepted_by recalculated, stays open
def test_resolve_rebuttals_withdraw_partial():
    state = _state_with_round_and_issues()
    # Add a second report from cc to isu_001
    state["issues"]["isu_001"]["reports"].append({
        "report_id": "rpt_003", "agent": "cc", "round": 1,
        "severity": "critical", "message": "Also missing validation",
        "reported_at": "2026-03-30T00:00:00+00:00", "status": "open",
    })
    state["issues"]["isu_001"]["accepted_by"] = ["codex", "cc"]
    # Withdraw only the codex report
    decisions = [{"report_id": "rpt_001", "decision": "withdraw", "reason": "Rebuttal accepted"}]
    result = resolve_rebuttals(state, round_num=1, step="1a", decisions=decisions)
    issue = state["issues"]["isu_001"]
    assert issue["reports"][0]["status"] == "withdrawn"
    assert issue["reports"][1]["status"] == "open"
    assert issue["accepted_by"] == ["cc"]  # only cc has open report
    assert issue["consensus_status"] == "open"  # not both agents
    assert issue.get("consensus_reason") is None  # cleared on partial withdraw

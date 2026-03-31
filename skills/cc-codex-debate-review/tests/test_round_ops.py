import pytest
from debate_review.round_ops import init_round, record_verdict, settle_round


def test_init_round(sample_state):
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    assert len(sample_state["rounds"]) == 1
    r = sample_state["rounds"][0]
    assert r["lead_agent"] == "codex"
    assert r["clean_pass"] is False


def test_record_verdict_has_findings(sample_state):
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    result = record_verdict(sample_state, round_num=1, verdict="has_findings")
    assert result["clean_pass"] is False


def test_record_verdict_clean_pass(sample_state):
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    result = record_verdict(sample_state, round_num=1, verdict="no_findings_mergeable")
    assert result["clean_pass"] is True


def test_settle_continue(sample_state):
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    record_verdict(sample_state, round_num=1, verdict="has_findings")
    result = settle_round(sample_state, round_num=1)
    assert result["result"] == "continue"
    assert sample_state["current_round"] == 2
    assert sample_state["status"] == "in_progress"


def test_settle_consensus(sample_state):
    # Round 1: clean pass (codex)
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    record_verdict(sample_state, round_num=1, verdict="no_findings_mergeable")
    settle_round(sample_state, round_num=1)
    # Round 2: clean pass (cc)
    init_round(sample_state, round_num=2, lead_agent="cc", synced_head_sha="abc")
    record_verdict(sample_state, round_num=2, verdict="no_findings_mergeable")
    result = settle_round(sample_state, round_num=2)
    assert result["result"] == "consensus_reached"
    assert sample_state["status"] == "consensus_reached"
    assert sample_state["final_outcome"] == "consensus"
    assert sample_state["finished_at"] is not None
    assert sample_state["head"]["terminal_sha"] == sample_state["head"]["last_observed_pr_sha"]


def test_settle_max_rounds(sample_state):
    sample_state["max_rounds"] = 1
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    record_verdict(sample_state, round_num=1, verdict="has_findings")
    result = settle_round(sample_state, round_num=1)
    assert result["result"] == "max_rounds_exceeded"
    assert sample_state["status"] == "max_rounds_exceeded"
    assert sample_state["final_outcome"] == "no_consensus"
    assert sample_state["head"]["terminal_sha"] == sample_state["head"]["last_observed_pr_sha"]


def test_settle_unresolved_issues(sample_state):
    from debate_review.issue_ops import upsert_issue
    upsert_issue(sample_state, agent="codex", round_num=1, severity="warning",
                 criterion=3, file="src/foo.ts", line=42, anchor="retry",
                 message="unbounded")
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    record_verdict(sample_state, round_num=1, verdict="has_findings")
    result = settle_round(sample_state, round_num=1)
    assert len(result["unresolved_issue_ids"]) == 1


def test_settle_consensus_requires_different_agents(sample_state):
    """Consensus requires 2 consecutive clean passes from DIFFERENT lead agents."""
    # Round 1: clean pass (codex)
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    record_verdict(sample_state, round_num=1, verdict="no_findings_mergeable")
    settle_round(sample_state, round_num=1)
    # Round 2: clean pass (codex again — same agent)
    init_round(sample_state, round_num=2, lead_agent="codex", synced_head_sha="abc")
    record_verdict(sample_state, round_num=2, verdict="no_findings_mergeable")
    result = settle_round(sample_state, round_num=2)
    # Should NOT be consensus — same lead agent
    assert result["result"] == "continue"
    assert sample_state["status"] == "in_progress"


def test_settle_continue_syncs_journal_round(sample_state):
    """settle_round with 'continue' should update journal.round."""
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    record_verdict(sample_state, round_num=1, verdict="has_findings")
    settle_round(sample_state, round_num=1)
    assert sample_state["journal"]["round"] == 2


def test_init_round_idempotent(sample_state):
    """init_round should skip if round already exists (no duplicate)."""
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    assert len(sample_state["rounds"]) == 1


def test_settle_fork_recommendation_issue_ids(sample_state):
    """Fork PR settle should populate recommendation_issue_ids."""
    sample_state["is_fork"] = True
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    sample_state["issues"]["isu_001"] = {
        "issue_id": "isu_001", "consensus_status": "accepted",
        "application_status": "recommended", "accepted_by": ["cc", "codex"],
    }
    record_verdict(sample_state, round_num=1, verdict="no_findings_mergeable")
    result = settle_round(sample_state, round_num=1)
    assert "isu_001" in result["recommendation_issue_ids"]


def test_settle_rejects_non_active_round(sample_state):
    """settle_round should reject already-completed rounds."""
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    record_verdict(sample_state, round_num=1, verdict="has_findings")
    settle_round(sample_state, round_num=1)
    with pytest.raises(ValueError, match="not active"):
        settle_round(sample_state, round_num=1)


def test_upsert_populates_step1_tracking(sample_state):
    """upsert_issue should populate the active round's step1 tracking arrays."""
    from debate_review.issue_ops import upsert_issue
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    result = upsert_issue(sample_state, agent="codex", round_num=1, severity="warning",
                          criterion=3, file="src/foo.ts", line=42, anchor="retry",
                          message="unbounded")
    r = sample_state["rounds"][0]
    assert result["report_id"] in r["step1"]["report_ids"]
    assert result["issue_id"] in r["step1"]["issue_ids_touched"]


def test_settle_returns_settled_issues(sample_state):
    """settle_round should return settled_issues for issues resolved in this round."""
    from debate_review.issue_ops import upsert_issue
    from debate_review.cross_verification import record_cross_verification

    # Round 1: codex finds issue, cc accepts → consensus_status=accepted
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    upsert_result = upsert_issue(
        sample_state, agent="codex", round_num=1, severity="warning",
        criterion=3, file="src/foo.ts", line=42, anchor="retry",
        message="unbounded loop",
    )
    report_id = upsert_result["report_id"]
    record_cross_verification(
        sample_state, round_num=1,
        verifications=[{"report_id": report_id, "decision": "accept", "reason": "agree"}],
    )
    # Mark as applied so verdict can be clean
    issue_id = upsert_result["issue_id"]
    sample_state["issues"][issue_id]["application_status"] = "applied"
    sample_state["issues"][issue_id]["applied_by"] = "codex"
    record_verdict(sample_state, round_num=1, verdict="no_findings_mergeable")
    result = settle_round(sample_state, round_num=1)

    assert "settled_issues" in result
    assert len(result["settled_issues"]) == 1
    settled = result["settled_issues"][0]
    assert settled["issue_id"] == issue_id
    assert settled["consensus_status"] == "accepted"


def test_settle_returns_empty_settled_issues_when_none(sample_state):
    """settle_round should return empty settled_issues when no issues were settled."""
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    record_verdict(sample_state, round_num=1, verdict="has_findings")
    result = settle_round(sample_state, round_num=1)
    assert result["settled_issues"] == []


def test_settle_detects_issues_settled_via_resolve_rebuttals(sample_state):
    """settled_issues should include issues withdrawn via resolve_rebuttals step 3."""
    from debate_review.issue_ops import upsert_issue
    from debate_review.cross_verification import record_cross_verification, resolve_rebuttals

    # Round 1: codex finds issue, cc rebuts
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    upsert_result = upsert_issue(
        sample_state, agent="codex", round_num=1, severity="warning",
        criterion=3, file="src/foo.ts", line=42, anchor="retry",
        message="unbounded loop",
    )
    report_id = upsert_result["report_id"]
    issue_id = upsert_result["issue_id"]
    record_cross_verification(
        sample_state, round_num=1,
        verifications=[{"report_id": report_id, "decision": "rebut", "reason": "intentional"}],
    )
    # Lead (codex) withdraws via resolve_rebuttals step 3
    resolve_rebuttals(
        sample_state, round_num=1, step="3",
        decisions=[{"report_id": report_id, "decision": "withdraw", "reason": "rebuttal accepted"}],
    )
    record_verdict(sample_state, round_num=1, verdict="has_findings")
    result = settle_round(sample_state, round_num=1)

    # Issue was withdrawn via step3, not step1/step2 — must still appear in settled_issues
    assert len(result["settled_issues"]) == 1
    assert result["settled_issues"][0]["issue_id"] == issue_id
    assert result["settled_issues"][0]["consensus_status"] == "withdrawn"


def test_settle_no_duplicate_settled_from_application(sample_state):
    """Issues only applied (not settled) in this round should not appear in settled_issues."""
    from debate_review.issue_ops import upsert_issue
    from debate_review.cross_verification import record_cross_verification

    # Round 1: issue accepted
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    upsert_result = upsert_issue(
        sample_state, agent="codex", round_num=1, severity="warning",
        criterion=3, file="src/foo.ts", line=42, anchor="retry",
        message="unbounded loop",
    )
    report_id = upsert_result["report_id"]
    issue_id = upsert_result["issue_id"]
    record_cross_verification(
        sample_state, round_num=1,
        verifications=[{"report_id": report_id, "decision": "accept", "reason": "agree"}],
    )
    record_verdict(sample_state, round_num=1, verdict="has_findings")
    r1 = settle_round(sample_state, round_num=1)
    # Issue was settled (accepted) in round 1
    assert len(r1["settled_issues"]) == 1

    # Round 2: issue gets applied but no new settlement decision
    init_round(sample_state, round_num=2, lead_agent="cc", synced_head_sha="abc")
    sample_state["rounds"][1]["step3"]["applied_issue_ids"].append(issue_id)
    sample_state["issues"][issue_id]["application_status"] = "applied"
    record_verdict(sample_state, round_num=2, verdict="no_findings_mergeable")
    r2 = settle_round(sample_state, round_num=2)
    # Issue should NOT appear again — it was only applied, not re-settled
    assert len(r2["settled_issues"]) == 0


def test_settle_deduplicates_against_debate_ledger(sample_state):
    """settled_issues should skip issues already in debate_ledger with same status."""
    from debate_review.issue_ops import upsert_issue
    from debate_review.cross_verification import record_cross_verification, resolve_rebuttals

    # Setup: issue accepted in round 1, recorded in ledger
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    r1 = upsert_issue(sample_state, agent="codex", round_num=1, severity="warning",
                       criterion=3, file="src/foo.ts", line=42, anchor="retry", message="loop")
    report_id_1 = r1["report_id"]
    issue_id = r1["issue_id"]
    record_cross_verification(sample_state, round_num=1,
                              verifications=[{"report_id": report_id_1, "decision": "accept", "reason": "ok"}])
    sample_state["issues"][issue_id]["application_status"] = "applied"
    record_verdict(sample_state, round_num=1, verdict="no_findings_mergeable")
    settle_round(sample_state, round_num=1)

    # Simulate ledger entry written by orchestrator
    sample_state["debate_ledger"] = [
        {"issue_id": issue_id, "status": "accepted", "summary": "...", "round": 1}
    ]

    # Round 2: same issue touched again (e.g., partial report withdraw on multi-report issue)
    sample_state["current_round"] = 2
    init_round(sample_state, round_num=2, lead_agent="cc", synced_head_sha="abc")
    r2 = upsert_issue(sample_state, agent="cc", round_num=2, severity="warning",
                       criterion=3, file="src/foo.ts", line=42, anchor="retry", message="still loop")
    # Issue is touched in step1, consensus still accepted
    sample_state["issues"][issue_id]["consensus_status"] = "accepted"
    sample_state["issues"][issue_id]["application_status"] = "applied"
    record_verdict(sample_state, round_num=2, verdict="has_findings")
    result = settle_round(sample_state, round_num=2)

    # Should NOT duplicate — already in ledger with same status
    assert len(result["settled_issues"]) == 0

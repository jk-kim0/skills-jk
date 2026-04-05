import pytest
from debate_review.round_ops import init_round, record_verdict, settle_round


def test_init_round(sample_state):
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    assert len(sample_state["rounds"]) == 1
    r = sample_state["rounds"][0]
    assert r["lead_agent"] == "codex"
    assert r["clean_pass"] is False


def test_init_round_auto_lead_agent(sample_state):
    """lead_agent=None auto-determines from round number."""
    init_round(sample_state, round_num=1, synced_head_sha="abc")
    assert sample_state["rounds"][0]["lead_agent"] == "codex"  # odd → codex
    init_round(sample_state, round_num=2, synced_head_sha="abc")
    assert sample_state["rounds"][1]["lead_agent"] == "cc"  # even → cc


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


def test_settle_deduplicates_same_round_same_status(sample_state):
    """settled_issues should skip issues already in ledger with same status AND same round."""
    from debate_review.issue_ops import upsert_issue
    from debate_review.cross_verification import record_cross_verification

    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    r1 = upsert_issue(sample_state, agent="codex", round_num=1, severity="warning",
                       criterion=3, file="src/foo.ts", line=42, anchor="retry", message="loop")
    issue_id = r1["issue_id"]
    record_cross_verification(sample_state, round_num=1,
                              verifications=[{"report_id": r1["report_id"], "decision": "accept", "reason": "ok"}])
    sample_state["issues"][issue_id]["application_status"] = "applied"

    # Ledger already has this issue settled in round 1
    sample_state["debate_ledger"] = [
        {"issue_id": issue_id, "status": "accepted", "summary": "...", "round": 1}
    ]

    record_verdict(sample_state, round_num=1, verdict="no_findings_mergeable")
    result = settle_round(sample_state, round_num=1)

    # Same round + same status → skip
    assert len(result["settled_issues"]) == 0


def test_settle_skips_partial_withdraw_no_status_change(sample_state):
    """Partial withdraw of multi-report issue that doesn't change consensus should NOT appear."""
    from debate_review.issue_ops import upsert_issue
    from debate_review.cross_verification import record_cross_verification, resolve_rebuttals

    # Round 1: codex reports, cc accepts → accepted
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    r1a = upsert_issue(sample_state, agent="codex", round_num=1, severity="warning",
                        criterion=3, file="src/foo.ts", line=42, anchor="retry", message="loop")
    issue_id = r1a["issue_id"]
    # Also add a second report from codex (same issue)
    r1b = upsert_issue(sample_state, agent="codex", round_num=1, severity="warning",
                        criterion=3, file="src/foo.ts", line=42, anchor="retry", message="loop")
    record_cross_verification(sample_state, round_num=1,
                              verifications=[
                                  {"report_id": r1a["report_id"], "decision": "accept", "reason": "ok"},
                                  {"report_id": r1b["report_id"], "decision": "accept", "reason": "ok"},
                              ])
    sample_state["issues"][issue_id]["application_status"] = "applied"
    record_verdict(sample_state, round_num=1, verdict="no_findings_mergeable")
    settle_round(sample_state, round_num=1)

    sample_state["debate_ledger"] = [
        {"issue_id": issue_id, "status": "accepted", "summary": "...", "round": 1}
    ]

    # Round 2: partial withdraw of first report — issue stays accepted
    init_round(sample_state, round_num=2, lead_agent="cc", synced_head_sha="abc")
    resolve_rebuttals(sample_state, round_num=2, step="1a",
                      decisions=[{"report_id": r1a["report_id"], "decision": "withdraw", "reason": "partial"}])
    record_verdict(sample_state, round_num=2, verdict="has_findings")
    result = settle_round(sample_state, round_num=2)

    # Issue was touched but status didn't change and no new report → should NOT appear
    assert result["settled_issues"] == []


def test_settle_allows_re_raised_issue_in_new_round(sample_state):
    """Re-raised issue settled again in a new round should appear in settled_issues."""
    from debate_review.issue_ops import upsert_issue
    from debate_review.cross_verification import record_cross_verification, resolve_rebuttals

    # Round 1: issue withdrawn
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    r1 = upsert_issue(sample_state, agent="codex", round_num=1, severity="warning",
                       criterion=3, file="src/foo.ts", line=42, anchor="retry", message="loop")
    issue_id = r1["issue_id"]
    record_cross_verification(sample_state, round_num=1,
                              verifications=[{"report_id": r1["report_id"], "decision": "rebut", "reason": "scope"}])
    resolve_rebuttals(sample_state, round_num=1, step="3",
                      decisions=[{"report_id": r1["report_id"], "decision": "withdraw", "reason": "scope"}])
    record_verdict(sample_state, round_num=1, verdict="has_findings")
    settle_round(sample_state, round_num=1)

    sample_state["debate_ledger"] = [
        {"issue_id": issue_id, "status": "withdrawn", "summary": "...", "round": 1, "reason": "scope"}
    ]

    # Round 2: re-raise same issue, then withdraw again
    init_round(sample_state, round_num=2, lead_agent="cc", synced_head_sha="abc")
    r2 = upsert_issue(sample_state, agent="cc", round_num=2, severity="warning",
                       criterion=3, file="src/foo.ts", line=42, anchor="retry", message="loop again")
    record_cross_verification(sample_state, round_num=2,
                              verifications=[{"report_id": r2["report_id"], "decision": "rebut", "reason": "still scope"}])
    resolve_rebuttals(sample_state, round_num=2, step="3",
                      decisions=[{"report_id": r2["report_id"], "decision": "withdraw", "reason": "still scope"}])
    record_verdict(sample_state, round_num=2, verdict="has_findings")
    result = settle_round(sample_state, round_num=2)

    # Different round → should appear (re-raised then re-withdrawn)
    assert len(result["settled_issues"]) == 1
    assert result["settled_issues"][0]["issue_id"] == issue_id


def test_withdraw_issue(sample_state):
    """withdraw_issue should mark an open issue as withdrawn."""
    from debate_review.issue_ops import upsert_issue, withdraw_issue

    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    r1 = upsert_issue(sample_state, agent="codex", round_num=1, severity="warning",
                       criterion=3, file="config.yml", line=10, anchor="agent_mode_fallback",
                       message="missing fallback")
    issue_id = r1["issue_id"]
    assert sample_state["issues"][issue_id]["consensus_status"] == "open"

    result = withdraw_issue(sample_state, issue_id=issue_id, agent="codex", round_num=1,
                            reason="duplicate of isu_002 — same root cause")
    assert result["status"] == "withdrawn"
    assert sample_state["issues"][issue_id]["consensus_status"] == "withdrawn"
    assert "duplicate" in sample_state["issues"][issue_id]["consensus_reason"]
    # issue_ids_touched should include the withdrawn issue
    round_data = sample_state["rounds"][0]
    assert issue_id in round_data["step1"]["issue_ids_touched"]


def test_withdraw_issue_rejects_non_open(sample_state):
    """withdraw_issue should reject issues that are not open."""
    from debate_review.issue_ops import upsert_issue, withdraw_issue
    import pytest

    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    r1 = upsert_issue(sample_state, agent="codex", round_num=1, severity="warning",
                       criterion=3, file="config.yml", line=10, anchor="fallback",
                       message="missing fallback")
    issue_id = r1["issue_id"]
    # Manually set to withdrawn
    sample_state["issues"][issue_id]["consensus_status"] = "withdrawn"

    with pytest.raises(ValueError, match="not open"):
        withdraw_issue(sample_state, issue_id=issue_id, agent="codex", round_num=1, reason="test")


def test_withdraw_issue_rejects_wrong_agent(sample_state):
    """withdraw_issue should reject withdrawal by an agent that didn't open the issue."""
    from debate_review.issue_ops import upsert_issue, withdraw_issue
    import pytest

    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    r1 = upsert_issue(sample_state, agent="codex", round_num=1, severity="warning",
                       criterion=3, file="config.yml", line=10, anchor="fallback",
                       message="missing fallback")
    issue_id = r1["issue_id"]

    with pytest.raises(ValueError, match="cannot withdraw"):
        withdraw_issue(sample_state, issue_id=issue_id, agent="cc", round_num=1, reason="not mine")


def test_settle_stall_detection_after_2_no_progress_rounds(sample_state):
    """2 consecutive rounds with no settlements and no applied code → stalled."""
    from debate_review.issue_ops import upsert_issue
    from debate_review.cross_verification import record_cross_verification

    # Round 1: create an accepted issue (this round has settled_issues → progress)
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    r1 = upsert_issue(sample_state, agent="codex", round_num=1, severity="warning",
                       criterion=3, file="src/foo.ts", line=42, anchor="retry", message="loop")
    issue_id = r1["issue_id"]
    record_cross_verification(sample_state, round_num=1,
                              verifications=[{"report_id": r1["report_id"], "decision": "accept", "reason": "ok"}])
    record_verdict(sample_state, round_num=1, verdict="has_findings")
    r1_result = settle_round(sample_state, round_num=1)
    assert r1_result["result"] == "continue"
    # Round 1 has settled_issues (accepted issue), so it's NOT stalled
    assert "stall_count" not in r1_result

    # Add ledger entry so round 2 won't re-count the same settled issue
    sample_state["debate_ledger"] = [
        {"issue_id": issue_id, "status": "accepted", "summary": "...", "round": 1}
    ]

    # Round 2: no new settlements, no code applied, but has unresolved issue
    init_round(sample_state, round_num=2, lead_agent="cc", synced_head_sha="abc")
    record_verdict(sample_state, round_num=2, verdict="has_findings")
    r2_result = settle_round(sample_state, round_num=2)
    assert r2_result["result"] == "continue"
    assert r2_result.get("stall_count") == 1

    # Round 3: still no progress
    init_round(sample_state, round_num=3, lead_agent="codex", synced_head_sha="abc")
    record_verdict(sample_state, round_num=3, verdict="has_findings")
    r3_result = settle_round(sample_state, round_num=3)
    assert r3_result["result"] == "stalled"
    assert r3_result["stall_count"] == 2
    assert sample_state["status"] == "stalled"
    assert sample_state["final_outcome"] == "stalled"
    assert "error_message" in sample_state
    assert "2 consecutive rounds" in sample_state["error_message"]


def test_settle_no_stall_when_clean_pass(sample_state):
    """Clean pass rounds (no unresolved issues) should NOT trigger stall detection."""
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    record_verdict(sample_state, round_num=1, verdict="no_findings_mergeable")
    r1 = settle_round(sample_state, round_num=1)
    assert r1["result"] == "continue"
    assert "stall_count" not in r1

    init_round(sample_state, round_num=2, lead_agent="codex", synced_head_sha="abc")
    record_verdict(sample_state, round_num=2, verdict="no_findings_mergeable")
    r2 = settle_round(sample_state, round_num=2)
    assert r2["result"] == "continue"  # not stalled, just no consensus (same agent)


def test_settle_stall_resets_after_progress(sample_state):
    """Progress in a round should reset the stall counter."""
    from debate_review.issue_ops import upsert_issue
    from debate_review.cross_verification import record_cross_verification

    # Round 1: create open issue (not accepted), no code applied → no progress
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    r1 = upsert_issue(sample_state, agent="codex", round_num=1, severity="warning",
                       criterion=3, file="src/foo.ts", line=42, anchor="retry", message="loop")
    issue_id = r1["issue_id"]
    # Do NOT accept — leave issue open so settled_issues is empty
    record_verdict(sample_state, round_num=1, verdict="has_findings")
    r1_result = settle_round(sample_state, round_num=1)
    assert r1_result["result"] == "continue"
    assert r1_result.get("stall_count") == 1  # first no-progress round

    # Round 2: accept issue + apply code → progress
    init_round(sample_state, round_num=2, lead_agent="cc", synced_head_sha="abc")
    record_cross_verification(sample_state, round_num=2,
                              verifications=[{"report_id": r1["report_id"], "decision": "accept", "reason": "ok"}])
    sample_state["rounds"][1]["step3"]["applied_issue_ids"] = [issue_id]
    sample_state["issues"][issue_id]["application_status"] = "applied"
    record_verdict(sample_state, round_num=2, verdict="has_findings")
    r2 = settle_round(sample_state, round_num=2)
    assert r2["result"] == "continue"
    assert "stall_count" not in r2  # progress was made (applied code)

    # Add ledger entry so settled_issues won't re-count in round 3
    sample_state["debate_ledger"].append(
        {"issue_id": issue_id, "status": "accepted", "summary": "...", "round": 2}
    )

    # Round 3: new open issue, no code applied → no progress, but stall_count resets to 1
    init_round(sample_state, round_num=3, lead_agent="codex", synced_head_sha="abc")
    upsert_issue(sample_state, agent="codex", round_num=3, severity="warning",
                 criterion=5, file="src/bar.ts", line=10, anchor="timeout", message="hardcoded")
    record_verdict(sample_state, round_num=3, verdict="has_findings")
    r3_result = settle_round(sample_state, round_num=3)
    assert r3_result["result"] == "continue"
    # stall_count is 1, NOT 2 — the progress in round 2 reset the streak
    assert r3_result.get("stall_count") == 1


def test_settle_populates_debate_ledger(sample_state):
    """settle_round should populate state['debate_ledger'] with settled issues."""
    from debate_review.issue_ops import upsert_issue
    from debate_review.cross_verification import record_cross_verification, resolve_rebuttals

    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    r1 = upsert_issue(sample_state, agent="codex", round_num=1, severity="warning",
                       criterion=3, file="src/foo.ts", line=42, anchor="retry",
                       message="unbounded loop")
    report_id = r1["report_id"]
    issue_id = r1["issue_id"]
    # cc rebuts, codex withdraws
    record_cross_verification(sample_state, round_num=1,
                              verifications=[{"report_id": report_id, "decision": "rebut", "reason": "scope"}])
    resolve_rebuttals(sample_state, round_num=1, step="3",
                      decisions=[{"report_id": report_id, "decision": "withdraw", "reason": "rebuttal accepted"}])
    record_verdict(sample_state, round_num=1, verdict="has_findings")
    settle_round(sample_state, round_num=1)

    ledger = sample_state["debate_ledger"]
    assert len(ledger) == 1
    entry = ledger[0]
    assert entry["issue_id"] == issue_id
    assert entry["status"] == "withdrawn"
    assert entry["round"] == 1


def test_record_verdict_auto_corrects_contradictory_has_findings(sample_state, capsys):
    """has_findings with no new findings and all issues resolved → auto-correct to no_findings_mergeable (#208)."""
    # Simulate: issues from earlier rounds are all resolved
    sample_state["issues"]["isu_001"] = {
        "issue_id": "isu_001", "issue_key": "k1",
        "opened_by": "codex", "introduced_in_round": 1,
        "criterion": 1, "file": "src/a.py", "line": 10, "anchor": "foo",
        "severity": "warning", "consensus_status": "accepted",
        "application_status": "applied", "accepted_by": ["codex", "cc"],
        "rejected_by": [], "applied_by": "codex", "application_commit_sha": "abc",
        "consensus_reason": None,
        "reports": [{"report_id": "rpt_001", "agent": "codex", "round": 1,
                     "severity": "warning", "message": "test",
                     "reported_at": "2026-03-30T00:00:00+00:00", "status": "open"}],
        "created_at": "2026-03-30T00:00:00+00:00", "updated_at": "2026-03-30T00:00:00+00:00",
    }
    # New round with no new findings — step1.report_ids is empty
    init_round(sample_state, round_num=4, lead_agent="cc", synced_head_sha="abc")
    # Agent says has_findings but step1 has no report_ids and no open issues
    result = record_verdict(sample_state, round_num=4, verdict="has_findings")
    assert result["verdict"] == "no_findings_mergeable"
    assert result["clean_pass"] is True
    err = capsys.readouterr().err
    assert "Auto-correcting" in err


def test_record_verdict_has_findings_with_open_issues_is_not_corrected(sample_state):
    """has_findings is valid when open issues exist, even without new findings."""
    from debate_review.issue_ops import upsert_issue
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    upsert_issue(sample_state, agent="codex", round_num=1, severity="warning",
                 criterion=3, file="src/a.py", line=1, anchor="x", message="test")
    result = record_verdict(sample_state, round_num=1, verdict="has_findings")
    assert result["verdict"] == "has_findings"
    assert result["clean_pass"] is False

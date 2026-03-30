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

import json
import sys

from debate_review.context import (
    build_applicable_issues,
    build_context,
    build_cross_findings,
    build_cross_rebuttals,
    build_debate_ledger_text,
    build_lead_reports,
    build_open_issues,
    build_pending_rebuttals,
    build_review_context,
)
from debate_review.issue_ops import upsert_issue
from debate_review.cross_verification import record_cross_verification, resolve_rebuttals
from debate_review.round_ops import init_round, record_verdict, settle_round
from debate_review.state import create_initial_state, load_state, save_state


def _make_state(**overrides):
    defaults = dict(
        repo="owner/repo", repo_root="/tmp/repo", pr_number=123,
        is_fork=False, head_sha="abc123", pr_branch_name="feat/test",
    )
    defaults.update(overrides)
    return create_initial_state(**defaults)


def _add_finding(state, round_num, agent="codex", severity="warning",
                 criterion=7, file="src/a.py", line=10, anchor="FOO", message="Test issue"):
    return upsert_issue(
        state, agent=agent, round_num=round_num, severity=severity,
        criterion=criterion, file=file, line=line, anchor=anchor, message=message,
    )


# --- build_review_context ---

def test_review_context_round_1():
    state = _make_state()
    result = build_review_context(state, round_num=1)
    assert "First round" in result


def test_review_context_with_completed_round():
    state = _make_state()
    init_round(state, round_num=1, synced_head_sha="abc123")
    _add_finding(state, 1, agent="codex", file="src/a.py", anchor="validate", message="Missing check")
    record_verdict(state, round_num=1, verdict="has_findings")
    settle_round(state, round_num=1)

    result = build_review_context(state, round_num=2)
    assert "Round 1" in result
    assert "codex" in result
    assert "src/a.py" in result


# --- build_open_issues ---

def test_open_issues_includes_open():
    state = _make_state()
    init_round(state, round_num=1, synced_head_sha="abc123")
    _add_finding(state, 1)
    result = build_open_issues(state)
    assert len(result) == 1
    assert result[0]["consensus_status"] == "open"


def test_open_issues_excludes_applied():
    state = _make_state()
    init_round(state, round_num=1, synced_head_sha="abc123")
    res = _add_finding(state, 1)
    issue = state["issues"][res["issue_id"]]
    issue["consensus_status"] = "accepted"
    issue["application_status"] = "applied"
    result = build_open_issues(state)
    assert len(result) == 0


def test_open_issues_includes_accepted_not_applied():
    state = _make_state()
    init_round(state, round_num=1, synced_head_sha="abc123")
    res = _add_finding(state, 1)
    issue = state["issues"][res["issue_id"]]
    issue["consensus_status"] = "accepted"
    issue["application_status"] = "pending"
    result = build_open_issues(state)
    assert len(result) == 1


def test_open_issues_fork_excludes_recommended():
    state = _make_state(is_fork=True)
    init_round(state, round_num=1, synced_head_sha="abc123")
    res = _add_finding(state, 1)
    issue = state["issues"][res["issue_id"]]
    issue["consensus_status"] = "accepted"
    issue["application_status"] = "recommended"
    result = build_open_issues(state)
    assert len(result) == 0


# --- build_debate_ledger_text ---

def test_debate_ledger_empty():
    state = _make_state()
    result = build_debate_ledger_text(state)
    assert "First round" in result


def test_debate_ledger_with_entries():
    state = _make_state()
    state["debate_ledger"] = [
        {"issue_id": "isu_001", "status": "accepted", "reason": None, "summary": "Fix applied", "round": 1},
        {"issue_id": "isu_002", "status": "withdrawn", "reason": "Intentional", "summary": "Dropped", "round": 2},
    ]
    result = build_debate_ledger_text(state)
    assert "isu_001 [accepted]" in result
    assert "isu_002 [withdrawn]" in result
    assert "(reason: Intentional)" in result
    assert "re-raise" in result


# --- build_pending_rebuttals ---

def test_pending_rebuttals_round_1():
    state = _make_state()
    result = build_pending_rebuttals(state, round_num=1)
    assert result == []


def test_pending_rebuttals_with_data():
    state = _make_state()
    init_round(state, round_num=1, synced_head_sha="abc123")
    res = _add_finding(state, 1)
    report_id = res["report_id"]

    # Simulate a step3 rebuttal from round 1
    state["rounds"][0]["step3"]["rebuttals"] = [
        {"report_id": report_id, "issue_id": res["issue_id"], "decision": "maintain", "reason": "Disagree"},
    ]

    result = build_pending_rebuttals(state, round_num=2)
    assert len(result) == 1
    assert result[0]["report_id"] == report_id
    assert result[0]["reason"] == "Disagree"
    assert result[0]["file"] == "src/a.py"


# --- build_lead_reports ---

def test_lead_reports():
    state = _make_state()
    init_round(state, round_num=1, synced_head_sha="abc123")
    res = _add_finding(state, 1, agent="codex")
    result = build_lead_reports(state, round_num=1)
    assert len(result) == 1
    assert result[0]["report_id"] == res["report_id"]


# --- build_cross_findings ---

def test_cross_findings():
    state = _make_state()
    init_round(state, round_num=1, synced_head_sha="abc123")
    _add_finding(state, 1, agent="codex")  # lead finding

    # Add cross-verifier finding
    cross_res = _add_finding(state, 1, agent="cc", file="src/b.py", anchor="BAR", message="Cross issue")
    result = build_cross_findings(state, round_num=1)
    assert len(result) == 1
    assert result[0]["report_id"] == cross_res["report_id"]


# --- build_applicable_issues ---

def test_applicable_issues():
    state = _make_state()
    init_round(state, round_num=1, synced_head_sha="abc123")
    res = _add_finding(state, 1)
    issue = state["issues"][res["issue_id"]]
    issue["consensus_status"] = "accepted"
    issue["application_status"] = "pending"
    result = build_applicable_issues(state)
    assert len(result) == 1
    assert result[0]["issue_id"] == res["issue_id"]


def test_applicable_issues_excludes_applied():
    state = _make_state()
    init_round(state, round_num=1, synced_head_sha="abc123")
    res = _add_finding(state, 1)
    issue = state["issues"][res["issue_id"]]
    issue["consensus_status"] = "accepted"
    issue["application_status"] = "applied"
    result = build_applicable_issues(state)
    assert len(result) == 0


def test_applicable_issues_fork_skips_code_application():
    state = _make_state(is_fork=True)
    init_round(state, round_num=1, synced_head_sha="abc123")
    res = _add_finding(state, 1)
    issue = state["issues"][res["issue_id"]]
    issue["consensus_status"] = "accepted"
    issue["application_status"] = "pending"
    result = build_applicable_issues(state)
    assert result == []


def test_applicable_issues_dry_run_skips_code_application():
    state = _make_state(dry_run=True)
    init_round(state, round_num=1, synced_head_sha="abc123")
    res = _add_finding(state, 1)
    issue = state["issues"][res["issue_id"]]
    issue["consensus_status"] = "accepted"
    issue["application_status"] = "pending"
    result = build_applicable_issues(state)
    assert result == []


# --- build_context (integration) ---

def test_build_context_returns_all_keys():
    state = _make_state()
    init_round(state, round_num=1, synced_head_sha="abc123")
    _add_finding(state, 1)
    result = build_context(state, round_num=1)
    expected_keys = {
        "review_context", "open_issues", "debate_ledger",
        "pending_rebuttals", "lead_reports", "cross_rebuttals",
        "cross_findings", "applicable_issues",
    }
    assert set(result.keys()) == expected_keys
    assert isinstance(result["review_context"], str)
    assert isinstance(result["open_issues"], list)
    assert isinstance(result["debate_ledger"], str)


# --- CLI integration ---

def _run_cli(monkeypatch, args):
    monkeypatch.setattr(sys, "argv", ["debate-review"] + args)
    from debate_review.cli import main
    try:
        main()
    except SystemExit:
        pass


def test_cli_build_context(monkeypatch, capsys, tmp_path):
    state = _make_state()
    init_round(state, round_num=1, synced_head_sha="abc123")
    _add_finding(state, 1)
    path = str(tmp_path / "ctx-state.json")
    save_state(state, path)

    _run_cli(monkeypatch, ["build-context", "--state-file", path, "--round", "1"])
    out = capsys.readouterr().out
    result = json.loads(out)
    assert "review_context" in result
    assert len(result["open_issues"]) == 1
    assert len(result["lead_reports"]) == 1

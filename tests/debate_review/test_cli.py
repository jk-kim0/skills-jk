import json
import sys
import pytest
from debate_review.state import create_initial_state, save_state, load_state
from debate_review.round_ops import init_round
from debate_review.cli import main


@pytest.fixture
def state_path(tmp_path):
    """Create a state file with round 1 initialized."""
    state = create_initial_state(
        repo="owner/repo", repo_root="/tmp/repo", pr_number=123,
        is_fork=False, head_sha="abc123", pr_branch_name="feat/test",
    )
    init_round(state, round_num=1, lead_agent="codex", synced_head_sha="abc123")
    path = str(tmp_path / "test-state.json")
    save_state(state, path)
    return path


def _run_cli(monkeypatch, args):
    """Run CLI main() with given args."""
    monkeypatch.setattr(sys, "argv", ["debate-review"] + args)
    try:
        main()
    except SystemExit:
        pass


# Test 1: Full flow — upsert → record-verdict → cross-verify → record-application → settle
def test_cli_full_round_flow(monkeypatch, capsys, state_path):
    # Step 1: upsert an issue
    _run_cli(monkeypatch, [
        "upsert-issue", "--state-file", state_path,
        "--agent", "codex", "--round", "1",
        "--severity", "critical", "--criterion", "1",
        "--file", "src/a.py", "--line", "10",
        "--anchor", "validate_input",
        "--message", "Missing input validation",
    ])
    out = capsys.readouterr().out
    result = json.loads(out)
    assert result["action"] == "created"
    issue_id = result["issue_id"]

    # Verify state was saved
    state = load_state(state_path)
    assert issue_id in state["issues"]

    # Step 2: record verdict
    _run_cli(monkeypatch, [
        "record-verdict", "--state-file", state_path,
        "--round", "1", "--verdict", "has_findings",
    ])
    out = capsys.readouterr().out
    result = json.loads(out)
    assert result["verdict"] == "has_findings"

    # Step 3: cross-verify — accept the issue
    state = load_state(state_path)
    report_id = state["issues"][issue_id]["reports"][0]["report_id"]
    verifications = json.dumps([{"report_id": report_id, "decision": "accept", "reason": "Valid"}])
    _run_cli(monkeypatch, [
        "record-cross-verification", "--state-file", state_path,
        "--round", "1", "--verifications", verifications,
    ])
    out = capsys.readouterr().out
    result = json.loads(out)
    assert result["processed"] == 1

    # Verify consensus reached for the issue
    state = load_state(state_path)
    assert state["issues"][issue_id]["consensus_status"] == "accepted"

    # Step 4: record-application phase 1
    _run_cli(monkeypatch, [
        "record-application", "--state-file", state_path,
        "--round", "1",
        "--applied-issues", json.dumps([issue_id]),
        "--failed-issues", json.dumps([]),
    ])
    out = capsys.readouterr().out
    result = json.loads(out)
    assert result["phase"] == 1

    # Phase 2
    _run_cli(monkeypatch, [
        "record-application", "--state-file", state_path,
        "--round", "1", "--commit-sha", "deadbeef",
    ])
    out = capsys.readouterr().out
    result = json.loads(out)
    assert result["phase"] == 2

    # Phase 3
    _run_cli(monkeypatch, [
        "record-application", "--state-file", state_path,
        "--round", "1", "--verify-push",
    ])
    out = capsys.readouterr().out
    result = json.loads(out)
    assert result["phase"] == 3

    # Step 5: settle round
    _run_cli(monkeypatch, [
        "settle-round", "--state-file", state_path,
        "--round", "1",
    ])
    out = capsys.readouterr().out
    result = json.loads(out)
    assert result["result"] == "continue"
    assert result["next_round"] == 2


# Test 2: show --json outputs valid JSON
def test_cli_show_json(monkeypatch, capsys, state_path):
    _run_cli(monkeypatch, ["show", "--state-file", state_path, "--json"])
    out = capsys.readouterr().out
    state = json.loads(out)
    assert state["repo"] == "owner/repo"
    assert state["pr_number"] == 123


# Test 3: show without --json outputs human-readable text
def test_cli_show_text(monkeypatch, capsys, state_path):
    _run_cli(monkeypatch, ["show", "--state-file", state_path])
    out = capsys.readouterr().out
    assert "owner/repo" in out
    assert "#123" in out


# Test 4: post-comment --no-comment outputs body without posting
def test_cli_post_comment_no_comment(monkeypatch, capsys, state_path):
    # Set up terminal state
    state = load_state(state_path)
    state["status"] = "consensus_reached"
    state["final_outcome"] = "consensus"
    state["current_round"] = 1
    save_state(state, state_path)

    _run_cli(monkeypatch, ["post-comment", "--state-file", state_path, "--no-comment"])
    out = capsys.readouterr().out
    result = json.loads(out)
    assert result["action"] == "dry_run"
    assert "[debate-review]" in result["body"]


# Test 5: resolve-rebuttals via CLI
def test_cli_resolve_rebuttals(monkeypatch, capsys, state_path):
    # First upsert an issue
    _run_cli(monkeypatch, [
        "upsert-issue", "--state-file", state_path,
        "--agent", "codex", "--round", "1",
        "--severity", "warning", "--criterion", "7",
        "--file", "src/c.py", "--line", "5",
        "--anchor", "MAX_RETRIES",
        "--message", "Hardcoded retry count",
    ])
    capsys.readouterr()  # consume output

    state = load_state(state_path)
    report_id = list(state["issues"].values())[0]["reports"][0]["report_id"]

    decisions = json.dumps([{"report_id": report_id, "decision": "withdraw", "reason": "OK"}])
    _run_cli(monkeypatch, [
        "resolve-rebuttals", "--state-file", state_path,
        "--round", "1", "--step", "1a", "--decisions", decisions,
    ])
    out = capsys.readouterr().out
    result = json.loads(out)
    assert result["processed"] == 1

    state = load_state(state_path)
    issue = list(state["issues"].values())[0]
    assert issue["consensus_status"] == "withdrawn"


# Test 6: Error on missing state file exits with code 1
def test_cli_missing_state_file(monkeypatch, capsys, tmp_path):
    fake_path = str(tmp_path / "nonexistent.json")
    monkeypatch.setattr(sys, "argv", ["debate-review", "upsert-issue", "--state-file", fake_path,
        "--agent", "cc", "--round", "1", "--severity", "critical",
        "--criterion", "1", "--file", "a.py", "--line", "1",
        "--anchor", "x", "--message", "test"])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1
    out = capsys.readouterr().out
    result = json.loads(out)
    assert "error" in result


# Test 7: init-round subcommand
def test_cli_init_round(monkeypatch, capsys, tmp_path):
    """init-round creates a round in a fresh state (no manual init_round needed)."""
    state = create_initial_state(
        repo="owner/repo", repo_root="/tmp/repo", pr_number=123,
        is_fork=False, head_sha="abc123", pr_branch_name="feat/test",
    )
    path = str(tmp_path / "fresh-state.json")
    save_state(state, path)

    _run_cli(monkeypatch, [
        "init-round", "--state-file", path,
        "--round", "1", "--lead-agent", "codex", "--synced-head-sha", "abc123",
    ])
    out = capsys.readouterr().out
    result = json.loads(out)
    assert result["round"] == 1
    assert result["lead_agent"] == "codex"

    reloaded = load_state(path)
    assert len(reloaded["rounds"]) == 1
    assert reloaded["rounds"][0]["lead_agent"] == "codex"
    assert reloaded["journal"]["step"] == "step0_sync"


# Test 8: journal.step updated by subcommands
def test_cli_journal_step_progression(monkeypatch, capsys, state_path):
    """CLI subcommands should update journal.step as they execute."""
    # upsert-issue sets step1_lead_review
    _run_cli(monkeypatch, [
        "upsert-issue", "--state-file", state_path,
        "--agent", "codex", "--round", "1",
        "--severity", "warning", "--criterion", "7",
        "--file", "src/c.py", "--line", "5",
        "--anchor", "MAX", "--message", "Hardcoded",
    ])
    capsys.readouterr()
    state = load_state(state_path)
    assert state["journal"]["step"] == "step1_lead_review"

    # record-verdict stays step1_lead_review
    _run_cli(monkeypatch, [
        "record-verdict", "--state-file", state_path,
        "--round", "1", "--verdict", "has_findings",
    ])
    capsys.readouterr()
    state = load_state(state_path)
    assert state["journal"]["step"] == "step1_lead_review"

    # settle-round sets step4_settle
    _run_cli(monkeypatch, [
        "settle-round", "--state-file", state_path,
        "--round", "1",
    ])
    capsys.readouterr()
    state = load_state(state_path)
    assert state["journal"]["step"] == "step4_settle"


# Test 9: Invalid JSON in --verifications
def test_cli_invalid_json_verifications(monkeypatch, capsys, state_path):
    _run_cli(monkeypatch, [
        "record-cross-verification", "--state-file", state_path,
        "--round", "1", "--verifications", "not-json",
    ])
    out = capsys.readouterr().out
    result = json.loads(out)
    assert "error" in result

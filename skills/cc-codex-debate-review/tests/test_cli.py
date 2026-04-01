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
    monkeypatch.setattr(
        "debate_review.application._get_pr_head_sha",
        lambda repo, pr_number: "deadbeef",
    )
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


def test_cli_build_commit_message_with_explicit_applied_issues(monkeypatch, capsys, state_path):
    _run_cli(monkeypatch, [
        "upsert-issue", "--state-file", state_path,
        "--agent", "codex", "--round", "1",
        "--severity", "critical", "--criterion", "1",
        "--file", "src/a.py", "--line", "10",
        "--anchor", "validate_input",
        "--message", "Missing input validation",
    ])
    out = capsys.readouterr().out
    issue_id = json.loads(out)["issue_id"]

    _run_cli(monkeypatch, [
        "build-commit-message", "--state-file", state_path,
        "--round", "1",
        "--applied-issues", json.dumps([issue_id]),
    ])
    out = capsys.readouterr().out
    assert "fix: apply debate review findings (round 1)" in out
    assert issue_id in out
    assert "Missing input validation" in out


def test_cli_build_commit_message_rejects_unknown_issue_ids(monkeypatch, capsys, state_path):
    monkeypatch.setattr(sys, "argv", [
        "debate-review",
        "build-commit-message",
        "--state-file", state_path,
        "--round", "1",
        "--applied-issues", json.dumps(["isu_missing"]),
    ])

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1
    out = capsys.readouterr().out
    result = json.loads(out)
    assert result["error"] == "Unknown issue IDs: ['isu_missing']"


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
    assert result["cross_verifier"] == "cc"
    assert result["worktree_path"] == "/tmp/repo/.worktrees/debate-pr-123"
    assert result["head_branch"] == "feat/test"
    assert result["synced_head_sha"] == "abc123"

    reloaded = load_state(path)
    assert len(reloaded["rounds"]) == 1
    assert reloaded["rounds"][0]["lead_agent"] == "codex"
    assert reloaded["journal"]["step"] == "step0_sync"


def test_cli_init_round_auto_lead_agent(monkeypatch, capsys, tmp_path):
    """init-round without --lead-agent auto-determines from round number."""
    state = create_initial_state(
        repo="owner/repo", repo_root="/tmp/repo", pr_number=42,
        is_fork=False, head_sha="abc123", pr_branch_name="feat/auto",
    )
    path = str(tmp_path / "auto-lead.json")
    save_state(state, path)

    # Odd round → codex
    _run_cli(monkeypatch, [
        "init-round", "--state-file", path,
        "--round", "1", "--synced-head-sha", "abc123",
    ])
    result = json.loads(capsys.readouterr().out)
    assert result["lead_agent"] == "codex"
    assert result["cross_verifier"] == "cc"

    # Even round → cc
    _run_cli(monkeypatch, [
        "init-round", "--state-file", path,
        "--round", "2", "--synced-head-sha", "abc123",
    ])
    result = json.loads(capsys.readouterr().out)
    assert result["lead_agent"] == "cc"
    assert result["cross_verifier"] == "codex"


def test_cli_init_round_dry_run_includes_round_metadata(monkeypatch, capsys, tmp_path):
    """init-round in dry-run mode returns full metadata (cross_verifier, worktree_path, etc.)."""
    state = create_initial_state(
        repo="owner/repo", repo_root="/tmp/repo", pr_number=99,
        is_fork=False, head_sha="abc123", pr_branch_name="feat/dry",
        dry_run=True,
    )
    path = str(tmp_path / "dry-run-init-round.json")
    save_state(state, path)

    _run_cli(monkeypatch, [
        "init-round", "--state-file", path,
        "--round", "1", "--synced-head-sha", "abc123",
    ])
    result = json.loads(capsys.readouterr().out)
    assert result["action"] == "dry_run"
    assert result["lead_agent"] == "codex"
    assert result["cross_verifier"] == "cc"
    assert result["worktree_path"] == "/tmp/repo/.worktrees/debate-pr-99"
    assert result["head_branch"] == "feat/dry"
    assert result["synced_head_sha"] == "abc123"


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

    state = load_state(state_path)
    report_id = list(state["issues"].values())[0]["reports"][0]["report_id"]
    verifications = json.dumps([{"report_id": report_id, "decision": "accept", "reason": "Valid"}])
    _run_cli(monkeypatch, [
        "record-cross-verification", "--state-file", state_path,
        "--round", "1", "--verifications", verifications,
    ])
    capsys.readouterr()
    state = load_state(state_path)
    assert state["journal"]["step"] == "step2_cross_review"

    # settle-round sets step4_settle
    _run_cli(monkeypatch, [
        "settle-round", "--state-file", state_path,
        "--round", "1",
    ])
    capsys.readouterr()
    state = load_state(state_path)
    assert state["journal"]["step"] == "step4_settle"


# Test 9: ValueError from business logic produces JSON error + exit 1
def test_cli_valueerror_json_exit(monkeypatch, capsys, state_path):
    """Business logic ValueError should produce JSON error, exit 1."""
    # record-verdict with no_findings_mergeable but open issues exist
    _run_cli(monkeypatch, [
        "upsert-issue", "--state-file", state_path,
        "--agent", "codex", "--round", "1",
        "--severity", "critical", "--criterion", "1",
        "--file", "src/a.py", "--line", "1",
        "--anchor", "x", "--message", "test",
    ])
    capsys.readouterr()

    monkeypatch.setattr(sys, "argv", ["debate-review",
        "record-verdict", "--state-file", state_path,
        "--round", "1", "--verdict", "no_findings_mergeable",
    ])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1
    out = capsys.readouterr().out
    result = json.loads(out)
    assert "error" in result
    assert "open issue" in result["error"]
    assert "error_log" not in result


def test_cli_mark_failed_saves_error_log(monkeypatch, capsys, state_path, tmp_path):
    """mark-failed should save an error log and return error_log path."""
    calls = []

    def fake_save_error_log(*, command, error_message, state_file=None):
        calls.append({
            "command": command,
            "error_message": error_message,
            "state_file": state_file,
        })
        return str(tmp_path / "error-log.json")

    monkeypatch.setattr("debate_review.cli.save_error_log", fake_save_error_log)
    _run_cli(monkeypatch, [
        "mark-failed", "--state-file", state_path,
        "--error-message", "git push failed",
        "--failed-command", "git push",
    ])
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "failed"
    assert result["error_message"] == "git push failed"
    assert result["error_log"] == str(tmp_path / "error-log.json")
    assert calls == [{
        "command": "git push",
        "error_message": "git push failed",
        "state_file": state_path,
    }]


def test_cli_mark_failed_without_failed_command(monkeypatch, capsys, state_path, tmp_path):
    """mark-failed without --failed-command defaults to 'unknown'."""
    calls = []

    def fake_save_error_log(*, command, error_message, state_file=None):
        calls.append(command)
        return str(tmp_path / "error-log.json")

    monkeypatch.setattr("debate_review.cli.save_error_log", fake_save_error_log)
    _run_cli(monkeypatch, [
        "mark-failed", "--state-file", state_path,
        "--error-message", "something broke",
    ])
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "failed"
    assert "error_log" in result
    assert calls == ["unknown"]


# Test 10: Invalid JSON in --verifications
def test_cli_invalid_json_verifications(monkeypatch, capsys, state_path):
    _run_cli(monkeypatch, [
        "record-cross-verification", "--state-file", state_path,
        "--round", "1", "--verifications", "not-json",
    ])
    out = capsys.readouterr().out
    result = json.loads(out)
    assert "error" in result


def test_cli_record_application_verify_push_mismatch_exits(monkeypatch, capsys, state_path):
    _run_cli(monkeypatch, [
        "upsert-issue", "--state-file", state_path,
        "--agent", "codex", "--round", "1",
        "--severity", "critical", "--criterion", "1",
        "--file", "src/a.py", "--line", "10",
        "--anchor", "validate_input",
        "--message", "Missing input validation",
    ])
    issue_id = json.loads(capsys.readouterr().out)["issue_id"]

    _run_cli(monkeypatch, [
        "record-application", "--state-file", state_path,
        "--round", "1",
        "--applied-issues", json.dumps([issue_id]),
        "--failed-issues", json.dumps([]),
    ])
    capsys.readouterr()
    _run_cli(monkeypatch, [
        "record-application", "--state-file", state_path,
        "--round", "1", "--commit-sha", "deadbeef",
    ])
    capsys.readouterr()

    monkeypatch.setattr(
        "debate_review.application._get_pr_head_sha",
        lambda repo, pr_number: "different-sha",
    )
    monkeypatch.setattr(sys, "argv", [
        "debate-review",
        "record-application", "--state-file", state_path,
        "--round", "1", "--verify-push",
    ])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1
    result = json.loads(capsys.readouterr().out)
    assert "match commit_sha" in result["error"]


def test_cli_dry_run_skips_mutating_commands(monkeypatch, capsys, tmp_path):
    state = create_initial_state(
        repo="owner/repo", repo_root="/tmp/repo", pr_number=123,
        is_fork=False, head_sha="abc123", pr_branch_name="feat/test",
        dry_run=True,
    )
    init_round(state, round_num=1, lead_agent="codex", synced_head_sha="abc123")
    path = str(tmp_path / "dry-run-state.json")
    save_state(state, path)

    before = load_state(path)
    _run_cli(monkeypatch, [
        "upsert-issue", "--state-file", path,
        "--agent", "codex", "--round", "1",
        "--severity", "warning", "--criterion", "7",
        "--file", "src/c.py", "--line", "5",
        "--anchor", "MAX", "--message", "Hardcoded",
    ])
    result = json.loads(capsys.readouterr().out)
    assert result["action"] == "dry_run"

    after = load_state(path)
    assert after == before


def test_cli_init_persists_language_from_config(monkeypatch, capsys, tmp_path):
    config_path = tmp_path / "config.yml"
    config_path.write_text("max_rounds: 7\nlanguage: ko\n")
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(
        "debate_review.cli.gh_json",
        lambda *args: {
            "headRefName": "feat/test",
            "headRefOid": "abc123",
            "headRepositoryOwner": {"login": "owner"},
        },
    )

    _run_cli(monkeypatch, [
        "init", "--repo", "owner/repo", "--pr", "123",
        "--config", str(config_path),
    ])
    result = json.loads(capsys.readouterr().out)
    assert result["language"] == "ko"
    assert result["codex_sandbox"] == "danger-full-access"
    assert result["agent_mode"] == "legacy"
    state = load_state(result["state_file"])
    assert state["language"] == "ko"
    assert state["max_rounds"] == 7


def test_cli_init_agent_mode_from_config(monkeypatch, capsys, tmp_path):
    config_path = tmp_path / "config.yml"
    config_path.write_text("agent_mode: persistent\n")
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(
        "debate_review.cli.gh_json",
        lambda *args: {
            "headRefName": "feat/test",
            "headRefOid": "abc123",
            "headRepositoryOwner": {"login": "owner"},
        },
    )

    _run_cli(monkeypatch, [
        "init", "--repo", "owner/repo", "--pr", "456",
        "--config", str(config_path),
    ])
    result = json.loads(capsys.readouterr().out)
    assert result["agent_mode"] == "persistent"


def test_cli_init_rejects_invalid_agent_mode(monkeypatch, capsys, tmp_path):
    config_path = tmp_path / "config.yml"
    config_path.write_text("agent_mode: invalid\n")
    monkeypatch.setattr(
        "debate_review.cli.gh_json",
        lambda *args: {
            "headRefName": "feat/test",
            "headRefOid": "abc123",
            "headRepositoryOwner": {"login": "owner"},
        },
    )
    monkeypatch.setattr(sys, "argv", [
        "debate-review",
        "init",
        "--repo", "owner/repo",
        "--pr", "456",
        "--config", str(config_path),
    ])

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1
    result = json.loads(capsys.readouterr().out)
    assert result["error"] == "Invalid agent_mode: invalid. Expected one of: legacy, persistent"


def test_cli_init_resumed_session_preserves_state_agent_mode(monkeypatch, capsys, tmp_path):
    config_path = tmp_path / "config.yml"
    config_path.write_text("agent_mode: legacy\n")
    state = create_initial_state(
        repo="owner/repo",
        repo_root="/tmp/repo",
        pr_number=789,
        is_fork=False,
        head_sha="abc123",
        pr_branch_name="feat/test",
        agent_mode="persistent",
    )
    path = tmp_path / "existing-state.json"
    save_state(state, str(path))

    monkeypatch.setattr("debate_review.cli.state_file_path", lambda *args: str(path))
    monkeypatch.setattr(
        "debate_review.cli.gh_json",
        lambda *args: {
            "headRefName": "feat/test",
            "headRefOid": "abc123",
            "headRepositoryOwner": {"login": "owner"},
        },
    )

    _run_cli(monkeypatch, [
        "init", "--repo", "owner/repo", "--pr", "789",
        "--config", str(config_path),
    ])
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "resumed"
    assert result["agent_mode"] == "persistent"
    assert load_state(str(path))["agent_mode"] == "persistent"


def test_cli_init_resumed_session_ignores_invalid_config_agent_mode(monkeypatch, capsys, tmp_path):
    config_path = tmp_path / "config.yml"
    config_path.write_text("agent_mode: invalid\n")
    state = create_initial_state(
        repo="owner/repo",
        repo_root="/tmp/repo",
        pr_number=790,
        is_fork=False,
        head_sha="abc123",
        pr_branch_name="feat/test",
        agent_mode="persistent",
    )
    path = tmp_path / "existing-state.json"
    save_state(state, str(path))

    monkeypatch.setattr("debate_review.cli.state_file_path", lambda *args: str(path))
    monkeypatch.setattr(
        "debate_review.cli.gh_json",
        lambda *args: {
            "headRefName": "feat/test",
            "headRefOid": "abc123",
            "headRepositoryOwner": {"login": "owner"},
        },
    )

    _run_cli(monkeypatch, [
        "init", "--repo", "owner/repo", "--pr", "790",
        "--config", str(config_path),
    ])
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "resumed"
    assert result["agent_mode"] == "persistent"
    assert load_state(str(path))["agent_mode"] == "persistent"


def test_cli_mark_failed(monkeypatch, capsys, state_path):
    _run_cli(monkeypatch, [
        "mark-failed", "--state-file", state_path,
        "--error-message", "Codex parse failure",
    ])
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "failed"
    state = load_state(state_path)
    assert state["status"] == "failed"
    assert state["final_outcome"] == "error"
    assert state["error_message"] == "Codex parse failure"


def test_cli_append_ledger(monkeypatch, capsys, state_path):
    entries = json.dumps([
        {"issue_id": "isu_001", "status": "accepted", "summary": "fix applied", "round": 1},
    ])
    _run_cli(monkeypatch, [
        "append-ledger", "--state-file", state_path,
        "--entries", entries,
    ])
    result = json.loads(capsys.readouterr().out)
    assert result["added"] == 1
    state = load_state(state_path)
    assert len(state["debate_ledger"]) == 1
    assert state["debate_ledger"][0]["issue_id"] == "isu_001"


def test_cli_record_application_warns_all_failed(monkeypatch, capsys, state_path):
    """record-application with applied=[] and failed=[...] should emit stderr warning."""
    _run_cli(monkeypatch, [
        "upsert-issue", "--state-file", state_path,
        "--agent", "codex", "--round", "1",
        "--severity", "critical", "--criterion", "1",
        "--file", "src/a.py", "--line", "10",
        "--anchor", "validate_input",
        "--message", "Missing input validation",
    ])
    issue_id = json.loads(capsys.readouterr().out)["issue_id"]

    _run_cli(monkeypatch, [
        "record-application", "--state-file", state_path,
        "--round", "1",
        "--applied-issues", json.dumps([]),
        "--failed-issues", json.dumps([issue_id]),
    ])
    captured = capsys.readouterr()
    result = json.loads(captured.out)
    assert result["phase"] == 1
    assert result["applied"] == 0
    assert result["failed"] == 1
    assert "WARNING" in captured.err
    assert "applied=0" in captured.err


def test_cli_record_application_accepts_failed_issue_objects(monkeypatch, capsys, state_path):
    _run_cli(monkeypatch, [
        "upsert-issue", "--state-file", state_path,
        "--agent", "codex", "--round", "1",
        "--severity", "critical", "--criterion", "1",
        "--file", "src/a.py", "--line", "10",
        "--anchor", "validate_input",
        "--message", "Missing input validation",
    ])
    issue_id = json.loads(capsys.readouterr().out)["issue_id"]
    report_id = load_state(state_path)["issues"][issue_id]["reports"][0]["report_id"]

    _run_cli(monkeypatch, [
        "record-cross-verification", "--state-file", state_path,
        "--round", "1",
        "--verifications", json.dumps([
            {"report_id": report_id, "decision": "accept", "reason": "Valid"},
        ]),
    ])
    capsys.readouterr()

    _run_cli(monkeypatch, [
        "record-application", "--state-file", state_path,
        "--round", "1",
        "--applied-issues", json.dumps([]),
        "--failed-issues", json.dumps([
            {"issue_id": issue_id, "reason": "Could not determine the correct fix"},
        ]),
    ])
    result = json.loads(capsys.readouterr().out)

    assert result["phase"] == 1
    assert result["failed"] == 1
    state = load_state(state_path)
    assert state["issues"][issue_id]["application_status"] == "failed"


def test_cli_test_error_exits_with_json_error(monkeypatch, capsys):
    """test-error should raise RuntimeError → _error_exit → JSON error + exit 1."""
    monkeypatch.setattr(sys, "argv", ["debate-review", "test-error"])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1
    out = capsys.readouterr().out
    result = json.loads(out)
    assert "error" in result
    assert "Intentional test error" in result["error"]


def test_cli_test_error_custom_message(monkeypatch, capsys):
    """test-error --message should use the custom message."""
    monkeypatch.setattr(sys, "argv", [
        "debate-review", "test-error", "--message", "custom failure"
    ])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1
    out = capsys.readouterr().out
    result = json.loads(out)
    assert result["error"] == "custom failure"

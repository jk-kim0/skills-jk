import json
import os

import pytest

from debate_review.state import (
    append_ledger,
    create_initial_state,
    determine_next_step,
    load_state,
    mark_failed,
    save_state,
    state_file_path,
)


def test_create_initial_state_has_required_fields(sample_state):
    required_top_level = [
        "repo", "repo_root", "pr_number", "is_fork", "dry_run",
        "max_rounds", "language", "status", "current_round", "head", "journal",
        "issues", "rounds", "final_comment_tag", "final_comment_id",
        "started_at", "finished_at", "final_outcome",
    ]
    for field in required_top_level:
        assert field in sample_state, f"Missing field: {field}"

    head = sample_state["head"]
    required_head = [
        "initial_sha", "last_observed_pr_sha", "terminal_sha",
        "pr_branch_name", "target_ref", "synced_worktree_sha",
    ]
    for field in required_head:
        assert field in head, f"Missing head field: {field}"

    journal = sample_state["journal"]
    required_journal = [
        "round", "step", "pre_sync_head_sha", "post_sync_head_sha",
        "synced_worktree_sha", "applied_issue_ids",
        "failed_application_issue_ids", "commit_sha",
        "push_verified", "state_persisted",
    ]
    for field in required_journal:
        assert field in journal, f"Missing journal field: {field}"


def test_create_initial_state_values(sample_state):
    assert sample_state["repo"] == "owner/repo"
    assert sample_state["pr_number"] == 123
    assert sample_state["is_fork"] is False
    assert sample_state["dry_run"] is False
    assert sample_state["max_rounds"] == 10
    assert sample_state["language"] == "en"
    assert sample_state["status"] == "in_progress"
    assert sample_state["current_round"] == 1
    assert sample_state["head"]["initial_sha"] == "abc1234def5678"
    assert sample_state["head"]["last_observed_pr_sha"] == "abc1234def5678"
    assert sample_state["head"]["pr_branch_name"] == "feat/test"
    assert sample_state["head"]["target_ref"] == "refs/debate-sync/pr-123/head"
    assert sample_state["journal"]["round"] == 1
    assert sample_state["journal"]["step"] == "init"
    assert sample_state["journal"]["state_persisted"] is True


def test_save_and_load_roundtrip(sample_state, tmp_path):
    path = str(tmp_path / "state.json")
    save_state(sample_state, path)
    loaded = load_state(path)
    assert loaded == sample_state


def test_load_nonexistent_returns_none(tmp_path):
    path = str(tmp_path / "nonexistent.json")
    result = load_state(path)
    assert result is None


def test_state_file_path_normal():
    path = state_file_path("owner/repo", 42)
    assert path.endswith("owner-repo-42.json")
    assert ".dry-run" not in path
    assert os.path.expanduser("~/.claude/debate-state") in path


def test_state_file_path_dry_run():
    path = state_file_path("owner/repo", 42, dry_run=True)
    assert path.endswith("owner-repo-42.dry-run.json")


def test_mark_failed(sample_state):
    mark_failed(sample_state, error_message="Something broke")
    assert sample_state["status"] == "failed"
    assert sample_state["final_outcome"] == "error"
    assert sample_state["error_message"] == "Something broke"
    assert sample_state["finished_at"] is not None
    assert sample_state["head"]["terminal_sha"] == sample_state["head"]["last_observed_pr_sha"]
    assert sample_state["journal"]["state_persisted"] is True


def test_append_ledger_adds_entries(sample_state):
    entries = [
        {"issue_id": "isu_001", "status": "accepted", "summary": "fix applied", "round": 1},
        {"issue_id": "isu_002", "status": "withdrawn", "reason": "intentional", "summary": "dropped", "round": 1},
    ]
    result = append_ledger(sample_state, entries=entries)
    assert result["added"] == 2
    assert result["total"] == 2
    assert len(sample_state["debate_ledger"]) == 2


def test_append_ledger_deduplicates(sample_state):
    entry = {"issue_id": "isu_001", "status": "accepted", "summary": "fix", "round": 1}
    append_ledger(sample_state, entries=[entry])
    result = append_ledger(sample_state, entries=[entry])
    assert result["added"] == 0
    assert result["total"] == 1


def test_append_ledger_allows_same_issue_different_round(sample_state):
    e1 = {"issue_id": "isu_001", "status": "withdrawn", "reason": "old", "summary": "v1", "round": 1}
    e2 = {"issue_id": "isu_001", "status": "accepted", "summary": "v2", "round": 3}
    append_ledger(sample_state, entries=[e1])
    result = append_ledger(sample_state, entries=[e2])
    assert result["added"] == 1
    assert result["total"] == 2


def test_load_config_default_reads_bundled_config(monkeypatch):
    """load_config should read the bundled config from the skill root."""
    from debate_review import config as config_module
    monkeypatch.setattr(config_module, "_USER_OVERRIDE_PATH", "/nonexistent/path.yml")
    result = config_module.load_config()
    assert result == {
        "max_rounds": 10,
        "codex_sandbox": "danger-full-access",
        "language": "en",
        "agent_mode": "legacy",
    }


def test_load_config_user_override(monkeypatch, tmp_path):
    """User override file should merge over defaults."""
    from debate_review import config as config_module
    override_file = tmp_path / "override.yml"
    override_file.write_text("language: ko\n")
    monkeypatch.setattr(config_module, "_USER_OVERRIDE_PATH", str(override_file))
    result = config_module.load_config()
    assert result["language"] == "ko"
    assert result["max_rounds"] == 10  # default preserved


def test_default_config_path_resolves_from_skill_root():
    from debate_review import config as config_module

    expected = os.path.abspath(
        os.path.join(
            os.path.dirname(config_module.__file__),
            "..",
            "..",
            "config.yml",
        )
    )

    assert os.path.abspath(config_module._DEFAULT_CONFIG_PATH) == expected


def test_load_config_missing_explicit_raises():
    """load_config should raise when explicit --config path doesn't exist."""
    from debate_review.config import load_config
    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/path/config.yml")


def test_load_config_malformed_yaml_override(monkeypatch, tmp_path):
    """Malformed YAML in override file should fall back to defaults."""
    from debate_review import config as config_module
    override_file = tmp_path / "bad.yml"
    override_file.write_text(": :\n  - :\n bad: [")
    monkeypatch.setattr(config_module, "_USER_OVERRIDE_PATH", str(override_file))
    result = config_module.load_config()
    assert result["max_rounds"] == 10
    assert result["language"] == "en"


def test_load_config_non_dict_yaml_override(monkeypatch, tmp_path):
    """Non-dict YAML in override file should fall back to defaults."""
    from debate_review import config as config_module
    override_file = tmp_path / "list.yml"
    override_file.write_text("- ko\n- en\n")
    monkeypatch.setattr(config_module, "_USER_OVERRIDE_PATH", str(override_file))
    result = config_module.load_config()
    assert result["max_rounds"] == 10
    assert result["language"] == "en"


# determine_next_step tests

def test_next_step_from_init(sample_state):
    result = determine_next_step(sample_state)
    assert result["next_step"] == "step0"


def test_next_step_from_step0(sample_state):
    sample_state["journal"]["step"] = "step0_sync"
    assert determine_next_step(sample_state)["next_step"] == "step1"


def test_next_step_from_step1_without_verdict(sample_state):
    """step1_lead_review with no verdict recorded → resume step1."""
    from debate_review.round_ops import init_round
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    sample_state["journal"]["step"] = "step1_lead_review"
    # No record_verdict called → verdict is None
    result = determine_next_step(sample_state)
    assert result["next_step"] == "step1"


def test_next_step_from_step1_has_findings(sample_state):
    """step1_lead_review with verdict recorded → step2."""
    from debate_review.round_ops import init_round, record_verdict
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    record_verdict(sample_state, round_num=1, verdict="has_findings")
    sample_state["journal"]["step"] = "step1_lead_review"
    result = determine_next_step(sample_state)
    assert result["next_step"] == "step2"
    assert result["resume_context"]["clean_pass"] is False


def test_next_step_from_step1_clean_pass(sample_state):
    from debate_review.round_ops import init_round, record_verdict
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    record_verdict(sample_state, round_num=1, verdict="no_findings_mergeable")
    sample_state["journal"]["step"] = "step1_lead_review"
    result = determine_next_step(sample_state)
    assert result["next_step"] == "step4"
    assert result["resume_context"]["clean_pass"] is True


def test_next_step_from_step2(sample_state):
    sample_state["journal"]["step"] = "step2_cross_review"
    assert determine_next_step(sample_state)["next_step"] == "step3"


def test_next_step_from_step3_phase1(sample_state):
    sample_state["journal"]["step"] = "step3_lead_apply"
    assert determine_next_step(sample_state)["next_step"] == "step3_phase1"


def test_next_step_from_step3_phase2(sample_state):
    sample_state["journal"]["step"] = "step3_lead_apply"
    sample_state["journal"]["phase1_completed"] = True
    sample_state["journal"]["applied_issue_ids"] = ["isu_001"]
    assert determine_next_step(sample_state)["next_step"] == "step3_phase2"


def test_next_step_from_step3_phase2_with_only_failed_issues(sample_state):
    """step3 with only failed_application_issue_ids (no applied) → step3_phase2."""
    sample_state["journal"]["step"] = "step3_lead_apply"
    sample_state["journal"]["phase1_completed"] = True
    sample_state["journal"]["failed_application_issue_ids"] = ["isu_002"]
    assert determine_next_step(sample_state)["next_step"] == "step3_phase2"


def test_next_step_from_step3_phase2_with_empty_lists(sample_state):
    """step3 with phase1_completed=True but empty applied/failed → step3_phase2."""
    sample_state["journal"]["step"] = "step3_lead_apply"
    sample_state["journal"]["phase1_completed"] = True
    assert determine_next_step(sample_state)["next_step"] == "step3_phase2"


def test_next_step_from_step3_push(sample_state):
    sample_state["journal"]["step"] = "step3_lead_apply"
    sample_state["journal"]["commit_sha"] = "deadbeef"
    result = determine_next_step(sample_state)
    assert result["next_step"] == "step3_push"
    assert result["resume_context"]["commit_sha"] == "deadbeef"


def test_next_step_from_step3_complete(sample_state):
    sample_state["journal"]["step"] = "step3_lead_apply"
    sample_state["journal"]["push_verified"] = True
    assert determine_next_step(sample_state)["next_step"] == "step4"


def test_next_step_from_step4(sample_state):
    sample_state["journal"]["step"] = "step4_settle"
    assert determine_next_step(sample_state)["next_step"] == "step0"

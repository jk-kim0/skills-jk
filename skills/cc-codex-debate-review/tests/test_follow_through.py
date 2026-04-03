"""Tests for follow_through module — operational automation after terminal state."""

import json
import os
import sys

from debate_review.state import create_initial_state, save_state
from debate_review.cli import main
from debate_review.follow_through import (
    create_failure_issue,
    update_pr_status,
    cleanup_worktree,
)


def _failed_state():
    state = create_initial_state(
        repo="owner/repo", repo_root="/tmp/repo", pr_number=42,
        is_fork=False, head_sha="abc1234def5678",
        pr_branch_name="feat/test", max_rounds=10,
    )
    state["status"] = "failed"
    state["final_outcome"] = "error"
    state["error_message"] = "Codex parse failure"
    state["journal"]["round"] = 2
    state["journal"]["step"] = "step2_cross_review"
    return state


def _consensus_state():
    state = create_initial_state(
        repo="owner/repo", repo_root="/tmp/repo", pr_number=42,
        is_fork=False, head_sha="abc1234def5678",
        pr_branch_name="feat/test", max_rounds=10,
    )
    state["status"] = "consensus_reached"
    state["final_outcome"] = "consensus"
    state["current_round"] = 3
    return state


def _max_rounds_state():
    state = create_initial_state(
        repo="owner/repo", repo_root="/tmp/repo", pr_number=42,
        is_fork=False, head_sha="abc1234def5678",
        pr_branch_name="feat/test", max_rounds=10,
    )
    state["status"] = "max_rounds_exceeded"
    state["final_outcome"] = "no_consensus"
    return state


def _stalled_state():
    state = create_initial_state(
        repo="owner/repo", repo_root="/tmp/repo", pr_number=42,
        is_fork=False, head_sha="abc1234def5678",
        pr_branch_name="feat/test", max_rounds=10,
    )
    state["status"] = "stalled"
    state["final_outcome"] = "stalled"
    state["error_message"] = "Stalled: 2 consecutive rounds with no progress"
    return state


# --- create_failure_issue ---

class TestCreateFailureIssue:
    def test_creates_github_issue(self):
        state = _failed_state()
        created = []

        def mock_gh(*args):
            created.append(args)
            return "https://github.com/owner/repo/issues/99\n"

        result = create_failure_issue(state, _gh=mock_gh)
        assert result["action"] == "created"
        assert "issues/99" in result["url"]
        args = created[0]
        assert "issue" in args
        assert "create" in args
        assert "--repo" in args
        assert "owner/repo" in args

    def test_includes_error_details_in_body(self):
        state = _failed_state()
        captured_args = []

        def mock_gh(*args):
            captured_args.append(args)
            return "https://github.com/owner/repo/issues/99"

        create_failure_issue(state, _gh=mock_gh)
        args = captured_args[0]
        body_idx = list(args).index("--body") + 1
        body = args[body_idx]
        assert "Codex parse failure" in body
        assert "#42" in body
        assert "step2_cross_review" in body

    def test_gh_failure_propagates(self):
        state = _failed_state()

        def mock_gh(*args):
            raise RuntimeError("gh: not authenticated")

        import pytest
        with pytest.raises(RuntimeError, match="not authenticated"):
            create_failure_issue(state, _gh=mock_gh)

    def test_dry_run_skips_creation(self):
        state = _failed_state()
        state["dry_run"] = True
        result = create_failure_issue(state)
        assert result["action"] == "dry_run"

    def test_non_failed_state_skips(self):
        state = _consensus_state()
        result = create_failure_issue(state)
        assert result["action"] == "skipped"
        assert "not failed" in result["reason"]

    def test_stalled_state_creates_issue(self):
        state = _stalled_state()
        created = []

        def mock_gh(*args):
            created.append(args)
            return "https://github.com/owner/repo/issues/100"

        result = create_failure_issue(state, _gh=mock_gh)
        assert result["action"] == "created"

    def test_title_contains_pr_number(self):
        state = _failed_state()
        captured_args = []

        def mock_gh(*args):
            captured_args.append(args)
            return "https://github.com/owner/repo/issues/99"

        create_failure_issue(state, _gh=mock_gh)
        args = captured_args[0]
        title_idx = list(args).index("--title") + 1
        title = args[title_idx]
        assert "#42" in title


# --- update_pr_status ---

class TestUpdatePrStatus:
    def _mock_gh_json_title(self, title="Fix stuff"):
        def mock(*args):
            return {"title": title}
        return mock

    def test_consensus_adds_label(self):
        state = _consensus_state()
        edited = []

        def mock_gh(*args):
            edited.append(args)
            return ""

        result = update_pr_status(state, _gh=mock_gh, _gh_json=self._mock_gh_json_title())
        assert result["action"] == "updated"
        assert result["label"] == "[debate: consensus]"
        args = edited[0]
        assert "pr" in args
        assert "edit" in args

    def test_failed_adds_label(self):
        state = _failed_state()
        edited = []

        def mock_gh(*args):
            edited.append(args)
            return ""

        result = update_pr_status(state, _gh=mock_gh, _gh_json=self._mock_gh_json_title())
        assert result["action"] == "updated"
        assert result["label"] == "[debate: failed]"

    def test_max_rounds_adds_label(self):
        state = _max_rounds_state()
        edited = []

        def mock_gh(*args):
            edited.append(args)
            return ""

        result = update_pr_status(state, _gh=mock_gh, _gh_json=self._mock_gh_json_title())
        assert result["action"] == "updated"
        assert result["label"] == "[debate: no consensus]"

    def test_stalled_adds_label(self):
        state = _stalled_state()
        edited = []

        def mock_gh(*args):
            edited.append(args)
            return ""

        result = update_pr_status(state, _gh=mock_gh, _gh_json=self._mock_gh_json_title())
        assert result["action"] == "updated"
        assert result["label"] == "[debate: stalled]"

    def test_in_progress_skips(self):
        state = create_initial_state(
            repo="owner/repo", repo_root="/tmp/repo", pr_number=42,
            is_fork=False, head_sha="abc1234def5678",
            pr_branch_name="feat/test", max_rounds=10,
        )
        result = update_pr_status(state)
        assert result["action"] == "skipped"
        assert "not terminal" in result["reason"]

    def test_dry_run_skips(self):
        state = _consensus_state()
        state["dry_run"] = True
        result = update_pr_status(state)
        assert result["action"] == "dry_run"

    def test_does_not_duplicate_label(self):
        """If title already has the label, skip."""
        state = _consensus_state()

        def mock_gh_json(*args):
            return {"title": "[debate: consensus] Fix stuff"}

        result = update_pr_status(state, _gh_json=mock_gh_json)
        assert result["action"] == "skipped"
        assert "already" in result["reason"]

    def test_edits_title_via_gh(self):
        state = _consensus_state()
        edited = []

        def mock_gh_json(*args):
            return {"title": "Fix stuff"}

        def mock_gh(*args):
            edited.append(args)
            return ""

        result = update_pr_status(state, _gh=mock_gh, _gh_json=mock_gh_json)
        assert result["action"] == "updated"
        args = edited[0]
        title_idx = list(args).index("--title") + 1
        assert args[title_idx] == "[debate: consensus] Fix stuff"

    def test_strips_old_label_before_adding_new(self):
        """If title already has a different debate label, strip it first."""
        state = _consensus_state()
        edited = []

        def mock_gh_json(*args):
            return {"title": "[debate: failed] Fix stuff"}

        def mock_gh(*args):
            edited.append(args)
            return ""

        result = update_pr_status(state, _gh=mock_gh, _gh_json=mock_gh_json)
        assert result["action"] == "updated"
        args = edited[0]
        title_idx = list(args).index("--title") + 1
        assert args[title_idx] == "[debate: consensus] Fix stuff"
        assert "[debate: failed]" not in args[title_idx]

    def test_gh_json_failure_returns_error(self):
        state = _consensus_state()

        def mock_gh_json(*args):
            raise RuntimeError("GraphQL: not found")

        result = update_pr_status(state, _gh_json=mock_gh_json)
        assert result["action"] == "error"
        assert "Failed to fetch PR title" in result["reason"]


# --- cleanup_worktree ---

class TestCleanupWorktree:
    def test_removes_existing_worktree(self, tmp_path):
        worktree_dir = tmp_path / ".worktrees" / "debate-pr-42"
        worktree_dir.mkdir(parents=True)
        (worktree_dir / "dummy.txt").write_text("test")

        state = create_initial_state(
            repo="owner/repo", repo_root=str(tmp_path), pr_number=42,
            is_fork=False, head_sha="abc1234def5678",
            pr_branch_name="feat/test", max_rounds=10,
        )

        removed = []

        def mock_run_git_worktree_remove(path):
            removed.append(path)

        result = cleanup_worktree(state, _remove_worktree=mock_run_git_worktree_remove)
        assert result["action"] == "removed"
        assert str(worktree_dir) in removed[0]

    def test_skips_if_not_exists(self, tmp_path):
        state = create_initial_state(
            repo="owner/repo", repo_root=str(tmp_path), pr_number=42,
            is_fork=False, head_sha="abc1234def5678",
            pr_branch_name="feat/test", max_rounds=10,
        )

        result = cleanup_worktree(state)
        assert result["action"] == "skipped"
        assert "not found" in result["reason"]

    def test_dry_run_skips(self, tmp_path):
        worktree_dir = tmp_path / ".worktrees" / "debate-pr-42"
        worktree_dir.mkdir(parents=True)

        state = create_initial_state(
            repo="owner/repo", repo_root=str(tmp_path), pr_number=42,
            is_fork=False, head_sha="abc1234def5678",
            pr_branch_name="feat/test", max_rounds=10,
        )
        state["dry_run"] = True

        result = cleanup_worktree(state)
        assert result["action"] == "dry_run"
        assert worktree_dir.exists()  # not actually removed

    def test_empty_repo_root_skips(self):
        state = create_initial_state(
            repo="owner/repo", repo_root="", pr_number=42,
            is_fork=False, head_sha="abc1234def5678",
            pr_branch_name="feat/test", max_rounds=10,
        )
        result = cleanup_worktree(state)
        assert result["action"] == "skipped"
        assert "repo_root" in result["reason"]

    def test_remove_failure_propagates(self, tmp_path):
        import pytest
        worktree_dir = tmp_path / ".worktrees" / "debate-pr-42"
        worktree_dir.mkdir(parents=True)

        state = create_initial_state(
            repo="owner/repo", repo_root=str(tmp_path), pr_number=42,
            is_fork=False, head_sha="abc1234def5678",
            pr_branch_name="feat/test", max_rounds=10,
        )

        def mock_remove_fail(path):
            raise RuntimeError("git worktree remove failed")

        with pytest.raises(RuntimeError, match="worktree remove failed"):
            cleanup_worktree(state, _remove_worktree=mock_remove_fail)


# --- CLI subcommand integration ---

def _run_cli(monkeypatch, args):
    monkeypatch.setattr(sys, "argv", ["debate-review"] + args)
    try:
        main()
    except SystemExit:
        pass


class TestCLIFollowThrough:
    def test_create_failure_issue_cli_dry_run(self, monkeypatch, capsys, tmp_path):
        state = _failed_state()
        state["dry_run"] = True
        path = str(tmp_path / "state.json")
        save_state(state, path)

        _run_cli(monkeypatch, ["create-failure-issue", "--state-file", path])
        out = json.loads(capsys.readouterr().out)
        assert out["action"] == "dry_run"

    def test_update_pr_status_cli_dry_run(self, monkeypatch, capsys, tmp_path):
        state = _consensus_state()
        state["dry_run"] = True
        path = str(tmp_path / "state.json")
        save_state(state, path)

        _run_cli(monkeypatch, ["update-pr-status", "--state-file", path])
        out = json.loads(capsys.readouterr().out)
        assert out["action"] == "dry_run"
        assert out["label"] == "[debate: consensus]"

    def test_cleanup_worktree_cli_not_exists(self, monkeypatch, capsys, tmp_path):
        state = create_initial_state(
            repo="owner/repo", repo_root=str(tmp_path), pr_number=42,
            is_fork=False, head_sha="abc1234def5678",
            pr_branch_name="feat/test", max_rounds=10,
        )
        path = str(tmp_path / "state.json")
        save_state(state, path)

        _run_cli(monkeypatch, ["cleanup-worktree", "--state-file", path])
        out = json.loads(capsys.readouterr().out)
        assert out["action"] == "skipped"

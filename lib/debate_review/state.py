import json
import os
import tempfile
from datetime import datetime, timezone


def create_initial_state(
    *,
    repo,
    repo_root,
    pr_number,
    is_fork,
    head_sha,
    pr_branch_name,
    max_rounds=10,
    dry_run=False,
) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "repo": repo,
        "repo_root": repo_root,
        "pr_number": pr_number,
        "is_fork": is_fork,
        "dry_run": dry_run,
        "max_rounds": max_rounds,
        "status": "in_progress",
        "current_round": 1,
        "head": {
            "initial_sha": head_sha,
            "last_observed_pr_sha": head_sha,
            "terminal_sha": None,
            "pr_branch_name": pr_branch_name,
            "target_ref": f"refs/debate-sync/pr-{pr_number}/head",
            "synced_worktree_sha": None,
        },
        "journal": {
            "round": 1,
            "step": "init",
            "pre_sync_head_sha": None,
            "post_sync_head_sha": None,
            "synced_worktree_sha": None,
            "applied_issue_ids": [],
            "failed_application_issue_ids": [],
            "commit_sha": None,
            "push_verified": False,
            "state_persisted": True,
        },
        "issues": {},
        "rounds": [],
        "final_comment_tag": None,
        "final_comment_id": None,
        "started_at": now,
        "finished_at": None,
        "final_outcome": None,
    }


def state_file_path(repo, pr_number, dry_run=False) -> str:
    owner_repo = repo.replace("/", "-")
    suffix = ".dry-run.json" if dry_run else ".json"
    filename = f"{owner_repo}-{pr_number}{suffix}"
    return os.path.expanduser(f"~/.claude/debate-state/{filename}")


def load_state(path) -> dict | None:
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def save_state(state, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    dir_ = os.path.dirname(path)
    with tempfile.NamedTemporaryFile("w", dir=dir_, delete=False, suffix=".tmp") as f:
        json.dump(state, f, indent=2)
        tmp_path = f.name
    os.replace(tmp_path, path)

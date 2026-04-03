"""Operational follow-through automation for terminal debate-review sessions."""

import os
import subprocess

from debate_review.gh import gh, gh_json


_OUTCOME_LABELS = {
    "consensus": "[debate: consensus]",
    "no_consensus": "[debate: no consensus]",
    "error": "[debate: failed]",
    "stalled": "[debate: stalled]",
}

_FAILURE_OUTCOMES = {"error", "stalled"}


def create_failure_issue(state, *, _gh=None) -> dict:
    """Create a GitHub issue when debate-review fails or stalls."""
    outcome = state.get("final_outcome")
    if outcome not in _FAILURE_OUTCOMES:
        return {"action": "skipped", "reason": "not failed"}

    if state.get("dry_run"):
        return {"action": "dry_run"}

    repo = state["repo"]
    pr_number = state["pr_number"]
    error_msg = state.get("error_message", "Unknown error")
    journal = state.get("journal", {})
    round_num = journal.get("round", "?")
    step = journal.get("step", "?")

    title = f"debate-review failed on PR #{pr_number}"
    body = (
        f"## debate-review failure\n\n"
        f"- **PR:** #{pr_number}\n"
        f"- **Outcome:** {outcome}\n"
        f"- **Round:** {round_num}\n"
        f"- **Step:** {step}\n"
        f"- **Error:** {error_msg}\n"
    )

    gh_fn = _gh or gh
    raw = gh_fn(
        "issue", "create",
        "--repo", repo,
        "--title", title,
        "--body", body,
        "--label", "debate-review",
    )

    import json
    try:
        data = json.loads(raw)
        url = data.get("url", "")
    except (json.JSONDecodeError, AttributeError):
        url = raw.strip()

    return {"action": "created", "url": url}


def update_pr_status(state, *, _gh=None, _gh_json=None) -> dict:
    """Add a debate result label to the PR title."""
    outcome = state.get("final_outcome")
    label = _OUTCOME_LABELS.get(outcome)
    if label is None:
        return {"action": "skipped", "reason": "not terminal"}

    if state.get("dry_run"):
        return {"action": "dry_run", "label": label}

    repo = state["repo"]
    pr_number = state["pr_number"]

    gh_json_fn = _gh_json or gh_json
    pr_data = gh_json_fn(
        "pr", "view", str(pr_number),
        "--repo", repo,
        "--json", "title",
    )
    current_title = pr_data.get("title", "")

    if label in current_title:
        return {"action": "skipped", "reason": "already labeled", "label": label}

    new_title = f"{label} {current_title}"
    gh_fn = _gh or gh
    gh_fn(
        "pr", "edit", str(pr_number),
        "--repo", repo,
        "--title", new_title,
    )

    return {"action": "updated", "label": label, "title": new_title}


def cleanup_worktree(state, *, _remove_worktree=None) -> dict:
    """Remove the debate worktree for this PR."""
    repo_root = state.get("repo_root", "")
    pr_number = state["pr_number"]
    worktree_path = os.path.join(repo_root, ".worktrees", f"debate-pr-{pr_number}")

    if not os.path.exists(worktree_path):
        return {"action": "skipped", "reason": "not found", "path": worktree_path}

    if state.get("dry_run"):
        return {"action": "dry_run", "path": worktree_path}

    def _default_remove(path):
        subprocess.run(
            ["git", "worktree", "remove", "--force", path],
            capture_output=True,
            text=True,
        )

    remove_fn = _remove_worktree or _default_remove
    remove_fn(worktree_path)

    return {"action": "removed", "path": worktree_path}

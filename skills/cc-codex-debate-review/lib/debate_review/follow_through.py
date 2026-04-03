"""Operational follow-through automation for terminal debate-review sessions."""

import json
import os
import re
import subprocess

from debate_review.gh import gh, gh_json


_OUTCOME_LABELS = {
    "consensus": "[debate: consensus]",
    "no_consensus": "[debate: no consensus]",
    "error": "[debate: failed]",
    "stalled": "[debate: stalled]",
}

_FAILURE_OUTCOMES = {"error", "stalled"}

_DEBATE_LABEL_RE = re.compile(r"\[debate: [^\]]+\]\s*")


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
    # gh issue create outputs a URL string, not JSON
    try:
        raw = gh_fn(
            "issue", "create",
            "--repo", repo,
            "--title", title,
            "--body", body,
            "--label", "debate-review",
        )
    except RuntimeError as e:
        return {"action": "error", "reason": f"Failed to create issue: {e}"}

    return {"action": "created", "url": raw.strip()}


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
    try:
        pr_data = gh_json_fn(
            "pr", "view", str(pr_number),
            "--repo", repo,
            "--json", "title",
        )
    except RuntimeError as e:
        return {"action": "error", "reason": f"Failed to fetch PR title: {e}"}

    current_title = pr_data.get("title", "")

    if label in current_title:
        return {"action": "skipped", "reason": "already labeled", "label": label}

    # Strip any existing debate label before adding the new one
    stripped_title = _DEBATE_LABEL_RE.sub("", current_title)
    new_title = f"{label} {stripped_title}"

    gh_fn = _gh or gh
    try:
        gh_fn(
            "pr", "edit", str(pr_number),
            "--repo", repo,
            "--title", new_title,
        )
    except RuntimeError as e:
        return {"action": "error", "reason": f"Failed to update PR title: {e}"}

    return {"action": "updated", "label": label, "title": new_title}


def cleanup_worktree(state, *, _remove_worktree=None) -> dict:
    """Remove the debate worktree for this PR."""
    repo_root = state.get("repo_root", "")
    if not repo_root:
        return {"action": "skipped", "reason": "repo_root not set"}

    pr_number = state["pr_number"]
    worktree_path = os.path.join(repo_root, ".worktrees", f"debate-pr-{pr_number}")

    if not os.path.exists(worktree_path):
        return {"action": "skipped", "reason": "not found", "path": worktree_path}

    if state.get("dry_run"):
        return {"action": "dry_run", "path": worktree_path}

    def _default_remove(path):
        result = subprocess.run(
            ["git", "worktree", "remove", "--force", path],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"git worktree remove failed (exit {result.returncode}): {result.stderr}"
            )

    remove_fn = _remove_worktree or _default_remove
    remove_fn(worktree_path)

    return {"action": "removed", "path": worktree_path}

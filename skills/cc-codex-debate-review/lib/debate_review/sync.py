"""sync-head: PR HEAD synchronization and supersede detection."""

import os
import subprocess

from debate_review.gh import gh_json
from debate_review.timing import record_step_timing, reset_step_timings


def _run_git(repo_root, *args):
    result = subprocess.run(
        ["git", "-C", repo_root, *args],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git failed: {result.stderr.strip()}")
    return result.stdout.strip()


def _get_pr_head_sha(repo, pr_number):
    data = gh_json("pr", "view", str(pr_number), "--repo", repo, "--json", "headRefOid")
    return data["headRefOid"]


def _ensure_worktree(repo_root, pr_number, target_ref):
    wt_path = os.path.join(repo_root, ".worktrees", f"debate-pr-{pr_number}")
    if not os.path.isdir(wt_path):
        _run_git(repo_root, "worktree", "add", "--detach", wt_path, target_ref)
    _run_git(wt_path, "reset", "--hard", target_ref)
    sha = _run_git(wt_path, "rev-parse", "HEAD")
    return wt_path, sha


def _reset_issues_for_supersede(state):
    for issue in state["issues"].values():
        cs = issue["consensus_status"]
        app = issue["application_status"]

        if cs == "accepted":
            issue["consensus_status"] = "open"
            issue["accepted_by"] = []
        elif cs == "open":
            issue["accepted_by"] = []
        # withdrawn stays withdrawn

        if app in ("applied", "failed", "recommended"):
            issue["application_status"] = "pending"
            if app == "applied":
                issue["applied_by"] = None
                issue["application_commit_sha"] = None
        # pending stays pending, not_applicable stays not_applicable


def sync_head(state, *, _get_head=None, _fetch=None, _ensure_wt=None) -> dict:
    """Sync PR HEAD to local worktree. Detect external changes."""
    repo = state["repo"]
    repo_root = state["repo_root"]
    pr_number = state["pr_number"]
    target_ref = state["head"]["target_ref"]
    journal = state["journal"]

    # Dry run: skip all git/gh operations
    if state.get("dry_run"):
        current_sha = state["head"]["last_observed_pr_sha"]
        return {
            "pre_sync_sha": current_sha,
            "post_sync_sha": current_sha,
            "external_change": False,
            "superseded_rounds": [],
            "dry_run": True,
        }

    # Step 1: Record pre-sync SHA
    pre_sync_sha = state["head"]["last_observed_pr_sha"]
    journal["pre_sync_head_sha"] = pre_sync_sha

    # Step 2: Get current PR HEAD
    get_head = _get_head or _get_pr_head_sha
    post_sync_sha = get_head(repo, pr_number)

    # Step 3: Fetch
    fetch = _fetch or (lambda rr, pn, tr: _run_git(rr, "fetch", "origin", f"pull/{pn}/head:{tr}"))
    fetch(repo_root, pr_number, target_ref)

    # Step 4-5: Worktree
    ensure_wt = _ensure_wt or _ensure_worktree
    wt_path, synced_sha = ensure_wt(repo_root, pr_number, target_ref)

    # Step 6: External change detection
    external_change = False
    superseded_rounds = []

    if pre_sync_sha != post_sync_sha:
        known_commit_shas = set()
        if journal.get("commit_sha"):
            known_commit_shas.add(journal["commit_sha"])
        for r in state["rounds"]:
            cs = r.get("step3", {}).get("commit_sha")
            if cs:
                known_commit_shas.add(cs)

        if post_sync_sha not in known_commit_shas:
            external_change = True
            for r in state["rounds"]:
                if r["status"] in ("active", "completed"):
                    r["status"] = "superseded"
                    superseded_rounds.append(r["round"])
            _reset_issues_for_supersede(state)
            # Preserve ledger entries for issues that remain withdrawn
            # (re-raise rule needs withdraw reasons); drop the rest
            withdrawn_ids = {
                iid for iid, issue in state["issues"].items()
                if issue.get("consensus_status") == "withdrawn"
            }
            state["debate_ledger"] = [
                e for e in state.get("debate_ledger", [])
                if e["issue_id"] in withdrawn_ids and e.get("status") == "withdrawn"
            ]
            state["current_round"] += 1
            # Reset journal for the new round
            journal["round"] = state["current_round"]
            journal["step"] = "step0_sync"
            reset_step_timings(state)
            record_step_timing(state, "step0_sync")
            journal["applied_issue_ids"] = []
            journal["failed_application_issue_ids"] = []
            journal["commit_sha"] = None
            journal["push_verified"] = False
            journal["state_persisted"] = True

    # Step 7: Update state
    state["head"]["last_observed_pr_sha"] = post_sync_sha
    journal["post_sync_head_sha"] = post_sync_sha
    state["head"]["synced_worktree_sha"] = synced_sha
    journal["synced_worktree_sha"] = synced_sha

    result = {
        "pre_sync_sha": pre_sync_sha,
        "post_sync_sha": post_sync_sha,
        "external_change": external_change,
        "superseded_rounds": superseded_rounds,
    }
    if external_change:
        result["next_round"] = state["current_round"]
    return result

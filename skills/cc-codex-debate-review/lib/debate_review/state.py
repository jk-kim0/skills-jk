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
    language="en",
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
        "language": language,
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
        "debate_ledger": [],
        "rounds": [],
        "final_comment_tag": None,
        "final_comment_id": None,
        "started_at": now,
        "finished_at": None,
        "final_outcome": None,
    }


def mark_failed(state, *, error_message="Unknown error"):
    """Mark state as terminal failed."""
    now = datetime.now(timezone.utc).isoformat()
    state["status"] = "failed"
    state["final_outcome"] = "error"
    state["finished_at"] = now
    state["error_message"] = error_message
    state["head"]["terminal_sha"] = state["head"]["last_observed_pr_sha"]
    state["journal"]["state_persisted"] = True


def append_ledger(state, *, entries):
    """Append settled issue entries to debate_ledger, deduplicating by (issue_id, status, round)."""
    ledger = state.setdefault("debate_ledger", [])
    existing = {(e["issue_id"], e["status"], e.get("round")) for e in ledger}
    added = 0
    for entry in entries:
        key = (entry["issue_id"], entry["status"], entry.get("round"))
        if key not in existing:
            ledger.append(entry)
            existing.add(key)
            added += 1
    return {"added": added, "total": len(ledger)}


def determine_next_step(state) -> dict:
    """Analyze journal to determine where to resume after restart."""
    journal = state["journal"]
    step = journal.get("step", "init")
    result = {"journal_step": step}

    if step == "init":
        result["next_step"] = "step0"
    elif step == "step0_sync":
        result["next_step"] = "step1"
    elif step == "step1_lead_review":
        current_round_num = journal.get("round", state["current_round"])
        round_data = None
        for r in state["rounds"]:
            if r["round"] == current_round_num:
                round_data = r
                break
        step1 = round_data.get("step1", {}) if round_data else {}
        verdict = step1.get("verdict")
        if verdict is None:
            result["next_step"] = "step1"
        elif round_data.get("clean_pass"):
            result["next_step"] = "step4"
            result["resume_context"] = {"clean_pass": True}
        else:
            result["next_step"] = "step2"
            result["resume_context"] = {"clean_pass": False}
    elif step == "step2_cross_review":
        result["next_step"] = "step3"
    elif step == "step3_lead_apply":
        phase1_recorded = journal.get("phase1_completed", False)
        if journal.get("push_verified"):
            result["next_step"] = "step4"
        elif journal.get("commit_sha"):
            result["next_step"] = "step3_push"
            result["resume_context"] = {"commit_sha": journal["commit_sha"]}
        elif phase1_recorded:
            result["next_step"] = "step3_phase2"
        else:
            result["next_step"] = "step3_phase1"
    elif step == "step4_settle":
        result["next_step"] = "step0"
    else:
        result["next_step"] = "step0"

    return result


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

import json
import os
import tempfile
from datetime import datetime, timezone


class StateCorruptedError(Exception):
    """Raised when a state file is corrupted or structurally invalid."""


def default_persistent_agents() -> dict:
    return {
        "cc_agent_id": None,
        "codex_session_id": None,
    }


def ensure_persistent_agents(state) -> bool:
    """Ensure the persisted state has the persistent agent handle block."""
    current = state.get("persistent_agents")
    if not isinstance(current, dict):
        state["persistent_agents"] = default_persistent_agents()
        return True

    changed = False
    for key, value in default_persistent_agents().items():
        if key not in current:
            current[key] = value
            changed = True
    return changed


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
    agent_mode="legacy",
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
        "agent_mode": agent_mode,
        "persistent_agents": default_persistent_agents(),
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
            "step_timings": {},
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


_REQUIRED_TOP_LEVEL = [
    "repo", "repo_root", "pr_number", "is_fork", "dry_run",
    "status", "current_round", "max_rounds", "started_at",
    "head", "journal", "issues", "rounds",
]

_REQUIRED_HEAD = [
    "initial_sha", "last_observed_pr_sha", "pr_branch_name", "target_ref",
]

_REQUIRED_JOURNAL = [
    "round", "step", "applied_issue_ids", "failed_application_issue_ids",
    "commit_sha", "push_verified", "state_persisted",
]


def validate_state(state) -> None:
    """Validate that a loaded state dict has the required structure.

    Raises StateCorruptedError if validation fails.
    """
    if not isinstance(state, dict):
        raise StateCorruptedError("State is not a JSON object")

    missing = [f for f in _REQUIRED_TOP_LEVEL if f not in state]
    if missing:
        raise StateCorruptedError(f"Missing top-level fields: {', '.join(missing)}")

    head = state["head"]
    if not isinstance(head, dict):
        raise StateCorruptedError("head must be a dict")
    missing_head = [f for f in _REQUIRED_HEAD if f not in head]
    if missing_head:
        raise StateCorruptedError(f"Missing head fields: {', '.join(missing_head)}")

    journal = state["journal"]
    if not isinstance(journal, dict):
        raise StateCorruptedError("journal must be a dict")
    missing_journal = [f for f in _REQUIRED_JOURNAL if f not in journal]
    if missing_journal:
        raise StateCorruptedError(f"Missing journal fields: {', '.join(missing_journal)}")

    if not isinstance(state["issues"], dict):
        raise StateCorruptedError("issues must be a dict")
    if not isinstance(state["rounds"], list):
        raise StateCorruptedError("rounds must be a list")


def load_state(path, *, validate=True) -> dict | None:
    if not os.path.exists(path):
        return None
    with open(path) as f:
        try:
            state = json.load(f)
        except json.JSONDecodeError as e:
            raise StateCorruptedError(f"JSON decode error in {path}: {e}") from e
    if validate:
        validate_state(state)
    return state


def save_state(state, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    dir_ = os.path.dirname(path)
    with tempfile.NamedTemporaryFile("w", dir=dir_, delete=False, suffix=".tmp") as f:
        json.dump(state, f, indent=2)
        tmp_path = f.name
    os.replace(tmp_path, path)

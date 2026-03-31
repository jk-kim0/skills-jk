"""record-application: 3-phase checkpoint for code application."""

import sys

from debate_review.gh import gh_json
from debate_review.round_ops import _find_round


def _get_pr_head_sha(repo, pr_number):
    data = gh_json("pr", "view", str(pr_number), "--repo", repo, "--json", "headRefOid")
    return data["headRefOid"]


def record_application_phase1(state, *, round_num, applied_issue_ids, failed_issue_ids) -> dict:
    """Phase 1: Record applied/failed issues before commit."""
    round_ = _find_round(state, round_num)
    journal = state["journal"]

    # Validate all issue IDs exist
    all_ids = list(applied_issue_ids) + list(failed_issue_ids)
    unknown = [iid for iid in all_ids if iid not in state["issues"]]
    if unknown:
        raise ValueError(f"Unknown issue IDs: {unknown}")

    # Warn if no issues were applied but some failed
    if not applied_issue_ids and failed_issue_ids:
        print(
            f"WARNING: applied=0, failed={len(failed_issue_ids)}. "
            "All applicable issues recorded as failed without any successful application.",
            file=sys.stderr,
        )

    # Checkpoint 0: initialize
    journal["step"] = "step3_lead_apply"
    journal["applied_issue_ids"] = []
    journal["failed_application_issue_ids"] = []
    journal["commit_sha"] = None
    journal["push_verified"] = False

    # Update each issue's application_status
    for issue_id in applied_issue_ids:
        state["issues"][issue_id]["application_status"] = "applied"

    for issue_id in failed_issue_ids:
        state["issues"][issue_id]["application_status"] = "failed"

    # Track touched issues in step3
    step3_touched = round_["step3"].setdefault("issue_ids_touched", [])
    for issue_id in all_ids:
        if issue_id not in step3_touched:
            step3_touched.append(issue_id)

    # Checkpoint 1: record in journal
    journal["applied_issue_ids"] = list(applied_issue_ids)
    journal["failed_application_issue_ids"] = list(failed_issue_ids)
    journal["phase1_completed"] = True

    return {
        "phase": 1,
        "round": round_num,
        "applied": len(applied_issue_ids),
        "failed": len(failed_issue_ids),
    }


def record_application_phase2(state, *, round_num, commit_sha) -> dict:
    """Phase 2: Record commit SHA."""
    _find_round(state, round_num)
    journal = state["journal"]

    if journal.get("step") != "step3_lead_apply":
        raise ValueError("Phase 2 requires Phase 1 to be completed first")

    # Checkpoint 2 (idempotent: skip if same SHA already recorded)
    if journal.get("commit_sha") == commit_sha:
        return {"phase": 2, "round": round_num, "commit_sha": commit_sha}

    if journal.get("commit_sha") is not None:
        raise ValueError(
            f"commit_sha already recorded as {journal['commit_sha']}, cannot overwrite with {commit_sha}"
        )

    journal["commit_sha"] = commit_sha

    return {"phase": 2, "round": round_num, "commit_sha": commit_sha}


def record_application_phase3(state, *, round_num, _get_head=None) -> dict:
    """Phase 3: Verify push and finalize."""
    round_ = _find_round(state, round_num)
    journal = state["journal"]

    if not journal.get("commit_sha"):
        raise ValueError("Phase 3 requires commit_sha from Phase 2 (record-application --commit-sha)")

    get_head = _get_head or _get_pr_head_sha
    head_sha = get_head(state["repo"], state["pr_number"])
    if head_sha != journal["commit_sha"]:
        raise ValueError(
            f"Phase 3 requires PR HEAD {head_sha} to match commit_sha {journal['commit_sha']}"
        )

    # Checkpoint 3
    journal["push_verified"] = True

    # Update issue-level fields
    lead_agent = round_["lead_agent"]
    commit_sha = journal["commit_sha"]
    for issue_id in journal["applied_issue_ids"]:
        if issue_id in state["issues"]:
            state["issues"][issue_id]["applied_by"] = lead_agent
            state["issues"][issue_id]["application_commit_sha"] = commit_sha

    # Record in round step3
    round_["step3"]["applied_issue_ids"] = list(journal["applied_issue_ids"])
    round_["step3"]["failed_application_issue_ids"] = list(journal["failed_application_issue_ids"])
    round_["step3"]["commit_sha"] = commit_sha
    round_["step3"]["push_verified"] = True

    # Checkpoint 4
    journal["state_persisted"] = True

    return {"phase": 3, "round": round_num, "push_verified": True}

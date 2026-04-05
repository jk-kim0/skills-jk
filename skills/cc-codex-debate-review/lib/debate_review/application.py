"""record-application: 3-phase checkpoint for code application."""

import re
import subprocess
import sys

from debate_review.gh import gh_json
from debate_review.issue_ops import latest_report_message
from debate_review.round_ops import _find_round
from debate_review.timing import record_step_timing


_HEX_SHA_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")


def _resolve_full_sha(short_sha, *, repo_root=None):
    """Resolve a (possibly short) SHA to a full 40-char SHA via git rev-parse."""
    cmd = ["git", "rev-parse", "--verify", f"{short_sha}^{{commit}}"]
    kwargs = {"capture_output": True, "text": True}
    if repo_root:
        kwargs["cwd"] = repo_root
    result = subprocess.run(cmd, **kwargs)
    if result.returncode != 0:
        raise ValueError(f"Cannot resolve SHA '{short_sha}': {result.stderr.strip()}")
    return result.stdout.strip()


def _normalize_commit_sha(commit_sha, *, repo_root=None):
    if not _HEX_SHA_RE.fullmatch(commit_sha):
        raise ValueError(
            f"Invalid commit SHA '{commit_sha}': expected 7-40 hexadecimal characters"
        )
    return _resolve_full_sha(commit_sha, repo_root=repo_root)


def _get_pr_head_sha(repo, pr_number):
    data = gh_json("pr", "view", str(pr_number), "--repo", repo, "--json", "headRefOid")
    return data["headRefOid"]


def _validate_issue_ids_exist(state, issue_ids):
    unknown = [issue_id for issue_id in issue_ids if issue_id not in state["issues"]]
    if unknown:
        raise ValueError(f"Unknown issue IDs: {unknown}")


def record_application_phase1(state, *, round_num, applied_issue_ids, failed_issue_ids) -> dict:
    """Phase 1: Record applied/failed issues before commit."""
    round_ = _find_round(state, round_num)
    journal = state["journal"]

    # Validate all issue IDs exist
    all_ids = list(applied_issue_ids) + list(failed_issue_ids)
    _validate_issue_ids_exist(state, all_ids)

    # Warn if no issues were applied but some failed
    if not applied_issue_ids and failed_issue_ids:
        print(
            f"WARNING: applied=0, failed={len(failed_issue_ids)}. "
            "All applicable issues recorded as failed without any successful application.",
            file=sys.stderr,
        )

    # Checkpoint 0: initialize
    journal["step"] = "step3_lead_apply"
    record_step_timing(state, "step3_lead_apply")
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

    # Normalize to full 40-char SHA
    full_sha = _normalize_commit_sha(commit_sha, repo_root=state.get("repo_root"))

    # Checkpoint 2 (idempotent: skip if same SHA already recorded)
    stored = journal.get("commit_sha")
    if stored is not None:
        stored_full_sha = _normalize_commit_sha(stored, repo_root=state.get("repo_root"))
        if stored_full_sha == full_sha:
            journal["commit_sha"] = full_sha
            return {"phase": 2, "round": round_num, "commit_sha": full_sha}
        raise ValueError(
            f"commit_sha already recorded as {stored}, cannot overwrite with {full_sha}"
        )

    journal["commit_sha"] = full_sha

    return {"phase": 2, "round": round_num, "commit_sha": full_sha}


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

    # Update head tracking so sync_head won't treat agent's push as external change
    state["head"]["last_observed_pr_sha"] = journal["commit_sha"]

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


def _build_commit_subject(state, *, round_num, applied_ids) -> str:
    """Build a localized commit subject for the current round."""
    language = state.get("language", "en")
    if language == "ko":
        return f"fix: 토론 리뷰 결과 반영 (라운드 {round_num})"
    if language == "en":
        return f"fix: apply debate review findings (round {round_num})"

    for issue_id in applied_ids:
        issue = state.get("issues", {}).get(issue_id)
        if issue:
            return f"fix: {latest_report_message(issue)}"

    return f"fix: debate-review r{round_num}"


def build_commit_message(state, *, round_num, applied_issue_ids=None) -> str:
    """Build a commit message from applied issues in the current round.

    Uses explicit applied_issue_ids when provided, otherwise falls back to
    journal.applied_issue_ids. Respects state["language"] for the subject line.
    """
    journal = state["journal"]
    applied_ids = applied_issue_ids if applied_issue_ids is not None else journal.get("applied_issue_ids", [])
    _validate_issue_ids_exist(state, applied_ids)
    subject = _build_commit_subject(state, round_num=round_num, applied_ids=applied_ids)

    if not applied_ids:
        return subject

    # Body: list each applied issue with its message
    lines = [subject, ""]
    for issue_id in applied_ids:
        issue = state.get("issues", {}).get(issue_id)
        if not issue:
            continue
        msg = latest_report_message(issue)
        loc = f"{issue.get('file', '?')}:{issue.get('line', '?')}"
        lines.append(f"- {issue_id} ({loc}): {msg}")

    return "\n".join(lines)

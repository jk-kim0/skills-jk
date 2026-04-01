"""post-comment: Generate and post final PR comment."""

from debate_review.gh import gh, gh_json
from debate_review.issue_ops import latest_report_message


def _make_tag(state):
    return f"[debate-review][sha:{state['head']['initial_sha']}]"


def _first_reporter(issue):
    """Get agent from the first report (opened_by)."""
    if issue.get("reports"):
        return issue["reports"][0]["agent"]
    return "unknown"


def _build_debate_summary_lines(state):
    """Build Debate Summary section from debate_ledger."""
    ledger = state.get("debate_ledger", [])
    if not ledger:
        return []
    lines = ["", "## Debate Summary"]
    for entry in ledger:
        status = entry.get("status", "unknown")
        summary = entry.get("summary", "")
        issue_id = entry.get("issue_id", "")
        lines.append(f"- {issue_id} [{status}] {summary}")
    return lines


def _build_consensus(state, tag):
    """Template for consensus (same-repo and fork)."""
    is_fork = state.get("is_fork", False)
    header = f"{tag} Consensus reached after {state['current_round']} rounds."
    if is_fork:
        header += " (fork PR - code push not allowed)"
    lines = [header]

    lines.extend(_build_debate_summary_lines(state))

    if is_fork:
        fixes = [i for i in state["issues"].values() if i["application_status"] == "recommended"]
        fixes_heading = "## Recommended Fixes"
    else:
        fixes = [i for i in state["issues"].values() if i["application_status"] == "applied"]
        fixes_heading = "## Applied Fixes"

    withdrawn = [i for i in state["issues"].values() if i["consensus_status"] == "withdrawn"]

    if not fixes and not withdrawn and not state.get("debate_ledger"):
        lines.append("")
        lines.append("No actionable issues remain.")
        return "\n".join(lines)

    if fixes:
        lines.append("")
        lines.append(fixes_heading)
        for issue in fixes:
            reporter = _first_reporter(issue)
            msg = latest_report_message(issue)
            if is_fork:
                lines.append(f"- {issue['file']}:{issue['line']} - (reported by {reporter}) {msg}")
            else:
                applier = issue.get("applied_by", "unknown")
                lines.append(
                    f"- {issue['file']}:{issue['line']} - (reported by {reporter}, applied by {applier}) {msg}"
                )

    if withdrawn:
        lines.append("")
        lines.append("## Withdrawn Findings")
        for issue in withdrawn:
            msg = latest_report_message(issue)
            reason = issue.get("consensus_reason", "")
            lines.append(f"- {issue['file']}:{issue['line']} - {msg}")
            if reason:
                lines.append(f"  Reason: {reason}")

    return "\n".join(lines)


def _build_max_rounds(state, tag):
    """Template 3: max rounds exceeded."""
    lines = [f"{tag} Consensus was not reached after {state['max_rounds']} rounds."]

    lines.extend(_build_debate_summary_lines(state))

    unresolved = [i for i in state["issues"].values()
                  if i["consensus_status"] == "open"
                  or (i["consensus_status"] == "accepted" and i["application_status"] not in ("applied", "recommended"))]

    if unresolved:
        lines.append("")
        lines.append("## Unresolved Issues")
        for issue in unresolved:
            msg = latest_report_message(issue)
            lines.append(f"- {issue['file']}:{issue['line']} - {msg}")

    lines.append("")
    lines.append("Manual review required.")
    return "\n".join(lines)


def _build_error(state, tag):
    """Template 4: error."""
    journal = state["journal"]
    lines = [f"{tag} Review stopped due to an error."]

    lines.extend(_build_debate_summary_lines(state))

    lines.append("")
    lines.append(f"Round: {journal.get('round', '?')}")
    lines.append(f"Step: {journal.get('step', '?')}")
    lines.append(f"Error: {state.get('error_message', 'Unknown error')}")
    lines.append("")
    lines.append("Manual review required.")
    return "\n".join(lines)


def build_comment_body(state) -> str:
    """Build comment body based on session state."""
    tag = _make_tag(state)
    outcome = state.get("final_outcome")

    if outcome == "consensus":
        return _build_consensus(state, tag)
    elif outcome == "no_consensus":
        return _build_max_rounds(state, tag)
    else:
        return _build_error(state, tag)


def _find_existing_comment(state):
    """Check if a comment with our tag already exists. Returns comment ID or None."""
    tag = _make_tag(state)
    try:
        data = gh_json(
            "pr", "view", str(state["pr_number"]),
            "--repo", state["repo"],
            "--json", "comments",
        )
        for comment in data.get("comments", []):
            if comment.get("body", "").startswith(tag):
                return comment.get("id")
    except RuntimeError:
        pass
    return None


def _post_comment_to_gh(state, body):
    """Post comment to GitHub PR. Returns comment URL."""
    return gh(
        "pr", "comment", str(state["pr_number"]),
        "--repo", state["repo"],
        "--body", body,
    )


def post_comment(state, *, no_comment=False, _find_existing=None, _post=None) -> dict:
    """Generate and optionally post the final PR comment.

    Injectable helpers for testing:
    - _find_existing(state) -> comment_id or None
    - _post(state, body) -> post result string
    """
    # Dry run: suppress posting
    if state.get("dry_run"):
        no_comment = True

    # Already posted?
    if state.get("final_comment_id"):
        body = build_comment_body(state)
        return {"action": "skipped", "reason": "already_posted", "body": body}

    body = build_comment_body(state)
    tag = _make_tag(state)

    if no_comment:
        return {"action": "dry_run", "body": body}

    # Check for existing comment (dedup)
    find_existing = _find_existing or _find_existing_comment
    existing_id = find_existing(state)
    if existing_id:
        state["final_comment_tag"] = tag
        state["final_comment_id"] = existing_id
        return {"action": "backfilled", "comment_id": existing_id, "body": body}

    # Post
    post_fn = _post or _post_comment_to_gh
    post_fn(state, body)

    # Verify — find the comment we just posted
    posted_id = find_existing(state)
    if posted_id:
        state["final_comment_tag"] = tag
        state["final_comment_id"] = posted_id

    return {"action": "posted", "comment_id": posted_id, "body": body}

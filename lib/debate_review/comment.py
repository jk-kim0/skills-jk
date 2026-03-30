"""post-comment: Generate and post final PR comment."""

from debate_review.gh import gh, gh_json


def _make_tag(state):
    return f"[debate-review][sha:{state['head']['initial_sha']}]"


def _latest_report_message(issue):
    """Get message from the latest report."""
    if not issue.get("reports"):
        return issue.get("severity", "unknown") + " issue"
    return issue["reports"][-1]["message"]


def _first_reporter(issue):
    """Get agent from the first report (opened_by)."""
    if issue.get("reports"):
        return issue["reports"][0]["agent"]
    return "unknown"


def _build_consensus_same_repo(state, tag):
    """Template 1: consensus, same-repo."""
    lines = [f"{tag} {state['current_round']}라운드 만에 합의에 도달했습니다."]

    applied = [i for i in state["issues"].values() if i["application_status"] == "applied"]
    withdrawn = [i for i in state["issues"].values() if i["consensus_status"] == "withdrawn"]

    if not applied and not withdrawn:
        lines.append("")
        lines.append("No actionable issues remain.")
        return "\n".join(lines)

    if applied:
        lines.append("")
        lines.append("## Applied Fixes")
        for issue in applied:
            reporter = _first_reporter(issue)
            applier = issue.get("applied_by", "unknown")
            msg = _latest_report_message(issue)
            lines.append(f"- {issue['file']}:{issue['line']} - (reported by {reporter}, applied by {applier}) {msg}")

    if withdrawn:
        lines.append("")
        lines.append("## Withdrawn Findings")
        for issue in withdrawn:
            msg = _latest_report_message(issue)
            reason = issue.get("consensus_reason", "")
            lines.append(f"- {issue['file']}:{issue['line']} - {msg}")
            if reason:
                lines.append(f"  Reason: {reason}")

    return "\n".join(lines)


def _build_consensus_fork(state, tag):
    """Template 2: consensus, fork PR."""
    lines = [f"{tag} {state['current_round']}라운드 만에 합의에 도달했습니다. (fork PR - code push not allowed)"]

    recommended = [i for i in state["issues"].values() if i["application_status"] == "recommended"]
    withdrawn = [i for i in state["issues"].values() if i["consensus_status"] == "withdrawn"]

    if not recommended and not withdrawn:
        lines.append("")
        lines.append("No actionable issues remain.")
        return "\n".join(lines)

    if recommended:
        lines.append("")
        lines.append("## Recommended Fixes")
        for issue in recommended:
            reporter = _first_reporter(issue)
            msg = _latest_report_message(issue)
            lines.append(f"- {issue['file']}:{issue['line']} - (reported by {reporter}) {msg}")

    if withdrawn:
        lines.append("")
        lines.append("## Withdrawn Findings")
        for issue in withdrawn:
            msg = _latest_report_message(issue)
            reason = issue.get("consensus_reason", "")
            lines.append(f"- {issue['file']}:{issue['line']} - {msg}")
            if reason:
                lines.append(f"  Reason: {reason}")

    return "\n".join(lines)


def _build_max_rounds(state, tag):
    """Template 3: max rounds exceeded."""
    lines = [f"{tag} {state['max_rounds']}라운드 후 합의에 도달하지 못했습니다."]

    unresolved = [i for i in state["issues"].values()
                  if i["consensus_status"] == "open"
                  or (i["consensus_status"] == "accepted" and i["application_status"] not in ("applied", "recommended"))]

    if unresolved:
        lines.append("")
        lines.append("## Unresolved Issues")
        for issue in unresolved:
            msg = _latest_report_message(issue)
            lines.append(f"- {issue['file']}:{issue['line']} - {msg}")

    lines.append("")
    lines.append("Manual review required.")
    return "\n".join(lines)


def _build_error(state, tag):
    """Template 4: error."""
    journal = state["journal"]
    lines = [f"{tag} 오류로 인해 리뷰가 중단되었습니다."]
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
        if state.get("is_fork"):
            return _build_consensus_fork(state, tag)
        else:
            return _build_consensus_same_repo(state, tag)
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

"""Build all state-derivable placeholder data for agent prompts."""


def _resolve_report(state, report_id):
    """Find a report by ID across all issues and return enriched data."""
    for iid, issue in state.get("issues", {}).items():
        for rpt in issue.get("reports", []):
            if rpt["report_id"] == report_id:
                return {
                    "report_id": report_id,
                    "issue_id": iid,
                    "severity": rpt.get("severity", issue.get("severity")),
                    "file": issue.get("file"),
                    "line": issue.get("line"),
                    "anchor": issue.get("anchor"),
                    "message": rpt.get("message", ""),
                }
    return None


def build_review_context(state, round_num):
    """Build {REVIEW_CONTEXT} text from the last 2 completed rounds."""
    if round_num <= 1:
        return "(First round — no previous reviews)"

    start = max(1, round_num - 2)
    rounds = [r for r in state.get("rounds", [])
              if start <= r["round"] < round_num
              and r.get("status") in ("completed", "superseded")]

    if not rounds:
        return "(No completed rounds in scope)"

    issues = state.get("issues", {})
    lines = [f"## Review Context (rounds {start} to {round_num - 1})"]

    for r in sorted(rounds, key=lambda x: x["round"]):
        rn = r["round"]
        lead = r.get("lead_agent", "?")
        cross = "cc" if lead == "codex" else "codex"
        status = r.get("status", "?")
        clean = r.get("clean_pass", False)
        lines.append("")
        lines.append(f"### Round {rn} [lead: {lead}, status: {status}, clean_pass: {clean}]")

        # Step 1
        step1 = r.get("step1", {})
        if step1.get("report_ids"):
            lines.append(f"\n**Step 1 ({lead} review):**")
            for rid in step1["report_ids"]:
                rpt = _resolve_report(state, rid)
                if rpt:
                    lines.append(f"- {rpt['issue_id']} ({rpt['severity']}) {rpt['file']}:{rpt['line']} — {rpt['message']}")

        # Step 2
        step2 = r.get("step2", {})
        if step2.get("accepted_report_ids") or step2.get("rebuttals"):
            lines.append(f"\n**Step 2 ({cross} cross-verification):**")
            for rid in step2.get("accepted_report_ids", []):
                rpt = _resolve_report(state, rid)
                if rpt:
                    lines.append(f"- {rid} ({rpt['issue_id']}): accepted")
            for reb in step2.get("rebuttals", []):
                lines.append(f"- {reb.get('report_id', '?')} ({reb.get('issue_id', '?')}): rebutted — \"{reb.get('reason', '')}\"")
            if step2.get("report_ids"):
                new_rids = [rid for rid in step2["report_ids"]
                            if rid not in step2.get("accepted_report_ids", [])]
                if new_rids:
                    lines.append(f"\n**Step 2 ({cross} new findings):**")
                    for rid in new_rids:
                        rpt = _resolve_report(state, rid)
                        if rpt:
                            lines.append(f"- {rpt['issue_id']} ({rpt['severity']}) {rpt['file']}:{rpt['line']} — {rpt['message']}")

        # Step 3
        step3 = r.get("step3", {})
        has_step3 = (step3.get("withdrawn_report_ids") or step3.get("accepted_report_ids")
                     or step3.get("applied_issue_ids"))
        if has_step3:
            lines.append(f"\n**Step 3 ({lead} response + application):**")
            for rid in step3.get("withdrawn_report_ids", []):
                rpt = _resolve_report(state, rid)
                iid = rpt["issue_id"] if rpt else "?"
                lines.append(f"- {rid} rebuttal: accepted → {iid} withdrawn")
            for rid in step3.get("accepted_report_ids", []):
                rpt = _resolve_report(state, rid)
                iid = rpt["issue_id"] if rpt else "?"
                lines.append(f"- {rid}: accepted → {iid} added to consensus")
            if step3.get("applied_issue_ids"):
                lines.append(f"- Applied: {', '.join(step3['applied_issue_ids'])}")

    # Unresolved issues
    unresolved = [iid for iid, iss in issues.items() if iss.get("consensus_status") == "open"]
    lines.append("")
    if unresolved:
        lines.append(f"**Unresolved issues:** {', '.join(unresolved)}")
    else:
        lines.append("**Unresolved issues:** (none)")

    return "\n".join(lines)


def build_open_issues(state):
    """Build {OPEN_ISSUES} list — unresolved issues for current state."""
    issues = state.get("issues", {})
    is_fork = state.get("is_fork", False)
    result = []
    for iid, issue in issues.items():
        cs = issue.get("consensus_status")
        app = issue.get("application_status")
        include = False
        if cs == "open":
            include = True
        elif cs == "accepted":
            if is_fork and app != "recommended":
                include = True
            elif not is_fork and app != "applied":
                include = True
        if include:
            result.append({
                "issue_id": iid,
                "consensus_status": cs,
                "application_status": app,
                "severity": issue.get("severity"),
                "file": issue.get("file"),
                "line": issue.get("line"),
                "anchor": issue.get("anchor"),
                "message": issue.get("reports", [{}])[-1].get("message", ""),
            })
    return result


def build_debate_ledger_text(state):
    """Build {DEBATE_LEDGER} text from state's debate_ledger array."""
    ledger = state.get("debate_ledger", [])
    if not ledger:
        return "(First round — no previous conclusions)"

    lines = ["## Debate Ledger (full-round conclusion summary)"]
    lines.append("")
    for entry in ledger:
        status = entry.get("status", "?")
        iid = entry.get("issue_id", "?")
        summary = entry.get("summary", "")
        reason = entry.get("reason")
        if reason:
            lines.append(f"- {iid} [{status}] (reason: {reason}) {summary}")
        else:
            lines.append(f"- {iid} [{status}] {summary}")
    lines.append("")
    lines.append("To re-raise a previously withdrawn issue, you must present new evidence different from the reason above.")
    return "\n".join(lines)


def build_pending_rebuttals(state, round_num):
    """Build {PENDING_REBUTTALS} — rebuttals from previous round's step3."""
    if round_num <= 1:
        return []
    prev_round = None
    for r in state.get("rounds", []):
        if r["round"] == round_num - 1:
            prev_round = r
            break
    if not prev_round:
        return []
    rebuttals = prev_round.get("step3", {}).get("rebuttals", [])
    result = []
    for reb in rebuttals:
        rid = reb.get("report_id")
        rpt = _resolve_report(state, rid) if rid else None
        entry = {
            "report_id": rid,
            "issue_id": reb.get("issue_id") or (rpt["issue_id"] if rpt else None),
            "decision": reb.get("decision"),
            "reason": reb.get("reason", ""),
        }
        if rpt:
            entry.update({
                "severity": rpt["severity"],
                "file": rpt["file"],
                "line": rpt["line"],
                "anchor": rpt["anchor"],
                "message": rpt["message"],
            })
        result.append(entry)
    return result


def build_lead_reports(state, round_num):
    """Build {LEAD_REPORTS} — lead agent's findings for the current round."""
    for r in state.get("rounds", []):
        if r["round"] == round_num:
            report_ids = r.get("step1", {}).get("report_ids", [])
            return [rpt for rid in report_ids if (rpt := _resolve_report(state, rid))]
    return []


def build_cross_rebuttals(state, round_num):
    """Build {CROSS_REBUTTALS} — cross-verifier's rebuttals for the current round."""
    for r in state.get("rounds", []):
        if r["round"] == round_num:
            rebuttals = r.get("step2", {}).get("rebuttals", [])
            result = []
            for reb in rebuttals:
                rid = reb.get("report_id")
                rpt = _resolve_report(state, rid) if rid else None
                entry = {
                    "report_id": rid,
                    "issue_id": reb.get("issue_id") or (rpt["issue_id"] if rpt else None),
                    "reason": reb.get("reason", ""),
                }
                if rpt:
                    entry.update({
                        "severity": rpt["severity"],
                        "file": rpt["file"],
                        "line": rpt["line"],
                        "anchor": rpt["anchor"],
                        "message": rpt["message"],
                    })
                result.append(entry)
            return result
    return []


def build_cross_findings(state, round_num):
    """Build {CROSS_FINDINGS} — cross-verifier's new findings for the current round."""
    for r in state.get("rounds", []):
        if r["round"] == round_num:
            step2 = r.get("step2", {})
            # Cross findings = step2 report_ids that are NOT in accepted_report_ids
            accepted = set(step2.get("accepted_report_ids", []))
            report_ids = step2.get("report_ids", [])
            new_rids = [rid for rid in report_ids if rid not in accepted]
            return [rpt for rid in new_rids if (rpt := _resolve_report(state, rid))]
    return []


def build_applicable_issues(state):
    """Build {APPLICABLE_ISSUES} — issues ready for code application."""
    result = []
    for iid, issue in state.get("issues", {}).items():
        if (issue.get("consensus_status") == "accepted"
                and issue.get("application_status") in ("pending", "failed")):
            result.append({
                "issue_id": iid,
                "file": issue.get("file"),
                "line": issue.get("line"),
                "anchor": issue.get("anchor"),
                "message": issue.get("reports", [{}])[-1].get("message", ""),
            })
    return result


def build_context(state, round_num):
    """Build all state-derivable placeholder data for agent prompts."""
    return {
        "review_context": build_review_context(state, round_num),
        "open_issues": build_open_issues(state),
        "debate_ledger": build_debate_ledger_text(state),
        "pending_rebuttals": build_pending_rebuttals(state, round_num),
        "lead_reports": build_lead_reports(state, round_num),
        "cross_rebuttals": build_cross_rebuttals(state, round_num),
        "cross_findings": build_cross_findings(state, round_num),
        "applicable_issues": build_applicable_issues(state),
    }

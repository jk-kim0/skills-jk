from debate_review.round_ops import _find_round


def _find_issue_by_report_id(state, report_id):
    """Return (issue_id, issue, report) for the given report_id, or raise."""
    for issue_id, issue in state["issues"].items():
        for report in issue["reports"]:
            if report["report_id"] == report_id:
                return issue_id, issue, report
    raise ValueError(f"report_id {report_id!r} not found in any issue")


def _recalculate_accepted_by(issue):
    """Recalculate accepted_by based on reports with status != 'withdrawn'."""
    seen = []
    for report in issue["reports"]:
        status = report.get("status", "open")
        if status != "withdrawn" and report["agent"] not in seen:
            seen.append(report["agent"])
    issue["accepted_by"] = seen


def _apply_withdraw(issue, report):
    """Mark report as withdrawn and recalculate issue consensus state."""
    report["status"] = "withdrawn"
    _recalculate_accepted_by(issue)
    accepted_by = issue["accepted_by"]
    if not accepted_by:
        issue["consensus_status"] = "withdrawn"
        issue["application_status"] = "not_applicable"
    elif set(accepted_by) != {"cc", "codex"}:
        issue["consensus_status"] = "open"


def record_cross_verification(state, *, round_num, verifications) -> dict:
    round_ = _find_round(state, round_num)
    lead_agent = round_["lead_agent"]
    cross_verifier = "cc" if lead_agent == "codex" else "codex"

    for v in verifications:
        report_id = v["report_id"]
        decision = v["decision"]
        reason = v.get("reason", "")

        issue_id, issue, _report = _find_issue_by_report_id(state, report_id)

        if decision == "accept":
            round_["step2"]["accepted_report_ids"].append(report_id)
            if cross_verifier not in issue["accepted_by"]:
                issue["accepted_by"].append(cross_verifier)
            if set(issue["accepted_by"]) >= {"cc", "codex"}:
                issue["consensus_status"] = "accepted"
                if state.get("is_fork"):
                    issue["application_status"] = "recommended"
        elif decision == "rebut":
            round_["step2"]["rebuttals"].append({
                "report_id": report_id,
                "issue_id": issue_id,
                "reason": reason,
            })

    return {"round": round_num, "processed": len(verifications)}


def resolve_rebuttals(state, *, round_num, step, decisions) -> dict:
    round_ = _find_round(state, round_num)
    lead_agent = round_["lead_agent"]

    re_report_ids = []

    for d in decisions:
        report_id = d["report_id"]
        decision = d["decision"]
        reason = d.get("reason", "")

        issue_id, issue, report = _find_issue_by_report_id(state, report_id)

        if step == "1a":
            round_["step1"]["rebuttal_responses"].append({
                "report_id": report_id,
                "decision": decision,
                "reason": reason,
            })
            if decision == "withdraw":
                _apply_withdraw(issue, report)
            elif decision == "maintain":
                re_report_ids.append(report_id)

        elif step == "3":
            if decision == "withdraw":
                _apply_withdraw(issue, report)
                round_["step3"]["withdrawn_report_ids"].append(report_id)
            elif decision == "maintain":
                round_["step3"]["rebuttals"].append({
                    "report_id": report_id,
                    "issue_id": issue_id,
                    "reason": reason,
                })
            elif decision == "accept":
                if lead_agent not in issue["accepted_by"]:
                    issue["accepted_by"].append(lead_agent)
                if set(issue["accepted_by"]) >= {"cc", "codex"}:
                    issue["consensus_status"] = "accepted"
                    if state.get("is_fork"):
                        issue["application_status"] = "recommended"
                round_["step3"]["accepted_report_ids"].append(report_id)

    result = {"round": round_num, "step": step, "processed": len(decisions)}
    if re_report_ids:
        result["re_report_ids"] = re_report_ids
    return result

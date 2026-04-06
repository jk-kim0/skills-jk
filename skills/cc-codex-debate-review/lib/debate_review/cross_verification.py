import sys

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


def _should_restore_pre_reopen(issue):
    """Check if all reports added after reopen are withdrawn, so we can restore."""
    pre = issue.get("pre_reopen_state")
    if not pre:
        return False
    reopen_round = issue.get("reopened_in_round")
    if reopen_round is None:
        return False
    for r in issue["reports"]:
        if r["round"] >= reopen_round and r.get("status", "open") != "withdrawn":
            return False
    return True


def _apply_withdraw(issue, report, reason="", *, round_num=None):
    """Mark report as withdrawn and recalculate issue consensus state."""
    prev_status = issue.get("consensus_status")
    report["status"] = "withdrawn"
    _recalculate_accepted_by(issue)
    accepted_by = issue["accepted_by"]
    if _should_restore_pre_reopen(issue):
        pre = issue.pop("pre_reopen_state")
        for key, val in pre.items():
            issue[key] = val
        issue["consensus_reason"] = None
    elif not accepted_by:
        issue.pop("pre_reopen_state", None)
        issue["consensus_status"] = "withdrawn"
        issue["consensus_reason"] = reason
        issue["application_status"] = "not_applicable"
    else:
        # Partial withdraw or still both agents — clear stale reason
        issue["consensus_reason"] = None
        if set(accepted_by) != {"cc", "codex"}:
            issue["consensus_status"] = "open"
            # Track reopening so settle_round can distinguish re-settlement
            if prev_status != "open" and round_num is not None:
                issue["reopened_in_round"] = round_num


def record_cross_verification(state, *, round_num, verifications) -> dict:
    round_ = _find_round(state, round_num)
    lead_agent = round_["lead_agent"]
    cross_verifier = "cc" if lead_agent == "codex" else "codex"

    skipped = []
    for v in verifications:
        report_id = v["report_id"]
        decision = v["decision"]
        reason = v.get("reason", "")

        try:
            issue_id, issue, _report = _find_issue_by_report_id(state, report_id)
        except ValueError:
            print(
                f"WARNING: skipping unknown report_id {report_id!r} "
                f"(cross-verifier fabricated a report_id not in lead findings)",
                file=sys.stderr,
            )
            skipped.append(report_id)
            continue

        if decision == "accept":
            if report_id not in round_["step2"]["accepted_report_ids"]:
                round_["step2"]["accepted_report_ids"].append(report_id)
            if issue_id not in round_["step2"]["issue_ids_touched"]:
                round_["step2"]["issue_ids_touched"].append(issue_id)
            if cross_verifier not in issue["accepted_by"]:
                issue["accepted_by"].append(cross_verifier)
            if set(issue["accepted_by"]) >= {"cc", "codex"}:
                issue["consensus_status"] = "accepted"
                issue["consensus_reason"] = None
                if state.get("is_fork"):
                    issue["application_status"] = "recommended"
        elif decision == "rebut":
            round_["step2"]["rebuttals"].append({
                "report_id": report_id,
                "issue_id": issue_id,
                "reason": reason,
            })

    result = {"round": round_num, "processed": len(verifications) - len(skipped)}
    if skipped:
        result["skipped_report_ids"] = skipped
    return result


def resolve_rebuttals(state, *, round_num, step, decisions) -> dict:
    if step not in ("1a", "3"):
        raise ValueError(f"step must be '1a' or '3', got {step!r}")
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
            if issue_id not in round_["step1"]["issue_ids_touched"]:
                round_["step1"]["issue_ids_touched"].append(issue_id)
            if decision == "withdraw":
                _apply_withdraw(issue, report, reason, round_num=round_num)
            elif decision == "maintain":
                re_report_ids.append(report_id)

        elif step == "3":
            if issue_id not in round_["step3"]["issue_ids_touched"]:
                round_["step3"]["issue_ids_touched"].append(issue_id)
            if decision == "withdraw":
                _apply_withdraw(issue, report, reason, round_num=round_num)
                if report_id not in round_["step3"]["withdrawn_report_ids"]:
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
                    issue["consensus_reason"] = None
                    if state.get("is_fork"):
                        issue["application_status"] = "recommended"
                if report_id not in round_["step3"]["accepted_report_ids"]:
                    round_["step3"]["accepted_report_ids"].append(report_id)

    result = {"round": round_num, "step": step, "processed": len(decisions)}
    if re_report_ids:
        result["re_report_ids"] = re_report_ids
    return result

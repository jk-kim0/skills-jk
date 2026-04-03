from datetime import datetime, timezone


def init_round(state, *, round_num, lead_agent=None, synced_head_sha):
    if lead_agent is None:
        lead_agent = "codex" if round_num % 2 == 1 else "cc"
    # Idempotent: skip if round already exists
    for r in state["rounds"]:
        if r["round"] == round_num:
            return
    state["rounds"].append({
        "round": round_num,
        "status": "active",
        "lead_agent": lead_agent,
        "synced_head_sha": synced_head_sha,
        "clean_pass": False,
        "step1": {
            "rebuttal_responses": [],
            "report_ids": [],
            "issue_ids_touched": [],
            "verdict": None,
        },
        "step2": {
            "report_ids": [],
            "issue_ids_touched": [],
            "accepted_report_ids": [],
            "rebuttals": [],
        },
        "step3": {
            "withdrawn_report_ids": [],
            "accepted_report_ids": [],
            "rebuttals": [],
            "issue_ids_touched": [],
            "applied_issue_ids": [],
            "failed_application_issue_ids": [],
            "commit_sha": None,
            "push_verified": False,
        },
        "step4": {
            "unresolved_issue_ids": [],
            "recommendation_issue_ids": [],
            "settled_issues": [],
            "result": None,
        },
    })


def _find_round(state, round_num):
    for r in state["rounds"]:
        if r["round"] == round_num:
            return r
    raise ValueError(f"Round {round_num} not found")


def record_verdict(state, *, round_num, verdict) -> dict:
    round_ = _find_round(state, round_num)
    round_["step1"]["verdict"] = verdict

    clean_pass = False
    if verdict == "no_findings_mergeable":
        issues = state["issues"]
        is_fork = state.get("is_fork", False)

        open_issues = [i for i in issues.values() if i["consensus_status"] == "open"]
        if open_issues:
            raise ValueError(
                f"verdict=no_findings_mergeable but {len(open_issues)} open issue(s) exist"
            )

        accepted_issues = [i for i in issues.values() if i["consensus_status"] == "accepted"]
        if is_fork:
            not_recommended = [
                i for i in accepted_issues if i["application_status"] != "recommended"
            ]
            if not_recommended:
                raise ValueError(
                    f"verdict=no_findings_mergeable but {len(not_recommended)} accepted issue(s) "
                    f"not yet recommended"
                )
        else:
            not_applied = [
                i for i in accepted_issues if i["application_status"] != "applied"
            ]
            if not_applied:
                raise ValueError(
                    f"verdict=no_findings_mergeable but {len(not_applied)} accepted issue(s) "
                    f"not yet applied"
                )

        clean_pass = True

    round_["clean_pass"] = clean_pass
    return {"round": round_num, "verdict": verdict, "clean_pass": clean_pass}


def _collect_touched_issue_ids(round_):
    """Collect all issue IDs touched in any step of the round."""
    touched = set()
    for step_key in ("step1", "step2", "step3"):
        touched.update(round_.get(step_key, {}).get("issue_ids_touched", []))
    return touched


def settle_round(state, *, round_num) -> dict:
    round_ = _find_round(state, round_num)
    if round_["status"] != "active":
        raise ValueError(f"Round {round_num} is not active (status={round_['status']})")
    round_["status"] = "completed"

    issues = state["issues"]
    is_fork = state.get("is_fork", False)

    # Calculate unresolved_issue_ids
    unresolved_issue_ids = []
    for iid, issue in issues.items():
        cs = issue["consensus_status"]
        app = issue["application_status"]
        if is_fork:
            if cs == "open":
                unresolved_issue_ids.append(iid)
        else:
            if cs == "open" or (cs == "accepted" and app != "applied"):
                unresolved_issue_ids.append(iid)

    # Calculate recommendation_issue_ids (fork only)
    recommendation_issue_ids = []
    if is_fork:
        for iid, issue in issues.items():
            if issue["consensus_status"] == "accepted" and issue["application_status"] == "recommended":
                recommendation_issue_ids.append(iid)

    round_["step4"]["recommendation_issue_ids"] = recommendation_issue_ids

    # Collect issues that were settled (withdrawn/accepted) during this round
    # Skip if the latest ledger entry for this issue has same status AND same round
    # (prevents double-counting within same round, but allows re-raised issues to append)
    latest_ledger = {}
    for entry in state.get("debate_ledger", []):
        latest_ledger[entry["issue_id"]] = (entry["status"], entry.get("round"))

    touched_ids = _collect_touched_issue_ids(round_)
    settled_issues = []
    for iid, issue in issues.items():
        cs = issue["consensus_status"]
        if cs in ("withdrawn", "accepted") and iid in touched_ids:
            prev = latest_ledger.get(iid)
            if prev and prev[0] == cs:
                if prev[1] == round_num:
                    # Same status + same round → already counted (idempotency)
                    continue
                # Different round with same status — only include if genuinely re-settled:
                # issue must have been reopened AFTER the last ledger entry
                reopened = issue.get("reopened_in_round")
                if not (reopened is not None and reopened > (prev[1] or 0)):
                    continue
            settled_issues.append({
                "issue_id": iid,
                "consensus_status": cs,
                "consensus_reason": issue.get("consensus_reason"),
                "file": issue.get("file"),
                "anchor": issue.get("anchor"),
            })

    # Auto-withdraw duplicates: open issues sharing criterion+anchor with an applied/accepted issue
    applied_anchors = {}  # (criterion, anchor) -> applied_issue_id
    for iid, issue in issues.items():
        if issue["consensus_status"] == "accepted" and issue["application_status"] == "applied":
            key = (issue.get("criterion"), issue.get("anchor"))
            if key[0] is not None and key[1] is not None:
                applied_anchors[key] = iid

    for iid, issue in issues.items():
        if issue["consensus_status"] == "open":
            key = (issue.get("criterion"), issue.get("anchor"))
            if key in applied_anchors and iid != applied_anchors[key]:
                issue["consensus_status"] = "withdrawn"
                issue["consensus_reason"] = f"duplicate of {applied_anchors[key]} (same criterion+anchor, different file)"
                settled_issues.append({
                    "issue_id": iid,
                    "consensus_status": "withdrawn",
                    "consensus_reason": issue["consensus_reason"],
                    "file": issue.get("file"),
                    "anchor": issue.get("anchor"),
                })

    # Remove auto-withdrawn duplicates from unresolved list
    unresolved_issue_ids = [iid for iid in unresolved_issue_ids
                            if issues[iid]["consensus_status"] != "withdrawn"]

    round_["step4"]["unresolved_issue_ids"] = unresolved_issue_ids
    round_["step4"]["settled_issues"] = settled_issues

    # Check consensus: last 2 completed rounds both have clean_pass==True
    # AND different lead agents (spec requirement)
    completed = [r for r in state["rounds"] if r["status"] == "completed"]
    last_two = completed[-2:]
    consensus_reached = (
        len(last_two) >= 2
        and last_two[1]["round"] == last_two[0]["round"] + 1
        and all(r["clean_pass"] for r in last_two)
        and last_two[0]["lead_agent"] != last_two[1]["lead_agent"]
    )

    # Check max_rounds
    max_rounds_exceeded = state["current_round"] >= state["max_rounds"]

    # Stall detection: check if this round made progress
    # Clean pass rounds are not stalls (no unresolved issues to fix)
    round_applied = len(round_.get("step3", {}).get("applied_issue_ids", []))
    no_progress = (
        unresolved_issue_ids
        and (not settled_issues)
        and (round_applied == 0)
    )
    stall_count = 0
    if no_progress:
        stall_count = 1
        for prev in reversed(completed[:-1]):
            prev_applied = len(prev.get("step3", {}).get("applied_issue_ids", []))
            prev_settled = prev.get("step4", {}).get("settled_issues", [])
            prev_unresolved = prev.get("step4", {}).get("unresolved_issue_ids", [])
            if prev_unresolved and (not prev_settled) and (prev_applied == 0):
                stall_count += 1
            else:
                break

    now = datetime.now(timezone.utc).isoformat()

    if consensus_reached:
        state["status"] = "consensus_reached"
        state["final_outcome"] = "consensus"
        state["finished_at"] = now
        state["head"]["terminal_sha"] = state["head"]["last_observed_pr_sha"]
        round_["step4"]["result"] = "consensus_reached"
        return {
            "round": round_num,
            "result": "consensus_reached",
            "unresolved_issue_ids": unresolved_issue_ids,
            "recommendation_issue_ids": recommendation_issue_ids,
            "settled_issues": settled_issues,
        }
    elif stall_count >= 2:
        state["status"] = "stalled"
        state["final_outcome"] = "stalled"
        state["error_message"] = (
            f"Stalled: {stall_count} consecutive rounds with no progress "
            "(no settlements, no code applied)"
        )
        state["finished_at"] = now
        state["head"]["terminal_sha"] = state["head"]["last_observed_pr_sha"]
        round_["step4"]["result"] = "stalled"
        return {
            "round": round_num,
            "result": "stalled",
            "stall_count": stall_count,
            "unresolved_issue_ids": unresolved_issue_ids,
            "recommendation_issue_ids": recommendation_issue_ids,
            "settled_issues": settled_issues,
        }
    elif max_rounds_exceeded:
        state["status"] = "max_rounds_exceeded"
        state["final_outcome"] = "no_consensus"
        state["finished_at"] = now
        state["head"]["terminal_sha"] = state["head"]["last_observed_pr_sha"]
        round_["step4"]["result"] = "max_rounds_exceeded"
        return {
            "round": round_num,
            "result": "max_rounds_exceeded",
            "unresolved_issue_ids": unresolved_issue_ids,
            "recommendation_issue_ids": recommendation_issue_ids,
            "settled_issues": settled_issues,
        }
    else:
        state["current_round"] += 1
        state["journal"]["round"] = state["current_round"]
        round_["step4"]["result"] = "continue"
        result = {
            "round": round_num,
            "result": "continue",
            "next_round": state["current_round"],
            "unresolved_issue_ids": unresolved_issue_ids,
            "recommendation_issue_ids": recommendation_issue_ids,
            "settled_issues": settled_issues,
        }
        if no_progress:
            result["stall_count"] = stall_count
        return result

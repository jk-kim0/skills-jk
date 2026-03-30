from datetime import datetime, timezone


def init_round(state, *, round_num, lead_agent, synced_head_sha):
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
            "applied_issue_ids": [],
            "failed_application_issue_ids": [],
            "commit_sha": None,
            "push_verified": False,
        },
        "step4": {
            "unresolved_issue_ids": [],
            "recommendation_issue_ids": [],
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


def settle_round(state, *, round_num) -> dict:
    round_ = _find_round(state, round_num)
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

    round_["step4"]["unresolved_issue_ids"] = unresolved_issue_ids
    round_["step4"]["recommendation_issue_ids"] = recommendation_issue_ids

    # Check consensus: last 2 completed rounds both have clean_pass==True
    # AND different lead agents (spec requirement)
    completed = [r for r in state["rounds"] if r["status"] == "completed"]
    last_two = completed[-2:]
    consensus_reached = (
        len(last_two) >= 2
        and all(r["clean_pass"] for r in last_two)
        and last_two[0]["lead_agent"] != last_two[1]["lead_agent"]
    )

    # Check max_rounds
    max_rounds_exceeded = state["current_round"] >= state["max_rounds"]

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
        }
    else:
        state["current_round"] += 1
        state["journal"]["round"] = state["current_round"]
        round_["step4"]["result"] = "continue"
        return {
            "round": round_num,
            "result": "continue",
            "next_round": state["current_round"],
            "unresolved_issue_ids": unresolved_issue_ids,
            "recommendation_issue_ids": recommendation_issue_ids,
        }

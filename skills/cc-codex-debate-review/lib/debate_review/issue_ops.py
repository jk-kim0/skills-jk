import hashlib
import re
from datetime import datetime, timezone


CANONICAL_KINDS = {
    1: "missing_validation",
    2: "missing_error_handling",
    3: "unbounded_loop",
    4: "wrong_target_ref",
    5: "stale_state_transition",
    6: "unused_variable",
    7: "hardcoded_value",
    8: "duplicate_logic",
    9: "security_injection",
    10: "race_condition",
    11: "resource_leak",
    12: "wrong_scope",
    13: "incorrect_algorithm",
    14: "missing_test",
    15: "doc_mismatch",
}


def latest_report_message(issue):
    """Get message from the latest report."""
    if not issue.get("reports"):
        return issue.get("severity", "unknown") + " issue"
    return issue["reports"][-1]["message"]


def normalize_message(msg: str) -> str:
    msg = msg.lower()
    # Remove file paths — require dot-extension or 2+ separators (src/foo.py, /abs/path/file)
    msg = re.sub(r"(?:[\w.-]+/){2,}[\w.-]+", " ", msg)  # 2+ separators: a/b/c
    msg = re.sub(r"[\w.-]+/[\w.-]*\.[\w]+", " ", msg)    # dot-extension: src/foo.py
    msg = re.sub(r"/[\w.-]+(?:/[\w.-]+)+", " ", msg)     # absolute: /abs/path
    # Remove line numbers (e.g. line 42, L42)
    msg = re.sub(r"\bl\d+\b", " ", msg)
    msg = re.sub(r"\bline\s+\d+\b", " ", msg)
    # Remove non-word chars except spaces
    msg = re.sub(r"[^\w\s]", " ", msg)
    # Collapse whitespace
    msg = re.sub(r"\s+", " ", msg).strip()
    return msg


def generate_issue_key(*, criterion: int, file: str, anchor: str, message: str) -> str:
    base = f"criterion:{criterion}|file:{file}|anchor:{anchor}"
    if criterion in CANONICAL_KINDS:
        return f"{base}|kind:{CANONICAL_KINDS[criterion]}"
    else:
        sha = hashlib.sha1(normalize_message(message).encode()).hexdigest()[:12]
        return f"{base}|msg:{sha}"


def _next_id(prefix: str, existing: dict) -> str:
    """Return next auto-incremented ID like isu_001, rpt_001."""
    max_n = 0
    for key in existing:
        if key.startswith(prefix + "_"):
            try:
                n = int(key[len(prefix) + 1:])
                if n > max_n:
                    max_n = n
            except ValueError:
                pass
    return f"{prefix}_{max_n + 1:03d}"


def _all_report_ids(issues: dict) -> set:
    ids = set()
    for issue in issues.values():
        for rpt in issue.get("reports", []):
            ids.add(rpt["report_id"])
    return ids


def _track_report_for_round(state, round_num, agent, report_id, issue_id):
    """Route report bookkeeping to step1 or step2 based on the reporting agent."""
    for r in state.get("rounds", []):
        if r["round"] == round_num and r["status"] == "active":
            step_key = "step1" if agent == r["lead_agent"] else "step2"
            step = r[step_key]
            if report_id not in step["report_ids"]:
                step["report_ids"].append(report_id)
            if issue_id not in step["issue_ids_touched"]:
                step["issue_ids_touched"].append(issue_id)
            break


def upsert_issue(
    state: dict,
    *,
    agent: str,
    round_num: int,
    severity: str,
    criterion: int,
    file: str,
    line: int,
    anchor: str,
    message: str,
    confirm_reopen: bool = False,
) -> dict:
    issues = state["issues"]
    issue_key = generate_issue_key(criterion=criterion, file=file, anchor=anchor, message=message)

    # Find existing issue by key
    existing_id = None
    for iid, issue in issues.items():
        if issue.get("issue_key") == issue_key:
            existing_id = iid
            break

    # Next report ID (scan all reports across all issues)
    existing_report_ids = _all_report_ids(issues)
    report_id = _next_id("rpt", {rid: None for rid in existing_report_ids})

    now = datetime.now(timezone.utc).isoformat()

    new_report = {
        "report_id": report_id,
        "agent": agent,
        "round": round_num,
        "severity": severity,
        "message": message,
        "reported_at": now,
        "status": "open",
    }

    if existing_id is None:
        issue_id = _next_id("isu", issues)
        issues[issue_id] = {
            "issue_id": issue_id,
            "issue_key": issue_key,
            "opened_by": agent,
            "introduced_in_round": round_num,
            "criterion": criterion,
            "file": file,
            "line": line,
            "anchor": anchor,
            "severity": severity,
            "consensus_status": "open",
            "application_status": "pending",
            "accepted_by": [agent],
            "rejected_by": [],
            "applied_by": None,
            "application_commit_sha": None,
            "consensus_reason": None,
            "reports": [new_report],
            "created_at": now,
            "updated_at": now,
        }
        _track_report_for_round(state, round_num, agent, report_id, issue_id)
        return {"issue_id": issue_id, "report_id": report_id, "action": "created", "issue_key": issue_key}

    # Existing issue — handle special statuses
    issue = issues[existing_id]
    consensus_status = issue.get("consensus_status")
    application_status = issue.get("application_status")

    if consensus_status == "withdrawn":
        issue["consensus_status"] = "open"
        issue["consensus_reason"] = None
        issue["application_status"] = "pending"
        issue["accepted_by"] = [agent]
        issue["reopened_in_round"] = round_num
    elif application_status == "applied":
        if not confirm_reopen:
            # Return existing reports for the orchestrator to review before reopening
            existing_messages = [
                {"agent": r["agent"], "round": r["round"], "message": r["message"]}
                for r in issue.get("reports", [])
            ]
            return {
                "issue_id": existing_id, "report_id": None,
                "action": "reopen_requires_review", "issue_key": issue_key,
                "new_message": message,
                "existing_reports": existing_messages,
            }
        issue["pre_reopen_state"] = {
            "consensus_status": issue.get("consensus_status"),
            "application_status": issue.get("application_status"),
            "applied_by": issue.get("applied_by"),
            "application_commit_sha": issue.get("application_commit_sha"),
            "accepted_by": list(issue.get("accepted_by", [])),
        }
        issue["consensus_status"] = "open"
        issue["consensus_reason"] = None
        issue["application_status"] = "pending"
        issue["applied_by"] = None
        issue["application_commit_sha"] = None
        issue["accepted_by"] = [agent]
        issue["reopened_in_round"] = round_num
    else:
        if agent not in issue["accepted_by"]:
            issue["accepted_by"].append(agent)

    issue["reports"].append(new_report)
    issue["updated_at"] = now

    _track_report_for_round(state, round_num, agent, report_id, existing_id)

    return {"issue_id": existing_id, "report_id": report_id, "action": "appended", "issue_key": issue_key}

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


def normalize_message(msg: str) -> str:
    msg = msg.lower()
    # Remove file paths (e.g. src/foo.py, /abs/path)
    msg = re.sub(r"\S+/\S+", " ", msg)
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
    }

    if existing_id is None:
        issue_id = _next_id("isu", issues)
        issues[issue_id] = {
            "issue_id": issue_id,
            "issue_key": issue_key,
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
            "reports": [new_report],
            "created_at": now,
            "updated_at": now,
        }
        return {"issue_id": issue_id, "report_id": report_id, "action": "created", "issue_key": issue_key}

    # Existing issue — handle special statuses
    issue = issues[existing_id]
    consensus_status = issue.get("consensus_status")
    application_status = issue.get("application_status")

    if consensus_status == "withdrawn":
        issue["consensus_status"] = "open"
        issue["application_status"] = "pending"
        issue["accepted_by"] = [agent]
    elif application_status == "applied":
        issue["consensus_status"] = "open"
        issue["application_status"] = "pending"
        issue["applied_by"] = None
        issue["application_commit_sha"] = None
        issue["accepted_by"] = [agent]
    else:
        if agent not in issue["accepted_by"]:
            issue["accepted_by"].append(agent)

    issue["reports"].append(new_report)
    issue["updated_at"] = now

    return {"issue_id": existing_id, "report_id": report_id, "action": "appended", "issue_key": issue_key}

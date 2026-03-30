import argparse
import json
import os
import shutil
import sys

from debate_review.config import load_config
from debate_review.gh import gh_json
from debate_review.application import (
    record_application_phase1,
    record_application_phase2,
    record_application_phase3,
)
from debate_review.cross_verification import record_cross_verification, resolve_rebuttals
from debate_review.issue_ops import upsert_issue
from debate_review.round_ops import init_round, record_verdict, settle_round
from debate_review.comment import post_comment
from debate_review.sync import sync_head
from debate_review.state import (
    create_initial_state,
    load_state,
    save_state,
    state_file_path,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="debate-review")
    subparsers = parser.add_subparsers(dest="command")

    # init subcommand
    init_parser = subparsers.add_parser("init", help="Initialize a debate-review session")
    init_parser.add_argument("--repo", required=True, help="owner/repo")
    init_parser.add_argument("--pr", required=True, type=int, help="PR number")
    init_parser.add_argument("--repo-root", help="Path to repo root")
    init_parser.add_argument("--config", help="Path to config YAML")
    init_parser.add_argument("--max-rounds", type=int, help="Override max_rounds from config")
    init_parser.add_argument("--dry-run", action="store_true", help="Dry run mode")

    # show subcommand
    show_parser = subparsers.add_parser("show", help="Show debate-review state")
    show_parser.add_argument("--state-file", help="Path to state file")
    show_parser.add_argument("--json", action="store_true", dest="as_json", help="Output as JSON")

    # upsert-issue subcommand
    p_upsert = subparsers.add_parser("upsert-issue")
    p_upsert.add_argument("--state-file", required=True)
    p_upsert.add_argument("--agent", required=True, choices=["cc", "codex"])
    p_upsert.add_argument("--round", type=int, required=True)
    p_upsert.add_argument("--severity", required=True, choices=["critical", "warning", "suggestion"])
    p_upsert.add_argument("--criterion", type=int, required=True)
    p_upsert.add_argument("--file", required=True)
    p_upsert.add_argument("--line", type=int, required=True)
    p_upsert.add_argument("--anchor", required=True)
    p_upsert.add_argument("--message", required=True)

    # init-round subcommand
    p_initr = subparsers.add_parser("init-round", help="Initialize a new round")
    p_initr.add_argument("--state-file", required=True)
    p_initr.add_argument("--round", type=int, required=True)
    p_initr.add_argument("--lead-agent", required=True, choices=["cc", "codex"])
    p_initr.add_argument("--synced-head-sha", required=True)

    # record-verdict subcommand
    p_verdict = subparsers.add_parser("record-verdict")
    p_verdict.add_argument("--state-file", required=True)
    p_verdict.add_argument("--round", type=int, required=True)
    p_verdict.add_argument("--verdict", required=True, choices=["has_findings", "no_findings_mergeable"])

    # settle-round subcommand
    p_settle = subparsers.add_parser("settle-round")
    p_settle.add_argument("--state-file", required=True)
    p_settle.add_argument("--round", type=int, required=True)

    # record-cross-verification subcommand
    p_xcv = subparsers.add_parser("record-cross-verification")
    p_xcv.add_argument("--state-file", required=True)
    p_xcv.add_argument("--round", type=int, required=True)
    p_xcv.add_argument("--verifications", required=True)

    # resolve-rebuttals subcommand
    p_rr = subparsers.add_parser("resolve-rebuttals")
    p_rr.add_argument("--state-file", required=True)
    p_rr.add_argument("--round", type=int, required=True)
    p_rr.add_argument("--step", required=True, choices=["1a", "3"])
    p_rr.add_argument("--decisions", required=True)

    # sync-head subcommand
    p_sync = subparsers.add_parser("sync-head")
    p_sync.add_argument("--state-file", required=True)

    # post-comment subcommand
    p_comment = subparsers.add_parser("post-comment")
    p_comment.add_argument("--state-file", required=True)
    p_comment.add_argument("--no-comment", action="store_true")

    # record-application subcommand
    p_app = subparsers.add_parser("record-application")
    p_app.add_argument("--state-file", required=True)
    p_app.add_argument("--round", type=int, required=True)
    p_app.add_argument("--applied-issues", default=None)
    p_app.add_argument("--failed-issues", default=None)
    p_app.add_argument("--commit-sha", default=None)
    p_app.add_argument("--verify-push", action="store_true")

    return parser


def _error_exit(message):
    """Print JSON error and exit with code 1."""
    print(json.dumps({"error": message}))
    sys.exit(1)


def _resolve_repo_root(repo, repo_root_arg):
    if repo_root_arg:
        return repo_root_arg
    workspace_root = os.environ.get("WORKSPACE_ROOT")
    repo_name = repo.split("/")[-1]
    if workspace_root:
        return os.path.join(workspace_root, repo_name)
    return os.path.expanduser(f"~/workspace/{repo_name}")


def cmd_init(args):
    repo = args.repo
    pr_number = args.pr
    dry_run = args.dry_run

    # Fetch PR metadata from GitHub
    pr_data = gh_json(
        "pr", "view", str(pr_number),
        "--repo", repo,
        "--json", "headRefName,headRefOid,headRepositoryOwner",
    )
    head_ref_name = pr_data["headRefName"]
    head_sha = pr_data["headRefOid"]
    head_repo_owner = pr_data["headRepositoryOwner"]["login"]
    repo_owner = repo.split("/")[0]
    is_fork = head_repo_owner != repo_owner

    repo_root = _resolve_repo_root(repo, args.repo_root)

    # Load config for max_rounds
    config = load_config(args.config)
    max_rounds = args.max_rounds if args.max_rounds is not None else config.get("max_rounds", 10)

    state_path = state_file_path(repo, pr_number, dry_run)
    existing = load_state(state_path)

    if existing is None:
        state = create_initial_state(
            repo=repo,
            repo_root=repo_root,
            pr_number=pr_number,
            is_fork=is_fork,
            head_sha=head_sha,
            pr_branch_name=head_ref_name,
            max_rounds=max_rounds,
            dry_run=dry_run,
        )
        save_state(state, state_path)
        result_status = "created"
        current_round = state["current_round"]
    elif existing["status"] == "in_progress":
        result_status = "resumed"
        current_round = existing["current_round"]
        is_fork = existing["is_fork"]
        dry_run = existing["dry_run"]
    else:
        # Terminal state — use terminal_sha for session identity
        existing_sha = existing["head"].get("terminal_sha") or existing["head"]["last_observed_pr_sha"]
        if existing_sha == head_sha:
            print(json.dumps({
                "state_file": state_path,
                "status": "already_terminal",
                "current_round": existing["current_round"],
                "is_fork": existing["is_fork"],
                "dry_run": existing["dry_run"],
            }))
            return
        else:
            # Archive old state and create new
            archive_sha = existing_sha[:8]
            archive_path = f"{state_path}.{archive_sha}.archived"
            shutil.copy2(state_path, archive_path)
            state = create_initial_state(
                repo=repo,
                repo_root=repo_root,
                pr_number=pr_number,
                is_fork=is_fork,
                head_sha=head_sha,
                pr_branch_name=head_ref_name,
                max_rounds=max_rounds,
                dry_run=dry_run,
            )
            save_state(state, state_path)
            result_status = "created"
            current_round = state["current_round"]

    print(json.dumps({
        "state_file": state_path,
        "status": result_status,
        "current_round": current_round,
        "is_fork": is_fork,
        "dry_run": dry_run,
    }))


def cmd_show(args):
    state_path = args.state_file
    if not state_path:
        _error_exit("--state-file is required")

    from debate_review.state import load_state
    state = load_state(state_path)
    if state is None:
        _error_exit(f"No state file found at {state_path}")

    if args.as_json:
        print(json.dumps(state, indent=2))
    else:
        print(f"Repo:          {state['repo']}")
        print(f"PR:            #{state['pr_number']}")
        print(f"Status:        {state['status']}")
        print(f"Round:         {state['current_round']} / {state['max_rounds']}")
        print(f"Is fork:       {state['is_fork']}")
        print(f"Dry run:       {state['dry_run']}")
        print(f"Started at:    {state['started_at']}")
        print(f"Head SHA:      {state['head']['last_observed_pr_sha']}")
        print(f"Branch:        {state['head']['pr_branch_name']}")
        open_count = sum(1 for i in state.get("issues", {}).values() if i.get("consensus_status") == "open")
        print(f"Open issues:   {open_count}")


def cmd_init_round(args):
    state = load_state(args.state_file)
    if state is None:
        _error_exit(f"No state file found at {args.state_file}")
    init_round(state, round_num=args.round, lead_agent=args.lead_agent, synced_head_sha=args.synced_head_sha)
    state["journal"]["round"] = args.round
    state["journal"]["step"] = "step0_sync"
    save_state(state, args.state_file)
    print(json.dumps({"round": args.round, "lead_agent": args.lead_agent}))


def cmd_upsert_issue(args):
    state = load_state(args.state_file)
    if state is None:
        _error_exit(f"No state file found at {args.state_file}")
    state["journal"]["step"] = "step1_lead_review"
    result = upsert_issue(
        state,
        agent=args.agent,
        round_num=args.round,
        severity=args.severity,
        criterion=args.criterion,
        file=args.file,
        line=args.line,
        anchor=args.anchor,
        message=args.message,
    )
    save_state(state, args.state_file)
    print(json.dumps(result))


def cmd_record_verdict(args):
    state = load_state(args.state_file)
    if state is None:
        _error_exit(f"No state file found at {args.state_file}")
    state["journal"]["step"] = "step1_lead_review"
    result = record_verdict(state, round_num=args.round, verdict=args.verdict)
    save_state(state, args.state_file)
    print(json.dumps(result))


def cmd_settle_round(args):
    state = load_state(args.state_file)
    if state is None:
        _error_exit(f"No state file found at {args.state_file}")
    state["journal"]["step"] = "step4_settle"
    result = settle_round(state, round_num=args.round)
    save_state(state, args.state_file)
    print(json.dumps(result))


def cmd_record_cross_verification(args):
    state = load_state(args.state_file)
    if state is None:
        _error_exit(f"No state file found at {args.state_file}")
    try:
        verifications = json.loads(args.verifications)
    except json.JSONDecodeError as e:
        _error_exit(f"Invalid JSON for --verifications: {e}")
    state["journal"]["step"] = "step2_cross_verify"
    result = record_cross_verification(state, round_num=args.round, verifications=verifications)
    save_state(state, args.state_file)
    print(json.dumps(result))


def cmd_resolve_rebuttals(args):
    state = load_state(args.state_file)
    if state is None:
        _error_exit(f"No state file found at {args.state_file}")
    try:
        decisions = json.loads(args.decisions)
    except json.JSONDecodeError as e:
        _error_exit(f"Invalid JSON for --decisions: {e}")
    step_map = {"1a": "step1a_rebuttal_response", "3": "step3_lead_respond"}
    state["journal"]["step"] = step_map.get(args.step, state["journal"]["step"])
    result = resolve_rebuttals(state, round_num=args.round, step=args.step, decisions=decisions)
    save_state(state, args.state_file)
    print(json.dumps(result))


def cmd_sync_head(args):
    state = load_state(args.state_file)
    if state is None:
        _error_exit(f"No state file found at {args.state_file}")
    state["journal"]["step"] = "step0_sync"
    result = sync_head(state)
    save_state(state, args.state_file)
    print(json.dumps(result))


def cmd_post_comment(args):
    state = load_state(args.state_file)
    if state is None:
        _error_exit(f"No state file found at {args.state_file}")
    result = post_comment(state, no_comment=args.no_comment)
    save_state(state, args.state_file)
    print(json.dumps(result))


def cmd_record_application(args):
    state = load_state(args.state_file)
    if state is None:
        _error_exit(f"No state file found at {args.state_file}")

    if args.verify_push:
        result = record_application_phase3(state, round_num=args.round)
    elif args.commit_sha:
        result = record_application_phase2(state, round_num=args.round, commit_sha=args.commit_sha)
    elif args.applied_issues is not None:
        try:
            applied = json.loads(args.applied_issues)
            failed = json.loads(args.failed_issues) if args.failed_issues else []
        except json.JSONDecodeError as e:
            _error_exit(f"Invalid JSON: {e}")
        result = record_application_phase1(
            state, round_num=args.round,
            applied_issue_ids=applied, failed_issue_ids=failed,
        )
    else:
        _error_exit("Must provide --applied-issues, --commit-sha, or --verify-push")

    save_state(state, args.state_file)
    print(json.dumps(result))


def main():
    parser = build_parser()
    args = parser.parse_args()

    commands = {
        "init": cmd_init,
        "show": cmd_show,
        "init-round": cmd_init_round,
        "upsert-issue": cmd_upsert_issue,
        "record-verdict": cmd_record_verdict,
        "settle-round": cmd_settle_round,
        "record-cross-verification": cmd_record_cross_verification,
        "resolve-rebuttals": cmd_resolve_rebuttals,
        "record-application": cmd_record_application,
        "sync-head": cmd_sync_head,
        "post-comment": cmd_post_comment,
    }

    if args.command in commands:
        try:
            commands[args.command](args)
        except ValueError as e:
            _error_exit(str(e))
    else:
        parser.print_help()

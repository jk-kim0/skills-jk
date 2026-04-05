import argparse
import json
import os
import shutil
import sys
import tempfile

from debate_review.config import load_config
from debate_review.timing import ensure_timing_fields, record_step_timing
from debate_review.context import build_context
from debate_review.prompt import build_prompt
from debate_review.reporting import generate_sessions_report, render_sessions_report_markdown
from debate_review.gh import gh_json
from debate_review.application import (
    build_commit_message,
    record_application_phase1,
    record_application_phase2,
    record_application_phase3,
)
from debate_review.cross_verification import record_cross_verification, resolve_rebuttals
from debate_review.issue_ops import upsert_issue, withdraw_issue
from debate_review.round_ops import init_round, record_verdict, settle_round
from debate_review.comment import post_comment
from debate_review.sync import sync_head
from debate_review.error_log import save_error_log
from debate_review.agent_cleanup import terminate_agents
from debate_review.follow_through import create_failure_issue, cleanup_worktree
from debate_review.state import (
    append_ledger,
    StateCorruptedError,
    create_initial_state,
    determine_next_step,
    ensure_persistent_agents,
    load_state,
    mark_failed,
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
    p_upsert.add_argument("--confirm-reopen", action="store_true",
                          help="Confirm reopening an already-applied issue")

    # init-round subcommand
    p_initr = subparsers.add_parser("init-round", help="Initialize a new round")
    p_initr.add_argument("--state-file", required=True)
    p_initr.add_argument("--round", type=int, required=True)
    p_initr.add_argument("--lead-agent", choices=["cc", "codex"], default=None)
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

    # mark-failed subcommand
    p_fail = subparsers.add_parser("mark-failed", help="Mark session as terminal failed")
    p_fail.add_argument("--state-file", required=True)
    p_fail.add_argument("--error-message", default="Unknown error")
    p_fail.add_argument("--failed-command", default="unknown", help="Command that caused the failure")

    # append-ledger subcommand
    p_ledger = subparsers.add_parser("append-ledger", help="Append entries to debate_ledger")
    p_ledger.add_argument("--state-file", required=True)
    p_ledger.add_argument("--entries", required=True, help="JSON array of ledger entries")

    # withdraw-issue subcommand
    p_withdraw = subparsers.add_parser("withdraw-issue", help="Withdraw an open issue by orchestrator/agent decision")
    p_withdraw.add_argument("--state-file", required=True)
    p_withdraw.add_argument("--issue-id", required=True)
    p_withdraw.add_argument("--agent", required=True)
    p_withdraw.add_argument("--round", required=True, type=int)
    p_withdraw.add_argument("--reason", required=True)

    # test-error subcommand
    p_test = subparsers.add_parser("test-error", help="Trigger an intentional error for pipeline verification")
    p_test.add_argument("--message", default="Intentional test error for pipeline verification")

    # build-context subcommand
    p_ctx = subparsers.add_parser("build-context", help="Build review context from state")
    p_ctx.add_argument("--state-file", required=True)
    p_ctx.add_argument("--round", type=int, required=True)

    # record-agent-sessions subcommand
    p_agents = subparsers.add_parser(
        "record-agent-sessions",
        help="Persist persistent-mode agent identifiers for restart/resume",
    )
    p_agents.add_argument("--state-file", required=True)
    p_agents.add_argument("--cc-agent-id")
    p_agents.add_argument("--codex-session-id")

    # build-commit-message subcommand
    p_bcm = subparsers.add_parser("build-commit-message", help="Build commit message from applied issues")
    p_bcm.add_argument("--state-file", required=True)
    p_bcm.add_argument("--round", type=int, required=True)
    p_bcm.add_argument("--applied-issues", default=None)

    # build-prompt subcommand
    p_bp = subparsers.add_parser("build-prompt", help="Build and persist agent prompt file")
    p_bp.add_argument("--state-file", required=True)
    p_bp.add_argument("--agent", required=True, choices=["cc", "codex"])
    p_bp.add_argument("--step", required=True, choices=["init", "1", "2", "3"])
    p_bp.add_argument("--round", type=int, default=None)
    p_bp.add_argument("--extra", default=None, help="Additional context to append")

    # create-failure-issue subcommand
    p_cfi = subparsers.add_parser("create-failure-issue", help="Create GitHub issue on failure/stall")
    p_cfi.add_argument("--state-file", required=True)

    # cleanup-worktree subcommand
    p_cw = subparsers.add_parser("cleanup-worktree", help="Remove debate worktree")
    p_cw.add_argument("--state-file", required=True)

    # terminate-agents subcommand
    p_ta = subparsers.add_parser("terminate-agents", help="Kill persistent agent processes")
    p_ta.add_argument("--state-file", required=True)

    # record-application subcommand
    p_app = subparsers.add_parser("record-application")
    p_app.add_argument("--state-file", required=True)
    p_app.add_argument("--round", type=int, required=True)
    p_app.add_argument("--applied-issues", default=None)
    p_app.add_argument("--failed-issues", default=None)
    p_app.add_argument("--commit-sha", default=None)
    p_app.add_argument("--verify-push", action="store_true")

    # report-sessions subcommand
    p_report = subparsers.add_parser("report-sessions", help="Generate a full-session timing report")
    p_report.add_argument("--state-dir", default=os.path.expanduser("~/.claude/debate-state"))
    p_report.add_argument("--claude-projects-root", default=os.path.expanduser("~/.claude/projects"))
    p_report.add_argument("--codex-sessions-root", default=os.path.expanduser("~/.codex/sessions"))
    p_report.add_argument("--format", choices=["markdown", "json"], default="markdown")
    p_report.add_argument("--output", default=None)

    return parser


def _error_exit(message):
    """Print JSON error and exit with code 1."""
    print(json.dumps({"error": message}))
    sys.exit(1)



def _dry_run_skip(state, *, command, **payload):
    result = {"action": "dry_run", "command": command, "current_round": state["current_round"]}
    result.update(payload)
    return result


def _normalize_failed_issues(raw_failed_issues):
    return _normalize_issue_ids(raw_failed_issues, flag_name="--failed-issues", allow_objects=True)

def _normalize_issue_ids(raw_issue_ids, *, flag_name, allow_objects=False):
    issue_ids = json.loads(raw_issue_ids) if raw_issue_ids else []
    if not isinstance(issue_ids, list):
        raise ValueError(f"{flag_name} must decode to a JSON array")

    normalized = []
    for item in issue_ids:
        if isinstance(item, str):
            normalized.append(item)
            continue
        if allow_objects and isinstance(item, dict) and isinstance(item.get("issue_id"), str):
            normalized.append(item["issue_id"])
            continue
        if allow_objects:
            raise ValueError(
                f"{flag_name} entries must be issue ID strings or objects with string field 'issue_id'"
            )
        raise ValueError(f"{flag_name} entries must be issue ID strings")
    return normalized


def _resolve_repo_root(repo, repo_root_arg):
    if repo_root_arg:
        return repo_root_arg
    workspace_root = os.environ.get("WORKSPACE_ROOT")
    repo_name = repo.split("/")[-1]
    if workspace_root:
        return os.path.join(workspace_root, repo_name)
    return os.path.expanduser(f"~/workspace/{repo_name}")


def _orchestrator_checkpoint_path(state_file: str) -> str:
    state_name = os.path.basename(state_file)
    return os.path.join(os.path.expanduser("~"), ".claude", "debate-state", "orchestrator", f"{state_name}.checkpoint.json")


def _clear_orchestrator_checkpoint(state_file: str) -> None:
    checkpoint_path = _orchestrator_checkpoint_path(state_file)
    if os.path.exists(checkpoint_path):
        os.remove(checkpoint_path)


def _migrate_resumed_state(existing: dict, *, language: str) -> bool:
    needs_save = False
    if "language" not in existing:
        existing["language"] = language
        needs_save = True
    if ensure_persistent_agents(existing):
        needs_save = True
    rounds_before = json.dumps(existing.get("rounds", []), sort_keys=True)
    journal_before = json.dumps(existing.get("journal", {}), sort_keys=True)
    ensure_timing_fields(existing)
    if rounds_before != json.dumps(existing.get("rounds", []), sort_keys=True):
        needs_save = True
    if journal_before != json.dumps(existing.get("journal", {}), sort_keys=True):
        needs_save = True
    return needs_save


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

    # Load config-driven session defaults
    config = load_config(args.config)
    max_rounds = args.max_rounds if args.max_rounds is not None else config.get("max_rounds", 10)
    language = str(config.get("language", "en"))
    codex_sandbox = str(config.get("codex_sandbox", "danger-full-access"))
    state_path = state_file_path(repo, pr_number, dry_run)
    existing = load_state(state_path)

    if existing is None:
        _clear_orchestrator_checkpoint(state_path)
        state = create_initial_state(
            repo=repo,
            repo_root=repo_root,
            pr_number=pr_number,
            is_fork=is_fork,
            head_sha=head_sha,
            pr_branch_name=head_ref_name,
            max_rounds=max_rounds,
            language=language,
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
        needs_save = _migrate_resumed_state(existing, language=language)
        if needs_save:
            save_state(existing, state_path)
    else:
        # Terminal state — use terminal_sha for session identity
        existing_sha = existing["head"].get("terminal_sha") or existing["head"]["last_observed_pr_sha"]
        if existing_sha == head_sha:
            checkpoint_path = _orchestrator_checkpoint_path(state_path)
            if os.path.exists(checkpoint_path) and existing["status"] in ("failed",):
                existing["status"] = "in_progress"
                existing["final_outcome"] = None
                existing["finished_at"] = None
                existing["head"]["terminal_sha"] = None
                existing.pop("error_message", None)
                _migrate_resumed_state(existing, language=language)
                save_state(existing, state_path)
                result_status = "resumed"
                current_round = existing["current_round"]
                is_fork = existing["is_fork"]
                dry_run = existing["dry_run"]
            else:
                _error_exit("Session already completed for this HEAD")
        else:
            # Archive old state and create new
            archive_sha = existing_sha[:8]
            archive_path = f"{state_path}.{archive_sha}.archived"
            shutil.copy2(state_path, archive_path)
            _clear_orchestrator_checkpoint(state_path)
            state = create_initial_state(
                repo=repo,
                repo_root=repo_root,
                pr_number=pr_number,
                is_fork=is_fork,
                head_sha=head_sha,
                pr_branch_name=head_ref_name,
                max_rounds=max_rounds,
                language=language,
                dry_run=dry_run,
            )
            save_state(state, state_path)
            result_status = "created"
            current_round = state["current_round"]

    result = {
        "state_file": state_path,
        "status": result_status,
        "current_round": current_round,
        "is_fork": is_fork,
        "dry_run": dry_run,
        "codex_sandbox": codex_sandbox,
        "language": existing.get("language", language) if result_status == "resumed" else language,
    }
    if result_status == "resumed":
        resume_info = determine_next_step(existing)
        result["next_step"] = resume_info["next_step"]
        if "resume_context" in resume_info:
            result["resume_context"] = resume_info["resume_context"]
    print(json.dumps(result))


def cmd_record_agent_sessions(args):
    state = load_state(args.state_file)
    if state is None:
        _error_exit(f"No state file found at {args.state_file}")
    if args.cc_agent_id is None and args.codex_session_id is None:
        _error_exit("Must provide --cc-agent-id and/or --codex-session-id")

    if state.get("dry_run"):
        print(json.dumps(_dry_run_skip(state, command="record-agent-sessions")))
        return

    ensure_persistent_agents(state)
    sessions = state["persistent_agents"]
    if args.cc_agent_id is not None:
        sessions["cc_agent_id"] = args.cc_agent_id
    if args.codex_session_id is not None:
        sessions["codex_session_id"] = args.codex_session_id

    save_state(state, args.state_file)
    print(json.dumps(sessions))


def cmd_show(args):
    state_path = args.state_file
    if not state_path:
        _error_exit("--state-file is required")

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
    lead_agent = args.lead_agent or ("codex" if args.round % 2 == 1 else "cc")
    cross_verifier = "cc" if lead_agent == "codex" else "codex"
    worktree_path = os.path.join(state["repo_root"], ".worktrees", f"debate-pr-{state['pr_number']}")
    if state.get("dry_run"):
        print(json.dumps(_dry_run_skip(
            state,
            command="init-round",
            round=args.round,
            lead_agent=lead_agent,
            cross_verifier=cross_verifier,
            worktree_path=worktree_path,
            head_branch=state["head"]["pr_branch_name"],
            synced_head_sha=args.synced_head_sha,
        )))
        return
    init_round(state, round_num=args.round, lead_agent=lead_agent, synced_head_sha=args.synced_head_sha)
    state["journal"]["round"] = args.round
    state["journal"]["step"] = "step0_sync"
    record_step_timing(state, "step0_sync")
    state["journal"]["phase1_completed"] = False
    save_state(state, args.state_file)
    print(json.dumps({
        "round": args.round,
        "lead_agent": lead_agent,
        "cross_verifier": cross_verifier,
        "worktree_path": worktree_path,
        "head_branch": state["head"]["pr_branch_name"],
        "synced_head_sha": args.synced_head_sha,
    }))


def cmd_upsert_issue(args):
    state = load_state(args.state_file)
    if state is None:
        _error_exit(f"No state file found at {args.state_file}")
    if state.get("dry_run"):
        print(json.dumps(_dry_run_skip(state, command="upsert-issue", round=args.round, agent=args.agent)))
        return
    state["journal"]["step"] = "step1_lead_review"
    record_step_timing(state, "step1_lead_review")
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
        confirm_reopen=args.confirm_reopen,
    )
    save_state(state, args.state_file)
    print(json.dumps(result))


def cmd_record_verdict(args):
    state = load_state(args.state_file)
    if state is None:
        _error_exit(f"No state file found at {args.state_file}")
    if state.get("dry_run"):
        print(json.dumps(_dry_run_skip(state, command="record-verdict", round=args.round, verdict=args.verdict)))
        return
    state["journal"]["step"] = "step1_lead_review"
    record_step_timing(state, "step1_lead_review")
    result = record_verdict(state, round_num=args.round, verdict=args.verdict)
    save_state(state, args.state_file)
    print(json.dumps(result))


def cmd_settle_round(args):
    state = load_state(args.state_file)
    if state is None:
        _error_exit(f"No state file found at {args.state_file}")
    if state.get("dry_run"):
        print(json.dumps(_dry_run_skip(state, command="settle-round", round=args.round)))
        return
    state["journal"]["step"] = "step4_settle"
    record_step_timing(state, "step4_settle")
    result = settle_round(state, round_num=args.round)
    if result.get("result") in ("consensus_reached", "max_rounds_exceeded", "stalled"):
        terminate_agents(state)
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
    if state.get("dry_run"):
        print(json.dumps(_dry_run_skip(state, command="record-cross-verification", round=args.round)))
        return
    state["journal"]["step"] = "step2_cross_review"
    record_step_timing(state, "step2_cross_review")
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
    if state.get("dry_run"):
        print(json.dumps(_dry_run_skip(state, command="resolve-rebuttals", round=args.round, step=args.step)))
        return
    step_map = {"1a": "step1_lead_review", "3": "step3_lead_apply"}
    new_step = step_map.get(args.step, state["journal"]["step"])
    state["journal"]["step"] = new_step
    record_step_timing(state, new_step)
    result = resolve_rebuttals(state, round_num=args.round, step=args.step, decisions=decisions)
    save_state(state, args.state_file)
    print(json.dumps(result))


def cmd_sync_head(args):
    state = load_state(args.state_file)
    if state is None:
        _error_exit(f"No state file found at {args.state_file}")
    state["journal"]["step"] = "step0_sync"
    record_step_timing(state, "step0_sync")
    result = sync_head(state)
    if not state.get("dry_run"):
        save_state(state, args.state_file)
    print(json.dumps(result))


def cmd_post_comment(args):
    state = load_state(args.state_file)
    if state is None:
        _error_exit(f"No state file found at {args.state_file}")
    result = post_comment(state, no_comment=args.no_comment)
    if not state.get("dry_run"):
        save_state(state, args.state_file)
    print(json.dumps(result))


def cmd_record_application(args):
    state = load_state(args.state_file)
    if state is None:
        _error_exit(f"No state file found at {args.state_file}")
    if state.get("dry_run"):
        print(json.dumps(_dry_run_skip(state, command="record-application", round=args.round)))
        return

    result = None
    if args.applied_issues is not None:
        try:
            applied = json.loads(args.applied_issues)
            failed = _normalize_failed_issues(args.failed_issues)
        except (json.JSONDecodeError, ValueError) as e:
            _error_exit(f"Invalid JSON: {e}")
        result = record_application_phase1(
            state, round_num=args.round,
            applied_issue_ids=applied, failed_issue_ids=failed,
        )

    if args.commit_sha:
        result = record_application_phase2(state, round_num=args.round, commit_sha=args.commit_sha)

    if args.verify_push:
        result = record_application_phase3(state, round_num=args.round)

    if result is None:
        _error_exit("Must provide --applied-issues, --commit-sha, or --verify-push")

    save_state(state, args.state_file)
    print(json.dumps(result))


def cmd_build_commit_message(args):
    state = load_state(args.state_file)
    if state is None:
        _error_exit(f"No state file found at {args.state_file}")
    try:
        applied_ids = _normalize_issue_ids(
            args.applied_issues,
            flag_name="--applied-issues",
        ) if args.applied_issues is not None else None
        msg = build_commit_message(state, round_num=args.round, applied_issue_ids=applied_ids)
    except ValueError as e:
        _error_exit(str(e))
    print(msg)


def cmd_build_context(args):
    state = load_state(args.state_file)
    if state is None:
        _error_exit(f"No state file found at {args.state_file}")
    result = build_context(state, round_num=args.round)
    print(json.dumps(result))


def cmd_mark_failed(args):
    state = load_state(args.state_file)
    if state is None:
        _error_exit(f"No state file found at {args.state_file}")
    if state.get("dry_run"):
        print(json.dumps(_dry_run_skip(state, command="mark-failed", error_message=args.error_message)))
        return
    mark_failed(state, error_message=args.error_message)
    terminate_agents(state)
    save_state(state, args.state_file)
    try:
        log_path = save_error_log(
            command=args.failed_command,
            error_message=args.error_message,
            state_file=args.state_file,
        )
    except OSError:
        log_path = None
    result = {"status": "failed", "error_message": args.error_message}
    if log_path:
        result["error_log"] = log_path
    print(json.dumps(result))


def cmd_test_error(args):
    raise RuntimeError(args.message)


def cmd_append_ledger(args):
    state = load_state(args.state_file)
    if state is None:
        _error_exit(f"No state file found at {args.state_file}")
    if state.get("dry_run"):
        print(json.dumps(_dry_run_skip(state, command="append-ledger")))
        return
    try:
        entries = json.loads(args.entries)
    except json.JSONDecodeError as e:
        _error_exit(f"Invalid JSON for --entries: {e}")
    if not isinstance(entries, list):
        _error_exit("--entries must be a JSON array")
    try:
        result = append_ledger(state, entries=entries)
    except (KeyError, TypeError) as e:
        _error_exit(f"Malformed ledger entry: {e}")
    save_state(state, args.state_file)
    print(json.dumps(result))


def cmd_withdraw_issue(args):
    state = load_state(args.state_file)
    if state is None:
        _error_exit(f"No state file found at {args.state_file}")
    if state.get("dry_run"):
        print(json.dumps(_dry_run_skip(state, command="withdraw-issue", issue_id=args.issue_id)))
        return
    try:
        result = withdraw_issue(state, issue_id=args.issue_id, agent=args.agent, round_num=args.round, reason=args.reason)
    except ValueError as e:
        _error_exit(str(e))
    save_state(state, args.state_file)
    print(json.dumps(result))


def cmd_create_failure_issue(args):
    state = load_state(args.state_file)
    if state is None:
        _error_exit(f"No state file found at {args.state_file}")
    result = create_failure_issue(state)
    print(json.dumps(result))


def cmd_cleanup_worktree(args):
    state = load_state(args.state_file)
    if state is None:
        _error_exit(f"No state file found at {args.state_file}")
    result = cleanup_worktree(state)
    print(json.dumps(result))


def cmd_terminate_agents(args):
    state = load_state(args.state_file)
    if state is None:
        _error_exit(f"No state file found at {args.state_file}")
    result = terminate_agents(state)
    print(json.dumps(result))


def cmd_build_prompt(args):
    state = load_state(args.state_file)
    if state is None:
        _error_exit(f"No state file found at {args.state_file}")
    # cli.py is at lib/debate_review/cli.py, skill root is 3 levels up
    skill_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    result = build_prompt(
        state,
        agent=args.agent,
        step=args.step,
        round_num=args.round,
        skill_root=skill_root,
        extra=args.extra,
        state_file=args.state_file,
    )
    output = {"prompt_file": result["prompt_file"]}
    # For non-init steps, write the step message to a separate file so callers
    # can read it directly without shell-variable corruption (zsh echo interprets
    # \\n as newlines, breaking JSON round-tripping of multiline markdown content).
    if args.step != "init":
        msg_fd, msg_path = tempfile.mkstemp(prefix="debate-msg-", suffix=".md")
        with os.fdopen(msg_fd, "w") as f:
            f.write(result["message"])
        output["message_file"] = msg_path
    print(json.dumps(output))


def cmd_report_sessions(args):
    report = generate_sessions_report(
        state_dir=args.state_dir,
        claude_projects_root=args.claude_projects_root,
        codex_sessions_root=args.codex_sessions_root,
    )
    rendered = render_sessions_report_markdown(report) if args.format == "markdown" else json.dumps(report, indent=2)
    if args.output:
        output_path = os.path.abspath(args.output)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            f.write(rendered)
        return
    print(rendered)


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
        "record-agent-sessions": cmd_record_agent_sessions,
        "build-commit-message": cmd_build_commit_message,
        "build-context": cmd_build_context,
        "build-prompt": cmd_build_prompt,
        "report-sessions": cmd_report_sessions,
        "create-failure-issue": cmd_create_failure_issue,
        "cleanup-worktree": cmd_cleanup_worktree,
        "terminate-agents": cmd_terminate_agents,
        "test-error": cmd_test_error,
        "mark-failed": cmd_mark_failed,
        "withdraw-issue": cmd_withdraw_issue,
        "append-ledger": cmd_append_ledger,
        "sync-head": cmd_sync_head,
        "post-comment": cmd_post_comment,
    }

    if args.command in commands:
        try:
            commands[args.command](args)
        except (RuntimeError, ValueError, StateCorruptedError) as e:
            _error_exit(str(e))
    else:
        parser.print_help()

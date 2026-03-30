import argparse
import json
import os
import shutil

from debate_review.config import load_config
from debate_review.gh import gh_json
from debate_review.issue_ops import upsert_issue
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

    return parser


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
        # Terminal state
        existing_sha = existing["head"]["last_observed_pr_sha"]
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
            archive_path = state_path + ".archived"
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
        print("Error: --state-file is required", flush=True)
        return

    from debate_review.state import load_state
    state = load_state(state_path)
    if state is None:
        print(f"No state file found at {state_path}")
        return

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


def cmd_upsert_issue(args):
    state = load_state(args.state_file)
    if state is None:
        print(json.dumps({"error": f"No state file found at {args.state_file}"}))
        return
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


def main():
    parser = build_parser()
    args = parser.parse_args()

    commands = {
        "init": cmd_init,
        "show": cmd_show,
        "upsert-issue": cmd_upsert_issue,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()

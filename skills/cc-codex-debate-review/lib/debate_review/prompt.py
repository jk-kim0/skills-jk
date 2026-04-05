"""Build and manage persistent prompt files for debate-review agents."""

import json
import os

from .context import (
    build_applicable_issues,
    build_cross_findings,
    build_cross_rebuttals,
    build_debate_ledger_text,
    build_lead_reports,
    build_open_issues,
    build_pending_rebuttals,
    build_potential_applicable_issues,
)

_PROMPTS_DIR = os.path.join(os.path.expanduser("~"), ".claude", "debate-state", "prompts")

_STEP_TEMPLATE_FILES = {
    "1": "prompt-step-1.md",
    "2": "prompt-step-2.md",
    "3": "prompt-step-3.md",
}


def _prompts_dir():
    os.makedirs(_PROMPTS_DIR, exist_ok=True)
    return _PROMPTS_DIR


def prompt_file_path(repo, pr_number, agent, *, dry_run=False):
    """Return the persistent prompt file path for an agent."""
    slug = repo.replace("/", "-")
    suffix = ".dry-run" if dry_run else ""
    return os.path.join(_prompts_dir(), f"{slug}-{pr_number}-{agent}{suffix}.md")


def _read_template(skill_root, filename):
    path = os.path.join(skill_root, filename)
    with open(path) as f:
        return f.read()


def _substitute(template, placeholders):
    result = template
    for key, value in placeholders.items():
        result = result.replace(key, str(value))
    return result


def _worktree_path(state):
    head = state.get("head", {})
    if head.get("worktree_path"):
        return head["worktree_path"]
    repo_root = state.get("repo_root")
    pr_number = state.get("pr_number")
    if repo_root is None or pr_number is None:
        return ""
    return os.path.join(repo_root, ".worktrees", f"debate-pr-{pr_number}")


def _debate_review_bin(skill_root):
    return os.path.join(skill_root, "bin", "debate-review")


def build_initial_prompt(state, skill_root):
    """Build the initial prompt from agent-initial-prompt.md template."""
    template = _read_template(skill_root, "agent-initial-prompt.md")
    review_criteria = _read_template(skill_root, "review-criteria.md")

    worktree_path = _worktree_path(state)
    placeholders = {
        "{REPO}": state["repo"],
        "{PR_NUMBER}": str(state["pr_number"]),
        "{WORKTREE_PATH}": worktree_path,
        "{OUTPUT_LANGUAGE}": state.get("language", "en"),
        "{REVIEW_CRITERIA}": review_criteria,
    }
    return _substitute(template, placeholders)


def build_step_message(state, step, round_num, skill_root, extra=None, state_file=None):
    """Build a step message from the step template + state data."""
    template_file = _STEP_TEMPLATE_FILES.get(str(step))
    if not template_file:
        raise ValueError(f"Unknown step: {step}. Valid steps: 1, 2, 3")

    template = _read_template(skill_root, template_file)

    placeholders = {
        "{ROUND}": str(round_num),
        "{DEBATE_LEDGER_TEXT}": build_debate_ledger_text(state),
    }

    if str(step) == "1":
        placeholders["{PENDING_REBUTTALS_JSON}"] = json.dumps(
            build_pending_rebuttals(state, round_num), ensure_ascii=False, indent=2
        )
        placeholders["{OPEN_ISSUES_JSON}"] = json.dumps(
            build_open_issues(state), ensure_ascii=False, indent=2
        )
    elif str(step) == "2":
        placeholders["{LEAD_FINDINGS_JSON}"] = json.dumps(
            build_lead_reports(state, round_num), ensure_ascii=False, indent=2
        )
    elif str(step) == "3":
        if state_file is None:
            raise ValueError("state_file is required for step 3")
        placeholders["{CROSS_REBUTTALS_JSON}"] = json.dumps(
            build_cross_rebuttals(state, round_num), ensure_ascii=False, indent=2
        )
        placeholders["{CROSS_NEW_FINDINGS_JSON}"] = json.dumps(
            build_cross_findings(state, round_num), ensure_ascii=False, indent=2
        )
        placeholders["{APPLICABLE_ISSUES_JSON}"] = json.dumps(
            build_applicable_issues(state), ensure_ascii=False, indent=2
        )
        placeholders["{POTENTIAL_APPLICABLE_ISSUES_JSON}"] = json.dumps(
            build_potential_applicable_issues(state, round_num), ensure_ascii=False, indent=2
        )
        placeholders["{WORKTREE_PATH}"] = _worktree_path(state)
        placeholders["{DEBATE_REVIEW_BIN}"] = _debate_review_bin(skill_root)
        placeholders["{STATE_FILE}"] = state_file
        placeholders["{HEAD_BRANCH}"] = state.get("head", {}).get("pr_branch_name", "")

    message = _substitute(template, placeholders)

    if extra:
        message += f"\n\n### Additional Context\n\n{extra}"

    return message


def build_prompt(state, agent, step, round_num=None, skill_root=None, extra=None, state_file=None):
    """Build prompt and write/append to the persistent prompt file.

    Returns dict with prompt_file path and the message content.
    """
    if skill_root is None:
        raise ValueError("skill_root is required")

    pf = prompt_file_path(
        state["repo"],
        state["pr_number"],
        agent,
        dry_run=state.get("dry_run", False),
    )

    if step == "init":
        message = build_initial_prompt(state, skill_root)
        with open(pf, "w") as f:
            f.write(message)
    else:
        if round_num is None:
            raise ValueError("round is required for step messages")
        message = build_step_message(
            state,
            step,
            round_num,
            skill_root,
            extra=extra,
            state_file=state_file,
        )
        separator = f"\n\n---\n\n"
        with open(pf, "a") as f:
            f.write(separator)
            f.write(message)

    return {"prompt_file": pf, "message": message}

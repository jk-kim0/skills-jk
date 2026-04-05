import argparse
import json
import os
import shlex
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime

from debate_review.config import load_config
from debate_review.context import (
    build_context,
    build_debate_ledger_text,
    build_open_issues,
)
from debate_review.issue_ops import normalize_message
from debate_review.progress import (
    ProgressReporter,
    format_step1,
    format_step2,
    format_step3,
)
from debate_review.prompt import build_initial_prompt, prompt_file_path
from debate_review.reporting import build_final_summary, export_debate_markdown
from debate_review.timing import utc_now_iso


class OrchestrationError(RuntimeError):
    pass


class TerminalActionError(OrchestrationError):
    pass


def _skill_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _debate_review_bin(skill_root=None) -> str:
    root = skill_root or _skill_root()
    return os.path.join(root, "bin", "debate-review")


def _checkpoint_path(state_file: str) -> str:
    state_name = os.path.basename(state_file)
    directory = os.path.join(os.path.expanduser("~"), ".claude", "debate-state", "orchestrator")
    os.makedirs(directory, exist_ok=True)
    return os.path.join(directory, f"{state_name}.checkpoint.json")


def _load_checkpoint(state_file: str) -> dict | None:
    path = _checkpoint_path(state_file)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def _save_checkpoint(state_file: str, payload: dict) -> None:
    path = _checkpoint_path(state_file)
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)


def _clear_checkpoint(state_file: str) -> None:
    path = _checkpoint_path(state_file)
    if os.path.exists(path):
        os.remove(path)


def _state_head_sha(state: dict) -> str | None:
    head = state.get("head", {})
    return (
        head.get("synced_worktree_sha")
        or head.get("last_observed_pr_sha")
        or head.get("terminal_sha")
    )


def _round_synced_head_sha(state: dict, round_num: int) -> str | None:
    for round_ in state.get("rounds", []):
        if round_.get("round") == round_num:
            return round_.get("synced_head_sha")
    return _state_head_sha(state)


def _recover_commit_sha_from_worktree(*, state: dict, round_num: int, worktree_path: str) -> str | None:
    head_sha = _run_command("git rev-parse HEAD", cwd=worktree_path).strip()
    if not head_sha:
        return None
    synced_head_sha = _round_synced_head_sha(state, round_num)
    if synced_head_sha and head_sha == synced_head_sha:
        return None
    return head_sha


def _parse_json_object(output: str) -> dict:
    text = output.strip()
    if not text:
        raise OrchestrationError("Expected JSON object, got empty output")
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    candidate = _extract_json_from_text(text)
    if candidate != text:
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

    for line in reversed([line.strip() for line in text.splitlines() if line.strip()]):
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed

    raise OrchestrationError(f"Could not parse JSON object from output:\n{text}")


def _parse_session_handle(output: str) -> str:
    text = output.strip()
    for line in [line.strip() for line in text.splitlines() if line.strip()]:
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if parsed.get("type") == "thread.started" and parsed.get("thread_id"):
            return str(parsed["thread_id"])
        for key in ("session_id", "agent_id", "thread_id", "id"):
            if key in parsed and parsed[key]:
                return str(parsed[key])

    for line in reversed([line.strip() for line in text.splitlines() if line.strip()]):
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        for key in ("session_id", "agent_id", "thread_id", "id"):
            if key in parsed and parsed[key]:
                return str(parsed[key])

    if text:
        return text.splitlines()[-1].strip()
    raise OrchestrationError("Could not extract persistent session handle from runtime output")


def _run_command(command: str, *, cwd=None, stdin_text=None) -> str:
    result = subprocess.run(
        shlex.split(command),
        cwd=cwd,
        input=stdin_text,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        stdout = result.stdout.strip()
        message = stderr or stdout or f"exit {result.returncode}"
        raise OrchestrationError(f"Command failed: {command}\n{message}")
    return result.stdout


def _trace_step_name(step: str) -> str:
    return {
        "step1": "step1_lead_review",
        "step2": "step2_cross_review",
        "step3": "step3_lead_apply",
    }.get(step, step)


def _parse_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _step_elapsed_seconds(state: dict, *, round_num: int, step: str) -> float:
    trace_name = _trace_step_name(step)
    for round_ in state.get("rounds", []):
        if round_.get("round") != round_num:
            continue
        trace = round_.get("step_traces", {}).get(trace_name, {})
        started_at = _parse_iso_datetime(trace.get("started_at"))
        completed_at = _parse_iso_datetime(trace.get("completed_at"))
        if started_at and completed_at:
            return max(0.0, (completed_at - started_at).total_seconds())
        break
    return 0.0


def _find_first_value(payload, keys: tuple[str, ...]) -> str | None:
    stack = [payload]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            for key in keys:
                value = current.get(key)
                if value:
                    return str(value)
            stack.extend(current.values())
        elif isinstance(current, list):
            stack.extend(current)
    return None


def _maybe_resolve_output_path(path: str | None) -> str | None:
    if not path:
        return None
    expanded = os.path.expanduser(path)
    try:
        if os.path.exists(expanded) or os.path.islink(expanded):
            return os.path.realpath(expanded)
    except OSError:
        return None
    return None


def _extract_dispatch_metadata(response: dict) -> dict:
    task_id = _find_first_value(response, ("task_id", "task-id", "taskId", "agentId"))
    tool_use_id = _find_first_value(response, ("tool_use_id", "tool-use-id", "toolUseId", "sourceToolUseID"))
    output_file = _find_first_value(response, ("output_file", "output-file", "outputFile"))
    metadata = {
        "task_id": task_id,
        "tool_use_id": tool_use_id,
        "output_file": output_file,
        "response_keys": sorted(response.keys()),
    }
    resolved = _maybe_resolve_output_path(output_file)
    if resolved:
        metadata["subagent_log_path"] = resolved
    return metadata


@dataclass
class AgentAdapter:
    name: str
    legacy_command: str | None
    create_command: str | None
    send_command: str | None

    def _format(self, template: str | None, *, sandbox="", session_id="") -> str:
        if not template:
            raise OrchestrationError(f"{self.name} runtime command is not configured")
        return template.format(
            sandbox=sandbox,
            codex_sandbox=sandbox,
            session_id=session_id,
        )

    def run_legacy(self, prompt: str, *, worktree_path: str, sandbox: str) -> dict:
        command = self._format(self.legacy_command, sandbox=sandbox)
        output = _run_command(command, cwd=worktree_path, stdin_text=prompt)
        return _parse_json_object(output)

    def create_session(self, prompt: str, *, worktree_path: str, sandbox: str) -> str:
        command = self._format(self.create_command, sandbox=sandbox)
        output = _run_command(command, cwd=worktree_path, stdin_text=prompt)
        return _parse_session_handle(output)

    def send_message(self, session_id: str, message: str, *, worktree_path: str) -> dict:
        command = self._format(self.send_command, session_id=session_id)
        output = _run_command(command, cwd=worktree_path, stdin_text=message)
        return _parse_json_object(output)


class CodexAdapter(AgentAdapter):
    def __init__(self):
        super().__init__(
            name="codex",
            legacy_command="codex exec -s {sandbox} -",
            create_command="codex exec --json -s {sandbox} -",
            send_command="codex exec resume {session_id} -",
        )


def _extract_json_from_text(text: str) -> str:
    """Extract JSON from text that may contain markdown fences or prose.

    Handles: plain JSON, ```json {...} ```, prose with embedded code blocks,
    and prose followed by a trailing JSON object.
    """
    import re

    stripped = text.strip()
    try:
        json.loads(stripped)
        return stripped
    except (json.JSONDecodeError, ValueError):
        pass

    decoder = json.JSONDecoder()
    for index, char in enumerate(stripped):
        if char != "{":
            continue
        try:
            parsed, end = decoder.raw_decode(stripped[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict) and not stripped[index + end :].strip():
            return stripped[index : index + end]

    matches = re.findall(r"```(?:json)?\s*\n(.*?)```", stripped, re.DOTALL)
    if matches:
        return matches[-1].strip()

    return stripped


def _unwrap_cc_result(output: str) -> dict:
    """Unwrap Claude Code --output-format json wrapper to extract agent response.

    Claude Code wraps the agent's text in {"type":"result","result":"<json-string>",...}.
    The inner result may be plain JSON, markdown-fenced, or prose with embedded JSON.
    """
    wrapper = _parse_json_object(output)
    if wrapper.get("type") == "result" and "result" in wrapper:
        inner = wrapper["result"]
        if isinstance(inner, str):
            candidate = _extract_json_from_text(inner)
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass
    return wrapper


def _normalize_cross_verifications(verifications: list, state: dict) -> list:
    """Normalize agent cross-verification responses to CLI-expected format.

    Agents may return {issue_id, verdict} or {issue_id, action}
    instead of {report_id, decision}.
    """
    issue_to_report: dict[str, str] = {}
    for issue_id, issue in state.get("issues", {}).items():
        reports = issue.get("reports", [])
        if reports:
            issue_to_report[issue_id] = reports[-1]["report_id"]

    normalized = []
    for v in verifications:
        entry = dict(v)
        if "report_id" not in entry and "issue_id" in entry:
            report_id = issue_to_report.get(entry["issue_id"])
            if report_id:
                entry["report_id"] = report_id
        if "decision" not in entry and "verdict" in entry:
            entry["decision"] = entry["verdict"]
        if "decision" not in entry and "action" in entry:
            entry["decision"] = entry["action"]
        normalized.append(entry)
    return normalized


def _normalize_rebuttal_responses(responses: list, state: dict) -> list:
    """Normalize agent rebuttal responses to CLI-expected format.

    Agents may return {issue_id, action} instead of {report_id, decision}.
    """
    issue_to_report: dict[str, str] = {}
    for issue_id, issue in state.get("issues", {}).items():
        reports = issue.get("reports", [])
        if reports:
            issue_to_report[issue_id] = reports[-1]["report_id"]

    normalized = []
    for response in responses:
        entry = dict(response)
        if "report_id" not in entry and "issue_id" in entry:
            report_id = issue_to_report.get(entry["issue_id"])
            if report_id:
                entry["report_id"] = report_id
        if "decision" not in entry and "action" in entry:
            entry["decision"] = entry["action"]
        if "decision" not in entry and "verdict" in entry:
            entry["decision"] = entry["verdict"]
        normalized.append(entry)
    return normalized


def _normalize_withdrawals(withdrawals: list) -> list:
    """Normalize withdrawal entries — agents may send plain strings or dicts."""
    normalized = []
    for item in withdrawals:
        if isinstance(item, str):
            normalized.append({"issue_id": item, "reason": ""})
        elif isinstance(item, dict):
            normalized.append(item)
    return normalized


def _is_non_owner_withdrawal_error(exc: OrchestrationError) -> bool:
    """Return True only for the expected 'wrong owner' withdrawal failure."""
    message = str(exc).lower()
    return "cannot withdraw" in message and "opened by" in message


class CcAdapter(AgentAdapter):
    def __init__(self):
        super().__init__(
            name="cc",
            legacy_command="claude -p --dangerously-skip-permissions --output-format json",
            create_command="claude -p --dangerously-skip-permissions --output-format stream-json --verbose",
            send_command="claude -p --dangerously-skip-permissions --resume {session_id} --output-format json",
        )

    def run_legacy(self, prompt: str, *, worktree_path: str, sandbox: str) -> dict:
        command = self._format(self.legacy_command, sandbox=sandbox)
        output = _run_command(command, cwd=worktree_path, stdin_text=prompt)
        return _unwrap_cc_result(output)

    def send_message(self, session_id: str, message: str, *, worktree_path: str) -> dict:
        command = self._format(self.send_command, session_id=session_id)
        output = _run_command(command, cwd=worktree_path, stdin_text=message)
        return _unwrap_cc_result(output)


class SubprocessDebateCli:
    def __init__(self, debate_review_bin: str):
        self.debate_review_bin = debate_review_bin

    def _run_json(self, *args: str) -> dict:
        result = subprocess.run(
            [self.debate_review_bin, *args],
            text=True,
            capture_output=True,
        )
        if result.returncode != 0:
            message = result.stderr.strip()
            if result.stdout.strip():
                try:
                    payload = json.loads(result.stdout)
                    message = payload.get("error", message)
                except json.JSONDecodeError:
                    if not message:
                        message = result.stdout.strip()
            raise OrchestrationError(message or f"{' '.join(args)} failed")
        return json.loads(result.stdout)

    def init_session(
        self,
        *,
        repo: str,
        pr_number: int,
        config_path: str | None,
        repo_root: str | None,
        dry_run: bool,
        agent_mode: str | None,
    ) -> dict:
        args = ["init", "--repo", repo, "--pr", str(pr_number)]
        if config_path:
            args.extend(["--config", config_path])
        if repo_root:
            args.extend(["--repo-root", repo_root])
        if dry_run:
            args.append("--dry-run")
        if agent_mode:
            args.extend(["--agent-mode", agent_mode])
        return self._run_json(*args)

    def show(self, state_file: str) -> dict:
        return self._run_json("show", "--state-file", state_file, "--json")

    def sync_head(self, state_file: str) -> dict:
        return self._run_json("sync-head", "--state-file", state_file)

    def init_round(self, state_file: str, *, round_num: int, synced_head_sha: str) -> dict:
        return self._run_json(
            "init-round",
            "--state-file", state_file,
            "--round", str(round_num),
            "--synced-head-sha", synced_head_sha,
        )

    def resolve_rebuttals(self, state_file: str, *, round_num: int, step: str, decisions: list[dict]) -> dict:
        return self._run_json(
            "resolve-rebuttals",
            "--state-file", state_file,
            "--round", str(round_num),
            "--step", step,
            "--decisions", json.dumps(decisions, ensure_ascii=False),
        )

    def upsert_issue(
        self,
        state_file: str,
        *,
        agent: str,
        round_num: int,
        finding: dict,
        confirm_reopen: bool = False,
    ) -> dict:
        args = [
            "upsert-issue",
            "--state-file", state_file,
            "--agent", agent,
            "--round", str(round_num),
            "--severity", finding["severity"],
            "--criterion", str(finding["criterion"]),
            "--file", finding["file"],
            "--line", str(finding["line"]),
            "--anchor", finding["anchor"],
            "--message", finding["message"],
        ]
        if confirm_reopen:
            args.append("--confirm-reopen")
        return self._run_json(*args)

    def withdraw_issue(self, state_file: str, *, issue_id: str, agent: str, round_num: int, reason: str) -> dict:
        return self._run_json(
            "withdraw-issue",
            "--state-file", state_file,
            "--issue-id", issue_id,
            "--agent", agent,
            "--round", str(round_num),
            "--reason", reason,
        )

    def record_verdict(self, state_file: str, *, round_num: int, verdict: str) -> dict:
        return self._run_json(
            "record-verdict",
            "--state-file", state_file,
            "--round", str(round_num),
            "--verdict", verdict,
        )

    def record_cross_verification(self, state_file: str, *, round_num: int, verifications: list[dict]) -> dict:
        return self._run_json(
            "record-cross-verification",
            "--state-file", state_file,
            "--round", str(round_num),
            "--verifications", json.dumps(verifications, ensure_ascii=False),
        )

    def record_application(
        self,
        state_file: str,
        *,
        round_num: int,
        applied_issues=None,
        failed_issues=None,
        commit_sha=None,
        verify_push=False,
    ) -> dict:
        args = [
            "record-application",
            "--state-file", state_file,
            "--round", str(round_num),
        ]
        if applied_issues is not None:
            args.extend(["--applied-issues", json.dumps(applied_issues, ensure_ascii=False)])
        if failed_issues is not None:
            args.extend(["--failed-issues", json.dumps(failed_issues, ensure_ascii=False)])
        if commit_sha:
            args.extend(["--commit-sha", commit_sha])
        if verify_push:
            args.append("--verify-push")
        return self._run_json(*args)

    def settle_round(self, state_file: str, *, round_num: int) -> dict:
        return self._run_json(
            "settle-round",
            "--state-file", state_file,
            "--round", str(round_num),
        )

    def post_comment(self, state_file: str, *, no_comment: bool) -> dict:
        args = ["post-comment", "--state-file", state_file]
        if no_comment:
            args.append("--no-comment")
        return self._run_json(*args)

    def mark_failed(self, state_file: str, *, error_message: str, failed_command: str) -> dict:
        return self._run_json(
            "mark-failed",
            "--state-file", state_file,
            "--error-message", error_message,
            "--failed-command", failed_command,
        )

    def create_failure_issue(self, state_file: str) -> dict:
        return self._run_json("create-failure-issue", "--state-file", state_file)

    def build_prompt(self, state_file: str, *, agent: str, step: str, round_num: int | None = None, extra: str | None = None) -> dict:
        args = [
            "build-prompt",
            "--state-file", state_file,
            "--agent", agent,
            "--step", step,
        ]
        if round_num is not None:
            args.extend(["--round", str(round_num)])
        if extra:
            args.extend(["--extra", extra])
        return self._run_json(*args)

    def record_agent_sessions(self, state_file: str, *, cc_agent_id: str | None, codex_session_id: str | None) -> dict:
        args = ["record-agent-sessions", "--state-file", state_file]
        if cc_agent_id is not None:
            args.extend(["--cc-agent-id", cc_agent_id])
        if codex_session_id is not None:
            args.extend(["--codex-session-id", codex_session_id])
        return self._run_json(*args)

    def record_step_trace(
        self,
        state_file: str,
        *,
        round_num: int,
        step_name: str,
        agent: str | None = None,
        started_at: str | None = None,
        completed_at: str | None = None,
        patch: dict | None = None,
    ) -> dict:
        from debate_review.state import load_state, save_state
        from debate_review.timing import complete_step_trace, start_step_trace, update_step_trace

        state = load_state(state_file)
        if state is None:
            raise OrchestrationError(f"No state file found at {state_file}")
        if started_at is not None:
            trace = start_step_trace(
                state,
                round_num=round_num,
                step_name=step_name,
                agent=agent or "unknown",
                started_at=started_at,
                patch=patch,
            )
        elif completed_at is not None:
            trace = complete_step_trace(
                state,
                round_num=round_num,
                step_name=step_name,
                completed_at=completed_at,
                patch=patch,
            )
        else:
            trace = update_step_trace(
                state,
                round_num=round_num,
                step_name=step_name,
                patch=patch or {},
            )
        if not state.get("dry_run"):
            save_state(state, state_file)
        return trace


def _read_file(path: str) -> str:
    with open(path) as f:
        return f.read()


def _read_json_file(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def _round_context(state: dict) -> dict:
    round_num = state["current_round"]
    current = None
    for round_ in state.get("rounds", []):
        if round_["round"] == round_num:
            current = round_
            break
    lead_agent = current["lead_agent"] if current else ("codex" if round_num % 2 == 1 else "cc")
    return {
        "round": round_num,
        "lead_agent": lead_agent,
        "cross_verifier": "cc" if lead_agent == "codex" else "codex",
        "worktree_path": os.path.join(state["repo_root"], ".worktrees", f"debate-pr-{state['pr_number']}"),
        "head_branch": state["head"]["pr_branch_name"],
    }


def _render_template(template: str, placeholders: dict[str, str]) -> str:
    rendered = template
    for key, value in placeholders.items():
        rendered = rendered.replace(key, value)
    return rendered


def _json_text(payload) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _build_legacy_prompt(*, skill_root: str, state: dict, state_file: str, round_ctx: dict, step: str, extra: str | None) -> str:
    context = build_context(state, round_ctx["round"])
    review_criteria = _read_file(os.path.join(skill_root, "review-criteria.md"))

    if step == "1":
        template_name = "agent-lead-review-prompt.md"
        placeholders = {
            "{REPO}": state["repo"],
            "{PR_NUMBER}": str(state["pr_number"]),
            "{ROUND}": str(round_ctx["round"]),
            "{WORKTREE_PATH}": round_ctx["worktree_path"],
            "{DEBATE_LEDGER}": context["debate_ledger"],
            "{OPEN_ISSUES}": _json_text(context["open_issues"]),
            "{PENDING_REBUTTALS}": _json_text(context["pending_rebuttals"]),
            "{OUTPUT_LANGUAGE}": state.get("language", "en"),
            "{REVIEW_CRITERIA}": review_criteria,
        }
    elif step == "2":
        template_name = "agent-cross-verify-prompt.md"
        placeholders = {
            "{REPO}": state["repo"],
            "{PR_NUMBER}": str(state["pr_number"]),
            "{ROUND}": str(round_ctx["round"]),
            "{WORKTREE_PATH}": round_ctx["worktree_path"],
            "{DEBATE_LEDGER}": context["debate_ledger"],
            "{LEAD_AGENT_ID}": round_ctx["lead_agent"],
            "{LEAD_REPORTS}": _json_text(context["lead_reports"]),
            "{OUTPUT_LANGUAGE}": state.get("language", "en"),
            "{REVIEW_CRITERIA}": review_criteria,
        }
    elif step == "3":
        template_name = "agent-lead-response-prompt.md"
        placeholders = {
            "{REPO}": state["repo"],
            "{PR_NUMBER}": str(state["pr_number"]),
            "{ROUND}": str(round_ctx["round"]),
            "{WORKTREE_PATH}": round_ctx["worktree_path"],
            "{HEAD_BRANCH}": round_ctx["head_branch"],
            "{DEBATE_REVIEW_BIN}": _debate_review_bin(skill_root),
            "{STATE_FILE}": state_file,
            "{DEBATE_LEDGER}": context["debate_ledger"],
            "{CROSS_REBUTTALS}": _json_text(context["cross_rebuttals"]),
            "{CROSS_FINDINGS}": _json_text(context["cross_findings"]),
            "{APPLICABLE_ISSUES}": _json_text(context["applicable_issues"]),
            "{OUTPUT_LANGUAGE}": state.get("language", "en"),
            "{REVIEW_CRITERIA}": review_criteria,
        }
    else:
        raise OrchestrationError(f"Unknown legacy step: {step}")

    rendered = _render_template(_read_file(os.path.join(skill_root, template_name)), placeholders)
    if extra:
        rendered += f"\n\n## Additional Context\n\n{extra}"
    return rendered


def _recovery_prompt(*, skill_root: str, state: dict, next_step: str) -> str:
    initial = build_initial_prompt(state, skill_root)
    ledger = build_debate_ledger_text(state)
    open_issues = _json_text(build_open_issues(state))
    round_num = state["current_round"]
    return (
        f"{initial}\n\n"
        "## Recovery Context\n\n"
        "Previous agent session was lost. Debate state so far:\n\n"
        f"### Debate Ledger\n{ledger}\n\n"
        f"### Open Issues\n{open_issues}\n\n"
        f"Resume from Round {round_num} {next_step}."
    )


def _skip_reopen(new_message: str, existing_reports: list[dict]) -> bool:
    normalized = normalize_message(new_message)
    for report in existing_reports:
        if normalize_message(report.get("message", "")) == normalized:
            return True
    return False


def _validate_runtime_commands(*, agent_name: str, agent_mode: str, adapter: AgentAdapter) -> None:
    required_fields = []
    if agent_mode == "persistent":
        if not adapter.create_command:
            required_fields.append("persistent_create_command")
        if not adapter.send_command:
            required_fields.append("persistent_send_command")
    else:
        if not adapter.legacy_command:
            required_fields.append("legacy_command")

    if not required_fields:
        return

    fields = ", ".join(required_fields)
    override_path = os.path.expanduser("~/.claude/debate-review-config.yml")
    raise OrchestrationError(
        f"{agent_name} runtime commands are not configured for agent_mode={agent_mode}: "
        f"missing {fields}. Set orchestrator.agents.{agent_name}.* in config.yml or {override_path}."
    )


class DebateReviewOrchestrator:
    def __init__(
        self,
        *,
        cli,
        adapters: dict[str, AgentAdapter],
        skill_root: str,
        config: dict,
        no_comment: bool = False,
        cleanup_worktree: bool = True,
    ):
        self.cli = cli
        self.adapters = adapters
        self.skill_root = skill_root
        self.config = config
        self.no_comment = no_comment
        self.cleanup_worktree = cleanup_worktree
        self.state_file = None
        self.round_extra_context = None
        self.fresh_session = False
        self.progress = ProgressReporter()
        self._announced_round: int | None = None

    def _checkpoint(self) -> dict | None:
        return _load_checkpoint(self.state_file)

    def _save_checkpoint(self, payload: dict) -> None:
        _save_checkpoint(self.state_file, payload)

    def _clear_checkpoint(self) -> None:
        _clear_checkpoint(self.state_file)

    def _make_step_checkpoint(self, *, step: str, round_num: int, agent: str, response: dict, state: dict) -> dict:
        progress = {}
        if step == "step1":
            progress = {
                "rebuttals_done": False,
                "withdrawals_done": 0,
                "findings_done": 0,
                "verdict_done": False,
            }
        elif step == "step2":
            progress = {
                "verifications_done": False,
                "withdrawals_done": 0,
                "findings_done": 0,
            }
        elif step == "step3":
            progress = {
                "decisions_done": False,
                "withdrawals_done": 0,
                "phase1_done": False,
                "phase2_done": False,
                "phase3_done": False,
            }
        return {
            "step": step,
            "round": round_num,
            "head_sha": _state_head_sha(state),
            "agent": agent,
            "response": response,
            "progress": progress,
        }

    def _load_state(self) -> dict:
        return self.cli.show(self.state_file)

    def _codex_sandbox(self) -> str:
        return str(self.config.get("codex_sandbox", "danger-full-access"))

    def _worktree_path(self, state: dict) -> str:
        return os.path.join(state["repo_root"], ".worktrees", f"debate-pr-{state['pr_number']}")

    def _cleanup_worktree(self, state: dict) -> None:
        if not self.cleanup_worktree:
            return
        if state.get("dry_run"):
            return
        path = self._worktree_path(state)
        if not os.path.isdir(path):
            return
        result = subprocess.run(
            ["git", "-C", state["repo_root"], "worktree", "remove", "--force", path],
            text=True,
            capture_output=True,
        )
        if result.returncode != 0:
            raise OrchestrationError(f"worktree cleanup failed: {result.stderr.strip()}")

    def _ensure_persistent_agents(self, state: dict, next_step: str) -> None:
        if state.get("agent_mode") != "persistent":
            return
        sessions = state.get("persistent_agents", {})
        cc_handle = sessions.get("cc_agent_id")
        codex_handle = sessions.get("codex_session_id")
        worktree_path = self._worktree_path(state)
        sandbox = self._codex_sandbox()

        updated = False
        if not cc_handle:
            prompt = (
                build_initial_prompt(state, self.skill_root)
                if self.fresh_session
                else _recovery_prompt(skill_root=self.skill_root, state=state, next_step=next_step)
            )
            cc_handle = self.adapters["cc"].create_session(prompt, worktree_path=worktree_path, sandbox=sandbox)
            updated = True
        if not codex_handle:
            prompt = (
                build_initial_prompt(state, self.skill_root)
                if self.fresh_session
                else _recovery_prompt(skill_root=self.skill_root, state=state, next_step=next_step)
            )
            codex_handle = self.adapters["codex"].create_session(prompt, worktree_path=worktree_path, sandbox=sandbox)
            updated = True

        if updated:
            self.cli.record_agent_sessions(
                self.state_file,
                cc_agent_id=cc_handle,
                codex_session_id=codex_handle,
            )
        if cc_handle and codex_handle:
            self.fresh_session = False

    def _dispatch_step(self, *, step: str, agent: str, state: dict, round_ctx: dict) -> dict:
        adapter = self.adapters[agent]
        sandbox = self._codex_sandbox()
        extra = self.round_extra_context

        if state.get("agent_mode") == "persistent":
            self._ensure_persistent_agents(state, next_step=step)
            trace_step = _trace_step_name(step)
            step_started_at = utc_now_iso()

            prompt_started = utc_now_iso()
            prompt_clock = time.monotonic()
            prompt_result = self.cli.build_prompt(
                self.state_file,
                agent=agent,
                step=step[-1],
                round_num=round_ctx["round"],
                extra=extra,
            )
            prompt_completed = utc_now_iso()
            prompt_span = {
                "name": "build_prompt",
                "started_at": prompt_started,
                "completed_at": prompt_completed,
                "duration_seconds": round(time.monotonic() - prompt_clock, 3),
                "status": "ok",
            }
            message = _read_file(prompt_result["message_file"])
            os.remove(prompt_result["message_file"])
            sessions = self._load_state()["persistent_agents"]
            handle_key = "cc_agent_id" if agent == "cc" else "codex_session_id"
            handle = sessions.get(handle_key)
            self.cli.record_step_trace(
                self.state_file,
                round_num=round_ctx["round"],
                step_name=trace_step,
                agent=agent,
                started_at=step_started_at,
                patch={
                    "persistent_session": {"handle_key": handle_key, "handle": handle},
                    "runtime_artifacts": {
                        "prompt_file": prompt_result["prompt_file"],
                        "message_file": prompt_result["message_file"],
                    },
                    "command_spans": [prompt_span],
                },
            )
            try:
                send_started = utc_now_iso()
                send_clock = time.monotonic()
                response = adapter.send_message(handle, message, worktree_path=round_ctx["worktree_path"])
                send_completed = utc_now_iso()
                send_span = {
                    "name": "send_message",
                    "started_at": send_started,
                    "completed_at": send_completed,
                    "duration_seconds": round(time.monotonic() - send_clock, 3),
                    "status": "ok",
                }
                dispatch = _extract_dispatch_metadata(response)
                patch = {"command_spans": [send_span], "dispatch": dispatch}
                if dispatch.get("subagent_log_path"):
                    patch["runtime_artifacts"] = {"subagent_log_path": dispatch["subagent_log_path"]}
                self.cli.record_step_trace(
                    self.state_file,
                    round_num=round_ctx["round"],
                    step_name=trace_step,
                    completed_at=send_completed,
                    patch=patch,
                )
                return response
            except OrchestrationError as exc:
                failed_completed = utc_now_iso()
                failed_span = {
                    "name": "send_message",
                    "started_at": send_started,
                    "completed_at": failed_completed,
                    "duration_seconds": round(time.monotonic() - send_clock, 3),
                    "status": "error",
                    "error": str(exc),
                }
                self.cli.record_step_trace(
                    self.state_file,
                    round_num=round_ctx["round"],
                    step_name=trace_step,
                    patch={"command_spans": [failed_span], "dispatch": {"send_error": str(exc)}},
                )
                prompt = _recovery_prompt(skill_root=self.skill_root, state=self._load_state(), next_step=step)
                create_started = utc_now_iso()
                create_clock = time.monotonic()
                new_handle = adapter.create_session(prompt, worktree_path=round_ctx["worktree_path"], sandbox=sandbox)
                create_completed = utc_now_iso()
                create_span = {
                    "name": "create_session",
                    "started_at": create_started,
                    "completed_at": create_completed,
                    "duration_seconds": round(time.monotonic() - create_clock, 3),
                    "status": "ok",
                }
                if agent == "cc":
                    self.cli.record_agent_sessions(self.state_file, cc_agent_id=new_handle, codex_session_id=None)
                else:
                    self.cli.record_agent_sessions(self.state_file, cc_agent_id=None, codex_session_id=new_handle)
                self.cli.record_step_trace(
                    self.state_file,
                    round_num=round_ctx["round"],
                    step_name=trace_step,
                    patch={
                        "command_spans": [create_span],
                        "persistent_session": {"handle_key": handle_key, "handle": new_handle},
                    },
                )
                send_started = utc_now_iso()
                send_clock = time.monotonic()
                response = adapter.send_message(new_handle, message, worktree_path=round_ctx["worktree_path"])
                send_completed = utc_now_iso()
                send_span = {
                    "name": "send_message",
                    "started_at": send_started,
                    "completed_at": send_completed,
                    "duration_seconds": round(time.monotonic() - send_clock, 3),
                    "status": "ok",
                    "recovered": True,
                }
                dispatch = _extract_dispatch_metadata(response)
                patch = {"command_spans": [send_span], "dispatch": dispatch}
                if dispatch.get("subagent_log_path"):
                    patch["runtime_artifacts"] = {"subagent_log_path": dispatch["subagent_log_path"]}
                self.cli.record_step_trace(
                    self.state_file,
                    round_num=round_ctx["round"],
                    step_name=trace_step,
                    completed_at=send_completed,
                    patch=patch,
                )
                return response

        prompt = _build_legacy_prompt(
            skill_root=self.skill_root,
            state=state,
            state_file=self.state_file,
            round_ctx=round_ctx,
            step=step[-1],
            extra=extra,
        )
        return adapter.run_legacy(prompt, worktree_path=round_ctx["worktree_path"], sandbox=sandbox)

    def _route_findings(self, *, checkpoint: dict, agent: str, round_num: int) -> None:
        findings = checkpoint["response"].get("findings", [])
        start = checkpoint["progress"]["findings_done"]
        for finding in findings[start:]:
            result = self.cli.upsert_issue(
                self.state_file,
                agent=agent,
                round_num=round_num,
                finding=finding,
            )
            if result.get("action") == "reopen_requires_review":
                if not _skip_reopen(result["new_message"], result["existing_reports"]):
                    self.cli.upsert_issue(
                        self.state_file,
                        agent=agent,
                        round_num=round_num,
                        finding=finding,
                        confirm_reopen=True,
                    )
            checkpoint["progress"]["findings_done"] += 1
            self._save_checkpoint(checkpoint)

    def _route_step1_checkpoint(self, checkpoint: dict, round_ctx: dict) -> str:
        response = checkpoint["response"]
        if not checkpoint["progress"]["rebuttals_done"] and response.get("rebuttal_responses"):
            decisions = _normalize_rebuttal_responses(
                response["rebuttal_responses"],
                self.cli.show(self.state_file),
            )
            self.cli.resolve_rebuttals(
                self.state_file,
                round_num=round_ctx["round"],
                step="1a",
                decisions=decisions,
            )
            checkpoint["progress"]["rebuttals_done"] = True
            self._save_checkpoint(checkpoint)

        withdrawals = _normalize_withdrawals(response.get("withdrawals", []))
        done = checkpoint["progress"]["withdrawals_done"]
        for item in withdrawals[done:]:
            try:
                self.cli.withdraw_issue(
                    self.state_file,
                    issue_id=item["issue_id"],
                    agent=round_ctx["lead_agent"],
                    round_num=round_ctx["round"],
                    reason=item.get("reason", ""),
                )
            except OrchestrationError as exc:
                if not _is_non_owner_withdrawal_error(exc):
                    raise
            checkpoint["progress"]["withdrawals_done"] += 1
            self._save_checkpoint(checkpoint)

        self._route_findings(checkpoint=checkpoint, agent=round_ctx["lead_agent"], round_num=round_ctx["round"])

        if not checkpoint["progress"]["verdict_done"]:
            verdict_result = self.cli.record_verdict(
                self.state_file,
                round_num=round_ctx["round"],
                verdict=response["verdict"],
            )
            checkpoint["progress"]["verdict_done"] = True
            self._save_checkpoint(checkpoint)
        else:
            state = self._load_state()
            verdict_result = {"clean_pass": any(r["round"] == round_ctx["round"] and r.get("clean_pass") for r in state.get("rounds", []))}

        self._clear_checkpoint()
        return "step4" if verdict_result.get("clean_pass") else "step2"

    def _route_step2_checkpoint(self, checkpoint: dict, round_ctx: dict) -> str:
        response = checkpoint["response"]
        if not checkpoint["progress"]["verifications_done"]:
            state = self._load_state()
            verifications = _normalize_cross_verifications(
                response.get("cross_verifications", []), state,
            )
            self.cli.record_cross_verification(
                self.state_file,
                round_num=round_ctx["round"],
                verifications=verifications,
            )
            checkpoint["progress"]["verifications_done"] = True
            self._save_checkpoint(checkpoint)

        withdrawals = _normalize_withdrawals(response.get("withdrawals", []))
        done = checkpoint["progress"]["withdrawals_done"]
        for item in withdrawals[done:]:
            try:
                self.cli.withdraw_issue(
                    self.state_file,
                    issue_id=item["issue_id"],
                    agent=round_ctx["cross_verifier"],
                    round_num=round_ctx["round"],
                    reason=item.get("reason", ""),
                )
            except OrchestrationError as exc:
                if not _is_non_owner_withdrawal_error(exc):
                    raise
            checkpoint["progress"]["withdrawals_done"] += 1
            self._save_checkpoint(checkpoint)

        self._route_findings(checkpoint=checkpoint, agent=round_ctx["cross_verifier"], round_num=round_ctx["round"])
        self._clear_checkpoint()
        return "step3"

    def _route_step3_checkpoint(self, checkpoint: dict, round_ctx: dict) -> str:
        response = checkpoint["response"]
        decisions = response.get("rebuttal_decisions", []) + response.get("cross_finding_evaluations", [])
        if decisions and not checkpoint["progress"]["decisions_done"]:
            self.cli.resolve_rebuttals(
                self.state_file,
                round_num=round_ctx["round"],
                step="3",
                decisions=decisions,
            )
            checkpoint["progress"]["decisions_done"] = True
            self._save_checkpoint(checkpoint)

        withdrawals = _normalize_withdrawals(response.get("withdrawals", []))
        done = checkpoint["progress"]["withdrawals_done"]
        for item in withdrawals[done:]:
            try:
                self.cli.withdraw_issue(
                    self.state_file,
                    issue_id=item["issue_id"],
                    agent=round_ctx["lead_agent"],
                    round_num=round_ctx["round"],
                    reason=item.get("reason", ""),
                )
            except OrchestrationError as exc:
                if not _is_non_owner_withdrawal_error(exc):
                    raise
            checkpoint["progress"]["withdrawals_done"] += 1
            self._save_checkpoint(checkpoint)

        app = response.get("application_result", {})
        applied = app.get("applied_issues", [])
        failed = app.get("failed_issues", [])
        commit_sha = app.get("commit_sha")

        if not checkpoint["progress"]["phase1_done"]:
            self.cli.record_application(
                self.state_file,
                round_num=round_ctx["round"],
                applied_issues=applied,
                failed_issues=failed,
            )
            checkpoint["progress"]["phase1_done"] = True
            self._save_checkpoint(checkpoint)

        state = self._load_state()
        needs_push = not state.get("is_fork") and not state.get("dry_run")
        if applied and needs_push and not commit_sha:
            commit_sha = _recover_commit_sha_from_worktree(
                state=state,
                round_num=round_ctx["round"],
                worktree_path=round_ctx["worktree_path"],
            )
            if commit_sha:
                app["commit_sha"] = commit_sha
        if applied and needs_push and not commit_sha:
            raise OrchestrationError("step3 application_result is missing commit_sha for applied issues")

        if commit_sha and not checkpoint["progress"]["phase2_done"]:
            self.cli.record_application(
                self.state_file,
                round_num=round_ctx["round"],
                commit_sha=commit_sha,
            )
            checkpoint["progress"]["phase2_done"] = True
            self._save_checkpoint(checkpoint)

        if commit_sha and needs_push and not checkpoint["progress"]["phase3_done"]:
            try:
                self.cli.record_application(
                    self.state_file,
                    round_num=round_ctx["round"],
                    verify_push=True,
                )
            except OrchestrationError:
                _run_command(
                    f"git push origin HEAD:{round_ctx['head_branch']}",
                    cwd=round_ctx["worktree_path"],
                )
                self.cli.record_application(
                    self.state_file,
                    round_num=round_ctx["round"],
                    verify_push=True,
                )
            checkpoint["progress"]["phase3_done"] = True
            self._save_checkpoint(checkpoint)

        self._clear_checkpoint()
        return "step4"

    _STEP_ACTIONS = {
        "step1": "lead review",
        "step2": "cross-verify",
        "step3": "lead response",
    }

    def _dispatch_and_checkpoint(self, *, step: str, agent: str, state: dict, round_ctx: dict) -> dict:
        action = self._STEP_ACTIONS.get(step, step)
        step_label = step.replace("step", "Step")
        self.progress.step_start(step_label, agent, action)
        t0 = time.monotonic()
        try:
            response = self._dispatch_step(step=step, agent=agent, state=state, round_ctx=round_ctx)
        except Exception:
            self.progress.abort_step()
            raise
        elapsed = time.monotonic() - t0
        checkpoint = self._make_step_checkpoint(
            step=step,
            round_num=round_ctx["round"],
            agent=agent,
            response=response,
            state=state,
        )
        self._save_checkpoint(checkpoint)
        self._report_step_done(step, step_label, agent, action, elapsed, response)
        return checkpoint

    def _report_step_done(self, step: str, step_label: str, agent: str, action: str, elapsed: float, response: dict) -> None:
        if step == "step1":
            findings = response.get("findings", [])
            rebuttals = response.get("rebuttal_responses", [])
            withdrawals = response.get("withdrawals", [])
            parts = []
            if findings:
                parts.append(f"{len(findings)} finding(s)")
            if rebuttals:
                parts.append(f"{len(rebuttals)} rebuttal(s)")
            if withdrawals:
                parts.append(f"{len(withdrawals)} withdrawal(s)")
            self.progress.step_done(step_label, agent, action, elapsed, ", ".join(parts))
            self.progress.debate_content(format_step1(response))
        elif step == "step2":
            verifications = response.get("cross_verifications", [])
            new_findings = response.get("findings", [])
            accepts = sum(1 for v in verifications if v.get("verdict", v.get("decision", v.get("action", ""))) == "accept")
            rebuts = sum(1 for v in verifications if v.get("verdict", v.get("decision", v.get("action", ""))) == "rebut")
            parts = []
            if accepts:
                parts.append(f"{accepts} accept")
            if rebuts:
                parts.append(f"{rebuts} rebut")
            if new_findings:
                parts.append(f"{len(new_findings)} new")
            self.progress.step_done(step_label, agent, action, elapsed, ", ".join(parts))
            self.progress.debate_content(format_step2(response))
        elif step == "step3":
            app = response.get("application_result", {})
            applied = len(app.get("applied_issues", []))
            failed = len(app.get("failed_issues", []))
            decisions = response.get("rebuttal_decisions", [])
            evals = response.get("cross_finding_evaluations", [])
            parts = []
            if decisions or evals:
                parts.append(f"{len(decisions) + len(evals)} decision(s)")
            if applied:
                parts.append(f"applied {applied}")
            if failed:
                parts.append(f"failed {failed}")
            self.progress.step_done(step_label, agent, action, elapsed, ", ".join(parts))
            self.progress.debate_content(format_step3(response))
        else:
            self.progress.step_done(step_label, agent, action, elapsed)

    def _ensure_round_progress(self, round_ctx: dict) -> None:
        if self._announced_round == round_ctx["round"]:
            return
        self.progress.round_start(round_ctx["round"], round_ctx["lead_agent"], round_ctx["cross_verifier"])
        self._announced_round = round_ctx["round"]

    def _replay_checkpoint_progress(self, state: dict, round_ctx: dict, checkpoint: dict) -> None:
        step = checkpoint["step"]
        action = self._STEP_ACTIONS.get(step, step)
        step_label = step.replace("step", "Step")
        agent = checkpoint.get("agent") or (
            round_ctx["cross_verifier"] if step == "step2" else round_ctx["lead_agent"]
        )
        elapsed = _step_elapsed_seconds(state, round_num=round_ctx["round"], step=step)
        self._report_step_done(step, step_label, agent, action, elapsed, checkpoint["response"])

    def _process_pending_checkpoint(self, state: dict, round_ctx: dict) -> str | None:
        checkpoint = self._checkpoint()
        if not checkpoint:
            return None
        checkpoint_head_sha = checkpoint.get("head_sha")
        if checkpoint_head_sha and checkpoint_head_sha != _state_head_sha(state):
            self._clear_checkpoint()
            return None
        if checkpoint.get("round") != round_ctx["round"]:
            self._clear_checkpoint()
            return None
        self._replay_checkpoint_progress(state, round_ctx, checkpoint)
        if checkpoint["step"] == "step1":
            next_step = self._route_step1_checkpoint(checkpoint, round_ctx)
            if next_step == "step4":
                self.progress.step_skip("Step2", "clean pass")
                self.progress.step_skip("Step3", "clean pass")
            return next_step
        if checkpoint["step"] == "step2":
            return self._route_step2_checkpoint(checkpoint, round_ctx)
        if checkpoint["step"] == "step3":
            return self._route_step3_checkpoint(checkpoint, round_ctx)
        self._clear_checkpoint()
        return None

    def _step0(self, state: dict) -> str:
        sync_result = self.cli.sync_head(self.state_file)
        state = self._load_state()
        current_round = state["current_round"]
        self.cli.init_round(
            self.state_file,
            round_num=current_round,
            synced_head_sha=sync_result["post_sync_sha"],
        )
        if sync_result.get("external_change"):
            self.round_extra_context = (
                "## External Push Detected\n\n"
                f"PR HEAD changed externally (new SHA: {sync_result['post_sync_sha']}).\n"
                "Previous line numbers and code references may be invalid.\n"
                "Re-read the PR diff in your next task."
            )
        else:
            self.round_extra_context = None
        return "step1"

    def _follow_through(self, state: dict) -> None:
        """Best-effort follow-through: create failure issues on error/stall."""
        if state.get("final_outcome") in ("error", "stalled"):
            try:
                self.cli.create_failure_issue(self.state_file)
            except Exception:
                pass

    def _build_final_result(self, state: dict, settle_result: str) -> dict:
        """Build enriched result dict for the final report."""
        summary = build_final_summary(state)

        # Export debate markdown
        state_dir = os.path.dirname(self.state_file)
        state_basename = os.path.splitext(os.path.basename(self.state_file))[0]
        debate_md_path = os.path.join(state_dir, f"{state_basename}-debate.md")
        try:
            export_debate_markdown(state, debate_md_path)
        except Exception:
            debate_md_path = None

        # Collect prompt file paths
        prompt_files = {}
        try:
            for agent in ("cc", "codex"):
                pf = prompt_file_path(
                    state.get("repo", ""),
                    state.get("pr_number", 0),
                    agent,
                    dry_run=state.get("dry_run", False),
                )
                if os.path.exists(pf):
                    prompt_files[agent] = pf
        except Exception:
            pass

        return {
            "state_file": self.state_file,
            "result": settle_result,
            "current_round": state["current_round"],
            "pr_url": summary["pr_url"],
            "outcome": summary["outcome"],
            "total_duration": summary["total_duration"],
            "round_timings": summary["round_timings"],
            "prompt_files": prompt_files,
            "debate_markdown": debate_md_path,
        }

    def _terminal(self, state: dict) -> None:
        comment_error = None
        try:
            self.cli.post_comment(self.state_file, no_comment=self.no_comment or state.get("dry_run", False))
        except Exception as exc:
            comment_error = exc

        self._follow_through(state)
        if comment_error is not None:
            raise TerminalActionError(str(comment_error)) from comment_error
        self._clear_checkpoint()
        try:
            self._cleanup_worktree(state)
        except Exception:
            pass

    def _mark_failed(self, message: str, command: str) -> None:
        if not self.state_file:
            raise OrchestrationError(message)
        try:
            self.cli.mark_failed(
                self.state_file,
                error_message=message,
                failed_command=command,
            )
            state = self._load_state()
            comment_error = None
            try:
                self.cli.post_comment(self.state_file, no_comment=self.no_comment or state.get("dry_run", False))
            except Exception as exc:
                comment_error = exc
            self._follow_through(state)
            if comment_error is not None:
                raise comment_error
        finally:
            try:
                state = self._load_state()
                self._cleanup_worktree(state)
            except Exception:
                pass

    def run(
        self,
        *,
        repo: str,
        pr_number: int,
        config_path: str | None = None,
        repo_root: str | None = None,
        dry_run: bool = False,
        agent_mode: str | None = None,
    ) -> dict:
        current_command = "init"
        try:
            init_result = self.cli.init_session(
                repo=repo,
                pr_number=pr_number,
                config_path=config_path,
                repo_root=repo_root,
                dry_run=dry_run,
                agent_mode=agent_mode,
            )
            self.state_file = init_result["state_file"]
            self.fresh_session = init_result["status"] == "created"
            next_step = init_result.get("next_step", "step0")

            while True:
                state = self._load_state()
                round_ctx = _round_context(state)
                if next_step != "step0":
                    self._ensure_round_progress(round_ctx)

                checkpoint_next = self._process_pending_checkpoint(state, round_ctx)
                if checkpoint_next:
                    next_step = checkpoint_next
                    continue

                if next_step == "step0":
                    current_command = "sync-head"
                    next_step = self._step0(state)
                    state = self._load_state()
                    round_ctx = _round_context(state)
                    self._ensure_round_progress(round_ctx)
                    continue

                state = self._load_state()
                round_ctx = _round_context(state)

                if next_step == "step1":
                    current_command = "step1"
                    checkpoint = self._dispatch_and_checkpoint(
                        step="step1",
                        agent=round_ctx["lead_agent"],
                        state=state,
                        round_ctx=round_ctx,
                    )
                    next_step = self._route_step1_checkpoint(checkpoint, round_ctx)
                    if next_step == "step4":
                        self.progress.step_skip("Step2", "clean pass")
                        self.progress.step_skip("Step3", "clean pass")
                    continue

                if next_step == "step2":
                    current_command = "step2"
                    checkpoint = self._dispatch_and_checkpoint(
                        step="step2",
                        agent=round_ctx["cross_verifier"],
                        state=state,
                        round_ctx=round_ctx,
                    )
                    next_step = self._route_step2_checkpoint(checkpoint, round_ctx)
                    continue

                if next_step in ("step3", "step3_phase1", "step3_phase2", "step3_push"):
                    current_command = next_step
                    checkpoint = self._checkpoint()
                    if checkpoint is None:
                        checkpoint = self._dispatch_and_checkpoint(
                            step="step3",
                            agent=round_ctx["lead_agent"],
                            state=state,
                            round_ctx=round_ctx,
                        )
                    next_step = self._route_step3_checkpoint(checkpoint, round_ctx)
                    continue

                if next_step == "step4":
                    current_command = "settle-round"
                    settle_result = self.cli.settle_round(self.state_file, round_num=round_ctx["round"])
                    settled_ids = [s["issue_id"] for s in settle_result.get("settled_issues", [])]
                    unresolved_ids = settle_result.get("unresolved_issue_ids", [])
                    self.progress.settle(
                        settle_result["result"],
                        next_round=settle_result.get("next_round"),
                        settled=settled_ids or None,
                        unresolved=unresolved_ids or None,
                    )
                    if settle_result["result"] == "continue":
                        self.round_extra_context = None
                        next_step = "step0"
                        continue
                    state = self._load_state()
                    self._terminal(state)
                    final = self._build_final_result(state, settle_result["result"])
                    summary = build_final_summary(state)
                    issues = state.get("issues", {})
                    applied = sum(1 for i in issues.values() if i.get("application_status") == "applied")
                    withdrawn = sum(1 for i in issues.values() if i.get("consensus_status") == "withdrawn")
                    unresolved = sum(
                        1
                        for i in issues.values()
                        if i.get("consensus_status") == "open"
                        or (
                            i.get("consensus_status") == "accepted"
                            and i.get("application_status") not in ("applied", "recommended")
                        )
                    )
                    self.progress.final_result(
                        summary["outcome"],
                        summary.get("total_rounds", state["current_round"]),
                        summary["total_duration"],
                        applied=applied,
                        withdrawn=withdrawn,
                        unresolved=max(0, unresolved),
                    )
                    return final

                raise OrchestrationError(f"Unsupported resume step: {next_step}")
        except TerminalActionError:
            raise
        except Exception as exc:
            self._mark_failed(str(exc), current_command)
            raise


def _build_adapters(config: dict) -> dict[str, AgentAdapter]:
    orch = config.get("orchestrator", {})
    agent_cfg = orch.get("agents", {}) if isinstance(orch, dict) else {}
    agent_mode = str(config.get("agent_mode", "persistent"))

    def _from_cfg(name: str, defaults: AgentAdapter | None = None) -> AgentAdapter:
        cfg = agent_cfg.get(name, {}) if isinstance(agent_cfg, dict) else {}
        if defaults is not None:
            if not cfg:
                return defaults
            defaults.legacy_command = cfg.get("legacy_command", defaults.legacy_command)
            defaults.create_command = cfg.get("persistent_create_command", defaults.create_command)
            defaults.send_command = cfg.get("persistent_send_command", defaults.send_command)
            return defaults
        return AgentAdapter(
            name=name,
            legacy_command=cfg.get("legacy_command"),
            create_command=cfg.get("persistent_create_command"),
            send_command=cfg.get("persistent_send_command"),
        )

    adapters = {
        "codex": _from_cfg("codex", defaults=CodexAdapter()),
        "cc": _from_cfg("cc", defaults=CcAdapter()),
    }
    for name, adapter in adapters.items():
        _validate_runtime_commands(agent_name=name, agent_mode=agent_mode, adapter=adapter)
    return adapters


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="run-debate-review")
    parser.add_argument("--repo", required=True, help="owner/repo")
    parser.add_argument("--pr", required=True, type=int, help="PR number")
    parser.add_argument("--config", help="Path to config YAML")
    parser.add_argument("--repo-root", help="Override repo root")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--agent-mode", choices=["legacy", "persistent"], default=None)
    parser.add_argument("--no-comment", action="store_true")
    parser.add_argument("--no-cleanup", action="store_true")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    skill_root = _skill_root()
    config = load_config(args.config)
    if args.agent_mode is not None:
        config["agent_mode"] = args.agent_mode
    orchestrator = DebateReviewOrchestrator(
        cli=SubprocessDebateCli(_debate_review_bin(skill_root)),
        adapters=_build_adapters(config),
        skill_root=skill_root,
        config=config,
        no_comment=args.no_comment,
        cleanup_worktree=not args.no_cleanup,
    )
    result = orchestrator.run(
        repo=args.repo,
        pr_number=args.pr,
        config_path=args.config,
        repo_root=args.repo_root,
        dry_run=args.dry_run,
        agent_mode=args.agent_mode,
    )
    print(json.dumps(result))

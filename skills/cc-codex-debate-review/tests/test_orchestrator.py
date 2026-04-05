import copy
import json
import os

import pytest

from debate_review.application import (
    record_application_phase1,
    record_application_phase2,
    record_application_phase3,
)
from debate_review.cross_verification import record_cross_verification, resolve_rebuttals
from debate_review.issue_ops import upsert_issue, withdraw_issue
from debate_review.orchestrator import DebateReviewOrchestrator, OrchestrationError, SubprocessDebateCli
from debate_review.round_ops import init_round, record_verdict, settle_round
from debate_review.state import create_initial_state, mark_failed, save_state

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class FakeCli:
    def __init__(self, state, *, state_file, init_status="created", next_step="step0"):
        self.state = state
        self.state_file = state_file
        self.init_status = init_status
        self.next_step = next_step
        self.post_comment_calls = []
        self.mark_failed_calls = []
        self.record_agent_sessions_calls = []
        self.record_application_calls = []
        self.build_prompt_calls = []
        self.record_step_trace_calls = []
        self.create_failure_issue_calls = []

    def init_session(self, **_kwargs):
        result = {
            "state_file": self.state_file,
            "status": self.init_status,
            "current_round": self.state["current_round"],
            "is_fork": self.state["is_fork"],
            "dry_run": self.state["dry_run"],
            "codex_sandbox": "danger-full-access",
            "language": self.state.get("language", "en"),
        }
        if self.init_status == "resumed":
            result["next_step"] = self.next_step
        return result

    def show(self, _state_file):
        return copy.deepcopy(self.state)

    def sync_head(self, _state_file):
        self.state["journal"]["step"] = "step0_sync"
        self.state["journal"]["pre_sync_head_sha"] = self.state["head"]["last_observed_pr_sha"]
        self.state["journal"]["post_sync_head_sha"] = self.state["head"]["last_observed_pr_sha"]
        self.state["head"]["synced_worktree_sha"] = self.state["head"]["last_observed_pr_sha"]
        return {
            "pre_sync_sha": self.state["head"]["last_observed_pr_sha"],
            "post_sync_sha": self.state["head"]["last_observed_pr_sha"],
            "external_change": False,
            "superseded_rounds": [],
        }

    def init_round(self, _state_file, *, round_num, synced_head_sha):
        init_round(self.state, round_num=round_num, synced_head_sha=synced_head_sha)
        self.state["journal"]["round"] = round_num
        self.state["journal"]["step"] = "step0_sync"
        lead_agent = "codex" if round_num % 2 == 1 else "cc"
        return {
            "round": round_num,
            "lead_agent": lead_agent,
            "cross_verifier": "cc" if lead_agent == "codex" else "codex",
            "worktree_path": f"{self.state['repo_root']}/.worktrees/debate-pr-{self.state['pr_number']}",
            "head_branch": self.state["head"]["pr_branch_name"],
            "synced_head_sha": synced_head_sha,
        }

    def resolve_rebuttals(self, _state_file, *, round_num, step, decisions):
        return resolve_rebuttals(self.state, round_num=round_num, step=step, decisions=decisions)

    def upsert_issue(self, _state_file, *, agent, round_num, finding, confirm_reopen=False):
        return upsert_issue(
            self.state,
            agent=agent,
            round_num=round_num,
            severity=finding["severity"],
            criterion=finding["criterion"],
            file=finding["file"],
            line=finding["line"],
            anchor=finding["anchor"],
            message=finding["message"],
            confirm_reopen=confirm_reopen,
        )

    def withdraw_issue(self, _state_file, *, issue_id, agent, round_num, reason):
        return withdraw_issue(self.state, issue_id=issue_id, agent=agent, round_num=round_num, reason=reason)

    def record_verdict(self, _state_file, *, round_num, verdict):
        return record_verdict(self.state, round_num=round_num, verdict=verdict)

    def record_cross_verification(self, _state_file, *, round_num, verifications):
        return record_cross_verification(self.state, round_num=round_num, verifications=verifications)

    def record_application(self, _state_file, *, round_num, applied_issues=None, failed_issues=None, commit_sha=None, verify_push=False):
        self.record_application_calls.append(
            {
                "round": round_num,
                "applied_issues": applied_issues,
                "failed_issues": failed_issues,
                "commit_sha": commit_sha,
                "verify_push": verify_push,
            }
        )
        if applied_issues is not None:
            return record_application_phase1(
                self.state,
                round_num=round_num,
                applied_issue_ids=applied_issues,
                failed_issue_ids=failed_issues or [],
            )
        if commit_sha is not None:
            return record_application_phase2(self.state, round_num=round_num, commit_sha=commit_sha)
        if verify_push:
            return record_application_phase3(
                self.state,
                round_num=round_num,
                _get_head=lambda *_args: self.state["journal"]["commit_sha"],
            )
        raise AssertionError("unexpected record_application call")

    def settle_round(self, _state_file, *, round_num):
        return settle_round(self.state, round_num=round_num)

    def post_comment(self, _state_file, *, no_comment):
        self.post_comment_calls.append(no_comment)
        return {"action": "dry_run" if no_comment else "posted", "body": "ok"}

    def mark_failed(self, _state_file, *, error_message, failed_command):
        self.mark_failed_calls.append((failed_command, error_message))
        mark_failed(self.state, error_message=error_message)
        return {"status": "failed", "error_message": error_message}

    def create_failure_issue(self, _state_file):
        self.create_failure_issue_calls.append(True)
        outcome = self.state.get("final_outcome")
        if outcome not in ("error", "stalled"):
            return {"action": "skipped", "reason": "not failed"}
        return {"action": "created", "url": "https://github.com/owner/repo/issues/99"}

    def build_prompt(self, _state_file, *, agent, step, round_num=None, extra=None):
        self.build_prompt_calls.append((agent, step, round_num, extra))
        prompt_path = f"{self.state_file}.{agent}.prompt.md"
        message_path = f"{self.state_file}.{agent}.message.md"
        with open(prompt_path, "w") as f:
            f.write(f"prompt:{agent}:{step}")
        if step != "init":
            with open(message_path, "w") as f:
                f.write(f"message:{agent}:{step}:{round_num}")
        result = {"prompt_file": prompt_path}
        if step != "init":
            result["message_file"] = message_path
        return result

    def record_agent_sessions(self, _state_file, *, cc_agent_id, codex_session_id):
        self.record_agent_sessions_calls.append((cc_agent_id, codex_session_id))
        if cc_agent_id is not None:
            self.state["persistent_agents"]["cc_agent_id"] = cc_agent_id
        if codex_session_id is not None:
            self.state["persistent_agents"]["codex_session_id"] = codex_session_id
        return copy.deepcopy(self.state["persistent_agents"])

    def record_step_trace(self, _state_file, *, round_num, step_name, agent=None, started_at=None, completed_at=None, patch=None):
        from debate_review.timing import complete_step_trace, start_step_trace, update_step_trace

        self.record_step_trace_calls.append(
            {
                "round": round_num,
                "step_name": step_name,
                "agent": agent,
                "started_at": started_at,
                "completed_at": completed_at,
                "patch": copy.deepcopy(patch),
            }
        )
        if started_at is not None:
            start_step_trace(
                self.state,
                round_num=round_num,
                step_name=step_name,
                agent=agent or "unknown",
                started_at=started_at,
                patch=patch,
            )
        elif completed_at is not None:
            complete_step_trace(
                self.state,
                round_num=round_num,
                step_name=step_name,
                completed_at=completed_at,
                patch=patch,
            )
        else:
            update_step_trace(self.state, round_num=round_num, step_name=step_name, patch=patch or {})
        return copy.deepcopy(self.state["rounds"][round_num - 1]["step_traces"][step_name])


class ScriptedAdapter:
    def __init__(self, name, *, send=None):
        self.name = name
        self.send = list(send or [])
        self.create_calls = []
        self.send_calls = []

    def create_session(self, prompt, *, worktree_path, sandbox):
        self.create_calls.append((prompt, worktree_path, sandbox))
        return f"{self.name}-session-{len(self.create_calls)}"

    def send_message(self, session_id, message, *, worktree_path):
        self.send_calls.append((session_id, message, worktree_path))
        if not self.send:
            raise AssertionError(f"{self.name} send queue exhausted")
        return self.send.pop(0)


def _sample_state():
    state = create_initial_state(
        repo="owner/repo",
        repo_root="/tmp/repo",
        pr_number=123,
        is_fork=False,
        head_sha="abc1234def5678",
        pr_branch_name="feat/test",
        max_rounds=3,
    )
    return state



def test_orchestrator_run_persistent_recovers_missing_handles(monkeypatch, tmp_path):
    import debate_review.orchestrator as orchestrator_module

    checkpoint_path = tmp_path / "checkpoint.json"
    monkeypatch.setattr(orchestrator_module, "_checkpoint_path", lambda _state_file: str(checkpoint_path))

    state = _sample_state()
    cli = FakeCli(state, state_file=str(tmp_path / "state.json"))
    codex = ScriptedAdapter(
        "codex",
        send=[{"rebuttal_responses": [], "withdrawals": [], "findings": [], "verdict": "no_findings_mergeable"}],
    )
    cc = ScriptedAdapter(
        "cc",
        send=[{"rebuttal_responses": [], "withdrawals": [], "findings": [], "verdict": "no_findings_mergeable"}],
    )

    orchestrator = DebateReviewOrchestrator(
        cli=cli,
        adapters={"codex": codex, "cc": cc},
        skill_root=SKILL_ROOT,
        config={"codex_sandbox": "danger-full-access"},
        no_comment=False,
        cleanup_worktree=False,
    )

    result = orchestrator.run(repo="owner/repo", pr_number=123)

    assert result["result"] == "consensus_reached"
    assert cli.record_agent_sessions_calls[0] == ("cc-session-1", "codex-session-1")
    assert cli.state["persistent_agents"] == {
        "cc_agent_id": "cc-session-1",
        "codex_session_id": "codex-session-1",
    }
    assert len(codex.create_calls) == 1
    assert len(cc.create_calls) == 1
    assert len(codex.send_calls) == 1
    assert len(cc.send_calls) == 1


def test_dispatch_step_persistent_records_trace_metadata(monkeypatch, tmp_path):
    import debate_review.orchestrator as orchestrator_module

    checkpoint_path = tmp_path / "checkpoint.json"
    monkeypatch.setattr(orchestrator_module, "_checkpoint_path", lambda _state_file: str(checkpoint_path))

    state = _sample_state()
    init_round(state, round_num=1, lead_agent="cc", synced_head_sha=state["head"]["last_observed_pr_sha"])
    state["persistent_agents"]["cc_agent_id"] = "cc-session-1"
    state["persistent_agents"]["codex_session_id"] = "codex-session-1"

    output_real = tmp_path / "subagents" / "agent-task-1.jsonl"
    output_real.parent.mkdir(parents=True)
    output_real.write_text("{}\n")
    output_link = tmp_path / "task-1.output"
    output_link.symlink_to(output_real)

    cli = FakeCli(state, state_file=str(tmp_path / "state.json"))
    cc = ScriptedAdapter(
        "cc",
        send=[{
            "rebuttal_responses": [],
            "withdrawals": [],
            "findings": [],
            "verdict": "no_findings_mergeable",
            "task_id": "task-1",
            "tool_use_id": "tool-1",
            "output_file": str(output_link),
        }],
    )
    orchestrator = DebateReviewOrchestrator(
        cli=cli,
        adapters={"codex": ScriptedAdapter("codex"), "cc": cc},
        skill_root=SKILL_ROOT,
        config={"codex_sandbox": "danger-full-access"},
        cleanup_worktree=False,
    )
    orchestrator.state_file = cli.state_file

    round_ctx = {
        "round": 1,
        "lead_agent": "cc",
        "cross_verifier": "codex",
        "worktree_path": f"{state['repo_root']}/.worktrees/debate-pr-{state['pr_number']}",
        "head_branch": state["head"]["pr_branch_name"],
    }

    checkpoint = orchestrator._dispatch_and_checkpoint(
        step="step1",
        agent="cc",
        state=state,
        round_ctx=round_ctx,
    )

    assert checkpoint["response"]["task_id"] == "task-1"
    trace = cli.state["rounds"][0]["step_traces"]["step1_lead_review"]
    assert trace["agent"] == "cc"
    assert trace["dispatch"]["task_id"] == "task-1"
    assert trace["dispatch"]["tool_use_id"] == "tool-1"
    assert trace["dispatch"]["output_file"] == str(output_link)
    assert trace["runtime_artifacts"]["subagent_log_path"] == str(output_real.resolve())
    assert trace["persistent_session"]["handle"] == "cc-session-1"
    assert [span["name"] for span in trace["command_spans"]] == ["build_prompt", "send_message"]


def test_dispatch_step_persistent_rehydrates_missing_round_with_subprocess_cli(monkeypatch, tmp_path):
    import debate_review.orchestrator as orchestrator_module

    checkpoint_path = tmp_path / "checkpoint.json"
    monkeypatch.setattr(orchestrator_module, "_checkpoint_path", lambda _state_file: str(checkpoint_path))
    monkeypatch.setenv("HOME", str(tmp_path))

    state = _sample_state(agent_mode="persistent")
    state["current_round"] = 1
    state["rounds"] = []
    init_round(state, round_num=1, lead_agent="cc", synced_head_sha=state["head"]["last_observed_pr_sha"])
    state["persistent_agents"]["cc_agent_id"] = "cc-session-1"
    state_file = tmp_path / "state.json"
    state_file.write_text(json.dumps(state))

    stub_root = tmp_path / "py-stubs"
    stub_root.mkdir()
    (stub_root / "yaml.py").write_text(
        "class YAMLError(Exception):\n"
        "    pass\n\n"
        "def safe_load(_stream):\n"
        "    return {}\n"
    )
    wrapper = tmp_path / "debate-review-wrapper"
    wrapper.write_text(
        "#!/bin/sh\n"
        f"export PYTHONPATH='{stub_root}:{SKILL_ROOT}/lib${{PYTHONPATH:+:$PYTHONPATH}}'\n"
        f"exec '{os.sys.executable}' '{orchestrator_module._debate_review_bin(SKILL_ROOT)}' \"$@\"\n"
    )
    wrapper.chmod(0o755)

    cli = orchestrator_module.SubprocessDebateCli(str(wrapper))
    cc = ScriptedAdapter(
        "cc",
        send=[{
            "rebuttal_responses": [],
            "withdrawals": [],
            "findings": [],
            "verdict": "no_findings_mergeable",
        }],
    )
    orchestrator = DebateReviewOrchestrator(
        cli=cli,
        adapters={"codex": ScriptedAdapter("codex"), "cc": cc},
        skill_root=SKILL_ROOT,
        config={"codex_sandbox": "danger-full-access"},
        cleanup_worktree=False,
    )
    orchestrator.state_file = str(state_file)

    checkpoint = orchestrator._dispatch_and_checkpoint(
        step="step1",
        agent="cc",
        state=json.loads(state_file.read_text()),
        round_ctx={
            "round": 1,
            "lead_agent": "cc",
            "cross_verifier": "codex",
            "worktree_path": f"{state['repo_root']}/.worktrees/debate-pr-{state['pr_number']}",
            "head_branch": state["head"]["pr_branch_name"],
            "synced_head_sha": state["head"]["last_observed_pr_sha"],
        },
    )

    saved = json.loads(state_file.read_text())
    assert checkpoint["response"]["verdict"] == "no_findings_mergeable"
    assert saved["rounds"][0]["round"] == 1
    assert "step1_lead_review" in saved["rounds"][0]["step_traces"]
    prompt_file = saved["rounds"][0]["step_traces"]["step1_lead_review"]["runtime_artifacts"]["prompt_file"]
    assert prompt_file.startswith(str(tmp_path))
    assert saved["rounds"][0]["step_traces"]["step1_lead_review"]["agent"] == "cc"


def test_route_step3_checkpoint_resumes_remaining_phases(monkeypatch, tmp_path):
    import debate_review.orchestrator as orchestrator_module

    checkpoint_path = tmp_path / "checkpoint.json"
    monkeypatch.setattr(orchestrator_module, "_checkpoint_path", lambda _state_file: str(checkpoint_path))

    state = _sample_state()
    init_round(state, round_num=1, synced_head_sha=state["head"]["last_observed_pr_sha"])
    state["issues"]["isu_001"] = {
        "issue_id": "isu_001",
        "issue_key": "criterion:6|file:src/app.py|anchor:line1|kind:unused_variable",
        "opened_by": "codex",
        "introduced_in_round": 1,
        "criterion": 6,
        "file": "src/app.py",
        "line": 1,
        "anchor": "line1",
        "severity": "warning",
        "consensus_status": "accepted",
        "application_status": "pending",
        "accepted_by": ["cc", "codex"],
        "rejected_by": [],
        "applied_by": None,
        "application_commit_sha": None,
        "consensus_reason": None,
        "reports": [
            {
                "report_id": "rpt_001",
                "agent": "codex",
                "round": 1,
                "severity": "warning",
                "message": "unused variable x",
                "reported_at": "2026-04-04T00:00:00+00:00",
                "status": "open",
            }
        ],
        "created_at": "2026-04-04T00:00:00+00:00",
        "updated_at": "2026-04-04T00:00:00+00:00",
    }
    record_application_phase1(state, round_num=1, applied_issue_ids=["isu_001"], failed_issue_ids=[])

    cli = FakeCli(state, state_file=str(tmp_path / "state.json"), init_status="resumed", next_step="step3_phase2")
    orchestrator = DebateReviewOrchestrator(
        cli=cli,
        adapters={"codex": ScriptedAdapter("codex"), "cc": ScriptedAdapter("cc")},
        skill_root=SKILL_ROOT,
        config={"codex_sandbox": "danger-full-access"},
        cleanup_worktree=False,
    )
    orchestrator.state_file = cli.state_file

    checkpoint = {
        "step": "step3",
        "round": 1,
        "agent": "codex",
        "response": {
            "rebuttal_decisions": [],
            "cross_finding_evaluations": [],
            "application_result": {
                "applied_issues": ["isu_001"],
                "failed_issues": [],
                "commit_sha": "deadbeef",
            },
        },
        "progress": {
            "withdrawals_done": 0,
            "decisions_done": True,
            "phase1_done": True,
            "phase2_done": False,
            "phase3_done": False,
        },
    }

    next_step = orchestrator._route_step3_checkpoint(checkpoint, {
        "round": 1,
        "lead_agent": "codex",
        "cross_verifier": "cc",
        "worktree_path": "/tmp/repo/.worktrees/debate-pr-123",
        "head_branch": "feat/test",
    })

    assert next_step == "step4"
    assert cli.record_application_calls == [
        {
            "round": 1,
            "applied_issues": None,
            "failed_issues": None,
            "commit_sha": "deadbeef",
            "verify_push": False,
        },
        {
            "round": 1,
            "applied_issues": None,
            "failed_issues": None,
            "commit_sha": None,
            "verify_push": True,
        },
    ]
    assert cli.state["issues"]["isu_001"]["application_commit_sha"] == "deadbeef"
    assert not checkpoint_path.exists()


def test_route_step3_checkpoint_recovers_commit_sha_from_local_head(monkeypatch, tmp_path):
    import debate_review.orchestrator as orchestrator_module

    checkpoint_path = tmp_path / "checkpoint.json"
    monkeypatch.setattr(orchestrator_module, "_checkpoint_path", lambda _state_file: str(checkpoint_path))
    monkeypatch.setattr(
        orchestrator_module,
        "_run_command",
        lambda command, *, cwd=None, stdin_text=None: "cafebabe12345678\n" if command == "git rev-parse HEAD" else "",
    )

    state = _sample_state()
    init_round(state, round_num=1, synced_head_sha=state["head"]["last_observed_pr_sha"])
    state["issues"]["isu_001"] = {
        "issue_id": "isu_001",
        "issue_key": "criterion:6|file:src/app.py|anchor:line1|kind:unused_variable",
        "opened_by": "codex",
        "introduced_in_round": 1,
        "criterion": 6,
        "file": "src/app.py",
        "line": 1,
        "anchor": "line1",
        "severity": "warning",
        "consensus_status": "accepted",
        "application_status": "pending",
        "accepted_by": ["cc", "codex"],
        "rejected_by": [],
        "applied_by": None,
        "application_commit_sha": None,
        "consensus_reason": None,
        "reports": [
            {
                "report_id": "rpt_001",
                "agent": "codex",
                "round": 1,
                "severity": "warning",
                "message": "unused variable x",
                "reported_at": "2026-04-04T00:00:00+00:00",
                "status": "open",
            }
        ],
        "created_at": "2026-04-04T00:00:00+00:00",
        "updated_at": "2026-04-04T00:00:00+00:00",
    }

    cli = FakeCli(state, state_file=str(tmp_path / "state.json"), init_status="resumed", next_step="step3")
    orchestrator = DebateReviewOrchestrator(
        cli=cli,
        adapters={"codex": ScriptedAdapter("codex"), "cc": ScriptedAdapter("cc")},
        skill_root=SKILL_ROOT,
        config={"codex_sandbox": "danger-full-access"},
        cleanup_worktree=False,
    )
    orchestrator.state_file = cli.state_file

    checkpoint = {
        "step": "step3",
        "round": 1,
        "agent": "codex",
        "response": {
            "rebuttal_decisions": [],
            "cross_finding_evaluations": [],
            "application_result": {
                "applied_issues": ["isu_001"],
                "failed_issues": [],
            },
        },
        "progress": {
            "withdrawals_done": 0,
            "decisions_done": True,
            "phase1_done": False,
            "phase2_done": False,
            "phase3_done": False,
        },
    }

    next_step = orchestrator._route_step3_checkpoint(checkpoint, {
        "round": 1,
        "lead_agent": "codex",
        "cross_verifier": "cc",
        "worktree_path": "/tmp/repo/.worktrees/debate-pr-123",
        "head_branch": "feat/test",
    })

    assert next_step == "step4"
    assert cli.record_application_calls == [
        {
            "round": 1,
            "applied_issues": ["isu_001"],
            "failed_issues": [],
            "commit_sha": None,
            "verify_push": False,
        },
        {
            "round": 1,
            "applied_issues": None,
            "failed_issues": None,
            "commit_sha": "cafebabe12345678",
            "verify_push": False,
        },
        {
            "round": 1,
            "applied_issues": None,
            "failed_issues": None,
            "commit_sha": None,
            "verify_push": True,
        },
    ]
    assert cli.state["issues"]["isu_001"]["application_commit_sha"] == "cafebabe12345678"
    assert not checkpoint_path.exists()


def test_route_step1_checkpoint_ignores_non_owner_withdrawal_error(monkeypatch, tmp_path):
    import debate_review.orchestrator as orchestrator_module

    checkpoint_path = tmp_path / "checkpoint.json"
    monkeypatch.setattr(orchestrator_module, "_checkpoint_path", lambda _state_file: str(checkpoint_path))

    state = _sample_state()
    init_round(state, round_num=1, synced_head_sha=state["head"]["last_observed_pr_sha"])
    issue = upsert_issue(
        state,
        agent="cc",
        round_num=1,
        severity="warning",
        criterion=6,
        file="src/app.py",
        line=1,
        anchor="line1",
        message="unused variable x",
    )

    class WrappingCli(FakeCli):
        def withdraw_issue(self, _state_file, *, issue_id, agent, round_num, reason):
            try:
                return super().withdraw_issue(
                    _state_file,
                    issue_id=issue_id,
                    agent=agent,
                    round_num=round_num,
                    reason=reason,
                )
            except ValueError as exc:
                raise OrchestrationError(str(exc))

    cli = WrappingCli(state, state_file=str(tmp_path / "state.json"))
    orchestrator = DebateReviewOrchestrator(
        cli=cli,
        adapters={"codex": ScriptedAdapter("codex"), "cc": ScriptedAdapter("cc")},
        skill_root=SKILL_ROOT,
        config={"codex_sandbox": "danger-full-access"},
        cleanup_worktree=False,
    )
    orchestrator.state_file = cli.state_file

    checkpoint = {
        "step": "step1",
        "round": 1,
        "agent": "codex",
        "response": {
            "rebuttal_responses": [],
            "withdrawals": [{"issue_id": issue["issue_id"], "reason": "not mine"}],
            "findings": [],
            "verdict": "has_findings",
        },
        "progress": {
            "rebuttals_done": False,
            "withdrawals_done": 0,
            "findings_done": 0,
            "verdict_done": False,
        },
    }

    next_step = orchestrator._route_step1_checkpoint(checkpoint, {
        "round": 1,
        "lead_agent": "codex",
        "cross_verifier": "cc",
        "worktree_path": "/tmp/repo/.worktrees/debate-pr-123",
        "head_branch": "feat/test",
    })

    assert next_step == "step2"
    assert checkpoint["progress"]["withdrawals_done"] == 1
    assert cli.state["issues"][issue["issue_id"]]["consensus_status"] == "open"


def test_route_step1_checkpoint_normalizes_issue_id_rebuttal_responses(monkeypatch, tmp_path):
    import debate_review.orchestrator as orchestrator_module

    checkpoint_path = tmp_path / "checkpoint.json"
    monkeypatch.setattr(orchestrator_module, "_checkpoint_path", lambda _state_file: str(checkpoint_path))

    state = _sample_state(agent_mode="legacy")
    init_round(state, round_num=1, synced_head_sha=state["head"]["last_observed_pr_sha"])
    issue = upsert_issue(
        state,
        agent="cc",
        round_num=1,
        severity="warning",
        criterion=6,
        file="src/app.py",
        line=1,
        anchor="line1",
        message="unused variable x",
    )
    report_id = issue["report_id"]
    state["rounds"][0]["step3"]["rebuttals"] = [{
        "report_id": report_id,
        "issue_id": issue["issue_id"],
        "reason": "please re-check",
    }]
    init_round(state, round_num=2, synced_head_sha=state["head"]["last_observed_pr_sha"])

    cli = FakeCli(state, state_file=str(tmp_path / "state.json"))
    orchestrator = DebateReviewOrchestrator(
        cli=cli,
        adapters={"codex": ScriptedAdapter("codex"), "cc": ScriptedAdapter("cc")},
        skill_root=SKILL_ROOT,
        config={"codex_sandbox": "danger-full-access"},
        cleanup_worktree=False,
    )
    orchestrator.state_file = cli.state_file

    checkpoint = {
        "step": "step1",
        "round": 2,
        "agent": "codex",
        "response": {
            "rebuttal_responses": [{
                "issue_id": issue["issue_id"],
                "action": "maintain",
                "reason": "still reproducible",
            }],
            "withdrawals": [],
            "findings": [],
            "verdict": "has_findings",
        },
        "progress": {
            "rebuttals_done": False,
            "withdrawals_done": 0,
            "findings_done": 0,
            "verdict_done": False,
        },
    }

    next_step = orchestrator._route_step1_checkpoint(checkpoint, {
        "round": 2,
        "lead_agent": "codex",
        "cross_verifier": "cc",
        "worktree_path": "/tmp/repo/.worktrees/debate-pr-123",
        "head_branch": "feat/test",
    })

    assert next_step == "step2"
    assert checkpoint["progress"]["rebuttals_done"] is True
    assert state["rounds"][1]["step1"]["rebuttal_responses"] == [{
        "report_id": report_id,
        "decision": "maintain",
        "reason": "still reproducible",
    }]


def test_route_step1_checkpoint_maps_issue_id_to_pending_rebuttal_report(monkeypatch, tmp_path):
    import debate_review.orchestrator as orchestrator_module

    checkpoint_path = tmp_path / "checkpoint.json"
    monkeypatch.setattr(orchestrator_module, "_checkpoint_path", lambda _state_file: str(checkpoint_path))

    state = _sample_state(agent_mode="legacy")
    init_round(state, round_num=1, synced_head_sha=state["head"]["last_observed_pr_sha"])
    issue = upsert_issue(
        state,
        agent="cc",
        round_num=1,
        severity="warning",
        criterion=6,
        file="src/app.py",
        line=1,
        anchor="line1",
        message="unused variable x",
    )
    original_report_id = issue["report_id"]
    init_round(state, round_num=2, synced_head_sha=state["head"]["last_observed_pr_sha"])
    state["rounds"][0]["step3"]["rebuttals"] = [{
        "report_id": original_report_id,
        "issue_id": issue["issue_id"],
        "reason": "please re-check",
    }]
    appended = upsert_issue(
        state,
        agent="codex",
        round_num=2,
        severity="warning",
        criterion=6,
        file="src/app.py",
        line=1,
        anchor="line1",
        message="unused variable x",
    )
    assert appended["report_id"] != original_report_id

    cli = FakeCli(state, state_file=str(tmp_path / "state.json"))
    orchestrator = DebateReviewOrchestrator(
        cli=cli,
        adapters={"codex": ScriptedAdapter("codex"), "cc": ScriptedAdapter("cc")},
        skill_root=SKILL_ROOT,
        config={"codex_sandbox": "danger-full-access"},
        cleanup_worktree=False,
    )
    orchestrator.state_file = cli.state_file

    checkpoint = {
        "step": "step1",
        "round": 2,
        "agent": "codex",
        "response": {
            "rebuttal_responses": [{
                "issue_id": issue["issue_id"],
                "action": "withdraw",
                "reason": "agree with rebuttal",
            }],
            "withdrawals": [],
            "findings": [],
            "verdict": "has_findings",
        },
        "progress": {
            "rebuttals_done": False,
            "withdrawals_done": 0,
            "findings_done": 0,
            "verdict_done": False,
        },
    }

    orchestrator._route_step1_checkpoint(checkpoint, {
        "round": 2,
        "lead_agent": "codex",
        "cross_verifier": "cc",
        "worktree_path": "/tmp/repo/.worktrees/debate-pr-123",
        "head_branch": "feat/test",
    })

    assert state["rounds"][1]["step1"]["rebuttal_responses"] == [{
        "report_id": original_report_id,
        "decision": "withdraw",
        "reason": "agree with rebuttal",
    }]


def test_route_step3_checkpoint_normalizes_issue_id_decisions(monkeypatch, tmp_path):
    import debate_review.orchestrator as orchestrator_module

    checkpoint_path = tmp_path / "checkpoint.json"
    monkeypatch.setattr(orchestrator_module, "_checkpoint_path", lambda _state_file: str(checkpoint_path))

    state = _sample_state(agent_mode="legacy")
    init_round(state, round_num=1, synced_head_sha=state["head"]["last_observed_pr_sha"])
    lead = upsert_issue(
        state,
        agent="codex",
        round_num=1,
        severity="warning",
        criterion=6,
        file="src/app.py",
        line=1,
        anchor="line1",
        message="unused variable x",
    )
    cross = upsert_issue(
        state,
        agent="cc",
        round_num=1,
        severity="warning",
        criterion=14,
        file="tests/test_app.py",
        line=10,
        anchor="missing_test",
        message="missing regression test",
    )
    record_cross_verification(
        state,
        round_num=1,
        verifications=[{"report_id": lead["report_id"], "decision": "rebut", "reason": "not reproducible"}],
    )

    cli = FakeCli(state, state_file=str(tmp_path / "state.json"))
    orchestrator = DebateReviewOrchestrator(
        cli=cli,
        adapters={"codex": ScriptedAdapter("codex"), "cc": ScriptedAdapter("cc")},
        skill_root=SKILL_ROOT,
        config={"codex_sandbox": "danger-full-access"},
        cleanup_worktree=False,
    )
    orchestrator.state_file = cli.state_file

    checkpoint = {
        "step": "step3",
        "round": 1,
        "agent": "codex",
        "response": {
            "rebuttal_decisions": [{
                "issue_id": lead["issue_id"],
                "action": "withdraw",
                "reason": "agree with rebuttal",
            }],
            "cross_finding_evaluations": [{
                "issue_id": cross["issue_id"],
                "action": "accept",
                "reason": "valid issue",
            }],
            "withdrawals": [],
            "application_result": {
                "applied_issues": [],
                "failed_issues": [],
            },
        },
        "progress": {
            "withdrawals_done": 0,
            "decisions_done": False,
            "phase1_done": False,
            "phase2_done": False,
            "phase3_done": False,
        },
    }

    orchestrator._route_step3_checkpoint(checkpoint, {
        "round": 1,
        "lead_agent": "codex",
        "cross_verifier": "cc",
        "worktree_path": "/tmp/repo/.worktrees/debate-pr-123",
        "head_branch": "feat/test",
    })

    assert state["rounds"][0]["step3"]["withdrawn_report_ids"] == [lead["report_id"]]
    assert state["rounds"][0]["step3"]["accepted_report_ids"] == [cross["report_id"]]


def test_route_step1_checkpoint_raises_on_unexpected_withdrawal_error(monkeypatch, tmp_path):
    import debate_review.orchestrator as orchestrator_module

    checkpoint_path = tmp_path / "checkpoint.json"
    monkeypatch.setattr(orchestrator_module, "_checkpoint_path", lambda _state_file: str(checkpoint_path))

    state = _sample_state()
    init_round(state, round_num=1, synced_head_sha=state["head"]["last_observed_pr_sha"])

    class FailingCli(FakeCli):
        def withdraw_issue(self, _state_file, *, issue_id, agent, round_num, reason):
            raise OrchestrationError(f"Unknown issue ID: {issue_id}")

    cli = FailingCli(state, state_file=str(tmp_path / "state.json"))
    orchestrator = DebateReviewOrchestrator(
        cli=cli,
        adapters={"codex": ScriptedAdapter("codex"), "cc": ScriptedAdapter("cc")},
        skill_root=SKILL_ROOT,
        config={"codex_sandbox": "danger-full-access"},
        cleanup_worktree=False,
    )
    orchestrator.state_file = cli.state_file

    checkpoint = {
        "step": "step1",
        "round": 1,
        "agent": "codex",
        "response": {
            "rebuttal_responses": [],
            "withdrawals": [{"issue_id": "isu_999", "reason": "broken"}],
            "findings": [],
            "verdict": "has_findings",
        },
        "progress": {
            "rebuttals_done": False,
            "withdrawals_done": 0,
            "findings_done": 0,
            "verdict_done": False,
        },
    }

    with pytest.raises(OrchestrationError, match="Unknown issue ID: isu_999"):
        orchestrator._route_step1_checkpoint(checkpoint, {
            "round": 1,
            "lead_agent": "codex",
            "cross_verifier": "cc",
            "worktree_path": "/tmp/repo/.worktrees/debate-pr-123",
            "head_branch": "feat/test",
        })

    assert checkpoint["progress"]["withdrawals_done"] == 0


def test_orchestrator_marks_failed_and_posts_comment_on_dispatch_error(monkeypatch, tmp_path):
    import debate_review.orchestrator as orchestrator_module

    checkpoint_path = tmp_path / "checkpoint.json"
    monkeypatch.setattr(orchestrator_module, "_checkpoint_path", lambda _state_file: str(checkpoint_path))

    state = _sample_state()
    cli = FakeCli(state, state_file=str(tmp_path / "state.json"))

    class FailingAdapter(ScriptedAdapter):
        def send_message(self, session_id, message, *, worktree_path):
            raise RuntimeError("agent dispatch failed")

    orchestrator = DebateReviewOrchestrator(
        cli=cli,
        adapters={"codex": FailingAdapter("codex"), "cc": ScriptedAdapter("cc")},
        skill_root=SKILL_ROOT,
        config={"codex_sandbox": "danger-full-access"},
        cleanup_worktree=False,
    )

    with pytest.raises(RuntimeError, match="agent dispatch failed"):
        orchestrator.run(repo="owner/repo", pr_number=123)

    assert cli.mark_failed_calls == [("step1", "agent dispatch failed")]
    assert cli.post_comment_calls == [False]
    assert cli.state["status"] == "failed"


def test_dispatch_and_checkpoint_aborts_progress_on_error(monkeypatch, tmp_path):
    import debate_review.orchestrator as orchestrator_module

    checkpoint_path = tmp_path / "checkpoint.json"
    monkeypatch.setattr(orchestrator_module, "_checkpoint_path", lambda _state_file: str(checkpoint_path))

    state = _sample_state()
    cli = FakeCli(state, state_file=str(tmp_path / "state.json"))
    orchestrator = DebateReviewOrchestrator(
        cli=cli,
        adapters={"codex": ScriptedAdapter("codex"), "cc": ScriptedAdapter("cc")},
        skill_root=SKILL_ROOT,
        config={"codex_sandbox": "danger-full-access"},
        cleanup_worktree=False,
    )
    orchestrator.state_file = cli.state_file

    class RecordingProgress:
        def __init__(self):
            self.started = 0
            self.aborted = 0

        def step_start(self, *_args):
            self.started += 1

        def step_done(self, *_args):
            raise AssertionError("step_done should not be called on dispatch error")

        def abort_step(self):
            self.aborted += 1

    progress = RecordingProgress()
    orchestrator.progress = progress
    monkeypatch.setattr(
        orchestrator,
        "_dispatch_step",
        lambda **_kwargs: (_ for _ in ()).throw(RuntimeError("dispatch failed")),
    )

    with pytest.raises(RuntimeError, match="dispatch failed"):
        orchestrator._dispatch_and_checkpoint(
            step="step1",
            agent="codex",
            state=state,
            round_ctx={
                "round": 1,
                "lead_agent": "codex",
                "cross_verifier": "cc",
                "worktree_path": "/tmp/repo/.worktrees/debate-pr-123",
                "head_branch": "feat/test",
            },
        )

    assert progress.started == 1
    assert progress.aborted == 1


def test_mark_failed_calls_create_failure_issue(monkeypatch, tmp_path):
    """_mark_failed() should call create_failure_issue."""
    import debate_review.orchestrator as orchestrator_module

    checkpoint_path = tmp_path / "checkpoint.json"
    monkeypatch.setattr(orchestrator_module, "_checkpoint_path", lambda _state_file: str(checkpoint_path))

    state = _sample_state()
    cli = FakeCli(state, state_file=str(tmp_path / "state.json"))

    class FailingAdapter(ScriptedAdapter):
        def send_message(self, session_id, message, *, worktree_path):
            raise RuntimeError("agent dispatch failed")

    orchestrator = DebateReviewOrchestrator(
        cli=cli,
        adapters={"codex": FailingAdapter("codex"), "cc": ScriptedAdapter("cc")},
        skill_root=SKILL_ROOT,
        config={"codex_sandbox": "danger-full-access"},
        cleanup_worktree=False,
    )

    with pytest.raises(RuntimeError, match="agent dispatch failed"):
        orchestrator.run(repo="owner/repo", pr_number=123)

    assert cli.create_failure_issue_calls == [True]


def test_follow_through_errors_do_not_propagate(monkeypatch, tmp_path):
    """Follow-through errors should be swallowed, not crash the orchestrator."""
    import debate_review.orchestrator as orchestrator_module

    checkpoint_path = tmp_path / "checkpoint.json"
    monkeypatch.setattr(orchestrator_module, "_checkpoint_path", lambda _state_file: str(checkpoint_path))

    state = _sample_state()
    cli = FakeCli(state, state_file=str(tmp_path / "state.json"))

    # Override follow-through to raise
    def exploding_create(_state_file):
        raise RuntimeError("gh API down")

    cli.create_failure_issue = exploding_create

    codex = ScriptedAdapter(
        "codex",
        send=[{"rebuttal_responses": [], "withdrawals": [], "findings": [], "verdict": "no_findings_mergeable"}],
    )
    cc = ScriptedAdapter(
        "cc",
        send=[{"rebuttal_responses": [], "withdrawals": [], "findings": [], "verdict": "no_findings_mergeable"}],
    )

    orchestrator = DebateReviewOrchestrator(
        cli=cli,
        adapters={"codex": codex, "cc": cc},
        skill_root=SKILL_ROOT,
        config={"codex_sandbox": "danger-full-access"},
        cleanup_worktree=False,
    )

    # Should complete successfully despite follow-through failure
    result = orchestrator.run(repo="owner/repo", pr_number=123)
    assert result["result"] == "consensus_reached"


def test_build_adapters_cc_has_default_commands_in_persistent_mode():
    from debate_review.orchestrator import CcAdapter, _build_adapters

    config = {}

    adapters = _build_adapters(config)
    cc = adapters["cc"]
    assert isinstance(cc, CcAdapter)
    assert cc.create_command is not None
    assert cc.send_command is not None


def test_terminal_still_runs_follow_through_when_post_comment_fails(monkeypatch, tmp_path):
    import debate_review.orchestrator as orchestrator_module

    checkpoint_path = tmp_path / "checkpoint.json"
    monkeypatch.setattr(orchestrator_module, "_checkpoint_path", lambda _state_file: str(checkpoint_path))

    state = _sample_state()

    class CommentFailingCli(FakeCli):
        def post_comment(self, _state_file, *, no_comment):
            self.post_comment_calls.append(no_comment)
            raise RuntimeError("comment failed")

    cli = CommentFailingCli(state, state_file=str(tmp_path / "state.json"))
    codex = ScriptedAdapter(
        "codex",
        send=[{"rebuttal_responses": [], "withdrawals": [], "findings": [], "verdict": "no_findings_mergeable"}],
    )
    cc = ScriptedAdapter(
        "cc",
        send=[{"rebuttal_responses": [], "withdrawals": [], "findings": [], "verdict": "no_findings_mergeable"}],
    )

    orchestrator = DebateReviewOrchestrator(
        cli=cli,
        adapters={"codex": codex, "cc": cc},
        skill_root=SKILL_ROOT,
        config={"codex_sandbox": "danger-full-access"},
        cleanup_worktree=False,
    )

    with pytest.raises(RuntimeError, match="comment failed"):
        orchestrator.run(repo="owner/repo", pr_number=123)

    assert cli.mark_failed_calls == []
    assert cli.state["status"] == "consensus_reached"
    assert not checkpoint_path.exists(), "checkpoint must be cleared even when post_comment fails"


def test_mark_failed_still_runs_follow_through_when_post_comment_fails(monkeypatch, tmp_path):
    import debate_review.orchestrator as orchestrator_module

    checkpoint_path = tmp_path / "checkpoint.json"
    monkeypatch.setattr(orchestrator_module, "_checkpoint_path", lambda _state_file: str(checkpoint_path))

    state = _sample_state()

    class CommentFailingCli(FakeCli):
        def post_comment(self, _state_file, *, no_comment):
            self.post_comment_calls.append(no_comment)
            raise RuntimeError("comment failed")

    cli = CommentFailingCli(state, state_file=str(tmp_path / "state.json"))

    class FailingAdapter(ScriptedAdapter):
        def send_message(self, session_id, message, *, worktree_path):
            raise RuntimeError("agent dispatch failed")

    orchestrator = DebateReviewOrchestrator(
        cli=cli,
        adapters={"codex": FailingAdapter("codex"), "cc": ScriptedAdapter("cc")},
        skill_root=SKILL_ROOT,
        config={"codex_sandbox": "danger-full-access"},
        cleanup_worktree=False,
    )

    with pytest.raises(RuntimeError, match="comment failed"):
        orchestrator.run(repo="owner/repo", pr_number=123)

    assert cli.create_failure_issue_calls == [True]


def test_run_final_progress_treats_recommended_as_resolved(monkeypatch, tmp_path):
    import debate_review.orchestrator as orchestrator_module

    checkpoint_path = tmp_path / "checkpoint.json"
    monkeypatch.setattr(orchestrator_module, "_checkpoint_path", lambda _state_file: str(checkpoint_path))

    state = _sample_state()
    state["is_fork"] = True
    state["issues"]["isu_001"] = {
        "issue_id": "isu_001",
        "issue_key": "criterion:13|file:src/app.py|anchor:line1|kind:incorrect_algorithm",
        "opened_by": "codex",
        "introduced_in_round": 1,
        "criterion": 13,
        "file": "src/app.py",
        "line": 1,
        "anchor": "line1",
        "severity": "warning",
        "consensus_status": "accepted",
        "application_status": "recommended",
        "accepted_by": ["cc", "codex"],
        "rejected_by": [],
        "applied_by": None,
        "application_commit_sha": None,
        "consensus_reason": None,
        "reports": [
            {
                "report_id": "rpt_001",
                "agent": "codex",
                "round": 1,
                "severity": "warning",
                "message": "recommend this fix",
                "reported_at": "2026-04-04T00:00:00+00:00",
                "status": "open",
            }
        ],
        "created_at": "2026-04-04T00:00:00+00:00",
        "updated_at": "2026-04-04T00:00:00+00:00",
    }
    cli = FakeCli(state, state_file=str(tmp_path / "state.json"))
    codex = ScriptedAdapter(
        "codex",
        send=[{"rebuttal_responses": [], "withdrawals": [], "findings": [], "verdict": "no_findings_mergeable"}],
    )
    cc = ScriptedAdapter(
        "cc",
        send=[{"rebuttal_responses": [], "withdrawals": [], "findings": [], "verdict": "no_findings_mergeable"}],
    )

    class RecordingProgress:
        def __init__(self):
            self.final_calls = []

        def round_start(self, *_args):
            pass

        def step_start(self, *_args):
            pass

        def step_done(self, *_args):
            pass

        def step_skip(self, *_args):
            pass

        def debate_content(self, *_args):
            pass

        def settle(self, *_args, **_kwargs):
            pass

        def final_result(self, outcome, rounds, duration, *, applied, withdrawn, unresolved):
            self.final_calls.append(
                {
                    "outcome": outcome,
                    "rounds": rounds,
                    "duration": duration,
                    "applied": applied,
                    "withdrawn": withdrawn,
                    "unresolved": unresolved,
                }
            )

    orchestrator = DebateReviewOrchestrator(
        cli=cli,
        adapters={"codex": codex, "cc": cc},
        skill_root=SKILL_ROOT,
        config={"codex_sandbox": "danger-full-access"},
        cleanup_worktree=False,
    )
    progress = RecordingProgress()
    orchestrator.progress = progress

    result = orchestrator.run(repo="owner/repo", pr_number=123)

    assert result["result"] == "consensus_reached"
    assert progress.final_calls[-1]["unresolved"] == 0


def test_run_resumed_step4_announces_round_start(monkeypatch, tmp_path):
    import debate_review.orchestrator as orchestrator_module

    checkpoint_path = tmp_path / "checkpoint.json"
    monkeypatch.setattr(orchestrator_module, "_checkpoint_path", lambda _state_file: str(checkpoint_path))

    state = _sample_state()
    state["max_rounds"] = 1
    init_round(state, round_num=1, synced_head_sha=state["head"]["last_observed_pr_sha"])
    record_verdict(state, round_num=1, verdict="no_findings_mergeable")
    state["journal"]["step"] = "step1_lead_review"

    cli = FakeCli(state, state_file=str(tmp_path / "state.json"), init_status="resumed", next_step="step4")

    class RecordingProgress:
        def __init__(self):
            self.round_calls = []

        def round_start(self, round_num, lead, cross):
            self.round_calls.append((round_num, lead, cross))

        def step_start(self, *_args):
            pass

        def step_done(self, *_args):
            pass

        def step_skip(self, *_args):
            pass

        def debate_content(self, *_args):
            pass

        def settle(self, *_args, **_kwargs):
            pass

        def final_result(self, *_args, **_kwargs):
            pass

    orchestrator = DebateReviewOrchestrator(
        cli=cli,
        adapters={"codex": ScriptedAdapter("codex"), "cc": ScriptedAdapter("cc")},
        skill_root=SKILL_ROOT,
        config={"codex_sandbox": "danger-full-access"},
        cleanup_worktree=False,
    )
    progress = RecordingProgress()
    orchestrator.progress = progress

    result = orchestrator.run(repo="owner/repo", pr_number=123)

    assert result["result"] == "max_rounds_exceeded"
    assert progress.round_calls == [(1, "codex", "cc")]


def test_run_resumed_checkpoint_replays_step_summary(monkeypatch, tmp_path):
    import debate_review.orchestrator as orchestrator_module

    checkpoint_path = tmp_path / "checkpoint.json"
    monkeypatch.setattr(orchestrator_module, "_checkpoint_path", lambda _state_file: str(checkpoint_path))

    state = _sample_state()
    state["max_rounds"] = 1
    init_round(state, round_num=1, synced_head_sha=state["head"]["last_observed_pr_sha"])

    checkpoint_path.write_text(json.dumps({
        "step": "step1",
        "round": 1,
        "agent": "codex",
        "response": {
            "rebuttal_responses": [],
            "withdrawals": [],
            "findings": [],
            "verdict": "no_findings_mergeable",
        },
        "progress": {
            "rebuttals_done": False,
            "findings_done": 0,
            "withdrawals_done": 0,
            "verdict_done": False,
        },
    }))

    cli = FakeCli(state, state_file=str(tmp_path / "state.json"), init_status="resumed", next_step="step1")

    class RecordingProgress:
        def __init__(self):
            self.round_calls = []
            self.step_done_calls = []
            self.content_calls = []

        def round_start(self, round_num, lead, cross):
            self.round_calls.append((round_num, lead, cross))

        def step_start(self, *_args):
            pass

        def step_done(self, step, agent, action, elapsed, summary=""):
            self.step_done_calls.append((step, agent, action, elapsed, summary))

        def step_skip(self, *_args):
            pass

        def debate_content(self, lines):
            self.content_calls.append(lines)

        def settle(self, *_args, **_kwargs):
            pass

        def final_result(self, *_args, **_kwargs):
            pass

    orchestrator = DebateReviewOrchestrator(
        cli=cli,
        adapters={"codex": ScriptedAdapter("codex"), "cc": ScriptedAdapter("cc")},
        skill_root=SKILL_ROOT,
        config={"codex_sandbox": "danger-full-access"},
        cleanup_worktree=False,
    )
    progress = RecordingProgress()
    orchestrator.progress = progress

    result = orchestrator.run(repo="owner/repo", pr_number=123)

    assert result["result"] == "max_rounds_exceeded"
    assert progress.round_calls == [(1, "codex", "cc")]
    assert progress.step_done_calls[0][:3] == ("Step1", "codex", "lead review")
    assert progress.content_calls[0][-1] == "verdict: no_findings_mergeable"


def test_process_pending_checkpoint_clears_stale_head_checkpoint(monkeypatch, tmp_path):
    import debate_review.orchestrator as orchestrator_module

    checkpoint_path = tmp_path / "checkpoint.json"
    monkeypatch.setattr(orchestrator_module, "_checkpoint_path", lambda _state_file: str(checkpoint_path))

    state = _sample_state()
    state["max_rounds"] = 1
    init_round(state, round_num=1, synced_head_sha=state["head"]["last_observed_pr_sha"])

    checkpoint_path.write_text(json.dumps({
        "step": "step1",
        "round": 1,
        "head_sha": "stale999",
        "agent": "codex",
        "response": {
            "rebuttal_responses": [],
            "withdrawals": [],
            "findings": [],
            "verdict": "no_findings_mergeable",
        },
        "progress": {
            "rebuttals_done": False,
            "findings_done": 0,
            "withdrawals_done": 0,
            "verdict_done": False,
        },
    }))

    cli = FakeCli(state, state_file=str(tmp_path / "state.json"), init_status="resumed", next_step="step1")
    orchestrator = DebateReviewOrchestrator(
        cli=cli,
        adapters={"codex": ScriptedAdapter("codex"), "cc": ScriptedAdapter("cc")},
        skill_root=SKILL_ROOT,
        config={"codex_sandbox": "danger-full-access"},
        cleanup_worktree=False,
    )
    orchestrator.state_file = cli.state_file

    next_step = orchestrator._process_pending_checkpoint(state, {
        "round": 1,
        "lead_agent": "codex",
        "cross_verifier": "cc",
        "worktree_path": "/tmp/repo/.worktrees/debate-pr-123",
        "head_branch": "feat/test",
    })

    assert next_step is None
    assert not checkpoint_path.exists()


def test_terminal_cleanup_failure_does_not_override_terminal_result(monkeypatch, tmp_path):
    import debate_review.orchestrator as orchestrator_module

    checkpoint_path = tmp_path / "checkpoint.json"
    monkeypatch.setattr(orchestrator_module, "_checkpoint_path", lambda _state_file: str(checkpoint_path))

    state = _sample_state()
    cli = FakeCli(state, state_file=str(tmp_path / "state.json"))
    codex = ScriptedAdapter(
        "codex",
        send=[{"rebuttal_responses": [], "withdrawals": [], "findings": [], "verdict": "no_findings_mergeable"}],
    )
    cc = ScriptedAdapter(
        "cc",
        send=[{"rebuttal_responses": [], "withdrawals": [], "findings": [], "verdict": "no_findings_mergeable"}],
    )

    orchestrator = DebateReviewOrchestrator(
        cli=cli,
        adapters={"codex": codex, "cc": cc},
        skill_root=SKILL_ROOT,
        config={"codex_sandbox": "danger-full-access"},
        cleanup_worktree=True,
    )
    monkeypatch.setattr(
        orchestrator,
        "_cleanup_worktree",
        lambda _state: (_ for _ in ()).throw(RuntimeError("cleanup failed")),
    )

    result = orchestrator.run(repo="owner/repo", pr_number=123)

    assert result["result"] == "consensus_reached"
    assert cli.state["final_outcome"] == "consensus"
    assert cli.state["status"] == "consensus_reached"


def test_cleanup_worktree_skips_dry_run(monkeypatch, tmp_path):
    import debate_review.orchestrator as orchestrator_module

    state = _sample_state()
    state["dry_run"] = True
    worktree_path = tmp_path / ".worktrees" / "debate-pr-123"
    worktree_path.mkdir(parents=True)
    state["repo_root"] = str(tmp_path)

    cli = FakeCli(state, state_file=str(tmp_path / "state.json"))
    orchestrator = DebateReviewOrchestrator(
        cli=cli,
        adapters={"codex": ScriptedAdapter("codex"), "cc": ScriptedAdapter("cc")},
        skill_root=SKILL_ROOT,
        config={"codex_sandbox": "danger-full-access"},
        cleanup_worktree=True,
    )

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("subprocess.run should not be called for dry-run cleanup")

    monkeypatch.setattr(orchestrator_module.subprocess, "run", fail_if_called)

    orchestrator._cleanup_worktree(state)


# --- Agent response normalization tests ---

from debate_review.orchestrator import (
    _extract_json_from_text,
    _normalize_cross_verifications,
    _normalize_rebuttal_responses,
    _normalize_withdrawals,
    _parse_json_object,
    _unwrap_cc_result,
)


def test_unwrap_cc_result_plain_json():
    inner = json.dumps({"verdict": "no_findings_mergeable", "findings": []})
    wrapper = json.dumps({"type": "result", "result": inner})
    assert _unwrap_cc_result(wrapper) == {"verdict": "no_findings_mergeable", "findings": []}


def test_unwrap_cc_result_markdown_fenced_json():
    inner = '```json\n{"verdict": "has_findings", "findings": []}\n```'
    wrapper = json.dumps({"type": "result", "result": inner})
    assert _unwrap_cc_result(wrapper)["verdict"] == "has_findings"


def test_unwrap_cc_result_prose_with_embedded_json():
    inner = 'Some explanation.\n\n```json\n{"verdict": "has_findings", "findings": []}\n```'
    wrapper = json.dumps({"type": "result", "result": inner})
    assert _unwrap_cc_result(wrapper)["verdict"] == "has_findings"


def test_extract_json_from_text_plain():
    assert _extract_json_from_text('{"a": 1}') == '{"a": 1}'


def test_extract_json_from_text_fenced():
    assert json.loads(_extract_json_from_text('```json\n{"a": 1}\n```')) == {"a": 1}


def test_extract_json_from_text_returns_last_fenced_block():
    text = '```json\n{"a": 1}\n```\n\n```json\n{"b": 2}\n```'
    assert json.loads(_extract_json_from_text(text)) == {"b": 2}


def test_extract_json_from_text_prose():
    text = "Here is the result:\n\n```json\n{\"b\": 2}\n```\n\nDone."
    assert json.loads(_extract_json_from_text(text)) == {"b": 2}


def test_extract_json_from_text_prose_with_trailing_object():
    text = 'Reasoning first.\n\n{"c": 3, "nested": {"ok": true}}'
    assert json.loads(_extract_json_from_text(text)) == {"c": 3, "nested": {"ok": True}}


def test_extract_json_from_text_prefers_trailing_object_over_fenced_example():
    text = (
        'Analysis first.\n\n```json\n{"example": true}\n```\n\n{\n'
        '  "verdict": "has_findings",\n'
        '  "findings": []\n'
        "}"
    )
    assert json.loads(_extract_json_from_text(text)) == {
        "verdict": "has_findings",
        "findings": [],
    }


def test_parse_json_object_prose_with_fenced_json():
    text = 'Applied the fix.\n\n```json\n{"applied_issues": ["isu_001"], "failed_issues": []}\n```'
    assert _parse_json_object(text) == {"applied_issues": ["isu_001"], "failed_issues": []}


def test_parse_json_object_prose_with_trailing_object():
    text = 'Analysis complete.\n{"verdict": "has_findings", "findings": []}'
    assert _parse_json_object(text) == {"verdict": "has_findings", "findings": []}


def test_normalize_cross_verifications_issue_id_and_verdict():
    state = {"issues": {"isu_001": {"reports": [{"report_id": "rpt_001"}]}}}
    raw = [{"issue_id": "isu_001", "verdict": "rebut", "reason": "disagree"}]
    result = _normalize_cross_verifications(raw, state)
    assert result[0]["report_id"] == "rpt_001"
    assert result[0]["decision"] == "rebut"


def test_normalize_cross_verifications_issue_id_and_action():
    state = {"issues": {"isu_001": {"reports": [{"report_id": "rpt_001"}]}}}
    raw = [{"issue_id": "isu_001", "action": "accept", "reason": "agree"}]
    result = _normalize_cross_verifications(raw, state)
    assert result[0]["report_id"] == "rpt_001"
    assert result[0]["decision"] == "accept"


def test_normalize_cross_verifications_already_correct():
    state = {"issues": {}}
    raw = [{"report_id": "rpt_001", "decision": "accept"}]
    assert _normalize_cross_verifications(raw, state) == raw


def test_normalize_rebuttal_responses_issue_id_and_action():
    state = {"issues": {"isu_001": {"reports": [{"report_id": "rpt_001"}]}}}
    raw = [{"issue_id": "isu_001", "action": "maintain", "reason": "still valid"}]
    result = _normalize_rebuttal_responses(raw, [{"issue_id": "isu_001", "report_id": "rpt_001"}])
    assert result[0]["report_id"] == "rpt_001"
    assert result[0]["decision"] == "maintain"


def test_normalize_rebuttal_responses_prefers_candidate_report_over_latest_state():
    state = {
        "issues": {
            "isu_001": {
                "reports": [{"report_id": "rpt_001"}, {"report_id": "rpt_002"}],
            }
        }
    }
    raw = [{"issue_id": "isu_001", "action": "withdraw"}]
    result = _normalize_rebuttal_responses(raw, [{"issue_id": "isu_001", "report_id": "rpt_001"}])
    assert result[0]["report_id"] == "rpt_001"


def test_normalize_withdrawals_strings():
    assert _normalize_withdrawals(["isu_001", "isu_002"]) == [
        {"issue_id": "isu_001", "reason": ""},
        {"issue_id": "isu_002", "reason": ""},
    ]


def test_normalize_withdrawals_dicts():
    items = [{"issue_id": "isu_001", "reason": "no longer relevant"}]
    assert _normalize_withdrawals(items) == items


def test_normalize_withdrawals_mixed():
    items = ["isu_001", {"issue_id": "isu_002", "reason": "duplicate"}]
    result = _normalize_withdrawals(items)
    assert result[0] == {"issue_id": "isu_001", "reason": ""}
    assert result[1] == {"issue_id": "isu_002", "reason": "duplicate"}


# ──────────────────────────────────────────────────────────────────────
# E2E scenario tests
# ──────────────────────────────────────────────────────────────────────

_CLEAN_PASS = {"rebuttal_responses": [], "withdrawals": [], "findings": [], "verdict": "no_findings_mergeable"}


def _patch_checkpoint(monkeypatch, tmp_path):
    import debate_review.orchestrator as orchestrator_module

    checkpoint_path = tmp_path / "checkpoint.json"
    monkeypatch.setattr(orchestrator_module, "_checkpoint_path", lambda _state_file: str(checkpoint_path))
    return checkpoint_path


def test_e2e_clean_pass_consensus_persistent(monkeypatch, tmp_path):
    """Persistent mode: both agents clean pass over 2 rounds → consensus."""
    _patch_checkpoint(monkeypatch, tmp_path)

    state = _sample_state()
    cli = FakeCli(state, state_file=str(tmp_path / "state.json"))
    # Round 1: codex leads (step1), Round 2: cc leads (step1)
    codex = ScriptedAdapter("codex", send=[_CLEAN_PASS])
    cc = ScriptedAdapter("cc", send=[_CLEAN_PASS])

    orchestrator = DebateReviewOrchestrator(
        cli=cli,
        adapters={"codex": codex, "cc": cc},
        skill_root=SKILL_ROOT,
        config={"codex_sandbox": "danger-full-access"},
        cleanup_worktree=False,
    )

    result = orchestrator.run(repo="owner/repo", pr_number=123)

    assert result["result"] == "consensus_reached"
    assert cli.state["status"] == "consensus_reached"
    # Persistent agents were created
    assert len(codex.create_calls) == 1
    assert len(cc.create_calls) == 1
    # Each agent sent exactly 1 message (their lead step1)
    assert len(codex.send_calls) == 1
    assert len(cc.send_calls) == 1
    # Sessions were recorded
    assert cli.record_agent_sessions_calls


def test_e2e_code_apply_and_push_verify(monkeypatch, tmp_path):
    """Same-repo: issue found → accepted → code applied → push verified → consensus."""
    _patch_checkpoint(monkeypatch, tmp_path)

    state = _sample_state()
    cli = FakeCli(state, state_file=str(tmp_path / "state.json"))

    finding = {
        "severity": "warning",
        "criterion": 6,
        "file": "src/app.py",
        "line": 10,
        "anchor": "unused_var",
        "message": "unused variable x",
    }

    # Round 1 (codex leads):
    #   step1 — codex finds issue
    #   step2 — cc accepts
    #   step3 — codex applies code
    # Round 2 (cc leads): step1 — cc clean pass
    # Round 3 (codex leads): step1 — codex clean pass
    codex = ScriptedAdapter(
        "codex",
        send=[
            # R1 step1: lead review
            {"rebuttal_responses": [], "withdrawals": [], "findings": [finding], "verdict": "has_findings"},
            # R1 step3: lead response — apply code
            {
                "rebuttal_decisions": [],
                "cross_finding_evaluations": [],
                "withdrawals": [],
                "application_result": {
                    "applied_issues": [],  # placeholder — filled after upsert
                    "failed_issues": [],
                    "commit_sha": "deadbeef1234",
                },
            },
            # R3 step1: clean pass
            _CLEAN_PASS,
        ],
    )
    cc = ScriptedAdapter(
        "cc",
        send=[
            # R1 step2: cross-verify — accept
            {"cross_verifications": [], "withdrawals": [], "findings": []},
            # R2 step1: clean pass
            _CLEAN_PASS,
        ],
    )

    # After R1 step1, we need to know the issue_id for step2 cross_verifications
    # and step3 applied_issues. Use a wrapper on FakeCli to intercept.
    original_upsert = cli.upsert_issue
    captured_issue_ids = []

    def capturing_upsert(state_file, *, agent, round_num, finding, confirm_reopen=False):
        result = original_upsert(state_file, agent=agent, round_num=round_num, finding=finding, confirm_reopen=confirm_reopen)
        captured_issue_ids.append(result["issue_id"])
        # Patch the pending step2 and step3 responses with the real issue/report IDs
        if cc.send and "cross_verifications" in cc.send[0]:
            cc.send[0]["cross_verifications"] = [
                {"report_id": result["report_id"], "decision": "accept"}
            ]
        if len(codex.send) >= 1 and "application_result" in codex.send[0]:
            codex.send[0]["application_result"]["applied_issues"] = [result["issue_id"]]
        return result

    cli.upsert_issue = capturing_upsert

    orchestrator = DebateReviewOrchestrator(
        cli=cli,
        adapters={"codex": codex, "cc": cc},
        skill_root=SKILL_ROOT,
        config={"codex_sandbox": "danger-full-access"},
        cleanup_worktree=False,
    )

    result = orchestrator.run(repo="owner/repo", pr_number=123)

    assert result["result"] == "consensus_reached"
    assert len(captured_issue_ids) == 1
    issue_id = captured_issue_ids[0]
    # Issue was applied
    assert cli.state["issues"][issue_id]["application_status"] == "applied"
    assert cli.state["issues"][issue_id]["consensus_status"] == "accepted"
    # Application phases were called: phase1, phase2, phase3
    app_calls = cli.record_application_calls
    assert any(c["applied_issues"] is not None for c in app_calls)  # phase1
    assert any(c["commit_sha"] is not None for c in app_calls)  # phase2
    assert any(c["verify_push"] for c in app_calls)  # phase3
    # 3 rounds completed
    assert len(cli.state["rounds"]) == 3


def test_e2e_fork_recommendation_path(monkeypatch, tmp_path):
    """Fork PR: issue accepted → recommended (no push) → consensus."""
    _patch_checkpoint(monkeypatch, tmp_path)

    state = _sample_state()
    state["is_fork"] = True
    cli = FakeCli(state, state_file=str(tmp_path / "state.json"))

    finding = {
        "severity": "warning",
        "criterion": 13,
        "file": "src/handler.py",
        "line": 5,
        "anchor": "wrong_algo",
        "message": "incorrect algorithm",
    }

    # Round 1: codex leads, finds issue, cc accepts (→ recommended for fork),
    #   step3: codex returns empty application (fork can't push)
    # Round 2: cc leads, clean pass
    # Round 3: codex leads, clean pass
    codex = ScriptedAdapter(
        "codex",
        send=[
            {"rebuttal_responses": [], "withdrawals": [], "findings": [finding], "verdict": "has_findings"},
            # step3: no code applied (fork recommendation)
            {
                "rebuttal_decisions": [],
                "cross_finding_evaluations": [],
                "withdrawals": [],
                "application_result": {"applied_issues": [], "failed_issues": []},
            },
            _CLEAN_PASS,
        ],
    )
    cc = ScriptedAdapter(
        "cc",
        send=[
            {"cross_verifications": [], "withdrawals": [], "findings": []},
            _CLEAN_PASS,
        ],
    )

    # Patch cross_verifications with correct IDs after upsert
    original_upsert = cli.upsert_issue
    captured_issue_ids = []

    def capturing_upsert(state_file, *, agent, round_num, finding, confirm_reopen=False):
        result = original_upsert(state_file, agent=agent, round_num=round_num, finding=finding, confirm_reopen=confirm_reopen)
        captured_issue_ids.append(result["issue_id"])
        if cc.send and "cross_verifications" in cc.send[0]:
            cc.send[0]["cross_verifications"] = [
                {"report_id": result["report_id"], "decision": "accept"}
            ]
        return result

    cli.upsert_issue = capturing_upsert

    orchestrator = DebateReviewOrchestrator(
        cli=cli,
        adapters={"codex": codex, "cc": cc},
        skill_root=SKILL_ROOT,
        config={"codex_sandbox": "danger-full-access"},
        cleanup_worktree=False,
    )

    result = orchestrator.run(repo="owner/repo", pr_number=123)

    assert result["result"] == "consensus_reached"
    issue_id = captured_issue_ids[0]
    # Fork: issue is recommended, not applied
    assert cli.state["issues"][issue_id]["application_status"] == "recommended"
    # No push verify calls — fork can't push
    assert not any(c["verify_push"] for c in cli.record_application_calls)


def test_e2e_supersede_by_external_push(monkeypatch, tmp_path):
    """External push detected during sync_head → extra context injected into prompt."""
    _patch_checkpoint(monkeypatch, tmp_path)

    state = _sample_state()
    new_sha = "external_push_sha_999"

    class ExternalPushCli(FakeCli):
        def __init__(self, *args, external_on_round=1, **kwargs):
            super().__init__(*args, **kwargs)
            self.external_on_round = external_on_round
            self._sync_count = 0

        def sync_head(self, _state_file):
            self._sync_count += 1
            if self._sync_count == self.external_on_round:
                # Simulate external push on first sync
                self.state["head"]["last_observed_pr_sha"] = new_sha
                self.state["head"]["synced_worktree_sha"] = new_sha
                self.state["journal"]["step"] = "step0_sync"
                self.state["journal"]["pre_sync_head_sha"] = "abc1234def5678"
                self.state["journal"]["post_sync_head_sha"] = new_sha
                return {
                    "pre_sync_sha": "abc1234def5678",
                    "post_sync_sha": new_sha,
                    "external_change": True,
                    "superseded_rounds": [],
                }
            return super().sync_head(_state_file)

    cli = ExternalPushCli(state, state_file=str(tmp_path / "state.json"))

    # Both rounds clean pass (persistent mode)
    codex = ScriptedAdapter("codex", send=[_CLEAN_PASS])
    cc = ScriptedAdapter("cc", send=[_CLEAN_PASS])

    orchestrator = DebateReviewOrchestrator(
        cli=cli,
        adapters={"codex": codex, "cc": cc},
        skill_root=SKILL_ROOT,
        config={"codex_sandbox": "danger-full-access"},
        cleanup_worktree=False,
    )

    result = orchestrator.run(repo="owner/repo", pr_number=123)

    assert result["result"] == "consensus_reached"
    # Round 1 step1 build_prompt should have received extra context with the new SHA.
    # FakeCli.build_prompt_calls records (agent, step, round_num, extra).
    # The orchestrator sets round_extra_context when external_change is True.
    round1_prompt_calls = [c for c in cli.build_prompt_calls if c[2] == 1]
    assert any(c[3] is not None and new_sha in c[3] for c in round1_prompt_calls), (
        f"Expected extra context with SHA {new_sha} in round 1 prompt calls, got: {round1_prompt_calls}"
    )


def test_e2e_persistent_recovery_after_agent_loss(monkeypatch, tmp_path):
    """Persistent mode: send_message fails → recovery via create_session → consensus."""
    _patch_checkpoint(monkeypatch, tmp_path)

    state = _sample_state()
    cli = FakeCli(state, state_file=str(tmp_path / "state.json"))

    class FailOnceThenSucceed(ScriptedAdapter):
        """First send_message raises OrchestrationError, subsequent calls succeed normally."""
        def __init__(self, name, *, send):
            super().__init__(name, send=send)
            self._first_send_should_fail = True

        def send_message(self, session_id, message, *, worktree_path):
            if self._first_send_should_fail:
                self._first_send_should_fail = False
                raise OrchestrationError(f"{self.name} session expired")
            return super().send_message(session_id, message, worktree_path=worktree_path)

    # codex leads round 1 — first send fails, recovery creates new session, retry succeeds
    codex = FailOnceThenSucceed("codex", send=[_CLEAN_PASS])
    # cc leads round 2 — normal
    cc = ScriptedAdapter("cc", send=[_CLEAN_PASS])

    orchestrator = DebateReviewOrchestrator(
        cli=cli,
        adapters={"codex": codex, "cc": cc},
        skill_root=SKILL_ROOT,
        config={"codex_sandbox": "danger-full-access"},
        cleanup_worktree=False,
    )

    result = orchestrator.run(repo="owner/repo", pr_number=123)

    assert result["result"] == "consensus_reached"
    # Codex: 1 initial create + 1 recovery create = 2 create_calls
    assert len(codex.create_calls) == 2
    # CC: 1 initial create only
    assert len(cc.create_calls) == 1
    # Recovery was recorded: agent sessions updated with new handle
    assert len(cli.record_agent_sessions_calls) >= 2
    # Verify the recovered session handle was actually used in send_message.
    # ScriptedAdapter.send_calls records (session_id, message, worktree_path).
    # The second create returns "codex-session-2", which must be used for the retry.
    codex_send_session_ids = [call[0] for call in codex.send_calls]
    assert "codex-session-2" in codex_send_session_ids, (
        f"Expected recovery handle 'codex-session-2' in send_calls, got: {codex_send_session_ids}"
    )


def test_e2e_terminal_comment_no_comment_and_dry_run(monkeypatch, tmp_path):
    """Terminal: no_comment=True skips comment; dry_run=True also skips."""
    _patch_checkpoint(monkeypatch, tmp_path)

    # Test 1: no_comment=True
    state1 = _sample_state()
    cli1 = FakeCli(state1, state_file=str(tmp_path / "state1.json"))
    codex1 = ScriptedAdapter("codex", send=[_CLEAN_PASS])
    cc1 = ScriptedAdapter("cc", send=[_CLEAN_PASS])

    orchestrator1 = DebateReviewOrchestrator(
        cli=cli1,
        adapters={"codex": codex1, "cc": cc1},
        skill_root=SKILL_ROOT,
        config={"codex_sandbox": "danger-full-access"},
        no_comment=True,
        cleanup_worktree=False,
    )
    result1 = orchestrator1.run(repo="owner/repo", pr_number=123)
    assert result1["result"] == "consensus_reached"
    # post_comment was called with no_comment=True
    assert cli1.post_comment_calls == [True]

    # Test 2: dry_run=True
    state2 = _sample_state()
    state2["dry_run"] = True
    cli2 = FakeCli(state2, state_file=str(tmp_path / "state2.json"))
    codex2 = ScriptedAdapter("codex", send=[_CLEAN_PASS])
    cc2 = ScriptedAdapter("cc", send=[_CLEAN_PASS])

    orchestrator2 = DebateReviewOrchestrator(
        cli=cli2,
        adapters={"codex": codex2, "cc": cc2},
        skill_root=SKILL_ROOT,
        config={"codex_sandbox": "danger-full-access"},
        no_comment=False,
        cleanup_worktree=False,
    )
    result2 = orchestrator2.run(repo="owner/repo", pr_number=123)
    assert result2["result"] == "consensus_reached"
    # post_comment was called with no_comment=True (due to dry_run)
    assert cli2.post_comment_calls == [True]

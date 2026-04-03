import copy
import os

import pytest

from debate_review.application import (
    record_application_phase1,
    record_application_phase2,
    record_application_phase3,
)
from debate_review.cross_verification import record_cross_verification, resolve_rebuttals
from debate_review.issue_ops import upsert_issue, withdraw_issue
from debate_review.orchestrator import (
    DebateReviewOrchestrator,
    OrchestrationError,
    _build_adapters,
)
from debate_review.round_ops import init_round, record_verdict, settle_round
from debate_review.state import create_initial_state, mark_failed

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

    def init_session(self, **_kwargs):
        result = {
            "state_file": self.state_file,
            "status": self.init_status,
            "current_round": self.state["current_round"],
            "is_fork": self.state["is_fork"],
            "dry_run": self.state["dry_run"],
            "codex_sandbox": "danger-full-access",
            "language": self.state.get("language", "en"),
            "agent_mode": self.state["agent_mode"],
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


class ScriptedAdapter:
    def __init__(self, name, *, legacy=None, send=None):
        self.name = name
        self.legacy = list(legacy or [])
        self.send = list(send or [])
        self.create_calls = []
        self.run_calls = []
        self.send_calls = []

    def run_legacy(self, prompt, *, worktree_path, sandbox):
        self.run_calls.append((prompt, worktree_path, sandbox))
        if not self.legacy:
            raise AssertionError(f"{self.name} legacy queue exhausted")
        return self.legacy.pop(0)

    def create_session(self, prompt, *, worktree_path, sandbox):
        self.create_calls.append((prompt, worktree_path, sandbox))
        return f"{self.name}-session-{len(self.create_calls)}"

    def send_message(self, session_id, message, *, worktree_path):
        self.send_calls.append((session_id, message, worktree_path))
        if not self.send:
            raise AssertionError(f"{self.name} send queue exhausted")
        return self.send.pop(0)


def _sample_state(agent_mode="legacy"):
    state = create_initial_state(
        repo="owner/repo",
        repo_root="/tmp/repo",
        pr_number=123,
        is_fork=False,
        head_sha="abc1234def5678",
        pr_branch_name="feat/test",
        max_rounds=3,
        agent_mode=agent_mode,
    )
    return state


def test_orchestrator_run_legacy_clean_pass_consensus(monkeypatch, tmp_path):
    import debate_review.orchestrator as orchestrator_module

    checkpoint_path = tmp_path / "checkpoint.json"
    monkeypatch.setattr(orchestrator_module, "_checkpoint_path", lambda _state_file: str(checkpoint_path))

    state = _sample_state(agent_mode="legacy")
    cli = FakeCli(state, state_file=str(tmp_path / "state.json"))
    codex = ScriptedAdapter(
        "codex",
        legacy=[{"rebuttal_responses": [], "withdrawals": [], "findings": [], "verdict": "no_findings_mergeable"}],
    )
    cc = ScriptedAdapter(
        "cc",
        legacy=[{"rebuttal_responses": [], "withdrawals": [], "findings": [], "verdict": "no_findings_mergeable"}],
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
    assert cli.state["status"] == "consensus_reached"
    assert cli.state["final_outcome"] == "consensus"
    assert cli.post_comment_calls == [False]
    assert len(codex.run_calls) == 1
    assert len(cc.run_calls) == 1
    assert not checkpoint_path.exists()


def test_orchestrator_run_persistent_recovers_missing_handles(monkeypatch, tmp_path):
    import debate_review.orchestrator as orchestrator_module

    checkpoint_path = tmp_path / "checkpoint.json"
    monkeypatch.setattr(orchestrator_module, "_checkpoint_path", lambda _state_file: str(checkpoint_path))

    state = _sample_state(agent_mode="persistent")
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


def test_route_step3_checkpoint_resumes_remaining_phases(monkeypatch, tmp_path):
    import debate_review.orchestrator as orchestrator_module

    checkpoint_path = tmp_path / "checkpoint.json"
    monkeypatch.setattr(orchestrator_module, "_checkpoint_path", lambda _state_file: str(checkpoint_path))

    state = _sample_state(agent_mode="persistent")
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


@pytest.mark.parametrize(
    ("config", "expected_message"),
    [
        (
            {"agent_mode": "legacy"},
            "Missing runtime command for cc legacy mode",
        ),
        (
            {"agent_mode": "persistent"},
            "Missing runtime command for cc persistent mode",
        ),
    ],
)
def test_build_adapters_requires_cc_runtime_commands(config, expected_message):
    with pytest.raises(OrchestrationError, match=expected_message):
        _build_adapters(config)


def test_route_step3_checkpoint_processes_withdrawals(monkeypatch, tmp_path):
    import debate_review.orchestrator as orchestrator_module

    checkpoint_path = tmp_path / "checkpoint.json"
    monkeypatch.setattr(orchestrator_module, "_checkpoint_path", lambda _state_file: str(checkpoint_path))

    state = _sample_state(agent_mode="persistent")
    init_round(state, round_num=1, synced_head_sha=state["head"]["last_observed_pr_sha"])
    state["issues"]["isu_001"] = {
        "issue_id": "isu_001",
        "issue_key": "criterion:8|file:src/app.py|anchor:line1|kind:duplicate_logic",
        "opened_by": "codex",
        "introduced_in_round": 1,
        "criterion": 8,
        "file": "src/app.py",
        "line": 1,
        "anchor": "line1",
        "severity": "warning",
        "consensus_status": "open",
        "application_status": "pending",
        "accepted_by": ["codex"],
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
                "message": "duplicate logic",
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
            "withdrawals": [
                {
                    "issue_id": "isu_001",
                    "reason": "duplicate of isu_002",
                }
            ],
            "application_result": {
                "applied_issues": [],
                "failed_issues": [],
            },
        },
        "progress": {
            "decisions_done": True,
            "withdrawals_done": 0,
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
    assert cli.state["issues"]["isu_001"]["consensus_status"] == "withdrawn"
    assert cli.state["issues"]["isu_001"]["consensus_reason"] == "duplicate of isu_002"
    assert not checkpoint_path.exists()


def test_orchestrator_marks_failed_and_posts_comment_on_dispatch_error(monkeypatch, tmp_path):
    import debate_review.orchestrator as orchestrator_module

    checkpoint_path = tmp_path / "checkpoint.json"
    monkeypatch.setattr(orchestrator_module, "_checkpoint_path", lambda _state_file: str(checkpoint_path))

    state = _sample_state(agent_mode="legacy")
    cli = FakeCli(state, state_file=str(tmp_path / "state.json"))

    class FailingAdapter(ScriptedAdapter):
        def run_legacy(self, prompt, *, worktree_path, sandbox):
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

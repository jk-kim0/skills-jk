import json
import os
import tempfile

import pytest

from debate_review.prompt import (
    build_initial_prompt,
    build_prompt,
    build_step_message,
    prompt_file_path,
)
from debate_review.state import create_initial_state
from debate_review.issue_ops import upsert_issue
from debate_review.round_ops import init_round, record_verdict
from debate_review.cross_verification import record_cross_verification

# Skill root is 3 levels up from this test file (tests/ -> cc-codex-debate-review/)
SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _make_state(**overrides):
    defaults = dict(
        repo="owner/repo", repo_root="/tmp/repo", pr_number=42,
        is_fork=False, head_sha="abc123", pr_branch_name="feat/test",
    )
    defaults.update(overrides)
    return create_initial_state(**defaults)


# --- prompt_file_path ---

def test_prompt_file_path_format():
    path = prompt_file_path("owner/repo", 42, "cc")
    assert path.endswith("owner-repo-42-cc.md")
    assert "debate-state/prompts" in path


def test_prompt_file_path_different_agents():
    cc = prompt_file_path("owner/repo", 1, "cc")
    codex = prompt_file_path("owner/repo", 1, "codex")
    assert cc != codex


def test_prompt_file_path_distinguishes_dry_run_sessions():
    real = prompt_file_path("owner/repo", 42, "cc")
    dry_run = prompt_file_path("owner/repo", 42, "cc", dry_run=True)
    assert real != dry_run
    assert dry_run.endswith("owner-repo-42-cc.dry-run.md")


# --- build_initial_prompt ---

def test_build_initial_prompt_substitutes_placeholders():
    state = _make_state()
    result = build_initial_prompt(state, SKILL_ROOT)
    assert "owner/repo" in result
    assert "#42" in result
    assert "/tmp/repo/.worktrees/debate-pr-42" in result
    assert "{WORKTREE_PATH}" not in result


def test_build_initial_prompt_includes_review_criteria():
    state = _make_state()
    result = build_initial_prompt(state, SKILL_ROOT)
    # review-criteria.md content should be embedded
    assert len(result) > 500  # initial prompt + criteria should be substantial


# --- build_step_message ---

def test_step1_message_contains_round():
    state = _make_state()
    init_round(state, round_num=1, synced_head_sha="abc123")
    msg = build_step_message(state, step=1, round_num=1, skill_root=SKILL_ROOT)
    assert "Round 1" in msg
    assert "Lead Review" in msg


def test_step2_message_contains_lead_findings():
    state = _make_state()
    init_round(state, round_num=1, synced_head_sha="abc123")
    upsert_issue(state, agent="codex", round_num=1, severity="warning",
                 criterion=7, file="a.py", line=1, anchor="foo", message="Test")
    msg = build_step_message(state, step=2, round_num=1, skill_root=SKILL_ROOT)
    assert "Cross-Verification" in msg
    assert "Test" in msg


def test_step3_message_contains_applicable_issues():
    state = _make_state()
    init_round(state, round_num=1, synced_head_sha="abc123")
    upsert_issue(state, agent="codex", round_num=1, severity="warning",
                 criterion=7, file="a.py", line=1, anchor="foo", message="Fix this")
    record_verdict(state, round_num=1, verdict="has_findings")
    issue_id = list(state["issues"].keys())[0]
    report_id = state["issues"][issue_id]["reports"][0]["report_id"]
    record_cross_verification(state, round_num=1, verifications=[
        {"report_id": report_id, "decision": "accept", "reason": "ok"}
    ])
    msg = build_step_message(
        state,
        step=3,
        round_num=1,
        skill_root=SKILL_ROOT,
        state_file="/tmp/state.json",
    )
    assert "Lead Response" in msg
    assert "/tmp/repo/.worktrees/debate-pr-42" in msg
    assert "/tmp/state.json" in msg
    assert os.path.join(SKILL_ROOT, "bin", "debate-review") in msg
    assert "{DEBATE_REVIEW_BIN}" not in msg
    assert "{STATE_FILE}" not in msg


def test_step_message_invalid_step():
    state = _make_state()
    with pytest.raises(ValueError, match="Unknown step"):
        build_step_message(state, step=9, round_num=1, skill_root=SKILL_ROOT)


def test_step_message_extra_context():
    state = _make_state()
    init_round(state, round_num=1, synced_head_sha="abc123")
    msg = build_step_message(state, step=1, round_num=1, skill_root=SKILL_ROOT,
                             extra="Check security headers")
    assert "Check security headers" in msg
    assert "Additional Context" in msg


def test_step3_message_requires_state_file():
    state = _make_state()
    init_round(state, round_num=1, synced_head_sha="abc123")
    with pytest.raises(ValueError, match="state_file is required"):
        build_step_message(state, step=3, round_num=1, skill_root=SKILL_ROOT)


# --- build_prompt (integration: file I/O) ---

def test_build_prompt_init_creates_file(tmp_path, monkeypatch):
    monkeypatch.setattr("debate_review.prompt._PROMPTS_DIR", str(tmp_path))
    state = _make_state()
    result = build_prompt(state, agent="cc", step="init", skill_root=SKILL_ROOT)
    assert os.path.exists(result["prompt_file"])
    content = open(result["prompt_file"]).read()
    assert "owner/repo" in content
    assert result["message"] == content


def test_build_prompt_step_appends(tmp_path, monkeypatch):
    monkeypatch.setattr("debate_review.prompt._PROMPTS_DIR", str(tmp_path))
    state = _make_state()
    init_round(state, round_num=1, synced_head_sha="abc123")

    # Init first
    r1 = build_prompt(state, agent="codex", step="init", skill_root=SKILL_ROOT)
    init_size = os.path.getsize(r1["prompt_file"])

    # Step 1 appends
    r2 = build_prompt(state, agent="codex", step="1", round_num=1, skill_root=SKILL_ROOT)
    assert r2["prompt_file"] == r1["prompt_file"]
    step1_size = os.path.getsize(r2["prompt_file"])
    assert step1_size > init_size

    # Step 2 appends further
    r3 = build_prompt(state, agent="codex", step="2", round_num=1, skill_root=SKILL_ROOT)
    step2_size = os.path.getsize(r3["prompt_file"])
    assert step2_size > step1_size


def test_build_prompt_contains_separator(tmp_path, monkeypatch):
    monkeypatch.setattr("debate_review.prompt._PROMPTS_DIR", str(tmp_path))
    state = _make_state()
    init_round(state, round_num=1, synced_head_sha="abc123")

    build_prompt(state, agent="cc", step="init", skill_root=SKILL_ROOT)
    build_prompt(state, agent="cc", step="1", round_num=1, skill_root=SKILL_ROOT)

    content = open(prompt_file_path("owner/repo", 42, "cc")).read()
    assert "\n\n---\n\n" in content


def test_build_prompt_step3_substitutes_runtime_placeholders(tmp_path, monkeypatch):
    monkeypatch.setattr("debate_review.prompt._PROMPTS_DIR", str(tmp_path))
    state = _make_state()
    init_round(state, round_num=1, synced_head_sha="abc123")
    upsert_issue(state, agent="codex", round_num=1, severity="warning",
                 criterion=7, file="a.py", line=1, anchor="foo", message="Fix this")
    record_verdict(state, round_num=1, verdict="has_findings")
    issue_id = list(state["issues"].keys())[0]
    report_id = state["issues"][issue_id]["reports"][0]["report_id"]
    record_cross_verification(state, round_num=1, verifications=[
        {"report_id": report_id, "decision": "accept", "reason": "ok"}
    ])

    result = build_prompt(
        state,
        agent="cc",
        step="3",
        round_num=1,
        skill_root=SKILL_ROOT,
        state_file="/tmp/state.json",
    )

    assert "/tmp/state.json" in result["message"]
    assert os.path.join(SKILL_ROOT, "bin", "debate-review") in result["message"]
    assert "{DEBATE_REVIEW_BIN}" not in result["message"]
    assert "{STATE_FILE}" not in result["message"]


def test_build_prompt_requires_skill_root():
    state = _make_state()
    with pytest.raises(ValueError, match="skill_root is required"):
        build_prompt(state, agent="cc", step="init")


def test_build_prompt_step_requires_round():
    state = _make_state()
    with pytest.raises(ValueError, match="round is required"):
        build_prompt(state, agent="cc", step="1", skill_root=SKILL_ROOT)

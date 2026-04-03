from pathlib import Path


def test_agent_lead_response_prompt_passes_applied_issues_to_build_commit_message():
    prompt_path = Path(__file__).resolve().parents[1] / "agent-lead-response-prompt.md"
    prompt = prompt_path.read_text()

    assert "build-commit-message" in prompt
    assert "--applied-issues" in prompt


def test_agent_initial_prompt_exists_and_has_required_placeholders():
    prompt_path = Path(__file__).resolve().parents[1] / "agent-initial-prompt.md"
    prompt = prompt_path.read_text()

    for placeholder in ["{REPO}", "{PR_NUMBER}", "{WORKTREE_PATH}", "{OUTPUT_LANGUAGE}", "{REVIEW_CRITERIA}"]:
        assert placeholder in prompt, f"Missing placeholder {placeholder}"


def test_skill_doc_defers_persistent_agent_creation_until_worktree_exists():
    skill_path = Path(__file__).resolve().parents[1] / "SKILL.md"
    skill = skill_path.read_text()

    assert "after the first `init-round` provides `WORKTREE_PATH`" in skill
    assert "before the round loop" not in skill


def test_skill_doc_uses_codex_resume_subcommand_for_persistent_dispatch():
    skill_path = Path(__file__).resolve().parents[1] / "SKILL.md"
    skill = skill_path.read_text()

    assert 'codex exec resume "$CODEX_SESSION_ID" - < "$STEP_FILE"' in skill
    assert 'codex exec --resume "$CODEX_SESSION_ID" -s "$CODEX_SANDBOX" - < "$STEP_FILE"' not in skill


def test_skill_doc_explains_how_to_capture_codex_session_id():
    skill_path = Path(__file__).resolve().parents[1] / "SKILL.md"
    skill = skill_path.read_text()

    assert 'codex exec --json -s "$CODEX_SANDBOX" - < "$CODEX_PROMPT_FILE"' in skill
    assert 'select(.type == "thread.started") | .thread_id' in skill
    assert "CODEX_SESSION_ID=<parse session ID from CODEX_OUTPUT>" not in skill


def test_skill_doc_persists_agent_identifiers_for_persistent_restart():
    skill_path = Path(__file__).resolve().parents[1] / "SKILL.md"
    skill = skill_path.read_text()

    assert 'record-agent-sessions --state-file "$STATE_FILE"' in skill
    assert "`persistent_agents.cc_agent_id` / `persistent_agents.codex_session_id`" in skill


def test_skill_doc_open_issues_excludes_recommended_fork_items():
    skill_path = Path(__file__).resolve().parents[1] / "SKILL.md"
    skill = skill_path.read_text()

    assert (
        "`OPEN_ISSUES_JSON` | `show --json` → issues where `consensus_status` is `open` "
        "or (`accepted` and `application_status` not in (`applied`, `recommended`)) |"
    ) in skill

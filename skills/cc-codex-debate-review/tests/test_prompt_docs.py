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

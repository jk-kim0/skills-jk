from pathlib import Path


def test_agent_lead_response_prompt_passes_applied_issues_to_build_commit_message():
    prompt_path = Path(__file__).resolve().parents[1] / "agent-lead-response-prompt.md"
    prompt = prompt_path.read_text()

    assert "build-commit-message" in prompt
    assert "--applied-issues" in prompt

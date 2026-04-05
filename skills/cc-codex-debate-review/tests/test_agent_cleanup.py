from unittest.mock import patch

from debate_review.agent_cleanup import terminate_agents


def test_terminate_agents_no_sessions():
    """No-op when no agent sessions are recorded."""
    state = {"persistent_agents": {"cc_agent_id": None, "codex_session_id": None}}
    result = terminate_agents(state)
    assert result["cc_killed"] == 0
    assert result["codex_killed"] == 0


def test_terminate_agents_finds_codex():
    """Kills codex processes matching session ID."""
    state = {"persistent_agents": {"cc_agent_id": None, "codex_session_id": "019d542d"}}
    with patch("debate_review.agent_cleanup._find_pids_by_pattern", return_value=[12345]) as mock_find, \
         patch("debate_review.agent_cleanup._kill_pids", return_value=1) as mock_kill:
        result = terminate_agents(state)
    mock_find.assert_called_once_with("codex.*019d542d")
    mock_kill.assert_called_once_with([12345])
    assert result["codex_killed"] == 1


def test_terminate_agents_no_matching_processes():
    """Graceful when pgrep finds nothing."""
    state = {"persistent_agents": {"cc_agent_id": "agent-123", "codex_session_id": "sess-456"}}
    with patch("debate_review.agent_cleanup._find_pids_by_pattern", return_value=[]):
        result = terminate_agents(state)
    assert result["cc_killed"] == 0
    assert result["codex_killed"] == 0


def test_terminate_agents_missing_persistent_agents():
    """Handles state without persistent_agents key."""
    state = {}
    result = terminate_agents(state)
    assert result["cc_killed"] == 0
    assert result["codex_killed"] == 0

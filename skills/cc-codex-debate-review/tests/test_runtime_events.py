"""Tests for runtime event normalization helpers."""

from debate_review.runtime_events import extract_response_from_event, normalize_event


def test_normalize_codex_turn_started():
    event = normalize_event(
        "codex",
        {"type": "turn.started"},
        observed_at="2026-04-07T00:00:05+00:00",
    )

    assert event["agent"] == "codex"
    assert event["kind"] == "turn_started"
    assert event["display_status"] == "thinking"
    assert event["heartbeat"] == "strong"
    assert event["raw_type"] == "turn.started"


def test_normalize_claude_partial_delta():
    event = normalize_event(
        "cc",
        {
            "type": "stream_event.content_block_delta",
            "delta": {"text": "partial assistant text"},
        },
        observed_at="2026-04-07T00:00:06+00:00",
    )

    assert event["agent"] == "cc"
    assert event["kind"] == "assistant_delta"
    assert event["display_status"] == "streaming_output"
    assert event["summary"] == "partial assistant text"


def test_extract_response_from_claude_result_wrapper():
    response = extract_response_from_event(
        "cc",
        {
            "type": "result",
            "result": '{"verdict":"no_findings_mergeable","findings":[]}',
        },
    )

    assert response == {"verdict": "no_findings_mergeable", "findings": []}


def test_extract_response_from_codex_agent_message():
    response = extract_response_from_event(
        "codex",
        {
            "type": "item.completed",
            "item": {
                "type": "agent_message",
                "text": '{"verdict":"has_findings","findings":[{"severity":"warning"}]}',
            },
        },
    )

    assert response["verdict"] == "has_findings"
    assert response["findings"] == [{"severity": "warning"}]


def test_normalize_codex_command_execution_activity():
    event = normalize_event(
        "codex",
        {
            "type": "item.started",
            "item": {
                "type": "command_execution",
                "command": ["git", "status"],
            },
        },
        observed_at="2026-04-07T00:00:07+00:00",
    )

    assert event["agent"] == "codex"
    assert event["kind"] == "tool_activity"
    assert event["display_status"] == "tool_activity"
    assert event["heartbeat"] == "strong"

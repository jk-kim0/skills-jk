"""Normalize vendor runtime events into a shared supervision schema."""

from __future__ import annotations

import json

from debate_review.timing import utc_now_iso


def _extract_json_from_text(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return stripped

    try:
        json.loads(stripped)
        return stripped
    except (json.JSONDecodeError, ValueError):
        pass

    if stripped.startswith("```"):
        parts = stripped.split("```")
        for candidate in reversed(parts):
            candidate = candidate.strip()
            if not candidate or candidate == "json":
                continue
            if candidate.startswith("json"):
                candidate = candidate[4:].strip()
            try:
                json.loads(candidate)
                return candidate
            except (json.JSONDecodeError, ValueError):
                continue

    decoder = json.JSONDecoder()
    for index, char in enumerate(stripped):
        if char != "{":
            continue
        try:
            parsed, end = decoder.raw_decode(stripped[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return stripped[index : index + end]

    return stripped


def _parse_json_object(text: str | dict | None) -> dict | None:
    if isinstance(text, dict):
        return text
    if not isinstance(text, str):
        return None
    candidate = _extract_json_from_text(text)
    if not candidate:
        return None
    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _raw_type(raw_event: dict) -> str:
    return str(raw_event.get("type") or raw_event.get("event") or "")


def _extract_summary(raw_event: dict) -> str:
    delta = raw_event.get("delta")
    if isinstance(delta, dict) and isinstance(delta.get("text"), str):
        return delta["text"]

    item = raw_event.get("item")
    if isinstance(item, dict):
        if isinstance(item.get("text"), str):
            return item["text"]
        content = item.get("content")
        if isinstance(content, list):
            for entry in content:
                if isinstance(entry, dict) and isinstance(entry.get("text"), str):
                    return entry["text"]

    message = raw_event.get("message")
    if isinstance(message, dict):
        content = message.get("content")
        if isinstance(content, list):
            for entry in content:
                if isinstance(entry, dict) and isinstance(entry.get("text"), str):
                    return entry["text"]

    result = raw_event.get("result")
    return result if isinstance(result, str) else ""


def normalize_event(agent: str, raw_event: dict, *, observed_at: str | None = None) -> dict | None:
    observed_at = observed_at or utc_now_iso()
    raw_type = _raw_type(raw_event)

    if agent == "codex":
        item = raw_event.get("item", {})
        if raw_type == "thread.started":
            return {
                "ts": observed_at,
                "agent": agent,
                "phase": "spawn",
                "kind": "session_started",
                "status": "active",
                "display_status": "awaiting_first_event",
                "summary": "persistent session ready",
                "raw_type": raw_type,
                "heartbeat": "strong",
                "meta": {},
            }
        if raw_type == "turn.started":
            return {
                "ts": observed_at,
                "agent": agent,
                "phase": "stream",
                "kind": "turn_started",
                "status": "active",
                "display_status": "thinking",
                "summary": "turn started",
                "raw_type": raw_type,
                "heartbeat": "strong",
                "meta": {},
            }
        if raw_type in {"item.started", "item.completed"} and item.get("type") == "command_execution":
            return {
                "ts": observed_at,
                "agent": agent,
                "phase": "stream",
                "kind": "tool_activity",
                "status": "active",
                "display_status": "tool_activity",
                "summary": item.get("type", "command_execution"),
                "raw_type": raw_type,
                "heartbeat": "strong",
                "meta": {},
            }
        if raw_type == "item.completed" and item.get("type") == "agent_message":
            return {
                "ts": observed_at,
                "agent": agent,
                "phase": "stream",
                "kind": "assistant_output",
                "status": "active",
                "display_status": "streaming_output",
                "summary": _extract_summary(raw_event),
                "raw_type": raw_type,
                "heartbeat": "strong",
                "meta": {},
            }
        if raw_type == "turn.completed":
            return {
                "ts": observed_at,
                "agent": agent,
                "phase": "result",
                "kind": "turn_completed",
                "status": "completed",
                "display_status": "completed",
                "summary": "turn completed",
                "raw_type": raw_type,
                "heartbeat": "strong",
                "meta": {},
            }

    if agent == "cc":
        if raw_type == "system/init":
            return {
                "ts": observed_at,
                "agent": agent,
                "phase": "resume",
                "kind": "session_started",
                "status": "active",
                "display_status": "awaiting_first_event",
                "summary": "session metadata loaded",
                "raw_type": raw_type,
                "heartbeat": "strong",
                "meta": {},
            }
        if raw_type == "stream_event.message_start":
            return {
                "ts": observed_at,
                "agent": agent,
                "phase": "stream",
                "kind": "turn_started",
                "status": "active",
                "display_status": "thinking",
                "summary": "message started",
                "raw_type": raw_type,
                "heartbeat": "strong",
                "meta": {},
            }
        if raw_type == "stream_event.content_block_delta":
            return {
                "ts": observed_at,
                "agent": agent,
                "phase": "stream",
                "kind": "assistant_delta",
                "status": "active",
                "display_status": "streaming_output",
                "summary": _extract_summary(raw_event),
                "raw_type": raw_type,
                "heartbeat": "strong",
                "meta": {},
            }
        if raw_type == "assistant":
            return {
                "ts": observed_at,
                "agent": agent,
                "phase": "stream",
                "kind": "assistant_output",
                "status": "active",
                "display_status": "streaming_output",
                "summary": _extract_summary(raw_event),
                "raw_type": raw_type,
                "heartbeat": "strong",
                "meta": {},
            }
        if raw_type == "result":
            return {
                "ts": observed_at,
                "agent": agent,
                "phase": "result",
                "kind": "turn_completed",
                "status": "completed",
                "display_status": "completed",
                "summary": "result received",
                "raw_type": raw_type,
                "heartbeat": "strong",
                "meta": {},
            }
        if raw_type.startswith("system/hook_"):
            return {
                "ts": observed_at,
                "agent": agent,
                "phase": "stream",
                "kind": "hook_activity",
                "status": "active",
                "display_status": "tool_activity",
                "summary": raw_type,
                "raw_type": raw_type,
                "heartbeat": "strong",
                "meta": {},
            }
        if raw_type == "rate_limit_event":
            return {
                "ts": observed_at,
                "agent": agent,
                "phase": "stream",
                "kind": "rate_limit",
                "status": "warning",
                "display_status": "idle_but_alive",
                "summary": "rate limit event",
                "raw_type": raw_type,
                "heartbeat": "strong",
                "meta": {},
            }

    return None


def extract_response_from_event(agent: str, raw_event: dict) -> dict | None:
    raw_type = _raw_type(raw_event)

    if agent == "cc" and raw_type == "result":
        return _parse_json_object(raw_event.get("result"))

    if agent == "codex" and raw_type == "item.completed":
        item = raw_event.get("item", {})
        if item.get("type") == "agent_message":
            if isinstance(item.get("structured_output"), dict):
                return item["structured_output"]
            return _parse_json_object(item.get("text"))

    return None

"""Tests for error_log module."""

import json
import os

from debate_review.error_log import save_error_log


def test_save_error_log_creates_file(tmp_path, monkeypatch):
    monkeypatch.setattr("debate_review.error_log.ERROR_LOG_DIR", str(tmp_path))

    path = save_error_log(command="sync-head", error_message="git failed: timeout")

    assert os.path.exists(path)
    with open(path) as f:
        data = json.load(f)
    assert data["command"] == "sync-head"
    assert data["error"] == "git failed: timeout"
    assert data["state_file"] is None
    assert "timestamp" in data


def test_save_error_log_with_state_file(tmp_path, monkeypatch):
    monkeypatch.setattr("debate_review.error_log.ERROR_LOG_DIR", str(tmp_path))

    path = save_error_log(
        command="init",
        error_message="gh pr view failed",
        state_file="/tmp/state.json",
    )

    with open(path) as f:
        data = json.load(f)
    assert data["state_file"] == "/tmp/state.json"


def test_save_error_log_creates_directory(tmp_path, monkeypatch):
    log_dir = str(tmp_path / "nested" / "dir")
    monkeypatch.setattr("debate_review.error_log.ERROR_LOG_DIR", log_dir)

    path = save_error_log(command="post-comment", error_message="network error")

    assert os.path.exists(path)
    assert os.path.isdir(log_dir)

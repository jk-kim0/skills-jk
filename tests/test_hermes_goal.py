import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "bin" / "hermes-goal"


def run_goal(tmp_path, *args, check=True):
    env = os.environ.copy()
    env["HERMES_GOAL_HOME"] = str(tmp_path / "goals")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and result.returncode != 0:
        raise AssertionError(
            f"command failed: {result.returncode}\nstdout={result.stdout}\nstderr={result.stderr}"
        )
    return result


def test_goal_lifecycle_json(tmp_path):
    created = run_goal(tmp_path, "create", "Finish the migration", "--token-budget", "1000", "--json")
    payload = json.loads(created.stdout)
    goal = payload["goal"]
    assert goal["objective"] == "Finish the migration"
    assert goal["status"] == "active"
    assert goal["token_budget"] == 1000
    assert goal["remaining_tokens"] == 1000

    status = run_goal(tmp_path, "status", "--json")
    assert json.loads(status.stdout)["goal"]["goal_id"] == goal["goal_id"]

    completed = run_goal(tmp_path, "complete", "--note", "Verified all requirements", "--json")
    completed_goal = json.loads(completed.stdout)["goal"]
    assert completed_goal["status"] == "complete"
    assert completed_goal["completed_at"]
    assert completed_goal["notes"][-1]["text"] == "Verified all requirements"


def test_create_fails_when_active_goal_exists(tmp_path):
    run_goal(tmp_path, "create", "First goal")
    duplicate = run_goal(tmp_path, "create", "Second goal", check=False)
    assert duplicate.returncode != 0
    assert "already exists" in duplicate.stderr


def test_prompt_contains_codex_inspired_completion_audit(tmp_path):
    run_goal(tmp_path, "create", "Ship the reviewable PR")
    prompt = run_goal(tmp_path, "prompt").stdout
    assert "Continue working toward the active Hermes goal" in prompt
    assert "<objective>" in prompt
    assert "Ship the reviewable PR" in prompt
    assert "Completion audit" in prompt
    assert "Do not rely on intent" in prompt


def test_named_goal_slots_are_independent(tmp_path):
    run_goal(tmp_path, "--name", "alpha", "create", "Alpha objective")
    run_goal(tmp_path, "--name", "beta", "create", "Beta objective")

    alpha = json.loads(run_goal(tmp_path, "--name", "alpha", "status", "--json").stdout)["goal"]
    beta = json.loads(run_goal(tmp_path, "--name", "beta", "status", "--json").stdout)["goal"]

    assert alpha["objective"] == "Alpha objective"
    assert beta["objective"] == "Beta objective"
    assert alpha["goal_id"] != beta["goal_id"]


def test_clear_deletes_goal_state(tmp_path):
    run_goal(tmp_path, "create", "Temporary goal")
    run_goal(tmp_path, "clear")
    status = run_goal(tmp_path, "status")
    assert "No Hermes goal" in status.stdout

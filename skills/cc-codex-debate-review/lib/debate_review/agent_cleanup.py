"""Terminate persistent agent processes on session end."""

import subprocess
import sys


def _find_pids_by_pattern(pattern):
    """Find PIDs of processes matching a pattern via pgrep."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", pattern],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            return []
        return [int(pid) for pid in result.stdout.strip().split("\n") if pid.strip()]
    except (OSError, ValueError):
        return []


def _kill_pids(pids):
    """Send SIGTERM to a list of PIDs. Returns count of successfully signaled."""
    import signal
    killed = 0
    for pid in pids:
        try:
            import os
            os.kill(pid, signal.SIGTERM)
            killed += 1
        except ProcessLookupError:
            pass
        except PermissionError:
            print(f"WARNING: no permission to kill PID {pid}", file=sys.stderr)
    return killed


def terminate_agents(state) -> dict:
    """Terminate persistent agent processes recorded in state.

    Searches for running processes that match the recorded session IDs
    and sends SIGTERM to them.
    """
    agents = state.get("persistent_agents", {})
    result = {"cc_killed": 0, "codex_killed": 0, "errors": []}

    # Terminate Codex processes by session ID
    codex_sid = agents.get("codex_session_id")
    if codex_sid:
        pids = _find_pids_by_pattern(f"codex.*{codex_sid}")
        if pids:
            result["codex_killed"] = _kill_pids(pids)

    # Terminate CC (Claude) processes by agent ID
    cc_aid = agents.get("cc_agent_id")
    if cc_aid:
        pids = _find_pids_by_pattern(f"claude.*{cc_aid}")
        if pids:
            result["cc_killed"] = _kill_pids(pids)

    return result

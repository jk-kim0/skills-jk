import json

from debate_review.reporting import generate_sessions_report, render_sessions_report_markdown
from debate_review.state import create_initial_state, save_state
from debate_review.round_ops import init_round, settle_round
from debate_review.timing import complete_step_trace, record_step_timing, start_step_trace


def test_generate_sessions_report_uses_state_trace_and_cc_subagent_breakdown(tmp_path):
    state_dir = tmp_path / "debate-state"
    claude_projects_root = tmp_path / "claude-projects"
    codex_sessions_root = tmp_path / "codex-sessions"
    state_dir.mkdir()
    claude_projects_root.mkdir()
    codex_sessions_root.mkdir()

    state = create_initial_state(
        repo="owner/repo",
        repo_root="/tmp/repo",
        pr_number=123,
        is_fork=False,
        head_sha="abc123",
        pr_branch_name="feat/report",
        agent_mode="persistent",
    )
    init_round(state, round_num=1, lead_agent="cc", synced_head_sha="abc123")
    record_step_timing(state, "step0_sync", timestamp="2026-04-04T00:00:00+00:00")
    start_step_trace(
        state,
        round_num=1,
        step_name="step1_lead_review",
        agent="cc",
        started_at="2026-04-04T00:01:00+00:00",
        patch={
            "runtime_artifacts": {
                "subagent_log_path": str(
                    claude_projects_root / "project" / "session" / "subagents" / "agent-task-1.jsonl"
                )
            }
        },
    )
    complete_step_trace(
        state,
        round_num=1,
        step_name="step1_lead_review",
        completed_at="2026-04-04T00:03:00+00:00",
    )
    state["finished_at"] = "2026-04-04T00:05:00+00:00"
    state["status"] = "consensus_reached"
    state["final_outcome"] = "consensus"
    settle_round(state, round_num=1)
    save_state(state, str(state_dir / "owner-repo-123.json"))

    subagent_log = claude_projects_root / "project" / "session" / "subagents" / "agent-task-1.jsonl"
    subagent_log.parent.mkdir(parents=True)
    subagent_log.write_text(
        "\n".join(
            [
                json.dumps({
                    "timestamp": "2026-04-04T00:01:00Z",
                    "type": "user",
                    "message": {
                        "role": "user",
                        "content": [{"type": "text", "text": "You are the lead reviewer for debate review round 1 on owner/repo#123."}],
                    },
                }),
                json.dumps({
                    "timestamp": "2026-04-04T00:01:10Z",
                    "type": "assistant",
                    "message": {
                        "role": "assistant",
                        "content": [{"type": "tool_use", "id": "toolu_read", "name": "Read", "input": {"file_path": "/tmp/repo/app.py"}}],
                    },
                }),
                json.dumps({
                    "timestamp": "2026-04-04T00:01:20Z",
                    "type": "user",
                    "message": {
                        "role": "user",
                        "content": [{"type": "tool_result", "tool_use_id": "toolu_read", "content": "ok"}],
                    },
                }),
                json.dumps({
                    "timestamp": "2026-04-04T00:01:30Z",
                    "type": "assistant",
                    "message": {
                        "role": "assistant",
                        "content": [{"type": "tool_use", "id": "toolu_git", "name": "Bash", "input": {"command": "git diff --stat"}}],
                    },
                }),
                json.dumps({
                    "timestamp": "2026-04-04T00:01:45Z",
                    "type": "user",
                    "message": {
                        "role": "user",
                        "content": [{"type": "tool_result", "tool_use_id": "toolu_git", "content": "ok"}],
                    },
                }),
                json.dumps({
                    "timestamp": "2026-04-04T00:01:50Z",
                    "type": "assistant",
                    "message": {
                        "role": "assistant",
                        "content": [{"type": "tool_use", "id": "toolu_gh", "name": "Bash", "input": {"command": "gh pr diff 123 --repo owner/repo"}}],
                    },
                }),
                json.dumps({
                    "timestamp": "2026-04-04T00:02:00Z",
                    "type": "user",
                    "message": {
                        "role": "user",
                        "content": [{"type": "tool_result", "tool_use_id": "toolu_gh", "content": "ok"}],
                    },
                }),
                json.dumps({
                    "timestamp": "2026-04-04T00:03:00Z",
                    "type": "assistant",
                    "message": {"role": "assistant", "content": [{"type": "text", "text": "{\"verdict\":\"no_findings_mergeable\"}"}]},
                }),
            ]
        )
        + "\n"
    )

    report = generate_sessions_report(
        state_dir=state_dir,
        claude_projects_root=claude_projects_root,
        codex_sessions_root=codex_sessions_root,
    )

    assert report["totals"]["sessions"] == 1
    session = report["sessions"][0]
    assert session["repo"] == "owner/repo"
    assert session["pr_number"] == 123
    step = session["rounds"][0]["steps"]["step1_lead_review"]
    assert step["duration_seconds"] == 120.0
    assert step["agent_breakdown"]["local_file_seconds"] == 10.0
    assert step["agent_breakdown"]["local_git_seconds"] == 15.0
    assert step["agent_breakdown"]["github_api_seconds"] == 10.0
    assert step["agent_breakdown"]["reasoning_seconds"] == 85.0

    markdown = render_sessions_report_markdown(report)
    assert "owner/repo#123" in markdown
    assert "step1_lead_review" in markdown
    assert "GitHub/API" in markdown

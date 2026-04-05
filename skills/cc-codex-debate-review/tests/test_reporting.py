import json

from debate_review.reporting import (
    _classify_cc_invocation,
    _mark_stats_eligibility,
    _stats,
    generate_sessions_report,
    render_sessions_report_markdown,
)
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
    assert step["wall_clock_seconds"] == 120.0
    assert step["agent_active_seconds"] == 120.0
    assert step["duration_seconds"] == 120.0
    assert step["agent_breakdown"]["local_file_seconds"] == 10.0
    assert step["agent_breakdown"]["local_git_seconds"] == 15.0
    assert step["agent_breakdown"]["github_api_seconds"] == 10.0
    assert step["agent_breakdown"]["unattributed_seconds"] == 85.0
    assert "reasoning_seconds" not in step["agent_breakdown"]

    markdown = render_sessions_report_markdown(report)
    assert "owner/repo#123" in markdown
    assert "step1_lead_review" in markdown
    assert "| Round | Lead |" in markdown
    assert "| Step0 | Step1 |" in markdown or "Step1" in markdown
    assert "GitHub/API" in markdown
    assert "Unattributed" in markdown


def test_generate_sessions_report_uses_completed_population_for_stats_and_split_step2_findings(tmp_path):
    state_dir = tmp_path / "debate-state"
    claude_projects_root = tmp_path / "claude-projects"
    codex_sessions_root = tmp_path / "codex-sessions"
    state_dir.mkdir()
    claude_projects_root.mkdir()
    codex_sessions_root.mkdir(parents=True)

    state = create_initial_state(
        repo="owner/repo",
        repo_root="/tmp/repo",
        pr_number=456,
        is_fork=False,
        head_sha="abc456",
        pr_branch_name="feat/findings",
        agent_mode="persistent",
    )
    state["started_at"] = "2026-04-04T00:00:00+00:00"
    state["finished_at"] = "2026-04-04T00:10:00+00:00"
    state["status"] = "consensus_reached"
    state["final_outcome"] = "consensus"
    state["persistent_agents"]["codex_session_id"] = "session-codex-1"

    init_round(state, round_num=1, lead_agent="codex", synced_head_sha="abc456")
    state["rounds"][0]["started_at"] = "2026-04-04T00:00:00+00:00"
    state["rounds"][0]["completed_at"] = "2026-04-04T00:05:00+00:00"
    state["rounds"][0]["status"] = "completed"
    start_step_trace(
        state,
        round_num=1,
        step_name="step2_cross_review",
        agent="cc",
        started_at="2026-04-04T00:01:00+00:00",
        patch={
            "runtime_artifacts": {
                "subagent_log_path": str(
                    claude_projects_root / "project" / "session" / "subagents" / "agent-task-3.jsonl"
                )
            }
        },
    )
    complete_step_trace(
        state,
        round_num=1,
        step_name="step2_cross_review",
        completed_at="2026-04-04T00:05:00+00:00",
    )

    init_round(state, round_num=2, lead_agent="cc", synced_head_sha="abc456")
    state["rounds"][1]["started_at"] = "2026-04-04T00:05:00+00:00"
    state["rounds"][1]["completed_at"] = "2026-04-04T00:10:00+00:00"
    state["rounds"][1]["status"] = "completed"
    start_step_trace(
        state,
        round_num=2,
        step_name="step1_lead_review",
        agent="cc",
        started_at="2026-04-04T00:06:00+00:00",
        patch={
            "runtime_artifacts": {
                "subagent_log_path": str(
                    claude_projects_root / "project" / "session" / "subagents" / "agent-task-2.jsonl"
                )
            }
        },
    )
    complete_step_trace(
        state,
        round_num=2,
        step_name="step1_lead_review",
        completed_at="2026-04-04T00:08:00+00:00",
    )
    start_step_trace(
        state,
        round_num=2,
        step_name="step2_cross_review",
        agent="codex",
        started_at="2026-04-04T00:08:30+00:00",
    )
    complete_step_trace(
        state,
        round_num=2,
        step_name="step2_cross_review",
        completed_at="2026-04-04T00:09:10+00:00",
    )
    save_state(state, str(state_dir / "owner-repo-456.json"))

    cc_log = claude_projects_root / "project" / "session" / "subagents" / "agent-task-2.jsonl"
    cc_log.parent.mkdir(parents=True)
    cc_log.write_text(
        "\n".join(
            [
                json.dumps({"timestamp": "2026-04-04T00:06:00Z", "message": {"content": [{"type": "text", "text": "You are the lead reviewer for debate review round 2 on owner/repo#456."}]}}),
                json.dumps({"timestamp": "2026-04-04T00:06:10Z", "message": {"content": [{"type": "tool_use", "id": "read-1", "name": "Read", "input": {"file_path": "/tmp/repo/a.py"}}]}}),
                json.dumps({"timestamp": "2026-04-04T00:06:20Z", "message": {"content": [{"type": "tool_result", "tool_use_id": "read-1", "content": "ok"}]}}),
                json.dumps({"timestamp": "2026-04-04T00:08:00Z", "message": {"content": [{"type": "text", "text": "{\"verdict\":\"no_findings_mergeable\"}"}]}}),
            ]
        )
        + "\n"
    )

    cc_cross_log = claude_projects_root / "project" / "session" / "subagents" / "agent-task-3.jsonl"
    cc_cross_log.write_text(
        "\n".join(
            [
                json.dumps({"timestamp": "2026-04-04T00:01:00Z", "message": {"content": [{"type": "text", "text": "You are the cross-verifier for debate review round 1 on owner/repo#456."}]}}),
                json.dumps({"timestamp": "2026-04-04T00:01:10Z", "message": {"content": [{"type": "tool_use", "id": "gh-1", "name": "Bash", "input": {"command": "gh pr diff 456 --repo owner/repo"}}]}}),
                json.dumps({"timestamp": "2026-04-04T00:01:40Z", "message": {"content": [{"type": "tool_result", "tool_use_id": "gh-1", "content": "ok"}]}}),
                json.dumps({"timestamp": "2026-04-04T00:05:00Z", "message": {"content": [{"type": "text", "text": "{\"verdict\":\"has_findings\"}"}]}}),
            ]
        )
        + "\n"
    )

    codex_log = codex_sessions_root / "2026" / "04" / "04" / "rollout-2026-04-04T00-00-00-session-codex-1.jsonl"
    codex_log.parent.mkdir(parents=True)
    codex_log.write_text(
        "\n".join(
            [
                json.dumps({
                    "timestamp": "2026-04-04T00:00:00Z",
                    "type": "session_meta",
                    "payload": {
                        "id": "session-codex-1",
                        "cwd": "/tmp/repo/.worktrees/debate-pr-456",
                        "originator": "codex_exec",
                    },
                }),
                json.dumps({
                    "timestamp": "2026-04-04T00:00:01Z",
                    "type": "response_item",
                    "payload": {
                        "type": "message",
                        "role": "user",
                        "content": [{"type": "input_text", "text": "# Debate Review Agent: owner/repo #456"}],
                    },
                }),
                json.dumps({"timestamp": "2026-04-04T00:00:05Z", "type": "event_msg", "payload": {"type": "task_started", "turn_id": "turn-1"}}),
                json.dumps({"timestamp": "2026-04-04T00:00:06Z", "type": "turn_context", "payload": {"turn_id": "turn-1"}}),
                json.dumps({
                    "timestamp": "2026-04-04T00:00:07Z",
                    "type": "response_item",
                    "payload": {
                        "type": "message",
                        "role": "user",
                        "content": [{"type": "input_text", "text": "## Round 1 — Lead Review"}],
                    },
                }),
                json.dumps({
                    "timestamp": "2026-04-04T00:00:10Z",
                    "type": "response_item",
                    "payload": {
                        "type": "function_call",
                        "name": "exec_command",
                        "arguments": json.dumps({"cmd": "rg TODO src"}),
                        "call_id": "call-1",
                    },
                }),
                json.dumps({
                    "timestamp": "2026-04-04T00:00:20Z",
                    "type": "response_item",
                    "payload": {"type": "function_call_output", "call_id": "call-1", "output": "ok"},
                }),
                json.dumps({
                    "timestamp": "2026-04-04T00:00:25Z",
                    "type": "response_item",
                    "payload": {
                        "type": "function_call",
                        "name": "exec_command",
                        "arguments": json.dumps({"cmd": "gh pr diff 456 --repo owner/repo"}),
                        "call_id": "call-2",
                    },
                }),
                json.dumps({
                    "timestamp": "2026-04-04T00:00:35Z",
                    "type": "response_item",
                    "payload": {"type": "function_call_output", "call_id": "call-2", "output": "ok"},
                }),
                json.dumps({"timestamp": "2026-04-04T00:01:00Z", "type": "event_msg", "payload": {"type": "task_complete", "turn_id": "turn-1"}}),
                json.dumps({"timestamp": "2026-04-04T00:08:30Z", "type": "event_msg", "payload": {"type": "task_started", "turn_id": "turn-2"}}),
                json.dumps({"timestamp": "2026-04-04T00:08:31Z", "type": "turn_context", "payload": {"turn_id": "turn-2"}}),
                json.dumps({
                    "timestamp": "2026-04-04T00:08:32Z",
                    "type": "response_item",
                    "payload": {
                        "type": "message",
                        "role": "user",
                        "content": [{"type": "input_text", "text": "## Round 2 — Cross-Verification"}],
                    },
                }),
                json.dumps({
                    "timestamp": "2026-04-04T00:08:40Z",
                    "type": "response_item",
                    "payload": {
                        "type": "function_call",
                        "name": "exec_command",
                        "arguments": json.dumps({"cmd": "gh pr view 456 --repo owner/repo"}),
                        "call_id": "call-3",
                    },
                }),
                json.dumps({
                    "timestamp": "2026-04-04T00:08:50Z",
                    "type": "response_item",
                    "payload": {"type": "function_call_output", "call_id": "call-3", "output": "ok"},
                }),
                json.dumps({"timestamp": "2026-04-04T00:09:05Z", "type": "event_msg", "payload": {"type": "task_complete", "turn_id": "turn-2"}}),
            ]
        )
        + "\n"
    )

    dry_run_state = create_initial_state(
        repo="owner/repo",
        repo_root="/tmp/repo",
        pr_number=457,
        is_fork=False,
        head_sha="abc457",
        pr_branch_name="feat/dry-run",
        agent_mode="persistent",
        dry_run=True,
    )
    dry_run_state["started_at"] = "2026-04-04T01:00:00+00:00"
    dry_run_state["finished_at"] = "2026-04-04T04:00:00+00:00"
    dry_run_state["status"] = "consensus_reached"
    save_state(dry_run_state, str(state_dir / "owner-repo-457.json"))

    in_progress_state = create_initial_state(
        repo="owner/repo",
        repo_root="/tmp/repo",
        pr_number=458,
        is_fork=False,
        head_sha="abc458",
        pr_branch_name="feat/in-progress",
        agent_mode="persistent",
    )
    in_progress_state["started_at"] = "2026-04-04T02:00:00+00:00"
    init_round(in_progress_state, round_num=1, lead_agent="codex", synced_head_sha="abc458")
    in_progress_state["rounds"][0]["started_at"] = "2026-04-04T02:00:30+00:00"
    save_state(in_progress_state, str(state_dir / "owner-repo-458.json"))

    report = generate_sessions_report(
        state_dir=state_dir,
        claude_projects_root=claude_projects_root,
        codex_sessions_root=codex_sessions_root,
    )

    target_session = next(session for session in report["sessions"] if session["pr_number"] == 456)
    round1 = next(round_data for round_data in target_session["rounds"] if round_data["round"] == 1)
    step1 = round1["steps"]["step1_lead_review"]
    assert step1["agent"] == "codex"
    assert step1["agent_breakdown"]["local_file_seconds"] == 10.0
    assert step1["agent_breakdown"]["github_api_seconds"] == 10.0
    assert step1["agent_breakdown"]["unattributed_seconds"] == 35.0

    assert report["populations"]["sessions"]["total"] == 3
    assert report["populations"]["sessions"]["included_in_wall_clock_stats"] == 1
    assert report["populations"]["sessions"]["excluded_dry_run"] == 1
    assert report["populations"]["sessions"]["excluded_in_progress"] == 1
    assert report["populations"]["rounds"]["included_in_wall_clock_stats"] == 2
    assert report["populations"]["rounds"]["excluded_missing_completed_at"] == 1
    assert report["stats"]["session_wall_clock_seconds"]["median"] == 600.0
    assert report["stats"]["round_wall_clock_seconds"]["max"] == 300.0
    assert report["stats"]["lead_agent_round_wall_clock_seconds"]["cc"]["median"] == 300.0
    assert report["stats"]["lead_agent_round_wall_clock_seconds"]["codex"]["median"] == 300.0
    assert report["coverage"]["rounds_total"] == 2
    assert report["coverage"]["rounds_with_any_breakdown"] == 2
    assert report["stats"]["step_wall_clock_seconds_by_agent"]["step2_cross_review / cc"]["median"] == 240.0
    assert report["stats"]["step_wall_clock_seconds_by_agent"]["step2_cross_review / codex"]["median"] == 40.0
    assert report["stats"]["step_active_seconds_by_agent"]["step2_cross_review / cc"]["median"] == 240.0
    assert report["stats"]["step_active_seconds_by_agent"]["step2_cross_review / codex"]["median"] == 35.0
    assert any(finding["title"] == "Excluded Population" for finding in report["findings"])
    assert any(finding["title"] == "Cross-Reviewer Split" for finding in report["findings"])

    markdown = render_sessions_report_markdown(report)
    assert "## Findings" in markdown
    assert "## Statistics" in markdown
    assert "## Population" in markdown
    assert "Median" in markdown
    assert "Codex" in markdown
    assert "Completed Step Wall-Clock Durations By Agent" in markdown
    assert "Completed Step Active Durations By Agent" in markdown
    assert "step2_cross_review / cc" in markdown
    assert "excluded from stats" in markdown
    assert "## Appendix" in markdown


def test_stats_include_quartiles_and_markdown_uses_requested_column_order(tmp_path):
    assert _stats([10.0, 20.0, 30.0, 40.0, 50.0]) == {
        "count": 5,
        "min": 10.0,
        "p25": 20.0,
        "median": 30.0,
        "p75": 40.0,
        "max": 50.0,
        "average": 30.0,
    }

    state_dir = tmp_path / "debate-state"
    claude_projects_root = tmp_path / "claude-projects"
    codex_sessions_root = tmp_path / "codex-sessions"
    state_dir.mkdir()
    claude_projects_root.mkdir()
    codex_sessions_root.mkdir()

    state = create_initial_state(
        repo="owner/repo",
        repo_root="/tmp/repo",
        pr_number=999,
        is_fork=False,
        head_sha="abc999",
        pr_branch_name="feat/quartiles",
        agent_mode="persistent",
    )
    state["started_at"] = "2026-04-04T00:00:00+00:00"
    state["finished_at"] = "2026-04-04T00:10:00+00:00"
    state["status"] = "consensus_reached"
    state["final_outcome"] = "consensus"
    init_round(state, round_num=1, lead_agent="codex", synced_head_sha="abc999")
    state["rounds"][0]["started_at"] = "2026-04-04T00:00:00+00:00"
    state["rounds"][0]["completed_at"] = "2026-04-04T00:10:00+00:00"
    start_step_trace(
        state,
        round_num=1,
        step_name="step1_lead_review",
        agent="codex",
        started_at="2026-04-04T00:01:00+00:00",
    )
    complete_step_trace(
        state,
        round_num=1,
        step_name="step1_lead_review",
        completed_at="2026-04-04T00:02:00+00:00",
    )
    settle_round(state, round_num=1)
    save_state(state, str(state_dir / "owner-repo-999.json"))

    report = generate_sessions_report(
        state_dir=state_dir,
        claude_projects_root=claude_projects_root,
        codex_sessions_root=codex_sessions_root,
    )
    markdown = render_sessions_report_markdown(report)

    assert "| Metric | Count | Min | 25% | Median | 75% | Max | Average |" in markdown


def test_mark_stats_eligibility_uses_explicit_reason_flags():
    assert _mark_stats_eligibility(
        dry_run=False,
        in_progress=False,
        missing_completed_at=False,
    ) == (True, [])
    assert _mark_stats_eligibility(
        dry_run=True,
        in_progress=True,
        missing_completed_at=True,
    ) == (False, ["dry_run", "in_progress", "missing_completed_at"])


def test_population_table_explains_session_missing_completed_at_column(tmp_path):
    state_dir = tmp_path / "debate-state"
    claude_projects_root = tmp_path / "claude-projects"
    codex_sessions_root = tmp_path / "codex-sessions"
    state_dir.mkdir()
    claude_projects_root.mkdir()
    codex_sessions_root.mkdir()

    state = create_initial_state(
        repo="owner/repo",
        repo_root="/tmp/repo",
        pr_number=1001,
        is_fork=False,
        head_sha="abc1001",
        pr_branch_name="feat/population-note",
        agent_mode="persistent",
    )
    state["started_at"] = "2026-04-04T00:00:00+00:00"
    state["finished_at"] = "2026-04-04T00:05:00+00:00"
    state["status"] = "consensus_reached"
    state["final_outcome"] = "consensus"
    save_state(state, str(state_dir / "owner-repo-1001.json"))

    report = generate_sessions_report(
        state_dir=state_dir,
        claude_projects_root=claude_projects_root,
        codex_sessions_root=codex_sessions_root,
    )
    markdown = render_sessions_report_markdown(report)

    assert "Sessions do not use the Excluded Missing Completed At column" in markdown


def test_generate_sessions_report_uses_trace_session_handle_for_codex_matching(tmp_path):
    state_dir = tmp_path / "debate-state"
    claude_projects_root = tmp_path / "claude-projects"
    codex_sessions_root = tmp_path / "codex-sessions"
    state_dir.mkdir()
    claude_projects_root.mkdir()
    codex_sessions_root.mkdir(parents=True)

    state = create_initial_state(
        repo="owner/repo",
        repo_root="/tmp/repo",
        pr_number=789,
        is_fork=False,
        head_sha="abc789",
        pr_branch_name="feat/recovery",
        agent_mode="persistent",
    )
    state["persistent_agents"]["codex_session_id"] = "session-new"
    init_round(state, round_num=1, lead_agent="codex", synced_head_sha="abc789")
    start_step_trace(
        state,
        round_num=1,
        step_name="step1_lead_review",
        agent="codex",
        started_at="2026-04-04T00:00:00+00:00",
        patch={"persistent_session": {"handle": "session-old"}},
    )
    complete_step_trace(
        state,
        round_num=1,
        step_name="step1_lead_review",
        completed_at="2026-04-04T00:01:00+00:00",
    )
    state["finished_at"] = "2026-04-04T00:02:00+00:00"
    save_state(state, str(state_dir / "owner-repo-789.json"))

    old_log = codex_sessions_root / "2026" / "04" / "04" / "rollout-session-old.jsonl"
    old_log.parent.mkdir(parents=True, exist_ok=True)
    old_log.write_text(
        "\n".join(
            [
                json.dumps({"timestamp": "2026-04-04T00:00:00Z", "type": "session_meta", "payload": {"id": "session-old"}}),
                json.dumps({"timestamp": "2026-04-04T00:00:01Z", "type": "event_msg", "payload": {"type": "task_started", "turn_id": "turn-1"}}),
                json.dumps({"timestamp": "2026-04-04T00:00:01Z", "type": "turn_context", "payload": {"turn_id": "turn-1"}}),
                json.dumps({
                    "timestamp": "2026-04-04T00:00:02Z",
                    "type": "response_item",
                    "payload": {
                        "type": "message",
                        "role": "user",
                        "content": [{"type": "input_text", "text": "# Debate Review Agent: owner/repo #789"}],
                    },
                }),
                json.dumps({
                    "timestamp": "2026-04-04T00:00:03Z",
                    "type": "response_item",
                    "payload": {
                        "type": "message",
                        "role": "user",
                        "content": [{"type": "input_text", "text": "## Round 1 — Lead Review"}],
                    },
                }),
                json.dumps({
                    "timestamp": "2026-04-04T00:00:10Z",
                    "type": "response_item",
                    "payload": {
                        "type": "function_call",
                        "name": "exec_command",
                        "arguments": json.dumps({"cmd": "rg TODO src"}),
                        "call_id": "call-old",
                    },
                }),
                json.dumps({
                    "timestamp": "2026-04-04T00:00:20Z",
                    "type": "response_item",
                    "payload": {"type": "function_call_output", "call_id": "call-old", "output": "ok"},
                }),
                json.dumps({"timestamp": "2026-04-04T00:00:40Z", "type": "event_msg", "payload": {"type": "task_complete", "turn_id": "turn-1"}}),
            ]
        )
        + "\n"
    )

    new_log = codex_sessions_root / "2026" / "04" / "05" / "rollout-session-new.jsonl"
    new_log.parent.mkdir(parents=True, exist_ok=True)
    new_log.write_text(
        "\n".join(
            [
                json.dumps({"timestamp": "2026-04-04T00:00:00Z", "type": "session_meta", "payload": {"id": "session-new"}}),
                json.dumps({"timestamp": "2026-04-04T00:00:01Z", "type": "event_msg", "payload": {"type": "task_started", "turn_id": "turn-1"}}),
                json.dumps({"timestamp": "2026-04-04T00:00:01Z", "type": "turn_context", "payload": {"turn_id": "turn-1"}}),
                json.dumps({
                    "timestamp": "2026-04-04T00:00:02Z",
                    "type": "response_item",
                    "payload": {
                        "type": "message",
                        "role": "user",
                        "content": [{"type": "input_text", "text": "# Debate Review Agent: owner/repo #789"}],
                    },
                }),
                json.dumps({
                    "timestamp": "2026-04-04T00:00:03Z",
                    "type": "response_item",
                    "payload": {
                        "type": "message",
                        "role": "user",
                        "content": [{"type": "input_text", "text": "## Round 1 — Lead Review"}],
                    },
                }),
                json.dumps({
                    "timestamp": "2026-04-04T00:00:10Z",
                    "type": "response_item",
                    "payload": {
                        "type": "function_call",
                        "name": "exec_command",
                        "arguments": json.dumps({"cmd": "gh pr diff 789 --repo owner/repo"}),
                        "call_id": "call-new",
                    },
                }),
                json.dumps({
                    "timestamp": "2026-04-04T00:00:25Z",
                    "type": "response_item",
                    "payload": {"type": "function_call_output", "call_id": "call-new", "output": "ok"},
                }),
                json.dumps({"timestamp": "2026-04-04T00:00:50Z", "type": "event_msg", "payload": {"type": "task_complete", "turn_id": "turn-1"}}),
            ]
        )
        + "\n"
    )

    report = generate_sessions_report(
        state_dir=state_dir,
        claude_projects_root=claude_projects_root,
        codex_sessions_root=codex_sessions_root,
    )

    step = report["sessions"][0]["rounds"][0]["steps"]["step1_lead_review"]
    assert step["artifact_path"] == str(old_log)
    assert step["agent_breakdown"]["local_file_seconds"] == 10.0
    assert step["agent_breakdown"]["github_api_seconds"] == 0.0


def test_build_final_summary_includes_pr_url_and_round_timings():
    from debate_review.reporting import build_final_summary

    state = create_initial_state(
        repo="owner/repo",
        repo_root="/tmp/repo",
        pr_number=42,
        is_fork=False,
        head_sha="abc123",
        pr_branch_name="feat/test",
        agent_mode="persistent",
    )
    state["started_at"] = "2026-04-04T00:00:00+00:00"
    state["finished_at"] = "2026-04-04T00:05:30+00:00"
    state["final_outcome"] = "consensus"
    state["current_round"] = 2

    init_round(state, round_num=1, lead_agent="codex", synced_head_sha="abc123")
    state["rounds"][0]["started_at"] = "2026-04-04T00:00:10+00:00"
    state["rounds"][0]["completed_at"] = "2026-04-04T00:02:44+00:00"

    init_round(state, round_num=2, lead_agent="cc", synced_head_sha="abc123")
    state["rounds"][1]["started_at"] = "2026-04-04T00:02:50+00:00"
    state["rounds"][1]["completed_at"] = "2026-04-04T00:05:25+00:00"

    summary = build_final_summary(state)
    assert summary["pr_url"] == "https://github.com/owner/repo/pull/42"
    assert summary["outcome"] == "consensus"
    assert summary["total_rounds"] == 2
    assert summary["total_duration"] == "5m 30s"
    assert len(summary["round_timings"]) == 2
    assert summary["round_timings"][0]["round"] == 1
    assert summary["round_timings"][0]["lead_agent"] == "codex"
    assert summary["round_timings"][0]["duration"] == "2m 34s"
    assert summary["round_timings"][1]["round"] == 2
    assert summary["round_timings"][1]["duration"] == "2m 35s"


def test_export_debate_markdown_creates_file(tmp_path):
    from debate_review.reporting import export_debate_markdown

    state = create_initial_state(
        repo="owner/repo",
        repo_root="/tmp/repo",
        pr_number=42,
        is_fork=False,
        head_sha="abc123",
        pr_branch_name="feat/test",
        agent_mode="persistent",
    )
    state["started_at"] = "2026-04-04T00:00:00+00:00"
    state["finished_at"] = "2026-04-04T00:03:00+00:00"
    state["final_outcome"] = "consensus"
    state["current_round"] = 1

    init_round(state, round_num=1, lead_agent="codex", synced_head_sha="abc123")
    state["rounds"][0]["started_at"] = "2026-04-04T00:00:10+00:00"
    state["rounds"][0]["completed_at"] = "2026-04-04T00:02:50+00:00"

    output_path = str(tmp_path / "debate.md")
    result = export_debate_markdown(state, output_path)
    assert result == output_path

    content = (tmp_path / "debate.md").read_text()
    assert "# Debate Review: owner/repo#42" in content
    assert "https://github.com/owner/repo/pull/42" in content
    assert "**Outcome**: consensus" in content
    assert "3m 0s" in content
    assert "| 1 | codex |" in content


def test_export_debate_markdown_uses_latest_issue_message(tmp_path):
    from debate_review.reporting import export_debate_markdown

    state = create_initial_state(
        repo="owner/repo",
        repo_root="/tmp/repo",
        pr_number=42,
        is_fork=False,
        head_sha="abc123",
        pr_branch_name="feat/test",
        agent_mode="persistent",
    )
    state["final_outcome"] = "consensus"
    state["issues"]["isu_001"] = {
        "issue_id": "isu_001",
        "issue_key": "criterion:13|file:foo.py|anchor:bar|kind:incorrect_algorithm",
        "opened_by": "codex",
        "introduced_in_round": 1,
        "criterion": 13,
        "file": "foo.py",
        "line": 10,
        "anchor": "bar",
        "severity": "warning",
        "consensus_status": "accepted",
        "application_status": "applied",
        "accepted_by": ["codex", "cc"],
        "rejected_by": [],
        "applied_by": "codex",
        "application_commit_sha": "deadbeef",
        "consensus_reason": None,
        "reports": [
            {
                "report_id": "rpt_001",
                "agent": "codex",
                "round": 1,
                "severity": "warning",
                "message": "initial stale message",
                "reported_at": "2026-04-04T00:00:00+00:00",
                "status": "open",
            },
            {
                "report_id": "rpt_002",
                "agent": "cc",
                "round": 2,
                "severity": "warning",
                "message": "latest clarified message",
                "reported_at": "2026-04-04T00:01:00+00:00",
                "status": "open",
            },
        ],
        "created_at": "2026-04-04T00:00:00+00:00",
        "updated_at": "2026-04-04T00:01:00+00:00",
    }

    output_path = str(tmp_path / "debate.md")
    export_debate_markdown(state, output_path)

    content = (tmp_path / "debate.md").read_text()
    assert "latest clarified message" in content
    assert "initial stale message" not in content


def test_format_duration():
    from debate_review.reporting import _format_duration

    assert _format_duration(None) == "-"
    assert _format_duration(45.0) == "45s"
    assert _format_duration(0.0) == "0s"
    assert _format_duration(125.0) == "2m 5s"
    assert _format_duration(3600.0) == "60m 0s"


def test_generate_sessions_report_returns_empty_when_state_dir_is_missing(tmp_path):
    report = generate_sessions_report(
        state_dir=tmp_path / "missing-state-dir",
        claude_projects_root=tmp_path / "claude-projects",
        codex_sessions_root=tmp_path / "codex-sessions",
    )

    assert report["totals"]["sessions"] == 0
    assert report["sessions"] == []


def test_classify_cc_invocation():
    assert _classify_cc_invocation({}) == "unknown"
    assert _classify_cc_invocation({"persistent_agents": {}}) == "unknown"
    assert _classify_cc_invocation({"persistent_agents": {"cc_agent_id": None}}) == "unknown"
    assert _classify_cc_invocation({"persistent_agents": {"cc_agent_id": "a885e6c9e21155bb9"}}) == "agent-tool"
    assert _classify_cc_invocation({"persistent_agents": {"cc_agent_id": "cc-debate-agent"}}) == "agent-tool"
    assert _classify_cc_invocation({"persistent_agents": {"cc_agent_id": "760929c7-1b95-4382-93f0-2b956c"}}) == "subprocess"
    assert _classify_cc_invocation({"persistent_agents": {"cc_session_id": "7efd8d9d-c877-4045-a819-c20fe9"}}) == "subprocess"


def test_session_summary_includes_agent_mode_and_cc_invocation_type(tmp_path):
    state_dir = tmp_path / "debate-state"
    state_dir.mkdir()

    state = create_initial_state(
        repo="owner/repo",
        repo_root="/tmp/repo",
        pr_number=500,
        is_fork=False,
        head_sha="abc500",
        pr_branch_name="feat/inv",
        agent_mode="persistent",
    )
    state["persistent_agents"]["cc_agent_id"] = "760929c7-1b95-4382-93f0-2b956c"
    state["started_at"] = "2026-04-05T00:00:00+00:00"
    state["finished_at"] = "2026-04-05T00:05:00+00:00"
    state["status"] = "consensus_reached"
    state["final_outcome"] = "consensus"
    save_state(state, str(state_dir / "owner-repo-500.json"))

    state2 = create_initial_state(
        repo="owner/repo",
        repo_root="/tmp/repo",
        pr_number=501,
        is_fork=False,
        head_sha="abc501",
        pr_branch_name="feat/old",
        agent_mode="legacy",
    )
    state2["persistent_agents"]["cc_agent_id"] = "a885e6c9e21155bb9"
    state2["started_at"] = "2026-04-04T00:00:00+00:00"
    state2["finished_at"] = "2026-04-04T00:10:00+00:00"
    state2["status"] = "consensus_reached"
    state2["final_outcome"] = "consensus"
    save_state(state2, str(state_dir / "owner-repo-501.json"))

    report = generate_sessions_report(
        state_dir=state_dir,
        claude_projects_root=tmp_path / "cp",
        codex_sessions_root=tmp_path / "cs",
    )

    session_500 = next(s for s in report["sessions"] if s["pr_number"] == 500)
    assert session_500["agent_mode"] == "persistent"
    assert session_500["cc_invocation_type"] == "subprocess"

    session_501 = next(s for s in report["sessions"] if s["pr_number"] == 501)
    assert session_501["agent_mode"] == "legacy"
    assert session_501["cc_invocation_type"] == "agent-tool"

    assert "stats_by_invocation" in report
    assert "subprocess" in report["stats_by_invocation"]
    assert "agent-tool" in report["stats_by_invocation"]
    assert report["stats_by_invocation"]["subprocess"]["session_count"] == 1
    assert report["stats_by_invocation"]["agent-tool"]["session_count"] == 1

    markdown = render_sessions_report_markdown(report)
    assert "Statistics By CC Invocation Type" in markdown
    assert "Subprocess (`claude -p`)" in markdown
    assert "Agent Tool (old API)" in markdown
    assert "Agent mode: persistent" in markdown
    assert "CC invocation: subprocess" in markdown


def test_legacy_session_without_handles_is_classified_as_agent_tool(tmp_path):
    state_dir = tmp_path / "debate-state"
    state_dir.mkdir()

    state = create_initial_state(
        repo="owner/repo",
        repo_root="/tmp/repo",
        pr_number=502,
        is_fork=False,
        head_sha="abc502",
        pr_branch_name="feat/legacy",
        agent_mode="legacy",
    )
    state["started_at"] = "2026-04-03T00:00:00+00:00"
    state["finished_at"] = "2026-04-03T00:10:00+00:00"
    state["status"] = "consensus_reached"
    state["final_outcome"] = "consensus"
    save_state(state, str(state_dir / "owner-repo-502.json"))

    report = generate_sessions_report(
        state_dir=state_dir,
        claude_projects_root=tmp_path / "cp",
        codex_sessions_root=tmp_path / "cs",
    )

    session = next(s for s in report["sessions"] if s["pr_number"] == 502)
    assert session["cc_invocation_type"] == "agent-tool"
    assert report["stats_by_invocation"]["agent-tool"]["session_count"] == 1


def test_missing_agent_mode_key_defaults_to_agent_tool(tmp_path):
    """State files without agent_mode key should default to legacy → agent-tool."""
    state_dir = tmp_path / "debate-state"
    state_dir.mkdir()

    state = create_initial_state(
        repo="owner/repo",
        repo_root="/tmp/repo",
        pr_number=503,
        is_fork=False,
        head_sha="abc503",
        pr_branch_name="feat/old",
        agent_mode="legacy",
    )
    # Simulate real old state files that lack the agent_mode key entirely
    del state["agent_mode"]
    state["started_at"] = "2026-04-03T00:00:00+00:00"
    state["finished_at"] = "2026-04-03T00:10:00+00:00"
    state["status"] = "consensus_reached"
    state["final_outcome"] = "consensus"
    save_state(state, str(state_dir / "owner-repo-503.json"))

    report = generate_sessions_report(
        state_dir=state_dir,
        claude_projects_root=tmp_path / "cp",
        codex_sessions_root=tmp_path / "cs",
    )

    session = next(s for s in report["sessions"] if s["pr_number"] == 503)
    assert session["agent_mode"] == "legacy"
    assert session["cc_invocation_type"] == "agent-tool"
    assert report["stats_by_invocation"]["agent-tool"]["session_count"] == 1

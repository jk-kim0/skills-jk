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


def test_skill_doc_uses_codex_resume_subcommand_for_persistent_dispatch():
    skill_path = Path(__file__).resolve().parents[1] / "SKILL.md"
    skill = skill_path.read_text()

    assert 'codex exec resume "$CODEX_SESSION_ID" - < "$STEP_FILE"' in skill
    assert 'codex exec --resume "$CODEX_SESSION_ID" -s "$CODEX_SANDBOX" - < "$STEP_FILE"' not in skill


def test_skill_doc_explains_how_to_capture_codex_session_id():
    skill_path = Path(__file__).resolve().parents[1] / "SKILL.md"
    skill = skill_path.read_text()

    assert 'codex exec --json -s "$CODEX_SANDBOX" - < "$CODEX_PROMPT_FILE"' in skill
    assert 'select(.type == "thread.started") | .thread_id' in skill
    assert "CODEX_SESSION_ID=<parse session ID from CODEX_OUTPUT>" not in skill


def test_skill_doc_persists_agent_identifiers_for_persistent_restart():
    skill_path = Path(__file__).resolve().parents[1] / "SKILL.md"
    skill = skill_path.read_text()

    assert 'record-agent-sessions --state-file "$STATE_FILE"' in skill
    assert "`persistent_agents.cc_agent_id` / `persistent_agents.codex_session_id`" in skill


def test_all_step_prompts_include_withdrawals_in_output_schema():
    """All step prompts should include withdrawals field for schema consistency."""
    root = Path(__file__).resolve().parents[1]
    for step_file in ["prompt-step-1.md", "prompt-step-2.md", "prompt-step-3.md"]:
        prompt = (root / step_file).read_text()
        output_section = prompt.split("### Output", 1)[1]
        assert '"withdrawals": [' in output_section, (
            f"{step_file} missing withdrawals in output schema"
        )


def test_legacy_and_persistent_step3_both_have_withdrawals():
    """Both legacy and persistent Step 3 prompts should include withdrawals."""
    root = Path(__file__).resolve().parents[1]
    legacy = (root / "agent-lead-response-prompt.md").read_text()
    persistent = (root / "prompt-step-3.md").read_text()
    assert "withdrawals" in legacy, "Legacy Step 3 prompt missing withdrawals"
    assert "withdrawals" in persistent, "Persistent Step 3 prompt missing withdrawals"


def test_persistent_step_prompts_require_report_id_for_rebuttal_decisions():
    root = Path(__file__).resolve().parents[1]
    step1 = (root / "prompt-step-1.md").read_text()
    step3 = (root / "prompt-step-3.md").read_text()

    assert "Use the provided `report_id`" in step1
    assert "Use the provided `report_id`" in step3


def test_skill_doc_step3_routing_includes_withdrawals():
    """SKILL.md Step 3 routing should mention withdraw-issue processing."""
    skill_path = Path(__file__).resolve().parents[1] / "SKILL.md"
    skill = skill_path.read_text()
    step3_start = skill.index("### Step 3: Lead Agent Response + Code Application")
    step3_end = skill.index("### Step 4: Settlement")
    step3_section = skill[step3_start:step3_end]
    route_start = step3_section.index("#### Route Response")
    route_end = step3_section.index("#### Code Application (Same-Repo PR, 3-Phase)")
    route_section = step3_section[route_start:route_end]
    assert (
        "`withdrawals` → `withdraw-issue`" in route_section
    ), "SKILL.md Step 3 routing missing withdraw-issue"


def test_skill_doc_open_issues_excludes_recommended_fork_items():
    skill_path = Path(__file__).resolve().parents[1] / "SKILL.md"
    skill = skill_path.read_text()

    assert (
        "`OPEN_ISSUES_JSON` | `show --json` → issues where `consensus_status` is `open` "
        "or (`accepted` and `application_status` not in (`applied`, `recommended`)) |"
    ) in skill


def test_retry_success_error_reporting_skips_issue_creation_in_dry_run():
    skill_path = Path(__file__).resolve().parents[1] / "SKILL.md"
    skill = skill_path.read_text()
    start = skill.index("### Retry-Success Error Reporting")
    end = skill.index("### Testing the Error Reporting Pipeline")
    section = skill[start:end]

    assert "If `DRY_RUN=true`, do not create a GitHub issue" in section

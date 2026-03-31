from debate_review.state import create_initial_state
from debate_review.comment import build_comment_body, post_comment, _make_tag


def _consensus_state(is_fork=False):
    state = create_initial_state(
        repo="owner/repo", repo_root="/tmp/repo", pr_number=123,
        is_fork=is_fork, head_sha="abc123", pr_branch_name="feat/test",
    )
    state["status"] = "consensus_reached"
    state["final_outcome"] = "consensus"
    state["current_round"] = 3
    state["issues"]["isu_001"] = {
        "issue_id": "isu_001", "file": "src/foo.ts", "line": 42,
        "consensus_status": "accepted",
        "application_status": "applied" if not is_fork else "recommended",
        "accepted_by": ["cc", "codex"],
        "applied_by": "codex" if not is_fork else None,
        "reports": [
            {"report_id": "rpt_001", "agent": "codex", "round": 1, "severity": "critical", "message": "Missing validation", "reported_at": "t"},
        ],
    }
    state["issues"]["isu_002"] = {
        "issue_id": "isu_002", "file": "src/baz.ts", "line": 21,
        "consensus_status": "withdrawn",
        "application_status": "not_applicable",
        "accepted_by": [],
        "applied_by": None,
        "consensus_reason": "Intentional design choice",
        "reports": [
            {"report_id": "rpt_002", "agent": "cc", "round": 1, "severity": "warning", "message": "Unused import", "reported_at": "t"},
        ],
    }
    return state


# Test 1: Same-repo consensus template
def test_build_comment_consensus_same_repo():
    state = _consensus_state(is_fork=False)
    body = build_comment_body(state)
    assert body.startswith("[debate-review][sha:abc123]")
    assert "3라운드 만에 합의에 도달했습니다." in body
    assert "## Applied Fixes" in body
    assert "src/foo.ts:42" in body
    assert "reported by codex" in body
    assert "applied by codex" in body
    assert "## Withdrawn Findings" in body
    assert "src/baz.ts:21" in body
    assert "Intentional design choice" in body


# Test 2: Fork consensus template
def test_build_comment_consensus_fork():
    state = _consensus_state(is_fork=True)
    body = build_comment_body(state)
    assert "fork PR" in body
    assert "## Recommended Fixes" in body
    assert "reported by codex" in body
    assert "## Withdrawn Findings" in body


# Test 3: Max rounds template
def test_build_comment_max_rounds():
    state = create_initial_state(
        repo="owner/repo", repo_root="/tmp/repo", pr_number=123,
        is_fork=False, head_sha="abc123", pr_branch_name="feat/test",
    )
    state["status"] = "max_rounds_exceeded"
    state["final_outcome"] = "no_consensus"
    state["max_rounds"] = 10
    state["issues"]["isu_001"] = {
        "issue_id": "isu_001", "file": "src/a.py", "line": 1,
        "consensus_status": "open", "application_status": "pending",
        "accepted_by": ["codex"],
        "reports": [{"report_id": "rpt_001", "agent": "codex", "round": 1, "severity": "critical", "message": "Bug", "reported_at": "t"}],
    }
    body = build_comment_body(state)
    assert "10라운드 후 합의에 도달하지 못했습니다" in body
    assert "## Unresolved Issues" in body
    assert "Manual review required." in body


# Test 4: Error template
def test_build_comment_error():
    state = create_initial_state(
        repo="owner/repo", repo_root="/tmp/repo", pr_number=123,
        is_fork=False, head_sha="abc123", pr_branch_name="feat/test",
    )
    state["status"] = "failed"
    state["final_outcome"] = "error"
    state["error_message"] = "Codex parse failure"
    state["journal"]["round"] = 2
    state["journal"]["step"] = "step2_cross_review"
    body = build_comment_body(state)
    assert "오류로 인해 리뷰가 중단되었습니다" in body
    assert "Round: 2" in body
    assert "Step: step2_cross_review" in body
    assert "Error: Codex parse failure" in body


# Test 5: post_comment with --no-comment (dry run)
def test_post_comment_no_comment():
    state = _consensus_state()
    result = post_comment(state, no_comment=True)
    assert result["action"] == "dry_run"
    assert "[debate-review]" in result["body"]
    assert state.get("final_comment_id") is None


# Test 6: post_comment skips if already posted
def test_post_comment_already_posted():
    state = _consensus_state()
    state["final_comment_id"] = "IC_existing123"
    result = post_comment(state)
    assert result["action"] == "skipped"


# Test 7: post_comment backfills existing comment
def test_post_comment_backfill():
    state = _consensus_state()
    result = post_comment(
        state,
        _find_existing=lambda s: "IC_found456",
        _post=lambda s, b: None,
    )
    assert result["action"] == "backfilled"
    assert state["final_comment_id"] == "IC_found456"


# Test 8: post_comment posts and records
def test_post_comment_posts():
    state = _consensus_state()
    posted = []
    call_count = [0]
    def mock_find(s):
        call_count[0] += 1
        if call_count[0] == 1:
            return None  # first check: no existing
        return "IC_new789"  # verification after post

    result = post_comment(
        state,
        _find_existing=mock_find,
        _post=lambda s, b: posted.append(b),
    )
    assert result["action"] == "posted"
    assert state["final_comment_id"] == "IC_new789"
    assert len(posted) == 1


# Test: dry_run suppresses posting (auto-sets no_comment)
def test_post_comment_dry_run():
    state = _consensus_state()
    state["dry_run"] = True
    result = post_comment(state)
    assert result["action"] == "dry_run"
    assert state.get("final_comment_id") is None


# Test 9: No issues — shows "No actionable issues remain."
def test_build_comment_no_issues():
    state = create_initial_state(
        repo="owner/repo", repo_root="/tmp/repo", pr_number=123,
        is_fork=False, head_sha="abc123", pr_branch_name="feat/test",
    )
    state["final_outcome"] = "consensus"
    state["current_round"] = 2
    body = build_comment_body(state)
    assert "No actionable issues remain." in body


# Test: Debate Summary from ledger
def test_build_comment_includes_debate_summary():
    state = _consensus_state(is_fork=False)
    state["debate_ledger"] = [
        {"issue_id": "isu_001", "status": "accepted", "summary": "batch exit code — R1 제기, R1 합의", "round": 1},
        {"issue_id": "isu_003", "status": "withdrawn", "summary": "KeyboardInterrupt — R1 제기, R5 withdraw", "round": 5},
    ]
    body = build_comment_body(state)
    assert "## Debate Summary" in body
    assert "isu_001 [accepted]" in body
    assert "isu_003 [withdrawn]" in body
    assert "batch exit code" in body


def test_build_comment_no_debate_summary_when_empty_ledger():
    state = _consensus_state(is_fork=False)
    state["debate_ledger"] = []
    body = build_comment_body(state)
    assert "## Debate Summary" not in body


def test_build_comment_max_rounds_includes_debate_summary():
    state = create_initial_state(
        repo="owner/repo", repo_root="/tmp/repo", pr_number=123,
        is_fork=False, head_sha="abc123", pr_branch_name="feat/test",
    )
    state["status"] = "max_rounds_exceeded"
    state["final_outcome"] = "no_consensus"
    state["max_rounds"] = 10
    state["debate_ledger"] = [
        {"issue_id": "isu_001", "status": "accepted", "summary": "fixed in R3", "round": 3},
    ]
    body = build_comment_body(state)
    assert "## Debate Summary" in body
    assert "isu_001 [accepted]" in body


def test_build_comment_error_includes_debate_summary():
    state = create_initial_state(
        repo="owner/repo", repo_root="/tmp/repo", pr_number=123,
        is_fork=False, head_sha="abc123", pr_branch_name="feat/test",
    )
    state["status"] = "failed"
    state["final_outcome"] = "error"
    state["error_message"] = "Codex parse failure"
    state["journal"]["round"] = 3
    state["journal"]["step"] = "step2_cross_review"
    state["debate_ledger"] = [
        {"issue_id": "isu_001", "status": "accepted", "summary": "fixed in R2", "round": 2},
    ]
    body = build_comment_body(state)
    assert "## Debate Summary" in body
    assert "isu_001 [accepted]" in body
    assert "Codex parse failure" in body

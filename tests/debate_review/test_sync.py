from debate_review.state import create_initial_state
from debate_review.round_ops import init_round
from debate_review.sync import sync_head, _reset_issues_for_supersede


def _make_state_with_round():
    state = create_initial_state(
        repo="owner/repo", repo_root="/tmp/repo", pr_number=123,
        is_fork=False, head_sha="sha_initial", pr_branch_name="feat/test",
    )
    init_round(state, round_num=1, lead_agent="codex", synced_head_sha="sha_initial")
    return state


def test_sync_no_change():
    state = _make_state_with_round()
    result = sync_head(
        state,
        _get_head=lambda repo, pr: "sha_initial",
        _fetch=lambda rr, pn, tr: None,
        _ensure_wt=lambda rr, pn, tr: ("/tmp/wt", "sha_initial"),
    )
    assert result["external_change"] is False
    assert result["superseded_rounds"] == []
    assert state["head"]["last_observed_pr_sha"] == "sha_initial"
    assert state["journal"]["pre_sync_head_sha"] == "sha_initial"
    assert state["journal"]["post_sync_head_sha"] == "sha_initial"


def test_sync_own_commit_not_supersede():
    state = _make_state_with_round()
    state["rounds"][0]["step3"]["commit_sha"] = "sha_our_commit"
    result = sync_head(
        state,
        _get_head=lambda repo, pr: "sha_our_commit",
        _fetch=lambda rr, pn, tr: None,
        _ensure_wt=lambda rr, pn, tr: ("/tmp/wt", "sha_our_commit"),
    )
    assert result["external_change"] is False


def test_sync_external_change_supersede():
    state = _make_state_with_round()
    state["rounds"][0]["status"] = "completed"
    state["issues"]["isu_001"] = {
        "issue_id": "isu_001", "issue_key": "k1", "criterion": 1,
        "file": "a.py", "line": 1, "anchor": "f",
        "severity": "critical", "consensus_status": "accepted",
        "application_status": "applied", "accepted_by": ["cc", "codex"],
        "rejected_by": [], "applied_by": "codex", "application_commit_sha": "sha_old",
        "reports": [], "created_at": "t", "updated_at": "t",
    }
    result = sync_head(
        state,
        _get_head=lambda repo, pr: "sha_external",
        _fetch=lambda rr, pn, tr: None,
        _ensure_wt=lambda rr, pn, tr: ("/tmp/wt", "sha_external"),
    )
    assert result["external_change"] is True
    assert result["superseded_rounds"] == [1]
    assert state["rounds"][0]["status"] == "superseded"
    assert state["current_round"] == 2
    issue = state["issues"]["isu_001"]
    assert issue["consensus_status"] == "open"
    assert issue["accepted_by"] == []
    assert issue["application_status"] == "pending"
    assert issue["applied_by"] is None
    assert issue["application_commit_sha"] is None


def test_reset_issues_withdrawn_preserved():
    state = create_initial_state(
        repo="owner/repo", repo_root="/tmp/repo", pr_number=123,
        is_fork=False, head_sha="sha1", pr_branch_name="feat/test",
    )
    state["issues"]["isu_001"] = {
        "issue_id": "isu_001", "consensus_status": "withdrawn",
        "application_status": "not_applicable", "accepted_by": [],
    }
    _reset_issues_for_supersede(state)
    assert state["issues"]["isu_001"]["consensus_status"] == "withdrawn"
    assert state["issues"]["isu_001"]["application_status"] == "not_applicable"


def test_reset_issues_open_resets_accepted_by():
    state = create_initial_state(
        repo="owner/repo", repo_root="/tmp/repo", pr_number=123,
        is_fork=False, head_sha="sha1", pr_branch_name="feat/test",
    )
    state["issues"]["isu_001"] = {
        "issue_id": "isu_001", "consensus_status": "open",
        "application_status": "pending", "accepted_by": ["codex"],
    }
    _reset_issues_for_supersede(state)
    assert state["issues"]["isu_001"]["consensus_status"] == "open"
    assert state["issues"]["isu_001"]["accepted_by"] == []


def test_reset_issues_recommended_to_pending():
    state = create_initial_state(
        repo="owner/repo", repo_root="/tmp/repo", pr_number=123,
        is_fork=False, head_sha="sha1", pr_branch_name="feat/test",
    )
    state["issues"]["isu_001"] = {
        "issue_id": "isu_001", "consensus_status": "accepted",
        "application_status": "recommended", "accepted_by": ["cc", "codex"],
    }
    _reset_issues_for_supersede(state)
    assert state["issues"]["isu_001"]["consensus_status"] == "open"
    assert state["issues"]["isu_001"]["application_status"] == "pending"
    assert state["issues"]["isu_001"]["accepted_by"] == []


def test_sync_updates_state_fields():
    state = _make_state_with_round()
    result = sync_head(
        state,
        _get_head=lambda repo, pr: "sha_new",
        _fetch=lambda rr, pn, tr: None,
        _ensure_wt=lambda rr, pn, tr: ("/tmp/wt", "sha_new"),
    )
    assert state["head"]["last_observed_pr_sha"] == "sha_new"
    assert state["head"]["synced_worktree_sha"] == "sha_new"
    assert state["journal"]["post_sync_head_sha"] == "sha_new"
    assert state["journal"]["synced_worktree_sha"] == "sha_new"

from unittest.mock import patch

import pytest
from debate_review.state import create_initial_state
import json


@pytest.fixture(autouse=True)
def _passthrough_resolve_sha():
    """Default: _resolve_full_sha returns input as-is (no git subprocess)."""
    with patch("debate_review.application._resolve_full_sha", side_effect=lambda sha, **kw: sha):
        yield


@pytest.fixture
def sample_state():
    return create_initial_state(
        repo="owner/repo", repo_root="/tmp/repo", pr_number=123,
        is_fork=False, head_sha="abc1234def5678",
        pr_branch_name="feat/test", max_rounds=10,
    )


@pytest.fixture
def state_file(tmp_path, sample_state):
    path = tmp_path / "test-state.json"
    with open(path, "w") as f:
        json.dump(sample_state, f)
    return str(path)

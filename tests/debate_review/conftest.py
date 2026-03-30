import pytest
from debate_review.state import create_initial_state
import json


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

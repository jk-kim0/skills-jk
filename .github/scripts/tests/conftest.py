"""Pytest fixtures for respond_to_review tests."""

import pytest
from respond_to_review.config import Config
from respond_to_review.clients import GitClient, GitHubClient, ClaudeClient


class MockGitClient(GitClient):
    """테스트용 Git 클라이언트 목."""

    def __init__(self):
        self._status = ""
        self._commits = []
        self._pushed = False
        self._current_sha = "abc1234"

    def config(self, key: str, value: str) -> None:
        pass

    def status_porcelain(self) -> str:
        return self._status

    def add_all(self) -> None:
        pass

    def commit(self, message: str) -> None:
        self._commits.append(message)

    def push(self) -> None:
        self._pushed = True

    def rev_parse_short(self) -> str:
        return self._current_sha

    # Test helpers
    def set_status(self, status: str) -> None:
        self._status = status

    def set_sha(self, sha: str) -> None:
        self._current_sha = sha


class MockGitHubClient(GitHubClient):
    """테스트용 GitHub 클라이언트 목."""

    def __init__(self):
        self._checked_out_pr = None
        self._replies = []
        self._comments = []

    def checkout_pr(self, pr_number: int) -> None:
        self._checked_out_pr = pr_number

    def reply_to_review_comment(self, pr_number: int, comment_id: int, body: str) -> None:
        self._replies.append({
            "pr_number": pr_number,
            "comment_id": comment_id,
            "body": body,
        })

    def comment_on_pr(self, pr_number: int, body: str) -> None:
        self._comments.append({
            "pr_number": pr_number,
            "body": body,
        })


class MockClaudeClient(ClaudeClient):
    """테스트용 Claude 클라이언트 목."""

    def __init__(self, output: str = "Test output"):
        self._output = output
        self._prompts = []

    def run(self, prompt: str) -> str:
        self._prompts.append(prompt)
        return self._output

    def set_output(self, output: str) -> None:
        self._output = output


@pytest.fixture
def config():
    """기본 테스트 설정을 반환합니다."""
    return Config(
        gh_token="test-token",
        pr_number=123,
        comment_id=456,
        comment_body="이 함수의 이름을 변경해주세요.",
        comment_path="src/main.py",
        comment_line=10,
        is_review_comment=True,
        dry_run=True,
        debug=False,
    )


@pytest.fixture
def mock_git():
    """Mock Git 클라이언트를 반환합니다."""
    return MockGitClient()


@pytest.fixture
def mock_github():
    """Mock GitHub 클라이언트를 반환합니다."""
    return MockGitHubClient()


@pytest.fixture
def mock_claude():
    """Mock Claude 클라이언트를 반환합니다."""
    return MockClaudeClient()

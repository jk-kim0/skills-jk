"""Clients 모듈 테스트."""

import pytest
from respond_to_review.clients import CommandResult


class TestCommandResult:
    """CommandResult 데이터클래스 테스트."""

    def test_success_when_exit_code_zero(self):
        """exit code가 0이면 성공입니다."""
        result = CommandResult(exit_code=0, stdout="output", stderr="")
        assert result.success

    def test_failure_when_exit_code_nonzero(self):
        """exit code가 0이 아니면 실패입니다."""
        result = CommandResult(exit_code=1, stdout="", stderr="error")
        assert not result.success


class TestGitClientInterface:
    """GitClient 인터페이스 테스트."""

    def test_has_changes_with_modified_file(self, mock_git):
        """수정된 파일이 있으면 True를 반환합니다."""
        mock_git.set_status(" M src/main.py\n")
        assert mock_git.has_changes()

    def test_has_changes_with_no_changes(self, mock_git):
        """변경사항이 없으면 False를 반환합니다."""
        mock_git.set_status("")
        assert not mock_git.has_changes()

    def test_has_staged_changes(self, mock_git):
        """스테이징된 변경사항을 감지합니다."""
        mock_git.set_status("M  src/main.py\n")
        assert mock_git.has_staged_changes()
        assert not mock_git.has_unstaged_changes()

    def test_has_unstaged_changes(self, mock_git):
        """스테이징되지 않은 변경사항을 감지합니다."""
        mock_git.set_status(" M src/main.py\n")
        assert not mock_git.has_staged_changes()
        assert mock_git.has_unstaged_changes()

    def test_has_both_staged_and_unstaged(self, mock_git):
        """스테이징된 것과 아닌 것 모두 감지합니다."""
        mock_git.set_status("MM src/main.py\n")
        assert mock_git.has_staged_changes()
        assert mock_git.has_unstaged_changes()


class TestMockClaudeClient:
    """MockClaudeClient 테스트."""

    def test_run_returns_output(self, mock_claude):
        """run은 설정된 출력을 반환합니다."""
        mock_claude.set_output("Custom output")
        result = mock_claude.run("test prompt")
        assert result == "Custom output"

    def test_run_stores_prompts(self, mock_claude):
        """run은 전달된 프롬프트를 저장합니다."""
        mock_claude.run("first prompt")
        mock_claude.run("second prompt")
        assert mock_claude._prompts == ["first prompt", "second prompt"]

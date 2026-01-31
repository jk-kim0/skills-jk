"""외부 서비스 클라이언트 모듈."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import subprocess
import logging

logger = logging.getLogger(__name__)


@dataclass
class CommandResult:
    """명령어 실행 결과."""

    exit_code: int
    stdout: str
    stderr: str

    @property
    def success(self) -> bool:
        return self.exit_code == 0


class GitClient(ABC):
    """Git 클라이언트 인터페이스."""

    @abstractmethod
    def config(self, key: str, value: str) -> None:
        """git config를 설정합니다."""
        pass

    @abstractmethod
    def status_porcelain(self) -> str:
        """git status --porcelain 결과를 반환합니다."""
        pass

    @abstractmethod
    def add_all(self) -> None:
        """모든 변경사항을 스테이징합니다."""
        pass

    @abstractmethod
    def commit(self, message: str) -> None:
        """커밋을 생성합니다."""
        pass

    @abstractmethod
    def push(self) -> None:
        """현재 브랜치를 푸시합니다."""
        pass

    @abstractmethod
    def rev_parse_short(self) -> str:
        """현재 커밋의 short SHA를 반환합니다."""
        pass

    def has_changes(self) -> bool:
        """변경사항이 있는지 확인합니다."""
        return bool(self.status_porcelain().strip())

    def has_staged_changes(self) -> bool:
        """스테이징된 변경사항이 있는지 확인합니다."""
        status = self.status_porcelain()
        for line in status.splitlines():
            if line and line[0] in "MADRC":
                return True
        return False

    def has_unstaged_changes(self) -> bool:
        """스테이징되지 않은 변경사항이 있는지 확인합니다."""
        status = self.status_porcelain()
        for line in status.splitlines():
            if len(line) > 1 and line[1] in "MADRC":
                return True
        return False


class GitClientImpl(GitClient):
    """실제 Git 클라이언트 구현."""

    def _run(self, *args: str) -> CommandResult:
        """git 명령어를 실행합니다."""
        cmd = ["git"] + list(args)
        logger.debug(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        return CommandResult(result.returncode, result.stdout, result.stderr)

    def config(self, key: str, value: str) -> None:
        result = self._run("config", key, value)
        if not result.success:
            raise RuntimeError(f"git config failed: {result.stderr}")

    def status_porcelain(self) -> str:
        result = self._run("status", "--porcelain")
        if not result.success:
            raise RuntimeError(f"git status failed: {result.stderr}")
        return result.stdout

    def add_all(self) -> None:
        result = self._run("add", "-A")
        if not result.success:
            raise RuntimeError(f"git add failed: {result.stderr}")

    def commit(self, message: str) -> None:
        result = self._run("commit", "-m", message)
        if not result.success:
            raise RuntimeError(f"git commit failed: {result.stderr}")

    def push(self) -> None:
        result = self._run("push", "origin", "HEAD")
        if not result.success:
            raise RuntimeError(f"git push failed: {result.stderr}")

    def rev_parse_short(self) -> str:
        result = self._run("rev-parse", "--short", "HEAD")
        if not result.success:
            raise RuntimeError(f"git rev-parse failed: {result.stderr}")
        return result.stdout.strip()


class GitHubClient(ABC):
    """GitHub 클라이언트 인터페이스."""

    @abstractmethod
    def checkout_pr(self, pr_number: int) -> None:
        """PR 브랜치를 체크아웃합니다."""
        pass

    @abstractmethod
    def reply_to_review_comment(self, pr_number: int, comment_id: int, body: str) -> None:
        """리뷰 댓글에 답글을 작성합니다."""
        pass

    @abstractmethod
    def comment_on_pr(self, pr_number: int, body: str) -> None:
        """PR에 일반 댓글을 작성합니다."""
        pass


class GitHubClientImpl(GitHubClient):
    """실제 GitHub 클라이언트 구현 (gh CLI 사용)."""

    def _run_gh(self, *args: str) -> CommandResult:
        """gh 명령어를 실행합니다."""
        cmd = ["gh"] + list(args)
        logger.debug(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        return CommandResult(result.returncode, result.stdout, result.stderr)

    def checkout_pr(self, pr_number: int) -> None:
        result = self._run_gh("pr", "checkout", str(pr_number))
        if not result.success:
            raise RuntimeError(f"gh pr checkout failed: {result.stderr}")

    def reply_to_review_comment(self, pr_number: int, comment_id: int, body: str) -> None:
        result = self._run_gh(
            "api",
            "--method", "POST",
            "-H", "Accept: application/vnd.github+json",
            f"/repos/{{owner}}/{{repo}}/pulls/{pr_number}/comments/{comment_id}/replies",
            "-f", f"body={body}",
        )
        if not result.success:
            raise RuntimeError(f"gh api failed: {result.stderr}")

    def comment_on_pr(self, pr_number: int, body: str) -> None:
        result = self._run_gh("pr", "comment", str(pr_number), "--body", body)
        if not result.success:
            raise RuntimeError(f"gh pr comment failed: {result.stderr}")


class ClaudeClient(ABC):
    """Claude Code 클라이언트 인터페이스."""

    @abstractmethod
    def run(self, prompt: str) -> str:
        """Claude Code를 실행하고 출력을 반환합니다."""
        pass


class ClaudeClientImpl(ClaudeClient):
    """실제 Claude Code 클라이언트 구현."""

    def run(self, prompt: str) -> str:
        logger.info("Running Claude Code...")
        result = subprocess.run(
            ["claude", "--print", prompt],
            capture_output=True,
            text=True,
        )
        logger.info(f"Claude Code exit code: {result.returncode}")
        logger.info(f"Claude Code output length: {len(result.stdout)}")

        if result.returncode != 0:
            raise RuntimeError(f"Claude Code failed (exit code: {result.returncode}): {result.stderr}")

        return result.stdout

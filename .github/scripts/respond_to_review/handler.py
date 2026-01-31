"""PR 리뷰 응답 핸들러."""

from dataclasses import dataclass
from typing import Optional
import logging
import os

from .config import Config
from .clients import GitClient, GitHubClient, ClaudeClient

logger = logging.getLogger(__name__)


@dataclass
class ReviewResponse:
    """리뷰 응답 결과."""

    success: bool
    message: str
    commit_sha: Optional[str] = None
    has_changes: bool = False


class ReviewHandler:
    """PR 리뷰 댓글 처리 핸들러."""

    def __init__(
        self,
        config: Config,
        git: GitClient,
        github: GitHubClient,
        claude: ClaudeClient,
    ):
        self.config = config
        self.git = git
        self.github = github
        self.claude = claude

    def build_prompt(self) -> str:
        """Claude에 전달할 프롬프트를 생성합니다."""
        prompt = f"""PR 리뷰 댓글을 처리해주세요.

## 댓글 내용
{self.config.comment_body}
"""

        if self.config.is_review_comment and self.config.comment_path:
            prompt += f"""
## 대상 파일
파일: {self.config.comment_path}
라인: {self.config.comment_line or '전체'}
"""

        prompt += """
## 지침
1. 댓글의 요청사항을 분석하세요.
2. 코드 수정이 필요하면 수정하고 커밋하세요.
3. 요청이 불명확하면 질문하세요.
4. 처리가 어려우면 이유를 설명하세요.

커밋 메시지 형식: 'fix: <변경 내용 요약>'
커밋 trailer 추가: 'Co-Authored-By: Atlas <atlas@jk.agent>'
"""
        return prompt

    def setup_git(self) -> None:
        """Git 설정을 초기화합니다."""
        logger.info("Setting up git configuration...")
        self.git.config("user.name", "github-actions[bot]")
        self.git.config("user.email", "github-actions[bot]@users.noreply.github.com")

    def checkout_pr(self) -> None:
        """PR 브랜치를 체크아웃합니다."""
        logger.info(f"Checking out PR #{self.config.pr_number}...")
        self.github.checkout_pr(self.config.pr_number)

    def run_claude(self, prompt: str) -> str:
        """Claude Code를 실행합니다."""
        return self.claude.run(prompt)

    def commit_and_push(self) -> str:
        """변경사항을 커밋하고 푸시합니다."""
        # unstaged 변경사항만 있으면 커밋
        if not self.git.has_staged_changes() and self.git.has_unstaged_changes():
            logger.info("Committing unstaged changes...")
            self.git.add_all()
            self.git.commit("fix: PR 리뷰 댓글 대응\n\nCo-Authored-By: Atlas <atlas@jk.agent>")

        logger.info("Pushing changes...")
        self.git.push()

        return self.git.rev_parse_short()

    def format_reply(self, response: ReviewResponse, claude_output: str) -> str:
        """답글 메시지를 포맷팅합니다."""
        if response.has_changes and response.commit_sha:
            return f"""✅ 수정 완료

{claude_output}

**커밋:** `{response.commit_sha}`"""

        if claude_output:
            return f"""💬 응답

{claude_output}"""

        return """⚠️ 처리 결과 없음

Claude Code가 응답을 생성하지 않았습니다.
Workflow 로그를 확인해주세요."""

    def reply(self, body: str) -> None:
        """댓글에 답글을 작성합니다."""
        logger.info(f"Replying to comment (is_review={self.config.is_review_comment})...")

        if self.config.is_review_comment:
            self.github.reply_to_review_comment(
                self.config.pr_number,
                self.config.comment_id,
                body,
            )
        else:
            self.github.comment_on_pr(self.config.pr_number, body)

    def handle(self) -> ReviewResponse:
        """리뷰 댓글을 처리합니다."""
        logger.info("Starting review handler")

        # 현재 작업 디렉토리 확인
        cwd = os.getcwd()
        logger.debug(f"Current working directory: {cwd}")
        logger.debug(f"Directory contents: {os.listdir(cwd)[:10]}...")

        # 1. Git 설정
        self.setup_git()

        # 2. PR 체크아웃
        self.checkout_pr()

        # 체크아웃 후 상태 확인
        logger.debug(f"After checkout - cwd: {os.getcwd()}")
        git_status_before = self.git.status_porcelain()
        logger.debug(f"Git status before Claude: '{git_status_before}'")

        # Claude 실행 전 HEAD SHA 기록
        head_before = self.git.rev_parse_short()
        logger.info(f"HEAD before Claude: {head_before}")

        # 3. 프롬프트 생성
        prompt = self.build_prompt()
        logger.debug("=== PROMPT START ===")
        logger.debug(prompt)
        logger.debug(f"=== PROMPT END (length: {len(prompt)}) ===")

        # 4. Claude 실행
        claude_output = self.run_claude(prompt)

        # Claude 출력 확인
        logger.debug("=== CLAUDE OUTPUT START ===")
        logger.debug(claude_output)
        logger.debug(f"=== CLAUDE OUTPUT END (length: {len(claude_output)}) ===")

        # Claude 실행 후 HEAD SHA 확인
        head_after = self.git.rev_parse_short()
        logger.info(f"HEAD after Claude: {head_after}")

        # Claude 실행 후 git 상태
        git_status_after = self.git.status_porcelain()
        logger.debug(f"Git status after Claude: '{git_status_after}'")

        # 5. 결과 처리
        response = ReviewResponse(success=True, message="")

        # Claude가 새 커밋을 만들었는지 확인
        new_commit_by_claude = head_before != head_after
        has_uncommitted_changes = self.git.has_changes()

        if new_commit_by_claude:
            logger.info(f"New commit detected by Claude: {head_before} -> {head_after}")
            response.has_changes = True
            # Claude가 이미 커밋했으므로 push만 수행
            logger.info("Pushing Claude's commit...")
            self.git.push()
            response.commit_sha = head_after
        elif has_uncommitted_changes:
            logger.info("Uncommitted changes detected")
            response.has_changes = True
            response.commit_sha = self.commit_and_push()
        else:
            logger.info("No changes detected")
            logger.debug(f"has_staged_changes: {self.git.has_staged_changes()}")
            logger.debug(f"has_unstaged_changes: {self.git.has_unstaged_changes()}")

        # 6. 답글 작성
        reply_body = self.format_reply(response, claude_output)

        if not self.config.dry_run:
            self.reply(reply_body)
        else:
            logger.info(f"[DRY RUN] Would reply with:\n{reply_body}")

        response.message = reply_body
        logger.info("Review handler completed successfully")

        return response

"""PR 리뷰 응답 핸들러."""

from dataclasses import dataclass
from typing import Optional
import logging

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

        # 1. Git 설정
        self.setup_git()

        # 2. PR 체크아웃
        self.checkout_pr()

        # 3. 프롬프트 생성
        prompt = self.build_prompt()

        # 4. Claude 실행
        claude_output = self.run_claude(prompt)

        # 5. 결과 처리
        response = ReviewResponse(success=True, message="")

        if self.git.has_changes():
            logger.info("Changes detected")
            response.has_changes = True
            response.commit_sha = self.commit_and_push()
        else:
            logger.info("No changes detected")

        # 6. 답글 작성
        reply_body = self.format_reply(response, claude_output)

        if not self.config.dry_run:
            self.reply(reply_body)
        else:
            logger.info(f"[DRY RUN] Would reply with:\n{reply_body}")

        response.message = reply_body
        logger.info("Review handler completed successfully")

        return response

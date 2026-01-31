#!/usr/bin/env python3
"""PR 리뷰 응답 스크립트 엔트리포인트."""

import sys
import logging

from .config import Config
from .clients import GitClientImpl, GitHubClientImpl, ClaudeClientImpl
from .handler import ReviewHandler


def setup_logging(debug: bool = False) -> None:
    """로깅을 설정합니다."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="[%(name)s] [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def main() -> int:
    """메인 함수."""
    try:
        # 설정 로드
        config = Config.from_env()
        config.validate()

        # 로깅 설정
        setup_logging(config.debug)
        logger = logging.getLogger(__name__)

        logger.info("Starting respond-to-review script")

        # 클라이언트 생성
        git = GitClientImpl()
        github = GitHubClientImpl()
        claude = ClaudeClientImpl()

        # 핸들러 실행
        handler = ReviewHandler(config, git, github, claude)
        response = handler.handle()

        if response.success:
            logger.info("Script completed successfully")
            return 0
        else:
            logger.error(f"Script failed: {response.message}")
            return 1

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        # 에러 답글 시도 (실패해도 무시)
        try:
            config = Config.from_env()
            github = GitHubClientImpl()
            error_body = f"""⚠️ 오류 발생

{str(e)}

Workflow 로그를 확인해주세요."""

            if config.is_review_comment:
                github.reply_to_review_comment(config.pr_number, config.comment_id, error_body)
            else:
                github.comment_on_pr(config.pr_number, error_body)
        except Exception:
            pass

        return 1


if __name__ == "__main__":
    sys.exit(main())

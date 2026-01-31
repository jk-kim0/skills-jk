"""설정 관리 모듈."""

from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class Config:
    """스크립트 실행 설정."""

    # GitHub 관련
    gh_token: str
    pr_number: int
    comment_id: int
    comment_body: str
    comment_path: Optional[str] = None
    comment_line: Optional[int] = None
    is_review_comment: bool = False

    # 실행 옵션
    dry_run: bool = False
    debug: bool = False

    @classmethod
    def from_env(cls) -> "Config":
        """환경 변수에서 설정을 로드합니다."""
        return cls(
            gh_token=os.environ["GH_TOKEN"],
            pr_number=int(os.environ["PR_NUMBER"]),
            comment_id=int(os.environ["COMMENT_ID"]),
            comment_body=os.environ["COMMENT_BODY"],
            comment_path=os.environ.get("COMMENT_PATH") or None,
            comment_line=int(os.environ["COMMENT_LINE"]) if os.environ.get("COMMENT_LINE") else None,
            is_review_comment=os.environ.get("IS_REVIEW_COMMENT", "false").lower() == "true",
            dry_run=os.environ.get("DRY_RUN", "false").lower() == "true",
            debug=os.environ.get("DEBUG", "false").lower() == "true",
        )

    def validate(self) -> None:
        """설정 값을 검증합니다."""
        if not self.gh_token:
            raise ValueError("GH_TOKEN is required")
        if self.pr_number <= 0:
            raise ValueError("PR_NUMBER must be positive")
        if self.comment_id <= 0:
            raise ValueError("COMMENT_ID must be positive")
        if not self.comment_body:
            raise ValueError("COMMENT_BODY is required")

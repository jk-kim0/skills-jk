"""Config 모듈 테스트."""

import os
import pytest
from respond_to_review.config import Config


class TestConfig:
    """Config 클래스 테스트."""

    def test_from_env(self, monkeypatch):
        """환경 변수에서 설정을 로드합니다."""
        monkeypatch.setenv("GH_TOKEN", "test-token")
        monkeypatch.setenv("PR_NUMBER", "123")
        monkeypatch.setenv("COMMENT_ID", "456")
        monkeypatch.setenv("COMMENT_BODY", "테스트 댓글")
        monkeypatch.setenv("COMMENT_PATH", "src/main.py")
        monkeypatch.setenv("COMMENT_LINE", "10")
        monkeypatch.setenv("IS_REVIEW_COMMENT", "true")

        config = Config.from_env()

        assert config.gh_token == "test-token"
        assert config.pr_number == 123
        assert config.comment_id == 456
        assert config.comment_body == "테스트 댓글"
        assert config.comment_path == "src/main.py"
        assert config.comment_line == 10
        assert config.is_review_comment is True

    def test_from_env_optional_fields(self, monkeypatch):
        """선택적 필드가 없을 때 기본값을 사용합니다."""
        monkeypatch.setenv("GH_TOKEN", "test-token")
        monkeypatch.setenv("PR_NUMBER", "123")
        monkeypatch.setenv("COMMENT_ID", "456")
        monkeypatch.setenv("COMMENT_BODY", "테스트 댓글")
        # COMMENT_PATH, COMMENT_LINE 없음

        config = Config.from_env()

        assert config.comment_path is None
        assert config.comment_line is None
        assert config.is_review_comment is False

    def test_validate_success(self):
        """유효한 설정은 검증을 통과합니다."""
        config = Config(
            gh_token="test-token",
            pr_number=123,
            comment_id=456,
            comment_body="테스트",
        )
        config.validate()  # 예외 없이 통과

    def test_validate_missing_token(self):
        """토큰이 없으면 검증 실패합니다."""
        config = Config(
            gh_token="",
            pr_number=123,
            comment_id=456,
            comment_body="테스트",
        )
        with pytest.raises(ValueError, match="GH_TOKEN"):
            config.validate()

    def test_validate_invalid_pr_number(self):
        """PR 번호가 유효하지 않으면 검증 실패합니다."""
        config = Config(
            gh_token="test-token",
            pr_number=0,
            comment_id=456,
            comment_body="테스트",
        )
        with pytest.raises(ValueError, match="PR_NUMBER"):
            config.validate()

    def test_validate_empty_comment_body(self):
        """댓글 내용이 없으면 검증 실패합니다."""
        config = Config(
            gh_token="test-token",
            pr_number=123,
            comment_id=456,
            comment_body="",
        )
        with pytest.raises(ValueError, match="COMMENT_BODY"):
            config.validate()

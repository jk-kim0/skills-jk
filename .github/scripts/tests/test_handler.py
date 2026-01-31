"""Handler 모듈 테스트."""

import pytest
from respond_to_review.handler import ReviewHandler, ReviewResponse


class TestReviewHandler:
    """ReviewHandler 클래스 테스트."""

    def test_build_prompt_basic(self, config, mock_git, mock_github, mock_claude):
        """기본 프롬프트를 생성합니다."""
        handler = ReviewHandler(config, mock_git, mock_github, mock_claude)
        prompt = handler.build_prompt()

        assert "이 함수의 이름을 변경해주세요." in prompt
        assert "src/main.py" in prompt
        assert "라인: 10" in prompt

    def test_build_prompt_without_path(self, config, mock_git, mock_github, mock_claude):
        """파일 경로 없이 프롬프트를 생성합니다."""
        config.comment_path = None
        config.is_review_comment = False

        handler = ReviewHandler(config, mock_git, mock_github, mock_claude)
        prompt = handler.build_prompt()

        assert "이 함수의 이름을 변경해주세요." in prompt
        assert "대상 파일" not in prompt

    def test_handle_with_changes(self, config, mock_git, mock_github, mock_claude):
        """변경사항이 있을 때 커밋하고 푸시합니다."""
        # 변경사항이 있는 상태로 설정
        mock_git.set_status(" M src/main.py\n")
        mock_claude.set_output("함수 이름을 변경했습니다.")

        handler = ReviewHandler(config, mock_git, mock_github, mock_claude)
        response = handler.handle()

        assert response.success
        assert response.has_changes
        assert response.commit_sha == "abc1234"
        assert mock_git._pushed
        assert "수정 완료" in response.message

    def test_handle_without_changes(self, config, mock_git, mock_github, mock_claude):
        """변경사항이 없을 때 응답만 반환합니다."""
        mock_git.set_status("")  # 변경사항 없음
        mock_claude.set_output("이 요청은 이미 처리되어 있습니다.")

        handler = ReviewHandler(config, mock_git, mock_github, mock_claude)
        response = handler.handle()

        assert response.success
        assert not response.has_changes
        assert response.commit_sha is None
        assert not mock_git._pushed
        assert "응답" in response.message

    def test_handle_empty_claude_output(self, config, mock_git, mock_github, mock_claude):
        """Claude 출력이 비어있을 때 경고 메시지를 반환합니다."""
        mock_git.set_status("")
        mock_claude.set_output("")

        handler = ReviewHandler(config, mock_git, mock_github, mock_claude)
        response = handler.handle()

        assert "처리 결과 없음" in response.message

    def test_handle_dry_run(self, config, mock_git, mock_github, mock_claude):
        """dry_run 모드에서는 답글을 작성하지 않습니다."""
        config.dry_run = True
        mock_git.set_status(" M src/main.py\n")

        handler = ReviewHandler(config, mock_git, mock_github, mock_claude)
        handler.handle()

        # 답글이 작성되지 않음
        assert len(mock_github._replies) == 0
        assert len(mock_github._comments) == 0

    def test_handle_reply_to_review_comment(self, config, mock_git, mock_github, mock_claude):
        """리뷰 댓글에 답글을 작성합니다."""
        config.dry_run = False
        config.is_review_comment = True
        mock_git.set_status("")

        handler = ReviewHandler(config, mock_git, mock_github, mock_claude)
        handler.handle()

        assert len(mock_github._replies) == 1
        assert mock_github._replies[0]["pr_number"] == 123
        assert mock_github._replies[0]["comment_id"] == 456

    def test_handle_reply_to_issue_comment(self, config, mock_git, mock_github, mock_claude):
        """일반 댓글에 답글을 작성합니다."""
        config.dry_run = False
        config.is_review_comment = False
        mock_git.set_status("")

        handler = ReviewHandler(config, mock_git, mock_github, mock_claude)
        handler.handle()

        assert len(mock_github._comments) == 1
        assert mock_github._comments[0]["pr_number"] == 123


class TestReviewResponse:
    """ReviewResponse 데이터클래스 테스트."""

    def test_response_with_changes(self):
        """변경사항이 있는 응답을 생성합니다."""
        response = ReviewResponse(
            success=True,
            message="완료",
            commit_sha="abc1234",
            has_changes=True,
        )
        assert response.success
        assert response.has_changes
        assert response.commit_sha == "abc1234"

    def test_response_without_changes(self):
        """변경사항이 없는 응답을 생성합니다."""
        response = ReviewResponse(
            success=True,
            message="완료",
        )
        assert response.success
        assert not response.has_changes
        assert response.commit_sha is None

#!/bin/bash
#
# respond-to-review.sh
#
# PR 리뷰 댓글에 자동으로 응답하고 수정 커밋을 생성하는 스크립트
#
# 사용법:
#   ./respond-to-review.sh
#
# 환경 변수:
#   GH_TOKEN: GitHub CLI 인증을 위한 토큰
#   PR_NUMBER: PR 번호
#   COMMENT_ID: 댓글 ID
#   COMMENT_BODY: 댓글 내용
#   COMMENT_PATH: 파일 경로 (리뷰 댓글인 경우)
#   COMMENT_LINE: 라인 번호 (리뷰 댓글인 경우)
#   IS_REVIEW_COMMENT: 리뷰 댓글 여부 (true/false)

set -o errexit -o nounset -o pipefail

# 필수 환경 변수 확인
: "${GH_TOKEN:?GH_TOKEN is required}"
: "${PR_NUMBER:?PR_NUMBER is required}"
: "${COMMENT_ID:?COMMENT_ID is required}"
: "${COMMENT_BODY:?COMMENT_BODY is required}"

IS_REVIEW_COMMENT="${IS_REVIEW_COMMENT:-false}"
COMMENT_PATH="${COMMENT_PATH:-}"
COMMENT_LINE="${COMMENT_LINE:-}"

# Git 사용자 설정
git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"

# PR 브랜치 checkout
echo "Checking out PR #${PR_NUMBER}..."
gh pr checkout "$PR_NUMBER"

# 컨텍스트 구성
CONTEXT="PR 리뷰 댓글에 대응해주세요.

## 댓글 내용
${COMMENT_BODY}
"

if [[ "$IS_REVIEW_COMMENT" == "true" && -n "$COMMENT_PATH" ]]; then
  CONTEXT="${CONTEXT}
## 대상 파일
파일: ${COMMENT_PATH}
라인: ${COMMENT_LINE:-전체}
"
fi

CONTEXT="${CONTEXT}
## 지침
1. 댓글의 요청사항을 분석하고 코드를 수정하세요.
2. 수정이 완료되면 커밋하세요. 커밋 메시지에 처리한 내용을 간단히 설명하세요.
3. 요청이 불명확하면 질문을 출력하세요. (코드 수정 없이)
4. 자동 처리가 어려우면 그 이유를 출력하세요. (코드 수정 없이)

출력 형식:
- 성공 시: [SUCCESS] 수정 내용 설명
- 질문 시: [QUESTION] 질문 내용
- 불가 시: [UNABLE] 사유
"

# Claude Code 실행
echo "Running Claude Code..."
CLAUDE_OUTPUT=$(claude --print "$CONTEXT" 2>&1) || true

# 결과 분석
if echo "$CLAUDE_OUTPUT" | grep -q "^\[SUCCESS\]"; then
  # 변경사항 확인 및 푸시
  if git status --porcelain | grep -q .; then
    git push origin HEAD
    COMMIT_SHA=$(git rev-parse --short HEAD)

    REPLY_BODY="✅ 수정 완료

${CLAUDE_OUTPUT#\[SUCCESS\] }

**커밋:** ${COMMIT_SHA}"
  else
    REPLY_BODY="✅ 확인 완료

${CLAUDE_OUTPUT#\[SUCCESS\] }

(코드 변경 없음)"
  fi

elif echo "$CLAUDE_OUTPUT" | grep -q "^\[QUESTION\]"; then
  REPLY_BODY="❓ 확인이 필요합니다

${CLAUDE_OUTPUT#\[QUESTION\] }

답글로 알려주시면 처리하겠습니다."

elif echo "$CLAUDE_OUTPUT" | grep -q "^\[UNABLE\]"; then
  REPLY_BODY="⚠️ 자동 처리 불가

${CLAUDE_OUTPUT#\[UNABLE\] }

수동 처리가 필요합니다."

else
  # 예상치 못한 출력
  REPLY_BODY="⚠️ 처리 중 문제 발생

Claude Code 출력을 분석할 수 없습니다.
Workflow 로그를 확인해주세요."
fi

# 댓글에 답글 작성
echo "Replying to comment..."
if [[ "$IS_REVIEW_COMMENT" == "true" ]]; then
  # 리뷰 댓글에 답글
  gh api \
    --method POST \
    -H "Accept: application/vnd.github+json" \
    "/repos/{owner}/{repo}/pulls/${PR_NUMBER}/comments/${COMMENT_ID}/replies" \
    -f body="$REPLY_BODY"
else
  # 일반 댓글에 답글 (issue comment)
  gh pr comment "$PR_NUMBER" --body "$REPLY_BODY"
fi

echo "Done."

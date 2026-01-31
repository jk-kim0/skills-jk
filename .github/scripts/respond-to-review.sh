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

#######################################
# 상수 정의
#######################################
readonly SCRIPT_NAME="$(basename "$0")"
readonly LOG_PREFIX="[${SCRIPT_NAME}]"

#######################################
# 로깅 함수
#######################################
log_info() {
  echo "${LOG_PREFIX} [INFO] $*"
}

log_error() {
  echo "${LOG_PREFIX} [ERROR] $*" >&2
}

log_debug() {
  if [[ "${DEBUG:-false}" == "true" ]]; then
    echo "${LOG_PREFIX} [DEBUG] $*"
  fi
}

#######################################
# 클린업 함수 (트랩에서 호출)
#######################################
cleanup() {
  local exit_code=$?
  log_debug "Cleanup called with exit code: $exit_code"
  # 필요한 정리 작업 수행
  exit "$exit_code"
}

trap cleanup EXIT

#######################################
# 에러 핸들러
#######################################
on_error() {
  local line_no=$1
  local error_code=$2
  log_error "Error on line $line_no (exit code: $error_code)"
}

trap 'on_error ${LINENO} $?' ERR

#######################################
# 필수 환경 변수 검증
#######################################
validate_env() {
  local missing_vars=()

  [[ -z "${GH_TOKEN:-}" ]] && missing_vars+=("GH_TOKEN")
  [[ -z "${PR_NUMBER:-}" ]] && missing_vars+=("PR_NUMBER")
  [[ -z "${COMMENT_ID:-}" ]] && missing_vars+=("COMMENT_ID")
  [[ -z "${COMMENT_BODY:-}" ]] && missing_vars+=("COMMENT_BODY")

  if [[ ${#missing_vars[@]} -gt 0 ]]; then
    log_error "Missing required environment variables: ${missing_vars[*]}"
    return 1
  fi

  log_info "Environment validation passed"
  return 0
}

#######################################
# 답글 작성 함수
#######################################
reply_to_comment() {
  local body="$1"
  local is_review="${IS_REVIEW_COMMENT:-false}"

  log_info "Replying to comment (is_review=$is_review)..."

  if [[ "$is_review" == "true" ]]; then
    gh api \
      --method POST \
      -H "Accept: application/vnd.github+json" \
      "/repos/{owner}/{repo}/pulls/${PR_NUMBER}/comments/${COMMENT_ID}/replies" \
      -f body="$body"
  else
    gh pr comment "$PR_NUMBER" --body "$body"
  fi

  log_info "Reply sent successfully"
}

#######################################
# 에러 답글 작성 및 종료
#######################################
reply_error_and_exit() {
  local message="$1"
  local exit_code="${2:-1}"

  log_error "$message"

  local reply_body="⚠️ 오류 발생

${message}

Workflow 로그를 확인해주세요."

  # 답글 실패해도 계속 진행
  reply_to_comment "$reply_body" || log_error "Failed to send error reply"

  exit "$exit_code"
}

#######################################
# Git 설정
#######################################
setup_git() {
  log_info "Setting up git configuration..."
  git config user.name "github-actions[bot]"
  git config user.email "github-actions[bot]@users.noreply.github.com"
}

#######################################
# PR 브랜치 체크아웃
#######################################
checkout_pr() {
  local pr_number="$1"

  log_info "Checking out PR #${pr_number}..."

  if ! gh pr checkout "$pr_number"; then
    reply_error_and_exit "PR #${pr_number} 체크아웃 실패"
  fi

  log_info "PR checkout successful"
}

#######################################
# 프롬프트 컨텍스트 생성
#######################################
build_context() {
  local comment_body="$1"
  local comment_path="${2:-}"
  local comment_line="${3:-}"
  local is_review="${4:-false}"

  local context="PR 리뷰 댓글을 처리해주세요.

## 댓글 내용
${comment_body}
"

  if [[ "$is_review" == "true" && -n "$comment_path" ]]; then
    context+="
## 대상 파일
파일: ${comment_path}
라인: ${comment_line:-전체}
"
  fi

  context+="
## 지침
1. 댓글의 요청사항을 분석하세요.
2. 코드 수정이 필요하면 수정하고 커밋하세요.
3. 요청이 불명확하면 질문하세요.
4. 처리가 어려우면 이유를 설명하세요.

커밋 메시지 형식: 'fix: <변경 내용 요약>'
커밋 trailer 추가: 'Co-Authored-By: Atlas <atlas@jk.agent>'
"

  echo "$context"
}

#######################################
# Claude Code 실행
#######################################
run_claude() {
  local context="$1"
  local output=""
  local exit_code=0

  log_info "Running Claude Code..."

  # errexit 일시 비활성화하여 exit code 캡처
  set +e
  output=$(claude --print "$context" 2>&1)
  exit_code=$?
  set -e

  log_info "Claude Code exit code: $exit_code"
  log_info "Claude Code output length: ${#output}"
  log_debug "Claude Code output: $output"

  if [[ $exit_code -ne 0 ]]; then
    reply_error_and_exit "Claude Code 실행 실패 (exit code: $exit_code)" "$exit_code"
  fi

  echo "$output"
}

#######################################
# 변경사항 커밋 및 푸시
#######################################
commit_and_push() {
  local has_staged=false
  local has_unstaged=false

  # 변경사항 상태 확인
  if git status --porcelain | grep -q "^[MADRC]"; then
    has_staged=true
  fi
  if git status --porcelain | grep -q "^.[MADRC]"; then
    has_unstaged=true
  fi

  log_debug "has_staged=$has_staged, has_unstaged=$has_unstaged"

  # unstaged 변경사항만 있으면 커밋
  if [[ "$has_staged" == "false" && "$has_unstaged" == "true" ]]; then
    log_info "Committing unstaged changes..."
    git add -A
    git commit -m "fix: PR 리뷰 댓글 대응

Co-Authored-By: Atlas <atlas@jk.agent>"
  fi

  # 푸시
  log_info "Pushing changes..."
  if ! git push origin HEAD; then
    reply_error_and_exit "Git push 실패. 충돌이 발생했을 수 있습니다."
  fi

  git rev-parse --short HEAD
}

#######################################
# 메인 함수
#######################################
main() {
  log_info "Starting respond-to-review script"

  # 환경 변수 검증
  validate_env

  # 변수 설정
  local pr_number="$PR_NUMBER"
  local comment_id="$COMMENT_ID"
  local comment_body="$COMMENT_BODY"
  local comment_path="${COMMENT_PATH:-}"
  local comment_line="${COMMENT_LINE:-}"
  local is_review="${IS_REVIEW_COMMENT:-false}"

  # Git 설정
  setup_git

  # PR 체크아웃
  checkout_pr "$pr_number"

  # 컨텍스트 생성
  local context
  context=$(build_context "$comment_body" "$comment_path" "$comment_line" "$is_review")

  # Claude Code 실행
  local claude_output
  claude_output=$(run_claude "$context")

  # 결과 처리
  local reply_body=""

  if git status --porcelain | grep -q .; then
    # 변경사항 있음
    log_info "Changes detected"

    local commit_sha
    commit_sha=$(commit_and_push)

    reply_body="✅ 수정 완료

${claude_output}

**커밋:** \`${commit_sha}\`"
  else
    # 변경사항 없음
    log_info "No changes detected"

    if [[ -n "$claude_output" ]]; then
      reply_body="💬 응답

${claude_output}"
    else
      reply_body="⚠️ 처리 결과 없음

Claude Code가 응답을 생성하지 않았습니다.
Workflow 로그를 확인해주세요."
    fi
  fi

  # 답글 작성
  reply_to_comment "$reply_body"

  log_info "Script completed successfully"
}

# 스크립트 실행
main "$@"

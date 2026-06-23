#!/usr/bin/env bash
#
# Jira 티켓 첨부파일 다운로드 및 정리 스크립트
#
# 사용법:
#     ./download_and_organize.sh <ISSUE_KEY>
#     ./download_and_organize.sh QPD-1234
#
# 환경변수:
#     JIRA_API_TOKEN: Jira API 토큰 (필수)
#     JIRA_USERNAME: Jira 사용자 이메일 (필수)
#     JIRA_URL: Jira 서버 URL (기본값: https://querypie.atlassian.net)
#
# 의존성:
#     jira CLI, jq, curl, unzip
#

set -euo pipefail

# 환경변수 설정
JIRA_USERNAME="${JIRA_USERNAME:-}"
JIRA_API_TOKEN="${JIRA_API_TOKEN:-}"
JIRA_URL="${JIRA_URL:-https://querypie.atlassian.net}"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 에러 출력 함수
error() {
    echo -e "${RED}Error: $1${NC}" >&2
    exit 1
}

# 정보 출력 함수
info() {
    echo -e "${GREEN}$1${NC}"
}

# 경고 출력 함수
warn() {
    echo -e "${YELLOW}$1${NC}"
}

# 사용법 출력
usage() {
    echo "Usage: $0 <ISSUE_KEY>"
    echo "Example: $0 QPD-1234"
    exit 1
}

# 환경변수 확인
check_env() {
    if [[ -z "$JIRA_API_TOKEN" ]]; then
        error "JIRA_API_TOKEN 환경변수가 설정되지 않았습니다."
    fi
    if [[ -z "$JIRA_USERNAME" ]]; then
        error "JIRA_USERNAME 환경변수가 설정되지 않았습니다."
    fi
}

# 의존성 확인
check_dependencies() {
    local deps=("jira" "jq" "curl")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            error "$dep 가 설치되어 있지 않습니다."
        fi
    done
}

# 첨부파일 다운로드
download_attachment() {
    local attachment_id="$1"
    local filename="$2"
    local output_dir="$3"
    local output_path="$output_dir/$filename"
    local url="$JIRA_URL/rest/api/3/attachment/content/$attachment_id"

    curl -sL -u "$JIRA_USERNAME:$JIRA_API_TOKEN" "$url" -o "$output_path"
    echo "$output_path"
}

# 디렉토리 이름 정규화
sanitize_dirname() {
    local text="$1"
    local max_len="${2:-30}"
    # 특수문자 제거, 공백을 언더스코어로
    echo "$text" | sed 's/[<>:"\/\\|?*]//g' | sed 's/ /_/g' | cut -c1-"$max_len" | sed 's/_$//'
}

# 압축 파일 해제
extract_archives() {
    local dir="$1"

    # ZIP 파일 해제
    find "$dir" -name "*.zip" -type f 2>/dev/null | while read -r zip_file; do
        local extract_dir="${zip_file%.zip}"
        mkdir -p "$extract_dir"
        if unzip -o "$zip_file" -d "$extract_dir" &>/dev/null; then
            rm -f "$zip_file"
            info "  Extracted: $(basename "$zip_file")"
        else
            warn "  Warning: Could not extract $(basename "$zip_file")"
        fi
    done

    # GZ 파일 해제
    find "$dir" -name "*.gz" -type f 2>/dev/null | while read -r gz_file; do
        local output_file="${gz_file%.gz}"
        if gunzip -k "$gz_file" 2>/dev/null; then
            rm -f "$gz_file"
            info "  Extracted: $(basename "$gz_file")"
        else
            warn "  Warning: Could not extract $(basename "$gz_file")"
        fi
    done
}

# 메인 README 생성
create_readme() {
    local output_dir="$1"
    local issue_key="$2"
    local summary="$3"
    local status="$4"
    local created="$5"

    cat > "$output_dir/README.md" << EOF
# $issue_key: $summary

## 개요

- **이슈 키**: $issue_key
- **제목**: $summary
- **상태**: $status
- **생성일**: ${created:0:10}
- **다운로드 일시**: $(date "+%Y-%m-%d %H:%M:%S")

## 디렉토리 구조

EOF

    # 디렉토리 목록 추가
    find "$output_dir" -mindepth 1 -maxdepth 1 -type d | sort | while read -r subdir; do
        local dirname=$(basename "$subdir")
        local file_count=$(find "$subdir" -type f | wc -l | tr -d ' ')
        echo "- \`$dirname/\` - ${file_count}개 파일" >> "$output_dir/README.md"
    done

    echo "" >> "$output_dir/README.md"
    echo "---" >> "$output_dir/README.md"
    echo "*이 파일은 download_and_organize.sh 스크립트에 의해 자동 생성되었습니다.*" >> "$output_dir/README.md"
}

# 메인 함수
main() {
    if [[ $# -lt 1 ]]; then
        usage
    fi

    local issue_key="${1^^}"  # 대문자로 변환

    check_env
    check_dependencies

    # 스크립트 디렉토리 기준 출력 경로 설정
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local output_dir="$script_dir/../download-and-organize/files/$issue_key"
    mkdir -p "$output_dir"

    info "Fetching issue $issue_key..."

    # 이슈 데이터 조회
    local issue_data
    issue_data=$(jira issue view "$issue_key" --raw 2>/dev/null) || error "이슈를 가져올 수 없습니다: $issue_key"

    # 이슈 정보 추출
    local summary status created
    summary=$(echo "$issue_data" | jq -r '.fields.summary // "No summary"')
    status=$(echo "$issue_data" | jq -r '.fields.status.name // "Unknown"')
    created=$(echo "$issue_data" | jq -r '.fields.created // "Unknown"')

    # 첨부파일 목록 추출
    local attachments
    attachments=$(echo "$issue_data" | jq -c '.fields.attachment // []')
    local attachment_count
    attachment_count=$(echo "$attachments" | jq 'length')

    if [[ "$attachment_count" -eq 0 ]]; then
        info "No attachments found."
        exit 0
    fi

    info "Found $attachment_count attachments"

    # 첨부파일을 00_attachments 디렉토리에 다운로드
    local attachments_dir="$output_dir/00_attachments"
    mkdir -p "$attachments_dir"

    echo ""
    info "[00_attachments]"

    echo "$attachments" | jq -c '.[]' | while read -r att; do
        local att_id att_filename
        att_id=$(echo "$att" | jq -r '.id')
        att_filename=$(echo "$att" | jq -r '.filename')

        info "  Downloading: $att_filename"
        download_attachment "$att_id" "$att_filename" "$attachments_dir"
    done

    # README 생성
    create_readme "$output_dir" "$issue_key" "$summary" "$status" "$created"

    # 압축 파일 해제
    echo ""
    info "Extracting archives..."
    extract_archives "$output_dir"

    echo ""
    info "Done! Files saved to: $output_dir"
    echo "cd $output_dir"
}

main "$@"

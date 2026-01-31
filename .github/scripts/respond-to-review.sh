#!/bin/bash
#
# respond-to-review.sh
#
# PR 리뷰 댓글 자동 응답 스크립트 (Python 모듈 실행)
#
# 환경 변수:
#   GH_TOKEN, PR_NUMBER, COMMENT_ID, COMMENT_BODY 등

set -o errexit -o nounset -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Python 모듈 실행 (리포지토리 루트에서 실행)
PYTHONPATH="$SCRIPT_DIR" python3 -m respond_to_review.main

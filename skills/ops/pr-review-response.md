---
name: pr-review-response
description: PR 리뷰 댓글 자동 응답 시스템 — JK의 리뷰 댓글에 Claude Code가 자동으로 코드 수정 및 답글
tags: [pr, github-actions, claude-code, automation]
---

# PR 리뷰 댓글 자동 응답 시스템

## 개요

JK(jk-kim0)가 GitHub PR에 리뷰 댓글을 달면, Claude Code CLI가 자동으로 코드를 수정하고 커밋을 push한 뒤 댓글에 답글을 작성한다.

## 동작 방식

```
JK가 PR에 리뷰 댓글 작성
    │
    ▼
GitHub Actions 트리거 (issue_comment / pull_request_review_comment)
    │
    ├── 필터: 작성자=jk-kim0, @태깅 없음
    │
    ▼
Self-hosted Runner
    1. PR 브랜치 checkout
    2. Claude Code 실행 (댓글 내용 + 파일/라인 정보 전달)
    3. 코드 수정 → 커밋 → push
    4. 처리 결과를 댓글에 답글
```

## 트리거 조건

| 조건 | 설명 |
|------|------|
| 작성자 | `jk-kim0`만 반응 |
| 이벤트 | `issue_comment` + `pull_request_review_comment` |
| @태깅 | `@username` 패턴이 있으면 스킵 |

## 답글 형식

- **수정 완료**: 변경 파일 목록 + 커밋 SHA
- **변경 없음**: Claude 분석 결과만 답글
- **오류 발생**: 에러 메시지 + workflow 로그 확인 요청

## 파일 구성

| 파일 | 설명 |
|------|------|
| `.github/workflows/pr-review-response.yml` | Workflow 정의 |
| `.github/scripts/respond-to-review.sh` | Shell wrapper |
| `.github/scripts/respond_to_review/main.py` | 진입점 |
| `.github/scripts/respond_to_review/config.py` | 환경 변수 → Config 로드 |
| `.github/scripts/respond_to_review/clients.py` | Git, GitHub, Claude 클라이언트 |
| `.github/scripts/respond_to_review/handler.py` | 리뷰 처리 핸들러 |
| `.github/scripts/tests/` | 테스트 25개 |

## 알려진 제약

- 이미 merge/삭제된 브랜치의 PR에 댓글 달면 checkout 실패 (에러 답글 자동 작성됨)
- Self-hosted runner에 Claude Code CLI가 설치되어 있어야 함
- 쿠키/인증 만료 시 Claude Code가 실행되지 않을 수 있음

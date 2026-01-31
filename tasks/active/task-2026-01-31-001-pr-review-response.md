---
id: task-2026-01-31-001
title: PR 리뷰 댓글 자동 응답 시스템 구현
status: active
priority: high
project: skills-jk
skills: [github-actions, claude-code]
repo: https://github.com/jk-kim0/skills-jk
created: 2026-01-31
due: 2026-02-07
---

# PR 리뷰 댓글 자동 응답 시스템 구현

## 목표

JK가 GitHub PR에 리뷰 댓글을 달면, AI Agent(Claude Code)가 자동으로 감지하여 수정 커밋을 푸시하고 PR을 개선하는 시스템 구현

## 요구사항

### 트리거 조건
- JK(jk-kim0)가 작성한 모든 PR 댓글에 자동 반응
- 다른 사람 태깅(@username)이 있는 댓글은 반응하지 않음
- `issue_comment`와 `pull_request_review_comment` 이벤트 모두 처리

### 처리 방식
- 새 커밋 추가 방식 (PR은 squash merge로 병합)
- 커밋 후 해당 댓글에 답글로 처리 결과 설명
- 처리 어려운 댓글은 명확화 질문으로 답글

### 실행 환경
- Self-hosted runner (office/home 중 사용 가능한 것)
- Claude Code CLI 사용

## 설계

### 아키텍처

```
GitHub PR (JK 리뷰 댓글)
        │
        ▼
GitHub Actions Workflow
(트리거: issue_comment, pull_request_review_comment)
(필터: 작성자=jk-kim0, @태깅 없음)
        │
        ▼
Self-hosted Runner
  1. PR 브랜치 checkout
  2. Claude Code 실행 (댓글 내용 전달)
  3. 코드 수정 및 커밋
  4. PR 브랜치에 push
  5. 댓글에 답글 작성
```

### 생성할 파일

| 파일 | 설명 |
|------|------|
| `.github/workflows/pr-review-response.yml` | Workflow 정의 |
| `.github/scripts/respond-to-review.sh` | 댓글 처리 스크립트 |

### Workflow 필터 조건

| 조건 | 체크 방법 |
|------|----------|
| JK 작성 | `github.event.comment.user.login == 'jk-kim0'` |
| PR 대상 | `github.event.issue.pull_request` 존재 여부 |
| 태깅 없음 | 스크립트에서 `@username` 패턴 체크 |

### 답글 형식

**성공 시:**
```markdown
✅ 수정 완료

**변경 사항:**
- `파일명`: 설명

**커밋:** abc1234
```

**명확화 필요 시:**
```markdown
❓ 확인이 필요합니다

요청을 처리하기 전에 확인이 필요합니다:
- 질문 내용

답글로 알려주시면 처리하겠습니다.
```

**처리 불가 시:**
```markdown
⚠️ 자동 처리 불가

이 요청은 자동으로 처리하기 어렵습니다:
- 사유

수동 처리가 필요합니다.
```

### 에러 처리

| 상황 | 대응 |
|------|------|
| Claude Code 실행 실패 | 답글로 에러 알림 + workflow 로그 링크 |
| Push 실패 (충돌 등) | 답글로 충돌 알림 + 수동 해결 요청 |
| 타임아웃 | 답글로 타임아웃 알림 |

## 완료 조건

- [ ] `.github/workflows/pr-review-response.yml` 작성
- [ ] `.github/scripts/respond-to-review.sh` 작성
- [ ] 테스트 PR에서 동작 확인
- [ ] 문서화 완료

## 진행 로그

### 2026-01-31
- 요구사항 분석 및 설계 완료
- Task 문서 작성

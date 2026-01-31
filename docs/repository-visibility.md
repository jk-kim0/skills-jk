# Repository 공개 범위

이 문서는 skills-jk Repository에서 공개/비공개 정보를 구분하고, 권한 정책을 명시합니다.

## 권한 정책

> **모든 변경사항은 JK 또는 JK가 권한을 위임한 AI Agent만 수행할 수 있다.**

### 변경 권한 보유자

| 주체 | 권한 | 비고 |
|------|------|------|
| JK (jk-kim0) | Admin | Repository 소유자 |
| Atlas | Write (위임) | GitHub Actions 통해 권한 위임 |

## 기능별 권한 현황

| 항목 | 읽기 | 쓰기/변경 | 비고 |
|------|------|----------|------|
| **Repository 코드** | 누구나 | JK / AI Agent | PUBLIC |
| **Issues** | 누구나 | 누구나 | 생성/댓글 가능 |
| **Pull Requests** | 누구나 | 누구나 (생성) / JK (Merge) | Fork에서 PR 제출 가능 |
| **Discussions** | 누구나 | 누구나 | 참여 가능 |
| **Wiki** | 누구나 | JK만 | collaborator 제한 |
| **Actions 로그** | 누구나 | - | 실행 결과 공개 |
| **Actions 실행** | - | JK / AI Agent | workflow_dispatch 등 |
| **GitHub Secrets** | JK만 | JK만 | API 키, 토큰 등 |
| **Environment Secrets** | JK만 | JK만 | 환경별 비밀 값 |
| **Self-hosted Runner** | JK만 | JK만 | PC 정보 비공개 |
| **Repository Settings** | JK만 | JK만 | 관리자 전용 |

## 주의사항

현재 Repository가 **PUBLIC**이므로:

1. **민감한 정보를 절대 커밋하지 말 것**
   - API 키, 토큰, 비밀번호
   - 개인정보, 회사 기밀
   - 내부 서버 주소

2. **Tasks/Projects에 민감한 내용 포함 금지**
   - 외부 Repository URL은 공개해도 무방한 것만
   - 내부 업무 상세 내용 주의

3. **GitHub Secrets 활용**
   - 민감한 값은 반드시 Secrets에 저장
   - 환경 변수로 주입하여 사용

## 현재 권한 설정 검증

### Collaborators (2026-01-31 확인)

| 사용자 | 권한 | 상태 |
|--------|------|------|
| jk-kim0 | Admin | ✓ 정상 |

외부 collaborator 없음 ✓

### Branch Protection (2026-01-31 설정됨)

| 항목 | 설정값 | 상태 |
|------|--------|------|
| PR 필수 | ✓ | 직접 push 불가 |
| 최소 승인 수 | 1명 | ✓ |
| Stale review 해제 | ✓ | 코드 변경 시 재승인 필요 |
| Force push 차단 | ✓ | ✓ |
| 브랜치 삭제 차단 | ✓ | ✓ |
| Admin 예외 | ✓ | JK 긴급 직접 merge 가능 |

### Actions 권한

| 항목 | 현재 값 | 상태 |
|------|---------|------|
| default_workflow_permissions | read | ✓ 안전 |
| can_approve_pull_request_reviews | false | ✓ 안전 |
| allow_actions_to_create_pull_requests | true | ✓ 필요 (Bot PR 생성용) |

**allow_actions_to_create_pull_requests 설정 (2026-01-31)**

로컬에서 AI Agent가 작업 후 `github-actions[bot]`으로 PR을 생성하려면 이 설정이 필요합니다.
Settings > Actions > General > Workflow permissions에서 활성화합니다.

### Fork PR Workflow

Fork에서 제출된 PR의 workflow는 maintainer(JK) 승인 후 실행됨 ✓

## 권장 조치

### Branch Protection 설정

✅ **완료** (2026-01-31)

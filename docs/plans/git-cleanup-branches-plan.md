# 로컬 브랜치 일괄 정리 스크립트 개발 계획

## 상태: ✅ 구현 완료 (2026-02-02)

## 개요

~/workspace 아래의 모든 git repository에 대해, 최근 2주일 이내에 commit이 변경된 로컬 브랜치의 PR 병합 상태를 검사하여 일괄 정리할 수 있는 스크립트를 개발합니다.

## 구현된 사용법

```bash
# dry-run (기본) - 삭제 대상만 확인
git-cleanup-branches

# 실제 삭제 수행
git-cleanup-branches --delete

# 최근 7일 이내 변경된 브랜치만
git-cleanup-branches --days 7

# 테스트용 디렉토리 지정 (기본: ~/workspace)
git-cleanup-branches --workspace /path/to/dir
```

## Task 목록

### Task 1: 요구사항 정의 ✅

스크립트의 기능 요구사항과 동작 방식을 정의합니다:

- 대상: ~/workspace 아래의 모든 git repository
- 조건: 최근 2주일 이내에 commit이 변경된 로컬 브랜치
- 검사 항목: PR 병합 여부, 원격 브랜치 존재 여부, main과의 차이
- 동작: dry-run 모드와 실제 삭제 모드 지원
- 출력: 삭제 대상 브랜치 목록과 판정 사유

### Task 2: ~/workspace 디렉토리 스캔 로직 구현 ✅

의존성: Task 1

~/workspace 아래의 모든 git repository를 찾아서 목록화하는 로직:

- .git 디렉토리를 포함한 디렉토리 탐색
- 중첩된 repository 처리 방안 (1depth만 또는 재귀)
- repository별 원격 URL 확인 (GitHub 여부)

### Task 3: 로컬 브랜치 분석 로직 구현 ✅

의존성: Task 1

각 repository의 로컬 브랜치를 분석하는 로직:

- 최근 2주일 이내 커밋 변경 여부 확인 (`git log --since`)
- main 브랜치와의 커밋 차이 계산 (`git rev-list --count`)
- main에 이미 머지되었는지 확인 (`git branch --merged`)
- 원격 브랜치 존재 여부 확인 (`git ls-remote`)

### Task 4: GitHub PR 상태 조회 로직 구현 ✅

의존성: Task 1

gh CLI를 사용하여 브랜치의 PR 상태를 조회하는 로직:

- `gh pr list --head <branch> --state all` 명령 사용
- PR 상태 분류: MERGED, CLOSED, OPEN, PR없음
- squash merge된 경우도 감지 (커밋이 다르지만 PR은 머지됨)
- GitHub 외 저장소 처리 (GitLab 등은 스킵 또는 별도 처리)

### Task 5: 브랜치 삭제 판정 로직 구현 ✅

의존성: Task 3, Task 4

수집된 정보를 기반으로 삭제 가능 여부를 판정하는 로직:

**삭제 가능 조건:**
- PR 상태가 MERGED인 경우 (squash merge 포함)
- PR 상태가 CLOSED인 경우
- main에 이미 머지된 경우 (`git branch --merged`)
- 원격 브랜치가 없고 main과 동일한 경우

**유지 필요 조건:**
- PR 상태가 OPEN인 경우
- main에 머지되지 않은 고유 커밋이 있고 PR이 없는 경우

### Task 6: 스크립트 CLI 인터페이스 구현 ✅

의존성: Task 1

사용자 친화적인 CLI 인터페이스 구현:

**옵션:**
- `--delete`: 실제 삭제 수행 (기본값: dry-run)
- `--days N`: 최근 N일 이내 변경된 브랜치 (기본값: 14)
- `--workspace <path>`: 스캔할 workspace 디렉토리 (기본값: ~/workspace)

**출력 형식:**
- 저장소별 브랜치 목록
- 각 브랜치의 상태와 판정 결과
- 요약 통계 (삭제 가능/유지 필요 개수)

### Task 7: 스크립트 작성 및 bin/ 디렉토리에 배치 ✅

의존성: Task 2, Task 5, Task 6

위 로직들을 통합하여 실행 가능한 스크립트 작성:

- 언어: bash 또는 python
- 위치: `bin/git-cleanup-branches`
- 실행 권한 부여 (`chmod +x`)
- `/usr/local/bin`에 심볼릭 링크 또는 복사

### Task 8: branch-workflow.md Skill 문서 업데이트 ✅

의존성: Task 7

기존 `skills/ops/branch-workflow.md`에 일괄 정리 스크립트 사용법 추가:

- 스크립트 소개 및 설치 방법
- 사용 예시 (dry-run, 실제 삭제)
- 옵션 설명
- 주의사항

### Task 9: 스크립트 테스트 및 검증 ✅

의존성: Task 7

작성된 스크립트를 실제 환경에서 테스트:

- dry-run 모드로 ~/workspace 전체 스캔
- 출력 결과 검증 (예상 브랜치가 올바르게 분류되는지)
- 일부 브랜치에 대해 실제 삭제 테스트
- 엣지 케이스 확인 (PR 없는 브랜치, non-GitHub 저장소 등)

## Task 의존성 다이어그램

```
#1 요구사항 정의
 │
 ├─► #2 디렉토리 스캔 로직 ─────────────────┐
 │                                          │
 ├─► #3 브랜치 분석 로직 ──┐                │
 │                         ├─► #5 삭제 판정 ├─► #7 스크립트 작성 ─┬─► #8 문서 업데이트
 ├─► #4 PR 상태 조회 ──────┘                │                     │
 │                                          │                     └─► #9 테스트
 └─► #6 CLI 인터페이스 ────────────────────┘
```

## 예상 출력 형식

```
======================================
  skills-jk
======================================
브랜치                              PR상태    커밋차이  판정
----------------------------------  --------  --------  ----------
feat/add-login                      MERGED    +2        ✅ 삭제가능
fix/bug-123                         CLOSED    +1        ✅ 삭제가능
docs/update-readme                  OPEN      +3        ⚠️ 유지
feature/wip                         -         +5        ⚠️ 확인필요

======================================
  요약
======================================
스캔된 저장소: 6개
총 브랜치: 24개
삭제 가능: 18개
유지 필요: 6개
```

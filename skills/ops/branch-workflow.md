---
name: branch-workflow
description: 새로운 PR 작업 시작 시 main 업데이트, 로컬 브랜치 정리, feature 브랜치 생성
tags: [git, branch, pr, workflow]
---

# Branch Workflow

## 목적

Local branch를 최소로 유지하며 항상 최신 main 위에서 작업하는 워크플로우.

## 필수 규칙

> **코드 변경 전 반드시 feature 브랜치 확인**
>
> 코드를 수정하기 전에 항상 현재 브랜치를 확인하고, main이면 feature 브랜치를 생성할 것.
> 이 규칙은 현재 repo뿐 아니라 **외부 repo에서 작업할 때도 동일하게 적용**한다.

```bash
# 코드 변경 전 브랜치 확인 (필수)
git branch --show-current

# main이면 즉시 feature 브랜치 생성
git checkout -b <prefix>/<descriptive-name>
```

## 적용 시점

- 새로운 PR 작업을 시작할 때
- 커밋을 만들기 전에 브랜치 상태를 정리할 때

## 수행 절차

### 1. Main 브랜치 업데이트

```bash
git checkout main
git pull origin main
```

### 2. 로컬 브랜치 정리

**자동화 스크립트 사용 (권장):**

```bash
# stale 브랜치 확인 (dry-run)
git-cleanup-branches

# stale 브랜치 삭제 실행
git-cleanup-branches --delete
```

> `git-cleanup-branches`는 `bin/git-cleanup-branches`에 위치. 최근 14일 이내 커밋이 있고 PR이 MERGED/CLOSED된 브랜치를 자동 감지합니다.

**수동 정리:**

```bash
# 모든 브랜치와 PR 상태 확인
git branch -a
gh pr list --state all --json number,headRefName,state --jq '.[] | "\(.headRefName) \(.state)"'

# MERGED/CLOSED된 PR의 로컬 브랜치 삭제
git branch -d <branch-name>

# 원격 추적 브랜치 정리
git remote prune origin
```

### 3. 새 Feature 브랜치 생성

```bash
git checkout -b <prefix>/<descriptive-name> origin/main
```

> 브랜치 시작점은 항상 `origin/main`으로 고정한다.  
> 로컬의 다른 작업 브랜치에서 분기하지 않는다.

## 브랜치 네이밍 규칙

| 접두사 | 용도 | 예시 |
|--------|------|------|
| `feat/` | 새 기능 | `feat/add-login` |
| `fix/` | 버그 수정 | `fix/null-pointer` |
| `docs/` | 문서 변경 | `docs/update-readme` |
| `refactor/` | 리팩토링 | `refactor/extract-utils` |

## 빠른 참조

| 단계 | 명령어 |
|------|--------|
| main 이동 및 업데이트 | `git checkout main && git pull origin main` |
| stale 브랜치 확인 | `git-cleanup-branches` |
| stale 브랜치 삭제 | `git-cleanup-branches --delete` |
| 브랜치 목록 확인 | `git branch -a` |
| PR 상태 확인 | `gh pr list --state all --json headRefName,state` |
| 로컬 브랜치 삭제 | `git branch -d <branch-name>` |
| 원격 추적 정리 | `git remote prune origin` |
| 새 브랜치 생성 | `git checkout -b feat/<name>` |

## 흔한 실수

| 실수 | 해결 |
|------|------|
| **main에서 코드 수정 시작** | 코드 변경 전 `git branch --show-current` 확인 필수 |
| **외부 repo에서 branch 생성 누락** | 외부 repo도 동일하게 feature branch 생성 후 작업 |
| main 업데이트 없이 브랜치 생성 | 항상 `git pull` 먼저 |
| 머지된 브랜치 방치 | PR 상태 확인 후 삭제 |
| 원격 추적 브랜치 누적 | `git remote prune origin` 실행 |

## PR 생성

작업 완료 후 [create-pr](./create-pr.md) 규칙에 따라 PR을 생성합니다.

**핵심:** `gh pr create` 직접 실행 금지 → `gh workflow run create-pr.yml` 사용

## 워크플로우 다이어그램

```
새 작업 시작
     │
     ▼
main으로 이동 & pull
     │
     ▼
로컬 브랜치 정리 (머지된 브랜치 삭제)
     │
     ▼
새 feature 브랜치 생성
     │
     ▼
작업 & 커밋 & 푸시
     │
     ▼
PR 생성 (create-pr 규칙 참조)
```

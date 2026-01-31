---
name: branch-workflow
description: 새로운 PR 작업 시작 시 main 업데이트, 로컬 브랜치 정리, feature 브랜치 생성
tags: [git, branch, pr, workflow]
---

# Branch Workflow

## 목적

Local branch를 최소로 유지하며 항상 최신 main 위에서 작업하는 워크플로우.

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
git checkout -b <prefix>/<descriptive-name>
```

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
| 브랜치 목록 확인 | `git branch -a` |
| PR 상태 확인 | `gh pr list --state all --json headRefName,state` |
| 로컬 브랜치 삭제 | `git branch -d <branch-name>` |
| 원격 추적 정리 | `git remote prune origin` |
| 새 브랜치 생성 | `git checkout -b feat/<name>` |

## 흔한 실수

| 실수 | 해결 |
|------|------|
| main 업데이트 없이 브랜치 생성 | 항상 `git pull` 먼저 |
| 머지된 브랜치 방치 | PR 상태 확인 후 삭제 |
| 원격 추적 브랜치 누적 | `git remote prune origin` 실행 |

## 워크플로우 다이어그램

```
새 작업 시작
     │
     ▼
main으로 이동 & pull
     │
     ▼
로컬 브랜치 목록 확인
     │
     ▼
각 브랜치의 PR 상태 확인 ──┐
     │                    │
     ▼                    │
PR이 MERGED/CLOSED? ──────┤
     │ yes               │ no/없음
     ▼                   │
로컬 브랜치 삭제 ◄────────┘
     │
     ▼
git remote prune origin
     │
     ▼
새 feature 브랜치 생성
     │
     ▼
작업 시작
```

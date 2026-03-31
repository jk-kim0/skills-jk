---
name: session-startup
description: Use when starting a new task in skills-jk repo - ensures main is updated and a new feature branch is created before any work begins
---

# Session Startup

## Overview

skills-jk repo에서 새로운 작업을 시작할 때, 항상 최신 main 위에서 새 feature branch를 만들어 작업하는 규칙.

## When to Use

- skills-jk repo에서 새로운 지시사항/과제를 받았을 때
- 현재 작업 브랜치가 main이거나 이전 작업의 브랜치일 때

## 필수 절차

### 1. Repo 확인

```bash
# 현재 디렉토리가 skills-jk repo인지 확인
basename $(git rev-parse --show-toplevel 2>/dev/null)
```

결과가 `skills-jk`가 아니면 이 스킬 적용하지 않음.

### 2. Main 브랜치 업데이트

```bash
git checkout main
git pull origin main
```

### 3. Feature 브랜치 생성

```bash
git checkout -b <prefix>/<descriptive-name>
```

| 접두사 | 용도 |
|--------|------|
| `feat/` | 새 기능, 스킬 추가 |
| `fix/` | 버그 수정 |
| `docs/` | 문서 변경 |
| `refactor/` | 리팩토링 |

## 흐름도

```
새 작업 지시 받음
       │
       ▼
skills-jk repo인가? ─No─→ 스킬 미적용
       │Yes
       ▼
git checkout main && git pull
       │
       ▼
git checkout -b <prefix>/<name>
       │
       ▼
작업 시작
```

## 예외

- 이미 해당 작업을 위한 feature branch가 존재하고 활성화된 경우
- 기존 작업을 이어서 하는 경우 (resume)

## 관련 스킬

- [branch-workflow](./branch-workflow.md): 브랜치 관리 전체 워크플로우
- [commit](./commit.md): 커밋 메시지 규칙

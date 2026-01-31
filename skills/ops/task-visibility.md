---
name: task-visibility
description: Task/Project 생성 시 공개/비공개 여부를 판단하는 체크리스트
tags: [task, project, visibility, private, public]
---

# Task Visibility

## 목적

Task/Project 생성 시 공개 가능 여부를 판단하여 적절한 Repository에 저장한다.

## 적용 시점

- 새로운 Task 또는 Project를 생성할 때
- 기존 Task/Project의 공개 여부를 재검토할 때

## 공개 여부 판단 체크리스트

Task/Project 생성 전 다음을 확인한다.
하나라도 해당되면 **Private repo**에서 관리한다.

| 조건 | 확인 방법 | 결과 |
|------|----------|------|
| Slack 메시지 기반 작업 | 출처가 Slack인가? | → Private |
| Private git repo 작업 | `gh api repos/{owner}/{repo}` visibility 확인 | → Private |
| 고객사 이름 명시 | 문서에 고객사명이 포함되는가? | → Private |

## 수행 절차

### 1. 출처 확인

```
작업 요청의 출처가 Slack인가?
├─ 예 → Private repo (skills-jk-private)
└─ 아니오 → 다음 단계
```

### 2. 대상 Repository 확인

작업 대상 git repository가 있는 경우:

```bash
gh api repos/{owner}/{repo} --jq '.visibility'
```

- `private` → Private repo에서 관리
- `public` → 다음 단계

### 3. 고객사 정보 확인

```
문서에 고객사 이름이 포함되는가?
├─ 예 → Private repo
└─ 아니오 → Public repo 가능
```

## Repository 선택

| 조건 | Repository |
|------|------------|
| 위 조건 중 하나라도 해당 | `skills-jk-private` |
| 모두 해당 없음 | `skills-jk` |

## 빠른 참조

```
새 Task/Project 생성
       │
       ▼
┌─────────────────────────────┐
│ □ Slack 기반?               │
│ □ Private repo 작업?        │
│ □ 고객사명 포함?            │
└─────────────────────────────┘
       │
       ▼
  하나라도 체크됨?
  ├─ 예 → skills-jk-private
  └─ 아니오 → skills-jk
```

## 관련 문서

- [Repository 공개 범위](../../docs/repository-visibility.md)

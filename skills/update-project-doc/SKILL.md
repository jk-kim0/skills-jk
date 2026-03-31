---
name: update-project-doc
description: Use when a PR is created, a major feature is committed, or a milestone is reached - ensures the project planning document in projects/active/ is updated with progress
---

# Update Project Doc

## Overview

작업 완료 후 프로젝트 계획 문서(`projects/active/*.md`)에 진행 경과를 반영하는 규칙. PR 생성, 주요 커밋, 마일스톤 달성 시 반드시 수행한다.

## When to Use

- PR을 생성한 직후
- 주요 기능 구현이 완료되었을 때
- 프로젝트 마일스톤에 도달했을 때

## 필수 절차

### 1. 프로젝트 문서 찾기

```bash
ls projects/active/
```

현재 작업과 관련된 프로젝트 문서를 확인한다. 없으면 이 스킬은 적용하지 않는다.

### 2. 업데이트할 항목

| 항목 | 설명 | 예시 |
|------|------|------|
| **진행 상태 체크박스** | `[ ]` → `[x]` 전환 | `- [x] 브랜치 기반 배치 검증` |
| **진행 로그** | 날짜 + PR 링크 + 요약 | `- 2026-02-09: --branch 배치 verify/push (#624)` |
| **잔여 작업** | 완료된 항목 제거 또는 갱신 | 완료된 섹션 삭제 |
| **문서 내용 동기화** | CLI 사용법, 파일 구조 등 | 새 옵션/함수 반영 |

### 3. 진행 로그 형식

프로젝트 문서에 `## 진행 로그` 섹션이 없으면 `## 진행 상태` 바로 위에 추가한다.

```markdown
## 진행 로그

| 날짜 | PR | 내용 |
|------|-----|------|
| 2026-02-09 | querypie-docs#624 | `--branch` 배치 verify/push 구현 |
| 2026-02-08 | querypie-docs#622 | push가 verify 자동 수행 |
```

최신 항목이 위로 오도록 역순 정렬한다.

### 4. 브랜치 확인 후 커밋

```bash
# 반드시 현재 브랜치 확인
git branch --show-current

# main이면 즉시 feature 브랜치 생성
git checkout -b docs/<descriptive-name>
```

**main 브랜치에서 직접 커밋/push 금지.** 반드시 feature 브랜치에서 작업한 뒤 PR을 통해 main에 머지한다.

## 흐름도

```
PR 생성 / 주요 커밋 완료
       │
       ▼
projects/active/에 관련 문서 있는가? ─No─→ 종료
       │Yes
       ▼
진행 상태 체크박스 갱신
       │
       ▼
진행 로그에 날짜+PR+요약 추가
       │
       ▼
잔여 작업 섹션 정리
       │
       ▼
문서 내용 동기화 (CLI, 파일 구조 등)
       │
       ▼
현재 브랜치 확인 ─main─→ feature 브랜치 생성
       │feature branch
       ▼
skills-jk에 커밋 → PR 생성
```

## 흔한 실수

| 실수 | 결과 |
|------|------|
| **main에서 직접 커밋/push** | branch protection 위반, PR 리뷰 우회 |
| PR 만들고 문서 업데이트 안 함 | 프로젝트 문서가 실제와 괴리 |
| 체크박스만 갱신하고 세부 내용 미반영 | CLI 사용법이 코드와 불일치 |
| 진행 로그 없이 체크박스만 토글 | 언제 무엇이 완료됐는지 추적 불가 |

## 관련 스킬

- [create-pr](./create-pr.md): PR 생성 규칙
- [branch-workflow](./branch-workflow.md): 브랜치 관리 워크플로우

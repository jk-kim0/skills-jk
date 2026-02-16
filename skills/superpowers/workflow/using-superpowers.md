---
name: using-superpowers
description: Use when starting any non-trivial implementation task - selects and enforces the minimal superpowers workflow (brainstorming, plans, execution, verification)
tags: [workflow, superpowers, planning]
---

# Using Superpowers

## 목적

코드 작업 전에 문제 정의, 계획, 실행, 검증 단계를 강제해 품질을 안정화합니다.

## 수행 절차

1. 작업 성격 분류 (신규 기능/버그/리팩토링)
2. 필수 스킬 최소 세트 선택
3. 아래 표 순서로 실행

| 상황 | 권장 순서 |
|------|-----------|
| 신규 기능 | `brainstorming` -> `writing-plans` -> `executing-plans` -> `verification-before-completion` |
| 버그 수정 | `systematic-debugging` -> `test-driven-development` -> `verification-before-completion` |
| 대규모 작업 | `writing-plans` -> `dispatching-parallel-agents` -> `requesting-code-review` |

## 규칙

- 스킬은 최소 집합만 사용
- 코드 변경 전 계획 또는 디버깅 근거를 먼저 남김
- 완료 선언 전 검증 결과를 반드시 제시

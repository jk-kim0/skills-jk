---
name: executing-plans
description: Use after an approved plan exists - execute tasks in order, report progress continuously, and re-plan immediately when assumptions break
tags: [workflow, execution]
---

# Executing Plans

## 목적

승인된 계획을 순차적으로 구현하고 단계마다 검증합니다.

## 수행 절차

1. Task 1부터 순차 실행
2. 각 Task 종료 시 검증 실행
3. 실패 시 원인/수정/재검증 기록
4. 계획 변경 필요 시 즉시 플랜 갱신

## 진행 보고 규칙

- 현재 Task 번호
- 변경 파일
- 검증 결과 (성공/실패)
- 다음 Task

---
name: writing-plans
description: Use when implementation scope is clear - create a concrete, file-level task plan with verification steps and rollback considerations
tags: [workflow, planning, implementation]
---

# Writing Plans

## 목적

작업을 작고 검증 가능한 단위로 분해합니다.

## 수행 절차

1. 범위와 비범위 선언
2. 작업을 2~15분 단위로 분해
3. 각 작업에 파일 경로/변경 요약/검증 명시
4. 실패 시 롤백 방법 정의

## 계획 템플릿

```markdown
## Task N
- 목표:
- 변경 파일:
- 변경 내용:
- 검증 명령:
- 완료 조건:
- 롤백:
```

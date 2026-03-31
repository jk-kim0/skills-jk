---
name: test-driven-development
description: Use when adding or changing behavior - enforce RED-GREEN-REFACTOR with minimal production changes and explicit failing-first tests
tags: [coding, test, tdd]
---

# Test Driven Development

## 목적

테스트 우선으로 안정적인 변경을 수행합니다.

## 수행 절차

1. RED: 실패하는 테스트 먼저 작성
2. GREEN: 테스트 통과를 위한 최소 코드 작성
3. REFACTOR: 중복 제거/구조 개선
4. 회귀 테스트 실행

## 필수 규칙

- 테스트 없는 기능 코드 선작성 금지
- 한 사이클에서 하나의 행위만 변경
- 실패 원인 불명확 시 `systematic-debugging` 우선

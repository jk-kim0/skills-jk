---
name: subagent-driven-development
description: Use for large tasks requiring repeated implementation-review loops - delegate scoped units and enforce two-stage review before merge
tags: [workflow, decomposition, review]
---

# Subagent Driven Development

## 목적

큰 작업을 분할해 구현-리뷰 루프를 빠르게 반복합니다.

## 수행 절차

1. 작업 단위를 명확한 계약으로 분해
2. 단위별 구현 수행
3. 1차 리뷰: 요구사항 충족 여부
4. 2차 리뷰: 품질/안전성
5. 통합 및 회귀 검증

## 규칙

- 리뷰 실패 단위는 즉시 재작업
- 통합 전 인터페이스 호환성 확인

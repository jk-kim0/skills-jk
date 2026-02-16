---
name: dispatching-parallel-agents
description: Use when tasks are independent and can run concurrently - split workstreams safely and merge after explicit compatibility checks
tags: [workflow, parallelism, coordination]
---

# Dispatching Parallel Agents

## 목적

독립 작업을 병렬화해 리드타임을 줄입니다.

## 적용 조건

- 파일 충돌 가능성이 낮음
- 공통 인터페이스가 선행 정의됨
- 통합 검증 단계가 존재함

## 수행 절차

1. 병렬 가능 작업 식별
2. 작업별 입력/출력 계약 정의
3. 워크스트림 병렬 실행
4. 통합 전 충돌/인터페이스 검증
5. 최종 통합 테스트

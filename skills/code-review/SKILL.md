---
name: code-review
description: 코드 리뷰 수행 방법
tags: [coding, review, quality]
---

# Code Review

## 목적

PR이나 코드 변경사항을 리뷰하고 피드백 제공

## 수행 절차

1. 변경된 파일 목록 확인
2. 각 파일의 diff 분석
3. 다음 관점에서 검토:
   - 로직 오류
   - 보안 취약점
   - 성능 이슈
   - 코드 스타일
4. 피드백을 구조화된 형태로 정리

## 출력 형식

- 심각도별 분류 (critical, warning, suggestion)
- 파일:라인 형식으로 위치 명시
- 개선 제안 포함

## 예시 출력

```
## Critical
- src/auth.js:45 - SQL injection 취약점 발견

## Warning
- src/utils.js:12 - 불필요한 루프, O(n²) 복잡도

## Suggestion
- src/api.js:78 - 에러 메시지를 더 구체적으로
```

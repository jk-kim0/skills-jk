---
name: dependency-check
description: 프로젝트 의존성 상태 확인 및 업데이트 제안
tags: [ops, dependencies, maintenance]
---

# Dependency Check

## 목적

프로젝트의 의존성 상태를 확인하고 업데이트가 필요한 패키지를 식별

## 수행 절차

1. 패키지 매니저 확인 (npm, yarn, pip 등)
2. outdated 패키지 목록 조회
3. 각 패키지별 분석:
   - 현재 버전 vs 최신 버전
   - major/minor/patch 구분
   - breaking changes 여부
4. 업데이트 계획 수립

## 출력 형식

### Major Updates (주의 필요)
| 패키지 | 현재 | 최신 | Breaking Changes |
|--------|------|------|------------------|

### Minor/Patch Updates (안전)
| 패키지 | 현재 | 최신 |
|--------|------|------|

### 권장 조치
- 즉시 업데이트 가능한 패키지
- 별도 검토 필요한 패키지

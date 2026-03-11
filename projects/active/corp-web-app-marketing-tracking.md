---
id: corp-web-app-marketing-tracking
title: "corp-web-app: 온라인 마케팅 트래킹 및 Lead 저장"
status: active
repos:
  - https://github.com/querypie/corp-web-app
created: 2026-03-09
updated: 2026-03-11
---

# corp-web-app: 온라인 마케팅 트래킹 및 Lead 저장

> **Target Repo:** [querypie/corp-web-app](https://github.com/querypie/corp-web-app)
> **설계 문서:** [docs/utm-tracking.md](https://github.com/querypie/corp-web-app/blob/main/docs/utm-tracking.md)

---

## 목표

www.querypie.com 방문자의 마케팅 유입 경로(UTM)를 추적하고, 폼 제출 시 Salesforce Lead에 attribution 정보를 함께 저장하여 디지털 마케팅 캠페인 성과를 측정한다.

---

## Phase 1 — UTM Attribution 트래킹 및 Salesforce 연동

**상태: 완료**

| PR | 내용 | 머지일 |
|----|------|--------|
| [#606](https://github.com/querypie/corp-web-app/pull/606) | UTM 파라미터 추적 및 Salesforce Lead 저장 연동 | 2026-03-09 |
| [#607](https://github.com/querypie/corp-web-app/pull/607) | UTM 트래킹 설계 문서 추가 | 2026-03-09 |
| [#608](https://github.com/querypie/corp-web-app/pull/608) | Playwright E2E 테스트 추가 | 2026-03-09 |

### 구현 내용

**트래킹 모델: First-touch + Last 2 touches**

- 방문자가 UTM 파라미터가 포함된 URL로 접근하면 `utm-attribution` 쿠키에 자동 저장
- First-touch는 영구 보존, 이후 방문은 최근 2개를 rolling 갱신 (FIFO)
- 폼 제출 시 쿠키에서 attribution을 읽어 Salesforce Lead 필드에 저장

**Salesforce 필드 매핑** (Pardot 기존 필드 재사용, 신규 필드 추가 없음)

| 저장 값 | Salesforce 필드 |
|---------|----------------|
| last-touch `utm_source` | `pi__utm_source__c` |
| last-touch `utm_medium` | `pi__utm_medium__c` |
| last-touch `utm_campaign` | `pi__utm_campaign__c` |
| last-touch `utm_content` | `pi__utm_content__c` |
| last-touch `utm_term` | `pi__utm_term__c` |
| first-touch landing URL | `pi__first_touch_url__c` |

**주요 추가 파일**

- `src/utils/utm.ts` — UTM 로직 단일 모듈 (parseUtm, updateUtmAttribution, toSalesforceFields, readUtmCookie, useUtmCapture)
- `src/utils/__tests__/utm.test.ts` — 유닛 테스트 12개
- `tests/e2e/utm-tracking.spec.ts` — E2E 테스트 5개 (Playwright, stage.querypie.com 검증 완료)
- `docs/utm-tracking.md` — 설계 및 동작 방식 문서

---

## 다음 단계 (미착수)

아래는 검토 가능한 후속 과제 후보이다.

| 과제 | 설명 |
|------|------|
| DB 기반 Lead 저장 | Salesforce 외 자체 DB에 리드/attribution 저장 (분석·조회용) |
| 전환 이벤트 확장 | Contact Us 외 다른 폼(파트너, 스타트업 등)에도 attribution 전달 여부 확인 |
| Attribution 리포트 | GA4 또는 내부 대시보드에서 캠페인별 리드 전환율 확인 |

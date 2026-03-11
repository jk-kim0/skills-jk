---
id: corp-web-app-marketing-tracking
title: "corp-web-app: 온라인 마케팅 트래킹 및 Lead 저장"
status: active
repos:
  - https://github.com/querypie/corp-web-app
created: 2026-03-09
updated: 2026-03-11
wiki:
  - https://github.com/querypie/corp-web-app/wiki/UTM-Tracking-Parameter-Guide
---

# corp-web-app: 온라인 마케팅 트래킹 및 Lead 저장

> **Target Repo:** [querypie/corp-web-app](https://github.com/querypie/corp-web-app)
> **설계 문서:** [docs/utm-tracking.md](https://github.com/querypie/corp-web-app/blob/main/docs/utm-tracking.md)
> **마케터 가이드:** [Wiki — UTM Tracking Parameter Guide](https://github.com/querypie/corp-web-app/wiki/UTM-Tracking-Parameter-Guide)

---

## 목표

www.querypie.com 방문자의 마케팅 유입 경로(UTM)를 추적하고, **캠페인별 리드 전환율과 이용자 행동 분석 대시보드를 구성**하여 디지털 마케팅 캠페인 성과를 측정한다.

### 최종 목표 상태

캠페인 담당자가 다음 질문에 스스로 답할 수 있는 환경:

- "이번 달 Google CPC 캠페인이 만든 리드는 몇 건인가?"
- "linkedin vs google, 어느 채널의 전환율이 높은가?"
- "어떤 landing page에서 폼 제출이 가장 많이 발생하는가?"
- "어떤 landing page에서 폼 제출 전 이탈이 많은가?"

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
- `docs/utm-tracking.md` — 설계 및 동작 방식 문서 (개발자용)

---

## Phase 2 — 마케터 가이드 문서

**상태: 완료**

| 문서 | 위치 | 작성일 |
|------|------|--------|
| UTM Tracking Parameter Guide | [corp-web-app Wiki](https://github.com/querypie/corp-web-app/wiki/UTM-Tracking-Parameter-Guide) | 2026-03-11 |

EN/JA/KO 3개국어 병기. 파라미터 종류, URL 작성법, 작명 규칙, 자주 하는 실수 포함.

---

---

## Phase 3 — Attribution Report 대시보드

**상태: 미착수**

### 데이터 흐름 (현재 → 목표)

```
방문자 UTM URL 접속
  ├─ GA4 세션 자동 기록 (utm_source/medium/campaign 포함) ← 이미 동작
  └─ utm-attribution 쿠키 저장 ← Phase 1 완료

폼 제출
  └─ GA4 Conversion Event (generate_lead) ← Phase 3A 구현 예정

GA4 기본 리포트 / Looker Studio 대시보드
  └─ GA4 단일 데이터 소스: 세션 수, 이벤트, 전환 (캠페인별) ← Phase 3B 구현 예정
```

> **Salesforce 연동 제외**: Salesforce는 향후 Deprecate 예정이므로 Phase 3 범위에서 제외한다. GA4 단일 데이터 소스로 구성한다.

### Phase 3A — GA4 Conversion Event 등록

**목표:** 폼 제출을 GA4 전환 이벤트로 등록해, GA4 Acquisition 리포트에서 캠페인별 전환수·전환율을 바로 확인할 수 있게 한다.

**구현 내용:**

1. Contact Us 폼 제출 성공 시 `generate_lead` 이벤트 전송
   - 기존 `cta_submit_gating_form` 이벤트는 있으나 GA4 Conversion으로 미등록
   - `src/models/ga.ts`에 `generate_lead` 추가, `sendToEvent` 호출
   - GA4 Admin에서 `generate_lead`를 Conversion으로 마킹
2. 이벤트 파라미터에 `form_type` 포함 (contact_us / partner / startup 구분)

**완료 기준:** GA4 > Acquisition > Traffic acquisition 리포트에서 utm_campaign별 Conversions 컬럼 확인 가능

### Phase 3B — 대시보드 구성

**목표:** GA4 데이터만으로 캠페인 성과를 한눈에 볼 수 있는 대시보드를 구성한다.

**옵션 A: GA4 기본 리포트** (별도 구현 불필요)

Phase 3A 완료 후 GA4 기본 리포트에서 즉시 확인 가능한 항목:

| 리포트 위치 | 확인 가능 항목 |
|------------|--------------|
| Acquisition > Traffic acquisition | 채널·캠페인별 세션 수, 전환 수, 전환율 |
| Acquisition > User acquisition | 신규 사용자 유입 채널 분포 |
| Engagement > Landing page | 랜딩 페이지별 세션 수, 전환율 |
| Explore > Funnel exploration | 커스텀 전환 퍼널 (UTM 방문 → 폼 제출) |
| Explore > Path exploration | 전환 전 페이지 탐색 경로 |

**옵션 B: Looker Studio Free 대시보드** (GA4 단일 소스, 추가 비용 없음)

GA4 기본 리포트로 부족할 경우 Looker Studio에서 커스텀 대시보드 구성:

| 차트 | 측정 항목 |
|------|----------|
| 채널별 세션 → 전환 퍼널 | 세션 수 / generate_lead 이벤트 수 / 전환율 |
| 캠페인별 전환 수 추이 | utm_campaign별 generate_lead 건수 (월별) |
| 랜딩 페이지별 전환율 | 페이지별 세션 수 대비 generate_lead 비율 |
| 국가 × 채널 교차 분석 | 지역별 유입 채널 분포 |

**권고:** Phase 3A 완료 후 GA4 기본 리포트(옵션 A)로 먼저 운영하고, 커스터마이징 필요 시 옵션 B로 전환.

**완료 기준:** 캠페인 담당자가 링크 하나로 주요 지표를 자체 확인 가능

### Phase 3C — 이용자 행동 분석 (선택)

**목표:** 캠페인 유입 방문자가 전환 전 어떤 페이지를 탐색하는지 파악한다.

**구현 내용:**

1. GA4 Funnel Exploration: UTM 방문자의 페이지 탐색 경로 분석
2. 주요 랜딩 페이지에 scroll depth 이벤트 추가 (콘텐츠 소비 측정)
3. `/en/contact` 등 전환 직전 페이지 체류 시간 분석

> Phase 3A, 3B 완료 후 필요 여부 재검토

---

## 검토 후보 (미정)

현재 진행 계획 없음. 필요 시 재검토.

| 과제 | 설명 |
|------|------|
| DB 기반 Lead 저장 | Salesforce Deprecate 이후 자체 DB에 리드/attribution 저장 (분석·조회용) |
| 전환 이벤트 확장 | Contact Us 외 다른 폼(파트너, 스타트업 등)에도 generate_lead 이벤트 전달 여부 확인 |

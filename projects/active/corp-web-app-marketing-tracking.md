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

### Conversion 정의

> **Conversion 유형 2가지**
>
> | # | 유형 | 트리거 | GA4 이벤트 |
> |---|------|--------|-----------|
> | 1 | 폼 제출 | 사이트 내 모든 폼 제출 성공 (리드 정보 저장 시점) | `generate_lead` |
> | 2 | Plans 페이지 버튼 클릭 | Subscribe / Contact Us 등 구독·구매 의도 버튼 클릭 | `select_plan` |

### 최종 목표 상태

캠페인 담당자가 다음 질문에 스스로 답할 수 있는 환경:

- "이번 달 Google CPC 캠페인이 만든 리드는 몇 건인가?" (`generate_lead`)
- "linkedin vs google, 어느 채널의 전환율이 높은가?" (`generate_lead`)
- "어떤 landing page에서 폼 제출이 가장 많이 발생하는가?" (`generate_lead`)
- "어떤 landing page에서 폼 제출 전 이탈이 많은가?" (`generate_lead`)
- "Plans 페이지에서 어떤 채널 유입이 플랜 선택으로 가장 많이 이어지는가?" (`select_plan`)
- "AIP vs ACP, 어느 제품의 플랜 선택률이 높은가?" (`select_plan`)

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

## Phase 2 — GA4 Conversion Event 등록

**상태: 미착수**

### 데이터 흐름 (현재 → 목표)

```
방문자 UTM URL 접속
  ├─ GA4 세션 자동 기록 (utm_source/medium/campaign 포함) ← 이미 동작
  └─ utm-attribution 쿠키 저장 ← Phase 1 완료

폼 제출
  └─ GA4 Conversion Event (generate_lead) ← Phase 2A 구현 예정

Plans 페이지 버튼 클릭
  └─ GA4 Conversion Event (select_plan) ← Phase 2B 구현 예정

GA4 리포트 / Looker Studio 대시보드
  └─ GA4 단일 데이터 소스: 세션 수, 전환 수, 전환율 (캠페인별) ← Phase 3 구성 예정
```

> **Salesforce 연동 제외**: Salesforce는 향후 Deprecate 예정이므로 Phase 2 이후 범위에서 제외한다. GA4 단일 데이터 소스로 구성한다.

### Phase 2A — 폼 제출 Conversion (`generate_lead`)

**목표:** 모든 폼 제출 성공을 GA4 전환 이벤트로 등록해, GA4 Acquisition 리포트에서 캠페인별 전환수·전환율을 확인할 수 있게 한다.

**구현 내용:**

1. 모든 폼 제출 성공 시 `generate_lead` 이벤트 전송
   - 기존 `cta_submit_gating_form` 이벤트는 있으나 GA4 Conversion으로 미등록
   - `src/models/ga.ts`에 `generate_lead` 추가, `sendToEvent` 호출
   - GA4 Admin에서 `generate_lead`를 Conversion으로 마킹
2. 이벤트 파라미터에 `form_type` 포함으로 폼 종류 구분

**대상 폼 목록** (corp-web-app 내 전체):

| form_type 값 | 폼 종류 | submitAction |
|-------------|---------|-------------|
| `contact_us` | Contact Us | `contact-sales` |
| `partner` | 파트너 신청 | `apply-partner` |
| `startup` | 스타트업 프로그램 신청 | `apply-startup` |
| `read_document` | 문서 다운로드 | `read-document` |
| `unlock_document` | 문서 잠금 해제 | `unlock-document` |
| `community_license` | Community 라이선스 신청 | `apply-querypie-community-license` |

**완료 기준:** GA4 > Acquisition > Traffic acquisition 리포트에서 utm_campaign별 `generate_lead` Conversions 컬럼 확인 가능

### Phase 2B — Plans 페이지 버튼 클릭 Conversion (`select_plan`)

**목표:** Plans 페이지 구독·구매 의도 버튼 클릭을 GA4 전환 이벤트로 등록해, 채널별 플랜 선택률을 확인할 수 있게 한다.

**구현 내용:**

1. Plans 페이지(`/plans`, `/en/plans`, `/ko/plans`, `/ja/plans`) 버튼 클릭 시 `select_plan` 이벤트 전송
   - `Plan.Button`에 `gaEvent` prop 연결 필요 (`ButtonLink`는 이미 지원)
   - GA4 Admin에서 `select_plan`을 Conversion으로 마킹
2. 이벤트 파라미터에 `plan_name` 포함으로 플랜 구분

**대상 버튼 목록:**

| 버튼 | plan_name 값 | 이동 위치 |
|------|-------------|---------|
| Subscribe ($20/mo) | `aip_starter` | app.querypie.com |
| Subscribe ($500/mo) | `aip_team` | app.querypie.com |
| Try Now (Enterprise) | `aip_enterprise` | app.querypie.com |
| Install Now (Community) | `acp_community` | docs.querypie.com |
| Contact Us (Standard) | `acp_standard` | /company/contact-us |
| Contact Us (Enterprise) | `acp_enterprise` | /company/contact-us |

**완료 기준:** GA4 > Acquisition > Traffic acquisition 리포트에서 utm_campaign별 `select_plan` Conversions 컬럼 확인 가능

---

## Phase 3 — Attribution Report 대시보드

**상태: 미착수** (Phase 2 완료 후 착수)

### Phase 3A — GA4 기본 리포트 운영

Phase 2 완료 즉시 GA4 기본 리포트에서 추가 구현 없이 확인 가능:

| 리포트 위치 | 확인 가능 항목 |
|------------|--------------|
| Acquisition > Traffic acquisition | 채널·캠페인별 세션 수, 전환 수, 전환율 |
| Acquisition > User acquisition | 신규 사용자 유입 채널 분포 |
| Engagement > Landing page | 랜딩 페이지별 세션 수, 전환율 |

**완료 기준:** 캠페인 담당자가 GA4 기본 리포트에서 최종 목표 상태의 6개 질문에 모두 답할 수 있음

### Phase 3B — Looker Studio 대시보드 (조건부)

> GA4 기본 리포트(Phase 3A)로 충분하면 생략한다. 커스터마이징 또는 공유 가능한 고정 링크가 필요할 때만 진행한다.

GA4 단일 소스, 추가 비용 없음(Looker Studio Free):

| 차트 | 측정 항목 |
|------|----------|
| 채널별 세션 → 전환 퍼널 | 세션 수 / generate_lead 이벤트 수 / 전환율 |
| 캠페인별 전환 수 추이 | utm_campaign별 generate_lead 건수 (월별) |
| 랜딩 페이지별 전환율 | 페이지별 세션 수 대비 generate_lead 비율 |
| 국가 × 채널 교차 분석 | 지역별 유입 채널 분포 |

**완료 기준:** 캠페인 담당자가 링크 하나로 주요 지표를 자체 확인 가능

### Phase 3C — 이용자 행동 심층 분석 (선택)

> Phase 3A 운영 후 추가 인사이트가 필요할 때만 진행한다.

GA4 Explore 기능을 활용한 심층 분석 (별도 코드 구현 없음):

1. **Funnel Exploration**: UTM 방문 → 주요 페이지 탐색 → 폼 제출 경로 시각화
2. **Path Exploration**: 전환 직전 방문 페이지 분포 확인
3. **Scroll depth 이벤트 추가** (선택): 주요 랜딩 페이지 콘텐츠 소비 측정 (코드 구현 필요)

---

## 지원 문서

| 문서 | 위치 | 작성일 | 대상 |
|------|------|--------|------|
| UTM Tracking Parameter Guide | [corp-web-app Wiki](https://github.com/querypie/corp-web-app/wiki/UTM-Tracking-Parameter-Guide) | 2026-03-11 | 마케터 |
| UTM 트래킹 설계 문서 | [docs/utm-tracking.md](https://github.com/querypie/corp-web-app/blob/main/docs/utm-tracking.md) | 2026-03-09 | 개발자 |

---

## 검토 후보 (미정)

현재 진행 계획 없음. 필요 시 재검토.

| 과제 | 설명 |
|------|------|
| 전환 이벤트 세분화 | form_type별 별도 Conversion 등록 여부 (예: partner 폼과 contact_us 폼을 분리 추적) |

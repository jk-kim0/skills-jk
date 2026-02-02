# QueryPie 도메인 현황 및 SEO 분석 대상 평가

## 개요

| 항목 | 내용 |
|------|------|
| 분석 일자 | 2026-02-02 |
| 분석 기간 | 2025-11-01 ~ 2026-01-30 (90일) |
| 등록된 도메인 | 11개 (도메인 속성 2개 포함) |
| 분석 도구 | `gsc` CLI (bin/gsc) |

---

## 0. QueryPie 제품 및 도메인 매핑

### 제품 개요

QueryPie는 두 가지 주요 제품 라인을 운영합니다:

| 제품 | 전체 명칭 | 배포 방식 | 설명 |
|------|-----------|-----------|------|
| **ACP** | Access Control Platform | 온프레미스 | 데이터베이스/서버 접근 제어 솔루션 |
| **AIP** | AI Platform | SaaS | AI 에이전트 보안 및 MCP 관리 플랫폼 |

### 제품-도메인 매핑

| 제품 | 도메인 | 용도 | GA Property |
|------|--------|------|-------------|
| **공통** | www.querypie.com | 마케팅 사이트 | 451239708 (QueryPie Homepage) |
| **ACP** | docs.querypie.com | ACP 제품 문서 | 522469891 (ACP Docs) |
| **ACP** | (온프레미스 설치) | ACP 애플리케이션 | 451236681 (ACP Application) |
| **AIP** | app.querypie.com | AIP 애플리케이션 (SaaS) | ⚠️ **미설정** |
| **AIP** | aip-docs.app.querypie.com | AIP 제품 문서 | 491852908 (AIP Docs) |

### ⚠️ 주의사항

**GA Property "ACP Application" (451236681)**:
- 이 Property는 **온프레미스로 설치된 ACP 제품**의 사용 데이터를 수집
- **app.querypie.com (AIP SaaS)과 무관**
- ACP Application의 트래픽 소스는 주로 기업 SSO (Okta 등)를 통한 접근

**app.querypie.com GA 설정 필요**:
- 현재 app.querypie.com에 대한 별도 GA Property가 없음
- AIP 서비스 사용자 분석을 위해 GA 설정 권장

---

## 1. 도메인 전체 현황

### 1.1 도메인 속성 (Domain Property) 총계

| 도메인 속성 | 클릭 | 노출 | CTR | 평균 순위 |
|-------------|------|------|-----|-----------|
| **sc-domain:querypie.com** | 5,741 | 306,586 | 1.9% | 13.4 |
| sc-domain:querypie.ai | 0 | 5 | 0.0% | 8.0 |

**참고**: 도메인 속성은 해당 도메인의 모든 하위 도메인 트래픽을 합산

### 1.2 개별 도메인 트래픽 요약

| 순위 | 도메인 | 클릭 | 노출 | CTR | 순위 | 분석 상태 |
|------|--------|------|------|-----|------|-----------|
| 1 | www.querypie.com | 4,566 | 273,036 | 1.7% | 13.6 | ✅ 완료 |
| 2 | docs.querypie.com | 1,175 | 36,376 | 3.2% | 9.8 | ✅ 완료 |
| 3 | aip-docs.app.querypie.com | 134 | 2,718 | 4.9% | 21.7 | 🔍 검토 필요 |
| 4 | trust.querypie.com | 2 | 127 | 1.6% | 4.5 | ⏸️ 보류 |
| 5 | app.querypie.com | 0 | 0 | - | - | ✅ 완료 |
| 6 | querypie.ai | 0 | 3 | 0.0% | 6.5 | ⏸️ 보류 |
| 7 | www.querypie.ai | 0 | 0 | - | - | ⏸️ 보류 |
| 8 | docs.querypie.ai | 0 | 0 | - | - | ⏸️ 보류 |
| 9 | querypie.com (non-www) | 0 | 0 | - | - | ⏸️ 보류 |

---

## 2. 도메인별 상세 분석

### 2.1 www.querypie.com ✅

| 항목 | 내용 |
|------|------|
| 역할 | 메인 마케팅 사이트 |
| 클릭 | 4,566 (전체의 80%) |
| 노출 | 273,036 |
| CTR | 1.7% |
| 사이트맵 | 14개, 1,455 URL |
| 분석 상태 | ✅ 완료 ([리포트](./2026-02-02-seo-analysis-www-querypie.md)) |

**주요 발견:**
- 미국 시장 CTR 0.1% (심각)
- 일본 현지화 성공 (CTR 6.8%)
- chat/publication 브랜드 희석 문제

---

### 2.2 docs.querypie.com ✅

| 항목 | 내용 |
|------|------|
| 역할 | 제품 문서 사이트 |
| 클릭 | 1,175 (전체의 20%) |
| 노출 | 36,376 |
| CTR | 3.2% |
| 사이트맵 | 4개, 864 URL (3개 언어) |
| 분석 상태 | ✅ 완료 ([리포트](./2026-02-02-seo-analysis-docs-querypie.md)) |

**주요 발견:**
- 월간 6배 성장 추세
- 한국 시장 CTR 8.5% (우수)
- 영어 콘텐츠 CTR 개선 필요

---

### 2.3 app.querypie.com ✅

| 항목 | 내용 |
|------|------|
| 역할 | **QueryPie AIP (AI Platform)** SaaS 서비스 |
| 제품 | AIP - AI 에이전트 보안 및 MCP 관리 플랫폼 |
| 클릭 | 0 |
| 노출 | 0 |
| 사이트맵 | 2개, 158 URL |
| GA Property | ⚠️ **미설정** (별도 설정 필요) |
| 분석 상태 | ✅ 완료 ([리포트](./2026-02-02-seo-analysis-app-querypie.md)) |

**주요 발견:**
- 인덱싱 실패 (Redirect Error)
- HTTP HEAD 요청 405 에러
- 긴급 조치 필요

**⚠️ 참고**: GA Property 451236681 (ACP Application)은 온프레미스 ACP 제품용이며, app.querypie.com (AIP SaaS)과 무관

---

### 2.4 aip-docs.app.querypie.com 🔍

| 항목 | 내용 |
|------|------|
| 역할 | AIP (AI Platform) 문서 |
| 클릭 | 134 |
| 노출 | 2,718 |
| CTR | 4.9% |
| 평균 순위 | 21.7 |
| 사이트맵 | 4개, 247 URL (3개 언어) |
| 분석 상태 | 🔍 검토 필요 |

**현황:**
- 최근 트래픽 증가 추세 (1월 중순 이후)
- MCP 관련 검색어에서 노출 (airtable, dify, slack 등)
- 순위가 매우 낮음 (평균 21.7위) → 개선 여지 큼

**분석 필요 여부:** ⚠️ **조건부 필요**
- 트래픽이 성장 중이나 아직 규모가 작음
- MCP 통합 문서 특성상 향후 성장 잠재력 있음
- 현재는 www.querypie.com 영어 콘텐츠 개선이 우선

---

### 2.5 trust.querypie.com ⏸️

| 항목 | 내용 |
|------|------|
| 역할 | Trust Center (보안 인증) |
| 클릭 | 2 |
| 노출 | 127 |
| CTR | 1.6% |
| 사이트맵 | 없음 |
| 분석 상태 | ⏸️ 보류 |

**현황:**
- 트래픽이 거의 없음 (90일간 2 클릭)
- 사이트맵 미등록
- 검색 트래픽보다 직접 방문 목적의 사이트

**분석 필요 여부:** ❌ **불필요**
- Trust Center는 검색 트래픽 목적이 아님
- B2B 고객이 직접 방문하여 인증 정보 확인 용도
- SEO 투자 대비 효과 낮음

---

### 2.6 querypie.ai / www.querypie.ai / docs.querypie.ai ⏸️

| 도메인 | 클릭 | 노출 | 상태 |
|--------|------|------|------|
| querypie.ai | 0 | 3 | 리다이렉트 추정 |
| www.querypie.ai | 0 | 0 | 리다이렉트 추정 |
| docs.querypie.ai | 0 | 0 | 리다이렉트 추정 |

**현황:**
- 트래픽 거의 없음
- .ai 도메인은 www.querypie.com으로 리다이렉트되는 것으로 추정
- 사이트맵 미등록

**분석 필요 여부:** ❌ **불필요**
- 독립 사이트가 아닌 리다이렉트 용도
- www.querypie.com에서 통합 관리

---

### 2.7 querypie.com (non-www) ⏸️

| 항목 | 내용 |
|------|------|
| 클릭 | 0 |
| 노출 | 0 |
| 상태 | www.querypie.com으로 리다이렉트 |

**분석 필요 여부:** ❌ **불필요**
- www 버전으로 리다이렉트되는 표준 설정

---

## 3. 분석 우선순위 권장

### 3.1 분석 완료 (3개)

| 우선순위 | 도메인 | 상태 | 후속 조치 |
|----------|--------|------|-----------|
| - | www.querypie.com | ✅ 완료 | 권장 조치 실행 |
| - | docs.querypie.com | ✅ 완료 | 권장 조치 실행 |
| - | app.querypie.com | ✅ 완료 | 긴급 조치 필요 |

### 3.2 추가 분석 검토 (1개)

| 우선순위 | 도메인 | 조건 | 권장 시점 |
|----------|--------|------|-----------|
| 낮음 | aip-docs.app.querypie.com | 트래픽 500+ 클릭/월 도달 시 | 2026년 Q2 |

### 3.3 분석 불필요 (5개)

| 도메인 | 사유 |
|--------|------|
| trust.querypie.com | 검색 트래픽 목적 아님 |
| querypie.ai | 리다이렉트 용도 |
| www.querypie.ai | 리다이렉트 용도 |
| docs.querypie.ai | 리다이렉트 용도 |
| querypie.com | www로 리다이렉트 |

---

## 4. 종합 트래픽 분석

### 4.1 트래픽 분포

```
전체 클릭: 5,741 (90일)
├── www.querypie.com: 4,566 (79.5%)
├── docs.querypie.com: 1,175 (20.5%)
├── aip-docs: 134 (미포함, 별도 서브도메인)
└── 기타: ~2 (<0.1%)
```

### 4.2 트래픽 트렌드

| 월 | www | docs | 합계 | 전월 대비 |
|----|-----|------|------|-----------|
| 11월 | 1,631 | 125 | 1,756 | - |
| 12월 | 1,207 | 393 | 1,600 | -9% |
| 1월 | 1,728 | 657 | 2,385 | +49% |

**트렌드 분석:**
- 12월 휴일 시즌 소폭 하락
- 1월 비즈니스 시즌 복귀로 강한 반등 (+49%)
- docs.querypie.com 성장률이 특히 높음 (11월 대비 5.3배)

---

## 5. 권장 액션 플랜

### 5.1 즉시 실행

| 우선순위 | 도메인 | 액션 |
|----------|--------|------|
| 1 | app.querypie.com | HTTP HEAD 요청 지원 추가 (405 에러 수정) |
| 2 | www.querypie.com | 미국 타겟 영어 콘텐츠 메타 설명 최적화 |
| 3 | www.querypie.com | chat/publication 관련 없는 콘텐츠 noindex |

### 5.2 단기 (1개월 내)

| 우선순위 | 도메인 | 액션 |
|----------|--------|------|
| 4 | docs.querypie.com | 영어 podman 문서 CTR 개선 |
| 5 | www.querypie.com | 블로그 CTR 최적화 (PAM, AI Security) |
| 6 | www.querypie.com | 사이트맵 오류/경고 해결 |

### 5.3 중기 (1-3개월)

| 우선순위 | 도메인 | 액션 |
|----------|--------|------|
| 7 | 전체 | MCP/AI 에이전트 보안 키워드 콘텐츠 확대 |
| 8 | aip-docs | 트래픽 모니터링 후 분석 여부 결정 |

---

## 6. 모니터링 계획

```bash
# 월간 도메인 전체 현황 체크

# 1. 도메인 속성 전체 트래픽
gsc query "sc-domain:querypie.com" --by-device --days 30

# 2. 주요 도메인별 트래픽
for site in "https://www.querypie.com/" "https://docs.querypie.com/" "https://aip-docs.app.querypie.com/"; do
  echo "=== $site ==="
  gsc query "$site" --by-device --days 30
done

# 3. 신규 도메인 트래픽 발생 여부
gsc query "https://trust.querypie.com/" --by-date --days 30
gsc query "sc-domain:querypie.ai" --by-date --days 30
```

---

## 7. 결론

### 현재 상태

- **핵심 도메인 2개** (www, docs)가 전체 트래픽의 99.9% 차지
- **app.querypie.com** 긴급 조치 필요 (인덱싱 실패)
- **aip-docs** 성장 잠재력 있으나 현재는 규모 작음
- **기타 도메인** 리다이렉트 또는 특수 목적으로 SEO 분석 불필요

### 핵심 메시지

> **"선택과 집중"**: www.querypie.com과 docs.querypie.com에 SEO 리소스를 집중하고,
> app.querypie.com의 기술적 문제를 해결하는 것이 최우선 과제입니다.

### 다음 단계

1. ✅ 완료된 3개 도메인 리포트의 권장 조치 실행
2. 🔧 app.querypie.com 기술 이슈 긴급 수정
3. 📊 월간 도메인 트래픽 모니터링 체계 구축
4. 🔍 aip-docs 트래픽 추이 관찰 후 Q2 분석 여부 결정

---

## 부록: 분석에 사용된 명령어

```bash
# 전체 사이트 목록
gsc sites

# 도메인 속성 전체 트래픽
gsc query "sc-domain:querypie.com" --by-device --days 90
gsc query "sc-domain:querypie.ai" --by-device --days 90

# 개별 도메인 트래픽
gsc query "https://www.querypie.com/" --by-device --days 90
gsc query "https://docs.querypie.com/" --by-device --days 90
gsc query "https://app.querypie.com/" --by-device --days 90
gsc query "https://aip-docs.app.querypie.com/" --by-device --days 90
gsc query "https://trust.querypie.com/" --by-device --days 90

# 사이트맵 현황
gsc sitemaps "https://querypie.ai/"
gsc sitemaps "https://trust.querypie.com/"
gsc sitemaps "https://aip-docs.app.querypie.com/"
```

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

## 5.5 도메인 간 시너지 전략 (2026-02-03 Round 5 추가)

### 내부 링크 시너지 맵

```
www.querypie.com (DR 55)
├── → docs.querypie.com (문서 링크)
├── → aip-docs.app.querypie.com (AIP 문서 링크) ⚠️ 강화 필요
└── → app.querypie.com (AIP 서비스 링크) ⚠️ 강화 필요

docs.querypie.com (DR 55 상속)
├── → www.querypie.com (홈페이지 링크)
└── ← www.querypie.com (인바운드 내부 링크) ✅ 양호

aip-docs.app.querypie.com (백링크 1개, 권위 부족)
├── ← www.querypie.com (인바운드 필요) 🔴 긴급
└── ← app.querypie.com (인바운드 필요) 🔴 긴급

app.querypie.com (인덱싱 실패)
├── ← www.querypie.com (인바운드 필요) 🔴 긴급
└── → aip-docs (문서 링크) 인덱싱 해결 후 자동 적용
```

### 초저경쟁 키워드 전체 현황 (Round 2-15 발굴)

**🔥 난이도 0-5 키워드 (최우선)**

| 키워드 | 시장 | 검색량 | 난이도 | 타겟 도메인 | 조치 상태 |
|--------|------|--------|--------|-------------|-----------|
| **database access management** | US | 150 | **0** | www.querypie.com | 🔴 콘텐츠 생성 필요 |
| **ldap integration** | US | 200 | **0** | docs.querypie.com | 🔴 영어 문서 최적화 |
| **データマスキング** | JP | 200 | **0** | www.querypie.com | 🔴 일본어 콘텐츠 |
| **内部統制** | JP | **6,800** | **0** | www.querypie.com | 🔥🔥🔥 대박 기회! |
| **アクセス制御** | JP | 500 | **0** | www.querypie.com | 🔴 ACP 핵심 |
| **権限管理** | JP | 200 | **0** | www.querypie.com | 🔴 ACP 기능 |
| **特権アクセス管理** | JP | 100 | **0** | www.querypie.com | 🔴 PAM 일본어 |
| **監査ログ** | JP | 450 | **1** | docs.querypie.com | 🔴 문서 최적화 |
| **sso** | JP | 9,300 | **3** | docs.querypie.com | 🔴 고볼륨 저경쟁 |
| **mfa** | JP | 13,000 | **5** | docs.querypie.com | 🔴 초고볼륨 |
| **데이터 마스킹** | KR | 80 | **0** | www.querypie.com | 🔴 한국어 콘텐츠 |
| **data access governance** | US | 450 | **1** | www.querypie.com | 🔴 콘텐츠 생성 필요 |
| **database audit** | US | 150 | **1** | www.querypie.com | 🔴 콘텐츠 생성 필요 |
| **ai 에이전트** | KR | 3,600 | **1** | app.querypie.com | 🔴 인덱싱 후 |
| **ai 플랫폼** | KR | 1,100 | **1** | app.querypie.com | 🔴 인덱싱 후 |
| **제로트러스트** | KR | 1,100 | **1** | www.querypie.com | 🔴 핫 키워드! |
| **iam** | KR | 1,300 | **2** | www.querypie.com | 🔴 고볼륨 |
| **내부통제** | KR | 350 | **0** | www.querypie.com | 🔴 컴플라이언스 |
| **mfa 인증** | KR | 350 | **0** | docs.querypie.com | 🔴 인증 가이드 |
| **데이터 암호화** | KR | 150 | **0** | docs.querypie.com | 🔴 ACP 기능 |
| **보안감사** | KR | 100 | **0** | www.querypie.com | 🔴 ACP 기능 |
| **감사로그** | KR | 70 | **0** | docs.querypie.com | 🔴 ACP 기능 |
| **database access control** | US | 90 | **2** | www.querypie.com | 🔴 랜딩 페이지 생성 |
| **active directory integration** | US | 400 | **2** | docs.querypie.com | 🔴 영어 문서 최적화 |
| **context model** | US | 90 | **4** | aip-docs | 🔴 MCP 문서 최적화 |
| **ai access control** | US | 250 | **5** | aip-docs | 🔴 AIP 핵심 키워드 |
| **data governance platform** | US | 800 | **6** | www.querypie.com | 🔴 콘텐츠 생성 필요 |

**🔥 Round 16: 추가 발굴 키워드 (난이도 1-6)**

| 키워드 | 시장 | 검색량 | 난이도 | 타겟 도메인 | 제품 매칭 |
|--------|------|--------|--------|-------------|-----------|
| **kubernetes secrets management** | US | 150 | **1** | docs.querypie.com | ACP 기능 |
| **sql server security** | US | 150 | **3** | docs.querypie.com | ACP 기능 |
| **ssh key management** | US | 200 | **3** | docs.querypie.com | ACP 기능 |
| **database activity monitoring** | US | 450 | **3** | www.querypie.com | ACP 핵심 |
| **database firewall** | US | 100 | **4** | www.querypie.com | ACP 기능 |
| **database compliance** | US | 150 | **6** | www.querypie.com | ACP 기능 |

**🟡 난이도 6-20 키워드 (중요)**

| 키워드 | 시장 | 검색량 | 난이도 | 타겟 도메인 | 조치 상태 |
|--------|------|--------|--------|-------------|-----------|
| **ai agent security** | US | 700 | **8** | www.querypie.com | 🔴 블로그 작성 |
| **postgresql security** | US | 150 | **9** | docs.querypie.com | 🔴 문서 추가 |
| **session recording** | US | 250 | **10** | www.querypie.com | 🔴 기능 페이지 |
| **privileged identity management** | US | 1,300 | **12** | www.querypie.com | 🔴 PAM 콘텐츠 |
| **just in time access** | US | 700 | **12** | www.querypie.com | 🔴 PAM 콘텐츠 |
| **mcp authentication** | US | 300 | **18** | aip-docs | 🔴 기술 문서 |
| **pam tools** | US | 500 | **19** | www.querypie.com | 🔴 비교 페이지 |
| **dynamic data masking** | US | 250 | **20** | docs.querypie.com | 🟡 기존 문서 개선 |

### 통합 백링크 전략

**1단계: 내부 링크 강화 (즉시 실행)**
```
[수정 필요 페이지: www.querypie.com]
- 홈페이지 푸터/네비게이션에 aip-docs, docs 링크 추가
- /solutions/aip 페이지에서 aip-docs 문서 링크
- /products 페이지에서 docs.querypie.com 링크
```

**2단계: 외부 백링크 확보 (1개월 내)**
| 타겟 | 소스 | 액션 |
|------|------|------|
| aip-docs | GitHub MCP 프로젝트 | README에 문서 링크 추가 |
| docs.querypie.com | Medium | 기술 블로그에 문서 인용 |
| www.querypie.com | G2, Capterra | 리뷰 페이지 업데이트 |

### 도메인별 Round 5 액션 요약

| 도메인 | 최우선 액션 | 담당 | 예상 효과 |
|--------|------------|------|-----------|
| **www.querypie.com** | "database access control" 랜딩 페이지 생성 | Content | 신규 트래픽 50+/월 |
| **docs.querypie.com** | "ldap integration" 영어 문서 title/meta 최적화 | Content | 영어 트래픽 3배 |
| **aip-docs** | "what is an mcp server" 개념 문서 생성 | Content | 신규 트래픽 100+/월 |
| **app.querypie.com** | HTTP HEAD 405 수정 | Backend | 인덱싱 시작 |

---

## 5.6 전체 액션 우선순위 매트릭스 (Round 7 종합)

Round 2-6 분석에서 도출된 모든 액션을 통합 정리:

### 🔴 긴급 (즉시 실행)

| # | 도메인 | 액션 | 예상 효과 | 담당 | 상태 |
|---|--------|------|-----------|------|------|
| 1 | **app.querypie.com** | HTTP HEAD 405 에러 수정 | 인덱싱 시작 | Backend | 🔴 대기 |
| 2 | **app.querypie.com** | GSC 수동 인덱싱 요청 | 크롤링 재시작 | Marketing | 🔴 대기 |
| 3 | **www.querypie.com** | /chat/publication noindex 처리 | 브랜드 희석 방지 | DevOps | 🔴 대기 |

### 🟡 높음 (1주 이내)

| # | 도메인 | 액션 | 예상 효과 | 담당 |
|---|--------|------|-----------|------|
| 4 | www.querypie.com | "database access control" 랜딩 페이지 생성 | 신규 트래픽 50+/월 | Content |
| 5 | docs.querypie.com | "ldap integration" 영어 문서 최적화 | 영어 트래픽 3배 | Content |
| 6 | aip-docs | "what is an mcp server" 개념 문서 생성 | 신규 트래픽 100+/월 | Content |
| 7 | www.querypie.com | sitemap.xml 오류 1개 수정 | 크롤링 정상화 | DevOps |
| 8 | www.querypie.com | 미국 타겟 영어 메타 설명 최적화 | CTR 0.1%→1%+ | Marketing |

### 🟢 중요 (2-4주 이내)

| # | 도메인 | 액션 | 예상 효과 | 담당 |
|---|--------|------|-----------|------|
| 9 | aip-docs | MCP 통합 허브 페이지 생성 | MCP 키워드 선점 | Product |
| 10 | docs.querypie.com | "active directory integration" 영어 문서 최적화 | 신규 트래픽 | Content |
| 11 | www.querypie.com | "ai agent security" 블로그 작성 | 신규 시장 진입 | Content |
| 12 | www.querypie.com | Substack 기술 블로그 개설 | DR 93 백링크 확보 | Marketing |
| 13 | 전체 | www → aip-docs 내부 링크 강화 | 권위 전달 | DevOps |

### 🔵 개선 (1-3개월)

| # | 도메인 | 액션 | 예상 효과 | 담당 |
|---|--------|------|-----------|------|
| 14 | www.querypie.com | Docker Hub 프로젝트 등록 | DR 92 백링크 | DevOps |
| 15 | docs.querypie.com | FAQ 구조화 데이터 추가 | 리치 스니펫 | DevOps |
| 16 | aip-docs | "mcp security" 보안 문서 강화 | AIP USP 강화 | Content |
| 17 | www.querypie.com | MCP 시장 콘텐츠 확대 | 장기 트래픽 | Content |
| 18 | docs.querypie.com | 일본어 페이지 크롤링 갱신 요청 | JP 트래픽 확대 | DevOps |

### 효과-노력 매트릭스

```
높은 효과 │
          │  [1] HTTP HEAD 수정     [4] database access control
          │  [3] noindex 처리       [6] MCP 개념 문서
          │  [5] ldap 최적화        [11] ai agent security
          │                         [12] Substack 개설
          │─────────────────────────────────────────────────────
          │  [7] sitemap 수정       [14] Docker Hub
          │  [8] 메타 설명          [15] FAQ 구조화
낮은 효과 │
          └──────────────────────────────────────────────────────
                 낮은 노력                  높은 노력
```

**Quick Wins (즉시 높은 효과)**:
- #1, #3: 기술 수정만으로 즉시 효과
- #5, #7, #8: 콘텐츠 수정만으로 효과

**Strategic Investments (노력 대비 높은 효과)**:
- #4, #6, #11: 신규 콘텐츠 생성 필요하지만 효과 높음
- #12: 외부 플랫폼 활용으로 백링크 확보

---

## 5.7 글로벌 경쟁사 현황 (Round 13 추가)

### PAM 시장 경쟁 포지션

```
Domain Rating 비교 (PAM 시장):

CyberArk      ████████████████████████████████████████ DR 81 | 트래픽 52,759/월
BeyondTrust   ███████████████████████████████████████████ DR 87 | 트래픽 56,400/월
Delinea       ██████████████████████████████████████ DR 77 | 트래픽 36,781/월
SSH.com       ████████████████████████████████████████ DR 80 | 트래픽 30,678/월
────────────────────────────────────────────────────────────────────────────
QueryPie      ███████████████████████████ DR 55 | 트래픽 955/월
```

### 국가별 주요 경쟁사

| 시장 | 경쟁사 | 공통 키워드 | 키워드 공유율 | 전략적 시사점 |
|------|--------|------------|--------------|---------------|
| 🇺🇸 US | CyberArk, BeyondTrust, Delinea | 6-7개 | 0.1% 미만 | PAM 직접 경쟁 어려움 → 니치 키워드 |
| 🇯🇵 JP | Qiita, zenn.dev | 1-3개 | 0.0% | 기술 커뮤니티 활용 기회 |
| 🇰🇷 KR | CyberArk, getastra.com | 2-5개 | **5.2%** (getastra) | 로컬 경쟁 활발 |

### 시장별 전략 방향

| 시장 | 현재 상태 | 권장 전략 |
|------|-----------|-----------|
| **US** | PAM 대기업 대비 DR/트래픽 격차 큼 | 초저경쟁 키워드 집중 (difficulty 0-5) |
| **JP** | Qiita/zenn.dev 기술 커뮤니티가 경쟁사 | 일본어 기술 블로그 연재로 노출 확보 |
| **KR** | 로컬 경쟁사 대비 우위 (트래픽 881) | 브랜드 키워드 강화, 로컬 SEO |

---

## 5.8 한국 시장 경쟁사 상세 분석 (Round 17 추가)

### 제품 영역별 경쟁사 매핑

| 영역 | QueryPie 제품 | 경쟁사 |
|------|--------------|--------|
| **DAC** (Database Access Control) | ACP | DbSafer, ChakraMax, DB-i, PETRA, PISO, SSDB |
| **SAC** (Server Access Control) | ACP | CyberArk PAM, HiWARE TAM, Password Manager Pro, IDoperation, ESS AdminOne, SecureCube Access Check |
| **KAC** (Kubernetes Access Control) | ACP | Teleport |
| **WAC** (Web Application Control) | ACP | CyberArk WAC |

### SEO 경쟁력 비교 (한국 시장)

```
한국 시장 Organic Traffic 순위:

PISO (piolink.com)         ████████████████████████████████████ 1,456/월
────────────────────────────────────────────────────────────────────────
QueryPie                   ██████████████████████████████ 881/월 ← 2위!
────────────────────────────────────────────────────────────────────────
ManageEngine               ████████████████████████ 684/월
ChakraMax (sinsiway)       █████████████████ 477/월
CyberArk                   █████████████████ 472/월
Teleport                   █████████████ 362/월
SecureOne                  ████████ 251/월
DbSafer                    ░ 0/월
HiWARE                     ░ 0/월
```

### DR 비교 (전체)

| 경쟁사 | DR | 백링크 | 참조도메인 | KR 키워드 | KR 트래픽 |
|--------|-----|--------|-----------|-----------|----------|
| **CyberArk** | 81 | 1.4M | 13,909 | 248 | 472 |
| **ManageEngine** | 81 | 4.1M | 13,862 | 521 | 684 |
| **Teleport** | 73 | 112K | 4,424 | 87 | 362 |
| **QueryPie** | **55** | 3,419 | 569 | 28 | **881** |
| PISO | 50 | 8,472 | 334 | 66 | 1,456 |
| ChakraMax | 28 | 803 | 173 | 69 | 477 |
| DbSafer | 15 | 317 | 65 | 0 | 0 |
| SecureOne | 9 | 495 | 66 | 11 | 251 |
| HiWARE | 0 | 0 | 0 | 0 | 0 |

### 💡 경쟁 분석 인사이트

1. **QueryPie는 한국 로컬 경쟁사 대비 SEO 우위**
   - DR 55로 로컬 경쟁사 중 최고
   - 트래픽 881로 PISO 다음 2위
   - 글로벌 경쟁사(CyberArk, ManageEngine)보다 한국 트래픽 높음

2. **PISO가 유일한 로컬 SEO 경쟁자**
   - 트래픽 1,456으로 1위
   - 하지만 DR 50으로 QueryPie보다 낮음
   - 93%가 브랜드 키워드 트래픽 (파이오링크)

3. **많은 경쟁사가 SEO 미비**
   - DbSafer, HiWARE: 검색 트래픽 제로
   - 한국어 SEO 콘텐츠로 시장 선점 가능

### 경쟁사 제품 시장 인식 (Round 17 웹서치)

**DAC (Database Access Control) 시장:**

| 제품명 | 개발사 | 시장 포지션 | 핵심 인증 |
|--------|--------|------------|-----------|
| **DBSAFER** | 피앤피시큐어 | 🥇 국내 시장 점유율 1위 | CC인증, 금융권 6,000+ 고객 |
| **ChakraMax** | 웨어밸리 | 🥈 아시아 최대 점유율 | CC인증 EAL4, GS인증, Gartner 인정 |
| **PETRA** | 신시웨이 | 코스닥 상장사 | CC인증 EAL3, 1,200+ 고객 |
| DB-i | - | - | - |
| SSDB | - | - | - |

**SAC (Server Access Control) 시장:**

| 제품명 | 개발사 | 시장 포지션 | 핵심 인증 |
|--------|--------|------------|-----------|
| **HiWARE TAM** | 넷앤드 | 🥇 국내 시장 점유율 1위, 조달 1위 | CC인증, GS인증, Gartner PAM 주목 기업 |
| **CyberArk PAM** | CyberArk | 글로벌 PAM 리더 | Gartner Magic Quadrant 리더 |
| **Teleport** | Gravitational | 제로트러스트, K8s 특화 | 오픈소스 기반 |
| Password Manager Pro | ManageEngine | 글로벌 | - |
| IDoperation | - | - | - |
| ESS AdminOne | - | - | - |
| SecureCube Access Check | - | - | - |

**KAC (Kubernetes Access Control) 시장:**

| 제품명 | 개발사 | 시장 포지션 | 핵심 특징 |
|--------|--------|------------|-----------|
| **Teleport** | Gravitational | K8s 접근제어 선도 | Zero Trust, 세션 녹화, RBAC/ABAC |

**WAC (Web Application Control) 시장:**

| 제품명 | 개발사 | 시장 포지션 |
|--------|--------|------------|
| **CyberArk WAC** | CyberArk | 글로벌 |

### 경쟁사 키워드 전략 분석

**PISO (piolink.com) 상위 키워드:**
| 키워드 | 순위 | 볼륨 | 트래픽 |
|--------|------|------|--------|
| 파이오링크 (브랜드) | 1 | 1,600 | **1,358** |
| 보안 컨설팅 | 1 | 200 | 7 |
| 클라우드 네이티브 | 1 | 800 | 5 |
| 취약점 진단 | 7 | 80 | 5 |

**ChakraMax (sinsiway.com) 상위 키워드:**
| 키워드 | 순위 | 볼륨 | 트래픽 |
|--------|------|------|--------|
| 신시웨이 (브랜드) | 1 | 250 | **210** |
| 딥페이크 긍정적 활용 | 2 | 500 | 176 |
| petra | 1 | 600 | 29 |
| db 암호화 솔루션 | 4 | 30 | 4 |

### 💡 QueryPie SEO 기회

1. **제품 키워드 공략**: 경쟁사들은 대부분 브랜드 키워드에 의존 → QueryPie가 "DB 접근제어", "서버 접근제어" 등 제품 키워드 선점 가능
2. **블로그 콘텐츠 전략**: ChakraMax처럼 트렌드 키워드 (딥페이크 등) 활용하면서 브랜드 노출
3. **기술 문서 SEO**: PISO의 "보안 컨설팅", "취약점 진단" 같은 기술 키워드 타겟팅

Sources:
- [DBSAFER - 피앤피시큐어](https://pnpsecure.com/02_1_dbsafer-db/)
- [ChakraMax - 웨어밸리](https://www.dsdata.co.kr/chakramax)
- [PETRA - 신시웨이](https://www.sinsiway.com/kr/solution/solution_petra)
- [HiWARE TAM - 넷앤드](https://www.netand.co.kr/home/HIWARE.php)
- [Teleport - Gravitational](https://goteleport.com/platform/protected-identities/kubernetes/)

---

## 5.9 일본 시장 초대형 SEO 기회 (Round 20 추가)

### 🎯 일본 시장 = 블루오션 확정

Round 19-20 분석 결과, 일본 시장에서 **난이도 0-5의 초대형 키워드**들이 대량 발견되었습니다.

### 핵심 키워드 발굴 결과

**Tier 1: 초대형 기회 (볼륨 1,000+, 난이도 ≤5)**

| 키워드 | 검색량/월 | 난이도 | Traffic Potential | 전략적 의미 |
|--------|----------|--------|-------------------|-------------|
| **ゼロトラスト** (제로트러스트) | 18,000 | 9 | 11,000 | 🔥 초대형, 난이도 낮음 |
| **mfa** | 13,000 | 5 | 21,000 | 인증 핵심 키워드 |
| **sso** | 9,300 | 3 | 3,200 | 블루오션 |
| **内部統制** (내부통제) | 6,800 | 0 | 7,000 | ⭐ 최대 기회 |
| **J-SOX** | 5,000 | 2 | 5,600 | 컴플라이언스 |
| **jsoxとは** | 1,200 | 2 | 5,200 | 교육 콘텐츠 |

**Tier 2: 고가치 기회 (볼륨 100-999, 난이도 ≤5)**

| 키워드 | 검색량/월 | 난이도 | 전략적 의미 |
|--------|----------|--------|-------------|
| **IT統制** | 450 | **0** | ⭐ 완전 블루오션 |
| **内部統制 とは** | 300 | 1 | 교육 콘텐츠 |
| **内部統制 わかりやすく** | 300 | 1 | 초보자 가이드 |
| **内部監査 目的** | 200 | **0** | 감사 관련 |
| **内部統制 具体例** | 150 | **0** | 사례 문서 |
| **j-soxとは わかりやすく** | 150 | **0** | J-SOX 입문 |
| **特権アクセス管理** (PAM) | 100 | **0** | 🎯 QueryPie 핵심 |
| **kubernetes セキュリティ** | 80 | 1 | KAC 관련 |

### SERP 경쟁 분석: "内部統制"

**Position 9**: DR 48 사이트가 7개 백링크만으로 랭킹 → **QueryPie (DR 44)도 진입 가능!**

| 순위 | 도메인 | DR | 백링크 | 트래픽 |
|------|--------|-----|--------|--------|
| 2 | persol-group.co.jp | 76 | 14 | 3,118 |
| 4 | obc.co.jp | 76 | 0 | 664 |
| 5 | fsa.go.jp (정부) | 88 | 28 | 1,150 |
| 6 | biz.moneyforward.com | 84 | 3 | 812 |
| **9** | **aladdin-office.com** | **48** | **7** | **590** |
| 10 | atled.jp | 62 | 14 | 357 |

### SERP 경쟁 분석: "データベース アクセス制御"

**경쟁사 발견:**
- Position 15-16: **Aegis Wall** (DR 11) - 일본 DAC 제품
- Position 25: **PISO** (DR 67) - 한국 경쟁사도 일본 시장 진출

### 일본 시장 진입 전략

```
우선순위별 콘텐츠 로드맵:

Phase 1 (즉시): 난이도 0 키워드
├── 内部統制 입문 가이드
├── IT統制 개요 문서
├── 特権アクセス管理 (PAM) 소개
└── j-soxとは わかりやすく 해설

Phase 2 (1개월): 난이도 1-3 키워드
├── sso 통합 가이드
├── ゼロトラスト 아키텍처
├── kubernetes セキュリティ
└── J-SOX 대응 가이드

Phase 3 (2-3개월): 난이도 5-9 키워드
├── mfa 구현 가이드
└── ゼロトラスト 심화 콘텐츠
```

### 💡 핵심 인사이트

1. **일본 시장은 미개척지**: DR 48 사이트가 볼륨 6,800 키워드에 Top 10 랭킹
2. **QueryPie 적합성 높음**: PAM, 내부통제, 제로트러스트 모두 QueryPie 제품 영역
3. **경쟁사 미비**: Aegis Wall (DR 11), PISO만 확인 → 선점 기회
4. **J-SOX 연계**: 일본 상장사 필수 컴플라이언스 → B2B 수요 확실

---

## 5.10 시장별 키워드 기회 통합 테이블 (Round 21 종합)

### 🇰🇷 한국 시장 핵심 키워드 발굴 (Round 21 추가)

**대발견!** 한국 시장에서 난이도 0-2의 고볼륨 키워드 대량 발견:

| 키워드 | 검색량/월 | 난이도 | 제품 연관 | 전략적 의미 |
|--------|----------|--------|-----------|-------------|
| **sso** | 4,500 | **0** | ACP | 🔥 최대 기회 |
| **mfa** | 2,100 | **0** | ACP | 인증 핵심 |
| **정보보안** | 1,900 | **0** | ACP/AIP | 브랜드 인지도 |
| **ldap** | 1,800 | 2 | ACP | 기술 문서 |
| **클라우드 보안** | 1,700 | **0** | ACP/AIP | 트렌드 키워드 |
| **oauth** | 1,700 | 6 | ACP | 인증 프로토콜 |
| **iam** | 1,300 | 2 | ACP | 정체성 관리 |
| **rbac** | 1,300 | **0** | ACP | 권한 모델 |
| **제로트러스트** | 1,100 | 1 | ACP | 보안 패러다임 |
| **ai 플랫폼** | 1,100 | 1 | AIP | AI 제품 |
| **saml** | 1,000 | 1 | ACP | SSO 프로토콜 |
| **pim** | 1,000 | **0** | ACP | 권한 관리 |
| **pam** | 800 | **0** | ACP | QueryPie 핵심 |
| **데이터 거버넌스** | 600 | **0** | ACP | 데이터 관리 |
| **내부통제** | 350 | **0** | ACP | 컴플라이언스 |
| **데이터 암호화** | 150 | **0** | ACP | 보안 기능 |
| **iam 솔루션** | 100 | **0** | ACP | 제품 키워드 |
| **보안 솔루션** | 100 | **0** | ACP/AIP | 제품 키워드 |
| **감사로그** | 70 | **0** | ACP | 감사 기능 |

### 초저경쟁 키워드 통합 현황 (난이도 ≤5)

| 시장 | 키워드 | 검색량 | 난이도 | 제품 연관 |
|------|--------|--------|--------|-----------|
| 🇯🇵 JP | ゼロトラスト | 18,000 | 9 | ACP/AIP |
| 🇯🇵 JP | mfa | 13,000 | 5 | ACP |
| 🇯🇵 JP | sso | 9,300 | 3 | ACP |
| 🇯🇵 JP | **内部統制** | **6,800** | **0** | ACP |
| 🇯🇵 JP | **J-SOX** | **5,000** | **2** | ACP |
| 🇰🇷 KR | **sso** | **4,500** | **0** | ACP |
| 🇰🇷 KR | ai 에이전트 | 3,600 | 1 | AIP |
| 🇰🇷 KR | **mfa** | **2,100** | **0** | ACP |
| 🇰🇷 KR | **정보보안** | **1,900** | **0** | ACP/AIP |
| 🇰🇷 KR | **ldap** | **1,800** | **2** | ACP |
| 🇰🇷 KR | **클라우드 보안** | **1,700** | **0** | ACP/AIP |
| 🇺🇸 US | mcp server | 1,400 | 0 | AIP |
| 🇰🇷 KR | **iam** | **1,300** | **2** | ACP |
| 🇰🇷 KR | **rbac** | **1,300** | **0** | ACP |
| 🇯🇵 JP | jsoxとは | 1,200 | 2 | ACP |
| 🇰🇷 KR | 제로트러스트 | 1,100 | 1 | ACP |
| 🇰🇷 KR | ai 플랫폼 | 1,100 | 1 | AIP |
| 🇰🇷 KR | **saml** | **1,000** | **1** | ACP |
| 🇰🇷 KR | **pim** | **1,000** | **0** | ACP |
| 🇰🇷 KR | **pam** | **800** | **0** | ACP |
| 🇰🇷 KR | **데이터 거버넌스** | **600** | **0** | ACP |
| 🇯🇵 JP | IT統制 | 450 | **0** | ACP |
| 🇰🇷 KR | **내부통제** | **350** | **0** | ACP |
| 🇺🇸 US | ai access control | 250 | 5 | AIP |
| 🇺🇸 US | database access management | 200 | **0** | ACP |
| 🇯🇵 JP | 特権アクセス管理 | 100 | **0** | ACP |
| 🇯🇵 JP | kubernetes セキュリティ | 80 | 1 | ACP |
| 🇰🇷 KR | 쿠버네티스 보안 | 30 | **0** | ACP |

### 시장별 총 기회 규모 (Round 21 업데이트)

| 시장 | 발굴 키워드 수 | 월간 잠재 트래픽 | 평균 난이도 | 우선순위 |
|------|---------------|-----------------|-------------|----------|
| 🇯🇵 **일본** | 15+ | **50,000+** | 2.1 | 🥇 최우선 |
| 🇰🇷 **한국** | **25+** | **22,000+** | **0.8** | 🥇 **최우선 (동급)** |
| 🇺🇸 미국 | 10+ | 3,000+ | 3.2 | 🥉 |

### 🇰🇷 한국 시장 SERP 경쟁 분석 (Round 22 추가)

**"sso" SERP (4,500/월, 난이도 0):**

| 순위 | 도메인 | DR | 백링크 | 트래픽 | 분석 |
|------|--------|-----|--------|--------|------|
| 2 | aws.amazon.com | 96 | 15 | 2,384 | 글로벌 기업 |
| 4 | ibm.com | 92 | 0 | 386 | 글로벌 기업 |
| **5** | **content.rview.com** | **47** | **0** | **192** | ⭐ QueryPie 진입 가능 |
| 6 | fortinet.com | 89 | 4 | 177 | 보안 기업 |
| 9 | pops.megazone.com | 74 | 0 | 42 | 한국 기업 |
| **11** | **smileshark.kr** | **44** | **0** | **5** | ⭐ DR=QueryPie |

**"mfa" SERP (2,100/월, 난이도 0):**

| 순위 | 도메인 | DR | 백링크 | 트래픽 | 분석 |
|------|--------|-----|--------|--------|------|
| 2 | aws.amazon.com | 96 | 13 | 671 | 글로벌 기업 |
| **3** | **paloaltonetworks.co.kr** | **48** | **0** | **160** | ⭐ QueryPie 진입 가능 |
| 5 | akamai.com | 89 | 1 | 293 | 글로벌 기업 |
| **23** | **pentasecurity.co.kr** | **52** | **0** | **22** | 한국 보안 기업 |

**"클라우드 보안" SERP (1,700/월, 난이도 0):**

| 순위 | 도메인 | DR | 백링크 | 트래픽 | 분석 |
|------|--------|-----|--------|--------|------|
| 2 | ibm.com | 92 | 1 | 655 | 글로벌 기업 |
| 4 | cloud.google.com | 99 | 1 | 231 | 글로벌 기업 |
| **5** | **ncsc.go.kr** | **55** | **5** | **154** | ⭐ DR=QueryPie |
| 6 | microsoft.com | 96 | 2 | 341 | 글로벌 기업 |
| **8** | **samsungsds.com** | **73** | **0** | **74** | 한국 기업 |

### 💡 SERP 분석 핵심 인사이트

1. **SSO Top 10 진입 현실적**: DR 47 사이트가 0개 백링크로 5위 랭킹
2. **MFA Top 5 도전 가능**: DR 48 사이트가 0개 백링크로 3위
3. **클라우드 보안 정부 수준**: ncsc.go.kr (DR 55)가 5위 - QueryPie 동급
4. **한국 기업 경쟁 약함**: 대부분 글로벌 기업 콘텐츠가 상위 랭킹

### 💡 Round 21-22 핵심 인사이트

1. **한국 시장 재평가 필요**: 난이도 0 키워드만 **15,000+** 월간 검색량
2. **SSO/MFA가 최대 기회**: 한국에서 sso 4,500, mfa 2,100 (둘 다 난이도 0)
3. **기술 키워드 선점 가능**: ldap, rbac, saml, pim, pam 모두 난이도 0-2
4. **일본-한국 동시 공략 권장**: 두 시장 모두 블루오션, 콘텐츠 현지화로 시너지
5. **SERP 진입 장벽 낮음**: DR 44-55 사이트들이 Top 10 랭킹 중

### 🇺🇸 미국 시장 추가 키워드 발굴 (Round 23 추가)

**Database/Data Access 관련 (난이도 ≤5):**

| 키워드 | 검색량/월 | 난이도 | 전략적 의미 |
|--------|----------|--------|-------------|
| **compliance automation** | 1,400 | 5 | 🔥 컴플라이언스 자동화 |
| **data governance platform** | 800 | 6 | 데이터 거버넌스 |
| **data access control** | 500 | 5 | DAC 핵심 키워드 |
| **pim vs pam** | 250 | 2 | 교육 콘텐츠 기회 |
| **data access management** | 250 | 2 | 데이터 접근 관리 |
| **open source pam** | 200 | 7 | 오픈소스 비교 |
| **cyberark endpoint privilege manager** | 200 | **0** | ⭐ 경쟁사 키워드 |
| **database access management** | 150 | **0** | ⭐ DAC 핵심 |
| **data access control system** | 150 | 2 | 시스템 키워드 |
| **server access management** | 100 | 4 | SAC 핵심 |
| **data access controls** | 100 | 2 | 복수형 변형 |
| **access control database** | 50 | **0** | ⭐ DAC 변형 |
| **pam audit** | 40 | 1 | 감사 기능 |
| **database security audit** | 20 | 1 | 감사 기능 |

### 전략적 권고 (Round 23 업데이트)

1. **한국 시장 즉시 강화**: SSO, MFA, 클라우드 보안 콘텐츠 최우선
2. **일본 시장 동시 진입**: 内部統制, J-SOX 콘텐츠 생성
3. **기술 문서 SEO 최적화**: LDAP, RBAC, SAML 등 프로토콜 문서 강화
4. **미국 시장 확대 전략**:
   - "compliance automation" (1,400/월) - 컴플라이언스 자동화 가이드
   - "data governance platform" (800/월) - 플랫폼 비교 콘텐츠
   - "cyberark endpoint privilege manager" (200/월, 난이도 0) - 경쟁사 대안 콘텐츠
   - "database access management" (150/월, 난이도 0) - 핵심 제품 키워드

---

## 5.11 MCP 시장 기회 분석 (Round 24 추가)

### MCP 키워드 현황

| 키워드 | 검색량/월 | 난이도 | 전략적 분석 |
|--------|----------|--------|-------------|
| **model context protocol** | 24,000 | 79 | 🔥 초대형 시장 (장기 목표) |
| **mcp protocol** | 6,000 | 80 | 대형 시장 |
| **claude mcp** | 4,600 | 66 | 진입 가능 구간 |
| **anthropic mcp** | 3,800 | - | 브랜드 연관 |
| **mcp server** | 1,400 | 0 | ⭐ AIP 핵심 기회 |
| **ai agent framework** | 700 | 45 | 중간 난이도 |
| **ai access control** | 250 | 5 | ⭐ AIP 특화 |

### MCP Server SERP 경쟁 분석

| 순위 | 도메인 | DR | 백링크 | 트래픽 | 분석 |
|------|--------|-----|--------|--------|------|
| 2 | modelcontextprotocol.io | 87 | 233,505 | 65,760 | 공식 사이트 |
| 4 | github.com | 96 | 27,315 | 8,826 | 공식 레포 |
| **5** | **k2view.com** | **66** | **8** | **5,400** | ⭐ **진입 벤치마크** |
| **7** | **mcpservers.org** | **67** | **1,549** | **6,021** | ⭐ **진입 벤치마크** |
| 12 | anthropic.com | 90 | 21,736 | 12,696 | 공식 발표 |
| **14** | **glama.ai** | **69** | **2,516** | **667** | MCP 디렉토리 |

### 💡 MCP 시장 핵심 인사이트

1. **DR 66-69 사이트가 Top 10 랭킹 중**: k2view, mcpservers.org, glama.ai
2. **aip-docs (DR 44) 진입 전략**: MCP 보안 특화 콘텐츠로 차별화
3. **"mcp server" 키워드 (1,400/월, 난이도 0)**: 즉시 공략 가능
4. **AIP USP 연계**: "MCP Security", "AI Agent Access Control" 포지셔닝

### AIP 문서 사이트 MCP 콘텐츠 전략

```
aip-docs.app.querypie.com MCP 콘텐츠 로드맵:

Phase 1 (즉시): 난이도 0-5 키워드
├── "What is MCP Server" 가이드 (1,400/월)
├── "MCP Security Best Practices" (신규)
├── "AI Access Control with MCP" (250/월)
└── "MCP Server Authentication" (신규)

Phase 2 (1개월): 난이도 5-15 키워드
├── "MCP vs API" 비교 가이드
├── "Building Secure MCP Servers"
├── "MCP Server Monitoring"
└── "AI Agent Security Framework"

Phase 3 (2-3개월): 롱테일 + 브랜드
├── "QueryPie MCP Integration"
├── "Enterprise MCP Security"
└── "MCP Compliance Guide"
```

---

## 5.12 Round 1-24 최종 종합 (Executive Summary)

### 📊 분석 요약

| 항목 | 내용 |
|------|------|
| 총 분석 라운드 | 24 |
| 분석 기간 | 2026-02-02 ~ 2026-02-03 |
| 분석 도구 | Ahrefs API, GSC, GA |
| 발굴 키워드 수 | **60+** |
| 총 월간 검색량 | **100,000+** |

### 🎯 시장별 최종 우선순위

| 순위 | 시장 | 키워드 수 | 월간 검색량 | 평균 난이도 | 투자 권장 |
|------|------|----------|------------|-------------|----------|
| 🥇 | **일본** | 15+ | 50,000+ | 2.1 | 즉시 진입 |
| 🥇 | **한국** | 25+ | 22,000+ | 0.8 | 즉시 강화 |
| 🥉 | **미국** | 20+ | 30,000+ | 5.2 | 니치 공략 |

### 🔥 Top 10 즉시 실행 키워드

| # | 시장 | 키워드 | 검색량 | 난이도 | 담당 도메인 |
|---|------|--------|--------|--------|-------------|
| 1 | 🇰🇷 | sso | 4,500 | **0** | docs.querypie.com |
| 2 | 🇯🇵 | 内部統制 | 6,800 | **0** | www.querypie.com |
| 3 | 🇯🇵 | J-SOX | 5,000 | 2 | www.querypie.com |
| 4 | 🇰🇷 | mfa | 2,100 | **0** | docs.querypie.com |
| 5 | 🇰🇷 | 클라우드 보안 | 1,700 | **0** | www.querypie.com |
| 6 | 🇺🇸 | mcp server | 1,400 | **0** | aip-docs |
| 7 | 🇺🇸 | compliance automation | 1,400 | 5 | www.querypie.com |
| 8 | 🇰🇷 | rbac | 1,300 | **0** | docs.querypie.com |
| 9 | 🇰🇷 | iam | 1,300 | 2 | docs.querypie.com |
| 10 | 🇰🇷 | 제로트러스트 | 1,100 | 1 | www.querypie.com |

### 🚀 도메인별 콘텐츠 액션 플랜

**www.querypie.com (마케팅)**
- 일본어 랜딩: 内部統制, J-SOX, ゼロトラスト
- 한국어 랜딩: 제로트러스트, 클라우드 보안, AI 플랫폼
- 영어 랜딩: compliance automation, data governance

**docs.querypie.com (ACP 문서)**
- 한국어: SSO, MFA, LDAP, RBAC, SAML, PAM 가이드
- 영어: database access management, server access control
- 일본어: 特権アクセス管理, IT統制

**aip-docs.app.querypie.com (AIP 문서)**
- MCP Server 시리즈: What is MCP, MCP Security, MCP Authentication
- AI Security: AI Access Control, AI Agent Framework
- 한국어: ai 에이전트, ai 플랫폼

### ⚠️ 긴급 기술 조치

1. **app.querypie.com HTTP HEAD 405 수정** → 인덱싱 시작
2. **www.querypie.com /chat/publication noindex** → 브랜드 희석 방지
3. **sitemap.xml 오류 수정** → 크롤링 정상화

---

## 5.13 Round 29 최신 Ahrefs 데이터 분석 (2026-02-03 업데이트)

### 📊 도메인별 현재 상태 (2026-01-31 기준)

| 도메인 | 유기검색 키워드 | 월 트래픽 | 트래픽 가치 | 상태 |
|--------|---------------|----------|------------|------|
| **www.querypie.com** | 42 | 952 | $486/월 | 🟢 성장 중 |
| docs.querypie.com | 8 | 20 | $11/월 | ⚠️ 개선 필요 |
| aip-docs.app.querypie.com | 4 | 0 | $0 | ⚠️ 개선 필요 |
| app.querypie.com | 4 | 0 | $0 | 🔴 인덱싱 실패 |

### 🇺🇸 미국 시장 현재 키워드 순위 (www.querypie.com)

| 키워드 | 순위 | 월 트래픽 | 검색량 | 난이도 | CPC |
|--------|------|----------|--------|--------|-----|
| querypie | 1 | 88 | 80 | 0 | - |
| q pie | 8 | 1 | 20 | 51 | - |
| aws inspector agent | 11 | 1 | 50 | 5 | - |
| multi cloud kubernetes | 27 | 0 | 300 | 2 | $4.06 |
| healthcare data security | 72 | 0 | 1,500 | 11 | $0.47 |
| pam solution | 92 | 0 | 1,200 | 31 | $0.47 |

### 🇰🇷 한국 시장 현재 키워드 순위

| 키워드 | 순위 | 월 트래픽 | 검색량 | 난이도 | 분석 |
|--------|------|----------|--------|--------|------|
| **쿼리파이** | 1 | 410 | 400 | 0 | 브랜드 키워드 |
| **querypie** | 1 | 392 | 400 | 0 | 브랜드 키워드 |
| chequer | 1 | 38 | 40 | 0 | 회사명 |
| PAM solutions | 7 | 1 | 20 | 5 | **핵심 제품** |
| zero trust | 39 | 0 | 800 | 2 | **기회!** |

### 🔥 신규 발굴 고가치 키워드 기회 (Round 29)

**미국 시장 - 대형 기회 발견!**

| 키워드 | 검색량 | 난이도 | 트래픽 잠재력 | CPC | 전략 |
|--------|--------|--------|--------------|-----|------|
| **cloud data security** | 2,200 | **5** | **4,700** | $0.50 | 🔥 최우선 타겟 |
| **data access governance** | 450 | **1** | 150 | **$8.00** | 고가치 키워드 |
| **database access control** | 90 | **2** | 70 | $6.00 | 핵심 제품 |
| llm tools | 900 | 7 | 100 | $3.00 | AIP 연계 |

**한국 시장 - 즉시 공략 가능**

| 키워드 | 검색량 | 난이도 | 트래픽 잠재력 | 분석 |
|--------|--------|--------|--------------|------|
| **클라우드 보안** | 1,700 | **0** | 500 | 🔥 즉시 1위 가능 |
| **제로 트러스트** | 600 | **0** | 500 | 즉시 1위 가능 |
| 데이터베이스 보안 | 30 | **0** | 10 | 롱테일 |

**일본 시장 - 초대형 기회 확인!**

| 키워드 | 검색량 | 난이도 | 트래픽 잠재력 | CPC | 분석 |
|--------|--------|--------|--------------|-----|------|
| **ゼロトラスト** | **18,000** | 9 | **24,000** | $1.10 | 🔥 최대 기회! |
| クラウドセキュリティ | 2,800 | **1** | 2,000 | $0.15 | 즉시 공략 |
| データガバナンス | 1,500 | 5 | 150 | $0.70 | 가치 키워드 |
| **特権アクセス管理** | 100 | **0** | **1,100** | $3.00 | PAM 핵심 |
| データベースセキュリティ | 100 | **0** | 70 | $0.20 | 즉시 공략 |

### 📈 MCP 시장 최신 동향 (2026-01-31)

| 키워드 | 검색량 | 난이도 | 트래픽 잠재력 | 전략적 분석 |
|--------|--------|--------|--------------|-------------|
| **mcp server** | **46,000** | 81 | 66,000 | 🔥 시장 폭발 (+3,200% from 1,400) |
| model context protocol | 24,000 | 79 | 66,000 | 대형 시장 |
| ai agent | 26,000 | 77 | 19,000 | 고경쟁 |
| ai automation | 7,600 | 57 | 3,500 | 중간 경쟁 |
| **llm tools** | 900 | **7** | 100 | ⭐ 진입 기회 |

### 💡 Round 29 핵심 인사이트

1. **MCP 시장 폭발적 성장**: "mcp server" 검색량이 1,400 → 46,000으로 3,200% 증가
2. **"cloud data security" 대형 기회**: 볼륨 2,200, 난이도 5, 트래픽 잠재력 4,700
3. **일본 "ゼロトラスト" 최대 기회**: 볼륨 18,000, 트래픽 잠재력 24,000
4. **한국 "클라우드 보안" 즉시 공략**: 볼륨 1,700, 난이도 0
5. **www.querypie.com 브랜드 의존도 높음**: US 트래픽 88% 브랜드 키워드

### 🎯 Round 29 추가 액션 아이템

| 우선순위 | 시장 | 키워드 | 액션 | 예상 효과 |
|---------|------|--------|------|-----------|
| 🔴 긴급 | 🇺🇸 | cloud data security | 전용 랜딩 페이지 생성 | +200 트래픽/월 |
| 🔴 긴급 | 🇰🇷 | 클라우드 보안 | 한국어 가이드 생성 | +100 트래픽/월 |
| 🔴 긴급 | 🇯🇵 | クラウドセキュリティ | 일본어 랜딩 페이지 | +150 트래픽/월 |
| 🟡 높음 | 🇺🇸 | data access governance | 심층 가이드 작성 | +30 트래픽/월 |
| 🟡 높음 | 🇯🇵 | 特権アクセス管理 | PAM 일본어 페이지 | +50 트래픽/월 |
| 🟢 중요 | 🇺🇸 | llm tools | AIP 기술 문서 확장 | +20 트래픽/월 |

---

## 5.14 Round 30 SERP 경쟁 분석 (2026-02-03)

### 🎯 "cloud data security" (US, 2,200/월, 난이도 5)

**QueryPie 진입 가능성: ⭐⭐⭐⭐ (높음)**

| 순위 | 도메인 | DR | 백링크 | 트래픽 | 분석 |
|------|--------|-----|--------|--------|------|
| 2 | cloud.google.com | 99 | 94 | 4,594 | 대기업 |
| 3 | wiz.io | 83 | 15 | 780 | 클라우드 보안 |
| 4 | crowdstrike.com | 86 | 25 | 515 | 사이버 보안 |
| **5** | **sentra.io** | **58** | 53 | 595 | ⭐ **QueryPie (DR 55) 벤치마크!** |
| 8 | microsoft.com | 96 | 10 | 1,004 | 대기업 |
| **20** | **upwind.io** | **63** | 0 | 9 | 신규 진입 |

**인사이트**: DR 58 사이트가 Position 5! QueryPie (DR 55)도 Top 10 진입 가능

### 🎯 "data access governance" (US, 450/월, 난이도 1)

**QueryPie 진입 가능성: ⭐⭐⭐⭐⭐ (매우 높음)**

| 순위 | 도메인 | DR | 백링크 | 트래픽 | 분석 |
|------|--------|-----|--------|--------|------|
| 2 | saviynt.com | 70 | 6 | 345 | IAM 솔루션 |
| **7** | **concentric.ai** | **66** | **0** | 72 | ⭐ **백링크 0으로 랭킹!** |
| 9 | alation.com | 73 | 2 | 116 | 데이터 카탈로그 |
| 10 | immuta.com | 71 | 2 | 99 | 데이터 보안 |
| 11 | zluri.com | 70 | 1 | 305 | SaaS 관리 |

**인사이트**: DR 66 사이트가 백링크 0개로 Top 10! QueryPie는 콘텐츠만으로 진입 가능

### 🎯 "ゼロトラスト" (JP, 18,000/월, 난이도 9)

**QueryPie 진입 가능성: ⭐⭐⭐⭐ (높음)**

| 순위 | 도메인 | DR | 백링크 | 트래픽 | 분석 |
|------|--------|-----|--------|--------|------|
| 3 | ntt.com | 83 | 33 | 6,115 | 대기업 |
| **4** | **ascentech.co.jp** | **56** | 6 | 1,157 | ⭐ **QueryPie (DR 55) 레벨!** |
| 6 | hitachi-solutions.co.jp | 72 | 7 | 1,117 | 대기업 |
| **10** | **skyseaclientview.net** | **60** | 2 | 80 | 중소 |
| **15** | **quest.co.jp** | **46** | - | 180 | ⭐ **DR 46도 랭킹!** |

**인사이트**: DR 46-56 사이트들이 Top 15 랭킹! 18,000/월 시장에서 QueryPie 진입 현실적

### 💡 Round 30 핵심 인사이트

1. **"cloud data security"**: DR 58 사이트가 Position 5 → QueryPie (DR 55) Top 10 가능
2. **"data access governance"**: 백링크 0개로 Top 10 진입 사례 → 콘텐츠 품질만으로 승부 가능
3. **"ゼロトラスト"**: DR 46 사이트도 Top 15 → 일본 시장 진입 장벽 낮음
4. **공통점**: 중소 DR (50-70) 사이트들도 품질 콘텐츠로 대기업과 경쟁 중

### 🚀 Round 30 추가 액션

| 우선순위 | 키워드 | 현재 경쟁 | QueryPie 액션 |
|---------|--------|----------|---------------|
| 🔴 최우선 | data access governance | DR 66, 0 백링크 Top 10 | 심층 가이드 작성 |
| 🔴 최우선 | ゼロトラスト | DR 56, 6 백링크 Top 5 | 일본어 랜딩 페이지 |
| 🟡 높음 | cloud data security | DR 58, 53 백링크 Top 5 | 콘텐츠 + 백링크 확보 |

---

## 5.15 Round 31 관련 키워드 확장 분석 (2026-02-03)

### 🔥 신규 발굴 고가치 키워드 (US 시장)

**Tier 1: 최고 우선순위 (난이도 ≤5)**

| 키워드 | 검색량/월 | 난이도 | CPC | 전략적 의미 |
|--------|----------|--------|-----|-------------|
| **access governance** | **900** | **0** | $0.45 | 🔥 **새로운 대형 기회!** |
| data access control | 500 | 5 | $4.00 | ACP 핵심 |
| cloud database security | 500 | 5 | $0.80 | DB 보안 |
| cloud security and privacy | 400 | **1** | $1.00 | 프라이버시 |
| data security in cloud | 400 | 9 | $0.50 | 변형 키워드 |

**Tier 2: 높은 우선순위 (난이도 6-15)**

| 키워드 | 검색량/월 | 난이도 | CPC | 전략적 의미 |
|--------|----------|--------|-----|-------------|
| data security in cloud computing | 1,000 | 12 | $0.50 | 대형 기회 |
| data security in the cloud | 600 | 12 | $0.50 | 변형 키워드 |
| cloud storage security | 500 | 14 | $0.50 | 스토리지 |
| what is database security | 450 | 7 | $0.15 | 교육 콘텐츠 |

### 🇰🇷 신규 발굴 한국 키워드 (난이도 0-2)

| 키워드 | 검색량/월 | 난이도 | CPC | 전략적 의미 |
|--------|----------|--------|-----|-------------|
| **csap** | **450** | **0** | $0.60 | 🔥 클라우드 보안 인증 |
| **csap 인증** | 150 | **0** | $0.25 | 인증 관련 |
| **데이터 보안** | 150 | **0** | $0.90 | 핵심 키워드 |
| cloud security | 600 | 2 | $0.25 | 영어 검색 |
| 클라우드 보안 솔루션 | 70 | **0** | $1.30 | 제품 키워드 |
| 데이터베이스 보안 | 30 | **0** | $0.20 | DB 관련 |

### 💡 Round 31 핵심 인사이트

1. **"access governance" (900/월, 난이도 0)**: 이전에 발견하지 못한 대형 기회!
2. **"csap" (450/월, 난이도 0)**: 한국 클라우드 보안 인증 관련 키워드
3. **난이도 0 키워드 추가 발굴**: 미국 4개, 한국 6개

### 🎯 Round 31 추가 콘텐츠 계획

| 키워드 | 도메인 | 콘텐츠 유형 | 예상 트래픽 |
|--------|--------|------------|------------|
| access governance | www.querypie.com | 가이드 페이지 | +80-200/월 |
| csap / csap 인증 | www.querypie.com | 인증 가이드 | +40-100/월 |
| data access control | docs.querypie.com | 기술 문서 | +30-80/월 |
| cloud database security | docs.querypie.com | DB 보안 가이드 | +30-80/월 |

**Round 31 발굴 총 잠재 트래픽: +180-460/월**

---

## 5.16 Round 32 성장 트렌드 분석 (2026-02-03)

### 📈 www.querypie.com 참조 도메인 성장 추이

| 기간 | 참조 도메인 | 변화 | 분석 |
|------|------------|------|------|
| 2025-01 | 350 | - | 기준점 |
| 2025-05 | 333 | -17 | 소폭 감소 |
| 2025-08 | 355 | +22 | 회복 |
| 2025-09 | 408 | +53 | 급성장 시작 |
| 2025-10 | 454 | +46 | 지속 성장 |
| 2025-12 | 566 | +112 | 🔥 **급증** |
| 2026-01 | 567 | +1 | 안정화 |

**연간 성장률: +62%** (350 → 567)

### 📊 키워드 순위 분포 변화

| 기간 | Top 3 | Top 4-10 | 총 (Top 10) | 변화 |
|------|-------|----------|-------------|------|
| 2025-01 | 3 | 6 | 9 | 기준 |
| 2025-06 | 4 | 4 | 8 | -1 |
| 2025-09 | 6 | 10 | 16 | **+7** |
| 2025-11 | 8 | 13 | 21 | **+5** |
| 2026-01 | 8 | 13 | 21 | 유지 |

**Top 10 키워드: +133%** (9 → 21)

### 💰 유기검색 트래픽 및 가치 추이

| 기간 | 월 트래픽 | 트래픽 가치 | 분석 |
|------|----------|------------|------|
| 2025-01 | 497 | $269 | 기준점 |
| 2025-02 | **1,170** | $631 | 🔥 피크 |
| 2025-05 | 914 | $469 | 안정 |
| 2025-09 | **1,094** | $580 | 2차 피크 |
| 2025-12 | 758 | $376 | 연말 감소 |
| 2026-01 | 909 | $467 | 회복 중 |

**평균 월 트래픽: ~900** / **평균 월 가치: ~$480**

### 🎯 Round 32 성장 인사이트

1. **참조 도메인 급성장**: 2025년 12월 대폭 증가 (+177 in 4개월)
2. **Top 10 키워드 2배 이상 증가**: 9개 → 21개 (+133%)
3. **트래픽 안정권**: 월 900-1,100 범위에서 안정적 유지
4. **성장 잠재력**: 참조 도메인 증가 → 향후 순위/트래픽 상승 예상

### 📋 Round 29-32 최종 요약

| 라운드 | 핵심 발견 | 비즈니스 임팩트 |
|--------|----------|----------------|
| R29 | MCP 시장 +3,186% 폭발 | aip-docs 긴급 콘텐츠 필요 |
| R29 | cloud data security (2,200, 난이도 5) | 대형 US 기회 |
| R30 | DR 58 사이트 Top 5 확인 | QueryPie 진입 가능 검증 |
| R30 | DR 46 사이트 일본 Top 15 | 일본 시장 진입 장벽 낮음 |
| R31 | access governance (900, 난이도 0) | **신규 대형 발굴!** |
| R31 | csap (450, 난이도 0) | 한국 인증 키워드 |
| R32 | 참조 도메인 +62% 성장 | 순위 상승 기반 |
| R32 | Top 10 키워드 +133% | SEO 효과 확인 |

---

## 5.17 Round 33 Data Governance 키워드 심층 분석 (2026-02-03)

### 🔥 Data Governance 롱테일 키워드 발굴 (US 시장)

**Tier 1: 최고 우선순위 (난이도 0-5)**

| 키워드 | 검색량/월 | 난이도 | CPC | 트래픽 잠재력 | 전략 |
|--------|----------|--------|-----|--------------|------|
| **enterprise data governance** | 700 | **0** | $5.00 | 400 | 🔥 즉시 공략! |
| **data governance tool** | 700 | 4 | $0.50 | **2,300** | 제품 비교 |
| **master data governance** | 700 | **1** | $0.10 | 350 | MDM 연계 |
| **data governance consulting** | 600 | **1** | $0.50 | 800 | 서비스 소개 |
| sap master data governance | 500 | 3 | $6.00 | 1,600 | SAP 연동 |
| data governance platforms | 300 | 4 | $15.00 | **2,100** | 플랫폼 비교 |
| **PAM best practices** | 300 | **1** | $0.45 | 250 | PAM 가이드 |
| data governance vs data management | 450 | 3 | $2.50 | 1,700 | 비교 가이드 |

**Tier 2: 높은 우선순위 (난이도 6-10)**

| 키워드 | 검색량/월 | 난이도 | 트래픽 잠재력 | 전략 |
|--------|----------|--------|--------------|------|
| data governance tools | 2,900 | 7 | 1,800 | 도구 비교 가이드 |
| data governance software | 1,900 | 8 | 2,300 | 소프트웨어 비교 |
| data governance and management | 1,800 | 8 | 1,800 | 개념 설명 |
| data governance strategy | 1,000 | 7 | 700 | 전략 가이드 |
| data governance platform | 800 | 6 | 2,100 | 플랫폼 소개 |

### 💡 Round 33 핵심 인사이트

1. **"enterprise data governance" (700/월, 난이도 0)**: B2B 타겟 완벽 적합
2. **"data governance tool/platforms"**: 트래픽 잠재력 2,000+로 높은 가치
3. **PAM best practices (300/월, 난이도 1)**: QueryPie 핵심 제품 연계
4. **Data Governance 영역**: QueryPie ACP와 직접 연관되는 키워드 다수

### 🎯 Round 33 콘텐츠 로드맵

| 우선순위 | 키워드 | 콘텐츠 유형 | 예상 트래픽 |
|---------|--------|------------|------------|
| 🔴 긴급 | enterprise data governance | 가이드 페이지 | +50-150/월 |
| 🔴 긴급 | PAM best practices | PAM 가이드 | +30-80/월 |
| 🟡 높음 | data governance tool | 비교 가이드 | +50-100/월 |
| 🟡 높음 | data governance platform | 플랫폼 소개 | +40-100/월 |
| 🟢 중요 | data governance strategy | 전략 가이드 | +30-70/월 |

**Round 33 발굴 총 잠재 트래픽: +200-500/월**

---

## 5.18 Round 34 일본 시장 대규모 키워드 발굴 (2026-02-03)

### 🇯🇵 일본 시장 = SEO 블루오션 확정!

**난이도 0 키워드가 대량 발굴됨. 일본 시장은 QueryPie의 최대 성장 기회!**

### 🔥 ゼロトラスト (Zero Trust) 계열 (난이도 0-5)

| 키워드 | 검색량/월 | 난이도 | 트래픽 잠재력 | 전략 |
|--------|----------|--------|--------------|------|
| **ゼロトラストネットワーク** | 800 | **0** | 1,400 | 🔥 즉시 공략 |
| **ismsクラウドセキュリティ認証** | 500 | **0** | 900 | ISMS 인증 가이드 |
| ゼロトラストとは | 5,400 | 5 | 6,100 | 입문 가이드 |
| ゼロトラストアーキテクチャ | 500 | **1** | 100 | 아키텍처 가이드 |
| ゼロトラスト わかりやすく | 500 | **1** | 1,100 | 쉬운 설명 |
| **sase ゼロトラスト 違い** | 200 | **0** | 400 | 비교 가이드 |
| **ゼロトラストネットワークとは** | 200 | **0** | 1,300 | 네트워크 가이드 |
| **パブリッククラウド セキュリティ** | 200 | **0** | 60 | 퍼블릭 클라우드 |
| **クラウドセキュリティ認証** | 150 | **0** | 1,000 | 인증 가이드 |
| **データガバナンス フレームワーク** | 150 | **0** | 50 | 프레임워크 |

### 🔥 内部統制/J-SOX 계열 (난이도 0-2)

| 키워드 | 검색량/월 | 난이도 | 트래픽 잠재력 | 전략 |
|--------|----------|--------|--------------|------|
| **内部統制** | **6,800** | **0** | 3,100 | 🔥🔥 최우선! |
| **内部統制とは** | **5,200** | **1** | 3,100 | 입문 가이드 |
| **j-sox** | **5,000** | **2** | 5,600 | J-SOX 가이드 |
| j-soxとは | 1,400 | 2 | 5,600 | J-SOX 설명 |
| **内部統制報告書** | 1,000 | **0** | 350 | 보고서 가이드 |
| **内部統制 3点セット** | 500 | **0** | 500 | 3점 세트 설명 |
| **内部統制システム** | 450 | **0** | 450 | 시스템 가이드 |
| **it統制** | 450 | **0** | 100 | IT 통제 |
| **j-sox法** | 350 | **0** | 5,600 | J-SOX 법률 |
| **j-sox 3点セット** | 300 | **0** | 600 | J-SOX 3점 |
| **it全般統制** | 250 | **0** | 1,000 | IT 전반 통제 |
| **内部統制 ガバナンス 違い** | 250 | **0** | 100 | 차이점 비교 |

### 💡 Round 34 핵심 인사이트

1. **내부통제/J-SOX 키워드**: 총 검색량 **20,000+/월**, 평균 난이도 **0.5**
2. **제로트러스트 키워드**: 총 검색량 **30,000+/월**, 평균 난이도 **3**
3. **일본 시장 총 기회**: **50,000+/월** 검색량, 대부분 난이도 0-5

### 📊 일본 시장 키워드 총계 (Round 34)

| 카테고리 | 키워드 수 | 총 검색량 | 평균 난이도 | 우선순위 |
|---------|----------|----------|-------------|----------|
| 内部統制/J-SOX | 12+ | 20,000+ | **0.5** | 🥇 최우선 |
| ゼロトラスト | 10+ | 30,000+ | 3 | 🥇 최우선 |
| クラウドセキュリティ | 5+ | 6,000+ | 1 | 🥇 최우선 |
| **총계** | **27+** | **56,000+** | **1.5** | 🇯🇵 **집중 투자** |

### 🎯 일본 시장 콘텐츠 로드맵

**Phase 1 (즉시): 난이도 0 키워드 (15개)**
- 内部統制 종합 가이드
- J-SOX 컴플라이언스 가이드
- ゼロトラストネットワーク 입문
- IT統制/IT全般統制 가이드

**Phase 2 (1개월): 난이도 1-2 키워드 (8개)**
- 内部統制とは 설명 페이지
- J-SOXとは 설명 페이지
- ゼロトラスト わかりやすく

**Phase 3 (2개월): 난이도 5-9 키워드 (4개)**
- ゼロトラストとは (5,400/월)
- ゼロトラスト (18,000/월)

### 🚀 예상 효과 (일본 시장)

| 단계 | 타겟 키워드 수 | 예상 트래픽 | 기간 |
|------|---------------|------------|------|
| Phase 1 | 15개 | +500-1,500/월 | 1개월 |
| Phase 2 | 8개 | +300-800/월 | 2개월 |
| Phase 3 | 4개 | +500-2,000/월 | 3-6개월 |
| **총계** | **27개** | **+1,300-4,300/월** | 6개월 |

**🇯🇵 일본 시장 SEO는 QueryPie의 최대 성장 기회입니다!**

---

## 5.19 Round 35 한국 시장 추가 키워드 발굴 (2026-02-03)

### 🇰🇷 한국 시장 신규 발굴 키워드

**Tier 1: 대형 기회 (난이도 0-2)**

| 키워드 | 검색량/월 | 난이도 | CPC | 트래픽 잠재력 | 전략 |
|--------|----------|--------|-----|--------------|------|
| **컴플라이언스** | **3,100** | **0** | $0.20 | 700 | 🔥🔥 최대 기회! |
| **컴플라이언스 뜻** | 700 | **0** | $0.10 | 700 | 교육 콘텐츠 |
| 관계형 데이터베이스 | 600 | 4 | $0.25 | 800 | 기술 문서 |
| 오라클 데이터베이스 | 400 | **1** | $0.70 | 500 | Oracle 연동 |
| **내부통제** | 350 | **0** | $0.15 | 150 | 컴플라이언스 |
| 데이터베이스 스키마 | 300 | 2 | $0.15 | 700 | 기술 문서 |
| **벡터 데이터베이스** | 300 | **1** | - | 700 | 🔥 AI 트렌드! |

**Tier 2: 제로트러스트 관련 (난이도 0-1)**

| 키워드 | 검색량/월 | 난이도 | 트래픽 잠재력 | 전략 |
|--------|----------|--------|--------------|------|
| 제로트러스트 | 1,100 | 1 | 250 | 메인 가이드 |
| **제로트러스트 아키텍처** | 90 | **0** | 250 | 아키텍처 |
| **클라우드보안** | 80 | **0** | 500 | 클라우드 |
| 제로트러스트 보안 | 60 | 1 | 600 | 보안 가이드 |
| **제로트러스트 솔루션** | 40 | **0** | - | 솔루션 |
| **데이터보안** | 30 | **0** | 100 | 데이터 보안 |

### 💡 Round 35 핵심 인사이트

1. **"컴플라이언스" (3,100/월, 난이도 0)**: 한국 시장 최대 신규 발굴!
2. **"벡터 데이터베이스" (300/월, 난이도 1)**: AI 트렌드 키워드
3. **"내부통제" (350/월, 난이도 0)**: 일본 시장과 연계 가능

### 🎯 한국 시장 콘텐츠 액션

| 우선순위 | 키워드 | 콘텐츠 | 예상 트래픽 |
|---------|--------|--------|------------|
| 🔴 긴급 | 컴플라이언스 | 종합 가이드 | +200-600/월 |
| 🔴 긴급 | 컴플라이언스 뜻 | 용어 설명 | +50-150/월 |
| 🟡 높음 | 내부통제 | 컴플라이언스 가이드 | +30-80/월 |
| 🟡 높음 | 벡터 데이터베이스 | AI DB 가이드 | +30-80/월 |
| 🟢 중요 | 제로트러스트 계열 | 보안 가이드 | +50-150/월 |

**Round 35 예상 추가 트래픽: +360-1,060/월**

---

## 5.20 Round 36 한국 컴플라이언스 키워드 (ISMS, ISMS-P 등)

### 🇰🇷 한국 컴플라이언스/인증 키워드 대량 발굴!

**QueryPie ACP의 핵심 가치 제안과 직결되는 컴플라이언스 키워드입니다.**

### 🔥 Tier 1: 최우선 (난이도 0-1)

| 키워드 | 검색량/월 | 난이도 | CPC | 트래픽 잠재력 | 전략 |
|--------|----------|--------|-----|--------------|------|
| **iso27001** | **1,300** | **0** | $0.80 | 1,900 | 🔥🔥 최대 기회! |
| **isms** | **900** | **1** | $0.45 | 700 | 🔥 ISMS 종합 가이드 |
| **csap** | 450 | **0** | $0.60 | 500 | 클라우드 보안 인증 |
| **pims** | 350 | **0** | $0.09 | 150 | 개인정보 관리 |
| **isms-p** | 200 | **0** | $0.30 | 700 | ISMS-P 인증 가이드 |
| **isms 인증** | 150 | **0** | $0.50 | 150 | 인증 절차 |
| **isms-p 인증심사원** | 100 | **0** | - | 40 | 심사원 정보 |
| **금융분야 개인정보보호 가이드라인** | 90 | **0** | - | 10 | 금융 규정 |
| **정보보호 채용** | 60 | **0** | $0.10 | 300 | 채용 연계 |
| **isms 인증심사원** | 40 | **0** | $0.80 | 60 | 심사원 |
| **개인정보보호 솔루션** | 30 | **0** | $0.80 | 40 | 🎯 제품 키워드! |
| **정보보호 전문가** | 30 | **0** | $0.45 | 250 | 전문가 가이드 |

### 📊 컴플라이언스 키워드 총계

| 카테고리 | 키워드 수 | 총 검색량 | 평균 난이도 | 우선순위 |
|---------|----------|----------|-------------|----------|
| ISO/ISMS | 6개 | 2,700+ | **0.3** | 🥇 최우선 |
| 클라우드 인증 (CSAP) | 2개 | 500+ | **0** | 🥇 최우선 |
| 개인정보 (PIMS) | 3개 | 450+ | **0** | 🥇 최우선 |
| 기타 정보보호 | 4개 | 200+ | **0** | 🥈 높음 |
| **총계** | **15개** | **3,850+** | **0.2** | 컴플라이언스 집중 |

### 💡 Round 36 핵심 인사이트

1. **iso27001 (1,300/월, 난이도 0)**: 국제 표준 인증 - QueryPie 핵심 USP!
2. **isms + isms-p (1,100/월)**: 한국 정보보호 인증 핵심
3. **csap (450/월)**: 클라우드 보안 인증 - ACP 관련
4. **컴플라이언스 평균 난이도 0.2**: 거의 모든 키워드가 즉시 공략 가능!

### 🎯 컴플라이언스 콘텐츠 로드맵

**Phase 1 (즉시): ISO/ISMS 계열**
```
docs.querypie.com 또는 www.querypie.com:
├── ISO 27001 종합 가이드 (1,300/월)
├── ISMS 인증 절차 가이드 (900/월)
├── ISMS-P 인증 가이드 (200/월)
└── ISMS vs ISMS-P 비교 (신규)
```

**Phase 2 (1주): 클라우드/개인정보**
```
├── CSAP 클라우드 보안 인증 가이드 (450/월)
├── PIMS 개인정보 관리 가이드 (350/월)
└── 금융분야 개인정보보호 가이드라인 해설 (90/월)
```

**Phase 3 (2주): 실무 가이드**
```
├── QueryPie로 ISO 27001 준비하기
├── ISMS 인증 체크리스트
└── 컴플라이언스 자동화 솔루션 비교
```

### 🚀 예상 효과

| 콘텐츠 | 타겟 키워드 | 예상 순위 | 예상 트래픽 |
|--------|------------|----------|------------|
| ISO 27001 가이드 | iso27001 (1,300) | 3-7위 | +100-400/월 |
| ISMS 가이드 | isms (900) | 3-7위 | +70-250/월 |
| CSAP 가이드 | csap (450) | 3-7위 | +40-130/월 |
| PIMS 가이드 | pims (350) | 3-7위 | +30-100/월 |
| ISMS-P 가이드 | isms-p (200) | 3-7위 | +20-60/월 |
| **총계** | **3,200+** | - | **+260-940/월** |

### 🔗 QueryPie 제품 연계 전략

| 컴플라이언스 | QueryPie 기능 | 콘텐츠 연계 |
|-------------|---------------|-------------|
| **ISO 27001** | 접근제어, 감사로그 | "ISO 27001 접근제어 요구사항" |
| **ISMS/ISMS-P** | 권한관리, 데이터 보호 | "ISMS 기술적 보호조치 가이드" |
| **CSAP** | 클라우드 접근제어 | "CSAP 인증을 위한 클라우드 보안" |
| **PIMS** | 개인정보 접근통제 | "PIMS 데이터 접근관리" |

**컴플라이언스 키워드는 QueryPie의 핵심 가치와 직접 연결됩니다!**

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

---

## 분석 이력

| 일시 | 내용 |
|------|------|
| 2026-02-02 01:00 KST | 초기 도메인 현황 분석 |
| 2026-02-03 16:30 KST | 제품-도메인 매핑 섹션 추가 (ACP/AIP 구분) |
| 2026-02-03 02:45 KST | Round 5: 도메인 간 시너지 전략, 초저경쟁 키워드 통합 현황, 통합 백링크 전략 추가 |
| 2026-02-03 02:55 KST | Round 7: 전체 액션 우선순위 매트릭스, 효과-노력 분석 추가 |
| 2026-02-03 04:10 KST | Round 20: 일본 시장 초대형 기회 분석, SERP 경쟁 분석, 시장별 키워드 통합 테이블 |
| 2026-02-03 04:20 KST | Round 21: 한국 시장 핵심 키워드 대량 발굴 (SSO 4,500, MFA 2,100 등 난이도 0) |
| 2026-02-03 04:30 KST | Round 22: 한국 시장 SERP 경쟁 분석 - DR 44-55 사이트 Top 10 진입 확인 |
| 2026-02-03 04:40 KST | Round 23: 미국 시장 심층 분석 - compliance automation 1,400, 경쟁사 키워드 발굴 |
| 2026-02-03 04:50 KST | Round 24: MCP 시장 분석, 최종 종합 Executive Summary, Top 10 즉시 실행 키워드 |
| 2026-02-03 06:15 KST | Round 29: 최신 Ahrefs 데이터 업데이트 - MCP 시장 폭발 (46,000/월), cloud data security 대형 기회 발굴 |
| 2026-02-03 06:45 KST | Round 30: SERP 경쟁 분석 - DR 58 사이트 Top 5 (cloud data security), DR 46 사이트 Top 15 (ゼロトラスト) 확인 |
| 2026-02-03 07:00 KST | Round 31: 관련 키워드 확장 - "access governance" (900/월, 난이도 0), "csap" (450/월, 난이도 0) 대형 발굴 |
| 2026-02-03 07:15 KST | Round 32: 성장 트렌드 분석 - 참조 도메인 +62%, Top 10 키워드 +133%, Round 29-32 최종 요약 |
| 2026-02-03 07:30 KST | Round 33: Data Governance 키워드 심층 분석 - enterprise data governance (700, 난이도 0), PAM best practices (300, 난이도 1) |
| 2026-02-03 07:45 KST | Round 34: 🇯🇵 일본 시장 대규모 발굴 - 内部統制 (6,800, 난이도 0), 56,000+/월 총 기회, 27개 키워드 |
| 2026-02-03 08:00 KST | Round 35: 🇰🇷 한국 시장 추가 - 컴플라이언스 (3,100, 난이도 0), 벡터 데이터베이스 (300, AI 트렌드) |
| 2026-02-03 08:15 KST | Round 36: 🇰🇷 컴플라이언스 키워드 - iso27001 (1,300, 난이도 0), isms (900, 난이도 1), csap (450, 난이도 0), 총 3,850+/월 |

---

*Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>*

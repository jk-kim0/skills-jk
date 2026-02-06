# GSC 인덱싱 상태 주간 점검 자동화 설계

## 개요

Google Search Console의 "Why pages aren't indexed" 데이터를 매주 자동 수집하여, 인덱싱 문제의 변화를 추적하고 해결방안을 도출하는 주간 리포트 시스템.

## 배경

- QueryPie 관련 4-6개 도메인의 SEO 상태를 정기적으로 점검할 필요가 있음
- GSC API는 인덱스 커버리지 리포트 엔드포인트를 제공하지 않음
- BigQuery 벌크 내보내기도 검색 성능 데이터만 포함, 인덱스 커버리지 제외
- Playwright 브라우저 자동화로 GSC 웹 UI에서 직접 데이터를 수집하는 방식 채택

## 요구사항

- 대상: GSC에 등록된 QueryPie 도메인들 (4-6개)
- 주기: 매주 월요일 자동 실행
- 수집 데이터: "Why pages aren't indexed" 테이블 (Reason, Source, Validation, Pages)
- 산출물: Markdown 리포트 (`reports/` 폴더) + PR 생성
- 분석: 전주 대비 변화 추적, 사유별 원인 분석 및 해결방안 제시

## 전체 구조

```
[GitHub Actions cron (매주 월요일 09:00 KST)]
    │
    ▼
[Playwright 스크립트 (bin/gsc-index-report)]
    │
    ├── 1. 저장된 쿠키로 GSC 웹 로그인
    ├── 2. 각 사이트별 "Why pages aren't indexed" 테이블 스크래핑
    ├── 3. 전주 데이터와 비교 → 변화량 계산
    ├── 4. 원인 분석 + 해결방안 매핑
    └── 5. Markdown 리포트 생성 → reports/ 저장 → PR 생성
```

## 파일 구조

```
skills-jk/
├── bin/
│   └── gsc-index-report              # Playwright 스크립트 (Python)
├── config/
│   └── gsc-sites.json                # 대상 사이트 목록
├── reports/
│   ├── data/
│   │   ├── gsc-index-2026-02-03.json # 원본 데이터 (비교용)
│   │   └── gsc-index-2026-02-10.json
│   ├── gsc-index-report-2026-02-03.md
│   └── gsc-index-report-2026-02-10.md
├── .github/workflows/
│   └── gsc-index-report.yml          # 주간 자동 실행
└── skills/
    └── ops/
        └── gsc-index-report.md       # 스킬 문서
```

## 스크래핑 상세

### 기술 스택

- Python 3.12 + Playwright
- 쿠키 저장: `~/.config/gsc/browser-cookies.json`

### 스크래핑 흐름

1. 쿠키 로드 → GSC 접속
2. `config/gsc-sites.json`에서 사이트 목록 읽기
3. 각 사이트마다:
   - GSC Pages 탭 이동
   - "Why pages aren't indexed" 테이블 대기
   - 테이블 행 파싱: Reason, Source, Validation, Pages
   - JSON으로 수집
4. 전체 결과를 JSON으로 저장 (`reports/data/gsc-index-YYYY-MM-DD.json`)
5. 이전 주 JSON과 비교 → 변화량 계산
6. Markdown 리포트 생성

### 인증

- 최초 1회: `bin/gsc-index-report --login` 으로 브라우저가 열리고 Google 로그인 수행
- 로그인 후 쿠키를 `~/.config/gsc/browser-cookies.json`에 자동 저장
- 이후 headless 모드에서 쿠키 재사용
- 쿠키 만료 시 수동으로 `--login` 재실행

### 설정 파일

`config/gsc-sites.json`:

```json
{
  "sites": [
    {"url": "sc-domain:querypie.com", "label": "querypie.com"},
    {"url": "https://docs.querypie.com/", "label": "docs.querypie.com"},
    {"url": "https://blog.querypie.com/", "label": "blog.querypie.com"}
  ]
}
```

## 변화 추적

### 비교 로직

- `reports/data/` 내 가장 최근 JSON 파일을 전주 데이터로 사용
- 각 Reason별 Pages 수 증감 계산 (`+5`, `-3`)
- 새로 나타난 Reason → 신규 문제로 표시
- 사라진 Reason → 해결됨으로 표시

### 주의 항목 자동 추출 기준

- 전주 대비 증가폭 +5 이상
- 신규 발생한 Reason

## 해결방안 매핑

스크립트 내 사유별 해결방안 사전:

| Reason | 원인 | 권장 조치 |
|--------|------|----------|
| Crawled - currently not indexed | Google이 크롤링했으나 품질/가치 부족으로 인덱싱 보류 | 콘텐츠 품질 개선, 내부 링크 보강, thin content 제거 |
| Discovered - currently not indexed | URL 발견했으나 아직 크롤링하지 않음 (크롤 예산 부족) | 사이트맵 제출 확인, 크롤 예산 최적화, 불필요 URL 정리 |
| Excluded by 'noindex' tag | 페이지에 noindex 메타태그 설정됨 | 의도된 설정인지 확인, 의도하지 않았다면 태그 제거 |
| Blocked by robots.txt | robots.txt에서 크롤링 차단 | robots.txt 규칙 검토, 필요한 페이지 허용 |
| Not found (404) | 페이지가 존재하지 않음 | 301 리다이렉트 설정 또는 사이트맵에서 제거 |
| Soft 404 | 페이지는 200 응답이지만 내용이 없는 것으로 판단됨 | 실제 콘텐츠 추가 또는 적절한 404 응답 반환 |
| Redirect page | 리다이렉트 URL이 사이트맵에 포함됨 | 사이트맵에서 리다이렉트 URL 제거, 최종 URL만 포함 |

알려지지 않은 Reason은 "확인 필요: GSC에서 상세 내용 직접 확인"으로 fallback 처리.

## 리포트 포맷

```markdown
# GSC 인덱싱 상태 주간 리포트

- 기간: 2026-02-03 → 2026-02-10
- 생성: 2026-02-10 09:00 (자동)

## 전체 요약

| 사이트 | 미인덱싱 페이지 | 전주 대비 | 신규 문제 | 해결됨 |
|--------|----------------|----------|----------|--------|
| querypie.com | 45 | +3 | 1 | 0 |
| docs.querypie.com | 62 | -5 | 0 | 1 |
| blog.querypie.com | 35 | +10 | 2 | 0 |
| **합계** | **142** | **+8** | **3** | **1** |

## 주의 필요 항목

- ⚠ blog.querypie.com: "Crawled - currently not indexed" +10 (35→45)
- 🆕 querypie.com: "Soft 404" 신규 발생 (3페이지)

## 사이트별 상세

### querypie.com

| Reason | Pages | 변화 | Source | Validation |
|--------|-------|------|--------|------------|
| Crawled - currently not indexed | 25 | +2 | Sitemap | N/A |
| Excluded by 'noindex' tag | 12 | 0 | Website | N/A |
| Soft 404 | 3 | 🆕 | Sitemap | N/A |

**권장 조치:**
- Crawled - currently not indexed (+2): 콘텐츠 품질 개선, 내부 링크 보강
- Soft 404 (신규): 해당 3페이지 확인하여 실제 콘텐츠 추가 또는 404 처리
```

## GitHub Actions 워크플로우

`.github/workflows/gsc-index-report.yml`:

```yaml
name: GSC Index Report (Weekly)

on:
  schedule:
    - cron: '0 0 * * 1'   # 매주 월요일 09:00 KST (UTC 0:00)
  workflow_dispatch:        # 수동 실행

jobs:
  report:
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v4
      - name: Install dependencies
        run: pip install playwright && playwright install chromium
      - name: Run report
        run: bin/gsc-index-report --headless
        env:
          GSC_COOKIE_PATH: ${{ secrets.GSC_COOKIE_PATH }}
      - name: Create PR
        run: |
          git checkout -b reports/gsc-index-$(date +%Y-%m-%d)
          git add reports/
          git commit -m "docs(report): GSC 인덱싱 주간 리포트 $(date +%Y-%m-%d)"
          gh pr create --title "GSC 인덱싱 주간 리포트 $(date +%Y-%m-%d)" \
            --body "자동 생성된 주간 인덱싱 상태 리포트입니다."
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## CLI 인터페이스

```bash
bin/gsc-index-report --login       # 최초 쿠키 설정 (브라우저 열림)
bin/gsc-index-report --headless    # 로컬 테스트 (headless)
bin/gsc-index-report --site querypie.com  # 특정 사이트만 실행
bin/gsc-index-report --no-compare  # 비교 없이 현재 스냅샷만
```

## 리스크 및 대응

| 리스크 | 대응 |
|--------|------|
| 쿠키 만료 | `--login`으로 수동 갱신. 실패 시 에러 리포트 생성 |
| GSC UI 변경 | 셀렉터 기반 스크래핑이므로 UI 변경 시 스크립트 수정 필요 |
| 사이트 추가/제거 | `config/gsc-sites.json` 수정으로 대응 |
| 네트워크 오류 | 사이트별 재시도(최대 2회), 실패한 사이트는 리포트에 오류 표시 |

## 구현 순서

1. `bin/gsc-index-report` 스크립트 작성 (로그인 + 스크래핑)
2. `config/gsc-sites.json` 설정
3. 변화 추적 로직 구현
4. 리포트 생성 로직 구현
5. 로컬 테스트
6. `.github/workflows/gsc-index-report.yml` 워크플로우 작성
7. self-hosted runner에서 E2E 테스트

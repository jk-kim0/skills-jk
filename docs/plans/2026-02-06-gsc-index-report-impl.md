# GSC 인덱싱 상태 주간 점검 - 구현 플랜

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** GSC "Why pages aren't indexed" 데이터를 Playwright로 스크래핑하여 주간 변화 추적 리포트를 자동 생성하는 시스템 구현

**Architecture:** Python 3.12 + Playwright 스크립트(`bin/gsc-index-report`)가 GSC 웹 UI에서 인덱싱 테이블을 스크래핑. 쿠키 기반 인증, JSON 데이터 저장, 전주 비교, Markdown 리포트 생성. GitHub Actions로 주간 자동 실행.

**Tech Stack:** Python 3.12, Playwright (async), argparse, JSON, pathlib

**Design doc:** `docs/plans/2026-02-06-gsc-index-report-design.md`

---

### Task 1: 설정 파일 및 디렉토리 생성

**Files:**
- Create: `config/gsc-sites.json`
- Create: `reports/data/.gitkeep`

**Step 1: config 디렉토리 및 사이트 설정 파일 생성**

```json
{
  "sites": [
    {"url": "sc-domain:querypie.com", "label": "querypie.com"},
    {"url": "https://docs.querypie.com/", "label": "docs.querypie.com"},
    {"url": "https://blog.querypie.com/", "label": "blog.querypie.com"}
  ]
}
```

**Step 2: reports/data 디렉토리 생성**

```bash
mkdir -p reports/data
touch reports/data/.gitkeep
```

**Step 3: Commit**

```bash
git add config/gsc-sites.json reports/data/.gitkeep
git commit -m "feat: GSC 인덱싱 리포트 설정 파일 및 데이터 디렉토리 추가"
```

---

### Task 2: 메인 스크립트 뼈대 + CLI 인터페이스

**Files:**
- Create: `bin/gsc-index-report`

**Step 1: CLI 파싱 + 메인 구조 작성**

`bin/gsc-index-report` — shebang `#!/usr/bin/env python3.12`, argparse로 CLI 구현.

인자:
- `--login`: 브라우저 열어서 쿠키 저장 (headed 모드)
- `--headless`: headless 모드 실행 (기본값)
- `--site LABEL`: 특정 사이트만 실행
- `--no-compare`: 전주 비교 없이 현재 스냅샷만
- `--config PATH`: 설정 파일 경로 (기본: `config/gsc-sites.json`)
- `--output-dir PATH`: 출력 디렉토리 (기본: `reports/`)

메인 흐름 함수 시그니처:
- `async def login_and_save_cookies()` → placeholder
- `async def scrape_site(page, site_url, site_label)` → placeholder, 빈 dict 반환
- `def compare_with_previous(current_data, output_dir)` → placeholder, None 반환
- `def generate_report(current_data, comparison, output_dir)` → placeholder
- `def load_config(config_path)` → JSON 로드

**Step 2: 실행 권한 부여 및 동작 확인**

```bash
chmod +x bin/gsc-index-report
bin/gsc-index-report --help
```

Expected: argparse 도움말 출력

**Step 3: Commit**

```bash
git add bin/gsc-index-report
git commit -m "feat: gsc-index-report CLI 뼈대 구현"
```

---

### Task 3: 로그인 + 쿠키 저장/로드

**Files:**
- Modify: `bin/gsc-index-report`

**Step 1: login_and_save_cookies() 구현**

- Playwright chromium 브라우저를 headed 모드로 실행
- `https://search.google.com/search-console` 로 이동
- 사용자가 수동 로그인할 때까지 대기 (콘솔에 "로그인 후 Enter를 눌러주세요" 출력)
- `input()` 으로 대기
- `context.cookies()` 로 쿠키 저장 → `~/.config/gsc/browser-cookies.json`

```python
COOKIE_PATH = Path(os.environ.get(
    'GSC_COOKIE_PATH',
    os.path.expanduser('~/.config/gsc/browser-cookies.json')
))
```

**Step 2: load_cookies() + 쿠키로 브라우저 시작**

- `COOKIE_PATH`에서 쿠키 로드
- `context.add_cookies(cookies)` 로 세션 복원
- headless 모드로 브라우저 실행

**Step 3: 로그인 테스트**

```bash
bin/gsc-index-report --login
```

Expected: 브라우저가 열리고 GSC 로그인 가능, 쿠키 파일 생성됨

**Step 4: Commit**

```bash
git add bin/gsc-index-report
git commit -m "feat: GSC 쿠키 기반 로그인/인증 구현"
```

---

### Task 4: GSC 스크래핑 핵심 로직

**Files:**
- Modify: `bin/gsc-index-report`

**Step 1: GSC URL 구성 함수**

사이트 URL을 GSC 페이지 인덱싱 리포트 URL로 변환:

```python
def build_gsc_page_indexing_url(site_url: str) -> str:
    """GSC Page Indexing 리포트 URL 생성.

    site_url 예시:
      "sc-domain:querypie.com" → resource_id=sc-domain%3Aquerypie.com
      "https://docs.querypie.com/" → resource_id=https%3A%2F%2Fdocs.querypie.com%2F
    """
    encoded = urllib.parse.quote(site_url, safe='')
    return f"https://search.google.com/search-console/page-indexing?resource_id={encoded}"
```

**Step 2: scrape_site() 구현**

핵심 스크래핑 로직:

```python
async def scrape_site(page, site_url: str, site_label: str) -> dict:
    url = build_gsc_page_indexing_url(site_url)
    await page.goto(url, wait_until='networkidle')

    # "Why pages aren't indexed" 테이블 로드 대기
    # GSC는 Angular 기반 SPA — 테이블이 동적으로 렌더링됨
    # 테이블 셀렉터는 실제 DOM 구조 확인 후 조정 필요
    await page.wait_for_selector('table', timeout=30000)

    # 테이블 행 파싱
    rows = await page.query_selector_all('table tbody tr')
    reasons = []
    for row in rows:
        cells = await row.query_selector_all('td')
        if len(cells) >= 2:
            reason = (await cells[0].inner_text()).strip()
            pages_text = (await cells[-1].inner_text()).strip()
            # Source, Validation 컬럼이 있으면 추출
            source = (await cells[1].inner_text()).strip() if len(cells) >= 3 else ''
            validation = (await cells[2].inner_text()).strip() if len(cells) >= 4 else ''
            pages_count = int(pages_text.replace(',', '')) if pages_text.replace(',', '').isdigit() else 0
            reasons.append({
                'reason': reason,
                'source': source,
                'validation': validation,
                'pages': pages_count,
            })

    return {
        'site_url': site_url,
        'label': site_label,
        'reasons': reasons,
        'scraped_at': datetime.now().isoformat(),
    }
```

**주의:** GSC의 실제 DOM 구조(셀렉터)는 첫 실행 시 확인하고 조정해야 함. 위 셀렉터(`table`, `tbody tr`, `td`)는 초기 추정치이며, `--login` 모드에서 DevTools로 실제 구조를 확인한 뒤 수정.

**Step 3: 재시도 로직**

```python
async def scrape_site_with_retry(page, site_url, site_label, max_retries=2):
    for attempt in range(max_retries + 1):
        try:
            return await scrape_site(page, site_url, site_label)
        except Exception as e:
            if attempt == max_retries:
                return {
                    'site_url': site_url,
                    'label': site_label,
                    'error': str(e),
                    'scraped_at': datetime.now().isoformat(),
                }
            await page.wait_for_timeout(3000)
```

**Step 4: JSON 저장**

```python
def save_data(data: dict, output_dir: str):
    data_dir = Path(output_dir) / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime('%Y-%m-%d')
    path = data_dir / f'gsc-index-{date_str}.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path
```

**Step 5: Commit**

```bash
git add bin/gsc-index-report
git commit -m "feat: GSC 페이지 인덱싱 테이블 스크래핑 구현"
```

---

### Task 5: 변화 추적 로직

**Files:**
- Modify: `bin/gsc-index-report`

**Step 1: 이전 데이터 로드**

```python
def find_previous_data(output_dir: str) -> dict | None:
    data_dir = Path(output_dir) / 'data'
    files = sorted(data_dir.glob('gsc-index-*.json'), reverse=True)
    # 오늘 파일 제외하고 가장 최근 파일
    today = datetime.now().strftime('%Y-%m-%d')
    for f in files:
        if today not in f.name:
            with open(f, encoding='utf-8') as fh:
                return json.load(fh)
    return None
```

**Step 2: 비교 로직**

```python
def compare_with_previous(current_data: dict, previous_data: dict | None) -> dict:
    if previous_data is None:
        return {'has_previous': False}

    comparison = {'has_previous': True, 'sites': {}}
    prev_by_label = {s['label']: s for s in previous_data.get('sites', [])}

    for site in current_data.get('sites', []):
        label = site['label']
        prev_site = prev_by_label.get(label)
        if not prev_site or 'error' in site:
            comparison['sites'][label] = {'new_site': True}
            continue

        prev_reasons = {r['reason']: r['pages'] for r in prev_site.get('reasons', [])}
        curr_reasons = {r['reason']: r['pages'] for r in site.get('reasons', [])}

        changes = {}
        all_reasons = set(prev_reasons) | set(curr_reasons)
        for reason in all_reasons:
            prev_count = prev_reasons.get(reason, 0)
            curr_count = curr_reasons.get(reason, 0)
            diff = curr_count - prev_count
            is_new = reason not in prev_reasons
            is_resolved = reason not in curr_reasons
            changes[reason] = {
                'previous': prev_count,
                'current': curr_count,
                'diff': diff,
                'is_new': is_new,
                'is_resolved': is_resolved,
            }
        comparison['sites'][label] = changes

    return comparison
```

**Step 3: Commit**

```bash
git add bin/gsc-index-report
git commit -m "feat: 전주 대비 변화 추적 로직 구현"
```

---

### Task 6: 해결방안 매핑 + Markdown 리포트 생성

**Files:**
- Modify: `bin/gsc-index-report`

**Step 1: REMEDIATION 딕셔너리 추가**

설계 문서의 해결방안 매핑 테이블을 Python dict로 스크립트 상단에 정의.

7개 주요 사유 + fallback:
- Crawled - currently not indexed
- Discovered - currently not indexed
- Excluded by 'noindex' tag
- Blocked by robots.txt
- Not found (404)
- Soft 404
- Redirect page
- Duplicate without user-selected canonical
- Duplicate, Google chose different canonical than user
- Page with redirect
- Server error (5xx)
- Blocked due to unauthorized request (401)
- Blocked due to access forbidden (403)

**Step 2: generate_report() 구현**

리포트 구조 (설계 문서 기준):
1. 헤더 (기간, 생성 시각)
2. 전체 요약 테이블 (사이트별 미인덱싱 페이지 수, 전주 대비, 신규/해결)
3. 주의 필요 항목 (diff >= 5 또는 is_new)
4. 사이트별 상세 (Reason 테이블 + 권장 조치)

Markdown 문자열을 조립하여 `reports/gsc-index-report-YYYY-MM-DD.md`에 저장.

**Step 3: Commit**

```bash
git add bin/gsc-index-report
git commit -m "feat: 해결방안 매핑 및 Markdown 리포트 생성 구현"
```

---

### Task 7: 메인 흐름 연결 + 로컬 테스트

**Files:**
- Modify: `bin/gsc-index-report`

**Step 1: main() 함수에서 전체 흐름 연결**

```python
async def run(args):
    if args.login:
        await login_and_save_cookies()
        return

    config = load_config(args.config)
    sites = config['sites']
    if args.site:
        sites = [s for s in sites if s['label'] == args.site]

    headless = not args.login
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context()
        await load_cookies(context)
        page = await context.new_page()

        results = {'sites': [], 'generated_at': datetime.now().isoformat()}
        for site in sites:
            data = await scrape_site_with_retry(page, site['url'], site['label'])
            results['sites'].append(data)

        await browser.close()

    data_path = save_data(results, args.output_dir)

    previous = None if args.no_compare else find_previous_data(args.output_dir)
    comparison = compare_with_previous(results, previous)
    report_path = generate_report(results, comparison, args.output_dir)

    print(f"데이터 저장: {data_path}")
    print(f"리포트 생성: {report_path}")
```

**Step 2: `--login`으로 쿠키 저장 테스트**

```bash
bin/gsc-index-report --login
```

Expected: 브라우저 열림, 로그인 후 쿠키 저장

**Step 3: 첫 실행 테스트 (단일 사이트)**

```bash
bin/gsc-index-report --site querypie.com --no-compare
```

Expected: `reports/data/gsc-index-YYYY-MM-DD.json` 생성, `reports/gsc-index-report-YYYY-MM-DD.md` 생성

**Step 4: 셀렉터 조정**

첫 실행 결과를 보고 GSC 테이블의 실제 DOM 셀렉터 조정. `--login` 모드에서 DevTools를 열어 확인.

**Step 5: Commit**

```bash
git add bin/gsc-index-report
git commit -m "feat: 메인 흐름 연결 및 로컬 테스트 완료"
```

---

### Task 8: GitHub Actions 워크플로우

**Files:**
- Create: `.github/workflows/gsc-index-report.yml`

**Step 1: 워크플로우 파일 작성**

설계 문서의 워크플로우 기반. self-hosted runner 사용, 주간 cron + workflow_dispatch.

기존 `scheduled-tasks.yml`의 runner 선택 패턴 참조.

**Step 2: Commit**

```bash
git add .github/workflows/gsc-index-report.yml
git commit -m "feat: GSC 인덱싱 주간 리포트 GitHub Actions 워크플로우 추가"
```

---

### Task 9: PR 업데이트

**Step 1: 기존 PR #62 에 구현 코드 push**

```bash
git push origin feat/gsc-index-report-design
```

**Step 2: PR 설명 업데이트 (설계 + 구현 포함으로)**

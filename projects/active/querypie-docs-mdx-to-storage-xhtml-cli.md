---
id: querypie-docs-mdx-to-storage-xhtml-cli
title: QueryPie Docs MDX -> Confluence Storage XHTML CLI
status: active
repos:
  - https://github.com/querypie/querypie-docs
created: 2026-02-15
updated: 2026-02-17
---

# QueryPie Docs MDX -> Confluence Storage XHTML CLI

## 목표

`../querypie-docs-translation-1/confluence-mdx` 기반으로, MDX 문서를 Confluence Storage Format(XHTML)으로 변환하는 독립 CLI를 구현한다.

핵심 요구사항:
- 문서 의미(구조/매크로/링크/코드)를 보존하는 변환
- 배치 실행 및 검증 가능한 테스트 체계 구축
- reverse-sync에서 재사용 가능한 변환 모듈 제공

## 배경

현재 `confluence-mdx/bin/reverse_sync/mdx_to_xhtml_inline.py`는 inline/부분 변환 중심이며,
리스트 중첩/Callout/테이블/매크로 경계에서 안정성이 부족하다.

reverse-sync verify 실패(21건 전체 실패)의 주요 원인:
- **heading 레벨 보정 누락**: Forward converter가 `<h1>`→`##`로 올리지만, 역변환 시 `##`→`<h2>`로 내보내 `<h1>`과 불일치
- **Callout/Panel 미처리**: `<Callout type="...">` 블록이 paragraph로 처리되어 `<ac:structured-macro>` 미생성
- **이미지/figure 미처리**: `<figure><img>` 블록이 html_block으로 그대로 전달되어 `<ac:image>` 미생성
- **수평선 미처리**: `______`이 paragraph로 처리되어 `<hr />` 미생성
- **italic 미처리**: `*text*` → `<em>text</em>` 변환 없음
- **Confluence 자동생성 속성 무시 미구현**: `ac:macro-id`, `ac:local-id` 등이 diff에 노출
- **layout 섹션 미처리**: `<ac:layout>` 래핑이 diff에 노출

## 기존 계획의 문제점과 개선 방향

### 1. 중립 IR 도입은 과설계

기존 계획: `MDX → 중립 IR → XHTML` 3단계 파이프라인.

**문제:**
- Forward converter(`core.py`, ~1,438줄)는 IR 없이 직접 변환하며 잘 작동
- 변환 규칙이 ~20개로 적다. IR 레이어의 추상화 비용이 이점을 초과
- MDX 블록 파서의 출력(`MdxBlock`)이 이미 사실상 IR

**개선:** MDX 블록 파싱 → 블록별 직접 XHTML 생성. 별도 IR 모듈(`ir.py`, `normalizer.py`) 불필요.

### 2. AST 파서 선택이 비현실적

기존 계획: "remark/mdast 또는 기존 파서 확장"

**문제:**
- remark/mdast는 JavaScript 생태계. 전체 코드베이스가 Python
- Node.js 의존성 추가는 배포/운영 복잡도를 크게 높임
- Python에 mdast 포트가 없음

**개선:** 기존 `mdx_block_parser.py`의 line-based 파서를 확장한다.
MDX 블록 구문은 규칙적이므로 line-based 파싱으로 충분하다.

### 3. 핵심 변환 규칙의 누락

기존 계획에서 언급하지 않은 필수 변환:

| 누락 항목 | 설명 |
|-----------|------|
| Heading 레벨 보정 | `##`→`<h1>` (level - 1). `# Title`은 skip (page title) |
| Callout 타입 역매핑 | `default→tip`, `info→info`, `important→note`, `error→warning` |
| Panel with emoji | `<Callout type="info" emoji="🌈">` → `<ac:structured-macro ac:name="panel">` |
| 이미지/figure | `<figure><img src="/path/img.png">` → `<ac:image><ri:attachment>` |
| 수평선 | `______` → `<hr />` |
| Frontmatter/import 스킵 | XHTML 출력에 미포함 |
| `# Title` 스킵 | Frontmatter의 title과 동일한 h1 heading은 XHTML에 미포함 |
| Layout 섹션 | `<ac:layout>` 래핑은 비교 시 strip |
| TOC/view-file 매크로 | 비교 시 무시 (역변환 불가) |
| 이미지 파일명 매핑 | Forward converter가 파일명을 정규화하므로 원본 복원 불가 |

### 4. 검증 기준 구체화

**XHTML 비교 시 무시할 속성** (명시적 정의):

| 속성 | 이유 |
|------|------|
| `ac:macro-id` | Confluence 자동생성 UUID |
| `ac:local-id`, `local-id` | Confluence 자동생성 |
| `ac:schema-version` | 스키마 버전 (항상 "1") |
| `ri:version-at-save` | 첨부 파일 버전 |
| `ac:original-height`, `ac:original-width` | 원본 이미지 크기 |
| `ac:custom-width` | 부가 속성 |
| `data-table-width`, `data-layout` | 테이블 레이아웃 힌트 |
| `ac:breakout-mode`, `ac:breakout-width` | 코드 매크로 레이아웃 |
| `style` (col 요소) | 컬럼 너비 스타일 |
| `class` (p 요소) | `media-group` 등 표시용 클래스 |

**비교 시 제거할 구조:**
- `<ac:layout>`, `<ac:layout-section>`, `<ac:layout-cell>` — 내용만 추출
- `<ac:structured-macro ac:name="toc">` — 역변환 불가
- `<ac:structured-macro ac:name="view-file">` — 역변환 불가
- `<ac:adf-mark>` — 이미지 border 장식
- `<ac:inline-comment-marker>` — 내용만 보존

### 5. ac:structured-macro 기본 전략

`ac:structured-macro`를 기본으로 한다 (기존 문서 대다수가 이 포맷).
`ac:adf-extension`(note panel 등)은 후속 지원.

## 확인한 현황 (2026-02-15)

### 코드베이스 구조

```
confluence-mdx/
├── bin/
│   ├── converter/
│   │   ├── core.py          # Forward converter XHTML→MDX (1,438줄)
│   │   ├── context.py       # 전역 상태, pages.yaml 로딩, 링크 해석 (665줄)
│   │   └── cli.py           # Forward CLI entry point
│   ├── reverse_sync/
│   │   ├── mdx_block_parser.py              # MDX 블록 파서 (130줄)
│   │   ├── mdx_to_xhtml_inline.py           # 블록→XHTML 변환 (271줄)
│   │   └── mdx_to_storage_xhtml_verify.py   # 검증 유틸 (125줄)
│   ├── mdx_to_storage_xhtml_verify_cli.py   # 검증 CLI (99줄)
│   └── xhtml_beautify_diff.py               # XHTML 정규화/diff (89줄)
├── tests/
│   ├── testcases/           # 21건 (19 page-id + lists + panels)
│   └── test_*.py            # pytest 테스트
└── var/
    └── pages.yaml           # 페이지 메타데이터
```

### 기존 변환 모듈 분석

**`mdx_block_parser.py` — 현재 지원 블록 타입:**
- `frontmatter`, `import_statement`, `heading`, `paragraph`, `code_block`, `list`, `html_block`, `empty`
- **미지원:** Callout, figure, 수평선(`______`), blockquote, `<details>`, `<Badge>`

**`mdx_to_xhtml_inline.py` — 현재 지원 변환:**
- heading → `<h{level}>` (레벨 보정 없음)
- paragraph → `<p>` (inline: bold, code, link)
- list → `<ul>`/`<ol>` (중첩 지원)
- code_block → `<ac:structured-macro ac:name="code">`
- html_block → passthrough
- **미지원:** italic, heading 레벨 보정, Callout, figure→ac:image

### 검증 인프라

- `xhtml_beautify_diff.py`: BeautifulSoup 정규화 + unified diff
- `mdx_to_storage_xhtml_verify_cli.py`: testcases 배치 검증
- 현재 결과: **total=21, passed=0, failed=21**

### Forward Converter 핵심 변환 규칙 (역변환 시 참조)

| Forward (XHTML→MDX) | Reverse (MDX→XHTML) |
|---------------------|---------------------|
| `<h1>` → `##` (레벨 +1) | `##` → `<h1>` (레벨 -1) |
| `<h2>` → `###` | `###` → `<h2>` |
| `<strong>` in heading → 마커 제거 | heading 내 bold 무시 |
| `<strong>` → `**text**` | `**text**` → `<strong>text</strong>` |
| `<em>` → `*text*` | `*text*` → `<em>text</em>` |
| `<code>` → `` `text` `` | `` `text` `` → `<code>text</code>` |
| `<a href>` → `[text](url)` | `[text](url)` → `<a href="url">text</a>` |
| `<ac:image><ri:attachment ri:filename="img.png">` → `<img src="images/img.png">` | `<figure><img src="...">` → `<ac:image>` |
| `ac:structured-macro name="tip"` → `<Callout type="default">` | `<Callout type="default">` → `ac:structured-macro name="tip"` |
| `ac:structured-macro name="info"` → `<Callout type="info">` | `<Callout type="info">` → `ac:structured-macro name="info"` |
| `ac:structured-macro name="note"` → `<Callout type="important">` | `<Callout type="important">` → `ac:structured-macro name="note"` |
| `ac:structured-macro name="warning"` → `<Callout type="error">` | `<Callout type="error">` → `ac:structured-macro name="warning"` |
| `ac:structured-macro name="panel"` → `<Callout emoji="...">` | `<Callout emoji="🌈">` → `ac:structured-macro name="panel"` |
| `ac:structured-macro name="code"` → ` ```lang ` | ` ```lang ` → `ac:structured-macro name="code"` |
| `<hr />` → `______` | `______` → `<hr />` |
| `<Badge color="blue">` ← `ac:structured-macro name="status"` | `<Badge>` → `ac:structured-macro name="status"` |

## 진행 현황 (2026-02-17)

### Phase 완료 상태

| Phase | 범위 | 상태 |
|-------|------|------|
| Phase 1 (Task 1.1~1.7) | 모듈 구조 + 핵심 블록/인라인 | **완료** — main 머지 완료 |
| Phase 2 (Task 2.1~2.3) | Callout, Figure, 중첩 리스트 | **완료** — main 머지 완료 (PR #772, #773, #774) |
| Phase 2 (Task 2.4~2.6) | 테이블, Blockquote, verify 필터 | **진행 중** — PR #775~#777 리뷰 대기 |
| Phase 2 (Task 2.7) | 통합 검증 | 미착수 |

### 모듈 현재 규모

| 모듈 | 줄 수 |
|------|-------|
| `bin/mdx_to_storage/parser.py` | 320줄 |
| `bin/mdx_to_storage/emitter.py` | 240줄 |
| `bin/mdx_to_storage/inline.py` | 63줄 |
| **합계** | **623줄** |

### 단위 테스트 현황

- **총 60개** (parser 16, inline 14, emitter 30)
- 전체 pass

### Batch verify 현황

- **결과: 0/21 pass** (변동 없음)
- **원인:** verify 정규화 필터(Task 2.6)가 아직 main에 미적용. `ac:macro-id`, `ac:layout` 등이 diff에 노출되어 모든 케이스 실패
- verify 필터가 적용되면 즉시 pass 수 증가 예상

### 오픈 PR 목록

| PR | Task | 제목 |
|----|------|------|
| #775 | Task 2.4 | 테이블 변환(마크다운/HTML) 구현 |
| #776 | Task 2.5 | blockquote 변환 구현 |
| #777 | Task 2.6 | verify 정규화 필터 구현 |

## 아키텍처

```
MDX 입력
  │
  ├─ 1. 전처리: frontmatter 파싱(title 추출), import 제거
  │
  ├─ 2. 블록 파싱: line-based parser → Block[]
  │     (heading, paragraph, list, code_block, callout,
  │      figure, table, html_block, hr, details, empty)
  │
  ├─ 3. 블록별 XHTML 생성: Block → XHTML string
  │     ├─ 인라인 변환: **bold**, *italic*, `code`, [link](), <br/> 등
  │     └─ 구조 변환: Callout→macro, figure→ac:image, table→<table>
  │
  └─ 4. XHTML 조립: 모든 블록의 XHTML을 연결
```

**IR 레이어 없음.** Block 타입은 기존 `MdxBlock`을 확장한 dataclass:

```python
@dataclass
class Block:
    type: str           # "heading", "paragraph", "callout", "figure", "hr", ...
    content: str        # 원본 MDX 텍스트
    level: int = 0      # heading level, list depth
    language: str = ""  # code block language
    children: list = field(default_factory=list)  # nested blocks (callout body 등)
    attrs: dict = field(default_factory=dict)      # callout type, image src/width 등
```

### 모듈 구조

```
bin/
├── mdx_to_storage_xhtml_cli.py   # CLI 로직 (기존 파일 확장)
└── mdx_to_storage/
    ├── __init__.py
    ├── parser.py                  # MDX → Block[] 파싱
    ├── emitter.py                 # Block → XHTML 문자열 생성
    ├── inline.py                  # 인라인 MDX → XHTML 변환
    └── link_resolver.py           # pages.yaml 기반 내부 링크 해석

tests/
└── test_mdx_to_storage/
    ├── test_parser.py
    ├── test_inline.py
    └── test_emitter.py
```

기존 `bin/reverse_sync/` 모듈은 유지. 신규 `bin/mdx_to_storage/` 모듈이
기존 `mdx_block_parser.py`, `mdx_to_xhtml_inline.py`를 대체하며,
검증 CLI(`mdx_to_storage_xhtml_verify_cli.py`)가 신규 모듈을 호출하도록 전환.

## 변환 규칙 전체 목록

### Block 레벨 (parser.py + emitter.py)

| # | MDX 입력 | XHTML 출력 | 우선순위 |
|---|---------|-----------|---------|
| 1 | `## Heading` | `<h1>Heading</h1>` (레벨 -1 보정) | P1 |
| 2 | `# Title` (page title) | skip (XHTML 미포함) | P1 |
| 3 | 일반 텍스트 | `<p>inline content</p>` | P1 |
| 4 | `* item` / `1. item` | `<ul><li><p>...</p></li></ul>` (중첩 포함) | P1 |
| 5 | ` ```lang ` | `<ac:structured-macro ac:name="code">` + CDATA | P1 |
| 6 | `<Callout type="X">` | `<ac:structured-macro ac:name="Y"><ac:rich-text-body>` | P1 |
| 7 | `<figure><img>` | `<ac:image><ri:attachment>` | P1 |
| 8 | `______` | `<hr />` | P1 |
| 9 | `\| col \|` 마크다운 테이블 | `<table><tbody><tr><td><p>` | P2 |
| 10 | `<table>` HTML 테이블 | XHTML로 보존 (인라인만 변환) | P2 |
| 11 | `> blockquote` | `<blockquote><p>` | P2 |
| 12 | `<details><summary>` | `<ac:structured-macro ac:name="expand">` | P3 |
| 13 | `<Badge color="X">` | `<ac:structured-macro ac:name="status">` | P3 |

### Inline 레벨 (inline.py)

| # | MDX | XHTML | 우선순위 |
|---|-----|-------|---------|
| 1 | `**text**` | `<strong>text</strong>` | P1 |
| 2 | `*text*` | `<em>text</em>` | P1 |
| 3 | `` `text` `` | `<code>text</code>` | P1 |
| 4 | `[text](url)` | `<a href="url">text</a>` (외부 링크) | P1 |
| 5 | `[text](relative)` | `<ac:link><ri:page ri:content-title="...">` (내부 링크) | P2 |
| 6 | `<br/>` | `<br />` | P1 |
| 7 | `<u>text</u>` | `<u>text</u>` | P2 |
| 8 | `&gt;` `&lt;` | 그대로 보존 | P1 |

### 특수 처리

| 항목 | 처리 |
|------|------|
| Frontmatter (`---`) | 파싱하여 title 추출, XHTML 출력에 미포함 |
| `# Title` | Frontmatter title과 동일하면 skip |
| Import 문 | 무시 (skip) |
| Callout 타입 역매핑 | `default→tip`, `info→info`, `important→note`, `error→warning` |
| Panel with emoji | `<Callout type="info" emoji="🌈">` → `<ac:structured-macro ac:name="panel">` + `panelIcon` params |
| Heading 레벨 보정 | MDX `##` (h2) → XHTML `<h1>`. MDX `###` → XHTML `<h2>`. 1단계 감소 |
| Heading 내 bold | `**text**` 마커 제거 (forward converter가 strip하므로) |
| 이미지 파일명 | MDX의 정규화된 파일명 사용 (원본 복원 불가 — 알려진 제약) |
| 빈 paragraph | `<p />` 생성 |
| Layout 섹션 | 비교 시 `<ac:layout>` 래핑 strip |
| TOC 매크로 | 역변환 불가. 비교 시 제거 |
| view-file 매크로 | `📎 [file](file)` 패턴으로부터 복원 시도 (P3) |

## CLI 인터페이스

```bash
# 단일 파일 변환
python3 bin/mdx_to_storage_xhtml_cli.py convert <input.mdx> -o <output.xhtml>

# 검증 (기존 XHTML과 비교)
python3 bin/mdx_to_storage_xhtml_cli.py verify <input.mdx> \
    --expected <page.xhtml> [--show-diff]

# 배치 검증 (testcases 디렉토리)
python3 bin/mdx_to_storage_xhtml_cli.py batch-verify \
    --testcases-dir <dir> [--show-diff-limit N] [--write-generated]
```

## 검증 전략

### 비교 알고리즘

1. 양쪽 XHTML을 BeautifulSoup으로 파싱
2. **구조 제거:** `<ac:layout>`, `<ac:layout-section>`, `<ac:layout-cell>` 래핑 제거 (내용 보존)
3. **매크로 제거:** `<ac:structured-macro ac:name="toc">`, `view-file` 등 역변환 불가 매크로 제거
4. **장식 제거:** `<ac:adf-mark>`, `<ac:inline-comment-marker>` 등 장식 요소 제거 (내용 보존)
5. **속성 제거:** 무시 대상 속성 제거 (ac:macro-id, ac:local-id, 등)
6. `beautify_xhtml()` 정규화 후 unified diff

### 검증 수준

- **Level 1:** 블록 요소 수 및 타입 일치 (heading, p, ul/ol, macro 등)
- **Level 2:** 텍스트 콘텐츠 일치 (인라인 포함)
- **Level 3:** 전체 XHTML 구조 일치 (무시 속성/구조 제외)

## 단계별 실행 계획

---

### Phase 1 — 모듈 구조 + 핵심 블록/인라인 (3일)

기본 블록(heading, paragraph, code, list)과 인라인(bold, italic, code, link)을
새 모듈로 구현하고, 검증 CLI를 신규 모듈로 전환한다.

#### Task 1.1: 모듈 구조 생성 ✅

- [x] `bin/mdx_to_storage/__init__.py` 생성
- [x] `bin/mdx_to_storage/parser.py` 스켈레톤 — `Block` dataclass + `parse_mdx()` 함수
- [x] `bin/mdx_to_storage/inline.py` 스켈레톤 — `convert_inline()` 함수
- [x] `bin/mdx_to_storage/emitter.py` 스켈레톤 — `emit_block()` + `emit_document()` 함수
- [x] `tests/test_mdx_to_storage/` 디렉토리 생성

#### Task 1.2: 블록 파서 구현 (`parser.py`) ✅

기존 `mdx_block_parser.py`를 참조하되 새로 작성. 추가 블록 타입 지원:

- [x] `Block` dataclass 정의 (type, content, level, language, children, attrs)
- [x] Frontmatter 파싱 — `---` 블록에서 `title` 추출, `attrs['title']`에 저장
- [x] Import 문 감지 — `import ` 시작 줄
- [x] Heading 파싱 — `#` 개수로 level 추출
- [x] Paragraph 파싱 — fallback, 빈 줄까지 수집
- [x] Code block 파싱 — ` ``` ` 펜스, `language` 추출
- [x] List 파싱 — `*`/`-`/`1.` 시작, 들여쓰기 연속 포함
- [x] 수평선 감지 — `______` 패턴 → `type="hr"`
- [x] Callout 블록 감지 — `<Callout` 시작 ~ `</Callout>` 종료, `type`/`emoji` attrs 추출
- [x] Figure 블록 감지 — `<figure` 시작 ~ `</figure>` 종료, `src`/`alt`/`width` attrs 추출
- [x] HTML block 감지 — `<table`, `<div` 등 기존 로직 유지
- [x] Empty line 처리
- [x] `parse_mdx(text: str) -> list[Block]` 통합 함수

#### Task 1.3: 인라인 변환 구현 (`inline.py`) ✅

- [x] Code span 보호 — `` `text` `` → placeholder → `<code>text</code>` 복원
- [x] Bold — `**text**` → `<strong>text</strong>`
- [x] Italic — `*text*` → `<em>text</em>` (bold과 충돌 방지: bold 먼저 처리)
- [x] Link — `[text](url)` → `<a href="url">text</a>`
- [x] `<br/>` 보존
- [x] HTML entity 보존 (`&gt;`, `&lt;`, `&amp;`)
- [x] `convert_inline(text: str) -> str` 통합 함수
- [x] `convert_heading_inline(text: str) -> str` — bold 마커 제거, code/link만 변환

#### Task 1.4: XHTML 이미터 구현 (`emitter.py`) ✅

- [x] Heading — level-1 보정, `<h{level-1}>content</h{level-1}>`
- [x] Page title skip — `# Title`이 frontmatter title과 동일하면 건너뛰기
- [x] Paragraph — `<p>convert_inline(content)</p>`
- [x] Code block — `<ac:structured-macro ac:name="code">` + `<ac:parameter ac:name="language">` + CDATA
- [x] List (단일 depth) — `<ul>/<ol>` + `<li><p>convert_inline(item)</p></li>`
- [x] Horizontal rule — `<hr />`
- [x] Frontmatter/import/empty — skip
- [x] HTML block — passthrough
- [x] `emit_block(block: Block, context: dict) -> str` 함수
- [x] `emit_document(blocks: list[Block]) -> str` — 전체 문서 XHTML 조립

#### Task 1.5: 검증 CLI 전환 ✅

- [x] `bin/mdx_to_storage_xhtml_verify_cli.py` 수정: 신규 모듈 import
- [x] `mdx_to_storage_xhtml_fragment()` 함수를 신규 모듈 기반으로 교체
- [x] 기존 `batch-verify` 동작 유지

#### Task 1.6: 단위 테스트 ✅

- [x] `tests/test_mdx_to_storage/test_parser.py`
  - frontmatter 파싱 + title 추출
  - heading 레벨 감지
  - code block 언어 추출
  - 수평선 감지
  - callout 블록 감지
  - figure 블록 감지
  - paragraph fallback
- [x] `tests/test_mdx_to_storage/test_inline.py`
  - bold, italic, code, link 개별 + 조합
  - code span 내부 bold/link 보호
  - HTML entity 보존
- [x] `tests/test_mdx_to_storage/test_emitter.py`
  - heading 레벨 보정
  - page title skip
  - code block CDATA 래핑
  - list ul/ol 생성
  - hr 생성

#### Task 1.7: 베이스라인 검증 ✅

- [x] `batch-verify` 실행하여 현재 pass 수 측정
- [x] 개선된 pass 수 기록 (목표: heading/paragraph/code 위주 간단한 케이스 pass)

**Phase 1 완료 기준:** 단순 MDX 파일(heading + paragraph + list + code)의 XHTML 생성이
구조적으로 원본과 부분 일치. heading 레벨 보정 동작 확인.

---

### Phase 2 — 복합 구조 (4일)

Callout, 이미지, 중첩 리스트, 테이블 등 복합 구조를 구현한다.

#### Task 2.1: Callout → ac:structured-macro ✅ (PR #772)

- [x] Callout body 파싱 — `<Callout>` ~ `</Callout>` 사이 내용을 재귀 파싱
- [x] 타입 역매핑 — `default→tip`, `info→info`, `important→note`, `error→warning`
- [x] XHTML 생성 — `<ac:structured-macro ac:name="{macro_name}"><ac:rich-text-body>{body}</ac:rich-text-body></ac:structured-macro>`
- [x] Callout body 내 다중 paragraph 지원 — 각각 `<p>` 래핑
- [x] Callout body 내 code block 지원 — 중첩 매크로
- [x] Panel with emoji — `<Callout type="info" emoji="🌈">` → `ac:name="panel"` + panelIcon params
- [x] 테스트: `panels` testcase 검증

#### Task 2.2: 이미지/Figure → ac:image ✅ (PR #773)

- [x] Figure 블록 파싱 — `src`, `alt`, `width`, `data-layout` 추출
- [x] 파일명 추출 — `/path/to/image.png` → `image.png` (basename)
- [x] XHTML 생성 — `<ac:image ac:align="center"><ri:attachment ri:filename="..."/></ac:image>`
- [x] Caption 지원 — `<ac:caption><p>caption text</p></ac:caption>`
- [x] `ac:width` 속성 — figure의 width 반영
- [x] 캡션 없는 이미지 지원
- [x] 테스트: 이미지가 포함된 testcase 검증

#### Task 2.3: 중첩 리스트 ✅ (PR #774)

- [x] Indent 기반 깊이 계산 (4칸 = 1 depth)
- [x] Mixed ul/ol 중첩 — 각 depth에서 마커 타입에 따라 `<ul>` 또는 `<ol>` 사용
- [x] `<li><p>content</p>{nested_list}</li>` 구조 생성
- [x] 테스트: `lists` testcase 검증

#### Task 2.4: 테이블 (PR #775 리뷰 대기)

- [ ] HTML 테이블 (`<table>`) — passthrough + 인라인 변환
  - `<td>` 내부의 bold, code 등 인라인 변환 적용
  - list 포함 셀 처리
- [ ] Markdown 테이블 (`| col |`) — 파서에서 감지 + `<table>` XHTML 생성 (P2)
  - header row → `<th>`
  - body rows → `<td>`
  - 셀 내용 인라인 변환

#### Task 2.5: Blockquote (PR #776 리뷰 대기)

- [ ] `>` 시작 줄 감지 → `type="blockquote"`
- [ ] XHTML: `<blockquote><p>content</p></blockquote>`

#### Task 2.6: 검증 속성/구조 필터 구현 (PR #777 리뷰 대기)

> **우선순위 노트:** verify 필터가 없으면 batch-verify에서 pass 수를 측정할 수 없다.
> `ac:macro-id`, `ac:layout` 등의 노이즈가 모든 diff를 실패로 만들기 때문이다.
> Task 2.4~2.5보다 이 Task를 먼저 머지하면 현재까지의 구현 진척도를 즉시 측정할 수 있다.

- [ ] `strip_ignored_attributes()` — 무시 대상 속성 제거
- [ ] `strip_layout_sections()` — `<ac:layout>` 래핑 제거 (내용 보존)
- [ ] `strip_nonreversible_macros()` — TOC, view-file 매크로 제거
- [ ] `strip_decorations()` — `<ac:adf-mark>`, `<ac:inline-comment-marker>` 제거
- [ ] 검증 파이프라인에 필터 통합

#### Task 2.7: 통합 검증

- [ ] `batch-verify` 실행
- [ ] 목표: **21건 중 10건 이상 pass**
- [ ] 실패 케이스 분석 및 우선순위 분류

**점진적 pass 목표:**
- verify 필터(Task 2.6) 적용 직후: ~3건 pass 예상 (1844969501, lists, panels 등 단순 구조)
- 테이블(Task 2.4) 머지 후: +3~5건
- Phase 2 전체 완료 후: 10건 이상

---

### Phase 3 — 마무리 및 검증 (3일)

edge case 처리, 내부 링크, 추가 매크로를 구현하여 pass율을 높인다.

#### Task 3.1: 내부 링크 해석 (`link_resolver.py`)

- [ ] `pages.yaml` 로딩 — 기존 `context.py`의 `load_pages_yaml()` 재사용
- [ ] 상대 경로 → page title 매핑
- [ ] XHTML 생성 — `<ac:link><ri:page ri:content-title="Page Title"/><ac:plain-text-link-body><![CDATA[text]]></ac:plain-text-link-body></ac:link>`
- [ ] 외부 링크 구분 — `http://`, `https://` 시작은 `<a href>` 유지

#### Task 3.2: 추가 매크로

- [ ] `<details><summary>` → `<ac:structured-macro ac:name="expand">`
  - summary → `<ac:parameter ac:name="title">`
  - body → `<ac:rich-text-body>`
- [ ] `<Badge color="X">text</Badge>` → `<ac:structured-macro ac:name="status">`
  - `<ac:parameter ac:name="title">text</ac:parameter>`
  - `<ac:parameter ac:name="colour">Color</ac:parameter>` (대문자 변환)

#### Task 3.3: Edge case 처리

- [ ] 빈 paragraph → `<p />`
- [ ] `<u>text</u>` passthrough
- [ ] Emoticon 텍스트 (✅, 📎 등) 보존
- [ ] `<br/>` → `<br />` — **우선순위 상향 검토:** 다수 testcase에서 `<br/>`가 사용되어 Phase 2 완료 전 처리가 pass율 향상에 유리
- [ ] Multiline paragraph join — 줄바꿈을 공백으로 변환
- [ ] 이미지 파일명 불일치 — 비교 시 `ri:filename` 속성 무시 옵션

#### Task 3.4: CLI 기능 완성

- [ ] `convert` 서브커맨드 — 단일 파일 변환, `-o` 출력 파일
- [ ] `verify` 서브커맨드 — 단일 파일 검증, `--expected`, `--show-diff`
- [ ] `batch-verify` 서브커맨드 — 기존 동작 유지 + 필터 적용

#### Task 3.5: 최종 검증

- [ ] `batch-verify` 실행
- [ ] 목표: **21건 중 18건 이상 pass**
- [ ] 나머지 실패 케이스 원인 문서화

---

### Phase 4 — reverse-sync 통합 (2일)

#### Task 4.1: reverse-sync 파이프라인 통합 PoC

- [ ] 기존 reverse-sync에서 `mdx_to_storage_xhtml_fragment()` 호출부를 신규 모듈로 교체
- [ ] 기존 reverse-sync 테스트 통과 확인

#### Task 4.2: 인터페이스 고정 및 문서화

- [ ] 공개 API 확정: `parse_mdx()`, `emit_document()`, `convert_inline()`
- [ ] README 또는 docstring에 사용법 문서화
- [ ] 지원 매트릭스 문서화 (지원/미지원 MDX 구문)

---

## 핵심 파일 참조

| 파일 | 역할 | 참조 이유 |
|------|------|----------|
| `bin/converter/core.py` | Forward converter (XHTML→MDX) | 모든 변환 규칙의 원본 (1,438줄) |
| `bin/converter/context.py` | 전역 상태, pages.yaml, 링크 해석 | 내부 링크 해석 로직 재사용 (665줄) |
| `bin/xhtml_beautify_diff.py` | XHTML 정규화/diff | 검증에 재사용 (89줄) |
| `bin/reverse_sync/mdx_block_parser.py` | 기존 MDX 블록 파서 | 파서 설계 참조 (130줄) |
| `bin/reverse_sync/mdx_to_xhtml_inline.py` | 기존 블록→XHTML 변환 | 인라인/리스트 변환 참조 (271줄) |
| `tests/testcases/*/page.xhtml` | 기대 XHTML | 검증 기준 |
| `tests/testcases/*/expected.mdx` | 입력 MDX | 변환 입력 |
| `var/pages.yaml` | 페이지 메타데이터 | 내부 링크 변환용 |

## 알려진 제약

1. **이미지 파일명 매핑 불가**: Forward converter가 파일명을 정규화(한글→ASCII 등)하므로,
   MDX의 파일명에서 원본 Confluence 첨부 파일명을 복원할 수 없다.
   검증 시 `ri:filename` 속성을 무시하거나 별도 매핑 파일이 필요하다.

2. **ac:adf-extension 미지원**: 일부 panel(note 등)은 `ac:adf-extension` 포맷을 사용한다.
   초기 버전은 `ac:structured-macro`만 생성. diff에서 해당 패널이 불일치할 수 있다.

3. **Layout 섹션 미생성**: Forward converter가 `<ac:layout>` 래핑을 strip하므로
   역변환 시 layout 정보가 없다. 검증 시 layout을 strip하여 비교한다.

4. **Inline comment marker 미복원**: `<ac:inline-comment-marker>` 내부 텍스트는 보존하되
   마커 자체는 역변환 불가. 검증 시 strip.

## 검증 방법

```bash
# 단위 테스트
cd /Users/jk/workspace/querypie-docs-translation-1/confluence-mdx
pytest tests/test_mdx_to_storage/ -v

# 통합 검증 (21건 테스트케이스)
python3 bin/mdx_to_storage_xhtml_cli.py batch-verify \
    --testcases-dir tests/testcases --show-diff-limit 3

# 개별 파일 검증
python3 bin/mdx_to_storage_xhtml_cli.py verify \
    tests/testcases/544375741/expected.mdx \
    --expected tests/testcases/544375741/page.xhtml --show-diff
```

## 리스크 및 대응

| 리스크 | 영향 | 대응 |
|--------|------|------|
| `ac:structured-macro` vs `ac:adf-extension` 혼재 | Panel 비교 실패 | `ac:structured-macro` 기본, `ac:adf-extension`은 후속 |
| 이미지 파일명 불일치 | 이미지 요소 비교 실패 | 검증 시 `ri:filename` 무시 옵션 |
| Callout 내 복잡 구조 (중첩 매크로) | 변환 누락 | 재귀 파싱으로 body 내 블록 처리 |
| MDX 사용자 정의 컴포넌트 다변성 | 미지원 구문 발생 | 지원 매트릭스 문서화 + skip 정책 |
| Layout 섹션 구조 차이 | 전체 diff 노이즈 | 비교 전 layout strip |

## 산출물

- `bin/mdx_to_storage/` — 신규 변환 모듈 (parser, inline, emitter)
- `bin/mdx_to_storage_xhtml_cli.py` — 개선된 CLI (convert, verify, batch-verify)
- `tests/test_mdx_to_storage/` — 단위 테스트
- 프로젝트 계획 문서 (본 문서) — 지속 업데이트

## 다음 액션

- [x] ~~`confluence-mdx` 내 구현 브랜치 생성 (`feat/mdx-to-storage-xhtml`)~~
- [x] ~~Phase 1 구현 완료: 모듈 구조 → 파서 → 인라인 → 이미터 → CLI 전환~~
- [x] ~~Phase 1 batch-verify 결과 기록~~
- [ ] PR #775~#777 리뷰 및 머지 (Task 2.4~2.6)
- [ ] Task 2.6 (verify 필터) 우선 머지 → batch-verify 재측정으로 진척 확인
- [ ] Task 2.7 통합 검증 실행 — 10건 이상 pass 목표
- [ ] Phase 3 착수: 내부 링크 해석(Task 3.1) 구현

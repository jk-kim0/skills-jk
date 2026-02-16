---
id: querypie-docs-mdx-to-storage-xhtml-cli
title: QueryPie Docs MDX -> Confluence Storage XHTML CLI
status: active
repos:
  - https://github.com/querypie/querypie-docs
created: 2026-02-15
updated: 2026-02-18
---

# QueryPie Docs MDX -> Confluence Storage XHTML CLI

## 목표

`../querypie-docs-translation-1/confluence-mdx` 기반으로, MDX 문서를 Confluence Storage Format(XHTML)으로 변환하는 모듈을 구현한다.

핵심 요구사항:
- 문서 의미(구조/매크로/링크/코드)를 보존하는 변환
- 배치 실행 및 검증 가능한 테스트 체계 구축
- reverse-sync에서 재사용 가능한 변환 모듈 제공

## 아키텍처

```
MDX 입력
  │
  ├─ 1. 전처리: frontmatter 파싱(title 추출), import 제거
  │
  ├─ 2. 블록 파싱: line-based parser → Block[]
  │     (heading, paragraph, list, code_block, callout,
  │      figure, table, blockquote, html_block, hr, empty)
  │
  ├─ 3. 블록별 XHTML 생성: Block → XHTML string
  │     ├─ 인라인 변환: **bold**, *italic*, `code`, [link](), <br/> 등
  │     └─ 구조 변환: Callout→macro, figure→ac:image, table→<table>
  │
  └─ 4. XHTML 조립: 모든 블록의 XHTML을 연결
```

**IR 레이어 없음.** Block 타입은 dataclass:

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
├── mdx_to_storage_xhtml_verify_cli.py   # 검증 CLI (배치/단건 검증 + 분석 리포트)
├── xhtml_beautify_diff.py               # XHTML 정규화 + unified diff
├── mdx_to_storage/
│   ├── __init__.py                      # 공개 API: parse_mdx, emit_document, Block
│   ├── parser.py                        # MDX → Block[] 파싱 (400줄)
│   ├── emitter.py                       # Block → XHTML 문자열 생성 (318줄)
│   └── inline.py                        # 인라인 MDX → XHTML 변환 (63줄)
└── reverse_sync/
    └── mdx_to_storage_xhtml_verify.py   # 검증 유틸 (정규화 필터 + 분석) (257줄)

tests/
├── test_mdx_to_storage/
│   ├── test_parser.py                   # 27 tests
│   ├── test_inline.py                   # 9 tests
│   └── test_emitter.py                  # 46 tests
├── test_mdx_to_storage_xhtml_verify.py  # 16 tests (필터 + 분석)
└── test_mdx_to_storage_xhtml_verify_cli.py  # 8 tests
```

## 변환 규칙

### Block 레벨 (parser.py + emitter.py)

| # | MDX 입력 | XHTML 출력 | 상태 |
|---|---------|-----------|------|
| 1 | `## Heading` | `<h1>Heading</h1>` (레벨 -1 보정) | ✅ |
| 2 | `# Title` (page title) | skip (XHTML 미포함) | ✅ |
| 3 | 일반 텍스트 | `<p>inline content</p>` | ✅ |
| 4 | `* item` / `1. item` | `<ul><li><p>...</p></li></ul>` (중첩 포함) | ✅ |
| 5 | ` ```lang ` | `<ac:structured-macro ac:name="code">` + CDATA | ✅ |
| 6 | `<Callout type="X">` | `<ac:structured-macro ac:name="Y"><ac:rich-text-body>` | ✅ |
| 7 | `<figure><img>` | `<ac:image><ri:attachment>` | ✅ |
| 8 | `______` | `<hr />` | ✅ |
| 9 | `\| col \|` 마크다운 테이블 | `<table><tbody><tr><td><p>` | ✅ |
| 10 | `<table>` HTML 테이블 | XHTML로 보존 (인라인만 변환) | ✅ |
| 11 | `> blockquote` | `<blockquote><p>` | ✅ |
| 12 | `<details><summary>` | `<ac:structured-macro ac:name="expand">` | Phase 3 |
| 13 | `<Badge color="X">` | `<ac:structured-macro ac:name="status">` | Phase 3 |

### Inline 레벨 (inline.py)

| # | MDX | XHTML | 상태 |
|---|-----|-------|------|
| 1 | `**text**` | `<strong>text</strong>` | ✅ |
| 2 | `*text*` | `<em>text</em>` | ✅ |
| 3 | `` `text` `` | `<code>text</code>` | ✅ |
| 4 | `[text](url)` | `<a href="url">text</a>` (외부 링크) | ✅ |
| 5 | `[text](relative)` | `<ac:link><ri:page ri:content-title="...">` (내부 링크) | Phase 3 |
| 6 | `&gt;` `&lt;` | 그대로 보존 | ✅ |

### 특수 처리

| 항목 | 처리 | 상태 |
|------|------|------|
| Frontmatter (`---`) | 파싱하여 title 추출, XHTML 출력에 미포함 | ✅ |
| `# Title` | Frontmatter title과 동일하면 skip | ✅ |
| Import 문 | 무시 (skip) | ✅ |
| Callout 타입 역매핑 | `default→tip`, `info→info`, `important→note`, `error→warning` | ✅ |
| Panel with emoji | `<Callout type="info" emoji="🌈">` → `ac:name="panel"` + panelIcon | ✅ |
| Heading 레벨 보정 | `##`→`<h1>`, `###`→`<h2>`. 1단계 감소 | ✅ |
| Heading 내 bold | `**text**` 마커 제거 (forward converter가 strip하므로) | ✅ |

## 검증 파이프라인

### 정규화 필터 (4단계)

1. **구조 제거:** `<ac:layout>`, `<ac:layout-section>`, `<ac:layout-cell>` 래핑 제거 (내용 보존)
2. **매크로 제거:** `<ac:structured-macro ac:name="toc">`, `view-file` 등 역변환 불가 매크로 제거
3. **장식 제거:** `<ac:adf-mark>`, `<ac:inline-comment-marker>`, `<colgroup>`, 빈 `<p>` 제거 (내용 보존)
4. **속성 제거:** 무시 대상 속성 19종 제거 (`ac:macro-id`, `ac:local-id`, `local-id`, `ac:schema-version`, `ri:version-at-save`, `ac:original-height`, `ac:original-width`, `ac:custom-width`, `ac:alt`, `ac:layout`, `data-table-width`, `data-layout`, `data-highlight-colour`, `data-card-appearance`, `ac:breakout-mode`, `ac:breakout-width`, `ri:space-key`, `style`, `class`)

정규화 후 `beautify_xhtml()` + unified diff 비교.

### CLI 사용법

```bash
# 단위 테스트
cd confluence-mdx
python3 -m pytest tests/test_mdx_to_storage/ tests/test_mdx_to_storage_xhtml_verify.py tests/test_mdx_to_storage_xhtml_verify_cli.py -v

# 배치 검증 + 분석 리포트
python3 bin/mdx_to_storage_xhtml_verify_cli.py \
    --show-analysis \
    --write-analysis-report reports/mdx_to_storage_batch_verify_analysis.md

# 개별 케이스 검증
python3 bin/mdx_to_storage_xhtml_verify_cli.py --case-id 544375741 --show-diff-limit 1

# diff 출력 수 조절
python3 bin/mdx_to_storage_xhtml_verify_cli.py --show-diff-limit 0  # diff 생략
```

## 현재 상태 (2026-02-18)

### 완료된 Phase

| Phase | 범위 | 상태 | PR |
|-------|------|------|-----|
| Phase 1 (Task 1.1~1.7) | 모듈 구조 + 핵심 블록/인라인 | **완료** | #766~#771 |
| Phase 2 (Task 2.1~2.7) | 복합 구조 + 검증 필터 + 통합 검증 | **완료** | #772~#778 |

### 모듈 규모

- 변환 모듈: **781줄** (parser 400 + emitter 318 + inline 63)
- 검증 모듈: **406줄** (verify 257 + verify-cli 149)
- 합계: **1,187줄**

### 테스트 현황

- **총 106개** (parser 27, inline 9, emitter 46, verify 16, verify-cli 8)
- 전체 pass

### Batch verify 결과

- **결과: 0/21 pass**
- 필터 효과: verify_filter_noise 20→1, non_reversible_macro_noise 10→0, table_cell_structure_mismatch 9→2, P2 7→0 (소멸)

**실패 원인 분류:**

| 우선순위 | 건수 | 주요 원인 |
|----------|------|-----------|
| P1 | 10 | `internal_link_unresolved` 8건, `table_cell_structure_mismatch` 2건 |
| P3 | 11 | `other` (아래 근본 원인 분석 참조) |

**P1: `internal_link_unresolved` 8건의 근본 한계:**

Forward converter가 `pages.yaml`에서 대상 페이지를 찾지 못하면 `[text](#link-error)`를 생성한다. 이 시점에서 원본 정보(`ri:content-title`, `ri:space-key`)가 소실된다. 역변환 시 `#link-error`에서 원본 `<ac:link>`를 복원할 수 없다.

대응 전략 (택일):
1. verify 필터에서 `<ac:link>` → `<a>` 변환하여 비교 기준 완화
2. Forward converter 수정: `#link-error` 대신 원본 정보를 보존하는 형식 사용
3. 이 8건을 "알려진 제약"으로 분류하고 pass 목표에서 제외

**P3: `other` 11건의 근본 원인 분석:**

| 근본 원인 | 영향 케이스 | 수정 난이도 |
|-----------|-----------|------------|
| `<ol>`에 `start="1"` 누락 | 5건+ (lists, 544113141, 544381877, 880181257, 544112828) | **trivial** |
| `<br/>` → `<br />` 정규화 미처리 | 10건 (43% — 99회 출현) | **low** |
| `ac:image`가 리스트 내에서 `<figure>`로 출력 | 2건 (544113141, 880181257) | medium |
| `ac:emoticon` → 유니코드 이모지 비가역 변환 | 2건 (544113141, 544381877) | high |
| `<details>` → `expand` 매크로 변환 미구현 | 1건 (544381877) | medium |
| 테이블 셀 내 리스트가 raw markdown으로 출력 | 1건 (544375741) | medium |
| `ac:adf-extension` 패널 vs `ac:structured-macro` 형식 차이 | 1건 (panels) | high |

## Phase 3 — Quick win + 내부 링크 + 매크로

영향도와 난이도 기반으로 태스크를 재배치한다. quick win을 먼저 수확하여 pass율을 조기에 올린다.

#### Task 3.0: Quick win 수정

- [ ] `<ol>` 생성 시 `start="1"` 속성 추가 — 이미터 1줄 수정, 5건+ 영향
- [ ] `<br/>` → `<br />` 정규화 — verify 필터에 추가, 10건 영향
- [ ] `classify_failure_reasons()` 분류기 보강 — `other` 11건을 구체적 카테고리로 재분류
- [ ] batch-verify 재측정 — quick win 효과 확인

#### Task 3.1: 내부 링크 해석 (`link_resolver.py`)

정상 해석된 상대 경로 링크(`[text](../relative/path)`)만 대상. `#link-error` 링크는 별도 전략.

- [ ] `pages.yaml` 로딩 — 기존 `context.py`의 `load_pages_yaml()` 재사용
- [ ] 상대 경로 → page title 역매핑 (path segments → `title_orig`)
- [ ] XHTML 생성 — `<ac:link><ri:page ri:content-title="..."/><ac:plain-text-link-body><![CDATA[text]]></ac:plain-text-link-body></ac:link>`
- [ ] 외부 링크 구분 — `http://`, `https://`, `#link-error` 는 `<a href>` 유지

#### Task 3.1b: `#link-error` 대응 전략 결정

- [ ] 대응 전략 택일:
  - (A) verify 필터에서 `<ac:link>` → `<a>` 변환 (비교 기준 완화, 8건 즉시 해소)
  - (B) Forward converter 수정: link text + content-title을 MDX에 보존
  - (C) 8건을 pass 목표에서 제외 (알려진 제약)
- [ ] 선택한 전략 구현

#### Task 3.2: 추가 매크로

- [ ] `<details><summary>` → `<ac:structured-macro ac:name="expand">` (1건 영향)
- [ ] `<Badge color="X">text</Badge>` → `<ac:structured-macro ac:name="status">` (2건, 31회 출현)

#### Task 3.3: Edge case 처리

- [ ] `ac:emoticon` → 유니코드 이모지 비가역 — verify 필터에서 `<ac:emoticon>` strip (2건)
- [ ] 리스트 내 `<figure>` → `<ac:image>` 구조 수정 (2건)
- [ ] 테이블 셀 내 markdown 리스트 → XHTML 리스트 변환 (1건)
- [ ] 이미지 파일명 불일치 — verify 필터에서 `ri:filename` 무시 옵션

#### Task 3.4: 최종 검증

- [ ] batch-verify 실행
- [ ] **목표:** `#link-error` 전략에 따라:
  - 전략 (A) 적용 시: 13건 이상 pass 목표
  - 전략 (C) 적용 시: 8건 이상 pass (13건 중, `#link-error` 8건 제외)
- [ ] 나머지 실패 케이스 원인 문서화

---

### Phase 4 — reverse-sync 통합

#### Task 4.1: reverse-sync 파이프라인 통합 PoC

- [ ] 기존 reverse-sync에서 `mdx_to_storage_xhtml_fragment()` 호출부를 신규 모듈로 교체
- [ ] 기존 reverse-sync 테스트 통과 확인

#### Task 4.2: 인터페이스 고정 및 문서화

- [ ] 공개 API 확정: `parse_mdx()`, `emit_document()`, `convert_inline()`
- [ ] 지원 매트릭스 문서화 (지원/미지원 MDX 구문)

---

## 알려진 제약

1. **`#link-error` 링크 비가역성**: Forward converter가 `pages.yaml`에서 대상 페이지를 찾지 못하면 `[text](#link-error)`를 생성한다. 이 시점에서 원본 `ri:content-title`, `ri:space-key` 정보가 소실되어 역변환으로 복원할 수 없다. 8건의 testcase가 영향.

2. **`ac:emoticon` 비가역 변환**: Forward converter가 `<ac:emoticon ac:name="tick">` → `✔️` (유니코드)로 변환한다. 이모지 shortname 정보가 소실되어 원본 `<ac:emoticon>` 태그를 복원할 수 없다.

3. **`ac:adf-extension` 미지원**: 일부 panel(note 등)은 `ac:adf-extension` 포맷을 사용한다. 현재는 `ac:structured-macro`만 생성. 원본 ADF 구조와 근본적으로 다르다.

4. **이미지 파일명 매핑 불가**: Forward converter가 파일명을 정규화(한글→ASCII 등)하므로, MDX의 파일명에서 원본 Confluence 첨부 파일명을 복원할 수 없다.

5. **Layout 섹션 미생성**: Forward converter가 `<ac:layout>` 래핑을 strip하므로 역변환 시 layout 정보가 없다. 검증 시 layout을 strip하여 비교한다.

6. **Inline comment marker 미복원**: `<ac:inline-comment-marker>` 내부 텍스트는 보존하되 마커 자체는 역변환 불가. 검증 시 strip.

7. **`<ol start="N">` 속성**: Confluence가 `<ol>` 에 자동 부여하는 `start` 속성은 MDX에 정보가 없다. `start="1"`은 기본값이므로 추가 가능하나, continuation numbering(`start="3"` 등)은 복원 불가.

## 핵심 파일 참조

| 파일 | 역할 |
|------|------|
| `bin/mdx_to_storage/parser.py` | MDX → Block[] 파싱 (400줄) |
| `bin/mdx_to_storage/emitter.py` | Block → XHTML 문자열 생성 (318줄) |
| `bin/mdx_to_storage/inline.py` | 인라인 MDX → XHTML 변환 (63줄) |
| `bin/reverse_sync/mdx_to_storage_xhtml_verify.py` | 검증 유틸 + 정규화 필터 + 분석 (257줄) |
| `bin/mdx_to_storage_xhtml_verify_cli.py` | 검증 CLI (149줄) |
| `bin/converter/core.py` | Forward converter XHTML→MDX (1,438줄) |
| `bin/converter/context.py` | 전역 상태, pages.yaml, 링크 해석 (665줄) |
| `var/pages.yaml` | 페이지 메타데이터 (293건) |
| `tests/testcases/*/page.xhtml` | 검증 기준 XHTML |
| `tests/testcases/*/expected.mdx` | 변환 입력 MDX |

## 다음 액션

- [ ] Task 3.0 quick win 구현: `ol start="1"`, `<br/>` 정규화, 분류기 보강
- [ ] Task 3.1b `#link-error` 대응 전략 결정
- [ ] Task 3.1 내부 링크 해석 (정상 경로만)
- [ ] Task 3.2 매크로 구현 (details, Badge)
- [ ] Task 3.4 최종 검증 — batch-verify pass 목표 재측정

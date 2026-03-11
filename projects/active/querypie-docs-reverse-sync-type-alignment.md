---
id: querypie-docs-reverse-sync-type-alignment
title: "Reverse Sync: generate_sidecar_mapping 타입 기반 정렬"
status: active
repos:
  - https://github.com/querypie/querypie-docs
created: 2026-03-11
updated: 2026-03-11
---

# Reverse Sync: generate_sidecar_mapping 타입 기반 정렬

> **Target Repo:** querypie/querypie-docs (confluence-mdx/)
> **상위 프로젝트:** [Confluence ↔ MDX 양방향 변환 시스템](querypie-docs-confluence-mdx.md)
> **배경:** [Sidecar Mapping 재설계](../done/querypie-docs-reverse-sync-mapping-redesign.md)

---

## 배경

[Sidecar Mapping 재설계](../done/querypie-docs-reverse-sync-mapping-redesign.md)에서 reverse sync의 fuzzy text matching을 sidecar lookup으로 교체했다. 그러나 `generate_sidecar_mapping()` 내부는 여전히 텍스트 비교로 XHTML–MDX 블록을 대응시키고, sidecar miss 시 `_find_containing_mapping()` 텍스트 포함 검색 폴백이 남아 있다 (querypie-docs#694).

forward converter는 XHTML DOM을 순서대로 처리하여 MDX를 같은 순서로 출력하므로, **타입 호환성 기반 순차 정렬**으로 텍스트 비교 없이 매핑할 수 있다.

### 현재 데이터로 검증한 근거

실제 mapping.yaml 6,733건 분석 결과:

| xhtml_type | has_mdx | no_mdx | no_mdx 원인 |
|---|---|---|---|
| paragraph | 2,493 | 10 | 빈 `<p>` |
| heading | 1,572 | 39 | 텍스트 매칭 cascade 실패 |
| html_block | 825 | 408 | `ac:image` 257건 + `hr` 93건 + `toc` 56건 + 기타 2건 |
| list | 1,104 | 28 | 텍스트 매칭 실패 |
| code | 147 | 7 | 텍스트 매칭 실패 |
| table | 87 | 13 | 텍스트 매칭 실패 |

**408건의 html_block no_mdx 중 352건(86%)이 텍스트 매칭 실패** (ac:image, hr 등 텍스트 없는 요소). 타입 정렬이면 이들은 모두 정상 매칭됨.

## 목표

1. `generate_sidecar_mapping()`에서 텍스트 비교 제거
2. mapping.yaml에 MDX line range + children 매핑 추가 (v2 → v3)
3. 소비자의 `_find_containing_mapping`, `_resolve_child_mapping` 제거

## 핵심 파일

| 파일 | 역할 |
|------|------|
| `bin/reverse_sync/sidecar.py` | `generate_sidecar_mapping()` 재작성 대상 |
| `bin/reverse_sync/patch_builder.py` | `_find_containing_mapping()` 제거, `_resolve_mapping_for_change()` 수정 |
| `bin/reverse_sync/list_patcher.py` | `_resolve_child_mapping()` 제거 |
| `bin/mdx_to_storage/parser.py` | `Block.line_start/line_end/children` — 이미 존재, 변경 없음 |
| `bin/reverse_sync/mapping_recorder.py` | 변경 없음 (XHTML 측 구조 유지) |
| `bin/text_utils.py` | `normalize_mdx_to_plain()` — 매칭 호출만 제거, 함수 유지 |

---

## Phase 1: `generate_sidecar_mapping()` 재작성

### 타입 호환 매핑 테이블

```python
# XHTML record_mapping type → 호환 MDX parse_mdx type
_TYPE_COMPAT = {
    'heading':    {'heading'},
    'paragraph':  {'paragraph'},
    'list':       {'list'},
    'code':       {'code_block'},
    'table':      {'table', 'html_block'},     # html table → html_block
    'html_block': {'callout', 'details', 'html_block', 'blockquote',
                   'figure', 'badge', 'hr'},   # ac:image→figure, <hr/>→hr
}

# MDX 출력을 생성하지 않는 XHTML 매크로 이름
_SKIP_MACROS = {'toc', 'children'}
```

### 순차 정렬 알고리즘

two-pointer로 XHTML top-level 블록과 MDX content 블록을 순차 정렬. 타입 불일치 시 XHTML 블록이 MDX를 생성하지 않은 것으로 판단하고 스킵.

```
for each XHTML top-level mapping:
    if skip macro → emit(mdx_blocks=[], mdx_range=null)
    if empty paragraph → match with empty MDX block
    if type_compatible(xhtml.type, mdx[ptr].type):
        emit(mdx_blocks=[ptr], mdx_range=block.line_start..line_end)
        if compound block (children):
            _align_children() → emit children entries
            advance ptr past children
        ptr++
    else:
        emit(mdx_blocks=[], mdx_range=null)  # XHTML-only block
```

### children 정렬 (`_align_children`)

callout/details의 XHTML children과 MDX `Block.children`을 동일한 타입 정렬로 매핑.

**주의**: MDX callout children의 `line_start`/`line_end`는 **inner content 기준 상대값**.
절대값 변환: `absolute_line = parent.line_start + child.line_start`

검증 결과:
```
callout: lines 7-14
  child paragraph: relative 1 → absolute 7+1=8 ✓
  child list:      relative 3-4 → absolute 10-11 ✓
  child paragraph: relative 6 → absolute 13 ✓
```

### mapping.yaml 스키마 변경 (v2 → v3)

```yaml
version: 3
mappings:
  - xhtml_xpath: "h2[1]"
    xhtml_type: heading
    mdx_blocks: [4]
    mdx_line_start: 8
    mdx_line_end: 8
  - xhtml_xpath: "macro-tip[1]"
    xhtml_type: html_block
    mdx_blocks: [8]
    mdx_line_start: 12
    mdx_line_end: 18
    children:
      - xhtml_xpath: "macro-tip[1]/p[1]"
        xhtml_block_id: "paragraph-6"
        mdx_line_start: 13
        mdx_line_end: 13
      - xhtml_xpath: "macro-tip[1]/ul[1]"
        xhtml_block_id: "list-7"
        mdx_line_start: 14
        mdx_line_end: 17
  - xhtml_xpath: "hr[1]"          # 이전: no_mdx (텍스트 없어서 매칭 실패)
    xhtml_type: html_block
    mdx_blocks: [10]              # 이제: hr 타입으로 정상 매칭
    mdx_line_start: 20
    mdx_line_end: 20
```

---

## Phase 2: 소비자 코드 업데이트

### `SidecarEntry` 확장 (`sidecar.py`)

```python
@dataclass
class SidecarChildEntry:
    xhtml_xpath: str
    xhtml_block_id: str
    mdx_line_start: int = 0
    mdx_line_end: int = 0

@dataclass
class SidecarEntry:
    xhtml_xpath: str
    xhtml_type: str
    mdx_blocks: List[int] = field(default_factory=list)
    mdx_line_start: int = 0
    mdx_line_end: int = 0
    children: List[SidecarChildEntry] = field(default_factory=list)
```

`load_sidecar_mapping()`, `build_mdx_to_sidecar_index()` 도 children 로딩하도록 수정.

### `patch_builder.py` — `_resolve_mapping_for_change()` 수정

- `_resolve_child_mapping()` → sidecar children에서 순서 기반 직접 조회
- `_find_containing_mapping()` → sidecar 매핑이 이미 complete하므로 불필요

### `list_patcher.py` — `build_list_item_patches()` 수정

- parent mapping 검색에서 `_find_containing_mapping()` 제거 → sidecar에서 직접 조회
- 리스트 블록은 children이 없으므로 (XHTML `<li>`는 개별 매핑 안됨) 나머지 로직 유지

### `reverse_sync_cli.py` — sidecar 인덱스 구축 수정

`build_mdx_to_sidecar_index()`가 children도 포함하여 인덱스 구축하도록 수정.

---

## Phase 3: 삭제할 코드

| 위치 | 대상 | 이유 |
|------|------|------|
| `sidecar.py` | `_find_text_match()` (L520-566) | 텍스트 매칭 4단계 |
| `sidecar.py` | `_count_child_mdx_blocks()` (L453-512) | 텍스트 기반 children 수 계산 |
| `sidecar.py` | `_strip_all_ws()` (L515-517) | 위 함수에서만 사용 |
| `patch_builder.py` | `_find_containing_mapping()` (L36-60) | 텍스트 containment 폴백 |
| `patch_builder.py` | `_strip_block_markers()` (L28-33) | 위 함수에서만 사용 |
| `list_patcher.py` | `_resolve_child_mapping()` (L15-76) | 5단계 텍스트 매칭 |
| `list_patcher.py` | PR #888 `<br/>` fallback (L180-191) | 텍스트 매칭 폴백 |

**유지**: `normalize_mdx_to_plain()` — `text_transfer.py`에서 사용 중.

---

## Phase 4: 검증

```bash
# 기존 테스트 전체
cd confluence-mdx && python3 -m pytest tests/ --ignore=tests/test_unused_attachments.py -q

# reverse sync 단건 테스트
make test-reverse-sync-one TEST_ID=<page_id>
make test-reverse-sync-bugs-one TEST_ID=<page_id>

# PR #888 문제 페이지
make test-reverse-sync-one TEST_ID=544380381
```

Phase 1 완료 시: 변경 전후 `generate_sidecar_mapping()` 출력을 비교하는 임시 스크립트로 old/new 매핑의 `xhtml_xpath ↔ mdx_blocks` 비교 (352건의 false no_mdx 해소 확인).

## 구현 순서

1. Phase 1 완료 → 기존 테스트 통과 확인
2. Phase 2 — Phase 1의 mapping.yaml v3 안정화 후 진행
3. Phase 3 (삭제) — Phase 2 완료 후 마지막에 수행

각 Phase에서 문제 발생 시 이전 Phase로 빠르게 롤백 가능.

---

## 진행 로그

| 날짜 | PR | 내용 |
|------|-----|------|
| 2026-03-11 | — | 계획 수립 |

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

## 목표 (확정)

목표는 "의미적으로 비슷한 XHTML" 생성이 아니라, **원문 `page.xhtml`를 byte-equal로 복원**하는 것이다.

- 허용되지 않는 것: 공백, self-closing 표기, attribute 순서, node 구성의 사소한 차이
- 허용되는 것: 없음 (최종 게이트는 byte-equal)

## 핵심 원칙

1. **byte-equal이 유일한 성공 기준이다.** normalize-diff 통과는 성공이 아니다.
2. **정보 보존 책임은 forward pass에 있다.** 역변환으로 복원할 수 없는 정보는 forward 단계에서 sidecar에 기록해야 한다.
3. **block-level splice가 복원의 핵심 메커니즘이다.** document-level hash match → raw return은 캐시일 뿐, 복원 능력의 증명이 아니다.
4. **검증은 splice 경로를 거쳐야 한다.** block-level alignment → splice → stitch를 거친 결과가 byte-equal이어야 sidecar 구조의 정확성을 증명한다.

## 현재 상태 (2026-02-17)

### 완료된 작업

| Phase | 범위 | PR |
|-------|------|----|
| Phase 1 (Task 1.1~1.7) | 모듈 구조 + 핵심 블록/인라인 emitter | #766~#771 |
| Phase 2 (Task 2.1~2.7) | 복합 구조 + normalize-based 검증 | #772~#778 |
| Lossless v1 (R1/R2/R5) | document-level sidecar + trivial rehydrator | #790 |

### 모듈 규모

| 구분 | 줄수 | 구성 |
|------|------|------|
| Forward converter | 2,261줄 | core.py 1,437 + context.py 664 + sidecar_mapping.py 160 |
| Reverse converter | 965줄 | parser.py 473 + emitter.py 397 + inline.py 95 |
| 검증 | 406줄 | verify 257 + verify-cli 149 |
| Lossless roundtrip (v1) | 191줄 | rehydrator.py 48 + byte_verify.py 71 + CLI 72 |
| 테스트 | 147개 pass | 기존 106 + lossless 41 |

### Batch verify 결과

| 검증 기준 | 결과 | 비고 |
|-----------|------|------|
| normalize-diff (기존) | **0/21 pass** | emitter 단독 출력 |
| document-level sidecar (PR #790) | **21/21 pass** | MDX 미변경 시 원본 XHTML 그대로 반환 (trivial) |
| block-level splice | **미구현** | |

### 실패 원인 분포 (emitter 단독 기준)

| 원인 | 건수 | 비가역 여부 |
|------|------|-------------|
| `ordered_list_start_mismatch` | 12 | emitter 수정 가능 |
| `internal_link_unresolved` (`#link-error`) | 7 | **비가역** — forward에서 원본 정보 소실 |
| `attachment_filename_mismatch` | 7 | **비가역** — forward에서 파일명 정규화 |
| `image_block_structure_mismatch` | 5 | emitter 수정 가능 |
| `emoticon_representation_mismatch` | 4 | **비가역** — forward에서 shortname 소실 |
| `adf_extension_panel_mismatch` | 3 | **비가역** — ADF 구조가 MDX에 없음 |

## 왜 emitter만으로는 byte-equal 불가능한가

Forward converter(XHTML→MDX)는 변환 과정에서 **비가역적 정보 손실**을 일으킨다. 이 정보는 MDX에 존재하지 않으므로, reverse converter(MDX→XHTML)가 아무리 정교해도 원본을 복원할 수 없다.

### 비가역 정보 손실 목록

| # | 소실 항목 | Forward converter 동작 | MDX에 남는 정보 | 복원 불가 이유 |
|---|----------|----------------------|-----------------|---------------|
| 1 | `ac:emoticon` shortname | `<ac:emoticon ac:name="tick">` → `✔️` | 유니코드 이모지 | shortname → emoji 매핑이 다대일 |
| 2 | `ri:filename` 원본명 | `스크린샷 2024-08-01.png` → `screenshot-20240801.png` | 정규화된 파일명 | 원본 유니코드 파일명 소실 |
| 3 | `ac:link` target | pages.yaml 누락 시 `[text](#link-error)` | `#link-error` 텍스트 | `ri:content-title`, `ri:space-key` 소실 |
| 4 | `ac:adf-extension` | ADF panel → 단순 Callout | Callout 구문만 존재 | ADF node 구조, adf-mark, adf-content 전체 소실 |
| 5 | `ac:layout` 래핑 | layout-section/cell strip | 래핑 없음 | 레이아웃 구조 소실 |
| 6 | `ac:inline-comment-marker` | marker strip, 내부 텍스트만 보존 | 텍스트만 | ref, 마커 범위 소실 |
| 7 | `ac:macro-id` 등 속성 19종 | 속성 strip | 없음 | Confluence 내부 ID 소실 |
| 8 | Attribute 순서 | DOM 파싱 시 순서 비보장 | N/A | XML spec상 순서 미정의 |
| 9 | Self-closing 표기 | `<br/>` vs `<br />` 혼재 | `<br/>` 고정 | 원본 표기법 소실 |
| 10 | Inter-block 공백/개행 | 변환 시 정규화 | N/A | 원본 공백 패턴 소실 |

**결론**: emitter 개선으로 해결 가능한 항목(ol start, image 구조 등)과, **본질적으로 forward pass에서 정보를 보존해야만 해결 가능한 항목**이 혼재한다. Sidecar 없이는 byte-equal 불가능.

## 아키텍처

### 전체 흐름

```
FORWARD PASS (XHTML → MDX + sidecar v2)
═══════════════════════════════════════

page.xhtml ──→ DOM parse ──→ top-level node 추출
                   │
                   ├─ 각 node의 raw XHTML fragment 추출 (outerHTML 원문)
                   │
                   ├─ 각 node → MDX 변환 (기존 converter)
                   │   └─ 변환 중 소실 정보를 per-block metadata에 기록
                   │
                   ├─ inter-node separator 기록 (원본 공백/개행)
                   │
                   └─ 출력:
                       ├─ expected.mdx (기존과 동일)
                       └─ expected.roundtrip.json (sidecar v2)


REVERSE PASS (MDX + sidecar v2 → XHTML)
═══════════════════════════════════════

expected.mdx + sidecar v2
    │
    ├─ MDX parse → Block[] (기존 parser.py)
    │
    ├─ Block alignment:
    │   MDX Block[i] ↔ Sidecar Block[j]
    │   (content hash + 위치 기반 매칭)
    │
    ├─ Block별 처리:
    │   ├─ hash 일치 → sidecar.blocks[j].xhtml_fragment 그대로 사용
    │   └─ hash 불일치 → emitter(기존) + lost_info metadata로 보정
    │
    └─ 문서 조립 (stitch):
        envelope.prefix + fragments + separators + envelope.suffix


VERIFICATION
═══════════════════════════════════════

output.xhtml vs page.xhtml → byte comparison
  ├─ 일치: PASS
  └─ 불일치: FAIL + first mismatch offset + context
```

### 핵심 설계 결정

**Q: 왜 document-level cache가 아니라 block-level splice인가?**

Document-level cache(`mdx_sha256 일치 → raw_xhtml 반환`)는 MDX가 단 1바이트라도 변경되면 전체 fallback된다. 실 사용 시나리오(번역, 수정)에서 MDX는 반드시 편집되므로, document-level cache는 실용성이 없다.

Block-level splice는:
- 편집되지 않은 블록은 원본 XHTML fragment를 그대로 보존
- 편집된 블록만 re-emit
- 문서의 대부분이 보존되는 일반적 편집 시나리오에서 byte-equal 비율 극대화

**Q: 왜 검증에서 splice 경로를 강제하는가?**

Document-level cache로 21/21 pass를 달성하는 것은 자명하며, sidecar 구조의 정확성을 증명하지 못한다. 검증 시 block-level splice 경로를 거쳐야:
- sidecar의 block 분할이 올바른지
- block alignment가 정확한지
- separator 보존이 정확한지
- stitch 결과가 byte-equal인지

를 모두 검증할 수 있다.

## Sidecar v2 스키마

```json
{
  "schema_version": "2",
  "page_id": "544381877",
  "mdx_sha256": "<전체 MDX SHA256>",
  "source_xhtml_sha256": "<전체 XHTML SHA256>",

  "blocks": [
    {
      "block_index": 0,
      "xhtml_xpath": "/body/h1",
      "xhtml_fragment": "<h1>Page Title</h1>",
      "mdx_content_hash": "<이 블록에 대응하는 MDX content의 SHA256>",
      "mdx_line_range": [3, 3],
      "lost_info": {}
    },
    {
      "block_index": 1,
      "xhtml_xpath": "/body/p[1]",
      "xhtml_fragment": "<p>Text with <ac:emoticon ac:name=\"tick\"/> inside.</p>",
      "mdx_content_hash": "<hash>",
      "mdx_line_range": [5, 5],
      "lost_info": {
        "emoticons": [
          {
            "mdx_text": "\u2714\ufe0f",
            "shortname": "tick",
            "raw_xhtml": "<ac:emoticon ac:name=\"tick\" ac:emoji-shortname=\":check_mark:\"/>"
          }
        ]
      }
    }
  ],

  "separators": ["", "\n", "\n"],

  "document_envelope": {
    "prefix": "",
    "suffix": "\n"
  }
}
```

### 스키마 필드 설명

| 필드 | 용도 |
|------|------|
| `blocks[].xhtml_fragment` | 원본 XHTML의 해당 블록 raw text. splice 시 그대로 사용 |
| `blocks[].mdx_content_hash` | 대응 MDX 블록의 SHA256. 변경 여부 판단용 |
| `blocks[].mdx_line_range` | expected.mdx에서의 줄 범위 `[start, end]`. alignment 보조 |
| `blocks[].lost_info` | forward 변환 시 소실된 정보. changed block re-emit 시 사용 |
| `separators[i]` | `blocks[i]`와 `blocks[i+1]` 사이의 원본 텍스트. stitch 시 사용 |
| `document_envelope` | 첫 블록 앞(`prefix`), 마지막 블록 뒤(`suffix`)의 원본 텍스트 |

### Sidecar 무결성 불변식

아래 조건이 항상 성립해야 sidecar의 block 분할이 올바름을 보장한다:

```
envelope.prefix
+ blocks[0].xhtml_fragment
+ separators[0]
+ blocks[1].xhtml_fragment
+ separators[1]
+ ...
+ blocks[N-1].xhtml_fragment
+ envelope.suffix
== page.xhtml  (byte-equal)
```

이 불변식은 sidecar 생성 직후 검증한다.

### `lost_info` 하위 필드

| 필드 | 대상 | 저장 내용 |
|------|------|----------|
| `emoticons[]` | `ac:emoticon` 태그 | shortname, raw XHTML |
| `links[]` | `#link-error` 링크 | 원본 `ri:content-title`, `ri:space-key`, raw XHTML |
| `filenames[]` | 정규화된 파일명 | 원본 `ri:filename`, 정규화 후 파일명 |
| `adf_extensions[]` | `ac:adf-extension` | raw XHTML 전체 |
| `stripped_attrs` | 제거된 속성 19종 | `{attr_name: value}` dict |
| `layout_wrapper` | `ac:layout` 래핑 | 래핑 구조 raw XHTML |

## 구현 단계

### Phase L1: Sidecar v2 스키마 + Block Fragment 추출 (PR-A)

**목표**: forward pass에서 block-level sidecar v2를 생성하고, fragment 재조립이 byte-equal함을 검증한다.

**태스크**:

1. `sidecar.py`에 v2 스키마 dataclass 추가 (`RoundtripSidecarV2`, `SidecarBlock`)
2. Forward converter의 DOM 파싱 단계에서 top-level node별 raw XHTML fragment 추출
   - BeautifulSoup `node.decode()` 또는 원본 텍스트에서 위치 기반 추출
   - inter-node text (NavigableString)를 separator로 기록
   - document envelope (prefix, suffix) 기록
3. 기존 `sidecar_mapping.py`의 xhtml_xpath ↔ mdx_blocks 매핑을 sidecar v2 blocks에 통합
4. 각 block에 대응하는 MDX content의 hash 계산 및 `mdx_line_range` 기록
5. Sidecar v2 writer CLI: `--write-sidecar-v2` 옵션
6. **Sidecar 무결성 검증기**: fragment + separator 재조립 == page.xhtml (byte-equal)
7. 21 testcase 전체에 대해 sidecar v2 생성 + 무결성 검증

**핵심 난이도**: BeautifulSoup은 HTML을 파싱할 때 원본 텍스트를 변형할 수 있다 (attribute 재정렬, 공백 정규화, self-closing 변환). 원본 byte-equal fragment를 추출하려면 **원본 텍스트에서 위치 기반으로 잘라내거나**, BeautifulSoup이 변형하지 않는 것을 검증해야 한다. 이 문제가 L1의 핵심 기술 과제이다.

**대안 접근**: BeautifulSoup 대신 원본 XHTML 텍스트를 직접 파싱하여 top-level tag boundary를 찾고, 해당 범위를 raw text로 추출. 이 경우 정규식 또는 간단한 tag-depth counter로 구현 가능.

**검증**:
```bash
python3 bin/sidecar_v2_integrity_check.py --testcases-dir tests/testcases
# 결과: 21/21 fragment-reassembly byte-equal
```

**인수 기준**: `envelope.prefix + join(fragments, separators) + envelope.suffix == page.xhtml` for all 21 cases

---

### Phase L2: Block Alignment + Splice Rehydrator (PR-B)

**목표**: MDX 블록과 sidecar 블록을 정렬하고, unchanged 블록은 원본 fragment를 splice하여 byte-equal XHTML을 조립한다.

**태스크**:

1. Block alignment 알고리즘 구현:
   - MDX `parse_mdx()` 결과 Block[]의 각 블록 content hash 계산
   - Sidecar v2 blocks의 `mdx_content_hash`와 순차 비교
   - 결과: `(mdx_block_idx, sidecar_block_idx, matched: bool)` 리스트
2. Splice rehydrator 구현:
   - matched block → `sidecar.blocks[j].xhtml_fragment` 그대로 사용
   - unmatched block → `emitter.emit_block()` fallback
3. Document stitcher 구현:
   - `envelope.prefix + fragment_0 + sep_0 + fragment_1 + sep_1 + ... + envelope.suffix`
4. `rehydrator.py`에 v2 경로 추가 (v1 하위호환 유지)
5. `byte_verify.py`에 `--force-block-splice` 옵션 추가: document-level fast path 비활성화

**검증**:
```bash
python3 bin/mdx_to_storage_xhtml_byte_verify_cli.py \
    --testcases-dir tests/testcases \
    --sidecar-name expected.roundtrip.v2.json \
    --force-block-splice
# 결과: 21/21 byte-equal (block-level splice 경로)
```

**인수 기준**: unchanged MDX에서 block-level splice 경로로 21/21 byte-equal

---

### Phase L3: Forward Converter 정보 보존 강화 (PR-C)

**목표**: forward converter가 변환 중 소실하는 정보를 sidecar v2의 `lost_info`에 기록한다.

**태스크**:

1. `SingleLineParser` 수정 — 소실 정보 수집 콜백 추가:
   - `ac:emoticon`: shortname, emoji-id, raw outerHTML
   - `ac:link` → `#link-error`: 원본 `ri:content-title`, `ri:space-key`, raw outerHTML
   - `ac:inline-comment-marker`: ref, raw outerHTML
2. `MultiLineParser` 수정 — 소실 정보 수집:
   - `ac:adf-extension`: raw outerHTML 전체
   - `ac:layout`: layout structure raw
3. `Attachment` 수정 — 소실 정보 수집:
   - 원본 `ri:filename` (정규화 전)
4. 속성 strip 시 제거된 속성값 수집 (19종)
5. 수집된 정보를 sidecar v2 blocks의 `lost_info`에 기록
6. 21 testcase에 대해 `lost_info` 포함 sidecar v2 재생성

**검증**:
- `#link-error` 케이스의 `lost_info.links`에 원본 `ri:content-title` 존재
- `ac:emoticon` 케이스의 `lost_info.emoticons`에 원본 `shortname` 존재
- `ri:filename` 케이스의 `lost_info.filenames`에 원본 파일명 존재
- 기존 block-level splice 21/21 byte-equal 유지 (regression 없음)

**인수 기준**: 비가역 정보를 포함하는 모든 블록에서 `lost_info`에 해당 원본 정보 존재

---

### Phase L4: Metadata-Enhanced Emitter (PR-D)

**목표**: changed block re-emit 시 `lost_info`를 활용하여 원본에 가까운 XHTML을 생성한다.

**태스크**:

1. Emitter에 `lost_info` 주입 인터페이스 추가 (`emit_block(block, lost_info=None)`)
2. 각 소실 항목별 복원 로직:
   - `emoticons`: 유니코드 이모지 → 원본 `ac:emoticon` 태그로 치환
   - `links`: `#link-error` → 원본 `ac:link` 태그로 치환
   - `filenames`: 정규화 파일명 → 원본 `ri:filename`으로 치환
   - `adf_extensions`: Callout → 원본 `ac:adf-extension` raw로 치환
   - `stripped_attrs`: 제거된 속성 복원
3. Partial edit 테스트 시나리오 구현:
   - 21 testcase 중 3건 선택 (lists, panels, 544211126)
   - MDX의 한 블록 텍스트만 수정
   - 나머지 unchanged 블록이 byte-equal인지 확인
   - 수정 블록이 well-formed XHTML인지 확인

**검증**:
```bash
python3 -m pytest tests/test_lossless_roundtrip_partial_edit.py -v
```

**인수 기준**: partial edit 시 unchanged blocks byte-equal 유지 + changed blocks well-formed

---

### Phase L5: Emitter 정확도 향상 (PR-E)

**목표**: emitter 자체의 XHTML 생성 정확도를 높인다 (sidecar fallback 시 품질 향상).

**태스크** (기존 Phase 3 quick win 흡수):

1. `<ol>` 생성 시 `start="1"` 속성 추가 (12건 영향)
2. `<br/>` → `<br />` 표기 통일 (원본 Confluence 패턴 준수)
3. 리스트 내 `<ac:image>` 구조 수정 (5건 영향)
4. `<details><summary>` → `expand` 매크로 구현
5. `<Badge>` → `status` 매크로 구현
6. 내부 링크 해석 개선 (`link_resolver.py`)

**검증**:
- emitter 단독 normalize-diff 결과 개선 (0/21 → 목표 미설정, 보조 지표)
- block-level splice 21/21 byte-equal 유지

**인수 기준**: emitter 개선 항목별 단위 테스트 통과

---

### Phase L6: CI Gate 전환 (PR-F)

**목표**: byte-equal 검증을 CI의 기본 게이트로 설정한다.

**태스크**:

1. byte-verify CLI를 CI 스크립트에 통합
2. 기존 normalize-verify를 `--diagnostic` 모드로 전환 (실패 원인 분석용)
3. CI 설정: byte mismatch → build fail, exit code 1
4. 문서 갱신: README, CLI help에서 목표를 byte-equal로 통일

**검증**:
```bash
# CI gate
python3 bin/mdx_to_storage_xhtml_byte_verify_cli.py \
    --testcases-dir tests/testcases \
    --sidecar-name expected.roundtrip.v2.json \
    --force-block-splice
echo $?  # 0 = all pass, 1 = any fail
```

**인수 기준**: CI pipeline에서 byte-equal gate 활성화, 21/21 pass

## 검증 방법론

### 1차 게이트: byte-equal (유일한 성공 기준)

```
output.xhtml (bytes) == page.xhtml (bytes)
```

비교 방식: `output.encode('utf-8') == expected.encode('utf-8')`

실패 출력:
```
FAIL case=544381877 offset=1423
  expected: ...tion ac:name="tick" ac:emoji-short...
  actual:   ...tion>✔️</ac:emoticon>...
```

### 검증 경로 (block-level splice 강제)

테스트에서는 **반드시 block-level splice 경로**를 사용한다:

1. MDX를 `parse_mdx()`로 Block[] 생성
2. 각 Block의 content hash를 sidecar block의 `mdx_content_hash`와 비교
3. matched → sidecar의 `xhtml_fragment` 사용
4. unmatched → `emitter.emit_block()` fallback
5. separator + envelope로 stitch
6. 결과를 `page.xhtml`과 byte 비교

Document-level fast path(`mdx_sha256 일치 → raw_xhtml 반환`)는 production shortcut이며, **검증에서는 사용하지 않는다.**

### 보조 지표 (디버깅용, 성공 판정 불가)

- normalize-diff: 의미적 차이 분석 (byte 불일치의 원인 추적용)
- failure reason 분류: 소실 항목별 건수 (sidecar 설계 피드백용)

## 기존 모듈 활용 계획

| 모듈 | 현재 역할 | 변경 후 역할 |
|------|----------|-------------|
| `parser.py` | MDX → Block[] | **유지**. block hash 계산 + alignment 입력 |
| `emitter.py` | Block → XHTML | **유지**. changed block fallback renderer |
| `inline.py` | 인라인 변환 | **유지**. emitter 하위 모듈 |
| `link_resolver.py` | 링크 해석 | **유지**. emitter fallback 시 사용 |
| `sidecar.py` | v1 document-level | **확장**: v2 block-level sidecar 추가 |
| `sidecar_mapping.py` | mapping.yaml 생성 | **확장**: sidecar v2 block entries 생성에 활용 |
| `rehydrator.py` | v1 document-level | **확장**: v2 block-level splice 경로 추가 |
| `byte_verify.py` | byte 비교 | **확장**: `--force-block-splice` 옵션 |
| `mdx_to_storage_xhtml_verify.py` | normalize-diff 검증 | **강등**: diagnostic 모드 |
| `mdx_to_storage_xhtml_verify_cli.py` | normalize-diff CLI | **강등**: `--diagnostic` 전용 |

## 완료 기준 (DoD)

1. `tests/testcases/*` 전체에서 **block-level splice 경로**로 `output.xhtml == page.xhtml` (byte-equal)
2. "known limitation"으로 제외되는 케이스 **없음**
3. Partial edit 시나리오에서 unchanged blocks byte-equal 유지
4. CI가 byte mismatch를 즉시 fail 처리
5. Sidecar 없는 경우 lossless 미보장을 명시적으로 경고 처리

## 핵심 파일 참조

| 파일 | 역할 | 줄수 |
|------|------|------|
| `bin/converter/core.py` | Forward converter XHTML→MDX | 1,437 |
| `bin/converter/context.py` | 전역 상태, pages.yaml, 링크 해석 | 664 |
| `bin/converter/sidecar_mapping.py` | XHTML↔MDX block 매핑 생성 | 160 |
| `bin/mdx_to_storage/parser.py` | MDX → Block[] 파싱 | 473 |
| `bin/mdx_to_storage/emitter.py` | Block → XHTML 문자열 생성 | 397 |
| `bin/mdx_to_storage/inline.py` | 인라인 MDX → XHTML 변환 | 95 |
| `bin/mdx_to_storage/link_resolver.py` | 내부 링크 해석 | ~100 |
| `bin/lossless_roundtrip/sidecar.py` | Sidecar 스키마 + IO | 72 |
| `bin/lossless_roundtrip/rehydrator.py` | Rehydration 로직 | 48 |
| `bin/lossless_roundtrip/byte_verify.py` | Byte-equal 검증 | 71 |
| `bin/reverse_sync/mdx_to_storage_xhtml_verify.py` | Normalize-diff 검증 (diagnostic) | 257 |
| `bin/mdx_to_storage_xhtml_verify_cli.py` | 검증 CLI | 149 |
| `var/pages.yaml` | 페이지 메타데이터 | 293건 |
| `tests/testcases/*/page.xhtml` | 검증 기준 XHTML (원본) | 21+건 |
| `tests/testcases/*/expected.mdx` | 변환 입력 MDX | 21+건 |
| `tests/testcases/*/mapping.yaml` | XHTML↔MDX block 매핑 (기존) | 21+건 |

## 즉시 다음 액션

- [ ] Phase L1 시작: sidecar v2 스키마 dataclass 정의
- [ ] Forward converter에서 DOM node별 raw fragment 추출 PoC (BeautifulSoup 변형 여부 확인)
- [ ] 3건 testcase (`lists`, `panels`, `544211126`)로 fragment reassembly byte-equal 확인

---
id: querypie-docs-confluence-mdx
title: "QueryPie Docs: Confluence ↔ MDX 양방향 변환 시스템"
status: active
repos:
  - https://github.com/querypie/querypie-docs
replaces:
  - querypie-docs-reverse-sync-phase2
  - querypie-docs-mdx-to-storage-xhtml-cli
  - querypie-docs-reverse-sync-code-review
created: 2026-02-17
updated: 2026-02-18
---

# QueryPie Docs: Confluence ↔ MDX 양방향 변환 시스템

> **Target Repo:** [querypie/querypie-docs/confluence-mdx](https://github.com/querypie/querypie-docs/tree/main/confluence-mdx)
> **아키텍처:** [confluence-mdx/docs/architecture.md](https://github.com/querypie/querypie-docs/blob/main/confluence-mdx/docs/architecture.md)
> **이전 문서:** [reverse-sync-phase2](querypie-docs-reverse-sync-phase2.md) | [mdx-to-storage-xhtml-cli](querypie-docs-mdx-to-storage-xhtml-cli.md) | [code-review](querypie-docs-reverse-sync-code-review.md)

---

## 용어 정의

[architecture.md](https://github.com/querypie/querypie-docs/blob/main/confluence-mdx/docs/architecture.md)의 용어를 따른다.

| 용어 | 방향 | 패키지 | 설명 |
|------|------|--------|------|
| **Forward Conversion (정순변환)** | XHTML → MDX | `converter/` | Confluence XHTML을 MDX로 변환 |
| **Backward Conversion (역순변환)** | MDX → XHTML | `mdx_to_storage/` | MDX를 Confluence Storage XHTML로 변환 |
| **Reverse Sync (역반영)** | MDX 편집 → Confluence 반영 | `reverse_sync/` | MDX 교정 내용을 Confluence에 반영하는 파이프라인 |
| **Round Trip Verification (라운드트립 검증)** | MDX → XHTML → MDX → 비교 | — | 역순변환 결과를 정순변환하여 원본 MDX와 비교 |
| **Mapping Sidecar** | — | `var/<page_id>/mapping.yaml` | XHTML↔MDX 블록 대응 관계 |
| **Roundtrip Sidecar** | — | `tests/testcases/<case_id>/expected.roundtrip.json` | Byte-exact XHTML 프래그먼트 저장 |

---

## 목표

### 1. Reverse Sync (역반영) — MDX 편집을 Confluence에 반영

AI Agent가 MDX 문서를 교정하면, 해당 변경 사항을 블록 단위로 XHTML 패치로 변환하여 Confluence에 반영한다.

| Phase | 범위 | 상태 |
|-------|------|------|
| Phase 1 | 텍스트 수준 변경 (블록 수 동일) | **완료** |
| Phase 2 | 구조적 변경 (블록 추가/삭제, 헤딩 재구성) | **완료** |
| Phase 2 안정화 | 버그 수정, CLI 개선, 정규화 보완 | **완료** |
| Phase 3 | 전면 재구성 (문서 위치/이름 변경, 페이지 트리) | 미착수 |

### 2. Byte-equal 라운드트립 — 원문 XHTML의 무손실 복원

역순변환(Backward Conversion) 결과가 원본 `page.xhtml`과 **byte-equal**해야 한다. 의미적 유사성이 아닌 바이트 수준 동일성이 유일한 성공 기준이다.

정순변환(Forward Conversion)은 구조적으로 비가역적 정보 손실을 일으키므로, 역순변환기(Backward Converter) 단독으로는 byte-equal을 달성할 수 없다. **Roundtrip Sidecar**에 원본 XHTML 프래그먼트를 보존하고, block-level splice로 복원하는 것이 핵심 메커니즘이다.

| Phase | 범위 | 상태 |
|-------|------|------|
| Phase 1 | 핵심 블록/인라인 emitter | **완료** |
| Phase 2 | 복합 구조 + normalize 기반 검증 | **완료** |
| Lossless v1 | Document-level sidecar + trivial rehydrator | **완료** |
| Phase L0 | 코드 통합 (lossless_roundtrip → reverse_sync 흡수) | **완료** (#791) |
| Phase L1 | Roundtrip Sidecar v2 + block fragment 추출 | **완료** (#792) |
| Phase L2 | Block alignment + splice rehydrator | **완료** (#794) |
| Phase L3 | Forward Conversion 정보 보존 강화 | 미착수 |
| Phase L4 | Metadata-enhanced emitter + patcher | 미착수 |
| Phase L5 | Backward Converter 정확도 개선 | **완료** (#799) |
| Phase L6 | CI gate 전환 (byte-equal을 기본 게이트로) | **완료** (#800) |

### 3. 코드 품질 개선

Reverse Sync 코드베이스(2,726줄 / 13 모듈)의 구조적 문제를 개선한다.

| 항목 | 상태 |
|------|------|
| `patch_builder.py` 테스트 확충 (7→52) | **완료** |
| `_INVISIBLE_RE` 정규식 통합 | **완료** |
| `text_transfer.py`, `text_normalizer.py` 테스트 추가 (59건) | **완료** |
| `mapping_recorder.py` 중복 제거 (232→210줄) | **완료** |
| CLI 통합 (`mdx_to_storage_xhtml_cli.py` 단일 진입점) | **완료** (#796) |
| 텍스트 유틸리티 통합 (`text_normalizer.py` → `text_utils.py`) | **완료** (#796) |
| MDX 파서 통합 (`mdx_block_parser.py` → `parser.py`) | **완료** (#796) |
| 인라인 변환기 통합 (`mdx_to_xhtml_inline` → `mdx_to_storage.inline`) | **완료** (#796) |
| Dead code 삭제 (`sidecar_mapping.py`, `test_verify.py` 등 235줄) | **완료** (#798) |
| `containing_changes` 패턴 공통 함수 추출 | 착수 가능 |
| `build_patches()` 분기 분리 (순환 복잡도 감소) | 착수 가능 |
| `run_verify()` God Function 분리 | 착수 가능 |

---

## 현재 구현 범위

### Reverse Sync (역반영)

역반영 파이프라인은 Phase 2까지 구현이 완료되어, 텍스트 변경과 구조적 변경(블록 추가/삭제)을 모두 처리한다.

**파이프라인 흐름:**

```
원본 MDX (main)    교정된 MDX (작업 브랜치)
      │                    │
      ▼                    ▼
 parse_mdx_blocks()   parse_mdx_blocks()     ← mdx_block_parser.py
      │                    │
      └────────┬───────────┘
               ▼
        diff_blocks()                         ← block_diff.py (SequenceMatcher)
               │
               ▼
        BlockChange[]                         ← modified / added / deleted
               │
      ┌────────┴────────┐
      ▼                 ▼
record_mapping()   Sidecar 인덱스             ← mapping_recorder.py + sidecar.py
      │                 │
      └────────┬────────┘
               ▼
        build_patches()                       ← patch_builder.py
               │
               ▼
        patch_xhtml()                         ← xhtml_patcher.py (delete→insert→modify)
               │
               ▼
        verify_roundtrip()                    ← roundtrip_verifier.py (XHTML→정순변환→MDX→비교)
               │
               ▼
     Confluence API push                      ← confluence_client.py
```

**모듈 구성:**

| 모듈 | 줄 수 | 역할 |
|------|-------|------|
| `reverse_sync_cli.py` | 734 | 오케스트레이터 + CLI |
| `patch_builder.py` | 547 | BlockChange → XHTML 패치 변환 |
| `sidecar.py` | 524 | Roundtrip sidecar + 매핑 인덱스 |
| `xhtml_patcher.py` | 333 | BeautifulSoup으로 XHTML 패치 적용 |
| `mdx_to_xhtml_inline.py` | 240 | 삽입 패치용 MDX → XHTML 블록 변환 (`mdx_to_storage.inline` 활용) |
| `mapping_recorder.py` | 210 | XHTML → BlockMapping 추출 |
| `fragment_extractor.py` | 204 | XHTML byte-exact 프래그먼트 추출 |
| `rehydrator.py` | 149 | Sidecar 기반 무손실 XHTML 복원 |
| `byte_verify.py` | 126 | Byte-equal 검증 |
| `roundtrip_verifier.py` | 174 | 라운드트립 검증 |
| `text_utils.py` | 94 | 텍스트 정규화 유틸리티 (통합) |
| `block_diff.py` | 90 | SequenceMatcher 기반 블록 시퀀스 diff |
| `text_transfer.py` | 79 | 텍스트 변경을 XHTML에 전사 |
| `confluence_client.py` | 65 | Confluence REST API 클라이언트 |

**테스트:** 632 유닛 테스트, 19 E2E 테스트 시나리오

**운영 실적:** 148페이지 배치 verify 100% 통과

### Backward Conversion (역순변환)

MDX를 Confluence Storage Format XHTML로 변환하는 역순변환기이다.

**모듈 구성:**

| 모듈 | 줄 수 | 역할 |
|------|-------|------|
| `mdx_to_storage/parser.py` | 474 | MDX → Block AST 파싱 (줄 단위 상태머신) |
| `mdx_to_storage/emitter.py` | 398 | Block AST → XHTML 생성 |
| `mdx_to_storage/inline.py` | 95 | 인라인 Markdown → XHTML 변환 |
| `mdx_to_storage/link_resolver.py` | 158 | MDX 상대 경로 → `<ac:link>` 변환 |

**Batch verify 결과 (emitter 단독):**

| 검증 기준 | 결과 | 비고 |
|-----------|------|------|
| normalize-diff | **1/21 pass** | emitter 단독 출력 (L5 개선 후) |
| document-level sidecar (Lossless v1) | **21/21 pass** | MDX 미변경 시 원본 XHTML 그대로 반환 |
| L1 fragment reassembly | **21/21 pass** | sidecar v2 프래그먼트 재조립 byte-equal |
| block-level splice (L2) | **21/21 pass** | forced-splice 경로 byte-equal |

### 정순변환 시 비가역 정보 손실

역순변환기 단독으로 byte-equal이 불가능한 근본 원인:

| # | 소실 항목 | 정순변환 동작 | 복원 불가 이유 |
|---|----------|-------------|---------------|
| 1 | `ac:emoticon` shortname | `<ac:emoticon ac:name="tick">` → `✔️` | 다대일 매핑 |
| 2 | `ri:filename` 원본명 | 유니코드 → 정규화 | 원본 파일명 소실 |
| 3 | `ac:link` target | pages.yaml 누락 → `#link-error` | 링크 메타데이터 소실 |
| 4 | `ac:adf-extension` | ADF panel → 단순 Callout | ADF 구조 소실 |
| 5 | `ac:layout` 래핑 | layout-section/cell strip | 래핑 구조 소실 |
| 6 | `ac:inline-comment-marker` | marker strip | 참조/범위 소실 |
| 7 | `ac:macro-id` 등 속성 19종 | 속성 strip | Confluence 내부 ID 소실 |
| 8 | 속성 순서 | DOM 파싱 시 재정렬 | XML spec상 순서 미정의 |
| 9 | Self-closing 표기 | `<br/>` vs `<br />` 혼재 | 원본 표기법 소실 |
| 10 | Inter-block 공백 | 정규화 | 원본 공백 패턴 소실 |

---

## 앞으로 구현할 것

### Phase L2: Block Alignment + Splice Rehydrator

**목표:** MDX 블록과 Roundtrip Sidecar 블록을 해시 매칭하고, 변경되지 않은 블록은 원본 프래그먼트를 그대로 splice한다.

**알고리즘:**

1. MDX → `MdxBlock[]` 파싱 + content 해시 계산
2. 각 `MdxBlock`의 해시를 sidecar 블록의 `mdx_content_hash`와 매칭
3. 매칭된 블록: `sidecar.blocks[j].xhtml_fragment` 그대로 사용
4. 매칭되지 않은 블록: `emitter.emit_block()` 폴백
5. `envelope.prefix` + fragments + separators + `envelope.suffix`로 조립

**인수 기준:** MDX 미변경 시 block-level splice 경로로 21/21 byte-equal

### Phase L3: Forward Conversion 정보 보존 강화

**목표:** 정순변환(Forward Conversion) 과정에서 손실되는 정보를 Roundtrip Sidecar v2의 `lost_info` 필드에 기록한다.

**수집 대상:**

| 필드 | 대상 | 저장 내용 |
|------|------|----------|
| `emoticons[]` | `ac:emoticon` 태그 | shortname, raw XHTML |
| `links[]` | `#link-error` 링크 | 원본 `ri:content-title`, `ri:space-key`, raw XHTML |
| `filenames[]` | 정규화된 파일명 | 원본 `ri:filename` |
| `adf_extensions[]` | `ac:adf-extension` | raw XHTML 전체 |
| `stripped_attrs` | 제거된 속성 19종 | `{attr_name: value}` |
| `layout_wrapper` | `ac:layout` 래핑 | 래핑 구조 raw XHTML |

**인수 기준:** 비가역 정보를 포함하는 모든 블록에서 `lost_info`에 해당 원본 정보 존재 + 기존 splice 21/21 유지

### Phase L4: Metadata-Enhanced Emitter + Patcher

**목표:** 변경된 블록을 재생성할 때 `lost_info`를 활용하여 원본에 가까운 XHTML을 생성한다.

**패치 유형:**

- Emoticon: 유니코드 이모지 → 원본 `<ac:emoticon>` 태그
- 링크: `#link-error` → 원본 `<ac:link>` 태그
- 파일명: 정규화 이름 → 원본 `ri:filename`
- ADF: Callout → 원본 `ac:adf-extension` raw

**인수 기준:** partial edit 시 unchanged blocks byte-equal 유지 + changed blocks well-formed

### Phase L5: Backward Converter 정확도 개선 ✅

**완료** (#799). 3개 항목 개선:

| 항목 | 영향 | 결과 |
|------|------|------|
| `<ol start="1">` 속성 추가 | 12건 | `ordered_list_start_mismatch` 완전 해소 |
| 인라인 `<Badge>` → `status` 매크로 | 2건 | paragraph/list 내 Badge 변환 |
| 리스트 내 `<figure>` → `<ac:image>` 형제 구조 | 5→3건 | 단순 구조 2건 해소 |

나머지 항목(`<br/>` 표기, `<details>` 매핑)은 이미 구현 완료 상태였음. normalize-diff 0/21 → 1/21 pass, splice 21/21 byte-equal 유지.

### Phase L6: CI Gate 전환 ✅

**완료** (#800). byte-equal 검증을 CI의 기본 게이트로 설정:

- `byte_verify` CLI에 `--splice` 플래그 추가 (forced-splice 경로 검증)
- `run-tests.sh`에 `byte-verify` 테스트 타입 추가
- Makefile에 `test-byte-verify` 타겟 추가
- GitHub Actions CI에 `Byte-equal verify` 단계 추가
- byte mismatch → build fail (exit code 1)

검증 결과: fast-path 21/21 pass, forced-splice 21/21 pass

### Reverse Sync Phase 3: 전면 재구성 (설계 미착수)

**목표:** 문서 구조, 위치, 이름 변경을 포함한 전면 재구성을 Confluence에 반영한다.

**필요한 확장:**

- 블록 이동/재정렬 감지 (Phase 2 SequenceMatcher 확장)
- 빈 컨테이너 자동 삭제
- Confluence API 페이지 이동/이름 변경 연동
- 페이지 트리 구조 관리

---

## 검증 방법론

### Reverse Sync 검증: 라운드트립 검증

역반영 파이프라인은 **라운드트립 검증(Round Trip Verification)**으로 정확성을 확인한다:

```
패치된 XHTML ──(정순변환)──▶ 재변환 MDX
      │                         │
      └──── 교정된 MDX와 비교 ───┘
```

- 정규화 항목: trailing whitespace, 날짜 포맷, 테이블 패딩, h1 헤딩, 코드 블록 엔티티
- 운영: `reverse_sync_cli.py verify <mdx>` (dry-run) / `push <mdx>` (반영)
- 배치: `reverse_sync_cli.py --branch <branch>` (브랜치 전체)

### Byte-equal 검증: block-level splice 경로

Byte-equal 라운드트립은 **block-level splice 경로를 강제**하여 검증한다:

```
MDX → parse_mdx_blocks() → MdxBlock[]
                               │
                    content hash 계산 + sidecar 매칭
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
      hash 일치: 원본 fragment         hash 불일치: emitter 폴백
               │                               │
               └───────────────┬───────────────┘
                               ▼
                    envelope + fragments + separators → output.xhtml
                               │
                               ▼
                    output.xhtml == page.xhtml (byte 비교)
```

Document-level fast path(MDX 전체 해시 일치 → 원본 반환)는 production shortcut이며, **검증에서는 사용하지 않는다.** Block-level splice 경로를 거쳐야 sidecar 구조의 정확성을 증명할 수 있다.

**보조 지표 (디버깅용):**

- `mdx_to_storage_xhtml_verify`: normalize-diff (byte 불일치 원인 추적)
- `mdx_to_storage_final_verify`: failure reason 분류 (sidecar 설계 피드백)

### 테스트 데이터

- **21개 실제 QueryPie 페이지**: `tests/testcases/<case_id>/` (page.xhtml, expected.mdx, mapping.yaml)
- **19개 E2E 역반영 시나리오**: 버그 재현 포함
- **632 유닛 테스트**

---

## 완료 기준 (DoD)

### Byte-equal 라운드트립

1. `tests/testcases/*` 전체에서 **block-level splice 경로**로 `output.xhtml == page.xhtml` (byte-equal)
2. "known limitation"으로 제외되는 케이스 없음
3. Partial edit 시 unchanged blocks byte-equal 유지
4. ~~CI가 byte mismatch를 즉시 fail 처리~~ **완료** (#800)
5. ~~`bin/lossless_roundtrip/` 디렉토리 완전 삭제, 모든 기능이 `reverse_sync/`에 통합~~ **완료** (#791)

### Reverse Sync Phase 3

- 별도 설계 후 DoD 정의 예정

---

## 통합 후 모듈 구조

L6 완료 후 현재 모듈 구조 (L3~L4 완료 시 추가 변경 예정):

```
bin/
├── converter/                              # Forward Conversion (정순변환)
│   ├── core.py                             # XHTML → MDX 변환 (L3: lost_info 수집 추가)
│   ├── context.py                          # 전역 상태, pages.yaml
│   └── cli.py                              # 단일 페이지 변환 진입점
│
├── mdx_to_storage/                         # Backward Conversion (역순변환)
│   ├── parser.py                           # MDX → Block AST (emission + diff/alignment 통합)
│   ├── emitter.py                          # Block → XHTML (L5: ol start, Badge, figure 개선)
│   ├── inline.py                           # 인라인 변환 (L5: Badge → status 매크로 추가)
│   └── link_resolver.py                    # 내부 링크 해석
│
├── reverse_sync/                           # Reverse Sync (역반영) + Roundtrip Sidecar
│   ├── sidecar.py                          # ★ 통합: v1+v2 스키마, IO, 인덱스
│   ├── rehydrator.py                       # ★ v1 fast path + v2 block splice
│   ├── byte_verify.py                      # ★ byte-equal 검증 (L6: --splice 지원)
│   ├── fragment_extractor.py               # XHTML byte-exact 프래그먼트 추출
│   ├── mapping_recorder.py                 # XHTML block 추출 (L1: fragment 추가)
│   ├── mdx_block_parser.py                 # backward-compat re-export 래퍼 → parser.py
│   ├── block_diff.py                       # SequenceMatcher 기반 블록 diff
│   ├── patch_builder.py                    # XHTML 패치 생성 (L4: lost_info 패치)
│   ├── xhtml_patcher.py                    # XHTML 패치 적용
│   ├── text_transfer.py                    # 텍스트 변경 전사
│   ├── mdx_to_xhtml_inline.py              # 삽입 패치용 MDX → XHTML (mdx_to_storage.inline 활용)
│   ├── roundtrip_verifier.py               # 라운드트립 검증
│   └── confluence_client.py                # Confluence REST API
│
├── text_utils.py                           # ★ 텍스트 정규화 유틸리티 (통합)
├── reverse_sync_cli.py                     # 역반영 CLI
├── mdx_to_storage_xhtml_cli.py             # 역순변환 통합 CLI (convert/verify/batch-verify/final-verify/baseline)
├── mdx_to_storage_roundtrip_sidecar_cli.py # Sidecar 생성 CLI
└── mdx_to_storage_xhtml_byte_verify_cli.py # Byte-equal 검증 CLI (L6: CI gate)
```

---

## 진행 로그

| 날짜 | PR | 내용 |
|------|-----|------|
| 2026-02-18 | querypie-docs#802 | 코드 품질 분석 보고서 전면 갱신 |
| 2026-02-18 | querypie-docs#800 | **Phase L6: byte-equal CI gate 추가** |
| 2026-02-18 | querypie-docs#799 | **Phase L5: Backward Converter 정확도 개선** |
| 2026-02-18 | querypie-docs#798 | Dead code 삭제 + 코드 품질 분석 문서 통합 |
| 2026-02-18 | querypie-docs#796 | 불필요/중복 코드 분석 + CLI 통합 리팩토링 |
| 2026-02-17 | querypie-docs#797 | 아키텍처 문서 L2 완료 상태 반영 |
| 2026-02-17 | querypie-docs#794 | **Phase L2: Block alignment + splice rehydrator** |
| 2026-02-17 | skills-jk#117 | 프로젝트 문서 통합 재작성 |
| 2026-02-17 | querypie-docs#792 | **Phase L1: Roundtrip Sidecar v2 + block fragment 추출** |
| 2026-02-17 | querypie-docs#791 | **Phase L0: 코드 통합 — reverse_sync 패키지 일원화** |
| 2026-02-15 | querypie-docs#790 | Lossless v1: document-level sidecar + trivial rehydrator |
| 2026-02-15 | querypie-docs#778 | Backward Converter Phase 2 완료 |
| 2026-02-15 | querypie-docs#740 | 버그 재현 테스트케이스 17건 + CLI 출력 개선 |
| 2026-02-15 | querypie-docs#734 | 네임스페이스 접두사 유지 + 코드 참조 수정 |
| 2026-02-14 | querypie-docs#724 | verify 실패 재검증 스크립트 + CLI 개선 |
| 2026-02-13 | querypie-docs#704 | **Reverse Sync Phase 2 구현 완료** |
| 2026-02-13 | querypie-docs#701 | Badge/코드 펜스 정규화 + 라운드트립 검증 보완 |
| 2026-02-13 | querypie-docs#700 | mapping_recorder 중복 제거 |
| 2026-02-13 | querypie-docs#699 | patch_builder 테스트 확충 (7→52) |
| 2026-02-13 | querypie-docs#697 | `_INVISIBLE_RE` 통합 + text utility 테스트 59건 |
| 2026-02-13 | querypie-docs#694 | Sidecar 전용 매칭 전환 완료 |
| 2026-02-12 | querypie-docs#688 | Fuzzy matching 제거, sidecar pipeline 전환 |
| 2026-02-12 | querypie-docs#685 | Sidecar mapping lookup 모듈 + 유닛 테스트 |
| 2026-02-12 | querypie-docs#682 | Sidecar mapping 파일 생성 |
| 2026-02-11 | querypie-docs#679 | 오케스트레이터 4개 모듈 분리 리팩토링 |
| 2026-02-10 | querypie-docs#653 | **Reverse Sync Phase 1 완료** |

## 관련 문서

| 문서 | 위치 | 내용 |
|------|------|------|
| architecture.md | querypie-docs-translation-2 | 전체 시스템 아키텍처 + 용어 정의 |
| Phase 2 설계 | docs/plans/2026-02-13-reverse-sync-phase2-design.md | Reverse Sync Phase 2 설계 |
| Phase 2 구현 계획 | docs/plans/2026-02-13-reverse-sync-phase2-impl.md | Phase 2 구현 태스크 분해 |
| Phase 1 회고 | projects/done/querypie-docs-reverse-sync-phase1-retrospective.md | Phase 1 회고 + 설계 개선 도출 |
| 매핑 재설계 | projects/done/querypie-docs-reverse-sync-mapping-redesign.md | Sidecar mapping 전환 |
| Phase 1 완료 | projects/done/querypie-docs-reverse-sync.md | Reverse Sync Phase 1 |

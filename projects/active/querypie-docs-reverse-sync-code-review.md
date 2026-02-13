# Reverse-Sync 코드 품질 진단 및 개선 계획

> **Status:** Phase 2 독립 항목 완료 — 나머지는 Phase 2 후 진행
> **Date:** 2026-02-13
> **Target Repo:** querypie/querypie-docs (confluence-mdx/bin/reverse_sync/)
> **Related:** [매핑 재설계 (완료)](../done/querypie-docs-reverse-sync-mapping-redesign.md) | [Phase 1 회고](../done/querypie-docs-reverse-sync-phase1-retrospective.md) | [Phase 2 계획](querypie-docs-reverse-sync-phase2.md)

---

## 1. 진단 범위

Sidecar 매핑 전환 완료(querypie-docs#694) 후 main 브랜치 기준으로 reverse-sync 전체 코드를 리뷰했다.

### 1.1 코드 규모 (2,726줄 / 13 모듈)

| 모듈 | 줄 수 | 역할 |
|------|-------|------|
| `reverse_sync_cli.py` | 734 | 오케스트레이터 + CLI |
| `patch_builder.py` | 470 | 매칭/패치 생성 |
| `sidecar_lookup.py` | 308 | sidecar 매핑 조회 + 생성 |
| `xhtml_patcher.py` | 268 | XHTML 텍스트 패칭 |
| `mapping_recorder.py` | 232 | XHTML 블록 매핑 |
| `mdx_to_xhtml_inline.py` | 202 | MDX→XHTML 인라인 변환 |
| `mdx_block_parser.py` | 129 | MDX 블록 파싱 |
| `roundtrip_verifier.py` | 90 | 라운드트립 검증 |
| `text_transfer.py` | 78 | 텍스트 변경 전이 |
| `text_normalizer.py` | 70 | 텍스트 정규화 |
| `confluence_client.py` | 64 | Confluence API |
| `test_verify.py` | 46 | 테스트 wrapper |
| `block_diff.py` | 34 | 블록 비교 |

### 1.2 테스트 규모 (2,623줄 / 10 파일)

| 테스트 파일 | 줄 수 | 대상 모듈 |
|------------|-------|----------|
| `test_reverse_sync_cli.py` | 1,051 | `reverse_sync_cli.py` |
| `test_reverse_sync_sidecar_lookup.py` | 538 | `sidecar_lookup.py` |
| `test_reverse_sync_mdx_to_xhtml_inline.py` | 252 | `mdx_to_xhtml_inline.py` |
| `test_reverse_sync_e2e.py` | 187 | E2E integration |
| `test_reverse_sync_mapping_recorder.py` | 172 | `mapping_recorder.py` |
| `test_reverse_sync_xhtml_patcher.py` | 138 | `xhtml_patcher.py` |
| `test_reverse_sync_mdx_block_parser.py` | 135 | `mdx_block_parser.py` |
| `test_reverse_sync_patch_builder.py` | 66 | `patch_builder.py` |
| `test_reverse_sync_block_diff.py` | 46 | `block_diff.py` |
| `test_reverse_sync_roundtrip_verifier.py` | 38 | `roundtrip_verifier.py` |

---

## 2. 진단 결과

### 2.1 높은 심각도 (구조적 문제)

#### A. `reverse_sync_cli.py` — `run_verify()` God Function (148줄)

`run_verify()`가 7단계 파이프라인을 한 함수에서 순차 실행한다:

1. MDX 파싱 + diff
2. diff.yaml 저장
3. 원본 매핑 생성 + mapping.original.yaml 저장
4. Sidecar 생성 + 인덱스 구축 (함수 내부 inline import 포함)
5. XHTML 패치 + patched.xhtml 저장
6. Forward 변환 + verify.mdx 저장
7. 라운드트립 검증 + result.yaml 저장

**문제:**
- 함수 내부에서 `from reverse_sync.sidecar_lookup import ...` inline import (L217)
- sidecar 관련 객체 3개 인라인 생성 (14줄)
- 중간 파일 저장 로직과 비즈니스 로직이 혼재
- 단위 테스트가 어려움 (전체 파이프라인을 한 번에 실행해야 함)

#### B. `patch_builder.py` — `build_patches()` 높은 순환 복잡도 (140줄)

하나의 함수에 6가지 분기 경로가 존재한다:

```
1. sidecar 매칭 → children 있음 → child 해석 성공 → 직접 패치
2. sidecar 매칭 → children 있음 → child 해석 실패 → list 분리
3. sidecar 매칭 → children 있음 → child 해석 실패 → containing block
4. sidecar 미스 → 텍스트 포함 검색 → containing block
5. sidecar 미스 → list/table 분리
6. sidecar 매칭 → children 없음 → 텍스트 불일치 → 재매핑
```

#### C. `containing_changes` 패턴 3회 중복

동일한 그룹화 + transfer_text_changes 패턴이 3곳에서 반복된다:

| 위치 | 함수 |
|------|------|
| `patch_builder.py` L80~L198 | `build_patches()` |
| `patch_builder.py` L369~L464 | `build_list_item_patches()` |
| `patch_builder.py` L292~L344 | `build_table_row_patches()` |

반복 패턴:
```python
bid = container.block_id
if bid not in containing_changes:
    containing_changes[bid] = (container, [])
containing_changes[bid][1].append((old_plain, new_plain))
# ... 후에 ...
for bid, (mapping, item_changes) in containing_changes.items():
    xhtml_text = mapping.xhtml_plain_text
    for old_plain, new_plain in item_changes:
        xhtml_text = transfer_text_changes(old_plain, new_plain, xhtml_text)
    patches.append({...})
```

---

### 2.2 중간 심각도

#### D. `sidecar_lookup.py` — 생성/소비 이중 역할 (308줄)

| 영역 | 줄 | 기능 |
|------|-----|------|
| **소비** (L1~L56) | 56줄 | `load_sidecar_mapping()`, `find_mapping_by_sidecar()`, `build_*_index()` |
| **생성** (L58~L308) | 252줄 | `generate_sidecar_mapping()`, `_find_text_match()`, `_count_child_mdx_blocks()` |

생성 로직은 forward converter 측의 `sidecar_mapping.py`(bin/converter/)와 동일한 목적이지만 별도로 존재한다. `run_verify()` 내부에서만 사용되며, forward converter의 `sidecar_mapping.py`와 로직이 분기될 위험이 있다.

#### E. `mapping_recorder.py` — 중복 함수 2개

`_add_rich_text_body_children()`(L122~L167)과 `_add_adf_content_children()`(L188~L233)이 **거의 동일한 로직**이다. 차이점은 컨테이너 요소를 찾는 방법뿐:

| 함수 | 컨테이너 |
|------|----------|
| `_add_rich_text_body_children()` | `ac:rich-text-body` 직접 탐색 |
| `_add_adf_content_children()` | `ac:adf-node` → `ac:adf-content` 2-hop 탐색 |

약 45줄의 중복.

#### F. `_INVISIBLE_RE` 정규식 불일치

`patch_builder.py`와 `text_normalizer.py`에서 동일 목적의 정규식이 별도 정의되어 있으며, 문자 집합이 미묘하게 다르다:

```python
# patch_builder.py L19 — \s, \u3000, \xa0 포함
_INVISIBLE_RE = re.compile(
    r'[\s\u200b\u200c\u200d\u2060\ufeff\u3164\u115f\u1160\u3000\xa0]+')

# text_normalizer.py L10 — \s 미포함, \u00AD 포함
INVISIBLE_RE = re.compile(
    r'[\u200B\u200C\u200D\u2060\uFEFF\u00AD\u3164\u115F\u1160]+')
```

의도적 차이인지 실수인지 불분명. 두 곳에서 독립적으로 진화하며 불일치가 발생했을 가능성이 높다.

#### G. `pages.yaml` 이중 로드

`reverse_sync_cli.py`의 `_resolve_page_id()`(L98~L109)와 `_resolve_attachment_dir()`(L112~L118)가 각각 `pages.yaml`을 독립적으로 로드한다. 한 번 verify 실행에 2회 파싱.

---

### 2.3 낮은 심각도 (코드 냄새)

#### H. 테스트 커버리지 불균형

| 모듈 | 프로덕션 줄 | 테스트 줄 | 비율 | 평가 |
|------|-----------|----------|------|------|
| `sidecar_lookup.py` | 308 | 538 | 1.75x | 충분 |
| `reverse_sync_cli.py` | 734 | 1,051 | 1.43x | 충분 |
| `mdx_to_xhtml_inline.py` | 202 | 252 | 1.25x | 충분 |
| `mapping_recorder.py` | 232 | 172 | 0.74x | 보통 |
| `mdx_block_parser.py` | 129 | 135 | 1.05x | 충분 |
| `xhtml_patcher.py` | 268 | 138 | 0.51x | 부족 |
| `roundtrip_verifier.py` | 90 | 38 | 0.42x | 부족 |
| **`patch_builder.py`** | **470** | **66** | **0.14x** | **심각** |
| **`text_transfer.py`** | **78** | **0** | **0x** | **심각** |
| **`text_normalizer.py`** | **70** | **0** | **0x** | **심각** |

`patch_builder.py`(470줄, 가장 복잡한 모듈)의 전용 테스트가 66줄(`_find_containing_mapping` 7개만). `text_transfer.py`와 `text_normalizer.py`는 전용 테스트 파일이 아예 없다.

#### I. `block_diff.py` Phase 1 전용 제약

```python
if len(original) != len(improved):
    raise ValueError(f"block count mismatch: ...")
```

Phase 2(구조적 변경)에서 시퀀스 정렬 알고리즘으로 전환 시 이 모듈 전체가 재작성 대상이다.

#### J. `test_verify.py` 위치 문제

`bin/reverse_sync/` 프로덕션 코드 디렉토리에 테스트 파일이 존재. `tests/` 디렉토리의 다른 테스트들과 불일치.

#### K. `_resolve_child_mapping()` 4단계 fallback 잔존

Sidecar 전환 후에도 child 해석에서 4단계 fallback이 남아 있다:

```
1. collapse_ws 완전 일치
2. 공백 무시 완전 일치
3. XHTML 리스트 마커 제거 후 비교
4. MDX 리스트 마커 제거 후 비교
```

Phase 1 회고에서 지적된 "whack-a-mole" 패턴이 축소되었으나 완전히 제거되지 않았다.

---

## 3. 긍정적 평가

| 항목 | 내용 |
|------|------|
| **모듈 분리** | Phase 1 회고 이후 1,143줄 → 734줄로 핵심 알고리즘 4개 모듈 분리 완료 |
| **Sidecar 전환** | fuzzy matching 7단계 → O(1) 직접 조회로 근본적 개선 |
| **데이터 클래스** | `MdxBlock`, `BlockMapping`, `SidecarEntry`, `BlockChange` 등 타입 명확 |
| **안전장치** | round-trip 검증 파이프라인 (패치 → forward 변환 → 비교)이 잘 설계됨 |
| **실용적 안정성** | 148페이지 배치 verify 100% 통과, pytest 251개 통과 |
| **관심사 분리** | sidecar 전환 후 매핑/정규화/전이/패칭이 적절히 분리됨 |

---

## 4. 개선 계획

### 4.1 P1 — 코드 품질 (patch_builder 리팩토링)

| # | 작업 | 대상 파일 | 효과 | 상태 |
|---|------|----------|------|------|
| 1 | `containing_changes` 패턴을 공통 함수로 추출 | `patch_builder.py` | 3곳 중복 제거, 버그 수정 시 일관성 | **보류** — Phase 2가 구조 변경 예정 |
| 2 | `build_patches()` 분기를 전략 패턴 또는 helper 함수로 분리 | `patch_builder.py` | 순환 복잡도 감소 | **보류** — 동일 사유 |
| 3 | `patch_builder.py` 전용 유닛 테스트 확충 | `tests/test_reverse_sync_patch_builder.py` | 6개 분기 경로별 테스트 | **완료** — querypie-docs#699 (7→52 tests) |

### 4.2 P2 — 모듈 구조 개선

| # | 작업 | 대상 파일 | 효과 | 상태 |
|---|------|----------|------|------|
| 4 | `sidecar_lookup.py` 생성/소비 분리 | `sidecar_lookup.py` → `sidecar_generator.py` 분리 | 책임 분리, forward converter와 일관성 | **보류** — Phase 2 sidecar 활용 방식 확정 후 |
| 5 | `_INVISIBLE_RE` 통합 — `text_normalizer.py`로 단일 정의 | `patch_builder.py`, `text_normalizer.py` | 정규화 규칙 일관성 | **완료** — querypie-docs#697 |
| 6 | `text_transfer.py`, `text_normalizer.py` 전용 테스트 추가 | `tests/` | 핵심 유틸리티 안전망 확보 | **완료** — querypie-docs#697 (59 tests) |

### 4.3 P3 — 가독성/정리

| # | 작업 | 대상 파일 | 효과 | 상태 |
|---|------|----------|------|------|
| 7 | `run_verify()` 파이프라인 단계별 private 함수 분리 | `reverse_sync_cli.py` | 가독성, inline import 제거 | **보류** — Phase 2 파이프라인 확정 후 |
| 8 | `mapping_recorder.py` rich_text/adf 중복 제거 | `mapping_recorder.py` | DRY, ~45줄 절감 | **완료** — querypie-docs#700 (232→210줄) |
| 9 | `test_verify.py`를 `tests/`로 이동 | `bin/reverse_sync/` → `tests/` | 일관성 | **스킵** — CLI wrapper이며 run-tests.sh가 참조 |
| 10 | `pages.yaml` 로드 캐싱 | `reverse_sync_cli.py` | 미미한 성능 개선 | **보류** |

---

## 진행 로그

| 날짜 | PR | 내용 |
|------|-----|------|
| 2026-02-13 | skills-jk#102 | 코드 품질 진단 문서 작성 |
| 2026-02-13 | querypie-docs#697 | P2-#5 `_INVISIBLE_RE` 통합 + P2-#6 text utility 테스트 59개 추가 |
| 2026-02-13 | querypie-docs#699 | P1-#3 `patch_builder` 테스트 확충 (7→52 tests) |
| 2026-02-13 | querypie-docs#700 | P3-#8 `mapping_recorder` 중복 제거 (232→210줄) |

## 진행 상태

- [x] 코드 리뷰 및 진단
- [x] Phase 2 독립 항목 완료 (P1-#3, P2-#5, P2-#6, P3-#8)
- [ ] P1-#1, #2: Phase 2 완료 후 patch_builder 리팩토링
- [ ] P2-#4: Phase 2 완료 후 sidecar_lookup 분리
- [ ] P3-#7, #10: Phase 2 완료 후 정리

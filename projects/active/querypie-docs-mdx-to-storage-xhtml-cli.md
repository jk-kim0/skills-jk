---
id: querypie-docs-mdx-to-storage-xhtml-cli
title: QueryPie Docs MDX -> Confluence Storage XHTML CLI
status: active
repos:
  - https://github.com/querypie/querypie-docs
created: 2026-02-15
updated: 2026-02-16
---

# QueryPie Docs MDX -> Confluence Storage XHTML CLI

## 목표 (확정)

목표는 "의미적으로 비슷한 XHTML" 생성이 아니라, **원문 `page.xhtml`를 byte-equal로 복원**하는 것이다.

- 허용되지 않는 것: 공백, self-closing 표기, attribute 순서, node 구성의 사소한 차이
- 허용되는 것: 없음 (최종 게이트는 byte-equal)

## 2026-02-16 기준 구현 현황 (main 확인)

확인 기준:
- repo: `querypie-docs-translation-2`
- branch: `main` (HEAD: `fe2becc7`)
- batch verify: `total=21 passed=0 failed=21`

주요 실패 원인 분포:
- `ordered_list_start_mismatch=12`
- `attachment_filename_mismatch=7`
- `internal_link_unresolved=7`
- `image_block_structure_mismatch=5`
- `emoticon_representation_mismatch=4`
- `adf_extension_panel_mismatch=3`

## 핵심 판단

현재 구현은 이미 방대한 기능을 갖고 있으므로, 전부 폐기하지 않는다.
다만 "normalize 기반 comparator 통과" 중심 설계를 **중단**하고,
기존 코드를 **lossless 복원 파이프라인의 하위 구성요소로 재배치**한다.

## 재활용/취소/축소 계획

### 1) 재활용 (Keep + Reuse)

| 대상 | 상태 | 재활용 방식 |
|------|------|-------------|
| `bin/mdx_to_storage/parser.py` | 유지 | block boundary/semantic fingerprint 생성기로 활용 |
| `bin/mdx_to_storage/emitter.py` | 유지 | 변경 블록 fallback renderer로 제한 사용 |
| `bin/mdx_to_storage/inline.py` | 유지 | fallback 렌더 단계에서만 사용 |
| `bin/mdx_to_storage/link_resolver.py` | 유지 | sidecar 메타와 결합하여 unresolved 링크 복원 보조 |
| `bin/reverse_sync/mapping_recorder.py` | 재활용 | sidecar 생성 메타 추출기로 확장 |
| `bin/reverse_sync/sidecar_lookup.py` | 재활용 | block_id -> raw fragment lookup에 재사용 |
| `bin/reverse_sync/xhtml_patcher.py` | 재활용 | raw splice/patch 조립 엔진 기반으로 확장 |
| 기존 pytest 세트 | 유지 | 회귀 테스트 + 신규 byte-equal 테스트의 기반으로 사용 |

### 2) 취소 (Stop)

| 대상 | 조치 | 이유 |
|------|------|------|
| normalize 후 diff 중심 성공판정 | 중단 | byte-equal 목표와 충돌 |
| "알려진 제약으로 pass 제외" 전략 | 중단 | 목표가 exact restore이므로 예외 패스 전략 불가 |
| failure reason 카테고리 중심 KPI | 보조지표로 강등 | 원인 분류는 디버깅용, 성공판정용 아님 |

### 3) 축소 (Deprioritize)

| 대상 | 조치 | 이유 |
|------|------|------|
| 신규 매크로 변환 rule 추가 | 후순위 | sidecar 기반 raw 복원이 우선 |
| verify 필터 추가 확장 | 후순위 | normalize 정교화는 목표 달성에 직접 기여 낮음 |

## 새 아키텍처 (기존 구현을 포함한 전환안)

```
XHTML source
  -> forward converter
     -> expected.mdx
     -> expected.roundtrip.json (sidecar, 신규)

expected.mdx + sidecar
  -> parse_mdx (기존 재활용)
  -> block_id align (신규)
  -> rehydrator (신규)
      - unchanged block: raw_xhtml splice (sidecar)
      - changed block: emitter fallback (기존 재활용)
  -> token-preserving stitcher (신규)

output.xhtml
  -> byte-verify (신규 기본 게이트)
```

## 구현 단계 (현실적인 전환 순서)

### Phase R0: 전환 기반 정리
- [ ] 계획 문서/README/CLI 도움말에서 목표를 byte-equal로 통일
- [ ] 기존 verify를 `diagnostic` 모드로 명시
- [ ] 신규 `byte-verify` 명령 인터페이스 설계

### Phase R1: Sidecar 계약 확정 + 생성
- [ ] `expected.roundtrip.json` 스키마 v1 정의
- [ ] forward 단계에서 sidecar 생성 (`--write-sidecar`)
- [ ] 저장 필드: raw_xhtml, span, link/macro/attachment metadata, token hints

### Phase R2: Rehydration 최소 구현
- [ ] stable `block_id` 생성기 구현
- [ ] unchanged block raw splice 구현
- [ ] changed block fallback to emitter 구현
- [ ] 문서 조립기(stitcher) 구현

### Phase R3: Token-preserving serializer
- [ ] self-closing 표기 보존 (`<br/>` vs `<br />`)
- [ ] attribute 순서 보존
- [ ] whitespace/linebreak 보존
- [ ] CDATA 경계/원문 텍스트 보존

### Phase R4: 비가역 항목 원복
- [ ] `#link-error` 원복: sidecar link metadata 우선
- [ ] `ac:adf-extension` raw payload 원복
- [ ] `ac:emoticon`/`ri:filename` 원복
- [ ] `ri:space`/absolute confluence link 복원

### Phase R5: 검증 전환 및 CI 게이트
- [ ] 21 testcase byte-equal 검증 추가
- [ ] CI 기본 게이트를 byte-equal로 전환
- [ ] 기존 normalize verify는 실패 분석 리포트용으로 유지

## 작업 분할 (PR 단위)

1. PR-A: Sidecar schema + writer
2. PR-B: block_id align + rehydrator minimal
3. PR-C: token-preserving stitcher
4. PR-D: lossless link/macro restore
5. PR-E: byte-verify CLI + CI gate 전환

## 완료 기준 (DoD)

1. `tests/testcases/*` 전체에서 output.xhtml == page.xhtml (byte-equal)
2. "known limitation"으로 제외되는 케이스 없음
3. sidecar 없는 경우에는 lossless 미보장을 명시적으로 실패 처리 또는 경고 처리
4. CI가 byte mismatch를 즉시 fail 처리

## 즉시 다음 액션

- [ ] R1 스키마 초안 PR 시작
- [ ] testcase 3건(`lists`, `panels`, `544211126`)으로 sidecar+rehydration PoC
- [ ] byte mismatch 리포터(최초 mismatch offset + context) 구현

# QueryPie Docs Reverse Sync — Phase 2/3

> **Status:** Phase 2 완료 + 안정화 진행 중 — Phase 3 미착수
> **Target Repo:** [querypie/querypie-docs/confluence-mdx][repo]
> **Phase 1:** [완료](../done/querypie-docs-reverse-sync.md)
> **매핑 재설계:** [완료](../done/querypie-docs-reverse-sync-mapping-redesign.md)
> **Phase 1 회고:** [조치 완료](../done/querypie-docs-reverse-sync-phase1-retrospective.md)
> **Phase 2 설계:** [승인됨](../../docs/plans/2026-02-13-reverse-sync-phase2-design.md)
> **Phase 2 구현 계획:** [완료](../../docs/plans/2026-02-13-reverse-sync-phase2-impl.md)

[repo]: https://github.com/querypie/querypie-docs/tree/main/confluence-mdx

## 목표

Phase 1(텍스트 수준 변경)에서 구축한 reverse-sync 파이프라인을 확장하여, **구조적 변경** 및 **전면 재구성**까지 Confluence에 역반영할 수 있도록 한다.

### 배경

Phase 1은 블록 수가 동일한 텍스트 변경만 처리한다. AI Agent가 헤딩을 재구성하거나 섹션을 분리/통합하는 등 구조적 편집을 수행하면, 현재 파이프라인에서는 블록 수 불일치 에러가 발생한다.

### 완료된 전제조건

Phase 1 회고에서 도출된 설계 개선 작업이 완료되어 Phase 2 착수 기반이 마련되었다:

| 항목 | PR | 상태 |
|------|-----|------|
| Sidecar mapping 파일 생성 (Forward converter) | querypie-docs#682 | 완료 |
| Sidecar lookup 모듈 + 유닛 테스트 | querypie-docs#685, #687 | 완료 |
| Fuzzy matching 제거, sidecar 전용 매칭 전환 | querypie-docs#688, #694 | 완료 |
| `reverse_sync_cli.py` 4개 모듈 분리 리팩토링 | querypie-docs#679 | 완료 |
| `pages_of_confluence.py` 모듈 분리 | querypie-docs#678 | 완료 |
| `pages.yaml` 기반 일괄 변환 파이프라인 | querypie-docs#681 | 완료 |

### 변경 범위

| Phase | 범위 | 상태 |
|-------|------|------|
| Phase 2 | 구조적 변경 (블록 추가/삭제, 헤딩 재구성, 섹션 분리/통합) | **완료** (querypie-docs#704) |
| Phase 2 안정화 | 버그 재현 테스트, CLI 개선, 정규화 보완 | **진행 중** |
| Phase 3 | 전면 재구성 (문서 구조, 위치, 이름 변경) | 미착수 |

---

## Phase 2 — 구조적 변경 역반영 ✅

블록 추가/삭제를 포함한 구조적 변경을 XHTML에 역반영한다. querypie-docs#704 (2026-02-13)에서 구현 완료.

### 구현 내용

| 모듈 | 변경 내용 |
|------|----------|
| `block_diff.py` | `difflib.SequenceMatcher` 기반 블록 시퀀스 정렬 (added/deleted/modified 감지) |
| `patch_builder.py` | `_build_delete_patch()`, `_build_insert_patch()`, `_find_insert_anchor()` 추가 |
| `xhtml_patcher.py` | DOM 요소 삭제/삽입 + 적용 순서 (delete→insert→modify) |
| `mdx_to_xhtml_inline.py` | `mdx_block_to_xhtml_element()` — 완전한 XHTML 요소 생성 (heading/paragraph/list/code) |
| `reverse_sync_cli.py` | `diff_blocks()` 반환값 변경 (changes, alignment) 반영 |

### 설계 결정

- **알고리즘**: `difflib.SequenceMatcher`로 원본/개선 MDX 블록 시퀀스를 정렬하여 `equal`/`replace`/`insert`/`delete` opcode 생성
- **패치 포맷 확장**: `delete` (xhtml_xpath), `insert` (after_xpath + new_element_xhtml) 추가
- **적용 순서**: delete (뒤→앞, xpath 인덱스 보존) → insert (앞→뒤) → modify (기존)
- **삽입 앵커**: improved 시퀀스에서 역순 탐색하여 alignment에 존재하는 최근접 매칭 블록의 xpath 사용

### Phase 2 안정화 (진행 중)

Phase 2 구현 후 실 데이터 검증 과정에서 발견된 이슈 대응:

| PR | 내용 | 상태 |
|-----|------|------|
| querypie-docs#701 | Badge 색상·코드 펜스 정규화 및 round-trip 검증 보완 | 완료 |
| querypie-docs#724 | verify 실패 항목 재검증 스크립트 및 CLI 개선 | 완료 |
| querypie-docs#734 | 네임스페이스 접두사 유지 및 코드 참조 수정 | 완료 |
| querypie-docs#740 | 버그 재현 테스트케이스 17건 추가 + CLI 출력 형식 개선 | 완료 |

---

## Phase 3 — 전면 재구성

문서 구조, 위치, 이름 변경을 포함한 전면 재구성을 Confluence에 반영한다.

### 필요한 확장

- **블록 이동/재정렬**: Phase 2의 SequenceMatcher를 확장하여 이동(reorder) 감지
- **빈 컨테이너 자동 삭제**: Callout 내부 자식 전체 삭제 시 빈 callout 정리
- **Confluence 전용 매크로 MDX→XHTML 생성**: Callout 등 복합 매크로
- **Confluence API 페이지 이동/이름 변경 연동**: REST API v1/v2를 통한 페이지 메타데이터 변경
- **페이지 트리 구조 관리**: 부모-자식 관계 변경, 페이지 순서 재배치

### 설계 고려사항

- Phase 2와 독립적으로 설계 가능하나, Phase 2의 블록 수준 변경이 선행되는 것이 자연스러움
- 설계 추가 필요

---

## 진행 로그

| 날짜 | PR | 내용 |
|------|-----|------|
| 2026-02-15 | querypie-docs#740 | 버그 재현 테스트케이스 17건 추가 + CLI 출력 형식 개선 |
| 2026-02-15 | querypie-docs#734 | 네임스페이스 접두사 유지 및 코드 참조 수정 |
| 2026-02-14 | querypie-docs#724 | verify 실패 항목 재검증 스크립트 및 CLI 개선 |
| 2026-02-13 | querypie-docs#704 | **Phase 2 구현 완료 — 블록 추가/삭제 구조적 변경 지원** |
| 2026-02-13 | querypie-docs#701 | Badge 색상·코드 펜스 정규화 및 round-trip 검증 보완 |
| 2026-02-13 | querypie-docs#700 | mapping_recorder 중복 제거 (코드 품질) |
| 2026-02-13 | querypie-docs#699 | patch_builder 테스트 확충 7→52 (코드 품질) |
| 2026-02-13 | querypie-docs#697 | `_INVISIBLE_RE` 통합 + text utility 테스트 (코드 품질) |
| 2026-02-13 | querypie-docs#694 | Sidecar 전용 매칭 전환 완료 — Phase 2 전제조건 충족 |
| 2026-02-12 | querypie-docs#688 | Fuzzy matching 제거, sidecar pipeline 전환 |
| 2026-02-12 | querypie-docs#685 | Sidecar mapping lookup 모듈 + 유닛 테스트 |
| 2026-02-12 | querypie-docs#682 | Sidecar mapping 파일 생성 기능 추가 |
| 2026-02-11 | querypie-docs#679 | 오케스트레이터 4개 모듈 분리 리팩토링 |

## 진행 상태

- [x] Phase 2 설계 — 2026-02-13 승인
- [x] Phase 2 구현 — querypie-docs#704 (2026-02-13)
- [ ] Phase 2 안정화 — 실 데이터 검증 + 버그 수정 진행 중
- [ ] Phase 3 설계
- [ ] Phase 3 구현

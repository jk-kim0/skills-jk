# QueryPie Docs Reverse Sync — Phase 2/3

> **Status:** Not Started
> **Target Repo:** [querypie/querypie-docs/confluence-mdx][repo]
> **Phase 1:** [완료](../done/querypie-docs-reverse-sync.md)

[repo]: https://github.com/querypie/querypie-docs/tree/main/confluence-mdx

## 목표

Phase 1(텍스트 수준 변경)에서 구축한 reverse-sync 파이프라인을 확장하여, **구조적 변경** 및 **전면 재구성**까지 Confluence에 역반영할 수 있도록 한다.

### 배경

Phase 1은 블록 수가 동일한 텍스트 변경만 처리한다. AI Agent가 헤딩을 재구성하거나 섹션을 분리/통합하는 등 구조적 편집을 수행하면, 현재 파이프라인에서는 블록 수 불일치 에러가 발생한다.

### 변경 범위

| Phase | 범위 | 상태 |
|-------|------|------|
| Phase 2 | 구조적 변경 (헤딩 재구성, 섹션 분리/통합, Callout 추가) | 미착수 |
| Phase 3 | 전면 재구성 (문서 구조, 위치, 이름 변경) | 미착수 |

---

## Phase 2 — 구조적 변경 역반영

블록 추가/삭제/이동을 포함한 구조적 변경을 XHTML에 역반영한다.

### 필요한 확장

- **`block_diff` 확장**: 현재 1:1 순차 비교 → 시퀀스 정렬 알고리즘으로 블록 추가/삭제/이동 감지
- **MDX → XHTML 부분 역변환 모듈**: 추가된 MDX 블록을 Confluence XHTML 요소(매크로 포함)로 변환
- **`xhtml_patcher` 확장**: 블록 삽입/삭제/이동 패치 지원

### 설계 고려사항

- 시퀀스 정렬: difflib `SequenceMatcher` 또는 LCS 기반 알고리즘 검토
- 추가된 블록의 XHTML 변환: Confluence 매크로(`ac:structured-macro` 등)를 생성해야 하므로 forward converter의 역변환 로직이 필요
- 검증: Phase 1의 round-trip 검증 프레임워크 재활용 가능

---

## Phase 3 — 전면 재구성

문서 구조, 위치, 이름 변경을 포함한 전면 재구성을 Confluence에 반영한다.

### 필요한 확장

- **Confluence API 페이지 이동/이름 변경 연동**: REST API v1/v2를 통한 페이지 메타데이터 변경
- **페이지 트리 구조 관리**: 부모-자식 관계 변경, 페이지 순서 재배치

### 설계 고려사항

- Phase 2와 독립적으로 설계 가능하나, Phase 2의 블록 수준 변경이 선행되는 것이 자연스러움
- 설계 추가 필요

---

## 진행 로그

(아직 시작 전)

## 진행 상태

- [ ] Phase 2 설계
- [ ] Phase 2 구현
- [ ] Phase 3 설계
- [ ] Phase 3 구현

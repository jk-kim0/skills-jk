---
id: querypie-docs-mdx-to-storage-xhtml-cli
title: QueryPie Docs MDX -> Confluence Storage XHTML CLI
status: active
repos:
  - https://github.com/querypie/querypie-docs
created: 2026-02-15
---

# QueryPie Docs MDX -> Confluence Storage XHTML CLI

## 목표

`../querypie-docs-translation-1/confluence-mdx` 기반으로, MDX 문서를 Confluence Storage Format(XHTML)으로 변환하는 독립 CLI를 구현한다.

핵심 요구사항:
- 문서 의미(구조/매크로/링크/코드)를 보존하는 변환
- reverse-sync에서 재사용 가능한 공통 모델(중립 IR) 도입
- 배치 실행 및 검증 가능한 테스트 체계 구축

## 배경

현재 `confluence-mdx/bin/reverse_sync/mdx_to_xhtml_inline.py`는 inline/부분 변환 중심이며, 리스트 중첩/Callout/테이블/매크로 경계에서 안정성이 부족하다.

또한 reverse-sync verify 실패에서 보이는 다수 이슈는 텍스트 기반 비교/치환 접근의 한계를 드러낸다. 신규 CLI는 AST 기반 구조 변환으로 이 문제를 줄이는 것을 목표로 한다.

## 확인한 현황 (2026-02-15)

- 대상 디렉토리: `../querypie-docs-translation-1/confluence-mdx`
- 기존 주요 스크립트:
  - `bin/converter/cli.py` (XHTML -> MDX)
  - `bin/reverse_sync_cli.py` (MDX 변경 역반영 오케스트레이션)
  - `bin/reverse_sync/mdx_to_xhtml_inline.py` (부분 MDX -> XHTML 변환)
- 테스트 자산:
  - `tests/test_reverse_sync_cli.py`
  - `tests/reverse-sync/*`
  - `tests/testcases/*`

## 범위

### In Scope

- 신규 CLI 엔트리포인트 구현 (`mdx-to-storage-xhtml`)
- MDX 파싱 -> 중립 IR -> Storage XHTML 직렬화 파이프라인
- 주요 블록/인라인 변환:
  - heading, paragraph, list(중첩 포함), code fence, table, blockquote
  - strong/em/code/link/image
  - Callout 계열 MDX 컴포넌트 -> `ac:structured-macro` 또는 `ac:adf-extension`
- 단일 파일/배치 파일 변환
- 검증 모드 (`--verify`) 및 diff 출력
- 회귀 테스트(기존 실패 유형 기반)

### Out of Scope (초기 버전)

- Confluence API push 자동화
- 페이지 트리 이동/이름 변경
- 모든 사용자 정의 MDX 컴포넌트의 완전 지원

## 아키텍처 계획

### 1) 파이프라인

1. MDX 입력 수집 (파일/STDIN)
2. MDX AST 파싱 (remark/mdast 또는 기존 파서 확장)
3. AST -> 중립 IR 변환
4. IR -> Confluence Storage XHTML 직렬화
5. 옵션: forward converter 재변환 검증 (`XHTML -> MDX`) 후 diff 출력

### 2) 모듈 분리

- `bin/mdx_to_storage_xhtml_cli.py` (CLI)
- `bin/mdx_to_storage/ir.py` (IR 모델)
- `bin/mdx_to_storage/parser.py` (MDX -> IR)
- `bin/mdx_to_storage/serializer.py` (IR -> Storage XHTML)
- `bin/mdx_to_storage/normalizer.py` (검증용 정규화)
- `tests/test_mdx_to_storage_xhtml_cli.py`

### 3) 설계 원칙

- regex 텍스트 치환 최소화, AST 기반 변환 우선
- 매크로/리소스 노드(`ac:*`, `ri:*`)를 1급 타입으로 유지
- 변환 불가 노드는 fail-fast 또는 explicit placeholder로 처리
- 라운드트립 검증은 문자열 완전 일치가 아니라 구조 동등성 중심으로 확장

## CLI 초안

```bash
mdx-to-storage-xhtml convert <input.mdx> -o <output.xhtml> [--page-id <id>]
mdx-to-storage-xhtml convert --stdin -o <output.xhtml> [--page-id <id>]
mdx-to-storage-xhtml verify <input.mdx> [--page-id <id>] [--show-diff]
mdx-to-storage-xhtml batch --from <glob|manifest> --out-dir <dir> [--fail-fast]
```

출력:
- 기본: Storage XHTML 파일
- verify 모드: `pass/fail`, 구조 diff, 주요 경고(unsupported node)

## 단계별 실행 계획

### Phase 0 — 착수 정리 (1일)

- [ ] 기존 `converter`/`reverse_sync` 코드 의존점 맵 작성
- [ ] 샘플 문서 20개 선정 (복잡도별)
- [ ] 실패 기준/성공 기준 정의

### Phase 1 — 최소 동작 버전 (3~4일)

- [ ] CLI 뼈대 + 단일 파일 변환
- [ ] heading/paragraph/code/list(1-depth) 지원
- [ ] 단위 테스트 작성

### Phase 2 — 구조 확장 (4~5일)

- [ ] 중첩 리스트, table, blockquote 지원
- [ ] inline strong/em/code/link/image 안정화
- [ ] Callout 기본 매핑 지원
- [ ] 회귀 테스트 케이스 추가

### Phase 3 — 검증/배치 (2~3일)

- [ ] verify 모드 + diff 리포트
- [ ] batch 변환 + 결과 요약
- [ ] 성능/오류 보고 개선

### Phase 4 — reverse-sync 통합 준비 (2일)

- [ ] reverse-sync에서 신규 serializer 재사용 PoC
- [ ] 인터페이스 고정
- [ ] 문서화(README, 운영 가이드)

## 테스트 전략

- 단위 테스트:
  - 블록/인라인 변환 함수별 golden test
- 통합 테스트:
  - MDX -> XHTML -> (기존 converter) -> MDX roundtrip 비교
- 회귀 테스트:
  - 기존 reverse-sync 실패 유형(공백, 빈 strong, 리스트/Callout 손상) 재현 케이스 추가

## 리스크 및 대응

- 리스크: Confluence 매크로 포맷(`ac:structured-macro` vs `ac:adf-extension`) 혼재
  - 대응: 우선순위 포맷 1개를 기준으로 시작, 나머지는 feature flag로 분리
- 리스크: MDX 사용자 정의 컴포넌트 다변성
  - 대응: 지원 매트릭스 문서화 + unsupported 정책 명시
- 리스크: 문자열 기반 검증 노이즈
  - 대응: 구조 동등성(IR) 기반 verify 추가

## 산출물

- 신규 CLI 및 모듈 코드
- 테스트 코드 + 회귀 케이스
- 사용 가이드 문서
- reverse-sync 통합 제안서(후속 PR용)

## 다음 액션

- [ ] `confluence-mdx` 내 구현 브랜치 생성
- [ ] Phase 0 착수: 의존점 맵/샘플 세트/성공기준 문서 작성
- [ ] Phase 1 구현 시작


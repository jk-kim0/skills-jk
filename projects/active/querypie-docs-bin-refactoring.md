---
id: querypie-docs-bin-refactoring
title: querypie-docs confluence-mdx/bin 리팩토링
status: completed
repos:
  - https://github.com/chequer-io/querypie-docs
created: 2026-02-08
---

# querypie-docs confluence-mdx/bin 리팩토링

## 목표

`querypie-docs/confluence-mdx/bin/` 디렉토리의 기존 스크립트들을 대상으로 파일명 정규화, 코드 구조 개선, 공통 모듈 정리를 수행하여 유지보수성과 가독성을 높인다. `reverse_sync` 관련 파일은 이미 별도 프로젝트로 관리되므로 이번 리팩토링 범위에서 제외한다.

## 배경

### 현재 상태

`confluence-mdx/bin/` 디렉토리에는 Confluence 위키 문서를 MDX로 변환하고, 한/영/일 번역 구조를 비교·동기화하는 16개의 스크립트가 존재한다(reverse_sync 제외). 약 8,000줄 규모이며, 시간에 걸쳐 점진적으로 추가되면서 아래와 같은 문제들이 축적되었다.

### 현황 요약

| 파일 | 언어 | 줄 수 | 역할 |
|---|---|---|---|
| `confluence_xhtml_to_markdown.py` | Python | 2,255 | Confluence XHTML → MDX 변환 (핵심 변환기) → `converter/` 패키지로 분리, 원본 삭제 |
| `mdx_to_skeleton.py` | Python | 1,470 | MDX → 스켈레톤 변환 (번역 구조 비교용) → `skeleton/cli.py`로 이동, 원본 삭제 |
| `xhtml2markdown.ko.sh` | Bash | 1,148 | 배치 변환 스크립트 (자동 생성) |
| `pages_of_confluence.py` | Python | 1,012 | Confluence API 데이터 수집 및 페이지 트리 구성 |
| `skeleton_diff.py` | Python | 629 | 스켈레톤 파일 diff 엔진 |
| `sync_ko_commit.py` | Python | 327 | KO 커밋의 기술적 변경을 EN/JA에 동기화 |
| `find_mdx_with_text.py` | Python | 300 | MDX 파일 내 텍스트 검색 유틸리티 |
| `restore_alt_from_diff.py` | Python | 153 | git diff 기반 img alt 텍스트 복원 |
| `generate_commands_for_xhtml2markdown.py` | Python | 130 | 배치 변환 스크립트 생성기 |
| `review-skeleton-diff.sh` | Bash | 124 | 스켈레톤 diff 대화형 리뷰 도구 |
| `1-setup-cache.sh` | Bash | 114 | Docker 기반 캐시 디렉토리 설정 |
| `skeleton_common.py` | Python | 102 | 스켈레톤 처리 공유 유틸리티 |
| `skeleton_compare.py` | Python | 84 | ko/en/ja 파일 존재 비교 |
| `text_utils.py` | Python | 81 | 텍스트 정리/slugify 유틸리티 |
| `ignore_skeleton_diff.yaml` | YAML | 79 | 스켈레톤 diff 예외 규칙 |
| `translate_titles.py` | Python | 65 | 한국어 제목 → 영어 번역 |

### 제외 대상

| 파일 | 이유 |
|---|---|
| `reverse_sync_cli.py` | 별도 프로젝트로 관리 |
| `reverse_sync/` (패키지 전체) | 별도 프로젝트로 관리 |

### 모듈 의존 관계 (리팩토링 전 → 후)

**리팩토링 전:**
```
text_utils.py
  ← confluence_xhtml_to_markdown.py
  ← generate_commands_for_xhtml2markdown.py
  ← pages_of_confluence.py

skeleton_common.py
  ← mdx_to_skeleton.py
  ← skeleton_diff.py

skeleton_compare.py ← mdx_to_skeleton.py
skeleton_diff.py    ← mdx_to_skeleton.py
```

**리팩토링 후:**
```
text_utils.py
  ← converter/context.py
  ← generate_commands_for_xhtml2markdown.py
  ← pages_of_confluence.py

skeleton/common.py  ← skeleton/cli.py, skeleton/diff.py
skeleton/compare.py ← skeleton/cli.py
skeleton/diff.py    ← skeleton/cli.py

converter/context.py ← converter/core.py, converter/cli.py
converter/core.py    ← converter/cli.py
```

## 식별된 문제점

### 1. 파일명 비일관성

- 숫자 접두사(`1-setup-cache.sh`), 하이픈(`review-skeleton-diff.sh`), 언더스코어(`confluence_xhtml_to_markdown.py`)가 혼재
- 자동 생성 파일(`xhtml2markdown.ko.sh`)이 수동 작성 파일과 같은 디렉토리에 위치
- 역할에 따른 논리적 그룹핑이 없음 (변환기, 유틸리티, 배치 스크립트가 혼합)

### 2. 대형 파일

- `confluence_xhtml_to_markdown.py` (2,255줄): 테이블 변환, 매크로 처리, 어태치먼트 관리 등이 하나의 파일에 집중
- `mdx_to_skeleton.py` (1,470줄): ContentProtector, TextProcessor 등 독립 가능한 클래스가 하나의 파일에 집중

### 3. 전역 상태 의존

- `confluence_xhtml_to_markdown.py`: `PAGES_BY_TITLE`, `PAGES_BY_ID`, `GLOBAL_ATTACHMENTS` 등 6개 이상의 전역 변수
- `skeleton_diff.py`: `_diff_count`, `_match_count`, `_max_diff` 등 모듈 수준 전역 상태
- 테스트 작성과 동시 실행이 어려움

### 4. 코드 중복

- `translate_titles.py`의 번역 로직이 `pages_of_confluence.py`의 `TranslationService`와 중복
- argparse 패턴이 스크립트마다 독립적으로 구현됨

### 5. 기타

- `translate_titles.py`: 유일하게 CLI 인자 미지원 (파일 경로 하드코딩)
- Protocol 타입이 선언만 되고 실제 타입 어노테이션에 사용되지 않음 (`pages_of_confluence.py`)
- 타입 힌트 불완전 (`align: str = None` → `Optional[str] = None`)

## 리팩토링 계획

### Phase 1: 파일명 정규화 및 디렉토리 구조 개선 ✅

**목표:** 일관된 명명 규칙 적용, 역할별 논리적 그룹핑

- [x] 숫자 접두사 제거: `1-setup-cache.sh` → `setup-cache.sh`
- [x] 자동 생성 파일을 `bin/generated/` 하위로 이동: `xhtml2markdown.ko.sh` → `generated/xhtml2markdown.ko.sh`
- [x] GHA workflow, Dockerfile, entrypoint.sh, README, CONTAINER_DESIGN.md 일괄 업데이트
- [x] 기존 테스트 통과 확인 (XHTML 21/21, Skeleton 18/18)

### Phase 2: 스켈레톤 모듈 패키지화 ✅

**목표:** `skeleton_*` 관련 파일들을 `bin/skeleton/` 패키지로 통합

- [x] `bin/skeleton/` 패키지 생성 (`__init__.py`)
- [x] `skeleton_common.py` → `bin/skeleton/common.py`
- [x] `skeleton_compare.py` → `bin/skeleton/compare.py`
- [x] `skeleton_diff.py` → `bin/skeleton/diff.py`
- [x] `ignore_skeleton_diff.yaml` → `bin/skeleton/ignore_rules.yaml`
- [x] `mdx_to_skeleton.py` → `bin/skeleton/cli.py` (shim 없이 완전 삭제, git rename R099로 인식)
- [x] `.claude/skills/`, `docs/translation.md` 등 참조 문서 일괄 업데이트
- [x] 기존 테스트 통과 확인 (pytest 55/55, XHTML 21/21, Skeleton 18/18)

**미적용 항목:**
- `review-skeleton-diff.sh` 이동: 외부 참조가 있어 하위 디렉토리 이동 시 호환성 위험
- `DiffProcessor` 클래스 리팩토링: 전역 상태 제거는 기능 변경 위험이 있어 별도 작업으로 분리
- `ContentProtector`/`TextProcessor` 별도 모듈 분리: 테스트에서 `skeleton.cli` 경유 import 사용 중

### Phase 3: 변환기 모듈 분리 ✅

**목표:** `confluence_xhtml_to_markdown.py`의 대형 구조를 분리

- [x] `bin/converter/` 패키지 생성 (`__init__.py`)
- [x] `converter/context.py`: 타입 정의, 전역 상태, 유틸리티 함수 (663줄)
- [x] `converter/core.py`: 8개 변환 클래스 — Attachment, SingleLineParser, MultiLineParser, TableToNativeMarkdown, TableToHtmlTable, StructuredMacroToCallout, AdfExtensionToCallout, ConfluenceToMarkdown (1445줄)
- [x] `converter/cli.py`: main() 진입점, generate_meta_from_children (211줄) + `sys.path` fix for standalone execution
- [x] 모듈 간 전역 변수 공유: `import converter.context as ctx` + `ctx.VAR = value` 패턴
- [x] `confluence_xhtml_to_markdown.py` 완전 삭제 (shim 없이), 모든 호출자를 `converter/cli.py`로 업데이트
- [x] 참조 업데이트: `entrypoint.sh`, `run-tests.sh`, `reverse_sync_cli.py`, `generate_commands_for_xhtml2markdown.py`, `generated/xhtml2markdown.ko.sh`, `.claude/skills/`, `docs/`, `README.md` 등 13개 파일
- [x] `.gitignore`에 `converter/__pycache__/`, `skeleton/__pycache__/` 추가
- [x] 기존 테스트 통과 확인 (XHTML 21/21, Skeleton 18/18, pytest 147/147)

### Phase 4: 유틸리티 및 동기화 도구 정리 ✅

**목표:** 소규모 유틸리티의 일관성 확보, 타입 힌트 개선

- [x] `translate_titles.py`에 argparse 추가, 하드코딩된 파일 경로를 CLI 인자로 변경
- [x] `pages_of_confluence.py` 타입 힌트: `Config.email/api_token` 및 `Page` dataclass 필드에 `Optional` 적용
- [x] `converter/core.py` 타입 힌트: `Attachment.as_markdown(align)` 파라미터 `Optional` 적용
- [x] 기존 테스트 통과 확인 (XHTML 21/21, pytest 149/149)

**미적용 항목:**
- 번역 로직 통합: `translate_titles.py`와 `pages_of_confluence.py`의 중복은 약 15줄로, 통합 시 불필요한 의존성(requests 등) 발생. 비용 대비 효과 부족
- Protocol 타입 적용: `ApiClientProtocol` 등이 실제 `ApiClient` 클래스와 불일치 (메서드명 변경됨). Protocol 정의 수정이 먼저 필요

## 핵심 설계 원칙

1. **동작 보존 우선**: 모든 Phase에서 기존 테스트를 반드시 통과해야 한다
2. **점진적 변경**: 한 번에 하나의 관심사만 변경하여 리뷰 가능한 크기를 유지한다
3. **import 호환성 유지**: 외부에서 사용하는 import 경로는 호환 레이어를 통해 유지한다
4. **reverse_sync 무관**: reverse_sync 코드는 수정하지 않으며, 공유 모듈(`text_utils.py` 등) 변경 시 reverse_sync 호환성을 확인한다

## 산출물

| Phase | 산출물 |
|---|---|
| Phase 1 | 정규화된 파일명, 디렉토리 구조, 업데이트된 README |
| Phase 2 | `bin/skeleton/` 패키지, 전역 상태 제거 |
| Phase 3 | `bin/converter/` 패키지, 컨텍스트 객체 |
| Phase 4 | 통합된 번역 유틸리티, 타입 힌트 보강 |

## 실행 결과

**PR 전략:** Phase별 독립 브랜치 → 각각 main에 rebase 후 merge (stacked PR 아닌 독립 PR)

| Phase | 브랜치 | PR | 상태 |
|---|---|---|---|
| Phase 1 | `refactor/bin-phase-1` | #628 | ✅ Merged |
| Phase 2 | `refactor/bin-phase-2` | #629 | ✅ Merged |
| Phase 3 | `refactor/bin-phase-3` | #630 | ✅ Merged |
| Phase 4 | `refactor/bin-phase-4` | #631 | ✅ Merged |

**최종 테스트 결과:** pytest 149/149, XHTML 21/21, Skeleton 18/18

### 최종 디렉토리 구조

```
bin/
├── converter/                  # Phase 3: XHTML → MDX 변환 패키지
│   ├── __init__.py
│   ├── context.py             # 타입, 전역 상태, 유틸리티 (663줄)
│   ├── core.py                # 8개 변환 클래스 (1445줄)
│   └── cli.py                 # main() 진입점 (211줄, sys.path fix 포함)
├── skeleton/                   # Phase 2: 스켈레톤 처리 패키지
│   ├── __init__.py
│   ├── cli.py                 # mdx_to_skeleton 핵심 로직 (mdx_to_skeleton.py에서 이동)
│   ├── common.py              # 공유 유틸리티
│   ├── compare.py             # ko/en/ja 비교
│   ├── diff.py                # diff 엔진
│   └── ignore_rules.yaml      # diff 예외 규칙
├── generated/                  # Phase 1: 자동 생성 파일 격리
│   └── xhtml2markdown.ko.sh
├── setup-cache.sh             # Phase 1: 숫자 접두사 제거
├── text_utils.py
├── pages_of_confluence.py
├── translate_titles.py        # Phase 4: argparse 추가
├── ... (기타 유틸리티)
└── reverse_sync/              # 별도 관리 (이번 범위 제외)
```

**삭제된 파일:**
- `confluence_xhtml_to_markdown.py` — `converter/cli.py`로 완전 대체, shim 미유지
- `mdx_to_skeleton.py` — `skeleton/cli.py`로 완전 이동 (git rename R099), shim 미유지

## 메모

### Shim 전략 변경

초기 계획은 backward-compatible shim을 유지하는 것이었으나, 최종적으로 shim 없이 원본 파일을 완전 삭제하고 모든 호출자를 직접 업데이트하는 방식으로 변경하였다. 이유:
- Shim 유지 시 git이 파일 이동을 rename으로 인식하지 못함 (M+A로 표시)
- 호출자가 명확히 파악 가능하여, 직접 업데이트가 더 깔끔함
- `converter/cli.py`에 `sys.path` fix를 추가하여 standalone 실행 지원 (`python bin/converter/cli.py` 직접 호출 가능)

### PR 운영

- 초기에는 단일 브랜치 `refactor/confluence-mdx-bin`에서 4개 커밋으로 진행하였으나, 리뷰 편의를 위해 Phase별 독립 브랜치로 분리
- Phase 1 merge 후 Phase 2를 main에 rebase (cherry-pick), Phase 2 merge 후 Phase 3를 main에 rebase, ... 순차 진행
- `--force-with-lease`로 안전한 force push 사용

### 기술 참고

- 모듈 간 전역 변수 공유 시 Python gotcha 주의: `from module import VAR`로 import 후 `global VAR; VAR = x`는 원본 모듈에 반영되지 않음. `import module as m; m.VAR = x` 패턴 사용 필요
- `PYTHONPATH=bin` prefix 또는 `export PYTHONPATH="${BIN_DIR}:${PYTHONPATH:-}"`가 shell-based test runner에서 필요
- 테스트 실행 전 `make clean`으로 stale output 파일 정리 권장 (이전 변환기 버전의 출력물이 잔존할 수 있음)

### 향후 검토 사항

- `converter/core.py` (1445줄) 클래스 수준 분리: `TableToNativeMarkdown`/`TableToHtmlTable` → `tables.py`, `StructuredMacroToCallout`/`AdfExtensionToCallout` → `callouts.py`, `Attachment` → `attachment.py` 등 가능. 단, `SingleLineParser` ↔ `MultiLineParser`는 양방향 재귀 호출로 분리 곤란
- `DiffProcessor` 전역 상태 제거 (skeleton/diff.py)

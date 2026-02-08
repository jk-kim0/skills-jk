---
id: querypie-docs-bin-refactoring
title: querypie-docs confluence-mdx/bin 리팩토링
status: active
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
| `confluence_xhtml_to_markdown.py` | Python | 2,255 | Confluence XHTML → MDX 변환 (핵심 변환기) |
| `mdx_to_skeleton.py` | Python | 1,470 | MDX → 스켈레톤 변환 (번역 구조 비교용) |
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

### 현재 모듈 의존 관계

```
text_utils.py
  ← confluence_xhtml_to_markdown.py
  ← generate_commands_for_xhtml2markdown.py
  ← pages_of_confluence.py

skeleton_common.py
  ← mdx_to_skeleton.py
  ← skeleton_diff.py

skeleton_compare.py
  ← mdx_to_skeleton.py

skeleton_diff.py
  ← mdx_to_skeleton.py
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

### Phase 1: 파일명 정규화 및 디렉토리 구조 개선

**목표:** 일관된 명명 규칙 적용, 역할별 논리적 그룹핑

- [ ] Python 파일명을 snake_case로 통일 (이미 대부분 준수)
- [ ] Bash 스크립트 파일명을 kebab-case로 통일
- [ ] 숫자 접두사 제거: `1-setup-cache.sh` → `setup-cache.sh`
- [ ] 자동 생성 파일을 `bin/generated/` 하위로 이동
- [ ] 관련 Makefile, README, import 경로 일괄 업데이트
- [ ] 기존 테스트 통과 확인

### Phase 2: 스켈레톤 모듈 패키지화

**목표:** `skeleton_*` 관련 파일들을 `bin/skeleton/` 패키지로 통합

- [ ] `bin/skeleton/` 패키지 생성
- [ ] `mdx_to_skeleton.py` → `bin/skeleton/cli.py` (진입점)
- [ ] `skeleton_common.py` → `bin/skeleton/common.py`
- [ ] `skeleton_compare.py` → `bin/skeleton/compare.py`
- [ ] `skeleton_diff.py` → `bin/skeleton/diff.py`
- [ ] `ignore_skeleton_diff.yaml` → `bin/skeleton/ignore_rules.yaml`
- [ ] `review-skeleton-diff.sh` → `bin/skeleton/review-diff.sh`
- [ ] `skeleton_diff.py`의 전역 상태를 클래스 기반으로 리팩토링 (`DiffProcessor` 클래스)
- [ ] `mdx_to_skeleton.py`에서 `ContentProtector`, `TextProcessor`를 별도 모듈로 분리
- [ ] 기존 테스트 통과 확인

### Phase 3: 변환기 모듈 분리

**목표:** `confluence_xhtml_to_markdown.py`의 대형 구조를 분리

- [ ] `bin/converter/` 패키지 생성
- [ ] 테이블 변환 로직 분리 (`TableToNativeMarkdown`, `TableToHtmlTable`)
- [ ] 매크로 변환 로직 분리 (`StructuredMacroToCallout`, `AdfExtensionToCallout`)
- [ ] 어태치먼트 관리 분리 (`Attachment` 클래스)
- [ ] 전역 변수를 컨텍스트 객체(`ConversionContext`)로 통합
- [ ] 기존 테스트 통과 확인

### Phase 4: 유틸리티 및 동기화 도구 정리

**목표:** 소규모 유틸리티의 일관성 확보, 중복 제거

- [ ] `translate_titles.py`에 argparse 추가, 하드코딩 제거
- [ ] `translate_titles.py`와 `pages_of_confluence.py`의 번역 로직 통합
- [ ] `pages_of_confluence.py`의 Protocol 타입을 실제 타입 어노테이션에 적용
- [ ] 타입 힌트 보강 (`Optional` 등)
- [ ] 기존 테스트 통과 확인

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

## 메모

- 각 Phase는 독립 브랜치에서 작업하고 별도 PR로 머지한다
- `xhtml2markdown.ko.sh`는 자동 생성 파일이므로 생성기(`generate_commands_for_xhtml2markdown.py`)만 이동하면 된다
- Phase 2와 Phase 3는 서로 독립적이므로 병렬 진행이 가능하다

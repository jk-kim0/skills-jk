# Reverse-Sync 매핑 방식 재설계: Sidecar Mapping File

> **Status:** Draft — 브레인스토밍 결과 정리, 상세 설계 검토 필요
> **Date:** 2026-02-11
> **Related:** [Phase 1 회고](querypie-docs-reverse-sync-phase1-retrospective.md) | [Phase 2 계획](querypie-docs-reverse-sync-phase2.md)

## 1. 배경 및 문제

### 현재 매핑 방식: Text-Based Fuzzy Matching

Phase 1에서 MDX 블록과 XHTML 요소를 연결할 때, 정규화된 plain text를 비교하는 7단계 fuzzy matching을 사용합니다.

```
Exact match → Prefix match → Whitespace-ignored → Invisible char strip
→ Emoji normalization → List marker removal → Substring containment
```

### 근본 원인

Forward converter(XHTML → MDX)가 변환 시 원본 XHTML 요소와의 **대응 정보를 기록하지 않습니다.** 따라서 reverse-sync는 텍스트 유사도로 매핑을 추론해야 합니다.

### Phase 1 회고에서 드러난 문제

| 버그 카테고리 | PR 수 | 문제 |
|---|---|---|
| 텍스트 정규화 실패 | 7 | `_normalize_mdx_to_plain()` 규칙 무한 증식 (whack-a-mole) |
| 블록 매핑 실패 | 6 | 7단계 fallback이 점점 brittle해짐 |
| XHTML 구조 파괴 | 4 | 매핑 오류로 잘못된 위치에 패치 적용 |

37개 PR 중 20개(54%)가 버그 수정이었으며, 대부분 매핑 관련입니다.

### Phase 2에서 더 심각해지는 이유

Phase 2는 구조적 변경(heading 재구성, 섹션 병합/분리, Callout 추가)을 다룹니다. 텍스트 기반 매핑으로는:

- 동일 텍스트가 여러 위치에 존재할 때 구분 불가
- 블록이 이동/분할되면 매핑 자체가 성립하지 않음
- 새로운 블록 추가 시 XHTML 삽입 위치를 특정할 수 없음

## 2. 검토한 접근법

### 접근법 A: Sidecar Mapping File (채택)

Forward converter가 변환 시 별도의 매핑 파일을 함께 생성합니다.

- MDX 출력물 자체를 오염시키지 않음 (Nextra 사이트에 영향 없음)
- 매핑이 deterministic — fuzzy matching 완전 제거
- 기존 forward converter에 "기록" 기능만 추가
- Phase 2의 구조적 변경도 xpath로 정확히 추적 가능

### 접근법 B: MDX 주석 임베딩 (탈락)

MDX 파일 자체에 `{/* xhtml:xpath */}` 주석을 삽입하는 방식.

- 탈락 사유: MDX 가독성 저하, AI Agent가 주석을 실수로 삭제/이동할 위험

### 접근법 C: Unified Normalization Pipeline (탈락)

매핑 파일 없이 XHTML/MDX 양쪽의 정규화 로직을 통합하는 방식.

- 탈락 사유: 근본적 해결이 아님, Phase 2 구조적 변경에 여전히 불충분

## 3. Sidecar Mapping File 초안 설계

> **Note:** 아래는 브레인스토밍 단계의 초안입니다. 상세 설계 검토가 필요합니다.

### 3.1 파일 위치 규칙

```
src/content/ko/user-manual/user-agent.mdx
→ var/mappings/ko/user-manual/user-agent.mapping.yaml
```

### 3.2 매핑 파일 스키마 (초안)

```yaml
version: 1
source_page_id: "12345678"
generated_at: "2025-02-10T15:30:00Z"
converter_version: "1.2.0"

blocks:
  - mdx_line_start: 5
    mdx_line_end: 5
    mdx_type: heading       # heading | paragraph | list | code_block | table | macro
    xhtml_xpath: "//h1[1]"
    xhtml_element_index: 0  # BlockMapping 배열 인덱스 (mapping_recorder 호환)
    text_digest: "sha256:a3f2c1..."  # 변경 감지용

  - mdx_line_start: 7
    mdx_line_end: 9
    mdx_type: paragraph
    xhtml_xpath: "//p[1]"
    xhtml_element_index: 1
    text_digest: "sha256:b4e3d2..."

  - mdx_line_start: 11
    mdx_line_end: 18
    mdx_type: macro
    xhtml_xpath: "//ac:structured-macro[@ac:name='info'][1]/ac:rich-text-body/p[1]"
    xhtml_element_index: 2
    text_digest: "sha256:c5f4e3..."
```

### 3.3 핵심 설계 결정

| 필드 | 역할 |
|---|---|
| `xhtml_xpath` | **Primary key** — reverse-sync가 XHTML에서 정확한 요소를 찾는 데 사용 |
| `xhtml_element_index` | 기존 `mapping_recorder.py`의 `BlockMapping` 리스트 인덱스와 호환 |
| `text_digest` | MDX가 수정되었을 때 매핑이 아직 유효한지 검증 |
| `version` | 향후 스키마 진화 대응 |

### 3.4 생성 시점

- Forward converter가 XHTML → MDX 변환을 실행할 때 자동 생성
- Forward converter 재실행 시 매핑 파일도 재생성

## 4. 미결 사항 (추후 검토 필요)

### 4.1 매핑 파일 구조

- [ ] `text_digest` 외에 추가 필드가 필요한가? (예: `xhtml_raw_snippet` 등)
- [ ] 불필요한 필드는 없는가? 스키마 단순화 가능 여부
- [ ] 1:N 매핑 (하나의 XHTML 요소 → 여러 MDX 블록) 지원 필요 여부
- [ ] N:1 매핑 (여러 XHTML 요소 → 하나의 MDX 블록) 케이스 처리

### 4.2 매핑 동기화

- [ ] AI Agent가 MDX를 수정한 후 매핑 파일과의 정합성 유지 방법
- [ ] MDX 줄 번호가 변경되면 `mdx_line_start/end` 갱신 전략
- [ ] 매핑 파일이 없거나 outdated일 때의 fallback 전략 (기존 fuzzy matching 유지?)

### 4.3 Forward Converter 수정 범위

- [ ] 기존 converter 코드에서 매핑 기록을 추가하기 위한 변경 범위 산정
- [ ] 매핑 파일 출력 형식: YAML vs JSON
- [ ] 기존 `mapping_recorder.py` 모듈과의 통합/재사용 방안

### 4.4 Reverse-Sync Pipeline 변경

- [ ] `_find_mapping_by_text()` 7단계 fallback을 매핑 파일 lookup으로 대체하는 마이그레이션 전략
- [ ] Phase 1(텍스트 변경)과 Phase 2(구조 변경) 코드의 분기 구조

### 4.5 Phase 2 구조적 변경 지원

- [ ] 블록 이동/분할/병합 시 매핑 파일 갱신 방법
- [ ] XHTML에 새 요소를 삽입할 때 삽입 위치 결정 방법 (xpath 기반)

## 5. 다음 단계

1. **미결 사항 검토** — 이 문서의 섹션 4를 검토하고 결정
2. **상세 설계** — 결정 사항을 반영하여 구현 계획 작성
3. **Forward converter 변경** — 매핑 파일 생성 기능 구현
4. **Reverse-sync pipeline 전환** — fuzzy matching → sidecar lookup 마이그레이션

# Reverse-Sync 매핑 방식 재설계: Sidecar Mapping File

> **Status:** In Progress — Forward converter 매핑 생성 구현 완료, reverse-sync pipeline 전환 대기
> **Date:** 2026-02-12
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

## 3. Sidecar Mapping File 설계

### 3.1 파일 위치

```
var/<page_id>/mapping.yaml
```

예시: `var/12345678/mapping.yaml`

- 기존 `var/<page_id>/` 디렉토리 구조와 일관됨
- page_id 기반으로 MDX 경로 변경에 영향받지 않음

### 3.2 매핑 파일 스키마

```yaml
version: 1
source_page_id: "12345678"
generated_at: "2026-02-10T15:30:00Z"
converter_version: "1.2.0"

mappings:
  - xhtml_xpath: "//h1[1]"
    xhtml_type: heading
    mdx_blocks: [0]

  - xhtml_xpath: "//p[1]"
    xhtml_type: paragraph
    mdx_blocks: [1, 2, 3]

  - xhtml_xpath: "//ac:structured-macro[@ac:name='info'][1]"
    xhtml_type: macro
    mdx_blocks: [4, 5, 6]
```

### 3.3 설계 결정 사항

| 항목 | 결정 | 근거 |
|---|---|---|
| **기준 축** | XHTML block 요소 | 1개 XHTML block → N개 MDX 라인이 자연스러운 변환 방향. 역방향(N:1)은 거의 없음 |
| **MDX 식별** | 블록 순서 인덱스 | 줄 번호는 AI 수정 시 바뀜. 블록 파서 순서 인덱스는 블록 내 텍스트 변경에 불변 |
| **1:N 매핑** | `mdx_blocks` 배열 | 1개 XHTML block 내 여러 문장이 각각 MDX 라인으로 변환되는 정책 반영 |
| **Fallback** | 없음 (매핑 필수) | 매핑 파일 없으면 reverse-sync 거부. 재생성이 쉬우므로 fuzzy matching 유지 불필요 |
| **파일 형식** | YAML | human-readable, 기존 프로젝트의 `pages.yaml` 등과 일관 |
| **유효성 검증** | 파일 mtime 비교 | `mapping.yaml` mtime = 원본 MDX mtime으로 설정. timestamp 비교로 가볍게 검증 |
| **text_digest** | 미포함 | mtime 비교로 충분. 스키마 단순화 |

### 3.4 생성, 유효성 검증, 재생성

**생성:**
- Forward converter가 XHTML → MDX 변환 시 자동 생성
- 생성 후 `mapping.yaml`의 파일 mtime을 원본 MDX 파일의 mtime과 동일하게 설정 (`touch -r`)

**유효성 검증 (timestamp 비교):**
- Reverse-sync 실행 시 `mapping.yaml`의 mtime과 original MDX의 mtime을 비교
- `mapping.yaml` mtime ≥ original MDX mtime → 유효 (매핑이 현재 MDX 기준으로 생성됨)
- `mapping.yaml` mtime < original MDX mtime → 무효 (MDX가 재변환되었으나 매핑 미갱신)
- 무효 시 reverse-sync를 거부하고, forward converter 재실행을 안내

**재생성:**
- Forward converter 재실행으로 전체 매핑 파일 일괄 재생성 가능
- 재생성 비용이 낮으므로, 의심스러울 때 재생성하면 됨

### 3.5 xhtml_type 값

| xhtml_type | 대응 XHTML 요소 |
|---|---|
| `heading` | `<h1>` ~ `<h6>` |
| `paragraph` | `<p>` |
| `list` | `<ul>`, `<ol>` |
| `table` | `<table>` |
| `code_block` | `<ac:structured-macro ac:name="code">` |
| `macro` | 기타 `<ac:structured-macro>` (info, warning, note 등) |

### 3.6 Reverse-Sync Pipeline 변경

기존 pipeline에서 변경되는 부분:

```
기존: ② Block diff → ③ _find_mapping_by_text() (7단계 fuzzy matching)
변경: ② Block diff → ③ mapping.yaml lookup (인덱스 기반 직접 참조)
```

- `_find_mapping_by_text()` 함수와 7단계 fallback 로직 전체 제거
- `_normalize_mdx_to_plain()` 함수 제거 (더 이상 필요 없음)
- `mapping_recorder.py`는 forward converter 측으로 이동하거나 통합

## 4. 구현 현황

### 4.1 생성 방식: Post-hoc Sequential Matching

Converter 내부(1600줄 `core.py`)를 계측하지 않고, 변환 완료 후 기존 모듈 2개를 조합하는 방식을 채택했습니다.

1. `record_mapping(xhtml)` → XHTML 블록 추출 (기존 `reverse_sync/mapping_recorder.py` 재사용)
2. `parse_mdx_blocks(mdx)` → MDX 블록 파싱 (기존 `reverse_sync/mdx_block_parser.py` 재사용)
3. 양쪽을 순서대로 매칭 — 두 모듈 모두 문서 순서(top-down)로 순회하므로 순서가 보존됨

**장점:**
- `core.py` 수정 불필요
- 기존 테스트된 모듈 2개를 그대로 조합
- 변환 로직과 매핑 로직의 관심사 분리

### 4.2 실제 생성된 매핑 파일 형식

```yaml
version: 1
source_page_id: "544112828"
generated_at: "2026-02-12T11:02:52Z"
mdx_file: page.mdx
mappings:
  - xhtml_xpath: "h2[1]"
    xhtml_type: heading
    mdx_blocks: [4]
  - xhtml_xpath: "macro-info[1]"
    xhtml_type: html_block
    mdx_blocks: [22]
```

- `converter_version` 필드는 설계안 대비 생략 (버전 관리 필요 시 추후 추가)
- `mdx_file` 필드 추가 (출력 파일명 참조용)
- `xhtml_xpath`는 간이 XPath (`h2[1]`, `macro-info[1]` 등) — 설계안의 `//` prefix 없이 단순화

### 4.3 수정 파일

| 파일 | 변경 | PR |
|---|---|---|
| `bin/converter/sidecar_mapping.py` | **신규** — 매핑 생성 로직 (~140줄) | querypie-docs#682 |
| `bin/converter/cli.py` | **수정** — 원본 XHTML 보존 + 매핑 생성 호출 (+13줄) | querypie-docs#682 |

### 4.4 검증 결과

- 21개 테스트 케이스 전체에서 `mapping.yaml` 정상 생성
- 기존 pytest 202개 테스트 모두 통과 (회귀 없음)
- 매핑 생성 실패 시 try/except로 변환 차단하지 않음

## 6. 범위 한정 (Scope)

### 이번 설계에 포함

- [x] Forward converter에 매핑 파일 생성 기능 추가
- [ ] Reverse-sync pipeline에서 fuzzy matching → sidecar lookup 전환
- [ ] 블록 내 텍스트 변경의 reverse-sync (Phase 1 기능 유지, 새 매핑 방식으로 전환)

### 추후 별도 검토 (YAGNI)

- 블록 추가/삭제/이동/분할/병합 (Phase 2 구조적 변경)
- MDX 블록 인덱스 변동 시 매핑 갱신 전략
- XHTML에 새 요소를 삽입할 때의 위치 결정 방법

## 진행 로그

| 날짜 | PR | 내용 |
|------|-----|------|
| 2026-02-12 | querypie-docs#682 | Forward converter sidecar mapping 생성 기능 구현 |

## 7. 다음 단계

- [x] **상세 구현 계획 작성** — forward converter 변경 범위 산정, 코드 수정 계획
- [x] **Forward converter 변경** — 매핑 파일 생성 기능 구현 (querypie-docs#682)
- [ ] **Reverse-sync pipeline 전환** — fuzzy matching 제거, sidecar lookup 적용
- [ ] **기존 테스트 케이스 검증** — 19개 integration test가 새 매핑 방식으로 통과하는지 확인

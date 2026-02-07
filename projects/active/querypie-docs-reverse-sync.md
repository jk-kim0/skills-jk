---
id: querypie-docs-reverse-sync
title: QueryPie Docs Reverse Sync
status: active
repos:
  - https://github.com/chequer-io/querypie-docs
created: 2026-02-07
---

# QueryPie Docs Reverse Sync

## 목표

AI Agent가 개선한 MDX 문서의 변경사항을 원본 Confluence 문서에 신뢰성 있게 역반영하는 파이프라인을 구축한다.

## 범위

### 배경

#### 현재 파이프라인 (단방향)

```
Confluence (QM Space) → XHTML → MDX → Nextra 사이트 (docs.querypie.com)
```

- `querypie-docs/confluence-mdx/` 에 구축된 변환 도구
- `confluence_xhtml_to_markdown.py` (2255줄) — 핵심 forward converter
- Docker + GitHub Actions로 자동화됨

#### 문제

AI Agent를 이용해 MDX 문서를 개선(오탈자 교정, 문장 개선, 구조 개선)하고 있으나, 개선 결과가 MDX에만 반영되고 원본 Confluence에는 반영되지 않는다. 내부 팀이 Confluence에서 직접 문서를 작성/편집하므로, Confluence가 최신 상태를 유지해야 한다.

#### 장기 방향

- 단기: Confluence를 source of truth로 유지하며 역반영 파이프라인 구축
- 장기: MDX 중심으로 점진적 전환

### 변경 범위 (Phase별)

| Phase | 범위 | 설명 |
|-------|------|------|
| Phase 1 | 텍스트 수준 변경 | 오탈자 교정, 문장 다듬기, 용어 통일. 문서 구조 유지 |
| Phase 2 | 구조적 변경 | 헤딩 재구성, 섹션 분리/통합, Callout 추가 등 |
| Phase 3 | 전면 재구성 | 문서 구조, 위치, 이름 변경 |

이 설계는 **Phase 1을 주 대상**으로 하며, Phase 2 확장 방향을 포함한다.

## 설계

### 핵심 메커니즘: 블록 매핑 기반 역반영

#### 기본 아이디어

기존 forward converter를 계측(instrument)하여, 변환 시 **XHTML 요소 ↔ MDX 블록** 매핑을 기록한다. 이 매핑을 이용해 MDX의 변경사항을 XHTML의 정확한 위치에 적용한다.

```
[변환 시 매핑 생성]
XHTML  <p>데이터베이스 접근 제어를 설정합니다.</p>
  ↕ mapping record
MDX    데이터베이스 접근 제어를 설정합니다.

[역반영 시]
1. 원본 MDX vs 개선 MDX → diff 추출
2. diff: "접근 제어" → "접근 통제"
3. mapping으로 대응하는 XHTML <p> 요소를 찾음
4. XHTML 내 텍스트를 업데이트
```

#### 매핑 단위: 블록

매핑은 **블록(block) 단위**로 수행한다.

- 블록: paragraph, heading, list-item, code-block, table 등 의미 단위
- 각 블록은 XHTML 요소와 MDX 줄 범위에 대응
- **블록 내부의 인라인 구조는 매핑하지 않음** (`**bold**` ↔ `<strong>` 등)

매핑 대상 블록 유형:

| XHTML 요소 | MDX 결과 | 비고 |
|------------|---------|------|
| `<p>` | 평문 텍스트 | 1:1 대응 |
| `<h1>`~`<h6>` | `##`~`######` | 레벨 +1 보정 |
| `<li>` | `- item` / `1. item` | 중첩 구조 추적 필요 |
| `<td>`/`<th>` | 테이블 셀 | 행/열 위치로 매핑 |
| `<ac:structured-macro name="code">` | ` ```lang ``` ` | CDATA 그대로 |

인라인 서식 보존 전략: XHTML 요소 내에서 평문 텍스트(text node)를 추출하고, old_text → new_text의 변경 부분을 text node 레벨에서 찾아 치환한다. `<strong>`, `<em>` 등 태그 구조는 건드리지 않는다.

### 파이프라인

#### Phase A: 로컬 검증 (네트워크 불필요, 반복 실행 가능)

```
① MDX 블록 파싱    (원본 MDX + 개선 MDX)
② 블록 Diff 추출   (변경된 블록 목록)
③ 매핑 로드        (mapping.yaml — 사전 생성됨)
④ XHTML 패치      (원본 XHTML + diff → 수정된 XHTML)
⑤ Forward 변환     (수정된 XHTML → 검증 MDX)
⑥ 완전 일치 검증   (검증 MDX == 개선 MDX)

결과: PASS / FAIL + 차이점 리포트
```

#### Phase B: Confluence 반영 (검증 통과 후 명시적 실행)

```
⑦ 검증 통과한 XHTML을 Confluence API로 업데이트
```

Phase A와 Phase B는 **완전히 분리된 명령**으로 실행한다.

```bash
# Phase A: 로컬 검증 (반복 가능)
python bin/reverse_sync.py verify \
  --page-id 544375784 \
  --original-mdx src/content/ko/overview.mdx \
  --improved-mdx improved/ko/overview.mdx

# Phase B: Confluence 반영 (검증 통과분만)
python bin/reverse_sync.py push \
  --page-id 544375784
```

#### Round-trip 검증 기준

검증은 **문자 단위 완전 일치(exact match)** 를 기준으로 한다.

- 공백 차이 → 불일치
- 줄바꿈 차이 → 불일치
- 인라인 서식 차이 → 불일치
- 어떤 정규화도 하지 않음

통과 = 검증 MDX의 모든 문자가 개선 MDX와 동일.
실패 = 1문자라도 다르면 실패, 차이점 리포트 생성 후 해당 페이지 건너뜀.

이 엄격한 기준은 XHTML 패치 시 공백, text node 경계까지 forward converter의 동작을 고려해야 함을 의미한다. 대신 **Confluence에 잘못된 내용이 올라가는 것을 완전히 방지**한다.

### Diff 추출 상세

#### Phase 1: 순차 비교

블록 시퀀스 구조가 동일하므로 1:1 순차 비교:

```
원본 블록: [h2-A, p-B, p-C, ul-D, code-E, p-F]
개선 블록: [h2-A, p-B, p-C, ul-D, code-E, p-F]  <- 구조 동일

각 블록의 텍스트를 비교하여 변경된 블록만 추출:
  diff = [
    { block_id: "p-2", type: "modified",
      old_text: "접근 제어를 설정합니다.",
      new_text: "접근 통제를 설정합니다." }
  ]
```

#### Phase 2: 시퀀스 정렬 (확장)

블록이 추가/삭제/이동될 수 있으므로 시퀀스 정렬 알고리즘 사용:

```
원본 블록: [h2-A, p-B, p-C,       ul-D, code-E, p-F]
개선 블록: [h3-A, p-B, callout-X, p-C', ul-D, p-F]

정렬 결과:
  h2-A    <-> h3-A     -> modified (레벨 변경)
  p-B     <-> p-B      -> unchanged
  (없음)  <-> callout-X -> added
  p-C     <-> p-C'     -> modified
  ul-D    <-> ul-D     -> unchanged
  code-E  <-> (없음)    -> removed
  p-F     <-> p-F      -> unchanged
```

Phase 2에서 `added` 블록은 MDX -> Confluence XHTML 부분 역변환이 필요하다 (callout -> panel 매크로 등 한정된 범위).

### 매핑 데이터 구조

```python
@dataclass
class BlockMapping:
    block_id: str           # 고유 식별자
    type: str               # paragraph | heading | list_item | code | table
    xhtml_element: str      # XHTML 요소 참조 (XPath 등)
    xhtml_text: str         # 원본 텍스트 (서식 태그 포함)
    xhtml_plain_text: str   # 평문 텍스트 (서식 태그 제거)
    mdx_text: str           # 변환된 MDX 텍스트
    mdx_line_start: int     # MDX 파일 내 시작 줄
    mdx_line_end: int       # MDX 파일 내 끝 줄
    children: List[str]     # 하위 블록 ID (nested list 등)
```

출력 형식 (`mapping.yaml`):

```yaml
page_id: "544375784"
blocks:
  - block_id: "h2-1"
    type: heading
    xhtml_xpath: "/body/h2[1]"
    xhtml_text: "시스템 아키텍처 개요"
    mdx_text: "## 시스템 아키텍처 개요"
    mdx_line_start: 3
    mdx_line_end: 3
  - block_id: "p-1"
    type: paragraph
    xhtml_xpath: "/body/p[1]"
    xhtml_text: "<strong>접근 제어</strong>를 설정합니다."
    xhtml_plain_text: "접근 제어를 설정합니다."
    mdx_text: "**접근 제어**를 설정합니다."
    mdx_line_start: 5
    mdx_line_end: 5
```

## 산출물

### Phase 1 산출물

```
querypie-docs/
  confluence-mdx/
    bin/
      confluence_xhtml_to_markdown.py  (기존, 수정 최소화)
      reverse_sync.py                  (신규 - 메인 진입점)
      mapping_recorder.py              (신규 - 블록 매핑 생성)
      mdx_block_parser.py              (신규 - MDX 블록 파싱)
      block_diff.py                    (신규 - 블록 Diff 추출)
      xhtml_patcher.py                 (신규 - XHTML 텍스트 패치)
      roundtrip_verifier.py            (신규 - 완전 일치 검증)
    tests/
      test_mapping_recorder.py
      test_block_diff.py
      test_xhtml_patcher.py
      test_roundtrip_verifier.py
```

### Phase 2 추가 산출물

```
    bin/
      block_diff.py 확장              (시퀀스 정렬 알고리즘)
      xhtml_block_writer.py           (신규 - MDX->XHTML 부분 역변환)
    tests/
      test_xhtml_block_writer.py
```

## 핵심 설계 원칙

1. **기존 forward converter 수정 최소화**: 래퍼로 계측, 기존 로직 변경하지 않음
2. **로컬 우선**: 검증까지 모두 로컬에서 수행, Confluence API 호출은 별도 단계
3. **엄격한 검증**: 문자 단위 완전 일치, 정규화 없음
4. **안전한 실패**: 검증 실패 시 해당 페이지를 건너뛰고 리포트만 남김
5. **점진적 확장**: Phase 1(텍스트) -> Phase 2(구조) -> Phase 3(재구성)

## 마일스톤

### Phase 1 - 텍스트 수준 역반영

- [ ] mapping_recorder.py 구현
- [ ] mdx_block_parser.py 구현
- [ ] block_diff.py 구현
- [ ] xhtml_patcher.py 구현
- [ ] roundtrip_verifier.py 구현
- [ ] reverse_sync.py 오케스트레이터 구현
- [ ] 실제 문서로 검증

### Phase 2 - 구조적 변경 역반영

- [ ] block_diff.py 시퀀스 정렬 확장
- [ ] xhtml_block_writer.py 구현

### Phase 3 - 전면 재구성

- [ ] Confluence API 페이지 이동/이름 변경 연동
- [ ] 설계 추가 필요

## 메모

- 대상 저장소: `querypie-docs/confluence-mdx/`
- 기존 forward converter: `confluence_xhtml_to_markdown.py` (2255줄, BeautifulSoup4)
- 기존 Confluence CLI: `skills-jk-1/bin/confluence` (update 명령 보유)
- Confluence Space: QM (QueryPie Manual)
- 원본 XHTML 저장 위치: `confluence-mdx/var/<page_id>/page.xhtml`

# QueryPie Docs Reverse Sync — Phase 1 회고 및 개선 방안

> **Status:** 조치 완료 — 즉시 조치 3건 중 2건 완료, 매핑 재설계(Sidecar) 완료
> **관련 프로젝트:** [Phase 1 (완료)](../done/querypie-docs-reverse-sync.md) · [Phase 2/3 (미착수)](querypie-docs-reverse-sync-phase2.md) · [매핑 재설계 (완료)](querypie-docs-reverse-sync-mapping-redesign.md)
> **분석 대상 기간:** 2026-02-08 ~ 2026-02-11 (PR #609 ~ #677)
> **분석 목적:** Phase 1 "완료" 이후 지속되는 bug fix PR의 근본 원인을 파악하고, Phase 2 착수 전 설계 개선 방안을 도출한다.

---

## 1. 현황 요약

### 1.1 PR 통계 (3일간)

| 구분 | 건수 | 비율 |
|------|------|------|
| **Merged** | 37건 | — |
| **Open** | 5건 (#673~#677) | — |
| **Closed (폐기)** | 3건 (#627, #640, #662) | — |
| 그 중 `fix(reverse-sync)` | **20건** | 전체의 50% |
| 그 중 `feat(reverse-sync)` | 8건 | 20% |
| 기타 (refactor, docs, mdx 등) | 17건 | 30% |

### 1.2 reverse-sync 코드 규모

| 모듈 | 라인 수 | 역할 |
|------|---------|------|
| `reverse_sync_cli.py` | **1,143** | 오케스트레이터 + 핵심 알고리즘 |
| `xhtml_patcher.py` | 268 | XHTML 텍스트 패칭 |
| `mapping_recorder.py` | 232 | XHTML 블록 매핑 생성 |
| `mdx_to_xhtml_inline.py` | 202 | MDX→XHTML 인라인 변환 |
| `mdx_block_parser.py` | 129 | MDX 블록 파싱 |
| `roundtrip_verifier.py` | 72 | 라운드트립 검증 |
| `confluence_client.py` | 64 | Confluence API |
| `block_diff.py` | 34 | 블록 비교 |
| **합계** | **2,184** | — |

핵심 로직의 52%가 `reverse_sync_cli.py` 한 파일에 집중되어 있다.

---

## 2. 버그 분류 및 패턴 분석

### 2.1 Category A: 텍스트 정규화 실패 (7건)

MDX plain text ↔ XHTML plain text 비교 시 정규화 규칙 누락으로 매칭 실패.

| PR | 누락된 정규화 |
|----|-------------|
| #674 | `*italic*` 마커 제거 |
| #675 | heading 내 backtick/bold/HTML 태그 제거 |
| #672 | Confluence 링크 `Title\|Anchor` 패턴 |
| #650 | Markdown 링크 `[text](url)` → `text` |
| #665 | 이모지 (ac:emoticon ↔ MDX 유니코드) |
| #667 | 보이지 않는 유니코드 문자 (U+200B, U+3164 등) |
| #668 | 한국어 날짜 형식 ("2024년 01월 15일" ↔ "Jan 15, 2024") |

**패턴**: `_normalize_mdx_to_plain()` 함수에 `re.sub()` 규칙이 점진적으로 추가되는 **Whack-a-Mole** 패턴. 새로운 문서를 처리할 때마다 새 정규화 규칙이 필요하다.

### 2.2 Category B: 블록 매핑 실패 (6건)

MDX 블록과 XHTML 요소 간의 대응 관계를 찾지 못하는 문제.

| PR | 매핑 실패 원인 |
|----|--------------|
| #634 | 인덱스 기반 매핑의 근본 결함 (오프셋 불일치) |
| #653 | prefix 매칭이 짧은 캡션 → 긴 리스트로 오매칭 |
| #658 | 동일 텍스트 블록이 항상 첫 번째 XHTML 요소에 매핑 |
| #673 | 부모-자식 중복 매핑 (used_ids 추적 미흡) |
| #671 | html_block이 직접 매핑 불가 (substring fallback 필요) |
| #667 | 리스트 항목의 substring 매칭 필요 |

**패턴**: `_find_mapping_by_text()` 함수의 fallback tier가 4단계 → 7단계로 성장. 현재 fallback 계층:

```
1차: 정확 일치 (공백 축약)
2차: prefix 일치 (50자+, 길이 유사도)
3차: 공백 무시 비교
3.2차: 보이지 않는 문자 무시
3.5차: 이모지 무시
4차: 리스트 마커 제거
(+ containing_changes: substring 포함 관계 탐색)
```

### 2.3 Category C: XHTML 구조 파괴 (4건)

패치 적용 시 Confluence 전용 인라인 구조가 훼손되는 문제.

| PR | 파괴된 구조 |
|----|-----------|
| #633 | `<code>`, `<ac:link>` 등 인라인 태그 소실 |
| #634 | `ac:image`, `ol`, `h2` 등 엉뚱한 요소 패치 |
| #648 | `ri:attachment`, `ac:caption`, `ac:adf-mark` 파괴 |
| #669 | `<![CDATA[...]]>` BeautifulSoup 파싱 시 소실 |

**패턴**: 초기 설계(innerHTML 전체 교체)의 근본 결함. PR #633→#648에서 텍스트 레벨 패칭으로 전환하며 대부분 해결되었으나, 파서(BeautifulSoup) 고유 동작에 의한 추가 이슈가 잔존.

### 2.4 Category D: Confluence 매크로 미지원 (3건)

새로운 Confluence 매크로 유형을 만날 때마다 지원 코드 추가 필요.

| PR | 매크로 유형 |
|----|-----------|
| #655 | `macro-*` xpath → `ac:structured-macro` 해석 |
| #656 | Callout 매크로 다중 블록 (`ac:rich-text-body`) |
| #657 | ADF 포맷 (`ac:adf-extension`, `ac:adf-content`) |

### 2.5 Category E: 검증 오탐 (2건)

| PR | 오탐 원인 |
|----|---------|
| #650 | frontmatter의 `confluenceUrl` 차이 |
| #668 | forward converter의 날짜 형식 변환 |

---

## 3. 근본 원인 분석

### 3.1 핵심 문제: "두 세계의 Impedance Mismatch"

reverse-sync의 근본적 어려움은 **MDX와 Confluence XHTML이 동일 콘텐츠의 완전히 다른 표현**이라는 점에 있다.

```
Confluence XHTML:
  <ac:structured-macro ac:name="info">
    <ac:rich-text-body>
      <p>시스템 <ac:link><ri:page ri:content-title="설정"/><ac:plain-text-link-body>
      <![CDATA[설정]]></ac:plain-text-link-body></ac:link> 가이드</p>
    </ac:rich-text-body>
  </ac:structured-macro>

MDX (forward 변환 결과):
  :::info
  시스템 [설정](/ko/admin-manual/settings) 가이드
  :::
```

이 두 표현 사이에는 다음과 같은 차이가 있다:

| 차이 유형 | 예시 |
|----------|------|
| **인라인 구조** | `<ac:link>` → `[text](url)` |
| **매크로 구조** | `ac:structured-macro` → `:::callout` |
| **텍스트 노드 경계** | `<p>시스템 <code>설정</code> 가이드</p>` → 3개 텍스트 노드 vs 1개 문자열 |
| **숨겨진 문자** | XHTML에만 존재하는 U+200B, U+3164 |
| **이모지 인코딩** | `ac:emoticon` vs 유니코드 이모지 |
| **날짜 형식** | forward converter가 한국어→영어로 변환 |
| **메타데이터** | forward converter가 `confluenceUrl` 등 주입 |

**현재 접근 방식**은 이 차이를 **정규화 규칙으로 하나씩 흡수**하는 것이다. 그러나 정규화 규칙의 수는 Confluence 마크업의 다양성에 비례하여 무한히 증가한다.

### 3.2 아키텍처 관점 문제

#### Problem 1: 매핑의 부재 — Forward 변환 시 원본 정보 소실

Forward converter (XHTML → MDX)는 **변환 시 원본 XHTML 요소와의 대응 관계를 기록하지 않는다**. 따라서 reverse-sync는 변환 결과(MDX)만 보고 원본(XHTML)의 어디를 수정해야 하는지 **추측**해야 한다.

이것이 "텍스트 기반 fuzzy matching" 접근의 근본 원인이다.

#### Problem 2: 오케스트레이터의 비대화 (God Object)

`reverse_sync_cli.py`(1,143줄)에 다음 책임이 모두 집중되어 있다:

- CLI 인터페이스 (argparse)
- MDX 소스 해석 (git ref, 파일 경로)
- 페이지 ID 유도
- **텍스트 정규화** (`_normalize_mdx_to_plain`)
- **블록 매핑** (`_find_mapping_by_text`, 7-tier fallback)
- **텍스트 전이** (`_transfer_text_changes`, `_align_chars`)
- **패치 빌드** (`_build_patches`, 리스트/html_block 분기)
- 검증 파이프라인
- Confluence push

이 중 볼드 처리된 4개 함수가 **버그의 90%를 차지**하며, 독립 모듈로 분리되지 않아 테스트와 디버깅이 어렵다.

#### Problem 3: 정규화의 비대칭성

MDX → plain text 정규화(`_normalize_mdx_to_plain`)와 XHTML → plain text 추출(`BeautifulSoup.get_text()`)은 **서로 다른 알고리즘**으로 "같은 결과"를 내려고 시도한다. 그러나 두 알고리즘의 동작이 미묘하게 달라 끊임없이 패치가 필요하다.

---

## 4. 개선 방안

### 4.1 단기 개선 (Phase 1 안정화, 코드 변경 필요)

#### A. 오케스트레이터 분리 리팩토링

`reverse_sync_cli.py`에서 핵심 알고리즘을 별도 모듈로 추출한다:

| 새 모듈 | 추출 대상 함수 |
|---------|--------------|
| `text_normalizer.py` | `_normalize_mdx_to_plain`, `_collapse_ws`, `_strip_list_marker`, `_EMOJI_RE`, `_INVISIBLE_RE` |
| `block_matcher.py` | `_find_mapping_by_text`, `_find_containing_mapping`, 전체 fallback 로직 |
| `text_transfer.py` | `_transfer_text_changes`, `_align_chars`, `_find_insert_pos` |
| `patch_builder.py` | `_build_patches`, `_build_list_item_patches`, `_split_list_items` |

**효과**: 모듈별 단위 테스트 가능, 책임 분리, 디버깅 용이

#### B. 정규화 테스트 매트릭스

현재 발견된 모든 정규화 케이스를 테이블로 관리하고, 새로운 문서 처리 전에 해당 매트릭스를 검증한다:

```python
# test_text_normalizer.py
NORMALIZATION_CASES = [
    ("**bold**", "bold"),
    ("`code`", "code"),
    ("*italic*", "italic"),
    ("[text](url)", "text"),
    ("Title|Anchor", ...),
    # ... 모든 케이스를 테이블 구동 테스트로 관리
]
```

#### C. 매칭 실패 로깅 강화

현재 매칭 실패 시 `None`을 반환하고 조용히 건너뛴다. 대신 어떤 tier까지 시도했는지, 왜 실패했는지를 구조화된 로그로 남긴다.

### 4.2 중기 개선 (설계 개선, Phase 2 착수 전 고려)

#### D. Forward Converter에 Block ID Embedding

**가장 근본적인 개선안.** Forward converter가 XHTML → MDX 변환 시, 각 블록에 원본 XHTML 요소의 식별자를 HTML 주석이나 frontmatter로 포함하도록 한다.

```mdx
{/* xhtml:p[3] */}
시스템 설정 가이드를 확인하세요.

{/* xhtml:macro-info[1]/p[1] */}
:::info
이 기능은 관리자 권한이 필요합니다.
:::
```

**효과**: fuzzy text matching 완전 제거, 매핑이 결정적(deterministic)으로 변환

**비용**: forward converter 수정 필요 (현재 설계 원칙 "기존 forward converter 수정 최소화"와 충돌)

**평가**: Phase 1의 설계 원칙은 "빠른 프로토타이핑"에 적합했으나, Phase 2 진행 시 구조적 변경(블록 추가/삭제)의 매핑 문제가 텍스트 매칭으로는 해결 불가능하다. **Phase 2의 전제 조건**으로 재검토해야 한다.

#### E. 공통 Plain Text 추출기

MDX와 XHTML **양쪽 모두에 동일한 정규화 파이프라인**을 적용한다. 현재는 MDX 쪽은 `_normalize_mdx_to_plain()`, XHTML 쪽은 `BeautifulSoup.get_text()`로 서로 다른 알고리즘이다.

개선: Forward converter의 변환 로직을 참조하여, **XHTML에서 MDX를 거쳐 plain text를 추출하는 단일 경로**를 구축한다.

```
XHTML 요소 → (forward converter 로직) → MDX 텍스트 → strip markers → plain text
```

이렇게 하면 양쪽의 plain text가 **동일한 변환 파이프라인**을 통과하므로, 정규화 차이가 원천적으로 제거된다.

#### F. 구조적 매칭 (DOM 기반)

텍스트 매칭 대신 **XHTML DOM 트리 구조**를 활용한다. Forward converter가 "이 `<p>` 태그는 heading 바로 다음에 나오는 첫 번째 paragraph"라는 구조 정보를 활용하면, 텍스트가 동일한 여러 요소 중 올바른 것을 특정할 수 있다.

---

## 5. 권고사항

### 5.1 즉시 조치 (Phase 1 안정화)

1. ~~Open PR 5건 (#673~#677) 리뷰 및 머지~~ → **완료** (2026-02-11, 전부 머지)
2. ~~`reverse_sync_cli.py` 리팩토링 (Section 4.1-A) — 모듈 분리~~ → **완료** (querypie-docs#679: `text_normalizer.py`, `block_matcher.py`, `text_transfer.py`, `patch_builder.py` 4개 모듈 분리)
3. 정규화 테스트 매트릭스 구축 (Section 4.1-B) — 미착수 (Sidecar 전환으로 정규화 의존도 대폭 감소)
4. 매칭 실패 로깅 강화 (Section 4.1-C) — 미착수 (Sidecar 전환으로 fuzzy matching 제거됨)

### 5.2 Phase 2 착수 전 필수 검토

1. ~~**Block ID Embedding 방안 결정** (Section 4.2-D)~~ → **완료** — Sidecar Mapping File 방식으로 결정 및 구현 완료 ([매핑 재설계 문서](querypie-docs-reverse-sync-mapping-redesign.md) 참조)
   - Forward converter가 `var/<page_id>/mapping.yaml` 생성 (querypie-docs#682)
   - Reverse-sync pipeline이 sidecar O(1) 직접 조회로 전환 (querypie-docs#688, #694)
   - Fuzzy matching 완전 제거, `block_matcher.py` 삭제
2. **공통 Plain Text 추출기 설계** (Section 4.2-E) — 미착수 (Sidecar 전환으로 정규화 의존도 대폭 감소하여 우선순위 하락)
3. 현재 테스트 커버리지 검토
   - pytest 251개로 확대 (Phase 1 초기 대비 +49)
   - 148개 페이지 배치 verify 100% 통과
   - 특히 table, ADF panel, nested list, multi-language 문서에 대한 커버리지 추가 필요

### 5.3 결론

Phase 1의 reverse-sync는 **빠른 프로토타이핑**에 성공했다. 3일간 40+건의 PR로 "텍스트 수준 변경 역반영"이라는 핵심 기능을 동작하게 만들었다.

그러나 현재 아키텍처에는 **구조적 한계**가 있다:
- 텍스트 기반 fuzzy matching은 본질적으로 불완전하며, 새 문서 유형마다 규칙 추가가 필요하다
- 오케스트레이터의 비대화로 유지보수와 테스트가 어렵다
- forward converter와의 인터페이스가 "블랙박스 출력 비교"에 의존한다

**Phase 2 진행 전에 이 구조적 한계를 해결하지 않으면, 구조적 변경 지원 시 복잡도가 기하급수적으로 증가할 것이다.** Forward converter에 Block ID를 embedding하는 방안(Section 4.2-D)이 가장 근본적인 해결책이며, Phase 2의 전제 조건으로 검토할 것을 권고한다.

---

## 6. 부록: 최근 3일 PR 전체 목록

### Merged (37건)

| PR | 제목 | 날짜 |
|----|------|------|
| #672 | fix(reverse-sync): Confluence 링크 Title\|Anchor 정규화 | 02-11 |
| #671 | fix(reverse-sync): html_block substring 매칭 fallback 추가 | 02-11 |
| #670 | docs(skills): sync-confluence-url 사용 가이드 Skill 추가 | 02-10 |
| #669 | fix(reverse-sync): BeautifulSoup CDATA 래핑 복원 | 02-10 |
| #668 | fix(reverse-sync): 한국어 날짜 형식 정규화로 roundtrip verify 통과 | 02-10 |
| #667 | fix(reverse-sync): 보이지 않는 유니코드 문자 매칭 및 리스트 항목 substring 매칭 지원 | 02-10 |
| #666 | mdx: en/ja 번역 파일에 confluenceUrl frontmatter 동기화 | 02-10 |
| #665 | fix(reverse-sync): _align_chars SequenceMatcher 기반 재작성 및 이모지/공백 매칭 개선 | 02-10 |
| #664 | fix(testcases): proofread 교정 결과를 testcase improved.mdx에 반영 | 02-10 |
| #663 | feat(sync): ko→en/ja confluenceUrl 동기화 CLI 추가 | 02-10 |
| #661 | mdx: 관리자 매뉴얼/Audit 문서 교정 및 오타 수정 (reverse-sync) | 02-10 |
| #660 | docs(skills): reverse-sync 사용 가이드 Skill 추가 | 02-10 |
| #659 | feat(reverse-sync): verify 배치 모드에 --failures-only 옵션 추가 | 02-10 |
| #658 | fix(reverse-sync): 중복 텍스트 매핑 시 잘못된 요소 매칭 방지 | 02-10 |
| #657 | feat(reverse-sync): ac:adf-extension 매핑 및 리스트 항목별 패치 지원 | 02-10 |
| #656 | feat(reverse-sync): Callout 매크로 다중 블록 매핑 지원 | 02-10 |
| #655 | fix(reverse-sync): macro-* xpath를 ac:structured-macro로 해석 | 02-10 |
| #654 | feat(reverse-sync): debug 커맨드 추가 및 verify 출력 간소화 | 02-10 |
| #653 | fix(reverse-sync): 리스트/테이블 블록 매핑 및 텍스트 전이 수정 | 02-10 |
| #652 | refactor(toc): Confluence 원문 링크 위치 및 디자인 개선 | 02-10 |
| #651 | docs(skills): XHTML Beautify-Diff Viewer 사용 가이드 추가 | 02-10 |
| #650 | fix(reverse-sync): frontmatter 제외 비교 및 마크다운 링크 정규화로 verify 실패 수정 | 02-10 |
| #649 | fix(skeleton): Badge 태그 속성 잘림 현상 수정 | 02-10 |
| #648 | fix(reverse-sync): innerHTML 교체 → 텍스트 레벨 패칭으로 verify 실패 수정 | 02-10 |
| #647 | feat(reverse-sync): CLI 경로 독립성 및 출력 개선 | 02-10 |
| #645 | fix(converter): emoji 패키지 미설치 시 converter 실행을 중단합니다 | 02-10 |
| #643 | mdx(ko): MDX frontmatter에 confluenceUrl 추가 | 02-10 |
| #642 | fix(tests): conftest.py 추가로 pytest PYTHONPATH 안정화 | 02-10 |
| #641 | fix(bin): python → python3으로 통일하여 macOS 호환성 확보 | 02-10 |
| #639 | refactor(tests): test-xhtml → test-convert 이름 변경 및 누락 타겟 추가 | 02-10 |
| #638 | feat(tests): xhtml-diff 테스트 타입 추가 | 02-10 |
| #637 | feat(bin): XHTML beautify-diff 도구 추가 | 02-10 |
| #636 | feat(ko): TOC 영역에 Confluence 원문 링크 컴포넌트 추가 | 02-10 |
| #635 | fix(tests): 이미지 경로를 slug 기반으로 통일하여 roundtrip 검증 pass | 02-10 |
| #634 | fix(reverse_sync): 위치 기반 매핑을 텍스트 기반 매핑으로 교체 | 02-10 |
| #633 | fix(reverse_sync): innerHTML 교체 시 old_plain_text 검증 가드 추가 | 02-09 |
| #632 | feat(reverse_sync): MDX→XHTML inner HTML 변환 모듈 추가 | 02-09 |

### ~~Open (5건)~~ → 전부 Merged (2026-02-11)

| PR | 제목 | 머지일 |
|----|------|--------|
| #677 | feat(pages_of_confluence): --recent 모드에서 변경 범위 자동 판별 기능 추가 | 02-11 |
| #676 | fix(reverse-sync): Markdown table 행별 분리 매칭 및 패딩 정규화 | 02-11 |
| #675 | fix(reverse-sync): heading 정규화에 backtick/bold/HTML 제거 추가 | 02-11 |
| #674 | fix(reverse-sync): italic(*...*) 제거 정규화 추가 | 02-11 |
| #673 | fix(reverse-sync): 동일 텍스트 블록 부모-자식 매핑 중복 방지 | 02-11 |

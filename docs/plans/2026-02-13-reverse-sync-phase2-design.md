# Reverse-Sync Phase 2 설계 — 구조적 변경 (블록 추가/삭제)

> **Date:** 2026-02-13
> **Status:** Approved
> **Target Repo:** querypie/querypie-docs (confluence-mdx/)
> **Related:** [Code Review](../../projects/active/querypie-docs-reverse-sync-code-review.md) | [Phase 2 계획](../../projects/active/querypie-docs-reverse-sync-phase2.md)

---

## 1. 배경

Phase 1 reverse-sync는 블록 수가 동일한 텍스트 변경만 처리한다. AI Agent가 섹션을 분리하거나 Callout/코드 블록을 추가하거나 불필요한 내용을 삭제하면, `block_diff.py`에서 블록 수 불일치 에러가 발생한다.

Phase 2는 블록 추가/삭제를 지원하여 구조적 변경을 Confluence XHTML에 역반영한다. 블록 이동(reorder)은 Phase 3 범위.

## 2. 접근 방식

**SequenceMatcher 기반 블록 정렬** (Approach A)

`difflib.SequenceMatcher`로 원본/개선 MDX 블록 시퀀스를 정렬하여 `equal`/`replace`/`insert`/`delete` opcode를 생성한다.

선정 사유:
- Python 표준 라이브러리, 검증된 알고리즘
- `text_transfer.py`에서 이미 사용 중
- Phase 2 범위(추가/삭제)에 정확히 부합
- Phase 3에서 이동 감지로 확장 가능

기각된 대안:
- **Sidecar 앵커 diff**: 기존 sidecar 인프라 활용하나, 결국 원본 비교와 동일하여 추가 indirection만 발생
- **투패스 유사도 매칭**: 이동 감지에 유리하나 Phase 2에서는 과잉 설계

---

## 3. 설계

### 3.1 `block_diff.py` — 시퀀스 정렬

**변경**: 1:1 순차 비교 → SequenceMatcher 기반

**BlockChange 확장**:
- `change_type`: `"modified"` | `"added"` | `"deleted"`
- `old_block`: `Optional[MdxBlock]` (added일 때 None)
- `new_block`: `Optional[MdxBlock]` (deleted일 때 None)

**반환값 확장**:
```python
def diff_blocks(original, improved) -> Tuple[List[BlockChange], Dict[int, int]]:
    # returns: (changes, alignment)
    # alignment: improved_idx → original_idx (매칭된 블록만)
```

**비교 키**: `normalize_mdx_to_plain(content, type)` + `collapse_ws()`. NON_CONTENT_TYPES(`frontmatter`, `import_statement`, `empty`)는 고유 키를 부여하여 항상 매칭.

**opcode 처리**:
- `equal`: 텍스트까지 동일하면 skip, 미세 변경이면 `modified`
- `replace`: 개별 `deleted` + `added`로 분해
- `insert`: `added`
- `delete`: `deleted`

### 3.2 패치 포맷 확장

기존 두 가지에 두 가지 추가:

```python
# modify (기존)
{"action": "modify", "xhtml_xpath": "p[3]",
 "old_plain_text": "...", "new_plain_text": "..."}

# modify_inner (기존)
{"action": "modify", "xhtml_xpath": "p[3]",
 "old_plain_text": "...", "new_inner_xhtml": "..."}

# delete (신규)
{"action": "delete", "xhtml_xpath": "p[3]"}

# insert (신규)
{"action": "insert", "after_xpath": "p[2]",
 "new_element_xhtml": "<p>새로운 내용</p>"}
```

하위 호환: `action` 키 없으면 기본값 `"modify"`.

### 3.3 `patch_builder.py` — 추가/삭제 패치 생성

**`_build_delete_patch(change, mappings, sidecar_index)`**:
원본 MDX 인덱스 → sidecar → xhtml_xpath → `{"action": "delete", ...}`

**`_build_insert_patch(change, changes, original_blocks, improved_blocks, sidecar_index)`**:
1. `_find_insert_anchor()`: improved 시퀀스에서 선행 매칭 블록의 xhtml_xpath 탐색. `alignment` map을 역순 탐색하여 가장 가까운 앵커 결정
2. `mdx_block_to_xhtml_element()`: 추가 블록의 XHTML 생성
3. `{"action": "insert", "after_xpath": ..., "new_element_xhtml": ...}` 반환

첫 번째 위치 삽입(선행 앵커 없음): `"after_xpath": null` → XHTML 첫 블록 앞에 삽입.

기존 `modified` 처리는 6-path 로직 그대로 유지.

### 3.4 `xhtml_patcher.py` — DOM 구조 변경

**적용 순서**:
1. **delete** (뒤에서 앞으로 — xpath 인덱스 보존)
2. **insert** (앞에서 뒤로)
3. **modify** (기존 로직)

**`_insert_element(soup, patch)`**:
- `after_xpath`가 있으면: 해당 요소 뒤에 삽입 (`insert_after`)
- `after_xpath`가 None이면: 첫 블록 요소 앞에 삽입 (`insert_before`)

**빈 컨테이너 처리**: Callout 내부 자식 전체 삭제 시 빈 callout은 그대로 유지 (추후 최적화).

`_find_element_by_xpath()` 재활용으로 `ac:layout` 내부도 자동 처리.

### 3.5 `mdx_to_xhtml_inline.py` — 완전한 XHTML 요소 생성

**새 함수**: `mdx_block_to_xhtml_element(block: MdxBlock) -> str`

기존 `mdx_block_to_inner_xhtml()`을 호출하고 블록 타입에 따라 outer tag 래핑:

| 블록 타입 | 생성 XHTML |
|----------|-----------|
| heading | `<h{level}>inner</h{level}>` |
| paragraph | `<p>inner</p>` |
| list | `<ul>inner</ul>` 또는 `<ol>inner</ol>` |
| code_block | `<ac:structured-macro ac:name="code">...</ac:structured-macro>` |
| html_block | content 그대로 반환 |

### 3.6 파이프라인 통합 (`reverse_sync_cli.py`)

변경 3곳:
1. `diff_blocks()` 반환값: `changes` → `changes, alignment`
2. `build_patches()` 호출: `alignment` 인자 추가
3. diff.yaml 직렬화: `old_block`/`new_block` None 처리

변경하지 않는 모듈: `mapping_recorder.py`, `sidecar_lookup.py`, `text_normalizer.py`, `text_transfer.py`, `roundtrip_verifier.py`, forward converter.

---

## 4. 테스트

### 단위 테스트 (~45개)

| 모듈 | 테스트 내용 |
|------|-----------|
| `block_diff.py` | equal/insert/delete/replace opcode, alignment map, NON_CONTENT 처리 |
| `patch_builder.py` | `_build_delete_patch`, `_build_insert_patch`, `_find_insert_anchor`, modified 회귀 |
| `xhtml_patcher.py` | delete 적용, insert 적용 (중간/처음/끝), 적용 순서 |
| `mdx_to_xhtml_inline.py` | `mdx_block_to_xhtml_element()` 블록 타입별 |

### E2E 테스트 (5개)

1. paragraph 추가 (기존 블록 사이에 삽입)
2. paragraph 삭제
3. heading 섹션 분리 (H2 + long_P → H2 + P1 + H3 + P2)
4. code block 추가 (ac:structured-macro 삽입)
5. 추가 + 삭제 + 수정 복합 시나리오

### 회귀

기존 310개 테스트 전부 통과 유지.

### 성공 기준

Round-trip 검증 통과: 패치된 XHTML → forward 변환 → improved MDX 비교.

---

## 5. 범위 외 (Phase 3)

- 블록 이동/재정렬
- 빈 컨테이너 자동 삭제
- Confluence 전용 매크로(Callout 등) MDX→XHTML 생성

---

## 6. 운영 가드레일 (2026-04 review follow-up)

이 문서는 Phase 2의 diff/patch 설계를 다루지만, 이후 reverse-sync를 장시간 실행하는 오케스트레이터나 자동화 CLI로 확장할 때 아래 가드레일을 기본 규칙으로 가져가야 한다. 이 항목들은 `skills-jk`의 review tooling 점검에서 실제로 드러난 운영 결함을 reverse-sync 설계로 역반영한 것이다.

### 6.1 런타임 의존성 fail-fast 검증

- 환경별로 달라지는 런타임 명령, 인증 정보, 외부 API 대상 repo/project 설정은 **라운드 루프나 state mutation 전에** 한 번에 검증한다.
- 누락 시 "무엇이 비어 있는지"를 구성 키 이름까지 포함해 즉시 실패시켜야 한다.
- reverse-sync에 적용하면, 향후 batch verify/push 오케스트레이터는 `gh`, Confluence credential, worktree root, 결과 게시 대상(repo 또는 artifact storage)를 시작 시점에 검증해야 한다.

### 6.2 실패 보고 대상 분리

- 문서 내용 오류와 자동화/tooling 오류를 같은 대상에 보고하면 운영 노이즈가 커진다.
- reverse-sync 실패 보고를 자동화할 때는 "콘텐츠/페이지 이슈"와 "도구 자체 버그"의 보고 대상을 분리한다.
- 특히 도구 버그는 target docs repo나 사용자 작업 브랜치가 아니라, automation/infra를 관리하는 저장소나 별도 tracker에 기록하도록 설계한다.

### 6.3 cleanup / git 명령의 cwd 독립성

- cleanup 류 helper는 현재 작업 디렉터리에 의존하지 않고, 항상 절대 경로 또는 `git -C <repo_root>` 형태로 실행한다.
- worktree 정리, 임시 산출물 삭제, verify artifact cleanup 모두 동일한 규칙을 따른다.
- 테스트도 repo root 밖의 임시 cwd에서 CLI를 호출해 동일하게 동작하는지 확인해야 한다.

### 6.4 테스트 요구사항

- 실패 보고 helper는 "어느 repo / tracker에 기록되는지"를 테스트로 고정한다.
- cleanup helper는 "repo root를 명시하지 않았을 때", "repo 밖 cwd에서 호출했을 때", "git command가 실패했을 때"를 모두 검증한다.
- startup validation은 누락된 설정별 에러 메시지까지 assertion해, 런타임 중간에 모호하게 실패하지 않도록 한다.

# Reverse-Sync Phase 2 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** MDX 블록 추가/삭제를 감지하여 Confluence XHTML에 구조적 변경을 역반영한다.

**Architecture:** `difflib.SequenceMatcher`로 원본/개선 MDX 블록 시퀀스를 정렬하여 added/deleted/modified 변경을 감지한다. 추가 블록은 `mdx_to_xhtml_inline.py`로 XHTML 요소를 생성하고, `xhtml_patcher.py`에서 DOM 삽입/삭제를 수행한다.

**Tech Stack:** Python 3, difflib, BeautifulSoup4, pytest

**Working Directory:** `/Users/jk/workspace/querypie-docs-translation-2/confluence-mdx`

**Test Command:** `cd /Users/jk/workspace/querypie-docs-translation-2/confluence-mdx && python3 -m pytest tests/ -v`

---

### Task 1: `block_diff.py` — BlockChange 데이터클래스 확장

**Files:**
- Modify: `bin/reverse_sync/block_diff.py:1-13`
- Test: `tests/test_reverse_sync_block_diff.py`

**Step 1: Write the failing test**

`tests/test_reverse_sync_block_diff.py`에 추가:

```python
def test_block_change_supports_optional_blocks():
    """BlockChange가 old_block=None (added), new_block=None (deleted)을 허용한다."""
    from reverse_sync.mdx_block_parser import MdxBlock
    block = MdxBlock(type='paragraph', content='Hello', line_start=1, line_end=1)

    added = BlockChange(index=0, change_type='added', old_block=None, new_block=block)
    assert added.old_block is None
    assert added.new_block is block

    deleted = BlockChange(index=0, change_type='deleted', old_block=block, new_block=None)
    assert deleted.old_block is block
    assert deleted.new_block is None
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/jk/workspace/querypie-docs-translation-2/confluence-mdx && python3 -m pytest tests/test_reverse_sync_block_diff.py::test_block_change_supports_optional_blocks -v`

Expected: FAIL — dataclass doesn't accept None for non-Optional fields (TypeError at instantiation)

**Step 3: Write minimal implementation**

`bin/reverse_sync/block_diff.py` 수정:

```python
"""Block Diff — 두 MDX 블록 시퀀스를 비교하여 변경된 블록을 추출한다."""
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from reverse_sync.mdx_block_parser import MdxBlock


@dataclass
class BlockChange:
    index: int              # 블록 인덱스 (original 기준 or improved 기준)
    change_type: str        # "modified" | "added" | "deleted"
    old_block: Optional[MdxBlock]   # None when added
    new_block: Optional[MdxBlock]   # None when deleted
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/jk/workspace/querypie-docs-translation-2/confluence-mdx && python3 -m pytest tests/test_reverse_sync_block_diff.py -v`

Expected: ALL PASS (기존 4개 + 신규 1개)

**Step 5: Commit**

```bash
git add bin/reverse_sync/block_diff.py tests/test_reverse_sync_block_diff.py
git commit -m "refactor(block_diff): make old_block/new_block Optional for add/delete support"
```

---

### Task 2: `block_diff.py` — SequenceMatcher 기반 `diff_blocks()` 재구현

**Files:**
- Modify: `bin/reverse_sync/block_diff.py:15-34`
- Test: `tests/test_reverse_sync_block_diff.py`

**Step 1: Write the failing tests**

`tests/test_reverse_sync_block_diff.py`에 추가 — 기존 `test_block_count_mismatch_raises` 삭제 후:

```python
from reverse_sync.mdx_block_parser import MdxBlock

def _make_block(content, type_='paragraph', line_start=1):
    lines = content.strip().split('\n')
    return MdxBlock(type=type_, content=content,
                    line_start=line_start, line_end=line_start + len(lines) - 1)


def test_diff_returns_alignment():
    """diff_blocks가 (changes, alignment) 튜플을 반환한다."""
    mdx = "# Title\n\nParagraph.\n"
    original = parse_mdx_blocks(mdx)
    improved = parse_mdx_blocks(mdx)
    changes, alignment = diff_blocks(original, improved)
    assert changes == []
    # 모든 improved 블록이 original에 매칭
    assert len(alignment) == len(original)


def test_paragraph_added():
    """블록 추가 감지."""
    original_mdx = "# Title\n\nPara one.\n"
    improved_mdx = "# Title\n\nNew para.\n\nPara one.\n"
    original = parse_mdx_blocks(original_mdx)
    improved = parse_mdx_blocks(improved_mdx)
    changes, alignment = diff_blocks(original, improved)

    added = [c for c in changes if c.change_type == 'added']
    assert len(added) == 1
    assert 'New para' in added[0].new_block.content
    assert added[0].old_block is None


def test_paragraph_deleted():
    """블록 삭제 감지."""
    original_mdx = "# Title\n\nPara one.\n\nPara two.\n"
    improved_mdx = "# Title\n\nPara two.\n"
    original = parse_mdx_blocks(original_mdx)
    improved = parse_mdx_blocks(improved_mdx)
    changes, alignment = diff_blocks(original, improved)

    deleted = [c for c in changes if c.change_type == 'deleted']
    assert len(deleted) == 1
    assert 'Para one' in deleted[0].old_block.content
    assert deleted[0].new_block is None


def test_replace_becomes_delete_plus_add():
    """SequenceMatcher의 replace opcode가 delete + add로 분해된다."""
    original_mdx = "# Title\n\nOld content.\n"
    improved_mdx = "# Title\n\nCompletely different.\n"
    original = parse_mdx_blocks(original_mdx)
    improved = parse_mdx_blocks(improved_mdx)
    changes, alignment = diff_blocks(original, improved)

    # 'Old content' → 'Completely different'는 SequenceMatcher에 의해
    # replace(delete+add) 또는 modified로 잡힐 수 있음.
    # 어느 쪽이든 변경이 감지되어야 함.
    assert len(changes) >= 1


def test_mixed_add_delete_modify():
    """추가 + 삭제 + 수정이 동시에 발생."""
    original_mdx = "# Title\n\nPara one.\n\nPara two.\n\nPara three.\n"
    improved_mdx = "# Title\n\nPara ONE.\n\nNew para.\n\nPara three.\n"
    original = parse_mdx_blocks(original_mdx)
    improved = parse_mdx_blocks(improved_mdx)
    changes, alignment = diff_blocks(original, improved)

    types = {c.change_type for c in changes}
    # Para one → Para ONE (modified 또는 delete+add)
    # Para two 삭제
    # New para 추가
    assert len(changes) >= 2


def test_alignment_maps_improved_to_original():
    """alignment이 improved index → original index 매핑을 올바르게 생성한다."""
    original_mdx = "# Title\n\nPara one.\n\nPara two.\n"
    improved_mdx = "# Title\n\nNew.\n\nPara one.\n\nPara two.\n"
    original = parse_mdx_blocks(original_mdx)
    improved = parse_mdx_blocks(improved_mdx)
    changes, alignment = diff_blocks(original, improved)

    # improved[0] = "# Title" → original[0]
    assert alignment[0] == 0
    # improved[1] = empty → original[1]
    # improved[2] = "New." → 추가된 블록, alignment에 없음
    # improved[3] = empty (추가 또는 매칭)
    # improved의 "Para one."은 original의 "Para one."에 매핑


def test_non_content_types_always_match():
    """frontmatter, empty, import_statement는 항상 매칭된다."""
    original_mdx = "---\ntitle: T\n---\n\nimport X from 'y'\n\n# Title\n"
    improved_mdx = "---\ntitle: T\n---\n\nimport X from 'y'\n\nNew para.\n\n# Title\n"
    original = parse_mdx_blocks(original_mdx)
    improved = parse_mdx_blocks(improved_mdx)
    changes, alignment = diff_blocks(original, improved)

    # frontmatter, empty, import_statement는 변경 없이 매칭
    non_content_changes = [c for c in changes
                           if c.old_block and c.old_block.type in ('frontmatter', 'empty', 'import_statement')]
    assert len(non_content_changes) == 0
```

**Step 2: Run tests to verify they fail**

Run: `cd /Users/jk/workspace/querypie-docs-translation-2/confluence-mdx && python3 -m pytest tests/test_reverse_sync_block_diff.py -v`

Expected: FAIL — `diff_blocks` returns single value, not tuple

**Step 3: Write implementation**

`bin/reverse_sync/block_diff.py`의 `diff_blocks()` 전체 재구현:

```python
from difflib import SequenceMatcher
from reverse_sync.text_normalizer import normalize_mdx_to_plain, collapse_ws

NON_CONTENT_TYPES = frozenset(('empty', 'frontmatter', 'import_statement'))


def _block_key(block: MdxBlock) -> str:
    """블록을 비교 가능한 키로 변환한다."""
    if block.type in NON_CONTENT_TYPES:
        return f'__non_content_{block.type}__'
    plain = normalize_mdx_to_plain(block.content, block.type)
    return collapse_ws(plain)


def diff_blocks(
    original: List[MdxBlock], improved: List[MdxBlock],
) -> Tuple[List[BlockChange], Dict[int, int]]:
    """두 블록 시퀀스를 SequenceMatcher로 정렬하여 변경 목록과 alignment를 반환한다.

    Returns:
        changes: BlockChange 목록 (modified, added, deleted)
        alignment: improved_idx → original_idx 매핑 (매칭된 블록만)
    """
    orig_keys = [_block_key(b) for b in original]
    impr_keys = [_block_key(b) for b in improved]

    sm = SequenceMatcher(None, orig_keys, impr_keys)
    changes: List[BlockChange] = []
    alignment: Dict[int, int] = {}

    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            for i, j in zip(range(i1, i2), range(j1, j2)):
                alignment[j] = i
                if original[i].content != improved[j].content:
                    changes.append(BlockChange(
                        index=i, change_type='modified',
                        old_block=original[i], new_block=improved[j],
                    ))
        elif tag == 'replace':
            for i in range(i1, i2):
                changes.append(BlockChange(
                    index=i, change_type='deleted',
                    old_block=original[i], new_block=None,
                ))
            for j in range(j1, j2):
                changes.append(BlockChange(
                    index=j, change_type='added',
                    old_block=None, new_block=improved[j],
                ))
        elif tag == 'insert':
            for j in range(j1, j2):
                changes.append(BlockChange(
                    index=j, change_type='added',
                    old_block=None, new_block=improved[j],
                ))
        elif tag == 'delete':
            for i in range(i1, i2):
                changes.append(BlockChange(
                    index=i, change_type='deleted',
                    old_block=original[i], new_block=None,
                ))

    return changes, alignment
```

**Step 4: Run all tests**

Run: `cd /Users/jk/workspace/querypie-docs-translation-2/confluence-mdx && python3 -m pytest tests/test_reverse_sync_block_diff.py -v`

Expected: ALL PASS

**주의:** 기존 `test_block_count_mismatch_raises`는 Phase 2에서 더 이상 에러를 던지지 않으므로 삭제하거나 수정해야 함. 기존 `test_no_changes`, `test_text_change_in_paragraph`, `test_multiple_changes`도 반환값이 튜플로 변경되므로 수정 필요:

```python
# 기존 테스트 수정: 반환값 언패킹
def test_no_changes():
    mdx = "---\ntitle: 'T'\n---\n\n# Title\n\nParagraph.\n"
    original = parse_mdx_blocks(mdx)
    improved = parse_mdx_blocks(mdx)
    changes, alignment = diff_blocks(original, improved)
    assert changes == []

def test_text_change_in_paragraph():
    # ... 동일, changes = → changes, alignment =
    changes, alignment = diff_blocks(original, improved)
    # ... assertions 동일

def test_multiple_changes():
    # ... 동일, changes = → changes, alignment =
    changes, alignment = diff_blocks(original, improved)
    # ... assertions 동일

# test_block_count_mismatch_raises 삭제
```

**Step 5: Commit**

```bash
git add bin/reverse_sync/block_diff.py tests/test_reverse_sync_block_diff.py
git commit -m "feat(block_diff): SequenceMatcher 기반 블록 정렬 (add/delete 지원)"
```

---

### Task 3: 파이프라인 호출부 업데이트 — `reverse_sync_cli.py` + `patch_builder.py`

**Files:**
- Modify: `bin/reverse_sync_cli.py:183,194-200,236-237`
- Modify: `bin/reverse_sync/patch_builder.py:47-54`

`diff_blocks()` 반환값 변경과 `build_patches()` 시그니처 변경을 반영한다. 이 단계에서는 `build_patches()`의 `alignment` 인자를 받기만 하고, added/deleted 처리는 아직 구현하지 않는다.

**Step 1: Write the failing test**

Run: `cd /Users/jk/workspace/querypie-docs-translation-2/confluence-mdx && python3 -m pytest tests/ -v`

Expected: FAIL — `diff_blocks()` 반환값이 튜플로 바뀌었으므로 `reverse_sync_cli.py`의 `changes = diff_blocks(...)` 에서 에러

**Step 2: Fix `reverse_sync_cli.py`**

`bin/reverse_sync_cli.py` L183:
```python
# Before
changes = diff_blocks(original_blocks, improved_blocks)

# After
changes, alignment = diff_blocks(original_blocks, improved_blocks)
```

L194-200 (diff.yaml 직렬화):
```python
'changes': [
    {'index': c.index,
     'block_id': f'{(c.old_block or c.new_block).type}-{c.index}',
     'change_type': c.change_type,
     'old_content': c.old_block.content if c.old_block else None,
     'new_content': c.new_block.content if c.new_block else None}
    for c in changes
],
```

L236-237 (build_patches 호출):
```python
patches = build_patches(changes, original_blocks, improved_blocks,
                        original_mappings, mdx_to_sidecar, xpath_to_mapping,
                        alignment)
```

**Step 3: Fix `patch_builder.py` signature**

`bin/reverse_sync/patch_builder.py` L47-54:
```python
def build_patches(
    changes: List[BlockChange],
    original_blocks: List[MdxBlock],
    improved_blocks: List[MdxBlock],
    mappings: List[BlockMapping],
    mdx_to_sidecar: Dict[int, SidecarEntry],
    xpath_to_mapping: Dict[str, 'BlockMapping'],
    alignment: Optional[Dict[int, int]] = None,
) -> List[Dict[str, str]]:
```

기존 `for change in changes:` 루프 상단에 added/deleted 필터 추가:
```python
    for change in changes:
        # Phase 2: added/deleted는 별도 처리 (Task 5에서 구현)
        if change.change_type in ('added', 'deleted'):
            continue

        if change.old_block.type in NON_CONTENT_TYPES:
            continue
        # ... 기존 modified 로직 ...
```

**Step 4: Run all tests**

Run: `cd /Users/jk/workspace/querypie-docs-translation-2/confluence-mdx && python3 -m pytest tests/ -v`

Expected: ALL PASS (기존 310개 + Task 1-2에서 추가한 테스트)

**Step 5: Commit**

```bash
git add bin/reverse_sync_cli.py bin/reverse_sync/patch_builder.py
git commit -m "refactor: update pipeline callers for new diff_blocks return value"
```

---

### Task 4: `mdx_to_xhtml_inline.py` — `mdx_block_to_xhtml_element()` 추가

**Files:**
- Modify: `bin/reverse_sync/mdx_to_xhtml_inline.py`
- Test: `tests/test_reverse_sync_mdx_to_xhtml_inline.py`

**Step 1: Write the failing tests**

`tests/test_reverse_sync_mdx_to_xhtml_inline.py`에 추가:

```python
from reverse_sync.mdx_to_xhtml_inline import mdx_block_to_xhtml_element
from reverse_sync.mdx_block_parser import MdxBlock


class TestMdxBlockToXhtmlElement:
    def test_heading_h2(self):
        block = MdxBlock(type='heading', content='## Section Title\n',
                         line_start=1, line_end=1)
        result = mdx_block_to_xhtml_element(block)
        assert result == '<h2>Section Title</h2>'

    def test_heading_h3_with_code(self):
        block = MdxBlock(type='heading', content='### `config` 설정\n',
                         line_start=1, line_end=1)
        result = mdx_block_to_xhtml_element(block)
        assert result == '<h3><code>config</code> 설정</h3>'

    def test_paragraph(self):
        block = MdxBlock(type='paragraph', content='Hello **world**\n',
                         line_start=1, line_end=1)
        result = mdx_block_to_xhtml_element(block)
        assert result == '<p>Hello <strong>world</strong></p>'

    def test_unordered_list(self):
        block = MdxBlock(type='list', content='- item1\n- item2\n',
                         line_start=1, line_end=2)
        result = mdx_block_to_xhtml_element(block)
        assert '<ul>' in result
        assert '<li><p>item1</p></li>' in result
        assert '</ul>' in result

    def test_ordered_list(self):
        block = MdxBlock(type='list', content='1. first\n2. second\n',
                         line_start=1, line_end=2)
        result = mdx_block_to_xhtml_element(block)
        assert '<ol>' in result
        assert '</ol>' in result

    def test_code_block(self):
        block = MdxBlock(type='code_block',
                         content='```python\nprint("hi")\n```\n',
                         line_start=1, line_end=3)
        result = mdx_block_to_xhtml_element(block)
        assert 'ac:structured-macro' in result
        assert 'ac:name="code"' in result
        assert 'python' in result
        assert 'print("hi")' in result

    def test_code_block_no_language(self):
        block = MdxBlock(type='code_block',
                         content='```\nsome code\n```\n',
                         line_start=1, line_end=3)
        result = mdx_block_to_xhtml_element(block)
        assert 'ac:structured-macro' in result
        # language 파라미터가 없거나 빈 값

    def test_html_block_passthrough(self):
        block = MdxBlock(type='html_block',
                         content='<div>custom html</div>\n',
                         line_start=1, line_end=1)
        result = mdx_block_to_xhtml_element(block)
        assert '<div>custom html</div>' in result
```

**Step 2: Run tests to verify they fail**

Run: `cd /Users/jk/workspace/querypie-docs-translation-2/confluence-mdx && python3 -m pytest tests/test_reverse_sync_mdx_to_xhtml_inline.py::TestMdxBlockToXhtmlElement -v`

Expected: FAIL — `cannot import name 'mdx_block_to_xhtml_element'`

**Step 3: Write implementation**

`bin/reverse_sync/mdx_to_xhtml_inline.py` 끝에 추가:

```python
def mdx_block_to_xhtml_element(block) -> str:
    """MDX 블록을 완전한 Confluence XHTML 요소(outer tag 포함)로 변환한다.

    Args:
        block: MdxBlock 인스턴스 (type, content 필드 사용)

    Returns:
        완전한 XHTML 요소 문자열
    """
    inner = mdx_block_to_inner_xhtml(block.content, block.type)

    if block.type == 'heading':
        level = _detect_heading_level(block.content)
        return f'<h{level}>{inner}</h{level}>'

    elif block.type == 'paragraph':
        return f'<p>{inner}</p>'

    elif block.type == 'list':
        tag = _detect_list_tag(block.content)
        return f'<{tag}>{inner}</{tag}>'

    elif block.type == 'code_block':
        lang = _extract_code_language(block.content)
        code = inner  # _convert_code_block already extracts content
        parts = ['<ac:structured-macro ac:name="code">']
        if lang:
            parts.append(
                f'<ac:parameter ac:name="language">{lang}</ac:parameter>')
        parts.append(
            f'<ac:plain-text-body><![CDATA[{code}]]></ac:plain-text-body>')
        parts.append('</ac:structured-macro>')
        return ''.join(parts)

    elif block.type == 'html_block':
        return block.content.strip()

    else:
        return f'<p>{inner}</p>'


def _detect_heading_level(content: str) -> int:
    """heading content에서 레벨(1-6)을 추출한다."""
    stripped = content.strip()
    level = 0
    for ch in stripped:
        if ch == '#':
            level += 1
        else:
            break
    return max(1, min(level, 6))


def _detect_list_tag(content: str) -> str:
    """list content의 첫 번째 마커로 ul/ol을 결정한다."""
    for line in content.strip().split('\n'):
        stripped = line.strip()
        if not stripped:
            continue
        if re.match(r'^\d+\.\s', stripped):
            return 'ol'
        if re.match(r'^[-*+]\s', stripped):
            return 'ul'
    return 'ul'


def _extract_code_language(content: str) -> str:
    """code fence 첫 줄에서 언어를 추출한다."""
    first_line = content.strip().split('\n')[0].strip()
    if first_line.startswith('```'):
        lang = first_line[3:].strip()
        return lang
    return ''
```

**Step 4: Run all tests**

Run: `cd /Users/jk/workspace/querypie-docs-translation-2/confluence-mdx && python3 -m pytest tests/test_reverse_sync_mdx_to_xhtml_inline.py -v`

Expected: ALL PASS

**Step 5: Commit**

```bash
git add bin/reverse_sync/mdx_to_xhtml_inline.py tests/test_reverse_sync_mdx_to_xhtml_inline.py
git commit -m "feat(mdx_to_xhtml): add mdx_block_to_xhtml_element() for full XHTML generation"
```

---

### Task 5: `xhtml_patcher.py` — delete/insert 패치 지원

**Files:**
- Modify: `bin/reverse_sync/xhtml_patcher.py:8-49`
- Test: `tests/test_reverse_sync_xhtml_patcher.py`

**Step 1: Write the failing tests**

`tests/test_reverse_sync_xhtml_patcher.py`에 추가:

```python
class TestDeletePatch:
    def test_delete_paragraph(self):
        xhtml = '<h1>Title</h1><p>Para one</p><p>Para two</p>'
        patches = [{'action': 'delete', 'xhtml_xpath': 'p[1]'}]
        result = patch_xhtml(xhtml, patches)
        assert '<p>Para one</p>' not in result
        assert '<p>Para two</p>' in result
        assert '<h1>Title</h1>' in result

    def test_delete_heading(self):
        xhtml = '<h1>Title</h1><h2>Sub</h2><p>Text</p>'
        patches = [{'action': 'delete', 'xhtml_xpath': 'h2[1]'}]
        result = patch_xhtml(xhtml, patches)
        assert '<h2>Sub</h2>' not in result
        assert '<h1>Title</h1>' in result

    def test_delete_multiple_preserves_order(self):
        """뒤에서 앞으로 삭제해도 올바르게 동작."""
        xhtml = '<p>A</p><p>B</p><p>C</p>'
        patches = [
            {'action': 'delete', 'xhtml_xpath': 'p[1]'},
            {'action': 'delete', 'xhtml_xpath': 'p[3]'},
        ]
        result = patch_xhtml(xhtml, patches)
        assert '<p>A</p>' not in result
        assert '<p>B</p>' in result
        assert '<p>C</p>' not in result

    def test_delete_nonexistent_xpath_skipped(self):
        xhtml = '<p>Only</p>'
        patches = [{'action': 'delete', 'xhtml_xpath': 'p[99]'}]
        result = patch_xhtml(xhtml, patches)
        assert '<p>Only</p>' in result


class TestInsertPatch:
    def test_insert_after_element(self):
        xhtml = '<h1>Title</h1><p>Existing</p>'
        patches = [{'action': 'insert', 'after_xpath': 'h1[1]',
                     'new_element_xhtml': '<p>New para</p>'}]
        result = patch_xhtml(xhtml, patches)
        assert '<p>New para</p>' in result
        # New para는 h1과 existing p 사이에 위치
        h1_pos = result.index('<h1>')
        new_pos = result.index('New para')
        exist_pos = result.index('Existing')
        assert h1_pos < new_pos < exist_pos

    def test_insert_at_beginning(self):
        """after_xpath=None이면 첫 블록 앞에 삽입."""
        xhtml = '<h1>Title</h1><p>Text</p>'
        patches = [{'action': 'insert', 'after_xpath': None,
                     'new_element_xhtml': '<p>First</p>'}]
        result = patch_xhtml(xhtml, patches)
        assert '<p>First</p>' in result
        first_pos = result.index('First')
        title_pos = result.index('Title')
        assert first_pos < title_pos

    def test_insert_at_end(self):
        xhtml = '<h1>Title</h1><p>Last</p>'
        patches = [{'action': 'insert', 'after_xpath': 'p[1]',
                     'new_element_xhtml': '<p>After last</p>'}]
        result = patch_xhtml(xhtml, patches)
        assert '<p>After last</p>' in result
        last_pos = result.index('Last')
        after_pos = result.index('After last')
        assert last_pos < after_pos

    def test_insert_nonexistent_anchor_skipped(self):
        xhtml = '<p>Only</p>'
        patches = [{'action': 'insert', 'after_xpath': 'h1[99]',
                     'new_element_xhtml': '<p>Ghost</p>'}]
        result = patch_xhtml(xhtml, patches)
        assert 'Ghost' not in result


class TestPatchOrdering:
    def test_delete_before_insert_before_modify(self):
        """delete → insert → modify 순서로 적용."""
        xhtml = '<p>Delete me</p><p>Modify me</p><p>Keep</p>'
        patches = [
            {'action': 'delete', 'xhtml_xpath': 'p[1]'},
            {'action': 'insert', 'after_xpath': 'p[2]',
             'new_element_xhtml': '<p>Inserted</p>'},
            {'action': 'modify', 'xhtml_xpath': 'p[2]',
             'old_plain_text': 'Modify me', 'new_plain_text': 'Modified'},
        ]
        result = patch_xhtml(xhtml, patches)
        assert 'Delete me' not in result
        assert 'Inserted' in result
        assert 'Modified' in result

    def test_legacy_patch_without_action_treated_as_modify(self):
        """action 키 없는 패치는 modify로 처리 (하위 호환)."""
        xhtml = '<p>Old text</p>'
        patches = [{'xhtml_xpath': 'p[1]',
                     'old_plain_text': 'Old text',
                     'new_plain_text': 'New text'}]
        result = patch_xhtml(xhtml, patches)
        assert 'New text' in result
```

**Step 2: Run tests to verify they fail**

Run: `cd /Users/jk/workspace/querypie-docs-translation-2/confluence-mdx && python3 -m pytest tests/test_reverse_sync_xhtml_patcher.py::TestDeletePatch tests/test_reverse_sync_xhtml_patcher.py::TestInsertPatch tests/test_reverse_sync_xhtml_patcher.py::TestPatchOrdering -v`

Expected: FAIL — delete/insert action 처리 로직 없음

**Step 3: Write implementation**

`bin/reverse_sync/xhtml_patcher.py`의 `patch_xhtml()` 전체 교체:

```python
def patch_xhtml(xhtml: str, patches: List[Dict[str, str]]) -> str:
    """XHTML에 패치를 적용한다.

    Args:
        xhtml: 원본 XHTML 문자열
        patches: 패치 목록. 각 패치는 dict:
            - action: "modify" (기본) | "delete" | "insert"
            - modify: xhtml_xpath, old_plain_text, new_plain_text 또는 new_inner_xhtml
            - delete: xhtml_xpath
            - insert: after_xpath (None이면 맨 앞), new_element_xhtml

    Returns:
        패치된 XHTML 문자열
    """
    soup = BeautifulSoup(xhtml, 'html.parser')

    # 패치를 action별로 분류
    delete_patches = [p for p in patches if p.get('action') == 'delete']
    insert_patches = [p for p in patches if p.get('action') == 'insert']
    modify_patches = [p for p in patches
                      if p.get('action', 'modify') == 'modify']

    # 1단계: delete (뒤에서 앞으로 — xpath 인덱스 보존)
    delete_patches.sort(
        key=lambda p: _xpath_index(p['xhtml_xpath']), reverse=True)
    for patch in delete_patches:
        element = _find_element_by_xpath(soup, patch['xhtml_xpath'])
        if element is not None:
            element.decompose()

    # 2단계: insert (앞에서 뒤로)
    for patch in insert_patches:
        _insert_element(soup, patch)

    # 3단계: modify (기존 로직)
    for patch in modify_patches:
        xpath = patch['xhtml_xpath']
        element = _find_element_by_xpath(soup, xpath)
        if element is None:
            continue

        if 'new_inner_xhtml' in patch:
            old_text = patch.get('old_plain_text', '')
            current_plain = element.get_text()
            if old_text and current_plain.strip() != old_text.strip():
                continue
            _replace_inner_html(element, patch['new_inner_xhtml'])
        else:
            old_text = patch['old_plain_text']
            new_text = patch['new_plain_text']
            current_plain = element.get_text()
            if current_plain.strip() != old_text.strip():
                continue
            _apply_text_changes(element, old_text, new_text)

    result = str(soup)
    result = _restore_cdata(result)
    return result


def _xpath_index(xpath: str) -> int:
    """xpath에서 인덱스 부분을 추출한다 (정렬용)."""
    match = re.search(r'\[(\d+)\]', xpath)
    return int(match.group(1)) if match else 0


def _insert_element(soup: BeautifulSoup, patch: Dict):
    """패치에 따라 새 요소를 삽입한다."""
    after_xpath = patch.get('after_xpath')
    new_html = patch['new_element_xhtml']
    new_parsed = BeautifulSoup(new_html, 'html.parser')

    if after_xpath is None:
        # 첫 번째 블록 요소 앞에 삽입
        first_block = _find_first_block_element(soup)
        if first_block:
            for child in reversed(list(new_parsed.children)):
                first_block.insert_before(child.extract())
        else:
            for child in list(new_parsed.children):
                soup.append(child.extract())
    else:
        anchor = _find_element_by_xpath(soup, after_xpath)
        if anchor is not None:
            # insert_after는 마지막 요소부터 역순으로 삽입해야 순서 유지
            children = list(new_parsed.children)
            for child in reversed(children):
                anchor.insert_after(child.extract())


def _find_first_block_element(soup: BeautifulSoup):
    """soup의 첫 번째 블록 레벨 요소를 찾는다."""
    for child in _iter_block_children(soup):
        if isinstance(child, Tag):
            return child
    return None
```

**Step 4: Run all tests**

Run: `cd /Users/jk/workspace/querypie-docs-translation-2/confluence-mdx && python3 -m pytest tests/test_reverse_sync_xhtml_patcher.py -v`

Expected: ALL PASS

Run: `cd /Users/jk/workspace/querypie-docs-translation-2/confluence-mdx && python3 -m pytest tests/ -v`

Expected: ALL PASS (전체 회귀 확인)

**Step 5: Commit**

```bash
git add bin/reverse_sync/xhtml_patcher.py tests/test_reverse_sync_xhtml_patcher.py
git commit -m "feat(xhtml_patcher): add delete/insert patch support with ordering"
```

---

### Task 6: `patch_builder.py` — `_build_delete_patch()` + `_build_insert_patch()` 구현

**Files:**
- Modify: `bin/reverse_sync/patch_builder.py`
- Test: `tests/test_reverse_sync_patch_builder.py`

**Step 1: Write the failing tests**

`tests/test_reverse_sync_patch_builder.py`에 추가:

```python
from reverse_sync.mdx_to_xhtml_inline import mdx_block_to_xhtml_element


class TestBuildDeletePatch:
    def test_delete_patch_from_sidecar(self):
        """deleted 변경이 sidecar에서 xpath를 찾아 delete 패치를 생성한다."""
        mapping = _make_mapping('m1', 'Delete this text', xpath='p[1]')
        sidecar = _make_sidecar('p[1]', [2])
        mdx_to_sidecar = {2: sidecar}
        xpath_to_mapping = {'p[1]': mapping}

        change = BlockChange(
            index=2, change_type='deleted',
            old_block=_make_block('Delete this text'),
            new_block=None,
        )
        patches = build_patches(
            [change], [], [], [mapping],
            mdx_to_sidecar, xpath_to_mapping, {})
        assert len(patches) == 1
        assert patches[0]['action'] == 'delete'
        assert patches[0]['xhtml_xpath'] == 'p[1]'

    def test_delete_non_content_skipped(self):
        """deleted된 empty/frontmatter 블록은 무시."""
        change = BlockChange(
            index=0, change_type='deleted',
            old_block=_make_block('', type_='empty'),
            new_block=None,
        )
        patches = build_patches([change], [], [], [], {}, {}, {})
        assert len(patches) == 0

    def test_delete_no_sidecar_skipped(self):
        """sidecar에 매핑되지 않은 삭제 블록은 무시."""
        change = BlockChange(
            index=5, change_type='deleted',
            old_block=_make_block('Unmapped text'),
            new_block=None,
        )
        patches = build_patches([change], [], [], [], {}, {}, {})
        assert len(patches) == 0


class TestBuildInsertPatch:
    def test_insert_patch_with_anchor(self):
        """added 변경이 선행 매칭 블록을 앵커로 insert 패치를 생성한다."""
        mapping = _make_mapping('m1', 'Anchor text', xpath='p[1]')
        sidecar = _make_sidecar('p[1]', [0])
        mdx_to_sidecar = {0: sidecar}
        xpath_to_mapping = {'p[1]': mapping}

        # improved: [anchor(idx=0, matched), new(idx=1, added)]
        alignment = {0: 0}  # improved[0] → original[0]
        change = BlockChange(
            index=1, change_type='added',
            old_block=None,
            new_block=_make_block('New paragraph text'),
        )
        improved_blocks = [
            _make_block('Anchor text'),
            _make_block('New paragraph text'),
        ]
        patches = build_patches(
            [change], [_make_block('Anchor text')], improved_blocks,
            [mapping], mdx_to_sidecar, xpath_to_mapping, alignment)

        insert_patches = [p for p in patches if p.get('action') == 'insert']
        assert len(insert_patches) == 1
        assert insert_patches[0]['after_xpath'] == 'p[1]'
        assert '<p>' in insert_patches[0]['new_element_xhtml']

    def test_insert_at_beginning(self):
        """선행 매칭 블록이 없으면 after_xpath=None."""
        alignment = {}  # 매칭 없음
        change = BlockChange(
            index=0, change_type='added',
            old_block=None,
            new_block=_make_block('Very first paragraph'),
        )
        patches = build_patches(
            [change], [], [_make_block('Very first paragraph')],
            [], {}, {}, alignment)

        insert_patches = [p for p in patches if p.get('action') == 'insert']
        assert len(insert_patches) == 1
        assert insert_patches[0]['after_xpath'] is None

    def test_insert_non_content_skipped(self):
        """added된 empty 블록은 무시."""
        change = BlockChange(
            index=0, change_type='added',
            old_block=None,
            new_block=_make_block('\n', type_='empty'),
        )
        patches = build_patches([change], [], [], [], {}, {}, {})
        assert len(patches) == 0
```

**Step 2: Run tests to verify they fail**

Run: `cd /Users/jk/workspace/querypie-docs-translation-2/confluence-mdx && python3 -m pytest tests/test_reverse_sync_patch_builder.py::TestBuildDeletePatch tests/test_reverse_sync_patch_builder.py::TestBuildInsertPatch -v`

Expected: FAIL — added/deleted는 `continue`로 건너뛰므로 빈 패치 반환

**Step 3: Write implementation**

`bin/reverse_sync/patch_builder.py` 수정:

import 추가:
```python
from reverse_sync.mdx_to_xhtml_inline import mdx_block_to_xhtml_element
```

`build_patches()` 내부, 기존 `for change in changes:` 루프의 added/deleted skip을 실제 구현으로 교체:

```python
    for change in changes:
        if change.change_type == 'deleted':
            patch = _build_delete_patch(
                change, mdx_to_sidecar, xpath_to_mapping)
            if patch:
                patches.append(patch)
            continue

        if change.change_type == 'added':
            patch = _build_insert_patch(
                change, improved_blocks, alignment,
                mdx_to_sidecar, xpath_to_mapping)
            if patch:
                patches.append(patch)
            continue

        if change.old_block.type in NON_CONTENT_TYPES:
            continue
        # ... 기존 modified 로직 유지 ...
```

새 함수 추가:

```python
def _build_delete_patch(
    change: BlockChange,
    mdx_to_sidecar: Dict[int, SidecarEntry],
    xpath_to_mapping: Dict[str, 'BlockMapping'],
) -> Optional[Dict[str, str]]:
    """삭제된 블록에 대한 delete 패치를 생성한다."""
    if change.old_block.type in NON_CONTENT_TYPES:
        return None
    mapping = find_mapping_by_sidecar(
        change.index, mdx_to_sidecar, xpath_to_mapping)
    if mapping is None:
        return None
    return {'action': 'delete', 'xhtml_xpath': mapping.xhtml_xpath}


def _build_insert_patch(
    change: BlockChange,
    improved_blocks: List[MdxBlock],
    alignment: Optional[Dict[int, int]],
    mdx_to_sidecar: Dict[int, SidecarEntry],
    xpath_to_mapping: Dict[str, 'BlockMapping'],
) -> Optional[Dict[str, str]]:
    """추가된 블록에 대한 insert 패치를 생성한다."""
    new_block = change.new_block
    if new_block.type in NON_CONTENT_TYPES:
        return None

    after_xpath = _find_insert_anchor(
        change.index, alignment, mdx_to_sidecar, xpath_to_mapping)
    new_xhtml = mdx_block_to_xhtml_element(new_block)

    return {
        'action': 'insert',
        'after_xpath': after_xpath,
        'new_element_xhtml': new_xhtml,
    }


def _find_insert_anchor(
    improved_idx: int,
    alignment: Optional[Dict[int, int]],
    mdx_to_sidecar: Dict[int, SidecarEntry],
    xpath_to_mapping: Dict[str, 'BlockMapping'],
) -> Optional[str]:
    """추가 블록의 삽입 위치 앵커를 찾는다.

    improved 시퀀스에서 역순으로 탐색하여 alignment에 존재하는
    (= original에 매칭되는) 첫 번째 블록의 xhtml_xpath를 반환한다.
    """
    if alignment is None:
        return None

    for j in range(improved_idx - 1, -1, -1):
        if j in alignment:
            orig_idx = alignment[j]
            mapping = find_mapping_by_sidecar(
                orig_idx, mdx_to_sidecar, xpath_to_mapping)
            if mapping is not None:
                return mapping.xhtml_xpath
    return None
```

**Step 4: Run all tests**

Run: `cd /Users/jk/workspace/querypie-docs-translation-2/confluence-mdx && python3 -m pytest tests/test_reverse_sync_patch_builder.py -v`

Expected: ALL PASS

Run: `cd /Users/jk/workspace/querypie-docs-translation-2/confluence-mdx && python3 -m pytest tests/ -v`

Expected: ALL PASS (전체 회귀)

**Step 5: Commit**

```bash
git add bin/reverse_sync/patch_builder.py tests/test_reverse_sync_patch_builder.py
git commit -m "feat(patch_builder): implement delete/insert patch generation"
```

---

### Task 7: E2E 통합 테스트

**Files:**
- Create: `tests/test_reverse_sync_structural.py`

이 테스트는 전체 파이프라인(MDX diff → patch build → XHTML patch)을 통합 검증한다.

**Step 1: Write E2E tests**

```python
"""구조적 변경 (블록 추가/삭제) E2E 테스트."""
from reverse_sync.mdx_block_parser import parse_mdx_blocks
from reverse_sync.block_diff import diff_blocks
from reverse_sync.mapping_recorder import record_mapping
from reverse_sync.patch_builder import build_patches
from reverse_sync.xhtml_patcher import patch_xhtml
from reverse_sync.sidecar_lookup import (
    SidecarEntry, build_mdx_to_sidecar_index, build_xpath_to_mapping,
)


def _run_pipeline(original_mdx, improved_mdx, xhtml, sidecar_entries):
    """테스트용 간이 파이프라인."""
    original_blocks = parse_mdx_blocks(original_mdx)
    improved_blocks = parse_mdx_blocks(improved_mdx)
    changes, alignment = diff_blocks(original_blocks, improved_blocks)

    mappings = record_mapping(xhtml)
    mdx_to_sidecar = build_mdx_to_sidecar_index(sidecar_entries)
    xpath_to_mapping = build_xpath_to_mapping(mappings)

    patches = build_patches(
        changes, original_blocks, improved_blocks,
        mappings, mdx_to_sidecar, xpath_to_mapping, alignment)
    return patch_xhtml(xhtml, patches)


class TestStructuralParagraphAdd:
    def test_paragraph_added_between_existing(self):
        xhtml = '<h1>Title</h1><p>Para one</p>'
        original_mdx = '# Title\n\nPara one\n'
        improved_mdx = '# Title\n\nNew para\n\nPara one\n'
        sidecar = [
            SidecarEntry(xhtml_xpath='h1[1]', xhtml_type='heading',
                         mdx_blocks=[0]),
            SidecarEntry(xhtml_xpath='p[1]', xhtml_type='paragraph',
                         mdx_blocks=[2]),
        ]
        result = _run_pipeline(original_mdx, improved_mdx, xhtml, sidecar)
        assert '<p>New para</p>' in result or 'New para' in result
        assert '<h1>Title</h1>' in result
        assert 'Para one' in result


class TestStructuralParagraphDelete:
    def test_paragraph_deleted(self):
        xhtml = '<h1>Title</h1><p>Para one</p><p>Para two</p>'
        original_mdx = '# Title\n\nPara one\n\nPara two\n'
        improved_mdx = '# Title\n\nPara two\n'
        sidecar = [
            SidecarEntry(xhtml_xpath='h1[1]', xhtml_type='heading',
                         mdx_blocks=[0]),
            SidecarEntry(xhtml_xpath='p[1]', xhtml_type='paragraph',
                         mdx_blocks=[2]),
            SidecarEntry(xhtml_xpath='p[2]', xhtml_type='paragraph',
                         mdx_blocks=[4]),
        ]
        result = _run_pipeline(original_mdx, improved_mdx, xhtml, sidecar)
        assert 'Para one' not in result
        assert 'Para two' in result


class TestStructuralCodeBlockAdd:
    def test_code_block_added(self):
        xhtml = '<h1>Title</h1><p>Description</p>'
        original_mdx = '# Title\n\nDescription\n'
        improved_mdx = '# Title\n\nDescription\n\n```python\nprint("hi")\n```\n'
        sidecar = [
            SidecarEntry(xhtml_xpath='h1[1]', xhtml_type='heading',
                         mdx_blocks=[0]),
            SidecarEntry(xhtml_xpath='p[1]', xhtml_type='paragraph',
                         mdx_blocks=[2]),
        ]
        result = _run_pipeline(original_mdx, improved_mdx, xhtml, sidecar)
        assert 'ac:structured-macro' in result or 'print' in result


class TestStructuralMixedChanges:
    def test_add_delete_modify_combined(self):
        xhtml = '<h1>Title</h1><p>Keep this</p><p>Delete this</p><p>Modify this</p>'
        original_mdx = '# Title\n\nKeep this\n\nDelete this\n\nModify this\n'
        improved_mdx = '# Title\n\nKeep this\n\nNew para\n\nModify THIS\n'
        sidecar = [
            SidecarEntry(xhtml_xpath='h1[1]', xhtml_type='heading',
                         mdx_blocks=[0]),
            SidecarEntry(xhtml_xpath='p[1]', xhtml_type='paragraph',
                         mdx_blocks=[2]),
            SidecarEntry(xhtml_xpath='p[2]', xhtml_type='paragraph',
                         mdx_blocks=[4]),
            SidecarEntry(xhtml_xpath='p[3]', xhtml_type='paragraph',
                         mdx_blocks=[6]),
        ]
        result = _run_pipeline(original_mdx, improved_mdx, xhtml, sidecar)
        assert 'Keep this' in result
        assert 'Delete this' not in result
        assert 'New para' in result
```

**Step 2: Run E2E tests**

Run: `cd /Users/jk/workspace/querypie-docs-translation-2/confluence-mdx && python3 -m pytest tests/test_reverse_sync_structural.py -v`

Expected: ALL PASS

**Step 3: Run full test suite**

Run: `cd /Users/jk/workspace/querypie-docs-translation-2/confluence-mdx && python3 -m pytest tests/ -v`

Expected: ALL PASS (기존 + 신규 모두)

**Step 4: Commit**

```bash
git add tests/test_reverse_sync_structural.py
git commit -m "test: add structural change E2E tests (add/delete/mixed)"
```

---

### Task 8: 전체 회귀 테스트 + PR 생성

**Step 1: Full regression**

Run: `cd /Users/jk/workspace/querypie-docs-translation-2/confluence-mdx && python3 -m pytest tests/ -v --tb=short`

Expected: ALL PASS

**Step 2: Create PR**

```bash
gh pr create --title "feat(reverse-sync): Phase 2 — 블록 추가/삭제 구조적 변경 지원" --body "$(cat <<'EOF'
## Summary
- `block_diff.py`: SequenceMatcher 기반 블록 시퀀스 정렬 (added/deleted/modified 감지)
- `patch_builder.py`: delete/insert 패치 생성 + 삽입 앵커 탐색
- `xhtml_patcher.py`: DOM 요소 삭제/삽입 + 적용 순서 (delete→insert→modify)
- `mdx_to_xhtml_inline.py`: 완전한 XHTML 요소 생성 (heading/paragraph/list/code)
- `reverse_sync_cli.py`: 파이프라인 통합

## Test plan
- [ ] 기존 테스트 전체 회귀 통과
- [ ] block_diff 단위 테스트 (equal/insert/delete/replace/alignment)
- [ ] xhtml_patcher delete/insert 단위 테스트
- [ ] mdx_block_to_xhtml_element 블록 타입별 테스트
- [ ] patch_builder delete/insert 패치 생성 테스트
- [ ] E2E 구조 변경 시나리오 (추가/삭제/복합)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

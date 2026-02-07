# Reverse Sync Phase 1 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** MDX 텍스트 변경사항을 원본 Confluence XHTML에 역반영하는 로컬 검증 파이프라인을 구축한다.

**Architecture:** 기존 forward converter(`confluence_xhtml_to_markdown.py`)를 래핑하여 블록 매핑을 생성하고, 원본/개선 MDX의 블록 단위 diff를 추출하여 XHTML을 패치한 뒤, forward converter로 round-trip 검증(문자 단위 완전 일치)을 수행한다. 로컬 검증과 Confluence 반영은 완전히 분리된 명령으로 실행한다.

**Tech Stack:** Python 3.12, BeautifulSoup4, PyYAML, pytest

**Target Repo:** `/Users/jk/workspace/querypie-docs/confluence-mdx/`

**Design Doc:** `/Users/jk/workspace/skills-jk-1/projects/active/querypie-docs-reverse-sync.md`

---

## Task 1: MDX Block Parser

MDX 파일을 블록 시퀀스로 파싱하는 모듈. 모든 후속 작업의 기반.

**Files:**
- Create: `confluence-mdx/bin/mdx_block_parser.py`
- Test: `confluence-mdx/tests/test_mdx_block_parser.py`

**블록 유형 정의:**
- `frontmatter`: `---` 사이의 YAML
- `import_statement`: `import` 로 시작하는 줄
- `heading`: `#` 으로 시작하는 줄
- `paragraph`: 일반 텍스트 줄 (연속된 비어있지 않은 줄)
- `code_block`: ` ``` ` 으로 시작/끝나는 블록
- `list`: `* `, `- `, `1. ` 등으로 시작하는 연속된 줄 (들여쓰기 포함)
- `html_block`: HTML 태그로 시작하는 여러 줄 블록 (`<table>`, `<details>` 등)
- `empty`: 빈 줄

### Step 1: Write failing test — 기본 블록 파싱

```python
# tests/test_mdx_block_parser.py
import pytest
from mdx_block_parser import MdxBlock, parse_mdx_blocks


def test_parse_simple_document():
    mdx = """---
title: 'Test'
---

# Test Title

First paragraph.

## Section

Second paragraph.
"""
    blocks = parse_mdx_blocks(mdx)

    assert blocks[0].type == "frontmatter"
    assert blocks[0].line_start == 1
    assert blocks[0].line_end == 3

    # empty line after frontmatter
    assert blocks[1].type == "empty"

    assert blocks[2].type == "heading"
    assert blocks[2].content == "# Test Title\n"

    assert blocks[3].type == "empty"

    assert blocks[4].type == "paragraph"
    assert blocks[4].content == "First paragraph.\n"

    assert blocks[5].type == "empty"

    assert blocks[6].type == "heading"
    assert blocks[6].content == "## Section\n"

    assert blocks[7].type == "empty"

    assert blocks[8].type == "paragraph"
    assert blocks[8].content == "Second paragraph.\n"
```

### Step 2: Run test to verify it fails

```bash
cd /Users/jk/workspace/querypie-docs/confluence-mdx
python -m pytest tests/test_mdx_block_parser.py::test_parse_simple_document -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'mdx_block_parser'`

### Step 3: Write minimal implementation

```python
# bin/mdx_block_parser.py
"""MDX Block Parser — MDX 파일을 블록 시퀀스로 파싱한다."""
from dataclasses import dataclass
from typing import List


@dataclass
class MdxBlock:
    type: str           # frontmatter | import_statement | heading | paragraph |
                        # code_block | list | html_block | empty
    content: str        # 원본 텍스트 (줄바꿈 포함)
    line_start: int     # 1-indexed
    line_end: int       # 1-indexed, inclusive


def parse_mdx_blocks(text: str) -> List[MdxBlock]:
    """MDX 텍스트를 블록 시퀀스로 파싱한다."""
    lines = text.split('\n')
    # 마지막 줄이 빈 문자열이면 (텍스트가 \n으로 끝나면) 제거하지 않음 —
    # 대신 파싱 로직에서 처리
    blocks: List[MdxBlock] = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]

        # Frontmatter
        if line == '---' and i == 0:
            start = i
            i += 1
            while i < n and lines[i] != '---':
                i += 1
            i += 1  # closing ---
            content = '\n'.join(lines[start:i]) + '\n'
            blocks.append(MdxBlock('frontmatter', content, start + 1, i))
            continue

        # Empty line
        if line == '':
            blocks.append(MdxBlock('empty', '\n', i + 1, i + 1))
            i += 1
            continue

        # Code block
        if line.startswith('```'):
            start = i
            i += 1
            while i < n and not lines[i].startswith('```'):
                i += 1
            i += 1  # closing ```
            content = '\n'.join(lines[start:i]) + '\n'
            blocks.append(MdxBlock('code_block', content, start + 1, i))
            continue

        # Heading
        if line.startswith('#'):
            blocks.append(MdxBlock('heading', line + '\n', i + 1, i + 1))
            i += 1
            continue

        # Import statement
        if line.startswith('import '):
            blocks.append(MdxBlock('import_statement', line + '\n', i + 1, i + 1))
            i += 1
            continue

        # HTML block
        if line.startswith('<') and not line.startswith('<Badge') and not line.startswith('<Callout'):
            start = i
            # HTML 블록은 들여쓰기 없는 빈 줄 또는 파일 끝까지
            i += 1
            while i < n and lines[i] != '':
                i += 1
            content = '\n'.join(lines[start:i]) + '\n'
            blocks.append(MdxBlock('html_block', content, start + 1, i))
            continue

        # List
        if _is_list_line(line):
            start = i
            i += 1
            while i < n and (lines[i] == '' or _is_list_continuation(lines[i])):
                # 빈 줄 다음에 리스트가 아니면 종료
                if lines[i] == '':
                    if i + 1 < n and _is_list_continuation(lines[i + 1]):
                        i += 1
                        continue
                    else:
                        break
                i += 1
            content = '\n'.join(lines[start:i]) + '\n'
            blocks.append(MdxBlock('list', content, start + 1, i))
            continue

        # Paragraph (fallback)
        start = i
        i += 1
        while i < n and lines[i] != '' and not lines[i].startswith('#') \
                and not lines[i].startswith('```') and not lines[i].startswith('<') \
                and not _is_list_line(lines[i]) and not lines[i].startswith('import '):
            i += 1
        content = '\n'.join(lines[start:i]) + '\n'
        blocks.append(MdxBlock('paragraph', content, start + 1, i))
        continue

    return blocks


def _is_list_line(line: str) -> bool:
    """줄이 리스트 항목으로 시작하는지 확인."""
    stripped = line.lstrip()
    if stripped.startswith('* ') or stripped.startswith('- '):
        return True
    # 번호 리스트: "1. ", "2. ", etc.
    parts = stripped.split('. ', 1)
    if len(parts) == 2 and parts[0].isdigit():
        return True
    return False


def _is_list_continuation(line: str) -> bool:
    """줄이 리스트의 연속(들여쓰기 또는 새 리스트 항목)인지 확인."""
    if _is_list_line(line):
        return True
    # 들여쓰기된 줄 (4칸 또는 탭)
    if line.startswith('    ') or line.startswith('\t'):
        return True
    return False
```

### Step 4: Run test to verify it passes

```bash
cd /Users/jk/workspace/querypie-docs/confluence-mdx
PYTHONPATH=bin python -m pytest tests/test_mdx_block_parser.py::test_parse_simple_document -v
```

Expected: PASS

### Step 5: Write failing test — 코드 블록, HTML 블록, 리스트

```python
# tests/test_mdx_block_parser.py 에 추가

def test_parse_code_block():
    mdx = """## Example

```python
def hello():
    print("world")
```

Next paragraph.
"""
    blocks = parse_mdx_blocks(mdx)
    code = [b for b in blocks if b.type == "code_block"][0]
    assert "def hello():" in code.content
    assert code.type == "code_block"


def test_parse_html_table():
    mdx = """## Table

<table>
<tbody>
<tr>
<td>cell</td>
</tr>
</tbody>
</table>

After table.
"""
    blocks = parse_mdx_blocks(mdx)
    html = [b for b in blocks if b.type == "html_block"][0]
    assert "<table>" in html.content
    assert "</table>" in html.content


def test_parse_list():
    mdx = """## Items

* item 1
* item 2
    * nested

After list.
"""
    blocks = parse_mdx_blocks(mdx)
    lst = [b for b in blocks if b.type == "list"][0]
    assert "* item 1" in lst.content
    assert "    * nested" in lst.content


def test_roundtrip_content():
    """파싱한 블록의 content를 합치면 원본과 동일해야 한다."""
    mdx = """---
title: 'Test'
---

# Title

Paragraph one.

## Section

* list item

```python
code
```

<table>
<tr><td>cell</td></tr>
</table>

End.
"""
    blocks = parse_mdx_blocks(mdx)
    reconstructed = ''.join(b.content for b in blocks)
    assert reconstructed == mdx
```

### Step 6: Run tests, iterate until all pass

```bash
PYTHONPATH=bin python -m pytest tests/test_mdx_block_parser.py -v
```

**중요**: `test_roundtrip_content`는 파싱한 블록의 content를 합쳤을 때 원본과 완전 일치해야 한다. 이 테스트가 통과해야 Phase 1의 블록 비교가 정확해진다.

### Step 7: 실제 MDX 파일로 검증 테스트

```python
# tests/test_mdx_block_parser.py 에 추가
from pathlib import Path

def test_parse_real_testcase_793608206():
    """실제 expected.mdx 파일로 roundtrip 검증."""
    mdx_path = Path(__file__).parent / "testcases" / "793608206" / "expected.mdx"
    if not mdx_path.exists():
        pytest.skip("Test case file not found")
    mdx = mdx_path.read_text()
    blocks = parse_mdx_blocks(mdx)
    reconstructed = ''.join(b.content for b in blocks)
    assert reconstructed == mdx
```

### Step 8: Commit

```bash
git add bin/mdx_block_parser.py tests/test_mdx_block_parser.py
git commit -m "feat: add MDX block parser with roundtrip guarantee"
```

---

## Task 2: Block Diff

두 MDX의 블록 시퀀스를 비교하여 변경된 블록을 추출하는 모듈.

**Files:**
- Create: `confluence-mdx/bin/block_diff.py`
- Test: `confluence-mdx/tests/test_block_diff.py`

### Step 1: Write failing test

```python
# tests/test_block_diff.py
import pytest
from mdx_block_parser import parse_mdx_blocks
from block_diff import diff_blocks, BlockChange


def test_no_changes():
    mdx = "---\ntitle: 'T'\n---\n\n# Title\n\nParagraph.\n"
    original = parse_mdx_blocks(mdx)
    improved = parse_mdx_blocks(mdx)
    changes = diff_blocks(original, improved)
    assert changes == []


def test_text_change_in_paragraph():
    original_mdx = "# Title\n\n접근 제어를 설정합니다.\n"
    improved_mdx = "# Title\n\n접근 통제를 설정합니다.\n"
    original = parse_mdx_blocks(original_mdx)
    improved = parse_mdx_blocks(improved_mdx)
    changes = diff_blocks(original, improved)

    assert len(changes) == 1
    assert changes[0].index == 2  # paragraph 블록의 인덱스
    assert changes[0].change_type == "modified"
    assert "접근 제어" in changes[0].old_block.content
    assert "접근 통제" in changes[0].new_block.content


def test_multiple_changes():
    original_mdx = "# Title\n\nPara one.\n\nPara two.\n"
    improved_mdx = "# Title\n\nPara ONE.\n\nPara TWO.\n"
    original = parse_mdx_blocks(original_mdx)
    improved = parse_mdx_blocks(improved_mdx)
    changes = diff_blocks(original, improved)

    assert len(changes) == 2


def test_block_count_mismatch_raises():
    """Phase 1에서 블록 수가 다르면 에러."""
    original_mdx = "# Title\n\nParagraph.\n"
    improved_mdx = "# Title\n\nParagraph.\n\nNew paragraph.\n"
    original = parse_mdx_blocks(original_mdx)
    improved = parse_mdx_blocks(improved_mdx)

    with pytest.raises(ValueError, match="block count mismatch"):
        diff_blocks(original, improved)
```

### Step 2: Run test to verify it fails

```bash
PYTHONPATH=bin python -m pytest tests/test_block_diff.py -v
```

### Step 3: Write minimal implementation

```python
# bin/block_diff.py
"""Block Diff — 두 MDX 블록 시퀀스를 비교하여 변경된 블록을 추출한다."""
from dataclasses import dataclass
from typing import List
from mdx_block_parser import MdxBlock


@dataclass
class BlockChange:
    index: int              # 블록 인덱스 (0-based)
    change_type: str        # "modified" (Phase 1에서는 modified만 발생)
    old_block: MdxBlock
    new_block: MdxBlock


def diff_blocks(original: List[MdxBlock], improved: List[MdxBlock]) -> List[BlockChange]:
    """두 블록 시퀀스를 1:1 비교하여 변경된 블록 목록을 반환한다.

    Phase 1: 블록 수가 동일해야 한다. 다르면 ValueError.
    """
    if len(original) != len(improved):
        raise ValueError(
            f"block count mismatch: original={len(original)}, improved={len(improved)}"
        )

    changes: List[BlockChange] = []
    for i, (orig, impr) in enumerate(zip(original, improved)):
        if orig.content != impr.content:
            changes.append(BlockChange(
                index=i,
                change_type="modified",
                old_block=orig,
                new_block=impr,
            ))
    return changes
```

### Step 4: Run tests

```bash
PYTHONPATH=bin python -m pytest tests/test_block_diff.py -v
```

### Step 5: Commit

```bash
git add bin/block_diff.py tests/test_block_diff.py
git commit -m "feat: add block diff for Phase 1 sequential comparison"
```

---

## Task 3: Mapping Recorder

Forward converter를 래핑하여 **XHTML 요소 ↔ MDX 블록** 매핑을 기록하는 모듈.

**Files:**
- Create: `confluence-mdx/bin/mapping_recorder.py`
- Test: `confluence-mdx/tests/test_mapping_recorder.py`
- Reference: `confluence-mdx/bin/confluence_xhtml_to_markdown.py` (수정 최소화)

**핵심 전략:**
기존 forward converter를 그대로 실행한 뒤, 그 출력(MDX)과 입력(XHTML)을 분석하여 매핑을 구축한다. converter 내부를 수정하는 것이 아니라, converter의 입/출력을 비교하여 매핑을 추론한다.

구체적으로:
1. XHTML을 BeautifulSoup으로 파싱하여 블록 레벨 요소 추출
2. Forward converter로 생성된 MDX를 `mdx_block_parser.py`로 파싱
3. XHTML 블록 요소와 MDX 블록을 순서대로 정렬하여 매핑

### Step 1: Write failing test

```python
# tests/test_mapping_recorder.py
import pytest
import yaml
from mapping_recorder import record_mapping, BlockMapping


def test_simple_mapping():
    xhtml = '<h2>Overview</h2><p>This is a paragraph.</p>'
    # forward converter 실행 결과를 시뮬레이션하는 대신,
    # XHTML 블록 요소를 직접 추출하여 매핑
    mappings = record_mapping(xhtml)

    assert len(mappings) >= 2
    heading_map = [m for m in mappings if m.type == 'heading'][0]
    assert 'Overview' in heading_map.xhtml_plain_text

    para_map = [m for m in mappings if m.type == 'paragraph'][0]
    assert 'This is a paragraph.' in para_map.xhtml_plain_text


def test_mapping_preserves_xhtml_markup():
    xhtml = '<p><strong>Bold</strong> normal text.</p>'
    mappings = record_mapping(xhtml)

    para_map = [m for m in mappings if m.type == 'paragraph'][0]
    assert '<strong>Bold</strong>' in para_map.xhtml_text
    assert para_map.xhtml_plain_text == 'Bold normal text.'


def test_mapping_to_yaml():
    xhtml = '<h2>Title</h2><p>Content.</p>'
    mappings = record_mapping(xhtml)
    yaml_str = yaml.dump(
        [m.__dict__ for m in mappings],
        allow_unicode=True,
        default_flow_style=False,
    )
    assert 'type: heading' in yaml_str
    assert 'type: paragraph' in yaml_str
```

### Step 2: Run test to verify it fails

```bash
PYTHONPATH=bin python -m pytest tests/test_mapping_recorder.py::test_simple_mapping -v
```

### Step 3: Write implementation

```python
# bin/mapping_recorder.py
"""Mapping Recorder — XHTML 블록 요소를 추출하여 매핑 레코드를 생성한다."""
from dataclasses import dataclass, field
from typing import List, Optional
from bs4 import BeautifulSoup, NavigableString, Tag


@dataclass
class BlockMapping:
    block_id: str
    type: str               # heading | paragraph | list_item | code | table | html_block
    xhtml_xpath: str        # 간이 XPath (예: "h2[1]", "p[3]")
    xhtml_text: str         # 서식 태그 포함 원본
    xhtml_plain_text: str   # 평문 텍스트
    xhtml_element_index: int  # soup.children 내 인덱스
    children: List[str] = field(default_factory=list)


# 블록 레벨 요소 태그 목록
BLOCK_TAGS = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'table',
              'blockquote', 'hr', 'ac:structured-macro'}

HEADING_TAGS = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}


def record_mapping(xhtml: str) -> List[BlockMapping]:
    """XHTML에서 블록 레벨 요소를 추출하여 매핑 레코드를 생성한다."""
    soup = BeautifulSoup(xhtml, 'html.parser')
    mappings: List[BlockMapping] = []
    counters: dict = {}  # 태그별 카운터

    for child in soup.children:
        if isinstance(child, NavigableString):
            if child.strip():
                # 텍스트 노드는 paragraph로 처리
                _add_mapping(mappings, counters, 'p', child.strip(), child.strip())
            continue
        if not isinstance(child, Tag):
            continue

        tag_name = child.name
        if tag_name in HEADING_TAGS:
            plain = child.get_text()
            inner = ''.join(str(c) for c in child.children)
            _add_mapping(mappings, counters, tag_name, inner, plain, block_type='heading')
        elif tag_name == 'p':
            plain = child.get_text()
            inner = ''.join(str(c) for c in child.children)
            _add_mapping(mappings, counters, 'p', inner, plain, block_type='paragraph')
        elif tag_name in ('ul', 'ol'):
            plain = child.get_text()
            inner = str(child)
            _add_mapping(mappings, counters, tag_name, inner, plain, block_type='list')
        elif tag_name == 'table':
            plain = child.get_text()
            inner = str(child)
            _add_mapping(mappings, counters, 'table', inner, plain, block_type='table')
        elif tag_name == 'ac:structured-macro':
            macro_name = child.get('ac:name', '')
            if macro_name == 'code':
                plain_body = child.find('ac:plain-text-body')
                plain = plain_body.get_text() if plain_body else ''
                _add_mapping(mappings, counters, f'macro-{macro_name}', str(child), plain,
                             block_type='code')
            else:
                plain = child.get_text()
                _add_mapping(mappings, counters, f'macro-{macro_name}', str(child), plain,
                             block_type='html_block')
        else:
            # 기타 블록 요소
            plain = child.get_text() if hasattr(child, 'get_text') else str(child)
            inner = str(child)
            _add_mapping(mappings, counters, tag_name, inner, plain, block_type='html_block')

    return mappings


def _add_mapping(
    mappings: List[BlockMapping],
    counters: dict,
    tag_name: str,
    xhtml_text: str,
    xhtml_plain_text: str,
    block_type: Optional[str] = None,
):
    if block_type is None:
        block_type = tag_name
    counters[tag_name] = counters.get(tag_name, 0) + 1
    idx = counters[tag_name]
    block_id = f"{block_type}-{len(mappings) + 1}"
    xpath = f"{tag_name}[{idx}]"
    mappings.append(BlockMapping(
        block_id=block_id,
        type=block_type,
        xhtml_xpath=xpath,
        xhtml_text=xhtml_text.strip(),
        xhtml_plain_text=xhtml_plain_text.strip(),
        xhtml_element_index=len(mappings),
    ))
```

### Step 4: Run tests

```bash
PYTHONPATH=bin python -m pytest tests/test_mapping_recorder.py -v
```

### Step 5: 실제 테스트 케이스로 검증

```python
# tests/test_mapping_recorder.py 에 추가
from pathlib import Path

def test_mapping_real_testcase():
    xhtml_path = Path(__file__).parent / "testcases" / "793608206" / "page.xhtml"
    if not xhtml_path.exists():
        pytest.skip("Test case not found")
    xhtml = xhtml_path.read_text()
    mappings = record_mapping(xhtml)
    # 기본 sanity check
    assert len(mappings) > 0
    types = {m.type for m in mappings}
    assert 'heading' in types
    assert 'paragraph' in types or 'table' in types
```

### Step 6: Commit

```bash
git add bin/mapping_recorder.py tests/test_mapping_recorder.py
git commit -m "feat: add mapping recorder for XHTML block extraction"
```

---

## Task 4: XHTML Patcher

매핑과 diff를 받아 원본 XHTML의 텍스트를 패치하는 모듈.

**Files:**
- Create: `confluence-mdx/bin/xhtml_patcher.py`
- Test: `confluence-mdx/tests/test_xhtml_patcher.py`

**핵심 전략:**
1. 매핑의 `xhtml_plain_text`(old)와 diff의 `new_block.content`에서 추출한 평문(new)을 비교
2. 원본 XHTML에서 해당 요소를 찾아 text node 단위로 변경 적용
3. 인라인 서식 태그(`<strong>`, `<em>` 등)는 보존

### Step 1: Write failing test

```python
# tests/test_xhtml_patcher.py
import pytest
from xhtml_patcher import patch_xhtml


def test_simple_text_replacement():
    xhtml = '<p>접근 제어를 설정합니다.</p>'
    patches = [
        {
            'xhtml_xpath': 'p[1]',
            'old_plain_text': '접근 제어를 설정합니다.',
            'new_plain_text': '접근 통제를 설정합니다.',
        }
    ]
    result = patch_xhtml(xhtml, patches)
    assert '접근 통제를 설정합니다.' in result
    assert '접근 제어' not in result


def test_preserve_inline_formatting():
    xhtml = '<p><strong>접근 제어</strong>를 설정합니다.</p>'
    patches = [
        {
            'xhtml_xpath': 'p[1]',
            'old_plain_text': '접근 제어를 설정합니다.',
            'new_plain_text': '접근 통제를 설정합니다.',
        }
    ]
    result = patch_xhtml(xhtml, patches)
    assert '<strong>접근 통제</strong>' in result
    assert '를 설정합니다.' in result


def test_heading_text_replacement():
    xhtml = '<h2>시스템 아키텍쳐</h2>'
    patches = [
        {
            'xhtml_xpath': 'h2[1]',
            'old_plain_text': '시스템 아키텍쳐',
            'new_plain_text': '시스템 아키텍처',
        }
    ]
    result = patch_xhtml(xhtml, patches)
    assert '<h2>시스템 아키텍처</h2>' in result


def test_no_change_when_text_not_found():
    xhtml = '<p>Original text.</p>'
    patches = [
        {
            'xhtml_xpath': 'p[1]',
            'old_plain_text': 'Not in document.',
            'new_plain_text': 'Replaced.',
        }
    ]
    result = patch_xhtml(xhtml, patches)
    assert result == xhtml  # 변경 없음
```

### Step 2: Run test to verify it fails

```bash
PYTHONPATH=bin python -m pytest tests/test_xhtml_patcher.py -v
```

### Step 3: Write implementation

```python
# bin/xhtml_patcher.py
"""XHTML Patcher — 매핑과 diff를 이용해 XHTML의 텍스트를 패치한다."""
from typing import List, Dict
from bs4 import BeautifulSoup, NavigableString, Tag
import re


def patch_xhtml(xhtml: str, patches: List[Dict[str, str]]) -> str:
    """XHTML에 텍스트 패치를 적용한다.

    Args:
        xhtml: 원본 XHTML 문자열
        patches: 패치 목록. 각 패치는 dict:
            - xhtml_xpath: 간이 XPath (예: "p[1]", "h2[3]")
            - old_plain_text: 원본 평문 텍스트
            - new_plain_text: 변경할 평문 텍스트

    Returns:
        패치된 XHTML 문자열
    """
    soup = BeautifulSoup(xhtml, 'html.parser')

    for patch in patches:
        xpath = patch['xhtml_xpath']
        old_text = patch['old_plain_text']
        new_text = patch['new_plain_text']

        element = _find_element_by_xpath(soup, xpath)
        if element is None:
            continue

        current_plain = element.get_text()
        if current_plain.strip() != old_text.strip():
            continue

        _replace_text_in_element(element, old_text, new_text)

    return str(soup)


def _find_element_by_xpath(soup: BeautifulSoup, xpath: str):
    """간이 XPath (예: "p[1]", "h2[3]")로 요소를 찾는다."""
    match = re.match(r'([a-z0-9:-]+)\[(\d+)\]', xpath)
    if not match:
        return None
    tag_name = match.group(1)
    index = int(match.group(2))  # 1-based

    count = 0
    for child in soup.descendants:
        if isinstance(child, Tag) and child.name == tag_name:
            count += 1
            if count == index:
                return child
    return None


def _replace_text_in_element(element: Tag, old_text: str, new_text: str):
    """요소 내 text node를 업데이트한다. 인라인 서식 태그는 보존."""
    # old_text와 new_text의 차이를 찾아 text node 단위로 적용
    old_parts = _extract_text_parts(element)
    # old_text → new_text 매핑 구축
    _apply_text_changes(element, old_text, new_text)


def _extract_text_parts(element: Tag) -> List[str]:
    """요소에서 text node만 순서대로 추출."""
    parts = []
    for child in element.descendants:
        if isinstance(child, NavigableString) and not isinstance(child, type(None)):
            if child.parent.name not in ('script', 'style'):
                parts.append(str(child))
    return parts


def _apply_text_changes(element: Tag, old_text: str, new_text: str):
    """text node 단위로 old→new 변경을 적용. 인라인 태그 구조 보존."""
    # 전략: old_text와 new_text에서 공통 접두사/접미사를 찾고,
    # 달라지는 부분만 해당 text node에서 교체

    # 간단한 접근: 각 text node를 순회하며 old 텍스트 조각 → new 텍스트 조각으로 교체
    old_remaining = old_text
    new_remaining = new_text

    for child in list(element.descendants):
        if not isinstance(child, NavigableString):
            continue
        if child.parent.name in ('script', 'style'):
            continue

        node_text = str(child)
        node_stripped = node_text.strip()
        if not node_stripped:
            continue

        # old_remaining에서 이 node의 텍스트를 찾아 소비
        pos = old_remaining.find(node_stripped)
        if pos == -1:
            continue

        # old_remaining에서 이 node까지의 텍스트 소비
        consumed_old = old_remaining[:pos + len(node_stripped)]
        consumed_new_end = _find_corresponding_position(old_remaining, new_remaining, pos + len(node_stripped))

        # new_remaining에서 대응하는 부분 추출
        new_node_start = _find_corresponding_position(old_remaining, new_remaining, pos)
        new_node_text = new_remaining[new_node_start:consumed_new_end]

        # 원본 whitespace 보존
        leading = node_text[:len(node_text) - len(node_text.lstrip())]
        trailing = node_text[len(node_text.rstrip()):]
        child.replace_with(NavigableString(leading + new_node_text + trailing))

        old_remaining = old_remaining[pos + len(node_stripped):]
        new_remaining = new_remaining[consumed_new_end:]


def _find_corresponding_position(old_text: str, new_text: str, old_pos: int) -> int:
    """old_text의 위치에 대응하는 new_text의 위치를 찾는다.

    공통 접두사 기반으로 매핑.
    """
    # 단순 휴리스틱: old_text[:old_pos]에서 비공백 문자 수를 세고,
    # new_text에서 같은 수의 비공백 문자가 나오는 위치를 찾는다.
    # 이 방식은 공백 변화가 적은 Phase 1에서 충분히 동작한다.

    # 더 정밀한 방법: difflib를 사용한 시퀀스 매칭
    import difflib
    matcher = difflib.SequenceMatcher(None, old_text, new_text)
    # old_pos에 가장 가까운 매칭 위치를 찾는다
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if i1 <= old_pos <= i2:
            ratio = (old_pos - i1) / max(i2 - i1, 1)
            return int(j1 + ratio * (j2 - j1))
    return min(old_pos, len(new_text))
```

### Step 4: Run tests, iterate

```bash
PYTHONPATH=bin python -m pytest tests/test_xhtml_patcher.py -v
```

**참고**: `_apply_text_changes`는 가장 복잡한 부분이다. 초기 구현에서 `test_preserve_inline_formatting`이 실패할 수 있으며, text node 매핑 로직을 반복 개선해야 한다. Round-trip 검증(Task 5)에서 최종 정확성을 보장하므로, 여기서는 합리적 수준의 정확도를 목표로 한다.

### Step 5: Commit

```bash
git add bin/xhtml_patcher.py tests/test_xhtml_patcher.py
git commit -m "feat: add XHTML patcher with inline formatting preservation"
```

---

## Task 5: Roundtrip Verifier

패치된 XHTML을 forward converter로 다시 변환하고, 개선 MDX와 문자 단위 완전 일치를 검증하는 모듈.

**Files:**
- Create: `confluence-mdx/bin/roundtrip_verifier.py`
- Test: `confluence-mdx/tests/test_roundtrip_verifier.py`

**참조:** `confluence-mdx/bin/confluence_xhtml_to_markdown.py`의 `ConfluenceToMarkdown` 클래스와 `main()` 함수

### Step 1: Write failing test

```python
# tests/test_roundtrip_verifier.py
import pytest
from roundtrip_verifier import verify_roundtrip, VerifyResult


def test_identical_mdx_passes():
    result = verify_roundtrip(
        expected_mdx="# Title\n\nParagraph.\n",
        actual_mdx="# Title\n\nParagraph.\n",
    )
    assert result.passed is True
    assert result.diff_report == ""


def test_different_mdx_fails():
    result = verify_roundtrip(
        expected_mdx="# Title\n\nParagraph.\n",
        actual_mdx="# Title\n\nParagraph\n",  # 마침표 누락
    )
    assert result.passed is False
    assert result.diff_report != ""


def test_whitespace_difference_fails():
    result = verify_roundtrip(
        expected_mdx="# Title\n\nParagraph. \n",  # trailing space
        actual_mdx="# Title\n\nParagraph.\n",
    )
    assert result.passed is False


def test_diff_report_shows_line_numbers():
    result = verify_roundtrip(
        expected_mdx="line1\nline2\nline3\n",
        actual_mdx="line1\nLINE2\nline3\n",
    )
    assert result.passed is False
    assert "2" in result.diff_report  # 2번째 줄
```

### Step 2: Run test to verify it fails

```bash
PYTHONPATH=bin python -m pytest tests/test_roundtrip_verifier.py -v
```

### Step 3: Write implementation

```python
# bin/roundtrip_verifier.py
"""Roundtrip Verifier — 패치된 XHTML의 forward 변환 결과와 개선 MDX의 완전 일치를 검증한다."""
from dataclasses import dataclass
import difflib


@dataclass
class VerifyResult:
    passed: bool
    diff_report: str


def verify_roundtrip(expected_mdx: str, actual_mdx: str) -> VerifyResult:
    """두 MDX 문자열의 완전 일치를 검증한다.

    정규화 없음. 공백, 줄바꿈, 모든 문자가 동일해야 PASS.

    Args:
        expected_mdx: 개선 MDX (의도한 결과)
        actual_mdx: 패치된 XHTML을 forward 변환한 결과

    Returns:
        VerifyResult: passed=True면 통과, 아니면 diff_report 포함
    """
    if expected_mdx == actual_mdx:
        return VerifyResult(passed=True, diff_report="")

    expected_lines = expected_mdx.splitlines(keepends=True)
    actual_lines = actual_mdx.splitlines(keepends=True)

    diff = difflib.unified_diff(
        expected_lines,
        actual_lines,
        fromfile='expected (improved MDX)',
        tofile='actual (roundtrip MDX)',
        lineterm='',
    )
    report = ''.join(diff)

    return VerifyResult(passed=False, diff_report=report)
```

### Step 4: Run tests

```bash
PYTHONPATH=bin python -m pytest tests/test_roundtrip_verifier.py -v
```

### Step 5: Commit

```bash
git add bin/roundtrip_verifier.py tests/test_roundtrip_verifier.py
git commit -m "feat: add roundtrip verifier with exact match validation"
```

---

## Task 6: Orchestrator (reverse_sync.py)

모든 모듈을 연결하는 CLI 도구. `verify`와 `push` 서브커맨드 제공.

**Files:**
- Create: `confluence-mdx/bin/reverse_sync.py`
- Test: `confluence-mdx/tests/test_reverse_sync.py`
- Reference: `confluence-mdx/bin/confluence_xhtml_to_markdown.py` (forward converter 호출)

### Step 1: Write failing test — verify 커맨드의 핵심 로직

```python
# tests/test_reverse_sync.py
import pytest
import tempfile
from pathlib import Path
from reverse_sync import run_verify


def test_verify_no_changes(tmp_path):
    """변경 없으면 PASS, 패치 없음."""
    mdx_content = "---\ntitle: 'Test'\n---\n\n# Test\n\nParagraph.\n"
    original = tmp_path / "original.mdx"
    improved = tmp_path / "improved.mdx"
    original.write_text(mdx_content)
    improved.write_text(mdx_content)

    result = run_verify(
        original_mdx_path=str(original),
        improved_mdx_path=str(improved),
    )
    assert result['status'] == 'no_changes'
    assert result['changes_count'] == 0


def test_verify_detects_changes(tmp_path):
    """텍스트 변경을 감지."""
    original = tmp_path / "original.mdx"
    improved = tmp_path / "improved.mdx"
    original.write_text("# Title\n\n접근 제어를 설정합니다.\n")
    improved.write_text("# Title\n\n접근 통제를 설정합니다.\n")

    result = run_verify(
        original_mdx_path=str(original),
        improved_mdx_path=str(improved),
    )
    assert result['changes_count'] == 1
```

### Step 2: Run test to verify it fails

```bash
PYTHONPATH=bin python -m pytest tests/test_reverse_sync.py -v
```

### Step 3: Write implementation

```python
# bin/reverse_sync.py
"""Reverse Sync — MDX 변경사항을 Confluence XHTML에 역반영하는 파이프라인.

Usage:
    python reverse_sync.py verify --original-mdx <path> --improved-mdx <path> [--page-id <id>]
    python reverse_sync.py push --page-id <id>
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any

from mdx_block_parser import parse_mdx_blocks
from block_diff import diff_blocks


def run_verify(
    original_mdx_path: str,
    improved_mdx_path: str,
    page_id: str = None,
    xhtml_path: str = None,
) -> Dict[str, Any]:
    """로컬 검증 파이프라인을 실행한다.

    Step 1: MDX 블록 파싱
    Step 2: 블록 Diff 추출
    Step 3-6: (XHTML이 있을 때만) 매핑 → 패치 → forward 변환 → 검증

    Returns:
        dict with: status, changes_count, changes, verify_result (if applicable)
    """
    original_mdx = Path(original_mdx_path).read_text()
    improved_mdx = Path(improved_mdx_path).read_text()

    # Step 1: MDX 블록 파싱
    original_blocks = parse_mdx_blocks(original_mdx)
    improved_blocks = parse_mdx_blocks(improved_mdx)

    # Step 2: 블록 Diff 추출
    changes = diff_blocks(original_blocks, improved_blocks)

    if not changes:
        return {
            'status': 'no_changes',
            'changes_count': 0,
            'changes': [],
        }

    result = {
        'status': 'changes_detected',
        'changes_count': len(changes),
        'changes': [
            {
                'index': c.index,
                'type': c.change_type,
                'old_content': c.old_block.content,
                'new_content': c.new_block.content,
            }
            for c in changes
        ],
    }

    # Step 3-6: XHTML이 있으면 패치 + 검증
    if xhtml_path and Path(xhtml_path).exists():
        from mapping_recorder import record_mapping
        from xhtml_patcher import patch_xhtml
        from roundtrip_verifier import verify_roundtrip

        xhtml = Path(xhtml_path).read_text()

        # Step 3: 매핑 생성
        mappings = record_mapping(xhtml)

        # Step 4: XHTML 패치 — diff의 각 변경에 대해 매핑으로 패치 구성
        patches = _build_patches(changes, original_blocks, improved_blocks, mappings)
        patched_xhtml = patch_xhtml(xhtml, patches)

        # Step 5-6: forward 변환 + 검증은 별도 호출 필요
        # (forward converter는 파일 경로, pages.yaml 등 많은 컨텍스트 필요)
        result['patched_xhtml'] = patched_xhtml
        result['status'] = 'patched'

    return result


def _build_patches(changes, original_blocks, improved_blocks, mappings):
    """diff 변경과 매핑을 결합하여 XHTML 패치 목록을 구성한다."""
    patches = []
    # 매핑에서 content block만 필터 (frontmatter, empty 등 제외)
    content_mappings = [m for m in mappings]

    for change in changes:
        # 변경된 블록이 content mapping의 어느 것에 해당하는지 찾기
        old_block = change.old_block
        if old_block.type in ('empty', 'frontmatter', 'import_statement'):
            continue

        # 매핑에서 평문 텍스트가 일치하는 것을 찾기
        old_plain = old_block.content.strip()
        # MDX 마크업 제거 (heading의 # 등)
        if old_block.type == 'heading':
            old_plain = old_plain.lstrip('#').strip()

        for mapping in content_mappings:
            if mapping.xhtml_plain_text.strip() == old_plain:
                new_block = change.new_block
                new_plain = new_block.content.strip()
                if new_block.type == 'heading':
                    new_plain = new_plain.lstrip('#').strip()

                patches.append({
                    'xhtml_xpath': mapping.xhtml_xpath,
                    'old_plain_text': mapping.xhtml_plain_text,
                    'new_plain_text': new_plain,
                })
                break

    return patches


def main():
    parser = argparse.ArgumentParser(description='Reverse Sync: MDX → Confluence XHTML')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # verify
    verify_parser = subparsers.add_parser('verify', help='로컬 검증')
    verify_parser.add_argument('--page-id', help='Confluence page ID')
    verify_parser.add_argument('--original-mdx', required=True, help='원본 MDX 경로')
    verify_parser.add_argument('--improved-mdx', required=True, help='개선 MDX 경로')
    verify_parser.add_argument('--xhtml', help='원본 XHTML 경로 (없으면 var/<page-id>/page.xhtml)')

    # push
    push_parser = subparsers.add_parser('push', help='Confluence 반영')
    push_parser.add_argument('--page-id', required=True, help='Confluence page ID')

    args = parser.parse_args()

    if args.command == 'verify':
        xhtml_path = args.xhtml
        if not xhtml_path and args.page_id:
            xhtml_path = f'var/{args.page_id}/page.xhtml'

        result = run_verify(
            original_mdx_path=args.original_mdx,
            improved_mdx_path=args.improved_mdx,
            page_id=args.page_id,
            xhtml_path=xhtml_path,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))

        if result['status'] == 'no_changes':
            print('\nNo changes detected.')
        else:
            print(f"\n{result['changes_count']} change(s) detected.")

    elif args.command == 'push':
        print(f"Push for page {args.page_id} — not yet implemented")
        sys.exit(1)


if __name__ == '__main__':
    main()
```

### Step 4: Run tests

```bash
PYTHONPATH=bin python -m pytest tests/test_reverse_sync.py -v
```

### Step 5: Commit

```bash
git add bin/reverse_sync.py tests/test_reverse_sync.py
git commit -m "feat: add reverse sync orchestrator with verify command"
```

---

## Task 7: 통합 테스트 — 실제 테스트 케이스로 전체 파이프라인 검증

실제 테스트 케이스 데이터를 사용하여 전체 파이프라인을 end-to-end로 검증한다.

**Files:**
- Create: `confluence-mdx/tests/test_reverse_sync_e2e.py`
- Create: `confluence-mdx/tests/testcases/reverse_sync/` (테스트 데이터)

### Step 1: 테스트 데이터 준비

기존 테스트 케이스 `793608206`의 expected.mdx를 원본으로, 일부 텍스트를 수정한 improved.mdx를 생성한다.

```python
# tests/test_reverse_sync_e2e.py
import pytest
from pathlib import Path
from mdx_block_parser import parse_mdx_blocks
from block_diff import diff_blocks
from mapping_recorder import record_mapping
from xhtml_patcher import patch_xhtml


TESTCASE_DIR = Path(__file__).parent / "testcases" / "793608206"


@pytest.fixture
def testcase_data():
    xhtml_path = TESTCASE_DIR / "page.xhtml"
    mdx_path = TESTCASE_DIR / "expected.mdx"
    if not xhtml_path.exists() or not mdx_path.exists():
        pytest.skip("Test case files not found")
    return {
        'xhtml': xhtml_path.read_text(),
        'mdx': mdx_path.read_text(),
    }


def test_e2e_text_replacement(testcase_data):
    """실제 MDX에서 텍스트를 변경하고 XHTML 패치가 동작하는지 확인."""
    original_mdx = testcase_data['mdx']
    xhtml = testcase_data['xhtml']

    # 텍스트 변경: "요청 제목" → "요청 타이틀"
    improved_mdx = original_mdx.replace('요청 제목', '요청 타이틀')
    assert improved_mdx != original_mdx, "변경이 적용되어야 함"

    # Step 1-2: 블록 파싱 + diff
    original_blocks = parse_mdx_blocks(original_mdx)
    improved_blocks = parse_mdx_blocks(improved_mdx)
    changes = diff_blocks(original_blocks, improved_blocks)
    assert len(changes) > 0

    # Step 3: 매핑
    mappings = record_mapping(xhtml)
    assert len(mappings) > 0

    # Step 4: XHTML 패치
    # (패치 구성은 reverse_sync.py의 _build_patches 로직 사용)
    from reverse_sync import _build_patches
    patches = _build_patches(changes, original_blocks, improved_blocks, mappings)

    if patches:
        patched = patch_xhtml(xhtml, patches)
        # 패치된 XHTML에 변경이 반영되었는지 확인
        assert '요청 타이틀' in patched
        assert '요청 제목' not in patched  # 원본 텍스트는 제거됨


def test_e2e_no_change_identity(testcase_data):
    """변경 없이 파이프라인을 돌리면 diff가 비어있어야 한다."""
    mdx = testcase_data['mdx']
    original_blocks = parse_mdx_blocks(mdx)
    improved_blocks = parse_mdx_blocks(mdx)
    changes = diff_blocks(original_blocks, improved_blocks)
    assert changes == []
```

### Step 2: Run e2e tests

```bash
PYTHONPATH=bin python -m pytest tests/test_reverse_sync_e2e.py -v
```

### Step 3: 실패하는 케이스 수정, 반복

e2e 테스트에서 실패하는 케이스가 있으면, 해당 모듈(주로 `xhtml_patcher.py` 또는 `mapping_recorder.py`)을 수정한다.

### Step 4: Commit

```bash
git add tests/test_reverse_sync_e2e.py
git commit -m "test: add end-to-end reverse sync tests with real data"
```

---

## Task 순서 요약

| Task | 모듈 | 의존성 | 설명 |
|------|------|--------|------|
| 1 | mdx_block_parser.py | 없음 | MDX → 블록 시퀀스 파싱 |
| 2 | block_diff.py | Task 1 | 블록 시퀀스 1:1 비교 |
| 3 | mapping_recorder.py | 없음 | XHTML → 블록 매핑 추출 |
| 4 | xhtml_patcher.py | 없음 | XHTML 텍스트 패치 |
| 5 | roundtrip_verifier.py | 없음 | MDX 문자 단위 완전 일치 검증 |
| 6 | reverse_sync.py | Task 1-5 | 전체 오케스트레이션 CLI |
| 7 | e2e tests | Task 1-6 | 실제 데이터로 통합 테스트 |

**독립 Task (병렬 가능)**: 1, 3, 4, 5
**순차 Task**: 2 (→1), 6 (→1-5), 7 (→6)

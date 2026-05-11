---
name: normalize-mdx-jsx-table-indentation
description: Normalize JSX-style <Table> blocks embedded in MDX files by removing stray leading whitespace and reindenting nested table tags with 2-space steps.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Normalize MDX JSX table indentation

Use when MDX files contain embedded JSX table blocks such as `<Table>`, `<Table.Tbody>`, `<Table.Tr>`, `<Table.Td>`, `<Table.Th>`, and the indentation has drifted from mixed-width or inconsistent whitespace.

Typical symptoms:
- table blocks start with large arbitrary left padding
- nested table tags do not increase by a consistent indent step
- content inside table cells has stale copied indentation from upstream HTML/JSX
- repo review asks for 2-space indentation per nesting level

## Goal
- remove arbitrary leading whitespace before table markup lines
- reindent table blocks so nesting increases by exactly 2 spaces
- keep non-table prose untouched
- preserve cell content text exactly except for leading indentation normalization inside the table block

## Safe approach
Use a line-based formatter scoped only to `<Table> ... </Table>` regions.

Do not try to run a whole-file generic formatter first if:
- the repo does not already have a stable MDX formatter for these files
- the files mix Markdown prose and JSX heavily
- only table indentation needs normalization

## Python script pattern
Run from the repo root or target worktree.

```python
from pathlib import Path
import re

root = Path('src/content/privacy-policy')

open_tag_re = re.compile(r'^<([A-Za-z][\w.]*)\b[^>]*?>$')
close_tag_re = re.compile(r'^</([A-Za-z][\w.]*)>$')
self_closing_re = re.compile(r'^<([A-Za-z][\w.]*)\b[^>]*?/>$')


def format_table_block(lines):
    out = []
    level = 0
    for raw in lines:
        s = raw.strip()
        if s == '':
            out.append('')
            continue

        is_close = bool(close_tag_re.match(s))
        is_open = bool(open_tag_re.match(s))
        is_self = bool(self_closing_re.match(s))

        if is_close:
            level = max(level - 1, 0)

        out.append(('  ' * level) + s)

        if is_open and not is_close and not is_self:
            level += 1
    return out


def normalize_tables(text):
    lines = text.splitlines()
    out = []
    i = 0
    changed = False
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped == '<Table>':
            block = []
            while i < len(lines):
                block.append(lines[i])
                if lines[i].strip() == '</Table>':
                    break
                i += 1
            formatted = format_table_block(block)
            if formatted != block:
                changed = True
            out.extend(formatted)
        else:
            out.append(lines[i])
        i += 1
    return '\n'.join(out) + ('\n' if text.endswith('\n') else ''), changed

changed_files = []
for path in sorted(root.glob('*.mdx')):
    original = path.read_text()
    updated, changed = normalize_tables(original)
    if changed:
        path.write_text(updated)
        changed_files.append(path)

for path in changed_files:
    print(path)
```

## What this does
- detects only `<Table>` blocks
- strips each line inside the block to semantic content
- reapplies indentation from nesting depth
- uses 2 spaces per level
- leaves non-table sections alone

## Verification
After rewriting:
1. read a representative file and confirm:
   - `<Table>` begins at column 0
   - immediate children are indented 2 spaces
   - grandchildren are indented 4 spaces, etc.
2. search for suspicious over-indented table lines, for example:
   - `^\s+<Table>$`
   - `^\s+<Table\.`
3. run the narrowest repo tests that cover the affected MDX family.

Example checks:
```bash
node --test tests/legal-privacy-policy-preview.test.mjs
```

## Pitfalls
- This normalizes indentation, not Markdown semantics. If a table cell should contain a real Markdown list, you may still need a manual follow-up.
- Because the script strips line prefixes inside table blocks, use it only when the review goal is indentation cleanup and the content meaning is unchanged.
- Do not apply blindly to arbitrary JSX blocks outside tables without checking nesting patterns first.

## Best use case
Large MDX corpora imported from upstream where embedded JSX tables have inconsistent legacy indentation and the repo expects a strict 2-space nesting style.
from pathlib import Path
import re

"""Normalize JSX-style <Table> blocks embedded in MDX files.

Usage: adjust `root = Path('src/content/privacy-policy')` to your target directory,
then run this script from the repo root or target worktree.

This script:
- detects only <Table> blocks
- strips each line inside the block to semantic content
- reapplies indentation from nesting depth
- uses 2 spaces per level
- leaves non-table sections alone
"""

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

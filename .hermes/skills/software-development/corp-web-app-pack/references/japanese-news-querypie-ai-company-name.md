# Japanese news company-name normalization

Use this when editing `src/content/news/<id>-*.ja.mdx` Japanese news copy that refers to the company.

## Rule

- When the Japanese article refers to the company itself, use `QueryPie AI`.
- This includes frontmatter `title`, `description`, body lead copy, section headings such as `## QueryPie AIについて`, quotes that identify the founder/representative, image alt text that names the company, and media-contact owner labels.
- Preserve product/platform names as written when they are not company-name references:
  - `QueryPie AIP`
  - `QueryPie AI Platform`

## Lightweight verification

After editing the target Japanese MDX files, verify that no standalone company-name `QueryPie` remains outside the allowed product-name patterns.

Example source-level check:

```python
from pathlib import Path
import re

files = [
    Path('src/content/news/24-iso-42001-certification-announcement.ja.mdx'),
    Path('src/content/news/25-iso-42001-certification-press-release.ja.mdx'),
    Path('src/content/news/26-lingo-launch.ja.mdx'),
]
pattern = re.compile(r'QueryPie(?! AI| AIP)')

for path in files:
    for line_no, line in enumerate(path.read_text().splitlines(), 1):
        if pattern.search(line):
            print(f'{path}:{line_no}: {line}')
```

A clean result means every remaining `QueryPie` is part of `QueryPie AI`, `QueryPie AI Platform`, or `QueryPie AIP`. Review matches manually if new product names are introduced.

## Pitfalls

- Do not blanket-replace all `QueryPie` with `QueryPie AI`; that would corrupt `QueryPie AIP` into `QueryPie AI AIP`.
- Do not change this as a site-wide metadata/title-brand policy. This reference is specifically for Japanese news article copy where the company itself is being named.

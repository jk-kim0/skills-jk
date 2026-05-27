# Use-cases source-root parity audit

Use this when checking whether a use-cases migration is complete against `corp-web-contents`.

## Key distinction

There are two similar-looking source roots:

- Full demo use-case corpus:
  - `../corp-web-contents/pages/features/demo/use-cases/<id>/<slug>/<locale>/content.mdx`
  - Observed coverage: 29 EN, 29 JA, 6 KO records = 64 MDX records total.
  - IDs: 1-29.
- Customer-success archive subset:
  - `../corp-web-contents/page-archives/customers/customer-success-cases/<id>/<slug>/<locale>/content.mdx`
  - Coverage: IDs 1-5 only, EN/JA/KO = 15 MDX records.
  - This subset overlaps the first five demo use-cases, but is not the full use-cases corpus.

If the user asks for parity with corp-web-japan use-cases or with `pages/features/demo/use-cases`, do not use the archive subset as the migration source.

## Fast source inventory

```bash
cd ../corp-web-contents
python3 - <<'PY'
import subprocess
from collections import Counter
files = subprocess.check_output([
    'git', 'ls-files', 'pages/features/demo/use-cases/*/*/*/content.mdx'
], text=True).splitlines()
print('files', len(files))
print('locale_counts', dict(Counter(path.split('/')[6] for path in files)))
print('ids', len({path.split('/')[4] for path in files}))
PY
```

Expected shape for full parity:

```text
files 64
locale_counts {'en': 29, 'ja': 29, 'ko': 6}
ids 29
```

## Source-to-target parity check

After generating/migrating target MDX files, compare normalized bodies and asset presence rather than only file counts.

```bash
python3 - <<'PY'
import re
from pathlib import Path
src = Path('../corp-web-contents/pages/features/demo/use-cases')
target_root = Path('src/content/demo/use-cases')
public_root = Path('public')

def split_frontmatter(text):
    m = re.match(r'^---\n([\s\S]*?)\n---\n?', text)
    return ('', text) if not m else (m.group(1), text[m.end():])

def normalize(text):
    return re.sub(r'\s+', ' ', text.replace('\r\n', '\n').strip())

missing = []
body_diffs = []
missing_assets = []

for source_file in src.glob('*/*/*/content.mdx'):
    id_, slug, locale = source_file.parts[-4], source_file.parts[-3], source_file.parts[-2]
    target_file = target_root / f'{id_}-{slug}.{locale}.mdx'
    if not target_file.exists():
        missing.append(str(target_file))
        continue
    _, source_body = split_frontmatter(source_file.read_text(encoding='utf-8'))
    _, target_body = split_frontmatter(target_file.read_text(encoding='utf-8'))
    if normalize(source_body) != normalize(target_body):
        body_diffs.append(f'{id_}-{slug}.{locale}')

for target_file in target_root.glob('*.mdx'):
    text = target_file.read_text(encoding='utf-8')
    match = re.search(r'^heroImageSrc: "?([^"\n]+)"?$', text, re.M)
    if match and not (public_root / match.group(1).lstrip('/')).exists():
        missing_assets.append((target_file.name, match.group(1)))

print('missing', len(missing), missing[:5])
print('body_diffs', len(body_diffs), body_diffs[:5])
print('missing_assets', len(missing_assets), missing_assets[:5])
print('mdx_count', len(list(target_root.glob('*.mdx'))))
PY
```

For a complete corp-web-app demo/use-cases migration, expected result is:

```text
missing 0 []
body_diffs 0 []
missing_assets 0 []
mdx_count 64
```

## Test contract recommendation

For full use-case parity, tests should assert:

- unique IDs exactly `1..29`
- total records exactly `64`
- EN list IDs exactly `1..29`
- JA list IDs exactly `1..29`
- KO list IDs exactly `1..6`
- `validatePublicationAssets(...)` returns `[]`

Avoid tests like `expect(ids.size).toBe(5)` unless the explicit task is only the customer-success archive subset.

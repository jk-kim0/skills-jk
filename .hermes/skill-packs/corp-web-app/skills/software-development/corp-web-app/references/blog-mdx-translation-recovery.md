# Blog MDX missing-translation recovery

Use this reference when asked to fill missing `src/content/blog/*.mdx` locale files in `corp-web-app` from `corp-web-contents` history.

## Source-of-truth order

1. Start from latest `origin/main` in a repo-local `.worktrees/<topic>` worktree.
2. Inspect `docs/inventories/corp-web-contents-document-locale-inventory.md` for blog rows and source paths. This inventory usually points at `corp-web-contents` paths such as:
   - `pages/features/documentation/blog/<id>/<slug>/<locale>/content.mdx`
   - historical/archive equivalents such as `page-archives/discover/blog/<id>/<slug>/<locale>/content.mdx`
3. If a locale is marked missing in the inventory, search the `corp-web-contents` git history before deciding it is unavailable:
   ```bash
   git log --all --name-only --pretty=format: | sed '/^$/d' | sort -u | grep 'pages/features/documentation/blog/<id>/' | grep 'content.mdx'
   git log --all --name-only --pretty=format: | sed '/^$/d' | sort -u | grep 'page-archives/discover/blog/<id>/' | grep 'content.mdx'
   ```
4. Only create locale files when an actual `corp-web-contents` source MDX exists. Do not machine-translate or paraphrase missing locales.

## Conversion rules

- Destination shape: `src/content/blog/<id>-<slug>.<locale>.mdx`.
- Preserve the destination repo's route-aligned frontmatter shape:
  - `id`, `slug`, localized `title` / `description` / `date`
  - `heroImageSrc: "/blog/<id>/thumbnail.png"`
  - `relatedIds` as numeric IDs, derived from existing locale variants when available; otherwise convert legacy `relatedPosts` blog URLs.
  - Preserve hidden redirect shadow-record behavior from an existing locale variant (`hidden`, `redirectUrl`) rather than making redirected news/blog shadows public in a new locale.
  - Preserve structural fields from existing locale variants (`gated`, `noindex`, `category`, `author`) when present.
  - Copy localized `keywords` from the source MDX if present.
- Body content must come from the source MDX exactly except for route-aligned image path rewrites.
- Rewrite legacy inline image filepaths from `public/blog/<filename>` to `public/blog/<id>/<filename>`. Leave already route-aligned `public/blog/<id>/...` paths unchanged.
- Keep one blank line between frontmatter and body.

## Verification pattern

Run the narrowest source-level proof first:

```bash
npx vitest run src/lib/repo-content/__tests__/blog-migration.test.ts
git diff --check
```

Then run a source scan that reports final locale coverage and fails on legacy image filepaths:

```bash
python3 - <<'PY'
from pathlib import Path
import collections, re, sys
root = Path('src/content/blog')
byid = collections.defaultdict(set)
for p in sorted(root.glob('*.mdx')):
    m = re.match(r'(\d+)-(.+)\.(en|ko|ja)\.mdx$', p.name)
    if m:
        byid[m.group(1)].add(m.group(3))
print('total files', sum(len(v) for v in byid.values()))
print('locale records', {loc: sum(loc in s for s in byid.values()) for loc in ['en', 'ko', 'ja']})
for id_, locs in sorted(byid.items(), key=lambda kv: int(kv[0])):
    miss = sorted({'en', 'ko', 'ja'} - locs)
    if miss:
        print(id_, 'missing', ','.join(miss), 'have', ','.join(sorted(locs)))
for p in sorted(root.glob('*.mdx')):
    text = p.read_text()
    if re.search(r'filepath="public/blog/(?!\d+/)', text):
        print('legacy filepath', p)
        sys.exit(1)
print('source scan ok')
PY
```

If broader publication tests are attempted from a fresh worktree and CSS route tests fail during PostCSS dependency resolution, do not broaden the change or install dependencies just to satisfy local verification. Report that the repo-content test passed and that the broader local collection was blocked by fresh-worktree dependency resolution; CI/PR checks remain the authoritative broad validation.

## Test update expectations

Update `src/lib/repo-content/__tests__/blog-migration.test.ts` with:

- new total record count
- locale-specific list counts
- a positive assertion that a recovered locale detail resolves as `found`
- a negative assertion that a locale with no source translation still resolves as `missing-locale`

This preserves the user's rule: recovered historical translations may be filled, but unknown translations must remain missing instead of being invented.

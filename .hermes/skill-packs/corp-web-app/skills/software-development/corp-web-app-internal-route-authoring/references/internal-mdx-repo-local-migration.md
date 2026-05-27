# Internal MDX repo-local migration note

Use this when an internal-only page currently comes from `corp-web-contents` / legacy `dynamic-page` but the user asks to move it into `corp-web-app`.

Session-derived pattern from PR 803:

- Do not treat a slug rename as complete if the actual MDX file still lives in `corp-web-contents`.
- If the requested source file is in `corp-web-contents`, first verify whether there is a companion contents PR/branch with the actual rename.
- For repo-local internal MDX, place the MDX under `src/content/internal/`.
  - Example: `src/content/internal/sample-article-2024-11-22.en.mdx`.
- Add an explicit App Router internal route under `src/app/[locale]/internal/<slug>/page.tsx`.
- The explicit internal route should read repo-local MDX directly, e.g. through a small `src/lib/internal/<page>.ts` loader using `fs.readFileSync` and frontmatter parsing.
- The explicit internal route should not import or delegate to:
  - `src/app/dynamic-page`
  - `FileQuery`
  - remote `corp-web-contents` fetch/listing flows
- Keep internal pages noindex/nofollow in metadata.
- If only EN source exists, make KO/JA behavior explicit. For internal sample content, EN fallback is acceptable when the internal index links each locale to the same internal route.
- Move referenced assets into a route-aligned app-local public directory.
  - Example: `public/internal/sample-article-2024-11-22/...`.
- Rewrite MDX asset references to the app-local public asset paths.
- Watch for hidden remote lookups through shared article components:
  - `ArticleFileImage` normally resolves `public/...` via `FileQuerySingleton`.
  - string `relatedPosts` can trigger remote frontmatter lookup.
  - `ogImage` can be used by shared article chrome and may also route through FileQuery-dependent components.
- For a fully repo-local internal sample route, override MDX image components or otherwise ensure images resolve from local `/public`, and remove/disable remote-looking related-post frontmatter if necessary.

Useful verification checks:

```bash
# Route should read repo-local MDX and avoid the legacy remote path.
rg -n 'getInternalSampleArticle|dynamic-page|FileQuery' \
  src/app/[locale]/internal/<slug>/page.tsx

# MDX should point at local internal assets, not legacy content paths.
rg -n 'public/internal/<slug>|/resources/discover|public/blog|public/white-paper' \
  src/content/internal/<slug>.en.mdx

# Every referenced internal asset should exist.
python3 - <<'PY'
from pathlib import Path
import re
root = Path('.')
mdx = root / 'src/content/internal/<slug>.en.mdx'
text = mdx.read_text()
for asset in sorted(set(re.findall(r'public/internal/<slug>/[A-Za-z0-9_.-]+', text))):
    assert (root / asset).exists(), asset
print('ok')
PY
```

Fresh worktree verification pitfall:

- Targeted Vitest can fail before collecting tests if the fresh worktree has no local devDependency install for `@tailwindcss/postcss` and imports CSS modules.
- Do not default to a slow worktree-local `npm install` when the user prefers avoiding it.
- Record the PostCSS dependency issue, run source-level checks plus `scripts/ci/assert-test-groups.mjs`, and rely on CI when appropriate.

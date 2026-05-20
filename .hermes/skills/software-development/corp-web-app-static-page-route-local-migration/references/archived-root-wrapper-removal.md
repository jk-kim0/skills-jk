# Archived root wrapper removal pattern

Use when corp-web-app has duplicate archived routes under both:

- `src/app/archived/**`
- `src/app/[locale]/archived/**`

## When the root wrappers are redundant

Root `src/app/archived/**` wrapper pages are redundant only when all of these are true:

1. `src/middleware.ts` already treats `/archived` as a default-locale rewrite prefix, e.g. `DEFAULT_LOCALE_REWRITE_PREFIXES = ['/archived']`.
2. Middleware tests prove:
   - English/default `/archived/<slug>` rewrites internally to `/en/archived/<slug>` without changing the public URL.
   - Non-English `/archived/<slug>` redirects to `/{locale}/archived/<slug>`.
   - Public static assets under `/archived/**` are not locale-redirected.
3. Every removed root wrapper has a matching `src/app/[locale]/archived/**/page.tsx` route entry.
4. Tests and docs no longer import or describe `src/app/archived/**` as the implementation source.

## Safe workflow

1. Inspect routing first:

```bash
rg -n "DEFAULT_LOCALE_REWRITE_PREFIXES|/archived|archived routes" src/middleware.ts src/__tests__/middleware.test.ts
find src/app/archived -type f -name 'page.tsx' | sort
find 'src/app/[locale]/archived' -type f -name 'page.tsx' | sort
```

2. Confirm coverage:

```bash
python3 - <<'PY'
from pathlib import Path
root = Path('.')
root_pages = sorted(Path('src/app/archived').rglob('page.tsx'))
missing = []
for p in root_pages:
    rel = p.relative_to('src/app/archived')
    target = Path('src/app/[locale]/archived') / rel
    if not target.exists():
        missing.append(str(target))
print('\n'.join(missing))
raise SystemExit(1 if missing else 0)
PY
```

3. Remove root wrappers:

```bash
git rm -r src/app/archived
```

4. Move mirrored route tests from `src/__tests__/app/archived/**` to `src/__tests__/app/[locale]/archived/**` and update imports from deleted root wrappers to the English locale authoring files, for example:

```ts
import Page, { generateMetadata } from 'src/app/[locale]/archived/<slug>/page.en';
```

Keep non-English imports pointing at `page.ko` / `page.ja`. Do not use a broad replacement that rewrites unrelated test files.

5. Update route-local README files only where they directly mention deleted root wrapper files. Preserve useful provenance details.

6. Verify:

```bash
git diff --check
node scripts/ci/assert-test-groups.mjs
rg -n "src/app/archived|from ['\"]src/app/archived|canonical: 'https://querypie\.example/archived" src --glob '*.{ts,tsx}'
test ! -e src/app/archived
```

Targeted Vitest is useful, but fresh worktrees in this repo may lack local `node_modules`; CSS/PostCSS-loading suites can fail locally with missing `@tailwindcss/postcss`. Do not spend time on local installs if the user prefers CI. Report partial test results and rely on CI after push.

## Pitfalls

- Do not delete `src/app/[locale]/archived/**`; that is the active route implementation.
- Do not remove or change public `/archived/**` behavior unless explicitly requested. The unprefixed URL remains public via middleware rewrite.
- Do not leave tests importing deleted root wrappers.
- Do not over-apply string replacements across all tests; restrict import/canonical rewrites to archived route tests and explicitly named flat archived tests.
- After the PR, keep the root checkout clean and fast-forward root `main` when safe.

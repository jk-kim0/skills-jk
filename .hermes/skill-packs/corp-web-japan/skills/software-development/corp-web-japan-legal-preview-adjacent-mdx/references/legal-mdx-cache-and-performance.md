# Legal MDX cache, privacy-policy latency, and selector navigation notes

Session context: corp-web-japan PR #498 investigated whether legal/privacy-policy MDX reads were cached like blog/whitepaper, why privacy-policy felt slow, and why changing the privacy-policy version looked like a page reload.

## Cache findings

Legal MDX source reads were already cached:

- `src/lib/legal-mdx-source.ts`
  - `legalMdxSourceCache = new Map<string, Promise<string>>()`
  - `readCachedLegalMdxSource(sourcePath)` caches raw MDX source reads by path
  - `renderLegalMdx(...)` reads through that helper and evaluates MDX with `parseFrontmatter: true`
- `src/app/privacy-policy/[slug]/page.tsx`
  - `renderPrivacyPolicyVersion = cache(async function renderPrivacyPolicyVersion(slug: string) { ... })`
  - reads `src/content/privacy-policy/${slug}.mdx`
  - calls `renderLegalMdx<PrivacyPolicyFrontmatter>({ sourcePath, components: buildPrivacyPolicyDocumentComponents() })`
- `src/app/terms-of-service/page.tsx` and `src/app/eula/page.tsx` use the same shared `renderLegalMdx` helper from route-level `cache(...)` wrappers.

Comparison with publication loaders:

- `src/lib/publications/create-standard-publication-post-loader.ts`
  - `bodySourceCache = new Map<string, string>()`
  - caches raw body source with `bodySourceCache.get(sourcePath)` / `set(sourcePath, source)`
- `src/lib/publications/create-gated-publication-post-loader.ts` has the same raw-source cache pattern for gated whitepapers.

Conclusion: legal already had the same class of raw MDX source-read cache. A minimal test-only PR is appropriate if the code is already correct: pin the cache contract instead of adding unnecessary product code.

## Privacy-policy latency findings

Live stage probes showed privacy-policy pages were not full-route cached:

```bash
curl -L -s -D - -o /dev/null https://stage.querypie.ai/privacy-policy | sed -n '1,40p'
```

Observed headers:

- `cache-control: private, no-cache, no-store, max-age=0, must-revalidate`
- `x-vercel-cache: MISS`

The same was true for `/privacy-policy/2026-01-15`.

Important distinction:

- `legalMdxSourceCache` caches raw MDX source reads inside a live server module instance.
- React `cache(...)` dedupes render helper calls request-locally.
- Neither is a CDN/full-route HTML cache, nor a cross-instance rendered-output cache.

Likely delay contributors:

1. Shared server-rendered chrome reads cookies:
   - `src/components/layout/site-header.tsx` calls `cookies()` for preview navigation
   - `src/components/layout/site-footer.tsx` calls `cookies()` for preview navigation
   - this can make otherwise-static public pages dynamic/no-store
2. Privacy policy is heavy:
   - latest `src/content/privacy-policy/2026-01-15.mdx` was about 49.9 KB and 1,357 lines
   - table-heavy: many `<Table>`, `<Table.Td>`, and `<Table.Th>` usages
   - rendered HTML was about 210 KB, larger than `/terms-of-service`, `/eula`, `/blog`, and `/whitepapers`
3. MDX evaluate / React tree generation still occurs for server-rendered requests even when raw source text is cached.

Useful measurement commands:

```bash
for url in \
  https://stage.querypie.ai/privacy-policy \
  https://stage.querypie.ai/privacy-policy/2026-01-15 \
  https://stage.querypie.ai/terms-of-service \
  https://stage.querypie.ai/eula \
  https://stage.querypie.ai/blog \
  https://stage.querypie.ai/whitepapers
 do
  echo "== $url"
  curl -L -o /dev/null -s -w "code=%{http_code} ttfb=%{time_starttransfer} total=%{time_total} size=%{size_download}\n" "$url"
 done
```

```bash
python3 - <<'PY'
from pathlib import Path
for p in [
  'src/content/privacy-policy/2026-01-15.mdx',
  'src/app/terms-of-service/content.mdx',
  'src/app/eula/content.mdx',
]:
    path = Path(p)
    text = path.read_text()
    print(p, 'bytes=', path.stat().st_size, 'lines=', text.count('\n') + 1, 'tables=', text.count('<Table'), 'td=', text.count('<Table.Td'), 'th=', text.count('<Table.Th'))
PY
```

## Version selector reload-like behavior

Root cause was document navigation, not MDX cache.

Old pattern:

```ts
window.location.assign(`/privacy-policy/${nextSlug}`);
```

This triggers a browser document navigation and makes version selection look like a full page reload.

Preferred pattern:

```tsx
"use client";

import { useRouter } from "next/navigation";

export function PrivacyPolicyVersionSelector({ currentSlug, slugs }: PrivacyPolicyVersionSelectorProps) {
  const router = useRouter();

  return (
    <select
      defaultValue={currentSlug}
      onChange={(event) => {
        const nextSlug = event.target.value;
        if (!nextSlug || nextSlug === currentSlug) {
          return;
        }

        router.push(`/privacy-policy/${nextSlug}`);
      }}
    >
      ...
    </select>
  );
}
```

This avoids document-level reload. The selected server-rendered RSC payload may still be fetched.

## Test pitfall

Privacy-policy structure is asserted in more than one source-structure test. When changing the selector contract, update both:

- `tests/legal-privacy-policy-preview.test.mjs`
- `tests/src/app/privacy-policy/page.test.mjs`

Both should assert:

- `import { useRouter } from "next/navigation";`
- `const router = useRouter();`
- `router.push(`/privacy-policy/${nextSlug}`)`
- absence of `window.location.assign`

Failure signature if only one test is updated:

```text
The input did not match the regular expression /window\.location\.assign\(`\/privacy-policy\/\$\{nextSlug\}`\)/
```

Recommended verification for this change:

```bash
node --test tests/legal-mdx-cache.test.mjs tests/legal-privacy-policy-preview.test.mjs tests/src/app/privacy-policy/page.test.mjs
npm run test:static-pages
node scripts/ci/assert-test-groups.mjs
git diff --check
```

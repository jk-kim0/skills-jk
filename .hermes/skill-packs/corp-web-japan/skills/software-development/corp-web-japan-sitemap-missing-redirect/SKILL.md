---
name: corp-web-japan-sitemap-missing-redirect
description: Route unmatched corp-web-japan paths based on querypie.com sitemap patterns, with special precedence for /ja/... paths to prefer real local content before redirecting externally.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, querypie.com, sitemap, redirects, nextjs, app-router]
---

# corp-web-japan sitemap-based missing redirects

Use this when:
- A user wants unknown or legacy `querypie.ai` paths to redirect to matching `querypie.com` content
- The redirect policy should be derived from `querypie.com/sitemap.xml`
- `/ja/...` requests need different precedence from generic missing-path handling

## Key findings

1. `https://www.querypie.com/sitemap.xml` is currently a single `urlset`, not a sitemap index.
2. The main content namespaces currently visible in that sitemap are:
   - `company`
   - `features`
   - `solutions`
   - `cookie-preference`
   - `eula`
   - `plans`
   - `sales-deck`
   - `search`
3. File-like sitemap paths also exist and should be handled explicitly:
   - `/rss.xml`
   - `/rss-en-blog.xml`
   - `/rss-en-learn.xml`
   - `/rss-en-webinar.xml`
   - `/rss-ja-blog.xml`
   - `/rss-ja-learn.xml`
   - `/rss-ja-webinar.xml`
   - `/rss-ko-blog.xml`
   - `/rss-ko-learn.xml`
   - `/rss-ko-webinar.xml`
4. Generic missing-path handling, `/ja/...` handling, and bare locale-root behavior should not necessarily use the same precedence.
5. User-preferred `/ja/...` precedence in later work was:
   - first check whether stripped `/path` is real `corp-web-japan` local content
   - if yes, redirect same-origin to `/path`
   - otherwise redirect to `https://www.querypie.com/ja/path`
6. Important locale-root nuance discovered later:
   - `src/app/[...missing]/page.tsx` still receives bare locale-root misses such as `/ko`
   - but `buildQueryPieContentRedirectUrl('/ko')` returns `null`
   - because the generic localized matcher only accepts `/{locale}/{contentRoot}/...`, not bare `/{locale}`
   - so `/ko` falls through the generic missing page to `notFound()` unless it is added as an exact allowlist path or handled by a dedicated locale route
   - meanwhile `/ja/**` can bypass `[...missing]` entirely when `src/app/ja/[[...path]]/route.ts` matches first

## Fast inspection workflow

Do not start with long Python loops. Use short steps.

### 1. Inspect the sitemap directly

```bash
curl -L --max-time 10 -sS https://www.querypie.com/sitemap.xml | sed -n '1,120p'
```

### 2. If you need quick grouping, use a single short parsing pass

Keep it to one sitemap file and a 10-second timeout. Avoid many network round-trips.

## Recommended implementation split

### A. Generic missing paths

Use `src/app/[...missing]/page.tsx` for page-like unknown paths.

Recommended behavior:
- if the pathname matches the allowed querypie sitemap redirect patterns, redirect to `https://www.querypie.com<same-path>`
- otherwise log `[runtime-404]` and call `notFound()`

### B. `/ja/...` paths

Use `src/app/ja/[[...path]]/route.ts` with special precedence.

Recommended behavior:
1. strip `/ja` to compute the same-origin candidate path
2. check whether that stripped path is actual local `corp-web-japan` content
3. if yes, redirect same-origin to the stripped path
4. if not, redirect to `https://www.querypie.com/ja<same-rest-of-path>`

Important lesson:
- Do not let the generic querypie sitemap matcher override `/ja/...` local-content-first behavior if the user explicitly wants local content to win.

## Helper design

### 0. Prefer local canonical recovery before querypie.com fallback for known legacy content paths

When a missing path is a historical content-detail route whose content now exists locally under a different canonical family, do not immediately fall back to `querypie.com`.

Add a small repo-local helper (for example `src/lib/corp-web-japan-legacy-redirect.ts`) and call it from `src/app/[...missing]/page.tsx` before `buildQueryPieContentRedirectUrl()`.

Proven case from `corp-web-japan`:
- incoming legacy paths:
  - `/resources/discover/whitepapers/:id/:slug`
  - `/resources/discover/white-paper/:id/:slug`
- desired behavior:
  - if local whitepaper record `<id>` exists, redirect to `/whitepapers/:id/:canonical-slug`
  - preserve the query string
  - log via the existing `[runtime-missing-redirect]` path so runtime evidence remains visible

Why this matters:
- production/runtime 404s can exist for historical resource-center whitepaper URLs even though the content is already migrated locally
- `querypie.com` may no longer have a stable working destination for one or both legacy families
- local canonical recovery is better than external fallback when the local site already owns the content

Implementation pattern:
1. parse the legacy path with narrow regexes
2. extract `id`
3. look up the local record (for example `getWhitepaperPublicationRecord(id)`)
4. if found, build `/whitepapers/${record.id}/${record.slug}`
5. in `[...missing]/page.tsx`, redirect to that local path before trying the general querypie.com allowlist helper

### 1. querypie sitemap redirect helper

Put querypie-target rules in a helper such as:
- `src/lib/querypie-content-redirect.ts`

Prefer explicit predicate-style helpers instead of one compressed conditional block.

Good structure:
- `isQueryPieContentFilePath()`
- `isQueryPieContentRootSegment()`
- `isQueryPieLocale()`
- `matchesDirectQueryPieContentPath()`
- `matchesLocalizedQueryPieContentPath()`
- `getQueryPieContentRedirectPath()`
- `buildQueryPieContentRedirectUrl()`

Also add a doc comment stating the accepted redirect patterns. The current best structure is:
1. runtime-log-validated exact paths that were checked against `https://www.querypie.com` and returned `200 OK`
2. file-like sitemap paths
3. direct content namespace paths: `/{contentRoot}/...`
4. localized namespace paths: `/{lang}/{contentRoot}/...`

This matters because users may complain that the rules are hard to read if the conditions stay buried in inline logic.

### 1.5 runtime-log-driven exact redirects

When the request is specifically to fix real production 404s seen in Vercel Runtime Logs, do not only rely on broad sitemap namespace matching.

Recommended decision rule:
1. collect the distinct 404 request paths from the requested runtime-log window
2. classify each candidate before choosing a redirect target:
   - scanner / junk path -> keep 404
   - upstream-owned path that still returns `200` on `querypie.com` -> redirect externally
   - legacy content path whose upstream path is now dead but whose local canonical content exists -> redirect same-origin to the local canonical path
   - path with no live upstream target and no local canonical target -> keep 404
3. before adding any exact-path redirect, check whether the current generic namespace rules already cover it
4. only add new exact allowlist entries for the remaining uncovered paths

Why this split matters:
- it prevents redirecting arbitrary 404 noise that does not exist on `querypie.com`
- it avoids redundant exact entries for paths already handled by namespace rules
- it preserves the more important distinction between:
  - `external exact redirects` for paths that are still truly upstream-owned
  - `local canonical redirects` for legacy content families that have already been migrated locally
- it keeps the code small and reviewable

A proven helper shape for this follow-up work was:
- `type QueryPieExactRedirectPath = ...`
- `const QUERYPIE_EXACT_REDIRECT_PATHS = [...]`
- `isQueryPieExactRedirectPath()`

In the observed Apr 25–26 runtime-log remediation, six paths returned `200` on `querypie.com`, but only two needed new exact rules because four were already covered by namespace matching.

### 1.6 content-family migration audit lesson: do not always mirror the same upstream path

A later `corp-web-japan` audit found an important failure mode: some runtime 404 paths looked like old upstream content URLs, but the best fix was **not** to redirect to the same path on `querypie.com`.

Examples discovered during the audit:
- `/resources/discover/whitepapers/15/redefining-pam-for-the-mcp-era`
- `/resources/discover/whitepapers/16/next-step-mcp-pam`
- `/resources/discover/whitepapers/17/ai-autonomous-access-control`
- `/resources/discover/whitepapers/18/uncovering-mcp-security`
- `/resources/discover/whitepapers/19/google-agentspace-vs-querypie-mcp-pam`
- `/resources/discover/white-paper/17/mcp-security-threats`
- `/resources/discover/white-paper/18/uncovering-mcp-security`
- `/resources/discover/white-paper/19/google-agentspace-vs-querypie-mcp-pam`

What was learned:
- some of these legacy paths still appear in production runtime 404 logs
- the plural `/resources/discover/whitepapers/...` family can be dead on `querypie.com`
- the singular `/resources/discover/white-paper/...` family may still resolve on `querypie.com`
- meanwhile, local canonical pages may already exist under `/whitepapers/:id/:slug`

Operational rule:
- if the runtime 404 path corresponds to a locally migrated whitepaper that already has a live local canonical detail page, prefer redirecting to the local `/whitepapers/:id/:slug` route instead of blindly copying the old upstream family path
- only keep an external redirect when the upstream destination is still the real canonical owner and there is no better local canonical page

This is especially important for migration-complete or migration-mostly-complete families, where preserving the legacy entrypoint should strengthen local ownership rather than bypass it.

### 1.7 separate broken in-content links from missing route redirects

A useful audit split from the same investigation:
- missing route redirect = incoming request path 404s and should be mapped somewhere
- broken in-content link = current repo content links directly to a dead URL and should usually be edited at the source

Concrete example found in `corp-web-japan`:
- `src/content/manuals/4-acp-api-reference.mdx` linked to `/api-docs.html`
- `https://querypie.ai/api-docs.html` returned `404`
- `https://www.querypie.com/api-docs.html` returned `200`

This should be treated as either:
- a missing redirect endpoint for `/api-docs.html`, or
- a broken internal content link to be corrected at the source,
not merely as a generic catch-all missing-path case.

Likewise, if current MDX files link to dead external URLs such as old `https://www.querypie.com/resources/discover/whitepapers/...` paths that now return `404`, prefer updating those links to the local canonical route or the surviving upstream canonical route instead of relying only on runtime catch-all behavior.

### 2. local-content helper for `/ja/...`

Put local-content precedence in a separate helper such as:
- `src/lib/corp-web-japan-internal-content-path.ts`

Do not reuse the querypie sitemap helper for this.

Recommended scope for real local content should come from the current repo implementation, not from querypie.com.

In the observed repo state, useful internal-content matches were:
- `/`
- `/blog`
- `/whitepapers`
- `/solutions/ai-crew`
- `/solutions/ai-dashi`
- local event detail hrefs from `eventItems`, e.g. `/posts/event/...`

Notably, do not blindly treat all top-level paths as local content.
For example, redirect endpoints like `/about-us` or gated pages like `/events` are different cases.

## Testing guidance

Add focused source-based tests for both helpers.

### querypie redirect helper test should verify
- known namespace strings are present
- locale-aware logic is present
- file-path exceptions are present
- exact runtime-validated paths are present when applicable
- redirect URL is built from `https://www.querypie.com`

For follow-up safety, add at least one behavioral test that actually imports the helper and verifies:
- a newly added exact path returns itself from `getQueryPieContentRedirectPath()`
- a known non-matching path returns `null`

This is useful when a source-pattern test alone might pass even though the helper logic is wired incorrectly.

### `/ja/...` precedence test should verify
- internal content helper is used first
- same-origin redirect uses `new URL(strippedPath, request.url)`
- external fallback uses `new URL(request.nextUrl.pathname, querypieOrigin)`

When behavior changes, remember to update older tests that still assert the previous precedence.
A real failure encountered during follow-up work was an old test still expecting the previous `buildQueryPieContentRedirectUrl`-first logic in `src/app/ja/[[...path]]/route.ts`.

## Verification workflow

Run:
```bash
npm test
npm run typecheck
npm run build
```

For a quick local behavior check, start a local server and test one path for each branch:

### querypie redirect case
```bash
curl -I http://127.0.0.1:3014/features/demo/use-cases/999/test
```
Expected:
- `307`
- `Location: https://www.querypie.com/features/demo/use-cases/999/test`

### true unknown path case
```bash
curl -I http://127.0.0.1:3014/__totally-unknown-route
```
Expected:
- `404`

### `/ja/...` local-content-first case
Examples to verify based on current repo:
- `/ja/blog` -> `/blog`
- `/ja/solutions/ai-crew` -> `/solutions/ai-crew`
- `/ja/posts/event/1` -> `/posts/event/1`
- `/ja/company/about-us` -> `https://www.querypie.com/ja/company/about-us`

## Pitfalls

- Do not treat `querypie.com` sitemap coverage as equivalent to local `corp-web-japan` content coverage.
- Do not assume `/ja/...` should always redirect externally; the user may want local-content-first behavior.
- Do not hide redirect conditions in one opaque conditional block. If the user says the code does not make the rules obvious, refactor immediately.
- When a follow-up change lands on an open PR, use a fresh worktree on the existing PR branch and push back to that same PR branch.
- If the PR was merged and the branch deleted, continue from fresh `origin/main` on a new follow-up branch/PR instead.

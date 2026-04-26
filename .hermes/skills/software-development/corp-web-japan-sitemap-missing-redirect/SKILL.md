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
4. Generic missing-path handling and `/ja/...` handling should not necessarily use the same precedence.
5. User-preferred `/ja/...` precedence in later work was:
   - first check whether stripped `/path` is real `corp-web-japan` local content
   - if yes, redirect same-origin to `/path`
   - otherwise redirect to `https://www.querypie.com/ja/path`

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
2. for each candidate path, check `https://www.querypie.com<same-path>` directly
3. only consider paths that return `200 OK`
4. before adding any exact-path redirect, check whether the current generic namespace rules already cover it
5. only add new exact allowlist entries for the remaining uncovered paths

Why this split matters:
- it prevents redirecting arbitrary 404 noise that does not exist on `querypie.com`
- it avoids redundant exact entries for paths already handled by namespace rules
- it keeps the code small and reviewable

A proven helper shape for this follow-up work was:
- `type QueryPieExactRedirectPath = ...`
- `const QUERYPIE_EXACT_REDIRECT_PATHS = [...]`
- `isQueryPieExactRedirectPath()`

In the observed Apr 25–26 runtime-log remediation, six paths returned `200` on `querypie.com`, but only two needed new exact rules because four were already covered by namespace matching.

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

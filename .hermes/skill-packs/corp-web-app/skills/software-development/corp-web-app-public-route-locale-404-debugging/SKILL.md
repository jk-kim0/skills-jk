---
name: corp-web-app-public-route-locale-404-debugging
description: Diagnose corp-web-app locale-prefixed public-route 404s by separating true missing resources from locale/route mismatches, including /public/** locale redirects and legacy share/redirect paths such as /:locale/chat/publication/**.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-app, nextjs, app-router, middleware, locale, public-files, 404, debugging]
---

# corp-web-app public-route locale 404 debugging

Use this when a public/legacy route under `https://www.querypie.com/**` appears to 404 only with a locale prefix, non-English locale environment, or a locale-specific legal/static rewrite. Common cases include:
- `/public/**` file URLs that become `/:locale/public/**`
- legacy/share redirect endpoints such as `/:locale/chat/publication/**`
- legal/static shortcuts such as `/terms-of-service`, `/en/terms-of-service`, `/privacy-policy`, or `/:locale/privacy-policy` whose `next.config.ts` rewrite destination points at a missing locale-shaped content route

The class-level question is: is the resource actually missing, did locale-aware routing move the request into a path shape that no handler owns, or does a config rewrite point to the wrong localized destination?

## Core lesson

A `404` on a `/public/**` file URL may be caused by locale middleware, not by a missing file.

In `corp-web-app` the key pattern is:
- `/public/**` is served by `src/app/public/[...pathname]/route.ts`
- middleware can redirect locale-less paths to `/:locale/...`
- `/:locale/public/**` is **not** handled by the public file route
- locale-prefixed `/public` requests therefore fall into `src/app/[...slug]/page.tsx` / `src/app/dynamic-page.tsx` and return 404

So always distinguish these two cases:
1. file genuinely missing from the backing content repo/storage
2. file exists, but locale redirect rewrites the URL into an unsupported route

## App Router private-folder underscore variant

Use this variant when a newly added App Router page appears to exist in source but returns 404 on Vercel/preview, especially for paths shaped like:
- `/_translations/<family>`
- `/:locale/_translations/<family>`
- any URL segment that intentionally starts with `_`

Next.js App Router treats folders whose names start with `_` as private folders. A folder such as `src/app/_translations/...` or `src/app/[locale]/_translations/...` is not considered by the routing system, even if it contains `page.tsx` or `route.ts`. The source module can still be imported by unit tests, so component-level tests may pass while the real deployed URL 404s.

Root-cause signature:
- Preview/deployed URL returns a normal site 404 in browser and via `curl`
- source contains `src/app/.../_segment/.../page.tsx`
- unit tests import the page module directly and pass
- no App Router route is generated because the segment is private

Correct route-folder fix:
- rename the route segment folder from `_segment` to `%5Fsegment`
- for example:
  - `src/app/_translations/blog/page.tsx` -> `src/app/%5Ftranslations/blog/page.tsx`
  - `src/app/[locale]/_translations/blog/page.tsx` -> `src/app/[locale]/%5Ftranslations/blog/page.tsx`
- keep implementation-only helper folders private as `_components`, `_lib`, etc.; only URL-owning underscore segments need `%5F...`

Investigation commands:
```bash
for path in /_translations/blog /en/_translations/blog /ja/_translations/blog /ko/_translations/blog; do
  url="https://<preview-host>$path"
  printf '\n== %s ==\n' "$url"
  curl -sS -o /tmp/route-body.html -w 'HTTP %{http_code} final:%{url_effective}\n' "$url"
done

git ls-tree -r --name-only HEAD src/app | grep '_translations\|%5Ftranslations' || true
```

Testing pitfall:
- A test like `import Page from 'src/app/_translations/blog/page'` verifies the component module but not route registration. Add or update source-level tests/checks to assert the URL-owning folder uses `%5F...`, or verify against a real Next/Vercel deployment when the task is route availability.

## Legal/static rewrite variant

Use this variant when reported 404 paths include legal/static shortcuts such as:
- `/terms-of-service`
- `/en/terms-of-service`
- `/privacy-policy`
- `/:locale/privacy-policy`
- `/eula`
- `/:locale/eula`

Known diagnostic patterns from `corp-web-app`:
- public shortcut paths may be implemented in `next.config.ts` `rewrites`, App Router route handlers, or the catch-all dynamic page plus middleware rewrites
- a rewrite destination can be locale-shaped differently from the public shortcut
- for example, `/terms-of-service` and `/en/terms-of-service` returned 404 when both rewrote to `/terms-of-service-en`, while `/en/terms-of-service-en` itself returned 200
- `/ko/terms-of-service` and `/ja/terms-of-service` worked because their destinations were already locale-prefixed: `/ko/terms-of-service-ko` and `/ja/terms-of-service-ja`
- `/eula` returned 404 while `/en/eula`, `/ko/eula`, and `/ja/eula` returned 200; this was not missing content, but a default-English middleware routing gap where `/eula` needed to be included in `DEFAULT_LOCALE_REWRITE_PATHS` so it internally rewrites to `/en/eula` for English/default users and still redirects to `/:locale/eula` for non-English users

Reproduction commands:
```bash
for host in stage.querypie.com www.querypie.com; do
  for path in \
    /terms-of-service /en/terms-of-service /ko/terms-of-service /ja/terms-of-service \
    /privacy-policy /en/privacy-policy /ko/privacy-policy /ja/privacy-policy \
    /terms-of-service-en /en/terms-of-service-en \
    /eula /en/eula /ko/eula /ja/eula; do
    echo "--- https://$host$path"
    curl -sS -o /dev/null -D - --max-redirs 0 --connect-timeout 10 --max-time 20 "https://$host$path" |
      awk 'BEGIN{IGNORECASE=1} /^HTTP\// || /^location:/ || /^x-matched-path:/ || /^x-vercel-id:/ {print}'
  done
done
```

Investigation workflow:
1. Test both requested public shortcuts and their configured rewrite/dynamic destinations literally on stage and production.
2. Inspect `next.config.ts`, `src/middleware.ts`, and `src/app/[...slug]/page.tsx` before adding route handlers.
3. If only English/default shortcuts fail, test whether the real working content route needs an explicit `/en/...` prefix; compare `/foo` against `/en/foo`, `/ko/foo`, and `/ja/foo`.
4. If the user prefers middleware over `next.config.ts`, prefer adding the unprefixed path to `DEFAULT_LOCALE_REWRITE_PATHS` when the locale-prefixed content routes already work.
5. Add a middleware regression test for the default-English internal rewrite and a companion non-English redirect test.
6. Keep the fix narrow: change the broken rewrite/middleware mapping rather than adding duplicate route handlers unless routing evidence shows no existing content route can serve the page.

Expected minimal config-level fix shape:
```ts
{
  source: '/terms-of-service',
  destination: '/en/terms-of-service-en',
},
{
  source: '/en/terms-of-service',
  destination: '/en/terms-of-service-en',
},
```

App Router route-handler replacement option:
- If the user asks to move legal shortcuts out of `next.config.ts`, implement localized handlers under `src/app/[locale]/.../route.ts` rather than keeping rewrites.
- Add the unprefixed legal shortcuts to `DEFAULT_LOCALE_REWRITE_PATHS` so `/terms-of-service` and `/privacy-policy` internally reach `/en/...` route handlers for English/default users while non-English users still redirect to `/:locale/...`.
- Put shared locale-to-content mapping in a helper such as `src/app/[locale]/_legal/redirect.ts` and export `HEAD = GET` from each route handler.
- If redirect destinations do not have dedicated endpoint files under `src/app/[locale]/`, add a code comment explaining that they are corp-web-contents-backed dynamic content paths resolved by the catch-all page, not missing route code.
- See `references/legal-page-route-handlers.md` for the concrete route-handler pattern, tests, and verification commands.

## Chat publication redirect variant

Use this variant when a reported 404 path looks like:
- `/:locale/chat/publication/<uuid>/<slug>`

Known current behavior from `corp-web-app` latest main:
- `src/app/chat/publication/[[...path]]/route.ts` handles only non-locale `/chat/publication/**`
- that handler returns `307` to `https://app.querypie.com${pathname}`
- `https://app.querypie.com/chat/publication/**` can return `200`
- `https://app.querypie.com/:locale/chat/publication/**` can redirect to app-side 404/error
- `/:locale/chat/publication/**` in corp-web-app has no matching app route, so it falls through to normal page/catch-all handling and 404s

Reproduction commands:
```bash
for url in \
  'https://www.querypie.com/ko/chat/publication/<uuid>/<slug>' \
  'https://www.querypie.com/chat/publication/<uuid>/<slug>' \
  'https://app.querypie.com/ko/chat/publication/<uuid>/<slug>' \
  'https://app.querypie.com/chat/publication/<uuid>/<slug>'; do
  echo "--- $url"
  curl -sS -o /dev/null -D - --max-redirs 0 "$url" |
    awk 'BEGIN{IGNORECASE=1} /^HTTP\// || /^location:/ || /^server:/ || /^x-vercel-id:/ {print}'
done
```

Root-cause signature:
- `www.querypie.com/chat/publication/**` -> `307 Location: https://app.querypie.com/chat/publication/**`
- `www.querypie.com/:locale/chat/publication/**` -> `404`
- `app.querypie.com/chat/publication/**` -> `200`
- `app.querypie.com/:locale/chat/publication/**` -> app-side 404/error redirect

Recommended fix direction:
- Strip the locale prefix in the upstream destination; do **not** forward `/ko` or `/ja` to `app.querypie.com`.
- If the user allows `next.config.ts`, an explicit redirect rule is the smallest config-level fix.
- If the user wants App Router ownership and/or wants to remove the old unprefixed handler, use a localized route handler plus middleware default-locale rewrite instead.

Config-level option:
```ts
{
  source: '/:locale(en|ko|ja)/chat/publication/:path*',
  destination: 'https://app.querypie.com/chat/publication/:path*',
  permanent: false,
}
```

App Router consolidation option:
1. Add `src/app/[locale]/chat/publication/[[...path]]/route.ts`.
2. In that handler, match only `^/(?:en|ko|ja)(/chat/publication(?:/.*)?/?$)` and redirect to `https://app.querypie.com${match[1]}` with status `307`.
3. Export `HEAD = GET` so HEAD checks also redirect.
4. Add `/chat/publication` to `DEFAULT_LOCALE_REWRITE_PREFIXES` in `src/middleware.ts`.
   - This lets unprefixed English `/chat/publication/**` internally rewrite to `/en/chat/publication/**` and reach the localized route handler.
   - Non-English users can still be redirected by middleware to `/:locale/chat/publication/**`, then handled by the same localized route handler.
5. Remove `src/app/chat/publication/[[...path]]/route.ts` once the middleware rewrite is covered by tests.

Expected result:
- `/ko/chat/publication/<uuid>/<slug>` returns a normal 30x, typically `307`, to `https://app.querypie.com/chat/publication/<uuid>/<slug>`.

Pitfall:
- Do not implement `destination: 'https://app.querypie.com/:locale/chat/publication/:path*'`; app.querypie.com does not treat the locale-prefixed version as the working content URL.
- Do not remove the unprefixed route handler unless `/chat/publication` is explicitly covered by middleware default-locale rewrite tests; otherwise English/default unprefixed share URLs can regress to 404.

## Investigation workflow

### 1. Check the exact requested URL literally

Do not normalize or “fix” the URL before testing.

Use curl headers first:
```bash
curl -I -L --max-redirs 5 'https://www.querypie.com/public/...'
curl -I -L --max-redirs 5 'https://www.querypie.com/ko/public/...'
```

If the originally reported URL includes a locale prefix such as `/ko/public/...`, test that exact literal path too instead of mentally normalizing it back to `/public/...`.

Interpretation:
- `200` on `/public/...` but `404` on `/ko/public/...` strongly indicates a locale-routing bug
- `404` on both suggests a true missing-file or storage problem

### 2. Reproduce locale-driven redirect behavior explicitly

Test with browser locale headers and locale cookies:
```bash
curl -I -H 'Accept-Language: ko' 'https://www.querypie.com/public/...'
curl -I -b 'user-selected-locale=ko' 'https://www.querypie.com/public/...'
```

Repo-specific note:
- the persisted user-choice cookie key is `user-selected-locale`, not `current_locale`
- `current_locale` is a runtime state cookie set by the app and is not the right knob for reproducing the middleware's locale-selection behavior
- in practice, `Accept-Language: ko` has been the most reliable way to trigger the problematic `307 -> /ko/public/...` redirect during debugging

Important finding from this repo:
- `Accept-Language: ko` can produce `307 Location: /ko/public/...`
- that redirected URL then returns `404`

This proves the bug can be user-locale dependent even when the raw non-locale URL works.

### 3. Inspect response headers for matched route evidence

Check `x-matched-path` in the response headers.

Expected patterns:
- working file request: `x-matched-path: /public/[...pathname]`
- broken locale-prefixed request: `x-matched-path: /[...slug]`

This is the fastest way to prove whether the request hit the file-serving route or the catch-all page route.

### 4. Verify the actual source file exists in sibling repos

Search both likely source repos first:
- `../corp-web-app`
- `../corp-web-contents`

Use file search, not assumptions:
```bash
search for `QueryPie_AIP_Intro_JP.pdf`
```

For introduction decks, a common real source is:
- `../corp-web-contents/public/downloads/intro-decks/<filename>.pdf`

If the file exists there, a 404 on the site is more likely a routing/deploy/serve issue than a missing source artifact.

### 5. Check where the link is authored

Search content for the exact URL string and determine whether the broken link is:
- hardcoded in MDX/content frontmatter
- opened after a form submit via `afterSubmitOpenPageHref`
- generated by client-side locale-aware link helpers

For introduction-deck downloads in `corp-web-contents`, one real pattern is:
- `pages/features/documentation/aip-introduction-download/ja/content.mdx`
- frontmatter `afterSubmitOpenPageHref: "https://www.querypie.com/public/downloads/intro-decks/QueryPie_AIP_Intro_JP.pdf"`

### 6. Read the middleware and route implementation together

The important files are:
- `src/middleware.ts`
- `src/app/public/[...pathname]/route.ts`
- `src/app/[...slug]/page.tsx`
- `src/app/dynamic-page.tsx`

Critical repo-specific behavior:
- middleware redirects locale-less paths to `/${userLocale}${pathname}` when locale is not EN
- public files are only handled under `/public/**`
- `dynamic-page.tsx` intentionally rejects `slug[0] === 'public'`, but that only helps for non-locale `/public/...`
- locale-prefixed `/ko/public/...` still enters the catch-all slug route and 404s

## Known root cause signature

If you see all of these together, the root cause is effectively confirmed:
- `/public/<file>` -> `200`
- `/ko/public/<file>` -> `404`
- `Accept-Language: ko` on `/public/<file>` -> `307 Location: /ko/public/<file>`
- 404 response has `x-matched-path: /[...slug]`
- 200 response has `x-matched-path: /public/[...pathname]`

## Recommended conclusions to report

Be explicit that this is **not** primarily a missing-PDF issue when the above signature is present.

State it as:
- the file exists
- the locale middleware rewrites `/public/**` to `/:locale/public/**`
- the app has no locale-prefixed public-file route
- the redirected request falls into the catch-all page route and returns 404

## Fix directions to consider later

Do not implement until requested, but the usual minimal fixes are:
1. exclude `/public/**` from locale redirect logic in middleware, or
2. add a rewrite/redirect from `/:locale/public/**` back to `/public/**`

In this repo, the smallest proven fix was:
- keep the existing locale redirect behavior for normal content routes
- add a narrow middleware exception for `/public` and `/public/**`
- leave `src/app/public/[...pathname]/route.ts` unchanged

Prefer the smallest fix that preserves existing public file serving behavior.

## Implementation notes when asked to patch it

Use TDD for middleware-related changes:
1. for `/public/**`, add a regression test showing `/public/...` with `Accept-Language: ko` does **not** redirect to `/ko/public/...`
2. add a companion test showing a normal route like `/plans` still redirects to `/ko/plans`
3. optionally also cover `/public` itself, since the middleware condition usually needs to special-case both `/public` and `/public/**`
4. for `/chat/publication/**`, add middleware tests for:
   - English/default unprefixed `/chat/publication/**` rewrites internally to `/en/chat/publication/**`
   - non-English unprefixed `/chat/publication/**` redirects to `/:locale/chat/publication/**`
5. add route-handler tests for `/:locale/chat/publication/**` returning `307` to the non-locale app URL and for `HEAD = GET`
6. only then patch `src/middleware.ts` and the App Router route handler(s)

A practical worktree/testing note from this repo:
- a fresh git worktree may not have its own `node_modules`
- focused route/middleware Vitest commands may still pass by resolving dependencies from the root checkout
- broader groups such as `npm run test:routing` can fail with PostCSS/config-time module resolution errors like `Cannot find module '@tailwindcss/postcss'` when run from a fresh worktree without local `node_modules`; do not misreport those as product regressions if the directly affected tests pass
- a workable repo-local workaround, when full local verification is actually needed, is to symlink the worktree's `node_modules` to the root repo's `node_modules` instead of doing a full new install
- pitfall: a failed or partial Vitest run in a fresh worktree can create a real `node_modules/.vite/...` cache directory; `ln -s ../../node_modules node_modules` will then fail because `node_modules` already exists as a directory. Check with `test -L node_modules` / `ls -ld node_modules`, remove only that cache-only worktree-local directory if safe (`rm -rf node_modules` when `git status` is clean except intended files and inspection shows only `.vite` cache), then recreate the symlink with the correct relative path or use an absolute symlink.

## Deployment verification

After the PR is merged and the user asks to verify production/stage rollout, test the exact URL literally with `curl` headers and `--max-redirs 0`.

Use bounded polling when deployment may still be rolling out:
```bash
url='https://www.querypie.com/ko/chat/publication/<uuid>/<slug>'
expected='https://app.querypie.com/chat/publication/<uuid>/<slug>'
for i in $(seq 1 11); do
  echo "--- attempt $i $(date -Is)"
  curl --connect-timeout 10 --max-time 25 -sS -o /dev/null -D - --max-redirs 0 "$url" |
    awk 'BEGIN{IGNORECASE=1} /^HTTP\// || /^location:/ || /^x-vercel-id:/ {print}'
  # stop manually when status is 307 and Location equals $expected
  sleep 60
done
```

If automating with Python/subprocess, include `--connect-timeout` and `--max-time`; a watcher without curl timeouts can hang on the first attempt and fail to produce minute-by-minute output.

Success criteria:
- status `HTTP/2 307` (or the expected 30x for that route)
- `Location: https://app.querypie.com/chat/publication/<uuid>/<slug>`
- include `x-vercel-id` in the report for deploy-edge evidence

If the expected redirect still is not live after the user-specified window (for example 10 minutes), create a follow-up debugging PR rather than continuing passive polling.

## Pitfalls

- Assuming the PDF/resource is missing just because the browser showed 404 once
- For legacy redirect endpoints, preserving the locale prefix in the upstream/app destination even after evidence shows only the non-locale upstream path works
- Testing only the non-locale URL and missing the locale-triggered redirect behavior
- Looking only in `corp-web-app` and forgetting that the source file may live in `corp-web-contents`
- Treating `/ko/public/**` as if it were covered by the same route as `/public/**`
- Ignoring `x-matched-path`, which quickly reveals whether the wrong route handled the request

## Done criteria

You have enough evidence when you can show:
- exact HTTP behavior for both `/public/**` and `/:locale/public/**`
- whether locale headers/cookies trigger the redirect
- which route actually handled each request
- whether the source file exists in sibling repos
- where the broken URL was authored

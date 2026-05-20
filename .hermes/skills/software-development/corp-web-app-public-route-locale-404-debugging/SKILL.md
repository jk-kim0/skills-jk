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

Use this when a public/legacy route under `https://www.querypie.com/**` appears to 404 only with a locale prefix or non-English locale environment. Common cases include:
- `/public/**` file URLs that become `/:locale/public/**`
- legacy/share redirect endpoints such as `/chat/publication/**` that work without a locale prefix but 404 as `/:locale/chat/publication/**`

The class-level question is: is the resource actually missing, or did locale-aware routing move the request into a path shape that no handler owns?

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
- Add an explicit Next.js redirect for locale-prefixed chat publication paths.
- Strip the locale prefix in the destination; do **not** forward `/ko` or `/ja` to `app.querypie.com`.

Example `next.config.ts` rule:
```ts
{
  source: '/:locale(en|ko|ja)/chat/publication/:path*',
  destination: 'https://app.querypie.com/chat/publication/:path*',
  permanent: false,
}
```

Expected result:
- `/ko/chat/publication/<uuid>/<slug>` returns a normal 30x, typically `307`, to `https://app.querypie.com/chat/publication/<uuid>/<slug>`.

Pitfall:
- Do not implement `destination: 'https://app.querypie.com/:locale/chat/publication/:path*'`; app.querypie.com does not treat the locale-prefixed version as the working content URL.

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

Use TDD for the middleware change:
1. add a regression test showing `/public/...` with `Accept-Language: ko` does **not** redirect to `/ko/public/...`
2. add a companion test showing a normal route like `/plans` still redirects to `/ko/plans`
3. optionally also cover `/public` itself, since the middleware condition usually needs to special-case both `/public` and `/public/**`
4. only then patch `src/middleware.ts`

A practical worktree/testing note from this repo:
- a fresh git worktree may not have its own `node_modules`
- `npm run test:run` can fail with `sh: vitest: command not found` or config-time module resolution errors even if the root checkout already has dependencies installed
- a workable repo-local workaround is to symlink the worktree's `node_modules` to the root repo's `node_modules` before running the focused Vitest command, instead of doing a full new install

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

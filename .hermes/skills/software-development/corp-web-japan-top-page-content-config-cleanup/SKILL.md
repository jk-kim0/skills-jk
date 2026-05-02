---
name: corp-web-japan-top-page-content-config-cleanup
description: Finish inlining remaining top-page content/config into route-local files in corp-web-japan, including deleting src/content/top-page.ts safely.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, top-page, route-local, static-pages, cleanup, nextjs]
---

# corp-web-japan top-page content config cleanup

Use this when follow-up work asks to finish the top-page refactor so `src/content/top-page.ts` can be removed entirely.

## When this applies

Typical request shape:
- remove the remaining unused or partially used exports from `src/content/top-page.ts`
- move final page-specific text/metadata/CTA URLs into `src/app/page.tsx`
- keep top-page authoring route-local and easy to read

## Key lesson

After the earlier top-page section refactors, `src/content/top-page.ts` may still contain a mix of:
- truly shared constants
- stale unused exports like `topPageHeader`
- route-local values that should already live in `src/app/page.tsx`

Do not stop after removing the obvious unused export. Check all remaining imports first.

## Required checks

1. Search all live references before deleting the file.

Use searches for:
- `@/content/top-page`
- `topPageMetadata`
- `topPageFloatingCtaUrl`
- `topPageHeroContactUrl`
- `topPageDownloadUrl`
- `topPageFinalDemoUrl`
- `topPageFinalConsultUrl`
- `topPageHeader`

Important practical finding:
- `src/app/not-found.tsx` may still import `topPageFloatingCtaUrl` even after `page.tsx` is mostly route-local.
- If you only update `page.tsx`, deleting `src/content/top-page.ts` will break `not-found.tsx`.

2. Inline route-local values directly into `src/app/page.tsx`.

Typical end state:
- `metadata` object literals live directly in `src/app/page.tsx`
- page-specific CTA URLs are defined as route-local constants inside `HomePage()` or as nearby top-level constants in the same file
- top-page copy stays visible in `page.tsx`, not hidden behind a content-config file

3. Update any non-top-page consumers.

Known example:
- `src/app/not-found.tsx`
  - replace imported `topPageFloatingCtaUrl` with the literal `"/contact-us"`
  - remove the `@/content/top-page` import

4. Remove `src/content/top-page.ts` completely once all imports are gone.

## Test expectations

Run targeted tests that reflect source-structure assumptions.

Minimum useful set:
```bash
node --test tests/top-page-structure.test.mjs tests/launch-readiness-coverage.test.mjs tests/not-found-page.test.mjs
```

Why these matter:
- `top-page-structure` checks the route-local top-page authoring shape
- `launch-readiness-coverage` checks CTA wiring and metadata-related expectations
- `not-found-page` catches lingering dependency on `src/content/top-page.ts`

## Existing helpful test behavior

`tests/not-found-page.test.mjs` already tolerates both states:
- `src/content/top-page.ts` exists
- `src/content/top-page.ts` does not exist

So if you fully remove the file, make sure the implementation matches the test's no-file branch:
- `FloatingConversionCta href="/contact-us"`

## Pitfalls

- removing only `topPageHeader` and forgetting `topPageMetadata`
- moving final CTA URLs out of `src/content/top-page.ts` but leaving `topPageDownloadUrl` and `topPageHeroContactUrl` half-shared without checking intent
- deleting `src/content/top-page.ts` before updating `src/app/not-found.tsx`
- updating `page.tsx` but forgetting tests that explicitly look for `src/content/top-page.ts`

## Done criteria

- `search` for `@/content/top-page` returns no live app imports
- `src/content/top-page.ts` is deleted
- top-page metadata and page-specific CTA URLs are route-local in `src/app/page.tsx`
- `src/app/not-found.tsx` no longer depends on the deleted file
- targeted tests pass

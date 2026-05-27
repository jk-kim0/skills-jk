# Home `/[locale]/t` preview authoring correction

Session pattern from corp-web-app PR #697.

## Problem

A home route-local PR initially added `src/app/[locale]/t/page.tsx` so Preview Deployments could render:

- `/en/t/`
- `/ja/t/`
- `/ko/t/`

However, the preview route imported the real authored modules from `src/app/page.en.tsx`, `src/app/page.ja.tsx`, and `src/app/page.ko.tsx`. The user corrected this: for preview review, the authored locale files themselves belong under the preview route directory.

## Correct structure

For a home-page preview route:

```text
src/app/[locale]/t/page.tsx        # thin locale dispatcher
src/app/[locale]/t/page.en.tsx     # EN authored page
src/app/[locale]/t/page.ja.tsx     # JA authored page
src/app/[locale]/t/page.ko.tsx     # KO authored page
src/app/page.tsx                   # thin public/default wrapper importing from /[locale]/t
src/app/en/page.tsx                # thin wrapper importing from /[locale]/t
src/app/ko/page.tsx                # thin wrapper importing from /[locale]/t
```

If `/ja` must continue redirecting before public rollout, keep `src/app/ja/route.ts` unchanged and review JA via `/ja/t/`.

## Checklist

1. Move, do not copy, the authored locale files into `src/app/[locale]/t/`.
2. Update thin wrappers to import from `src/app/[locale]/t/page.{locale}`.
3. Update `src/app/[locale]/t/page.tsx` to import sibling `./page.en`, `./page.ja`, `./page.ko`.
4. Update tests to import the new canonical authoring location.
5. Update README/provenance and PR body to list `/en/t/`, `/ja/t/`, `/ko/t/` as review paths and `src/app/[locale]/t/page.{locale}.tsx` as implementation files.
6. Grep for stale imports:
   - `src/app/page.en`
   - `src/app/page.ja`
   - `src/app/page.ko`
   - `../page.en`
   - `../page.ja`
   - `../page.ko`
7. Run the targeted route-local test and `git diff --check`, then push the existing PR branch with `--force-with-lease` after rebase.

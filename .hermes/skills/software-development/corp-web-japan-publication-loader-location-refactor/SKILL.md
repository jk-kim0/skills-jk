---
name: corp-web-japan-publication-loader-location-refactor
description: Move publication loader and list-item derivation modules from src/content/publications into src/lib/publications in corp-web-japan, then realign imports, docs, and path-sensitive tests.
version: 1.0.1
author: Hermes Agent
license: MIT
---

# corp-web-japan publication loader location refactor

Use this when `corp-web-japan` contains non-UI publication loader/adaptor code under `src/content/publications/**` and the goal is to align it with the repository convention that shared non-UI logic belongs under `src/lib/publications/**`.

## Why this skill exists

In this repo, code-location guidance prefers:
- source content under `src/content/**`
- shared non-UI publication logic under `src/lib/publications/**`

A location-only refactor is not just file moves. Multiple route files, helper modules, docs, and tests assert exact import paths and file locations.

## When to use

Use this skill when the task says things like:
- move `src/content/publications/*.ts` into `src/lib/publications`
- make sure no TypeScript code remains under `src/content/publications`
- update docs after publication loader relocation
- refactor publication-record modules without changing behavior

## Safe workflow

1. Start from latest `origin/main` in a fresh worktree.
- In `corp-web-japan`, use the latest-main worktree flow.
- Do not edit a dirty root checkout.

2. Inventory the scope before moving files.
- List `src/content/publications/*.ts`.
- Search the repo for both:
  - `@/content/publications`
  - `src/content/publications`
- Expect hits in:
  - route files under `src/app/**`
  - helpers under `src/lib/**`
  - resource aggregators under `src/content/resources*.ts`
  - project docs such as `README.md` and `docs/code-location-conventions.md`
  - tests that read exact source paths

3. Move the modules into `src/lib/publications/`.
- Preserve filenames when moving.
- Keep the change behavior-preserving; this is primarily a location refactor.

4. Update imports everywhere.
- Replace `@/content/publications/...` with `@/lib/publications/...`.
- Re-check for remaining references after the move.

5. Keep `src/content/**` content-focused.
- If `src/content/publications` becomes empty, remove the directory.
- Goal: no `.ts` code remains under `src/content/publications`.

## Required doc alignment

Update docs in the same PR so the repo guidance matches reality.

### README.md
- Remove any directory description that presents `src/content/publications/` as the loader location.
- Update the `src/lib/` description so it explicitly covers publication loaders / list-item derivation if needed.

### docs/code-location-conventions.md
- If it still lists `src/content/publications/*` as current mismatches or examples, update the wording to reflect that publication loader/adaptor code should live under `src/lib/publications/**`.

## Required test alignment

Important finding: several repo tests read source files by exact path and will fail after a pure file move even when runtime code is correct.

After moving publication loaders, check tests for hardcoded path assertions such as:
- `readSource("src/content/publications/...`)`
- `existsSync(new URL("../src/content/publications/...`))`
- regex expectations that import from `@/content/publications/...`

Typical affected tests include publication routing/preview tests for:
- ACP demo
- AIP demo
- events
- use-cases
- news
- whitepapers

Update those tests to the new `src/lib/publications/**` paths.

## Verification

Run:
```bash
npm run test:ci
```

This is the key verification because it catches:
- stale import paths
- stale path-based tests
- doc/code drift surfaced by repo checks

Also run:
```bash
git diff --check
```

## Practical lessons

- In this repo, a location-only refactor often requires test updates because tests inspect exact source paths, not only behavior.
- `README.md` may lag behind `docs/code-location-conventions.md`; update both in the same change.
- If the move empties `src/content/publications`, remove the directory so the result is unambiguous.

## Done criteria

- publication loader/list-item derivation modules live under `src/lib/publications/**`
- no `.ts` files remain under `src/content/publications`
- all imports are updated
- docs are aligned
- path-sensitive tests are updated
- `npm run test:ci` passes

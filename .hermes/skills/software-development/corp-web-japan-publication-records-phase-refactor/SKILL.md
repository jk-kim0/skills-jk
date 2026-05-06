---
name: corp-web-japan-publication-records-phase-refactor
description: Safely refactor duplicated MDX publication repository modules in corp-web-japan in small PRs, starting with the most identical records files and using test-first architecture checks.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, publications, mdx, refactor, repository, tdd]
    related_skills: [corp-web-japan-origin-main-worktree-safety, github-pr-workflow, test-driven-development, writing-plans]
---

# corp-web-japan publication-records phased refactor

Use this when the user asks to reduce duplication in `src/lib/publications/**`, especially the repeated `*-publication-records.ts` modules, and wants the work split into a small safe PR rather than a broad architecture rewrite.

## When this skill applies

- the repo is `corp-web-japan`
- the target is publication loader/repository duplication under `src/lib/publications/**`
- the user wants a real implementation PR, not only analysis
- the previous PR on a related topic may already be merged, so the new work must start from a fresh branch/worktree on latest `origin/main`
- the user values a design memo plus a narrowly scoped first-pass refactor

## Key lesson

Do **not** start by trying to unify every publication module or by renaming everything to `records.ts` / `get-post.ts` in one pass.

The safe first pass is:
1. identify the strongest duplication cluster
2. add a failing architecture regression test
3. extract one shared helper for that cluster only
4. keep the public API and file paths stable
5. document the later follow-up path in a memo

This produced a small, reviewable PR and avoided entangling path renames, post-loader differences, and whitepaper/news special cases.

## Proven first-pass target

Start with these three record modules first:
- `src/lib/publications/use-case-publication-records.ts`
- `src/lib/publications/aip-demo-publication-records.ts`
- `src/lib/publications/acp-demo-publication-records.ts`

Why these first:
- nearly identical frontmatter shape
- same hidden filtering and redirect-aware list-link behavior
- same cache/list/lookup structure
- differ mainly by content root, category, badge, and error label

Do **not** include these in phase 1 unless the user explicitly expands scope:
- `get-*-publication-post.ts` loader unification
- blog/news/whitepaper/event record migration
- path restructuring to category-local directories
- `records.ts` / `get-post.ts` renames

## Recommended branch/worktree workflow

Follow `corp-web-japan-origin-main-worktree-safety`.

Important additional rule learned here:
- if the prior PR on a nearby topic was already merged, create a **separate** fresh branch/worktree from latest `origin/main`
- do not continue from the old branch even if the code area is related

Typical sequence:
```bash
git fetch origin --prune
git worktree add .worktrees/refactor-publication-records-repo -b refactor/publication-records-repo origin/main
```

Verify the new worktree before editing.

## TDD workflow that worked well

### 1. Write a failing architecture test first

Add a dedicated architecture regression test under:
- `tests/src/lib/publications/records-repository-architecture.test.mjs`

Assert that:
- a shared helper file exists, for example `src/lib/publications/create-standard-publication-records-repository.ts`
- the three target record modules import that helper
- the three wrappers no longer define their own `load...Records`, `create...Cache`, or `get...Cache` functions

Example expectations to assert in the wrapper files:
- contains `createStandardPublicationRecordsRepository`
- contains import from `@/lib/publications/create-standard-publication-records-repository`
- does **not** contain `function load...PublicationRecords`
- does **not** contain `function create...PublicationCache`
- does **not** contain `function get...PublicationCache`

Run only this test first and verify it fails.

### 2. Extract the shared helper

Create:
- `src/lib/publications/create-standard-publication-records-repository.ts`

The helper should own:
- frontmatter block parsing with YAML
- source file enumeration from a content root
- source-path attachment
- descending numeric-id sort
- hidden-record filtering for list pages
- redirect-aware href generation for list cards
- precomputed `records` and `listItems`
- functions for `listParams`, `listIds`, and `getRecord`

Keep the helper narrow. Do not cram whitepaper/news special behavior into it on phase 1.

## Wrapper shape for phase 1

Each target file should keep only:
- the category-specific frontmatter type
- the category-specific `normalize...Frontmatter()` function
- repository instantiation config:
  - `contentRoot`
  - `category`
  - `badge`
- the existing exported API surface expected by routes/tests:
  - `...PublicationRecords`
  - `list...PublicationItems()`
  - `list...PublicationParams()`
  - `list...PublicationIds()`
  - `get...PublicationRecord()`

This preserves route imports and keeps the PR small.

## Design memo convention

Also add a short memo documenting:
- what phase 1 includes
- what it explicitly excludes
- why the three-file cluster was chosen first
- why `records.ts` / `get-post.ts` renames are deferred until category-local directory restructuring
- recommended follow-up order

Proven path:
- `docs/plans/2026-05-06-publication-records-refactor-phase-1.md`

## Validation commands that worked

Run:
```bash
node --test tests/src/lib/publications/records-repository-architecture.test.mjs
node --test tests/use-cases-mdx-routing-and-preview.test.mjs tests/aip-demo-mdx-routing-and-preview.test.mjs tests/acp-demo-mdx-routing-and-preview.test.mjs
npx tsc --noEmit --pretty false
```

This was enough to validate the first-pass extraction without paying for a broad repo-wide build.

## PR guidance

Use a separate PR with a title like:
- `refactor: share standard publication records repository`

Useful PR body structure:
- summary of the shared helper extraction
- explicit scope boundaries
- note that loader unification and path renames are intentionally excluded
- exact test commands

## Important findings to preserve

- `records.ts` / `get-post.ts` path shortening is only sane after moving to category-local directories such as `src/lib/publications/demo/acp/records.ts`; do not attempt filename-only shortening in the current flat layout
- architecture tests are effective for this refactor style because they let you prove the intended code shape directly before and after extraction
- keeping file paths and exported function names stable in phase 1 dramatically reduces route/test churn and keeps the PR reviewable
- extract the strongest duplication cluster first; trying to unify blog/news/whitepaper/event in the same initial PR increases special-case pressure too early

## Done criteria

- fresh branch/worktree from latest `origin/main`
- design memo added
- shared standard repository helper added
- use-case, AIP demo, and ACP demo record modules migrated to the helper
- architecture regression test passes
- route-level regression tests for those three categories pass
- `npx tsc --noEmit --pretty false` passes
- branch pushed and PR opened

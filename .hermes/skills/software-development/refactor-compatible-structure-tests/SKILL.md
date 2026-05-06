---
name: refactor-compatible-structure-tests
description: Write structure-oriented tests that keep validating behavior across implementation relocation refactors, including separate test-only PR preparation before moving code.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [testing, refactor, structure-tests, regression, git, pr]
    related_skills: [github-pr-workflow, existing-pr-followup-worktree]
---

# Refactor-compatible structure tests

Use this when a codebase has tests that assert source layout or implementation structure, and you need those tests to keep working before and after a refactor that moves code between files.

Typical trigger phrases:
- "make the tests validate both before and after the refactor"
- "separate test-only PR first"
- "do not let the tests get rewritten together with the implementation PR"
- "the tests should verify equivalence, not one exact file layout"

## Goal

Preserve regression coverage while reducing coupling to a single implementation location.

The key idea:
- test semantic structure and required content
- tolerate one of several valid source locations during a migration window
- centralize the source-location branching in helpers, not in every test

## Recommended workflow

### 1. Split test preparation from implementation refactor

If the user wants strong equivalence validation, do this in two PRs:

1. Test-only PR on latest main
   - no production code changes
   - update tests so they can validate both old and new layouts
2. Implementation PR
   - move code freely while keeping the already-adapted tests green

Do not mix the test decoupling with the implementation relocation unless the user explicitly asks for one combined PR.

### 2. Introduce focused source-discovery helpers

Create a helper under `tests/helpers/` that answers questions like:
- where is the top-page data source currently?
- where is the top-page structure source currently?
- does the old externalized content file still exist?

Good helper style:
- one small helper per page/domain family
- return the first existing source among ordered candidates
- expose boolean helpers like `isTopPageContentExternalized()` when needed

Example pattern:

```js
import { existsSync, readFileSync } from "node:fs";

export function readSource(relativePath) {
  return readFileSync(new URL(`../../${relativePath}`, import.meta.url), "utf8");
}

export function sourceExists(relativePath) {
  return existsSync(new URL(`../../${relativePath}`, import.meta.url));
}

export function readFirstExistingSource(relativePaths) {
  for (const relativePath of relativePaths) {
    if (sourceExists(relativePath)) {
      return readSource(relativePath);
    }
  }
  throw new Error(`None of the candidate source files exist: ${relativePaths.join(", ")}`);
}
```

Then add page-specific wrappers, for example:

```js
export function getTopPageDataSource() {
  return readFirstExistingSource([
    "src/content/top-page.ts",
    "src/app/page.tsx",
  ]);
}

export function getTopPageStructureSource() {
  return readFirstExistingSource([
    "src/components/sections/top-page-sections.tsx",
    "src/app/page.tsx",
  ]);
}
```

### 3. Prefer page-specific test files over one mixed structural test

If a single test file mixes top page and AI Crew page expectations, split it.

Preferred:
- `tests/top-page-structure.test.mjs`
- `tests/ai-crew-page-structure.test.mjs`

This reduces churn when only one page family changes.

### 4. Keep assertions semantic, not overly path-specific

Prefer these kinds of checks:
- required CTA labels/hrefs still exist
- a route still uses the site chrome
- a section still contains the same heading/body pair
- a structure source still contains required reusable UI or interaction markers

Avoid brittle assertions like:
- exact requirement that content must live only in one file path
- exact giant object name unless the migration stage explicitly requires it
- assertions that break only because the same content moved from `src/content/**` to `src/app/**`

Good pattern:

```js
const topPageDataSource = getTopPageDataSource();
assert.match(topPageDataSource, /primaryCta: \{ label: "お問い合わせ", href: topPageHeroContactUrl \}/);
```

### 5. Use conditional assertions only for layout-coupling cleanup checks

When verifying the refactor removed old dependencies, gate that assertion on whether the old file still exists.

Example:

```js
if (!isTopPageContentExternalized()) {
  assert.doesNotMatch(topPage, /@\/content\/top-page/);
}
```

This lets the same test pass both:
- before the refactor, when old files still exist
- after the refactor, when those imports should be gone

### 6. Update related tests that read the moved files directly

When removing old files like `src/content/top-page.ts` or `src/components/sections/top-page-sections.tsx`, search tests for direct reads of those files and convert them to helpers too.

Common affected test themes:
- CTA link checks
- structure/readability checks
- not-found page checks using top-page constants
- asset path checks that read a specific old content file

Important practical lesson from `corp-web-japan` relocation work:
- many tests may not show up from one narrow grep because they fail by calling `readSource("old/path.tsx")` or `sourceExists("old/path.ts")` rather than importing the old module name
- in relocation PRs, expect CI to reveal additional exact-path tests in waves; one grep pass is often not enough
- after the first CI failure, use `gh run view <RUN_ID> --log-failed` and update every remaining hard-coded source path mentioned in the failing tests before re-pushing
- likely hotspots include publication/page architecture tests, canonical endpoint tests, launch-readiness tests, inline-link style tests, metadata integrity tests, and any tests asserting loader import paths directly
- for pure relocation PRs where the user wants one combined implementation PR, it is acceptable to update these exact-path tests in the same PR rather than splitting a separate test-only PR
- when the old file truly no longer exists, rewrite the assertion to target the new path or to validate the same semantic contract from the new file, rather than trying to preserve a stale compatibility shim just for tests

### 7. Verify on latest main before opening the test-only PR

Run the repo’s normal verification flow from the new worktree on latest main.

For this repo pattern, use:

```bash
npm run test:ci
```

The point is to prove:
- the test-only PR passes against the current old layout
- the later implementation PR can reuse those tests unchanged or with minimal adjustments

## Practical lessons

### A. Centralize migration tolerance
Do not scatter arrays of fallback paths through many test files if you can avoid it. Put the path branching in one helper module.

### B. Split by page family
If the user is refactoring top page first, isolate top-page tests from AI Crew tests so that the top-page PR does not produce unnecessary AI Crew test churn.

### C. Treat tests as compatibility scaffolding during refactor windows
During a staged refactor, tests may need to accept both layouts temporarily. That is a feature, not a weakness, when the user explicitly wants equivalence validation.

### D. Keep implementation PRs cleaner by landing test decoupling first
If a separate test-only PR is available, later rebases of the implementation PR become easier. Prefer the latest-main version of the tests during conflict resolution and keep the implementation diff focused.

### E. When shared helpers absorb logic, assert delegation or contract — not the old inline implementation site
Practical lesson from publication-records refactoring in `corp-web-japan`:
- a structure/regression test can become falsely red even when runtime behavior is still correct if it insists that a wrapper file must literally contain a direct helper call such as `href: resolveRedirectablePublicationHref(...)`
- after extracting common logic into a shared repository/helper, the wrapper may only contain a call like `createStandardPublicationRecordsRepository(...)` while the actual redirect-aware href logic moved into the shared helper
- in that situation, the old test is over-coupled to implementation placement, not validating the real contract

Preferred rewrite pattern:
- for files that still own the logic directly, keep the explicit inline assertion
- for files intentionally migrated onto a shared helper, assert one of:
  - they delegate to the expected shared helper/factory
  - the shared helper itself still contains the required contract implementation
  - both, if you want stronger coverage

Example shape:

```js
const sharedRepositoryFiles = new Set([
  "src/lib/publications/use-case-publication-records.ts",
  "src/lib/publications/aip-demo-publication-records.ts",
  "src/lib/publications/acp-demo-publication-records.ts",
]);

for (const filePath of redirectAwareRecordFiles) {
  const source = readSource(filePath);

  if (sharedRepositoryFiles.has(filePath)) {
    assert.match(source, /createStandardPublicationRecordsRepository/);
    continue;
  }

  assert.match(source, /href:\s*resolveRedirectablePublicationHref\(/);
}
```

Why this matters:
- preserves regression intent during abstraction extraction
- avoids CI failures caused only by moving code into a shared helper
- keeps structure tests aligned with refactor-safe contracts rather than one historical file shape

## Component-level UI state coverage in this repo

Additional practical pattern from `corp-web-japan` UI follow-up work:
- this repo's existing fast tests are mostly `node:test` files that inspect source text, not browser/runtime-rendered component tests
- when the user asks for tests around a small presentational UI component and there is no existing lightweight React component test harness, prefer a narrow source-based contract test under `tests/src/components/**`
- this is especially appropriate for components whose main risk is preserving explicit state branches and UI contract details such as:
  - guard clauses like `return null` when a terminal state is reached
  - progress/percentage calculation expressions
  - loading vs idle button branches
  - required class-based affordances for hover/disabled/spinner/icon states
  - stable visible copy that the product/review cares about

Recommended shape:
- place the test near its source path mirror, for example:
  - source: `src/components/ui/progressive-load-more.tsx`
  - test: `tests/src/components/ui/progressive-load-more.test.mjs`
- use `node:test` + `node:assert/strict`
- read the source from `process.cwd()` with `readFileSync(path.join(repoRoot, relativePath), "utf8")`
- assert the expected state branches with targeted regexes

Example covered states:
- progress math safety guard such as `Math.max(totalCount, 1)`
- hidden/completed branch such as `if (currentCount >= totalCount) return null`
- default idle state copy and progress bar markup
- loading state spinner + disabled button branch
- interactive/disabled affordance classes and icon path contract

Why this is useful here:
- avoids introducing a new runtime test stack just for one UI component
- stays consistent with the repository's existing source-contract test style
- gives fast regression coverage for review-sensitive UI state branches

Important limitation:
- this verifies code-level UI contract, not actual rendered browser behavior
- if the user's concern is visual parity, spacing, or deployed preview behavior, add browser/preview verification separately instead of treating the source-based test as sufficient UX proof

## Worktree recovery note for test follow-up

Practical follow-up finding:
- if a supposedly fresh worktree path turns out not to be a real checkout and only contains a partial subtree (for example only `tests/`), do not salvage it
- remove that directory, run `git worktree prune`, recreate the worktree at a clean path, and re-verify with `git rev-parse --show-toplevel`, `git status -sb`, and a shallow `find` listing before editing or running tests

## Done criteria

A good result means:
- a test-only PR changes no production code
- tests pass on latest main before the implementation refactor
- the source-location branching is concentrated in helpers
- page/domain structure tests are split sensibly
- the later implementation refactor can move code without rewriting every test again

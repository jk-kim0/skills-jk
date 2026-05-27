---
name: corp-web-japan-launch-readiness-tests
description: Add and maintain launch-readiness regression tests in corp-web-japan for shared links, CTA targets, route metadata, and SEO/indexing surfaces.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, testing, launch-readiness, seo, links, metadata]
---

# corp-web-japan launch-readiness tests

Use when the user asks to improve test coverage for corp-web-japan around launch readiness, broken links, metadata, or shared navigation integrity.

## When to use
- the user mentions issue #62 or launch-readiness gaps
- the user asks to add regression tests for broken links, CTA targets, `/events`, `robots`, `sitemap`, or metadata
- the user asks whether earlier broken links from the wiki `Links` page were fully fixed
- the user wants broad safety checks over existing pages/components rather than a single feature test

## Key findings to remember
- The repo uses lightweight Node test files under `tests/*.test.mjs`, not a browser E2E suite.
- `npm run test:ci` runs `eslint`, `tsc --noEmit`, and `node --test tests/*.test.mjs`.
- A tiny helper for reading source files is useful and reusable: `tests/helpers/source-readers.mjs`.
- For this repo, launch-readiness regression tests are mostly source-level assertions against route files, content files, and shared layout components.
- `Links.md` in `corp-web-japan.wiki` is a good reference for expected shared navigation destinations, but tests must reflect the latest code, not the wiki blindly.
- `/events` may intentionally remain gated with `notFound()` plus an `unblock` query param; in that state, test the gate explicitly and ensure `/events` is excluded from `src/app/sitemap.ts`.
- A remaining `href="#"` can still hide in non-navigation UI such as success-state buttons; search broadly, not just header/footer.
- Brand/title drift can remain in route metadata even after page-title cleanup PRs; search `src/app` for `AI Staff` and verify intended `QueryPie AI` branding.

## Recommended workflow
1. Start from latest `origin/main` in a fresh worktree.
2. Check open PRs first so you do not duplicate in-flight work.
3. Read current tests:
   - `tests/home-structure.test.mjs`
   - `tests/footer-legal-links.test.mjs`
   - `tests/seo-metadata.test.mjs` if present
4. Read the current wiki reference if relevant:
   - `~/workspace/corp-web-japan.wiki/Links.md`
5. Inspect these source-of-truth files first:
   - `src/components/layout/site-header.tsx`
   - `src/components/layout/site-footer.tsx`
   - `src/content/home.ts`
   - `src/app/events/page.tsx`
   - `src/app/robots.ts`
   - `src/app/sitemap.ts`
   - route files under `src/app/**/page.tsx`
   - suspicious component surfaces such as resource post pages and FAQ/contact CTAs
6. Write failing tests first.
7. Run the specific new test file and verify failure.
8. Make the minimum code changes needed.
9. Run `npm run test:ci` and `npm run build`.
10. If opening/updating a PR tied to issue #62, use a partial-progress reference only unless the work truly closes the issue.

## Good reusable test areas

### 1. Shared navigation integrity
Create tests that assert current header/footer destinations match the implemented links.
Check for:
- internal routes such as `/solutions/ai-crew`, `/solutions/ai-dashi`, `/whitepapers`, `/blog`
- expected external QueryPie links
- no regressions back to deprecated `/whitepaper`

### 2. Broken placeholder link detection
Search for and test against bare hash links:
- `href="#"`
- `href: "#"`
- `ctaHref: "#"`

Important nuance:
- `#contact`, `/#contact`, and section anchors like `#roles` may still be intentionally used; do not ban all anchors.
- Ban only bare placeholders unless the user explicitly wants anchor removal too.

### 3. Launch-risk CTA target coverage
For main public flows, test that CTA targets resolve to explicit anchors or real destinations.
Useful sources:
- `src/content/home.ts`
- `src/app/page.tsx`
- `src/app/solutions/ai-crew/page.tsx`
- `src/components/sections/ai-crew-floating-guide.tsx`
- `src/components/sections/ai-dashi-faq.tsx`
- `src/components/sections/resource-post-page.tsx`

### 4. `/events` readiness contract
If `/events` is intentionally gated:
- assert the `unblock` param logic still exists
- assert `notFound()` remains in place for normal access
- assert `/events` is not listed in `src/app/sitemap.ts`

If the gate is later removed:
- update tests to require normal availability
- add `/events` back to sitemap expectations

### 5. Metadata/title integrity
For user-facing pages, assert metadata exists and titles use the intended branding.
Check:
- `export const metadata: Metadata = { ... }`
- `generateMetadata` for dynamic routes
- `title`, `description`, and canonical metadata where applicable
- no stale `AI Staff` titles if the current agreed branding is `QueryPie AI`

Typical files:
- `src/app/page.tsx`
- `src/app/blog/page.tsx`
- `src/app/whitepapers/page.tsx`
- `src/app/events/page.tsx`
- `src/app/demo/use-cases/page.tsx`
- `src/app/solutions/ai-crew/page.tsx`
- `src/app/solutions/ai-dashi/page.tsx`
- `src/app/posts/[category]/[slug]/page.tsx`

### 6. SEO/indexing surfaces
Test for presence and core contents of:
- `src/app/robots.ts`
- `src/app/sitemap.ts`
- expected core route entries in sitemap
- exclusion of gated/non-public routes when appropriate

## Suggested helper
Create and reuse:

`tests/helpers/source-readers.mjs`

```js
import { readFileSync } from "node:fs";

export function readSource(relativePath) {
  return readFileSync(new URL(`../../${relativePath}`, import.meta.url), "utf8");
}
```

This keeps repo-level tests concise and avoids repetitive file-loading code.

## Practical pitfalls
- Do not assume latest local `main` equals `origin/main`; fetch and use a worktree from `origin/main`.
- Do not assume an issue-closing keyword is appropriate in the PR body. For issue #62 follow-up work, prefer `partial progress for #62` unless the PR actually resolves the remaining issue scope.
- `gh pr view` can momentarily appear stale right after push; re-run it once if file/commit lists look cached.
- A PR body temp file left untracked in the worktree can trigger `gh pr create` warnings about uncommitted changes; clean it up after editing the PR.
- `npm run test:ci` and `npm run build` may fail in a fresh worktree until `npm install` is run.
- Build warnings about multiple lockfiles in worktrees are expected here; distinguish them from real build failures.

## Verification checklist
- New test file fails before code changes.
- New tests cover at least one launch-risk surface not previously tested.
- No bare placeholder links remain in the tested surfaces.
- Shared header/footer links align with current implementation.
- Public route titles/metadata reflect current branding and intended canonical state.
- `npm run test:ci` passes.
- `npm run build` passes.
- PR body references issue #62 as partial progress unless the issue is fully resolved.

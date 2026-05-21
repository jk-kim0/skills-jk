---
name: corp-web-app-internal-route-authoring
description: Author and review corp-web-app internal-only utility pages so they stay under the internal namespace, remain noindex, avoid sitemap/canonical exposure, and are verified with route-mirrored tests.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-app, nextjs, app-router, internal-routes, seo, sitemap, testing]
---

# corp-web-app Internal Route Authoring

Use this skill when adding, relocating, or reviewing corp-web-app pages that are operational, QA, translation coverage, preview tooling, or otherwise internal-only rather than public customer-facing pages.

## Core rule

Internal-only pages must be treated as internal application surfaces, not public content routes.

Prefer route paths under:

```text
src/app/[locale]/internal/<tool-or-family>/page.tsx
```

Avoid public-looking App Router paths such as:

```text
src/app/<tool-or-family>/page.tsx
src/app/[locale]/<tool-or-family>/page.tsx
```

unless the user explicitly asks for public release or public navigation exposure.

## Required implementation checks

1. Put route entrypoints under `src/app/[locale]/internal/**`.
2. Keep any route-specific components colocated under the internal route subtree when the components are only used by that internal page.
   - Example: `src/app/[locale]/internal/translations/events/_components/*`.
   - Do not leave internal-only route components under a top-level `src/app/translations/**` tree, because it reads like a public route family even when it contains no `page.tsx`.
3. Export metadata that blocks indexing:

```ts
export const metadata: Metadata = {
  title: '...',
  description: '...',
  robots: {
    index: false,
    follow: false,
  },
};
```

4. Do not add canonical alternates for internal-only pages unless there is a deliberate internal-canonical policy in the task.
   - For internal-only utility pages, prefer no `alternates.canonical` over a public-looking canonical URL.
5. Link from the internal index using internal paths only, for example:

```text
/{locale}/internal/translations/events
/{locale}/internal/translations/blog
```

not:

```text
/{locale}/translations/events
/{locale}/translations/blog
```

6. Mirror tests to the route path:

```text
src/app/[locale]/internal/<tool-or-family>/page.tsx
src/__tests__/app/[locale]/internal/<tool-or-family>/page.test.tsx
```

## Sitemap and search exposure audit

Before finishing an internal-route PR, run source-level checks to verify there is no accidental public exposure:

```bash
git ls-files | grep -E '(^src/app/(\[locale\]/)?<family>|^src/__tests__/app/<family>)' && exit 1 || echo 'no public route files tracked'
```

For the translation-coverage example, this was:

```bash
git ls-files | grep -E '(^src/app/(\[locale\]/)?translations|^src/__tests__/app/translations)' && exit 1 || echo 'no public translations route files tracked'
```

Also scan for public path references:

```bash
git grep -nE '/(en|ko|ja)/<family>|/<family>/' -- src public || true
```

Interpretation:
- References under `/internal/<family>` are expected.
- Top-level public route references should be removed or explicitly justified.
- `public/` sitemap/static references should not include internal route families.

## Internal MDX pages migrated from corp-web-contents

When an internal-only MDX page is moved from `corp-web-contents` into `corp-web-app`, do not stop at changing internal index links. Move the actual MDX into `src/content/internal/`, add an explicit `src/app/[locale]/internal/<slug>/page.tsx` route, and make that route read the repo-local MDX directly rather than delegating to `dynamic-page`, `FileQuery`, or remote `corp-web-contents` lookups.

Also migrate referenced assets into a route-aligned app-local public directory such as `public/internal/<slug>/...` and rewrite the MDX references. Watch for indirect remote dependencies in shared article rendering: `ArticleFileImage`, `ogImage`, and string `relatedPosts` can still trigger FileQuery/remote frontmatter behavior unless the internal route or frontmatter handles them explicitly.

See `references/internal-mdx-repo-local-migration.md` for the session-derived checklist and verification snippets.

## Tests to add or update

Add tests that lock all three contracts:

1. Internal index links point at `/{locale}/internal/...`.
2. The route metadata is noindex/nofollow.
3. The metadata has no public canonical alternate when the page is internal-only.

For publication translation coverage pages such as `/internal/translations/blog` or `/internal/translations/news`, follow the reusable implementation and verification pattern in `references/publication-translation-coverage-endpoints.md`.

Example assertion:

```ts
expect(metadata).toMatchObject({
  robots: {
    index: false,
    follow: false,
  },
});
expect(metadata).not.toHaveProperty('alternates');
```

## Verification pattern

Run the narrowest route tests first:

```bash
npx vitest run 'src/__tests__/app/[locale]/internal/<family>/<page>/page.test.tsx'
```

For visual/layout questions on deployed internal pages, inspect the exact stage URL in the browser and measure computed layout before judging from code alone. Prefer a targeted DOM script that identifies semantic elements and reports `getBoundingClientRect()` plus computed `margin`, `padding`, `display`, and `gap`; this quickly separates intentional hero/list spacing from accidental CSS inheritance. For translation coverage pages specifically, avoid broad text-walker matching only by text content because Next.js inline flight `script` payloads may also contain strings like `Translation coverage`; constrain by tag/role/id/aria labels such as the eyebrow `p`, `[aria-label="... summary"]`, and `section[aria-labelledby="..."]`.

Then run test group assignment validation if test files moved:

```bash
node scripts/ci/assert-test-groups.mjs
```

For visual/layout follow-ups on internal utility pages, verify the exact affected URL in the browser and at least one sibling route that shares the same layout primitive. Prefer concrete computed-style checks for the contract being changed (for example shell padding, shell background, eyebrow/header position, and content/list section margin) instead of relying only on screenshots or subjective spacing impressions. If the visible list label duplicates the page heading, promote the meaningful label to the page-level `h1` and remove the list-level visible `h2`; add a route test that asserts the label is an `h1` and is not also rendered as an `h2`. If a local dev server was started for this review, stop it and confirm the port is clear before creating the PR.

If a broad internal index test fails before collection because a fresh worktree lacks worktree-local PostCSS/Tailwind dependencies, do not install by default if the user prefers avoiding local installs. Report it explicitly and rely on the narrower tests that can run plus CI.

## Pitfalls

- A route can be noindex and still be wrongly modeled as public if it lives under `src/app/[locale]/<family>`. For internal tools, fix the path, not only the metadata.
- Removing a top-level `page.tsx` is not enough if route-only components remain under a top-level app subtree and future maintainers may recreate public routes from them. Move internal-only components under the internal route subtree.
- Do not add redirects from old public-looking internal paths unless the user explicitly asks for compatibility. For internal-only surfaces, removal is usually preferable.
- Do not assume sitemap behavior from memory. Inspect the repo's sitemap implementation and static `public/` references for the current branch.

## References

- `references/translation-coverage-internalization.md` — session-specific example: moving translation coverage pages from public-looking `/translations/*` paths to internal-only `/internal/translations/*` paths.
- `references/translation-coverage-layout-spacing.md` — session-specific spacing/layout pattern for internal translation coverage pages, including shared primitive extraction, computed-style browser verification, and dev-server cleanup before PR creation.

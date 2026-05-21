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

## Tests to add or update

Add tests that lock all three contracts:

1. Internal index links point at `/{locale}/internal/...`.
2. The route metadata is noindex/nofollow.
3. The metadata has no public canonical alternate when the page is internal-only.

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

Then run test group assignment validation if test files moved:

```bash
node scripts/ci/assert-test-groups.mjs
```

If a broad internal index test fails before collection because a fresh worktree lacks worktree-local PostCSS/Tailwind dependencies, do not install by default if the user prefers avoiding local installs. Report it explicitly and rely on the narrower tests that can run plus CI.

## Pitfalls

- A route can be noindex and still be wrongly modeled as public if it lives under `src/app/[locale]/<family>`. For internal tools, fix the path, not only the metadata.
- Removing a top-level `page.tsx` is not enough if route-only components remain under a top-level app subtree and future maintainers may recreate public routes from them. Move internal-only components under the internal route subtree.
- Do not add redirects from old public-looking internal paths unless the user explicitly asks for compatibility. For internal-only surfaces, removal is usually preferable.
- Do not assume sitemap behavior from memory. Inspect the repo's sitemap implementation and static `public/` references for the current branch.

## References

- `references/translation-coverage-internalization.md` — session-specific example: moving translation coverage pages from public-looking `/translations/*` paths to internal-only `/internal/translations/*` paths.

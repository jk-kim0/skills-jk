---
name: corp-web-japan-publication-detail-layout
description: Maintain corp-web-japan publication/article detail page layout across blog, whitepaper, news, events, use-cases, demos, and resource documents, including shared sidebar spacing and source-level layout contracts.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, publications, layout, sidebar, article-detail]
    related_skills:
      - corp-web-japan-origin-main-worktree-safety
      - corp-web-japan-production-inline-link-parity
---

# Corp Web Japan: publication detail layout

Use this when changing the visual structure or layout of MDX-backed publication/detail pages in `corp-web-japan`, especially shared article surfaces rendered through `PublicationPostPage`.

## When to use

- The user asks for layout/spacing changes on a blog, whitepaper, news, event, use-case, demo, introduction-deck, glossary, or manual detail page.
- A requested change should apply consistently to multiple document families rather than one MDX file.
- The right sidebar contains table-of-contents, related items, or contact blocks.
- The user points to a deployed detail URL such as `https://stage.querypie.ai/blog/<id>/<slug>` and asks for visual/sidebar adjustment.

## Source of truth

Shared detail rendering currently lives in:

- `src/components/sections/publication-post-page.tsx`

This component is used by multiple publication/resource families, so prefer changing it for cross-family layout behavior rather than editing individual route files or MDX records.

## Sidebar spacing rule

Session detail: see `references/sidebar-offset-80px.md` for the concrete stage-page example and verification commands.

If the sidebar's first visible section needs to move down, apply spacing to the sidebar content wrapper, not to a specific section such as only the TOC block.

Why:

- The TOC can be hidden when `post.toc.length === 0`.
- Related items can also be conditional via `post.relatedItems.length > 0`.
- Applying top spacing only to the TOC fails on documents where the TOC is absent: the related-items block or contact block would still sit too high.
- Wrapper-level spacing preserves the same first-visible-block offset regardless of which conditional sidebar sections render.

Preferred shape for a desktop-only 80px offset:

```tsx
<aside className="w-full lg:w-[280px] lg:flex-shrink-0">
  <div className="space-y-[60px] lg:pt-[80px]">
    {post.toc.length > 0 ? (...toc...) : null}
    {post.relatedItems.length > 0 ? (...related...) : null}
    {...contact...}
  </div>
</aside>
```

Use `lg:` for right-sidebar-only desktop behavior unless the user explicitly asks to change mobile stacked layout spacing.

## Verification pattern

For layout contract changes that are visible but mechanically simple, add or update a small source-level test under `tests/` rather than starting a local dev server by default.

Example test target:

- `tests/publication-post-sidebar-layout.test.mjs`

Example assertions:

```js
const source = readSource("src/components/sections/publication-post-page.tsx");

assert.match(source, /<aside className="w-full lg:w-\[280px\] lg:flex-shrink-0">\s*<div className="space-y-\[60px\] lg:pt-\[80px\]">/);
assert.match(source, /post\.toc\.length > 0 \? \(/);
assert.match(source, /post\.relatedItems\.length > 0 \? \(/);
```

If adding a new `tests/**/*.test.mjs` file, update `scripts/ci/test-groups.mjs` in the same PR and run:

```bash
node --test tests/<new-test>.test.mjs
node scripts/ci/assert-test-groups.mjs
git diff --check
```

## Browser/stage evidence

When the user reports a layout issue on a specific deployed stage URL, open that exact URL before or after the change when practical. For sidebar alignment checks, a lightweight DOM geometry probe can be enough to confirm the pre-change condition:

```js
(() => {
  const h1 = document.querySelector("h1");
  const toc = [...document.querySelectorAll("h2")]
    .find((el) => el.textContent.trim() === "目次");
  const related = [...document.querySelectorAll("h2")]
    .find((el) => el.textContent.trim().includes("関連記事"));
  return {
    innerWidth,
    h1Top: h1?.getBoundingClientRect().top,
    h1Bottom: h1?.getBoundingClientRect().bottom,
    tocTop: toc?.getBoundingClientRect().top,
    relatedTop: related?.getBoundingClientRect().top,
  };
})()
```

Do not overstate a source-level class check as final visual parity. If the PR relies on Preview Deployment for visual confirmation, report that CI/Preview is pending rather than claiming deployed visual verification.

## Pitfalls

- Changing only the TOC block when the first visible sidebar section can be related items or contact.
- Applying desktop right-sidebar offset to mobile stacked layout unintentionally.
- Editing individual MDX documents for a shared layout issue.
- Starting a local dev server when the user prefers CI/preview and the change can be verified by source-level tests.
- Forgetting to add new source-level tests to `scripts/ci/test-groups.mjs`.

---
name: corp-web-japan-article-preview-parity
description: Compare a live/stage corp-web-japan article page against a legacy or preview article URL, identify whether differences come from shared layout CSS, sidebar policy, or content source, and map the visual delta to the exact files to change.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, article, blog, preview, stage, parity, css, sidebar, mdx]
    related_skills: [corp-web-japan-origin-main-worktree-safety, github-pr-workflow, dogfood]
---

# corp-web-japan article preview parity workflow

Use this when the user says a current `stage.querypie.ai` article/detail page should look like an older preview deployment or legacy `/posts/...` page, and wants a concrete change list before implementation.

## Why this skill exists

In `corp-web-japan`, article pages that look different at first glance may still share the same top-level component and CSS system. The visible delta can come from:
- sidebar composition (`ToC` vs `related`)
- route-specific rendering policy
- MDX-based content vs legacy HTML content
- metadata suffix differences

If you assume the whole article shell changed, you can overestimate the implementation scope. First prove whether the shell is actually different.

## High-value finding from prior use

For the current blog/article system:
- `/blog/[id]/[slug]` and legacy/preview `/posts/[category]/[slug]` can both render through `src/components/PublicationPostPage.tsx`
- The biggest visual difference may be that blog pages provide `toc` data while legacy resource posts provide `toc: []`
- In that case, the page shell is already nearly identical and the main UX delta is simply `ToC + related + CTA` vs `related + CTA`
- The current local ToC is not just conditionally shown; its visible height is intentionally capped in `src/components/sections/resource-post-toc.tsx` with `max-h-[220px] lg:max-h-[320px] overflow-y-auto`, so users may describe the right column as having a "fixed height" even though the whole aside is not fixed.
- Secondary differences may come from content source format:
  - blog route: MDX via `src/lib/publications/get-publication-post.ts`
  - legacy `/posts/...`: HTML extraction via `src/lib/resource-posts.ts`
- Be careful when the user mentions whitepapers alongside blog posts in `corp-web-japan`: the current `/whitepapers` page is a local list page, but whitepaper detail links currently go out to `querypie.com`, so the local repo may not control the whitepaper detail ToC/layout being compared.

## Required investigation order

1. Compare the exact live URLs the user requested first, not the code.
2. Confirm whether each requested URL stays on that host/path or redirects.
3. If one page redirects, record the redirect explicitly, but do not silently replace the user's requested comparison target with some other canonical page unless the user agrees.
4. Confirm console cleanliness.
5. Extract computed style metrics and resource/network behavior from both requested pages.
6. Only then inspect the repository to map the differences to files.

Do not start by reading local files and guessing.

### Important host/path rule

When the user's question is about runtime behavior such as font loading, caching, CDN warmth, or browser resource timing, the exact host and path matter.

Examples:
- `www.querypie.com/ja/solutions/aip`
- `querypie.ai/`
- `stage.querypie.ai/`

These are not interchangeable, even if some pages share content or branding. Browser cache is origin-specific, CDN warmth can differ by host, and page-specific preload assets can differ by route. If the user asked to compare a page under `www.querypie.com/ja/`, keep that page in the comparison unless it truly redirects away.

## Browser investigation checklist

Open both URLs and capture:
- title
- header structure and height
- main content width
- aside width
- H1 size / line-height
- body paragraph size / line-height / weight
- share UI style
- aside text content
- whether a ToC is present
- whether console errors exist

Useful browser-console expression pattern:

```js
(() => {
  const title = document.querySelector('main h1');
  const aside = document.querySelector('aside');
  const hero = Array.from(document.querySelectorAll('main img')).find(
    (img) => img.alt && img.alt.length > 20,
  );
  function cs(el) {
    if (!el) return null;
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return {
      tag: el.tagName,
      cls: String(el.className).slice(0, 140),
      width: Math.round(r.width),
      x: Math.round(r.x),
      y: Math.round(r.y),
      fs: s.fontSize,
      lh: s.lineHeight,
      fw: s.fontWeight,
      position: s.position,
      bg: s.backgroundColor,
    };
  }
  return {
    pageTitle: document.title,
    titleBox: cs(title),
    asideBox: cs(aside),
    heroBox: cs(hero),
    asideText: (aside?.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 500),
  };
})();
```

## Repository mapping checklist

After the browser diff, inspect these files first:

### Page-local MDX structure first for single-article visual issues
Before changing the shared article shell, inspect the target content file itself for wrapper/layout constructs that can explain the visual delta.

High-value checks in `src/content/**.mdx`:
- a first body image wrapped in `<Box center>` around `<ArticleFileImage ... />`, which can make the image appear narrower than the content column even when the shared shell is correct
- manual spacing with `<br />` before a `<ButtonLink ...>` CTA, which may still read as visually cramped and is often better replaced with a small explicit margin wrapper such as `<div className="mt-6">...</div>`
- duplicated hero/body image usage with `hideHeroImageOnDetail: true`, where the perceived "hero size bug" can actually be the body image wrapper rather than the route header image

Practical rule:
- if the request is about one specific article page and the cause is visible in that page's MDX structure, prefer a page-local MDX fix over editing `PublicationPostPage` or global publication component styles
- only change the shared shell when multiple pages need the same behavior or the MDX does not explain the problem

### Current blog/publication route
- `src/app/blog/[id]/[slug]/page.tsx`
- `src/lib/publications/get-publication-post.ts`
- `src/content/blog/<id>.mdx`
- For shared publication-MDX layout follow-ups such as first-body-image width or CTA-wrapper extraction, see `references/shared-publication-mdx-layout-fixes.md`.

### Legacy/preview resource-post route
- `src/app/posts/[category]/[slug]/page.tsx`
- `src/lib/resource-posts.ts`

### Shared article shell
- `src/components/PublicationPostPage.tsx`
- `src/components/sections/resource-post-toc.tsx`

## How to reason about the result

### Case 1: shell is mostly identical
If these are nearly the same between stage and preview:
- header
- title size
- hero style
- main column width
- aside width
- share buttons

Then do NOT propose a full redesign.

Instead, focus on:
1. sidebar rendering policy
2. route-specific data source
3. content-structure parity

### Case 2: preview has related sidebar only, stage has ToC first
This usually maps to:
- `src/components/PublicationPostPage.tsx` rendering the ToC block when `post.toc.length > 0`
- `src/lib/publications/get-publication-post.ts` filling `toc` via `extractHeadingsFromMdx(bodySource)`
- `src/lib/resource-posts.ts` returning `toc: []` for legacy posts

In that situation, the minimal implementation is usually one of:
- keep `toc` extraction but add a `showToc` / `sidebarMode` prop to `PublicationPostPage`
- or suppress ToC for blog detail routes specifically

Prefer route-level or prop-level policy over deleting the utility entirely.

## Recommended implementation options

### Minimal parity option
- Add `showToc` or `sidebarVariant` to `PublicationPostPage`
- Pass `showToc={false}` from `src/app/blog/[id]/[slug]/page.tsx`
- Keep `extractHeadingsFromMdx()` intact
- Update tests to reflect conditional ToC rendering instead of unconditional rendering

### Stronger preview parity option
In addition to the minimal option:
- revise the MDX content file (for example `src/content/blog/28.mdx`) to match the legacy paragraph grouping and copy flow more closely
- optionally align metadata suffix if the user cares about browser-tab parity

## Tests likely affected

Check and update:
- `tests/blog-mdx-rendering-architecture.test.mjs`

A prior version of this test assumed blog detail pages consume and render structured MDX ToC data directly. If ToC becomes conditional, rewrite the expectation to cover:
- heading extraction utility still exists
- `PublicationPostPage` supports conditional ToC rendering
- blog detail route selects the intended sidebar policy

## Reporting pattern to the user

Summarize the outcome in this order:
1. whether the two pages are actually different shells or mostly the same shell
2. the biggest visual delta the user is reacting to
3. which differences are content-source differences vs CSS/layout differences
4. the exact files to change
5. minimal vs extended implementation options

## Pitfalls

- Misdiagnosing a sidebar-policy issue as a full page redesign
- Ignoring that preview `/posts/...` may use legacy HTML data while stage `/blog/...` uses MDX
- Proposing large CSS changes when widths, typography, and share UI are already aligned
- Forgetting to update tests that assume unconditional ToC rendering
- Treating browser-tab title suffix differences as article-layout differences

## Done criteria

You are done when you can name:
- the exact visual deltas
- whether each delta comes from shared shell, sidebar policy, or content source
- the specific files that must change
- the minimal viable implementation path

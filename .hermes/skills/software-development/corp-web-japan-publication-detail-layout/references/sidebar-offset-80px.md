# Session note: publication sidebar 80px offset

Trigger example:
- User pointed to `https://stage.querypie.ai/blog/28/ai-security-threat-map-2026-cxo` and reported that the right sidebar sections (`目次`, `関連記事`) appeared too high.
- Desired behavior: add 80px top padding to the right sidebar so the `目次` heading aligns closer to the blog title line.
- Important conditional: the TOC can be hidden by document settings/content, so the same offset must still apply when the first visible sidebar section is related items or contact.

Implementation that worked:

```tsx
<aside className="w-full lg:w-[280px] lg:flex-shrink-0">
  <div className="space-y-[60px] lg:pt-[80px]">
    {post.toc.length > 0 ? (...toc...) : null}
    {post.relatedItems.length > 0 ? (...related...) : null}
    {...contact...}
  </div>
</aside>
```

Why wrapper-level spacing was chosen:
- `post.toc.length > 0` controls whether the TOC appears.
- `post.relatedItems.length > 0` controls whether related items appear.
- A TOC-only padding fix would fail when the TOC is absent.
- `lg:pt-[80px]` keeps the adjustment scoped to desktop/right-sidebar layout.

Verification used:

```bash
node --test tests/publication-post-sidebar-layout.test.mjs
node scripts/ci/assert-test-groups.mjs
git diff --check
```

Stage DOM probe used to confirm the pre-change symptom:

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

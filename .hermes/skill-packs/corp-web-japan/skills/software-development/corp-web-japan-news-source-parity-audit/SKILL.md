---
name: corp-web-japan-news-source-parity-audit
description: Cross-check corp-web-japan local news MDX coverage against the live QueryPie Japan news page and the corp-web-contents source list, then lock parity with a regression test.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, news, mdx, parity, migration, regression-test]
    related_skills: [corp-web-japan-origin-main-worktree-safety, github-pr-workflow]
---

# corp-web-japan news source parity audit

Use this when the user suspects the local `src/content/news/*.mdx` corpus is incomplete, or asks whether all news postings from QueryPie Japan have been migrated.

## What we learned

For the current QueryPie Japan news flow:
- the exact live verification target is `https://www.querypie.com/ja/company/news`
- the checked-in upstream source of truth is `../corp-web-contents/pages/company/news/ja/content.mdx`
- that source currently stores news as a single `items={[ ... ]}` list, not as one MDX file per posting
- some items link to QueryPie blog posts, but most items are external press/media URLs
- local migration coverage should be checked against the visible source list, not by assuming there are hidden per-post MDX files elsewhere in `corp-web-contents`
- when auditing `src/content/news/*.mdx` `redirectUrl` values for the Japan site, use `ja/content.mdx` as the primary source of truth; `ko/content.mdx` is not a 1:1 parity source for JP because it currently contains more items and different locale-specific coverage
- `ko/content.mdx` can still be useful as a secondary cross-check for older shared/global media links, but a mismatch in counts or missing same-title entries there does not by itself mean the JP `redirectUrl` is wrong

## Recommended workflow

1. Start from latest `origin/main`.
- Follow the repo safety workflow.
- Do not audit from a stale local `main`.

2. Check the live page directly.
- Visit exactly `https://www.querypie.com/ja/company/news`.
- Extract the visible list count and the ordered title list.
- Also extract the visible href list when link-target parity matters.

Browser-side extraction that worked well:

```js
Array.from(document.querySelectorAll('main li h4')).map((el, i) => ({
  index: i + 1,
  title: el.textContent.trim(),
}))
```

And for hrefs:

```js
Array.from(document.querySelectorAll('main li a')).map((a, i) => ({
  index: i + 1,
  href: a.href,
  text: a.textContent.trim(),
}))
```

3. Parse the corp-web-contents source list.
- Read `../corp-web-contents/pages/company/news/ja/content.mdx`.
- Find the `items={[ ... ]}` array and evaluate only that array payload.
- Compare count, ordered titles, hrefs, and dates against the live page.

A simple Node extraction pattern that worked:

```js
const src = fs.readFileSync('../corp-web-contents/pages/company/news/ja/content.mdx', 'utf8');
const start = src.indexOf('items={[');
const end = src.indexOf(']}', start);
const arrayText = src.slice(start + 'items={'.length, end + 1);
const items = Function(`return (${arrayText});`)();
```

4. Compare with local `src/content/news/*.mdx`.
- Count files.
- Parse each file's frontmatter `id`, `title`, and `date`.
- Compare local ordered titles against the source list.
- Do not stop at count equality alone; check ordered titles too.

5. If postings are missing, migrate them.
- Create a fresh worktree from latest `main`.
- Add one MDX file per missing item under `src/content/news/<id>.mdx`.
- Copy route-aligned thumbnails to `public/news/<id>/thumbnail.png`.
- Keep `heroImageSrc: "/news/<id>/thumbnail.png"`.
- If the page shell already renders the hero, do not duplicate the same image at the top of the MDX body.

## Important experiential findings

- In this repo snapshot, there were no missing local postings once live, source, and local were compared carefully: all three counts were 14 and titles matched in order.
- The user's suspicion was still valid to investigate, because earlier migration work had produced abbreviated local news bodies and that can look incomplete even when the posting set is complete.
- The most reusable follow-up is not speculative migration but a parity regression test that prevents future omissions.
- Worktree-relative paths matter in tests. From a worktree under `.worktrees/<name>`, the corp-web-contents source path was:

```js
path.join(process.cwd(), '../../../corp-web-contents/pages/company/news/ja/content.mdx')
```

Using `../corp-web-contents/...` from inside the worktree test failed.

## Regression test to add

Create a test like `tests/news-source-parity.test.mjs` that asserts:
- local news MDX count equals the corp-web-contents source count
- local news titles match the source titles in the same visible order
- each local file has non-empty `id`, `title`, and `date`

This is enough to catch dropped or forgotten migrations without relying on live network access in CI.

## Verification

Run the targeted set:

```bash
node --test tests/news-source-parity.test.mjs tests/news-mdx-routing-and-preview.test.mjs tests/news-imported-corpus.test.mjs
```

If code changes were required beyond the test, then continue with the normal repo PR workflow.

## Done criteria

- live page count and titles verified against the exact requested URL
- corp-web-contents source list parsed successfully
- local `src/content/news/*.mdx` compared against source list
- any real missing postings migrated, or parity explicitly confirmed with evidence
- parity regression test added or updated

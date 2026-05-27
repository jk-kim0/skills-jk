---
name: corp-web-japan-mdx-buttonlink-style-debugging
description: Diagnose corp-web-japan article/manual/resource CTA button UI regressions caused by MDX ButtonLink children being wrapped in paragraph elements that inherit article-body typography styles.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, mdx, buttonlink, cta, styling, publication, manuals, whitepapers]
---

# corp-web-japan MDX ButtonLink style debugging

Use this when a CTA/link box inside an MDX article body looks visually broken on `stage.querypie.ai` or locally, especially on manuals/resources/publication detail pages rendered through `PublicationPostPage`.

## Typical symptom

The CTA appears as a dark full-width button/bar but looks wrong compared with other pages:
- text color looks muted instead of white
- vertical centering feels off
- button height is unexpectedly tall or cramped
- top spacing inside the button looks wrong
- there is no visible gap between a preceding sentence/paragraph and the button
- the same `ButtonLink` looks fine on whitepapers but broken on manuals/resources

## Additional high-value finding: missing gap above ButtonLink can be a shared body-style contract bug

In this repo, a report like:
- "there is no spacing between `フォーム送信後、以下のリンクから資料を確認できます。` and the next button"

often means the problem is not the MDX text itself, but the shared publication body spacing rules in:
- `src/components/sections/publication-post-page.tsx`
- especially `publicationBodyClassName`

A concrete proven pattern:
- the paragraph gets body spacing from `[&_p]:mt-4`
- the CTA class `.article-content-btn` has button visuals and `mb-*`
- but it has no corresponding top margin when it follows a paragraph
- adding extra blank lines in MDX does not create real spacing before a JSX component like `<ButtonLink>`

So if a paragraph is followed immediately by:

```mdx
<ButtonLink href="/introduction-deck/1/QueryPie_AIP_Intro_JP.pdf" external={true}>QueryPie AIP 製品紹介書を開く</ButtonLink>
```

the visual gap can still be zero even though the MDX source contains blank lines.

### Correct fix direction for spacing bugs

Prefer fixing the shared article-body spacing contract, not sprinkling `<br />` into one MDX file.

Good systemic fixes are sibling-aware rules such as:
- `p + .article-content-btn`
- `ul + .article-content-btn`
- `ol + .article-content-btn`
- optionally `h2 + .article-content-btn`

This is safer than adding unconditional top margin to every `.article-content-btn`, because some top-of-body CTA placements may intentionally sit flush and should not all shift.

### Practical diagnosis rule

If the complaint is specifically about the gap between a sentence and the next CTA:
1. find the exact MDX source line containing the sentence
2. confirm the next node is a `ButtonLink`
3. inspect `publicationBodyClassName` before editing the MDX
4. treat `<br />` insertion as a last-resort workaround, not the default fix

## High-value finding

In this repo, the root cause can be the **MDX authoring shape**, not the button component CSS itself.

If `ButtonLink` is authored as a multiline block like:

```mdx
<ButtonLink href="/api-docs.html">
  QueryPie ACP OpenAPI Reference を開く
</ButtonLink>
```

MDX can render it as:

```html
<a class="article-content-btn" href="/api-docs.html"><p>QueryPie ACP OpenAPI Reference を開く</p></a>
```

Then the body-wide paragraph styles from `PublicationPostPage` leak into the button label, especially:
- `[&_p]:mt-4`
- `[&_p]:text-slate-500`

This makes the button look broken even though `.article-content-btn` itself is correct.

By contrast, a one-line `ButtonLink` such as:

```mdx
<ButtonLink href="https://app.querypie.com/">🚀 QueryPie AIを今すぐ体験する</ButtonLink>
```

can render without an inner `<p>`, so the same button class looks fine.

## Required investigation order

1. Check the live/stage page in the browser first.
2. Inspect the actual rendered CTA DOM.
3. Compare a broken page and a good page.
4. Only then inspect MDX source and shared renderer/styles.

Do not start by guessing from the MDX files alone.

## Browser workflow

Open the broken page and run a console probe like:

```js
(() => {
  const btn = [...document.querySelectorAll('main a')].find((a) => /を開く|体験する|入手する|申し込み/.test(a.textContent || ''));
  if (!btn) return null;
  const s = getComputedStyle(btn);
  const r = btn.getBoundingClientRect();
  const child = btn.firstElementChild;
  return {
    text: btn.textContent?.replace(/\s+/g, ' ').trim(),
    className: btn.className,
    width: Math.round(r.width),
    height: Math.round(r.height),
    bg: s.backgroundColor,
    color: s.color,
    childTag: child?.tagName || null,
    childMargin: child ? getComputedStyle(child).margin : null,
    childColor: child ? getComputedStyle(child).color : null,
    outer: btn.outerHTML,
  };
})();
```

What to look for:
- broken case: `childTag: "P"`, non-zero `childMargin`, child paragraph color inheriting article body color
- good case: no child wrapper or no `<p>` margin/color leak

## Files to inspect after browser proof

### Shared body/article shell
- `src/components/sections/publication-post-page.tsx`
  - especially `publicationBodyClassName`
  - watch for global descendant selectors like `[&_p]:...`
  - CTA selector currently lives here as `[&_.article-content-btn]:...`

### MDX button component
- `src/lib/publications/mdx/components.tsx`
  - `ButtonLink()`

### MDX renderer
- `src/lib/publications/mdx/renderer.ts`

### Affected content families
- `src/content/manuals/*.mdx`
- `src/content/introduction-deck/*.mdx`
- `src/content/whitepapers/*.mdx`
- `src/content/events/*.mdx`

## Fast repository checks

Search for multiline ButtonLink usage:

- `src/content/manuals/*.mdx` often uses:
  - opening tag on one line
  - label on next line
  - closing tag on third line
- many whitepapers use one-line `ButtonLink`, which is a useful control sample

Compare examples such as:
- broken-pattern style: `src/content/manuals/4-acp-api-reference.mdx`
- good-pattern style: `src/content/whitepapers/27.mdx`

## How to reason about the result

If the visual regression differs across pages but the shared button class is the same, first suspect:
1. MDX-generated wrapper elements (`<p>` inside `<a>`) 
2. article-body descendant styles leaking into CTA children
3. content authoring shape differences between families

Do not misdiagnose this as a thumbnail/sidebar/layout issue when the complaint is about the in-body CTA box.

## Likely fix options

### Minimal content fix
Normalize affected MDX to one-line `ButtonLink` usage where practical:

```mdx
<ButtonLink href="https://docs.querypie.com/ja/api-reference">QueryPie ACP OpenAPI Reference を開く</ButtonLink>
```

This is the safest fix when the issue is isolated to a few files.

### Manuals-specific remediation rule
For `src/content/manuals/*.mdx`, if the user says these entries are only link-hub pages and do not have their own true local content, treat both of the following as part of the fix:
- the in-body `ButtonLink` CTA must point to the final external documentation URL
- `relatedItems[*].href` should also point to external documentation URLs instead of local `/t/manuals/...` detail pages
- normalize the `ButtonLink` source to a single-line MDX form so the rendered CTA does not wrap its label in a paragraph element

In prior successful remediation, the practical safe fix was:
1. replace dead/local manuals CTA paths such as `/api-docs.html` with the real external docs URL
2. rewrite multiline ButtonLink blocks into one-line form
3. convert all manuals `relatedItems` hrefs to external docs destinations in the same batch
4. if a route title should include the product prefix, update both frontmatter `title` and the first in-body heading together so the detail page stays visually consistent

High-value repo finding:
- the stage-local `/api-docs.html` path was a dead 404 during investigation, so leaving manuals CTA links on that local path is incorrect
- resolve the final external documentation target from the live docs site rather than guessing

Reliable URL resolution workflow for manuals:
1. Open `https://docs.querypie.com/ja`
2. Inspect the live top-nav / page links
3. Read the actual hrefs for the relevant docs destinations

Confirmed mappings discovered during prior use:
- ACP docs home: `https://docs.querypie.com/ja`
- Administrator Manual: `https://docs.querypie.com/ja/administrator-manual`
- User Manual: `https://docs.querypie.com/ja/user-manual`
- Release Notes: `https://docs.querypie.com/ja/release-notes`
- ACP API Reference: `https://docs.querypie.com/ja/api-reference`
- ACP Community Edition install guide: `https://docs.querypie.com/installation/querypie-acp-community-edition`
- AIP user guide: `https://aip-docs.app.querypie.com/ja/user-guide`

Also normalize related-card labels when needed. Example: if a manuals related card says only `API Docs`, prefer the explicit product title `QueryPie ACP OpenAPI Reference` when that is the actual destination.

### Structural component fix
Harden `ButtonLink` or article-body styles so paragraph wrappers cannot break the CTA:
- style `.article-content-btn p` to reset margin/color
- or make `ButtonLink` normalize children into inline content
- or add a descendant reset under `.article-content-btn`

Use this if many families are affected and you want a systemic fix.

## Recommended evidence to report

Summarize with:
1. exact broken page and exact good page compared
2. actual DOM difference (`<a><p>...</p></a>` vs `<a>text</a>`)
3. exact leaking selectors in `publicationBodyClassName`
4. exact MDX source pattern difference
5. smallest safe fix options

## Additional routing/debugging lesson for file links

A `ButtonLink` issue in this repo is not always purely visual. For same-origin file-like paths such as `.pdf`, the current `ButtonLink` implementation can also cause broken navigation behavior.

### High-value finding

`ButtonLink` currently treats only absolute `http(s)` URLs as external:

```ts
function isExternalHref(href: string) {
  return /^https?:\/\//.test(href);
}
```

So a same-origin file URL like:

```mdx
<ButtonLink href="/introduction-deck/1/QueryPie_AIP_Intro_JP.pdf">
  QueryPie AIP 製品紹介書を開く
</ButtonLink>
```

is rendered with Next `<Link>` instead of a plain `<a>`.

That means the first click is handled by the client router as an internal app navigation, not as a direct static file request.

### Symptom pattern

Users may report:
- first click shows a 404 or wrong page
- reloading the destination makes the PDF appear
- direct URL open in a new tab works
- `curl -I` to the PDF URL returns `200 application/pdf`

### Why this happens

In `corp-web-japan`, static files under `public/` can share a path prefix with app routes.

For the introduction-deck example:
- direct file request to `/introduction-deck/1/QueryPie_AIP_Intro_JP.pdf` returns the PDF
- but the app also has detail routes under `/t/introduction-deck/[id]/[slug]`
- client-side navigation can interpret the PDF path as an internal route-like transition first
- a refresh then reissues a full document request, which lets the server return the real static PDF

A strong confirmation pattern is:
- direct file URL -> `200`, `content-type: application/pdf`
- stage article/source page contains `ButtonLink href="/…pdf"`
- server-rendered output shows the CTA emitted as Next `Link` rather than plain anchor

### Required investigation order for file-link bugs

1. Test the reported PDF/file URL directly with `curl -I`.
2. Verify the source file exists under `public/...` in the repo.
3. Search the MDX/content source that authored the CTA.
4. Inspect `ButtonLink` and `isExternalHref()` in `src/lib/publications/mdx/components.tsx`.
5. Compare direct-request behavior vs in-app click behavior.

### Practical conclusion to report

If the direct file URL returns `200` but in-app clicking is flaky, report the root cause as:
- the file exists
- the problem is the MDX `ButtonLink` rendering same-origin file URLs through Next client routing
- the fix is to render file-like hrefs (`.pdf`, and similar static assets if applicable) as plain `<a>` elements instead of Next `<Link>`

### Likely fix directions

Prefer one of these minimal fixes when asked to patch:
1. add an explicit `external?: boolean` prop to `ButtonLink` and render `external={true}` as a plain `<a target="_blank" rel="noopener noreferrer">...` so same-origin static files can opt out of Next client routing without changing the shared default for ordinary internal links
2. if a broader systemic policy is desired later, update `ButtonLink` so file-like hrefs such as `.pdf` are treated like external/static links automatically and rendered as `<a>`
3. or, for a one-off case, rewrite the specific CTA to a plain `<a>`/external-style link instead of `ButtonLink`

### Proven implementation pattern for explicit opt-in

A successful minimal implementation in `corp-web-japan` was:

1. extend `ButtonLinkProps` in `src/lib/publications/mdx/components.tsx`

```ts
type ButtonLinkProps = {
  href: string;
  children?: ReactNode;
  external?: boolean;
};
```

2. update the component to respect the prop

```ts
function ButtonLink({ href, children, external = false }: ButtonLinkProps) {
  if (external || isExternalHref(href)) {
    return (
      <a href={href} className="article-content-btn" target="_blank" rel="noopener noreferrer">
        {children}
      </a>
    );
  }

  return (
    <Link href={href} className="article-content-btn">
      {children}
    </Link>
  );
}
```

3. opt affected same-origin PDFs into the new behavior at the MDX callsite, for example:

```mdx
<ButtonLink href="/introduction-deck/1/QueryPie_AIP_Intro_JP.pdf" external={true}>
  QueryPie AIP 製品紹介書を開く
</ButtonLink>
```

4. add a small source-level regression test that verifies both:
- `ButtonLink` supports `external?: boolean`
- the affected MDX files actually use `external={true}`

This explicit-opt-in approach is a good default when the user wants a narrow fix with low routing risk.

## Pitfalls

- Blaming the `ButtonLink` class alone without checking rendered child markup
- Looking only at source MDX and not the browser DOM
- Missing that descendant body styles in `PublicationPostPage` affect nested `<p>` inside CTA links
- Confusing the in-body CTA issue with sidebar related-resource card styling
- Assuming a reported PDF 404 means the file is missing before testing the direct URL
- Missing that same-origin static files can break only when navigated through Next `<Link>`

## Done criteria

You are done when you can name:
- the broken page and the good comparison page
- the rendered DOM difference inside the CTA
- the exact shared style selectors causing the leak
- whether the fix should be content-only or systemic

---
name: corp-web-japan-font-stack-regression-debugging
description: Diagnose corp-web-japan font regressions where article/body text falls back to Times or English link text looks mismatched after font pipeline changes.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, fonts, next-font, css-variables, debugging, typography]
    related_skills: [systematic-debugging, corp-web-japan-font-pr-workflow]
---

# corp-web-japan font stack regression debugging

Use this when the user reports that English text in article links looks like a different font, or when body/article typography in `corp-web-japan` appears serif / Times-like instead of the intended brand sans stack.

## Symptom pattern

Typical complaint:
- English characters in external links look different from surrounding text
- Article body on `stage.querypie.ai` looks wrong even though link color/underline are correct
- Computed font may show `Times` instead of Mona Sans / Pretendard JP

Important finding: this usually is **not a link-only style bug**. It is often a **global font stack resolution failure** that becomes most visible on English link text.

## Proven investigation flow

### 1. Confirm whether the issue is link-only or whole-body fallback

Use browser console on the affected page and compare computed styles for:
- `body`
- `main`
- `h1`
- a normal article paragraph
- `strong`
- an external link in the article body

Example checks:
- `getComputedStyle(document.body).fontFamily`
- `getComputedStyle(document.querySelector('main a[href^="http"]')).fontFamily`
- `getComputedStyle(document.querySelector('main p')).fontFamily`

Interpretation:
- If all or most of them resolve to `Times`, the bug is global font fallback, not anchor styling.
- The English link text only *appears* uniquely wrong because serif/sans differences are much more obvious on Latin glyphs than on JP text.

### 2. Inspect font variables live in the browser

For this repo, check these variables:
- `--font-app-sans`
- `--font-sans`
- `--font-mona-sans`
- `--font-pretendard-jp`

Read them from both `document.documentElement` and `document.body` via `getComputedStyle(...)`.

Known failure pattern:
- `--font-mona-sans` and `--font-pretendard-jp` exist on `body`
- `--font-app-sans` and/or `--font-sans` resolve empty
- computed `font-family` falls back to `Times`

This points to a broken CSS variable chain rather than a missing `a { font-family: ... }` rule.

### 3. Check the two canonical files together

Always inspect both:
- `src/app/layout.tsx`
- `src/app/globals.css`

Current architecture to understand:
- `layout.tsx` may inject `next/font/local` variables on `<body>`
- `globals.css` may define `--font-app-sans` at `:root`
- Tailwind `font-sans` is wired through `--font-sans` -> `--font-app-sans`

Danger pattern:
- `:root` defines `--font-app-sans: var(--font-mona-sans), var(--font-pretendard-jp), ...`
- but `--font-mona-sans` / `--font-pretendard-jp` only exist on `<body>` from `next/font/local`
- result: the root-level variable chain can fail and `font-sans` may collapse to fallback serif

### 4. Use git history to identify which font refactor introduced it

Inspect commits affecting:
- `src/app/layout.tsx`
- `src/app/globals.css`

Useful commands:
- `git log --oneline --all -- src/app/layout.tsx src/app/globals.css`
- `git show <commit> -- src/app/layout.tsx src/app/globals.css`
- `git blame -L <range> src/app/globals.css`
- `git blame -L <range> src/app/layout.tsx`

Known repo history from Apr 2026:
- `92b8985` (JK): simple self-hosted `@font-face` + `"QueryPie Sans"` stack; not the cause
- `15ff0a6` (Chikako): restored the simpler PR #48 setup; not the cause
- `81895f5` (Chikako): split Mona Sans / Pretendard JP into separate `next/font/local` variables and changed `--font-app-sans` to reference those vars; this is the likely root-cause commit for Times fallback
- `b6d6eca` (Chikako): added `html` inline `fontFamily` as a partial workaround; not the original cause, and it may not fix `body.font-sans`

## Root cause statement you can reuse

When this regression appears, the likely root cause is:

`font-sans` depends on `--font-app-sans`, but `--font-app-sans` is defined at `:root` using `var(--font-mona-sans)` / `var(--font-pretendard-jp)` while those `next/font/local` variables are only injected on `<body>`. That variable chain can resolve empty, causing article/body text to fall back to `Times`.

## What NOT to conclude too early

Do not assume:
- external links have a special font rule
- `strong` inside links is the cause of the font-family mismatch
- only article MDX rendering is broken
- ToC/article component CSS is the font culprit

The article shell may be fine; the global font variable pipeline is usually the real issue.

## Separate font-family bugs from link color/weight bugs

After the font-family issue is understood, you may still see article links rendering differently by position. In `PublicationPostPage.tsx`, the body style currently combines:
- `[&_a]:text-[#2563EB]` + underline rules
- `[&_strong]:font-medium [&_strong]:text-slate-950`

This creates a second, independent issue:
- plain `<a>` links appear blue
- `<a><strong>...</strong></a>` links appear dark because the inner `strong` overrides the link color
- the mismatch is caused by markup structure plus descendant selectors, not by a different font-family

### Proven inspection pattern for article link inconsistencies

When a user says some inline article links are blue and others dark:
1. Inspect `src/content/blog/<id>.mdx` and compare link markup
2. Check whether the dark examples are wrapped as `<a><strong>...</strong></a>` or `**<a>...</a>**`
3. Check whether the blue examples are plain `<a>...</a>`
4. Confirm in DevTools / browser console whether the computed difference is color / font-weight only, while `font-family` is the same

### Production parity guidance for inline text links

For `querypie.com/ja` article pages, the observed pattern is:
- most inline reference links use body-colored text rather than blue
- some self-referential / next-action links (for example linked whitepapers) are selectively blue and underlined
- related-content cards and sidebar links are not generally made blue just because they are internal links; they are differentiated mostly by layout/card treatment

Do not generalize this as "all internal links should be blue." A better parity rule is:
- default inline reference links: body-colored
- selectively emphasized self-referential inline CTA links: blue + underline
- related/sidebar links: keep body/card styling unless the design explicitly calls for CTA emphasis

## Recommended fix direction

After confirming the root cause, use the proven minimal fix for the current split `next/font/local` architecture:
- keep `localFont(... variable: "--font-mona-sans")` and `localFont(... variable: "--font-pretendard-jp")`
- move those two variable classes from `<body>` to `<html>` in `src/app/layout.tsx`
- keep `<body className="font-sans antialiased">` without the font variable classes
- remove any inline `html style={{ fontFamily: ... }}` workaround once the variables are scoped correctly on `<html>`

Why this works:
- `globals.css` defines `--font-app-sans` using `var(--font-mona-sans), var(--font-pretendard-jp), ...`
- those variables must exist at or above the scope where `font-sans` is resolved
- putting the variable classes on `<html>` makes the chain resolve consistently for `body`, headings, article text, and links

### Proven verification pattern

1. Run a source-level regression test that locks the contract:
- `layout.tsx` attaches `${monaSansFont.variable} ${pretendardJPFont.variable}` on `<html>`
- `body` keeps `font-sans antialiased`
- `layout.tsx` no longer relies on `fontFamily:` inline styling as a workaround

2. Run at least:
- `node --test tests/font-and-mobile-layout.test.mjs`
- `npm run build`

3. Verify in a browser on a real article page such as `/blog/28/ai-security-threat-map-2026-cxo`:
- `body`, `h1`, a normal paragraph, and an external link should all resolve to the Mona Sans / Pretendard JP stack
- none of them should resolve to `Times`

### Fallback rollback test

If the user asks whether the older JK font setup fixed the bug, you can verify by checking out commit `92b8985` in a temporary worktree and measuring computed fonts in the browser. In prior validation, that commit restored:
- body/article/external-link font-family to `"QueryPie Sans", ...`
- and eliminated the `Times` fallback

## Done criteria

- Browser computed `font-family` on `body`, article paragraphs, headings, and external links is no longer `Times`
- Font behavior is explained by commit history, with the introducing commit identified
- Any workaround-only commit is distinguished from the true introducing commit
- The repo contains a regression test that protects the correct variable scoping contract

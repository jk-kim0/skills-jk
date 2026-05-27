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

## Cross-site font loading comparison notes

Use this when the complaint is not a wrong font-family, but a perceived difference like:
- one live `www.querypie.com/ja/...` page appears to apply the custom font quickly
- the corresponding stage site appears to apply it slowly

### 1. Use the exact page the user named

Do not silently replace the requested production URL with some other JP page just because `/ja` may redirect somewhere else.

Important lesson:
- `https://www.querypie.com/ja` may redirect to `https://querypie.ai/`
- but deeper `www.querypie.com/ja/...` pages can stay on `www.querypie.com`
- for example, `https://www.querypie.com/ja/solutions/aip` stayed on that exact URL in live testing

So the rule is:
- compare the exact production page the user asked about
- record the final resolved URL from the browser
- do not generalize root-path redirect behavior to deeper paths

### 2. Compare these browser-side facts in order

For both prod and stage, capture:
1. final URL
2. `body` / `h1` / visible paragraph computed `font-family`
3. `link[rel="preload"][as="font"]` list
4. `performance.getEntriesByType("resource")` filtered to font files
5. `document.fonts` status
6. live `@font-face` rules from loaded stylesheets

If those match, the issue is usually not a basic font wiring mismatch.

### 3. Compare HTTP cache policy separately from cache warmth

Fetch the HTML and actual font asset URLs directly and compare:
- `Cache-Control`
- `X-Vercel-Cache`
- `Age`
- `ETag`
- `Content-Length`
- `Last-Modified`

Important interpretation:
- same `Cache-Control` means the policy is the same
- different `Age` usually means different cache warmth / recent deployment state
- same `ETag` and `Content-Length` strongly suggest the font file content is identical

### 4. Run repeated trials before concluding stage is slower

A single browser run is not enough for this comparison.

Proven workflow:
- run at least 3 independent browser trials when the claim is about perceived loading speed
- collect per-trial timing for:
  - Mona Sans duration
  - Pretendard JP duration
  - `DOMContentLoaded`
  - `load`
- summarize mean values and how many trials each side was faster

Why this matters:
- one run may be dominated by transient cache/CDN state
- a second or third run can reverse the first impression
- in the `www.querypie.com/ja/solutions/aip` vs `stage.querypie.ai` comparison, the first run alone suggested one story, but the 3-trial aggregate showed stage was faster overall on average

### 5. Page-to-page mismatch can dominate the result

Do not over-interpret results when comparing different route types.

Example lesson from live measurement:
- production `www.querypie.com/ja/solutions/aip` is a deep solution detail page
- stage `stage.querypie.ai/` is the homepage
- production preloaded an extra `JetBrains Mono` asset that remained unloaded for normal visible text

So if the pages are not the same route/content type, part of the timing difference may be page-specific rather than environment-specific.

### 6. Reporting guidance for cross-site timing complaints

When reporting results, distinguish clearly between:
- font policy differences
- cache warmth differences
- page-specific asset-loading differences
- actual repeated-trial timing trend

A safe reusable conclusion pattern is:
- no evidence of a different font cache policy if headers and `@font-face` match
- no evidence of a font-family/config regression if computed styles match
- avoid calling stage slower unless repeated trials consistently show it
- if only different page types were compared, explicitly say the result is not fully apples-to-apples

## Done criteria

When users report that `querypie.com` applies the custom font quickly but `stage.querypie.ai` feels slow, do not assume a cache-header mismatch first.

### Proven comparison checklist

Compare both live sites for:
- `performance.getEntriesByType('resource')` filtered to font files
- `document.fonts` status
- `link[rel="preload"][as="font"]`
- `@font-face` rules and `font-display`
- response headers for HTML and font assets (`Cache-Control`, `Age`, `X-Vercel-Cache`, `ETag`)

### Key finding pattern

A common outcome is:
- both prod and stage font files use the same long-lived asset caching, typically `Cache-Control: public,max-age=31536000,immutable`
- both preload the fonts and use `font-display: swap`
- the perceived difference comes instead from **which font is needed above the fold**

Interpretation:
- `querypie.com` home is English-first, so the small Mona Sans font (~137 KB) is enough to make the first viewport look "correct" quickly
- `stage.querypie.ai` home is Japanese-first, so it needs the large Pretendard JP variable font (~5.3 MB) for first-viewport text
- with `font-display: swap`, stage shows fallback first and then visibly swaps once the large JP font finishes loading
- prod may also download the large JP font slowly, but if that font is not actually needed for the first viewport, users perceive the site as fast anyway

### Important cache nuance

Even if the font content is identical, prod and stage do **not** share browser cache in practice when:
- the origins differ (`www.querypie.com` vs `stage.querypie.ai`)
- the emitted asset URLs differ

So a user who already visited prod does not necessarily get a cache hit for the same font on stage.

### Reusable root-cause statement

If headers match but stage still feels slower, the likely cause is not weaker font caching. It is that stage's first viewport depends on a very large Japanese font file, while prod's first viewport appears correct after only the small Latin font loads; cross-origin and different asset URLs also prevent practical cache reuse between prod and stage.

### Optimization directions to suggest

If asked for fixes, prioritize:
1. subsetting or splitting the Japanese font
2. reducing first-viewport dependence on the full JP variable font
3. page- or locale-specific preload strategy rather than always preloading the full large font
4. remembering that frequent stage deploys reduce warm-cache benefits because asset URLs churn

### Proven implementation path for corp-web-japan

When the goal is to keep the PR #104 correctness fix but materially reduce JP font cost, the strongest practical baseline is:
- keep Mona Sans on `next/font/local` with the html-scoped variable class from PR #104
- remove the full `PretendardJPVariable.woff2` variable file from the runtime font path
- replace JP with static subset files for the weights the repo actually uses
- preload only one representative JP body weight first, and let heavier JP weights load on demand

Important lesson from implementation:
- a two-file JP swap (for example only 400 and 700) is not a complete replacement if the repo actively uses 500 and 600 in headings, buttons, badges, and section labels
- for this repo, inspect actual weight usage first; current code uses 400/500/600/700 in practice, with especially heavy use of 500 and 600 utility classes
- if only one JP file should preload, 400 is the safest representative body weight; do not preload the whole JP family by default

A proven repo-level implementation is:
- `Mona-Sans.woff2` remains managed by `next/font/local` on `<html>`
- generate `PretendardJPSubset-400.woff2`, `PretendardJPSubset-500.woff2`, `PretendardJPSubset-600.woff2`, and `PretendardJPSubset-700.woff2` from `PretendardJPVariable.woff2`
- subset to JP/CJK ranges such as `U+3000-303F,U+3040-309F,U+30A0-30FF,U+31F0-31FF,U+3400-4DBF,U+4E00-9FFF,U+F900-FAFF,U+FF01-FF60,U+FF65-FF9F`
- place the JP subset files under `public/fonts/` so preload URLs are stable and explicit
- define one `@font-face` family, for example `Pretendard JP Subset`, across weights 400/500/600/700 in `src/app/globals.css`
- set `--font-pretendard-jp: "Pretendard JP Subset"` and keep `--font-app-sans: var(--font-mona-sans), var(--font-pretendard-jp), ...`
- add `src/app/head.tsx` that preloads only `/fonts/PretendardJPSubset-400.woff2`
- do not keep JP on a second `localFont()` definition if the preload strategy needs per-weight control; `@font-face` + explicit preload is clearer and more controllable than trying to partially preload one `localFont()` family

Measured size guidance from this repo's assets:
- original `PretendardJPVariable.woff2`: about 5.10 MiB
- subset static 400: about 1.15 MiB
- subset static 500: about 1.20 MiB
- subset static 600: about 1.21 MiB
- subset static 700: about 1.22 MiB

This keeps the PR #104 Mona/font-scope correctness fix intact while turning the JP side into a weight-complete static family with a fast-path preload strategy.

### Measured asset sizes and practical recommendation

In `corp-web-japan`, the important real-world size finding is:
- `Mona-Sans.woff2` is about 134 KiB
- `PretendardJPVariable.woff2` is about 5.10 MiB

This means the dominant performance problem is **not** Mona Sans and not the CSS mechanism by itself; it is the very large JP variable font.

Useful measured checkpoints:
- current JP unicode-range subsetting of the existing Pretendard variable font still lands around **2.99 MiB**
- instancing Pretendard JP to a static weight and then subsetting gives much better results:
  - JP weight 400 subset: about **1.15 MiB**
  - JP weight 700 subset: about **1.22 MiB**
- instancing Mona Sans to a static weight and Latin subsetting gives about **57 KiB**, but Mona is not the main bottleneck

Interpretation:
- switching between `next/font/local` and `@font-face` alone does **not** solve the main loading problem if the site still ships the same 5 MiB JP variable font
- `unicode-range` is useful for explicit script assignment and download control, but it is **not** the main win if the underlying asset remains huge
- for this repo, the best correctness baseline is still the PR #104-style fix: keep `next/font/local`, scope the font variables on `<html>`, and keep `body` on `font-sans`
- for performance, the best next step is to replace the full Pretendard JP variable font with **subsetted static JP weights** (for example 400 and 700) rather than preload the full 5.10 MiB variable file site-wide

### Preferred architecture when both correctness and speed matter

Recommended approach for future work in this repo:
1. keep the PR #104 variable-scoping contract for correctness
2. preload Mona Sans if needed for above-the-fold Latin brand text
3. stop site-wide preloading of the full Pretendard JP variable font
4. ship JP fonts as subsetted static weights (start with 400 and 700 unless design proves more are needed)
5. preload only the minimum JP weight actually needed above the fold

This is the most robust conclusion from recent debugging: **PR #92 introduced the structural regression, PR #104 fixed correctness, and the real performance win comes from replacing the oversized JP variable font rather than debating CSS font wiring alone.**

## Done criteria

- Browser computed `font-family` on `body`, article paragraphs, headings, and external links is no longer `Times`
- Font behavior is explained by commit history, with the introducing commit identified
- Any workaround-only commit is distinguished from the true introducing commit
- The repo contains a regression test that protects the correct variable scoping contract

---
name: corp-web-japan-font-loading-performance-investigation
description: Investigate perceived font-loading regressions between live corp-web-japan environments, validate actual runtime font behavior in the browser, and distinguish source-level intent from built/live output.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, fonts, performance, nextjs, preload, debugging, browser]
    related_skills: [systematic-debugging, corp-web-japan-font-stack-regression-debugging, github-issues]
---

# corp-web-japan font loading performance investigation

Use this when the user reports that custom fonts appear to apply faster/slower across `corp-web-japan` environments such as:
- `https://www.querypie.com/ja/...`
- `https://stage.querypie.ai/...`
- a PR deployment after a font-loading change

This skill is specifically for **runtime font-loading behavior**, not font-family fallback regressions like Times/serif issues.

## Critical first rule: compare the actual requested route

Do **not** substitute a different production route just because another page redirects.

Proven pitfall:
- `https://www.querypie.com/ja` may redirect elsewhere
- but `https://www.querypie.com/ja/solutions/aip` can remain on `www.querypie.com`

If the user asks to compare `www.querypie.com/ja/...` against stage, you must test that exact route family.

## Investigation goals

You need to determine:
1. whether the live environments actually use different font-loading behavior
2. whether the difference is due to cache policy, cache warmth, route-specific content, or runtime output differences
3. whether source-level intent (for example a preload in `src/app/head.tsx`) is really present in built/live HTML

## Proven workflow

### 1. Reproduce in a real browser

For each target URL, collect from the live browser:
- final resolved URL
- page title
- computed `font-family` for `body`, `h1`, and a visible paragraph
- `document.fonts` entries with family / status / weight
- `<link rel="preload" as="font">` entries
- `@font-face` rules from loaded stylesheets
- resource timing for font files:
  - name
  - initiatorType
  - transferSize
  - encodedBodySize
  - duration
  - startTime
  - responseEnd
- navigation timing:
  - DOMContentLoaded
  - load

Important: measure the exact production page and the exact stage page, not approximate equivalents unless the user explicitly allows that.

### 2. Repeat at least 3 times before concluding directionality

Single-run conclusions can be misleading.

For each environment, run 3 independent browser measurements and compute:
- mean duration for the primary Latin font resource
- mean duration for the primary Japanese font resource(s)
- mean DOMContentLoaded
- mean load
- number of trials where stage was faster/slower

When post-change architecture uses multiple JP subset files instead of one variable font, report:
- per-weight durations (400 / 500 / 600 / 700 if applicable)
- earliest subset completion time per trial
- total JP bytes if all subset files loaded on the page

## Header and cache validation

Check HTTP headers for:
- HTML document
- each main font asset

Record at least:
- `Cache-Control`
- `Age`
- `X-Vercel-Cache`
- `ETag`
- `Content-Length`
- `Last-Modified`

Interpretation guidance:
- identical `Cache-Control` does **not** mean equivalent runtime behavior
- `Age` can reveal cache warmth differences at the edge
- different origins mean browser cache is not shared even if the file bytes match

## Root-cause checklist for subset-font PRs

If a PR claims to improve JP loading by splitting a variable font into subset files, verify all of the following:

### A. Was the old variable font actually removed on live?
Check whether live `@font-face` still references something like:
- `PretendardJPVariable`

If not, confirm the subset family is live.

### B. Did the intended preload actually reach built/live HTML?
This is the most important lesson from Apr 2026.

A source-level preload in `src/app/head.tsx` may exist while **not appearing in built output**.

Do not trust source alone.

Always verify in both places:
1. local production build output
2. live HTML/DOM on the deployed environment

Run:
- `npm run build`
- inspect `.next/server/app/index.html` (or the route-specific built HTML when applicable)
- search for the expected preload target such as `/fonts/PretendardJPSubset-600.woff2`

If the built HTML lacks the preload, report that the current preload mechanism is ineffective in practice for the current Next version/runtime path.

### C. Are all subset weights still being loaded because the page genuinely uses them?
Measure live font weights used by rendered text.

Recommended browser check:
- collect computed `fontWeight` counts across visible text elements
- collect a second count for only elements in the initial viewport

Interpretation:
- if the first viewport already uses 400 / 500 / 600, the browser will naturally request multiple subset files
- splitting by weight alone will not produce a large network win if the UI still depends on many weights above the fold

### D. Compare total JP bytes before vs after
Example pattern:
- before: one `PretendardJPVariable` file ~5.35 MB
- after: 4 subset files totaling ~5.02 MB

If all subset files still load, total byte savings may be small (for example ~6%), even though the architecture changed.

## Important conclusion patterns

### Pattern 1: headers same, runtime still differs
Likely causes:
- cache warmth (`Age`)
- different route/content surfaces
- different asset initiation timing
- browser cache split by origin

### Pattern 2: PR deployed, but intended preload effect missing
Likely cause:
- source-level preload path did not survive to built/live HTML

This happened in corp-web-japan with:
- `src/app/head.tsx` containing a subset preload
- but `.next/server/app/index.html` and live stage HTML showing only Mona Sans preload

### Pattern 3: subset splitting deployed, but large improvement not visible
Likely causes:
- all subset weights still needed by the page
- preload not emitted
- above-the-fold content uses too many JP weights

## Reporting structure for GitHub issues/comments

When writing the issue or follow-up comment:

### English first, Japanese translation second
Use this order explicitly:
1. English report
2. `## Japanese translation`
3. Japanese translation of the report

### Include numeric tables
Prefer:
- per-trial timing table
- aggregated statistics table
- before vs after table for follow-up PR validation

### For post-PR follow-up, separate these clearly
1. what changed structurally on live
2. what improved measurably
3. what did not improve yet
4. likely root cause(s)
5. concrete fix directions

## Proven fix directions

When the issue is that the intended behavior was not achieved, the strongest recommendations are:

### Fix direction 1: use a preload mechanism verified in built HTML
Do not assume `src/app/head.tsx` is sufficient.

Proven implementation from Apr 2026 in this repo:
- remove `src/app/head.tsx` for the JP subset font preload path
- import `preload` from `react-dom` in `src/app/layout.tsx`
- call:
  - `preload("/fonts/PretendardJPSubset-600.woff2", { as: "font", type: "font/woff2", crossOrigin: "anonymous" })`
  inside `RootLayout()` before returning the JSX

Why this was needed:
- source-level `src/app/head.tsx` looked correct
- but `npm run build` showed no `/fonts/PretendardJPSubset-600.woff2` preload in `.next/server/app/index.html`
- after moving to `react-dom` `preload()` in `layout.tsx`, the built homepage HTML emitted both the Mona Sans preload and the JP subset preload as intended

Recommended regression checks after implementing:
- source-level test asserts:
  - `layout.tsx` imports `preload` from `react-dom`
  - `layout.tsx` contains the `preload("/fonts/PretendardJPSubset-600.woff2", ...)` call
  - `src/app/head.tsx` is absent
- build-output verification asserts:
  - `.next/server/app/index.html` contains `/fonts/PretendardJPSubset-600.woff2`
  - live stage HTML/DOM also contains that preload

Done criteria:
- expected font preload appears in local built HTML
- same preload appears in live HTML/DOM
- performance entry shows preload-driven request behavior

### Fix direction 2: reduce above-the-fold JP weight diversity
If first viewport uses 400 / 500 / 600 / 700, browser will fetch many files.

Done criteria:
- fewer JP weights used in the initial viewport
- homepage first render no longer needs all subset weights

### Fix direction 3: add build-output regression tests
Source-level tests alone are insufficient.

Add tests that verify:
- built homepage HTML contains the expected subset preload
- built output does not reference the removed variable font

## Done criteria

You are done when:
- the exact requested routes were compared
- browser measurements were repeated at least 3 times
- header differences and cache warmth were documented
- built output was checked, not just source
- live output was checked, not just build
- root cause was separated into source-intent vs runtime-output issues
- the issue/comment includes concrete next fixes, not just observations

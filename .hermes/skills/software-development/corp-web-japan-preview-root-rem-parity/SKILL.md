---
name: corp-web-japan-preview-root-rem-parity
description: Preserve visual parity when importing QueryPie public pages into corp-web-japan while the source site may use a 15px html root and corp-web-japan intentionally keeps a 16px root.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, preview, typography, rem, parity, static-page, migration]
---

# corp-web-japan preview root-rem parity

Use this when copying or recreating UI design from `querypie.com/ja/**` or `querypie.com/en/**` into `corp-web-japan` preview routes.

## Core finding
Source QueryPie public pages can render under `html { font-size: 15px; }`, while `corp-web-japan` should keep the more standard `html { font-size: 16px; }`.

Because of that, do not blindly copy source computed pixel values into corp-web-japan.

## Important distinction
DevTools can show two different but both-correct values:
- author/token value in CSS rules, e.g. `--rem-52px` or `3.25rem`
- final computed value, e.g. `48.75px`

Example:
- source token: `3.25rem`
- source root: `15px`
- source computed size: `48.75px`
- preview root: `16px`
- preview token-equivalent size: `52px`

## Rule
If corp-web-japan keeps 16px root, preserve the source token/design intent and convert values for the 16px-root environment instead of copying 15px-root computed output.

Important override learned from real preview-page follow-up work:
- if the user explicitly says the preview page should follow the website's shared typography system rather than remain a one-off parity exception,
- do **not** force the source page's computed text sizes onto the preview just because they were measured from the live page.
- In that case, prefer the repo's established shared text tokens/patterns for the relevant content type (for example marketing/company body copy vs publication/article body), while still keeping the 16px root.
- Practical example: a live company page paragraph rendered at `15px / 24.375px` under a `15px` root, but the user later asked for site-wide consistency. The correct outcome was to stop treating that page as a typography exception and switch the preview page to the repo's shared body pattern instead.

## Calculations
- `final_px = rem_value * source_root_px`
- `rem_value = computed_px / source_root_px`
- then rebuild in preview with `preview_px = rem_value * 16`

## Decision order
1. inspect the source page's exact computed values and root font size
2. inspect the repo's existing shared typography patterns for comparable pages/components
3. decide whether the task priority is:
   - source-page visual parity, or
   - site-wide consistency inside corp-web-japan
4. if parity wins, convert source token intent for the 16px-root preview environment
5. if site-wide consistency wins, use the repo's shared typography values instead of preserving the source page's special-case used values

## Also convert consistently
Do this for:
- title/body font sizes
- line heights
- button padding
- border radius
- gap
- icon sizes

## Site-wide typography rule comes before blind live-value copying
A practical follow-up lesson from `/t/about-us`:
- sometimes the live source page computes body copy at `15px` only because the source site runs under `html { font-size: 15px; }`
- if `corp-web-japan` intentionally keeps a `16px` root and already has a shared/default body typography convention, do not preserve the source page's smaller computed body text just for numeric parity
- instead, prefer the repository's shared body-copy style when the user asks for site-wide consistency rather than route-specific visual exception matching

Practical rule:
- for route-level preview pages in `corp-web-japan`, first check whether the repo already has a common body text pattern such as `text-base leading-8 text-slate-600`
- if the user explicitly wants the page to match the overall website's default typography, upgrade imported `15px`/`24.375px` body copy to that shared site-wide body style instead of freezing the live page's 15px-root used value
- reserve exact smaller-value preservation for cases where the user explicitly prioritizes visual parity with the source page over site-wide consistency

Example:
- source live body copy: root `15px`, computed `15px / 24.375px`
- preview site root: `16px`
- site-wide default body copy in `corp-web-japan`: `text-base leading-8 text-slate-600`
- if the user wants consistency with `/news`, `/whitepapers`, top page, and solutions pages, prefer `text-base leading-8` for the preview route body copy

## Verification
1. inspect source `html` root font size
2. inspect source exact element rule/token and computed style
3. keep corp-web-japan root at 16px
4. rebuild token-equivalent values in preview
5. compare live and preview in the browser on the exact preview deployment URL

## Route lookup pitfall for company pages
Do not assume guessed `querypie.com/ja/<slug>` paths are the correct live source for company-family pages.

Practical lesson:
- `about-us` and `certifications` can live under `querypie.ai/<slug>` and then resolve to `www.querypie.com/ja/company/<slug>`
- guessed paths like `www.querypie.com/ja/about-us` or `www.querypie.com/ja/certifications` can 404 even though the real page exists elsewhere

Required check before measuring typography:
1. open the exact user-requested source domain/path first
2. if it redirects, measure the final live destination that actually renders the page
3. only treat a page as missing after checking the real redirect target or canonical live path

## Legal/cookie pages: detect 15px-root values hardcoded into a 16px-root page
When comparing a corp-web-japan preview legal/cookie page against `www.querypie.com/ja/**`, do not stop after confirming both pages currently report `html { font-size: 16px; }`.

A preview page can still contain hardcoded pixel values that were copied from a 15px-root computed rendering. Look for repeated 0.9375 scaling versus live values:
- live `60px / 72px` h1 vs preview `56.25px / 67.5px` means preview captured `3.75rem / 4.5rem` under a 15px root; reconstruct as `60px / 72px` for a 16px-root page.
- live `20px / 28px` section labels vs preview `18.75px / 26.25px` means preview captured `1.25rem / 1.75rem`; reconstruct as `20px / 28px`.
- live body/category descriptions `16px / 26px` vs preview `15px / 24.375px` means preview captured `1rem / 1.625rem`; reconstruct as `16px / 26px`.

For legal document defaults, separate short cookie-preference parity from long-document readability:
- cookie/list description parity candidate: `16px / 26px`, weight 300, tracking about `0.36px`, `#57606A`/`text-slate-600`.
- long legal MDX body candidate: `16px / 28px` is usually calmer and more readable than preserving `15px`; if current legal components use `text-[15px] leading-7`, consider raising only the font-size to `16px` while keeping `leading-7`.
- lead/intro paragraphs may be intentionally larger on live pages (for example `18px / 28px`); do not apply that size blindly to every legal body paragraph.

## When the user wants one shared company-body size across several pages
Default parity advice is page-specific, but the user may explicitly ask for one shared body size across multiple company pages such as `about-us`, `certifications`, and `contact-us`.

In that case:
- do not average blindly or keep the smallest measured page value just because one source page computes smaller under a 15px root
- first identify the dominant shared token family among the requested pages
- convert that family into the 16px-root environment, then apply one common token to the user-named pages only

Practical lesson from company-page follow-up work:
- source `certifications` and `contact-us` body copy measured `16.875px / 26.25px` at a `15px` root
- that corresponds to a `1.125rem / 1.75rem` token family
- in corp-web-japan's 16px-root environment, the strict token-equivalent reconstruction is `18px / 28px`, not `15px / 28px`
- however, if the user wants one shared body size across `about-us`, `certifications`, and `contact-us`, treat `18px / 28px` as the upper bound candidate, not an automatic final answer
- a user can still find the mathematically reconstructed `18px` too large in the 16px-root preview environment and prefer a visually calmer common compromise such as `16px / 28px`
- when that happens, prefer the user-approved shared value over strict token reconstruction

Approval rule learned from the same follow-up:
- if a first typography adjustment already went up for review and the next step is another visible size change, do not silently iterate again
- summarize the candidate value first and get explicit user approval before changing the PR branch
- this is especially important when moving between `18px` and `16px` class-level body text decisions, because both can be defensible but only one matches the user's visual preference

Important scope rule:
- if the user asks for a shared company-page token, limit the shared-token rollout to the pages they explicitly named
- do not automatically drag in neighboring families such as `news` list/detail typography until those were separately measured or explicitly included by the user

## Cookie/legal body typography case

Practical lesson from comparing:
- `https://stage.querypie.ai/t/cookie-preference`
- `https://www.querypie.com/ja/cookie-preference`

Even when both currently report `html { font-size: 16px; }`, a preview implementation can still contain values that look like they were copied from a 15px-root computed environment:
- preview title `56.25px / 67.5px` reconstructs to live `60px / 72px`
- preview label `18.75px / 26.25px` reconstructs to live `20px / 28px`
- preview body `15px / 24.375px` reconstructs to live `16px / 26px`

For legal-page body typography, if the user chooses the live-cookie parity baseline, use:
- body paragraph: `16px / 26px`
- color: `text-slate-600`
- keep larger lead/intro text separate; do not promote live cookie lead `18px / 28px` into the default legal body baseline unless explicitly requested

Scope pitfall:
- when asked to change legal pages' “본문 기본 문단” / default body paragraphs, update the shared legal document body paragraph rules and blockquote paragraphs, but do not automatically change headings, list items, tables, or cookie-preference-specific components unless the user explicitly expands scope.

See `references/cookie-legal-body-typography.md` for the measured values and conversion table.

## Practical example
A CTA title that looks like `52px` in source Styles but computes to `48.75px` under a 15px root should usually become `52px` again in corp-web-japan, because the preview keeps a 16px root.

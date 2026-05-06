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

## Practical example
A CTA title that looks like `52px` in source Styles but computes to `48.75px` under a 15px root should usually become `52px` again in corp-web-japan, because the preview keeps a 16px root.

---
name: browser-render-parity-comparison
description: Compare stage vs production (or any two deployed pages) by actual browser rendering in corp-web-app. Use before claiming a UI mismatch.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [browser, visual-parity, screenshots, stage-vs-prod, corp-web-app]
---

# Browser render parity comparison

Trigger: user asks to compare stage and production URLs, or asks to fix UI discrepancies on a page.

## Workflow

1. Open both URLs in separate browser tabs.
   - First verify the reference URL renders the intended page, not a live 404/not-found body.
   - If an inferred path-shaped URL 404s, inspect the live page's navigation/footer links and tab controls for the real canonical target. Some QueryPie pages expose variants by query string rather than nested paths (for example live AIP plans is `/ja/plans?aip`, not `/ja/plans/aip`).
   - For query/tab-driven pages, measure the exact active query-state page instead of the default tab.
2. Sync viewport: verify both show the same `window.innerWidth`.
3. Reset scroll: run `window.scrollTo(0, 0)` on both before any full-page screenshot.
4. Capture full-page screenshots (this avoids sticky headers looking like mid-page bugs).
5. Run automated probes (see `references/stage-production-audit-checklist.md`).
6. Compare computed styles before declaring a layout bug.
7. When the user names a specific mismatch (for example "H1 heading and lead description spacing"), measure that exact element pair with DOM geometry before changing anything. Also measure the nearest semantic/container wrapper (section/hero/content) and its computed padding/margins, because the heading and lead typography/gap can match while the parent section offset differs. Do not infer the fix from downstream landmarks such as card-grid start position.
8. For multi-element sections such as CTAs, measure each internal landmark separately: section top, heading-to-heading gap, final heading-to-button gap, alignment, and button width. Do not assume matching text means matching UI.
9. Build a full-page landmark inventory before reporting completion: hero, lead, primary content/cards, page-local CTA, global bottom CTA, footer. Route-local rewrites can preserve the main content while silently dropping downstream layout components such as `DownloadBottom` / `Stop Thinking. Start Transforming.`.
10. Explicitly check background visual layers for major sections, especially hero sections: compare computed `backgroundImage`, `backgroundColor`, pseudo-element backgrounds, absolutely positioned decorative images, gradient overlays, and section wrapper assets. Do not stop at text/media geometry; a page can match hero copy and screenshot sizes while still missing a production gradient background image layer.
11. Inspect source content data for copy/description mismatches.

## Common false positives

- **Header shadow appearing mid-page**: caused by capturing at scrollY > 0. Remedy: `window.scrollTo(0,0)`.
- **Viewport width difference**: stage tab may be 1467 px, prod tab 1535 px. Always sync width.

## Visual layer pitfall

When auditing marketing pages, inspect hero and section background layers as first-class visual parity targets. A full-page screenshot or DOM geometry pass can still miss that production uses a gradient background image, masked decorative asset, or pseudo-element overlay while stage renders a plain white section. For each major section, include background layers in the report and name the likely source contract (for example the shared hero primitive or live CSS background asset), not only typography, screenshots, cards, and CTA spacing.

## Browser automation fallback pitfalls

### Playwright browser availability

In repo worktrees, `require('playwright')` can resolve successfully while the bundled Chromium executable is missing, producing an error like `Executable doesn't exist at ... chromium_headless_shell ... Please run npx playwright install`. Do not stop the render audit there if a system Chrome is installed. On macOS, check `/Applications` for `Google Chrome.app` and launch Playwright with the installed browser channel instead:

```js
const browser = await chromium.launch({ channel: 'chrome', headless: true });
```

Use this as a lightweight fallback for screenshot/DOM collection when installing Playwright browsers would be slower or outside the task scope.

### Direct CDP computed-style probe

When interactive Chrome DevTools MCP is unavailable during a live visual parity task, do not encode the failure as a durable limitation and do not switch to subjective visual guessing. Launch system Chrome headless with a remote debugging port, connect via Chrome DevTools Protocol, and evaluate computed styles/DOM geometry directly. This is especially useful for matching CTA/button details such as size, padding, gap, gradient, border radius, typography, and SVG chevron path data.

See `references/headless-chrome-cdp-style-probe.md` for a concise reusable Node/CDP recipe. Note that current Chrome requires `PUT /json/new?...`; `GET /json/new?...` can fail with `Using unsafe HTTP verb GET...`.

## Evidence to keep

- URLs, viewport sizes, scrollY values
- JSON from `evaluate_script` probes
- Screenshot paths
- Fixes made and intentional differences

## References

- [Stage ↔ Production Audit Checklist](references/stage-production-audit-checklist.md) — step-by-step probes and common false positives.
- [Cookie preference H1/lead gap parity case](references/cookie-preference-heading-gap.md) — corp-web-app example where production used a shared `Box` `gapSize="sm"` wrapper while stage used a plain section, causing a 0px vs 20px H1-to-lead gap.
- [Hero background layer miss](references/hero-background-layer-miss.md) — lesson and probe for avoiding missed live hero gradient/background-image layers when foreground geometry appears similar.

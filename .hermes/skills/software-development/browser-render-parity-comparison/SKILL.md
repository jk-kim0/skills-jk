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
   - For responsive header/GNB questions, probe exact breakpoint-adjacent widths and distinguish interaction modes from visual viewport bands; see `references/responsive-header-gnb-breakpoint-audit.md`.
6. Compare computed styles before declaring a layout bug.
   - Always include `getComputedStyle(document.documentElement).fontSize` at the same viewport width for both pages. A responsive root rem difference (for example 16px vs 15px or 14px) scales all rem-based typography, gaps, padding, radii, and icon boxes; do not misdiagnose that as many independent component regressions.
   - If one repo intentionally keeps a constant 16px root and another has responsive `html { font-size: ... }` breakpoints, quantify the global rem impact before proposing a local CSS fix. See `references/root-rem-breakpoint-parity.md`.
7. When the user names a specific mismatch (for example "H1 heading and lead description spacing"), measure that exact element pair with DOM geometry before changing anything. Also measure the nearest semantic/container wrapper (section/hero/content) and its computed padding/margins, because the heading and lead typography/gap can match while the parent section offset differs. Do not infer the fix from downstream landmarks such as card-grid start position.
   - For "GNB/header to title" spacing, the parity contract is usually `header.getBoundingClientRect().bottom → h1.getBoundingClientRect().top`, not only `hero.getBoundingClientRect().top → h1.getBoundingClientRect().top`. Always record header `position`, `height`, `bottom`, and whether the header is fixed/overlay or sticky/in-flow. If the reference header is fixed but the target header occupies document flow, copying the reference hero padding can double-count the header and create an oversized visible gap.
8. For multi-element sections such as CTAs, measure each internal landmark separately: section top, heading-to-heading gap, final heading-to-button gap, alignment, and button width. Do not assume matching text means matching UI.
9. For interactive controls inside those sections, measure every relevant state before claiming parity: normal, hover when applicable, programmatic `:focus`, keyboard `:focus-visible`, active/pressed if present, SVG child/path computed fill/stroke, and pseudo-elements. A CTA button is not visually matched until its icon color and focus ring/glow behavior match the reference, not only its normal-state size/background.
   - Measure typography at the correct internal element level, not only the clickable wrapper. For CTA/button parity, record both the anchor/button computed font/line-height and the visible text span's computed font/line-height, plus padding, gap, border radius, icon wrapper size, and SVG/path fill. A wrapper can be `16px/16px` while the text span is `15px/22px`.
   - Re-measure the current live page and the current preview/deploy URL at the same viewport/root font-size before follow-up claims. Do not reuse an earlier scaled measurement or mix reference states from different deploys; if root font-size or viewport changed, all rem-derived values such as padding, gap, radius, and icon box need a fresh comparison.
   - Before cloning or approximating CSS for a button/CTA, search the current repo for a known-good rendered instance and reuse its shared primitive when possible. In corp-web-app, a correctly rendered bottom CTA such as `Stop Thinking. Start Transforming.` may be implemented through `DownloadBottom` + `ButtonLink variant="gradation" size="lg"`; if that canonical path exists, make the new CTA use the same component/CSS instead of copying button/icon/focus styles into a route-specific or section-specific module. CSS cloning is a parity risk because it can miss nested icon fill rules, hover gradients, and browser focus/glow behavior.
   - Before porting a Tailwind/className implementation from a sibling repo such as corp-web-japan into corp-web-app, verify the target repo actually has Tailwind in its build pipeline: `package.json` dependencies, `package-lock.json`, `postcss.config.mjs`, and `src/app/globals.css` imports. If Tailwind is absent, do not rewrite UI with Tailwind classes in the feature PR; either use the target repo's existing styling system for the immediate parity fix, or split a separate Tailwind foundation PR before a Tailwind-based page migration.
   - When parity target is an existing live querypie.com page, measure that live page directly and treat its computed values as the contract. Avoid approximate scaled values copied from corp-web-japan or inferred rem conversions if live metrics show exact values such as `60px/72px` headings, `120px` icons, or two stacked headings with a `20px` gap. See `references/corp-web-app-certifications-live-metric-parity.md`.
10. Build a full-page landmark inventory before reporting completion: hero, lead, primary content/cards, page-local CTA, global bottom CTA, footer. Route-local rewrites can preserve the main content while silently dropping downstream layout components such as `DownloadBottom` / `Stop Thinking. Start Transforming.`.
11. For shared chrome parity, audit header and footer as first-class UI surfaces, not just as present/absent landmarks. Compare:
   - header logo size/position and actual SVG/icon identity;
   - language/search/tool icons by identity, count, size, and href/action;
   - header CTA nested structure, visible text span, chevron/icon presence, font weight, gap, padding, radius, gradient, hover background, and computed dimensions;
   - footer logo SVG identity/size/color;
   - footer social links by exact count, order, aria-labels, hrefs, icon components/SVG viewBox, size, color, and spacing;
   - footer navigation columns, legal links, address text, borders, padding, background, typography, and responsive breakpoints.
   A chrome implementation can look broadly similar while still being wrong if a CTA chevron is missing, an icon is substituted (for example arrow instead of globe), or social icons are omitted.
12. Explicitly check background visual layers for major sections, especially hero sections: compare computed `backgroundImage`, `backgroundColor`, pseudo-element backgrounds, absolutely positioned decorative images, gradient overlays, and section wrapper assets. Do not stop at text/media geometry; a page can match hero copy and screenshot sizes while still missing a production gradient background image layer.
11. Inspect source content data for copy/description mismatches.
12. For MDX/publication detail parity, explicitly check whether the target renders raw MDX/JSX text. Literal tags such as `<Box>`, `<ArticleFileImage>`, `<br />`, or markdown links in the visible body mean the route is a body-preview stub, not a publication renderer. In that case, inspect the route for direct `{post.body}` / `renderBodyPreview` usage and fix it by evaluating MDX with the appropriate component map and composing the full article layout (hero, body images, TOC, related/sidebar CTAs), rather than patching typography around the raw text.

## Cross-repo Tailwind port pitfall

When comparing a page ported from another repository, especially `corp-web-japan` → `corp-web-app`, do not stop at matching JSX or Tailwind `className` strings. A reference implementation's visual output may depend on global CSS cascade layers, root route shell, header/footer wrappers, fonts/theme variables, sibling client components, and static assets. If the user says to reference or bring over the sibling implementation, treat that as the full rendered implementation contract: UI, layout shell, global CSS assumptions, interactions/client components, assets, and route-specific behavior.

Required checks before declaring the port faithful:

1. Open the exact Preview URL and exact reference URL in the browser.
2. Compare computed styles for the main section and its ancestors: `padding`, `margin`, `width`, `maxWidth`, `top`, `fontFamily`, and root/body font settings.
3. Verify that Tailwind utilities actually win in computed style, not just that the class names and CSS rules exist.
4. Inspect global resets. In Tailwind v4, an unlayered reset such as `* { padding: 0; margin: 0; }` can override `@layer utilities`; the reference repo may put reset/base rules inside `@layer base` so utilities win.
5. Trace the full implementation dependency graph: component file, sibling client components, assets, route shell, layout wrappers, fonts, theme tokens, and global CSS layer contract.
6. If the target repo has an unlayered reset but the task is a scoped page/PR migration, do not bundle a global `@layer base` reset conversion into the feature PR. Add route-scoped CSS Module overrides for the reset-invalidated spacing, verify computed styles, and leave the global reset conversion for a separate visual-risk PR.
7. If the target repo now intentionally supports Tailwind on the migrated endpoint but still has an unlayered global reset such as `* { padding: 0; margin: 0; }` or `button { background: none; border: none; }`, Tailwind class names can be present while computed `margin`, `padding`, `border`, or `background` remain wrong. For a narrow page migration, use Tailwind important modifiers (`!mt-*`, `!px-*`, `!border`, `!bg-*`, etc.) only on the reset-affected utilities, then re-run computed-style probes. Do not treat JSX/className parity as sufficient.
5. Trace the full implementation dependency graph: component file, sibling client components, assets, route shell, layout wrappers, fonts, theme tokens, and global CSS layer contract.

Mitigation when global reset cannot safely change in the same PR:
- Do not immediately move unlayered `globals.css` reset into `@layer base` inside a page-migration PR; that is a global visual-risk change and should normally be a separate PR.
- If the affected surface is an App Router route group with its own root layout (for example `src/app/(tailwind)/layout.tsx`) and the user wants it independent from legacy, prefer a route-group globals split first: add `src/app/(tailwind)/globals.css`, import it with `import './globals.css';`, include only required Tailwind/theme tokens/CSS variables/minimal base rules, and exclude legacy reset rules such as `* { padding: 0; margin: 0; }` and `button { background: none; border: none; }`.
- If a route-group globals split is not available or is too broad for the current PR, add a route-local/stable wrapper such as `data-publication-post` and a page-specific CSS Module that reasserts only the reset-overridden computed `padding`/`margin`/spacing values.
- Keep the Tailwind className contract visible in JSX, but verify the browser computed values are owned by the route-scoped mitigation until either the route-group globals split or a separate global reset layer migration lands.
- After a separate global `@layer base` migration or route-group globals split is merged and validated, remove temporary `!` utilities / route-scoped spacing overrides that only existed to fight the legacy reset.

See `references/corp-web-app-tailwind-port-cascade-pitfall.md` for a concrete corp-web-app/corp-web-japan failure mode and browser probe.
See `references/corp-web-app-tailwind-route-scoped-reset-workaround.md` for the safe interim route-scoped CSS Module pattern when global reset conversion is too broad for the current PR.
See `references/corp-web-app-tailwind-route-group-responsive-chrome.md` for the corp-web-app pattern where a `(tailwind)` route-group root layout must use Tailwind shared chrome while matching legacy desktop/tablet/compact breakpoints and accounting for unlayered global reset overrides.

## Common false positives

- **Header shadow appearing mid-page**: caused by capturing at scrollY > 0. Remedy: `window.scrollTo(0,0)`.
- **Viewport width difference**: stage tab may be 1467 px, prod tab may be 1535 px. Always sync width.

## App Router private-folder 404 pitfall

When a Preview URL 404s for a newly added Next.js App Router route, inspect the physical `src/app` folder names before assuming deployment or middleware failure. In App Router, folders prefixed with `_` are private folders and are opted out of routing, even if they contain `page.tsx` or `route.ts`. A route implemented under `src/app/_translations/...` or `src/app/[locale]/_translations/...` will not register and will 404 on Preview. If the public URL truly needs a leading underscore, use the encoded folder segment `%5Fname`; otherwise prefer a normal segment such as `translations`. Direct unit tests that import `src/app/_segment/.../page` can still pass because they bypass Next's route registration, so validate the deployed path with HTTP/browser evidence after route-segment changes.

## App Router route-group chrome parity pitfall

When a Next.js App Router page is moved into or tested under a separate route group such as `(tailwind)`, visual breakage may come from the group-level `layout.tsx`, not the page component. If the rendered page lacks global chrome (Header/GNB/Main wrapper/Footer) while the legacy route works, compare `src/app/(legacy)/layout.tsx` and the target group layout before editing page-level UI. Reuse the same layout primitives and pass the same preview/navigation state where the visual contract is meant to match legacy. Also inspect source-shape tests: an earlier smoke test may explicitly assert that Header/Footer are absent and must be updated when the route-group contract changes from isolated smoke page to legacy-chrome parity.

For Tailwind route groups, do not fix chrome parity by copying the entire legacy global CSS into `src/app/(tailwind)/globals.css`. Keep Tailwind globals minimal, exclude legacy token/reset dumps, and remove or narrow legacy CSS-variable dependencies in the shared chrome. See `nextjs-app-router-route-group-layouts` reference `corp-web-app-tailwind-group-legacy-chrome-parity.md` for the implementation pattern.

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

## Responsive header/GNB breakpoint audits

When a header/GNB changes behavior by viewport width, inspect the full breakpoint contract rather than only the visible hamburger threshold:

- React/client hooks such as `useIsMobileHeader()` / `useIsPhoneWidth()`.
- CSS media queries for the header container, mobile toggle, menu item layout, menu-space/mega-menu, preview/debug toggles, and global header variables.
- Fixed-width desktop containers that become newly exposed when the mobile breakpoint is lowered. If desktop GNB remains active below the content max width, avoid `width: var(--content-max-width)` without a shrink rule; prefer `width: 100%; max-width: var(--content-max-width)` plus explicit gutters if the header needs side spacing.
- One-pixel boundary widths around every band, e.g. `479`, `480`, `850`, `851`.

See `references/responsive-header-breakpoint-audit.md` for a compact checklist.

## Evidence to keep

- URLs, viewport sizes, scrollY values
- JSON from `evaluate_script` probes
Keep evidence of compared URLs, viewports, screenshots, observed differences,
fixes, and intentional differences.

Reference example:
- `references/corp-web-app-certifications-live-metric-parity.md` captures a concrete corp-web-app case where subtle live-page drift required measuring H1 typography, lead line-height, certification card/icon dimensions, and stacked CTA heading gaps directly in the browser.

## References

- [Stage ↔ Production Audit Checklist](references/stage-production-audit-checklist.md) — step-by-step probes and common false positives.
- [Raw MDX preview vs publication rendering](references/raw-mdx-preview-vs-publication-rendering.md) — pitfall and fix pattern for routes that display literal MDX/JSX instead of the live article layout.
- [Cookie preference H1/lead gap parity case](references/cookie-preference-heading-gap.md) — corp-web-app example where production used a shared `Box` `gapSize="sm"` wrapper while stage used a plain section, causing a 0px vs 20px H1-to-lead gap.
- [Hero background layer miss](references/hero-background-layer-miss.md) — lesson and probe for avoiding missed live hero gradient/background-image layers when foreground geometry appears similar.
- [Simple CTA parity lesson](references/simple-cta-parity-lesson.md) — bottom CTA landmark and nested button measurement checklist from a corp-web-app Simple CTA transfer/application follow-up.
- [Header-to-title gap parity](references/header-to-title-gap-parity.md) — pitfall and probe for GNB/header-to-H1 spacing when one site uses a fixed overlay header and the target header occupies document flow.
- [Root rem breakpoint parity](references/root-rem-breakpoint-parity.md) — checklist and impact math for responsive `html` root font-size differences such as corp-web-app 15px/14px breakpoints versus corp-web-japan's constant 16px root.

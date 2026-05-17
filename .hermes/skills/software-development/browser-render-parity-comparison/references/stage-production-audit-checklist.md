# Stage ↔ Production Render Audit Checklist

Use this when asked to compare a stage/preview deployment against a live production page.

## Pre-check: viewport sync
- Ensure both pages are evaluated at the **same viewport width** (e.g., 1440px desktop).
- Full-page screenshots must be captured at **scrollY = 0**. If scrollY > 0, sticky headers will appear mid-page in the screenshot and produce false layout mismatches.

## Automated probes (run via browser evaluate_script)
1. `document.title` — compare page titles
2. `document.querySelector('meta[property="og:title"]')?.content` — compare OG title
3. `window.getComputedStyle(header).boxShadow` — verify shadow at scrollY=0 vs scrolled
4. If the user identifies a specific spacing issue, measure the exact elements with `getBoundingClientRect()` and compute the gap. Example for H1 → lead spacing:
   ```js
   (() => {
     const h1 = document.querySelector('main h1');
     const lead = document.querySelector('main h1 + p, main p');
     const rect = (el) => el?.getBoundingClientRect().toJSON();
     const style = (el) => {
       const cs = el && getComputedStyle(el);
       return cs && {
         marginTop: cs.marginTop,
         marginBottom: cs.marginBottom,
         fontSize: cs.fontSize,
         lineHeight: cs.lineHeight,
       };
     };
     return {
       h1: rect(h1),
       lead: rect(lead),
       gapH1ToLead: h1 && lead ? lead.getBoundingClientRect().top - h1.getBoundingClientRect().bottom : null,
       h1Style: style(h1),
       leadStyle: style(lead),
     };
   })()
   ```
   Pitfall: do not fix H1/lead spacing by shifting the whole section or card grid; downstream card positions can move for unrelated reasons.
5. For CTA or other multi-element sections, probe section geometry and internal gaps, not just whether the text exists. Example for a two-line CTA and button:
   ```js
   (() => {
     const h3s = [...document.querySelectorAll('main h3')]
       .filter((h) => h.textContent.includes('Want') || h.textContent.includes('compliance'));
     const link = [...document.querySelectorAll('main a')]
       .find((a) => a.textContent.includes('Go to Trust Center'));
     const list = document.querySelector('main ul');
     const section = h3s[0]?.parentElement;
     const rect = (el) => el?.getBoundingClientRect().toJSON();
     const style = (el) => {
       const cs = el && getComputedStyle(el);
       return cs && {
         display: cs.display,
         alignItems: cs.alignItems,
         gap: cs.gap,
         textAlign: cs.textAlign,
         width: cs.width,
         marginTop: cs.marginTop,
       };
     };
     return {
       section: rect(section),
       sectionStyle: style(section),
       h3s: h3s.map((h) => ({ text: h.innerText, rect: rect(h), style: style(h) })),
       link: { rect: rect(link), style: style(link) },
       gapListToCta: section && list ? section.getBoundingClientRect().top - list.getBoundingClientRect().bottom : null,
       gapHeadingToHeading: h3s[1] ? h3s[1].getBoundingClientRect().top - h3s[0].getBoundingClientRect().bottom : null,
       gapHeadingToButton: link && h3s[1] ? link.getBoundingClientRect().top - h3s[1].getBoundingClientRect().bottom : null,
     };
   })()
   ```
   Pitfall: in route-local rewrites, a CTA can silently regress to `display: block`, left alignment, zero internal gaps, or a full-width button even when all visible text is present.
6. Confirm downstream section presence, not just the currently discussed section. For route-local migrations, compare a compact text/landmark inventory:
   ```js
   (() => [...document.querySelectorAll('main h1, main h2, main h3, main a')]
     .map((el) => ({ tag: el.tagName, text: el.innerText?.trim(), href: el.getAttribute('href') }))
     .filter((item) => item.text))()
   ```
   Pitfall: a page can match hero/cards/page-local CTA but still be missing the global bottom CTA (`Stop Thinking. Start Transforming.` / `Make It Happen`) because the old dynamic renderer appended `DownloadBottom` outside the page body.
7. `window.getComputedStyle(cardsContainer).gap` / `.gridTemplateColumns` — compare grid metrics
8. `window.getComputedStyle(firstCard).backgroundColor` / `.padding` — compare card styling

## Common false positives
- **Header shadow appearing mid-page**: caused by capturing full-page screenshot at scrollY > 0. Remedy: `window.scrollTo(0,0)` before screenshot.
- **Viewport width mismatch**: stage may render at 1467px while production is at 1535px if captured on different tabs/devices. Always set viewport explicitly.

## Evidence to keep for PR/review
- URLs compared
- Viewport sizes
- Computed style deltas (JSON from evaluate_script)
- Screenshot paths
- Fixes made and intentional differences

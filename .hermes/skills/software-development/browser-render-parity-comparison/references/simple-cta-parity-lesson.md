# Simple CTA parity lesson

Use this reference when a bottom CTA or shared CTA component looks almost right but the user reports repeated visual mismatches.

## What went wrong

A route-local corp-web-app `/[locale]/t/` page was missing the legacy/source bottom CTA that appeared above the footer on corp-web-contents `/ko/` and `/en/`. After adding a shared Simple CTA, visual parity still required checking the full section and nested button contract, not just headline text or approximate button dimensions.

Common miss pattern:

- Only comparing the CTA text and outer wrapper.
- Copying CSS from a source repo instead of finding the target repo's canonical button primitive.
- Measuring the clickable anchor/button but not the visible text span, icon wrapper, SVG/path colors, hover, active, and keyboard focus-visible states.
- Accepting scaled spacing values such as `112.5px`, `37.5px`, or `19.2px` when the target repo's canonical tokens were effectively `120px`, `40px`, and `20px`.
- Forgetting the bottom-of-page landmark order: main content -> Simple CTA -> footer.

## Better approach

1. Build a full-page landmark inventory before claiming route-local parity: hero, main content, bottom CTA, footer.
2. Locate an in-repo known-good CTA/button instance before cloning CSS. In corp-web-app, an existing bottom CTA may route through a shared `DownloadBottom` plus `ButtonLink variant="gradation" size="lg"` contract.
3. Measure section geometry and nested button internals in the browser:
   - section top/bottom/height;
   - padding and max-width/width contract (`100%` vs `100vw`);
   - title line boxes and title-description gap;
   - text block bottom to button top;
   - button bottom to section bottom;
   - section bottom to footer;
   - wrapper and visible text span typography;
   - icon wrapper size and SVG/path fill/stroke;
   - normal, hover, active/programmatic focus, and keyboard focus-visible.
4. Re-measure the exact deployed preview URL after changes; local render or previous measurements can be stale.

## Reusable probe idea

Collect a single JSON object per URL with named CTA landmarks and nested button styles. The key is not the exact script, but the scope: include the section, the heading/body, the anchor/button, the text span, the icon wrapper, SVG/path computed styles, and footer distance in one pass.

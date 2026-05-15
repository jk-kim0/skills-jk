# CTA glyph and icon parity lesson

## Trigger

Use this reference when a corp-web-japan page parity task compares a stage/preview page against a live QueryPie page or an upstream `corp-web-app` implementation and the page includes CTAs, buttons, tabs, cards, or icon-bearing links.

## Session lesson

During `/t/plans` parity work, the first pass correctly identified a comparison-table gutter/overflow defect but missed that plan-card CTA buttons rendered a text external-link arrow (`↗`) while the live/upstream widget used a right-chevron SVG icon (`ButtonArrowIcon`, `viewBox="0 0 7 12"`). The user explicitly pointed out that screenshot comparison should have caught this.

## Required practice

1. Treat screenshot review as a control-level visual pass, not only a layout/spacing pass.
2. Zoom into interactive controls and card CTAs in screenshots.
3. For every CTA/control, compare:
   - visible label
   - href/target behavior
   - icon presence/absence
   - icon/glyph type: text glyph, SVG icon, pseudo-element, CSS background
   - arrow direction and semantic meaning, e.g. external-link `↗` vs chevron `>`
   - icon size, color, and gap from label
4. If a glyph/icon mismatch appears in screenshots, inspect upstream source to identify the real contract:
   - upstream component name
   - SVG `viewBox`
   - SVG `path d`
   - whether the icon is aria-hidden
   - whether the icon comes from a reusable button primitive
5. Add source-level tests when implementing the fix so a text glyph cannot silently replace the upstream SVG contract again.

## Useful browser snippet

```js
(() =>
  [...document.querySelectorAll("main a, main button")].map((control, i) => {
    const r = control.getBoundingClientRect();
    const cs = getComputedStyle(control);
    return {
      i,
      text: (control.innerText || control.textContent || "").replace(/\s+/g, " ").trim(),
      tag: control.tagName.toLowerCase(),
      href: control instanceof HTMLAnchorElement ? control.href : null,
      rect: { left: r.left, top: r.top + scrollY, width: r.width, height: r.height },
      style: { display: cs.display, gap: cs.gap, color: cs.color, fontSize: cs.fontSize },
      textGlyphs: (control.textContent || "").match(/[↗→›>←‹↓↑]/g) || [],
      svgIcons: [...control.querySelectorAll("svg")].map((svg, svgIndex) => ({
        svgIndex,
        viewBox: svg.getAttribute("viewBox"),
        paths: [...svg.querySelectorAll("path")].map((path) => path.getAttribute("d")),
      })),
    };
  }).filter((item) => item.text || item.textGlyphs.length || item.svgIcons.length)
)();
```

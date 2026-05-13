# Mobile footer overflow and mixed-column notes

Use this note when a footer causes right-side blank space or horizontal scrolling on mobile.

## Symptom signature
- User reports blank space on the right side while vertical scrolling.
- Mobile Safari or DevTools device emulation shows the page can be dragged sideways.
- The visible route body may look fine; global chrome such as the footer can still be the true cause.

## Investigation recipe

Measure document overflow first:

```js
() => ({
  viewport: window.innerWidth,
  docClientWidth: document.documentElement.clientWidth,
  docScrollWidth: document.documentElement.scrollWidth,
  bodyClientWidth: document.body.clientWidth,
  bodyScrollWidth: document.body.scrollWidth,
})
```

Then enumerate likely offenders:

```js
() => {
  const all = [...document.querySelectorAll('body *')];
  return all
    .map((el) => {
      const r = el.getBoundingClientRect();
      const cs = getComputedStyle(el);
      return {
        tag: el.tagName.toLowerCase(),
        className: String(el.className || '').slice(0, 120),
        text: (el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 100),
        left: Math.round(r.left),
        right: Math.round(r.right),
        width: Math.round(r.width),
        scrollWidth: el.scrollWidth,
        clientWidth: el.clientWidth,
        display: cs.display,
        gridTemplateColumns: cs.gridTemplateColumns,
        gap: cs.gap,
        whiteSpace: cs.whiteSpace,
        overflowX: cs.overflowX,
      };
    })
    .filter((x) => x.right > window.innerWidth + 1 || x.scrollWidth > x.clientWidth + 1)
    .slice(0, 40);
}
```

## Common root cause pattern
- Mobile footer container is narrow
- Footer uses a 2-column grid on mobile
- Links keep `white-space: nowrap`
- Long localized labels force one or both columns wider than intended
- Column widths plus gap exceed the container width
- The footer widens the document, so the whole page gets horizontal scroll

## Preferred fix direction
1. Keep the outer footer section stack safe on mobile, often as a single-column stack.
2. Vary the link-list layout per section instead of forcing all sections into the same mobile rule.
3. Use two-column mobile grids only for sections with short labels.
4. Keep long-label sections as single-column lists.
5. If compact grids are mobile-only, restore the standard vertical list at tablet/desktop breakpoints.

## Practical implementation pattern
- Add a section-level layout flag in the footer data, for example `mobileLayout: "single" | "compact"`.
- Apply `compact` to short sections such as solutions/demo/company info.
- Apply `single` to long-label sections such as services or preview/internal developer links.
- In CSS:
  - base `.linkList` = vertical flex list
  - mobile `.linkListCompact` = 2-column grid
  - tablet+ `.linkListCompact` resets back to vertical flex if the desktop footer should remain a normal list

## Verification checklist
- Confirm document `scrollWidth` equals viewport width on the reported mobile viewport.
- Confirm long-label sections remain readable and do not clip.
- Confirm short sections actually render denser as intended.
- Confirm tablet/desktop footer layout still matches the expected vertical-list pattern.

# Inline footnote render parity

When comparing a corp-web-japan preview/stage page against a live QueryPie page, do not treat a lead paragraph as a single uniform text style if it contains a trailing note such as `*ユーザーの利用量により異なります`.

Live pages may render the lead body and the note with different parent elements and styles, for example:

- main lead paragraph: `font-size: 18px`, `line-height: 28px`, `font-weight: 300`, `letter-spacing: 0.36px`
- inline footnote wrapped in `<small>`: `font-size: 10px`, inherited `line-height: 28px`, `font-weight: 300`, `letter-spacing: 0.36px`, same lead color

Measurement pattern:

```js
const p = [...document.querySelectorAll('p')].find((el) =>
  (el.innerText || '').includes('*ユーザーの利用量'),
);
const walker = document.createTreeWalker(p, NodeFilter.SHOW_TEXT);
const parts = [];
let node;
while ((node = walker.nextNode())) {
  if (!node.textContent.trim()) continue;
  const range = document.createRange();
  range.selectNodeContents(node);
  parts.push({
    text: node.textContent.trim(),
    parentTag: node.parentElement.tagName,
    parentClass: node.parentElement.className,
    parentStyle: {
      fontSize: getComputedStyle(node.parentElement).fontSize,
      lineHeight: getComputedStyle(node.parentElement).lineHeight,
      fontWeight: getComputedStyle(node.parentElement).fontWeight,
      letterSpacing: getComputedStyle(node.parentElement).letterSpacing,
      verticalAlign: getComputedStyle(node.parentElement).verticalAlign,
    },
    rects: [...range.getClientRects()].map((r) => ({ x: r.x, y: r.y, w: r.width, h: r.height })),
  });
}
parts;
```

Implementation pattern:

- Keep the paragraph component for the main lead text.
- Add an explicit footnote component/wrapper that renders `<small>` and carries the measured style contract.
- Keep the footnote inline in the same paragraph when live does so; do not turn it into a separate block unless live renders it as a separate block.
- Update source-inspection tests to assert both the wrapper usage in the route and the concrete footnote style class in the section component.

Example class contract from a live AIP lead:

```tsx
export function AipUsageBasedLlmHeroFootnote({ children }: { children: ReactNode }) {
  return <small className="text-[10px] font-light leading-[28px] tracking-[0.36px] text-[#57606A]">{children}</small>;
}
```

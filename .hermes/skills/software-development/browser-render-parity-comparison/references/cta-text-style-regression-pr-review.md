# CTA text style regression PR review

Use this note when reviewing a PR that claims to align a header, GNB, drawer, or marketing CTA text style.

## Failure pattern

A PR can make a CTA look more different even when it says it is aligning the text style. Common causes:

- The PR edits a stale route-local or Tailwind-cloned button instead of the current shared CTA primitive.
- The review compares only the clickable anchor/button wrapper and not the visible text span inside it.
- The implementation changes approximate Tailwind utilities such as `font-medium`, `text-white`, or a fixed drawer height instead of matching the reference computed output.
- The branch was created before a header/chrome refactor, so the touched files are no longer the source of truth on latest `main`.

## Required probe

For each reference and target URL, at the same viewport, collect both wrapper and visible text styles:

```js
() => {
  const norm = s => (s || '').replace(/\s+/g, ' ').trim();
  const candidates = [...document.querySelectorAll('a,button')].filter(el => norm(el.textContent) === 'Free Now');
  const visible = candidates.filter(el => {
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden';
  });
  const pick = el => {
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    const span = el.querySelector('span');
    const spanCs = span && getComputedStyle(span);
    const spanRect = span && span.getBoundingClientRect();
    return {
      className: String(el.className || ''),
      text: norm(el.textContent),
      rect: { x: r.x, y: r.y, width: r.width, height: r.height },
      style: {
        fontSize: cs.fontSize,
        fontWeight: cs.fontWeight,
        lineHeight: cs.lineHeight,
        color: cs.color,
        background: cs.background,
        padding: cs.padding,
        gap: cs.gap,
        display: cs.display,
      },
      textSpan: span && {
        className: String(span.className || ''),
        rect: { x: spanRect.x, y: spanRect.y, width: spanRect.width, height: spanRect.height },
        style: {
          fontSize: spanCs.fontSize,
          fontWeight: spanCs.fontWeight,
          lineHeight: spanCs.lineHeight,
          color: spanCs.color,
          letterSpacing: spanCs.letterSpacing,
        },
      },
    };
  };
  return {
    url: location.href,
    viewport: { width: innerWidth, height: innerHeight },
    rootFontSize: getComputedStyle(document.documentElement).fontSize,
    all: candidates.map(pick),
    visible: visible.map(pick),
  };
}
```

## Review checklist

- Compare the reference and target visible text span, not only the wrapper.
- Record exact `font-size`, `font-weight`, `line-height`, `color`, `width`, `height`, `padding`, and `gap`.
- Check desktop and mobile/drawer CTAs separately; mobile height can drift even when font values look close.
- Trace the reference CTA back to its owning primitive. In corp-web-app this may be `ButtonLink variant="gradation" size="md"` plus `StaticButton`, or a header-specific `HeaderRightButton` / `HeaderMobileBottomButton` primitive after a chrome refactor.
- If latest `main` changed header/chrome structure, classify PR edits to old Tailwind clone files as stale until the branch is rebased and the current source-of-truth files are inspected.
- Treat changes from `font-weight: 400` / `#f6f6f6` to `font-weight: 500` / `#fff` as a visual regression unless the live/reference page actually computes those values.

## Fix preference

Prefer reusing or preserving the shared primitive that already renders the reference CTA. Avoid one-off Tailwind class edits like `font-medium text-white` unless browser-computed evidence proves those exact values match the reference.

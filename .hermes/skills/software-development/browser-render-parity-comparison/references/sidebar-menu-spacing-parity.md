# Sidebar menu spacing parity

Use this when a migrated/list page sidebar must match an existing sidebar implementation, especially when one side is Tailwind/className-based and the reference is CSS Module based.

## Durable lesson

Do not compare only the container's CSS `gap` or only the class names. Sidebar item spacing can be implemented as:

- `ul { gap: 20px }` on the reference implementation;
- sibling margins such as `li + li { margin-top: 20px }` or Tailwind arbitrary variants on the migrated implementation;
- responsive overrides where mobile uses card-like padding/gap and desktop removes padding/backgrounds.

The parity contract is the visible vertical distance between adjacent menu item text/link boxes at the same viewport.

## Probe pattern

At the target desktop viewport, reset scroll and measure both pages:

```js
() => {
  window.scrollTo(0, 0);
  const norm = s => (s || '').replace(/\s+/g, ' ').trim();
  const links = [...document.querySelectorAll('aside nav a, aside nav span[aria-disabled="true"]')]
    .filter(el => norm(el.textContent));

  return {
    url: location.href,
    viewport: { width: innerWidth, height: innerHeight },
    rootFontSize: getComputedStyle(document.documentElement).fontSize,
    items: links.map((el, i) => {
      const r = el.getBoundingClientRect();
      const cs = getComputedStyle(el);
      const next = links[i + 1]?.getBoundingClientRect();
      return {
        text: norm(el.textContent),
        rect: { top: r.top, bottom: r.bottom, height: r.height },
        display: cs.display,
        lineHeight: cs.lineHeight,
        padding: cs.padding,
        marginBottom: cs.marginBottom,
        gapToNext: next ? next.top - r.bottom : null,
      };
    }),
    containers: [...document.querySelectorAll('aside nav ul')].map(ul => ({
      className: String(ul.className || ''),
      gap: getComputedStyle(ul).gap,
    })),
  };
};
```

## Fix pattern

1. Match `gapToNext` first, because it is what the user sees.
2. Preserve the mobile/sidebar-drawer contract unless the user explicitly mentions mobile.
3. If desktop spacing is implemented through sibling margin classes, update the desktop sibling margin rather than changing mobile `gap` or link padding.
4. Add a narrow source-level contract test only if the repo already has route/source tests around that sidebar; do not add heavyweight browser tests for a one-value CSS parity fix.

## Example outcome

For a resource list sidebar, a reference page measured `gapToNext: 20` while the migrated page measured `gapToNext: 12`. The minimal fix was to change the desktop sibling margin class from a 12px value to a 20px value while leaving mobile card spacing unchanged.
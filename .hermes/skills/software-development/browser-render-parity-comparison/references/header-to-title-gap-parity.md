# Header-to-title gap parity pitfall

Case: QueryPie blog list parity work comparing `https://querypie.ai/blog` against a corp-web-app Preview `/<locale>/t/blog` route.

## What went wrong

The first pass matched the hero-internal metric:

- `hero.getBoundingClientRect().top -> h1.getBoundingClientRect().top`

That was insufficient because the two sites had different header layout contracts:

- Reference (`querypie.ai/blog`): header was `position: fixed`, overlaid at the top of the viewport, height/bottom about `64px`.
- Target Preview: header was `position: sticky` and occupied document flow, including a language banner, height/bottom about `162px`.

Copying the reference hero padding (`143px`) into the in-flow target header made the visible gap from GNB bottom to H1 far too large.

## Correct measurement

For user reports about "GNB and title spacing" or "header to H1 gap", measure and compare this exact visible contract:

```js
(() => {
  window.scrollTo(0, 0);
  const header = document.querySelector('header');
  const h1 = document.querySelector('h1');
  const hero = h1?.closest('section');
  const rect = (el) => {
    if (!el) return null;
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    return {
      top: r.top + scrollY,
      bottom: r.bottom + scrollY,
      height: r.height,
      position: cs.position,
      paddingTop: cs.paddingTop,
      paddingBottom: cs.paddingBottom,
      marginTop: cs.marginTop,
      marginBottom: cs.marginBottom,
      fontSize: cs.fontSize,
      lineHeight: cs.lineHeight,
    };
  };
  return {
    url: location.href,
    viewport: { width: innerWidth, height: innerHeight },
    rootFontSize: getComputedStyle(document.documentElement).fontSize,
    header: rect(header),
    hero: rect(hero),
    h1: rect(h1),
    gaps: {
      headerBottomToH1: header && h1 ? h1.getBoundingClientRect().top - header.getBoundingClientRect().bottom : null,
      heroTopToH1: hero && h1 ? h1.getBoundingClientRect().top - hero.getBoundingClientRect().top : null,
      viewportTopToH1: h1 ? h1.getBoundingClientRect().top : null,
    },
  };
})();
```

## Fix pattern

If the reference header is fixed/overlay and the target header is sticky/in-flow, do not blindly port the reference hero top padding. Instead set target hero top padding so:

```text
target header bottom -> target H1 top == reference header bottom -> reference H1 top
```

Example from the session:

- Reference: header bottom `64px`, H1 top `143px`, visible gap `79px`.
- Target before fix: header bottom `162px`, H1 top `305px`, visible gap `143px`.
- Target fix: reduce hero top padding so the target visible gap is approximately `79px`.

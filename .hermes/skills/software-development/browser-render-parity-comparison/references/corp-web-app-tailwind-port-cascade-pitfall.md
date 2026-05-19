# corp-web-app Tailwind port cascade pitfall

Session learning: when porting a Tailwind-rendered page from `corp-web-japan` into `corp-web-app`, copying the component `className` strings is not enough. The visual contract also depends on the reference repo's global CSS cascade, root layout shell, fonts/theme tokens, header/footer composition, and client-side interaction components.

Observed failure mode:

- The DOM on the corp-web-app Preview contained the same Tailwind classes as corp-web-japan, for example `px-[30px]`, `pt-[112px]`, `lg:pt-[144px]`, `mb-[13px]`.
- The built CSS contained matching Tailwind utility rules.
- The browser computed styles still showed `padding: 0px` and missing margins on the article section/headings.

Root cause:

- corp-web-app had an unlayered global reset in `src/app/globals.css`:
  - `* { box-sizing: border-box; padding: 0; margin: 0; }`
- Tailwind v4 utilities are emitted inside `@layer utilities`.
- In CSS cascade layer ordering, unlayered rules can override layered utility rules, so the global reset defeated Tailwind spacing utilities.
- corp-web-japan put base/reset behavior inside `@layer base`, so Tailwind utilities won there.

Other missing implementation-contract dependencies found in the same class of failure:

- corp-web-japan route shell rendered the publication page inside a local `<main className="relative overflow-x-hidden bg-white text-slate-950">` with `SiteHeader`, `PublicationPostPage`, and `SiteFooter`.
- corp-web-app wrapped the route in its existing root layout: `Header`, `Main`, `Footer`, where `Main` used flex/centering behavior that changed the section width/position.
- corp-web-japan defined font/theme/base contracts such as `Pretendard JP Subset`, `--font-app-sans`, and body `font-sans`; corp-web-app did not have the same theme contract.
- corp-web-japan `PublicationPostPage` depended on sibling client components/assets such as publication TOC smooth-scroll/active state, share/copy buttons, and `/header-assets/stage-arrow-right.svg`.

Required investigation pattern:

1. Open the exact Preview URL and exact reference URL in the browser.
2. Compare computed styles, not only source or DOM class names.
3. Probe the section and ancestors: `padding`, `margin`, `width`, `maxWidth`, `top`, `fontFamily`, and root/body font settings.
4. Inspect matching CSS rules and whether they actually apply with `element.matches(...)` and computed style.
5. Trace the reference component's full dependency graph:
   - component file
   - sibling client components
   - required assets
   - route shell
   - layout/header/footer wrappers
   - global CSS layer/base reset
   - font/theme variables
6. Treat a port as incomplete if any of those contracts are missing, even when the visible JSX/className strings look similar.

Minimal browser probe shape:

```js
() => {
  const h1 = document.querySelector('h1');
  const section = h1?.closest('section');
  const cs = section && getComputedStyle(section);
  const ancestors = [];
  let el = h1;
  while (el && ancestors.length < 8) {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    ancestors.push({
      tag: el.tagName.toLowerCase(),
      className: String(el.className || '').slice(0, 200),
      top: Math.round(r.top + scrollY),
      left: Math.round(r.left),
      width: Math.round(r.width),
      padding: s.padding,
      margin: s.margin,
      maxWidth: s.maxWidth,
      fontFamily: s.fontFamily,
    });
    el = el.parentElement;
  }
  return {
    url: location.href,
    rootFontSize: getComputedStyle(document.documentElement).fontSize,
    bodyFont: getComputedStyle(document.body).fontFamily,
    section: section && {
      className: String(section.className || ''),
      padding: cs.padding,
      margin: cs.margin,
      maxWidth: cs.maxWidth,
      width: cs.width,
    },
    ancestors,
  };
};
```

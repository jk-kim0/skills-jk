# Hero background layer miss in render-parity audits

Session lesson: during a corp-web-japan ACP child page audit, the initial browser comparison missed that live QueryPie pages rendered a hero `backgroundImage: linear-gradient(...)` layer while stage rendered a plain hero. The audit reported FAQ, section count, mobile typography, card structure, and feature-band rhythm, but omitted the hero gradient until the user pointed it out.

## Root cause

The collection script only captured foreground geometry and a small style subset:

- `backgroundColor`
- `paddingTop` / `paddingBottom`
- `overflow`
- headings, paragraphs, images, links, controls

It did not capture:

- `backgroundImage`
- gradient backgrounds
- `::before` / `::after` pseudo-element backgrounds
- absolutely positioned decorative children
- hero/section background asset URLs

Because both stage and live hero sections reported `backgroundColor: rgba(0, 0, 0, 0)`, the structured JSON made the hero background appear equivalent. Later targeted probing showed live hero sections had `linear-gradient(...)` and stage had no comparable hero background-image layer.

## Required workflow update

For every visual/render-parity audit of marketing pages:

1. Treat hero and major section background layers as first-class parity targets, not secondary decoration.
2. For each major `section`/`article` and its first few ancestors, collect:
   - computed `backgroundColor`
   - computed `backgroundImage`
   - `backgroundSize`
   - `backgroundPosition`
   - `::before` and `::after` computed `content`, `backgroundImage`, `backgroundColor`, dimensions, and position
   - absolute/fixed decorative children near the hero band
3. Compare the exact requested URLs at the same viewport.
4. Use side-by-side screenshot or hero crop review in addition to DOM geometry.
5. Do not conclude that hero parity is close merely because h1, lead, foreground screenshot, and scroll metrics match.

## Minimal browser probe pattern

```js
(() => {
  const text = (el) => (el?.innerText || el?.textContent || "").replace(/\s+/g, " ").trim();
  const rect = (el) => {
    const r = el.getBoundingClientRect();
    return { top: r.top + scrollY, left: r.left, width: r.width, height: r.height };
  };
  const style = (el, pseudo) => {
    const cs = getComputedStyle(el, pseudo);
    return {
      backgroundColor: cs.backgroundColor,
      backgroundImage: cs.backgroundImage,
      backgroundSize: cs.backgroundSize,
      backgroundPosition: cs.backgroundPosition,
      position: cs.position,
      zIndex: cs.zIndex,
      opacity: cs.opacity,
      content: pseudo ? cs.content : undefined,
    };
  };

  const h1 = document.querySelector("main h1");
  const ancestors = [];
  let el = h1;
  while (el && el !== document.body && ancestors.length < 10) {
    ancestors.push({
      tag: el.tagName.toLowerCase(),
      className: String(el.className || "").slice(0, 160),
      text: text(el).slice(0, 80),
      rect: rect(el),
      style: style(el),
      before: style(el, "::before"),
      after: style(el, "::after"),
    });
    el = el.parentElement;
  }

  const heroBandBackgroundCandidates = [...document.querySelectorAll("main *")]
    .map((node, i) => ({
      i,
      tag: node.tagName.toLowerCase(),
      className: String(node.className || "").slice(0, 160),
      text: text(node).slice(0, 80),
      rect: rect(node),
      style: style(node),
      before: style(node, "::before"),
      after: style(node, "::after"),
    }))
    .filter((item) => {
      const inHeroBand = item.rect.top < 900 && item.rect.width > 50 && item.rect.height > 10;
      const hasBgImage = [item.style, item.before, item.after].some((s) => s.backgroundImage && s.backgroundImage !== "none");
      const hasBgColor = [item.style, item.before, item.after].some((s) => !["rgba(0, 0, 0, 0)", "transparent"].includes(s.backgroundColor));
      return inHeroBand && (hasBgImage || hasBgColor);
    });

  return { h1: text(h1), ancestors, heroBandBackgroundCandidates };
})();
```

## ACP child route promotion and subtle-gradient lesson

Follow-up lesson from the corp-web-japan ACP child-page work:

- Always compare the exact user-provided URL first, even when you suspect it has been promoted or redirected. In this case, `https://stage.querypie.ai/t/platforms/acp/web-access-controller` rendered the local 404 page because ACP child pages had moved from `/t/platforms/acp/...` to public `/platforms/acp/...` routes.
- Record that as a route-state finding before switching to the current public route for the body/parity comparison. Do not silently substitute the new route and report it as if the exact requested URL rendered the page.
- For source-backed QueryPie Japan pages, triangulate against `../corp-web-contents` after the browser evidence is clear. The ACP child source pages store hero background variants on the first page-body wrapper, e.g. `background="dac"`, `background="sac"`, `background="kac"`, and `background="wac"`.
- Screenshot/vision descriptions can call a subtle gradient “plain white” when the top stop is white and the color shift happens lower in the hero band. Treat that as a weak signal; verify with computed `backgroundImage` and, when useful, side-gutter pixel samples lower in the hero band.
- Do not stop at `backgroundImage !== "none"` or matching variant colors. Compare the full gradient stop list and inspect the actual rendering implementation, not only the MDX source prop. In the ACP child-page case, `corp-web-contents` only stored `background="wac"`; the concrete live contract lived in `corp-web-app/src/components/foundation/layout/layout.module.css` as `linear-gradient(180deg, #fff 30%, #dfeff2 84%, #fff 84%, #fff 100%)`. A Tailwind utility approximation like `via-[#...] via-[84%] to-white` faded to white at 100%, leaving a visibly different color wash behind the lower hero/media area. Copy the concrete gradient string, including the duplicated white stop at `84%`, when parity is the goal.
- Add or update source-level tests to pin the source contract when the same route family has several variants. For ACP child pages, each route should keep the corresponding `AcpHeroSection background="..."` variant from the source content, and the shared hero primitive should pin the exact stop behavior.

## Reporting rule

In the final report, include a dedicated bullet for hero/background layer parity:

- exact requested URL result, including whether it rendered the target page, redirected, or returned 404/not-found
- live background layer present? `backgroundImage` / pseudo-element / decorative asset
- stage/background layer present on the comparable current route?
- classification: defect candidate, intentional local adaptation, route-state finding, external artifact, or environment artifact
- likely source area: shared hero primitive, route-level wrapper, CSS module, source content background variant, or asset import

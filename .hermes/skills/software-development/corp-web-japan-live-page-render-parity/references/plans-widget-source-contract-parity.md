# `/t/plans` source-backed widget parity failure

Session context:
- User compared `https://stage.querypie.ai/t/plans` / PR 504 preview against `../corp-web-app` plans implementation and reported many remaining detailed UI differences.
- The upstream source existed in `../corp-web-app/src/app/ja/plans/page.tsx` plus widget components/CSS under:
  - `../corp-web-app/src/components/widget/pricing/{pricing,product,plan-card}.*`
  - `../corp-web-app/src/components/widget/compare-table/*`
- PR 504 improved broad shape but was still unsatisfactory because it rebuilt the widget with local Tailwind primitives instead of preserving the upstream widget contract.

Root cause pattern:
- `/ja/plans` is a widget / application-contract page, not a normal static marketing page.
- Text parity and route-local JSX are insufficient for widget pages.
- A manually translated Tailwind implementation can pass structure tests while losing button chrome, icon rendering, type scale, tab underline behavior, table overflow/padding, row heights, and root-rem/final-pixel details.

Concrete evidence after PR 504 / follow-up parity passes:
- PR preview root: `16px`; live root: `15px`.
- Preview plan title: `26px / 34px`; live computed title: about `24.375px / 31.875px` because upstream uses a 15px root.
- Preview button used text plus `↗`; upstream uses the real `ButtonLink` component and icon wrapper.
- Preview table wrapper started around left `80px`; live table started around left `40px` inside its own overflow wrapper.
- Preview first table row was about `64px`; live first row was about `60px`.
- A later follow-up missed comparison-table section header spacing (`一般`, etc.): the local Tailwind rebuild ported the visible `.heading` row concept but dropped cascade-derived `td:first-of-type { padding-left: 20px }` and the `StaticBadge asChild` typography contract (`12px / 17px / 500 / 0.24px`).

Additional root-cause pattern:
- Source-backed CSS-module widgets can encode important visual behavior outside the JSX class attached to the element being migrated.
- Broad selectors such as `.table td:first-of-type`, `.table tbody > tr`, pseudo-elements, CSS variables, and slot/asChild typography wrappers can materially affect the rendered element.
- “I inspected the source component” is not enough if the inspection did not enumerate every selector/wrapper that can match the rendered node.

Required workflow for future source-backed widget migrations:
1. Classify the page before coding: static marketing vs widget/application-contract.
2. If widget and upstream source exists, inspect the full upstream component chain and CSS modules before creating local primitives.
3. Enumerate every selector that can affect important rendered nodes, not only classes named in JSX; include `td:first-of-type`, `tbody > tr`, pseudo-elements, inherited variables, and responsive/container selectors.
4. Inspect slot/asChild typography wrappers such as `StaticBadge asChild` and port their computed text contract when rebuilding locally.
5. Prefer a direct-port or compatibility-layer strategy over a Tailwind approximation.
6. If direct port is rejected, explicitly choose a measured-rebuild strategy and collect browser geometry/computed-style anchors before declaring parity.
7. Add tests that defend widget UI contracts, not only route-local copy ownership.
8. Report remaining deltas honestly; do not call the page aligned from source-only checks.

Useful browser snippet for table-cell cascade checks:

```js
(() =>
  [...document.querySelectorAll("main table th, main table td")].map((cell, i) => {
    const r = cell.getBoundingClientRect();
    const row = cell.closest("tr");
    const rr = row?.getBoundingClientRect();
    const cs = getComputedStyle(cell);
    return {
      i,
      tag: cell.tagName.toLowerCase(),
      text: (cell.innerText || cell.textContent || "").replace(/\s+/g, " ").trim(),
      colSpan: cell instanceof HTMLTableCellElement ? cell.colSpan : null,
      rect: { left: r.left, top: r.top + scrollY, width: r.width, height: r.height },
      rowRect: rr && { left: rr.left, top: rr.top + scrollY, width: rr.width, height: rr.height },
      style: {
        fontSize: cs.fontSize,
        lineHeight: cs.lineHeight,
        fontWeight: cs.fontWeight,
        letterSpacing: cs.letterSpacing,
        textAlign: cs.textAlign,
        paddingLeft: cs.paddingLeft,
        paddingTop: cs.paddingTop,
        paddingBottom: cs.paddingBottom,
        color: cs.color,
        backgroundColor: cs.backgroundColor,
      },
    };
  }).filter((item) => item.text)
)();
```

Issue created from this session:
- `querypie/corp-web-japan` issue 505: `Investigate source-backed plans widget parity gap`

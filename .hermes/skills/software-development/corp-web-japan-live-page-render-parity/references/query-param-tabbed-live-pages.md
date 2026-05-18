# Query-string tabbed live pages in corp-web-japan parity work

Lesson from `/t/plans/aip` comparison-table parity work:

- The local preview route used a path-shaped URL: `https://stage.querypie.ai/t/plans/aip`.
- The initially inferred live URL `https://www.querypie.com/ja/plans/aip` rendered the live 404 body.
- The correct live reference was `https://www.querypie.com/ja/plans?aip`, discovered from live footer/navigation links and the plans page tab state.

Workflow to reuse:

1. Open the inferred live URL and verify the page body is not a 404/not-found page before taking measurements.
2. If it is 404, inspect live navigation/footer anchors and tab controls for the canonical target.
3. For tabbed pages, compare the active query-state page, not the default route.
4. Record both the attempted URL and the corrected reference URL in the PR/report.

Concrete visual details observed for the live AIP plans comparison table:

- Root font size on live was `15px`; local corp-web-japan preview keeps `16px`.
- Live section header rows used a dark band around `#2f3a49`, light text `#f6f6f6`, bottom border `#dae1e7`, and a 44px-token row height that computed to about 41.25px under the 15px root.
- Live row labels used lighter weight than the preview (`font-weight: 300` computed on live).
- Live check/cross indicators were filled circular 32x32 viewBox SVG icons sized to about 15px, not lucide outline icons.
- Live boolean icon fills were blue `#0762d4` for supported and red `#d43823` for unsupported.

Implementation pattern used:

- Keep table data and route authoring unchanged.
- Update only the shared comparison-table primitives in `src/components/sections/plans/section.tsx`.
- Add/adjust source-inspection tests under `tests/src/app/t/plans/page.test.mjs` to pin section-band and status-icon contracts.

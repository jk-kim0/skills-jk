# Simple CTA section port and `/[locale]/t` application

Use this reference when a corp-web-app static/preview page is missing the shared bottom CTA that exists in the legacy/source site, or when porting a reusable CTA section from corp-web-japan into corp-web-app.

## Class of work

This is two related but separable PRs:

1. Component/library PR: port the reusable shared `SimpleCtaSection` primitive into corp-web-app.
2. Usage/page PR: apply the shared primitive to the affected static/preview page(s), such as `src/app/[locale]/t/**`, and verify the CTA sits immediately above the global footer.

Keep these separate when the user asks for separate PRs, even if the usage PR is small. The first PR should be a reusable component transfer; the second should be the page-level adoption.

## Source/provenance checks

- Inspect the corp-web-japan implementation named `SimpleCtaSection` and port its component shape rather than inventing a new CTA API.
- Inspect `corp-web-contents` legacy/source pages for `/ko/` and `/en/` home routes to confirm whether the bottom CTA exists above the footer and what copy/links it used.
- Compare corp-web-app route-local preview pages such as `/{locale}/t/` against that source behavior; do not assume the page is complete just because hero/main sections render.

## Implementation guidance

- Put the common component under the repo's shared components area, not inside a single route directory, when it is intended for multiple pages.
- Keep page-level copy/composition visible in the route-local page file when the route-local authoring contract applies. The shared component should own reusable layout/style primitives, not hide all marketing copy in a central registry.
- Reuse existing corp-web-app button/link primitives if they already produce the desired visual behavior. Do not clone button CSS from another repo when an in-repo primitive matches the canonical CTA button behavior.
- Insert the bottom CTA as a page landmark immediately before the footer/layout boundary, not inside unrelated content sections.

## Verification checklist

- Tests should cover both PR layers when applicable:
  - component/export or structure test for the shared CTA primitive;
  - route test asserting the preview page renders the expected CTA text/link before the footer boundary or as part of the route composition.
- Browser parity checks should include the bottom-of-page landmark inventory: page content, Simple CTA, then footer.
- If using a deployment preview for final review, measure the exact preview URL; local or source-only inspection can miss spacing/gradient/focus differences.

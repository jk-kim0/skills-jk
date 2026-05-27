# ACP hero background parity failure pattern

Session context:
- Stage example: `https://stage.querypie.ai/t/platforms/acp/web-access-controller`
- Live example: `https://www.querypie.com/ja/solutions/acp/web-access-controller`
- Scope later expanded to all ACP child pages under `/platforms/acp/*`.

## What went wrong

Repeated screenshot comparison did not resolve the hero background mismatch because the workflow over-weighted rendered screenshots and under-weighted source-of-truth confirmation.

For ACP child pages, the background contract was not only a visible color in the screenshot. It came from the live page's authored implementation and surrounding section/shell primitives. A future parity pass must verify both:

1. the live page's authored source in the sibling content repository, for example `../corp-web-contents/pages/solutions/acp/<slug>/ja/content.mdx` or the matching live-source route family; and
2. the browser-rendered style layers on the live page and stage page.

If either side is skipped, the agent can keep tuning the wrong local element while the actual difference remains in a parent shell, pseudo/background layer, gradient token, or route-family primitive.

## Required ACP hero parity checklist

For each ACP child page:

1. Open the exact stage URL and exact live URL requested by the user.
2. Capture screenshots at the same viewport and compare the hero area first.
3. Confirm the live source from `corp-web-contents`; do not merely infer from the current corp-web-japan implementation.
4. Inspect the live hero and the stage hero with DevTools/browser style extraction:
   - hero container background-color
   - background-image, linear/radial gradients, and CSS variables
   - pseudo-elements such as `::before` / `::after`
   - mask/overlay layers
   - parent section/page-shell background
   - any image/visual wrapper background that blends into the hero
5. Fix the shared ACP primitive when the contract is family-wide; do not patch one child page in isolation unless the source proves it is unique.
6. Add or update structure tests that pin the shared primitive/class contract so a later child page cannot drift.
7. Update the repository parity guide with the root cause and the checklist before declaring the issue solved.

## Implementation guidance

Prefer one shared ACP hero primitive for recurring child-page contracts:
- shared hero copy/title/lead primitives should live under `src/components/sections/acp/**`;
- child pages should compose the shared primitives explicitly in `page.tsx` so route-local copy remains visible;
- background and spacing contracts should live in the section primitive, not duplicated across every child page;
- if parent `/platforms/acp` and children share the same hero title/lead contract, re-export from one source of truth rather than maintaining parallel class strings.

When the user asks for all ACP child pages to be fixed in one PR, this is an exception to the usual “split multi-page service pages” rule: use one PR if the defect is a shared ACP family primitive/background contract and all affected routes are under the same `/platforms/acp` family.

## Reporting requirement

When reporting the investigation, explicitly answer whether the live page source was checked in `corp-web-contents`. If it was not checked yet, say so and check it before recommending a CSS fix.

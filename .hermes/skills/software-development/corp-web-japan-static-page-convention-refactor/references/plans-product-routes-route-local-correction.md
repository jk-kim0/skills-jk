# `/t/plans` product-route route-local correction

Session lesson from corp-web-japan PR #520 follow-up.

## What went wrong

The first implementation tried to keep `/t/plans`, `/t/plans/aip`, and `/t/plans/acp` deduplicated by introducing:

- `src/app/t/plans/[product]/page.tsx`
- `src/app/t/plans/plans-page-content.tsx`
- wrappers like `PlansPageContent`, `PlansContentShell`, and `AipPlansContent`
- `activeProduct` props that selected AIP vs ACP content

This technically avoided duplication, but it failed the user's route-local authoring intent.

## Correct interpretation

For static marketing/product pages, route-local authoring means:

- product-specific `page.tsx` files should be the caller/composer of the UI primitives
- visible pricing/comparison copy should be readable in the relevant route page
- shared primitives belong under `src/components/sections/<family>/...`
- app route directories should not accumulate shared page-body helper files just to avoid a few repeated shell lines

## Correct `/t/plans` shape

Use explicit static product routes when requested:

- `src/app/t/plans/page.tsx`
- `src/app/t/plans/aip/page.tsx`
- `src/app/t/plans/acp/page.tsx`

Avoid:

- `src/app/t/plans/[product]/page.tsx` unless dynamic routing is explicitly requested
- `src/app/t/plans/plans-page-content.tsx`
- `<PlansPageContent activeProduct="..." />`
- `<PlansContentShell activeProduct="...">...`
- `AipPlansContent` or similar thin page-body wrappers

Keep shared UI primitives in:

- `src/components/sections/plans/section.tsx`

Examples of acceptable primitives:

- `PlansPageSection`
- `PricingRoot`
- `PricingHeader`
- `ProductTabs`
- `ProductTab`
- `PlanRoot`
- `PlanCard`
- `CompareTable`
- `CompareTableRow`
- `CompareTableTextCell`

## Test guidance

Add/update structure tests to assert:

- dynamic `[product]` route is absent
- route-adjacent `plans-page-content.tsx` is absent
- wrapper names like `PlansPageContent`, `PlansContentShell`, and `AipPlansContent` are absent
- AIP page contains the real AIP plan cards and comparison rows
- ACP page contains the real ACP plan cards
- `src/components/sections/plans/section.tsx` remains primitive-focused rather than owning the whole page body

## Review heuristic

If the explanation for a route-local refactor is “there is no duplicate code because everything goes through one shared page-content wrapper,” pause.

Ask whether the product/page content is actually shared. If not, the wrapper is probably hiding route-local authored content and should be removed.

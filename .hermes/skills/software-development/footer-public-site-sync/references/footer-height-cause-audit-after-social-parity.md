# Footer height cause audit after social parity

Session-derived pattern from corp-web-app #865 / PR #886.

## Context

After Footer social-link policy has been aligned, a remaining Footer height delta should be remeasured and decomposed instead of being attributed to the number of social links.

Observed case:

- Legacy `/ko/internal?footerAudit=884`: Footer height `842px`, social links `5`, footer links `23`
- Tailwind `/ko/internal/tailwind?footerAudit=884`: Footer height `856px`, social links `5`, footer links `23`
- Viewport: `1280 x 633`, root font-size `16px`
- The `?footerAudit=884` query string was used to bypass stale browser/CDN state while preserving the same route rendering.

## Measurement checklist

When the user asks to separate a footer height delta after social policy parity:

1. Verify the social links are actually equal on the rendered pages.
   - Count footer links and social links.
   - Capture each social label and href.
2. Measure footer section geometry for both variants.
   - footer rect + computed padding/min-height
   - top section rect
   - footer navigation rect
   - navigation list rect + padding/gap/border
   - bottom section rect + padding/gap
   - additional/legal links row rect
   - footer information wrapper rect
   - copyright and address rects
3. Measure the tallest navigation column and its link-list item heights.
4. Compare source-level primitive contracts after browser measurement.
   - Legacy `FooterFrame` / CSS modules
   - Tailwind `TailwindFooterFrame`
   - legacy `FooterMenuLink` / `FooterAdditionalLink`
   - Tailwind `TailwindFooterLink` / `TailwindFooterAdditionalLink`
5. Report a numeric breakdown before proposing a fix.

## Diagnostic finding pattern

In the observed implementation, frame padding/gap/min-height was not the cause:

- outer footer padding: `60px 0` on both
- top section height: `184px` on both
- bottom section padding/gap: `20px 0` / `20px` on both
- footer min-height: `0px` on both

The remaining `+14px` Tailwind height decomposed into:

- `+12px` in the navigation link-list area
- `+2px` in the additional/legal links row

Root cause:

- Legacy uses `StaticDetail asChild`, so the `li` flex item itself receives the `14px / 22px` text contract.
- Tailwind applies `text-sm leading-[22px]` to the nested `a`, while the parent `li` remains unstyled and inherits the surrounding `24px` line-height.
- The visible anchor text is `14px / 22px`, but the Tailwind flex item height follows the unstyled parent `li` line box.
- In the six-link `Features` column, `2px` extra per `li` accounts for `+12px`; the additional/legal row accounts for the remaining `+2px`.

## Narrow next implementation when strict parity is required

Make Tailwind footer link `li` items participate in the same `22px` line-height contract as legacy, then remeasure the same two URLs. Do not change outer frame padding or social-link structure unless measurement shows those are the real cause.

## Browser probe shape

Use a browser console/MCP probe that returns:

- `footer`, `top`, `nav`, `navList`, `bottom`, `additional`, `info`, `copyright`, `address` rect/style
- `socialCount`, `linkCount`, social labels/hrefs/rects
- navigation columns with heading/list/link rects and computed styles

Record the exact URL, viewport, and root font-size in the audit or PR body.

# Publication detail GNB spacing: fixed reference vs in-flow target

Use this when comparing article/publication detail pages where the reference site uses a fixed/overlay header but the target site uses a sticky or in-flow header.

## Case pattern

A reference page can have a section `padding-top` that visually sits partly underneath a fixed header. The same raw padding on a target page with an in-flow sticky header produces an oversized visible GNB-to-content gap, because the header consumes document space before the section begins.

Concrete measurement pattern from a QueryPie news detail comparison at desktop `1440x1200`:

- Reference: `https://querypie.ai/news/14/mitoco-buddy-official-launch`
  - header `position: fixed`
  - header bottom: `64px`
  - section top: `0px`
  - first title Y: `191px`
  - visible header-bottom-to-title gap: `127px`
- Target: `https://www.querypie.com/ja/news/23/mitoco-buddy-official-launch`
  - header `position: sticky` / in document flow, including language banner
  - header bottom: `162px`
  - section top: `162px`
  - first title Y: `353px`
  - visible header-bottom-to-title gap: `191px`

The target gap was `64px` too large: exactly the fixed reference header height. The correct fix was to reduce the target article section top padding by that amount, not to move the header.

## Required probe fields

For both pages, at the same viewport and `scrollY=0`, record:

- `window.innerWidth` and `window.innerHeight`
- root/body computed font size
- header `position`, rect top/bottom/height
- main rect top
- publication section rect top and computed `padding-top`
- first semantic content heading rect top
- `header.bottom -> heading.top`
- `section.top -> heading.top`

## Fix rule

When the reference header is fixed/overlay and the target header is in-flow:

1. Treat `header.bottom -> first content heading.top` as the visual contract.
2. Compute `gapDelta = targetVisibleGap - referenceVisibleGap`.
3. If `gapDelta` equals the fixed reference header height or other known overlay offset, reduce the target section top padding by `gapDelta`.
4. Apply the change only to the requested page family/surface unless the user explicitly asks for all publication families.
5. Add a source-level assertion for the padding contract when an existing route/publication test reads the page source.

## Pitfall

Do not copy the reference raw section padding when header positioning differs. A raw `pt-[144px]` can be visually correct under a fixed `64px` header but render as a `64px` larger visible gap under an in-flow/sticky header.
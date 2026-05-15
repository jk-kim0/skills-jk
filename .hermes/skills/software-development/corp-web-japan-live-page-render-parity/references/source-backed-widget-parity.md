# Source-backed widget render parity

Use this reference when a corp-web-japan preview/stage page is expected to match a QueryPie reference page whose implementation exists in `../corp-web-app` as concrete widget/application components.

## Key lesson

Screenshot comparison is useful, but it is only a hotspot detector. It can reveal that a migrated page looks different, but it does not reliably explain whether the cause is root font-size policy, header/banner offset, lazy media timing, font loading, animation state, or a broken upstream component contract.

For source-backed widget pages, use this evidence chain:

1. Full-page and section-level screenshots / pixel diff identify visible hotspots.
2. DOM geometry quantifies the specific element or section delta.
3. Computed styles identify the property-level difference.
4. Upstream source inspection identifies which component/CSS contract should be ported or intentionally rebuilt.

A report that only says “screenshots differ” without element measurements and a source target is incomplete.

## Source-backed widget classification

Treat a page as source-backed widget/application work when:

- the reference implementation exists in `../corp-web-app`, and
- the page body is built from reusable application/widget components rather than simple static marketing sections, and
- visual details are owned by concrete CSS modules or design-system primitives.

Examples include pricing, plans, compare tables, tabbed product widgets, application-like feature browsers, and other components where button/icon/table/card chrome matters.

## Required source-contract inventory

Before coding or judging parity, record:

- upstream route file
- upstream widget/component files
- upstream CSS module files
- local route file
- local section/component files
- whether local code directly ports the upstream contract or rebuilds it
- compatibility layers for upstream buttons, icons, tabs, cards, tables, and tokens
- whether remaining deltas are intentional local policy or missing contract porting

## Strategy decision

Choose and document one strategy before declaring the page acceptable:

### Direct-port strategy

Port the upstream component structure and CSS-module visual contract as closely as possible. Add small compatibility layers for local tokens, buttons, icons, layout wrappers, or asset paths when needed.

Use this when the upstream source already expresses the intended UI contract and the page is widget-like.

### Measured-rebuild strategy

Keep local primitives, but require evidence that the rebuilt UI is visually equivalent enough:

- screenshot / pixel diff artifacts
- DOM geometry anchors
- computed-style comparisons
- explicit root-rem / final-pixel decision
- source-contract checklist showing what was intentionally not ported

Use this only when direct porting is not practical or would conflict with an approved local site policy.

## `/t/plans` lesson

`/t/plans` is not just a static marketing page. The reference plans page is backed by pricing and compare-table widgets in `../corp-web-app`.

For this page, text presence and route-local authoring are not sufficient. A parity audit must check at least:

- product tab geometry/style
- plan card outer geometry and internal typography
- button component and icon wrapper behavior, not text glyph approximations
- feature-list icon/text rhythm
- comparison-table wrapper width/overflow
- table section rows, normal rows, cell padding, and row heights
- root font-size and final-visible-pixel vs token-intent decision

If local code replaces the upstream pricing/compare-table contract with generic local Tailwind cards/tables/buttons without a documented measured-rebuild decision, classify that as a likely root cause of visual drift.

## Reporting rule

Classify findings as one of:

- actual defect
- intentional local-site adaptation
- external live-site artifact
- environment artifact
- needs decision

For every actual defect, include:

- screenshot or diff hotspot
- DOM geometry or computed-style evidence
- likely source/component/CSS contract to inspect next
- whether the fix should direct-port or measured-rebuild the upstream contract

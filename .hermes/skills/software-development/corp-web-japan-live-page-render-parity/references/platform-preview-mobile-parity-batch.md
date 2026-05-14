# Platform preview mobile parity batch notes

Context: a six-page corp-web-japan preview parity pass covering `/t/platforms/acp`, `/t/platforms/aip`, `/t/platforms/aip/integrations`, `/t/platforms/aip/mcp-gateway`, `/t/platforms/aip/usage-based-llm`, and `/t/services/fde` against the corresponding live `querypie.com/ja/solutions/**` pages.

## Useful audit pattern

When the user asks for several `/t/platforms/**` or `/t/services/**` parity improvements in one request, still split implementation into one branch/worktree/PR per page, but collect render evidence in a batch first:

1. Use current stage routes for the local preview baseline, not a local dev server, unless the user explicitly asks for local preview.
2. Compare each stage/live pair at desktop `1440x900` and mobile `390x844`.
3. Record `scrollWidth/clientWidth` on mobile; it catches responsive overflow faster than visual inspection.
4. Record header, h1, section, and media rectangles; for these pages, mobile H1 and fixed media wrappers were the most actionable signals.
5. Classify live header/banner chrome separately from body rhythm. Live QueryPie pages may have a language banner/header around `181px` on mobile or `162px` on desktop, while corp-web-japan stage uses its own fixed header. Compare body rhythm as `header.bottom -> h1.top` and section-internal gaps, not only absolute document top.

## Findings worth reusing

### ACP preview

Desktop hero geometry was already aligned. Mobile H1 was too large because the local ACP title used desktop-only `60px/72px`. The live mobile title used `48px/56px` while desktop stayed `60px/72px`.

Good fix shape:
- keep desktop `lg:text-[60px] lg:leading-[72px]`
- use mobile `text-[48px] leading-[56px]`
- if the route uses a family hero primitive whose desktop spacing is correct but mobile starts too close/far, make the route/page-specific hero section own `pt-[134px] lg:pt-[144px]` rather than changing the shared family primitive for all pages

### AIP preview

Desktop top offset and hero rhythm were already correct after prior AIP parity work. The remaining issue was mobile hero start: local mobile `h1.top` was about `120px` with a `64px` local header, while live mobile effectively used `header.bottom -> h1.top ~= 70px` after its own taller header. A page-specific hero section with `pt-[134px] lg:pt-[144px]` preserved desktop while improving mobile.

### AIP integrations preview

Desktop catalog geometry was close. Mobile differed in two visible ways:
- local hero started too high because `.heroSection` used `padding-top: 64px`
- live mobile integration icons rendered around `60x60`, while local kept `68x68`

Good fix shape:
- set mobile `.heroSection { padding-top: 120px; }` under the existing small viewport media query
- override `.icon` and `.iconImage` to `60px` under the same media query
- keep the semantic keyword filter contract unless public rollout explicitly needs live numeric query compatibility

### MCP Gateway preview

Mobile rendered with a huge horizontal overflow (`scrollWidth` around `1168` for a `390` viewport). Causes:
- hero image wrapper used fixed `w-[1200px] max-w-[1200px]` and image `w-[1200px] max-w-none`
- feature rows used unqualified desktop `flex-row` / fixed route widths such as `w-[540px]`
- H1 used desktop `60px/72px` on mobile and had too-wide layout

Good fix shape:
- make hero media wrapper `w-full max-w-[1200px]` and image `w-full max-w-full`
- make feature layout mobile-first stacked: `flex flex-col ... lg:flex-row` / `lg:flex-row-reverse`
- make route-authored fixed widths desktop-only, e.g. `w-full lg:w-[540px]`
- give copy/visual primitives `w-full max-w-full shrink-0`
- make H1 mobile `48px/56px`, desktop `60px/72px`, with a centered max width matching live wrapping

### Usage-based LLM preview

The body sections and media were close, but hero was visibly off:
- local mobile H1 was `64px/72px`, producing about `360px` height
- live mobile H1 was `48px/56px`, about `168px` height
- local hero started too early (`pt-[76px]`) relative to the preview header/body rhythm

Good fix shape:
- hero section `pt-[134px] lg:pt-[144px]`
- H1 `text-[48px] leading-[56px] text-[#24292F] lg:text-[60px] lg:leading-[72px]`

### FDE preview

Desktop was largely aligned, but mobile feature rows were broken by unqualified desktop flex/fixed widths:
- local scroll height nearly doubled because feature text and images stayed side-by-side with fixed widths on mobile
- live mobile stacked feature rows with media at full content width

Good fix shape:
- hero H1 mobile `48px/56px`, desktop `60px/72px`
- hero section `pt-[134px] lg:pt-[144px]`
- feature rows `flex-col ... lg:flex-row` / `lg:flex-row-reverse`
- image frame `w-full max-w-full lg:w-[var(--fde-feature-image-width)]`

## Testing pattern

For each page-specific PR, update and run only the mirrored route source test first, e.g.

```bash
node --test tests/src/app/t/platforms/acp/page.test.mjs
node --test tests/src/app/t/platforms/aip/page.test.mjs
node --test tests/src/app/t/platforms/aip/integrations/page.test.mjs
node --test tests/src/app/t/platforms/aip/mcp-gateway/page.test.mjs
node --test tests/src/app/t/platforms/aip/usage-based-llm/page.test.mjs
node --test tests/src/app/t/services/fde/page.test.mjs
```

This fits the user's preference to avoid long local build/dev verification and rely on CI/Preview for full validation.

## PR workflow note

For multi-page parity requests, open separate PRs per page even if evidence collection is batched. Each route can have its own preview deployment and reviewer can inspect the mobile fix independently.

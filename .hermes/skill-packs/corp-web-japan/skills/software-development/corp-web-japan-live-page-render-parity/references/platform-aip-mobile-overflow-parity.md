# `/t/platforms/aip` mobile render-overflow parity note

Session: 2026-05-14

Compared exact URLs:
- stage: `https://stage.querypie.ai/t/platforms/aip`
- live: `https://www.querypie.com/ja/solutions/aip`

Viewports measured:
- desktop `1440 x 900`
- mobile `390 x 844`

## Desktop result

Desktop body parity was broadly good once global chrome was separated:

- stage root font size: `16px`
- live root font size: `16px`
- stage header height: `64px`
- live header plus language banner height: `162px`
- `header.bottom -> h1.top`: `80px` on both pages
- `h1`: `60px / 72px` on both pages
- hero iframe/video: `1024 x 576` on both pages
- feature GIF desktop widths matched the live/source widths: `540`, `580`, `520`, `600`, `520`, `600` px

Main desktop differences were external/global chrome, not migrated body defects:
- live fresh profile showed a language banner
- live fresh profile could show a cookie banner
- stage uses a different header/footer implementation

## Mobile result

Mobile exposed the real discrepancy:

- stage root font size: `16px`
- live root font size: `14px`
- stage `h1`: `60px / 72px`, height about `216px`
- live `h1`: `48px / 56px`, height about `168px`
- stage section `h2`: `52px / 62px`
- live section `h2`: `32px / 40px`
- stage feature GIFs rendered at desktop widths such as `540px`, `580px`, and `600px` inside a `390px` viewport
- live feature GIFs rendered at about `342px`, matching the mobile content column
- stage feature paragraphs collapsed to narrow columns around `30px` or `73px` wide
- live feature paragraphs stayed around `342px` wide
- stage mobile scroll height was about `14043px`; live mobile scroll height was about `7258px`

Visible symptoms:
- awkward Japanese word breaks in headings such as `プラットフォーム` and `エンタープライズAI`
- feature screenshots clipped or overflowing horizontally
- feature copy squeezed into near-vertical columns
- long inline link rendered as a narrow vertical strip
- much taller stage page due to broken row layout

## Code-level root-cause candidates

Relevant files:
- `src/components/sections/aip/page.tsx`
- `src/components/sections/platform/page-primitives.tsx`
- `src/app/t/platforms/aip/page.tsx`

Observed code pattern:
- `AipFeatureRow` renders `flex-row` / `flex-row-reverse` without a mobile stacking breakpoint.
- `AipFeatureImage` sets the wrapper with route-authored fixed `style={{ width }}` values such as `540`, `580`, and `600`.
- The media wrapper has `max-w-full`, but inside the non-stacking flex row the fixed image width still consumes most of the viewport and squeezes text.
- `AipHeroTitle`, `AipValueTitle`, and `AipFeatureHeaderTitle` use desktop-sized text classes without mobile-specific downscaling.
- `PlatformPageShell` uses `overflow-x-hidden`, so the page may hide horizontal overflow while still allowing the flex layout to collapse text columns.

## Required future check pattern

When desktop looks correct but mobile is reported wrong:

1. Measure both desktop and mobile; do not infer mobile from desktop parity.
2. Compare `html` root font sizes on both pages.
3. Measure `h1`/`h2` computed font-size and line-height.
4. Measure feature-row paragraph widths, not just screenshot width.
5. Measure image rect and parent wrapper rect.
6. Compare total `document.body.scrollHeight`; a near-doubling is a strong signal that layout has collapsed.
7. Inspect whether row wrappers stack on mobile and whether fixed media widths are constrained to viewport/content width.

## Likely fix direction

Do not change the desktop fixed media widths that already match live.

Instead, add responsive behavior:
- stack `AipFeatureRow` on mobile and apply `md:`/`lg:` row direction only at desktop breakpoints
- constrain `AipFeatureImage` to `w-full` / content-column width on mobile while preserving the source-derived fixed width at desktop breakpoints
- add mobile-specific typography for `AipHeroTitle`, `AipValueTitle`, and `AipFeatureHeaderTitle` to match live mobile scale more closely

Verify on the exact hosted stage/preview URL after deployment, not only by source inspection.

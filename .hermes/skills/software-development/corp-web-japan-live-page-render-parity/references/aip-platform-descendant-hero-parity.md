# AIP platform descendant hero parity notes

Use this note when fixing existing corp-web-japan preview pages under `/t/platforms/aip/*`, especially pages that were migrated from `https://www.querypie.com/ja/solutions/aip/*` and look visually broken around the hero.

## Session-derived pattern

The AIP usage-based LLM parity PR and the MCP Gateway parity PR converged on the same hero lead pattern:

- Hero lead/description should generally use `max-w-[1000px]` with `mt-[20px]` when the source lead is intended to render as about three 28px lines on desktop.
- Narrower widths such as `max-w-[743px]` can make the same Japanese lead wrap into twice as many lines and push the hero visual down.
- Hero visual gap is commonly `lg:mt-[80px]` after the lead.
- Keep the 1200px hero image width when the source hero uses a centered 1200px visual; fix copy padding/gap before resizing the image.

## Mobile pitfall

Measure mobile separately. A desktop-oriented copy wrapper such as `px-10 pt-[155px]` can push the mobile hero far below the live page even if desktop looks close.

A verified MCP Gateway fix used:

```tsx
"mx-auto max-w-[1200px] px-6 pt-[55px] lg:px-10 lg:pt-[167px]"
"mx-auto mt-[20px] max-w-[1000px] ..."
"mt-[68px] flex justify-center lg:mt-[80px]"
```

At `390x844` this moved the preview h1 from roughly `top=230px` to `top=130px`, matching the live reference, while preserving desktop hero image alignment around `top=570px`.

## Testing

Pin the spacing contract in the mirrored source test:

- `tests/src/app/t/platforms/aip/<page>/page.test.mjs`
- Assert the hero lead has `max-w-[1000px]` and `mt-[20px]`.
- Assert the hero visual gap has the intended mobile/desktop values.
- If mobile padding was part of the defect, assert the mobile-specific wrapper classes too.

## Browser evidence to collect

For both stage/preview and live reference, at desktop `1440x900` and mobile `390x844`, capture:

- root font size
- h1 bounding rect and computed font/line-height
- lead bounding rect, max-width, margin-top, line-height
- hero image bounding rect
- horizontal overflow

Classify global header/footer differences separately from page-body geometry.
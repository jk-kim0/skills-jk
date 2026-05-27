# /t/platforms/aip render-parity implementation pattern

Session context: after comparing `https://stage.querypie.ai/t/platforms/aip` with `https://www.querypie.com/ja/solutions/aip`, the follow-up implementation PR fixed the stage/preview page rather than only reporting differences.

## Useful implementation mapping

When the browser comparison shows mobile feature rows collapsing into narrow text columns and desktop feature rows shifted because copy columns are too narrow, patch both the section primitive and the route callsites.

### 1. Feature rows need a mobile contract and a desktop contract

Broken pattern:

```tsx
<div className={`flex items-center justify-center gap-[80px] ${reverse ? "flex-row-reverse" : "flex-row"}`}>
```

Why it breaks:
- mobile still uses `flex-row` / `flex-row-reverse`
- fixed 540-600px feature media stays beside text at a 390px viewport
- the text column can collapse to ~30px and make page height almost double

Reliable pattern:

```tsx
<div className={`flex w-full flex-col items-center justify-center gap-[40px] lg:gap-[80px] ${reverse ? "lg:flex-row-reverse" : "lg:flex-row"}`}>
```

This gives:
- mobile: stacked readable copy + media
- desktop: preserve alternating row direction and 80px gap

### 2. Feature media width should be mobile-fluid and desktop-fixed

Broken pattern:

```tsx
<div className="max-w-full flex-none ..." style={{ width }}>
```

Why it breaks:
- it fixes desktop source widths correctly, but also keeps those widths on mobile

Reliable pattern:

```tsx
const featureImageStyle = { "--aip-feature-image-width": `${width}px` } as CSSProperties;

<div
  className="w-full max-w-full flex-none overflow-hidden rounded-[8px] shadow-[0_8px_20px_rgba(0,0,0,0.15)] lg:w-[var(--aip-feature-image-width)]"
  style={featureImageStyle}
>
```

This keeps the route-authored source width on desktop while letting mobile fit the content column.

### 3. Reveal wrappers can block full-width mobile behavior

If `RevealOnScroll` wraps feature copy or media, pass `className="w-full lg:w-auto"` at the route callsite. Otherwise the child can be made `w-full` but its client wrapper may still size as an auto-width flex item.

Example:

```tsx
<RevealOnScroll className="w-full lg:w-auto">
  <AipFeatureCopy className="max-w-[538px]">
    ...
  </AipFeatureCopy>
</RevealOnScroll>

<RevealOnScroll delayMs={80} className="w-full lg:w-auto">
  <AipFeatureImage width={580} ... />
</RevealOnScroll>
```

### 4. Desktop feature copy widths may need route-callsite correction

After media widths are correct, compare the copy column width and whole group anchoring. In the observed AIP comparison, the first three feature rows were still too narrow on stage, causing the group to be centered inside 1200px instead of filling the row like live.

Measured correction targets used:
- `プロンプト自動生成`: about `476px`
- `シンプルな統合`: about `538px`
- `社内文書の学習機能`: about `553px`

Keep these as route-authored `AipFeatureCopy className="max-w-[...]"` values rather than hiding the row-specific copy widths inside the primitive.

### 5. Value cards need the visible card and reveal wrapper to fill the grid row

If live shows equal-height value cards but stage action links have different baselines, check whether only the outer grid item is equal height while the visible `article` still shrinks.

Reliable pattern:
- `AipValueCard`: `flex h-full flex-col ...`
- each value-card `RevealOnScroll`: `className="h-full"`
- keep `AipValueCardLink` as `mt-auto` so action links align after the card body

### 6. Add a source-level structure test for the visual contract

For this repo, add/update the mirrored route test, for example `tests/src/app/t/platforms/aip/page.test.mjs`, to assert:
- mobile-first feature row classes exist (`flex-col`, `lg:flex-row`, `lg:flex-row-reverse`)
- media uses the CSS variable desktop-width pattern
- `RevealOnScroll` wrappers use `w-full lg:w-auto` around feature columns/media
- value cards use `h-full` on both visible card and reveal wrapper
- responsive typography classes exist where the live comparison required mobile scale-down

## Verification used

Useful lightweight checks before opening the PR:

```bash
node --test tests/src/app/t/platforms/aip/page.test.mjs
npm run typecheck
npm run test:static-pages
npx eslint src/components/sections/aip/page.tsx src/app/t/platforms/aip/page.tsx tests/src/app/t/platforms/aip/page.test.mjs
```

Do not start a local dev server by default for this user. Push the PR and let CI / Preview Deployment provide the reviewable rendered output unless explicit local browser verification is requested.

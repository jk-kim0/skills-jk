# corp-web-app `(tailwind)` route-group legacy chrome parity

Context: after corp-web-app split `(legacy)` and `(tailwind)` root layouts, the internal Tailwind smoke page at `/ko/internal/tailwind` later needed to display the same global chrome as legacy: layout shell, header/GNB, footer, and shared runtime behavior. The first visual failure mode was not the page content itself; it was the `(tailwind)` group-level layout/global CSS contract.

Durable lesson:

- When a route group changes from an isolated smoke page to legacy-chrome parity, compare and update the group `layout.tsx` before changing page content.
- Reuse the same chrome primitives and runtime inputs as legacy when the user asks for the same visible behavior.
- Keep the Tailwind group global CSS intentionally small. Do not copy the full legacy `globals.css` token/reset dump into the Tailwind root just to make shared chrome compile.

Implementation pattern used:

1. Make `src/app/(tailwind)/layout.tsx` render the same high-level chrome structure as legacy:
   - shared `Provider`
   - `Header`
   - main/content wrapper as appropriate for the route group
   - `Footer`
   - cookie preference/dimmed layer if shared runtime UX requires them
2. Import `src/app/(tailwind)/globals.css` from the Tailwind root layout, but make the preferred end state one line:
   - `@import "tailwindcss";`
   - no copied `@theme inline` block
   - no base `html/body`, `box-sizing`, `a`, `ul`, or `.dimmed-layer` rules unless a route-group-specific browser bug proves they are necessary
   - if the UI is being rebuilt in Tailwind anyway, do not keep legacy globals just to make old components keep working accidentally
3. Exclude legacy global artifacts from the Tailwind group:
   - giant `:root` token dump
   - `--rem-*`, `--doc-*`, `--gradation-*`
   - layout variables such as `--header-height`, `--layout-padding`, `--content-max-width`
   - unlayered resets such as `* { padding: 0; margin: 0; }`
   - `button { background: none; border: none; }`
4. Remove chrome dependencies on legacy CSS variables inside Tailwind-owned components. Replace with explicit Tailwind utilities or component-local values:
   - `var(--header-height)` -> explicit header height classes such as `h-[5.5rem] max-[479px]:h-[60px]`
   - `var(--layout-padding)` -> explicit gutters such as `px-[1.714rem] max-[479px]:px-6`
   - `var(--content-max-width)` -> explicit max width such as `max-w-[1200px]`
   - `var(--rem-60px)` -> explicit spacing such as `py-[3.75rem]`
5. For shared components still used by both route groups, prefer moving concrete values into the component/module or scheduling a focused refactor over growing the Tailwind group globals. Examples:
   - progress color: `#2f81f7` instead of `var(--color-blue-hover, #2f81f7)`
   - cookie banner spacing/background: explicit CSS module values instead of `var(--rem-*)` or `var(--bg-blue, ...)`
   - preview navigation toggle: keep the legacy runtime behavior and position contract, but avoid importing the legacy CSS Module component directly into Tailwind-owned chrome if it pulls legacy/PostCSS/global assumptions into the minimal route group. Instead, add a Tailwind-owned toggle wrapper/component that posts to `/api/preview-navigation`, refreshes the router, and uses explicit Tailwind classes for the same absolute position (`top: calc(100% + 16px)`, `right: 20px`; mobile `top: calc(100% + 12px)`, `right: 30px`). Wire `showPreviewModeToggle` from the route-group root layout through the Tailwind layout/header props so it appears under the same condition as legacy.
   - if the old component contract is undesirable, keep the Tailwind globals minimal and let tests/visual verification drive the component refactor
6. Update source-shape tests when the route-group contract changes. A smoke-page test may have asserted that Header/Footer are absent; replace that with assertions that the Tailwind root includes the intended chrome and runtime toggles such as Preview Toggle when `showPreviewModeToggle` is true.

Verification pattern:

```bash
git diff --check
npx vitest run src/__tests__/app/route-groups-route-local.test.tsx
```

Source-level check pattern for the minimal-global contract:

```bash
node <<'NODE'
const fs = require('fs');
const globals = fs.readFileSync('src/app/(tailwind)/globals.css', 'utf8');
if (globals.trim() !== '@import "tailwindcss";') throw new Error('tailwind globals is not minimal');
for (const forbidden of ['@theme', 'dimmed-layer', 'var(--']) {
  if (globals.includes(forbidden)) throw new Error(`tailwind globals still contains ${forbidden}`);
}
console.log('minimal Tailwind globals check passed');
NODE
```

If browser verification is in scope, open the exact deployed stage/preview URL and compare at least the following landmarks against legacy:

- header/GNB height and menu behavior
- header tool icons: language selector should use the legacy globe `LanguageIcon`, not a rotated GNB arrow placeholder
- header CTA: `Free Now` should match the legacy gradient button contract, including normal font weight, `10px 20px` padding, 10px text/icon gap, and 12px chevron `ButtonArrowIcon`
- main page top offset/wrapper width
- footer presence and spacing
- footer social links: verify the full legacy icon set is present (LinkedIn, Youtube, X, Facebook, Instagram), not only a subset
- cookie/banner/dimmed-layer behavior if visible
- whether Tailwind utilities win in computed `margin`, `padding`, `background`, and `border`

Pitfall:

Copying legacy globals into a Tailwind group can make the page look superficially closer while reintroducing the old cascade problem: unlayered reset rules and broad custom properties override Tailwind utilities or make Tailwind chrome depend on legacy-only state. The better fix is a one-line Tailwind-group global contract plus explicit Tailwind chrome values/component-local CSS. When the user says the Tailwind UI will be rebuilt anyway, do not preserve legacy global compatibility as a goal; keep the global file minimal and treat old-component compatibility as a separate tested refactor concern.
# corp-web-app Tailwind route-group responsive chrome parity

Use this reference when a `src/app/(tailwind)/**` route renders broken or incomplete site chrome compared with `(legacy)`.

## Durable lesson

A Tailwind route group can appear to have the right JSX but still break visually because the route shell, responsive breakpoint contract, and global CSS contract differ from legacy.

For corp-web-app Tailwind route-group chrome parity, check these together:

1. Root layout shell
   - `(tailwind)/layout.tsx` should compose the intended Tailwind shared layout wrapper, not a bare `<main>`.
   - Keep `Provider`, cookie preference, dimmed layer, locale detection, and preview-navigation state wiring aligned with the legacy root layout.
   - Do not satisfy a Tailwind route-group chrome request by importing legacy `Header`, `Main`, and `Footer` unless the user explicitly asks to reuse legacy components. If the task is about the Tailwind route group, wire the existing Tailwind shared chrome and make it match legacy behavior.

2. Global CSS separation
   - In corp-web-app, `(legacy)/layout.tsx` imports `src/app/globals.css`, which includes Tailwind plus legacy unlayered resets such as `* { padding: 0; margin: 0; }` and `button { background: none; border: none; }`.
   - If the user wants `(tailwind)` to be independent from legacy, create/use `src/app/(tailwind)/globals.css` and import it from `src/app/(tailwind)/layout.tsx` with `import './globals.css';` instead of `import '../globals.css';`.
   - The Tailwind route-group globals should include Tailwind import, theme token mapping, required CSS variables, dimmed layer support, and minimal base rules only. Exclude the legacy reset rules that invalidate Tailwind spacing/background utilities.
   - After splitting globals, remove workaround `!` utilities that were only compensating for the legacy reset. Keep `!` only where there is a real cascade need unrelated to the removed legacy globals.

3. Responsive bands
   - Legacy header/GNB has multiple visual bands; do not collapse them into only “desktop/tablet/compact” by Tailwind defaults.
   - Actual legacy header/GNB contract in this repo:
     - `>1260px`: desktop container with `max-width: 1200px` and no side padding.
     - `851px–1260px`: tablet/narrow band with side padding (`var(--layout-padding)`), while desktop horizontal GNB remains visible.
     - `<=850px`: mobile/compact interaction band; desktop GNB/tools hide and hamburger/mobile menu appears.
     - `<=479px`: phone compact band; global variables set `--header-height: 60px` and `--layout-padding: 24px`; `useIsPhoneWidth()` also uses `window.innerWidth <= 479`.
   - Legacy footer uses additional layout bands around `1260px`, `920px`, and `480px`.
   - Do not blindly use Tailwind defaults such as `lg:` (`1024px`) for shared chrome when the reference contract is legacy. That creates a tablet band where legacy shows desktop GNB but Tailwind shows compact UI.

4. Test shape
   - Source-shape tests should assert the route group uses the intended Tailwind layout wrapper and its own route-group globals, not stale assumptions like “Tailwind layout must not include header/footer.”
   - Add tests that `(tailwind)/layout.tsx` imports `./globals.css` and does not import `../globals.css` when the route group is meant to be independent.
   - Add a responsive contract test covering `>1260`, `851–1260`, `<=850`, `<=479`, and footer breakpoints.
   - Add a guard that the Tailwind route-group globals do not contain the legacy reset strings: `padding: 0;`, `margin: 0;`, `background: none;`, `border: none;`.

## Implementation details to check for chrome parity

When the requested comparison is specifically the `(tailwind)` group header/footer versus an existing legacy page such as `/company/about-us`, inspect more than the top-level layout wrapper:

- Header CTA: legacy uses the shared gradient button look (`linear-gradient(100deg, #0762d4 34.93%, #875ac5 76.81%, #c55a8c 99.98%)`), square-ish `6px` radius, `16px/16px` button text, `10px 20px` padding, normal `font-weight: 400`, `10px` icon gap, and the 12px `ButtonArrowIcon` chevron. A dark rounded Tailwind placeholder button, a bold `Free Now` label, or a gradient button without the chevron is visibly wrong even if the label/background matches.
- Header language/search tools: legacy uses the globe `LanguageIcon` for the language selector and a 24px search icon. Do not fake the language control with a rotated GNB arrow; the shape is visibly different in screenshots. Check the tool wrapper height/gap (`32px` wrapper, `20px` desktop gap, `10px` language/search inner gap) so the CTA aligns with legacy.
- Desktop GNB dropdown: legacy is a full-width mega menu pinned below the `88px` header, not a small per-item popover. It includes a left title/description column, a middle menu column, an optional right related-article card, a top border, and page dimming behind the menu.
- GNB menu labels should expose legacy text and related article content in source, not only simple child link arrays, so future visual parity can preserve the dropdown composition.
- Footer: legacy uses `#141920`, white logo icon, social icons (not text links), top/nav/bottom sections, `60px` vertical footer padding, `100px` desktop column gap, explicit column widths (`210px`, `105px`), and the address/copyright block. Social links should match the legacy set, not just the first few icons: LinkedIn, Youtube, X, Facebook, and Instagram, using the shared footer icon components and the same public URLs where possible. A compact black footer with text-only or incomplete social links is not parity.
- Mobile header: preserve the `<=850px` fixed menu behavior and bottom CTA bar (`Contact Us` / `Free Now`) rather than only rendering an inline accordion list.
- Source-shape tests for this class should assert the full-width mega-menu/gradient/footer contract, and tests may need `getAllByRole` for duplicated desktop/mobile controls such as `Search`.

## Common pitfalls

- A quick fix that imports the legacy `Header`, `Main`, and `Footer` into `(tailwind)/layout.tsx` restores visible chrome but bypasses Tailwind shared chrome implementation.
- Looking only at `useIsMobileHeader <= 850` misses the `1260px` container-padding band and the `479px` phone variable band.
- Keeping legacy globals in the Tailwind route group forces Tailwind classes to fight legacy resets. Prefer a route-group global CSS split over scattering `!` modifiers through Tailwind chrome.
- Treating matching header/footer presence as parity is insufficient; verify dropdown menu shape, footer section structure, CTA gradient, and social icon rendering against the reference page.

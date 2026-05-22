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

## Common pitfalls

- A quick fix that imports the legacy `Header`, `Main`, and `Footer` into `(tailwind)/layout.tsx` restores visible chrome but bypasses Tailwind shared chrome implementation.
- Looking only at `useIsMobileHeader <= 850` misses the `1260px` container-padding band and the `479px` phone variable band.
- Keeping legacy globals in the Tailwind route group forces Tailwind classes to fight legacy resets. Prefer a route-group global CSS split over scattering `!` modifiers through Tailwind chrome.

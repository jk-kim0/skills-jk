# Next.js Tailwind Adoption / CSS Modules Migration Review

Use this when the user asks whether a Next.js/React website should adopt Tailwind CSS, especially when comparing sibling repos or judging reuse between a CSS Modules-heavy app and a Tailwind-heavy app.

## Lightweight evidence to collect

1. Confirm repo identity and branch:
   ```bash
   pwd
   git rev-parse --show-toplevel
   git status --short --branch
   ```
2. Inspect styling stack in `package.json`:
   - `tailwindcss`
   - `@tailwindcss/postcss`
   - `tailwind-merge`
   - `clsx`
   - `class-variance-authority`
   - `shadcn` / `tw-animate-css`
3. Check PostCSS and Tailwind entrypoints:
   ```bash
   find . -maxdepth 2 -name 'postcss.config.*' -o -name 'tailwind.config.*'
   sed -n '1,220p' src/app/globals.css
   ```
4. Sample current styling usage:
   ```bash
   find src -name '*.module.css' | head
   rg -n 'className="[^"]*(text-|flex|grid|px-|py-|bg-|max-w-|mx-auto|gap-|rounded|shadow)' src --glob '*.tsx' | head
   ```
5. If the repo has an inventory script or plan doc, use it before forming a conclusion. For corp-web-app specifically, check:
   - `docs/plans/2026-05-19-tailwind-route-ui-transition-plan.md`
   - `npm run inventory:tailwind-pages -- --json --only-verification`

## Review lens

Separate three questions:

1. **Is Tailwind necessary?**
   - No: it is not the only viable CSS architecture.
   - Yes-ish for efficiency: in modern React/Next.js marketing/content sites, Tailwind is often a highly practical standard choice for fast section/page work, responsive layout, and shared UI primitives.

2. **Is Tailwind beneficial for this repo?**
   - Stronger yes when a sibling repo already uses Tailwind and the user wants UI/code reuse.
   - Stronger yes when many marketing/resource/publication pages need visual parity and frequent iteration.
   - Weaker yes when the existing CSS Modules/design-token system is already compact, stable, and rarely changed.

3. **What is the safe migration shape?**
   - Prefer Tailwind-first for new or migrated route/page surfaces and shared UI primitives.
   - Keep CSS Modules for complex decorative layers, pseudo-elements, animations, MDX/prose nested selectors, third-party widgets, and temporary cascade workarounds.
   - Do not make “remove all CSS Modules” the default goal.

## Reuse guidance for sibling website repos

When comparing a Tailwind-heavy repo such as corp-web-japan with a CSS Modules-heavy repo such as corp-web-app, recommend sharing at the UI primitive / layout-pattern level, not the full site/page level.

Good candidates for reuse:
- button / CTA / card / badge primitives
- section shells
- publication detail layout
- resource list/sidebar layout
- TOC/share/contact CTA patterns
- `cn()` helper conventions
- Tailwind token conventions
- browser render-parity verification patterns

Poor candidates for direct sharing:
- whole `page.tsx` files
- locale routing
- metadata/canonical/sitemap logic
- content loaders
- site-specific GNB/footer data
- CMS/blob/MDX business logic

## Global CSS baseline during route-group migration

When introducing a Tailwind route group inside an existing CSS Modules/legacy app, keep the new group-local `globals.css` as small as the user will allow. If the user says legacy UI will be rebuilt anyway, do not recreate the old token/reset layer just to keep old components comfortable.

Recommended progression:

1. Start with only the Tailwind import:
   ```css
   @import "tailwindcss";
   ```
2. Move page-shell colors, spacing, header/footer sizes, and border colors into the Tailwind layout/header/footer components rather than defining group-wide CSS variables.
3. Remove group-only legacy overlay/reset hooks such as `dimmed-layer` unless a new Tailwind component actually uses them.
4. If a sibling Tailwind repo exists, inspect its `globals.css` for useful patterns, but classify each item before copying:
   - imports that require unavailable dependencies (`tw-animate-css`, `shadcn/tailwind.css`) are not copy-paste safe;
   - shadcn-style semantic tokens (`--background`, `--foreground`, `--border`, `@theme inline`) are useful only if the new repo intends to use those semantic utilities;
   - cursor, selection, font-inheritance, and `text-rendering` base rules can be added later when repeated need is proven;
   - page-specific keyframes/helper classes belong near the owning section/component unless they are truly site-wide.
5. Add global rules later in the smallest possible units, with a test or source-level check that prevents the new `globals.css` from silently accreting legacy variables.

## Key pitfalls

- Tailwind class presence is not enough. Existing unlayered global reset or CSS Modules selectors can defeat utilities in computed style.
- In Tailwind v4, global reset/base styles should eventually live in `@layer base`; changing that can affect existing CSS Modules pages, so treat it as a separate PR/change set.
- Do not treat a sibling site's `globals.css` as automatically canonical. It may include shadcn tokens, font-face declarations, imports, dark-mode variables, and homepage animation helpers that are correct for that sibling but too broad for the target route group.
- Arbitrary values (`text-[15px]`, `max-w-[1200px]`, `bg-[#F7F9FD]`) are useful for parity but can destroy design consistency if every page invents values.
- Long className strings are a real maintainability cost. Extract repeated visual contracts into small UI/section primitives while keeping route-specific copy/composition visible in `page.tsx`.

## Recommended answer shape

1. Direct conclusion first.
2. Explain Tailwind advantages and disadvantages in general terms.
3. State whether it is “necessary” versus “efficient/practical” for modern website work.
4. Ground the recommendation in inspected repo facts.
5. Give a migration strategy: route/page-level, shared primitives first, global reset separately, CSS Modules allowed for exceptions.

---
name: documentation-list-live-parity
description: Match a documentation/resource list page or internal demo to an existing live documentation list UX by measuring the live page first and preserving sticky/CTA behavior accurately.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Documentation list live parity

Use this when a user wants a local or internal documentation/resource list page to visually and behaviorally match an existing live documentation list page.

Typical examples:
- match `/internal/mdx-list-demo` to `https://www.querypie.com/en/features/documentation`
- match a whitepaper/blog documentation list demo to the live QueryPie documentation UX
- fix a CTA/footer/sidebar parity issue after a first-pass approximation was not close enough

## Core lessons

1. Do not infer live spacing/sticky behavior from screenshots or the accessibility tree alone.
   - Use browser inspection and computed styles.
   - Measure exact values with `browser_console(expression=...)`.

2. Separate content/route migration from user-facing list UX migration.
   - A route that proves MDX/publication records load (for example a heading, developer verification sentence, and plain `<ul>`) is only a verification stub.
   - For a migrated resource/blog list to be visually complete, also check hero copy, category sidebar/drawer, card grid, thumbnails, badges, dates, responsive behavior, and load-more/progressive state.
   - When documenting gaps, call this out explicitly as an experience-migration gap, not a small styling mismatch.

3. If the user asks for a parity/migration document in Korean or requests the work in Korean, write the report body, headings, tables, and checklist items in Korean by default.
   - Keep implementation identifiers such as URLs, routes, file paths, component names, code fields, and established technical terms in English.
   - Do not leave broad English report headings like `Executive summary`, `Current state`, `Recommended implementation plan`, or `Bottom line` in an otherwise Korean document.

2. For sticky sidebars, choose the sticky target carefully.
   - If the layout needs a mobile horizontal-scroll wrapper, do **not** assume the innermost nav should be sticky.
   - A safer pattern is often:
     - `aside` = sticky column (`lg:sticky lg:top-[...] lg:self-start`)
     - inner wrapper = mobile overflow handling only
     - nav = semantic structure only
   - If sticky appears not to work, inspect which ancestor has overflow or flex constraints.

3. When the user says “match the live CTA exactly,” compare the whole section, not only the button.
   - Background color
   - section padding
   - spacing from the previous section
   - inner max-width
   - headline/body line-height
   - button component/style

4. Before approximating a button, re-check latest `origin/main` for newly merged shared UI.
   - In corp-web-japan, rebasing onto latest main can reveal a shared CTA button that was not available on the older PR base.
   - Example learning: `BrandGradientCtaButton` existed on latest main and matched the live documentation CTA button better than custom local gradient classes.

## Recommended workflow

1. Start from the correct branch context.
   - New work: latest `origin/main` + fresh worktree.
   - Existing PR follow-up: fresh worktree from the PR branch tip.

2. Inspect the live target page with browser tools.
   - Navigate to the exact live URL.
   - Use computed-style inspection for:
     - sticky sidebar target and `top`
     - CTA background color
     - CTA padding
     - gap between content section and CTA
     - button dimensions and typography

   Example inspection targets:
   - CTA section
   - CTA inner text wrapper
   - CTA button
   - sidebar nav / aside / parent row

3. Inspect the current local implementation.
   - Read the route file.
   - Read any shared list/CTA/sidebar primitives.
   - Search for reusable shared button components before adding new one-off styles.

4. Implement the smallest parity fix.
   - Prefer route-local composition changes.
   - Prefer shared components already present on latest main.
   - Only add new hooks to shared primitives if the route truly needs them.

5. Re-check likely parity traps.
   - Sticky placed on wrong element
   - parent/ancestor overflow breaking sticky
   - background applied only to an outer wrapper while the visible inner surface stays white
   - CTA spacing mismatch caused by previous section bottom padding, not CTA padding alone

## Specific parity findings worth reusing

### Plain route-local index vs MDX-rendered internal list

When comparing an internal/demo index route against another simple-looking index page, do not assume both pages share the same renderer just because both show a heading plus links. In corp-web-app, a dynamic MDX route may receive MDX list components, section wrappers, and default bottom CTA injection from `dynamic-page.tsx`, while a route-local TSX page with plain `<ul>/<li>/<Link>` receives only global CSS resets.

Investigation pattern:
- Inspect the actual DOM chain and computed styles for a representative list item on both pages.
- Check for nested landmarks such as an inner `<main>` under the root layout `<Main>`; flex parents with `align-items: center` can make the child shrink to content width unless `width: 100%` is set.
- Check global resets for `a { color: inherit; text-decoration: none; }` and `ul { list-style: none; }`; plain route-local lists may lose link affordance and bullets unless they use explicit classes/components.
- If the reference page has a CTA below the list, verify whether it is authored by the page or injected by a dynamic/MDX layout path.
- Also audit the explicit list registry against actual available routes; visual confusion can hide missing index entries.

See `references/corp-web-app-archived-vs-internal-index.md` for a concrete stage investigation.

### Sticky sidebar

When a list page has:
- a flex row with sidebar + content
- mobile overflow wrapper for the sidebar menu

A robust structure is:
- `aside`: sticky at desktop (`lg:sticky lg:top-[128px] lg:self-start`)
- `ResourceListSidebarViewport`: mobile overflow only
- `nav`: semantic wrapper, not the sticky target

### Live docs CTA values observed on QueryPie docs

For `https://www.querypie.com/en/features/documentation` the CTA section used values like:
- background: `#F6F8FA`
- section padding: about `112.5px 22.5px`
- previous content section bottom padding: about `187.5px`
- CTA content max width: about `772px`
- headline size/line-height: about `48.75px / 58.125px`
- body size/line-height: about `15px / 24.375px`

Treat these as a starting parity reference, but always re-measure the live page in case it changed.

## Verification

Use the lightest checks first:
- eslint on touched files
- `npm run typecheck`

For visual parity complaints, prefer a browser/live inspection loop over local speculation.

## Pitfalls

- Saying “it matches” after changing only one property like background color
- Forgetting that the visible CTA surface may be an inner wrapper, not the outer section
- Leaving a PR branch unrebased when latest main already contains the better shared button/component
- Treating sticky failure as a Tailwind issue before checking overflow/flex ancestor behavior

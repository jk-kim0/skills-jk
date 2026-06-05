# corp-web-app Tailwind route with legacy CSS-variable components

## Trigger

Use this when a corp-web-app page is moved from `(legacy)` to `(tailwind)` and the Preview renders as visually broken even though the route exists and CI passes.

## Symptom pattern

A page migrated into `src/app/(tailwind)/**` may still import legacy visual primitives such as:

- `CenterSection`
- `StaticH1` / `StaticH2` / legacy heading primitives
- `StaticHeader` / legacy text primitives
- form widgets whose CSS Modules use `var(--rem-*)`, `var(--text-body)`, `var(--bg-white)`, `var(--color-error)`, etc.

In `(tailwind)/globals.css`, only Tailwind may be imported. The legacy global token file may not be loaded, so those CSS variables resolve empty. Browser evidence can show:

- H1 computes to browser/default inherited text size such as `16px` instead of the intended marketing heading size.
- Section padding/gap computes to `0px`/`normal` because `var(--rem-*)` is undefined.
- Form inputs lose padding, background, radius, and label sizing.
- The JSX/className source looks plausible but computed styles are broken.

## Diagnosis probe

Use a rendered Preview probe, not source inspection only. Compare at least:

- `getComputedStyle(document.documentElement).getPropertyValue('--rem-12px')`
- `getComputedStyle(document.documentElement).getPropertyValue('--text-body')`
- H1 `fontSize` / `lineHeight`
- section `padding`
- form `gap`
- first text input `padding`, `backgroundColor`, `borderRadius`, `fontSize`

If the variables are empty and computed values collapse, the migration kept legacy CSS-variable components inside the Tailwind route group.

## Fix pattern

Prefer rebuilding the migrated page shell with Tailwind-native primitives that mirror the sibling/canonical implementation. For corp-web-app pages ported from corp-web-japan, this often means copying the structural primitive shape rather than keeping legacy wrappers:

- `CompanyPageSection`
- `CompanyPageLayout`
- `CompanyPageIntro`
- `CompanyPageTitle`
- `CompanyPageLead`
- route-specific checklist/panel primitives

Remove legacy foundation visual imports from locale page files. Keep route-local authoring visible in `page.en.tsx`, `page.ko.tsx`, and `page.ja.tsx`.

If an existing legacy form widget must be reused to preserve submission behavior, do not import the whole legacy globals file into `(tailwind)/globals.css` as a quick fix. Scope only the required legacy variables to the form panel/wrapper. This keeps the page migration narrow and avoids changing global Tailwind route behavior.

## Verification

After pushing, wait for the new Preview attached to the current head SHA and rerun the same probe. A recovered page should show concrete computed values rather than empty variable fallbacks, for example:

- H1 has an intended marketing size/line-height, not `16px / 24px`.
- Section has explicit top/bottom/side padding.
- Form has a real flex gap.
- Inputs have real padding, background, radius, and font size.

Update the PR body if the initial implementation notes claimed a different Tailwind contract than the final fix.
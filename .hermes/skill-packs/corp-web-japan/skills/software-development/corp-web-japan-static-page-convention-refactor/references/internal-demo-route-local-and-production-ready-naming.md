# Internal demo route-local authoring and production-ready naming correction

Session lesson from corp-web-japan PR #496 / issue #395 follow-up.

## What went wrong

Two separate route-local-authoring mistakes happened on an internal demo route:

1. Treating `src/app/internal/demo-sections/page.tsx` as exempt from route-local refactoring because it was an internal route.
   - The route still had large top-level prop/data blobs such as `roleSlidesDemoProps`, `useCaseShowcaseDemoProps`, and `aiDashiFaqItems`.
   - The route body still used hard-to-review raw wrapper markup like `<section className=...>` and `<article className=...>`.
   - The user corrected that internal demo pages can still be route-local refactoring targets when they are static review/demo pages.

2. Naming extracted primitives with route-status terminology such as `InternalDemoAvatarSwatch`.
   - Even when the file path remains under `src/components/sections/internal-demo/`, exported component symbols should be production-ready and neutral.
   - The user explicitly rejected `InternalDemo*` component names.

## Corrected pattern

For a static internal demo page:

- Keep `src/app/internal/<route>/` limited to `page.tsx` unless framework route files are actually needed.
- Put demo-only implementation under a clear family directory such as `src/components/sections/internal-demo/**`.
- Keep `page.tsx` as the readable authored surface:
  - no large top-level prop blobs for the showcased content
  - no opaque raw wrapper markup when semantic primitives make intent clearer
  - children/slot-style examples are preferred so sample copy is visible in route order
- Use production-ready component symbols even inside internal/demo file paths:
  - good: `SectionShowcaseSection`, `SectionShowcaseIntro`, `SectionShowcaseCardGrid`, `SectionShowcaseAvatarSwatch`
  - bad: `InternalDemoSection`, `InternalDemoIntro`, `InternalDemoCardGrid`, `InternalDemoAvatarSwatch`

## Structure-test contract used

The structure test should assert both the route connection and the naming/readability contract:

- old orphan/root paths are absent
- `src/app/internal/<route>/` contains only `page.tsx`
- demo widgets are imported from `src/components/sections/internal-demo/**`
- old prop blob names are absent
- raw `<section className=` / `<article className=` wrappers are absent when semantic primitives are the chosen route contract
- neutral primitives such as `SectionShowcaseSection`, `SectionShowcaseIntro`, and `SectionShowcaseCardGrid` are present
- `InternalDemo` does not appear in the route source

## Verification commands from the session

```bash
node --test tests/src/app/internal/demo-sections/page.test.mjs tests/crew-role-assets.test.mjs tests/launch-readiness-coverage.test.mjs tests/link-and-metadata-integrity.test.mjs
/Users/jk/workspace/corp-web-japan/node_modules/.bin/tsc --noEmit
/Users/jk/workspace/corp-web-japan/node_modules/.bin/eslint src/app/internal/demo-sections/page.tsx src/components/sections/internal-demo/section-showcase-primitives.tsx src/components/sections/internal-demo/role-slides.tsx src/components/sections/internal-demo/use-case-showcase.tsx src/components/sections/internal-demo/ai-dashi-faq.tsx tests/src/app/internal/demo-sections/page.test.mjs
```

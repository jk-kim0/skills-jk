# Route-local authoring component placement correction

## Session lesson

In the issue #395 internal-demo follow-up, "route-local authoring" was misread as "move internal-only UI widgets beside the App Router `page.tsx`." That produced component files such as:

- `src/app/internal/demo-sections/role-slides.tsx`
- `src/app/internal/demo-sections/use-case-showcase.tsx`
- `src/app/internal/demo-sections/ai-crew-avatar.tsx`
- `src/app/internal/demo-sections/ai-dashi-faq.tsx`

The user corrected this directly: `src/app/internal/demo-sections/` should contain `page.tsx` only.

## Correct interpretation

Route-local authoring is about authorship and readability, not filesystem colocation of UI components.

- `src/app/<route>/page.tsx` owns route entry, metadata, visible copy, section order, and composition.
- `src/components/sections/**` owns section/UI component implementations, styling, layout classes, and isolated client behavior.

For internal demo widgets, the corrected destination was:

- `src/components/sections/internal-demo/role-slides.tsx`
- `src/components/sections/internal-demo/use-case-showcase.tsx`
- `src/components/sections/internal-demo/ai-crew-avatar.tsx`
- `src/components/sections/internal-demo/ai-dashi-faq.tsx`

The route file then imports them via `@/components/sections/internal-demo/...`.

## Review check

Before committing route-local refactors, check:

```bash
find src/app/<route> -maxdepth 1 -type f -print | sort
```

For ordinary static/internal demo routes, expect only `page.tsx` plus explicit App Router route files such as `layout.tsx`, `loading.tsx`, `not-found.tsx`, or `route.ts` if actually needed.

If you see ordinary component files like `hero-section.tsx`, `faq.tsx`, `role-slides.tsx`, or `use-case-showcase.tsx`, move them under `src/components/sections/<family-or-surface>/**` unless the user explicitly approved a route-adjacent exception.

## Related PRs

- PR #496 corrected the internal demo branch to keep `src/app/internal/demo-sections/` limited to `page.tsx` and move widgets under `src/components/sections/internal-demo/**`.
- PR #501 updated the repo-local `static-page-route-local-authoring` skill to make this file-location contract explicit.

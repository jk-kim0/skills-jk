# Component Name Debug implementation pattern

Use when implementing or following up on the `platform-component-name-debug` reviewer tool in `corp-web-app`, especially when porting from `corp-web-japan` PR #592 or `outbound-agent`.

## Reference shape

The working implementation mirrors the sibling apps at the contract level, but `corp-web-app` has both legacy and Tailwind header/layout surfaces.

Core files:

- `src/lib/component-name-debug.ts`
  - build-time `COMPONENT_NAME_DEBUG_ENABLED = true`
  - `componentNameDebugProps(componentName)` validation/helper
  - localStorage mode key/event helper
  - mode list in this order: `Off`, `Pointer`, `Pointer + Ancestors`, `Always`
  - `nextComponentNameDebugMode()` for `Alt+Shift+N`
- `src/components/layout/component-name-debug-overlay.tsx`
  - global client overlay
  - pointer / ancestor / always marker collection
  - lower-left and upper-right label placement
  - click-to-copy via Clipboard
- `src/components/layout/component-name-debug-overlay.module.css`
  - fixed max z-index overlay, `pointer-events: none`
  - labels use `pointer-events: auto` and `cursor: copy`
- `src/components/layout/component-name-debug-menu-section.tsx`
  - `Show Component Name` menu section
  - `Shortcut: Alt+Shift+N`
- `src/app/(legacy)/layout.tsx` and `src/app/(tailwind)/layout.tsx`
  - both must mount `<ComponentNameDebugOverlay />`

## Header integration

`corp-web-app` has two header variants:

- legacy: `src/components/layout/header/ui/header-primitives.component.tsx`
- Tailwind: `src/components/layout/tailwind-header/ui/header-primitives.component.tsx`

Apply the same feature contract to both:

1. Import `componentNameDebugProps` and `isComponentNameDebugEnabled` from `src/lib/component-name-debug`.
2. Compute `const componentNameDebugEnabled = isComponentNameDebugEnabled();` in `HeaderFrame`.
3. Add markers to meaningful existing surfaces, not marker-only wrappers:
   - `<header {...componentNameDebugProps('SiteHeader')}>`
   - `<nav {...componentNameDebugProps('SiteHeaderNav')}>`
   - desktop action wrapper: `{...componentNameDebugProps('SiteHeaderActions')}`
4. Render the reviewer tool independently from preview-mode controls:
   - `showPreviewModeToggle || componentNameDebugEnabled ? <PreviewModeToggle ... showPreviewModeControls={showPreviewModeToggle} /> : null`
   - Tailwind variant uses `TailwindPreviewModeToggle` but should expose the same behavior.

## Tailwind route group named marker follow-up

When following up on Component Name Debug for the Tailwind route group, do not stop at the Tailwind header/menu/overlay contract. Add markers to meaningful page-shell and shared-section components that reviewers actually point at on Tailwind pages:

- Common Tailwind shell: `TailwindLayout`, `TailwindMain`.
- Resource list surfaces: `ResourceCollectionListPage`, `ResourceListHeroSection`, `ResourceListContentSection`, `ResourceListSidebar`, `ResourceListItems`, `ResourceListCard`, `NewsListPageSection`, `NewsListItems`, `NewsListCard`, `ProgressiveLoadMore`.
- Resource detail surfaces: `ResourceDetailLayout`, `ResourceDetailHeader`, `ResourceDetailBody`, `ResourceDetailSidebar`, `ResourceDetailSidebarSection`, `ResourceDetailTocList`, `ResourceRelatedPostCards`.
- Route-local detail page roots: `BlogDetailPostPage`, `NewsDetailPostPage`, demo/event/whitepaper/privacy/tutorial detail page roots, plus major route-local widgets such as `BlogPostToc`, `PublicationShareButtons`, and `IntroductionDeckGatedContent`.
- Company/Tailwind section primitives: `CompanyPageSection`, `CompanyPageIntro`, `CompanyPageTitle`, `CompanyPageLead`, `CompanyPageLayout`, `AboutUsSection`, `AboutUsHeroCopy`, `AboutUsHeroImage`, `AboutUsLeaderCard`, `AboutUsLocationCard`, `ContactUsChecklist`, `ContactUsFormPanel`, and similar meaningful existing surfaces.

For shared layouts used by multiple detail pages, prefer a typed pass-through like `componentNameDebugName?: string` on the shared component instead of wrapping page output only to expose a label. For example, `ResourceDetailLayout` can default to `ResourceDetailLayout` but accept `componentNameDebugName="IntroductionDeckDetailPostPage"` so the overlay shows the route-local page component name on the real root section.

Verification additions:

- Extend `src/components/layout/__tests__/component-name-debug.test.ts` with source-level assertions for the Tailwind route group markers.
- Assert both the shared component default marker contract and route-local overrides where a common layout is reused.
- Run focused shell tests and eslint over all changed TS/TSX files; no dev server is needed for this source-level marker work.

## Preview toggle/menu pattern

Extend the existing preview toggle instead of adding a second floating button:

- Add optional `showPreviewModeControls?: boolean`.
- Trigger label is `Preview mode menu: ON/OFF` when preview controls are present.
- Trigger label is `Reviewer tools menu` when only Component Name Debug is available.
- Button letter can switch from `P` to `D` when preview controls are hidden.
- Menu should contain preview controls only when `showPreviewModeControls` is true, but always include `<ComponentNameDebugMenuSection />` when the build-time debug constant is enabled.
- Use click-outside and Escape handling for the menu.

For Tailwind routes, keep the public `src/components/layout/tailwind-preview-mode-toggle.tsx` entrypoint. If latest `main` already has an inline Tailwind dropdown implementation there, preserve that inline implementation and add the Component Name Debug section inside the same panel instead of replacing it with the CSS-module version. The legacy header toggle can continue to use `preview-mode-toggle.module.css`.

## Rebase/conflict follow-up pattern

When rebasing this feature over a `main` that already added preview toggle dropdown behavior, expect conflicts in:

- `src/components/layout/header/ui/preview-mode-toggle.component.tsx`
- `src/components/layout/tailwind-preview-mode-toggle.tsx`
- `src/components/layout/__tests__/tailwind-layout.test.tsx`

Resolve by preserving the newer `main` preview dropdown behavior and copy, then reapply only the debug additions:

1. Keep `useId`, `useRef`, `isMenuOpen`, click-outside, Escape handling, and `aria-haspopup="menu"` from latest `main`.
2. Add `isComponentNameDebugEnabled`, `ComponentNameDebugMenuSection`, `showPreviewModeControls?: boolean`, and the `Reviewer tools menu` label path.
3. Keep latest-main preview option descriptions when present, for example `Use preview navigation for review routes.` and `Use public navigation and normal routes.` Do not revert them to older sibling-repo wording such as `reviewer unlocks` / `normal gates` unless explicitly requested.
4. In the Tailwind toggle, preserve the inline Tailwind classes and just widen the panel enough for both sections, e.g. `grid w-[min(280px,calc(100vw-32px))] gap-3`, then append `<ComponentNameDebugMenuSection />`.
5. In the Tailwind layout test, keep latest-main assertions such as `aria-haspopup="menu"`, and keep/add source assertions for `showPreviewModeControls?: boolean`, `Reviewer tools menu`, and `<ComponentNameDebugMenuSection />`.

## Verification pattern

Use source-level shell tests because this feature is a reviewer/debug foundation and should not require starting a dev server.

Recommended tests:

- Add/maintain `src/components/layout/__tests__/component-name-debug.test.ts`.
- Assert:
  - build-time constant exists and does not read `process.env`
  - both legacy and Tailwind headers expose the reviewer menu when `componentNameDebugEnabled`
  - mode order includes `off`, `pointer`, `ancestors`, `always`
  - `Alt+Shift+N` shortcut checks `altKey`, `shiftKey`, `KeyN`
  - shortcut ignores `INPUT`, `TEXTAREA`, `SELECT`, and contenteditable targets
  - markers use `data-component-name` via `componentNameDebugProps`
  - header markers include `SiteHeader`, `SiteHeaderNav`, `SiteHeaderActions`
  - overlay includes Always mode, max label cap, lower-left/right-top label placement, Clipboard copy
  - both route group layouts mount `<ComponentNameDebugOverlay />`

Commands that proved the pattern:

```bash
npm run test:shell
npm exec -- eslint src/lib/component-name-debug.ts \
  src/components/layout/component-name-debug-overlay.tsx \
  src/components/layout/component-name-debug-menu-section.tsx \
  src/components/layout/header/ui/preview-mode-toggle.component.tsx \
  src/components/layout/tailwind-preview-mode-toggle.tsx \
  src/components/layout/header/ui/header-primitives.component.tsx \
  src/components/layout/tailwind-header/ui/header-primitives.component.tsx \
  src/components/layout/__tests__/component-name-debug.test.ts \
  src/components/layout/__tests__/tailwind-layout.test.tsx \
  --max-warnings=0
git diff --check
```

After a conflict rebase, rerun the same commands before `git rebase --continue`, then `git diff --check origin/main...HEAD` before force-pushing.

## Pitfalls

- Do not add page-local wrappers or generic shells only to make debug labels appear. Mark already meaningful component roots/sections/cards/panels/headers/bodies.
- Do not gate availability by runtime environment variables. The spec requires a build-time implementation constant.
- Do not implement only one route group/header variant; legacy and Tailwind routes need equivalent controls and overlay mounting.
- Do not blindly prefer the feature branch side during rebase conflicts. If `main` evolved the preview toggle UI, keep `main` as the base behavior and reapply only the component-name debug layer.
- After running Prettier, source-level tests that assert exact double-quoted strings can fail because this repo formats TypeScript with single quotes. Prefer quote-neutral regex assertions.
- Worktrees may not have a direct `./node_modules/.bin/eslint`; `npm exec -- eslint ...` is a safer focused-lint invocation when dependencies are available through npm resolution.

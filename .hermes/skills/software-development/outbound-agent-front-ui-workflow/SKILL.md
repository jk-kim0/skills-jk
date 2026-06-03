---
name: outbound-agent-front-ui-workflow
description: Implement and review QueryPie outbound-agent front-end UI changes in Next.js App Router, especially AppShell/top-bar/dropdown/menu work grounded in docs/ui decisions.
version: 1.0.0
metadata:
  hermes:
    tags: [outbound-agent, frontend, nextjs, ui, app-shell, pull-requests]
---

# Outbound Agent Front UI Workflow

Use this skill when working in `querypie/outbound-agent` on front-end UI changes, especially `front/src/components`, App Shell, top-bar controls, dropdown menus, shared UI class tokens, or UI changes derived from `docs/ui/*` guidance.

## Workflow

1. Confirm repo state before editing.
   - Run `git status --short --branch` in the repo root.
   - Fetch/update latest `origin/main` and use a repo-local `.worktrees/<topic>` worktree for file changes.
   - Do not modify the root checkout except for read-only inspection or fast-forwarding clean local `main` when appropriate.

2. Ground the UI change in canonical docs and existing implementation.
   - Read relevant `docs/ui/*` docs first, such as `docs/ui/display-size-guidelines.md`, `docs/ui/screen-overview.md`, and `docs/ui/terms.md`.
   - Inspect existing shell/control code before adding new UI: `front/src/components/app-shell.tsx`, route-local components, `front/src/lib/ui/class-names.ts`, and any design-contract tests.
   - When updating UI design docs for an already-implemented page, name page regions/parts by the actual Named Component names in the current implementation (for example `PageHeader`, `EmailSenderRegistrySection`, `EmailSenderEntityCardList`, `EmailSenderEntityCard`) rather than generic phrases like “영역”, “부분”, “card list”, or “wrapper section”. Add a short component-name map when the doc introduces the screen.
   - If a prior PR is referenced, verify whether it is merged and inspect the landed files on latest `main` rather than relying on the PR title/body alone.

3. Preserve top-bar ordering and future reserved slots.
   - When adding or moving a top-bar utility near Help, place it intentionally relative to the build version and Help.
   - Current outbound-agent top-bar direction is to keep user-facing utility clutter folded under a single `Help` dropdown when the user asks to replace separate compact buttons.
   - For Help consolidation work, implement `version → Help Dropdown Menu → notification indicator` in `topbar-tools`; do not leave separate `FV`, `Hidden`, or direct `/docs` Help triggers next to it.
   - Structure the Help Dropdown Menu in the requested order when applicable: `User Manual` linking to `/docs`, separator, `Hidden pages` section with the hidden page list, separator, then `Feature Visibility` section with the three visibility options.
   - If latest `main` already contains `HelpMenu`, do not leave implementation plans saying “convert Help to a dropdown” or “create `help-menu.tsx`.” Rebase first, inspect `front/src/components/app-shell.tsx` and `front/src/components/help-menu.tsx`, then phrase follow-up work as modifying the existing `HelpMenu` and adding any new section in the current menu order.
   - Preserve Feature Visibility state/localStorage behavior by moving only the option UI into the Help menu; a state helper module may still own `visibilityOptions`, storage key, event name, subscribe/read helpers, and `shouldShowFeatureStatus`.
   - If the user says a utility should be “right next to Version” or that a version label will be placed to the left of the new button, implement the requested source order in `topbar-tools`, not inside the Team selector/context group.
   - When a top-bar utility dropdown is moved or consolidated, update structure/design tests that pin the source order, absence of old triggers, section ordering, and option counts so future edits do not drift it back into `topbar-context` or separate buttons.

4. Prefer a focused client component for browser-side controls.
   - Put browser-only interactions such as `window.resizeTo`, `window.innerWidth`, localStorage, or `useSyncExternalStore` into a separate `"use client"` component.
   - Keep `AppShell` as a thin server component that imports and places the client control.
   - Define standard option lists as exported constants when tests or future docs may need to verify them.
  - For debug-only visual aids such as component-name inspection, prefer a single global client overlay plus explicit DOM markers (`data-component-name`) over making every component render its own hover label. The component should declare its code-matching React component name; the overlay should own pointer tracking, label positioning, localStorage state, and non-interference (`pointer-events: none`, `aria-hidden`).
  - For component-name inspection controls, prefer a four-mode selector rather than a binary toggle when the user needs focused inspection, ancestor context, and full-screen structure review: `Off`, `Pointer`, `Pointer + Ancestors`, and `Always`. Prefer `Pointer` over `Hover` because the implementation tracks pointer targets, not CSS `:hover`; prefer `Pointer + Ancestors` over `Hover & Ancestors` for clearer menu wording. Put these under a distinct `Show Component Name` section in the Help dropdown, use radio-style menu items, and persist the mode (not a boolean). Apply shell-wide: authenticated `AppShell` uses the existing `HelpMenu`, while public `DocsShell` needs an equivalent docs-header debug menu because it does not have the authenticated Help dropdown. For broad marker coverage, plan a stacked PR sequence and defer `Always` until route-local marker coverage is in place; early PRs should implement only `Off`, `Pointer`, and `Pointer + Ancestors`. If a keyboard shortcut is requested, document a low-conflict cycling shortcut such as `Alt+Shift+N` / `⌥⇧N`, avoid Chrome DevTools picker conflicts like `Cmd/Ctrl+Shift+C`, and ignore the shortcut while `input`, `textarea`, `select`, or `contenteditable` has focus. See `references/component-name-debug-mode-stacked-plan.md` for the staged implementation pattern.
  - If a requested top-bar Help utility needs controls under “Help” but `Help` is currently a plain `/docs` link, plan or implement a `HelpMenu` client component that preserves the existing Docs navigation as a menu item and adds the new control below it, rather than adding a separate adjacent top-bar button without addressing the requested menu location.

5. Use shared class tokens and structure tests.
   - Add or reuse tokens in `front/src/lib/ui/class-names.ts` instead of scattering one-off class strings through the component.
   - Update design-contract tests such as `front/src/components/app-shell-design.test.ts` when placement/order is part of the product expectation.
   - For simple UI contracts, string-based Vitest tests can verify labels, standard sizes, and shell placement without starting a dev server.
   - When moving an existing App Shell control between regions (for example Top Bar → Left Sidebar), assert both the new order and the absence/staleness of the old placement expectation in the design contract test.

6. For settings/profile UI refactors, preserve the data contract deliberately.
   - If the user asks to remove a broad edit section but keep one editable property, prefer a dedicated server action/service for that single property instead of reusing a multi-field update action with hidden inputs for all required fields.
   - Hidden required fields can fail when current data is optional or not set, and they can accidentally keep unrelated fields editable through the back door. A single-field action should validate only the field being changed and revalidate the same route/layout paths as the broader action.
   - When the user says rarely changed settings do not need an aggregate editor, keep them as read-only rows with small per-row `Edit` triggers. Each row Dialog should save only that row's field(s): for example Team name, Team slug, and Team market should use separate actions/services instead of resurrecting an `Edit Team` section.
   - For grouped-but-atomic rows such as Team market, edit the natural row unit together (`country` + `language`) while still avoiding unrelated Team fields such as name, slug, or profile image.
   - Reuse existing primitives such as `front/src/components/ui/dialog.tsx` for pop-up/Dialog edits before adding a new modal implementation.
   - In route-local app pages, keep the page readable by extracting meaningful local components such as `TeamProfileSection`, `TeamProfileImageChangeDialog`, `TeamNameEditDialog`, `TeamSlugEditDialog`, `TeamMarketEditDialog`, and `TeamDangerZoneSection` rather than leaving long anonymous sections or moving copy into a generic renderer.

7. Keep UI design docs in sync with shell placement changes.
   - For App Shell placement changes, update `docs/ui/screen-overview.md` and the relevant shared widget doc such as `docs/ui/common-widgets.md` in the same PR.
   - If the change affects Sidebar IA expectations, also update `docs/ui/sidebar-navigation-ia-plan.md` so docs no longer point users to the old menu location.
   - Replace old location language explicitly (for example “Top Bar Team selector”) rather than only adding new copy, otherwise design docs will contradict the implementation.

7A. For docs-only UI design/OpenSpec requests, inspect implementation but do not implement code unless explicitly asked.
   - When the user asks to improve a route's UI design and says to update 설계 문서/OpenSpec, treat it as documentation/spec work by default.
   - Read the live route implementation enough to identify current section names, copy location, wrapper surfaces, and data/order assumptions, but keep file changes in `docs/**` and `openspec/**`.
   - If no route-specific UI doc exists, create a focused `docs/ui/<route-or-surface>.md`, add it to `docs/ui/README.md`, and connect it from the relevant feature doc.
   - Record accepted product choices in the active OpenSpec `design.md` plus SHALL/SHALL NOT scenarios in the relevant spec, including explicit non-goals such as “UI does not invent client-side default sorting.”
   - For Entity Card-style absence states, distinguish passive empty/no-item states from required-creation cards; required setup should be documented as a required-creation card, not generic empty text.
   - For root-level system/admin surfaces such as `/system/`, explicitly distinguish them from Team-scoped settings (`/{teamSlug}/settings/**`) in the feature/UI plan. Document the route-level access guard, where the entrypoint appears, and the visible paths that need PR `UI 변경` coverage.
   - When a feature plan asks whether a rarely changed setting needs a DB table or code/YAML configuration, include a concrete persistence trade-off in `Domain / Data / API 영향`: code/YAML + env vars, existing model reuse, and new DB table options; do not default to a settings table unless runtime editing/audit is in scope.

8. Verification should be narrow unless the user requests local full verification.
   - Link worktree `front/node_modules` to the root checkout when needed: `cd front && ln -s ../../../front/node_modules node_modules`.
   - Run `git diff --check`.
   - Run focused Vitest tests for changed components.
   - Run focused ESLint on changed files. With the current ESLint flat config, do not use Next-era `npm run lint -- --file ...`; run from `front/` with explicit path arguments instead, for example `./node_modules/.bin/eslint src/components/foo.tsx src/__tests__/foo.test.ts --max-warnings=0`.
   - If a front-end task touches `front/prisma/schema.prisma`, run `npm run prisma:validate` and `npm run typecheck` from `front/` using Node 24.
   - In outbound-agent, Prisma schema changes are folded into the single baseline migration `front/prisma/migrations/20260530000100_baseline_main_schema/migration.sql`; do not add a second migration directory unless the repo policy/tests change. The CI test `src/__tests__/schema-migration-artifacts.test.ts` currently rejects additional migration directories.
   - Do not start a dev server or run full build/test unless explicitly requested or necessary for confidence.

9. Commit, push, and create/update the PR.
   - Re-fetch and rebase onto latest `origin/main` before pushing.
   - After pushing, re-query the PR with `gh pr view <number> --json headRefOid,baseRefOid,mergeStateStatus,statusCheckRollup` and compare the PR `baseRefOid` with the freshly fetched `origin/main`. If `main` advanced while the work was being rebased or pushed, fetch/rebase/push again before reporting that the PR is on the latest main.
   - Commit only relevant files.
   - Push the feature branch and create/update the PR with a Korean title/body for this repo.
   - For PRs that include UI changes, include a required `UI 변경` section in the PR description.
     - List URI paths where the changed UI can be checked as bullet items.
     - Use Demo Scenario team slugs in those paths when team-scoped routes are involved: `sales-demo`, `querypie-jp`, `querypie-kr`, and `querypie-us`.
     - Under each URI path, add nested bullets summarizing what changed on that screen in roughly 1–3 lines.
     - If 10 or more URI paths changed, list at most 10, prioritizing paths that show the major changes, and omit the rest.
   - Use the repository/user GitHub CLI policy; on this workstation that commonly means `env -u GITHUB_TOKEN gh ...`.
   - Check CI after PR creation/update. If checks are still running after a short active watch, report the in-progress checks rather than waiting silently for a long time.

10. Revert already-merged frontend PRs with a new PR.
   - Confirm the target PR is `MERGED` and read `mergeCommit.oid` with `gh pr view <pr> --json number,title,state,mergeCommit,mergedAt,url`.
   - Start from latest `origin/main` in a repo-local worktree and run `git revert -m 1 --no-edit <mergeCommitOid>`.
   - Verify the revert diff only cancels the target PR, run `git diff --check`, then push and create a Korean revert PR.
   - Do not include issue auto-close keywords in the PR body unless the user explicitly requests issue closure.
   - See `references/revert-merged-frontend-pr.md` for the command sequence and pitfalls.

## Pitfalls

- Do not implement from a PR body alone. PR # references may be stale or already merged; inspect the landed docs/code on latest `main`.
- Do not create separate `node_modules` in a worktree unless the root checkout dependencies are unavailable or incompatible.
- Do not hide browser-only APIs inside server components.
- Do not substitute full local builds for fast PR delivery when the user has asked to prefer commit/push and CI monitoring.
- Do not leave the user with only a local change; for repo work, push and PR reporting are part of completion unless explicitly excluded.
- When a PR body contains backticked paths or commands, write the body to a temporary file and use `gh pr create --body-file` or `gh pr edit --body-file`; do not pass a double-quoted multiline `--body` through the shell because command substitution can execute the backticked text.
- When rebasing a UI PR after a route-local i18n refactor has landed, do not resolve conflicts by resurrecting the old `page.tsx` body. Keep the latest thin route entry, move any PR-added visible sections/copy into each `page.en.tsx`, `page.ko.tsx`, and `page.ja.tsx` authoring module, and adjust source-structure tests to read the locale module rather than `page.tsx`.
- When rebasing a settings/profile UI PR after latest `main` extracted page sections into a wrapper component (for example `TeamSettingsManagementSections`), preserve the latest extracted wrapper and insert the PR-added card/section inside that wrapper. Do not flatten the page back to the older inline JSX just to keep the PR hunk.
- If a shared widget gains variants that do not need normal entity actions (for example state-only or required-creation cards), preserve the route-local copy boundary: normal entity cards should still require page-supplied labels, while actionless variants may render without those labels only when they truly have no drag/detail copy.

## Example: standard viewport dropdown

For a top-bar dropdown that resizes the current browser viewport from `docs/ui/display-size-guidelines.md`:

- Use a separate client component like `front/src/components/viewport-size-menu.tsx`.
- Include the standard options from the doc: Desktop review `1440 x 1000`, Desktop smoke `1280 x 720`, Tablet portrait `834 x 1194`, Tablet landscape `1194 x 834`, Mobile display `393 x 852`, Mobile browser `393 x 659`.
- Show the current `window.innerWidth × window.innerHeight`.
- When resizing, compensate for browser chrome using `window.outerWidth - window.innerWidth` and `window.outerHeight - window.innerHeight`, then call `window.resizeTo(option.width + chromeWidth, option.height + chromeHeight)` from the user-triggered click handler.
- Mention in PR notes that normal browser windows may restrict `window.resizeTo` depending on browser policy/window state.

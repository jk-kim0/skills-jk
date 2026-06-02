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
   - If a prior PR is referenced, verify whether it is merged and inspect the landed files on latest `main` rather than relying on the PR title/body alone.

3. Preserve top-bar ordering and future reserved slots.
   - When adding or moving a top-bar utility near Help, place it intentionally relative to the build version and Help.
   - For the outbound-agent top bar, the observed useful order is: build version, compact utility control, Help, notification indicator.
   - If the user says a utility should be “right next to Version” or that a version label will be placed to the left of the new button, implement `version → utility → Help` in `topbar-tools`, not inside the Team selector/context group.
   - For internal compact utilities such as Feature Visibility, the visible trigger may be a short code such as `FV`, but the `aria-label` should carry the full purpose and current selected state.
   - When a top-bar utility dropdown is moved, update structure/design tests that pin the source order so future edits do not drift it back into `topbar-context`.

4. Prefer a focused client component for browser-side controls.
   - Put browser-only interactions such as `window.resizeTo`, `window.innerWidth`, localStorage, or `useSyncExternalStore` into a separate `"use client"` component.
   - Keep `AppShell` as a thin server component that imports and places the client control.
   - Define standard option lists as exported constants when tests or future docs may need to verify them.

5. Use shared class tokens and structure tests.
   - Add or reuse tokens in `front/src/lib/ui/class-names.ts` instead of scattering one-off class strings through the component.
   - Update design-contract tests such as `front/src/components/app-shell-design.test.ts` when placement/order is part of the product expectation.
   - For simple UI contracts, string-based Vitest tests can verify labels, standard sizes, and shell placement without starting a dev server.
   - When moving an existing App Shell control between regions (for example Top Bar → Left Sidebar), assert both the new order and the absence/staleness of the old placement expectation in the design contract test.

6. Keep UI design docs in sync with shell placement changes.
   - For App Shell placement changes, update `docs/ui/screen-overview.md` and the relevant shared widget doc such as `docs/ui/common-widgets.md` in the same PR.
   - If the change affects Sidebar IA expectations, also update `docs/ui/sidebar-navigation-ia-plan.md` so docs no longer point users to the old menu location.
   - Replace old location language explicitly (for example “Top Bar Team selector”) rather than only adding new copy, otherwise design docs will contradict the implementation.

7. Verification should be narrow unless the user requests local full verification.
   - Link worktree `front/node_modules` to the root checkout when needed: `cd front && ln -s ../../../front/node_modules node_modules`.
   - Run `git diff --check`.
   - Run focused Vitest tests for changed components.
   - Run focused ESLint on changed files.
   - Do not start a dev server or run full build/test unless explicitly requested or necessary for confidence.

7. Commit, push, and create/update the PR.
   - Re-fetch and rebase onto latest `origin/main` before pushing.
   - Commit only relevant files.
   - Push the feature branch and create/update the PR with a Korean title/body for this repo.
   - Use the repository/user GitHub CLI policy; on this workstation that commonly means `env -u GITHUB_TOKEN gh ...`.
   - Check CI after PR creation/update. If checks are still running after a short active watch, report the in-progress checks rather than waiting silently for a long time.

8. Revert already-merged frontend PRs with a new PR.
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

## Example: standard viewport dropdown

For a top-bar dropdown that resizes the current browser viewport from `docs/ui/display-size-guidelines.md`:

- Use a separate client component like `front/src/components/viewport-size-menu.tsx`.
- Include the standard options from the doc: Desktop review `1440 x 1000`, Desktop smoke `1280 x 720`, Tablet portrait `834 x 1194`, Tablet landscape `1194 x 834`, Mobile display `393 x 852`, Mobile browser `393 x 659`.
- Show the current `window.innerWidth × window.innerHeight`.
- When resizing, compensate for browser chrome using `window.outerWidth - window.innerWidth` and `window.outerHeight - window.innerHeight`, then call `window.resizeTo(option.width + chromeWidth, option.height + chromeHeight)` from the user-triggered click handler.
- Mention in PR notes that normal browser windows may restrict `window.resizeTo` depending on browser policy/window state.

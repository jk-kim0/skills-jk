# Tailwind named-component PR rebase conflict pattern

Use when rebasing a `corp-web-app` PR that extracts Tailwind route/page bodies into named component files while latest `main` has added Component Name Debug markers or related shell tests.

## Conflict shape

Common conflicted files:

- `src/app/(tailwind)/[locale]/internal/tailwind/page.tsx`
- `src/components/layout/__tests__/component-name-debug.test.ts`
- adjacent route-local extracted component files such as `*-page.component.tsx`

The PR's intent is usually to keep `page.tsx` thin and move authored JSX into a named component file. Latest `main` may meanwhile add `componentNameDebugProps(...)` markers and tests that still read the old `page.tsx` body.

## Resolution rule

1. Rebase the PR onto the freshly fetched `origin/main` in a repo-root `.worktrees/<pr-purpose>` worktree.
2. Preserve latest-main behavior and markers; do not resurrect the pre-extraction page body in `page.tsx`.
3. Keep `page.tsx` thin: metadata, params/locale resolution, and a handoff to the extracted named component.
4. Move/keep the actual JSX, `componentNameDebugProps(...)` calls, helper functions, and route-card UI inside the extracted component file.
5. Update source-shape tests to read the extracted component file for markers that moved out of `page.tsx`, while retaining latest-main assertions for newly marked legacy/internal/shared components.
6. Remove stale expected marker names that only existed before extraction, unless the marker still exists in another source file by design.
7. Verify before continuing the rebase:
   - `git diff --check`
   - no conflict markers via `git grep -n '<<<<<<<\|=======$\|>>>>>>>'`
8. Continue with `GIT_EDITOR=true git rebase --continue`, then push with `--force-with-lease`.
9. Re-query `gh pr view <pr> --json headRefOid,baseRefOid,mergeStateStatus,statusCheckRollup` after push. Treat immediate `BLOCKED` with empty rollup as checks not yet populated; re-query briefly rather than assuming conflicts remain.

## Pitfalls

- Do not satisfy tests by moving debug markers back into `page.tsx`; that defeats the named-component extraction.
- Do not drop latest-main Component Name Debug test coverage while resolving the conflict. Merge both sides: new source-file constants from `main` plus the PR's extracted-component source constants.
- Avoid long passive `gh pr checks --watch` waits after a force-push. Prefer a bounded JSON re-query and report the current state if GitHub is slow.

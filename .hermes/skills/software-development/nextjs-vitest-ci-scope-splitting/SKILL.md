---
name: nextjs-vitest-ci-scope-splitting
description: Split Next.js/Vitest GitHub Actions CI by changed file scope, using paths-filter, grouped test runners, and an aggregate required check so PRs run only the validation needed for their diff.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [nextjs, vitest, github-actions, ci, paths-filter, test-splitting]
---

# Next.js/Vitest CI scope splitting

Use this skill when a Next.js repository has a monolithic GitHub Actions validation workflow and the user wants corp-web-japan-style CI narrowing: detect changed file scopes, run only relevant test groups, and keep a stable aggregate required check.

## Trigger conditions

- The repo uses Next.js, npm, Vitest, and GitHub Actions.
- The current CI runs broad `npm run build`, `npm run lint`, or `npm run test:run` for every PR.
- The user asks to split CI by code scope, reduce CI runtime, or copy a similar setup from another repo.
- A repo already has grouped tests and needs workflow/path filters maintained.
- A newly added or moved Vitest file makes `assert-test-groups.mjs`, `test:smoke`, `test:ci`, or the CI "Detect changed scope"/test grouping stage fail with an unassigned or overlapping test file.

## Core approach

1. Start safely from latest `origin/main` in a non-main worktree.
2. Inspect the current CI workflow, package scripts, test config, and test file layout.
3. If a sibling/reference repo has the target pattern, compare it directly but adapt names and scopes to the current repo.
4. Add a `changes` / `Detect changed scope` job with `dorny/paths-filter@v3`.
5. Add or update small CI helper scripts under `scripts/ci/`:
   - `test-groups.mjs`: declares group names and maps test files to exactly one group.
   - `run-vitest-group.mjs`: runs `npx vitest run <files...>` for one group or all groups.
   - `assert-test-groups.mjs`: fails if any test file is unassigned or belongs to multiple groups.
6. Add package scripts for each group and a smoke/grouping check.
7. Split GitHub Actions jobs by group with `if:` expressions based on `needs.changes.outputs.<scope>`.
8. Add a final always-running aggregate job that treats skipped scoped jobs as success and keeps branch protection stable.
9. Verify syntax and grouping locally with lightweight checks; avoid full local build/test if the user prefers CI validation.
10. Commit, push, open/update the PR, and verify fresh workflow runs attach to the pushed head SHA.

## Recommended workflow structure

- `changes`: detects PR file scopes; marks all scopes dirty for non-PR events or `workflow_dispatch`.
- `validate-lint` or `smoke`: runs lint plus `assert-test-groups.mjs` when any relevant scope changed.
- One job per test group: e.g. `test-publications`, `test-forms`, `test-routing`, `test-marketing-widgets`, `test-shell`, `test-utilities`.
- `build`: runs only when build-impacting paths changed and all needed scoped jobs succeeded or skipped.
- `ci-result` / `validate-test`: always runs and fails if any dependency failed or was cancelled.

Keep existing required check names where possible. If the repo already requires `Validate Lint`, `Validate Next Build`, and `Validate Test`, preserve those job names and put new scoped jobs underneath them rather than replacing the public check contract.

## Test grouping rules

- Every in-scope test file must map to exactly one group.
- The grouping assertion should fail on both unassigned and overlapping tests.
- Prefer path-based regexes that mirror source ownership, not fragile filename-only matching.
- Keep end-to-end tests out of Vitest grouping unless they are actually run by Vitest.
- If E2E files live under `tests/e2e/**`, mark them as CI/build-impacting or separate workflow-impacting files, but do not feed them to `vitest run`.
- When a test is about routing, middleware, locale redirect, or preview navigation, place it in a routing/SEO-style group rather than the content group it happens to mention.
- When `npm run test:run` passes but `npm run test:ci` fails, inspect the smoke stage first. In repos with `assert-test-groups.mjs`, the root cause may be classification metadata rather than a failing test assertion.
- If the failure is `Unassigned test files: <path>`, update only the appropriate matcher in `scripts/ci/test-groups.mjs`, then run `node scripts/ci/assert-test-groups.mjs` and the affected group script (for example `npm run test:routing`) before the full CI script.
- For route-local static/marketing page tests named like `*-route-local.test.tsx`, compare similar existing entries such as `solution-sac-route-local` and classify them in the routing group unless they are clearly publication/content-loader tests.

## Change filter rules

- Include CI/config files in a `ci` scope: workflow YAML, `scripts/ci/**`, `package.json`, lockfile, `vitest.config.*`.
- Include build-impacting config in the `build` scope: Next config, tsconfig, eslint/postcss/tailwind/vitest config, app/components/lib/utils/content/public paths.
- Map content/publication source paths to the publication group.
- Map forms/API/form utilities to forms.
- Map middleware, locale app routes, catch-all/dynamic routes, preview navigation, and route helpers to routing.
- Map site shell/layout/assets/public paths to shell/assets.
- Be conservative: if a shared path can affect several groups, either mark it `ci` or add it to a cross-cutting/build scope.

## Lightweight verification

Run these before commit:

```bash
node scripts/ci/assert-test-groups.mjs
node -e "JSON.parse(require('fs').readFileSync('package.json','utf8')); console.log('package.json ok')"
python3 - <<'PY'
import yaml
from pathlib import Path
yaml.safe_load(Path('.github/workflows/ci.yml').read_text())
print('workflow yaml ok')
PY
git diff --check
```

If the repository defines grouped npm scripts, also run the affected group script and then the aggregate script that CI uses:

```bash
npm run test:<affected-group>
npm run test:ci
```

If a fresh worktree has no `node_modules` but the root checkout has a compatible install and the user wants to avoid repeated installs, a temporary worktree-local symlink can be used for verification:

```bash
ln -s ../../node_modules node_modules
npm run test:ci
```

Do not commit the symlink. Confirm with `git status --short` before staging.

If `actionlint` is available, also run:

```bash
actionlint .github/workflows/ci.yml
```

Do not start dev servers for this task. Prefer pushing and letting CI validate the actual GitHub Actions behavior.

## Pitfalls

- Do not create local edits in the main checkout. Use a linked worktree under `.worktrees/`.
- Do not blindly copy a sibling repo's test groups; first list the current repo's tests and source directories.
- Do not treat `npm run test:run` success as proof that grouped CI is healthy. `test:ci` may still fail earlier in the smoke/grouping assertion stage when a new test file is unassigned.
- Do not fix an `Unassigned test files` failure by widening a regex too broadly. Add the narrowest path/name that reflects the file's ownership, and verify the file maps to exactly one group.
- After rebasing a CI-splitting PR over newer main, rerun `node scripts/ci/assert-test-groups.mjs` before pushing. Newly merged tests can appear outside the original grouping set and make `Validate Lint` fail even when ESLint is clean.
- Locale-prefixed verification routes are easy to miss: match both `src/__tests__/app/t/*-verification-route.test.tsx` and `src/__tests__/app/[locale]/t/*-verification-route.test.tsx`, and keep the corresponding paths-filter entries aligned.
- Route-local page and Next config route tests under `src/__tests__/app/*route*.test.tsx` or `src/__tests__/next-config-*-route.test.ts` usually belong in the routing group unless they exercise a narrower owned subsystem.
- Do not let the final required check skip completely on docs-only PRs if branch protection expects a result. Use an always-running aggregate job.
- Do not feed Playwright/E2E spec files to Vitest; keep them in a separate concern.
- Do not remove existing branch-protection check names without confirming repository settings.
- `paths-ignore` on pull requests can prevent required checks from appearing. Prefer a `changes` job plus an aggregate result over broad PR `paths-ignore` unless the repo already accepts missing checks for those paths.
- PyYAML parses GitHub Actions YAML but does not validate GitHub expression semantics; use it only as a syntax smoke check.

## Reference examples

- `references/corp-web-app-2026-05-ci-scope-splitting.md` summarizes one successful corp-web-app implementation adapted from corp-web-japan.

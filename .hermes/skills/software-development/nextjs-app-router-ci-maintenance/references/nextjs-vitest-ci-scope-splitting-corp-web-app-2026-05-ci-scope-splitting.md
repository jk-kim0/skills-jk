# corp-web-app CI scope splitting session (2026-05)

## Context

The user noted that `corp-web-japan` had already narrowed CI by changed code scope and asked to perform the same class of work in `corp-web-app`.

The current repo was `/Users/jk/workspace/corp-web-app`; root checkout was `main` and behind origin, so work was done in a fresh worktree:

```bash
git fetch origin --prune
git worktree add .worktrees/ci-scope-splitting -b ci/scope-splitting origin/main
```

## Reference pattern

`corp-web-japan/.github/workflows/ci.yml` used:

- `Detect changed scope` job with `dorny/paths-filter@v3`
- grouped test jobs such as publications/forms/routing/static pages/assets/cross-cutting
- a build job gated by changed scope and prior scoped job results
- a final always-running aggregate `CI result` job
- scripts under `scripts/ci/`:
  - `test-groups.mjs`
  - `run-node-tests.mjs`
  - `assert-test-groups.mjs`

## corp-web-app adaptation

The existing `corp-web-app` workflow had three broad jobs:

- `Validate Next Build` -> `npm run build`
- `Validate Lint` -> `npm run lint`
- `Validate Test` -> `npm run test:run`

The repo used Vitest, with tests under `src/**/__tests__/**` and `src/__tests__/**`; Playwright specs under `tests/e2e/**` were not part of Vitest.

Added groups:

- `publications`: `src/lib/repo-content/**` tests and `/t/*` publication verification route tests
- `forms`: contact-sales/form widget tests and contact-us route tests
- `routing`: middleware, preview navigation, locale/client routing tests
- `marketingWidgets`: pricing/plans/marketing widget tests
- `shell`: layout/provider/header tests
- `utilities`: remaining utility tests

The grouping assertion result at initial implementation time:

```json
{
  "total": 45,
  "perGroupCounts": {
    "publications": 15,
    "forms": 10,
    "routing": 3,
    "marketingWidgets": 11,
    "shell": 2,
    "utilities": 4
  }
}
```

Follow-up after rebasing over newer main: PR #675 failed `Validate Lint` even though ESLint passed, because `assert-test-groups.mjs` found 17 newly merged/unmatched tests. The missing patterns were:

- locale-prefixed publication verification routes: `src/__tests__/app/[locale]/t/*-verification-route.test.tsx`
- route-local page tests: `src/__tests__/app/*route*.test.tsx`
- Next config route tests: `src/__tests__/next-config-*-route.test.ts`

The fixed grouping assertion result was:

```json
{
  "total": 65,
  "perGroupCounts": {
    "publications": 24,
    "forms": 10,
    "routing": 9,
    "marketingWidgets": 11,
    "shell": 4,
    "utilities": 7
  }
}
```

When updating an open CI-splitting PR, always rerun the grouping assertion after rebase and keep `test-groups.mjs` and `.github/workflows/ci.yml` paths-filter patterns in sync.

## Important implementation choices

- Kept existing required check names for branch-protection compatibility:
  - `Validate Lint`
  - `Validate Next Build`
  - `Validate Test`
- `Validate Test` became an always-running aggregate result job.
- `Validate Lint` runs `npm run test:smoke`, which combines lint and `assert-test-groups.mjs`.
- `Validate Next Build` runs only when build-impacting paths changed and scoped dependencies succeeded or skipped.
- `tests/e2e/**` was added to the `ci` scope, not to a Vitest group, because those specs are Playwright tests.
- Non-PR events mark all scopes dirty via an `alltrue` step.

## Lightweight verification used

```bash
node scripts/ci/assert-test-groups.mjs
python3 - <<'PY'
import yaml, json
from pathlib import Path
yaml.safe_load(Path('.github/workflows/ci.yml').read_text())
json.loads(Path('package.json').read_text())
print('workflow yaml ok')
print('package json ok')
PY
git diff --check
```

Full local lint/build/test were intentionally not run because the user prefers avoiding long local verification and relying on CI for repo work.

## PR outcome

PR opened: `querypie/corp-web-app#675`

Remote head verification pattern:

```bash
BRANCH=$(git branch --show-current)
HEAD_SHA=$(git rev-parse HEAD)
REMOTE_SHA=$(git ls-remote origin refs/heads/$BRANCH | awk '{print $1}')
```

Then confirm `gh pr view` and recent `gh run list` both refer to the pushed SHA.

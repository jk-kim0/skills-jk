---
name: corp-web-japan-dependabot-batch-pr
description: Reusable notes for resolving many open Dependabot alerts in corp-web-japan with one PR by checking GitHub alert data, refreshing both lockfiles, and validating locally before opening a Draft PR.
version: 1.0.1
author: Hermes Agent
license: MIT
---

# Corp Web Japan Dependabot Batch PR

## Purpose

This skill captures the successful approach for fixing many open Dependabot alerts in `corp-web-japan` with one reviewable PR.

## Key findings

- The GitHub security page can show far more alerts than local `npm audit` because GitHub counts alerts across both the root application and `scripts/deploy`.
- Many alerts can collapse into a much smaller number of actual package updates.
- In the successful case, the important package families were `next`, `hono`, `@hono/node-server`, `minimatch`, `picomatch`, `path-to-regexp`, `brace-expansion`, `ajv`, `flatted`, `qs`, and `express-rate-limit`.
- A direct patch upgrade of `next` plus lockfile refreshes was sufficient; custom `overrides` were not needed.

## Recommended workflow

1. Check open PRs first.
2. Inspect the live Dependabot alert list from GitHub, not only local audit output.
3. Summarize alerts by manifest path and by package family.
4. Confirm whether both `package.json` and `scripts/deploy/package.json` participate in the alert set.
5. Use an isolated worktree if the main checkout contains unrelated tracked or untracked changes.
6. Refresh the root lockfile and the `scripts/deploy` lockfile.
7. If the root app still shows unresolved `next` advisories, allow the direct patch bump needed for the fixed release.
8. Reinstall cleanly and verify with local audit, PR-style checks, and production build.
9. Open a Draft PR explaining that the alerts should close after merge and dependency-graph reprocessing.

## Repo-specific findings

- `scripts/deploy` matters for the security page and should not be skipped.
- A worktree is safer than the main checkout because this repo may already contain unrelated local scratch files.
- The Next.js build can emit a multi-lockfile workspace-root warning when invoked from a worktree. If the build succeeds, that warning alone is not a reason to expand scope.

## Verification standard

A good batch-fix PR in this repo includes all of the following:
- root audit result at zero vulnerabilities
- `scripts/deploy` audit result at zero vulnerabilities
- `npm run test:ci` passing
- `npm run build` passing

## Communication guidance

- Before merge, the repository security page may still show the old alert count because the default branch is unchanged.
- The correct claim is that the PR contains the dependency updates expected to close the current alerts after merge, not that the alerts are already closed.

## Pitfalls

- Relying only on local `npm audit`
- Forgetting `scripts/deploy/package-lock.json`
- Adding unnecessary overrides before testing whether lockfile refreshes already solve the issue
- Treating the pre-merge security-page count as proof that the branch fix failed

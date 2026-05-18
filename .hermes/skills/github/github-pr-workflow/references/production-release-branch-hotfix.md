# Production release-branch hotfix PRs

Use this reference when a bug is visible on production but latest `main` or staging already appears fixed.

## Diagnostic pattern

1. Identify the deployment source of the affected environment before opening a PR.
   - Read repo deployment docs if available.
   - Inspect workflow files or Vercel/GitHub deployment notes when docs are unclear.
   - Do not assume production deploys directly from `main`.
2. Compare the affected code on the production deployment branch against `origin/main`.
   - Example: `git show origin/release:path/to/file` vs `git show origin/main:path/to/file`.
   - If production is based on `release` and `main` already contains the fix, create a hotfix PR with `--base release` that cherry-picks or manually ports only the required minimal change.
3. Keep the PR body explicit that the PR is a production-branch hotfix, not a new main-target feature PR.

## Browser verification pattern for visual CSS hotfixes

If local rendering for the production branch is blocked by environment-only data requirements (for example Blob tokens or remote content init), avoid broad setup work. Instead:

1. Reproduce the issue on the real production URL in a mobile/target viewport.
2. Measure DOM/computed state, not just screenshots.
   - For hidden footer/header/navigation bugs, record whether the DOM nodes exist and the computed `display`/visibility values.
3. Inject the proposed CSS rule into the live page via DevTools/evaluate-script to validate the same DOM would render correctly.
4. Record before/after evidence in the PR body:
   - affected URL and viewport
   - before computed style (for example `navDisplay: "none"`)
   - after computed style (for example `navDisplay: "block"`)
   - visible link/count or layout direction
   - overflow check such as `documentElement.scrollWidth === clientWidth`

This is not a substitute for source tests. Add a narrow regression test when the repo can cheaply assert the source contract, then use browser injection as render evidence for the production branch delta.

## Pitfalls

- Do not open a `main` PR for a production-only regression when `main` already contains the fix; it will not help production if deploys are based on `release`.
- Do not broaden the hotfix by merging all of `main` into `release` unless the user explicitly asks for a release promotion.
- Do not encode environment setup failures as durable rules. If local rendering fails because credentials are missing, capture the live-page verification workaround and continue with narrow source tests.

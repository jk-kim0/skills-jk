# Fresh worktree Node dependency resolution pitfall

Use this when a targeted Node/Vitest/Next.js check fails before collecting tests from a fresh git worktree.

## Symptom

A targeted check such as:

```bash
npm test -- --run src/__tests__/app/example.test.tsx
```

fails during CSS/PostCSS/Vite setup before any tests run, for example:

```text
Failed to load PostCSS config
Loading PostCSS Plugin failed: Cannot find module '@tailwindcss/postcss'
Require stack:
- <worktree>/postcss.config.mjs
```

## Interpretation

This is usually a fresh-worktree dependency resolution problem, not evidence that the source change broke the test assertions. Some repositories keep `node_modules` effectively tied to the root checkout or require a worktree-local install for CSS/PostCSS plugin resolution.

## Preferred handling when speed matters

1. Do not run `npm install`/`npm ci` in the worktree if the user's repo preference is to avoid slow local installs.
2. Record the attempted command and the exact dependency-resolution blocker.
3. Run the lightest non-install checks that still prove file hygiene, such as:

```bash
git diff --check
```

4. Commit/push the branch and verify that GitHub Actions runs attach to the pushed head SHA.
5. In the PR body/final report, mark the targeted local test as blocked by dependency resolution rather than failed by assertions.

## What not to do

- Do not silently install dependencies in a fresh worktree when the user has expressed a preference to avoid repeated local installs.
- Do not describe the blocked local test as a product-code failure.
- Do not wait passively for CI completion unless the user explicitly asked you to watch.

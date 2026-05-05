---
name: corp-web-japan-worktree-verification-without-node-modules
description: Verify corp-web-japan changes safely from a fresh worktree when the worktree does not have its own node_modules.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, worktree, verification, ci, nextjs, npm]
---

# Verify corp-web-japan from a fresh worktree without local node_modules

Use this skill when working in `corp-web-japan` from a fresh git worktree and the worktree does not contain its own `node_modules`.

## When this skill applies

- The user wants a fresh worktree from latest `origin/main`.
- The repo worktree should avoid its own `node_modules`.
- You still need meaningful verification before commit/PR.
- The change is in routing, publication loaders, metadata, or tests.

## Key finding

In this repo, simply pointing `PATH` at the parent repo's `node_modules/.bin` can be enough for some direct CLI entrypoints to start, but it is **not sufficient by itself** for reliable verification from a fresh worktree.

Observed failure modes:
- `npm run test:ci` may fail immediately with `eslint: command not found` if the worktree has no local install.
- Even with `PATH=~/workspace/corp-web-japan/node_modules/.bin:$PATH`, `npm run typecheck` can still fail with widespread module-resolution errors for `next`, `react`, `yaml`, Node built-ins, and JSX runtime types.
- `npm run build` can fail because Next/Turbopack cannot resolve `next/package.json` from the worktree and infers the wrong workspace root.

However, an important practical workaround worked in a later task:
- creating a worktree-local symlink `node_modules -> ~/workspace/corp-web-japan/node_modules`
- then rerunning narrow verification such as touched-file `npm run lint -- ...` and `npm run typecheck`

This is materially different from only exporting `.bin` on `PATH`: the symlink lets module resolution succeed from the worktree without paying the cost of a fresh install inside that worktree.

So the rule is:
- shared parent `.bin` alone is only a partial workaround
- a worktree-local `node_modules` symlink to the root checkout can be a good fast-path for narrow verification when the user wants to avoid repeated installs
- if even the symlink path is not acceptable or does not work, fall back to targeted source-based tests and rely on PR CI for full verification

## Recommended workflow

1. Create a fresh worktree from latest `origin/main`.
2. Implement the change there.
3. Prefer targeted verification that does not depend on a full worktree-local install.
4. Run narrow `node --test ...` commands for the affected test files when the tests are source-based or otherwise independent of a full Next build.
5. If the user does **not** want `node_modules` inside worktrees, do not add a local install just to satisfy full local `test:ci` or `build`.
6. Commit, push, and rely on PR CI as the authoritative full verification path.
7. In the PR body, explicitly note:
   - which targeted tests passed locally
   - that full `npm run test:ci` / `npm run build` could not be completed in the fresh worktree due dependency-resolution limits without worktree-local `node_modules`

## Good verification choices in this mode

Use these first:
- `node --test tests/<targeted-file>.test.mjs ...`
- targeted source-inspection tests already present in `tests/`
- `git diff --stat` and focused `git diff`

Avoid assuming these will work from the fresh worktree without local deps:
- `npm run test:ci`
- `npm run typecheck`
- `npm run build`

## If stronger local verification is explicitly required

Only if the user explicitly asks for stronger local verification, explain that one of these is needed:
- install dependencies in the worktree, or
- switch to a non-worktree environment where the repo has a proper local install

Do not silently add worktree-local `node_modules` in this repo, because the user prefers avoiding that overhead.

## PR note template

Use wording like:

- Targeted tests passed locally: `<exact commands>`
- Full local `npm run test:ci` / `npm run build` were not completed from the fresh worktree because the worktree did not have its own dependency install; PR CI should be treated as the authoritative full verification.

## Minimal summary

For `corp-web-japan` fresh worktrees without local `node_modules`, do targeted local verification only, avoid repeated installs by default, and use PR CI as the full-validation source of truth.
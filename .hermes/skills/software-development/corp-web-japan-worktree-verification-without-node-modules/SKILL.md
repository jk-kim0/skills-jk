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

However, later tasks exposed an important limitation and a better escalation path.

First workaround that can help for narrow checks:
- create a worktree-local symlink `node_modules -> ~/workspace/corp-web-japan/node_modules`
- rerun narrow verification such as targeted `node --test ...` or `npm run typecheck`

This is materially different from only exporting `.bin` on `PATH`: the symlink lets module resolution succeed from the worktree without paying the cost of a fresh install inside that worktree.

But an important experiential finding:
- that symlink can still break Next.js runtime/build flows under Turbopack
- observed errors included:
  - `Symlink [project]/node_modules is invalid, it points out of the filesystem root`
  - failure both on `next build` and on `next dev`
- so the symlink is a useful fast-path for narrow static verification, but it is **not reliable** when you need an actual local Next server or local build output for browser parity work

Best escalation path when browser verification is required and the user still wants to avoid a slow fresh install:
- remove the symlinked `node_modules`
- create a copy-on-write local clone from the root checkout instead, for example on APFS/macOS:
  - `cp -cR ~/workspace/corp-web-japan/node_modules ./node_modules`
- then start `next dev` or other local Next verification from the worktree

Why this matters:
- the copy-on-write clone behaves like a real in-worktree `node_modules` directory for Next/Turbopack
- but it avoids most of the time and disk cost of a full reinstall
- this is the practical fallback for visual/browser validation tasks where a local server is truly needed

So the rule is now:
- shared parent `.bin` alone is only a partial workaround
- a worktree-local `node_modules` symlink to the root checkout can be a good fast-path for narrow verification
- do **not** trust that symlink for `next dev` / Turbopack / local build flows
- when local browser verification is required, prefer a temporary copy-on-write local clone of `node_modules`
- if even that is undesirable, fall back to targeted source-based tests and rely on PR CI for full verification

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
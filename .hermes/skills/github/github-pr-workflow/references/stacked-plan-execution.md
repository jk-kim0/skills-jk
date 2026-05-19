# Stacked plan execution from a merged planning PR

Use this when a merged planning/documentation PR explicitly describes a multi-PR implementation sequence such as foundation first, first usage second.

## Workflow

1. Treat the merged planning PR as context, not as a branch to revive.
   - Fetch/prune and fast-forward local `main` to `origin/main` first.
   - Read the merged plan from latest `main`.
2. Create PR 1 from latest `origin/main` in a fresh worktree.
   - Keep PR 1 limited to foundation/infrastructure scope.
   - Do not include the first page/feature migration if the plan separates it.
3. After PR 1 is pushed/opened, create PR 2 from `origin/<pr-1-branch>` if PR 1 is still open.
   - Open PR 2 with `--base <pr-1-branch>`.
   - State `Base branch: <pr-1-branch>` and `Parent PR: #<number>` in the PR body.
4. If the plan is a living document, update it on the branch that represents the relevant state.
   - PR 1 branch: record the foundation PR status.
   - PR 2 branch: record the stacked child PR status and parent relationship.
5. Verify stacked scope against the parent branch, not only against `main`.
   - `git diff --stat origin/<parent-branch>...HEAD`
   - `gh pr view <child-pr> --json files,baseRefName,headRefOid`

## Dependency / node_modules hygiene

When a foundation PR adds new build tooling such as Tailwind/PostCSS:

- Prefer lockfile-only dependency updates for the foundation commit when the user wants to avoid worktree-local `node_modules`:
  - `npm install --package-lock-only --ignore-scripts -D <dev-deps>`
  - `npm install --package-lock-only --ignore-scripts <deps>`
- A child PR's targeted tests may fail before collection if the fresh worktree lacks the newly added tooling package required by config loading. In that case, installing dependencies in that worktree is a verification step, not a source change.
- After verification, remove worktree-local `node_modules` before final status/reporting if the repo/user preference is to avoid keeping it in worktrees.

## Reporting

Report both PR URLs, their parent/base relationship, local verification commands, and current check/deploy attachment status. Do not passively wait for CI unless asked.
# Tailwind menu-wave plan refresh

Use this when the user asks to refresh `docs/plans/2026-05-19-tailwind-route-ui-transition-plan.md` against the latest `main` and wants the plan organized by major menu groups rather than only by route families.

## Goal

Update the planning document from current `origin/main` so it reflects:

- latest merged Tailwind route-group migrations already on `main`
- current inventory counts from `npm run inventory:tailwind-pages -- --json`
- current open Tailwind PR queue
- next actions grouped by menu-level reviewer entrypoints such as Company, Solutions, Features, Resources, Plans, and long-tail utility/archive routes

## Recommended workflow

1. Fast-forward the root `main` to `origin/main`.
2. Create a fresh docs worktree from `origin/main`.
3. Run the Tailwind inventory and capture JSON from the first `[` onward rather than piping raw `npm` output directly into `jq`.
4. Summarize counts by menu group, not only by raw route family.
5. Check merged PRs relevant to the current plan baseline and list current open Tailwind PRs with `gh pr list` filtered by title/head branch.
6. Refresh the document sections in this order:
   - latest baseline SHA/date
   - recent merged PRs affecting Tailwind migration status
   - inventory counts
   - menu status board
   - per-menu execution waves / next actions
7. Verify with `git diff --check`, then commit/push/open PR.

## Useful commands

```bash
git fetch origin --prune
git checkout main
git merge --ff-only origin/main
git worktree add .worktrees/<name> -b <branch> origin/main

npm run inventory:tailwind-pages -- --json
env -u GITHUB_TOKEN gh pr list --state open --limit 30 \
  --json number,title,headRefName,baseRefName,url
```

## Menu grouping heuristic used in planning

Use the route itself as the grouping source of truth:

- Company: `/[locale]/company/*`, `/[locale]/t/company/*`
- Solutions: `/[locale]/t/solutions/*`
- Features: `/[locale]/t/demo/*`, `/[locale]/t/features/*`, `/[locale]/learn/documentation/*`
- Resources: remaining `/[locale]/t/*` publication/document families
- Plans: `/[locale]/plans*`
- Platform / Search / Cookie: `/[locale]/platform/*`, `/search`, `/cookie-preference`, `/[locale]/cookie-preference`
- Archived: `/[locale]/archived/*`

## Pitfalls

- `npm run inventory:tailwind-pages -- --json | jq ...` can fail because `npm run` prefixes banner text before the JSON payload. Strip everything before the first `[` or parse via Python/Node instead of assuming pure JSON on stdout.
- Re-check whether earlier “in progress” Tailwind PRs are now merged before copying old status text into the plan.
- The inventory style label (`tailwind`, `mixed`, `unknown`, `css-modules`) does not itself prove the route lives under `(tailwind)`; confirm the file path too.
- For planning docs, keep the PR documentation-only: do not start implementing route migrations just because open PRs exist.

## Verification

- `git diff --check`
- confirm the document baseline SHA matches current `origin/main`
- confirm any cited merged/open PR numbers still match live GitHub state

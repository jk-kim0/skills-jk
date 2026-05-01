---
name: corp-web-japan-static-page-slot-pr-comparison
description: Create comparison PRs for corp-web-japan static-page authoring experiments, especially when evaluating slot-style semantic section APIs versus content-object props.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, static-pages, refactor, stacked-pr, worktree, nextjs]
---

# corp-web-japan static-page slot-style comparison PRs

Use this when the user wants to compare a narrower authoring approach for one static-page section, such as:
- move marketing copy into the authoring layer
- replace giant content-object props with slot-style semantic components
- create a small comparison PR for one section only

## Core lessons

1. First identify the real authoring layer on the requested base branch.
- If the target branch is a broad route-localization PR, the authoring layer may be `src/app/page.tsx`.
- If the target is latest `origin/main`, the authoring layer may still be `src/components/sections/top-page-sections.tsx`.
- Do not force a `page.tsx`-centric solution onto `main` if `main` still authors the page in `TopPageSections`.

2. If the parent PR has grown beyond the desired comparison target, choose the correct baseline commit, not just the latest parent head.
- Example: parent PR later absorbed broader semantic-composition work, but the comparison PR should isolate only `TopPageSolutionOverviewSection`.
- In that case, branch from the earlier parent commit that still contains the prerequisite route-localization but not the later broader changes.

3. Prefer one-section-only experiments.
- Good first candidate: `TopPageSolutionOverviewSection`
- Keep other sections unchanged so the review compares one authoring model change at a time.

4. For slot-style authoring experiments, extracted components should be shells, not content registries.
- Good pattern:
  - `TopPageSolutionOverviewSection`
  - `TopPageSolutionOverviewIntro`
  - `TopPageSolutionOverviewLead`
  - `TopPageSolutionChoiceGroup`
  - `TopPageSolutionChoiceContent`
  - `TopPageSolutionChoiceHeading`
- Put the actual marketing copy directly in the authoring layer (`page.tsx` or `top-page-sections.tsx`, depending the chosen base).
- Avoid passing a giant `solutionBranch` object prop into the section shell when the purpose of the experiment is authoring readability.

## Decision guide

### A. User wants a comparison PR on top of an unmerged parent PR
Use a stacked PR.

Workflow:
1. inspect parent PR commits and current diff
2. decide whether to branch from parent head or an earlier parent commit
3. create fresh worktree from that exact commit
4. create child branch
5. change only the target section
6. open PR with parent branch as base

### B. User wants the comparison PR rewritten to be independent from the parent
Use latest `origin/main`.

Workflow:
1. inspect latest `origin/main`
2. identify the real top-page authoring layer on `main`
3. create fresh worktree from latest `origin/main`
4. reimplement only the target section refactor on top of `main`
5. force-push the existing comparison PR branch if the user wants to preserve the PR number
6. change the PR base to `main`

## Verification

Always run on the actual comparison branch/worktree:
```bash
npm run test:ci
npm run build
```

If structure-oriented tests fail after moving copy out of one file and into a new section shell:
- update the relevant test helper to read from the new authoring-layer file(s)
- do not loosen tests more than necessary; keep the original intent

## Common pitfalls

- assuming `page.tsx` is always the authoring layer
- branching comparison PRs from the latest parent head when the parent already contains broader follow-up refactors
- replacing one giant content-object prop with another giant section prop and calling it slot-style
- changing multiple sections in the same comparison PR
- forgetting to rebase or rewrite on latest `origin/main` when converting a stacked PR into an independent PR

## Success criteria

- the PR changes only the intended section experiment
- the authoring layer contains the marketing copy directly
- extracted components act as semantic shells or slots
- local `test:ci` and `build` pass
- if independent, PR base is `main`
- if stacked, PR base is the parent PR branch

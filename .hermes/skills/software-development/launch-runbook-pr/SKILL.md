---
name: launch-runbook-pr
description: Turn launch-readiness audit findings into a repository-tracked deploy/launch runbook and open a documentation PR, while capturing confirmed answers and leaving unresolved operational decisions as explicit questions.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [launch, readiness, docs, runbook, github, pr, operations]
    related_skills: [launch-readiness-issue-audit, github-pr-workflow, writing-plans]
---

# Launch Runbook Documentation PR

Use when:
- A launch/open-readiness audit found missing operational documentation
- The user wants to resolve audit items one by one and record them in the repo
- The task is to create a GitHub PR that documents deploy/launch decisions, not to change infra yet

## Goal
Create a small documentation-only PR that:
1. records repository-grounded deploy behavior already visible in workflows/scripts
2. records confirmed operational decisions from the user
3. leaves unresolved items as explicit open questions / TBDs
4. links the document from an obvious existing entry point such as `README.md`

## Recommended scope
Prefer a single file such as:
- `docs/deploy-and-launch-runbook.md`

Keep it documentation-only unless the user explicitly asks to implement runtime behavior (redirects, metadata, infra settings, GitHub environment rules, etc.).

## Workflow

### 1. Ground the document in repository evidence
Read before writing:
- `README.md`
- `.github/workflows/ci.yml`
- `.github/workflows/deploy-preview.yml`
- `.github/workflows/deploy-staging.yml`
- `.github/workflows/deploy-production.yml`
- deploy scripts such as `scripts/deploy/index.js`

Document only what the repo actually shows:
- triggers
- target environments
- known required secrets / vars
- deployment mechanism

Do not invent undocumented ownership or approval policy.

### 2. Use a docs-only branch/worktree
In repos that prefer worktrees, create a dedicated worktree/branch from latest `origin/main`.
Example naming:
- branch: `docs/launch-runbook`
- worktree: `.worktrees/docs-launch-runbook`

### 3. Write the runbook in two layers

#### Layer A: confirmed facts
Record the current known deployment flow and visible config from the repo.

#### Layer B: decision records + open questions
For each launch topic, structure as:
- Current status
- Open questions
- Decision record

Useful topic headings:
- Production URL / canonical domain
- Staging URL
- Rollback procedure
- Required secrets / vars ownership
- Production deploy approval

### 4. Good documentation pattern for partial answers
When the user answers only part of a topic:
- fill the confirmed values into `Decision record`
- narrow the remaining `Open questions`
- remove questions that are already answered

Example:
- If the user gives the representative production URL and redirect rule, set them directly.
- Keep only unresolved items like launch-day final approver or fallback path.

### 5. Record operational policy precisely
Capture phrasing that matters operationally, e.g.:
- “general-change rollbacks should be handled by creating an appropriate branch and performing a new deployment”
- “broader-impact production deploys require approval from either Keizo or Brant; one is sufficient”
- “major deploy/rollback issues should be shared in Slack channel #jp-marketing”

Be careful with channel names, approver lists, and representative URLs; these are easy to misstate and should be patched immediately if corrected.

### 6. Keep checklist items aligned with the documented policy
If rollback becomes branch-based redeploy, the checklist should mention:
- rollback operator / communication target known
- known-good state identified

If canonical domain is fixed, the checklist should name the confirmed canonical domain explicitly.

### 7. Make the doc discoverable
Patch `README.md` or the nearest existing docs index with a one-line pointer such as:
- `Deployment and launch decisions are tracked in docs/deploy-and-launch-runbook.md.`

### 8. Verify before opening the PR
For docs-only PRs in app repos, run the repo’s standard verification if practical.
If dependencies are missing, install them first, then rerun.
Typical flow:
- `npm ci`
- `npm run test:ci`

### 9. Open a PR with explicit non-scope
PR body should say:
- this is documentation-only
- it records current known deploy behavior and confirmed decisions
- it does not yet implement redirects / metadata / infra changes

## Pitfalls
- Don’t present undocumented ownership as fact before the user confirms it.
- Don’t silently keep outdated values after the user corrects them (e.g. `#jk-marketing` -> `#jp-marketing`, `www` -> non-`www`). Patch immediately.
- Don’t mix “minor change” approval policy with “broader-impact production deploy” approval policy.
- Don’t change runtime implementation when the task is only to document policy.

## Deliverable standard
A good result should leave the repo with:
- one clear runbook file
- one small README pointer
- a docs-only PR
- unresolved items narrowed to a short list of concrete questions

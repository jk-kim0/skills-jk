---
name: launch-readiness-issue-audit
description: Audit a web product repository for public launch/open readiness and create a GitHub tracking issue grounded in repository evidence.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [launch, readiness, audit, github, issue, deployment, operations]
    related_skills: [github-issues, github-repo-management, codebase-inspection]
---

# Launch Readiness Audit → GitHub Issue

Use when the user asks some variation of:
- "Can this website be opened publicly?"
- "What is needed before launch?"
- "Audit current readiness and create an issue"
- "Figure out blockers / conditions / checklist for going live"

Goal: produce a repository-grounded launch-readiness assessment, then create a GitHub tracking issue with evidence, blockers, checklist, and acceptance criteria.

## Principles

1. Do not answer from intuition alone. Ground every claim in files, workflows, branch state, and recent runs.
2. Distinguish between:
   - assets/config that exist
   - implementation gaps visible in the current codebase
   - actual operating procedure that is production-ready
   - missing or contradictory policy
3. Separate current status into Green / Yellow / Red (blockers).
4. Before creating a new issue, search for existing launch/open/readiness issues to avoid duplicates.
5. Prefer a tracking issue with actionable sections over a vague narrative.
6. Bias toward implementation-level blockers over documenting internal operational facts that are already known unless the user explicitly asks for runbooks/ownership/process documentation.
7. Before prioritizing remaining work, inspect open PRs so the issue reflects what is already in flight and does not treat merged or active work as still unowned.

## Audit flow

### 1. Confirm repo context, remote, and latest main state
Run in the repo root:

```bash
git status -sb
git remote -v | sed -n '1,2p'
git branch --show-current
git fetch origin main --quiet
git rev-parse main
git rev-parse origin/main
```

Important lesson: when writing or updating a tracking issue, do not analyze stale local branch state if the latest `origin/main` differs. Re-check claims against `origin/main`, especially after merges land while the audit is in progress.

echo "ORIGIN_MAIN=$(git rev-parse origin/main)"
```

Important lesson: do not analyze launch readiness from a stale local branch or assume local `main` is current. Ground the issue in latest `origin/main`, or explicitly say when you are analyzing something else.

### 2. Check for existing relevant issues
Search broadly with OR-style terms:

```bash
gh issue list --state open --limit 100 --search 'open OR launch OR release OR production OR prod OR public OR website OR deploy'
```

If a clearly duplicate tracking issue exists, update or comment there instead of creating a new one.

### 3. Check open PRs and recently merged PRs before stating remaining work
Inspect work already in flight:

```bash
gh pr list --state open --limit 20
gh pr list --state merged --limit 20
```

For any PR that appears related, inspect its changed files and status before treating that work as still missing. Important lesson: an issue becomes misleading if it keeps listing work that is already merged or actively under review.

### 4. Read the high-value repository sources first
Inspect these first if present:
- `README.md`
- `onboarding.md`
- `TODO.md`
- `.github/workflows/ci.yml`
- deploy workflows such as `.github/workflows/deploy-*.yml`
- promotion/release workflows such as `.github/workflows/promote-*.yml`
- production deploy docs like `deploy/single-host/README.md`
- infra docs like `docs/reference/infra/*.md`
- legal/policy content paths

Typical evidence targets:
- deploy paths exist?
- prod workflow exists?
- release branch policy exists?
- secrets/env contracts documented?
- monitoring/alerting documented?
- legal pages exist?
- TODOs reveal unfinished launch-critical work?

### 4. Inspect open PRs before finalizing the issue
Check what is already in flight so the issue does not repeat active work or describe recently fixed problems as still open.

```bash
gh pr list --state open --limit 20
```

For PRs that appear related, inspect their changed files and summaries:

```bash
gh pr view <NUMBER> --json title,body,files,headRefName,isDraft,statusCheckRollup
```

Important lesson: merged or in-flight PRs can invalidate earlier audit findings. Refresh the issue body after checking open PRs and after any relevant merge to `main`.

### 5. Inspect current operational signals
Check recent workflow health, not just static config.

```bash
gh run list --workflow=ci.yml --limit 5
gh run list --workflow=docker.yml --limit 5
gh run list --workflow=watchtower.yml --limit 5
```

Also inspect deploy workflows if present:

```bash
gh run list --workflow='deploy-dev.yml' --limit 5
gh run list --workflow='deploy-stage.yml' --limit 5
```

Important lesson: CI success alone is not enough. If Docker/release/prod-adjacent workflows fail repeatedly, call that out as a launch risk.

### 5b. Separate real source-health failures from local or generated-artifact failures
When the audit includes repo-health or technical-debt findings, do not stop at a failing top-level verification command. Determine whether the failure comes from the actual source tree or from local/generated residue.

Check for common false-signal sources first:

```bash
# nested worktrees / local residue
find . -maxdepth 2 -type d -name '.worktrees' -print
git status --short --ignored

# compare repo-level lint with source-scoped lint
npm run lint
npx eslint src tests

# inspect TS include patterns for generated artifacts
cat tsconfig.json
```

What to look for:
- ESLint scanning nested repo-local worktrees such as `./.worktrees/**`
- CI or local verification failing because a nested checkout contains merge-conflict markers or stale files
- `tsconfig.json` including generated directories such as `.next/dev/types/**/*.ts`
- stale Next-generated validators referencing routes that were already deleted or renamed

Important lesson: if `npm run build` and source-scoped lint/tests pass, but repo-level lint or typecheck fails due to `.worktrees/**` or stale `.next/dev` validators, classify that as verification-contract technical debt rather than a product-code defect. Call it out explicitly in the issue so maintainers do not chase the wrong root cause.

### 5. Check branch promotion reality
Do not assume `release` is current just because promotion workflows exist.

```bash
git fetch origin develop release --quiet
git rev-list --left-right --count origin/release...origin/develop
```

Interpretation:
- a large `release behind develop` count is a real launch blocker if release is the production source
- note exact counts in the issue

### 6. Check production-path completeness
Look for prod deploy workflow files explicitly:

```bash
find .github/workflows -name '*prod*'
```

Also inspect prod references in workflows/docs/config:
- release image tags in docker workflow
- prod overlays in gitops
- prod compose files

Important lesson: having prod manifests/config is not the same as having an official production deployment path.
If prod artifacts exist but no prod deployment workflow/runbook exists, classify as Yellow or Red depending on context.

### 7. Check SEO / public-indexing policy consistency
Search both implementation and internal guidance:
- `robots.txt`
- meta robots tags
- sitemap/canonical references
- agent/docs instructions that mention noindex/nofollow

Commands/tools:
- search for `robots`, `noindex`, `nofollow`, `sitemap`, `canonical`
- read actual `robots.txt`

Important lesson: contradictory signals matter. Example pattern:
- repo guidance says noindex/nofollow
- actual `robots.txt` says `Allow: /`
- no actual meta robots implementation found

This should be called out as a policy inconsistency, not guessed one way or the other.

### 8. Keep internal operational facts out of repository blocker lists unless the user explicitly wants them documented
Do not automatically turn already-known internal facts into required repo tasks such as:
- production domain decisions
- approver lists
- rollback owner
- runbook/ownership docs

unless the user explicitly wants repository documentation or process codification.

Important lesson: in some repos, the correct launch-readiness issue should focus only on implementation gaps visible in code, not on governance facts that are already settled outside the repository.

### 9. Check auth / OAuth launch readiness
Search for provider setup docs and status tables. Useful files often include:
- `docs/reference/infra/oauth-clients.md`
- auth setup docs

Specifically check:
- production redirect URIs present?
- verification/review status complete?
- Search Console/domain verification complete?
- provider sections still contain TODO?

Important lesson: if OAuth providers are documented for dev/stage but production rows are TODO, treat as launch blocker for public launch.

### 9. Check seed/default-account risk
Search for known default credentials and admin bootstrap traces:
- `admin`
- known sample passwords
- onboarding/readme references
- dev/ci seed docs and code

If default credentials are documented or seed patterns are mixed with operations docs, call out the need to separate dev/ci seed strategy from production bootstrap policy.

### 10. Check monitoring / accessibility / quality gates
Look for:
- Watchtower/health docs
- alerting TODOs
- Grafana/Prometheus setup
- axe/Lighthouse or equivalent

Important lesson: if monitoring exists only for dev, do not overstate readiness for stage/prod.

## Recommended issue structure

Use sections like:

1. Background
2. Current status
   - already in place
   - major blockers / uncertainties
3. Required checks before open
   - Release / deploy
   - Infra / domain / TLS
   - Auth / external integrations
   - Security
   - SEO / public indexing policy
   - Quality validation
   - Observability / operations
   - Legal / support
4. Green / Yellow / Red summary
5. Recommended sequence
6. Acceptance criteria
7. Evidence / references

## Labeling guidance

When creating the issue, prefer repo labels such as:
- `enhancement`
- `state/tracking`
- `priority/p1` or appropriate priority
- `severity/high` if launch blockers are substantial
- `size/xl` for cross-cutting readiness work

Always list labels first with `gh label list` if you do not already know the repo’s actual labels.

## Writing guidance

- Be explicit about what is confirmed vs inferred.
- Use exact file paths in the issue body.
- Quote concrete findings when helpful, e.g.:
  - `release behind develop by 1055 commits`
  - `frontend/app/public/robots.txt` currently allows indexing
  - recent `CI / Docker` runs failed repeatedly
- Frame missing items as launch blockers only when they materially affect real public operation.
- Do not inflate the issue with operational documentation tasks just because those facts are not written in the repository. If the user treats production URL, approvers, rollback owner, or similar facts as already-set internal knowledge, do not turn that into a required runbook/documentation task unless the user explicitly asks for repository docs.
- Prefer implementation-grounded tasks over governance wording. In repositories like marketing sites, focus the issue on missing routes, placeholder links, broken conversion paths, SEO artifacts, tests, analytics, and monitoring that can actually be implemented or verified in the codebase.

## Common pitfalls

1. Mistaking infrastructure scaffolding for operational readiness.
2. Looking only at CI and ignoring Docker/deploy workflows.
3. Ignoring branch promotion lag.
4. Failing to check for duplicate tracking issues first.
5. Declaring SEO policy without checking both docs and implementation.
6. Missing default credential references in docs and seed code.

## Minimal command checklist

```bash
# Duplicate issue search
gh issue list --state open --limit 100 --search 'open OR launch OR release OR production OR prod OR public OR website OR deploy'

# Current workflow signals
gh run list --workflow=ci.yml --limit 5
gh run list --workflow=docker.yml --limit 5
gh run list --workflow=watchtower.yml --limit 5

# Branch promotion reality
git fetch origin develop release --quiet
git rev-list --left-right --count origin/release...origin/develop
```

## Deliverable standard

A good output should let a maintainer answer:
- Are we launch-ready today?
- If not, what blocks us?
- What exists already vs what is missing?
- In what order should we close the gaps?
- What does "done" mean?

---
name: repository-maintenance-audits
description: Use when auditing or remediating repository maintenance state, including documented migration progress, GitHub Dependabot/npm security alerts, lockfile health, and PR-ready evidence packages.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [repository-maintenance, audit, migration, dependabot, npm, security, lockfile]
    related_skills: [github-pr-workflow, github-auth, codebase-inspection, systematic-debugging]
---

# Repository Maintenance Audits

## Overview

Use this umbrella when the user asks for a repository-level maintenance audit or remediation pass where documentation, GitHub state, lockfiles, and actual source state must be cross-checked before reporting or opening a PR.

It consolidates two recurring maintenance classes:

- **Migration / project status audits** — compare a documented multi-phase migration plan or roadmap against actual repository state and report completed, in-progress, and remaining work.
- **Dependabot / npm security batch PRs** — inspect GitHub security alerts directly, update affected npm manifests/lockfiles, validate audits/dependency trees, and prepare one reviewable PR.

The common library value is the method: do not trust one source of truth. Cross-check the plan/security page against the live repo, GitHub API, local lockfiles, PR branches, and CI evidence.

## When to Use

- User asks to review a migration plan and report current status, gaps, blockers, or what's left.
- User points to a `docs/**` plan, roadmap, or phase document and asks for a comprehensive status report.
- User asks to resolve Dependabot alerts, npm audit failures, or lockfile security issues in a batch PR.
- GitHub security page and local `npm audit` disagree and the task needs source-of-truth reconciliation.
- A repository maintenance task needs evidence tables and a PR-ready remediation summary.

Do not use this for generic feature development unless the main deliverable is audit/remediation evidence.

## Shared Audit Principles

1. Verify repository identity, default branch, current branch, and latest baseline before acting.
2. Read the user's referenced document or GitHub source, but never rely on it alone.
3. Enumerate the concrete units of work: phases, endpoints, routes, collections, manifests, packages, alerts, or PRs.
4. Cross-check each unit against live repository state and GitHub API state.
5. Report in evidence-backed tables before synthesis.
6. For remediation PRs, keep changes reviewable and avoid unrelated cleanup.

## Pre-flight Commands

```sh
pwd
git rev-parse --show-toplevel
git status --short --branch
git remote -v
git fetch origin --prune
gh auth status || true
gh repo view --json nameWithOwner,defaultBranchRef,url || true
```

For edits, create a fresh non-main worktree/branch from the default branch and verify the merge base before committing.

## Migration / Multi-Phase Project Status Audit

Extract from the plan document:

- Phase definitions and scope boundaries.
- Collection, endpoint, package, route, or feature enumeration.
- Completion criteria per phase.
- Target architecture/directory conventions.
- Dependencies and blockers.

Cross-check repository state for each enumerated unit. For content/MDX migrations, verify counts, unique IDs, locale coverage, verification routes, public routes, and whether catch-all/dynamic/blob-backed rendering is still active. For PR-backed phases, list open PRs, draft status, update time, and branch tip state.

Use a comparison table with columns:

| Phase / Unit | Plan Status | Actual Verified Status | Gap | Evidence / Blocking PR |
| --- | --- | --- | --- | --- |

Report in this order:

1. **Completed** — fully satisfies plan criteria.
2. **In progress** — open PRs, partial implementations, verification routes.
3. **Remaining** — no implementation or known missing units.
4. **Blockers / decisions** — external content, policy, release decisions, stale plan assumptions.

Pitfall: A plan's "current main" section may be stale. Verify file and route existence independently.

## Dependabot / npm Security Batch PR

Inspect GitHub Dependabot alerts directly; do not rely only on local `npm audit`.

```sh
gh api -H 'Accept: application/vnd.github+json' \
  /repos/OWNER/REPO/dependabot/alerts --paginate \
  --jq '.[] | select(.state=="open") | {number,package:.dependency.package.name,ecosystem:.dependency.package.ecosystem,manifest:.dependency.manifest_path,severity:.security_advisory.severity,summary:.security_advisory.summary,vulnerable:.security_vulnerability.vulnerable_version_range,patched:.security_vulnerability.first_patched_version.identifier}'
```

Group by manifest, package, highest patched version, and whether the dependency is direct or transitive. Include every affected npm manifest/lockfile, including nested deployment/analysis scripts.

Preferred remediation order:

1. Bump direct dependencies within compatible semver ranges.
2. Regenerate lockfiles with `npm install --package-lock-only --ignore-scripts`.
3. Run `npm audit --json` for every manifest.
4. If alerts remain, try lockfile-only audit fixes.
5. Add narrowly scoped overrides only when necessary and justified.
6. Validate overridden or suspicious dependency trees with `npm ls ... --package-lock-only`.
7. Commit only valid lockfiles and package manifests.

Good override pattern: scope a vulnerable transitive dependency to the parent that needs it when broad overrides would force invalid majors. Bad pattern: a broad override that makes `npm audit` pass but `npm ls` reports `invalid`.

## Verification Recipes

Migration audits:

```sh
find src/content/<collection> -name '*.mdx' 2>/dev/null | wc -l
find src/app -path '*/t/<collection>*' -name page.tsx 2>/dev/null | sort
gh pr list --state open --limit 50 --json number,title,isDraft,updatedAt,headRefName
```

Dependabot/npm:

```sh
npm install --package-lock-only --ignore-scripts
npm audit --json >/tmp/root-audit.json
npm ls <package> <parent-package> --package-lock-only
node - <<'NODE'
const fs = require('fs')
for (const f of ['/tmp/root-audit.json']) {
  if (!fs.existsSync(f)) continue
  const data = JSON.parse(fs.readFileSync(f, 'utf8'))
  console.log(f, data.metadata?.vulnerabilities)
}
NODE
```

In Hermes CLI sessions, a single very long `npm ls <many packages> --package-lock-only` command may be falsely rejected as long-running. Split `npm ls` by dependency family or inspect the lockfile with a small Node script.

## Reporting Pattern

For audits, provide:

- Scope and sources checked.
- Evidence tables for each unit/alert/manifest.
- Completed / in-progress / remaining / blocked synthesis.
- Commands or artifacts used for verification.
- For PRs, exact branch/commit/PR/check state and expected post-merge effects.

For Dependabot PRs, note that GitHub security counts often update only after merge/default-branch reprocessing; pre-merge counts may still reflect `main`.

## References

Session-specific examples migrated from the absorbed skills live under `references/` with `migration-status-audit-*` and `npm-dependabot-security-batch-pr-*` prefixes.

## Common Pitfalls

- Trusting a plan document's status without verifying the repository.
- Counting files without checking route/public exposure or locale coverage.
- Treating an open PR as current without checking branch tip and update time.
- Ignoring secondary npm manifests such as `scripts/deploy/package-lock.json`.
- Believing local `npm audit` has the same view as GitHub Dependabot alerts.
- Adding broad overrides that make audit output green while `npm ls` is invalid.
- Reporting security-page alert closure as immediate before merge/default-branch reprocessing.
- Running broad install scripts unnecessarily; prefer `--package-lock-only --ignore-scripts` for lockfile remediation.

## Verification Checklist

- [ ] Repository/default branch/baseline verified.
- [ ] Every plan unit or GitHub alert was enumerated from the source of truth.
- [ ] Repository state was cross-checked independently.
- [ ] Tables distinguish documented status from verified status.
- [ ] npm remediations include audit and dependency-tree validation for every affected manifest.
- [ ] PR/report explains expected residual GitHub alert behavior after merge.

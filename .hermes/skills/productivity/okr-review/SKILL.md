---
name: okr-review
description: Use when running an OKR review meeting for one Objective or Key Result from a roadmap/OKR document, auditing latest main implementation status, quality gaps, blockers, decisions needed, and recording meeting material plus follow-up notes in GitHub issues.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [okr, roadmap, product-review, github-issues, meeting-notes]
    related_skills: [github-issues, codebase-inspection, migration-status-audit]
---

# OKR Review Meeting

## Overview

Use this skill to run a structured OKR review meeting for one Objective or Key Result from a roadmap, OKR, or product planning document.

The workflow is collaborative: the agent prepares evidence from the latest main branch, opens or updates a GitHub issue as meeting material, then discusses findings with the Product Owner, developer, or decision maker. After the discussion, the agent records the meeting note and follow-up Action Plan as a GitHub issue comment.

This is a review and decision-support workflow, not an implementation workflow. Do not start code changes unless the user explicitly asks for implementation after the review.

Default outputs:

1. Pre-meeting GitHub issue containing the OKR review material
2. Post-meeting GitHub issue comment containing decisions, deferred items, blockers, and Action Plan

## When to Use

Use this skill when the user asks for any of the following:

- “OKR review”, “OKR 점검”, “roadmap objective review”, “Key Result status check”
- Audit one roadmap Objective or Key Result against current repository implementation
- Determine whether a roadmap/OKR item is implemented, partially implemented, missing, or below quality bar
- Identify blockers, external setup needs, or product decisions required before implementation can continue
- Prepare a Product Owner / developer meeting issue and then record meeting notes in GitHub

Do not use this skill when:

- The user asks for direct implementation rather than review
- The request is a single bug fix or narrow code review with no roadmap/OKR meeting context
- The main task is only to update specs/ADRs/decision logs; use the repository’s specification or documentation maintenance skill if one exists

## Required Inputs

Collect or infer these inputs:

- The roadmap/OKR source document
  - Examples: `docs/sprint-roadmap.md`, `docs/roadmap.md`, `docs/okrs.md`, a product plan, or a GitHub issue
- The target Objective or Key Result
  - Examples: `Objective 5`, `KR 2`, `Gmail-based actual sending`, `Reduce onboarding time`
- Whether to create a new GitHub issue or update an existing one
- The expected meeting audience
  - Product Owner, developer, tech lead, designer, or stakeholder
- Whether local tests/builds should be run or only static evidence + CI status should be used

If not specified, use these defaults:

- Baseline: latest `origin/main`
- Output: create a new GitHub issue
- Language: match the repository/user language; otherwise use the language of the roadmap document
- Local verification: avoid long local test/build runs unless explicitly requested; prefer static repo evidence and current CI status
- Side effects: do not start servers, send emails, call external providers, or run production actions without explicit approval

## Phase 0. Preflight

1. Confirm repository and working tree state.

```bash
git status --short --branch
pwd
git remote -v
git fetch origin --prune
```

2. Use latest `origin/main` as the review baseline unless the user specifies another base.

- Do not trust a stale local branch or in-progress feature branch for implementation status.
- If the current checkout is dirty, do not overwrite it.
- Create a separate worktree from `origin/main` when needed.

```bash
git worktree add .worktrees/okr-review-<slug> -b docs/okr-review-<slug> origin/main
```

3. Load relevant repository guidance.

- Read `AGENTS.md`, `CLAUDE.md`, or equivalent repo guidance if present.
- Load any repo-local skill that governs the repository or feature area.
- If GitHub issues are involved, use the GitHub issue workflow and the repository’s required `gh` invocation policy.

4. Find existing related work.

```bash
gh issue list --state open --search "<objective or key result terms>" --limit 20
gh pr list --state open --search "<objective or key result terms>" --limit 20
```

If the environment requires it, run GitHub CLI as `env -u GITHUB_TOKEN gh ...`.

Do not create a duplicate issue if an existing tracking/review issue clearly owns the same OKR review. Update or comment on the existing issue instead, unless the user asks for a new issue.

## Phase 1. Prepare the Meeting Material Issue

### 1. Anchor the OKR item

Quote or precisely summarize the target Objective/Key Result from the roadmap/OKR source.

Keep the review boundary narrow:

- If the target is an Objective, review its Key Results and directly related enabling work.
- If the target is a Key Result, focus on that KR and mention sibling KRs only as context.
- Do not broaden into adjacent roadmap items unless they are true blockers or dependencies.

### 2. Audit latest main implementation status

Gather evidence from current main branch.

Recommended static checks:

```bash
git grep -n "<domain term>" -- .
git ls-tree -r --name-only origin/main -- <relevant-root>
git log --oneline --decorate --max-count=30 -- <related-path>
```

Recommended GitHub checks:

```bash
gh pr list --state open --search "<terms>" --json number,title,url,headRefName,mergeStateStatus

gh issue list --state open --search "<terms>" --json number,title,url,labels
```

Verification rules:

- Separate static code/doc evidence from test/build/smoke evidence.
- Long local verification is optional unless requested.
- Existing CI can be cited, but do not overstate CI as product smoke evidence.
- External side effects require explicit approval.

### 3. Classify each review scope

Use these status labels consistently.

| Status | Meaning |
| --- | --- |
| Implemented | Current main has a usable product/runtime path plus enough test, CI, or smoke evidence for the claimed result |
| Partially implemented | Some model/service/API/UI/test pieces exist, but required end-to-end flow or integration is not closed |
| Not implemented | No meaningful implementation path exists on current main |
| Below quality bar | Implementation exists but core UX, correctness, safety, observability, tests, docs, or operational readiness are insufficient |
| Blocked | Work cannot proceed safely without external setup, credentials, infra, product policy, dependency resolution, or another team’s action |
| Decision needed | Product/technical/operational policy must be decided before implementation scope can be fixed |

Important: a schema field, service helper, adapter unit test, mocked path, or checked task box is not enough to mark an OKR/KR as Implemented if users cannot complete the actual outcome.

### 4. Draft the meeting material issue

Use this issue structure by default. Adapt headings to the repo language, but preserve the information architecture.

```md
## Background

<Why this OKR/KR is being reviewed now.>

## Reviewed Roadmap / OKR Item

- Source: `<roadmap-or-okr-path-or-url>`
- Objective: <quoted or precise summary>
- Key Result: <quoted or precise summary, if applicable>
- Baseline: `origin/main` <sha>
- Review scope: <what is included/excluded>

## Current Implementation Summary

Implemented:

- <evidence-backed item>

Current gaps:

- <missing, partial, or below-quality item>

## Detailed Status

| Scope | Current state | Evidence | Status |
| --- | --- | --- | --- |
| <scope> | <facts> | <paths/tests/docs/PRs> | Implemented / Partial / Missing / Quality gap |

## Blockers

### Required blockers

| Category | Blocker | Current state | Required action |
| --- | --- | --- | --- |
| <category> | <blocker> | <evidence> | <next step> |

### Recommended hardening / quality items

| Category | Item | Why it matters |
| --- | --- | --- |
| <category> | <item> | <reason> |

## Decisions Needed

### Required decisions

1. <decision question>
   - Option A: <...>
   - Option B: <...>
   - Current evidence: <paths/facts>

### Recommended decisions

1. <decision question>

## External Setup / Configuration Needed

### Required

- <credentials/provider/admin setting/config/dependency>

### Recommended

- <hardening/operational setting>

## Proposed Implementation / Follow-up Scope

### Phase 1: <name>

- <action>

### Phase 2: <name>

- <action>

## Done Criteria

Required done criteria:

- <observable acceptance criterion>

Recommended done criteria:

- <quality or hardening criterion>

## Verification Notes

Commands or evidence checked:

```bash
<commands>
```

Not run and why:

- <verification not run because...>

## Related Files / References

- `<path>`
- <issue/PR/doc URL>
```

Good issue title patterns:

```text
<OKR/KR name> implementation status and blocker review
<OKR/KR name> 구현 상태와 blocker 점검
<Feature outcome> completion blocker review
```

### 5. Create or update the GitHub issue

Use a body file to avoid shell quoting problems.

```bash
gh issue create \
  --title "<title>" \
  --body-file /tmp/okr-review-<slug>.md
```

If a relevant issue already exists:

```bash
gh issue edit <issue-number> --body-file /tmp/okr-review-<slug>.md
```

After creation/update, verify and share the issue URL.

```bash
gh issue view <issue-number> --json number,title,url,body
```

## Phase 2. Run the Meeting with the User

Treat the conversation as a Product Owner / developer review meeting.

Agent responsibilities:

- Walk through the meeting material in small chunks.
- Explain blockers and decision items briefly, with evidence.
- Ask for decisions only where the answer changes implementation scope.
- Record user decisions, deferrals, rejections, and newly discovered constraints.
- Separate facts from assumptions.
- Translate decisions into a small Action Plan.

Meeting classifications:

| Classification | Meaning |
| --- | --- |
| Decided | The user made a product/technical/operational decision |
| Deferred | The user explicitly left the item for later review |
| Needs more evidence | More repo, user, market, provider, or operational evidence is needed |
| Rejected / non-goal | The user ruled the item out of scope |
| Actionable now | A follow-up PR, issue, spec, design doc, or test can be created immediately |

Rules:

- If the user says an item is for later review, do not write it as a decided requirement.
- If the user provides a final policy decision, record it clearly.
- If the repo has a canonical decision-log system, create or plan a separate docs/spec PR for durable decisions.
- Do not close the issue unless the user explicitly asks.

## Phase 3. Record Meeting Notes as an Issue Comment

After the discussion, add a comment to the same GitHub issue.

Default comment format:

```md
## OKR Review Meeting Notes

Date/time: YYYY-MM-DD <timezone>
Participants/roles: Product Owner / Developer, AI Agent
Target: <Objective/KR>
Baseline: `origin/main` <sha>

## Decisions

- <decision>

## Deferred Items

- <item> — <reason for deferral>

## Newly Confirmed Blockers

- <blocker>

## Quality Gaps / Revalidation Needed

- <item>

## Action Plan

### P0

- [ ] <action> — owner: <owner or TBD>, output: <PR/issue/doc/test>

### P1

- [ ] <action>

## Spec / Docs Follow-up

- <needed or none>

## Candidate Implementation PRs / Issues

- <candidate scope>

## Evidence

- <commands, paths, CI links, issue/PR references>

## Notes

- This comment records the review and does not close the issue.
```

Post the comment with a body file.

```bash
gh issue comment <issue-number> --body-file /tmp/okr-review-note-<slug>.md
```

Then verify the latest comment.

```bash
gh issue view <issue-number> --json comments --jq '.comments[-1]'
```

## Evidence and Quality Rules

- Always ground implementation status in current main branch files, tests, docs, issue/PR state, or CI/smoke evidence.
- Do not mark a result as Implemented if only internal pieces exist but no usable end-to-end path exists.
- Do not let an OKR task checkbox override live repository evidence.
- A mocked adapter/unit test does not prove real provider readiness.
- A passing build does not prove product quality unless the OKR is only about buildability.
- Call out missing UX, missing guardrails, missing docs, missing operational controls, and missing test evidence as quality gaps when they affect the OKR outcome.
- Include verification not run and the reason.
- Prefer explicit assumptions over hidden guesses.

## GitHub Issue Hygiene

- Match the issue language to the repo/user preference.
- Prefer neutral issue/PR references unless the user explicitly wants auto-closing behavior.
- Do not use `Closes`, `Fixes`, or `Resolves` unless the user explicitly says the PR or issue should close another issue.
- Do not leave meeting material only in a local Markdown file.
- Do not leave decisions only in chat history; record them as issue comments or canonical docs.
- If GitHub CLI must be wrapped as `env -u GITHUB_TOKEN gh ...`, apply that wrapper to every issue/PR/run command.

## Common Pitfalls

1. Reviewing from a stale local branch instead of latest `origin/main`.
2. Rewriting the roadmap item from memory instead of quoting the source document.
3. Treating internal implementation fragments as user-visible OKR completion.
4. Hiding quality gaps under “recommended improvements” when they block the Key Result.
5. Writing deferred items as if they were decided requirements.
6. Creating a duplicate issue when a living review/tracking issue already owns the same scope.
7. Creating only a draft file and forgetting to publish the real GitHub issue.
8. Ending the meeting without posting the issue comment with decisions and Action Plan.
9. Closing the issue or adding auto-closing PR keywords without explicit user approval.

## Verification Checklist

- [ ] Latest baseline branch/SHA recorded.
- [ ] Roadmap/OKR source and target Objective/KR recorded.
- [ ] Review scope and non-scope stated.
- [ ] Current implementation status classified with evidence.
- [ ] Required blockers separated from recommended hardening items.
- [ ] Required decisions separated from recommended decisions.
- [ ] External setup/configuration needs listed when relevant.
- [ ] Done criteria are observable.
- [ ] Commands/evidence checked are recorded.
- [ ] Verification not run is recorded with reasons.
- [ ] GitHub issue created or updated and URL shared.
- [ ] Meeting notes and Action Plan posted as an issue comment.
- [ ] No issue close or auto-close keyword was used without explicit instruction.

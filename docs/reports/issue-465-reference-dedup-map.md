# Issue 465 reference deduplication map

## Scope

Issue 465 asked for a reference-document map, topic keywords, duplicate-candidate discovery, pairwise comparison, and duplicate removal.

This report is the human-readable map.
The full row-level inventory is tracked in `docs/reports/issue-465-reference-map.tsv`.

## Inventory map

| Area | Reference rows after dedup |
| --- | ---: |
| `active-hermes` | 468 |
| `inactive-pack` | 152 |
| `repo-skills` | 7 |
| Total | 627 |

The TSV uses these columns:

| Column | Meaning |
| --- | --- |
| `path` | Reference document path. |
| `area` | `active-hermes`, `inactive-pack`, or `repo-skills`. |
| `owner` | Nearest owning `SKILL.md`. |
| `lines` | Current line count. |
| `title` | First H1, or basename fallback. |
| `topic_keywords` | Topic categories applied from path and content signals. |

Primary topic keywords used in this pass:

- `skills-jk-gha`
- `git-worktree-cleanup`
- `github-pr-ci`
- `pr-body-safety`
- `outbound-gmail-oauth`
- `tencent-devops`
- `mlops-structured-generation`
- `mlops-training-inference`
- `creative-baoyu`
- `creative-rendering`
- `browser-render-parity`
- `corp-web-app`
- `corp-web-japan`
- `corp-web-v2`
- `querypie-docs`
- `memory-context`
- `troubleshooting`
- `examples`
- `advanced-usage`
- `source-dump`
- `domain-specific`

## Duplicate-candidate map

| Candidate cluster | Topic keywords | Compared documents | Decision |
| --- | --- | --- | --- |
| `skills-jk-gha-pr-creation` cleanup incidents | `skills-jk-gha`, `git-worktree-cleanup`, `github-pr-ci`, `memory-context` | 27 repo-specific incident references under `.hermes/skills/software-development/skills-jk-gha-pr-creation/references/` plus canonical `git-worktree-safety-pack` references. | Rewrote `dirty-root-preserve-pr-cleanup-loop.md` as the single repo-specific quirk map, retained 4 distinct support references, deleted 22 duplicate incident notes. |
| `git-worktree-safety-pack` active entrypoint | `git-worktree-cleanup`, `github-pr-ci` | `SKILL.md` common-pitfall list and related cleanup references. | Removed duplicate numbering and folded the repeated root-dirty follow-up rule into the ordered pitfall list. |
| `github-pr-workflow` PR-body notes | `github-pr-ci`, `pr-body-safety` | `pr-body-shell-quoting-safety.md`, `shell-safe-pr-body.md`, and the active `SKILL.md` PR-body section. | Kept `pr-body-shell-quoting-safety.md` as canonical, folded the extra trigger/verification wording into it, deleted `shell-safe-pr-body.md`, and shortened the active skill to a pointer. |
| `github-pr-workflow` production workflow reference | `github-pr-ci` | Duplicate `workflow-dispatch-production-branch.md` bullet in active `SKILL.md`. | Removed the repeated bullet. |
| `unsloth` generated source references | `mlops-training-inference`, `source-dump` | `llms-txt.md`, `llms-full.md`, and `llms.md` under `.hermes/skills/mlops/training/unsloth/references/`. | Kept `llms-txt.md` as the canonical generated source reference because it is the only file listed by the skill and index; deleted unreferenced duplicate/source-overlap files `llms-full.md` and `llms.md`. |
| `guidance` and `outlines` structured-generation references | `mlops-structured-generation` | `guidance/references/backends.md`, `outlines/references/backends.md`, `guidance/references/examples.md`, `outlines/references/examples.md`. | Compared as same basename and same category, but retained separately because API/backend examples are library-specific. The map records the candidate for future shared-reference extraction if a shared owner is introduced. |
| `baoyu-comic` and `baoyu-infographic` framework references | `creative-baoyu` | `analysis-framework.md` and `base-prompt.md` in both skills. | Compared as same basename and adjacent creative workflow, but retained separately because comic and infographic output contracts differ. The map records the boundary instead of forcing an abstraction. |
| outbound-agent Gmail/Tencent runbooks | `outbound-gmail-oauth`, `tencent-devops` | Gmail OAuth, Tencent deploy, secret sync, and Slack notification references under `outbound-agent-dev-environment-operations`. | Compared the negative secret-test pair and kept `tencent-gmail-oauth-negative-test-and-restore.md` as canonical, with a negative-test-only variant folded in. Other Gmail/Tencent references were retained because they cover distinct layers: product OAuth diagnostics, VM-local env sync, target-aware deploy, Slack notification secret triage, or deployment status. |
| remaining same-owner high-similarity pairs | `git-worktree-cleanup`, `creative-rendering` | `repo-local-workspace-cleanup-sweep.md` with `unregistered-worktrees-during-cleanup.md`; `touchdesigner-mcp` `audio-reactive.md` with `pitfalls.md`. | Retained after direct comparison: the worktree pair is summary-plus-specialized-detail, and the TouchDesigner pair is audio-bus implementation guidance plus cross-version pitfall guidance. |

Verification scans after the dedup pass found 0 exact duplicate document bodies. Remaining basename collisions such as `troubleshooting.md`, `advanced-usage.md`, `examples.md`, and `migrated-memory-and-user-context.md` are owner-specific topic files, not exact duplicates.

## Canonical ownership map

| Topic | Canonical owner after dedup |
| --- | --- |
| Local workspace cleanup, dirty-root preservation, stale worktree/branch classification | `.hermes/skills/software-development/git-worktree-safety-pack/` |
| General PR lifecycle, CI interpretation, PR body safety, merged/open PR follow-up | `.hermes/skills/github/github-pr-workflow/` |
| `skills-jk` bot-authored PR workflow and repo-specific `create-pr.yml` quirks | `.hermes/skills/software-development/skills-jk-gha-pr-creation/` |
| Unsloth generated documentation corpus | `.hermes/skills/mlops/training/unsloth/references/llms-txt.md` |
| Structured-generation library-specific backend/example details | The owning library skill, currently `guidance` or `outlines`. |
| Baoyu comic/infographic output contracts | The owning creative skill, currently `baoyu-comic` or `baoyu-infographic`. |
| Outbound-agent Gmail/Tencent operational runbooks | `.hermes/skills/software-development/outbound-agent-dev-environment-operations/`, with product OAuth diagnostics, VM runtime env sync, and deploy/notification runbooks kept as separate topic rows. |

## Removed duplicate references

The following `skills-jk-gha-pr-creation` references were removed because their durable guidance is now represented in `git-worktree-safety-pack`, `github-pr-workflow`, or the rewritten repo-specific quirk reference:

- `avoid-duplicate-payload-prs.md`
- `behind-main-untracked-upstream-collapse.md`
- `behind-root-stale-deletion-hunks.md`
- `cleanup-discovered-branch-pr.md`
- `copy-to-worktree-repeated-local-sweep.md`
- `final-cleanup-merge-race-and-regenerated-residue.md`
- `iterative-root-residue-amend-pr.md`
- `local-sweep-meaningful-nonpr-worktree-pr.md`
- `local-sweep-requested-subset-collapse.md`
- `merged-pr-during-scoped-memory-update.md`
- `multi-bucket-root-residue-pr-split.md`
- `post-reset-skill-reference-residue.md`
- `preserved-payload-root-clean-completion.md`
- `repeated-cleanup-after-followup-pr.md`
- `repeated-scoped-memory-cleanup-with-preserve-branch.md`
- `repeated-workspace-sweep-final-clean-loop.md`
- `root-behind-false-scoped-payload.md`
- `scoped-config-memory-noop-skill-residue-pr.md`
- `scoped-memory-pr-root-reset-cleanup.md`
- `scoped-memory-pr-with-open-skill-residue.md`
- `stale-generated-skill-bundle-residue.md`
- `temporary-draft-worktree-cleanup.md`

The following outbound-agent reference was removed because its durable negative-test guidance is now represented in `tencent-gmail-oauth-negative-test-and-restore.md`:

- `tencent-gmail-oauth-negative-secret-test.md`

The following unreferenced `unsloth` source-overlap references were removed because `llms-txt.md` is the skill-listed canonical documentation corpus:

- `llms-full.md`
- `llms.md`

## Retained `skills-jk-gha-pr-creation` references

| File | Reason retained |
| --- | --- |
| `dirty-root-preserve-pr-cleanup-loop.md` | Rewritten as the repo-specific cleanup quirk map and canonical-owner pointer. |
| `create-pr-workflow-node-runtime-upgrade.md` | Covers the special case where the workflow used to open the PR is itself being changed. |
| `repeated-cleanup-old-active-skill-port.md` | Covers stale active-skill residue after pack migration, not generic cleanup. |
| `sed-conflict-strip-pitfall.md` | Covers a markdown conflict-resolution trap specific enough to keep as a safety note. |
| `squash-merged-pr-worktree-cleanup.md` | Covers tree-diff validation for squash-merged PR worktrees. |

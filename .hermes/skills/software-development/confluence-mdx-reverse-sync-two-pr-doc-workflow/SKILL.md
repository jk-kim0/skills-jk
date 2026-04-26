---
name: confluence-mdx-reverse-sync-two-pr-doc-workflow
description: "Update querypie-docs/confluence-mdx reverse-sync docs in two sequential PRs: first a current-state documentation PR, then a separate Draft PR for a replacement plan document."
---

# Confluence MDX reverse-sync two-PR doc workflow

Use this when the user wants reverse-sync documentation work in `querypie-docs/confluence-mdx/` split into two PRs:
1. first, update docs to match the current implementation exactly
2. second, create a separate Draft PR for a new replacement plan document and refine it through review

This skill captures the user's preferred workflow for reverse-sync doc/planning work.

## When to use
- User asks to document the current reverse-sync implementation state
- User asks to replace stale reverse-sync plan docs with a new plan
- User wants the work split across separate PRs, with the plan PR left as Draft for review
- The task involves `confluence-mdx/docs/`, reverse-sync code/tests, commit history, and plan docs together

## Core principles
- Do not mix “current state” and “future plan” into one PR
- Start each PR from a fresh worktree and fresh branch
- Base the current-state PR on what the code actually does now, not what older docs said it would do
- Base the replacement-plan PR on the current implementation, not on stale phase numbering
- Mark older plan docs as superseded rather than silently leaving them as active guidance

## Recommended sequence

### PR 1 — Current-state docs (non-Draft)
1. Inspect only the narrow relevant scope:
   - recent commit log for `confluence-mdx/bin/reverse_sync*`, tests, and docs
   - reverse-sync code modules
   - reverse-sync tests/fixtures/manifests
   - existing docs under `confluence-mdx/docs/`
2. Identify stale assumptions in docs, especially references to removed or outdated modules/flows.
3. Update the architecture/current-analysis docs so they reflect the real implementation.
4. Prefer updating these kinds of docs:
   - `confluence-mdx/docs/architecture.md`
   - reverse-sync analysis/status docs such as `confluence-mdx/docs/analysis-reverse-sync-refactoring.md`
5. Commit, push, and create a normal PR.

### PR 2 — Replacement plan (Draft)
1. Start from a separate fresh worktree/branch from `main`.
2. Read the old reverse-sync plan docs and review docs, but treat them as historical context only.
3. Write a new replacement plan document that:
   - explicitly says it supersedes the older plan docs
   - starts from the current code reality
   - separates current-state description from future design/work
   - defines concrete review questions for the user
4. Add a short superseded banner/link at the top of the old plan docs.
5. Commit, push, and create a Draft PR.

## Good investigation checklist
- `git log` on reverse-sync code, tests, and docs
- current branch/PR state before starting
- reverse-sync docs under `confluence-mdx/docs/`
- plan docs under `confluence-mdx/docs/plans/`
- code hotspots like:
  - `bin/reverse_sync_cli.py`
  - `bin/reverse_sync/patch_builder.py`
  - `bin/reverse_sync/sidecar.py`
  - list/table/reconstructor/verifier-related modules
- tests and manifests such as:
  - `tests/test_reverse_sync_cli.py`
  - `tests/testcases/`
  - `tests/reverse-sync/pages.yaml`

## What to emphasize in the current-state PR
- what `run_verify()` / current verify flow actually does
- distinction between `mapping.yaml` and roundtrip sidecar v3 roles
- `patch_builder.py` as the current policy engine
- current capability boundaries and conservative skip behavior
- known weak areas such as table/preserved-anchor/normalization-sensitive cases
- whether older design terms still match the code, especially when reviewing reverse-sync docs for terminology drift

### Terminology-alignment audit for reverse-sync docs
When the user asks whether a past design was actually implemented, do a narrow terminology audit across code and docs before editing prose.

1. Search only the reverse-sync scope for both old and current terms.
   - Old design vocabulary to check: `ParagraphEditSequence`, `EditSequence`, `TextSegment`, `edit sequence`, `mdx fragment segment`
   - Current implementation vocabulary to check: `VisibleSegment`, `visible_segments`, `replace_fragment`, `reconstruct_fragment_with_sidecar`, `patch_xhtml`, `structural_fingerprint`, `mapping`, `sidecar`
2. Confirm whether the old design names still exist as code symbols, not just as prose in docs.
3. Distinguish local vs system-wide concepts:
   - `visible_segments.py` is evidence that segment-based modeling still exists in some paths, especially list handling
   - do not overstate this into "the whole reverse-sync engine is edit-sequence based" unless the broader pipeline actually uses that abstraction end-to-end
4. Treat the current implementation's center of gravity as:
   - block diff / mapping / sidecar
   - strategy selection inside `patch_builder.py`
   - patch actions such as `modify`, `delete`, `insert_*`, `replace_fragment`
   - roundtrip verification / proof-like checks
5. When a doc mixes old and new terms, call that out explicitly instead of silently normalizing it away. In particular, inspect both the top and bottom sections of long docs like `confluence-mdx/docs/architecture.md`; some sections may already describe `replace_fragment` and reconstruction accurately while later summary sections still use stale `edit sequence` wording.
6. In summaries, use precise conclusions:
   - "partially reflected" when segment ideas survive only in local paths
   - "not the current main abstraction" when old design terms no longer exist in code
   - "terminology is mixed/stale" when current-state docs and historical design docs use different conceptual frames

## What to emphasize in the replacement-plan PR
- move away from old phase-driven stale planning
- define future work around current bottlenecks, not already-completed migrations
- useful framing includes:
  - capability registry / capability matrix
  - planner vs strategy vs proof separation
  - verifier/result taxonomy cleanup
  - fixture/manifest role clarification
  - explicit support boundary for risky structures like tables
- if review narrows scope, update the plan doc instead of defending the earlier broader framing
- for tables specifically, capture the user's current preference as:
  - current table support is sufficient for now
  - near-term work should prioritize verifier-side judgment/normalization, not broader table patching support
  - whitespace-only differences and column-width-only differences in table verification should be treated as matches rather than mismatches
- when the Draft plan PR is refined through review and core directions become agreed, update the replacement plan so it:
  - explicitly states the new replacement plan is the current primary planning document
  - leaves the older 3월 plan/review/cleanup docs as superseded historical records
  - replaces open-ended review-question wording with an "agreed direction" section once consensus is reached
- if the user agrees to move toward a visible-segment-centered redesign, update the replacement plan to describe that precisely as:
  - visible segment is promoted to the planner layer's main planning language, not a universal replacement for all reverse-sync logic
  - text-bearing blocks should follow `visible segment -> edit sequence -> XHTML node operation`
  - the apply layer should continue using patch/DOM/sidecar mechanics such as `patch_xhtml()` rather than inventing a second apply system
  - preserved-anchor / container / table / risky structures should remain on sidecar/template-preserving fallback paths or explicit `replace_fragment` / `skip` boundaries
  - paragraph/heading expansion should be framed as a staged follow-up after the existing list-oriented visible-segment path
- capture the following reverse-sync planning conventions when they are agreed in review:
  - `pages.yaml` should be described as a reference metadata catalog for real reverse-sync usage; extra fields belong to test-case implementation context and should not be over-framed as a major architecture problem
  - verifier taxonomy should be allowed to grow more detailed than simple pass/fail and can be documented at an intermediate operational resolution such as Accept / Review / Block / Error
  - planner / strategy / proof can be treated as the main cleanup/reorganization axis for the codebase when the user agrees

## Branch / PR conventions
- Use separate fresh worktrees for each PR
- Keep PR 1 as a normal reviewable PR
- Keep PR 2 as Draft unless the user explicitly asks otherwise
- Mention PR numbers and URLs in the final report

## Commit guidance
- Since files are under `confluence-mdx/`, use the `confluence-mdx:` prefix per repo convention
- Commit message/body should be in Korean honorific style
- Include Claude co-author line when applicable

## Pitfalls
- Do not create the plan PR before the current-state docs PR
- Do not keep using old plan docs as if they are still authoritative
- Do not mix implementation-state edits and future-plan rewrites into one PR
- Do not reuse an existing PR branch for the second task
- Do not rely on heavy repo-wide scans when a narrow reverse-sync/doc scope is enough

## Minimal deliverables
- PR 1: current-state reverse-sync docs updated and opened as a normal PR
- PR 2: new replacement plan doc added, old plan docs marked superseded, opened as a Draft PR
- Final report includes both PR numbers and URLs

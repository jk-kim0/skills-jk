---
name: corp-web-japan-pack
description: Use when working in corp-web-japan, querypie.ai, querypie.jp, or Japanese public-site migration/parity tasks. Thin active entrypoint that points to the inactive repo-specific skill pack index instead of injecting every detailed skill into the default skills index.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [repo-skill-pack, corp-web-japan, prompt-size]
    related_skills: []
---
# corp-web-japan Pack

## Overview

This is a thin active entrypoint for the `corp-web-japan` repo-specific skill pack. The detailed skills live outside active `.hermes/skills/` at:

`.hermes/skill-packs/corp-web-japan/`

Keeping the detailed skills outside `.hermes/skills/` prevents their full name/description index from being injected into every default Hermes request.

## When to Use

- Use when working in corp-web-japan, querypie.ai, querypie.jp, or Japanese public-site migration/parity tasks.
- The user explicitly mentions `corp-web-japan` or a task clearly belongs to that repository/workstream.
- You need repo-specific historical workflow, route/content, visual parity, CI, or PR guidance for this area.

## Required First Step

Read the pack index before selecting detailed skills:

`.hermes/skill-packs/corp-web-japan/INDEX.md`

Then read only the specific `SKILL.md` files referenced by the index that match the current task.

If the pack index is not present in the active checkout, fall back to the repo-local skill index at `.agents/skills/README.md`, then load the narrowest checked-in skill for the task. For public MDX publication work, this usually means `.agents/skills/mdx-publication-operations/SKILL.md` followed by the matching family wrapper such as `.agents/skills/news-posting/SKILL.md`.

## References

- `references/news-publication-addition.md` — checklist and pitfall for adding local `src/content/news/*.mdx` records, including route-aligned assets and the news corpus test expectation.
- `references/og-preview-image-authoring.md` — durable rule for route-aligned PNG Open Graph preview images in public MDX authoring guidance, including how to port equivalent rules from `corp-web-app` without documenting unsupported frontmatter as active contract.
- `references/lingo-web-sibling-migration.md` — workflow for refreshing `corp-web-japan/src/app/lingo/**` from sibling `../lingo-web`, including import/path rewriting, `/lingo` namespace policy, same-site `querypie.ai` link normalization, and conflict-safe PR verification.
- `references/component-name-debug-marker-authoring.md` — follow-up workflow for adding `componentNameDebugProps()` marker coverage after the Component Name Debug infrastructure exists, including no-wrapper authoring rules and source-level verification.
- `references/component-name-debug-followups.md` — durable workflow for Component Name Debug follow-up marker authoring when the overlay exists but most pages do not expose component names.

## Common Pitfalls

0. When the user asks from a `corp-web-japan` context to use files from a sibling/private repo (for example `../skills-jk-private`) and says to move/copy a draft directory into `docs/...`, treat the sibling repo as the source of truth and `corp-web-japan` as the target unless they explicitly ask to modify the sibling repo. Do not open a PR in the source repo. Create/update the `corp-web-japan` PR, copy only the requested files, and apply follow-up naming/format requests (such as `.ko.md` / `.ja.md` language pairs) in the target repo's PR.
0a. When opening or updating a public `corp-web-japan` PR from private/sibling draft material, do not expose the private source repository name in the PR title/body unless the user explicitly asks. Describe provenance in stakeholder-safe terms such as “based on Brant's direction and the provided reference materials” when that matches the task context. If the user requests English PR metadata, use English even if repo defaults often prefer Korean PR descriptions.
0b. For draft planning docs under `docs/draft-*`, do not leave vague checklist bullets like “confirm technical scope” without explaining the underlying decision. Rewrite open questions so each item states the context, the uncertainty, why it matters, and how it affects public copy/implementation. When the user confirms a capability is in QueryPie’s service scope, replace tentative language with confident service-coverage wording. Do not add defensive caveats such as “subject to customer environment, PoC/diagnosis results, priorities, or deliverable-level agreement” unless the user explicitly asks for that qualification; consultation-specific adjustment is obvious and does not need to appear before the customer conversation. Do not generalize concrete timelines from a private/customer-specific reference meeting into public homepage copy: for example, a “one-week investigation” or “1–2 month” estimate from a Payroll context where Brant already understood the system should not become a generic public service timeline.
1. Do not assume these detailed skills are available through `skill_view`; they are intentionally outside active skill discovery.
2. Do not read the entire pack for narrow tasks. Use the index trigger map and load the smallest relevant subset.
3. If `.hermes/skill-packs/corp-web-japan/INDEX.md` is absent in the active checkout, use `.agents/skills/README.md` as the repo-local fallback index rather than stopping.
4. For repo-maintenance requests in `corp-web-japan` such as `workspace 정리`, the repo-local publication/migration skills are usually not needed after the index check. Treat the request as generic repo-local git cleanup: verify live cwd/repo root, fetch/prune, cross-check open/merged PRs before deleting branches or worktrees, update root `main` by fast-forward when safe, and report preserved open-PR worktrees explicitly.
5. If this pack is needed frequently in a dedicated profile, symlink or copy `.hermes/skill-packs/corp-web-japan/skills/*` into that profile's active `.hermes/skills/` instead of re-expanding the default profile.

## Verification Checklist

- [ ] `.hermes/skill-packs/corp-web-japan/INDEX.md` was read.
- [ ] Only task-relevant detailed skill files were loaded.
- [ ] Active `.hermes/skills/` remains compact.

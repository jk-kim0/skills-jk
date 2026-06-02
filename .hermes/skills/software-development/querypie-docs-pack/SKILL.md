---
name: querypie-docs-pack
description: Use when working in querypie-docs, especially confluence-mdx reverse sync or MDX translation follow-up tasks. Thin active entrypoint that points to the inactive repo-specific skill pack index instead of injecting every detailed skill into the default skills index.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [repo-skill-pack, querypie-docs, prompt-size]
    related_skills: []
---
# querypie-docs Pack

## Overview

This is a thin active entrypoint for the `querypie-docs` repo-specific skill pack. The detailed skills live outside active `.hermes/skills/` at:

`.hermes/skill-packs/querypie-docs/`

Keeping the detailed skills outside `.hermes/skills/` prevents their full name/description index from being injected into every default Hermes request.

## When to Use

- Use when working in querypie-docs, especially confluence-mdx reverse sync or MDX translation follow-up tasks.
- The user explicitly mentions `querypie-docs` or a task clearly belongs to that repository/workstream.
- You need repo-specific historical workflow, route/content, visual parity, CI, or PR guidance for this area.

## Required First Step

Read the pack index before selecting detailed skills:

`.hermes/skill-packs/querypie-docs/INDEX.md`

Then read only the specific `SKILL.md` files referenced by the index that match the current task.

If the `.hermes/skill-packs/querypie-docs/INDEX.md` file is not present in the checkout, fall back to the repo-local guidance files instead of proceeding from memory:

1. Read `CLAUDE.md` for repository conventions and required docs.
2. Read `.claude/skills/README.md` if present.
3. For Korean source changes that need English/Japanese parity, read `.claude/skills/sync-ko-to-en-ja.md`, `.claude/skills/translation.md`, and `.claude/skills/mdx-skeleton-comparison.md`.
4. For commit/PR wording, read `docs/commit-pr-guide.md` and `.claude/skills/commit.md` if needed.

If the pack index is absent in the current checkout, do not stop or guess. Fall back to the repo-local guidance files that are actually present, in this order:

1. `CLAUDE.md` or `AGENTS.md` in the repo/subdirectory context.
2. `.claude/skills/README.md` and any matching `.claude/skills/*/SKILL.md` files, if present.
3. `docs/commit-pr-guide.md` for commit/PR title, body, language, and footer conventions.

Record in the progress note that the pack index was unavailable and which fallback guidance was used.

## Common Pitfalls

1. Do not assume these detailed skills are available through `skill_view`; they are intentionally outside active skill discovery.
2. Do not read the entire pack for narrow tasks. Use the index trigger map and load the smallest relevant subset.
3. If this pack is needed frequently in a dedicated profile, symlink or copy `.hermes/skill-packs/querypie-docs/skills/*` into that profile's active `.hermes/skills/` instead of re-expanding the default profile.
4. For Confluence Space synchronization PRs, do not frame the PR as only a file rename or a single-language update when the source change affects localized docs. PR titles should start with `mdx:` and describe the content synchronization, and PR bodies should emphasize content changes. When a Korean MDX file is renamed or its links/meta change, apply the corresponding filename, `_meta.ts`, product/link, and translated content updates to English and Japanese as well.
5. For localized MDX changes, verify that old slugs/titles such as the previous release-note range and temporary `#link-error` placeholders are fully removed across `src/content/{ko,en,ja}` before pushing.
6. After adding or translating structure-heavy MDX changes, run targeted skeleton comparisons from `confluence-mdx` using `target/{lang}/...` paths for the affected English/Japanese files, then reset generated `.skel.mdx` files before committing.

## References

- `references/local-content-pr-from-existing-changes.md` — workflow for turning existing querypie-docs local MDX/content changes into a PR, including release-note rename consistency checks and repo PR conventions.

## Verification Checklist

- [ ] `.hermes/skill-packs/querypie-docs/INDEX.md` was read, or repo-local fallback guidance (`CLAUDE.md` / `.claude/skills/`) was read when the pack index was absent.
- [ ] Only task-relevant detailed skill files were loaded.
- [ ] Active `.hermes/skills/` remains compact.
- [ ] For Confluence Space MDX sync PRs, apply the checklist in `references/confluence-space-mdx-sync-pr.md`.

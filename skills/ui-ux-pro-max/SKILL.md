---
name: ui-ux-pro-max
description: Use for UI/UX design intelligence by reading the external UI UX Pro Max skill, then applying repo-local overrides and additions.
tags: [ui, ux, design, design-system, accessibility, frontend, external-skill]
---

# UI UX Pro Max Wrapper

This repository tracks only the integration surface for UI UX Pro Max.
The upstream skill content is kept in a git submodule and must not be edited here.

## When to Use

Use this skill for tasks involving UI structure, visual design, interaction design, accessibility review, responsive layout, frontend polish, component UX, dashboards, landing pages, design systems, typography, color systems, or UI quality review.

Do not use this skill for pure backend, database, infrastructure, or non-visual automation work.

## Required Loading Order

1. Read the upstream skill first:

   `/Users/jk/workspace/skills-jk/external-skills/ui-ux-pro-max-skill/.claude/skills/ui-ux-pro-max/SKILL.md`

   Human-readable equivalent:

   `~/workspace/skills-jk/external-skills/ui-ux-pro-max-skill/.claude/skills/ui-ux-pro-max/SKILL.md`

   Repo-relative maintenance path, only when the current working directory is the `skills-jk` repository root:

   `external-skills/ui-ux-pro-max-skill/.claude/skills/ui-ux-pro-max/SKILL.md`

2. Then read the repo-local overrides:

   `references/local-overrides.md`

3. Apply repo-local overrides after upstream guidance.
   When upstream and local guidance conflict, local guidance wins.

Do not rely on the current working directory or wrapper-relative traversal for upstream paths.
Codex may load this wrapper from the `~/.codex/skills` symlink while working in another repository.

## Upstream Search Tool

Use the upstream search and design-system helper from the submodule when a UI task needs product-specific recommendations, style matching, color palettes, typography, chart guidance, or UX rule lookup.
Use the canonical absolute path below so the commands work from any current working directory.
For readability, the same location is `~/workspace/skills-jk/external-skills/ui-ux-pro-max-skill`.

```bash
python3 /Users/jk/workspace/skills-jk/external-skills/ui-ux-pro-max-skill/src/ui-ux-pro-max/scripts/search.py "<query>" --design-system -f markdown
python3 /Users/jk/workspace/skills-jk/external-skills/ui-ux-pro-max-skill/src/ui-ux-pro-max/scripts/search.py "<query>" --domain ux -n 3
python3 /Users/jk/workspace/skills-jk/external-skills/ui-ux-pro-max-skill/src/ui-ux-pro-max/scripts/search.py "<query>" --stack nextjs
```

## Maintenance Boundary

- Do not edit files under `external-skills/ui-ux-pro-max-skill`.
- To update upstream, move the submodule to a new tag or commit and review the wrapper assumptions.
- Put repo-specific behavior, restrictions, examples, and additions under this skill directory.
- Keep this wrapper small so upstream remains the source of the imported design knowledge.

---
name: corp-web-app-pack
description: Use when working in corp-web-app, especially route-local authoring, Tailwind migration, content unification, or stage E2E tasks. Thin active entrypoint that points to the inactive repo-specific skill pack index instead of injecting every detailed skill into the default skills index.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [repo-skill-pack, corp-web-app, prompt-size]
    related_skills: []
---
# corp-web-app Pack

## Overview

This is a thin active entrypoint for the `corp-web-app` repo-specific skill pack. The detailed skills live outside active `.hermes/skills/` at:

`.hermes/skill-packs/corp-web-app/`

Keeping the detailed skills outside `.hermes/skills/` prevents their full name/description index from being injected into every default Hermes request.

## When to Use

- Use when working in corp-web-app, especially route-local authoring, Tailwind migration, content unification, or stage E2E tasks.
- The user explicitly mentions `corp-web-app` or a task clearly belongs to that repository/workstream.
- You need repo-specific historical workflow, route/content, visual parity, CI, or PR guidance for this area.

## Required First Step

Read the pack index before selecting detailed skills:

`.hermes/skill-packs/corp-web-app/INDEX.md`

Then read only the specific `SKILL.md` files referenced by the index that match the current task.

## Task References

- `references/introduction-deck-mdx-gating.md` — proven pattern for fixing gated introduction-deck MDX detail pages by splitting at `<GatingCut />`, rendering the post-cut content behind `GatingFormWrapper`, and using a temporary root `node_modules` symlink for fast fresh-worktree verification when appropriate.

## Common Pitfalls

1. Do not assume these detailed skills are available through `skill_view`; they are intentionally outside active skill discovery.
2. Do not read the entire pack for narrow tasks. Use the index trigger map and load the smallest relevant subset.
3. If this pack is needed frequently in a dedicated profile, symlink or copy `.hermes/skill-packs/corp-web-app/skills/*` into that profile's active `.hermes/skills/` instead of re-expanding the default profile.
4. For gated introduction-deck MDX, do not render the entire body with `GatingCut: () => null`; split at the marker first so the post-cut content and download CTA stay behind the form.

## Verification Checklist

- [ ] `.hermes/skill-packs/corp-web-app/INDEX.md` was read.
- [ ] Only task-relevant detailed skill files were loaded.
- [ ] Active `.hermes/skills/` remains compact.

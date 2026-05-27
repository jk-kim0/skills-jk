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

First check whether this repository exposes repo-local checked-in skills under `.agents/skills/`.

In the current `corp-web-app` setup, treat `.agents/skills/README.md` as the first local index and load only the minimum matching repo-local skills from `.agents/skills/<name>/SKILL.md`.

If a future checkout instead uses the external pack layout, read the pack index before selecting detailed skills:

`.hermes/skill-packs/corp-web-app/INDEX.md`

Then read only the specific `SKILL.md` files referenced by the index that match the current task.

## Task References

- `references/introduction-deck-mdx-gating.md` — proven pattern for fixing gated introduction-deck MDX detail pages by splitting at `<GatingCut />`, rendering the post-cut content behind `GatingFormWrapper`, and using a temporary root `node_modules` symlink for fast fresh-worktree verification when appropriate.

## Common Pitfalls

1. Do not assume these detailed skills are available through `skill_view`; they are intentionally outside active skill discovery.
2. Do not read the entire pack for narrow tasks. Use the index trigger map and load the smallest relevant subset.
3. If this pack is needed frequently in a dedicated profile, symlink or copy `.hermes/skill-packs/corp-web-app/skills/*` into that profile's active `.hermes/skills/` instead of re-expanding the default profile.
4. For publish/public-route conflict reviews in `corp-web-app`, do not stop at filesystem route existence. Also inspect the legacy catch-all route, preview-navigation mappings, and live production responses/redirects, because a public path can already be behaviorally occupied even when no dedicated App Router file exists.
5. In this repo, the active skill source may be `.agents/skills/**` rather than `.hermes/skill-packs/**`; verify the real local skill root before assuming the pack layout.

## Verification Checklist

- [ ] `.hermes/skill-packs/corp-web-app/INDEX.md` was read.
- [ ] Only task-relevant detailed skill files were loaded.
- [ ] Active `.hermes/skills/` remains compact.

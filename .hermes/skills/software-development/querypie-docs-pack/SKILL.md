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

## Common Pitfalls

1. Do not assume these detailed skills are available through `skill_view`; they are intentionally outside active skill discovery.
2. Do not read the entire pack for narrow tasks. Use the index trigger map and load the smallest relevant subset.
3. If this pack is needed frequently in a dedicated profile, symlink or copy `.hermes/skill-packs/querypie-docs/skills/*` into that profile's active `.hermes/skills/` instead of re-expanding the default profile.

## Verification Checklist

- [ ] `.hermes/skill-packs/querypie-docs/INDEX.md` was read.
- [ ] Only task-relevant detailed skill files were loaded.
- [ ] Active `.hermes/skills/` remains compact.

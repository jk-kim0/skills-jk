# querypie-docs skill pack

Use when working in querypie-docs, especially confluence-mdx reverse sync or MDX translation follow-up tasks.

This pack is intentionally stored outside active `.hermes/skills/` so its detailed skill index is not injected into every Hermes request. Load this index only when the current task matches this repository area, then read the specific `SKILL.md` files needed for the task.

## Summary

- skills: 2
- skill root: `.hermes/skill-packs/querypie-docs/skills/`
- active entrypoint: `.hermes/skills/software-development/querypie-docs-pack/SKILL.md`

## How to use

1. Read this `INDEX.md` first.
2. Pick the smallest relevant skill set from the trigger map below.
3. Read the selected `.hermes/skill-packs/.../SKILL.md` files directly with file tools.
4. Do not copy the whole pack into the prompt unless the task truly requires broad repo archaeology.

## Trigger map

### content/MDX migration

- `querypie-docs` — `.hermes/skill-packs/querypie-docs/skills/software-development/querypie-docs/SKILL.md`
  - Use when working in querypie-docs, especially confluence-mdx forward conversion and reverse-sync workflows; contains migrated repo-specific memory and user preferences.
- `querypie-docs-mdx-translation-followup` — `.hermes/skill-packs/querypie-docs/skills/software-development/querypie-docs-mdx-translation-followup/SKILL.md`
  - Update English and Japanese translations for querypie-docs Confluence/MDX Korean source-sync PRs, using repo-local skills and targeted skeleton checks.

## Full skill list

| skill | path | description |
| --- | --- | --- |
| `querypie-docs` | `.hermes/skill-packs/querypie-docs/skills/software-development/querypie-docs/SKILL.md` | Use when working in querypie-docs, especially confluence-mdx forward conversion and reverse-sync workflows; contains migrated repo-specific memory and user preferences. |
| `querypie-docs-mdx-translation-followup` | `.hermes/skill-packs/querypie-docs/skills/software-development/querypie-docs-mdx-translation-followup/SKILL.md` | Update English and Japanese translations for querypie-docs Confluence/MDX Korean source-sync PRs, using repo-local skills and targeted skeleton checks. |

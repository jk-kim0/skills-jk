# Local Overrides

These rules adapt the external UI UX Pro Max skill to this repository and the standing Codex UI guidance.

## Priority

1. System and developer instructions remain the highest-priority guidance.
2. Repository `AGENTS.md` guidance remains higher priority than upstream UI UX Pro Max guidance.
3. This local override file wins over upstream UI UX Pro Max guidance when they conflict.
4. Upstream UI UX Pro Max guidance fills gaps when local instructions do not decide the issue.

## Local Rules

- Do not vendor or modify upstream skill files in this repository.
- Do not copy upstream datasets or scripts into `skills/ui-ux-pro-max/`.
- Use the submodule as read-only reference material.
- Keep additions small and explicit: local trigger notes, repo-specific UI quality rules, and compatibility notes belong here.
- For frontend implementation, keep following the active Codex frontend guidance for assets, responsive behavior, visual verification, accessibility, cards, colors, text fit, and browser checks.
- For local wrapper changes, verify that the upstream skill path and search script path still exist.

## Wrapper Verification

From the repository root:

```bash
test -f external-skills/ui-ux-pro-max-skill/.claude/skills/ui-ux-pro-max/SKILL.md
test -f external-skills/ui-ux-pro-max-skill/src/ui-ux-pro-max/scripts/search.py
python3 external-skills/ui-ux-pro-max-skill/src/ui-ux-pro-max/scripts/search.py "SaaS dashboard analytics" --design-system -f markdown
```

## Update Procedure

To update the external skill reference:

```bash
git -C external-skills/ui-ux-pro-max-skill fetch --tags
git -C external-skills/ui-ux-pro-max-skill checkout <tag-or-commit>
git add external-skills/ui-ux-pro-max-skill
```

After updating, compare upstream release notes or diff the upstream skill file, then adjust this wrapper only if the loading path, command path, or local conflict rules need to change.

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
- Do not assume the agent's current working directory is `skills-jk`; wrapper commands must work when Codex is operating from another repository such as `/Users/jk/workspace/outbound-agent`.

## Wrapper Verification

Use the canonical absolute upstream path so verification works from any current working directory.
The same location can be read as `~/workspace/skills-jk/external-skills/ui-ux-pro-max-skill`, but command examples should keep the expanded `/Users/jk/...` path.

```bash
UI_UX_PRO_MAX_ROOT=/Users/jk/workspace/skills-jk/external-skills/ui-ux-pro-max-skill
test -f "$UI_UX_PRO_MAX_ROOT/.claude/skills/ui-ux-pro-max/SKILL.md"
test -f "$UI_UX_PRO_MAX_ROOT/src/ui-ux-pro-max/scripts/search.py"
python3 "$UI_UX_PRO_MAX_ROOT/src/ui-ux-pro-max/scripts/search.py" "SaaS dashboard analytics" --design-system -f markdown
```

## Update Procedure

To update the external skill reference:
Set `SKILLS_JK_ROOT` to the checkout you are intentionally updating.
The canonical root checkout is `/Users/jk/workspace/skills-jk` (`~/workspace/skills-jk`); when committing from a linked worktree, use that worktree root instead.

```bash
SKILLS_JK_ROOT=/Users/jk/workspace/skills-jk
UI_UX_PRO_MAX_ROOT="$SKILLS_JK_ROOT/external-skills/ui-ux-pro-max-skill"
git -C "$UI_UX_PRO_MAX_ROOT" fetch --tags
git -C "$UI_UX_PRO_MAX_ROOT" checkout <tag-or-commit>
git -C "$SKILLS_JK_ROOT" add external-skills/ui-ux-pro-max-skill
```

After updating, compare upstream release notes or diff the upstream skill file, then adjust this wrapper only if the loading path, command path, or local conflict rules need to change.

---
name: cc-codex-debate-review-plugin-wrapper
description: Plugin-mode wrapper for cc-codex-debate-review that forwards to the canonical skill at the plugin root without duplicating its body.
---

> **Plugin mode:** Assets (bin, lib, config) are located at the plugin root.
> Set `SKILL_ROOT` to `${CLAUDE_PLUGIN_ROOT}` when following the procedure below.

!`awk 'BEGIN{n=0} /^---$/{n++; if(n<=2) next} n>=2' "${CLAUDE_SKILL_DIR}/../../SKILL.md"`

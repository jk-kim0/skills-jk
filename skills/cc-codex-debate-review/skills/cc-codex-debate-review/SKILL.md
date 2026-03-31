---
name: cc-codex-debate-review
description: Debate-driven PR review orchestration where CC and Codex alternate as lead agent until consensus is reached
---

> **Plugin mode:** Assets (bin, lib, config) are located at the plugin root.
> Set `SKILL_ROOT` to `${CLAUDE_PLUGIN_ROOT}` when following the procedure below.

!`awk 'BEGIN{n=0} /^---$/{n++; if(n<=2) next} n>=2' "${CLAUDE_SKILL_DIR}/../../SKILL.md"`

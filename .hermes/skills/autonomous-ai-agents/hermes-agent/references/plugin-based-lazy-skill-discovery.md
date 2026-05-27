# Plugin-based lazy skill discovery

Use this when reducing Hermes prompt overhead while avoiding long-lived forks or repeated patches to Hermes Agent core.

## Problem

When the built-in `skills` toolset is enabled, Hermes currently injects the skills catalog/index into the system prompt. Large skill libraries can add thousands of tokens even for short user turns.

Changing `agent/prompt_builder.py` / `run_agent.py` can solve this directly, but maintaining a local core patch across Hermes upgrades is operationally expensive.

## Recommended extension pattern

Implement lazy skill discovery as a plugin instead of patching core:

1. Disable the built-in `skills` toolset in the lean/default profile.
2. Enable a plugin-provided toolset such as `lazy_skills`.
3. The plugin registers separate tools, for example:
   - `lazy_skills_search(query, limit, category=None)`
   - `lazy_skill_view(name, file_path=None)`
4. The plugin uses the `pre_llm_call` hook to inject a small, ephemeral top-k candidate list into the current user message.
5. The model loads a selected skill through `lazy_skill_view` before substantial work.

This avoids the full `<available_skills>` system-prompt block while preserving skill discovery.

## Why `pre_llm_call`

Hermes plugin `pre_llm_call` context is appended to the current turn's user message, not the system prompt. This is desirable for lazy/top-k skill discovery because:

- candidates can depend on the current user request and cwd;
- the stable system prompt remains smaller;
- plugin context is ephemeral and not persisted to session DB;
- the approach avoids monkeypatching Hermes internals.

## Suggested profile shape

```yaml
plugins:
  enabled:
    - lazy-skills

platform_toolsets:
  cli:
    - terminal
    - file
    - code_execution
    - memory
    - todo
    - lazy_skills
    - no_mcp
```

Do not include the built-in `skills` toolset in the same lean profile, or the full skills index may still be injected.

## Plugin skeleton

Directory layout:

```text
.hermes/plugins/lazy-skills/
  plugin.yaml
  __init__.py
  lazy_index.py
  README.md
  tests/
    test_lazy_index.py
    test_plugin_tools.py
```

`plugin.yaml`:

```yaml
manifest_version: 1
name: lazy-skills
version: 0.1.0
description: Lazy/top-k skill discovery without injecting the full skills index into the system prompt.
author: jk
kind: standalone
provides_tools:
  - lazy_skills_search
  - lazy_skill_view
provides_hooks:
  - pre_llm_call
```

## Tool design

`lazy_skills_search` should return JSON:

```json
{
  "success": true,
  "query": "...",
  "count": 5,
  "results": [
    {
      "name": "hermes-agent",
      "category": "autonomous-ai-agents",
      "score": 182,
      "description": "Complete guide to using and extending Hermes Agent...",
      "path": ".../SKILL.md"
    }
  ],
  "hint": "Call lazy_skill_view(name) to load the selected skill."
}
```

`lazy_skill_view` should mirror built-in `skill_view` response shape where practical:

```json
{
  "success": true,
  "name": "hermes-agent",
  "description": "...",
  "content": "...",
  "path": ".../SKILL.md",
  "skill_dir": "...",
  "linked_files": {"references": ["..."]}
}
```

Avoid overriding built-in `skills_list` / `skill_view` names unless there is a strong reason; separate names/toolsets are easier to maintain across Hermes upgrades.

## Ranking v1

Start with deterministic lexical ranking instead of embeddings:

- exact name match: +120
- query token in skill name: +40
- query token in category/path: +25
- query token in `metadata.hermes.tags`: +25
- query token in `metadata.hermes.related_skills`: +20
- query token in description: +12
- query token in body headings / first N chars: +5
- cwd basename or git repo name matches skill name/category/path: +25
- Hermes setup/config/troubleshooting query boosts `hermes-agent`

Cache metadata with an mtime/size manifest, e.g. `.hermes/cache/lazy-skills-index.json`, so every turn does not re-parse all SKILL.md files.

## `pre_llm_call` gating

Do not inject candidates on every trivial turn. Recommended gating:

- inject on first turn;
- inject for substantial/specialized tasks: repo work, PR/review/debug/plan/config/Hermes/skill-related requests;
- skip simple greetings and generic chit-chat;
- default top_k: 5;
- cap rendered context to ~1,000-1,500 chars.

Example injected context:

```text
[Lazy skill candidates]
The full skill catalog is not in the system prompt. Based on this request, these skills may be relevant:
- hermes-agent: Complete guide to using and extending Hermes Agent...
- skills-jk: Use when working in the skills-jk repository...

If a candidate is relevant, call lazy_skill_view(name=...) before substantial work. If none is relevant, proceed without a skill.
```

## Bootstrap instruction

Because the plugin does not modify the system prompt, add a tiny rule in repo/profile context such as AGENTS.md or SOUL.md:

```text
When the `lazy_skills` toolset is available, do not assume the full skill catalog is in the system prompt. Before substantial or specialized work, use lazy_skills_search with the user's request and cwd. If a relevant skill is found, load it with lazy_skill_view before acting.
```

This is far cheaper than injecting the full skills index.

## Upgrade/maintenance strategy

Treat the plugin as the compatibility boundary. Avoid:

- monkeypatching `run_agent.py` or `prompt_builder.py`;
- parsing or rewriting the system prompt;
- overriding built-in tools without need;
- depending on private internal functions.

Rely on relatively stable surfaces:

- plugin manifest + `register(ctx)`;
- `ctx.register_tool(...)`;
- `pre_llm_call` hook;
- filesystem layout `skills/**/SKILL.md`;
- YAML frontmatter.

## Tests and smoke checks

Unit tests:

- scan SKILL.md frontmatter and category/path;
- skip archive/disabled/platform-incompatible skills;
- ranking exact-name and repo/cwd boosts;
- limit/category filtering;
- linked file read and path traversal blocking.

Smoke checks after Hermes upgrades:

```bash
HERMES_HOME=/path/to/profile HERMES_PLUGINS_DEBUG=1 hermes tools list
hermes chat --toolsets terminal,file,code_execution,memory,todo,lazy_skills -q "Hermes prompt size 줄이는 방법 점검해줘"
```

Prompt-size regression checks:

- the lean profile should not include built-in `skills`;
- the system prompt should not contain a full `<available_skills>` block;
- simple request token size should stay below an agreed threshold.

## Tradeoff

This is not identical to a core `skills.index_mode=lazy` feature. It is an operationally safer extension pattern:

- easier to keep across Hermes upgrades;
- reversible by re-enabling built-in `skills`;
- slightly weaker enforcement because the model must follow bootstrap/context hints;
- good enough for repo-local prompt-cost reduction experiments.

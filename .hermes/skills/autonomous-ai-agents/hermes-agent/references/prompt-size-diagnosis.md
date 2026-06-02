# Prompt size diagnosis

Use this when a user asks how large Hermes requests really are, or why a "short" prompt still feels expensive/slow.

## What to measure

Hermes request size is usually dominated by four buckets:

1. System prompt
2. Tool schemas
3. Skills index in the system prompt
4. Memory / user-profile / project-context blocks

For simple prompts, the user message itself is often negligible.

## Fast measurement recipe

Run a Python probe against the live Hermes install:

```python
import sys, json, os
sys.path.insert(0, '/Users/jk/.hermes')
from run_agent import AIAgent
from agent.model_metadata import estimate_request_tokens_rough
from agent.prompt_builder import (
    build_skills_system_prompt,
    build_context_files_prompt,
    build_environment_hints,
    load_soul_md,
)

sample_msg = [{'role': 'user', 'content': '안녕'}]
agent = AIAgent(quiet_mode=True, platform='cli', session_id='prompt-sizing-probe')

system_prompt = agent._build_system_prompt(None)
tools = agent.tools or []

result = {
    'system_prompt_tokens_rough': estimate_request_tokens_rough([], system_prompt=system_prompt, tools=None),
    'tool_tokens_rough': estimate_request_tokens_rough([], system_prompt='', tools=tools),
    'full_simple_request_tokens_rough': estimate_request_tokens_rough(sample_msg, system_prompt=system_prompt, tools=tools),
    'skills_prompt_tokens_rough': estimate_request_tokens_rough([], system_prompt=build_skills_system_prompt(), tools=None),
    'project_context_tokens_rough': estimate_request_tokens_rough([], system_prompt=build_context_files_prompt(cwd=os.getcwd(), skip_soul=True), tools=None),
    'environment_tokens_rough': estimate_request_tokens_rough([], system_prompt=build_environment_hints(), tools=None),
    'soul_tokens_rough': estimate_request_tokens_rough([], system_prompt=load_soul_md() or '', tools=None),
}
print(json.dumps(result, ensure_ascii=False, indent=2))
```

## Memory-specific checks

Distinguish two different memory costs:

1. Memory/user-profile text already baked into the system prompt
2. Per-turn recalled memory injected into the current user message via `prefetch_all()`

Check recalled memory separately:

```python
mem = agent._memory_manager.prefetch_all('안녕') if getattr(agent, '_memory_manager', None) else ''
```

If this returns empty, dynamic recall is not contributing to that specific prompt, even if the system prompt still contains MEMORY / USER PROFILE sections.

## Reproducing the real CLI toolset

Do **not** assume `AIAgent()` with no `enabled_toolsets` matches the current CLI session. In current Hermes builds, `AIAgent()` direct construction can bypass `platform_toolsets` and load the broader default tool registry, producing an inflated "actual default" measurement. To measure what `hermes chat` / CLI really uses, resolve the configured CLI platform toolsets first:

```python
from hermes_cli.config import load_config
from hermes_cli.tools_config import _get_platform_tools

cfg = load_config()
cli_toolsets = sorted(_get_platform_tools(cfg, 'cli'))
agent = AIAgent(
    quiet_mode=True,
    platform='cli',
    session_id='prompt-sizing-probe-cli',
    enabled_toolsets=cli_toolsets,
)
```

For profile-specific measurements, set `HERMES_HOME` to the target profile directory before running the probe, or invoke the probe through the target profile's environment. Also inspect `hermes -p <profile> tools list` and the profile-local `skills/`, `memories/MEMORY.md`, and `memories/USER.md`: a profile can have the `skills` toolset enabled but zero profile-local skills, causing the system prompt to be much smaller than the default profile.

## Minimal-profile comparisons

To show users what actually matters, compare against stripped variants:

```python
AIAgent(skip_memory=True, skip_context_files=True)
AIAgent(skip_memory=True, skip_context_files=True, enabled_toolsets=['terminal'])
AIAgent(skip_memory=True, skip_context_files=True, enabled_toolsets=[])
```

When comparing against the user's live CLI defaults, include both:

```python
# CLI-configured default
AIAgent(enabled_toolsets=cli_toolsets)

# Explicit lean variants
AIAgent(skip_memory=True, skip_context_files=True, enabled_toolsets=['terminal', 'file'])
AIAgent(skip_memory=True, skip_context_files=True, enabled_toolsets=['terminal', 'file', 'code_execution'])
AIAgent(skip_memory=True, skip_context_files=True, enabled_toolsets=['terminal', 'file', 'code_execution', 'skills', 'memory', 'session_search'])
```

This usually reveals:

- tool schemas are the largest cost bucket until the default toolsets are narrowed
- once toolsets are narrowed, the skills index and USER profile often become the remaining largest buckets
- profile-local skill/memory availability can dominate system prompt size
- AGENTS.md / project context is often smaller than users expect
- dynamic memory recall may be zero for simple prompts

## Interpretation notes

- `estimate_request_tokens_rough()` is a sizing estimator, not exact provider billing.
- It is still good enough for relative attribution: which bucket is large and what a profile change would save.
- When users want practical optimization advice, prioritize toolset reduction first, then skills/system-prompt reduction, then memory/profile cleanup.

## Report session-history overhead separately

For prompt-size diagnosis sessions, distinguish the reusable baseline from the current conversation after the diagnosis work itself. Loading `hermes-agent`, repo-context skills, and prompt-size reference files can add many thousands of tokens to the active conversation history. If the user asks about "this session" or practical next steps, measure or estimate loaded skill/reference files as a separate "diagnosis overhead" bucket and recommend `/reset` or a fresh session after the report when that overhead is material. Do not mix this temporary history growth into the baseline CLI/profile request size.

## User/home AGENTS.md slimming

When reducing prompt overhead from user-scope `AGENTS.md` files, do not assume full deletion is best. Classify each section into:

1. global hard gates that should remain as a short router,
2. detailed procedures that belong in class-level skills,
3. repo-dependent workflows that should be removed from global/user-scope guidance and kept only in the owning repository context.

A good slim user-scope `AGENTS.md` keeps only stable triggers and invariants, such as which skill to load, `env -u GITHUB_TOKEN gh ...` wrappers, KST reporting defaults, PR/CI follow-through expectations, and branch safety reminders. Move command sequences, gate stage details, and output contracts into the relevant skill. If a workflow is repository-specific (for example reverse-sync), remove the global `~/AGENTS.md` trigger and global skill copy instead of preserving it as a user-wide rule.

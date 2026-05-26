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

## Minimal-profile comparisons

To show users what actually matters, compare against stripped variants:

```python
AIAgent(skip_memory=True, skip_context_files=True)
AIAgent(skip_memory=True, skip_context_files=True, enabled_toolsets=['terminal'])
AIAgent(skip_memory=True, skip_context_files=True, enabled_toolsets=[])
```

This usually reveals:

- tool schemas are the largest cost bucket
- the skills index can be surprisingly large
- AGENTS.md / project context is often smaller than expected
- dynamic memory recall may be zero for simple prompts

## Interpretation notes

- `estimate_request_tokens_rough()` is a sizing estimator, not exact provider billing.
- It is still good enough for relative attribution: which bucket is large and what a profile change would save.
- When users want practical optimization advice, prioritize toolset reduction first, then skills/system-prompt reduction, then memory/profile cleanup.
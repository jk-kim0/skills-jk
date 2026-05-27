# Skills lazy/top-k index design

Use this reference when reducing Hermes prompt overhead caused by the skills index, or when implementing/configuring lazy skill discovery.

## Problem

When the `skills` toolset is enabled, Hermes currently injects a skill catalog into the system prompt via `agent.prompt_builder.build_skills_system_prompt()`. On large skill libraries, this can dominate baseline request size even for trivial user messages.

In a measured repo-local setup with ~200 skills:
- default CLI simple request: ~15.9k tokens
- system prompt: ~10.3k tokens
- skill block: ~5.7k tokens
- dynamic memory recall for `안녕`: 0 tokens

The remaining largest prompt-reduction opportunity after toolset slimming is to avoid injecting the full skills index every turn.

## Relevant code paths

- `run_agent.py`
  - `AIAgent._build_system_prompt()` checks whether skill tools are available.
  - It calls `build_skills_system_prompt(available_tools=..., available_toolsets=...)` when any of `skills_list`, `skill_view`, or `skill_manage` is loaded.

- `agent/prompt_builder.py`
  - `build_skills_system_prompt()` scans local/external skills, honors disabled/platform/condition filters, uses `.skills_prompt_snapshot.json`, and renders the full `<available_skills>` block.

- `tools/skills_tool.py`
  - `skills_list(category=None)` currently lists metadata and should be extended with `query` and `limit` for lazy discovery.
  - `skill_view(name, file_path=None)` loads actual skill content.

- `hermes_cli/config.py`
  - `DEFAULT_CONFIG['skills']` is the right place to add mode/config defaults.

## Recommended config shape

```yaml
skills:
  index_mode: full        # full | compact | lazy | off
  index_top_k: 10
  index_always_include:
    - hermes-agent
```

Suggested rollout:
- Keep upstream default as `full` initially for backward compatibility.
- Let heavy repo-local profiles opt into `lazy`.
- Consider later changing new-install defaults after observing behavior.

## Mode semantics

- `full`: current behavior; render all categories and skills.
- `lazy`: do not render `<available_skills>`; render a short instruction telling the model to use `skills_list(query=...)` and `skill_view(name=...)` before substantial/specialized work.
- `compact`: render only a small stable subset, preferably based on cwd/profile/always-include rather than the current user query.
- `off`: no skills prompt despite skill tools being enabled; advanced/debug use only.

## Implementation sequence

### Phase 1 — minimal lazy mode

Files:
- `hermes_cli/config.py`
- `agent/prompt_builder.py`
- tests around prompt builder

Steps:
1. Add `skills.index_mode`, `skills.index_top_k`, and `skills.index_always_include` to default config.
2. Add lightweight config reading in `prompt_builder.py` without importing heavy CLI chains if possible.
3. In `build_skills_system_prompt()`, check mode before full scanning.
4. If mode is `lazy`, return a short guidance block and skip catalog rendering.
5. If mode is `off`, return an empty string.
6. If mode is invalid/missing, fall back to `full` for compatibility.
7. Include mode-related values in the in-process prompt cache key.

Lazy guidance should be short and must not say “scan the skills below” because no full list is shown. It should say:
- the full catalog is available through `skills_list` / `skill_view`
- before substantial or specialized work, call `skills_list(query=...)`
- if the user names a skill, call `skill_view(name=...)`
- for Hermes setup/config/troubleshooting, load `hermes-agent` first
- patch stale/wrong loaded skills with `skill_manage` when available

### Phase 2 — queryable `skills_list`

Files:
- `tools/skills_tool.py`
- optionally `agent/skill_utils.py` if metadata scanning is deduplicated
- tests for skills list query behavior

Extend signature:

```python
def skills_list(category: str = None, query: str = None, limit: int = None, task_id: str = None) -> str:
    ...
```

Extend schema with optional `query` and `limit`.

Ranking v1 can be deterministic lexical scoring:
- exact name match: high score
- token in name/category/tags/related skills: medium score
- token in description/path: lower score
- cwd/repo-name token match: optional bonus

Backcompat:
- no query and no limit returns the existing full listing shape.
- category filter still works.

### Phase 3 — compact/top-k mode

Only add after lazy mode and queryable `skills_list` are stable.

Avoid putting user-query-specific top-k into the stable system prompt because it changes the prompt every turn and weakens prompt caching. Prefer stable inputs:
- `index_always_include`
- cwd basename / repo name / profile name
- category or skill name matches

Render with explicit non-exhaustive wording:

```text
## Skills (compact)
Use skills_list(query=...) to search the full catalog. The subset below is not exhaustive.
<available_skills>
...
</available_skills>
```

## Tests

Recommended test files:
- `tests/test_prompt_builder_skills_index_modes.py`
- `tests/test_skills_list_query.py`

Cases:
- default/missing config preserves full behavior
- `lazy` mode contains lazy guidance and omits `<available_skills>`
- `off` mode returns empty prompt
- invalid mode falls back to full
- `skills_list(query='hermes-agent', limit=5)` ranks `hermes-agent` first
- category + query combine correctly
- disabled/platform-incompatible skills remain excluded

Avoid asserting exact token counts; assert relative prompt length reductions instead.

## Verification probe

After implementation, measure real CLI defaults by resolving platform toolsets first; direct `AIAgent()` construction can overstate tool schema cost.

```python
from hermes_cli.config import load_config
from hermes_cli.tools_config import _get_platform_tools
from run_agent import AIAgent
from agent.model_metadata import estimate_request_tokens_rough

cfg = load_config()
toolsets = sorted(_get_platform_tools(cfg, 'cli'))
agent = AIAgent(quiet_mode=True, platform='cli', session_id='probe', enabled_toolsets=toolsets)
sp = agent._build_system_prompt(None)
tools = agent.tools or []
print(estimate_request_tokens_rough([{'role': 'user', 'content': '안녕'}], system_prompt=sp, tools=tools))
```

Expected heavy-library result after lazy mode: skills block drops from several thousand tokens to a few hundred tokens, while skill tools remain available.

## Pitfalls

- Do not rely on direct `AIAgent()` with no `enabled_toolsets` to measure CLI defaults; it bypasses `platform_toolsets` and can load too many tools.
- Do not put query-specific top-k into the stable system prompt in the first implementation; preserve prompt caching.
- Do not remove the `hermes-agent` hard trigger from short guidance.
- Do not break plugin skills, external skill dirs, disabled skills, platform filters, or conditional skill activation.

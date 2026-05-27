# Lean toolset/profile configuration for prompt-size reduction

Use this when reducing Hermes baseline prompt/tool-schema cost while preserving richer tools in task-specific profiles.

## Pattern proven in skills-jk

Goal:
- Keep the default CLI profile on frequently used baseline toolsets only.
- Put heavier/rarer toolsets in named profiles that can be launched on demand.
- Document the launch commands in repo `AGENTS.md` so future agents suggest them immediately.

Baseline default toolsets used in the session:

```yaml
platform_toolsets:
  cli:
    - terminal
    - file
    - skills
    - code_execution
    - todo
    - memory
    - no_mcp
```

Notes:
- `no_mcp` prevents globally configured MCP servers from being injected into the default CLI session.
- The `tools_config._get_platform_tools()` resolver may still report `kanban` if the Kanban plugin/toolset is available by default; verify actual schemas via `AIAgent` rather than relying only on config text.

Task-specific profiles:

```yaml
# browser-check profile
platform_toolsets:
  cli:
    - terminal
    - file
    - skills
    - code_execution
    - todo
    - memory
    - browser
    - vision
    - chrome-devtools

# cron-config profile
platform_toolsets:
  cli:
    - terminal
    - file
    - skills
    - code_execution
    - todo
    - memory
    - cronjob
    - session_search
    - no_mcp
```

Launch commands:

```bash
hermes -p browser-check
hermes -p browser-check chat -q "..."
hermes -p cron-config
hermes -p cron-config chat -q "..."
```

## Profile creation flow

```bash
HERMES_HOME=/path/to/repo/.hermes hermes profile create browser-check --clone --no-alias
HERMES_HOME=/path/to/repo/.hermes hermes profile create cron-config --clone --no-alias
```

Then edit:
- `.hermes/profiles/browser-check/config.yaml`
- `.hermes/profiles/cron-config/config.yaml`

If profile directories live inside a repository, add `.hermes/profiles/` to `.gitignore`; cloned profiles can contain `.env`, sessions, logs, auth/runtime state, and should not become a PR payload.

## Verification commands

List toolsets per profile:

```bash
HERMES_HOME=/path/to/repo/.hermes hermes tools list
HERMES_HOME=/path/to/repo/.hermes hermes -p browser-check tools list
HERMES_HOME=/path/to/repo/.hermes hermes -p cron-config tools list
```

Resolve actual toolsets and estimate token impact using the live Hermes install:

```python
import sys
sys.path.insert(0, '/path/to/hermes-agent')
from hermes_cli.config import load_config
from hermes_cli.tools_config import _get_platform_tools
from run_agent import AIAgent
from agent.model_metadata import estimate_request_tokens_rough

cfg = load_config()
toolsets = sorted(_get_platform_tools(cfg, 'cli'))
a = AIAgent(quiet_mode=True, platform='cli', session_id='verify-profile-tools', enabled_toolsets=toolsets)
sp = a._build_system_prompt(None)
tools = a.tools or []
print('toolsets=', ','.join(toolsets))
print('tool_count=', len(tools))
print('tool_names=', ','.join(t['function']['name'] for t in tools))
print('system_tokens=', estimate_request_tokens_rough([], system_prompt=sp, tools=None))
print('tool_tokens=', estimate_request_tokens_rough([], system_prompt='', tools=tools))
print('simple_total=', estimate_request_tokens_rough([{'role':'user','content':'안녕'}], system_prompt=sp, tools=tools))
```

## Important behavior

- Tool/profile changes do not hot-swap into the current session; start a new session or use `/reset`.
- If `skills` remains enabled, the skills index can still dominate system prompt tokens. Toolset trimming reduces schema tokens but does not solve skills-index cost by itself.
- To preserve prompt caching and stability, prefer task-specific profiles/new sessions over trying to add tool schemas mid-session.

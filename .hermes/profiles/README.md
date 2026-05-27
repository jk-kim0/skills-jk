# Hermes repo-local profiles

This directory keeps repo-managed Hermes profile settings that should be reviewed in Git.

Tracked per profile:
- `config.yaml`: non-secret profile configuration, including CLI toolset selection.
- `SOUL.md`: profile-specific persona/system prompt override.

Ignored per profile:
- `.env`: secrets and local provider credentials.
- `sessions/`, `logs/`, `cron/`, `auth.json`, state DBs, PID/process files: local runtime state.

## `browser-check`

Use for browser/render verification work:

```bash
hermes -p browser-check
hermes -p browser-check chat -q "..."
```

CLI toolsets enabled in `.hermes/profiles/browser-check/config.yaml`:

```yaml
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
```

## `cron-config`

Use for cron job setup and maintenance work:

```bash
hermes -p cron-config
hermes -p cron-config chat -q "..."
```

CLI toolsets enabled in `.hermes/profiles/cron-config/config.yaml`:

```yaml
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

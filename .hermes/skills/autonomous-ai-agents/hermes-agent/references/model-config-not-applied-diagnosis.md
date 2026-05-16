# Diagnosing Hermes model config not being applied

Use when a user says a configured model/provider (for example a custom provider like `querypie-kimi`) is not actually active.

## Key lesson

A provider entry under `providers:` only registers the provider. It does not make that provider active. The active model comes from the top-level `model:` block at Hermes process/session start.

Example non-active registration:

```yaml
model:
  provider: openai-codex
  default: gpt-5.5
providers:
  querypie-kimi:
    base_url: http://10.11.0.51:8011/v1
    key: querypie
```

Here `querypie-kimi` exists but is not selected. Hermes will use `openai-codex` / `gpt-5.5`.

## Fast diagnosis sequence

1. Confirm the live config path and active config values:

```bash
pwd
hermes config path
hermes status --all | sed -n '1,40p'
hermes config | sed -n '/^model:/,/^[^ ]/p; /^providers:/,/^[^ ]/p'
```

2. Read the actual config file if CLI output truncates or hides structure:

```bash
sed -n '1,40p' "$(hermes config path)"
```

3. Check whether the desired change exists only on a PR/worktree branch, not in the current checkout/main:

```bash
git branch --show-current
git status --short .hermes/config.yaml
git show origin/main:.hermes/config.yaml | sed -n '1,20p'
git show <branch>:.hermes/config.yaml | sed -n '1,20p'
```

4. Check the session file for what the current session actually started with:

```bash
hermes sessions list | head
python3 - <<'PY'
import json, glob, os
for p in sorted(glob.glob(os.path.expanduser('~/.hermes/sessions/session_*.json')))[-5:]:
    try:
        d=json.load(open(p))
    except Exception:
        continue
    print(p, d.get('model'), d.get('base_url'), d.get('platform'))
PY
```

In repo-local setups, session files may live under `$HERMES_HOME/sessions`, not `~/.hermes/sessions`.

5. If the config changed while a session/gateway was already running, restart or start a new session. Hermes does not hot-apply model/profile/config changes to an already-running conversation.

## Common root causes

- The custom provider is registered under `providers:` but top-level `model.provider` still points elsewhere.
- The desired config change is committed only on a PR branch/worktree and has not been merged or checked out in the runtime checkout.
- The current session started before the config change; session metadata still shows the old model/base_url.
- Gateway service is still running an older process; restart the gateway after config changes.
- The PR carrying runtime config changes is open or conflicted, so `origin/main` still has the old config.

## Reporting format

Be explicit and evidence-based:

- current config path
- current `model.provider` / `model.default` / `model.base_url`
- whether the target provider is merely registered or actively selected
- current session metadata model/base_url
- whether the desired config only exists on another branch/PR
- exact next action: merge/rebase PR, checkout branch, change config, restart gateway, or start new session

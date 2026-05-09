---
name: chrome-devtools-mcp-setup
description: Configure and troubleshoot Chrome DevTools MCP for Hermes, including Node/PATH issues, Chrome remote debugging prerequisites, and autoConnect vs browserUrl connection modes.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [MCP, Chrome, DevTools, Troubleshooting]
    related_skills: [native-mcp]
---

# Chrome DevTools MCP Setup

Use this when Hermes can see `mcp_chrome_devtools_*` tools or should be configured to use them, but Chrome DevTools MCP is not connecting reliably.

## When to use

- You need to enable Chrome DevTools MCP in Hermes.
- `mcp_chrome_devtools_list_pages` or similar tools fail to connect.
- You see errors like `Could not find DevToolsActivePort`.
- `chrome-devtools-mcp` fails due to Node version mismatch.

## Core lessons

1. Hermes MCP registration alone is not enough; Chrome itself must be reachable in a debuggable mode.
2. `chrome-devtools-mcp` is sensitive to the effective `node` version, not just `npx`.
3. If you override PATH in `mcp_servers.<name>.env.PATH`, make sure both `node` and `npx` resolve to a supported version from that PATH.
4. `autoConnect` and `browserUrl` are distinct connection strategies; choose one deliberately.
5. Duplicate `mcp_servers:` keys in YAML are dangerous and should be consolidated to one block.

## Recommended config patterns

Hermes config file is typically:
- `$HERMES_HOME/config.yaml`

Example with `autoConnect`:

```yaml
mcp_servers:
  chrome-devtools:
    command: npx
    args:
      - -y
      - chrome-devtools-mcp@latest
      - --autoConnect
      - --no-usage-statistics
      - --logFile=/tmp/chrome-devtools-mcp-hermes.log
    env:
      PATH: /opt/homebrew/opt/node@20/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
    timeout: 120
    connect_timeout: 60
```

Example with explicit `browserUrl`:

```yaml
mcp_servers:
  chrome-devtools:
    command: npx
    args:
      - -y
      - chrome-devtools-mcp@latest
      - --browserUrl
      - http://127.0.0.1:9222
      - --no-usage-statistics
      - --logFile=/tmp/chrome-devtools-mcp-hermes.log
    env:
      PATH: /opt/homebrew/opt/node@20/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
    timeout: 120
    connect_timeout: 60
```

## Choose a connection mode

### Mode A: `--autoConnect`

Use when you want the MCP server to attach to a locally running Chrome profile automatically.

Practical prerequisite:
- Chrome must already be running.
- Chrome must expose a debuggable endpoint in the way expected by `chrome-devtools-mcp`.
- Current help text indicates this may require starting the remote debugging server from `chrome://inspect/#remote-debugging`.

Symptom if not ready:
- `Could not find DevToolsActivePort ...`

### Mode B: `--browserUrl http://127.0.0.1:9222`

Use when you want explicit and more inspectable connectivity.

Typical launch example on macOS:

```bash
open -na "Google Chrome" --args --remote-debugging-port=9222
```

Then Hermes can connect via:
- `--browserUrl http://127.0.0.1:9222`

This mode is often easier to troubleshoot because you can validate the debugging endpoint directly.

## Verification checklist

### 1. Confirm Hermes home and config path

```bash
printf '%s\n' "$HERMES_HOME"
```

Then inspect the active config file.

### 2. Confirm effective Node version

Do not check `npx` alone. Check both:

```bash
node -v
npm -v
npx -y chrome-devtools-mcp@latest --help
```

If PATH is being overridden for the MCP server, verify under the same PATH:

```bash
PATH=/opt/homebrew/opt/node@20/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin node -v
PATH=/opt/homebrew/opt/node@20/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin npx -y chrome-devtools-mcp@latest --help
```

Important lesson: if help still reports an unsupported Node version, then your `node` binary is still resolving to the wrong version even if you thought you changed `npx`.

### 3. Check Chrome installation

macOS example:

```bash
test -x /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome && echo CHROME_OK || echo CHROME_MISSING
```

### 4. Check MCP server log

Default useful log path:

```bash
/tmp/chrome-devtools-mcp-hermes.log
```

Read it when connection fails.

### 5. If using `browserUrl`, validate Chrome debug endpoint

```bash
curl http://127.0.0.1:9222/json/version
```

If that does not respond, Hermes will not be able to connect via `browserUrl` either.

## Common failure patterns

### Unsupported Node version

Example symptom:
- `chrome-devtools-mcp does not support Node v22.10.0`

Fix:
- Put a supported Node version first in PATH.
- Ensure the PATH override is inside the MCP server config if Hermes launches the MCP subprocess with a filtered environment.
- Re-test `node -v` and `npx ... --help` under that exact PATH.

### `Could not find DevToolsActivePort`

Meaning:
- The MCP server started, but could not attach to a locally debuggable Chrome instance.

Likely fixes:
- Start Chrome first.
- Enable remote debugging as required by the selected mode.
- Switch from `autoConnect` to explicit `browserUrl` if diagnosis is unclear.

### Config looks right but behavior is inconsistent

Check for duplicate YAML keys, especially repeated `mcp_servers:` blocks. Consolidate them into one block so the active configuration is unambiguous.

## Suggested troubleshooting order

1. Inspect active Hermes config.
2. Remove duplicate `mcp_servers:` blocks.
3. Verify `node` and `npx` under the exact PATH used by the MCP server.
4. Decide whether to use `autoConnect` or `browserUrl`.
5. Make Chrome reachable in the matching mode.
6. Re-read `/tmp/chrome-devtools-mcp-hermes.log`.
7. Retry an MCP tool such as page listing.

## Good first live test

After restarting Hermes, run a simple DevTools MCP tool like page listing. If it fails, immediately compare:
- current config
- effective Node version
- Chrome debug availability
- log output

That combination usually reveals the real cause quickly.

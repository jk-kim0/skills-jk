---
name: chrome-devtools-mcp-local-chrome-attach
description: Attach Hermes to a user’s local Chrome session via chrome-devtools-mcp by verifying true remote-debugging availability, distinguishing it from browser-extension-only setups, and checking the exact local signals that prove the connection is usable.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [mcp, chrome, devtools, remote-debugging, browser, local-debugging]
---

# Local Chrome attach via chrome-devtools-mcp

Reference files:
- `references/browser-websocket-fallback.md` — how to attach via the `DevToolsActivePort` browser WebSocket when `/json/list` and `/json/version` return 404.
- `references/persistent-debug-profile-for-automation.md` — how to avoid repeated Chrome approval prompts by using a persistent automation profile and a single batch WebSocket attach.

Use this when:
- the user wants Hermes to control or inspect their already-open local Chrome session
- `chrome-devtools-mcp` is configured in Hermes MCP
- connection attempts fail and you need to distinguish “Chrome is open” from “Chrome is remotely debuggable”

## Key finding

Installing a Chrome extension or simply having Chrome open is not enough for `chrome-devtools-mcp` to attach.
For the MCP/DevTools connection path Hermes uses, Chrome must expose a real DevTools remote debugging endpoint.

Practical implication:
- browser extensions marketed as MCP/browser automation helpers do **not** by themselves satisfy Hermes `chrome-devtools-mcp` connectivity
- `--autoConnect` still depends on Chrome being launched with working remote debugging support

## Required proof that Chrome is actually attachable

Check all of these on the local machine:

1. DevToolsActivePort file exists
```bash
ls -l ~/Library/"Application Support"/Google/Chrome/DevToolsActivePort
```

2. Remote debugging port is listening
```bash
lsof -nP -iTCP:9222 -sTCP:LISTEN
```

3. Chrome process really has the remote debugging flag
```bash
ps -axo pid,etime,command | grep 'Google Chrome' | grep -- '--remote-debugging-port' | grep -v grep
```

4. DevTools HTTP endpoint responds when available
```bash
curl -fsS http://127.0.0.1:9222/json/version
```

If checks 1-3 pass but `/json/version` or `/json/list` returns 404, do **not** conclude remote debugging is unusable. Some Chrome sessions expose only the browser WebSocket path through `DevToolsActivePort`, e.g.:

```bash
cat "$HOME/Library/Application Support/Google/Chrome/DevToolsActivePort"
# 9222
# /devtools/browser/<uuid>
```

In that case a low-level CDP client should connect to `ws://127.0.0.1:9222/devtools/browser/<uuid>` and use browser-level `Target.getTargets` + `Target.attachToTarget` to attach to the desired page. The MCP tool may still list/control pages even when the HTTP JSON discovery endpoints return 404.

If Chrome/macOS presents a remote-debugging approval prompt, design automation so that the user approves once and the agent keeps that single WebSocket connection alive for the whole batch. Repeated helper subprocesses that reconnect per site/page can cause repeated approval prompts and intermittent WebSocket handshake timeouts; prefer one long-lived browser-level CDP connection for multi-site operations.

If these are missing, Hermes cannot attach, even if Chrome is visibly running and even if a browser-side extension is installed.

## Strong negative signal

If you see all of the following:
- Chrome process exists
- `DevToolsActivePort` missing
- no `9222` listener
- no `--remote-debugging-port` in process args

then the correct diagnosis is:
- Chrome is running normally
- remote debugging is **not** enabled
- MCP attach will fail until Chrome is relaunched appropriately

## Safe user guidance

### Avoid repeated approval prompts for multi-step automation
When a workflow will process many sites/pages through CDP, prefer a persistent debug-only Chrome profile and keep one WebSocket attach open for the whole batch. This avoids re-triggering Chrome remote-debugging approval for every helper subprocess. See `references/persistent-debug-profile-for-automation.md`.

### Reuse current profile/session if the user wants their existing login state
Ask them to fully quit Chrome, then relaunch with:

```bash
open -na "Google Chrome" --args \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/Library/Application Support/Google/Chrome"
```

Caveat:
- Chrome should be fully closed first
- if the profile is already locked by another running Chrome instance, this may not work reliably

### Safer alternative: separate debug-only Chrome instance
If the user does not want to disturb their current Chrome session, use:

```bash
open -na "Google Chrome" --args \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.chrome-hermes-debug"
```

This launches a separate profile dedicated to debugging/automation.

## chrome-devtools-mcp config notes

A working Hermes MCP config can look like:

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

But config correctness alone does not prove Chrome is attachable. Always verify the four local signals above.

## Troubleshooting sequence

1. Confirm Hermes MCP sees the server configured
```bash
hermes mcp list
```

2. Confirm `npx chrome-devtools-mcp@latest --help` runs

3. If attach still fails, check:
- `DevToolsActivePort`
- `lsof` on `9222`
- Chrome process args for `--remote-debugging-port`
- `curl http://127.0.0.1:9222/json/version`
- if `/json/version` or `/json/list` returns 404, inspect `DevToolsActivePort` and try the browser WebSocket path directly instead of stopping at HTTP discovery failure

4. If all four attachability signals fail, stop debugging MCP internals and fix the Chrome launch method first

## Practical lesson

When a user says “I turned on remote debugging” but the local checks still show no port/file/flag, trust the machine evidence over the verbal state claim. The next step is not more MCP tuning; it is re-launching Chrome in an actually debuggable mode.

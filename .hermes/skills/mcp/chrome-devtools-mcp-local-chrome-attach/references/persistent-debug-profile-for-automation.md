# Persistent Chrome debug profile for repeated automation

Use this when browser automation repeatedly asks for Chrome remote-debugging approval or CDP WebSocket handshakes hang despite a listening port.

## Symptom pattern

- `DevToolsActivePort` exists and a port is listening.
- TCP connect to the port succeeds.
- Browser WebSocket open hangs or times out.
- A task that processes many sites/pages repeatedly starts a helper process, causing repeated Chrome attach/approval prompts.

## Stabilization pattern

Prefer a dedicated, persistent automation profile instead of attaching repeatedly to the user's normal Chrome profile:

```bash
DEBUG_PROFILE="$HOME/.chrome-hermes-gsc"
mkdir -p "$DEBUG_PROFILE"
open -na "Google Chrome" --args \
  --remote-debugging-port=9333 \
  --remote-allow-origins='*' \
  --user-data-dir="$DEBUG_PROFILE" \
  --no-first-run \
  --no-default-browser-check \
  "https://search.google.com/search-console"
```

Verify it before running the real task:

```bash
lsof -nP -iTCP:9333 -sTCP:LISTEN
curl -fsS http://127.0.0.1:9333/json/version
```

Then perform a tiny WebSocket open smoke test against the `webSocketDebuggerUrl` from `/json/version`.

## Operational notes

- The dedicated profile needs Google login once. After that, the login state remains in `~/.chrome-hermes-gsc`.
- Point automation at `--port 9333` so it uses this profile.
- For multi-site workflows, keep one WebSocket attach open and process the whole batch inside that process. Do not spawn one browser helper per site/page if it will cause repeated authorization prompts.
- Keep the user's regular Chrome untouched unless they explicitly prefer using their normal profile.

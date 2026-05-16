# Browser WebSocket fallback when `/json/list` is unavailable

Observed pattern:
- `DevToolsActivePort` exists and contains a port plus `/devtools/browser/<uuid>`.
- `lsof -nP -iTCP:9222 -sTCP:LISTEN` shows Chrome listening.
- `chrome-devtools-mcp` can list/control pages.
- But raw HTTP discovery endpoints such as `http://127.0.0.1:9222/json`, `/json/list`, and `/json/version` return `404 Not Found`.

Do not treat this as a failed remote-debugging launch. Use the browser-level WebSocket endpoint from `DevToolsActivePort`.

Minimal Node 22 CDP shape:

```js
const fs = await import('node:fs/promises');
const os = await import('node:os');
const path = await import('node:path');

const p = path.join(os.homedir(), 'Library/Application Support/Google/Chrome/DevToolsActivePort');
const [port, browserPath] = (await fs.readFile(p, 'utf8')).trim().split(/\r?\n/);
const ws = new WebSocket(`ws://127.0.0.1:${port}${browserPath}`);

// After open:
// 1. send {method:'Target.getTargets'}
// 2. choose targetInfo where type === 'page' and url matches the desired tab
// 3. send {method:'Target.attachToTarget', params:{targetId, flatten:true}}
// 4. send page commands such as Runtime.evaluate with the returned sessionId
```

Notes:
- Node 22 has a built-in `WebSocket`; older Node versions may need a dependency.
- With `flatten:true`, include `sessionId` on subsequent page-scoped CDP commands.
- This fallback is useful for browser-session automation where cookies must stay inside the page context, such as replaying frontend fetches from an already logged-in tab.

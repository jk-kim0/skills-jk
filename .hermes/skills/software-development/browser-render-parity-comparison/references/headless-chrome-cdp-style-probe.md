# Headless Chrome CDP style probe fallback

Use this when a live visual-parity task needs exact computed styles but the interactive Chrome DevTools MCP connection is unavailable or inappropriate. Capture the technique, not a permanent claim that any browser tool is broken.

## Pattern

1. Launch the installed system Chrome in headless mode with remote debugging and a temporary profile:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new \
  --disable-gpu \
  --remote-debugging-port=9223 \
  --user-data-dir=/tmp/chrome-style-probe \
  --no-first-run \
  --no-default-browser-check \
  about:blank
```

Use the terminal background-process facility for the long-lived Chrome process. Do not shell-background it with `&` in a foreground terminal call.

2. Verify CDP readiness:

```bash
curl -sf http://127.0.0.1:9223/json/version | python3 -m json.tool
```

3. Use Node's built-in `WebSocket` (available in modern Node) to create/open a page and evaluate DOM probes through CDP. Current Chrome requires `PUT /json/new?...`, not `GET`.

Minimal skeleton:

```js
const http = require('http');
function requestJson(path, method = 'GET') {
  return new Promise((resolve, reject) => {
    const req = http.request({ host: '127.0.0.1', port: 9223, path, method }, response => {
      let body = '';
      response.on('data', chunk => (body += chunk));
      response.on('end', () => resolve(JSON.parse(body)));
    });
    req.on('error', reject);
    req.end();
  });
}

const target = await requestJson('/json/new?https://www.querypie.com/ko', 'PUT');
const ws = new WebSocket(target.webSocketDebuggerUrl);
let id = 0;
const pending = new Map();
function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const mid = ++id;
    pending.set(mid, { resolve, reject });
    ws.send(JSON.stringify({ id: mid, method, params }));
  });
}
ws.onmessage = event => {
  const message = JSON.parse(event.data);
  if (message.id && pending.has(message.id)) {
    const { resolve, reject } = pending.get(message.id);
    pending.delete(message.id);
    message.error ? reject(message.error) : resolve(message.result);
  }
};
```

4. Evaluate exact computed styles and geometry for the target element:

```js
const expression = `(() => {
  const el = Array.from(document.querySelectorAll('a,button'))
    .find(node => (node.textContent || '').trim().includes('Make It Happen'));
  const cs = getComputedStyle(el);
  const rect = el.getBoundingClientRect();
  const svg = el.querySelector('svg');
  const path = svg?.querySelector('path');
  return {
    text: (el.textContent || '').trim(),
    href: el.href || null,
    className: String(el.className),
    rect: { width: rect.width, height: rect.height, x: rect.x, y: rect.y },
    style: {
      display: cs.display,
      alignItems: cs.alignItems,
      justifyContent: cs.justifyContent,
      gap: cs.gap,
      padding: cs.padding,
      backgroundImage: cs.backgroundImage,
      color: cs.color,
      border: cs.border,
      borderRadius: cs.borderRadius,
      fontSize: cs.fontSize,
      fontWeight: cs.fontWeight,
      lineHeight: cs.lineHeight,
    },
    svg: svg ? {
      outer: svg.outerHTML,
      pathD: path?.getAttribute('d') || null,
      pathFill: path?.getAttribute('fill') || null,
    } : null,
  };
})()`;
const result = await send('Runtime.evaluate', {
  expression,
  returnByValue: true,
  awaitPromise: true,
});
console.log(JSON.stringify(result.result.value, null, 2));
```

## What to capture in the PR body

For visual parity fixes, report measured live values rather than subjective claims. Useful values include size, padding, gap, radius, background gradient, typography, SVG path data, and icon box size.

## Pitfalls

- Do not encode temporary MCP connection failures as durable constraints. The durable workflow is: if interactive browser tooling is unavailable, fall back to a direct CDP probe against system Chrome.
- `/json/new` may reject GET with `Using unsafe HTTP verb GET...`; use PUT.
- If you scroll before measuring, `getBoundingClientRect().y` can be negative. That is fine for style parity; width, height, computed style, and SVG geometry remain useful.

---
name: nextjs-local-preview-locks
description: Safely start and verify a Next.js local preview when existing dev servers, occupied ports, or .next/dev lock files cause stale or misleading results.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [nextjs, local-preview, dev-server, troubleshooting, verification]
---

# Next.js Local Preview With Port/Lock Conflicts

Use this when a repo needs a local preview but `next dev` is blocked by an existing server, stale page content on port 3000, or `Unable to acquire lock at .next/dev/lock`.

## When to use
- `npm run dev` appears to work, but browser content does not match the current repo
- Port 3000 (or another default port) is already serving an older/stale app
- Starting another Next dev instance fails with `EADDRINUSE`
- Starting on a different port still fails with `Unable to acquire lock at .../.next/dev/lock`

## Core findings
- A browser check against `localhost:3000` can accidentally hit an unrelated or stale dev server.
- In the same repo, a second `next dev` instance may fail even on a different port because Next.js holds a repo-local dev lock under `.next/dev/lock`.
- To get a trustworthy preview, first identify and stop the existing same-repo dev instance, then start a fresh server on a known port.

## Workflow

### 1. Check whether a port is already in use
```bash
lsof -nP -iTCP:3000 -sTCP:LISTEN
```

If the page looks wrong, do not assume the current repo owns that port.

### 2. Try starting on an explicit port
```bash
npm run dev -- --port 3456
```

Prefer the CLI flag form above for Next.js. It is explicit and easy to verify in logs.

### 3. If startup fails with `.next/dev/lock`
This means another `next dev` instance is already running for the same repo. Starting on a new port is not enough.

Find and stop the existing same-repo dev process before retrying. If you started it through Hermes with `terminal(background=true)`, kill that tracked process first.

Then restart:
```bash
npm run dev -- --port 3456
```

### 4. Verify the correct server, not just any server
Open the exact port you started, for example:
```text
http://127.0.0.1:3456
```

Do not fall back to `:3000` unless you verified that the current repo owns it.

### 5. Confirm rendered assets or changes in-browser
For image optimizations or asset swaps, inspect actual loaded image URLs in the page and confirm the expected extension/path is being served.

Examples to verify in browser JS:
```js
Array.from(document.images).map(img => ({
  alt: img.alt,
  src: img.currentSrc || img.src,
}))
```

Use filtering to confirm specific replacements, e.g. `.webp` assets.

## Practical pattern for asset optimization tasks
1. Make asset/path changes in code
2. Run verification commands (`npm run test:ci`, `npm run build`)
3. Kill any stale same-repo dev instance if needed
4. Start `npm run dev -- --port <known-port>`
5. Browse that exact port
6. Inspect loaded image URLs to confirm optimized assets are actually used

## Pitfalls
- `PORT=3456 npm run dev` may still leave ambiguity in logs/workflow; prefer `npm run dev -- --port 3456`
- `EADDRINUSE` means the port is busy; it does not prove the right app is running there
- `.next/dev/lock` means another instance of the same repo is active; changing ports alone will not fix it
- Browser snapshots can look fine while still hitting the wrong dev server; verify the URL and loaded asset paths

## Evidence to report
When handing results back to the user, include:
- The exact preview URL used
- Whether an older/stale server had to be stopped
- Any confirmed loaded asset URLs that prove the intended change is live

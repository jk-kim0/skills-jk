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
- `next start` serves the last completed production build, not your current source tree. If you changed code after the previous build, the browser can keep showing an older page until you run `npm run build` again and restart the `next start` process.
- To get a trustworthy preview, first identify and stop the existing same-repo server, then rebuild/restart on a known port.

## Workflow

### 1. Check whether a port is already in use
```bash
lsof -nP -iTCP:3000 -sTCP:LISTEN
```

If the page looks wrong, do not assume the current repo owns that port.

Then verify which checkout actually owns that listener before trusting any browser result:
```bash
ps -p <PID> -o pid=,ppid=,command=
lsof -p <PID> | grep ' cwd '
```

Why:
- in multi-worktree setups, the same repo can have another Next server already listening on the target port
- the browser may open successfully but be serving a different worktree's route tree
- this can produce misleading results such as an empty page or a valid page from the wrong branch

### 2a. In a fresh worktree without local dependencies, prefer a `node_modules` symlink over a full reinstall when you only need a short-lived dev preview
If the root checkout already has dependencies installed and the user wants to avoid repeated installs inside worktrees, a fast-path is:
```bash
ln -s /path/to/root-checkout/node_modules node_modules
npm run dev -- --port 3456
```

Before trusting the symlink fast-path, verify that the root install can resolve key build-time packages used by the current repo, especially PostCSS/Tailwind plugins:
```bash
node -p "require.resolve('@tailwindcss/postcss')" || echo 'root install is missing Tailwind PostCSS plugin'
```

Why:
- for local browser verification, this is often enough to boot the correct worktree without paying the cost of another install
- this is especially useful for quick rendering checks after a small UI/style fix
- still verify the server PID/cwd after startup so you know the browser is hitting the intended worktree
- if the symlinked server returns 500 with `Cannot find module '@tailwindcss/postcss'`, the root `node_modules` is incomplete for the current branch; remove the symlink, run a worktree-local `npm install`, then restart the dev server


### 2. Try starting on an explicit port
```bash
npm run dev -- --port 3456
```

Prefer the CLI flag form above for Next.js. It is explicit and easy to verify in logs.

Find and stop the existing same-repo dev process before retrying. If you started it through Hermes with `terminal(background=true)`, kill that tracked process first.

Then restart:
```bash
npm run dev -- --port 3456
```

### 4a. If you are using `next start`, rebuild before trusting the browser
After any source change:
```bash
npm run build
```
Then stop the old `next start` process and restart it:
```bash
npm run start -- --port 3456
```

Why:
- `next start` serves the previous build output until you rebuild.
- It is easy to think your latest edit is live when the browser is actually showing an older compiled page.
- This is especially dangerous during layout-parity work, where stale production output can make you chase the wrong visual diff.

### 4b. For visual parity work, verify layout with DOM measurements, not vision alone
When comparing a live page and a local preview of a long static marketing page:
- use the browser screenshot/vision tools for general impressions
- but also extract concrete measurements with `browser_console`, such as:
  - heading positions (`getBoundingClientRect()`)
  - image/logo sizes and positions
  - section background colors and padding values

Useful patterns:
```js
Array.from(document.querySelectorAll('main h2, main h3')).map((h) => {
  const r = h.getBoundingClientRect();
  return { text: h.textContent?.trim(), left: Math.round(r.left), top: Math.round(r.top + window.scrollY) };
})
```

```js
Array.from(document.images).map((img) => {
  const r = img.getBoundingClientRect();
  return { alt: img.alt, w: Math.round(r.width), h: Math.round(r.height), left: Math.round(r.left), top: Math.round(r.top + window.scrollY) };
})
```

Why:
- Vision summaries can misread very long pages, blank space, or off-screen sections.
- DOM measurements are much more reliable for matching hero media width/height, logo row sizing, section start positions, and multi-column alignment.
- Use vision for qualitative checks, DOM measurements for final layout decisions.


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

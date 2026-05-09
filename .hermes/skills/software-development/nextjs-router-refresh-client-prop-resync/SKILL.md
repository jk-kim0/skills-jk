---
name: nextjs-router-refresh-client-prop-resync
description: Fix Next.js App Router bugs where a client component initializes local state from a server prop, but `router.refresh()` updates the prop without updating the visible UI.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [nextjs, react, app-router, router.refresh, client-state, debugging]
---

# Next.js router.refresh client-prop re-sync

Use this when a Next.js App Router page reads server state (cookies, headers, draft/preview flags, feature toggles, auth state) and passes a boolean/string prop into a client component, but toggling that state plus `router.refresh()` does not immediately update the UI.

Typical symptom:
- a toggle updates a cookie or server-side flag
- the page calls `router.refresh()`
- the server component recomputes and passes a new prop
- the client component still shows the old locked/unlocked/open/closed state until a full navigation or remount

## Root cause

The client component used something like:

```tsx
const [open, setOpen] = useState(initiallyOpen);
```

and never re-synced local state when `initiallyOpen` changed.

`useState(initialValue)` only uses the prop on the first mount. After `router.refresh()`, the component can stay mounted while receiving a new prop, so the visible state stays stale.

## Fix pattern

1. Find the client component that derives local UI state from a server prop.
2. Confirm the prop really changes server-side after refresh.
3. Add a sync effect:

```tsx
const [open, setOpen] = useState(initiallyOpen);

useEffect(() => {
  setOpen(initiallyOpen);
}, [initiallyOpen]);
```

4. Keep the local state only if the component still needs post-mount interactions (submit success, dismiss, expand/collapse, etc.).
5. Add a regression test that asserts the component source includes the re-sync effect, or preferably a behavior test if the repo supports it.

## When this pattern is appropriate

Use the sync effect when local UI state is intentionally seeded by the server and must follow later server-prop changes, such as:
- preview/draft toggle changes
- cookie-based gating or unlock state
- auth/session banner visibility
- locale or feature-flag toggles
- server-driven open/closed drawers or notices

## When NOT to use it

Do not blindly sync if the component is supposed to preserve client-only edits even when the parent prop changes. In that case, reconsider ownership of state instead of forcing prop mirroring.

## Corp-web-japan example

Preview Toggle updated the server-side preview cookie and called `router.refresh()`. The gated content page recomputed `initiallyUnlocked` on the server, but `ResourcePostGated` kept showing the old state because it only did:

```tsx
const [unlocked, setUnlocked] = useState(initiallyUnlocked);
```

The fix was:

```tsx
useEffect(() => {
  setUnlocked(initiallyUnlocked);
}, [initiallyUnlocked]);
```

This made gating form locked/unlocked state switch immediately when Preview Toggle was turned off/on.

## Verification checklist

- confirm the server prop changes after the cookie/flag update
- confirm the client component remains mounted across `router.refresh()`
- add `useEffect` sync from prop to local state
- verify the visible UI updates immediately after the toggle
- add a regression test for the re-sync behavior

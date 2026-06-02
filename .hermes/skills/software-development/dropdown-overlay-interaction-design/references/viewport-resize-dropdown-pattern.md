# Viewport resize dropdown pattern

Session context: Outbound Agent PR #257 added a top-bar `Viewport` dropdown based on PR #256's standard viewport sizes.

## Durable pattern

When a dropdown option is intended to resize the browser to a standard CSS-pixel viewport, the target is `window.innerWidth / window.innerHeight`, not the outer browser window size.

Use each option's documented viewport dimensions as the source of truth:

```ts
const widthDelta = option.width - window.innerWidth;
const heightDelta = option.height - window.innerHeight;
window.resizeTo(window.outerWidth + widthDelta, window.outerHeight + heightDelta);
```

Then re-check the actual viewport and repeat a small bounded number of times, because browser chrome, OS window manager constraints, toolbar changes, and browser clamping can make a single resize undershoot or overshoot.

```ts
const MAX_ATTEMPTS = 8;
const TOLERANCE_PX = 1;

function isAtTarget(option: { width: number; height: number }) {
  return Math.abs(window.innerWidth - option.width) <= TOLERANCE_PX &&
    Math.abs(window.innerHeight - option.height) <= TOLERANCE_PX;
}

function resizeViewportTo(option: { width: number; height: number }, attempt = 1) {
  if (isAtTarget(option)) return;

  const widthDelta = option.width - window.innerWidth;
  const heightDelta = option.height - window.innerHeight;
  window.resizeTo(window.outerWidth + widthDelta, window.outerHeight + heightDelta);

  window.requestAnimationFrame(() => {
    if (attempt < MAX_ATTEMPTS && !isAtTarget(option)) {
      resizeViewportTo(option, attempt + 1);
    }
  });
}
```

## UX notes

- Display the current viewport from `innerWidth × innerHeight`, not outer size.
- Highlight the matching option only when the current viewport matches the option dimensions within tolerance.
- State the browser limitation in PR notes or docs: normal browser windows may refuse or clamp `window.resizeTo` when maximized, tabbed, permission-limited, or controlled by OS/window-manager constraints.
- This pattern is useful for review tooling and internal dev controls; do not present it as a guaranteed user-facing resize mechanism for all browsers.

## Tests

Source-level tests can assert:

- the standard dimensions are present;
- resize logic computes deltas from `innerWidth / innerHeight`;
- `window.resizeTo(window.outerWidth + widthDelta, window.outerHeight + heightDelta)` is used;
- there is a bounded retry loop and target check.

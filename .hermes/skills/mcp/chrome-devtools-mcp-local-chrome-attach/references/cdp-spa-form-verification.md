# CDP verification for SPA/admin-console form settings

Use this when a logged-in browser page is reachable only through the user's local Chrome profile and the rendered text does not expose the setting values you need to verify.

## Pattern

1. Attach to the browser WebSocket from `DevToolsActivePort`.
2. Use `Target.getTargets` to find the page by URL/title.
3. `Target.attachToTarget` with `flatten:true`.
4. Run `Runtime.evaluate` in the page session.
5. Verify both visible text and form element values.

For Google Cloud Console / other SPAs, `document.body.innerText` may show labels such as `URIs 1`, `URIs 2`, etc. while hiding the actual `input` values. Query inputs directly:

```js
(() => Array.from(document.querySelectorAll('input, textarea')).map((el, i) => ({
  i,
  type: el.type,
  value: el.value,
  aria: el.getAttribute('aria-label') || '',
  placeholder: el.getAttribute('placeholder') || '',
})))()
```

## Approval retry note

If the first browser WebSocket attach times out while Chrome has a remote-debugging approval prompt open, ask the user to approve it and then retry the same browser WebSocket path. Do not switch approaches just because `/json/version` returns 404 when `DevToolsActivePort` and the 9222 listener are present.

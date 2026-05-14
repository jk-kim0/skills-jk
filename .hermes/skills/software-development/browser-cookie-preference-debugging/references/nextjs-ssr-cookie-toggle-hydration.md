# Next.js SSR cookie-toggle hydration mismatch

## Symptom
A cookie preference toggle appears to save on click, but after refreshing the page the UI visually resets to off.

## Evidence pattern
Use a live browser, not source inspection only:

1. Open the page and check initial state:
   ```js
   ({ cookie: document.cookie, switches: Array.from(document.querySelectorAll('[role="switch"]')).map(el => ({ id: el.id, checked: el.getAttribute('aria-checked') })) })
   ```
2. Click a non-required switch.
3. Verify a preference cookie is written, for example:
   - `cookie-preference-performance=1`
   - `cookie-preference-set=1`
4. Refresh/revisit the same page.
5. If `document.cookie` still contains the saved `=1` value but the DOM switch reports `aria-checked="false"`, suspect SSR/client hydration mismatch rather than cookie persistence failure.
6. Click the visually-off switch once more. If the cookie changes from `1` to `0`, React internally believed the state was already on while the DOM looked off.

## Root cause shape
A server-rendered client component initialized state with `useState(() => readDocumentCookie())`.
On the server, `document` is unavailable, so the emitted HTML uses the default/off state. On the client, the state initializer can see the cookie and initialize to on, leaving server HTML and client state disagreeing during hydration.

## Preferred fix pattern
For Next.js App Router pages:

1. Keep the route/page as a server component, or make it `async` if needed.
2. Read persisted preference cookies on the server with `cookies()` from `next/headers`.
3. Pass the values to the client toggle as `initialChecked`/`initialValue` props.
4. Keep the client toggle responsible only for user-initiated writes with `document.cookie`.
5. Extract cookie names, max-age, and parsing helpers to a shared server-safe module (for example `src/lib/cookie-preferences.ts`) so server and client paths cannot drift.
6. Add a source or component contract test that prevents reintroducing `useState(() => document.cookie...)` or equivalent SSR-unsafe initialization.

## Anti-pattern
Do not use `document.cookie` directly inside a `useState` initializer for a component that is server-rendered. A `useEffect` mount read can be an acceptable quick fallback, but it may flash the default state; server-provided initial props are cleaner when the page can read cookies server-side.

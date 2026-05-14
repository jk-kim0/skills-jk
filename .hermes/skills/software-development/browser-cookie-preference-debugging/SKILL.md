---
name: browser-cookie-preference-debugging
description: Debug browser-side preference persistence bugs by reproducing live, inspecting cookies and locale state, and comparing deployed bundle behavior against source code.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [browser, cookies, preferences, i18n, debugging, production]
    related_skills: [systematic-debugging]
---

# Browser Cookie/Preference Debugging

Use this when a website appears to ignore a user preference such as language, theme, dismissal state, or banner choice.

## When to use
- A preference banner keeps reappearing
- Language selection does not stick
- A cookie seems to be saved but behavior resets on navigation
- Production behavior differs from expected source code behavior

## Core idea
Do not stop at source inspection. Reproduce in a real browser, inspect live cookies and runtime state, then compare that against the deployed bundle and source.

## Workflow

### 1. Reproduce in a live browser
Open the exact production/staging URL and verify the bug with the actual user-facing flow.

Capture:
- starting URL
- current page locale/state
- browser language (`navigator.language`, `navigator.languages`)
- visible banner/prompt text

Useful browser-console expression:
```js
({
  href: location.href,
  language: navigator.language,
  languages: navigator.languages,
  cookie: document.cookie,
})
```

### 2. Identify the exact control being used
If the page has multiple locale or preference controls, inspect the DOM and distinguish them before interacting.

Useful expression:
```js
Array.from(document.querySelectorAll('select')).map((el, i) => ({
  i,
  value: el.value,
  aria: el.getAttribute('aria-label'),
  options: Array.from(el.options).map(o => ({ value: o.value, text: o.text, selected: o.selected })),
  outer: el.outerHTML.slice(0, 300),
}))
```

This is especially useful when accessibility snapshots do not let you reliably click specific `<option>` items.

### 3. Drive the real state change
If normal click automation on `<option>` is unreliable, set the `<select>` value directly and dispatch a change event:
```js
const el = document.querySelectorAll('select')[0]
el.value = 'ja'
el.dispatchEvent(new Event('change', { bubbles: true }))
```
Then trigger the real submit/change button.

### 4. Compare pre- and post-navigation state
After the preference change, check:
- destination URL
- relevant cookies
- whether the banner reappeared

If the behavior only fails for some options (for example non-English locales), test both:
- matching-browser-language option
- non-matching-browser-language option

This helps distinguish “preference saved” from “symptom hidden because page now matches browser defaults”.

### 5. Verify whether the cookie can be stored at all
Before blaming browser policy, manually set the cookie in page context:
```js
document.cookie = 'user-selected-locale=ja; path=/'
```
If it appears in `document.cookie`, browser storage is working and the site code is the likely culprit.

### 6. Check whether the deployed bundle contains the expected logic
If source code says the cookie should be set, inspect the loaded `_next/static` bundle to confirm production is actually running that code.

Useful pattern:
```js
(async () => {
  const urls = Array.from(document.querySelectorAll('script[src]'))
    .map(s => s.src)
    .filter(u => u.includes('/_next/static/chunks/'))

  for (const url of urls) {
    const text = await fetch(url).then(r => r.text())
    if (text.includes('user-selected-locale')) {
      return { url, snippet: text.slice(text.indexOf('user-selected-locale') - 200, text.indexOf('user-selected-locale') + 500) }
    }
  }
  return null
})()
```

This lets you distinguish:
- source changed but not deployed
- source deployed, but another runtime path deletes/resets state afterward

### 7. Look for a later delete/reset path
If the cookie is set but missing after reload/navigation, search for any initialization code that deletes it.
Common culprits:
- consent initialization
- “functional cookies disabled” cleanup
- provider bootstrapping on mount
- locale mismatch hooks that only consult a specific cookie

Typical pattern to watch for:
- preference setter saves `user-selected-*`
- provider init reads consent
- consent false branch deletes `user-selected-*`
- mismatch hook sees missing cookie and re-shows the banner

### 8. Compare with the guard condition that suppresses the banner
Find the hook/component that decides whether to show the prompt. Confirm exactly what state it checks.

For example:
- if `getCookie(USER_SELECTED_LOCALE_COOKIE_KEY)` exists, suppress mismatch banner
- else compare `pageLocale !== browserLocale`

This often reveals why one option appears to work while another does not.

## Practical findings worth remembering
- If English browser users switch to English pages and the banner disappears, that does not prove the user-choice cookie persisted. It may simply mean browser locale and page locale now match.
- A cookie being writable manually in DevTools/browser console strongly suggests the bug is application logic, not browser storage policy.
- Inspecting the deployed bundle is the fastest way to verify whether production still has old logic or whether a different runtime path is overriding the new logic.
- A very common failure mode is: the app correctly saves a `user-selected-*` cookie during the explicit user action, but a later provider/bootstrap initialization path deletes it because a consent flag is false.
- In Next.js/React SSR, a preference can be persisted correctly while the refreshed UI still appears reset because of a hydration mismatch: a client component initializes `useState(() => readDocumentCookie())`, the server render cannot access `document.cookie` and emits the default/off HTML, while the client state may initialize from the cookie. Evidence pattern: after refresh `document.cookie` still contains the saved value, the DOM switch shows `aria-checked="false"`, and the first click writes the opposite value (for example `0`) because React internally thought it was already on.

## Remediation pattern
When fixing this class of bug, separate two cases:

1. initialization/bootstrap
- reading existing consent or preference state on page load
- must not delete user-selected preference cookies just because a consent value is currently false

2. explicit user action
- the user manually turns a preference category off in the UI
- this is the appropriate time to clear dependent `user-selected-*` cookies if the product truly requires that behavior

A safe implementation shape is:
- keep a `userAction` or equivalent flag in the setter
- only delete `user-selected-*` cookies when `!value && userAction`
- do not delete them during initial state hydration like `setFunctionalCookie(existingValue, false)`

For Next.js/React SSR hydration mismatches:
- Prefer reading the cookie on the server with `cookies()` and passing an `initialChecked`/`initialValue` prop into the client component so server HTML and client initial render agree.
- If server propagation is too large for the scope, read `document.cookie` in `useEffect` after mount and update state there, accepting a possible brief default-state flash.
- Avoid using `document.cookie` directly inside a `useState` initializer when the component is server-rendered; it can create server/client DOM-state disagreement even when persistence itself works.

This preserves user-selected locale/theme/banner state across navigation while still allowing explicit cleanup when the user intentionally disables the relevant category.

## References
- `references/nextjs-ssr-cookie-toggle-hydration.md` — live evidence pattern and preferred Next.js App Router fix for cookie toggles that save correctly but visually reset after refresh because SSR HTML and client state disagree.

## Output format for findings
Summarize in four parts:
1. reproduction steps
2. observed cookie/runtime evidence
3. code path responsible
4. root cause in one sentence

## Example root-cause shape
"The selected locale cookie is saved during language change, but a later consent/provider initialization path deletes it on page load when functional cookies are off, so the mismatch banner treats the visit as if no user preference exists and reappears for non-browser-matching locales."

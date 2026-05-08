---
name: browsermcp-connection-verification
description: Verify whether Browser MCP is actually usable from Hermes, distinguish UI-level extension connection from real tool usability, and handle transient false negatives by retrying a live browser action.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [mcp, browsermcp, browser, extension, connectivity, troubleshooting]
---

# Browser MCP connection verification

Use this when:
- the user says Browser MCP is connected but Hermes tool calls fail
- you need to confirm whether Hermes can actually control the browser
- you need to distinguish extension UI state from MCP tool usability

## Key lesson

The Browser MCP extension showing `Connected` is not by itself authoritative proof that Hermes can use the browser immediately.
A real Browser MCP tool call such as `browser_navigate` / `mcp_browsermcp_browser_navigate` is the authoritative check.

A first call can fail with:
- `No connection to browser extension`

even when the extension UI later shows or already shows `Connected`.
This can happen because of transient attach/session timing issues.

## Verification sequence

1. Confirm Hermes sees the MCP server configured
```bash
hermes mcp list
```
Look for `browsermcp` as enabled.

2. If needed, inspect config to confirm Browser MCP is registered under `mcp_servers`

3. Perform a live Browser MCP action instead of trusting UI state
- Preferred smoke test: navigate to `https://example.com`
- Accept success if Hermes receives page URL/title/snapshot back

Example tool-level success signal:
- URL: `https://example.com/`
- Title: `Example Domain`
- snapshot content returned

4. If the first Browser MCP action fails with `No connection to browser extension`, retry once after the user confirms the extension/tab is connected

5. If the second live action succeeds, conclude Browser MCP is usable and treat the earlier failure as transient rather than as a hard configuration error

## Interpretation rules

### Strong positive signal
If a live Browser MCP action returns page data or snapshot data, Browser MCP is working.
Do not over-weight earlier connection errors once a real navigation/snapshot succeeds.

### Strong negative signal
If all of the following are true:
- `browsermcp` is enabled in `hermes mcp list`
- live actions repeatedly fail with `No connection to browser extension`
- no resources/session state appear from Browser MCP

then the likely issue is that the extension/tab connection is not actually established for the Hermes session yet.

## Practical guidance

- Prefer real browser actions over status assumptions
- Use `navigate -> snapshot` as the canonical smoke test
- Explain clearly that `browsermcp` and `chrome-devtools` are separate integrations
- Do not conflate Browser MCP extension connectivity with Chrome remote-debugging availability for `chrome-devtools-mcp`

## Important distinction from chrome-devtools

Browser MCP and chrome-devtools are separate:
- Browser MCP depends on the Browser MCP extension/tab connection
- chrome-devtools depends on Chrome DevTools remote debugging availability

So this state is possible and valid:
- Browser MCP works
- chrome-devtools still fails because there is no DevTools remote-debugging port

## Recommended user-facing wording

When Browser MCP succeeds after an earlier failure, explain:
- Browser MCP is now confirmed working
- the earlier error was likely transient attach/session timing
- a real navigate/snapshot call is more trustworthy than the extension badge alone

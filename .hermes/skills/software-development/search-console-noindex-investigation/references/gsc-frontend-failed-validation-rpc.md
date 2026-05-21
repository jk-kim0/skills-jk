# GSC frontend-session Failed validation resubmission internals

Context: `./bin/gsc validate-index-issues-all --submit` showed `Failed` rows as candidates but left them as `OUTCOME=FAIL` with `ACTION=item_key was not present...` for `https://querypie.ai/`.

## Key learning

This is not a policy decision to skip `Failed` validations. It is a frontend-session extraction failure before submission.

Current GSC Page indexing markup may omit drilldown `href` / `item_key` from table row markup. The issue keys can still be present in bootstrapped `AF_initDataCallback` data, especially the block that also contains support article anchors such as:

- `page_with_redirect`
- `duplicate_page_with_proper_canonical_tag`
- `blocked_by_noindex_tag`
- `discovered__unclear_status`
- `crawled`
- `google_chose_different_canonical_than_user`
- `blocked_by_robotstxt`
- `not_found_404`

In the observed `querypie.ai` case:

- `Page with redirect` -> `CAMYCyAC`
- `Alternate page with proper canonical tag` -> `CAMYGCAC`

## Validation RPC learning

The validation detail page may show `START NEW VALIDATION` but not expose an old static RPC template near the button. The current frontend Wiz controller constructs a direct RPC at click time.

Captured by intercepting `/batchexecute` while clicking the button in Chrome:

```text
rpcid: RYZlBc
args: [site, 13, itemKey, 3, null, failedAt]
source-path: /search-console/index/validation
```

Example payload for `Page with redirect`:

```json
[[["RYZlBc","[\"https://querypie.ai/\",13,\"CAMYCyAC\",3,null,\"2026-05-16T04-55-07Z\"]",null,"generic"]]]
```

`failedAt` can be recovered from validation-page bootstrap data. If unavailable, direct mode should fail clearly rather than guessing.

## Safe verification pattern

To verify automation without changing live GSC state:

1. Run discovery/dry-run and confirm `itemKeySource: af-init-data` for affected rows.
2. In a Node harness, monkeypatch `global.fetch` so `/batchexecute` POSTs are intercepted and return a fake success response.
3. Run the CLI with `--submit --limit 1` or `--limit 2`.
4. Confirm:
   - intercepted RPC id is `RYZlBc`
   - body contains expected site, itemKey, and failedAt
   - CLI reports `started` only because of the fake response
5. State explicitly that no real validation was submitted during the intercepted test.

## Browser/network investigation pattern

When the direct-mode RPC shape is unknown:

1. Open the exact validation URL in a fresh Chrome tab.
2. Install a page-level interceptor for `fetch` and `XMLHttpRequest` that records and blocks `/batchexecute`.
3. Click `START NEW VALIDATION`.
4. Read the captured request body and reconstruct only if enough bootstrap data exists.

Do not silently fall back to controlling the browser in the normal frontend-session command path; direct-mode failures should surface so the helper can be fixed.

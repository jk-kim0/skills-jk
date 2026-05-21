# GSC frontend-session `item_key` missing during issue validation

Session learning: `./bin/gsc validate-index-issues-all --submit` can correctly select `Failed` rows as candidates but still fail before sending validation requests if the saved frontend-session HTML does not contain row-level `item_key` values.

Observed output shape:

```text
GSC Page indexing issue report | mode=frontend-session | site=https://querypie.ai/ | submit=true
discovered=8 candidates=2
VALIDATION    | OUTCOME | ACTION       | REASON
Failed        | FAIL    | item_key wa… | Page with redirect
Failed        | FAIL    | item_key wa… | Alternate page with proper canonical tag
summary: total=2 started=0 skipped=0 failed=2
```

Interpretation:

- `Failed` is actionable by default. The row was not skipped because it was `Failed`.
- `discovered=N candidates=M` proves the helper selected the rows.
- The failure happens inside submit processing before the validation URL/RPC can be built.
- Full error from `bin/gsc-frontend-indexing`: `item_key was not present in fetched frontend markup; refresh the saved frontend session from an index page that has loaded issue rows.`

Root cause pattern:

- frontend-session mode fetches `https://search.google.com/search-console/index?resource_id=...` using saved cookies/WIZ tokens.
- It parses issue rows and expects `item_key` in row markup or embedded row data.
- Without `item_key`, it cannot build `/search-console/index/validation?...&item_key=...` and cannot extract/call the `START NEW VALIDATION` RPC.
- The helper intentionally refuses to silently drive Chrome fallback in direct mode; browser/CDP fallback belongs behind explicit `*-browser` commands.

Recommended explanation to user:

- “Yes, Failed rows should be retried. This run did select them. It did not send the validation requests because direct frontend mode could not extract `item_key`, so it had no safe target for the validation action.”
- If the user asks why the Search Console UI still shows `Failed` after a `--submit` run, explain the state transition explicitly: a successful submit should change the issue to `Started` / `Validation started`; if the CLI row shows `OUTCOME=FAIL`, `started=0`, and an `ACTION` like `item_key was not present...`, no validation request was sent, so GSC correctly remains `Failed`.
- Do not describe this as “skipped because Failed.” In this CLI contract, `Failed` is a retry target. The failure is a pre-submit addressing/parser failure.

Reporting improvement for maintainers:

- Avoid truncating the only actionable error in the `ACTION` column without a nearby full message. If table width truncates `item_key was not present...`, include a post-table diagnostic note such as `failed before submit: item_key missing; validation request not sent` so users can distinguish GSC refusal from CLI extraction failure.

Next actions:

1. Re-export the frontend session from a Search Console Page indexing page after issue rows have fully loaded, then retry frontend mode.
2. If direct mode still cannot see `item_key`, inspect the current GSC frontend markup/bootstrap data and fix the direct helper parser. Do not silently fall back to browser control in the normal `validate-index-issues-all --submit` path.
3. Browser/CDP control may be used as a debugging tool to discover the current frontend route/RPC shape, but the final implementation should run from the CLI using only the saved authentication session.
4. When maintaining the CLI, preserve this distinction in reporting: candidate selection success is separate from validation submission success.

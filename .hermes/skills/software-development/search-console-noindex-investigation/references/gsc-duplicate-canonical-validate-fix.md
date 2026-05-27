# GSC duplicate canonical Validate Fix routing

Use this note when `validate-index-issues` or `validate-index-issues-all` fails on `Duplicate without user-selected canonical`.

## Durable behavior split

This issue type currently behaves differently by validation state and transport:

- frontend-session direct mode can list the row but still return `itemKey: null` / no drilldown href for `Duplicate without user-selected canonical`.
- On `Not Started` drilldown pages, GSC can expose a direct `VALIDATE FIX` control on the drilldown page instead of the older `SEE DETAILS` -> `START NEW VALIDATION` path.
- On some `Failed` drilldowns, clicking the wrong `SEE DETAILS` can land on a partial validation page that shows only `Examples` and no actionable start button.

## What to do

1. Treat `Duplicate without user-selected canonical` as a direct/frontend-session parser/RPC problem first, not a reason to silently switch transports.
2. Extend the direct helper's AF_initData anchor-to-reason mapping so `duplicate_page_without_canonical_tag` resolves to the current UI label `Duplicate without user-selected canonical` and yields the correct `itemKey`.
3. Reuse the same saved-session frontend flow as other failed validations: open `/search-console/index/validation?...&item_key=...`, recover `failedAt`, and send the `RYZlBc` validation RPC directly.
4. Keep browser helpers useful for debugging selector/RPC shape changes, but do not make normal `validate-index-issues` / `validate-index-issues-all` silently drive Chrome.
5. Verify success by state change in the CLI/direct flow: the issue row should transition from `Failed`/`Not Started` to `Started`, and stdout should report `OK started` with a real `itemKey` source.

## Regression signals

- direct mode shows candidate row but submit fails with `item_key was not present ...`
- AF_initData contains `duplicate_page_without_canonical_tag` (or equivalent current anchor) plus a `CA...` issue key, but the helper still leaves `itemKey: null`
- the validation page contains enough bootstrap data to reconstruct `RYZlBc` (`itemKey`, `failedAt`, issue type), but the CLI still reports missing template/RPC
- drilldown contains `VALIDATE FIX` or `SEE DETAILS` only as Material `role="button"`; browser helpers may need that for debugging, but the product CLI should still stay on the saved-session direct path unless the user explicitly asks for browser mode

## Known live examples from session work

- `https://querypie.ai/`: `Duplicate without user-selected canonical` with `Validation: Not Started` successfully transitioned through drilldown `VALIDATE FIX`.
- `https://www.querypie.com/`: same reason with `Validation: Failed` could still reach drilldown but may expose a partial `Examples` validation view if the wrong detail control is chosen, so the helper must score/select the validation-status-card `SEE DETAILS` path carefully.

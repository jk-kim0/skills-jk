# GSC validation detail partial-view and drilldown SEE DETAILS flow

Use this note when maintaining `bin/gsc-browser-indexing` or any browser automation that starts Search Console Page indexing issue validation.

## Observed durable UI pattern

Some GSC issue types, including `Page with redirect` on `https://querypie.ai/`, do not reliably expose `START NEW VALIDATION` if automation jumps straight to:

`https://search.google.com/search-console/index/validation?resource_id=...&item_key=...`

The same issue can expose `START NEW VALIDATION` when reached through the real UI transition:

1. Open the Page indexing report:
   `https://search.google.com/search-console/index?resource_id=<encoded property>`
2. Click the issue row in `Why pages aren't indexed`.
3. Wait for the drilldown URL:
   `/search-console/index/drilldown?resource_id=...&item_key=...`
4. On the drilldown page, click the right-side `SEE DETAILS` button for the validation-status card, e.g. `Validation Failed`.
5. Wait for the validation URL:
   `/search-console/index/validation?resource_id=...&item_key=...`
6. Click `START NEW VALIDATION` and verify `Validation started` or table state `Started`.

## Automation implications

- Do not treat a direct validation page with only `Examples` as immediately non-actionable.
- First retry via drilldown → validation-card `SEE DETAILS`.
- If multiple `SEE DETAILS` controls exist, choose the one whose surrounding text matches the target validation state (`Validation Failed`, `Not started`, etc.) and preferably the issue reason.
- Use CDP/Playwright-style real mouse clicks at row/button centers; DOM `.click()` may keep the GSC SPA in a partial view.
- Only report non-actionable after the real drilldown/SEE DETAILS path also lacks `START NEW VALIDATION`.
- Never fall back from issue-level validation to URL-level Request indexing unless the user explicitly asks for URL-level submission.

## Regression checklist

A browser helper should have tests or source assertions that verify:

- issue rows are opened from the Page indexing table before validation details;
- drilldown `SEE DETAILS` is required rather than optional direct URL fallback;
- `SEE DETAILS` selection scores nearby validation-status context;
- missing `START NEW VALIDATION` after the real path is reported as skipped/failed, not success;
- parent/batch summaries propagate per-issue failures clearly.

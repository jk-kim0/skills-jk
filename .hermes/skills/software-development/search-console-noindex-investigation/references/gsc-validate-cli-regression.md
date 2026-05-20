# GSC Validate Fix CLI regression notes

Use this reference when maintaining a repo-local `bin/gsc` wrapper for Search Console Page indexing issue validation.

## Durable lessons

- If the user asks for `validate-index-issues`, provide that exact subcommand. Do not expose only longer internal names such as `validate-index-issues-all` or `validate-index-issues-all-browser`.
- Keep issue validation actions dry-run by default; require `--submit` for starting validation.
- Browser/CDP and direct frontend helpers must propagate per-issue failures to the process exit code. A site summary that says OK while nested issues failed is misleading and should be treated as a regression.
- The default `--only-status` for `validate-index-issues`, `validate-index-issues-all`, browser helpers, and frontend helpers should be `actionable`, where `actionable = Failed + Not Started`. Do not default to `Failed` only; the user expects `Not Started` rows to run validation by default.
- `--only-status all` should not blindly include `Passed`, `N/A`, or already-started validations. For action runs, treat `all` as actionable unless the user explicitly asks to include other states.
- On GSC validation detail pages, wait for the real `Validation details` view plus either `START NEW VALIDATION` or a terminal/started validation state. Seeing an `Examples` section alone is not proof that the validation detail view is actionable.
- For clicking `START NEW VALIDATION`, DOM `button.click()` may not trigger the same behavior as a user gesture. Prefer a CDP/Playwright-style mouse click at the button center and verify the post-click state.
- When a browser/CDP path is flaky, preserve the result as partial evidence and report which property/issue actually reached `Validation started`; do not claim all-site success from a partially failed run.

## Regression tests to add

- `bin/gsc validate-index-issues --help` succeeds and documents dry-run/submit/browser options plus `--only-status` defaulting to `actionable = Failed + Not Started`.
- The exact subcommand delegates to the direct frontend path by default and to the browser path only when `--browser` is supplied.
- Browser and direct helper defaults are aligned with the wrapper: `onlyStatus` starts as `actionable`, not `Failed`.
- Nested per-issue browser failures produce non-zero exit status.
- `--only-status all` action mode filters to actionable statuses rather than retrying already passed or non-actionable rows.
- Validation detail waits do not conclude failure merely because only `Examples` content appeared before the start button finished loading.

## Reporting pattern

When execution is partial, report:

1. Which properties/issues were successfully changed to `Validation started`.
2. Which properties/issues failed due to CLI/runtime behavior.
3. Whether a code fix/PR was created to make future all-site validation reliable.
4. Logs or artifacts only as supporting evidence, not as proof of all-site completion.

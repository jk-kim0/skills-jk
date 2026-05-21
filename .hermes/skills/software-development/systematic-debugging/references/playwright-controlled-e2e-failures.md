# Playwright controlled E2E failure output

Use this when a Playwright E2E test is intentionally validating a large external contract, such as sitemap URL health, and the default `expect(...).toBe(...)` failure output adds noisy stack traces instead of the actionable failure list.

## Symptom

A test already logs a useful `Summary` and `Errors` section, but the final failure still prints an assertion stack such as:

```text
Error: Every archived/live sitemap URL should return 200 on stage...
expect(received).toBe(expected)
Expected: 0
Received: 182
  at tests/e2e/sitemap-stage.spec.ts:273:5
```

## Preferred pattern

1. Keep the per-item result logging and final `Errors:` section.
2. Replace the final Playwright `expect(errors.length).toBe(0)` assertion with an explicit branch.
3. Throw a controlled `Error` whose message includes the actionable summary and failed result lines.
4. Override `error.stack` with the same controlled message prefixed by `Error:` so Playwright does not print source stack frames for this expected validation failure.

Example:

```ts
function formatFailureMessage(errors: CheckResult[], total: number) {
  return [
    'Sitemap stage URL check failed.',
    'Every archived/live sitemap URL should return 200 on stage, allowing redirects only when the final response is 200.',
    `Summary: total=${total} errors=${errors.length}`,
    'Errors:',
    ...errors.map((error) => `- ${formatResultLine(error)}`),
  ].join('\n');
}

function failWithControlledMessage(message: string): never {
  const error = new Error(message);
  error.stack = `Error: ${message}`;
  throw error;
}

if (errors.length > 0) {
  failWithControlledMessage(formatFailureMessage(errors, results.length));
}
```

## Verification

- Run the narrow linter or typecheck for the touched spec file if available.
- If the worktree lacks `node_modules`, use the repo root dependency install only when that is the established local convention for the repo and avoid installing dependencies in the worktree unless explicitly needed.
- Smoke-test the stack override with a tiny Node snippet and assert the captured stack has no `\n\s*at\s` frames.

## Pitfalls

- Do not hide the actual failing URLs. The controlled message must include the existing error lines or an equivalent actionable failure list.
- Do not use this for unexpected programming errors; ordinary stack traces are useful for those. This pattern is for expected validation failures where the data output is more useful than source frames.
- Avoid replacing every assertion in a test file. Use it only at the final aggregate failure point where the test has already collected and printed detailed diagnostics.

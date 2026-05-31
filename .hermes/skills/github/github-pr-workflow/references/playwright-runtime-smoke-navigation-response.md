# Playwright runtime smoke: navigation response races

Use this when a deployed-URL Playwright smoke fails while clicking through login/navigation and the error is a timeout from `page.waitForResponse(...)` or similar response-event waiting.

## Symptom

A deployed runtime smoke fails with an error such as:

```text
Test timeout exceeded
Error: page.waitForResponse: Test timeout exceeded
```

But the Playwright `error-context.md` / page snapshot shows the target page is already rendered correctly, for example:

- URL/navigation shell is at the expected authenticated page
- target heading is visible
- app layout and user/session UI are present
- recent runtime logs do not show app/server errors such as Prisma `P2021`/`P2022`

## Interpretation

Do not immediately treat this as an app runtime failure. If the snapshot proves the page rendered, the test may have missed the response event because navigation completed before the listener matched, the relevant response was not the document response the matcher expected, or the click used a server action/redirect path that does not produce a clean URL-matching response event.

## Fix pattern

Prefer user-visible navigation assertions first, then explicitly probe the protected route response under the same authenticated browser session.

Example before:

```ts
const dashboardResponsePromise = page.waitForResponse((response) => response.url().includes("/dashboard"));
await page.getByRole("button", { name: "Sign in" }).click();
await expectHealthyResponse(await dashboardResponsePromise, "/dashboard");
await expect(page).toHaveURL(/\/dashboard$/);
await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
```

Example after:

```ts
await page.getByRole("button", { name: "Sign in" }).click();
await expect(page).toHaveURL(/\/dashboard$/);
await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();

await expectHealthyResponse(await page.goto("/dashboard", { waitUntil: "domcontentloaded" }), "/dashboard");
await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
```

This keeps both contracts:

1. the click/login flow reaches the expected page from a user perspective
2. the authenticated route returns a non-5xx response when explicitly requested

## Verification

- Inspect failed run logs and `error-context.md` before changing the spec.
- Query relevant runtime logs for actual server errors in the same time window when the smoke is meant to catch deployment/schema issues.
- Run the updated deployed-URL smoke workflow on the PR branch, not only local tests, because the bug is often a deployed-navigation synchronization issue.
- After merge, run the smoke again from `main` if the issue close criteria require latest-main evidence.

## Pitfalls

- Do not remove response-status coverage entirely; replace fragile event waiting with an explicit authenticated route request.
- Do not weaken the smoke to only check URL changes if the original purpose was to catch runtime 500s.
- Do not report a failed smoke as DB/schema mismatch when same-window runtime logs show zero schema-mismatch markers and the page snapshot is already healthy.

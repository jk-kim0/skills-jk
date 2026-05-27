---
name: corp-web-app-stage-e2e
description: Add or maintain corp-web-app Playwright E2E coverage against https://stage.querypie.com, including production-vs-stage availability gates such as sitemap URL checks.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-app, playwright, e2e, stage, querypie, availability]
    related_skills: [corp-web-app-contact-us-stage-e2e, github-pr-workflow]
---

# corp-web-app stage E2E

Use this when the user asks to add, update, or run E2E tests for `corp-web-app` against the hosted stage site `https://stage.querypie.com`.

This is a class-level umbrella for stage-hosted E2E coverage. For Contact Us-specific form behavior, also load `corp-web-app-contact-us-stage-e2e`.

## Preconditions

1. Confirm the repo is really `corp-web-app`:
   ```bash
   pwd
   git rev-parse --show-toplevel
   git remote -v
   ```
2. Start from the latest `origin/main` in a fresh worktree for PR work:
   ```bash
   git fetch origin --prune
   git worktree add .worktrees/<topic> -b test/<topic> origin/main
   git -C .worktrees/<topic> merge-base HEAD origin/main
   git -C .worktrees/<topic> rev-parse origin/main
   ```
3. Use the existing Playwright workspace under `tests/`; do not create a separate root-level harness unless explicitly requested.
4. Prefer CI or targeted hosted E2E checks. Do not start a local dev server unless the user explicitly asks.

## Existing E2E workspace

Key files:
- `tests/package.json`
- `tests/package-lock.json`
- `tests/e2e/playwright.config.ts`
- `tests/e2e/*.spec.ts`
- `tests/README.md`

The config defaults `baseURL` to `https://www.querypie.com`, so stage scripts should set:
```bash
BASE_URL=https://stage.querypie.com npx playwright test --config=e2e/playwright.config.ts <spec> --reporter=line
```

When adding a focused hosted-stage check, add a named script in `tests/package.json` and document it in `tests/README.md`.

## Production-vs-stage availability gates

For production pre-deploy checks, the user expects the target website to be stage, not production. Example pattern:
- collect/commit a production artifact snapshot at PR creation time when requested
- fetch the live production source at E2E runtime when requested
- use the union of archived and live production URLs as the expected route set
- transform those URLs to `https://stage.querypie.com`
- verify the stage responses

### Sitemap URL availability pattern

When asked to test `www.querypie.com/sitemap.xml` coverage before production deploy:

1. Save the production sitemap snapshot into a stable fixture such as:
   ```bash
   mkdir -p tests/e2e/fixtures
   curl -fsSL --retry 3 --retry-delay 2 https://www.querypie.com/sitemap.xml \
     -o tests/e2e/fixtures/sitemap.<YYYY-MM-DD>.xml
   ```
2. Add a Playwright spec that reads the archived sitemap and fetches `https://www.querypie.com/sitemap.xml` at runtime.
3. Extract `<loc>` URLs from both XML documents, decode basic XML entities, filter to `https://www.querypie.com/`, dedupe, sort, and convert each URL to the `https://stage.querypie.com` origin while preserving path and query.
4. Check each stage URL with explicit request handling rather than Playwright browser navigation when the test only needs HTTP status and redirect chains.
5. Follow 30x redirects manually up to a bounded limit. A 30x is acceptable only when the final response is 200.
6. Print human-readable text output:
   - one URL per line
   - status chain, final status, source URL, stage URL, redirect chain, final URL
   - final `Summary:` line
   - final `Errors:` section
7. Fail the test only after all URLs have been checked and printed:
   ```ts
   expect(errors.length, 'See the Errors section above.').toBe(0);
   ```
   Avoid asserting deep equality on the whole errors array because Playwright will print a huge object diff that hides the useful human-readable log.

### Critical URL fixture pattern

A sitemap-only availability test is not enough when the bug involves public entrypoints, redirects, legacy inbound routes, or content links that are intentionally absent from `sitemap.xml`. In those cases, keep the sitemap-derived checks and add a small explicit fixture such as `tests/e2e/fixtures/required-public-urls.txt`.

Use this pattern for URLs like unprefixed legal/pricing entrypoints, `/chat/publication/...` redirects, and broken MDX/publication links that real traffic or runtime logs show are important. Merge the fixture URLs with archived + live sitemap URLs, dedupe, convert them to the stage origin, and require each final response to resolve to 200 after bounded redirects.

When expanding the fixture from runtime logs, filter out scanner/probe/feed noise and image/icon probes first. Add only app/content/publication URLs that should resolve for real users or crawlers. Verify added fixture URLs are absent from the live sitemap so reviewers understand why the extra fixture exists.

See `references/sitemap-critical-required-urls.md` for the full workflow and review checklist.

## Logging contract

For URL availability checks, prefer output shaped like:
```text
OK status=200 final=200 source=https://www.querypie.com/foo stage=https://stage.querypie.com/foo redirects=- finalUrl=https://stage.querypie.com/foo
ERROR status=404 final=404 source=https://www.querypie.com/bar stage=https://stage.querypie.com/bar redirects=- finalUrl=https://stage.querypie.com/bar
Summary: total=182 direct200=171 redirectTo200=0 errors=11
Errors:
- ERROR status=404 final=404 source=https://www.querypie.com/bar stage=https://stage.querypie.com/bar redirects=- finalUrl=https://stage.querypie.com/bar
```

The user specifically values readable terminal output over large assertion diffs.

## Worktree dependency pitfall

Fresh worktrees may not have `tests/node_modules`, and `npx playwright` can fail with:
```text
Error [ERR_MODULE_NOT_FOUND]: Cannot find package '@playwright/test' imported from tests/e2e/playwright.config.ts
```

If the root checkout already has `tests/node_modules`, you can temporarily symlink it for local verification instead of running a slow install in the fresh worktree:
```bash
ln -s /absolute/path/to/corp-web-app/tests/node_modules /absolute/path/to/worktree/tests/node_modules
npm run test:e2e:<script>
rm -f /absolute/path/to/worktree/tests/node_modules
rm -rf /absolute/path/to/worktree/tests/test-results /absolute/path/to/worktree/tests/playwright-report
```

Never commit this symlink or generated Playwright output.

## PR workflow notes

- Rebase the branch onto latest `origin/main` before push.
- In the PR body, state when a new E2E test is expected to fail because stage currently has real Non-200 URLs. This is not a failed implementation if the test's purpose is to expose those gaps.
- Report current CI/check status after PR creation without passively waiting unless the user asks.

## RSS 404 diagnosis pitfall

If the stage sitemap availability E2E fails only for `/rss*.xml` URLs, do not assume corp-web-contents is missing RSS files. Check for a policy mismatch first:

- `src/app/sitemap.xml/route.ts` may serve Blob-backed `public/sitemap.xml` on stage.
- corp-web-contents `scripts/generate-sitemap.js` includes `public/rss*.xml` files in the sitemap.
- `src/utils/middleware/rss.ts` may still have a production-only `isProduction()` early return, causing stage `/rss*.xml` to return 404 before Blob lookup.

Preferred fix, when the test is meant to verify production sitemap URL availability on stage: allow stage to serve Blob-backed RSS files too, and return 404 only when the RSS file is actually missing. See `references/stage-sitemap-rss-404-diagnosis.md` for the full checklist.

## References

- `references/sitemap-stage-availability-pr-783.md`: session notes for the archived + live sitemap URL availability E2E added in corp-web-app PR #783.
- `references/stage-sitemap-rss-404-diagnosis.md`: diagnosis checklist and fix options for stage sitemap E2E failures where production RSS is 200 but stage `/rss*.xml` is 404.
- `references/sitemap-critical-required-urls.md`: workflow for augmenting sitemap-derived E2E coverage with an explicit required-public-URLs fixture when real 404s are absent from `sitemap.xml`.

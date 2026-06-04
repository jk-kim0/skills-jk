# UI screenshot evidence for PR reviews

Use this reference when a PR description includes a UI-change section and the review needs screenshot evidence.

## Workflow

1. Parse only the PR body's UI-change section and extract explicitly listed URI paths. Preserve query strings, drop fragments, deduplicate in order, and cap comparison to the first 3 paths unless the user asks for more.
2. Resolve the stable/before base URL and preview/after deployment URL from the repository deployment system, PR checks, or GitHub deployment statuses. Do not substitute a redirected or unrelated route without saying so.
   - For Vercel checks, the commit status `target_url` may point to the Vercel dashboard rather than the public preview host. In that case query GitHub deployments for the PR head SHA/ref, then read the latest successful deployment status `environment_url` / `target_url`; use that public host for `After:` links and page probes.
   - Example with `gh`: `gh api --method GET repos/$OWNER_REPO/deployments -f ref=$HEAD_SHA --jq '.[] | {id, environment, task}'`, then `gh api repos/$OWNER_REPO/deployments/$DEPLOYMENT_ID/statuses --jq '.[] | {state, environment_url, target_url, created_at}'`.
   - Pitfall: with `gh api`, `-f/--field` can make the request default to POST when no method is specified. Always pass `--method GET` for deployment lookups, otherwise GitHub may treat the call as a create-deployment request and return a misleading 409 about commit status contexts.
3. Capture Before and After with the same viewport, browser, auth/session state, and wait strategy. Use `1440x1000` unless the PR or user specifies another viewport.
   - If the UI change is stateful or interactive (collapse/expand, hover/focus reveal, dropdown open state, mobile-only behavior), capture the default Before/After plus the changed After states needed to prove the behavior. A plain expanded Before/After screenshot is insufficient evidence for a stateful UI PR.
   - If the changed state cannot be reached without mutating shared preview/demo data (for example setup must be saved before a real-send confirmation button enables), do not mutate the data just for screenshot evidence unless the user explicitly approves it. Capture the reachable default state, probe/report why the stateful control is disabled, and state the limitation in the PR screenshot comment.
   - For auth-protected routes, use the same demo/login path for every run, and assert the expected control/state before taking extra screenshots when possible.
4. After capture, run a lightweight DOM/text verification pass for the same Before/After URLs when the intended change is expressible as visible text, form/control presence, redirects, or status codes. This catches screenshots that were captured successfully but do not prove the exact contract.
   - Check both positive and negative conditions, for example “After shows new form/CTA/copy” and “After no longer shows old blocker/copy.”
   - Record the DOM findings in the screenshot comment notes so reviewers do not need to infer everything visually.
   - For subtle visual changes that screenshots may not prove clearly (typography, dropdown row sizing, button/link parity, border radius, padding, hover/focus styles), supplement screenshots with browser-computed style probes for the actual rendered elements. Include the relevant values in the PR comment when they are the review contract, for example `font-size`, `font-weight`, `line-height`, `height`, `border-radius`, padding, and visible text/state. This is especially important when native controls or global CSS can override source-level class tokens.
   - For Node/Playwright one-off verification scripts in a package repo, place the temporary script under that package root or run it from a location where `node_modules` resolution works; avoid writing the script to `/tmp` if it imports package-local test dependencies such as `@playwright/test`.
5. Prefer a repository-owned Playwright screenshot test/config or reusable script over one-off browser automation when this will recur. Keep screenshots under ignored test/artifact directories such as `test-results/ui-screenshots/` rather than committing them.
6. If login is required, make authentication an explicit screenshot-runner option so Before and After use the same account/session assumptions.
7. Post the screenshot evidence before normal code-review findings. A code blocker does not excuse skipping UI evidence.
8. If capture, DOM verification, or upload is blocked, post a PR comment with the blocker and the evidence checked before moving on to general review.
   - If a listed route is auth-protected and unauthenticated HTTP/browser capture only redirects to login, say exactly that in the evidence note instead of claiming the route UI was reviewed. Continue reviewing public paths and code-level UI contracts when they still provide useful evidence.
9. If a PR already has a prior screenshot-evidence comment and the user asks for a fresh PR review or screenshot comment, do not assume the old comment is sufficient. Re-query the current PR head SHA, current preview deployment URL, and current stable/main URL. If the head/base or deployed URLs differ from the prior comment, post a new “current recapture” evidence comment that names the reviewed head and explains any changed Before/After baseline.
10. If the review turns into a follow-up commit/push on the same PR, do not imply older screenshots cover the new head. Either recapture After screenshots from the new successful preview deployment, or explicitly report that the latest preview/check is still in progress and the previously posted evidence was for the earlier head.
11. If a follow-up commit changes the product/design policy behind already-posted screenshot evidence, post a short superseding PR comment before or along with any new review work. Name the new head/commit if known, state which prior screenshot conclusion is stale, and state the replacement expectation so reviewers do not treat old visual evidence as current.

## Comment expectations

- Include direct full URLs for each compared path, not only base deployment URLs.
- Write `Before:` and `After:` as clickable URLs that include scheme, host, and path.
- Keep the screenshot links/images close to the path they document so reviewers can match evidence to page quickly.
- Describe visible differences, layout/spacing/overflow issues, auth redirects, server errors, or blockers.

## Example format

```md
### `/sales-demo/settings`

Before: https://outbound-dev.vercel.app/sales-demo/settings
After: https://outbound-abc123-querypie.vercel.app/sales-demo/settings

![Before](...)
![After](...)

Notes:
- The settings form spacing matches the intended layout.
- No horizontal overflow at 1440x1000.
```

## Upload path guidance

Use the repository-approved attachment/upload path. If the repository already approves a GitHub attachment extension such as `gh-attach`, prefer that over public gists, committed screenshots, or third-party storage.

Generic pattern:

```bash
gh extension list | grep -F gh-attach || gh extension install enthus-appdev/gh-attach
# This extension uses Go-style single-dash flags. When passing -repo, pass the PR/issue number explicitly before FILE...
gh attach -repo "$OWNER_REPO" -title "UI Screenshot Review - PR #${PR_NUMBER}" "$PR_NUMBER" path/to/before.png path/to/after.png > /tmp/ui-screenshot-links.md
# gh-attach uploads/prints markdown; it does not reliably create the final narrative PR comment by itself.
# Build a separate review comment that embeds the uploaded image URLs and includes Before:/After: full URLs.
gh pr comment "$PR_NUMBER" --body-file /tmp/ui-screenshot-comment.md
```

If upload fails with `--repo requires an explicit NUMBER or --key` or treats `--repo` as a filename, run `gh attach --help` and switch to the extension's single-dash flags (`-repo`, `-title`) plus explicit PR number.
Use `gh attach -json` when scripts need machine-readable upload output, and compose the final multiline comment with `gh pr comment --body-file`.

Important: `gh attach` uploads files and prints Markdown/link output, but does not necessarily create the final PR review comment you want. Treat its stdout as attachment/link material, then write a dedicated comment body file and post it explicitly with `gh pr comment <pr> --body-file <file>`. After using repo-root artifact paths such as `test-results/`, clean untracked screenshot artifacts or move reusable comment drafts to `/tmp` so the root checkout stays clean.
After upload, verify the PR's recent comments (`gh pr view --json comments`) before telling the user a comment was posted; if only the upload happened, report the prepared comment file or post it explicitly.

## Dynamic route and missing data blockers

For PR-body paths that include placeholders such as `/{id}`, first try to resolve a real path from the deployed list page using the same authenticated session. If the demo deployment has no records and no detail link can be found, do not invent an ID or substitute a different route. Capture the non-placeholder pages that are available, and in the screenshot comment add a short blocker note for the placeholder routes explaining which list page was checked, its HTTP status, and that no real detail link was exposed in stable or preview.

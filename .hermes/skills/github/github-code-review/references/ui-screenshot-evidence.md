# UI screenshot evidence for PR reviews

Use this reference when a PR description includes a UI-change section and the review needs screenshot evidence.

## Workflow

1. Parse only the PR body's UI-change section and extract explicitly listed URI paths. Preserve query strings, drop fragments, deduplicate in order, and cap comparison to the first 3 paths unless the user asks for more.
2. Resolve the stable/before base URL and preview/after deployment URL from the repository deployment system, PR checks, or GitHub deployment statuses. Do not substitute a redirected or unrelated route without saying so.
3. Capture Before and After with the same viewport, browser, auth/session state, and wait strategy. Use `1440x1000` unless the PR or user specifies another viewport.
4. Prefer a repository-owned Playwright screenshot test/config or reusable script over one-off browser automation when this will recur. Keep screenshots under ignored test/artifact directories such as `test-results/ui-screenshots/` rather than committing them.
5. If login is required, make authentication an explicit screenshot-runner option so Before and After use the same account/session assumptions.
6. Post the screenshot evidence before normal code-review findings. A code blocker does not excuse skipping UI evidence.
7. If capture or upload is blocked, post a PR comment with the blocker and the evidence checked before moving on to general review.

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
gh attach --repo "$OWNER_REPO" --title "UI Screenshot Review - PR #${PR_NUMBER}" path/to/before.png path/to/after.png > /tmp/ui-screenshot-links.md
gh pr comment "$PR_NUMBER" --body-file /tmp/ui-screenshot-comment.md
```

Use `gh-attach --json` when scripts need machine-readable upload output, and compose the final multiline comment with `gh pr comment --body-file`.

# PR preview vs stage render audit pattern

Session-derived pattern from auditing a corp-web-japan PR that refactored shared company page primitives.

## When this matters

Use this when a PR changes shared layout/page primitives and the user asks whether the Preview Deployment renders the same as `https://stage.querypie.ai`.

## Workflow

1. Identify the exact preview URL and PR head SHA.
   - `gh pr view <number> --repo querypie/corp-web-japan --json headRefOid,comments,statusCheckRollup,files`
   - Extract the latest Vercel `[Preview](...)` URL from comments/status.
2. Identify affected routes from the PR file list.
   - Shared primitive changes require checking every changed callsite route.
   - Example route set from a company-page primitive PR: `/about-us`, `/contact-us`, `/certifications`, `/news`.
3. Capture stage and preview with the same desktop and mobile viewports.
   - Suggested: desktop `1440x1200`, mobile `390x1000`.
4. Collect DOM geometry and computed styles, not just screenshots.
   - body scroll height/width
   - `html` font size
   - H1 rect and computed font metrics
   - each `main section` rect plus computed `paddingTop`, `paddingBottom`, `paddingLeft`, `paddingRight`, `backgroundColor`
   - important images/cards/forms/links
5. Save full-page screenshots under `/tmp/<task-name>`.
6. If visual differences are small, compute a pixel-diff summary.
   - Use repo-local `sharp` if Pillow/pixelmatch is unavailable.
   - Report image size, nonzero %, mean diff, and bbox.
7. Trace visible differences back to code-level wrapper contracts.
   - Compare old page-specific wrappers against the new shared primitive.
   - Common causes:
     - mobile bottom padding: `pb-20` -> `pb-[96px]` creates a 16px footer shift
     - desktop bottom padding: `lg:pb-[128px]` -> `lg:pb-[120px]` creates an 8px CTA/footer shift
     - mobile gutter: `px-6` -> `px-[30px]` narrows content by 12px total, causing text rewrap and card-width changes
8. Classify each difference by severity.
   - blocker: missing/wrong content or broken structure
   - major: visibly different layout in main body, e.g. narrower cards and rewrapped intro text
   - minor: small CTA/footer vertical shift with unchanged body
   - non-issue: exact pixel match or intentionally shared chrome difference

## Node script pitfall

If a Playwright script is saved under `/tmp`, Node resolves packages relative to `/tmp` and may fail with `ERR_MODULE_NOT_FOUND: Cannot find package 'playwright'` even though the repo has Playwright installed.

Use one of these fixes:

```js
import { createRequire } from 'node:module';
const require = createRequire('/absolute/path/to/repo/package.json');
const { chromium } = require('playwright');
```

Or place/run the script from the repo root.

## Reporting pattern

Report in this order:

1. exact URLs, SHA, routes, viewports, artifact directory
2. route-by-route judgment
3. measured evidence for each route
4. root cause in old wrapper vs new primitive terms
5. fix recommendation using semantic primitive presets instead of reintroducing raw `className` escape hatches

## Good fix direction for shared primitive regressions

When the PR goal is to remove raw `className` customization from shared primitives, do not fix parity by adding the escape hatches back.

Prefer semantic presets, for example:

- `CompanyPageSection padding="form"` for contact form pages that need mobile `pb-20`
- `CompanyPageSection padding="certifications"` for pages that need `lg:pb-[112px]`
- `CompanyPageSection padding="newsList"` for pages that need `lg:pb-[128px]`
- `CompanyPageSection gutter="marketing"` for pages that need `px-6 lg:px-0` rather than `px-[30px]`

This preserves visual parity while keeping route code free of ad hoc layout classes.

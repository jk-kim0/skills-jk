---
name: web-render-parity-audit
description: Audit visual and content differences between production and staging/preview deployments of a web page using browser screenshots, vision analysis, and source code inspection.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [web, browser, parity, screenshot, visual-regression, stage, production, audit]
---

# Web Render Parity Audit

Use when the user asks to:
- compare production vs stage/preview UI for a specific page
- identify visual regressions between live environments
- debug why a page looks different on stage vs production
- audit migrated/reimplemented pages for parity against upstream

This skill complements traditional diff-based debugging by adding visual evidence. It is especially useful after route migrations, static page re-implementations, or content pipeline changes where metadata and copy regressions are common.

## Goals

1. Capture full-page screenshots of both environments for the same URL path
2. Identify visible differences (layout, spacing, typography, colors, content)
3. Trace each visible difference back to a specific source file or data asset
4. Fix the root cause and verify on the updated environment

## Procedure

### 1. Normalize comparison URLs

Production and stage URLs often differ by hostname only. Ensure the path and query parameters are identical before capturing.

Example mapping:
- Production: `https://www.querypie.com/ko/company/certifications`
- Stage:     `https://stage.querypie.com/ko/company/certifications`

If the user provides only one URL, derive the comparable URL by swapping the known domain pattern.

### 2. Capture full-page screenshots

Use browser automation tools (e.g., MCP chrome-devtools) to capture the complete rendered page for both environments.

Save screenshots with clear labels:
```
/tmp/<page>-prod.png
/tmp/<page>-stage.png
```

If the page is long, ensure the screenshot captures below-the-fold content. Use full-page capture when available.

### 3. Analyze screenshots

Use vision analysis to compare the two screenshots side by side. Focus on:

**Layout and structure:**
- Header presence and styling (shadow, height, background)
- Hero section layout and typography
- Content grid/card layout (column count, spacing, alignment)
- Footer presence and styling

**Content:**
- Page title (browser tab / rendered heading)
- Body copy text and accuracy
- Card titles, descriptions, and ordering
- Image presence and sizing

**Visual polish:**
- Box shadows, borders, background colors
- Font rendering differences
- Spacing and margin discrepancies

Record every identified delta with a classification:
- `bug`: unexpected difference that should be fixed
- `expected`: known divergence (e.g., environment-specific flags)
- `unclear`: needs source code investigation

### 4. Map differences to source code

For each confirmed bug, locate the relevant source files.

Common file patterns for static/route-local pages:
- `src/app/[locale]/<route>/page.*.tsx` — metadata, title, hero copy
- `src/app/[locale]/<route>/*.ts` — data arrays, card items
- `src/components/widget/<route>/*.tsx` — layout component
- `src/components/widget/<route>/*.module.css` — styles

For metadata title mismatches:
1. Check `export const metadata` in locale page files
2. Compare against the legacy source (e.g., meta.json, CMS blob)
3. Look for missing site name prefix (e.g., `QueryPie AI <page>`)

For content copy mismatches:
1. Check data files that feed the page component
2. Look for incorrect copy-paste during migration (e.g., one card's description copied to another)
3. Verify against upstream source of truth

### 5. Fix and verify

Apply the smallest fix that resolves the parity gap.

After pushing/deploying to stage:
1. Reload the stage page
2. Capture a new screenshot
3. Re-run vision analysis to confirm the delta is resolved

## Common regression patterns

### Metadata title prefix dropped
During route-local migration or static page extraction, the global site prefix (e.g., `QueryPie AI`) may be omitted from the explicit `metadata.title` export, while the previous dynamic page automatically prepended it from a shared meta config.

Fix: prepend the site prefix explicitly in each locale page's metadata object.

### Content copy incorrectly duplicated
When migrating card-based content arrays, one item's description may be accidentally copied to another item. This is visible as two cards showing identical descriptions.

Fix: trace the correct upstream description and patch the data file.

### Missing or different CSS module classes
After component extraction or route-local refactoring, wrapper class names may change, causing spacing or background differences.

Fix: compare the rendered computed styles against production and align the CSS module classes.

## Verification checklist

- [ ] Screenshots captured for both environments
- [ ] Vision analysis performed and deltas classified
- [ ] Each bug traced to a specific source file
- [ ] Fix committed and pushed
- [ ] Stage re-screenshotted and confirmed resolved

## Related skills

- `corp-web-japan-live-page-render-parity` — Japan-specific variant with additional corp-web-japan conventions
- `corp-web-japan-article-preview-parity` — article-level comparison for publication pages
- `safe-git-worktree-branch-cleanup` — when parity audit is combined with workspace cleanup

---
name: footer-public-site-sync
description: Sync the repo footer with the live public site footer, verify locale/legal/address copy, add regression tests, and ship via PR.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [footer, localization, copy, verification, pull-requests]
    related_skills: [github-pr-workflow, github-code-review]
---

# Footer Public-Site Sync

Use this skill when the user asks to update the repo footer to match the live public site footer, including copyright year, office addresses, legal labels, and locale-specific copy.

## When to use
- Footer copy needs to match the public website
- Office/address/legal text may have changed upstream
- The change should be verified against the live site before editing

## Workflow

1. Inspect the live site footer in the browser
   - Open `https://www.querypie.com/`
   - Check footer text in the browser console or snapshot
   - If the site has locale-specific variants, inspect `/en`, `/ko`, and `/ja`

2. Compare against repo sources
   - `src/components/layout/Footer.tsx`
   - `src/constants/navigation.ts`
   - `src/app/[locale]/page.tsx`
   - Any locale copy helpers used by the shell/footer

3. Update the footer source of truth
   - Keep the footer component and navigation/legal mapping in sync
   - Prefer updating shared constants over hardcoding duplicates
   - If the public site uses a different English legal label, align the mapping everywhere the label is surfaced
   - Update copyright year when needed

4. Add or update a regression test
   - Add a focused footer test that checks the updated year/copy/address/legal label
   - Test the exact rendered text the user would see

5. Verify
   - `npm run typecheck`
   - targeted footer tests
   - `npm run build`

6. Ship via PR
   - Create a branch from the latest `main`
   - Commit and push the change
   - Create a PR and keep the branch name aligned with the actual PR head branch

## Pitfalls
- Do not trust only one locale; footer/legal labels can differ by locale
- Do not update the footer component without checking shared navigation/legal constants
- Do not assume a label like `Terms of Use` is correct if the live site says `Terms of Service`
- Confirm the PR head branch with `gh pr view` before pushing to avoid pushing to the wrong branch
- If the change is already merged into `main`, do not create a duplicate PR

## Suggested verification command sequence

```bash
npm run typecheck
npm run test:run -- src/components/layout/Footer.test.tsx
npm run build
```

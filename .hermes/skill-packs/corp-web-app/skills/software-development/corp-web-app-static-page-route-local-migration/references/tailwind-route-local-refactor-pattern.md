# Tailwind route-local refactor pattern

Use this reference when following up on corp-web-app static/semistatic route-local PRs that convert page shells from CSS Modules or legacy widget CSS to Tailwind.

## Situation

A Tailwind transition plan produced several independent route-local PRs:

- `/[locale]/company/contact-us`: CSS Module route-local wrappers were replaced with Tailwind.
- `/[locale]/company/about-us`: legacy company widget CSS Module imports were removed from the route-local layout wrapper.
- `/[locale]/company/certifications`: the route was already Tailwind, so the follow-up was audit/test-only.

The user then asked to rebase the three open PRs onto latest `main` and refactor them, not to create replacement PRs.

## Preferred refactor shape

### Contact Us

Avoid exporting many implementation-only class constants such as `contactUsChecklistClassName`, `contactUsDirectEmailSectionClassName`, or `contactUsCommunityLinkIconClassName` into each locale page. That makes `page.en.tsx`, `page.ko.tsx`, and `page.ja.tsx` read like class plumbing instead of route-local page composition.

Prefer semantic route-local wrappers in `contact-us-page-section.component.tsx`:

- `ContactUsSection`
- `ContactUsIntro`
- `ContactUsChecklist`
- `ContactUsInfoBlock`
- `ContactUsContactList`
- `ContactUsCommunityLink`
- `ContactUsFormPanel`

Keep the locale pages focused on authored copy, list items, direct email labels, community link text, and the `ContactSalesForm` locale.

### About Us

If converting old widget CSS Module classes to Tailwind leaves very long class strings inside JSX, keep the Tailwind implementation route-local but extract named constants in the support component file, for example:

- `investorLogoListClassName`
- `timelineClassName`
- `timelineYearClassName`
- `teamGridClassName`
- `teamLeaderClassName`
- `locationsGridClassName`

This keeps the JSX readable while avoiding a return to shared widget CSS Modules.

### Certifications audit-only PRs

If inventory already reports `tailwind`, do not force a visual rewrite just to have a code diff. A source-level audit/test PR can be the right follow-up: assert that the route continues to use shared company/certification section primitives and does not import route-local CSS Modules.

## Existing PR follow-up sequence

For open PRs in this class:

1. Verify each PR is still `OPEN` and record `headRefName`, `headRefOid`, `baseRefName`, and file list.
2. Fetch and update local `main` to latest `origin/main`.
3. Rebase each existing PR branch onto latest `origin/main`.
4. Apply refactors on the same PR branch.
5. Run the narrow checks:
   - `git diff --check`
   - `npm run inventory:tailwind-pages -- --json --grep '<route-pattern>'`
   - targeted route Vitest
   - `node scripts/ci/assert-test-groups.mjs` when tests changed
6. Amend the existing scoped commit when the history is one iterative commit.
7. Force-push with an explicit lease to the same branch.
8. Verify:
   - local HEAD equals `git ls-remote origin refs/heads/<branch>`
   - `git merge-base HEAD origin/main` equals `origin/main`
   - `git rev-list --left-right --count origin/main...HEAD` is `0 1` for a single scoped commit
   - `gh pr view <number> --json headRefOid,statusCheckRollup,mergeStateStatus` shows fresh checks on the new head

## Pitfalls

- Do not leave mismatched JSX closing tags when replacing raw `<div>` or `<a>` elements with semantic wrappers. Re-read the locale files after scripted replacements.
- Do not push route-local Tailwind class constants into locale pages unless the constant is tiny and semantically obvious.
- Do not convert an audit-only route into a larger rewrite if the planned task only asks for parity/audit.
- Do not start a dev server for these PRs unless explicitly requested; targeted tests and CI are enough for this user's preferred workflow.

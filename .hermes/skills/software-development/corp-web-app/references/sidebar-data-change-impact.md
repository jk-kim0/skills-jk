# Navigation/Sidebar Data Change Impact Pattern

## Context
In corp-web-app, shared navigation data lives in `src/components/sections/resource-list/resource-category-data.ts` (`getResourceCategorySidebar`, `getDemoCategorySidebar`). These functions return a list of sidebar links used across multiple routes (blog, whitepapers, events, manuals, glossary, introduction-deck, resources).

## Lesson
When adding, removing, or renaming a category in a shared sidebar data function, the change propagates to ALL routes that consume that sidebar. This means tests far beyond the immediate route may break.

## Files to check after any `getResourceCategorySidebar` or `getDemoCategorySidebar` change

1. `src/lib/repo-content/__tests__/resources-list.test.ts` — hardcodes the expected sidebar link array for each locale and asserts on aggregated item IDs.
2. `src/__tests__/app/[locale]/t/events-verification-route.test.tsx` — asserts that the events list/detail page sidebar contains an active link for "イベント".
3. Any other `*-verification-route.test.tsx` or page-level tests that render a page shell containing the sidebar and assert on sidebar link presence/active state.
4. Snapshot tests under `src/__tests__/` that capture the sidebar markup.

## Workflow

1. Edit the data source (`resource-category-data.ts`).
2. Search the codebase for assertions against the changed label or href:
   - `grep -r "label: '이벤트'" src/__tests__`
   - `grep -r "getAllByRole('link', { name:" src/__tests__`
   - `grep -r "stringMatching(/\^events:/)" src/__tests__`
3. Update all matching tests before pushing.
4. Run the relevant test file(s) locally or watch CI for `Test publications` / `Validate Test`.
5. If the change is locale-specific copy inside the shared sidebar data (for example changing only the English `introductionDeck` label), do not rely only on an existing KO/JA contract test. Add or run a verification that exercises the locale you actually changed so a one-locale wording tweak is directly covered.

## Locale-specific copy pitfall

A shared-sidebar test can still pass while missing the exact locale that changed. Example: `src/lib/repo-content/__tests__/resources-list.test.ts` currently validates the KO sidebar contract, so an English-only label change in `resource-category-data.ts` needs either an EN assertion in that test family or another narrow EN-targeted check before push.

## Past Incident
- Removing the "Events" category from `getResourceCategorySidebar` caused `events-verification-route.test.tsx` line 61 to fail because it expected `screen.getAllByRole('link', { name: 'イベント' }).some(... aria-current === 'page')` to be true, but the sidebar no longer rendered that link.
- Fix: remove the sidebar-link assertion from the events page test while keeping all other event-specific assertions (page heading, resource cards, load-more button, etc.).

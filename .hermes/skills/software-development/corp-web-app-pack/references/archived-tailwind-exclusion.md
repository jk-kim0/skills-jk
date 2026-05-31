# Archived routes in corp-web-app Tailwind planning

Use this reference when updating Tailwind route migration plans or reviewing open Tailwind route-group PRs in `corp-web-app`.

## Durable rule

Archived routes are not Tailwind migration backlog.

Keep these routes under:

```text
src/app/(legacy)/[locale]/archived/**
```

They exist primarily to:

- give redirect rules a stable target so stale URLs avoid 404 Not Found;
- preserve old route-local/static content for future reference or reuse;
- provide a maintainer-facing archive index, not public navigation or Tailwind review inventory.

Do not treat Tailwind utility signals inside archived routes as evidence that they should be moved into `(tailwind)`.

## Planning document update pattern

When refreshing `docs/plans/2026-05-19-tailwind-route-ui-transition-plan.md` or similar Tailwind plans:

1. Mark Archived as excluded from Tailwind migration, not long-tail backlog.
2. Remove archived routes from migration priority waves and route conversion acceptance criteria.
3. State that archived routes remain in `(legacy)` for preservation/redirect purposes.
4. If current main changed route state elsewhere, update counts with the live inventory before editing.
5. Keep customer-facing/public navigation language out of archived descriptions; archived is an internal preservation surface.

## Archived index IA audit pattern

For `https://stage.querypie.com/{locale}/archived`, verify the archive index against source rather than guessing from rendered UI alone:

1. Enumerate source page files under `src/app/(legacy)/[locale]/archived/**/page.tsx`.
2. Inspect `src/app/(legacy)/[locale]/archived/archived-pages.ts` for index grouping and locale coverage.
3. Compare the source child routes to index entries.
4. Probe every index URL on stage and require 200 responses.
5. Document IA groups and locale coverage in the plan when the user asks for planning updates.

Typical IA groups observed:

- Company: bounty program, terms, careers, customers, customer success, hall of fame
- Partners: become-a-parter, partner-apply
- Solutions: automated auditing/reporting, engineering/workforce efficiency, compliance, optimized integration, simplified access control
- Why QueryPie: why-querypie-acp

Keep legacy spelling such as `become-a-parter` when it is part of the existing URL contract.

## PR handling

If an open PR moves archived routes into `src/app/(tailwind)/[locale]/archived/**`, close it when the user asks to apply this policy. Leave a concise Korean comment explaining that archived pages are excluded from Tailwind migration and remain legacy preservation/redirect targets. Deleting the remote branch is acceptable when closing those obsolete migration PRs.

After closing, re-check open PRs for `archived|archive` so no archived Tailwind conversion PR remains open.

## Verification

Lightweight verification is enough for documentation-only updates:

```bash
git diff --check
npm run inventory:tailwind-pages -- --json
```

For the archive index audit, also record that stage archive child URLs returned 200. Do not run local dev server unless explicitly requested.
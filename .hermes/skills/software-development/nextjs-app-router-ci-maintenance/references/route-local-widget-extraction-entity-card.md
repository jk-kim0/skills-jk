# Route-local widget extraction: hidden Entity Card example

Session pattern from querypie/outbound-agent `/hidden/entity-card`.

## Situation

A hidden App Router page implemented an Entity Card mock-up directly in the route file. The user asked to make the entity card a reusable widget component while following the repo's route-local i18n/authoring approach.

## Boundary that worked

- Route page owns mock data, scenario composition, intro copy, lanes/sections, and model-specific examples.
- Shared widget owns card presentation and interaction shell only: standard/compact variants, tone styles, meta rows, preview entries, status/note rendering.
- The widget exposes broad props/unions such as `EntityCardType`, `EntityCardTone`, `EntityCardPreviewEntry`, and `EntityCardProps`; it does not know about a specific route's sample data.

## Test-first guardrail

Add/update a lightweight source-inspection test before extraction to force the desired boundary:

- route source imports the shared component path;
- route source no longer defines duplicate `StandardEntityCard`, `CompactEntityCard`, or route-local `toneStyles` helpers;
- widget source includes the approved entity type names;
- route data still includes the intended visible scenarios.

This makes the first test run fail for the missing widget, then pass after extraction without requiring a local browser server.

## Model-derived entity card attributes

When adding an entity such as `Email Sender`, read both model docs and schema source before choosing mock attributes.

Example mapping used:

- `SenderIdentity.providerType` -> UI meta `Provider: Gmail`
- `SenderIdentity.emailAddress` -> UI meta `Address: minji@chequer.io`
- `SenderIdentity.status` -> UI status/meta `auth_required`
- `GmailSenderCredential.connectedEmailAddress` -> safe preview/note describing pending OAuth credential linkage

Keep these as mock field/value examples and schema field names only. Do not include credential values, OAuth tokens, refresh tokens, secrets, connection strings, or production account data.

## Verification stack

Preferred quick checks for this class of refactor:

```sh
npm test -- --run src/__tests__/<route-or-widget-source-test>.test.ts
npx eslint <touched-test> <touched-route> <touched-component> --max-warnings=0
git diff --check
```

If broader `npm run typecheck` is blocked by an unrelated local dependency or generated-client issue, document the exact blocker in the PR body rather than representing the targeted refactor as unverified.

# Email Sender settings rebase conflict pattern

Use this reference when rebasing an Email Sender settings PR after `main` has added Dry-Run Sender support or Entity Card center-plus CTA contracts.

## Durable resolution rules

- Preserve latest `main` support for `providerType === "dry_run"`.
  - Dry-Run Sender should render as an explicit Email Sender entity.
  - It should communicate that no external account/Gmail auth is needed.
  - Do not turn Dry-Run rows into Gmail OAuth or Delete-only flows unless the PR explicitly changes Dry-Run lifecycle.
- Preserve the provider-specific Optional Create Card for adding Gmail senders.
  - Gmail OAuth should start from the always-visible optional create card.
  - Do not resurrect row-level `Connect Gmail` actions for existing sender rows when the PR intentionally moved Gmail creation to the optional card.
  - The OAuth connect URL should not require a preselected `senderEmail`; the verified provider identity is known after callback.
- Existing Gmail sender rows should remain Delete-only when the PR changed lifecycle from Disconnect/reconnect to hard-delete/re-add.
- If a later PR removes broad registry guidance copy, do not restore the old `EmailSenderRegistryGuidance` block during conflict resolution.
  - Keep source tests asserting stale long guidance copy is absent from both Sales Person creation and Team Email Sender Settings.
- For Entity Card optional-create conflicts, prefer the latest `circle-action` center-plus CTA contract.
  - Action-connected optional cards use `data-entity-card-optional-symbol="circle-action"`.
  - Actionless optional visual symbols may use `circle`.
  - Keep pointer affordance (`cursor-pointer`) on the action-connected centered `+` and do not add a duplicate bottom primary/text CTA.

## Focused verification

From `front/`, run focused tests around the conflict surface:

```bash
npm test -- --run \
  src/__tests__/entity-card-widget-state-variants.test.ts \
  src/features/email-sending/team-email-senders-ui.test.ts \
  src/features/email-sending/sender-identities.test.ts \
  src/features/email-sending/sales-person-sender-selection.test.ts \
  src/__tests__/email-senders-entity-card-page.test.ts
```

Run focused ESLint for touched source/test files and `git diff --check` before continuing the rebase or pushing.

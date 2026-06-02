# Connected mailbox email provider notes

Use these notes when drafting feature plans or model docs for mailbox-backed Email Sender Providers.

## Concept split

- Sender identity: the product-level From identity, usually `SenderIdentity.emailAddress` plus `displayName` and provider type.
- Connected account: the OAuth-authenticated mailbox/account that supplies credentials, for example `GmailSenderCredential.connectedEmailAddress` or a Microsoft credential's connected mailbox address.
- Provider credential/settings/ledger: provider-specific token, account id, tenant id, granted scopes, quota/cooldown status, and provider result ids.

If alias/delegation is not in scope, require sender email and connected account to match and say so before discussing future extensibility.

## Gmail / Google Workspace pattern

- Default path: Gmail API `users.messages.send` with send-only OAuth scope.
- Same-address validation should be explicit in MVP.
- Do not treat Gmail as a bulk provider; use low internal soft caps and account-protection guardrails.
- Post-MVP items: sendAs alias validation, inbox/reply sync, separate quota state, warm-up/cooldown model.

## Microsoft Exchange Online pattern

- Default path: Microsoft Graph delegated permission for Exchange Online / Microsoft 365 work mailbox sending.
- Credential fields to consider: Microsoft user id, tenant id, connected mailbox address, granted scopes, encrypted refresh credential, token key version.
- Settings fields to consider: mailbox type, auth status, verification status, daily/hourly soft cap, cooldown, disabled reason, health-check timestamp.
- Error categories to normalize: auth/refresh failure, sender mismatch, mailbox not found, missing permission, tenant policy block, conditional access block, Graph throttling, mailbox quota/send limit, generic send failure.
- Exclude by default unless requested: shared mailbox, delegated mailbox, send-as alias, send-on-behalf-of, application-permission tenant-wide send, SMTP AUTH, EWS, inbox/reply sync.

## Feature-plan checklist

- Position the feature as connected-mailbox provider, external bulk provider, or test/local provider.
- Define provider type value and provider-specific credential/settings/ledger candidates.
- Include Sales Person sender binding and SendRun locked-sender validation.
- Include connect/reconnect/disconnect lifecycle and UI recovery states.
- Include OpenSpec requirement/scenario candidates.
- Include `/goal` implementation prompt with success conditions, exclusions, required references, and verification commands.
- Link the plan from feature README and sprint/roadmap independent-track sections when those indexes exist.

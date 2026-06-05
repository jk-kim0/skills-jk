# Gmail Sales Person sender-selection smoke notes

Context captured from an outbound-agent Gmail actual-send readiness session.

## Durable implementation contract

A merged sender-selection change moved actual Gmail send from an email-string matching model to an explicit Team Email Sender selection model:

- `SalesPerson.senderIdentityId` points at a Team `SenderIdentity`.
- `SalesPerson.email` is derived from the selected `SenderIdentity.emailAddress`.
- `SenderIdentity.salesPeople` is a non-unique relation; multiple Sales Person personas may reuse one Team Email Sender.
- SendRun approval resolves the Campaign Sales Person's selected Gmail sender and locks `SendRun.senderIdentityId`.
- SendRun actual batch requires the locked sender to be Gmail with a `GmailSenderCredential`.
- `test_email_sender` remains message-level fake-local and is not an actual SendRun fallback.

## Safe smoke sequence

1. Confirm app deploy and DB schema readiness.
   - If the shared DB migration/repair/schema-check workflow fails, resolve that before provider smoke.
   - A 200 app response is not enough if schema repair failed.

2. Confirm Google OAuth setup.
   - Gmail API enabled.
   - OAuth client type: Web application.
   - Redirect URIs include local and each dev host callback path.
   - Scope is `https://www.googleapis.com/auth/gmail.send` only for send-only MVP.

3. Connect Gmail from Team Settings > Email Senders.
   - Verify active Gmail sender appears in the Team-scoped Email Senders table.
   - Verify DB row presence without printing refresh tokens.

4. Create a fresh Sales Person persona after the Gmail sender exists.
   - Select the connected Gmail sender in the `senderIdentityId` field.
   - Prefer this over relying on old Sales Person rows; old rows can have `senderIdentityId = null` if backfill ran before Gmail sender creation.

5. Create/use a Campaign referencing that Sales Person.
   - Use a Contact List with only intentional test recipient(s), because actual send does not apply a test-recipient allowlist.

6. Approve SendRun and send the smallest possible batch.
   - Verify `SendRun.senderIdentityId` lock.
   - Verify `SendAttempt.providerType = gmail`, `status = sent`, `gmailMessageId`, and `gmailThreadId`.
   - Record evidence in status/issue docs without secrets.

## Evidence wording pattern

Use neutral, non-closing GitHub issue comments such as:

```text
Gmail live smoke evidence (neutral reference; does not close the issue):
- Environment: dev-vercel
- Team: <team slug>
- Sender: <redacted or explicit allowed test sender email>
- OAuth connect: success; Gmail SenderIdentity + GmailSenderCredential row present
- Sales Person: selected Gmail sender by senderIdentityId
- SendRun approval: locked senderIdentityId present
- SendAttempt: providerType=gmail, status=sent, gmailMessageId present, gmailThreadId present
- Note: sent means Gmail API accepted; delivery/open/reply not verified.
```

## Pitfalls observed

- A deploy can succeed while the manual DB repair workflow fails. Do not start live OAuth/send smoke until the DB workflow is healthy.
- Existing issue text may say “email match”; after sender selection, require both selected `senderIdentityId` and derived email match.
- Do not paste OAuth client secrets into chat/docs/issues. If a secret was pasted into chat, recommend rotation if logs are not considered secret-safe.

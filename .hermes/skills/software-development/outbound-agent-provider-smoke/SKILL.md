---
name: outbound-agent-provider-smoke
description: Plan and execute live provider smoke tests in querypie/outbound-agent, especially OAuth-backed email sending, while preserving repo workflow, schema readiness, and secret safety.
version: 1.0.0
metadata:
  hermes:
    tags: [outbound-agent, provider-smoke, gmail, oauth, live-smoke]
---

# Outbound Agent Provider Smoke

Use this skill when working in `querypie/outbound-agent` and the task involves live provider smoke tests, OAuth credential storage, Gmail actual send, external-provider evidence, or issue/status updates for provider readiness.

## Core rules

1. Start from current repo reality, not old issue text.
   - Fetch/read latest `origin/main` state and inspect the relevant implementation/status docs before planning a smoke.
   - If a PR recently changed schema or sender-selection semantics, base the smoke on the merged code contract.

2. Do schema readiness before provider side effects.
   - Confirm the target environment has the latest code deployed.
   - Confirm shared DB migration/repair/schema-check workflows have succeeded before running OAuth connect or send smoke.
   - If schema repair/check is failing, resolve/report that blocker first; do not spend provider-side effects against a schema that may reject or mis-store the credential.

3. Keep secrets out of durable artifacts.
   - Never write OAuth client secrets, refresh tokens, generated token encryption secrets, generated state secrets, DB URLs, or credential values into issues, docs, PR bodies, comments, or chat summaries.
   - Evidence should record presence/status, environment, URL/route, row existence, and redacted IDs only.

4. Prefer the smallest real side effect.
   - Use exactly the intended test account and recipient(s).
   - For real email, start with one Gmail SendRun test send or a one-recipient actual batch before broader smoke.

## Gmail actual-send smoke under Sales Person sender selection

Current model: Sales Person does not own a free-form sender email. A Sales Person selects a Team Email Sender (`SenderIdentity`) by `senderIdentityId`; the Sales Person email is derived from that selected sender identity.

### Demo seed / send-ready asset contract

When the task is to prepare or document an email-sending demo, treat “all assets needed for an actual send after OAuth” as the baseline, not an optional polish item.

Before changing docs/specs or running a demo smoke, explicitly inventory and reconcile the complete asset chain:

- Team and user/persona context.
- Connected Team Email Sender / `SenderIdentity` for the intended provider.
- Sales Person linked to that sender, with compatible legacy `email` value where guards still require it.
- Company/Product assets referenced by the sales narrative.
- Campaign.
- Audience/Contact List with intentional demo recipients only.
- Email Template or generated message content.
- Recipient preview / SendRun readiness state.
- Approval/send path and evidence expectations.

If any asset is missing, stale, disconnected, or only implied by prose, update the seed/demo docs to say the asset must be created or filled before the demo can be considered ready. For documentation-only PRs, do not implement the seed silently; instead make the missing-asset fill requirement explicit in the canonical demo scenario and relevant OpenSpec contract/use-case docs.

Recommended sequence:

1. Environment readiness
   - Verify target app URL returns 200 and shows the expected deployed commit/version when available.
   - Verify shared DB repair/migration workflow succeeded and schema check is drift-free for the target environment.

2. Gmail OAuth connect
   - Navigate to Team Settings > Email Senders for the target Team.
   - Use `Connect Gmail` for the actual sender Google account.
   - Verify the Team-scoped Gmail sender appears in the Email Senders table as active/ready.
   - Verify callback evidence when present: `gmail=connected`, returned `senderIdentityId`, connected email, and row health text.
   - Verify DB evidence without revealing tokens: `SenderIdentity(providerType = gmail)` exists, `GmailSenderCredential` exists, encrypted refresh token is present but not printed.
   - For Vercel-backed dev environments, if using `psql` from pulled env vars, prefer `POSTGRES_URL_NON_POOLING`/`POSTGRES_URL` over `POSTGRES_PRISMA_URL`; Prisma URLs can include pooler query parameters that direct `psql` rejects.

3. Sales Person persona
   - Create a fresh Sales Person persona after Gmail connect when possible.
   - In the Sales Person form, choose the connected Team Email Sender from the `senderIdentityId` select.
   - Do not type or patch a free-form sender email unless deliberately repairing legacy data.
   - Existing pre-selection-model Sales Person rows can have `senderIdentityId = null`; treat them as unsafe for smoke until verified/updated.
- Also verify the Sales Person `email` itself matches the selected Gmail sender email. The current send-run guard still rejects a selected `senderIdentityId` if the legacy Sales Person email remains an old `*.example.local` value, with `sales_person_sender_mismatch`, before any Gmail provider call.

4. Campaign / SendRun
   - Use a Campaign that references the Sales Person persona selected above.
   - Use a Contact List containing only intentional test recipients. Actual Gmail send does not apply a test-recipient/domain allowlist, so any eligible Contact List recipient can receive real email.
   - Confirm recipient preview is ready before approval.

5. Approval and send evidence
   - Approve the SendRun and verify `SendRun.senderIdentityId` locks to the Sales Person selected Gmail sender.
   - Prefer Gmail SendRun test send before actual batch.
   - For actual batch, use one recipient first and verify `SendAttempt.providerType = gmail`, `status = sent`, and `gmailMessageId` / `gmailThreadId` presence.
   - Record that `sent` means Gmail API accepted, not delivery/open/reply confirmation.

## Pitfalls

- Do not confuse message-level `test_email_sender` with SendRun actual Gmail send. `test_email_sender` is fake-local/message-level only and must not be treated as a SendRun fallback.
- Do not proceed with OAuth connect/send if the environment's schema repair workflow just failed; the UI may load while credential persistence or Sales Person sender selection is still broken.
- Do not preserve old issue language that says only “Sales Person email must match Gmail account” without also checking `senderIdentityId` selection/lock.
- When Google OAuth fails with `invalid_client`, inspect the actual OAuth URL before changing Google Cloud settings. If `client_id` contains encoded whitespace such as `%0A`, re-set the deployed OAuth env values without trailing newlines and redeploy before retrying.
- When using Chrome/Google Console for OAuth setup verification, keep a persistent DevTools/CDP session alive if already attached; avoid reconnecting for every page read/action. If the user completes password/2FA manually, resume from the same CDP connection and verify the callback redirect plus Email Senders table state.

## References

- `references/gmail-sales-person-sender-selection-smoke.md` — detailed notes from the Gmail OAuth setup and PR #185 sender-selection transition.
- `references/gmail-oauth-vercel-env-and-cdp-continuation.md` — live-smoke notes for `invalid_client` caused by trailing-newline Vercel OAuth env values, plus the persistent CDP resume pattern after user-completed Google password/2FA.
- `references/demo-send-ready-asset-contract.md` — documentation pattern for requiring the complete post-OAuth email-send demo asset chain instead of assuming missing seed assets.

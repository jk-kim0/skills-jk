# Gmail OAuth smoke: Vercel env hygiene and CDP continuation

Session learning from a live `querypie/outbound-agent` Gmail sender connection on `outbound-dev.vercel.app`.

## Durable technique

When Google OAuth reaches `invalid_client` and the OAuth URL shows `client_id=...%0A`, treat it as a deployment/environment value hygiene issue before changing Google Cloud configuration. The OAuth client ID may have been copied into Vercel with a trailing newline.

Recommended sequence:

1. Inspect the actual OAuth error URL for encoded whitespace such as `%0A` in `client_id`.
2. Re-set the affected Vercel environment variables using a non-interactive/API path or another method that preserves the exact value without terminal newlines.
3. Redeploy the target environment after env replacement.
4. Re-run `Connect Gmail` from the Email Senders page and verify Google login/consent appears rather than `invalid_client`.

## Secret-safety notes

- Do not print OAuth client secrets, token encryption secrets, refresh tokens, DB URLs, or raw credential rows.
- It is safe to record the presence of a connected sender, redacted/non-secret sender IDs, email address intended for smoke, and UI status.

## Browser/CDP continuation pattern

If the user must complete password/2FA manually, keep the existing CDP browser connection alive and resume from it after the user says completion is done.

A useful verification after manual login/consent:

1. List browser targets/pages from the persistent CDP connection.
2. Look for redirect back to `/settings/email-senders?gmail=connected&reason=<senderIdentityId>`.
3. Evaluate the Email Senders page DOM and confirm:
   - banner title includes `Gmail sender connected`
   - the table contains the intended Gmail account
   - status is `active`
   - health text is `Ready for Gmail sending.`

This proves UI-level Gmail sender readiness without exposing credential material.

## Example evidence shape

Use concise evidence like:

- URL: `https://outbound-dev.vercel.app/<teamSlug>/settings/email-senders?gmail=connected&reason=<senderIdentityId>`
- Sender ID: `<non-secret SenderIdentity id>`
- Gmail sender: `<intended test Gmail address>`
- Status: `active`
- Health: `Ready for Gmail sending.`

Do not include secrets or token values in the evidence.
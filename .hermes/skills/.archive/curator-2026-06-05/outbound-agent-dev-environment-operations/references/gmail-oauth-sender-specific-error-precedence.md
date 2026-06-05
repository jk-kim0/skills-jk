# Gmail OAuth sender-specific error precedence

Use this reference when an Outbound Agent Email Senders page reports `gmail_refresh_token_missing` after the operator says they clicked `Connect Gmail` on the wrong Email Sender row or authenticated with an unexpected Google account.

## Durable lesson

Do not treat every `gmail_refresh_token_missing` report as purely a Google refresh-token consent problem. First check whether the OAuth start/callback carried the selected Email Sender address all the way through signed state and failure redirects.

## Correct behavior contract

1. The Email Senders UI should start Gmail OAuth from the specific sender row, not from a generic page-level button.
2. The OAuth start route should require `senderEmail` and validate that it belongs to a Gmail `SenderIdentity` in the current Team.
3. The signed OAuth state must include the selected `senderEmailAddress`.
4. The callback must not fall back from missing `state.senderEmailAddress` to Google `id_token.email`.
   - Missing selected sender in state should fail as a sender-selection/state error such as `gmail_sender_email_missing`.
5. After token exchange and id-token validation, compare selected sender email with Google identity email before persistence decides whether a refresh token is required.
   - Different selected sender vs Google account: return `gmail_alias_mismatch`.
   - Same selected sender/account, no stored credential, and Google omitted `refresh_token`: `gmail_refresh_token_missing` is appropriate.
6. Failure redirects should include the selected `senderEmail` when it is known so the failure UI can say which row was being connected.

## Why this matters

Google can omit `refresh_token` for an already-approved OAuth client/scope combination. If the callback loses the selected sender email and falls back to `id_token.email`, a wrong-row or legacy-state flow can be misreported as a refresh-token problem. That makes the user revoke Google consent when the immediate recovery might simply be starting from the correct sender row.

## Suggested regression tests

- Callback unit test: state has selected `senderEmailAddress=seller@example.com`, Google id token has `other@example.com`, token payload has no `refresh_token`; expect `gmail_alias_mismatch`, not `gmail_refresh_token_missing`.
- Callback unit test: state has no selected sender email; expect `gmail_sender_email_missing` and no fallback to Google identity email.
- Route test: failed callback redirect includes `senderEmail=<selected sender>` when verified state had a selected sender.
- UI/source test: failure message for refresh-token-missing includes the selected sender context and tells the user to start again from the correct row if it was not the intended sender.

## Operational triage

When this appears on `outbound-seoul` or another dev runtime:

1. Verify exact deployed revision before assuming stale code.
   - Tencent VM signals: `/opt/outbound-agent/repo/.deployed-revision`, `/opt/outbound-agent/deployments/current-image`, and `systemctl is-active outbound-front`.
2. If the deployed revision includes sender-row OAuth, inspect the redirected query string.
   - `reason=gmail_alias_mismatch`: wrong Google account for the selected row.
   - `reason=gmail_sender_email_missing`: legacy/bad OAuth start path; restart from the row button.
   - `reason=gmail_refresh_token_missing&senderEmail=...`: selected sender and Google account likely matched, but no new refresh token and no stored credential; revoke app consent or use the intended row.

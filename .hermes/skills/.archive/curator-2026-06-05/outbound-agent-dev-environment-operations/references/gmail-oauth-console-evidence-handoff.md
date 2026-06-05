# Gmail OAuth Console evidence handoff and docs update

Use this note when the user has completed Google Console or OAuth consent steps outside the agent session and asks to update repository records.

## Scope captured from the session

For Outbound Agent development environments, the canonical Authorized redirect URI set is:

```text
http://localhost:3000/api/gmail/oauth/callback
https://outbound-dev.vercel.app/api/gmail/oauth/callback
https://outbound-seoul.dev.querypie.io/api/gmail/oauth/callback
https://outbound-tokyo.dev.querypie.io/api/gmail/oauth/callback
```

If the user explicitly says they confirmed these in Google Console, treat that as operator evidence and update the repository records without trying to re-verify with a gcloud account that lacks `querypie-saas-dev` access.

## Recommended repository updates

Update the active documentation sources that carry Gmail OAuth status:

- `docs/gcp/gmail-dev-oauth-setup.md`
  - Record that `querypie-saas-dev` / `Outbound` Google OAuth client has the local/dev redirect URI set registered.
  - Distinguish Google Console registration from runtime smoke for each environment.
  - Record `outbound-dev` OAuth authentication success if the user completed consent there.
  - If send smoke was intentionally skipped, say so explicitly; do not imply message id/thread id evidence exists.
- `openspec/changes/sprint-3-working-email-sending/design.md`
  - Mark the redirect URI live-confirmation checklist item complete when the user confirmed Console registration.
- `docs/feature/status-gmail.md`
  - Update Provider evidence notes to separate OAuth connect success from actual send evidence.

## Wording discipline

Prefer precise statements:

- `Google Console 등록 상태 확인 완료` for operator-confirmed Console state.
- `OAuth 인증 작동 확인 완료` only for an environment where consent/callback actually succeeded.
- `send smoke intentionally skipped` or Korean equivalent when the user chooses not to test sending.
- `VM runtime smoke는 별도 검증` for Seoul/Tokyo if only Console registration was confirmed.

Avoid overclaiming:

- Do not claim Gmail message id/thread id evidence unless an actual Gmail send was performed and recorded.
- Do not claim Seoul/Tokyo OAuth runtime success solely from Console registration.
- Do not print or persist OAuth client secrets, refresh tokens, or encrypted token payloads.

## PR workflow

This is usually a docs-only follow-up:

1. Start from latest `origin/main` in a repo-local `.worktrees/` worktree.
2. Keep the diff narrow to docs/status/OpenSpec records.
3. Run `git diff --check`.
4. Commit and open a Korean PR with a body that states no secrets were added.
5. Report the PR URL immediately.

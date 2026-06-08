# Outbound Agent Chrome E2E OpenSpec Pattern

Use this reference when the user asks for an OpenSpec plan/spec for browser E2E coverage that spans Google SSO, Gmail/Email Sender OAuth, and actual email sending.

## Recommended change shape

Create a docs-only OpenSpec change rather than implementing Playwright immediately unless the user explicitly asks for code.

Suggested path shape:

```text
openspec/changes/<change-id>/
  proposal.md
  tasks.md
  specs/uc-<flow-id>/spec.md
```

For an end-to-end user journey, prefer a `uc-*` spec because the contract is user-visible browser behavior and staged journey composition.
Update `openspec/specs/README.md` change inventory so future agents discover the new change.

## Required content for Chrome SSO + Email Sending E2E

The spec should split the full journey into reusable stages and then define a full-suite composition requirement.
A good stage breakdown is:

1. Chrome Browser execution contract.
2. Secret and credential safety.
3. Test data and environment readiness preflight.
4. Google SSO login from `/login` through application session creation.
5. Target Team navigation and settings route readiness.
6. Team Email Sender configuration and Gmail OAuth connection or reuse of an existing connected sender.
7. Sales Person selected sender readiness.
8. Campaign, Contact List, Email Template, recipient preview, and SendRun readiness.
9. Test send before actual recipient sending.
10. SendRun approval and actual send.
11. Full journey suite composition and fail-fast behavior.
12. Safe reporting/evidence and CI gating for real provider side effects.

## Security and side-effect requirements

Always state that Google SSO account credentials, OAuth client secrets, authorization codes, refresh/access tokens, cookies, and app passwords must not be committed, documented, printed in logs, embedded in screenshots/traces/videos, or copied into PR bodies.
Represent user-provided credentials as approved secret-source references or runtime environment key names only.
Diagnostics may report secret-source names, key names, and presence/absence, but not values.

Real Gmail provider send stages should be opt-in in CI via an explicit enable input, manual gate, or equivalent side-effect guard.
Default PR validation should not send external email.

## Evidence boundaries

Distinguish test send and actual send evidence.
For test send, require at least two non-secret evidence points such as UI success state, test SendAttempt/equivalent ledger, and provider accepted marker/provider message id presence.
For actual send, require UI completion state, SendAttempt ledger, locked sender/template/recipient snapshot, and provider message id presence or redacted provider accepted marker.
Do not require inbox-receipt verification as the default completion condition; treat it as optional follow-up unless the user explicitly asks for it.

## Pitfalls

- Do not conflate Google SSO login tokens with Gmail sender OAuth tokens.
- Do not let Google SSO login alone imply an Email Sender is connected.
- Do not use current session user email, Dry-Run Sender, or local test sender as late fallback for actual Gmail send.
- Do not create arbitrary domain data inside the UI journey when fixture/setup helpers should prepare Campaign, Contact List, Email Template, Sales Person, and SendRun readiness.
- Do not put raw credentials or secret values in OpenSpec, chat, PR body, task docs, screenshots, traces, or logs.

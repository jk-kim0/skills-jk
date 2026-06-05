# Outbound Agent auth / SSO planning decisions

Use this as the canonical reference for Outbound Agent Google SSO, account-linking, System Settings access, and Login SSO vs Email Sender OAuth boundary decisions.

## Product decisions to preserve

- Google SSO is a general user login feature, not an administrator-only System Settings feature.
- Google SSO accepts all verified email addresses inside the Outbound App.
- Google OAuth Client restrictions such as test users, organization/domain limits, consent screen policy, or allowed domains are Google platform setup constraints, not Outbound App authorization policy.
- If Google SSO succeeds and the verified normalized email does not match an existing User/auth identity, the app should create a new User and allow immediate product access.
- A user may have multiple SSO/auth mechanisms. If verified normalized email is the same, they represent the same User.
- SAML, Okta, and Auth0 are backlog providers after Google SSO, in that order, unless the user changes the roadmap.

## Account-linking model guidance

- Distinguish provider/admin configuration from the user identity model.
  - Provider/admin settings that rarely change can start as YAML/code config plus secret references.
  - Multiple SSO providers or mixed SSO + username/password normally need `UserIdentity` / `AuthIdentity`, not only `User.email`.
- Candidate identity fields: `userId`, `providerType`, `providerSubject`, `email`, `normalizedEmail`, `emailVerified`, `linkedAt`, `lastSignedInAt`.
- Add uniqueness around provider identity, such as `providerType + providerSubject`.
- Treat verified normalized email as the linking key only when the provider has verified it.

## Username/password email ownership constraint

- Email entered through username/password account creation, login, seed, or profile flow is not a User email until ownership verification completes.
- Before verification, treat it only as an unverified contact claim or equivalent field/state.
- Do not use unverified email for SSO account linking, System administrator allowlist checks, primary/canonical User identity, or notification targets.
- Email verification and promotion of that value to verified email is backlog unless explicitly scoped.

## Login SSO vs Email Sender OAuth boundary

- Login SSO and Email Sender OAuth are separate settings even if both use Google OAuth/OAuth2.
- Keep separate config objects, environment namespaces, routes, services, token stores, tests, and OpenSpec requirements.
- Login SSO callback must not touch Email Sender OAuth token storage.
- Email Sender OAuth callback must not create login sessions.
- It is acceptable for local/dev to point both config namespaces to the same actual OAuth2 client value, but code must still treat them as separate boundaries.

Suggested namespace pattern:

```text
GOOGLE_SSO_CLIENT_ID
GOOGLE_SSO_CLIENT_SECRET
GOOGLE_SSO_REDIRECT_URI

GMAIL_SENDER_OAUTH_CLIENT_ID
GMAIL_SENDER_OAUTH_CLIENT_SECRET
GMAIL_SENDER_OAUTH_REDIRECT_URI
```

## System Settings planning

- Use a System administrator allowlist separate from Team roles.
- Add/change/delete administrator workflow is out of scope unless the user asks for it; show a short contact message instead.
- SSO settings and System administrator allowlist can start as YAML or code config if they rarely change. Do not introduce a DB settings table just to display read-only config.

## Document update checklist after Product Owner corrections

1. Add or update an explicit accepted decision section.
2. Replace contradictory In Scope / Out of Scope bullets.
3. Update user flows, config examples, UI settings summaries, OpenSpec Requirement candidates, Scenarios, `/goal` success criteria, task checklists, risks, trade-offs, and open questions.
4. Search for stale opposite assumptions such as `existing users only`, `self-sign-up 없이`, `workspaceDomain`, `Workspace domain`, `domain 제한`, `chequer.io`, `autoProvisionUsers: false`, `unmatched email is rejected`, and `match existing User.email only`.
5. Update the PR body to summarize the corrected accepted policy.
6. Run `git diff --check`, amend/push the same PR branch, and re-check CI.

## Recommended scenario set

- SSO verified email matches an existing verified identity -> same User session is created.
- SSO verified email has no matching User/identity -> new User and SSO identity are created when auto-provisioning is in scope.
- SSO email is not verified -> no session is created.
- A second SSO provider presents the same verified email -> identity is linked to the existing User, not a duplicate User.
- Username/password account has the same email but the app has not verified it -> do not auto-link to the SSO User.
- System/admin allowlist checks use the User primary email or verified email identity, not an unverified local email.

## Source-session files used as examples

- `docs/feature/google-sso-system-settings.md`
- `docs/user-auth-requirements.md`
- `openspec/specs/platform-front-app-foundation/spec.md`
- `openspec/specs/contract-mvp-domain-schema/spec.md`

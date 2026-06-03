# Auth / SSO account-linking plan adapter

Canonical Outbound Agent auth/account-linking decisions live in `../../outbound-auth-feature-planning/references/google-sso-system-settings-decisions.md`.
Use this adapter when turning those decisions into a feature plan or implementation plan.

## Plan-specific checklist

- Identify whether the accepted product policy is general-user auto-provisioning or existing-user-only login.
- Include identity model trade-offs only once in the plan; prefer linking to the canonical decision when a separate OpenSpec/design doc owns the rationale.
- Include scenarios for verified SSO login, no existing user, second provider with same verified email, unverified provider email, and unverified username/password email.
- Put username/password email verification explicitly in Backlog / Out of Scope if it is not part of the current slice.
- After edits, search for stale opposite assumptions such as `existing users only`, `autoProvisionUsers: false`, `unmatched email is rejected`, or `match existing User.email only`.

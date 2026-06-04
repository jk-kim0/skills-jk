# Outbound Agent Google SSO OpenSpec decision adapter

Canonical auth/account-linking decisions live in `../../outbound-auth-feature-planning/references/google-sso-system-settings-decisions.md`.
Use this adapter only when applying those decisions to OpenSpec or feature-plan decision logs.

## OpenSpec-specific checklist

1. Record the accepted decision in `openspec/changes/<change-id>/design.md` or the repo's canonical decision log.
2. Express durable behavior in specs with SHALL / SHALL NOT language and GIVEN/WHEN/THEN scenarios.
3. Keep Google OAuth platform restrictions out of Outbound App authorization requirements unless the user explicitly asks to design platform setup/operations.
4. Search and remove stale contradictory requirement text after Product Owner corrections:
   - `existing users only`
   - `self-sign-up 없이`
   - `workspaceDomain`
   - `domain 제한`
   - `chequer.io`
   - `autoProvisionUsers: false`
   - `unmatched email is rejected`
5. Update PR body/docs changed summary so reviewers can see that the accepted policy changed.

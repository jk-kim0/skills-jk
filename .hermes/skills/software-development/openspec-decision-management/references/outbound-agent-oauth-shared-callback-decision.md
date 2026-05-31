# Outbound Agent OAuth shared callback decision example

Use this as a compact example when an OpenSpec decision affects OAuth/provider route structure and environment docs.

## Decision class

A Product Owner accepted `Team UI + shared callback` for a multi-tenant OAuth flow:

- OAuth starts from the Team-scoped UI: `/{teamSlug}/settings/email-senders`.
- The provider redirect URI stays fixed per environment: `/api/gmail/oauth/callback`.
- Team context and return path are restored from a verifiable OAuth `state`.
- Team slug is not placed in the callback route path.

## OpenSpec/doc layers to update

When recording this kind of decision, update these layers together:

1. Canonical decision log in `openspec/changes/<change-id>/design.md`.
   - Change `Status: Open` / `Decision: TBD` to `Status: Accepted`.
   - Mark the selected alternative as `Accepted` and rejected options as `Rejected`.
   - Include implementation impact and follow-up test requirements.
2. User behavior spec such as `specs/uc-*/spec.md`.
   - Add a scenario for starting from the Team settings page.
   - Add a scenario for successful callback returning to the same Team context.
3. Implementation contract spec such as `specs/contract-*/spec.md`.
   - Require shared callback route.
   - Require state integrity/expiry/session user/Team membership checks before token exchange.
   - State that invalid state or membership mismatch must not exchange tokens or save credentials.
4. Operational setup docs such as `docs/gcp/*oauth*.md`.
   - List local/dev/prod authorized redirect URIs using the fixed shared callback path.
   - Explicitly say not to register Team-scoped UI paths in the provider console.
   - Update implementation checklists for `state` contents and validation order.
5. `tasks.md`.
   - Mark documentation/spec follow-through complete only if completed in the PR.
   - Leave actual implementation/test work as future checkboxes unless code was implemented.

## PR body pattern

For a docs/OpenSpec-only decision PR, include:

- Summary of the accepted decision.
- Canonical record path.
- Resulting contract/spec paths.
- Follow-up implementation tasks.
- Lightweight verification such as `git diff --check` and touched-doc sanity checks.
- Explicit note that it is docs/OpenSpec-only.

## Pitfall

Do not treat the provider redirect URI and the user-facing entry route as the same concern.
For OAuth flows, a Team-scoped entry screen can coexist with a non-Team shared callback; the Team context belongs in verified `state`, not necessarily in the callback URL path.

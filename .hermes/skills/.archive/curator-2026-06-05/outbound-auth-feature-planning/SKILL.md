---
name: outbound-auth-feature-planning
description: Use when planning or documenting outbound-agent authentication features, SSO/account-linking, System Settings access, OAuth boundary decisions, or credential-reference CLI plans.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [outbound-agent, authentication, sso, oauth, feature-plan, openspec]
    related_skills: [openspec-decision-management, writing-plans, domain-model-design-docs]
---

# Outbound Auth Feature Planning

Use this skill when working in `querypie/outbound-agent` on authentication feature plans, auth-related OpenSpec changes, login SSO, account identity linking, System Settings access, OAuth configuration boundaries, or credential-management CLI planning.

## References

- `references/google-sso-system-settings-decisions.md` — canonical Outbound Agent auth/SSO/account-linking/System Settings decisions and scenario checklist.
- `references/credential-cli-dev-secret-management.md` — CLI-specific planning for reading approved 1Password credentials and configuring/verifying Dev Secret Manager targets. Storage/security boundaries are canonical in `../domain-model-design-docs/references/credential-encryption-key-management.md`.

## Core workflow

1. Work in a repo-local `.worktrees/` worktree, not the root checkout.
2. Start by reading repo context and canonical auth documents:
   - `AGENTS.md`
   - `docs/user-auth-requirements.md`
   - `docs/ui/auth-account-terminology.md`
   - `openspec/README.md`
   - `openspec/project.md`
   - `openspec/specs/platform-front-app-foundation/spec.md`
   - `openspec/specs/contract-mvp-domain-schema/spec.md`
3. If the user makes a product decision, record it in the active feature plan and update OpenSpec Requirement/Scenario candidates or canonical OpenSpec docs in the same PR when the request explicitly asks for OpenSpec coverage.
4. Keep feature plans actionable: include goals, in/out scope, user flows, data/API impact, UI surfaces, OpenSpec follow-up, `/goal` execution candidate, task breakdown, validation, risks, and open questions.
5. Prefer docs-only changes unless the user explicitly asks for implementation.

## Decision source-of-truth split

- Auth/SSO/account-linking product decisions live in `references/google-sso-system-settings-decisions.md`.
- OpenSpec-specific application notes live in `../openspec-decision-management/references/outbound-agent-google-sso-account-linking-decision.md`.
- Plan-writing adapter notes live in `../writing-plans/references/auth-sso-account-linking-plans.md`.
- Credential storage and Secret Manager/KMS/1Password boundaries live in `../domain-model-design-docs/references/credential-encryption-key-management.md`.
- Credential CLI command design lives in `references/credential-cli-dev-secret-management.md`.

Do not copy the same decision table or rationale across these files. Link to the canonical reference and add only the skill-specific application checklist.

## Quick reminders

- Do not write “SSO settings” ambiguously when Login SSO and Email Sender OAuth are both in scope. Say which boundary owns which setting.
- Do not treat a typed email in a username/password login/account form as verified identity.
- Do not use System administrator email allowlist as a general SSO allowlist.
- Do not imply Google SSO is limited to `chequer.io` inside the app unless the user explicitly changes the product decision.
- Do not bury OpenSpec-impacting auth constraints only in `docs/feature/**`; add or update OpenSpec Requirement/Scenario when the user asks for OpenSpec coverage.
- For credential CLI work, default write-capable operations to dry-run, require approval evidence for apply, and never print plaintext credentials.

## Google SSO credential reference implementation pattern

When implementing Google SSO OAuth client credential management in `querypie/outbound-agent`, do not leave `front/src/lib/auth/google-sso.ts` reading `GOOGLE_SSO_CLIENT_ID` / `GOOGLE_SSO_CLIENT_SECRET` directly. Wire the SSO route config through `front/src/features/credentials/runtime-credential-loader.ts` and provider `google-sso-oauth-client`.

Use this boundary:

- OAuth `clientId` is a public OAuth client identifier, not a password. It may be stored in git-tracked credential reference YAML as `publicFields.clientId`.
- OAuth `clientSecret` remains secret material. It must not be stored in YAML, docs, PRs, logs, or chat; load it from the referenced secret source only.
- Local Google SSO reference should use `credential-reference/v1`, provider `google-sso-oauth-client`, `publicFields.clientId`, `requiredFields: [clientSecret]`, and a 1Password `secretRef` for the secret.
- Dev Vercel can use `credential-reference/v1` with `publicFields.clientId` and a Vercel env `secretRef` for `GOOGLE_SSO_CLIENT_SECRET`.
- Tencent dev VM environments (`dev-seoul`, `dev-tokyo`) should use `legacy-runtime-secret/v1` during the current transition: `publicFields.clientId` in YAML, and `runtimeRefs` pointing only to `GOOGLE_SSO_CLIENT_SECRET` env/env-file for `clientSecret`.
- Update `front/.env.example` to use `OUTBOUND_CREDENTIAL_REFERENCE_DIR`, `OUTBOUND_SECRET_SOURCE`, and `OUTBOUND_SECRET_SOURCE_ENVIRONMENT` rather than direct Google SSO client id/secret env variables. Do not keep `GOOGLE_SSO_STATE_SECRET` as a runtime env var when the accepted implementation is YAML-backed state secret loading.
- For the current Google SSO credential-reference transition, put the environment-specific OAuth state HMAC secret in the Google SSO credential YAML as `fixedFields.stateSecret`. Treat this as active technical debt because the value is not in Secret Store yet; record `technicalDebt.status`, `technicalDebt.reason`, `technicalDebt.targetState`, and `technicalDebt.migrationMode`, and state that Secret Store adoption will move `stateSecret` to a Secret Store reference and remove the YAML fixed value.
- Update `front/.env.example` to use `OUTBOUND_CREDENTIAL_REFERENCE_DIR`, `OUTBOUND_SECRET_SOURCE`, and `OUTBOUND_SECRET_SOURCE_ENVIRONMENT` rather than direct Google SSO client id/secret/state-secret env variables.
- Do not leave `GOOGLE_SSO_STATE_SECRET` as a direct runtime env requirement for this repo's current Google SSO credential-reference path. Model the state secret as an environment-specific YAML `fixedFields.stateSecret` value, and mark this as active technical debt in `technicalDebt` because the value is not yet stored in Secret Store. State explicitly in docs/OpenSpec/PR body that Secret Store adoption will move `stateSecret` to a Secret Store reference and retire the YAML fixed value.
- Search after the change for `GOOGLE_SSO_CLIENT_ID`, `GOOGLE_SSO_STATE_SECRET`, and old config helpers such as `readGoogleSsoConnectionConfig`; only docs/tests/YAML `technicalDebt.reason` entries that intentionally describe legacy or debt state should remain.

## Implementation status audit add-on

When auditing whether Google SSO follows `docs/feature/credential-encryption-key-management.md`, distinguish three layers instead of giving one blended status:

1. **Login flow implementation** — inspect `/login`, `front/src/app/api/auth/google/**`, `front/src/lib/auth/google-sso.ts`, `UserIdentity`, and route/service tests. This can be implemented even when credential management is not complete.
2. **Credential Reference infrastructure** — inspect `front/src/features/credentials/**`, `front/scripts/credentials/cli.ts`, `front/package.json` `credentials`, and `config/credentials/**` for `credential-reference/v1`, `legacy-runtime-secret/v1`, `secretRef`, redacted field checks, and dry-run/apply behavior.
3. **Actual Google SSO credential integration** — verify whether Google SSO runtime code calls the credential loader or still reads `GOOGLE_SSO_CLIENT_ID` / `GOOGLE_SSO_CLIENT_SECRET` directly. Search for `loadRuntimeCredential`, `readCredentialRuntimeConfig`, `GOOGLE_SSO_CLIENT_ID`, and provider-specific reference files such as `google-sso-oauth-client`. If SSO reads env directly while the credential reference slice exists only for Gmail OAuth, report it as partial implementation, not complete compliance.

Report with exact evidence paths and classify: implemented/reachable, lower-level infrastructure only, env/legacy direct path, missing reference inventory, and missing live smoke/read-back evidence.

## Verification Checklist

- [ ] Canonical reference was updated instead of duplicating the same auth/credential decision text in multiple skills.
- [ ] Feature plan and OpenSpec wording use the current accepted decision and contain no stale opposite assumptions.
- [ ] Docs-only work did not add implementation unless explicitly requested.
- [ ] `git diff --check` passes.
- [ ] PR body states docs changed, OpenSpec changed when applicable, and whether the work is docs-only/no UI implementation.

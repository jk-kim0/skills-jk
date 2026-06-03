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

## Verification Checklist

- [ ] Canonical reference was updated instead of duplicating the same auth/credential decision text in multiple skills.
- [ ] Feature plan and OpenSpec wording use the current accepted decision and contain no stale opposite assumptions.
- [ ] Docs-only work did not add implementation unless explicitly requested.
- [ ] `git diff --check` passes.
- [ ] PR body states docs changed, OpenSpec changed when applicable, and whether the work is docs-only/no UI implementation.

# Outbound Agent OpenSpec doc PR rebase conflict recipes

Use this reference when rebasing Outbound Agent documentation/OpenSpec PRs and conflicts appear because `main` recently converted older docs into active OpenSpec bridge pages.

## General rule

Preserve the latest `origin/main` document architecture first, then reapply only the PR's still-valid contract pointer or active spec payload.

Do not resurrect long detailed prose in bridge documents just because the PR commit predates the bridge conversion.

## Bridge document conflicts

Typical shape:

- `main` has shortened a docs page into `상태: OpenSpec bridge` plus canonical active spec links.
- The PR commit tries to reintroduce detailed page-level requirements or old section inventories.

Resolution:

1. Keep the `OpenSpec bridge` structure from latest `main`.
2. Keep existing canonical links from `main`, especially newly landed active specs such as `integration-gmail-sender-auth`, `ui-gmail-sender-oauth`, `entity-email-sender`, or `entity-contact-list`.
3. Add only the PR's missing canonical pointer, such as `ui-component-entity-card` or `integration-google-sso` / `ui-google-sso-oauth`.
4. Update the implementation/regression note to mention both the main-owned spec and the PR-owned spec when both are relevant.
5. Do not duplicate detailed requirements in the bridge; those belong in active `openspec/specs/**/spec.md` files.

Example outcomes:

- For `docs/ui/email-senders-settings.md`, keep Gmail Sender OAuth and Email Sender entity bridge links from `main`, then add an Entity Card affordance link to `ui-component-entity-card`.
- For `openspec/specs/README.md`, keep newly landed Gmail Sender active spec rows and merge the PR's Google SSO active spec rows/change-spec descriptions instead of choosing one side.

## Entity model bridge conflicts

Typical shape:

- `main` has newly landed specialized entity specs such as `entity-contact-list` or `entity-email-sender`.
- The PR converts the broad MVP schema contract into a cross-entity bridge and adds many `entity-*` active specs.
- The conflict file contains a large old field inventory before `## Cross-entity validation rule`.

Resolution:

1. Prefer the PR's final bridge-style version when it already references the newly landed active entity specs.
2. Remove old detailed field inventory from `docs/model/05-mvp-schema-contract.md`.
3. Keep the concise source-of-truth table, entity spec index, common fields, front API boundary, cross-entity validation, exclusions, and implementation verification checklist.

## MVP domain schema verified email guard conflicts

Typical shape:

- `main` has converted `openspec/specs/contract-mvp-domain-schema/spec.md` into a cross-entity contract that delegates provider identity, provider subject uniqueness, and email verification state to `entity-user-identity`.
- A Google SSO PR adds implementable SSO language about verified Google email, provider subject resolution, auto-provisioning, and Gmail Sender OAuth token separation.
- The conflict appears inside `### Requirement: verified email identity guard`.

Resolution:

1. Keep the latest-main delegation sentence to `entity-user-identity`; do not reintroduce the older standalone `UserIdentity table for authentication providers` section if the broad schema contract has already been narrowed.
2. Add the PR's Google SSO-specific contract as additional sentences inside the existing verified email guard requirement.
3. Preserve the rule that `User.email` / equivalent primary email is verified-only and that username/password email input remains an unverified claim until ownership verification.
4. Preserve the fixture carve-out only as local/dev seed behavior, explicitly not production-grade verification evidence.
5. Keep Gmail Sender OAuth token separation pointing to `integration-google-sso`; do not duplicate Gmail Sender credential storage details in the domain schema contract.

## Verification

After resolving:

- Run `git diff --check`.
- Search for conflict markers.
- Stage all conflict files and continue with `GIT_EDITOR=true git rebase --continue`.
- After force-push, verify `git merge-base origin/main origin/<branch>` equals current `origin/main` and `gh pr view` reports `MERGEABLE` / `CLEAN` after metadata refresh.

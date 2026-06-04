---
name: domain-model-design-docs
description: Maintain repository domain/entity model design docs, especially when clarifying boundaries between setup entities, top-level aggregate/context entities, and pipeline-stage models.
version: 1.0.0
metadata:
  hermes:
    tags: [documentation, domain-modeling, entity-models, repository-docs, planning]
---

# Domain Model Design Docs

Use this skill when the user asks to inspect, revise, or decide repository data/domain/entity model documentation before UI or implementation work. This includes requests to clarify whether something belongs in a setup step, pipeline stage, aggregate/root entity, reusable entity, or separate model document.

## Core workflow

1. Confirm the repo, branch, and worktree policy before editing. If repo guidance says to use repo-local `.worktrees/`, do all writes there and keep the root checkout read-only.
2. Inspect existing docs first, especially:
   - `docs/model/**`
   - main pipeline/architecture docs such as `docs/data-pipeline-design.md`
   - UI planning docs when the entity boundary affects screen grouping or navigation
   - repo dictionary/glossary docs when terminology could drift
3. Identify the model-boundary correction as a source-of-truth change, not just prose cleanup.
4. Update the narrow source-of-truth model doc first, then propagate terminology and flow changes to dependent docs.
5. If an entity is clarified as a top-level aggregate/context rather than part of a setup/stage model, extract it into a dedicated model doc instead of leaving its fields under the wrong stage.
6. Keep the work documentation-only unless the user explicitly asks for implementation, migrations, code, or tests.
7. Verify with targeted searches for old boundary terms and misspellings before committing.
8. Commit, push, and create/update the PR when the repo workflow expects it.

## Boundary editing pattern

When the user says a setup/stage should contain only specific entities:

1. Remove any excluded entity from that setup/stage doc's “included entities” list.
2. Remove the excluded entity's detailed field/status section from the setup/stage doc.
3. Leave a short relationship note explaining that the setup/stage entities are referenced by the excluded entity if that helps reviewers.
4. Create or update a separate top-level model doc for the excluded entity when it is still central to the product.
5. Update the model index/README so the new hierarchy is obvious.
6. Update pipeline docs so flow labels match the model hierarchy, for example `Seller Setup → Campaign Configuration → Audience ...` instead of implying Campaign is part of Seller Setup.
7. Update UI planning docs only enough to preserve the model boundary; do not invent UI behavior beyond the clarified model.

## Source list vs execution audience pattern

When the user distinguishes an imported/customer-list concept from a campaign-specific audience:

1. Do not keep calling the campaign-independent import artifact an `Audience` if `Audience` is meant to represent a campaign execution target.
2. Introduce a reusable source-list entity such as `Contact List` plus a row entity such as `Contact List Entry` for CSV/spreadsheet/CRM/event imports that are managed outside any campaign.
3. Define `Audience` as campaign-scoped: it belongs to a Campaign and is shaped by the Campaign's Product, target criteria, messaging goal, and conversion goal.
4. Connect the two with references/snapshots rather than ownership: `Audience.sourceContactListId?` and `LeadCandidate.sourceContactListEntryId?` are clearer than making Campaign own the source list.
5. Preserve source data separately from campaign interpretation: imported row/original fields stay on the source-list entry, while campaign-specific scoring, rejection reason, enrichment, and qualification state live on Lead Candidate / Company Profile / Contact Profile / Prospect.
6. Update sourceMode/status names to avoid implying the source list itself is the audience; prefer `contact_list`, `importing_from_list`, or `mixed` over an ambiguous standalone `imported` when the import is mediated by a reusable list.

## Locale / market isolation pattern

When the user defines country/language scope for product or UI-facing features:

1. Treat the country/language decision as a source-of-truth model constraint, not only an i18n UI note.
2. Update the main pipeline/requirements doc with the supported first-scope languages and explicitly mark other languages as lower-priority future scope when that is the user decision.
3. Add `country` and `language` fields to every affected reusable or execution entity named by the user, especially setup entities (`Company`, `Product`, `Sales Person`) and execution entities (`Campaign`, `Audience`, `Lead Candidate`, `Prospect`) when applicable.
4. State that country/language are immutable after creation if the user says so; reflect this in both model fields and UI creation/editing guidance.
5. Define country/language as a market isolation boundary: do not allow Product, Sales Person, Campaign, Audience, or downstream execution entities to cross country/language combinations.
6. For multi-country or multi-language operation, document separate Campaigns per country/language combination as the required design path.
7. Remove or avoid duplicate target fields that conflict with the isolation model, for example replacing a mutable `targetCountry` with immutable Campaign `country` plus narrower target criteria.
8. Propagate the constraint to UI planning docs: creation screens show country/language, edit screens explain immutability, selectors only show compatible entities, and execution/review screens display country/language context.

## Locale, market, and campaign timezone pattern

When the user clarifies locale/market constraints for domain-model docs:

1. Treat country and language as model-boundary decisions, not just UI labels. Update the source-of-truth model docs first, then propagate to pipeline and UI planning docs.
2. If country/language are immutable, add them to the relevant entity field examples and design notes, and say explicitly that changing market/language requires a separate entity or campaign rather than editing the existing one.
3. For market isolation, state both the positive rule and the disallowed case: same country/language entities may be reused together; cross-country or cross-language Product/Sales Person/Campaign/Audience combinations are not supported.
4. If multi-country or multi-language operation is allowed only by separation, document that separate Campaigns per country/language combination are required.
5. If campaign operations depend on timezone, model it as a Campaign-level representative timezone such as `campaignTimezone`, even when a country can have multiple timezones.
6. Document that messaging execution, follow-up time references, scheduling, and meeting-time interpretation use the Campaign timezone.
7. Keep country default timezones as system constants or configuration defaults, not as a replacement for the Campaign-level timezone. The UI should propose the country default but require one Campaign timezone to be set.
8. Update outreach/response and conversion/follow-up docs when timezone affects scheduled messages, response deadlines, or meeting scheduling; do not leave timezone only in the campaign setup doc.

## Slug uniqueness and generated-route-code verification pattern

When the user asks to verify whether Entity Model design and implementation support a slug uniqueness rule, treat it as a schema-contract audit.

1. Identify the route/business identifier separately from the internal primary key.
2. Determine the intended uniqueness scope in words first: global, Team + entity type, parent aggregate + entity type, or another owning boundary.
3. Inspect the canonical model/OpenSpec contract and the Prisma schema together; do not infer the rule from route code alone.
4. For Team-scoped root business entities, look for `@@unique([teamId, slug])` on that model and avoid requiring uniqueness against other entity tables in the same Team unless the user explicitly asks for a shared namespace.
5. For generated short slugs, verify both the generator contract and collision path: allowed alphabet/length regex, candidate lookup in the same scope as the schema constraint, retry on collision, bounded failure behavior, and tests that force at least one collision.
6. Update feature/UI docs when a generated slug appears in user-facing routes, because URL behavior is part of the UX contract even when the slug is system-generated.

## Primary key / ID policy documentation pattern

When the user makes a repository-wide primary key or ID generation decision, treat it as a cross-cutting contract, not as a local field-note in one model document.

1. Add or update a dedicated document under `docs/contract/` when the rule affects multiple entities, migrations, seed data, app create paths, and reviewer criteria.
2. Link the contract from `docs/contract/README.md`, the deployment/schema-change principles doc, and the common field/type section of the canonical model contract.
3. If existing schema must be converted, add a separate `docs/feature/` plan for the conversion. Keep that plan scoped to the ID/PK transition unless the user explicitly asks for broader model changes.
4. State the default generation authority clearly: DB-generated, app-generated, or exception-only. For DB-generated IDs, instruct application create paths to omit `id` and read the inserted row's generated value.
5. Separate internal primary keys from user-facing route/business identifiers. Use slugs/codes/public IDs for visible routes when appropriate.
6. Preserve explicit timestamp fields and business ordering rules. Do not let sortable IDs replace `createdAt`, `updatedAt`, cursor order, or audit semantics.
7. Document allowed exceptions narrowly: deterministic fixtures/seeds, bulk workflows that require pre-insert IDs, pure join-table composite primary keys, or later high-volume log/event exceptions.
8. For an existing all-ID conversion where the user explicitly says to ignore backward compatibility, classify it as a `비호환 migration`, list all affected models, and specify migrate-first then app deploy/redeploy ordering.

## Provider-type replacement and default asset documentation pattern

When the user asks to replace a fake/test/local artifact with an explicit provider/type or default Team asset, treat it as a source-of-truth model change, not only feature prose.

1. Update the canonical schema/model contract with the root entity, provider enum value, optional provider-specific settings/result entity, and the bootstrap/default-asset rule.
2. Update ERD diagrams and relationship notes so old fake/test entities are renamed, replaced, or removed rather than left as parallel concepts.
3. State the distinction between an explicit selectable provider/type and a hidden fallback. Default assets may be auto-created, but runtime fallback or late assignment must be called out separately and usually rejected unless the user explicitly wants it.
4. Sweep docs that commonly preserve stale negative requirements: OpenSpec decision entries, contract scenarios, user-facing UC specs, feature status tables, seed/demo scenario docs, E2E scenario docs, UI settings docs, and feature bridge docs.
5. If the PR is docs-only, leave implementation/schema/migration/fixture changes out and mark Team bootstrap, provider adapter/result handling, UI list rendering, and legacy artifact cleanup as follow-up implementation tasks.

## Sync Front API / async backend boundary pattern

When the user clarifies that MVP Front APIs should be synchronous while actual long-running execution will be handled by a later async backend, treat it as a source-of-truth scope boundary, not a prose-only preference.

1. Define the MVP Front API as synchronous request/response mutations for save, review, approval, and status changes: validate input, persist immediately, and return the latest entity state.
2. Exclude real email sending, LLM model calls, enrichment execution, provider callbacks/webhooks, message queues, job runners, retry/cancel/timeout, and generic Job/EventLog/Audit Event contracts from MVP implementation.
3. Keep MVP timeline/event UI as a display layer over entity status, timestamps, and manual/fixture engagement rows unless the user explicitly asks for a canonical event table now.
4. Update technology-stack and backlog docs so they no longer say initial LLM wrappers or job stubs are adopted when actual model calls and async execution are post-MVP.
5. Update phase plans so implementation PRs do not introduce `queued`/`processing` async job states or placeholder Job/EventLog tables merely to anticipate later backend work.

## Use-case facade over existing entity graph pattern

When the user asks for a backend-centered feature design derived from a use-case/UI draft, and explicitly wants to minimize Entity Model or relation changes, design the feature as a facade/read-model/service layer over the existing domain graph before proposing new relations.

1. Start by reading the UI/use-case draft, then inspect the current canonical model docs, Prisma schema, and existing services/actions that already create or transition the relevant entities.
2. Build a mapping table from UI components/actions to backend entities and operations. For example, `Contact List Card` may map to `ContactList` selection plus internal `Audience` creation, while a `Start` control may map to `SendRun` approval/chunk-send transitions.
3. Distinguish user-facing capability names from persistence classifications. If the UI hides internal terms like Campaign/Audience/SendRun, keep those backend entities when they remain the correct aggregate/execution boundaries.
4. Prefer reusing existing enum values or modes when the behavior is the same; present a new enum value as a classification-only alternative only when lifecycle, approval policy, caps, analytics, or filtering materially diverge.
5. Treat auto-created internal records as a model-preserving technique, not a shortcut: when a user selects a reusable source list, backend may create the campaign-scoped execution entity at that moment to preserve the source-list vs execution-audience boundary.
6. Avoid creating UI-term entities such as `MessageExample` when an existing domain entity or immutable snapshot already represents the concept. Document whether the UI term maps to a reusable asset, a per-run snapshot, or both.
7. Include explicit alternatives and selection conditions: recommended no-schema-change facade, enum/classification addition, metadata/provenance addition, and any small preference/metadata model that is optional rather than core.
8. Add a self-review section to the feature doc that challenges the main recommendation against the UI draft, current model intent, current implementation caps, and out-of-scope execution constraints.

## Credential reference and Secret Manager feature-plan pattern

When the user asks for a feature plan involving provider credentials, Secret Manager, credential references, runtime secret loading, user OAuth token custody, or key rotation, treat it as a security/infra feature boundary rather than only a provider implementation detail.

Canonical detail lives in `references/credential-encryption-key-management.md`. Keep this SKILL.md section as a trigger only: do not repeat the full storage table, incident-response sequence, or environment-specific recommendations here.

Quick reminders:

- Prefer `Credential Reference` / `secretRef` for the final design; use CEK/KEK terminology only for encryption internals.
- Git-tracked files should contain metadata only, never plaintext or encrypted credential blobs by default when Secret Manager/1Password/Vercel Sensitive Env exists.
- Separate system-operation credentials from user/team dynamic OAuth credentials.
- Get explicit user approval before creating or modifying any secret store, env var, KMS key, CAM role, GitHub secret, or VM env file.
- When the user asks direct review questions about credential storage, add an explicit `Q/A` section to the feature doc and link the canonical reference for rationale.

## Scope reversal / docs-only reset pattern

When the user initially asks to continue into code or implementation but then narrows the scope back to model design docs, OpenSpec, or ERD only:

1. Acknowledge the correction explicitly and stop the implementation path immediately.
2. Reset any active TODOs so code/schema/API/UI implementation items are cancelled or removed, not left in-progress.
3. Continue only with Git-tracked documentation, OpenSpec, ERD, and relevant repo-local skill/context files.
4. Before finalizing, verify the changed file list contains no source, Prisma schema, migration, fixture, generated, or test code files unless the user re-explicitly reopens implementation scope.
5. In the final report, state that implementation/code changes were intentionally excluded.

This is especially important when a product model decision affects Prisma relations: do not let the obvious next implementation step override the user's latest docs-only scope.

## Read-only entity explanation pattern

When the user asks to explain a domain entity or compare two attributes without explicitly requesting edits:

1. Treat it as a read-only model clarification task. Inspect the current source of truth before answering, usually the canonical model docs plus the live schema/service code when implementation already exists.
2. Distinguish conceptual fields from implementation relations. For example, in email sender models, explain that a `Sender`/`SenderIdentity.emailAddress` is the actual From identity, while a `Connected account` such as `GmailSenderCredential.connectedEmailAddress` is the OAuth-authenticated account that provides credentials.
3. When the question is “why does creation of X require Y?”, verify both the model contract and the actual create/read UI path. Separate a true persistence dependency such as an FK or required relation from a UX/readiness prerequisite such as “Team Company context must exist before showing a form.”
4. Call out current product constraints separately from future extensibility. If the current implementation requires two concepts to match, state that first, then explain why the model still stores them separately for aliases, delegation, shared mailboxes, or external providers.
5. If docs say an entity is not directly related but UI blocks creation until another entity exists, explain that as a product-flow or setup-readiness guard, not as a data-model dependency. Mention whether the action/service layer itself enforces the prerequisite.
6. Walk every field one by one when the user asks for “속성 전체” or equivalent, including relation fields, enum meanings, unique constraints, and indexes that materially affect behavior.
7. Keep the answer as an explanation, not a documentation PR, unless the user explicitly asks to update docs.

## Team-rooted asset relation pattern

When the user changes a domain model from user-owned or company-owned assets to Team-scoped assets:

1. Treat Team as the sharing, permission, and market-boundary root.
2. Remove direct `User` / `Owner` ownership relations from the affected reusable business asset unless the user preserves them as provenance.
3. Replace parent-company relations with direct Team ownership when the asset should be reusable across the Team rather than under one Company.
4. If Team has a 1:1 Company profile, document Campaign or execution entities as deriving company context from Team instead of selecting/storing `companyId` directly.
5. Distinguish creation blockers from execution/readiness blockers. In outbound-agent's Team-rooted model, a missing Team Company can block Campaign readiness/submission, but it must not become a hard blocker for creating Team-scoped reusable assets such as Product or Sales Person.
6. Update ERD cardinality, field contract, OpenSpec requirements, UI prerequisite text, seed/demo docs, and verification searches together; otherwise old relation assumptions survive in secondary docs.
7. Search for old FK names and prose, for example `companyId`, `ownerUserId`, `USER ||--o{ <ASSET>`, prose saying a Team-scoped asset is owned by a User/Owner, or UI copy that says to create Team Company before adding Product/Sales Person.

### Implementation follow-up checklist for Team-rooted asset changes

When the user asks to turn a design-doc PR into code changes after this model decision, apply the same boundary across the implementation rather than only editing Prisma fields:

1. Update Prisma schema and migration together:
   - Remove obsolete relation fields such as `Company.ownerUserId`, `ContactList.ownerUserId`, `Product.companyId`, `SalesPerson.companyId`, and `Campaign.companyId` when the accepted model no longer stores them.
   - Add backfill steps before `DROP COLUMN` / `SET NOT NULL` so existing rows derive `teamId` from the old owner/company relation.
   - Replace old unique constraints such as `Product_companyId_productName_key` with Team-scoped equivalents.
2. Update create paths and validators:
   - Remove obsolete form/API payload fields such as Campaign `companyId` and Product/Sales Person `companyId`.
   - Persist new rows with current Team scope and validate same-Team compatibility between remaining references such as Product and Sales Person.
3. Update read models and UI call sites:
   - Remove `include: { company: true }`, `campaign.company`, `product.company`, and `salesPerson.company` accesses once those relations are removed.
   - Replace Company selectors with Team Company context text when Company is now a Team-level profile, not a per-asset choice.
4. Update seeds/fixtures and tests:
   - Keep old fixture `companySlug` only as a consistency check if fixtures still need to prove the Team has a Company; do not write removed `companyId` columns.
   - Update structure/contract tests to assert the removed fields are absent, not merely that new fields exist.
5. Verification should include at least Prisma client generation, TypeScript typecheck, targeted contract/unit tests around the changed models, lint, and `git diff --check` before commit/push.

## Connected mailbox email provider feature-plan pattern

When the user asks for a feature plan for an Email Sender Provider that is a user/work mailbox provider, such as Gmail/Google Workspace or Microsoft Exchange Online, treat it as a connected-mailbox provider track rather than an external bulk email provider track.

Reference detail: `references/connected-mailbox-email-providers.md` summarizes the concept split, Gmail pattern, Microsoft Exchange Online pattern, and feature-plan checklist.

1. Separate three concepts explicitly: `SenderIdentity.emailAddress` is the actual From identity; the provider credential's `connectedEmailAddress` or equivalent is the OAuth-authenticated mailbox/account; the provider-specific settings/ledger hold token, quota, tenant, and provider result details.
2. State the current same-mailbox or same-address validation first when aliases/delegation are out of scope, then list alias, shared mailbox, delegated mailbox, send-as, and send-on-behalf-of as post-MVP or excluded scope unless the user explicitly asks to include them.
3. Keep connected mailbox providers distinct from external bulk providers. Do not reuse bulk-provider domain verification, DNS warm-up, or webhook reputation models for mailbox providers unless the feature specifically requires them.
4. For Microsoft Exchange Online plans, model it as a Microsoft Graph delegated-permission provider by default; call out tenant id, Microsoft user id, connected mailbox address, granted scopes, encrypted refresh credential, throttling, conditional access, tenant policy block, and mailbox-level soft cap/error normalization.
5. Include Sales Person sender binding and SendRun locked-sender validation in the plan: actual send must use the selected/locked Team Email Sender and must not fall back to the current user's mailbox or another provider.
6. Add OpenSpec, UI, `/goal`, task-breakdown, verification, and explicit out-of-scope sections so the feature plan can hand off to a later implementation without reinterpreting the provider boundary.
7. Link the new feature plan from the feature README and sprint/roadmap independent-track list when the repo uses those index documents.

## Verification searches

Run targeted content searches over docs for:

- Old section labels such as `<Entity> Setup` when the new term is `<Entity> Configuration`.
- Old grouped labels such as `A, B, C, Campaign` when Campaign is no longer part of the group.
- UI group names that still imply the old boundary.
- Old ownership or FK terms such as `companyId`, `ownerUserId`, `USER ||--o{ <ENTITY>`, or prose saying a Team-scoped asset is owned by a User/Owner.
- Common misspellings from the user prompt or prior docs, e.g. `Compaign`.

Report the absence of old contradictory terms separately from the positive new terms that remain valid.

## PR/reporting guidance

In the final report and PR body, state the model-boundary decision first:

- what now belongs to the setup/stage
- what was moved to a top-level aggregate/context model
- which dependent docs were updated
- what verification search was run

For docs-only planning PRs, `git diff --check` plus targeted text searches are usually sufficient. Do not spend time on local builds/tests unless explicitly requested.

## Pitfalls

- Do not treat an entity-boundary correction as a cosmetic rename; dependent docs and UI planning docs often need small alignment edits.
- Do not keep detailed fields for an excluded entity in the old setup/stage doc “for convenience”; that preserves the wrong model hierarchy.
- Do not over-broaden the PR into implementation scaffolding after a data model planning request.
- Do not bury the top-level aggregate/context entity inside a pipeline stage just because it references stage-specific entities.
- Do not use auto-closing issue keywords in PR bodies unless the user explicitly asks to close the issue.

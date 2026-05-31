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

## Sync Front API / async backend boundary pattern

When the user clarifies that MVP Front APIs should be synchronous while actual long-running execution will be handled by a later async backend, treat it as a source-of-truth scope boundary, not a prose-only preference.

1. Define the MVP Front API as synchronous request/response mutations for save, review, approval, and status changes: validate input, persist immediately, and return the latest entity state.
2. Exclude real email sending, LLM model calls, enrichment execution, provider callbacks/webhooks, message queues, job runners, retry/cancel/timeout, and generic Job/EventLog/Audit Event contracts from MVP implementation.
3. Keep MVP timeline/event UI as a display layer over entity status, timestamps, and manual/fixture engagement rows unless the user explicitly asks for a canonical event table now.
4. Update technology-stack and backlog docs so they no longer say initial LLM wrappers or job stubs are adopted when actual model calls and async execution are post-MVP.
5. Update phase plans so implementation PRs do not introduce `queued`/`processing` async job states or placeholder Job/EventLog tables merely to anticipate later backend work.

## Verification searches

Run targeted content searches over docs for:

- Old section labels such as `<Entity> Setup` when the new term is `<Entity> Configuration`.
- Old grouped labels such as `A, B, C, Campaign` when Campaign is no longer part of the group.
- UI group names that still imply the old boundary.
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

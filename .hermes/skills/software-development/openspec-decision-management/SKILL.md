---
name: openspec-decision-management
description: "Manage product and technical decisions in OpenSpec-backed repositories: capture accepted decisions, promote broad principles into specs, and keep related docs from drifting."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [openspec, decision-log, product-policy, documentation, spec-maintenance]
---

# OpenSpec Decision Management

Use this skill when a user makes or updates a product, technical, permission, ownership, provider, or workflow decision in a repository that uses `openspec/` as a durable specification source.

The goal is not just to write down the latest sentence from the chat.
The goal is to keep the decision traceable, accepted/rejected alternatives explicit, and active specs/docs consistent enough that future implementation agents do not reopen settled policy questions.

Role boundary:

- The Product Owner / user performs the product decision-making.
- The AI agent structures the topic, asks for missing confirmation when necessary, records the Product Owner's decision in the canonical OpenSpec location, and creates or updates the PR that carries the record.
- The AI agent must not decide between product alternatives on behalf of the Product Owner. If the agent recommends an option, record it as `Status: Proposed` or keep the entry `Status: Open` until the Product Owner accepts it.

## Triggers

Use this skill when:

- The user says they are making a decision for a GitHub issue, OpenSpec change, product policy, provider policy, Team/permission boundary, ownership model, or integration flow.
- A previously open decision in `openspec/changes/<change-id>/design.md` is now accepted or rejected.
- A user clarifies a broad product principle that affects more than one feature.
- A decision changes the interpretation of existing schema fields, roles, permissions, route boundaries, or integration ownership.
- Existing docs/specs contain stale alternatives, old role models, or contradictory wording after the new decision.

## Workflow

1. Confirm the repository guidance and worktree rule.
   - For repo work, check the current branch/status before editing.
   - If the repo requires `.worktrees/`, perform changes there, not in the root checkout.

1A. If the task is to replace or demote a long-lived `docs/**` design document with OpenSpec authority, use the doc-to-OpenSpec migration pattern.
   - Create or update a class-level `openspec/specs/contract-<topic>/spec.md` when the old doc contains cross-cutting implementation rules.
   - Convert normative prose into OpenSpec Requirements and Scenarios, not another long prose doc.
   - Shrink the original docs file into a short `Superseded by OpenSpec` bridge that links to the canonical spec and preserves only background context.
   - Update active references and OpenSpec inventory files so future agents discover the new canonical source.
   - When the migration deletes or drastically shortens an existing plan/handoff doc, preserve reviewer trust with a deletion-to-canonical-source trace: compare the old doc's removed sections/line ranges against the new OpenSpec/docs surfaces, then record a mapping table in the PR body, a reviewer issue, or a companion audit note when the user asks for traceability. Explicitly call out any details that were only partially covered or moved to non-OpenSpec docs/backlog/status files.
   - See `references/doc-to-openspec-contract-migration.md` for the detailed pattern and pitfalls.
   - See `references/deleted-plan-to-openspec-mapping.md` for a concrete mapping-table issue pattern from an Outbound Agent Sprint plan migration.
   - Run a lightweight Markdown relative-link check after moves; `git diff --check` alone does not catch stale relative links.
   - See `references/doc-to-openspec-contract-migration.md` for the detailed pattern and pitfalls.
   - Update active references and OpenSpec inventory files so future agents discover the new canonical source. For example, refresh `docs/sprint-roadmap.md`, `docs/feature/README.md`, `openspec/README.md`, and `openspec/specs/README.md` when those indexes exist.
   - After the rewrite, run lightweight Markdown hygiene: `git diff --check`, scan touched files for accidental line-number prefixes or conflict markers, and verify relative Markdown links in the touched docs.
   - See `references/doc-to-openspec-contract-migration.md` for the detailed pattern and pitfalls.

1B. If the user asks whether sprint plans or planning docs should be converted to OpenSpec, perform an authority-boundary audit before recommending edits.
   - Inspect `docs/*sprint*`, related `docs/feature/*plan*`, `docs/product-roadmap.md`, `docs/sprint-roadmap.md`, `openspec/README.md`, `openspec/specs/README.md`, `openspec/project.md`, and any existing `openspec/changes/<sprint-or-feature>/` files.
   - Classify each document by responsibility: product strategy/roadmap, sprint index, feature narrative, UI/UX review, historical done record, implementation checklist, user scenario, implementation contract, or decision log.
   - Recommend OpenSpec authority for only the normative pieces: In/Out scope, accepted decisions, SHALL/SHALL NOT contracts, GIVEN/WHEN/THEN scenarios, and implementation checklists.
   - Keep roadmap, product-value narrative, UX critique, status, and historical context in `docs/`; do not propose moving them wholesale into OpenSpec.
   - When duplicate implementation plans already exist in both `docs/` and `openspec/changes/**`, recommend shrinking the docs file to a bridge/summary and making the OpenSpec change/spec/tasks the canonical implementation source.

2. Locate the canonical decision home.
   - Prefer `openspec/changes/<change-id>/design.md` for change-specific decision logs.
   - Use `openspec/project.md` for broad project principles.
   - Use `openspec/specs/**/spec.md` for durable implementation requirements and scenarios.
   - Use feature docs only as secondary consistency surfaces; do not make them the only source of truth.

3. Update the decision log.
   - If the user says they will decide, identifies a decision topic, or provides alternatives but does not choose one yet, still create/update the decision record as `Status: Open` / `Decision: TBD` so the canonical OpenSpec location exists before implementation work continues.
   - Change `Status: Open` / `Decision: TBD` to `Status: Accepted` only when the user has clearly decided.
   - Write the accepted decision as one direct sentence or short paragraph.
   - Keep rejected alternatives visible when helpful, but mark them as `Rejected` instead of leaving them as open choices.
   - Add rationale that cites the product principle, schema evidence, operational boundary, or user-stated policy.

4. Promote broad principles into general specs.
   - If the decision is broader than one feature, add it to `openspec/project.md` or the relevant base `openspec/specs/**/spec.md`.
   - Express durable contracts with `SHALL`, `SHALL NOT`, `MAY`, or `MUST`.
   - Add `GIVEN` / `WHEN` / `THEN` scenarios so future code/tests can validate the decision.

5. Add feature-specific contract only where needed.
   - For provider/integration decisions, update the related change spec under `openspec/changes/<change-id>/specs/**/spec.md`.
   - Avoid duplicating the entire general principle; reference it and add only feature-specific behavior.

6. Sweep stale docs and implementation surfaces for contradictions.
   - If the user says to update design/docs first and then code in one PR, preserve that sequence: make the OpenSpec/domain/UI documentation edits first, then implement schema/UI/test cleanup in the same branch/PR rather than splitting the work unless asked.
   - For decisions that move a setting from child objects to a parent scope, search both names and concepts: old role names, alternatives, permission models, decision labels, schema fields, seed fixtures, UI labels, tests, implementation helpers, and user-facing copy that could still imply child-level overrides.
   - Search for old role names, alternatives, permission models, decision labels, schema fields, seed fixtures, UI labels, tests, and implementation helpers that contradict the accepted policy.
   - Update adjacent docs enough that reviewers do not see two competing policies.
   - For UI flows where a required selector can send the user to a different settings/create screen, record the dependency selector as the first form step before fields that could be lost, add an explicit dropdown/menu action for creating the missing dependency, and move long explanatory policy copy to the owning settings surface instead of the transient creation form.
   - For route/auth/provider decisions, check all affected documentation layers together: canonical `design.md`, user-facing `uc-*` spec, implementation `contract-*` spec, feature/UI docs, environment/operator docs such as Google Console redirect URI or local/dev/prod credential setup, and `tasks.md`.
   - When updating `tasks.md`, distinguish documentation follow-through completed in the current PR from future implementation work; do not mark implementation/testing tasks complete merely because the decision was recorded.
   - When an issue-driven implementation PR advances one concrete OpenSpec contract gap, it is acceptable to update the related `tasks.md` checkbox and short feature-doc status in the same PR if the user explicitly asked for implementation plus documentation updates. Mark only the exact regression/evidence now covered; leave broader snapshot/approval-lock tasks open if they are not fully proven by the patch.
   - If the user asks to implement the decision to Release Ready, do not stop at OpenSpec/docs: remove or update stale product guards, schema/fixture fields, baseline migration definitions, UI copy, and regression tests that still enforce the rejected policy.
   - It is acceptable to include small doc consistency edits in the same OpenSpec decision PR when the user asked for the decision/spec update and those docs would otherwise contradict the new source of truth.

7. Create or update the PR and tracking surfaces.
   - The required deliverable is a branch/PR carrying the canonical decision record; do not stop at an issue comment or chat summary.
   - If a GitHub issue prompted the decision, comment on the issue with the PR link and concise accepted policy.
   - If a PR already exists for the OpenSpec change, update its body after the decision expands scope.
   - Do not use auto-closing keywords unless the user explicitly asks to close the issue.

8. Verify and report.
   - Run lightweight docs verification such as `git diff --check`.
   - For docs-only PRs, CI scope detection plus skipped app CI can be sufficient if repository norms prefer avoiding local builds.
   - Report PR URL, issue comment URL, commit SHA, and CI state.

## Decision record shape

Use this structure inside `design.md` when possible:

```md
### Decision: <short name>

Status: Accepted
Decision: <accepted policy in one direct sentence or paragraph>
Related issue item: GitHub issue #<n> `<label>`

#### Question

<the original question>

#### Rationale

<why this policy is right, including product principle or schema evidence>

#### Current schema evidence

- `<Field>` means ...

#### Alternatives

- Accepted: <chosen alternative>
- Rejected: <alternative and why it was rejected>

#### Implementation impact

- <contract / UI / API / migration impact>

#### Recording rule

<this decision follows the broader spec at ...>
```

## Pitfalls

- Do not wait for a final answer before creating a decision record when the user has explicitly named the decision topic and options; use `Status: Open` / `Decision: TBD` until the accepted policy is provided.
- Do not mark a decision as `Accepted` because the agent thinks one option is better; only the Product Owner's explicit decision or confirmation can move an entry to `Accepted`.
- Do not let the workflow end with a chat answer, local file edit, or issue comment only; create or update the PR that records the decision unless the user explicitly asks not to.
- Do not leave `Status: Open` or `Decision: TBD` after the user clearly decides.
- Do not bury a broad product principle only inside a feature-specific Gmail/provider decision.
- Do not preserve stale alternatives as if implementation still needs to choose among them.
- Do not leave old docs saying `Viewer`, per-asset permission, or user-scoped ownership if the accepted policy removed those concepts.
- Do not treat “post-MVP” as “prepare extension points now.” If the user says they will accept the future design/development cost, keep the current OpenSpec simple and avoid future-compatible abstraction, placeholder state, compatibility layers, extra enum states, adapter hooks, provider-specific failure reasons, or UI placeholders. If useful, explicitly state that the current MVP contract does not guarantee a natural migration path for that future capability.
- Do not add implementation code when the user asked only to record an OpenSpec/product decision. If the user explicitly asks to implement the decision to Release Ready, code/schema/test cleanup that removes the rejected policy is part of the decision follow-through, not scope creep.
- Do not preserve a rejected restriction as a narrower “test-only” rule unless the user explicitly chose that split. When the accepted policy says the product should not consider a restriction, remove the corresponding helper, schema, seed, UI, and docs instead of leaving dormant settings that imply the old policy still exists.
- Do not put long ownership/reuse/setup explanation on a transient create form when the user should configure the reusable dependency elsewhere; put that copy on the owning settings/configuration surface and make the create form expose a short, direct add action.
- Do not auto-close issues from PR body text unless explicitly instructed.

## References

- `references/outbound-agent-team-shared-sender-decision.md`: concrete example of turning a Gmail OAuth sender decision into a broad Team shared-workspace product spec and sweeping stale docs.
- `references/outbound-agent-recipient-range-decision.md`: example of a decision that removed a recipient allowlist policy and therefore required OpenSpec, docs, schema, seed, UI, helper, and regression-test cleanup.
- `references/outbound-agent-oauth-shared-callback-decision.md`: example of recording a Team-scoped OAuth entry + shared callback route decision across design, UC spec, contract spec, GCP/OAuth setup docs, and tasks.
- `references/outbound-agent-sendrun-approval-lock-decision.md`: example of an approval-boundary lock decision where sender/template/recipient preview is confirmed before approval and batch-time fallback/late assignment must be prohibited.
- `references/outbound-agent-sales-person-gmail-sender-decision.md`: example of binding a provider sender to a reusable Sales Person entity while keeping OAuth authentication owned by the actual Gmail account holder, not the current user by default.
- `references/outbound-agent-sales-person-email-sender-selection-flow.md`: example of refining a Sales Person creation UI so a required Email Sender dependency is selected/added first, with long policy copy moved to Team Settings.
- `references/outbound-agent-team-market-settings-decision.md`: example of moving country/language from multiple child entities to a single Team-scoped market setting, requiring OpenSpec/domain/UI docs first and then schema/UI/test cleanup in one PR.

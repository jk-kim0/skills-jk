# Outbound Agent Team Market Settings Decision

Use as a concrete example when a product requirement changes where country/language (or a similar market/configuration axis) is owned.

## Accepted policy captured

- Country and language are Team settings.
- One Team uses a single country/language configuration across the workspace.
- Company, Product, Sales Person, Contact List, Campaign, Audience, Email Template, and similar child objects do not define independent country/language settings unless a future accepted decision explicitly reopens that model.
- UI copy and flows should refer to the Team market/context instead of asking for per-object market selection.

## Follow-through surfaces that needed coordinated updates

When this class of ownership change is accepted, update documentation first, then implementation in the same PR if the user asks for both:

1. Canonical OpenSpec surfaces
   - `openspec/project.md` for durable product principles.
   - Relevant `openspec/specs/**/spec.md` requirements/scenarios for the invariant.
   - Relevant `openspec/changes/<change-id>/design.md` or change specs for the accepted decision and impact.
2. Design/domain documents
   - Domain model docs that describe entity ownership and attributes.
   - UI design docs for create/edit/settings flows.
   - User-facing docs that mention where country/language is configured.
3. Implementation surfaces
   - Schema/fixture/seed fields that previously stored per-object market settings.
   - Create/edit forms that collected country/language on child objects.
   - Derived display/copy that should read Team country/language.
   - Tests that assumed child-level country/language.

## Pitfalls

- Do not leave per-object selectors in create flows after the decision moves the setting to Team scope; they imply unsupported overrides.
- Do not only update the Team settings UI. Search child entities and docs for stale references to independent `country`, `language`, `locale`, or market settings.
- Do not split docs and code across different PRs if the user explicitly requested a single PR with design/docs first and code second; use commit/order discipline inside one PR instead.
- Do not encode fresh-worktree dependency failures such as missing `node_modules` as durable guidance. Report them as verification limitations for that PR only.

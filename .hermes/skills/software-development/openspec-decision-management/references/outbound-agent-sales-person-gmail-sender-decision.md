# Outbound Agent: Sales Person-bound Gmail sender decision example

Use this reference when a product decision binds an integration credential or sender identity to a reusable business entity rather than the current user.

## Decision pattern

In `querypie/outbound-agent`, the Product Owner clarified that the Gmail sender for Template Email Campaigns is determined by the Campaign's Sales Person setting.
The sender is not implicitly the current user's personal Gmail address.
A Sales Person may represent another Team member, and the Gmail/Google Workspace address may belong to that other Team member.
OAuth authentication must be performed by the Team member who actually controls that Gmail address.
The product must not let a different user authenticate or store their own Gmail OAuth token as if it were that Sales Person's credential.

A later UX clarification separated two layers that are easy to confuse:

- Team Settings may own the Team-scoped provider registry/connection surface, such as Gmail OAuth sender identities that the Team can choose from.
- Sales People / Sales Person settings own the business sender persona and the selected sender identity used for Campaigns and SendRuns.

Therefore a Team Settings button should be framed as an admin/provider connection inventory, not as the primary place where a Sales Person's campaign sender is chosen.
If the live UI label reads like "Team email sender settings", inspect and update the route/copy so users understand it manages provider-backed sender identities, while the Sales Person form selects one of those identities.

## Canonical record shape

Add an accepted decision to the active change `design.md`, not only to feature docs.
A good decision entry includes:

- Question: whether the actual sender is the current user connected account or the Campaign Sales Person sender.
- Decision: Sales Person's configured Gmail address is the actual From sender.
- Rationale: Sales Person is a reusable seller-side identity; Campaigns can be operated on behalf of another Team member; OAuth consent remains the credential owner's responsibility.
- Rejected alternatives:
  - current-user sender fallback
  - admin-delegated authentication
  - free-form From override detached from Sales Person
- Implementation impact:
  - Sales Person form shows sender display name and Gmail address.
  - Sales Person form should choose from Team sender identities rather than accepting a detached free-form email address.
  - Team Settings may expose the OAuth/provider connection inventory, but it should not look like the main Campaign sender decision UI.
  - Sales Person persona fields such as profile image, personality notes, and signature belong with the reusable Sales Person entity, not with provider credential setup.
  - Campaign setup and SendRun approval resolve and lock sender from the Sales Person's selected sender identity, never from current user fallback or string-only email matching.
  - not-connected/auth-required Sales Person senders block test send, approval, and actual send.

## Surfaces to update together

For this class of decision, sweep both broad product/spec layers and UI/implementation handoff layers:

- `openspec/project.md` for the broad principle.
- Base schema/domain spec, e.g. `openspec/specs/contract-mvp-domain-schema/spec.md`.
- Active change decision log, e.g. `openspec/changes/<change-id>/design.md`.
- User-story spec, e.g. `specs/uc-*/spec.md`.
- Implementation contract spec, e.g. `specs/contract-*/spec.md`.
- Active change `tasks.md` for documentation follow-through.
- Feature plan and implementation plan.
- Provider-specific design docs.
- UI design docs for Team Settings provider registry, Sales People list/create flow, Sales Person detail/edit flow, and SendRun approval/preview screens.
- Schema/model docs if the reusable entity field meaning changes.
- Focused regression tests for sender identity listing, Sales Person sender selection, and SendRun sender resolution.

## Pitfalls

- Do not collapse sender selection into “the current user connects Gmail” just because OAuth is session-based.
- Do not treat Team-shared sender usage as permission to let one Team member create another member's OAuth credential.
- Do not leave UI copy saying “connect your Gmail” where the required action may be “the Sales Person Gmail address owner must authenticate.”
- Do not make Team Settings appear to be the place where Campaign sender persona is configured; reserve it for Team-scoped provider connection/identity inventory and point sender choice back to Sales Person settings.
- Do not add a free-form From override as a shortcut; it breaks audit, same-address validation, and Sales Person semantics.
- Do not rely on raw email string matching for send-time resolution once a first-class sender identity exists; bind by sender identity relation and treat email/address as display/provider data.
- Do not update only the email feature docs; the Sales Person entity contract and UI setup docs also need to change.

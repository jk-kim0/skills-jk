# Provider OAuth Create Card Pattern

Use this reference for outbound-agent settings pages where a provider-backed entity is created through OAuth and the user cannot know or supply the final provider identity until the callback.

## Pattern

- Show an always-visible Optional Create card for each currently supported provider type.
  - Example: Email Sender currently supports only Gmail, so show one Gmail Account based Sender card.
  - Future provider types should add more provider-specific cards instead of turning the current card into a generic form.
- Do not ask the user for the provider email address before OAuth if the provider callback is the source of truth.
- Start OAuth from the card action and create the entity only after the callback has returned verified provider identity information.
- At callback time, use the verified provider email to check for an existing, not-deleted entity in the same Team/scope.
  - If one exists, fail creation with a clear duplicate error such as “already exists” and do not attach/overwrite credentials.
  - Do not silently treat duplicate OAuth as reconnect unless reconnect was explicitly designed for that entity type.
- For created entities that are intended to be removed rather than disconnected, expose Delete only; omit Disconnect/reconnect controls.

## Delete policy review

Before implementing Delete, review the entity model and foreign key boundaries:

- If historical/operational rows can keep nullable references or otherwise remain valid after sender removal, prefer hard delete for the settings entity.
- If downstream invariants require the entity row to remain addressable, use soft delete, but do not design a restore path unless the product explicitly asks for resurrection.
- Document the chosen policy in both model docs and OpenSpec/design docs so reviewers can verify why Delete is hard or soft.

## Documentation/spec checklist

- UI design doc: describe the Optional Create card as always visible, provider-specific, and callback-created.
- Feature/model docs: state where verified provider identity comes from and how duplicate active provider identities are rejected.
- OpenSpec design/spec: add SHALL scenarios for provider card visibility, callback-based creation, duplicate rejection, and delete-only behavior.
- PR body `UI 변경`: include the exact Team-scoped settings route using demo slugs, e.g. `/sales-demo/settings/email-senders`.

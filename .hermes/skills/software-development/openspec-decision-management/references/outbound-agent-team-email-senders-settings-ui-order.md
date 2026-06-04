# Outbound Agent: Team Email Senders settings UI order decision

Use this reference when recording UI/OpenSpec decisions for `/{teamSlug}/settings/email-senders` or similar Team-scoped settings pages that render Entity Card-style registries.

## Decision pattern

- If a settings page already has an AppShell Content Container and Page Header, do not add a second large wrapper box/panel around the entire card list unless it has a distinct responsibility.
- Keep route-level explanation near the Page Header. For Email Senders, `Manage connected sender identities for {teamName}.` is appropriate because it accurately scopes the page to the current Team's connected sender identity registry.
- If the page needs policy/help copy such as “Sales Person email is selected from Team Settings Email Senders” and “one Email Sender can be reused by multiple Sales Person personas,” put it as screen-level help under the Page Header, not inside the card-list wrapper.
- The default object order for Team Email Sender cards is the backend API response order. UI should not invent a default sort by name, created date, status, connected state, or email address.
- If the current user's email account matches one or more Email Sender cards, stable-partition those matching cards to the front while preserving API response relative order within both the matching and non-matching groups.
- If there are zero current-user matching cards, render a required-creation/add-settings guide card in the first card slot. This card is not a real Entity Card: do not expose detail, drag, selected/included, or sender-status affordances.

## Documentation surfaces to update

- `docs/ui/<route-specific-doc>.md` for the route-level UI design.
- `docs/ui/README.md` so future agents discover the new UI design doc.
- The relevant feature doc, e.g. `docs/feature/(email)-gmail-email-sending.md`, when the UI is part of a feature surface.
- `openspec/changes/<change-id>/design.md` with an Accepted decision when the Product Owner has clearly chosen the policy.
- `openspec/changes/<change-id>/specs/**/spec.md` with SHALL/SHALL NOT requirements and GIVEN/WHEN/THEN scenarios.

## Pitfalls

- Do not treat “API response order” as permission for a UI-side default sort. It means the backend owns ordering based on request/team context.
- Do not collapse “no current-user matching sender” into passive empty text. If the user must add or connect a sender for their account, use a required-creation card.
- Do not repeat long Team Email Sender reuse policy copy on Sales Person creation forms; keep it on the Team Email Senders settings surface and provide only concise select/add actions elsewhere.

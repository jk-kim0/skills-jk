# Outbound Agent Gmail sender disconnect UI pattern

Use this reference when an Outbound Agent request changes the Team Email Senders settings lifecycle UI or the Gmail credential connect/reconnect/disconnect contract.

## Product contract

- Team Email Senders settings owns Gmail credential lifecycle.
- Sales Person records and approved SendRun snapshots may reference the same `SenderIdentity.id`, so disconnect must not replace or delete the sender identity itself.
- A Gmail sender row that is `active` and has stored Gmail credential material should show `Disconnect`, not another `Connect Gmail` CTA.
- A Gmail sender row that is missing credential material or has a non-active status such as `auth_required`, `quota_blocked`, `cooldown`, or `disabled` should show `Connect Gmail` / reconnect.
- Disconnect removes provider credential material and moves the sender out of the actual-send eligible path, typically by setting `SenderIdentity.status` to `disabled`.
- Reconnect should preserve the existing `SenderIdentity.id` and replace/create the credential for that identity.

## Implementation shape

- In `front/src/features/email-sending/service.ts`, add a Team-scoped service that:
  - uses `getMutableTeamScopeForUserByTeamId`;
  - finds the Gmail `SenderIdentity` by `id`, Team scope, and `providerType: "gmail"`;
  - includes `gmailCredential` so the update can conditionally delete the relation;
  - updates the sender to `status: "disabled"`;
  - deletes `gmailCredential` only when one exists;
  - returns the sender with credential relation included for consistency.
- In `front/src/app/actions.ts`, add a server action that:
  - requires the current user;
  - resolves the Team from submitted `teamSlug`;
  - calls the service with `membership.teamId` and `senderIdentityId`;
  - revalidates `/{teamSlug}/settings/email-senders`;
  - redirects back with a non-secret query status such as `?gmail=disconnected`.
- In `front/src/app/[teamSlug]/settings/email-senders/page.tsx`, compute a row-level boolean similar to `isConnectedGmailSender = providerType === "gmail" && status === "active" && gmailCredential`.
- Render `Disconnect` as a form submit for connected Gmail rows, and keep `Connect Gmail` links for non-connected/non-active rows.
- Keep viewer/read-only members disabled for mutation actions.

## Source-level regression checks

When the repo uses source-contract Vitest tests for UI/server-action contracts, add or update checks in `front/src/features/email-sending/sender-identities.test.ts` that assert:

- the Email Senders page contains the connected-row discriminator such as `isConnectedGmailSender`;
- the page references `disconnectGmailSenderAction`;
- the visible action label/title includes `Disconnect` / `Disconnect this Gmail sender`;
- the service body for `disconnectGmailSenderIdentityForTeam` uses Team mutable scope, restricts to `providerType: "gmail"`, touches `gmailCredential`, deletes credential material, and sets `status: "disabled"`.

## Documentation/OpenSpec surfaces

Update all three surfaces in the same PR when the user explicitly asks for UI design, OpenSpec, and code together:

- `docs/ui/email-template-campaign.md`: Team Settings Email Senders UI row behavior.
- `openspec/changes/sprint-3-working-email-sending/design.md`: Gmail credential revocation/reconnect/disconnect decision and implementation impact.
- `openspec/changes/sprint-3-working-email-sending/specs/contract-working-email-sending-mvp/spec.md`: SHALL requirement and GIVEN/WHEN/THEN scenario for connected row showing Disconnect.

## Pitfalls

- Do not delete `SenderIdentity` on disconnect; preserve references from Sales Person and approved SendRun snapshots.
- Do not show another `Connect Gmail` CTA for a row that already has an active credential; that reads as an unconnected sender.
- Do not store or display OAuth code, access token, refresh token, encryption secret, or credential material in UI status/query strings.
- Do not split the docs/spec/code updates when the user explicitly requested one PR for the whole change.
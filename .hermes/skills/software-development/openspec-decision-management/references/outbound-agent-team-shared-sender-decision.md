# Outbound Agent Team-scoped sender decision example

This reference captures a reusable pattern from an `outbound-agent` OpenSpec decision session.

## Situation

The user decided the Gmail OAuth connection unit for issue #145:

- Gmail OAuth connected accounts are Team-scoped senders.
- A sender used by a Team is a Team asset.
- All active Team members can use shared Team senders.
- If a sender or work asset must not be shared with the current Team, the product answer is to create a separate Team.
- The Team feature intentionally avoids complex permissions.
- Team Owner may add/exclude members; aside from that, Team members have equal work permissions and can delegate work to one another.

## Documentation actions taken

A narrow Gmail decision was promoted into a general product spec because it expressed the core Team principle.

Updated surfaces included:

- `openspec/project.md`
  - Added Team as a shared workspace and delegation boundary.
  - Added that Team assets are shared and non-shared assets require a separate Team.

- `openspec/specs/contract-mvp-domain-schema/spec.md`
  - Added `Requirement: Team shared workspace and flat work permissions`.
  - Added scenarios for shared Team assets, Owner-only member add/exclude, and separate-Team separation.

- `openspec/changes/sprint-3-working-email-sending/design.md`
  - Changed `Gmail OAuth 연결 단위` from `Status: Open` / `Decision: TBD` to `Status: Accepted`.
  - Marked Team-scoped sender as accepted and user-scoped/hybrid options as rejected.

- `openspec/changes/sprint-3-working-email-sending/specs/contract-working-email-sending-mvp/spec.md`
  - Added `Requirement: Team-scoped Gmail sender ownership`.
  - Added scenarios that a Team member can use a Team Gmail sender and that per-sender permissions are not supported.

- Related docs such as Team feature design, backlog requirements, auth requirements, and UI docs.
  - Removed stale `Viewer` / read-only member model references.
  - Removed stale role-change/per-asset/per-sender permission assumptions.

## Reusable lesson

When a feature-specific decision reveals a broad product principle, do not only patch the feature decision log.
Promote the principle into the base OpenSpec project/spec contract, then sweep adjacent docs for contradictory historical wording.

For this class of task, stale contradictions are often in:

- `docs/feature/*team*`
- `docs/backlog-requirements.md`
- `docs/user-auth-requirements.md`
- `docs/ui/*.md`
- change-specific `openspec/changes/**/design.md`
- change-specific `openspec/changes/**/specs/**/spec.md`

## Search terms that exposed stale docs

Useful patterns:

- `Viewer`
- `read-only member`
- `per-sender`
- `per-asset`
- `role override`
- `역할 변경`
- `access_limited`
- `Member/Viewer`
- `조회할 수만`

## PR/issue hygiene

- Update the existing OpenSpec decision PR if one is already open for the same decision scope.
- Update the PR body after the decision expands from a narrow feature item into a broad product principle.
- Comment on the originating issue with the accepted policy and PR link.
- Avoid auto-closing issue keywords unless explicitly requested.
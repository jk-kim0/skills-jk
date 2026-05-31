# Feature Status Doc Authoring

Use this reference when converting a GitHub issue, blocker note, or scattered implementation evidence into a per-feature status document such as `docs/feature/status-*.md`.

## Goal

Create a compact, code-backed status file that lists everything currently implemented or missing for one feature area, without turning the document into an issue narrative or duplicating long aggregate status tables.

## Recommended workflow

1. Start from the latest base branch evidence, not only the issue body.
   - Fetch/rebase against `origin/main` before editing if the task will become a PR.
   - Treat the issue as a question set and stale blocker source, not as canonical truth.
2. Inspect existing status-doc conventions before writing.
   - Look for `docs/feature/status-*.md`, `docs/feature/README.md`, and aggregate docs such as `docs/feature-status.md`.
   - Mirror the local heading/status vocabulary if a sibling feature status doc already exists.
3. Audit implementation evidence by layer.
   - Schema/models and seed data
   - Domain/service code
   - API routes/server actions
   - UI routes/navigation
   - Tests and fixtures
   - Docs that define out-of-scope or promotion criteria
4. Classify each item explicitly.
   - Implemented and reachable in the product flow
   - Implemented but lower-level/internal only
   - Fake/local/test-only
   - In progress or promotion-blocked
   - Missing/not started
   - Out of MVP scope
5. Make the status doc discoverable.
   - Add/update the local feature index if present.
   - If an aggregate status document already has detailed rows for the same feature, replace long duplicate detail there with a concise pointer to the per-feature status doc.
6. Keep evidence close to each claim.
   - Prefer exact file paths and current behavior over broad summaries.
   - Avoid saying production-ready unless live/provider/external evidence exists where relevant.
7. Use promotion criteria as the closing section.
   - List concrete conditions that would move the feature from In-Progress/Partial to Released.

## Useful document shape

```md
# <Feature> Feature Status

_Last updated: YYYY-MM-DD_

## Summary

- Current status: <Released | In Progress | Partial | Planned>
- Scope: <what this feature area includes>
- Conservative boundary: <why it is not more complete, if applicable>

## Implemented

| Area | Status | Evidence |
| --- | --- | --- |
| <capability> | Implemented | `<path>` ... |

## Partial / In Progress

| Area | Current behavior | Remaining gap |
| --- | --- | --- |

## Missing / Not in Scope

- <item> — <why / reference>

## Promotion criteria

- [ ] <specific evidence or implementation condition>
```

## Pitfalls

- Do not copy an issue body directly into a status doc.
- Do not duplicate detailed feature rows in both an aggregate status file and the per-feature status file; keep one source of detail and link to it.
- Do not treat design docs, desired UX, or issue comments as implementation evidence.
- Do not omit test-only/fake-local boundaries; they are often the difference between implemented code and user-facing production readiness.

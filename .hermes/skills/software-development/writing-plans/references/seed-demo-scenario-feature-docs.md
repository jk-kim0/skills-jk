# Seed/demo scenario feature documentation

Use this reference when a user asks to design or document default local/dev seed data, demo fixtures, or scenario population rules before implementation.

## Pattern

1. Treat the request as a documentation/planning task unless the user explicitly asks to edit fixtures, Prisma schema, or seed code.
2. Inspect the current source of truth before writing:
   - existing seed/demo docs under `docs/`
   - feature index docs such as `docs/feature/README.md`
   - fixture files such as `front/fixtures/*.json` and `front/fixtures/*.csv`
   - seed entrypoints such as `front/prisma/seed.ts`
   - schema fields that affect the proposed data shape, such as Team country/language/timezone fields
   - importer code or parser schemas that define canonical CSV field names
3. Reconcile the new scenario with existing decisions instead of replacing them silently. If an older seed scenario exists, state whether the new document extends it, supersedes it, or leaves it as product/campaign detail.
4. Write the feature document with these sections when applicable:
   - document purpose and current seed baseline
   - demo scenario summary table
   - entity-by-entity seed rules
   - conceptual fixture shape, clearly marked non-binding if schema is not final
   - demo flow from login/team context through the target surfaces
   - seed execution boundaries: local/dev only, no production fixture loading, no external provider activation by seed alone
   - implementation considerations and unresolved questions
   - completion criteria
5. If the repo has a feature index, update it in the same docs-only PR so the new document is discoverable.
6. Commit and open a docs PR when the repo workflow expects PRs for planning docs. Do not run full local build/test for docs-only changes unless requested; use lightweight checks such as `git diff --check` and then let CI run.

## Decision/question handling

When the user explicitly asks you to ask questions for scenario detail, include a dedicated `확인 필요 질문` / `Open questions` section in the document and also summarize those questions in the final reply.

Prefer concrete default proposals inside the doc rather than only open-ended questions. Example shape:

- “Default proposal: seed `sales-demo` as Owner for all demo Teams.”
- “Question: should `admin` also be Owner or only Member?”

## Timezone seed notes

For Pacific Time / DST scenarios, store IANA timezone IDs such as `America/Los_Angeles` instead of abbreviations like `PDT` or `PST`. Runtime display can compute PST/PDT based on date.

If the current schema has no Team default timezone field, document implementation choices separately: add a field, derive campaign defaults from country constants, or keep timezone only on Campaign/Sales Person calendar context until settings schema exists.

## Contact-list CSV fixture guidance

When the demo scenario uses a CSV fixture for contact import or sample recipients, make the file match the application's canonical import contract, not the shape of the raw source list.

Recommended steps:

1. Inspect the importer or documented template to identify canonical headers and order.
2. Convert source fields to canonical names, for example:
   - `fullName`
   - `familyName`
   - `givenName`
   - `email`
   - `roleTitle`
   - `companyName`
   - `companyDomain`
   - `department`
   - `notes`
3. Quote all CSV fields when that makes review easier and avoids escaping edge cases in names, titles, and notes.
4. Keep `email` as a plain deliverable email address. Do not put `mailto:` URLs or other source-link syntax in canonical email fields.
5. If a source value is useful but not canonical, preserve it in `notes`, for example `sourceMailto=mailto:person@example.com`.
6. Validate with a lightweight parser check for header order, row count, required fields, duplicate or excluded contacts, and email shape before committing.

In the feature document, distinguish between:

- demo Team members / Sales Persons who can own or operate demo flows; and
- imported Contact List staff/recipient fixtures that appear as target data.

If the same human appears in multiple Teams, document whether that means one reusable Sales Person entity with multiple team memberships or separate per-team fixture rows. If a user removes a person from the contact fixture but keeps them as a Sales Person, call out that the two fixture roles are independent.

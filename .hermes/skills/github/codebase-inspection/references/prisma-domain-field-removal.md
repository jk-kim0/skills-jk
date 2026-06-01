# Prisma-backed domain field removal checklist

Use this reference when a domain attribute is removed or collapsed into another concept in a Prisma/TypeScript repository, such as removing legacy `Team.type` values (`personal`, `collaboration`) after deciding Team is a unified entity.

## What to verify

1. Prisma schema/model
   - Remove the field and any enum only if no remaining model uses it.
   - Check seed data, fixtures, migrations, and schema comments.

2. Generated-client call sites
   - Search not only for domain semantics, but also stale ORM projections:
     - `type: true`
     - `select: { ... }`
     - `include: { ... }`
     - `where: { type: ... }`
     - `orderBy: { type: ... }`
   - TypeScript build failures often surface as Prisma `TeamSelect<DefaultArgs>` errors when a removed field remains in a `select` object.

3. Service/defaulting logic
   - Re-check helper functions that choose defaults, such as `getDefaultTeamForUser()` or current-user/team bootstrap services. These often select fields that are no longer used by the UI.

4. API, UI, and docs
   - Remove user-facing copy that still describes the old variants.
   - Update requirements/spec docs to state the new unified concept positively.

5. Verification
   - Run a narrow source-contract/type check when available.
   - If CI fails after the initial cleanup, inspect cache-only/Docker build logs for TypeScript errors; stale Prisma `select` fields can be caught there even when a narrower search missed them.

## Failure signature

Example TypeScript/Prisma failure shape:

```text
Object literal may only specify known properties, and 'type' does not exist in type 'TeamSelect<DefaultArgs>'
```

This means the schema/type removal succeeded, but a call site still asks Prisma to select the removed field. Fix the call site; do not reintroduce the field just to satisfy the query.

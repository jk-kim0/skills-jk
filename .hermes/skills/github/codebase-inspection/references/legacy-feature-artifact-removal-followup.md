# Legacy feature artifact removal follow-up

Use this reference when a prior docs/OpenSpec PR accepts removing a legacy feature concept and the follow-up task is to remove remaining implementation artifacts.

## Pattern

1. Start from latest `origin/main` in a repo-local worktree.
2. Read the accepted decision text and implementation-impact checklist before editing.
3. Search broadly for exact legacy identifiers and user-facing copy, not only service code. Include:
   - Prisma schema enums/models/defaults/relations
   - migrations and repair SQL
   - seed scripts and fixture schemas
   - YAML/CSV demo fixtures
   - route handlers/server actions
   - UI pages and public docs copy
   - E2E helpers and structure/source tests
4. For Prisma enum/model removal:
   - delete dependent rows first in the migration
   - drop dependent tables before dropping enum types
   - recreate enum types when removing a value from PostgreSQL enums
   - update schema defaults from the removed enum value to the remaining canonical provider
5. For demo seed removal:
   - remove fake/local identities from sender fixtures
   - convert demo SendAttempt examples to a real-provider blocked state when the product still needs a “not ready because auth is missing” demo
   - remove fixture schema fields for deleted legacy event ledgers/settings
6. For UI/action/API cleanup:
   - remove action handlers and route handlers that execute the deleted flow
   - repurpose listing pages as history/inspection pages only when the route remains useful
   - remove copy that implies the legacy concept still exists
7. Update source/contract tests so they assert absence of the deleted identifiers and validate the new canonical boundary.
8. Verify with targeted tests, targeted lint, and `git diff --check`. If full Prisma/typecheck commands fail because generated client or shared dependency setup is missing, report that as a verification limitation and rely on CI for full validation.

## Pitfalls

- Do not leave a removed enum value as the default on a Prisma model.
- Do not keep fixture schema support for deleted YAML fields; otherwise seed fixtures can silently reintroduce the concept.
- Do not preserve message-level fake send APIs just because a send-attempt history page still exists.
- Do not edit old baseline migrations unless the repo convention explicitly permits rewriting history; add a forward migration instead.

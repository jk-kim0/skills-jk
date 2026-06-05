# Outbound Agent baseline-only DB migration cleanup

Use this reference when cleaning up Outbound Agent Prisma migration/backfill history after a non-compatible baseline reset decision.

## Durable pattern

- Keep `front/prisma/migrations/20260530000100_baseline_main_schema/migration.sql` as the single current-schema baseline migration artifact.
- Remove intermediate Prisma migration directories once their DDL has been absorbed into the baseline.
- Remove one-off `front/prisma/backfills/**` and `front/prisma/repairs/**` artifacts from the clean-install path.
- Do not keep a workflow step that iterates `prisma/repairs/*.sql` after the project has moved to baseline-only installs.
- For an existing shared dev DB that differs from the baseline, use the approved reset path (`reset_database=true`) to run `prisma migrate reset --force` plus seed, then schema check. Do not add new repair/backfill SQL merely to preserve old migration history.
- If an implementation plan is completed, move the plan from `docs/feature/` to `docs/done/`, set `상태: Done`, add concise completion evidence, and update indexes/status docs such as `docs/feature/README.md` and `docs/feature-status.md`.

## Verification checklist

- `find front/prisma/migrations -mindepth 1 -maxdepth 1 -type d` shows only the baseline directory.
- `front/prisma/backfills` and `front/prisma/repairs` do not exist.
- Search for `@default(cuid())`, `cuid(`, `autoincrement(`, `@default(uuid())` in `front/prisma`, `front/src`, and fixtures; only absence assertions should remain.
- Check every independent model `id` line in `schema.prisma` has `@default(dbgenerated("uuidv7()")) @db.Uuid`.
- Check internal relation scalar `*Id String` lines have `@db.Uuid`, excluding external provider/message/correlation IDs.
- Compare the committed baseline body to `prisma migrate diff --from-empty --to-schema prisma/schema.prisma --script`, while preserving any deliberate prelude such as a PostgreSQL 17-compatible `uuidv7()` helper.
- Run focused tests: `npm run prisma:validate` and the UUID/schema migration artifact tests.

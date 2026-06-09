# Baseline-only DB install cleanup pattern

Use this reference when Outbound Agent is intentionally reset to a clean-install database contract instead of preserving migration/backfill history.

## Goal

A new database should install with one Prisma baseline migration and one seed run.
Intermediate migration directories, one-off backfill SQL, and shared-DB repair SQL should not remain as install-path artifacts when the product decision is to recreate/reset rather than preserve existing rows.

## Implementation pattern

1. Regenerate the current-schema baseline SQL from the Prisma schema:
   - `cd front`
   - use Node 24 for Prisma 7 CLI compatibility in this repo
   - `npx prisma migrate diff --from-empty --to-schema prisma/schema.prisma --script > /tmp/outbound-baseline-generated.sql`
2. Preserve repo-specific prelude that Prisma diff does not generate:
   - keep `CREATE SCHEMA IF NOT EXISTS "public";`
   - keep the PostgreSQL 17-compatible `public.uuidv7()` helper and `pgcrypto` extension setup
3. Replace the baseline body from the first `CREATE TYPE "UserRole"` onward with the generated SQL body.
4. Delete intermediate migration directories under `front/prisma/migrations/`, leaving only:
   - `20260530000100_baseline_main_schema/`
   - `migration_lock.toml`
5. Delete one-off install-path helpers that are no longer part of the baseline contract:
   - `front/prisma/repairs/**`
   - obsolete backfill SQL directories, if present
   - SQL-file runner scripts/tests if their only remaining use was repair/backfill execution
6. Simplify DB mutation workflows so clean install/reset paths do not run repair/backfill SQL:
   - non-reset: `npm run prisma:migrate:deploy`
   - reset: `npm run db:reset` then `npm run db:seed`
   - always follow with `npm run db:schema:check -- --from-env DATABASE_DIRECT_URL`
7. Update tests and docs to assert the new contract:
   - only one migration directory exists
   - no `prisma/repairs` or `prisma/backfills` directory exists
   - workflow contains no `db:sql:file`, `prisma/repairs`, `migrate resolve`, or `prisma db push`
   - feature-specific migration assertions move to baseline assertions

## Verification

- Compare committed baseline body against Prisma-generated body, ignoring only the preserved uuidv7 helper/prelude:
  - split both SQL files at `-- CreateEnum\nCREATE TYPE "UserRole"`
  - compare the suffixes exactly
- Run `npm run prisma:validate`.
- Run focused tests that cover schema migration artifacts, ID contract, and features whose assertions used to read intermediate migration files.
- Confirm `front/prisma/backfills` and `front/prisma/repairs` do not exist and the normal workflows no longer iterate `prisma/repairs/*.sql`.
- Search for legacy ID defaults in `front/prisma`, `front/src`, and fixtures: `@default(cuid())`, `cuid(`, `autoincrement(`, and `@default(uuid())`; remaining hits should be absence assertions or deliberate external IDs only.
- Check independent model `id` fields use `@default(dbgenerated("uuidv7()")) @db.Uuid` and internal relation scalar `*Id String` fields include `@db.Uuid`, excluding external provider/message/correlation IDs.
- `prisma migrate diff --from-migrations ...` may require `shadowDatabaseUrl` in Prisma 7; do not treat that as a product failure if local shadow DB is not configured.

## PR / operations note

In the PR body and docs, state that existing shared DBs that diverge from the baseline should use the approved `reset_database=true` path and reseed, instead of adding new repair/backfill artifacts.
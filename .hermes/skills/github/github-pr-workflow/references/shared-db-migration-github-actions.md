# Shared DB migration workflows in GitHub Actions

Use this when a repo has Vercel Preview/Production deployments that share one development PostgreSQL/Neon database, and a PR introduces Prisma migrations or backfills that must be applied through GitHub Actions.

## Recommended separation

- Keep Preview deployment workflows free of DB-mutating steps when Preview and Production share the same DB. A PR Preview applying unmerged schema can break main and other Preview deployments.
- Use a separate manual `workflow_dispatch` workflow for one-time or operator-approved DB work such as Prisma baseline `migrate resolve`, data backfills, and recovery tasks.
- After the migration workflow is stable, Production/main deployment may have a predecessor `db-migrate` job that runs `prisma migrate deploy` before the app deploy job.
- Do not put one-time baseline `migrate resolve --applied <baseline>` in a recurring deploy workflow. Make it a guarded manual input or a PR-specific/manual workflow action.

## Safe manual workflow shape

- Trigger: `workflow_dispatch` only.
- `runs-on`: use the repo's established runner labels.
- `environment`: prefer a protected environment such as `outbound-dev-db-migration` or equivalent.
- `concurrency`: one DB migration group, `cancel-in-progress: false`.
- Secret: direct DB URL only, e.g. `DATABASE_DIRECT_URL`; do not use Vercel runtime pooled `DATABASE_URL` for Prisma Migrate or backfills.
- Steps:
  1. checkout
  2. setup Node using the app runtime version
  3. install app dependencies in the app workspace
  4. optional guarded baseline resolve
  5. `npm run prisma:generate`
  6. `npm run prisma:migrate:deploy`
  7. optional explicit backfill script
  8. write a summary with migration/backfill result counts; do not print full DB URLs

## Backfill execution

If the runner may not have `psql`, prefer a small repo script that uses the existing PostgreSQL client dependency (for example `pg`) to execute a checked-in SQL file. This avoids relying on runner-local package state.

Backfills need an execution policy before they are automated broadly:
- track executed backfills in a table with filename/checksum/status; or
- include the data change in a Prisma migration; or
- keep each backfill as an explicit manual workflow input and record evidence in the PR/run summary.

## Read-only schema checks

Read-only drift checks are useful but are not a substitute for migration application. Run them before/after migration to produce evidence.

Prisma CLI compatibility matters: in Prisma 7, `prisma migrate diff --from-url` was removed. Use config datasource based options such as `--from-config-datasource` with a Prisma config datasource, or another Prisma-7-compatible form, instead of copying old `--from-url` examples.

## Reporting guidance

When reporting to the user, separate these states clearly:
- deploy workflow exists but only deploys the app;
- read-only schema check exists but does not mutate DB;
- migration/backfill workflow exists and can change the shared DB;
- the one-time baseline resolve/backfill was actually executed or remains pending.

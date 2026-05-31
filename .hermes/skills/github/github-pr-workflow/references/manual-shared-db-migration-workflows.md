# Manual shared DB migration workflows for Prisma/Vercel preview repos

Use this when a repository deploys Preview and Production to the same shared development database and a PR needs actual shared DB migration/backfill execution via GitHub Actions.

## Pattern

Prefer a dedicated `workflow_dispatch` workflow for shared DB mutations instead of putting DB writes into PR Preview deploy workflows.

Recommended workflow properties:

- `permissions: contents: read`
- `workflow_dispatch` only for one-time or operator-controlled DB work
- `concurrency` with one fixed DB-level group, e.g. `outbound-dev-db-migration`, and `cancel-in-progress: false`
- `environment` dedicated to DB mutation, e.g. `outbound-dev-db-migration`, so maintainers can add approval/protection rules
- direct DB URL secret such as `DATABASE_DIRECT_URL`; do not use the pooled Vercel runtime `DATABASE_URL` for Prisma migrate/backfill
- no redundant typed confirmation input by default; prefer manual `workflow_dispatch` plus a protected GitHub Environment as the safety gate, and add a typed phrase only if the user explicitly asks for that extra friction
- checkout `ref` input for the branch/ref containing migration artifacts
- install the nested app workspace dependencies before Prisma commands
- upload non-secret artifacts such as schema-diff SQL after the run

## Prisma baseline + deploy + backfill sequence

For a Prisma Migrate adoption where the live shared DB already matches a committed baseline schema:

1. Run `prisma migrate resolve --applied <baseline-migration-name>` as a one-time step only.
2. Run `npm run prisma:generate`.
3. Run `npm run prisma:migrate:deploy` with `DATABASE_DIRECT_URL`.
4. Run the idempotent backfill script after migration deploy.
5. Run a read-only schema drift check using the same direct DB URL.

Do not run `migrate resolve` on every deploy. Treat it as a one-time history repair/adoption step, ideally guarded by a boolean input only while the one-time adoption is still pending.

After the one-time baseline/adoption/backfill operation has completed, remove those dispatch inputs and steps from the ordinary migration workflow instead of leaving them as permanent options. The steady-state shared-DB migration workflow should be boring and narrow: checkout the canonical deploy ref (usually `main`), validate the direct DB secret, run `prisma migrate deploy`, then run the read-only schema drift check. Keeping old `run_baseline_resolve`, `baseline_migration`, `run_backfill`, or arbitrary branch/file inputs around creates accidental repeat-execution risk and makes future operators choose between obsolete paths.

## Backfill execution

If `psql` may not exist on the runner, add a small project script that reads a SQL file and executes it with an already-present database client dependency (for example Node `pg`). This keeps the workflow portable across self-hosted runners.

Recommended script UX:

```bash
npm run db:sql:file -- --file prisma/backfills/<file>.sql
npm run db:sql:file -- --file prisma/backfills/<file>.sql --database-url-env DATABASE_DIRECT_URL
```

Print row counts / returned summary rows, but never print database URLs.

## Prisma 7 drift check note

Prisma 7 removed `migrate diff --from-url`. For live DB to schema comparisons with a Prisma config datasource, use:

```bash
npx prisma migrate diff \
  --from-config-datasource \
  --to-schema prisma/schema.prisma \
  --script \
  --exit-code
```

When the script accepts `--from-env DATABASE_DIRECT_URL`, set both `DATABASE_URL` and `DATABASE_DIRECT_URL` in the spawned Prisma env to that selected URL so `prisma.config.ts` resolves the expected datasource.

## Pitfalls

- Do not add redundant typed confirmation prompts to shared-DB mutation workflows when the repository already relies on manual dispatch, a dedicated secret, fixed concurrency, and GitHub Environment approval/protection. They slow routine operator work without adding much safety; use them only if the user explicitly requests that UX.
- Do not add DB mutation to PR Preview deploy workflows when Preview and Production share one database; an unmerged PR can mutate shared state for all previews/main.
- Do not use `prisma db push`, `migrate reset`, truncate, or destructive seed overwrite as the automation path for reviewable shared DB migrations.
- Do not rely on Vercel `DATABASE_URL` if it is pooled. Prisma migrate/backfill should use a direct connection string.
- Do not shell-interpolate untrusted `workflow_dispatch` string inputs directly inside `run:` commands. Pass them through `env:` variables, quote the shell variables, and validate before use.
- For user-facing reports, distinguish “workflow added” from “actual DB migration executed”; the latter only happens after the manual workflow is dispatched with secrets configured.

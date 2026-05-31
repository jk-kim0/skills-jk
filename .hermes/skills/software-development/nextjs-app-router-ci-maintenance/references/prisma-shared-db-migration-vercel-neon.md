# Shared Vercel/Neon DB Migration and Drift Recovery

Use this reference when a Next.js/Prisma app on Vercel uses a shared Neon development database and a manual GitHub Actions workflow applies Prisma migrations/backfills.

## Pattern that worked

1. Treat the Vercel runtime `DATABASE_URL` as pooled and app-only.
2. Use a direct/non-pooling Neon URL for Prisma Migrate and backfills, usually exposed as a GitHub Actions secret such as `DATABASE_DIRECT_URL`.
3. If the Vercel Project only syncs pooled `DATABASE_URL`, inspect the connected Vercel Storage/Neon resource for non-pooling secret names such as `POSTGRES_URL_NON_POOLING` or `DATABASE_URL_UNPOOLED`.
4. If a direct value cannot be read directly but the pooled host is clearly a Neon `*-pooler` hostname, a direct URL can often be derived by removing `-pooler` from the hostname. Before storing it as a GitHub secret, verify it with a non-mutating query such as `select current_database(), length(current_user);` and never print the URL.
5. Set the GitHub secret with `gh secret set DATABASE_DIRECT_URL --body "$(cat /tmp/secret-file)"`, then delete temporary secret files.

## Running the manual workflow

- Prefer `workflow_dispatch` with explicit inputs for the branch/ref, one-time baseline resolve toggle, migration name, backfill toggle, and backfill file.
- Do not add text-confirmation inputs when the workflow is already protected by GitHub environment approval/concurrency and the user wants low-friction operation; they often cause false failures without adding useful safety.
- For the first one-time baseline run, use `run_baseline_resolve=true` with the baseline migration name.
- After baseline resolve has succeeded once, rerun with `run_baseline_resolve=false` if you need the workflow itself to finish green after separate drift remediation.
- Keep `concurrency.cancel-in-progress: false` for mutating DB workflows.

## When apply succeeds but schema check fails

A manual migration/backfill workflow can have `migrate resolve`, `migrate deploy`, and backfill succeed, then fail only at the final drift check. Diagnose that as a schema-history mismatch rather than assuming the whole migration failed.

Typical cause:
- `prisma/schema.prisma` on `main` contains schema changes that were committed without a corresponding `prisma/migrations/**/migration.sql` artifact.

Recovery approach:
1. Read the drift SQL from the failed workflow log/artifact.
2. Inspect live row counts and duplicate risks before applying constraints or NOT NULL columns.
3. For NOT NULL additions, backfill existing rows from reliable current data or system defaults before `ALTER COLUMN ... SET NOT NULL`.
4. For renamed columns, copy old values into the new column before dropping the old column. Example: preserve `ContactListEntry.contactName` into `fullName` before dropping `contactName`.
5. Create unique indexes only after checking for duplicate key groups.
6. Run the read-only schema drift workflow again and require a green result.
7. Rerun the mutating workflow with already-completed one-time steps disabled if you need a final green apply run.

## Safety notes

- Do not print full database URLs in logs, summaries, or chat reports.
- Use read-only probes before mutation: row counts, duplicate grouping checks for planned unique indexes, and column inventory via `information_schema.columns`.
- Do not use `prisma db push` or `migrate reset` against shared development DBs.
- Treat Node/action runtime deprecation warnings as separate workflow-maintenance work unless they caused the migration failure.

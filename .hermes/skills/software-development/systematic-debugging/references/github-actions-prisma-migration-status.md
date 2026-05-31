# GitHub Actions Prisma migration status failures

Use this reference when a GitHub Actions run fails in a Prisma schema drift or migration-status check.

## Signature

A real repository/workflow failure, not runner acquisition failure, usually has:

- job steps are present and logs exist
- a specific step failed, for example `Check Prisma schema drift`
- logs include `prisma migrate status` output
- logs say `Following migrations have not yet been applied:` followed by one or more migration directory names
- the script may exit before producing diff SQL because migration status failed first

Example output shape:

```text
Datasource "db": PostgreSQL database "...", schema "public" at "..."

2 migrations found in prisma/migrations
Following migrations have not yet been applied:
20260530000100_baseline_main_schema
20260530000200_add_team_email_foundation

To apply migrations in development run prisma migrate dev.
To apply migrations in production run prisma migrate deploy.
Prisma migration status check failed.
```

## Investigation steps

1. Inspect the failed job, not only the workflow conclusion:

```bash
env -u GITHUB_TOKEN gh run view <RUN_ID> --repo <owner>/<repo> --json status,conclusion,name,displayTitle,headBranch,headSha,event,createdAt,updatedAt,url,jobs
env -u GITHUB_TOKEN gh run view <RUN_ID> --repo <owner>/<repo> --job <JOB_ID> --log-failed
```

2. Download artifacts if the workflow uploads schema-check logs:

```bash
env -u GITHUB_TOKEN gh run download <RUN_ID> --repo <owner>/<repo> -n <artifact-name> -D /tmp/<artifact-dir>
```

3. Read the workflow and script contract:

- `.github/workflows/*schema*.yml`
- `package.json` scripts such as `db:schema:check`, `prisma:migrate:deploy`
- schema diff/status helper scripts
- deployment workflows to see whether deploy actually runs migrations
- repository docs for migration apply order, direct vs pooled DB URL, baseline resolve, and backfill rules

4. Check whether a separate manual migration workflow exists and whether it has run:

```bash
env -u GITHUB_TOKEN gh workflow list --repo <owner>/<repo> --all
env -u GITHUB_TOKEN gh run list --repo <owner>/<repo> --workflow <migration-workflow.yml> --limit 10 --json databaseId,status,conclusion,headSha,url,createdAt
```

## Interpretation

If `prisma migrate status` lists unapplied migrations, the schema check is doing its job: the database migration history is behind the repository migration artifacts. Do not treat a successful app deploy as evidence that DB schema was migrated unless the deploy workflow actually runs `prisma migrate deploy` or an equivalent migration step.

For shared development DBs, the correct action is usually the repository-approved migration path, not `prisma db push` or ad-hoc SQL. Common safe sequence:

1. one-time baseline `prisma migrate resolve --applied <baseline>` only if the existing DB is already known to match the baseline
2. `prisma migrate deploy` using a direct/migration-capable DB URL, not a pooled runtime URL when repo policy says so
3. idempotent backfill if required
4. rerun schema drift check
5. smoke runtime paths that exercise the changed tables/columns and check logs for Prisma `P2021`/`P2022`

## Reporting guidance

Report separately:

- immediate failing step and exact log excerpt
- whether runner acquisition was ruled out
- whether diff SQL exists or status failed before diff generation
- unapplied migration names
- whether app deploy workflow includes migration execution
- recommended migration workflow/input values if the repo already defines them
- verification command to rerun the schema check after migration

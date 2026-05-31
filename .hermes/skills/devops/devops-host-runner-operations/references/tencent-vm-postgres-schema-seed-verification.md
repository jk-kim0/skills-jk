# Tencent/Linux VM PostgreSQL schema and seed verification pattern

Use this when a user asks whether a deployed web app's VM-local PostgreSQL instance has schema migrations and demo/seed data applied.

## Pattern

1. Start read-only and classify access layers:
   - Confirm current repo context and branch if a repo is involved.
   - Resolve the public FQDN and test the public HTTPS endpoint.
   - Do not assume the FQDN resolves to the SSH target. In Tencent VM deployments, app FQDNs may resolve to internal/private IPs while GitHub workflows or infra docs contain the public SSH IP and user.
2. Mine repo deployment artifacts for the canonical SSH target before guessing:
   - `.github/workflows/*deploy*`, `*db-migration*`, `*db-schema*`
   - deployment helper scripts such as `.github/scripts/*vm*.sh`
   - infra docs under `infra/<env>/`
3. SSH read-only checks:
   - `hostname; uname -a; whoami`
   - `systemctl is-active <app-service>`
   - deployed revision file such as `/opt/<app>/repo/.deployed-revision`
   - `docker compose ... ps` and `ss -ltnp` for app, nginx, and Postgres listeners
4. Inspect PostgreSQL from inside the DB container when direct DB credentials are local-only:
   - `docker exec <postgres-container> pg_isready -U <user> -d <db>`
   - count public tables from `information_schema.tables`
   - list `public` table names
   - query `_prisma_migrations` for applied migration names and finished status
   - count core domain tables and login/user tables
5. Compare DB migration state with repository migration files:
   - list repo migrations under `front/prisma/migrations/` or equivalent
   - if DB has fewer completed migrations than current main, report "schema partially applied" rather than simply "schema exists"
6. Check whether seed/population actually happened:
   - Login page rendering is not enough; it may be static/default-filled.
   - Verify user rows, team rows, and key domain objects directly.
   - For reviewer apps, absence of seeded login users means data population is not complete even if `/login` returns 200.
7. Check CI/GitHub workflow history only with the repository owner confirmed from `git remote -v` or `gh repo view`; do not assume personal forks.

## When verification turns into remediation

If the user asks to make the DB current after verification, keep the mutation path explicit and auditable:

1. Prefer the repository's deployment/migration script or GitHub workflow over ad-hoc manual commands so the fix remains repeatable.
2. For Prisma deployments, `prisma migrate deploy` only applies migrations; it does not imply seed/demo data. If the expected outcome is "schema + data population", ensure the workflow/script also runs the seed command after migration, usually after `prisma generate` when generated client types may be stale.
3. If the database schema already matches a migration but `_prisma_migrations` is missing that applied row, Prisma may report drift or a failed migration row. Do not drop/reset a deployed DB by default. Inspect the actual schema and, only when the schema is verified equivalent, use `prisma migrate resolve --applied <migration_name>` to align migration history. Report any retained rolled-back/failed history row separately.
4. Use environment-specific seed guards such as `APP_ENV=dev npm run db:seed` when seeds are demo/dev-only. Never assume production should load fixtures.
5. After remediation, verify both the direct DB state and the automation path: run the workflow against the target branch/environment and confirm the run's migration/seed step plus smoke check succeed.

## GitHub Actions runner/SSH deployment details

- Self-hosted runners can have different egress IPs than the operator's workstation. If a workflow SSH step times out while local SSH works, check the runner egress IP and cloud security group ingress separately.
- Add narrow `/32` SSH ingress for the runner egress IP with a descriptive policy label; keep existing admin ingress rules intact.
- Avoid stale SSH aliases on persistent self-hosted runners. Deployment scripts should rewrite the relevant SSH config entry each run or use explicit `user@host` for verification steps, rather than relying on a possibly cached alias from a previous target.

## Reporting contract

Report separately:

- Host/app reachability
- PostgreSQL container health
- Applied migrations vs current repo migrations
- Seed/data population counts
- Deployed app revision vs current main
- Automation status: whether the workflow/script applies migration only or migration + seed, and the latest successful run if verified
- Any access caveat, e.g. public FQDN SSH reset/private IP vs canonical workflow SSH target, runner security-group ingress, or stale SSH alias risk

Avoid dumping secrets. Redact `DATABASE_URL`, passwords, auth secrets, and environment files.
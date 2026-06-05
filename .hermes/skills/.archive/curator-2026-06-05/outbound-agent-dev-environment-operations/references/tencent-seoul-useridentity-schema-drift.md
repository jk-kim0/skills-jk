# Dev Seoul UserIdentity schema drift after baseline-only migration

## When to use

Use this reference when Dev Seoul deployment metadata shows the latest image/revision is active but authenticated runtime smoke or logs fail around Google SSO / System Settings / login-home routes.

## Observed evidence pattern

- Public `/login` returns HTTP 200 and `/` redirects to `/login`.
- VM deployment metadata matches the target SHA:
  - `/opt/outbound-agent/deployments/current-revision`
  - `/opt/outbound-agent/repo/.deployed-revision`
  - `/opt/outbound-agent/deployments/current-image`
- `outbound-front`, `nginx`, and the PostgreSQL container are active/healthy.
- Runtime smoke can reach an authenticated `/<team>/home` URL but may fail on a UI assertion such as `Setup checklist` not found.
- Container logs show Prisma `P2021` for `prisma.userIdentity.findFirst()` with missing table `public.UserIdentity`.

Example log signature:

```text
PrismaClientKnownRequestError:
Invalid `prisma.userIdentity.findFirst()` invocation:
The table `public.UserIdentity` does not exist in the current database.
code: 'P2021'
meta.modelName: 'UserIdentity'
```

## Read-only confirmation commands

```bash
ssh ubuntu@43.133.247.7 '
  echo current_revision=$(cat /opt/outbound-agent/deployments/current-revision 2>/dev/null || true)
  echo deployed_revision=$(cat /opt/outbound-agent/repo/.deployed-revision 2>/dev/null || true)
  echo current_image=$(cat /opt/outbound-agent/deployments/current-image 2>/dev/null || true)
  echo outbound_front=$(systemctl is-active outbound-front || true)
  echo nginx=$(systemctl is-active nginx || true)
  docker ps --format "container={{.Names}} image={{.Image}} status={{.Status}} ports={{.Ports}}" | sed -n "1,20p"
  docker logs --since 30m outbound-front 2>&1 | tail -80
'
```

```bash
ssh ubuntu@43.133.247.7 '
  docker exec outbound-agent-postgres psql -U outbound -d outbound -v ON_ERROR_STOP=1 \
    -c "select table_name from information_schema.tables where table_schema='"'"'public'"'"' and table_name in ('"'"'UserIdentity'"'"','"'"'_prisma_migrations'"'"','"'"'User'"'"') order by table_name;" \
    -c "select migration_name, finished_at from \"_prisma_migrations\" order by finished_at desc nulls last limit 10;"
'
```

Also check recent migration/schema workflow freshness:

```bash
gh run list --repo querypie/outbound-agent --workflow 'Apply tencent/outbound-seoul DB Migration' --limit 10 --json databaseId,displayTitle,headSha,status,conclusion,createdAt,url
gh run list --repo querypie/outbound-agent --workflow 'Check tencent/outbound-seoul DB Schema' --limit 10 --json databaseId,displayTitle,headSha,status,conclusion,createdAt,url
```

## Root cause classification

Classify this as existing shared dev DB schema drift, not as a container deploy failure, when:

- The VM is serving the intended image/revision.
- Service processes are active.
- Public `/login` is healthy.
- The database lacks `UserIdentity` while the current repo schema/baseline includes it.

With the baseline-only migration policy, the baseline migration directory can be updated to include `UserIdentity`, but an existing DB that already recorded the same baseline migration as applied will not replay that baseline. A migrate-only path can therefore leave the shared dev DB missing tables added to the revised baseline.

`UserIdentity` was introduced by the Google SSO/System Settings feature track; future incidents should verify the current git history rather than relying on these exact commit IDs.

## Recommended remediation

After confirming no newer `origin/main` deploy is still in progress, use the approved Dev Seoul reset path rather than ad-hoc SQL repair:

1. Dispatch `Apply tencent/outbound-seoul DB Migration` with `branch=main` and `reset_database=true`.
2. Verify the workflow actually ran reset and seed, not just concluded success.
3. Dispatch `Check tencent/outbound-seoul DB Schema` with `branch=main`.
4. Verify `UserIdentity` now exists and seed counts/session fixture behavior are sane.
5. Rerun runtime smoke against `https://outbound-seoul.dev.querypie.io`.
6. Re-fetch `origin/main`; if main moved during the operation, re-check deployed revision and smoke against the final SHA.

Do not report the environment as fixed from public `/login` 200 alone; pair exact-version evidence with DB-backed/authenticated smoke.

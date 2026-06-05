# Tencent container runtime config file packaging

Use this reference when a Tencent dev VM is running the expected latest image/revision but authenticated routes fail after login with `Internal Server Error`.

## Symptom

- Public `/login` returns HTTP 200 and renders normally.
- VM metadata matches the expected latest main SHA:
  - `/opt/outbound-agent/deployments/current-image`
  - `/opt/outbound-agent/deployments/current-revision`
  - `/opt/outbound-agent/repo/.deployed-revision`
- `outbound-front` and `nginx` are active.
- `E2E - Runtime Smoke` logs in successfully and reaches `/<team>/home`, but the page body is `Internal Server Error` and the test cannot find the expected Home headings.
- `docker logs outbound-front` shows an `ENOENT` for a non-secret runtime config file, for example:

```text
ENOENT: no such file or directory, open '/app/front/config/system-access.yaml'
```

## Durable diagnosis

Treat this as an image packaging/runtime artifact issue, not as a DB seed/migration issue.

Vercel can still work because it deploys from the repository/workdir context, while the Tencent Docker runner stage may only contain the files explicitly copied from the builder stage. If `front/config/` is read at runtime by SSR code but not copied into the runner image, authenticated routes can 500 even though build, deploy metadata, `/login`, and service health are green.

## Verification pattern

1. Confirm latest target SHA and PR/merge commit:

```bash
git fetch origin main --prune
git rev-parse origin/main
gh pr view <pr-number> --repo querypie/outbound-agent --json state,mergedAt,mergeCommit,headRefOid,files
```

2. Verify the main image/deploy workflow job state before judging VM state:

```bash
gh run list --repo querypie/outbound-agent --limit 20 --json databaseId,workflowName,status,conclusion,headSha,createdAt,displayTitle,event
```

3. Verify Dev Seoul exact deployed version over SSH:

```bash
ssh ubuntu@43.133.247.7 'set -Eeuo pipefail; \
  echo current_image=$(sudo cat /opt/outbound-agent/deployments/current-image 2>/dev/null || true); \
  echo current_revision=$(sudo cat /opt/outbound-agent/deployments/current-revision 2>/dev/null || true); \
  echo repo_deployed_revision=$(sudo cat /opt/outbound-agent/repo/.deployed-revision 2>/dev/null || true); \
  echo outbound_front=$(systemctl is-active outbound-front || true); \
  echo nginx=$(systemctl is-active nginx || true); \
  docker ps --format "container={{.Names}} image={{.Image}} status={{.Status}}" | grep -E "outbound|postgres" || true'
```

4. Check public `/login` separately from authenticated smoke. `/login` 200 is only a health signal, not proof that authenticated SSR is healthy.

5. Dispatch or follow the deployed runtime smoke and inspect artifacts/logs if it fails:

```bash
gh workflow run 'E2E - Runtime Smoke' --repo querypie/outbound-agent --ref main -f base_url=https://outbound-seoul.dev.querypie.io
# then poll the run and inspect failed job logs/artifacts
```

6. If smoke fails after login, inspect recent container logs:

```bash
ssh ubuntu@43.133.247.7 'sudo docker logs --since 20m outbound-front 2>&1 | tail -n 300'
```

## Fix pattern

- Update `front/Dockerfile` runner stage so non-secret runtime config directories needed by SSR are copied from the builder image, e.g. `front/config/`.
- Add or update an artifact-contract test such as `front/src/__tests__/container-deployment-artifacts.test.ts` so Dockerfile runner-stage copies include these runtime config files.
- After merge, wait for the main image build and Dev Seoul deployment to finish, then verify:
  - VM image tag/revision equals the merge commit SHA prefix/full SHA.
  - `/login` returns 200.
  - `Smoke dev-seoul after deployment` or `E2E - Runtime Smoke` succeeds.
  - Recent `docker logs outbound-front` no longer contain the missing config `ENOENT` or `Internal Server Error`.

## Reporting shape

Keep the result separated into:

- PR/merge commit understood.
- Exact Dev Seoul deployment metadata.
- Public `/login` health.
- Runtime smoke result.
- Recent server-log regression check.

If the overall main workflow continues to deploy Tokyo after Seoul smoke succeeds, report that the top-level workflow is still in progress but the requested Dev Seoul deployment and smoke are complete.
# Tencent Seoul/Tokyo container deploy status triage: disk-full before remote deployment

Use this reference when checking whether Dev Seoul and Dev Tokyo are running the latest Tencent container image after a `main` push or manual `Deploy Tencent container image` run.

## Pattern

1. Establish the target revision/image.
   - `git fetch origin main --prune`
   - `git rev-parse origin/main`
   - Expected image shape: `ireg.querypie.io/ci/outbound-front:<short-sha>`.

2. Inspect the relevant GitHub Actions run before touching the VM.
   - `gh run list --workflow 'PR Cache-Only Build Validation / Main Deploy outbound-front image' --limit ...`
   - `gh run view <run-id> --json status,conclusion,headSha,jobs`
   - For a failed deploy job, inspect the job log: `gh run view <run-id> --job <job-id> --log`.

3. Interpret job-level state, not only top-level workflow state.
   - Image publish can succeed while VM deploy fails.
   - Seoul and Tokyo deploys may be separate jobs; one target can fail or be skipped while the other is not attempted.
   - In the `Deploy Tencent container image` workflow, `target=all` may gate one target on another target's success depending on workflow dependencies; report skipped targets as not deployed, not as healthy.

## Disk-full failure signature

A latest image deployment can fail before the remote deployment script actually runs if the VM cannot accept uploaded temp files:

```text
scp: /tmp/outbound-registry.env: No space left on device
Process completed with exit code 1.
```

Meaning:

- The container image may have been successfully built and pushed to `ireg.querypie.io`.
- The target VM did not deploy that image.
- If the failure occurs on Seoul and Tokyo is skipped by dependency/concurrency, Tokyo also did not deploy the latest image.
- Public `/login` returning 200 only proves the old/current app is serving; it is not exact-version proof.

## Reporting shape

Separate the report into:

- Target latest SHA and image.
- GitHub Actions evidence:
  - image build/publish result,
  - per-target deploy job result,
  - failed step/log excerpt,
  - skipped target reason.
- VM/public health evidence:
  - direct metadata if SSH/workflow diagnostics are available,
  - public `/login` status as health-only evidence.
- Exact conclusion:
  - `latest image deployed`, `latest image deploy failed`, `latest image skipped/not attempted`, or `ambiguous`.

## If direct SSH is unavailable from the agent runtime

Do not stop at SSH timeout when GitHub Actions can reach the VM through repository secrets/self-hosted runner network.

- Use workflow logs as deployment truth for the attempted latest image.
- If VM metadata is required and no diagnostic workflow exists for the target, prefer adding or dispatching a repo-tracked diagnostic workflow/script that prints only non-secret state:
  - disk usage for `/`, `/tmp`, `/opt`, `/var/lib/docker`,
  - `/opt/outbound-agent/deployments/current-image`,
  - `/opt/outbound-agent/deployments/current-revision`,
  - `/opt/outbound-agent/repo/.deployed-revision`,
  - `systemctl is-active outbound-front nginx docker`,
  - `docker ps` and `docker inspect outbound-front`,
  - filtered recent `journalctl -u outbound-front` and `docker logs outbound-front` error lines.

Avoid reporting public HTTP 200 as proof that a new image deployed.

## Smoke follow-up

If deployment completed successfully, run public/runtime smoke.
If latest deployment failed or a target was skipped, smoke can still be useful as current-health evidence, but label it clearly as health of the currently deployed version, not validation of the latest image.

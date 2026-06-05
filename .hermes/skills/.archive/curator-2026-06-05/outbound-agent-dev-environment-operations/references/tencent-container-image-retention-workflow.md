# Tencent container image retention cleanup workflow

Use this reference when adding or maintaining GitHub Actions that keep dev-seoul/dev-tokyo VM disk usage stable after container image deployments.

## Pattern

1. Keep the cleanup as a repo-tracked remote script plus a reusable/manual workflow.
   - Remote script path pattern: `infra/tencent-vm/cleanup-container-images.sh`.
   - Workflow path pattern: `.github/workflows/cleanup-tencent-container-images.yml`.
   - The workflow should support both `workflow_dispatch` and `workflow_call` so it can be run manually and invoked after deployment jobs.

2. Retain a fixed number of recent app images, not every pulled image.
   - Default repository: `ireg.querypie.io/ci/outbound-front`.
   - Default retain count: 10 newest image tags per VM.
   - Sort by Docker image `CreatedAt` and keep the first N refs.

3. Protect images referenced by containers.
   - Collect `docker ps -a --format '{{.Image}}'` for the target repository.
   - Exclude active/referenced image refs from deletion even if they are older than the retention window.
   - This preserves rollback/current-service safety when a container still references an older image.

4. Delete only old unused image refs and safe cache residue.
   - Run `docker image rm <old-ref>` for selected old unused refs.
   - Then run `docker image prune -f` and `docker builder prune -f`.
   - Do not prune volumes; PostgreSQL data volumes must be preserved.

5. Emit useful before/after evidence.
   - `df -h / /tmp /var/lib/docker` when available.
   - `docker system df`.
   - running containers and their images.
   - retained refs, active protected refs, deletion candidates, remaining app images.
   - `systemctl is-active docker outbound-front nginx`.

6. Wire deployment workflows after successful target deployment.
   - Main push image deploy: run target cleanup after each target deploy succeeds.
   - Manual container image deploy: run cleanup only for the target(s) that were actually deployed successfully.
   - Propagate deployment dry-run into cleanup dry-run.
   - Include cleanup results in deployment notification/status summaries if the deploy workflow reports aggregate status.

## Verification

Before opening a PR, verify:

```bash
bash -n infra/tencent-vm/cleanup-container-images.sh
actionlint \
  .github/workflows/cleanup-tencent-container-images.yml \
  .github/workflows/build-outbound-front-image.yml \
  .github/workflows/deploy-tencent-container-image.yml
git diff --check
```

Also run a fake-Docker dry-run simulation when changing retention logic. The important assertions are:

- with 12 ordered images and retain count 10, only images older than the newest 10 become deletion candidates;
- an old image referenced by `docker ps -a` is protected and not selected for deletion;
- dry-run prints actions without deleting or pruning.

## Pitfalls

- Do not use broad `docker system prune --volumes`; it can endanger PostgreSQL data.
- Do not rely on `docker image prune -a` alone if the requirement is “keep newest 10 images”; implement explicit repository/tag retention first.
- Do not delete an image merely because it is older than the retention window; first verify no existing container references it.
- A cleanup workflow should be independently manually dispatchable so disk pressure can be remediated without forcing a new deployment.

# Tencent VM Docker image cleanup via TAT

Use this when Dev Seoul/Tokyo container deployment fails because the VM disk is full, especially when direct SSH from the agent runtime times out but Tencent TAT is online.

## Trigger evidence

- Tencent container image deploy fails before the remote deploy script runs with an error like:
  - `scp: /tmp/outbound-registry.env: No space left on device`
- Direct SSH to the VM public IP may time out from the agent runtime.
- `tccli tat DescribeAutomationAgentStatus` reports `AgentStatus: Online` for the VM instance.

Known Outbound Agent Tencent VM instance mapping:

- Dev Seoul: region `ap-seoul`, instance `ins-43by4ge7`
- Dev Tokyo: region `ap-tokyo`, instance `ins-phcrqzii`

## Safe cleanup approach

Prefer TAT `RunCommand` with a root shell script that preserves images referenced by existing containers and removes only unused images/build cache:

```bash
docker ps --format 'container={{.Names}} image={{.Image}} status={{.Status}}'
docker system df
docker image prune -a -f
docker builder prune -f || true
df -h / /tmp /var/lib/docker 2>/dev/null || df -h
docker images --format 'image={{.Repository}}:{{.Tag}} id={{.ID}} size={{.Size}} created={{.CreatedSince}}'
for s in docker outbound-front nginx; do printf '%s=' "$s"; systemctl is-active "$s" || true; done
docker ps --format 'container={{.Names}} image={{.Image}} status={{.Status}}'
```

`docker image prune -a -f` removes images not referenced by any existing container, so the current `outbound-front` and `postgres` images are preserved as long as their containers still exist.

## Verification

After cleanup, run a compact TAT verification command and report:

- disk usage for `/` and `/tmp`
- image count and remaining image names
- running containers and their images
- `docker`, `outbound-front`, and `nginx` systemd active state
- public `/login` HTTP smoke for both `https://outbound-seoul.dev.querypie.io/login` and `https://outbound-tokyo.dev.querypie.io/login`

Expected healthy post-cleanup shape in the observed incident:

- disk improved from Seoul `100%` used to about `15%` used
- disk improved from Tokyo `84%` used to about `15%` used
- remaining images were only the active app image and `postgres:18`
- `outbound-front`, PostgreSQL container, Docker, nginx stayed active

## Pitfalls

- Do not run broad volume pruning unless explicitly requested; the PostgreSQL data volume must be preserved.
- Do not equate `/login` 200 with latest-version proof. It only proves current public health.
- TAT output is base64-encoded in `TaskResult.Output`; decode it before summarizing if full command output is needed.
- Avoid printing `tccli configure list` output in user-facing responses because it can include credential-looking values.
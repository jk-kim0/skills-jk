# Container Image VM Deployment Pattern

Use this reference when a Linux VM deployment should stop building source on the host and instead run a CI-built container image from a private registry.

## Core architecture

```text
CI
  -> build image from source
  -> push registry/app:<immutable-git-hash>

VM
  -> pull exact image tag
  -> run DB migration according to schema-change class
  -> replace app container
  -> keep nginx/TLS as public ingress
```

The VM should be an image consumer/runtime host, not the primary build host.

## Tagging

- Use an immutable Git-derived tag, normally 12-char short SHA.
- Avoid using `latest`, `dev`, or `main` as the deployment source of truth.
- Record the running image tag on the VM for audit and rollback.

## Runtime layout

Recommended host-managed paths:

```text
/etc/<app>/<service>.env                  # root-only runtime env
/opt/<app>/deployments/current-image
/opt/<app>/deployments/previous-image
/opt/<app>/scripts/deploy-image.sh
```

Run app containers behind nginx on localhost:

```bash
docker run --rm \
  --name <service> \
  --env-file /etc/<app>/<service>.env \
  -p 127.0.0.1:<host-port>:<container-port> \
  <registry>/<image>:<hash>
```

If the app container must reach a VM-local database published on host localhost, use Docker's host gateway pattern:

```bash
--add-host host.docker.internal:host-gateway
DATABASE_URL=postgresql://user:***@host.docker.internal:5432/db
```

## Direct single-VM deployment

When the user asks to deploy one named VM, avoid workflows that fan out to multiple environments unless the user explicitly asked for that. A safe direct path is:

```bash
IMAGE=registry/app:<immutable-sha>
scp infra/<vm>/deploy-image.sh <user>@<host>:/tmp/deploy-image.sh
scp infra/<vm>/<service>.service <user>@<host>:/tmp/<service>.service
ssh <user>@<host> 'bash -s' -- "$IMAGE" <<'REMOTE'
set -Eeuo pipefail
image="$1"
sudo install -d -m 755 /opt/<app>/scripts /opt/<app>/deployments
sudo install -m 755 /tmp/deploy-image.sh /opt/<app>/scripts/deploy-image.sh
sudo install -m 644 /tmp/<service>.service /etc/systemd/system/<service>.service
sudo env PUBLIC_URL="https://<fqdn>" /opt/<app>/scripts/deploy-image.sh "$image"
sudo systemctl enable <service> >/dev/null
REMOTE
```

The deploy script should run DB migrations before replacing the app container and abort on migration failure. `No pending migrations to apply` is a valid migration result and should be reported.

After the deploy command exits, verify final state rather than relying only on inline smoke logs:

```bash
ssh <user>@<host> '
cat /opt/<app>/deployments/current-image
systemctl is-active <service>
systemctl is-enabled <service>
systemctl show <service> -p ActiveState -p SubState -p ExecMainPID -p ExecStart --no-pager
docker ps --filter name=<service> --format "{{.Names}} {{.Image}} {{.Status}}"
curl -fsSI --max-time 20 http://127.0.0.1:<port>/login | sed -n "1,12p"
curl -fsSI --max-time 30 https://<fqdn>/login | sed -n "1,12p"
'
```

A transient `curl: Failed to connect` line can appear while systemd/container startup is still racing with a retrying smoke loop. Treat the final command exit and the separate verification checks above as authoritative.

## Migration and rollback

- Compatible migration: run migration before container replacement; abort if migration fails.
- App-use commit: ensure the required migration is already applied before running the image.
- Incompatible migration: handle as a separate maintenance operation; image-only rollback may not be enough.

Rollback should normally redeploy the previous immutable image tag, after verifying DB compatibility.

## Security

- CI gets registry push credentials; VM gets pull-only credentials.
- Keep secrets out of image layers and repository docs.
- Keep DB and app ports bound to localhost; expose public traffic through nginx 80/443 only.
- Avoid service restart designs that require registry availability if the image is already pulled locally.
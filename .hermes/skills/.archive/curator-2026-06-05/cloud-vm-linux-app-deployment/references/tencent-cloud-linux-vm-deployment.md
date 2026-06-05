# Tencent Cloud Linux VM Deployment Notes

This reference captures durable patterns from an outbound-agent Tencent Cloud dev VM session. Treat hostnames, IPs, and paths as examples unless the active repo context says they are current.

## CLI access

On the user's macOS workstation, `tccli` may already be installed and configured. Verify with read-only commands before asking for console access:

```sh
/opt/homebrew/bin/tccli --version
tccli cvm DescribeRegions --region ap-guangzhou
```

A successful `DescribeRegions` response proves that Tencent Cloud API credentials are usable from the current runtime. Continue with `DescribeZones`, `DescribeImages`, `DescribeInstanceTypeConfigs`, `DescribeVpcs`, `DescribeSubnets`, `DescribeSecurityGroups`, and key-pair discovery for resource planning.

## Outbound-agent VM assumptions used in the session

- Public FQDN requested for the first VM: `outbound-tencent.dev.querypie.io`.
- Dev VM sizing assumption: 4 vCPU, 8 GiB memory, 100 GiB disk; document as adjustable, not permanent.
- Final multi-region dev hosts created in the session:
  - `outbound-dev-tokyo` / `outbound-tokyo.dev.querypie.io`
  - `outbound-dev-seoul` / `outbound-seoul.dev.querypie.io`
- App deploy path: `/opt/outbound-agent/repo`.
- Deployed revision marker: `/opt/outbound-agent/repo/.deployed-revision`.
- App environment file: `/etc/outbound-agent/front.env`.
- App service: `outbound-front.service` from `front/`.

## PostgreSQL via Docker Compose

The repo `compose.yml` default published PostgreSQL as `5432:5432`, which binds on all interfaces on Linux. For a public VM, use a VM-local override so PostgreSQL is reachable only from localhost:

```yaml
# /opt/outbound-agent/compose.localhost.yml
services:
  postgres:
    ports: !override
      - "127.0.0.1:5432:5432"
```

Run Compose with both files:

```sh
cd /opt/outbound-agent/repo
docker compose -f compose.yml -f /opt/outbound-agent/compose.localhost.yml up -d postgres
docker compose -f compose.yml -f /opt/outbound-agent/compose.localhost.yml ps
```

If the host has package-managed PostgreSQL from an earlier attempt, stop/disable it before relying on Docker PostgreSQL to avoid port conflicts and ambiguity:

```sh
sudo systemctl disable --now postgresql || true
```

Verify bind address:

```sh
sudo ss -ltnp | grep ':5432'
docker ps --format 'table {{.Names}}\t{{.Ports}}\t{{.Status}}'
```

Expected Docker port shape: `127.0.0.1:5432->5432/tcp`.

## Node / Prisma build pattern

For outbound-agent front app, production runtime env is not the same as dependency installation mode. In the session, `NODE_ENV=production npm ci` omitted dev dependencies and broke Prisma config loading through `dotenv/config`. The durable pattern is:

```sh
cd /opt/outbound-agent/repo/front
npm ci --include=dev
npm run prisma:migrate:deploy
npm run db:seed   # dev/demo only
npm run build
sudo systemctl restart outbound-front.service
```

Run the systemd service with production env from `/etc/outbound-agent/front.env`; do not rely on production-mode install to build/migrate if the repo requires dev tooling.

## External access and TLS

Use nginx as the internet-facing reverse proxy and Let's Encrypt certificates on the host. Open inbound 80/443 to the public internet. Keep the app port and PostgreSQL on localhost.

Layered smoke tests used successfully:

```sh
systemctl status outbound-front.service --no-pager
curl -fsS http://127.0.0.1:3000/login
curl -I https://outbound-tokyo.dev.querypie.io/login
curl -I https://outbound-seoul.dev.querypie.io/login
```

When reporting completion, include active service status, deployed revision, PostgreSQL bind state, and HTTPS status for each VM.

# Tencent Cloud Ubuntu VM: Next.js + nginx TLS + localhost PostgreSQL notes

Use these notes when documenting or verifying a Tencent Cloud CVM that hosts a small Next.js app plus PostgreSQL on the same Ubuntu VM.

## Final-state verification checklist

Collect live evidence before updating infra docs:

```sh
# Tencent Cloud resource identity and current state
TC_REGION=ap-tokyo
TC_INSTANCE_NAME=outbound-dev-tokyo
tccli cvm DescribeInstances \
  --region "$TC_REGION" \
  --Filters '[{"Name":"instance-name","Values":["'"$TC_INSTANCE_NAME"'"]}]'

# Security Group rules
tccli vpc DescribeSecurityGroupPolicies \
  --region "$TC_REGION" \
  --SecurityGroupId <sg-id>

# Public DNS and HTTPS smoke
for r in 1.1.1.1 8.8.8.8; do
  dig +short @"$r" <fqdn> A
done
curl -sSIL --max-time 20 "https://<fqdn>/login" | sed -n '1,12p'

# Host runtime state, avoiding secret output
ssh ubuntu@<public-ip> '
  echo HOST=$(hostname)
  echo REV=$(cat /opt/outbound-agent/repo/.deployed-revision 2>/dev/null || true)
  echo FRONT_ACTIVE=$(systemctl is-active outbound-front)
  echo FRONT_ENABLED=$(systemctl is-enabled outbound-front)
  echo NGINX_ACTIVE=$(systemctl is-active nginx)
  echo POSTGRES_HOST_ACTIVE=$(systemctl is-active postgresql 2>/dev/null || true)
  echo POSTGRES_HOST_ENABLED=$(systemctl is-enabled postgresql 2>/dev/null || true)
  sudo docker compose -f /opt/outbound-agent/repo/compose.yml -f /opt/outbound-agent/compose.localhost.yml ps
  sudo ss -ltnp | grep -E ":(80|443|3000|5432)\\b" || true
  sudo certbot certificates | sed -n "/Certificate Name:/,/VALID:/p"
  systemctl is-active certbot.timer 2>/dev/null || true
  sudo nginx -t
'
```

## PostgreSQL on the same public VM

For a public VM, do not rely on a repository `compose.yml` that publishes `5432:5432`, because Docker will bind it to `0.0.0.0` by default. Use a VM-local override file that is not a secret but is host-specific:

```yaml
# /opt/outbound-agent/compose.localhost.yml
services:
  postgres:
    ports: !override
      - "127.0.0.1:5432:5432"
```

Run with both files:

```sh
sudo docker compose \
  -f /opt/outbound-agent/repo/compose.yml \
  -f /opt/outbound-agent/compose.localhost.yml \
  up -d postgres
```

Verify `127.0.0.1:5432->5432/tcp` in `docker compose ps` and with `ss -ltnp`.

## App and build notes

For Prisma/Next.js deployments, `NODE_ENV=production npm ci` can omit build-time devDependencies such as `dotenv/config` used by Prisma config. If the VM builds in place, install with dev dependencies, then run the build with production env loaded from the root-only env file:

```sh
cd /opt/outbound-agent/repo/front
NODE_ENV=development npm ci --include=dev
set -a
. /etc/outbound-agent/front.env
set +a
npm run prisma:migrate:deploy
npm run db:seed
npm run build
sudo systemctl restart outbound-front
```

Record the deployed commit in `/opt/outbound-agent/repo/.deployed-revision`.

## Documentation pitfall

Do not leave infra docs in pre-provisioning language after the VM is live. Replace “DNS/TLS 후속 작업” and “host package PostgreSQL” assumptions with the observed final state: instance IDs, public IPs, Security Group rules, cert expiry, Docker Compose PostgreSQL binding, service status, smoke results, and remaining improvement candidates.

If a Next.js service listens on `*:3000`, document the distinction precisely: host listener is broad, but external exposure is controlled by Security Group rules. Prefer tightening the service bind address later, but do not overstate it as public when 3000/tcp ingress is absent.

---
name: linux-host-tls-certbot-nginx
description: Issue, deploy, and verify Let's Encrypt TLS certificates on Linux hosts running nginx reverse proxies, including SSH preflight, DNS/public-IP checks, certbot automation, renewal timers, and external HTTPS smoke tests.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [devops, linux, nginx, tls, letsencrypt, certbot, ssh, dns]
    related_skills: [devops-host-runner-operations]
---

# Linux Host TLS with Certbot and nginx

## Overview

Use this skill when a user asks to configure HTTPS/TLS for a Linux VM or bare host that already serves HTTP through nginx, especially when using Let's Encrypt certbot with an nginx reverse proxy. The goal is to issue the certificate, let certbot update nginx safely, and prove the public FQDN works over HTTPS.

This skill is for host-level TLS operations, not application-level TLS in a framework, Kubernetes ingress, CDN-managed certificates, or DNS provider automation.

## When to Use

- Issuing a Let's Encrypt certificate on a VM or Linux host.
- Converting an nginx HTTP reverse proxy to HTTPS.
- Verifying `http://...` redirects to `https://...`.
- Checking certbot auto-renewal timers and certificate expiry.
- Troubleshooting a mismatch between public DNS and local/internal resolver behavior during HTTPS verification.

If SSH reachability is unknown, first use `devops-host-runner-operations` Phase 1 to prove non-interactive SSH access.

## Safety Rules

1. Confirm the target host, public IP, FQDN, and SSH account before mutation.
2. Do not print or copy private key material from `/etc/letsencrypt/live/*/privkey.pem`.
3. Always run `sudo nginx -t` before certbot modifies nginx.
4. Prefer `certbot --nginx` for normal nginx-managed hosts; use webroot/standalone only when nginx integration is inappropriate.
5. Avoid using `--force-renewal` unless there is a clear reason. Prefer `--keep-until-expiring` for idempotent repeat runs.
6. Use `--register-unsafely-without-email` only when the user has not provided an email and the task should not pause for input. If an operational email is available, use `-m <email>` instead.
7. If a dry-run or certbot command hangs, check for a remaining certbot process and clear only the known dry-run process; do not kill unrelated package managers or web services.

## Standard Workflow

### 1. Local and DNS preflight

Verify what the public internet should see before touching the VM:

```sh
for r in 1.1.1.1 8.8.8.8 9.9.9.9; do
  echo "# resolver $r"
  dig +short @$r <fqdn> A
done
curl -sSIL --max-time 20 http://<fqdn>/ | sed -n '1,10p'
```

If local DNS returns an internal/private/CGNAT address but public resolvers return the expected public IP, preserve that distinction in the report. For verification, force the public path with curl `--resolve` and openssl `-connect <public-ip>:443`.

### 2. SSH and host preflight

Prove remote execution and inspect the current listener state:

```sh
ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new <user>@<public-ip> 'hostname; whoami; uname -a'
ssh -o BatchMode=yes <user>@<public-ip> '
  sudo ss -ltnp | grep -E ":(80|443|3000|5432)\\b" || true
  systemctl is-active nginx 2>/dev/null || true
  command -v certbot || true
  certbot --version 2>/dev/null || true
  ls -l /etc/nginx/sites-enabled 2>/dev/null || true
'
```

For Ubuntu cloud images, `ubuntu@<public-ip>` is a common first account to test, but verify rather than assume.

### 3. nginx syntax check

```sh
ssh <user>@<public-ip> 'sudo nginx -t'
```

Do not proceed with certbot nginx integration until this passes.

### 4. Issue and deploy the certificate

Interactive-safe default when no email was specified:

```sh
ssh <user>@<public-ip> 'sudo certbot --nginx --non-interactive --agree-tos --register-unsafely-without-email --redirect --keep-until-expiring -d <fqdn>'
```

With an operations email:

```sh
ssh <user>@<public-ip> 'sudo certbot --nginx --non-interactive --agree-tos -m ops@example.com --redirect --keep-until-expiring -d <fqdn>'
```

Expected success signals:

- `Successfully received certificate.`
- `Successfully deployed certificate ... to /etc/nginx/sites-enabled/...`
- `Congratulations! You have successfully enabled HTTPS on https://<fqdn>`

### 5. Verify HTTPS and certificate identity

Use both normal DNS and forced public-IP verification when needed:

```sh
curl -sSIL --max-time 20 http://<fqdn>/login | sed -n '1,10p'
curl -sSIL --max-time 20 https://<fqdn>/login | sed -n '1,10p'

curl -sSIL \
  --resolve <fqdn>:80:<public-ip> \
  --resolve <fqdn>:443:<public-ip> \
  --max-time 20 https://<fqdn>/login | sed -n '1,10p'

echo | openssl s_client -servername <fqdn> -connect <public-ip>:443 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates
```

Check the host-side state too:

```sh
ssh <user>@<public-ip> '
  sudo certbot certificates | sed -n "/Certificate Name:/,/VALID:/p"
  systemctl list-timers --all | grep -E "certbot|snap.certbot" || true
  systemctl is-active certbot.timer 2>/dev/null || true
  sudo nginx -t
'
```

### 6. Renewal dry-run discipline

A renewal dry-run is useful, but it can take longer than expected. Run it only when the extra assurance is worth the wait, and prefer a bounded foreground command:

```sh
ssh <user>@<public-ip> 'sudo certbot renew --dry-run --quiet'
```

If the command times out locally, immediately inspect the remote process list:

```sh
ssh <user>@<public-ip> 'ps -ef | grep -E "[c]ertbot renew|[l]etsencrypt" || true'
```

If a known `certbot renew --dry-run` process remains and the user did not ask to keep it running, terminate that process only. Avoid a broad `pkill -f certbot` that could catch the current shell command or future legitimate certbot activity.

## Reporting Pattern

Report concise operational facts:

- host/IP/FQDN for each target
- certbot command outcome, not private keys
- certificate path and expiry date
- HTTP redirect result and HTTPS status code
- certbot timer state
- any DNS caveat, separating local resolver behavior from public resolver behavior

For user-facing final reports, do not overstate verification if only forced-IP checks passed. Say exactly which path was verified.

## References

- `references/tencent-cloud-ubuntu-certbot-nginx.md` — condensed notes from Tencent Cloud Ubuntu VM certbot issuance, including public-vs-local DNS split verification and dry-run cleanup pitfalls.
- `references/tencent-cloud-nextjs-postgres-vm.md` — Tencent Cloud Ubuntu VM notes for a Next.js app behind nginx, Docker Compose PostgreSQL bound to localhost, deployed revision tracking, and final-state infra documentation.

## Common Pitfalls

- Verifying only from the VM itself and missing external firewall/DNS problems.
- Treating local resolver output as authoritative when public resolvers disagree.
- Letting a local timeout leave a remote `certbot renew --dry-run` running unnoticed.
- Using a broad remote `pkill -f "certbot ..."` command whose pattern can match the SSH shell itself and disconnect the session. Prefer listing PIDs first or use a safer exact process-management approach.
- Forgetting that certbot modifies nginx configs; always run `nginx -t` before and after.
- Reporting the private key path is acceptable, but never read or print the key contents.

## Verification Checklist

- [ ] SSH remote command execution confirmed.
- [ ] Public DNS resolves to the intended public IP, or any local/public DNS split is explicitly documented.
- [ ] nginx syntax passed before certbot.
- [ ] certbot reported successful receipt and deployment.
- [ ] HTTP redirects to HTTPS.
- [ ] HTTPS returns the expected application response externally or via forced public IP.
- [ ] Certificate subject/issuer/dates verified with openssl or certbot output.
- [ ] certbot renewal timer is active or otherwise documented.
- [ ] No secret material was printed.

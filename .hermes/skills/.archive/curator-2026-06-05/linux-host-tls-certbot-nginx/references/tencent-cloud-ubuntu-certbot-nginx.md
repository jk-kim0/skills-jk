# Tencent Cloud Ubuntu VMs: certbot nginx issuance notes

## Context

Two Tencent Cloud Ubuntu VMs were serving a Next.js app behind nginx on HTTP and needed Let's Encrypt TLS:

- Tokyo: `outbound-tokyo.dev.querypie.io` → `124.156.231.41`, SSH `ubuntu@124.156.231.41`
- Seoul: `outbound-seoul.dev.querypie.io` → `43.133.247.7`, SSH `ubuntu@43.133.247.7`

The VMs already had nginx, certbot, a reverse proxy to port 3000, and PostgreSQL on localhost:5432.

## Durable workflow detail

1. Public DNS should be checked with external resolvers (`1.1.1.1`, `8.8.8.8`, `9.9.9.9`) rather than relying only on the local resolver.
2. If local DNS resolves the same FQDN to an internal/CGNAT address such as `100.64.x.x`, HTTPS verification may fail from the agent machine even when public DNS is correct. Use:

```sh
curl -sSIL \
  --resolve outbound-seoul.dev.querypie.io:80:43.133.247.7 \
  --resolve outbound-seoul.dev.querypie.io:443:43.133.247.7 \
  https://outbound-seoul.dev.querypie.io/login

echo | openssl s_client \
  -servername outbound-seoul.dev.querypie.io \
  -connect 43.133.247.7:443 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates
```

3. A working issuance command for an nginx-managed Ubuntu host without a provided email was:

```sh
sudo certbot --nginx \
  --non-interactive \
  --agree-tos \
  --register-unsafely-without-email \
  --redirect \
  --keep-until-expiring \
  -d <fqdn>
```

4. After issuance, verify:

```sh
sudo certbot certificates | sed -n '/Certificate Name:/,/VALID:/p'
systemctl list-timers --all | grep -E 'certbot|snap.certbot' || true
systemctl is-active certbot.timer || true
sudo nginx -t
```

## Observed success signals

- Certbot prints `Successfully received certificate.`
- Certbot prints `Successfully deployed certificate ... to /etc/nginx/sites-enabled/...`
- HTTP `/login` returns `301` to HTTPS.
- HTTPS `/login` returns `200 OK` from nginx/Next.js.
- Certificate issuer was Let's Encrypt `YE1`; certbot timer was active.

## Pitfall learned

Running `certbot renew --dry-run --quiet` over SSH can exceed a local tool timeout and leave a remote dry-run process active. Inspect with:

```sh
ps -ef | grep -E '[c]ertbot renew|[l]etsencrypt' || true
```

If cleanup is needed, avoid broad patterns that match the current SSH shell command. Prefer identifying the specific dry-run PID first, then terminating only that PID.

---
name: querypie-acp-multi-agent-seamless-ssh
description: Use when connecting to internal servers or VMs through QueryPie ACP Multi Agent Seamless SSH, especially when direct SSH aliases/DNS fail but the server is visible in QueryPie SAC.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [querypie, acp, multi-agent, seamless-ssh, ssh, devops]
    related_skills: [ssh-host-access-probing, github-self-hosted-runner-operations]
---

# QueryPie ACP Multi Agent Seamless SSH

## Overview

Use QueryPie ACP Multi Agent Seamless SSH when a server is accessible through QueryPie Server Access Control but not directly reachable by local DNS/SSH alias. Multi Agent installs the `qpctl` command, which can either wrap `ssh` directly or act as an OpenSSH `ProxyCommand` through `qpctl ssh-proxy`.

Primary reference:
- https://docs.querypie.com/ko/user-manual/multi-agent/multi-agent-seamless-ssh-usage-guide

Session-specific reference:
- `references/chequer-runner-diagnosis.md` — Chequer GitHub runner mapping, proven QueryPie SSH command, and the operator-facing querypie-mono wiki handoff for skill-less agents.

The most reliable automation pattern for Hermes/non-interactive diagnostics is the explicit OpenSSH `ProxyCommand` form:

```sh
ssh -o 'ProxyCommand=qpctl ssh-proxy %r %h %p sec.querypie.io' <account>@<host-or-ip> '<remote command>'
```

This avoids several `qpctl ssh` argument-order edge cases when adding non-interactive SSH options and remote commands.

## When to Use

- A QueryPie SAC server/VM is visible at `https://sec.querypie.io/servers/connections`.
- Direct `ssh <alias>` fails with DNS resolution, network routing, or QueryPie seamless-auth errors.
- The user says they logged into QueryPie ACP / Multi Agent and asks to connect to internal servers.
- You need to run read-only diagnostics on self-hosted GitHub runners or build machines that are reachable via QueryPie.
- The user asks for operator documentation for skill-less AI agents; document the `qpctl` host-selection and `qpctl ssh-proxy` verification path first, and treat browser UI checks as a fallback inventory refresh step.

Do not use for:
- Kubernetes access through QueryPie (`qpctl kube get-token` is a separate flow).
- Browser-only QueryPie Terminal/SFTP usage unless the user asks for GUI access.
- Long-lived interactive remote shells from Hermes unless a PTY/background process is explicitly appropriate.

## Prerequisite Checks

Run these locally first:

```sh
command -v qpctl
qpctl host list
ssh -V
```

Expected facts:
- `qpctl` exists, often at `/usr/local/bin/qpctl` on macOS.
- `qpctl host list` includes the target QueryPie host, for example `https://sec.querypie.io`.
- OpenSSH is 6.7+; the docs example shows checking with `ssh -V`.

Select the right QueryPie host if needed:

```sh
qpctl host use sec.querypie.io
qpctl host list
```

Notes:
- `qpctl host list` is the locally registered QueryPie host list; it is not the server connection list from the web UI.
- If the current host is wrong, seamless SSH may fail even when the target server exists.

## Discover and Verify QueryPie Access

For AI-agent diagnostics, prefer a `qpctl`-first flow over browser scraping. The reproducible sequence is:

1. Confirm `qpctl` is installed and which QueryPie ACP hosts are registered:

```sh
command -v qpctl
qpctl host list
```

2. Select the intended QueryPie ACP host, usually `sec.querypie.io` for Chequer self-hosted runner work:

```sh
qpctl host use sec.querypie.io
qpctl host list
```

3. Treat `qpctl host list` correctly: it lists QueryPie ACP hosts, not the downstream server/VM inventory. Do not describe it as the runner/server list.

4. Use a maintained inventory or GitHub/wiki source for candidate runner names and host/IPs, then verify each candidate with `qpctl ssh-proxy`:

```sh
ssh \
  -o BatchMode=yes \
  -o ConnectTimeout=8 \
  -o StrictHostKeyChecking=accept-new \
  -o 'ProxyCommand=qpctl ssh-proxy %r %h %p sec.querypie.io' \
  ubuntu@<host-or-ip> \
  'hostname; whoami; uname -srmo'
```

5. Only fall back to the QueryPie web UI when the candidate inventory is stale or missing:
   - Open `https://sec.querypie.io/servers/connections`.
   - Check the relevant server group, e.g. `[DC] Github Runner`.
   - Use the UI only to refresh connection name and host/IP; still verify access with `qpctl ssh-proxy`.

Avoid making Browser DevTools/grpc-web response decoding the primary documented method. It can be useful for emergency extraction, but it is brittle and risks exposing cookies/access tokens if copied carelessly. If used, never print raw request headers or cookies.

Reference for the Chequer runner handoff and wiki wording: `references/chequer-runner-diagnosis.md`.

## Recommended Non-Interactive SSH Pattern

For one-shot diagnostics, prefer explicit OpenSSH with `ProxyCommand`:

```sh
ssh \
  -o BatchMode=yes \
  -o ConnectTimeout=8 \
  -o StrictHostKeyChecking=accept-new \
  -o 'ProxyCommand=qpctl ssh-proxy %r %h %p sec.querypie.io' \
  <server-account>@<querypie-server-host-or-ip> \
  '<remote command>'
```

Example:

```sh
ssh \
  -o BatchMode=yes \
  -o ConnectTimeout=8 \
  -o StrictHostKeyChecking=accept-new \
  -o 'ProxyCommand=qpctl ssh-proxy %r %h %p sec.querypie.io' \
  ubuntu@10.11.12.5 \
  'hostname; whoami; df -hT / /var/lib/docker 2>/dev/null'
```

Why this pattern:
- `BatchMode=yes` avoids password prompts/hangs.
- `ConnectTimeout=8` keeps diagnostics bounded.
- `StrictHostKeyChecking=accept-new` accepts first-time internal host keys but still protects against changed keys.
- The explicit `ProxyCommand` works well with remote commands and extra SSH options.

## Direct `qpctl ssh` Pattern

The docs also support prefixing normal SSH commands with `qpctl`:

```sh
qpctl ssh <account>@<host-or-ip>
qpctl ssh <account>@<host-or-ip> -i ~/.ssh/key.pem
qpctl ssh <ssh-config-alias>
```

However, for automation be careful: `qpctl ssh` can append the generated `-o ProxyCommand=...` after a remote command, which may cause arguments to be interpreted by the remote command instead of OpenSSH. If you need remote one-shot commands, prefer the explicit `ssh -o 'ProxyCommand=...'` form above.

## SSH Config Option

For repeated manual use, add a host stanza:

```sshconfig
Host <short-name>
  HostName <QueryPie server host/IP>
  User <server account>
  Port 22
  ProxyCommand qpctl ssh-proxy %r %h %p sec.querypie.io
```

Then:

```sh
ssh <short-name>
```

If server host/port combinations are globally unique, the docs also show a wildcard form:

```sshconfig
Host *
  ProxyCommand qpctl ssh-proxy %r %h %p sec.querypie.io
```

Avoid broad `Host *` in agent environments unless the user explicitly wants all SSH traffic routed through QueryPie.

## Shell Alias Option

The docs show an alias pattern:

```sh
alias qshsec='ssh -o ProxyCommand="qpctl ssh-proxy %r %h %p sec.querypie.io"'
qshsec <account>@<host-or-ip>
```

This is useful for humans, but Hermes should prefer explicit `ssh -o ...` commands for clarity and reproducibility.

## Troubleshooting

1. `Could not resolve hostname <alias>`
   - The local SSH alias/DNS name is not resolvable.
   - Use the QueryPie connection's actual host/IP from the web UI, or add an SSH config `Host` stanza mapping the alias to that host/IP.

2. `Host key verification failed`
   - First-time host key trust is blocking the connection.
   - For diagnostics, retry with `-o StrictHostKeyChecking=accept-new`.
   - If the host key changed for a known host, do not blindly bypass; inspect `~/.ssh/known_hosts` and confirm the host identity.

3. `qpctl: error: ... Custom account not supported on seamless SSH`
   - The requested local account or seamless account mapping is not supported.
   - Use an account that QueryPie allows for that server, such as `ubuntu` when confirmed by server policy, or inspect QueryPie server/account privileges.

4. Direct `qpctl ssh ... '<remote command>'` mangles arguments
   - Use explicit OpenSSH `ProxyCommand` instead.

5. `scp` through qpctl
   - The referenced QueryPie docs say `scp` is not supported for this seamless SSH flow.

6. Custom ProxyCommand
   - `qpctl ssh` itself uses ProxyCommand, so user-specified ProxyCommand is unsupported by the wrapper.
   - If a custom jump chain is required, confirm scope manually instead of stacking ProxyCommand options.

## Verification Checklist

- [ ] `command -v qpctl` succeeds.
- [ ] `qpctl host list` includes the intended QueryPie host.
- [ ] `qpctl host use <host>` sets the correct host when needed.
- [ ] QueryPie web UI or grpc-web response confirms the server connection name and actual host/IP.
- [ ] A bounded command using explicit `ssh -o 'ProxyCommand=qpctl ssh-proxy %r %h %p <QueryPie Host>'` succeeds.
- [ ] The remote `hostname` matches the expected server, not just any reachable host.
- [ ] Diagnostics avoid printing QueryPie cookies, access tokens, `.env`, runner credentials, or private keys.

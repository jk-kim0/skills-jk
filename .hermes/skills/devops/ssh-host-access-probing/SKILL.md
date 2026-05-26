---
name: ssh-host-access-probing
description: Use when the user asks whether a named machine, workstation, Mac, server, or SSH alias is reachable from the current agent environment. Probe local context, SSH configuration, hostname resolution, and non-interactive SSH access before answering.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ssh, networking, access, diagnostics, devops]
    related_skills: [systematic-debugging, codebase-inspection, github-self-hosted-runner-operations]
---

# SSH Host Access Probing

## Overview

Use this skill to answer questions like "can you access llm1?", "is my Mac Studio reachable?", or "can you SSH into <host>?" The goal is to produce a grounded yes/no/partial answer from the current agent runtime, not from memory.

The current runtime may not be on the user's expected network, and SSH aliases can exist even when DNS, VPN, mDNS, or credentials are not usable. Separate those layers explicitly.

## When to Use

- User asks whether a named host, workstation, Mac, server, or SSH alias is reachable.
- User asks to verify access before doing remote work.
- SSH fails and the user needs a quick reachability diagnosis.
- You need to distinguish: alias exists, hostname resolves, port is reachable, authentication works, and remote command execution works.

Don't use this for deep server administration after login succeeds; switch to a more specific deployment/debugging skill for that class of work. If login succeeds and the user asks where GitHub Actions runners are configured, switch to `github-self-hosted-runner-operations`.

## Fast Probe Sequence

Run a compact, non-destructive probe from the current environment:

```sh
pwd
hostname
ssh -G <host> 2>/dev/null | sed -n '1,40p'
ssh -o BatchMode=yes -o ConnectTimeout=5 <host> 'hostname; uname -a'
```

Interpretation:

- `ssh -G <host>` succeeds: OpenSSH can expand config for the alias. This does not prove DNS or login works.
- `Could not resolve hostname`: the alias points to a hostname that the current resolver cannot resolve. Report this as name-resolution failure, not credential failure.
- `Permission denied` with `BatchMode=yes`: host resolved and SSH answered, but non-interactive auth failed.
- `Connection timed out` / `No route to host`: name may resolve, but network path or firewall is blocked.
- Remote `hostname; uname -a` output: command execution works; access is confirmed.

## Optional Follow-up Probes

If the first probe fails due to name resolution and the user expects a local Mac, LAN/VPN device, or known workstation, actively look for the IP before asking the user for it. Check local static mappings and config first; this is often faster and more reliable than broad network discovery.

If the user asks to quickly find a working SSH key for a host, do not stop at host reachability. Enumerate plausible private keys under `~/.ssh` without printing key material, then test them with `BatchMode=yes`, `IdentitiesOnly=yes`, `PreferredAuthentications=publickey`, short timeouts, and the likely accounts. Report the exact successful key path, account, host, and a copy-pasteable verified SSH command.

```sh
# Static local mappings and SSH config are the first places to check.
grep -nE '<host>|<host-alias>|mac.?studio|studio|llm|<expected-subnet>' /etc/hosts 2>/dev/null || true
grep -RniE '<host>|<host-alias>|mac.?studio|studio|llm|HostName[[:space:]]+[0-9]' ~/.ssh/config ~/.ssh/config.d 2>/dev/null || true

# If a candidate hostname is found, resolve it through the OS resolver.
dscacheutil -q host -a name <candidate-hostname> 2>/dev/null || true
```

Then try common low-impact alternatives before giving up when appropriate:

```sh
ssh -G <host>.local 2>/dev/null | sed -n '1,20p'
ssh -o BatchMode=yes -o ConnectTimeout=5 <host>.local 'hostname; uname -a'
getent hosts <host> 2>/dev/null || true
getent hosts <host>.local 2>/dev/null || true
```

On macOS, `getent` may not exist. Use:

```sh
dscacheutil -q host -a name <host> 2>/dev/null || true
dscacheutil -q host -a name <host>.local 2>/dev/null || true
```

If you find or receive an IP address, separate network reachability from authentication:

```sh
route -n get <ip> 2>/dev/null | sed -n '1,40p' || true
nc -vz -G 3 <ip> 22
ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectionAttempts=1 -o ConnectTimeout=3 <user>@<ip> 'hostname; uname -a'
```

Interpretation:

- `nc` succeeds but SSH says `Permission denied`: the host is reachable and port 22 is open; the remaining issue is credentials/authorized keys/account policy.
- Route output via `utun*` often indicates VPN/tunnel reachability; report it as context, not proof of login.

If the user specifically points to a sibling private repo or config repo, search it narrowly for hostnames, aliases, and candidate subnets, including git history when current files have no matches:

```sh
rg -n '(<host>|mac.?studio|studio|llm|10\.11\.|192\.168\.)' ../private-or-config-repo 2>/dev/null || true
git -C ../private-or-config-repo log --all -G'(<host>|mac.?studio|studio|llm|10\.11\.)' --format='%h %ad %s' --date=short -- . 2>/dev/null | sed -n '1,80p'
```

## References

- `references/mac-studio-hosts-ip-discovery.md` — concrete macOS example where `/etc/hosts` revealed `mac-studio-llm1.local -> 10.11.1.11`, `nc` proved port 22 reachability, and SSH auth still failed.

## Reporting Pattern

Answer in layers:

1. Current local context: cwd and local hostname if relevant.
2. SSH config/alias status: whether `ssh -G` found a usable config.
3. Reachability/auth result: exact failure class or remote command output.
4. Next useful step: specific, minimal follow-up such as `llm1.local`, actual IP, VPN/network, or SSH key setup.

Example concise answer:

```text
현재 이 세션에서는 llm1에 바로 접근되지 않습니다.

- SSH alias는 존재합니다: user=jk, hostname=llm1, port=22
- 하지만 hostname llm1이 resolve되지 않습니다.
- 따라서 현재 실패 원인은 인증이 아니라 DNS/네트워크 이름 해석입니다.

다음 확인은 llm1.local 또는 실제 IP로 직접 SSH probe입니다.
```

## Common Pitfalls

1. **Treating an SSH alias as confirmed access.** `ssh -G` only expands config. Always run a short remote command with `BatchMode=yes`.

2. **Mislabeling DNS failure as permission failure.** `Could not resolve hostname` means the current environment cannot resolve the host name. Ask for IP/VPN/mDNS follow-up only after saying that clearly.

3. **Hanging on interactive auth.** Use `BatchMode=yes` and a short `ConnectTimeout` for reachability probes so the agent does not wait on password prompts.

4. **Assuming the user's remembered environment is the runtime environment.** Always check `pwd` and local `hostname`; the agent may run on a different machine or outside the user's LAN/VPN.

5. **Over-explaining before probing.** If the target host name is clear, run the probe first and then report the evidence.

6. **Answering a key-finding request with only reachability details.** When the user asks which key works, the deliverable is the working private key path plus account/host and verified command, not a general SSH diagnosis. Keep failures concise and stop after the first confirmed success unless broader coverage is requested.

## Verification Checklist

- [ ] Checked current runtime context (`pwd`, local `hostname`) when relevant.
- [ ] Expanded SSH config with `ssh -G <host>` or reported that no config exists.
- [ ] Tried a non-interactive remote command with `BatchMode=yes` and a short timeout.
- [ ] Classified the failure layer correctly: alias/config, DNS, network, auth, or remote command execution.
- [ ] Gave a concrete next probe or input needed when access is not confirmed.

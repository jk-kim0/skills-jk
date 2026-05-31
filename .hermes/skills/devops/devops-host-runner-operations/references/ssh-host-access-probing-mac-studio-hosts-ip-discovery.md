# Mac Studio / LLM host IP discovery example

Session pattern: user asked whether `llm1` Mac Studio was reachable. Initial `ssh -G llm1` showed an SSH alias with `hostname llm1`, but direct SSH failed with `Could not resolve hostname llm1`.

Useful correction: do not stop at “hostname does not resolve” when the user expects a known local/VPN machine. Actively inspect local host mappings and nearby private/config repos for the IP.

Observed effective sequence on macOS:

```sh
# Check local static mappings first.
grep -nE 'llm1|mac|studio|Mac|Studio|LLM' /etc/hosts || true
grep -nEv '^\s*(#|$)' /etc/hosts || true

# Confirm OS resolver result for the mapped hostname.
dscacheutil -q host -a name mac-studio-llm1.local || true

# Confirm route and port reachability separately from SSH auth.
route -n get 10.11.1.11 2>/dev/null | sed -n '1,40p' || true
nc -vz -G 3 10.11.1.11 22
ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectionAttempts=1 -o ConnectTimeout=3 jk@10.11.1.11 'hostname; sw_vers -productName; sw_vers -productVersion; uname -m'
```

Example evidence found:

```text
/etc/hosts:
10.11.1.11    mac-studio-llm1.local
10.11.1.25    mac-studio-llm2.local

dscacheutil:
mac-studio-llm1.local -> 10.11.1.11

nc:
Connection to 10.11.1.11 port 22 [tcp/ssh] succeeded!

ssh:
Permission denied (publickey,password,keyboard-interactive).
```

Interpretation:

- The host IP was discovered as `10.11.1.11`.
- Port 22 reachability proved the machine/service was reachable at network level.
- `Permission denied` meant the remaining blocker was SSH credentials or account authorization, not DNS/network reachability.

If the user asks to search a sibling private/config repository, run narrow content and history searches. In this example, `../skills-jk-private` had no relevant current-file or git-history matches, so `/etc/hosts` remained the authoritative local clue.

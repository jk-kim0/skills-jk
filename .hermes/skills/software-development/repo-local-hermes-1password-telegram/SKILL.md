---
name: repo-local-hermes-1password-telegram
description: Configure Telegram for a repository-local Hermes setup that uses 1Password as the secret source and bin/hermes-sync-env to materialize the runtime env file.
---

# Repo-local Hermes + 1Password + Telegram

Use this when working in a repository that runs Hermes with `HERMES_HOME="$PWD/.hermes"` and follows the repo-local secret workflow:
- 1Password stores real secret values
- `.env.1password` stores only `op://...` references
- `bin/hermes-sync-env` materializes the runtime env file
- normal Hermes runs should read `HERMES_HOME/.env` and should not call 1Password directly

## When to use
- User wants to connect Hermes to Telegram in this repo-local setup
- Need to align local config with the repo’s documented secret workflow
- Telegram gateway fails and the repo uses 1Password-backed env sync

## Expected layout
- Repo-local Hermes home: `HERMES_HOME="$PWD/.hermes"`
- 1Password item title: `skills-jk-hermes-local`
- 1Password item type: `Secure Note`
- 1Password custom field names must match `.env` keys exactly
- Local reference file: `.env.1password`
- Local materialized secrets file used by Hermes runtime: `.hermes/.env`
- Sync script: `bin/hermes-sync-env`

Important runtime detail discovered in practice:
- Hermes loads `HERMES_HOME/.env` first.
- In this repo-local setup, that means `.hermes/.env` is the effective runtime env file.
- A repo-root `.env` may exist for convenience, but if `.hermes/.env` still contains stale values, Hermes will keep using the stale values.


Important runtime fact:
- Hermes loads `HERMES_HOME/.env` first.
- In this repo-local setup, that means `.hermes/.env` is the env file that actually matters at runtime.
- If repo-root `.env` and `.hermes/.env` diverge, Hermes may appear misconfigured even when 1Password is correct.

## Gateway execution model

Important runtime rule:
- One Hermes gateway instance should run per `HERMES_HOME`.
- Multiple terminal tabs can each run `hermes`, but they do **not** each create separate Telegram connections.
- If a gateway is already running, starting another `hermes gateway run` against the same `HERMES_HOME` can conflict or be refused.
- Prefer service-style controls for always-on use:
  - `hermes gateway install`
  - `hermes gateway start`
  - `hermes gateway stop`
  - `hermes gateway restart`
  - `hermes gateway status`
- Use `hermes gateway run` mainly for foreground/manual debugging.

## Correct Telegram setup

### 1. Verify the 1Password item
Check the actual item being used:

```bash
op item get skills-jk-hermes-local --format json
```

If multiple vaults may contain the same item title, verify the exact vault and item ID first, then prefer the item ID for edits:

```bash
op item get skills-jk-hermes-local --format json
op item get <item-id> --format json --reveal
```

Confirm:
- correct vault/item
- field exists with label `TELEGRAM_BOT_TOKEN`
- field value is the full Telegram bot token, not a masked value
- `op --reveal` is returning a real token, not a literal string containing `***`

### 2. Ensure the field name matches the env key
Bad:
- `HERMES_EXAMPLE_TOKEN`
- any placeholder/example field name

Good:
- `TELEGRAM_BOT_TOKEN`

If needed, rename/update the item so the custom field label is exactly `TELEGRAM_BOT_TOKEN`.

### 3. Store the reference in `.env.1password`
Use the actual vault and item path, for example:

```dotenv
TELEGRAM_BOT_TOKEN=op://Employee/skills-jk-hermes-local/TELEGRAM_BOT_TOKEN
```

Do not put plaintext token values in `.env.1password`.

### 4. Materialize the env file that Hermes actually reads
Run:

```bash
bin/hermes-sync-env
```

Expected result in this repo-local layout:
### 4. Materialize the runtime env file
Run:

```bash
bin/hermes-sync-env
```

In this repo-local setup, the correct target is `.hermes/.env` because Hermes loads `HERMES_HOME/.env` first.
If you manually inspect generated secrets, inspect `.hermes/.env`, not just repo-root `.env`.

### 5. Run Hermes with repo-local HERMES_HOME
For gateway startup:

```bash
HERMES_HOME="$PWD/.hermes" hermes gateway run
```

For normal CLI:

```bash
HERMES_HOME="$PWD/.hermes" hermes
```

## Verification
- `.env.1password` contains `TELEGRAM_BOT_TOKEN=op://...`
- `.hermes/.env` contains `TELEGRAM_BOT_TOKEN=...`
- `op read 'op://.../TELEGRAM_BOT_TOKEN'` returns a full-length token
- `https://api.telegram.org/bot<TOKEN>/getMe` succeeds
- `hermes gateway run` starts without `telegram.error.InvalidToken`
- Telegram bot responds to `/start`
- For group chat use, inbound group messages appear in gateway logs

## Telegram group vs channel caveats

For interactive conversations, prefer a Telegram group/supergroup over a channel.

Why:
- Channels are broadcast-oriented; Hermes may be able to send outbound messages there but still receive no inbound conversational updates.
- In logs this looks like:
  - outbound `Sending response ... to <negative chat id>` exists
  - but no matching `inbound message: ... chat=<same id>` entries appear
- If that happens, the issue is not gateway connectivity — it means the bot is not receiving conversational updates from that chat.

### Group privacy mode
Check the bot capability via Telegram `getMe`.
If `can_read_all_group_messages` is `false`, privacy mode is enabled.
That can prevent reliable group-message handling except for limited cases such as commands, replies, or mentions.

Recommended fix:
1. Open `@BotFather`
2. `/mybots`
3. Select the bot
4. Bot Settings → Group Privacy
5. Turn privacy mode off

Then retest from a real group/supergroup by sending a direct mention or command:
- `@your_bot hello`
- `/sethome`

### Channel/home-channel distinction
- `TELEGRAM_HOME_CHANNEL` can be useful as an outbound destination
- but a home channel is not automatically a good inbound conversation target
- if you want a place where users talk to Hermes and Hermes answers back, use DM or a group/supergroup


### Root causes
- 1Password field contains a masked token (`***`) instead of the real full token
- old revoked token still stored
- truncated copy/paste
- field name does not match `.env` key, so the wrong secret path is used
- duplicate item titles across vaults caused inspection/editing of the wrong item
- repo-root `.env` was refreshed but `.hermes/.env` remained stale, so Hermes kept using the stale token
- writing secret values through tool layers can reintroduce redacted placeholder values; prefer shell-local `op run` / `op read` flows that write directly to `.hermes/.env`

### Telegram group/channel findings
- Telegram DM worked reliably once pairing and token issues were fixed.
- A Telegram channel/group may still fail to behave like a conversation target even when outbound sends succeed.
- If logs show outbound sends to a non-DM chat ID but no corresponding `inbound message` lines for that chat, Hermes is not receiving updates from that chat.
- Check `getMe`: if `can_read_all_group_messages=false`, privacy mode is still on. Turn off Group Privacy in BotFather for more reliable group handling.
- Prefer Telegram groups/supergroups over channels for conversational use. Channels can work poorly for inbound conversational updates.
- `bin/hermes-sync-env` updated repo-root `.env`, but Hermes runtime is still reading stale `HERMES_HOME/.env`
- secret values were piped through a tool layer that redacted them before writing files

### Telegram no-response but gateway is running
A distinct failure mode observed in practice:
- `hermes gateway status` shows the launchd service is loaded and the gateway PID is alive
- `hermes pairing list` shows the Telegram user is already approved
- `.hermes/.env` contains a real-looking `TELEGRAM_BOT_TOKEN`
- but Telegram still gets no replies

In that case, do not assume pairing, ACL, or token problems first. Check raw network reachability to Telegram:
- `api.telegram.org` DNS resolution can fail after wake / network transitions even while the rest of the internet works
- direct TCP to a Telegram fallback IP may succeed while TLS handshake to Telegram still times out
- this leaves the gateway process alive but unable to poll updates, so the bot appears "running but silent"

Recommended diagnostic sequence:
1. Check gateway logs for:
   - `Primary api.telegram.org connection failed`
   - `Fallback IP ... failed`
   - `Connect attempt ... failed: Timed out`
2. Verify pairing/approval is not the blocker:
   - `HERMES_HOME="$PWD/.hermes" hermes pairing list`
3. Verify the token is present in `.hermes/.env` without printing it in full
4. Test Telegram Bot API reachability directly:
   - `curl --max-time 15 "https://api.telegram.org/bot<TOKEN>/getMe"`
5. If DNS is broken, test fallback IP with preserved hostname:
   - `curl --max-time 20 --resolve api.telegram.org:443:149.154.167.220 "https://api.telegram.org/bot<TOKEN>/getMe"`
6. If needed, inspect local macOS network state:
   - `scutil --dns`
   - `scutil --proxy`
   - `nc -vz 149.154.167.220 443`

Interpretation:
- DNS failure for `api.telegram.org` + timeout on direct fallback/TLS means this is a network-path problem, not a Hermes config problem
- successful TCP connect to fallback IP does not prove Telegram is usable; TLS/HTTP can still hang
- after sleep/wake, Wi‑Fi/VPN/DNS state may be partially broken and require network reattachment or a proxy

### Investigation order
1. `op read` the exact secret reference and verify length/shape without exposing it broadly
2. Compare the resolved token hash/length with the value in `.hermes/.env`
3. Confirm what Hermes actually reads: `HERMES_HOME/.env` overrides project-root `.env`
4. Validate the token directly against Telegram with `getMe`
5. If the gateway is running but Telegram is silent, check pairing state and raw Telegram DNS/TLS reachability before changing Hermes config
6. If this repo has a local watchdog (`bin/hermes-gateway-watchdog`), run `bin/hermes-gateway-watchdog check --repair --json` to distinguish “Telegram API still unreachable” from “API recovered, restart gateway now”
7. Only then restart gateway and retest

### Watchdog-based auto-recovery (repo-local)
When this repository includes `bin/hermes-gateway-watchdog`, prefer that over ad hoc restart loops.

What it does:
- checks whether the Hermes gateway service is actually running
- checks whether Telegram Bot API `getMe` is reachable from this machine
- avoids pointless restart loops while Telegram API is still unreachable
- starts the gateway if Telegram is reachable and the service is down
- restarts the gateway once when Telegram API transitions from unreachable back to reachable
- applies exponential back-off to repeated `recent_connect_failure` repair attempts: 5m → 10m → 20m → 40m → max 60m
- suppresses duplicate retries for the same failure fingerprint until a new failure signal appears
- advances the back-off window even when the `recent_connect_failure` restart command itself fails, so a broken repair path does not retry every 60s
- treats an unchanged failure fingerprint as `awaiting_new_failure_signal` rather than as recovery/healthy state
- can be installed as a user launchd job to run every minute on macOS

Repo-local Git hygiene learned in practice:
- runtime watchdog/gateway state files under `.hermes/` should be ignored locally via `.hermes/.gitignore`
- at minimum ignore:
  - `*.json`
  - `*.pid`
  - `*.lock`
  - `state.db*`
  - `.hermes_history`
  - `interrupt_debug.log`
  - `processes.json`
  - `models_dev_cache.json`
  - `ollama_cloud_models_cache.json`
  - `channel_directory.json`
- keep long-lived human-maintained docs/config under `.hermes/` explicitly tracked, but keep generated runtime state untracked

Typical commands:

```bash
bin/hermes-gateway-watchdog check --json
bin/hermes-gateway-watchdog check --repair --json
bin/hermes-gateway-watchdog install-launch-agent --interval 60
bin/hermes-gateway-watchdog status
```

Interpretation:
- `decision.reason=telegram_api_unreachable` means the problem is still the current network path to Telegram, not Hermes process state
- `decision.action=start` means launchd/service is down and can be recovered immediately
- `decision.action=restart` with API reachable means Telegram connectivity recovered and the gateway should be bounced back into a healthy polling state
- `decision.reason=network_backoff_active` means the watchdog still sees a recoverable network-related failure pattern, but restart attempts are being intentionally throttled
- `decision.reason=awaiting_new_failure_signal` means the same failure fingerprint is still present and should not trigger another immediate restart

### Telegram response delay with gateway apparently healthy
Another distinct failure mode observed in practice:
- user reports Hermes replies are delayed rather than fully silent
- `hermes gateway status` shows the launchd service is loaded and the gateway PID is alive
- Telegram API direct checks are healthy
- watchdog keeps reporting `decision.reason=healthy`
- but `gateway.error.log` contains repeated lines like:
  - `Telegram polling conflict (1/3), will retry in 10s`
  - `Conflict: terminated by other getUpdates request; make sure that only one bot instance is running`

Interpretation:
- this is not a generic model/API latency problem first
- it means some other process is consuming `getUpdates` for the same bot token
- the active gateway may stay alive, but inbound updates are being interrupted or delayed by polling ownership fights
- the watchdog can miss this because it may only check process liveness and Telegram API reachability, not update-stream exclusivity

Recommended diagnostic sequence for delayed Telegram replies:
1. Check the active runtime/config first:
   - `hermes config path`
   - `hermes config env-path`
   - `hermes gateway status`
2. Search the gateway error log for polling conflicts:
   - `rg -n 'Telegram polling conflict|getUpdates request' .hermes/logs/gateway.error.log`
3. Count how persistent the conflict is:
   - `rg -c 'Telegram polling conflict' .hermes/logs/gateway.error.log`
4. Confirm the model path is not the main bottleneck with a minimal direct query:
   - `hermes chat -q 'Reply with exactly OK.' -Q`
5. Enumerate likely duplicate Hermes/gateway processes on the local machine:
   - `ps -Ao pid,ppid,etime,command | grep '/Users/.../.local/bin/hermes'`
   - `launchctl list | grep -i hermes`
6. If only one local gateway exists, expand suspicion to:
   - another `HERMES_HOME` on the same machine
   - another terminal running `hermes gateway run`
   - another profile/repo-local install
   - another machine using the same bot token
7. Treat repeated polling conflicts as the primary root cause for Telegram delay until disproven

Operational lesson:
- `gateway running` plus `telegram_api_ok=true` does not prove Telegram update consumption is healthy
- a gateway can look healthy while still losing the `getUpdates` lock to another bot instance
- when users report delayed Telegram responses, check polling conflict before deeper model-latency investigation

### Watchdog back-off behavior
A key operational lesson from practice:
- Running the watchdog every minute is fine for monitoring.
- It is **not** fine to restart the gateway every minute when the same network/connect failure keeps recurring.

Recommended watchdog behavior for `recent_connect_failure` repairs:
- keep health checks at a short cadence (for example 60s)
- apply exponential back-off only to the repair action
- use a max retry interval of 1 hour

Working schedule used here:
- 5m → 10m → 20m → 40m → 60m cap

Current repo-local watchdog behavior to preserve:
- launchd still runs the watchdog every 60 seconds for observation
- the backoff applies to repair actions, not to the health-check cadence
- `recent_connect_failure` with a new fingerprint can trigger repair only when the backoff window has expired
- an unchanged fingerprint should return an `awaiting_new_failure_signal` style outcome, not be treated as recovery
- if a `recent_connect_failure` repair command itself fails, the watchdog should still advance the backoff window so it does not retry the same broken repair every minute
- only clear the backoff window on genuinely healthy state, not merely because no new fingerprint appeared during the last minute

Important details:
- advance the back-off window even when the restart command itself fails, otherwise the watchdog can attempt the same broken repair every minute
- do not treat an unchanged error fingerprint as recovery; suppress duplicate retries until a new failure signal appears
- only clear the back-off window on genuinely healthy state, not merely because no *new* fingerprint appeared during the last minute

### Watchdog pitfall: repeated restarts without backoff
A practical failure mode discovered after adding the repo-local watchdog:
- launchd runs the watchdog every 60 seconds
- the watchdog may classify a "recent_connect_failure" by fingerprinting the latest matching lines in `gateway.error.log`
- if that fingerprint changes whenever new timeout lines are appended, the watchdog can keep deciding `restart` repeatedly even though the underlying issue is just unstable/recovering network conditions

Symptoms:
- `launchctl print gui/<uid>/ai.hermes.gateway-watchdog` shows increasing `runs`
- `gateway.error.log` contains repeated `Shutdown diagnostic` / restart-related churn
- `gateway-watchdog-state.json` keeps recording `last_action_reason: recent_connect_failure`
- Telegram Bot API direct checks may already be healthy while the gateway still gets bounced too often

Recommended design adjustment:
- add network-repair backoff for watchdog-triggered restarts
- apply backoff specifically to network-related reasons such as:
  - `telegram_api_recovered`
  - `recent_connect_failure`
- keep the watchdog check cadence frequent (for observation), but gate actual restart attempts with exponential backoff
- suggested restart cadence cap:
  - 5m → 10m → 20m → 40m → 60m → 60m ...
- reset the backoff only after a clearly healthy state is observed

Operational guidance:
- if the watchdog appears to be bouncing the gateway every minute, treat this as an over-eager repair policy, not necessarily a new Telegram config problem
- inspect both:
  - `.hermes/gateway-watchdog-state.json`
  - `.hermes/logs/gateway.error.log`
- distinguish:
  - watchdog scheduling working normally
  - watchdog repair policy being too aggressive

Example direct checks:

```bash
op read 'op://<vault>/skills-jk-hermes-local/TELEGRAM_BOT_TOKEN'
curl "https://api.telegram.org/bot$(op read 'op://<vault>/skills-jk-hermes-local/TELEGRAM_BOT_TOKEN')/getMe"
HERMES_HOME="$PWD/.hermes" hermes config env-path
```

### Important tool-layer pitfall
If you read a secret through a tool that redacts secrets in its returned output, then write that returned value back to a file, you can accidentally persist a masked `***` token.
Prefer shell-internal plumbing (`op run ... > file`) when materializing secrets so the secret value never round-trips through a redacted assistant/tool response.

### Fix order
1. Open the 1Password item
2. Set the field label to `TELEGRAM_BOT_TOKEN`
3. Paste the full BotFather token as the value
4. Re-run `bin/hermes-sync-env`
5. Confirm `.hermes/.env` matches what `op read` returns
6. Re-run gateway

## Pitfalls
- Do not write secrets into tracked files
- Do not rely on ad hoc names like `HERMES_EXAMPLE_TOKEN`
- Do not assume the documented example vault name is the actual local vault; inspect the real item first
- Do not treat `8600962995:***` as a usable token; that is not a valid credential
- If multiple 1Password items share the same title across vaults, prefer item ID when editing to avoid vault mismatch errors
- If you rename a field in 1Password, update `.env.1password` to the matching `op://<vault>/<item>/<field>` reference before re-running sync

## Helpful commands
Inspect item:

```bash
op item get skills-jk-hermes-local --format json
```

Check generated env keys without exposing values:

```bash
python3 - <<'PY'
from pathlib import Path
for line in Path('.hermes/.env').read_text().splitlines():
    if '=' in line and not line.lstrip().startswith('#'):
        print(line.split('=',1)[0] + '=<masked>')
PY
```

Check gateway status under repo-local Hermes home:

```bash
HERMES_HOME="$PWD/.hermes" hermes gateway status
```

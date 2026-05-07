---
name: hermes-session-forensics
description: Recover prior Hermes work by inspecting repo-local .hermes session files directly when session_search is too fuzzy or misses the exact session.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, sessions, forensics, recall, runtime, troubleshooting]
    related_skills: [hermes-agent]
---

# Hermes session forensics

Use this when the user refers to a prior Hermes session (for example: “that other session,” “continue the Vercel investigation,” or “find the corp-web-japan session”) and `session_search` does not reliably identify the exact conversation.

## Why this exists

`session_search` is useful for semantic recall, but it can miss the exact session when:
- the remembered phrasing differs from the stored summary
- the topic was only mentioned briefly
- the important clue is in raw message text, not the generated session summary
- the Hermes home is repo-local rather than the default `~/.hermes`

In this setup, Hermes state may live under a repo-local home such as:
- `~/workspace/skills-jk/.hermes`

So do not assume the default global path first.

## Recommended recovery order

1. **Check the active Hermes home**
   - Prefer the repo-local Hermes home if known for this setup.
   - In this environment, start with `~/workspace/skills-jk/.hermes`.

2. **Use `session_search` first for cheap recall**
   - Search broad topic keywords.
   - Useful for getting candidate session IDs quickly.

3. **If recall is ambiguous, inspect raw session files directly**
   - Search under:
     - `<HERMES_HOME>/sessions/`
   - Useful file patterns:
     - `session_*.json`
     - `*.jsonl`

4. **Search raw content, not just filenames**
   - Search for repo names, issue numbers, route paths, quoted user phrases, and tool arguments.
   - Good queries often include combinations like:
     - repo name (`corp-web-japan`)
     - symptom (`404`, `notFound`, `runtime log`, `vercel`)
     - exact user wording when available

5. **Interpret carefully**
   - A hit in the current session file is not evidence of the prior session.
   - Distinguish between:
     - current session discussing the search
     - older session that actually did the work

6. **Report confidence honestly**
   - If the exact prior session is not found, say so.
   - Then offer the strongest candidate session files instead of pretending to have found a match.

## Practical search pattern

Use database + file/content search in this order:

1. Check whether `<HERMES_HOME>/state.db` exists.
   - If it does, inspect it first.
   - Useful tables:
     - `sessions`
     - `messages`
   - In this setup, `sessions.source` is especially useful for distinguishing `cli` vs `telegram` work.

2. For **recent activity by time window** (for example “last 3 hours”), query `state.db` before trusting filenames.
   - Use `sessions.started_at` and `sessions.source`.
   - Then join `messages` on `session_id` to inspect actual user wording.
   - This is more reliable than guessing from `session_*.json` filenames alone.

3. List session artifacts on disk as a cross-check:
```text
<HERMES_HOME>/sessions/session_*.json
<HERMES_HOME>/sessions/*.jsonl
```
   - Filesystem enumeration is still useful, especially when the DB is stale, missing, or a session was interrupted.

4. Read `session_*.json` for metadata when needed:
```text
session_id
session_start
last_updated
message_count
platform
```
   - These files are often enough to identify candidate sessions quickly.
   - Do not expect a useful title to always be present.
   - Do not assume all `session_*.json` files in a recent window are distinct workstreams; interrupted/resumed conversations can create multiple nearby artifacts.

5. Then inspect `*.jsonl` for transcript content:
   - Use it to extract the first real user request, tool usage, and what work was actually done.
   - Search for the repository name, issue number, route path, or exact remembered phrase.

6. Search for the repository name or key phrase:
```text
corp-web-japan
```

7. Search for the symptom phrase:
```text
runtime log
404
notFound
vercel
```

8. Search for the user’s exact remembered wording if available.

## Edge cases

- Some short-lived or interrupted sessions may have a `session_*.json` metadata file but no matching `*.jsonl` transcript file.
- In that case, report it as a metadata-only candidate instead of pretending the content was recovered.
- If `session_search` says there was only one recent session but the filesystem shows more, trust the filesystem for exact recent-session enumeration.
- A long-lived CLI process can stay alive for days while the user uses `/clear`; process start time is not reliable evidence of recent work.
- If the user asks about **currently alive CLI sessions**, inspect the running Hermes processes directly and do not infer recency from their launch timestamps alone.
- If the user is trying to recover an **exact shell one-liner** they typed (for example a `git log`, `git show`, or `docker logs` command), Hermes session transcripts may only preserve summarized intent or tool arguments, not the literal shell history. In that case, after checking `state.db` and session files, fall back to the user's shell history such as `~/.zsh_history` and search the most recent few thousand lines for the relevant command family and keywords.

## Exact shell-command recovery fallback

Use this when the user says things like:
- "I used a one-line git command yesterday; do you remember it?"
- "Find the exact shell command I ran"
- "Recover the one-liner from my history"

Recommended order:
1. Search `session_search` and raw session files for semantic clues.
2. Query `state.db` messages for likely session IDs and timestamps.
3. If the exact command string is still missing, inspect shell history directly:
   - `~/.zsh_history`
   - other shell history files if the environment indicates a different shell
4. Search for both command family and domain keywords together, e.g.:
   - `git` + `mdx`
   - `git log` + `blog`
   - `docker logs` + container name
5. Report confidence honestly:
   - exact command recovered
   - probable candidates only
   - no literal command found in preserved history

## Live CLI session workflow

Use this when the user says things like:
- "find the live CLI session"
- "don't use Telegram sessions"
- "the process started days ago but I kept working in it"

1. Enumerate running Hermes processes.
   - Check commands like `hermes --yolo` and any `--resume <session_id>` arguments.
   - Capture `pid`, `tty`, elapsed time, and command.

2. Inspect each process environment.
   - Read `HERMES_HOME` and `PWD`/cwd for each PID.
   - Do not assume `~/.hermes`; live CLI processes may all point at a repo-local home such as `~/workspace/skills-jk/.hermes`.

3. Use `HERMES_HOME/state.db` as the source of truth.
   - Query `sessions` where `source='cli'`.
   - For live/open CLI sessions, filter with `ended_at is null`.
   - Join `messages` and use `max(messages.timestamp)` as the latest actual activity marker.

4. Distinguish **live process age** from **last conversational activity**.
   - Process `lstart` / elapsed time tells you how long the shell process has existed.
   - `max(messages.timestamp)` tells you when the CLI session last actually did work.
   - If the latter is old, say the process is still alive but there is no recent recorded CLI activity.

5. Only then cross-check session files under `<HERMES_HOME>/sessions/`.
   - Use them to inspect metadata or transcript details.
   - If recent files are all `platform=telegram`, do not mislabel them as CLI sessions.

6. Avoid broad home-directory searches unless necessary.
   - Searching all of `/Users/<user>` can hit permission errors and timeouts.
   - Scope content/file searches to the discovered `HERMES_HOME` first.

## What to extract for the user


If the user insists there is a recent CLI session and `state.db` does not show one, do not stop there. Check live processes.

1. Find active Hermes/Codex processes:
   - use `ps` to list `hermes`, `codex`, and gateway processes
2. Check each candidate process for:
   - current working directory (`cwd`) via `lsof -a -p <pid> -d cwd`
   - `HERMES_HOME` from `ps eww -p <pid>`
   - terminal association (`tty`) from `ps -o pid,ppid,tty,etime,lstart,command`
3. For macOS Terminal sessions, capture:
   - `TERM_SESSION_ID` from `ps eww -p <pid>`
   - then inspect matching files under `~/.zsh_sessions/` if needed
4. Verify which `state.db` the live process has open with `lsof -p <pid>`.
   - This is often more reliable than guessing the active Hermes home.

## Practical signals from live-process forensics

When a live Hermes CLI process is found, extract and report:
- PID
- tty
- process state from `ps` (for example `S`, `S+`, `T`, `Ss+`)
- elapsed runtime
- cwd
- command line (especially `--resume <session_id>`)
- `HERMES_HOME`
- `TERM_SESSION_ID`
- which `state.db` / logs are currently open

A `--resume <session_id>` argument is especially strong evidence for the underlying session identity even if recent turns are not yet visible in the DB.

## Additional anomaly checks for "weird" Hermes CLI state

When the user is not asking to recover a past session but to diagnose a suspicious live CLI state, add these checks:

1. Compare **live Hermes CLI process count** vs **`sessions where source='cli' and ended_at is null`** in `state.db`.
   - If the DB shows far more open CLI sessions than the actual live process count, treat that as evidence that session shutdown bookkeeping is not completing reliably.
   - Also compute how many of those open CLI sessions have been idle for a long time (for example 24h+) by looking at the latest `messages.timestamp` per session.

2. Check for **multiple Hermes PIDs on the same `tty` or `TERM_SESSION_ID`**.
   - This is a strong sign that an earlier CLI instance in the same terminal tab did not shut down cleanly and a newer Hermes was launched on top of it.
   - The combination `same tty + same TERM_SESSION_ID + multiple Hermes PIDs` is especially suspicious.

3. Inspect the **process state flags**.
   - `T` means stopped/suspended and is not a cleanly exited CLI.
   - A stopped Hermes sharing a tty with a newer active Hermes instance is a useful concrete finding to report.

4. Cross-check `errors.log` for shutdown / interruption symptoms.
   - In particular, warnings like `Agent thread still alive after interrupt` are relevant evidence when open sessions and duplicate processes accumulate.

5. Separate **runtime provider/model issues** from **process/session cleanup issues**.
   - Auxiliary-provider failures (timeouts, 429s, unsupported model errors, memory-flush warnings) can coexist with bad session cleanup.
   - Report them as parallel contributing symptoms, not as proof that one caused the other unless the logs show the direct sequence.

## What to extract for the user

When you find likely matches, summarize:
- session ID / filename
- approximate timestamp
- repo involved
- whether it is an exact match or only a candidate
- the most relevant evidence line(s)
- what was actually accomplished in that session

## Important lessons learned

- Direct inspection of raw session files can outperform `session_search` for exact recovery.
- Repo-local Hermes homes matter; checking the wrong `.hermes` tree leads to false negatives.
- Searching only for high-level labels like “Vercel runtime log” may fail even when the session discussed the same underlying issue using different wording.
- When searching for a remembered past task, combine semantic recall (`session_search`) with raw transcript forensics (`search_files` on session JSON).

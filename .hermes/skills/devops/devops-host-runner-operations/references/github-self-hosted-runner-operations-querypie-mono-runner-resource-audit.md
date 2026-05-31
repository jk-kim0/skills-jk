# QueryPie mono runner resource audit notes

Use this reference when updating `chequer-io/querypie-mono` GitHub Wiki runner status pages with self-hosted runner resource investigations.

## Wiki shape

- Main status index: `Self‐Hosted-Runner-Status.md`.
- Per-runner pages use `SVR-...-Status.md` page files, e.g. `SVR-L2-RUNNER-6-Status.md`.
- Append investigation sections to the relevant per-runner page, then commit/push the wiki repo.
- Keep per-runner results separate; do not collapse multiple machines into one long monolithic note.

## Connection mapping used in the audit

L2 runners:

| Runner | SSH user | Runner root |
|---|---|---|
| `SVR-L2-RUNNER-1`..`SVR-L2-RUNNER-6` | `ubuntu` | `/home/ubuntu/actions-runner` |

L3 runners:

| Runner | SSH user | Runner root |
|---|---|---|
| `SVR-L3-RUNNER-1`..`SVR-L3-RUNNER-2` | `deploy` | `/home/deploy/actions-runner` |

Pitfall: L3 runners can fail with QueryPie authentication when probed as `ubuntu`; use the account recorded in the existing wiki page (`deploy`) before concluding the host is inaccessible.

## `/actions-runner` disk usage probe pattern

Run read-only probes only. Do not print secrets or file contents.

Recommended remote categories:

```sh
RUNNER=/home/ubuntu/actions-runner   # or /home/deploy/actions-runner on L3
hostname; whoami; uname -a
du -sh "$RUNNER"
du -xh --max-depth=1 "$RUNNER" | sort -hr | sed -n '1,80p'
du -xh --max-depth=1 "$RUNNER/_work" | sort -hr | sed -n '1,80p'
du -xh --max-depth=2 "$RUNNER/_work" | sort -hr | sed -n '1,80p'
for p in "$RUNNER/_diag" "$RUNNER/_work/_temp" "$RUNNER/_work/_tool" "$RUNNER/_work/_actions" "$RUNNER/_work/_update"; do
  [ -e "$p" ] && du -sh "$p"
done
find "$RUNNER/_work" -mindepth 3 -maxdepth 3 -type d -name .git -exec du -sh {} + | sort -hr | sed -n '1,80p'
find "$RUNNER" -xdev -type f -printf '%s\t%TY-%Tm-%Td %TH:%TM\t%p\n' | sort -nr | sed -n '1,80p'
find "$RUNNER" -xdev -type f \( -iname '*.log' -o -iname '*.diag' -o -iname '*.txt' \) -printf '%s\t%TY-%Tm-%Td %TH:%TM\t%p\n' | sort -nr | sed -n '1,80p'
```

For repo-level attribution, inspect `du -xh --max-depth=2 "$RUNNER/_work/<repo>/<repo>"` for the largest `_work` entries.

## Interpretation lessons from 2026-05 querypie-mono audit

- For L2 runners, `/home/ubuntu/actions-runner` being 18-28G was mostly `_work`, not logs.
- Common root causes:
  - repo checkout `.git/objects` pack files and Git LFS;
  - lingering `node_modules` and build outputs under `_work/<repo>/<repo>`;
  - `_work/_tool` toolcache for CodeQL, Go, Java, Node, Python, uv;
  - transient `_work/_temp/*/cache.tgz` or `cache.tzst` created by currently running jobs.
- `_diag` logs were usually only ~500-700MB and individual runner logs were around 8MB. They are safe cleanup candidates, but deleting logs does not solve a 20G+ runner root.
- L3 runners can have much larger `_work/_tool`, especially CodeQL. One observed L3 runner had `_work/_tool` 40G with CodeQL 32G because many CodeQL versions accumulated.
- Existing runner updates can leave old `bin.<version>`, `externals.<version>`, and `_work/_update` directories. If current `bin`/`externals` symlinks point to the newer version, the old version is a cleanup candidate, but treat it as a rollback-policy decision rather than an automatic delete.

## Cleanup guidance to document

Always state that cleanup should happen only when the runner is `busy=false`.

Good cleanup candidate taxonomy:

| Candidate | Reclaim potential | Risk |
|---|---:|---|
| `_work/_temp` orphan cache archives | high if present | avoid while jobs run |
| `_diag` old logs | low/medium | usually safe; small impact |
| stale `_work/<repo>/<repo>` workspaces | high | next job reclones/rebuilds |
| old `_work/_tool` versions | medium/high, especially CodeQL | next job redownloads tools |
| old `bin.*`/`externals.*` and `_work/_update` | medium | confirm runner rollback/update policy |

Do not present logs as the primary cause unless the measurements show they dominate. Prefer evidence-backed wording like: “logs are cleanup candidates, but the main driver is `_work` checkout/toolcache.”

---
name: macos-system-data-disk-investigation
description: Investigate sudden macOS Storage/System Data growth by separating APFS accounting artifacts from real large consumers like Docker sparse disks, local snapshots, app VM bundles, and caches.
---

# macOS System Data Disk Investigation

Use when the user says macOS `System Data` or `System Data/Other` suddenly grew, especially by tens or hundreds of GiB.

## Goal
Determine whether the growth is:
1. real on-disk usage,
2. APFS/sparse-file accounting,
3. local snapshots/purgeable space,
4. container/VM data (especially Docker), or
5. large app support/model/cache files.

## Key findings this workflow is designed to catch
- Docker Desktop often appears under macOS `System Data` via:
  - `~/Library/Containers/com.docker.docker`
  - `~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw`
- `Docker.raw` can have a much larger logical size than actual allocated size.
  - Check both `ls -lh` and `du -h`.
- `docker system df -v` can reveal large build cache usage even when containers/volumes are small.
- Local Time Machine/APFS snapshots may be absent; verify before blaming snapshots.
- If `diskutil apfs listSnapshots /` shows only a single `com.apple.os.update-*` snapshot, treat that as an OS update snapshot, not evidence of bulk local snapshot accumulation.
- Large repo-local runtime artifacts can also be a major hidden contributor when the user does lots of local agent/repo work, especially Hermes checkpoints under a workspace repo such as:
  - `~/workspace/skills-jk/.hermes/checkpoints`
  - many checkpoint directories with git `objects/pack/*.pack` files can add up to tens of GiB
- Large app artifacts can also contribute, e.g.:
  - Claude VM bundles under `~/Library/Application Support/Claude/vm_bundles/`
  - Chrome on-device model weights under `~/Library/Application Support/Google/.../weights.bin`
- macOS free-space/System Data figures can fluctuate during inspection; a single `df` reading is not enough evidence.

## Investigation order

### 1) Establish live filesystem state
Run:
```bash
pwd
 date
 df -h /
```

If needed, inspect APFS volume accounting:
```bash
diskutil apfs listVolumeGroups
```
Look for the Data volume’s consumed size.

### 2) Check for local snapshots first
Do not guess.
Run:
```bash
tmutil listlocalsnapshots /
 diskutil apfs listSnapshots /
```
If none are present, rule snapshots out explicitly.

### 3) Find the biggest high-yield top-level buckets first
Start with both the home directory and Library, because `System Data` growth can actually be dominated by repo/workspace data rather than only `~/Library`:
```bash
du -xhd 1 ~ 2>/dev/null | sort -h | tail -n 30
 du -xhd 1 ~/Library 2>/dev/null | sort -h | tail -n 30
 du -xhd 1 ~/workspace 2>/dev/null | sort -h | tail -n 50
 du -xhd 1 ~/Library/Containers 2>/dev/null | sort -h | tail -n 30
 du -xhd 1 ~/Library/'Application Support' 2>/dev/null | sort -h | tail -n 30
```
If one repo dominates, immediately drill into it before spending time on lower-yield system paths.

### 4) Search for very large files
```bash
find ~/Library -type f -size +2G -print 2>/dev/null | head -n 100
```
Then measure suspicious files with both logical and actual size:
```bash
ls -lh <file1> <file2>
 du -h <file1> <file2>
 stat -f '%N %z bytes' <file1> <file2>
```
Important for sparse images like Docker.raw.

### 5) If Docker is present, inspect it explicitly
Check the container directory size:
```bash
du -hd 1 ~/Library/Containers 2>/dev/null | sort -h | tail -n 30
```
Then inspect Docker usage:
```bash
docker system df -v
```
Interpretation:
- Large `Build cache usage` with small image/container totals usually means build cache is the main real consumer.
- A very large `Docker.raw` logical size does not automatically mean that many GiB are truly allocated.

### 6) Inspect repo-local runtime/checkpoint stores when workspace usage is large
If `~/workspace` or a specific repo is unexpectedly huge, check for agent/runtime artifacts before assuming user files are the cause:
```bash
du -xhd 1 ~/workspace/<repo> 2>/dev/null | sort -h | tail -n 50
 du -xhd 2 ~/workspace/<repo>/.hermes 2>/dev/null | sort -h | tail -n 80
```
For Hermes checkpoint explosions, quantify count and recent growth:
```bash
python3 - <<'PY'
import os, subprocess, time
base = os.path.expanduser('~/workspace/skills-jk/.hermes/checkpoints')
rows = []
for name in os.listdir(base):
    p = os.path.join(base, name)
    if not os.path.isdir(p):
        continue
    kb = int(subprocess.check_output(['du', '-sk', p], text=True).split('\t', 1)[0])
    st = os.stat(p)
    rows.append((name, kb, st.st_mtime))
rows.sort(key=lambda x: x[2])
now = max(m for _, _, m in rows)
print('count', len(rows))
print('total_gib', round(sum(kb for _, kb, _ in rows) / 1024 / 1024, 2))
recent = [(n, kb, m) for n, kb, m in rows if now - m <= 24 * 3600]
print('last24h_count', len(recent))
print('last24h_gib', round(sum(kb for _, kb, _ in recent) / 1024 / 1024, 2))
PY
```
This is especially useful when dozens of sub-1GiB checkpoints together explain a sudden 10s-of-GiB increase.

### 7) Sample caches and system-ish paths only after the obvious large consumers
If needed:
```bash
du -hd 1 ~/Library/Caches 2>/dev/null | sort -h | tail -n 30
 du -sh /private/var/folders /private/var/log /private/var/vm /private/var/tmp /private/var/db 2>/dev/null
```
If broad `du` commands time out, use a scripted per-subdirectory scan rather than retrying the same expensive command.

## Practical heuristics
- If `tmutil` snapshots are empty and Docker.raw was recently modified, Docker is the leading suspect.
- If `ls` shows Docker.raw at e.g. 128G but `du` shows ~27G, explain the difference as sparse-file accounting.
- If macOS UI reports `System Data` wildly larger than the sum of obvious files, mention APFS/purgeable/accounting effects rather than overstating certainty.
- Distinguish:
  - actual allocated size,
  - logical file size,
  - macOS Storage UI category accounting.

## Reporting format
Summarize with:
1. top proven large consumers,
2. whether snapshots exist,
3. whether Docker sparse-file accounting is involved,
4. whether the growth appears real vs mostly accounting,
5. safe next cleanup candidates.

Example conclusion structure:
- `Most likely real growth source: Docker build cache / Docker.raw`
- `Snapshots: none`
- `Additional large artifacts: Claude VM bundle, Chrome model weights`
- `Caveat: macOS System Data may over-report sparse/APFS-managed storage`

## Cleanup guidance
Do not delete automatically unless the user asks.
Prefer proposing targeted next steps such as:
- `docker builder prune` / `docker system prune`
- review and possibly remove unused VM bundles
- clear oversized app caches
- re-check free space after cleanup

If the user explicitly asks you to free disk space, use this safe cleanup order:
1. Re-check live free space first with `df -h /` because APFS/macOS accounting may have already rebounded.
2. If Docker is a top consumer and no containers are running, run:
   - `docker system prune -af`
   - `docker builder prune -af`
3. Re-check both `du -h ~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw` and `ls -lh .../Docker.raw` after prune. Logical size may stay large while actual allocated size drops sharply.
4. Inspect remaining Docker volumes with `docker system df -v` / `docker volume ls`.
   - It is usually safe to remove unlinked anonymous volumes and inactive buildx state volumes such as `buildx_buildkit_*_state`.
   - Preserve named data volumes that look user-meaningful (for example DB volumes like `deck-postgres-main`) unless the user clearly wants them removed.
5. Safe user-cache cleanup candidates that are typically regenerable:
   - `~/Library/Caches/JetBrains`
   - `~/Library/Caches/Google`
   - `~/Library/Caches/ms-playwright`
   - `~/Library/Caches/Homebrew`
   - other obviously regenerable tool caches
6. Expect best-effort behavior for app caches in use (for example Chrome/Google cache directories may leave behind live files while the app is running). Re-measure instead of retrying aggressively.
7. Do not remove large user-data or VM artifacts without explicit confirmation, especially:
   - `~/Library/Containers/com.utmapp.UTM`
   - `~/Library/Application Support/Claude/vm_bundles`
   - large app model/runtime payloads under `~/Library/Application Support/...`

When reporting cleanup, include:
- how much space was reclaimed,
- which classes of data were removed,
- which large items were deliberately preserved,
- the final `df -h /` result.

## Pitfalls
- Do not rely on one `df` snapshot only.
- Do not equate `System Data` exactly with `/System` usage.
- Do not treat Docker.raw logical size as actual usage without checking `du`.
- Do not blame Time Machine snapshots without evidence.
- Broad `du` over `/System/Volumes/Data` can be too slow; pivot to narrower high-yield directories.

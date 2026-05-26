# Behind-main untracked upstream collapse

Use this note during `skills-jk` local workspace sweeps when root `main` is behind `origin/main` and local dirty state appears to include untracked skill/reference files.

## Pattern

1. Fetch first and inspect both root status and `main...origin/main`.
2. For each untracked skill/reference file that looks meaningful, check whether the same path already exists in `origin/main`.
3. If it exists, compare bytes against `git show origin/main:<path>` before treating it as local work.
4. If the untracked file is byte-identical to `origin/main:<path>`, classify it as a behind-main artifact, not a PR payload.
5. Save a safety backup of tracked diff plus untracked files before cleanup.
6. Remove only the confirmed duplicate untracked blockers and runtime residue, then fast-forward root `main` to `origin/main`.
7. Re-run root status after the fast-forward; runtime SQLite WAL/SHM files such as `.hermes/kanban.db-wal` can reappear during the session and should be removed again if they are the only residue.

## Reporting

Report that no PR/worktree was created when every apparent local skill/reference change either:

- was already present in `origin/main`, or
- was runtime/backup residue such as `.hermes/kanban.db-wal`, `.hermes/kanban.db-shm`, or `.hermes/skills/.curator_backups/`.

Include the backup directory path if one was created, and verify `main` equals `origin/main` with a clean root status before finishing.

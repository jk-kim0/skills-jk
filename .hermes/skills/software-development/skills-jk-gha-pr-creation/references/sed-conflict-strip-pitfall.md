# Rebase conflict marker stripping: sed pitfalls

## Problem

When resolving rebase conflicts in `skills-jk` append-only markdown files (especially `.hermes/memories/*.md` and skill `SKILL.md` files), using `sed` to strip conflict markers without careful direction can silently discard one side.

## The trap

A naive `sed -e '/<<<<<<< HEAD/,/=======/d' -e '/>>>>>>>/d'` **only keeps the remote side** (`======` to `>>>>>>>`) and silently **discards the local side** (`<<<<<<< HEAD` to `=======`).

In this repo, both sides often contain independently valid new entries:
- Local side = your carefully authored new bullets
- Remote side = freshly merged entries from another follow-up PR

## Session evidence

A rebase of `docs/hermes-skill-followup-20260516f` onto `origin/main` produced a conflict in `skills-jk-gha-pr-creation/SKILL.md`. The agent ran:

```bash
sed -e '/<<<<<<< HEAD/,/=======/d' -e '/>>>>>>>/d' FILE
```

This stripped the HEAD-side bullet about squash-merged PR worktree cleanup (`references/squash-merged-pr-worktree-cleanup.md`). The agent did not notice the omission until a later re-read of the resolved file, requiring a manual patch to re-insert the lost content.

## Correct approaches

1. **Prefer manual inspection.** Read the conflict block and keep both sides' new entries unless they are true duplicates.
2. **If using sed for quick strip, choose the side to keep explicitly:**
   - Keep HEAD side:
     ```bash
     sed -e '/<<<<<<< HEAD/d' -e '/=======/,/>>>>>>>/d'
     ```
   - Keep remote side:
     ```bash
     sed -e '/<<<<<<< HEAD/,/=======/d' -e '/>>>>>>>/d'
     ```
   But always re-read the file afterward.
3. **Post-stripping required verification:**
   - Re-read the resolved file to confirm both local and remote additions are present
   - Search for leftover markers: `rg -n '^(<<<<<<<|=======|>>>>>>>)' <files...>`
   - Check file structure integrity (no broken lists, orphaned separators)
4. **Preserve separators:** Keep `§` delimiters in memory files intact.
5. **YAML parse check:** For `.yaml` conflicts:
   ```bash
   python3 -c 'import yaml, pathlib; yaml.safe_load(pathlib.Path("path/to/file").read_text())'
   ```
6. **Source of truth:** When resolving against latest `main`, prefer the actual `origin/main` file content (`git show origin/main:path`) as the source of truth rather than guessing which side to keep.

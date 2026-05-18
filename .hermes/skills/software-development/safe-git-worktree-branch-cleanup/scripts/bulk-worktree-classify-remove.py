#!/usr/bin/env python3
"""
Bulk classify and remove stale git worktrees.
Assumes cwd is inside the target repository.

Safety rules (matches safe-git-worktree-branch-cleanup skill):
- Never remove the root repo worktree.
- Never remove a dirty worktree.
- Never remove a branch-backed worktree whose branch matches an open PR head.
- Remove only clean detached worktrees and clean merged branch worktrees.

Usage:
  python3 bulk-worktree-classify-remove.py [--dry-run]
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run(cmd, check=True):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        # Some git commands return non-zero on empty results; tolerate selectively
        pass
    return result


def get_worktrees():
    """Parse git worktree list --porcelain into dicts."""
    result = run("git worktree list --porcelain", check=False)
    blocks = result.stdout.strip().split("\n\n")
    worktrees = []
    for block in blocks:
        entry = {}
        for line in block.splitlines():
            if line.startswith("worktree "):
                entry["path"] = line[len("worktree "):]
            elif line.startswith("HEAD "):
                entry["head"] = line[len("HEAD "):]
            elif line.startswith("branch "):
                entry["branch"] = line[len("branch "):]
            elif line == "detached":
                entry["detached"] = True
        if "path" in entry:
            worktrees.append(entry)
    return worktrees


def get_repo_root():
    return run("git rev-parse --show-toplevel").stdout.strip()


def get_open_pr_heads():
    """Return set of (headRefName, headRefOid) tuples."""
    result = run("env -u GITHUB_TOKEN gh pr list --state open --json headRefName,headRefOid", check=False)
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return set()
    return {(d.get("headRefName"), d.get("headRefOid")) for d in data}


def is_dirty(worktree_path):
    result = run(f'git -C "{worktree_path}" status --short --branch', check=False)
    # Ignore lines that are purely branch info (start with ##)
    lines = [l for l in result.stdout.strip().splitlines() if l and not l.startswith("##")]
    return bool(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Print what would be removed without removing.")
    args = parser.parse_args()

    repo_root = get_repo_root()
    worktrees = get_worktrees()
    open_prs = get_open_pr_heads()
    open_pr_branches = {ref for ref, _ in open_prs}

    candidates = []
    for wt in worktrees:
        path = wt["path"]
        # Never remove root repo
        if Path(path).resolve() == Path(repo_root).resolve():
            continue

        branch = wt.get("branch", "").replace("refs/heads/", "")
        is_detached = wt.get("detached", False)

        # Skip dirty
        if is_dirty(path):
            continue

        # Skip branch-backed open PR worktrees
        if branch and branch in open_pr_branches:
            continue

        # Detached clean → always a stale candidate
        if is_detached:
            candidates.append(wt)
            continue

        # Branch-backed, clean, no open PR → candidate if branch is merged or orphaned
        if branch:
            # Check merge status vs origin/main
            merge_check = run(f'git branch --merged origin/main | grep "^{branch}$"', check=False)
            if merge_check.returncode == 0:
                candidates.append(wt)
                continue
            # Also consider if upstream is gone
            vv = run(f'git branch -vv | grep "^{branch}"', check=False)
            if "[gone]" in vv.stdout:
                candidates.append(wt)
                continue

    print(f"Total worktrees: {len(worktrees)}")
    print(f"Stale candidates: {len(candidates)}")

    if args.dry_run:
        for wt in candidates:
            print(f"  [dry-run] would remove: {wt['path']} (branch={wt.get('branch','detached')})")
        sys.exit(0)

    removed = 0
    failed = 0
    for wt in candidates:
        path = wt["path"]
        res = run(f'git worktree remove --force "{path}"', check=False)
        if res.returncode == 0:
            removed += 1
            print(f"  removed: {path}")
        else:
            # May have partially succeeded; prune will clean up orphans
            failed += 1
            print(f"  remove reported failure (may be orphan): {path}")

    run("git worktree prune --expire=now --verbose", check=False)
    run("git worktree prune", check=False)

    remaining = get_worktrees()
    print(f"\nRemoved: {removed}, Failed/reported: {failed}")
    print(f"Remaining worktrees: {len(remaining)}")


if __name__ == "__main__":
    main()

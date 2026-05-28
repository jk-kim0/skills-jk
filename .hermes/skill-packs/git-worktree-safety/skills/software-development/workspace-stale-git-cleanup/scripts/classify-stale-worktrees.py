#!/usr/bin/env python3
"""
Classify local git worktrees as stale or keep.
Reads `git worktree list --porcelain` and cross-checks open PRs via `gh` CLI.
Outputs JSON with `stale_candidates` and `keep` arrays.

Usage:
    python3 scripts/classify-stale-worktrees.py /path/to/repo

Requires: GitHub CLI (`gh`) authenticated, `git` available.
"""
import json, shlex, subprocess, sys


def run(cmd: str, cwd: str | None = None) -> tuple[str, str, int]:
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    return r.stdout.strip(), r.stderr.strip(), r.returncode


def main(repo_dir: str | None) -> None:
    repo = repo_dir or "."

    # Open PR heads
    out, _, _ = run(
        "env -u GITHUB_TOKEN gh pr list --state open --json headRefName,headRefOid",
        cwd=repo,
    )
    open_prs: list[dict] = json.loads(out) if out else []
    open_heads: set[str] = {p["headRefName"] for p in open_prs}
    open_oids: set[str] = {p["headRefOid"] for p in open_prs}

    # Parse `git worktree list --porcelain`
    out, _, _ = run("git worktree list --porcelain", cwd=repo)
    lines = out.split("\n")
    worktrees: list[dict] = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("worktree "):
            wt: dict = {"path": line[9:]}
            i += 1
            while i < len(lines) and lines[i].strip():
                l2 = lines[i].strip()
                if l2.startswith("HEAD "):
                    wt["head"] = l2[5:]
                elif l2.startswith("branch "):
                    wt["branch"] = l2[7:]
                i += 1
            worktrees.append(wt)
        else:
            i += 1

    stale: list[dict] = []
    keep: list[dict] = []

    # Determine root worktree path once
    root_path, _, _ = run("git -C {} rev-parse --show-toplevel".format(shlex.quote(repo)), cwd=repo)

    for wt in worktrees:
        path = wt["path"]
        if path == root_path:
            continue

        branch = wt.get("branch", "").replace("refs/heads/", "")
        head = wt.get("head", "")

        # Open PR branch match
        if branch and branch in open_heads:
            keep.append({"path": path, "branch": branch, "reason": "open-pr"})
            continue

        # Alias worktree matching open PR by SHA
        if head in open_oids:
            keep.append(
                {
                    "path": path,
                    "branch": branch,
                    "reason": "alias-of-open-pr",
                    "head": head,
                }
            )
            continue

        # Dirty check
        st_out, _, _ = run("git -C {} status --short".format(shlex.quote(path)))
        if st_out:
            keep.append(
                {
                    "path": path,
                    "branch": branch,
                    "reason": "dirty",
                    "status_preview": st_out[:200],
                }
            )
            continue

        stale.append({"path": path, "branch": branch, "head": head})

    result = {
        "repo": root_path or repo,
        "open_pr_count": len(open_prs),
        "stale_candidates": stale,
        "keep": keep,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)

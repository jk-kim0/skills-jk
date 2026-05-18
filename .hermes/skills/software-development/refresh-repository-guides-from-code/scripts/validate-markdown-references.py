#!/usr/bin/env python3
"""Validate repository markdown references used by docs-refresh tasks.

Checks:
- relative markdown links point to existing files/directories
- GitHub blob/tree links pinned to a commit in the current repository resolve at that commit

Run from the repository root:
  python3 <skill-dir>/scripts/validate-markdown-references.py docs
"""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys
import urllib.parse

MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
GITHUB_PINNED_RE = re.compile(
    r"https://github\.com/([^/]+/[^/]+)/(?:blob|tree)/([0-9a-f]{7,40})/([^\s)]+)"
)


def git_remote_owner_repo() -> str | None:
    try:
        remote = subprocess.check_output(["git", "remote", "get-url", "origin"], text=True).strip()
    except Exception:
        return None
    remote = remote.removesuffix(".git")
    if "github.com:" in remote:
        return remote.split("github.com:", 1)[1]
    if "github.com/" in remote:
        return remote.split("github.com/", 1)[1]
    return None


def git_path_exists(commit: str, path: str) -> bool:
    return subprocess.run(
        ["git", "cat-file", "-e", f"{commit}:{path}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode == 0


def iter_markdown_files(paths: list[str]) -> list[pathlib.Path]:
    files: list[pathlib.Path] = []
    for raw in paths:
        p = pathlib.Path(raw)
        if p.is_file() and p.suffix.lower() in {".md", ".mdx"}:
            files.append(p)
        elif p.is_dir():
            files.extend(sorted(q for q in p.rglob("*") if q.is_file() and q.suffix.lower() in {".md", ".mdx"}))
    return sorted(set(files))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", help="Markdown files/directories to validate")
    parser.add_argument("--owner-repo", default=git_remote_owner_repo(), help="GitHub owner/repo for pinned link checks")
    args = parser.parse_args()

    errors: list[str] = []
    files = iter_markdown_files(args.paths)

    for md in files:
        text = md.read_text(errors="replace")
        for _label, url in MD_LINK_RE.findall(text):
            if url.startswith(("http://", "https://", "#", "mailto:")):
                continue
            target = urllib.parse.unquote(url.split("#", 1)[0])
            if not target:
                continue
            if not (md.parent / target).resolve().exists():
                errors.append(f"{md}: missing relative markdown link: {url}")

        for owner_repo, commit, url_path in GITHUB_PINNED_RE.findall(text):
            if args.owner_repo and owner_repo != args.owner_repo:
                continue
            path = urllib.parse.unquote(url_path)
            if not git_path_exists(commit, path):
                errors.append(f"{md}: missing commit-pinned GitHub path: {commit}:{path}")

    if errors:
        print("\n".join(errors))
        print(f"error_count {len(errors)}")
        return 1
    print(f"validated {len(files)} markdown files; error_count 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())

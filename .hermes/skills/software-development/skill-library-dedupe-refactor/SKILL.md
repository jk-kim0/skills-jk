---
name: skill-library-dedupe-refactor
description: Use when auditing the skills-jk skill library for duplicate or near-duplicate skills and reference documents, then consolidating the overlapping content into canonical owner skills/references without losing durable guidance.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [skills-jk, skills, dedupe, refactor, references]
    related_skills: [skills-jk, hermes-agent-skill-authoring, git-worktree-safety-pack]
---

# Skill Library Dedupe Refactor

## Overview

Use this skill to find and remove duplicated procedure text, duplicated `SKILL.md` responsibilities, and duplicated `references/` documents inside the `skills-jk` repository.

The goal is not to delete useful knowledge. The goal is to choose one canonical owner for each recurring workflow, merge unique durable guidance into that owner, delete or thin out redundant siblings, and verify that future agents can still discover the resulting source of truth.

This workflow applies to all checked-in skill roots in this repository:

- `.hermes/skills/**/SKILL.md` and `.hermes/skills/**/references/*`
- `.hermes/skill-packs/**/SKILL.md` and `.hermes/skill-packs/**/references/*`
- `skills/**/SKILL.md` and `skills/**/references/*`

## When to Use

Use this skill when the user asks to:

- find duplicate skills or duplicate reference documents in this repo;
- reduce overlap between active skills, inactive skill packs, and root-level governed skills;
- refactor near-duplicate `references/*.md` files into canonical topic-level references;
- review newly migrated skills for overlap with existing owners;
- clean up session/PR/incident-named reference files that repeat durable guidance already documented elsewhere.

Do not use this skill for ordinary local branch/worktree cleanup. For stale worktrees, dirty root preservation, or repeated `workspace 정리`, use `git-worktree-safety-pack` first.

## Required Setup

1. Work from the repository root and start from latest `origin/main` in a repo-root worktree.
2. If root `main` has unrelated dirty changes, do not stage them. Either preserve them in their own PR if requested, or create the dedupe/refactor branch from `origin/main` and leave root unchanged.
3. Before creating any new reference file, read `skills-jk` reference `references/reference-dedupe-preflight.md`.
4. Before adding a new skill, inspect existing owners first. Prefer updating a canonical class-level skill over creating a narrow sibling.

Recommended branch naming:

```bash
branch=docs/skill-library-dedupe-refactor
wt=.worktrees/skill-library-dedupe-refactor
git fetch --prune origin
git worktree add "$wt" -b "$branch" origin/main
```

## Discovery Pass

Run the scans in layers. Do not start by opening every file manually.

### 1. Inventory all skill files

```bash
python3 - <<'PY'
from pathlib import Path
roots = [Path('.hermes/skills'), Path('.hermes/skill-packs'), Path('skills')]
for root in roots:
    if not root.exists():
        continue
    print(f'## {root}')
    for path in sorted(root.rglob('SKILL.md')):
        print(path.as_posix())
PY
```

Look for:

- identical `name:` values in different locations;
- same directory basename under multiple roots;
- narrow one-session skill names where an umbrella skill already exists;
- active skills that duplicate inactive skill-pack detailed procedures;
- root-level governed skills that mostly restate a class-level `.hermes/skills/**` owner.

### 2. Parse frontmatter and group likely duplicate skills

```bash
python3 - <<'PY'
from pathlib import Path
from collections import defaultdict
import re
try:
    import yaml
except Exception as e:
    raise SystemExit(f'PyYAML required: {e}')
roots = [Path('.hermes/skills'), Path('.hermes/skill-packs'), Path('skills')]
by_name = defaultdict(list)
by_desc = defaultdict(list)
for root in roots:
    if not root.exists():
        continue
    for path in sorted(root.rglob('SKILL.md')):
        text = path.read_text(errors='ignore')
        m = re.match(r'^---\n(.*?)\n---\n', text, re.S)
        if not m:
            print(f'BAD_FRONTMATTER\t{path}')
            continue
        data = yaml.safe_load(m.group(1)) or {}
        name = str(data.get('name','')).strip()
        desc = re.sub(r'\s+', ' ', str(data.get('description','')).strip().lower())
        by_name[name].append(path.as_posix())
        by_desc[desc].append(path.as_posix())
print('## duplicate names')
for key, paths in sorted(by_name.items()):
    if key and len(paths) > 1:
        print(key, *paths, sep='\n  ')
print('## duplicate descriptions')
for key, paths in sorted(by_desc.items()):
    if key and len(paths) > 1:
        print(key, *paths, sep='\n  ')
PY
```

Treat exact duplicate names or descriptions as high-confidence review targets, not automatic delete targets.

### 3. Find exact and normalized duplicate references

```bash
python3 - <<'PY'
from pathlib import Path
from collections import defaultdict
import hashlib, re
roots = [Path('.hermes/skills'), Path('.hermes/skill-packs'), Path('skills')]
exact = defaultdict(list)
normalized = defaultdict(list)
for root in roots:
    if not root.exists():
        continue
    for path in root.rglob('*'):
        if path.is_file() and '/references/' in path.as_posix() and path.suffix.lower() in {'.md', '.txt'}:
            raw = path.read_bytes().strip()
            exact[hashlib.sha256(raw).hexdigest()].append(path.as_posix())
            text = path.read_text(errors='ignore')
            norm = re.sub(r'\s+', ' ', text).strip().lower().encode()
            normalized[hashlib.sha256(norm).hexdigest()].append(path.as_posix())
print('## exact duplicate reference groups')
for paths in exact.values():
    if len(paths) > 1:
        print('\n'.join(paths), end='\n\n')
print('## normalized duplicate reference groups')
for paths in normalized.values():
    if len(paths) > 1:
        print('\n'.join(paths), end='\n\n')
PY
```

Exact duplicates under `.hermes/skills/.archive/**/references/` can usually be deleted if an active non-archive copy exists. Active duplicates need a canonical owner decision first.

### 4. Find stale session/PR/incident reference names

```bash
python3 - <<'PY'
from pathlib import Path
import re
roots = [Path('.hermes/skills'), Path('.hermes/skill-packs'), Path('skills')]
pattern = re.compile(r'(^|[-_/])(pr-?\d+|issue-?\d+|\d{8}|\d{4}-\d{2}-\d{2})([-_.]|$)', re.I)
for root in roots:
    if not root.exists():
        continue
    for path in sorted(root.rglob('*')):
        if path.is_file() and '/references/' in path.as_posix() and pattern.search(path.as_posix()):
            print(path.as_posix())
PY
```

Session/PR-number names are not always wrong, but they are strong candidates for merging into a topic-level reference.

### 5. Cluster near-duplicates instead of global all-pairs review

A full pairwise similarity scan across the library can be too slow and noisy. First group by owner and topic tokens, then compare within those smaller clusters.

Useful tokens:

- `worktree`, `cleanup`, `dirty`, `preservation`, `rebase`
- `github`, `pr`, `workflow`, `ci`, `checks`
- `vercel`, `runtime`, `logs`, `deployment`
- `nextjs`, `rsc`, `tailwind`, `mdx`, `wiki`
- `skill`, `reference`, `dedupe`, `memory`, `governed`

Example clustered scan:

```bash
python3 - <<'PY'
from pathlib import Path
from collections import defaultdict
import difflib, re
roots = [Path('.hermes/skills'), Path('.hermes/skill-packs'), Path('skills')]
tokens = 'worktree cleanup dirty preservation rebase github pr workflow ci vercel runtime nextjs rsc tailwind mdx wiki skill reference dedupe memory governed'.split()
files = []
for root in roots:
    if not root.exists():
        continue
    for path in root.rglob('*'):
        if path.is_file() and (path.name == 'SKILL.md' or '/references/' in path.as_posix()):
            text = re.sub(r'\s+', ' ', path.read_text(errors='ignore')).lower()
            files.append((path, text))
for tok in tokens:
    group = [(p,t) for p,t in files if tok in p.as_posix().lower() or tok in t]
    if len(group) < 2 or len(group) > 80:
        continue
    for i, (a, ta) in enumerate(group):
        for b, tb in group[i+1:]:
            ratio = difflib.SequenceMatcher(None, ta[:12000], tb[:12000]).ratio()
            if ratio >= 0.72:
                print(f'{tok}\t{ratio:.2f}\t{a}\t{b}')
PY
```

Use the output as a candidate list. Read the files before editing.

## Canonical Owner Decision Rules

Choose one owner for each repeated workflow:

1. Prefer the broader, class-level skill over a one-repo or one-session skill.
2. Prefer an active `.hermes/skills/**` entrypoint for common workflows that future sessions must load directly.
3. Prefer `.hermes/skill-packs/<pack>/` for detailed procedures that are too large or too niche for active prompt surface.
4. Prefer `skills/<name>/SKILL.md` for root-level governed/shared policy directives that apply to both Hermes and Codex agents.
5. If the duplicate belongs to another product repository, keep it in that repository's own `.hermes/skills` and do not duplicate it in `skills-jk` unless the workflow is genuinely cross-repo reusable.
6. If two files each contain unique durable content, merge the unique parts into the canonical owner before deleting or thinning either file.

Common owner examples in this repository:

| Repeated topic | Canonical owner |
| --- | --- |
| repo-local stale branch/worktree cleanup | `git-worktree-safety-pack` and its references |
| GitHub PR lifecycle, checks, PR body safety | `github-pr-workflow` and its references |
| `skills-jk` bot-authored PR workflow_dispatch | `skills-jk-gha-pr-creation` |
| skill authoring/frontmatter/reference structure | `hermes-agent-skill-authoring` |
| root-level persistent memory policy | `skills/memory-directives-governed/SKILL.md` |
| shell/Bash implementation style | `skills/bash-scripting/SKILL.md` |

## Refactor Procedure

For each duplicate cluster:

1. Read all candidate files fully enough to identify overlapping vs unique durable guidance.
2. Pick the canonical owner and state why in your working notes or PR body.
3. Move unique durable bullets, pitfalls, commands, and verification checks into the canonical `SKILL.md` or a canonical topic-level `references/<topic>.md`.
4. Delete exact duplicate reference files only after confirming the canonical copy exists and is linked by the owner skill.
5. For near-duplicate references, either:
   - delete the narrower file after merging its unique content; or
   - shrink it to a short adapter that links to the canonical reference and contains only owner-specific application notes.
6. Update every pointer to moved/deleted references:
   - owner `SKILL.md` reference lists;
   - `.hermes/skill-packs/**/INDEX.md` when relevant;
   - `docs/reports/*reference*.tsv` or other inventory reports;
   - any markdown links found by basename or exact path search.
7. Avoid large unrelated cleanup in the same PR. If multiple clusters are unrelated, create separate PRs.

## Deletion Safety Checks

Before deleting a skill or reference, verify:

- it is not the only trigger entrypoint for a recurring task;
- its unique durable guidance has been moved or intentionally dropped as stale;
- no active `SKILL.md`, pack `INDEX.md`, report, or doc still points to it;
- the filename is not referenced by basename under `.hermes`, `skills`, or `docs`;
- archive deletion does not remove the only copy of historical context needed by a live active skill.

Search by both exact path and basename:

```bash
deleted='references/example-old-file.md'
base=$(basename "$deleted")
rg -n "$(printf '%s' "$deleted" | sed 's/[].[^$*+?{}|()\\]/\\&/g')|$base" .hermes skills docs || true
```

## Verification Checklist

Run these before committing:

```bash
git diff --check
python3 - <<'PY'
from pathlib import Path
for root in [Path('.hermes/skills'), Path('.hermes/skill-packs'), Path('skills')]:
    if not root.exists():
        continue
    for path in root.rglob('*'):
        if path.is_file() and path.suffix in {'.md', '.txt'}:
            for i, line in enumerate(path.read_text(errors='ignore').splitlines(), 1):
                if line.startswith(('<<<<<<< ', '>>>>>>> ')) or line == '=======':
                    print(f'{path}:{i}:{line}')
PY
```

If you deleted or moved references, rerun the exact/normalized duplicate scans and stale path searches. The PR body should report:

- which roots were scanned;
- how many exact duplicate groups were found and fixed or left intentionally;
- which canonical owners were selected;
- which files were merged, deleted, or thinned;
- verification commands run.

## Common Pitfalls

1. Do not create a new skill to describe a workflow that already has a canonical owner. Patch the owner instead.
2. Do not preserve a one-session incident reference just because it contains useful details. Extract durable details into a topic-level reference and delete the session-shaped duplicate.
3. Do not rely only on exact hash duplicates. Near-duplicates are usually the real maintenance problem.
4. Do not run a broad all-pairs similarity scan over the entire library as the first step; it can be slow and noisy. Cluster first.
5. Do not delete a narrow adapter if it is the only discoverable trigger for a repo-specific workflow. Thin it and link to the canonical owner instead.
6. Do not leave stale inventory/report rows after deleting references. Reports that mention deleted files make future agents think the file still exists.
7. Do not mix unrelated dedupe clusters in one PR. Reviewers need to understand each canonical owner decision.
8. Do not stage runtime residue such as `.hermes/lsp/`, sessions, logs, caches, or generated temporary reports unless the user explicitly asked for those artifacts to be tracked.
9. Do not close or merge PRs as part of this workflow unless the user explicitly asks.

## Completion Report

Report concisely:

- new or updated canonical owner paths;
- deleted/thinned duplicate paths;
- exact/normalized/near-duplicate scan results;
- validation commands;
- PR URL if changes were pushed.

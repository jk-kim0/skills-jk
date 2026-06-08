# Reference dedupe preflight for skills-jk

Use this checklist before adding or preserving any new `.hermes/skills/**/references/*.md` file in this repository.

## Why this exists

PR #466 removed repeated incident notes that accumulated when Hermes preserved one reference per cleanup or operations session. Most of those files were not exact byte duplicates, but they repeated the same durable routing rules that already belonged to canonical owner skills.

The goal is not to block useful new knowledge. The goal is to add the lesson to the right owner once, instead of creating another session-named note that future agents must route around.

## Preflight before creating a reference

1. Identify the durable topic, not the session story.
   - Good topic: `dirty-root preservation during workspace cleanup`.
   - Bad topic: `today's post-reset branch cleanup after PR N`.
2. Check the canonical owner map below.
3. Search the candidate owner before writing a new file:

```bash
find .hermes/skills .hermes/skill-packs skills -path '*/references/*' -type f | sort
rg -n "<topic keyword>|<error phrase>|<workflow name>" .hermes/skills .hermes/skill-packs skills
```

4. Prefer patching an existing `SKILL.md` section or reference when the rule is a clarification, pitfall, or repeated edge case.
5. Create a new `references/<topic>.md` only when all are true:
   - no existing reference owns the same durable rule;
   - the content is reusable beyond the current session transcript;
   - the filename names the class of problem, not the incident date, PR number, branch name, or temporary symptom;
   - the owning `SKILL.md` gains a short pointer to the new reference.
6. For very thin migrated-memory references, prefer inlining the one or two durable rules into the owning `SKILL.md` and deleting the reference file. This is especially appropriate when the file mostly contains migration boilerplate plus a single user preference or inventory note.
7. If deleting or moving a reference file, update repo-local inventories and reports that list reference paths (for example `docs/reports/*reference*.tsv`) so stale deleted paths do not remain as apparent live references.
8. If the new lesson belongs to another repository, keep it in that repository's `.hermes/skills` instead of duplicating it here.

## Canonical owner map

| Durable topic | Update here |
| --- | --- |
| Local workspace cleanup, dirty-root preservation, stale branches/worktrees, repeated `workspace 정리` loops | `.hermes/skills/software-development/git-worktree-safety-pack/` and its references |
| General GitHub PR lifecycle, branch creation, CI interpretation, PR body safety, existing/open PR follow-up | `.hermes/skills/github/github-pr-workflow/` and `.hermes/skill-packs/github-pr-workflow/` |
| `skills-jk` bot-authored PR creation through `.github/workflows/create-pr.yml` | `.hermes/skills/software-development/skills-jk-gha-pr-creation/` |
| Repo-local Hermes profile/config-as-code conventions | `.hermes/skills/software-development/skills-jk/` or a more specific repo-local Hermes setup skill |
| Skill authoring structure, frontmatter, references/templates/scripts conventions | `.hermes/skills/software-development/hermes-agent-skill-authoring/` |
| Outbound-agent operational procedures | the outbound-agent repository's own `.hermes/skills` when available; only keep cross-repo reusable workflow here |

## Review checklist for PRs that add references

- [ ] The PR body names the canonical owner considered.
- [ ] The diff does not add a one-session incident note when an existing reference could be patched.
- [ ] The new filename is topic-level and does not include a PR number, branch name, date, or temporary failure wording.
- [ ] `SKILL.md` links to the reference if the file should be discoverable by future agents.
- [ ] Exact duplicate scan is clean when the PR adds or moves multiple reference files.

Suggested exact duplicate scan:

```bash
python3 - <<'PY'
from pathlib import Path
from collections import defaultdict
import hashlib
roots = [Path('.hermes/skills'), Path('.hermes/skill-packs'), Path('skills')]
groups = defaultdict(list)
for root in roots:
    if not root.exists():
        continue
    for path in root.rglob('*'):
        if path.is_file() and '/references/' in path.as_posix() and path.suffix in {'.md', '.txt'}:
            groups[hashlib.sha256(path.read_bytes().strip()).hexdigest()].append(path.as_posix())
for files in groups.values():
    if len(files) > 1:
        print('\n'.join(files), end='\n\n')
PY
```

Suggested normalized duplicate scan:

```bash
python3 - <<'PY'
from pathlib import Path
from collections import defaultdict
import hashlib, re
roots = [Path('.hermes/skills'), Path('.hermes/skill-packs'), Path('skills')]
groups = defaultdict(list)
for root in roots:
    if not root.exists():
        continue
    for path in root.rglob('*'):
        if path.is_file() and '/references/' in path.as_posix() and path.suffix in {'.md', '.txt'}:
            text = path.read_text(errors='ignore')
            normalized = re.sub(r'\s+', ' ', text).strip()
            groups[hashlib.sha256(normalized.encode()).hexdigest()].append(path.as_posix())
for files in groups.values():
    if len(files) > 1:
        print('\n'.join(files), end='\n\n')
PY
```

Suggested stale session-name / PR-number filename scan:

```bash
python3 - <<'PY'
from pathlib import Path
import re
roots = [Path('.hermes/skills'), Path('.hermes/skill-packs'), Path('skills')]
pattern = re.compile(r'(^|[-_/])(pr-?\d+|issue-?\d+|\d{8}|\d{4}-\d{2}-\d{2})([-_.]|$)', re.I)
for root in roots:
    if root.exists():
        for path in root.rglob('*'):
            if path.is_file() and '/references/' in path.as_posix() and pattern.search(path.as_posix()):
                print(path.as_posix())
PY
```

## Reference reduction workflow

Use this when the user asks to reduce duplicate `references/` files across the skill library, not only to prevent a new reference from being added.

1. Work in a fresh latest-`origin/main` worktree. If root has same-scope dirty skill/reference edits, apply that payload into the refactor worktree and reset the root duplicate only after the PR branch is pushed and verified.
2. Run exact/normalized duplicate scans across `.hermes/skills`, `.hermes/skill-packs`, and `skills`. Exact duplicates under `.hermes/skills/.archive/**/references/` that have an active non-archive copy can usually be deleted from the archive; keep the active copy.
3. Pairwise near-duplicate scans over hundreds of reference files can time out. Use a clustered pass instead: group by owner directory and high-value tokens such as `worktree`, `cleanup`, `dirty`, `preservation`, `rebase`, `github`, `workflow`, `vercel`, `nextjs`, `mdx`, `wiki`, and compare only within those clusters.
4. For active near-duplicates, prefer one canonical owner reference plus deletion of the narrower duplicate. Before deleting, merge any unique durable section into the canonical file. Examples: a repo-specific PR-DIRTY rebase note can defer to the general GitHub PR workflow reference; two Vercel ESM/CJS runtime-500 notes can become one canonical runtime-forensics reference with remediation bullets.
5. When deleting or moving references, update repo-local inventory/report files such as `docs/reports/*reference*.tsv`; stale rows make deleted paths look live.
6. Verify after refactoring:
   - exact duplicate group count is zero for the chosen roots;
   - deleted reference paths have no remaining hits in `.hermes`, `docs`, or `skills` text files;
   - anchored conflict-marker scan is clean;
   - `git diff --check` passes;
   - final report includes reference count by root and the number of removed/merged references.

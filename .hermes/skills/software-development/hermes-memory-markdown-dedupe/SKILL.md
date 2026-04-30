---
name: hermes-memory-markdown-dedupe
description: Dedupe and compress Hermes markdown memory files safely, using a fresh worktree or existing PR branch and verifying exact/near-duplicate removal.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, memory, markdown, dedupe, git, pr]
---

# Hermes memory markdown dedupe

Use this when:
- Hermes says markdown memory is getting too large
- the user asks to remove duplicate or redundant memory entries
- `.hermes/memories/MEMORY.md` and/or `.hermes/memories/USER.md` have accumulated repeated rules, stale snapshots, or near-duplicate preferences

## Goal

Reduce memory size without losing durable intent.

Priority order:
1. Remove exact duplicates
2. Merge near-duplicates that express the same rule
3. Replace multiple historical snapshots with one current durable rule
4. Remove stale implementation-history or branch-state notes that no longer help future steering

## Safe branching rule

If there is already an open PR for the dedupe work, use a fresh worktree on that same PR branch.
If this is new work, create a fresh worktree from latest `origin/main` and open a new PR.

Examples:
```bash
# new work
git fetch origin --prune
git worktree add .worktrees/chore-dedupe-hermes-memories -b chore/dedupe-hermes-memories origin/main

# follow-up on existing PR branch
git fetch origin --prune
git worktree add .worktrees/chore-dedupe-hermes-memories origin/chore/dedupe-hermes-memories
```

## What counts as duplicate enough to merge

### Exact duplicate
Same meaning and same scope. Delete all but one.

### Near duplicate
Small wording differences but same durable rule.
Example pattern:
- multiple notes saying `pages.yaml` is straightforward/non-core
- multiple notes saying CMS edits still require local server + commit/push
- multiple notes saying use-cases should use plural route naming

Keep one merged version with the strongest current wording.

### Stale snapshot
Older branch/PR/timestamp-specific notes that are superseded by a broader current rule.
Examples:
- old route snapshots replaced by a newer canonical route policy
- historical branch names that only mattered during one follow-up cycle
- implementation snapshots that are restated more generally elsewhere

Do not remove if it is still the only place storing a durable, repo-specific fact.

## Recommended inspection method

Read both files fully, then use a scripted pass to detect exact and near duplicates.

Suggested script logic:
- split entries on `§`
- normalize whitespace and lowercase for exact-match detection
- run pairwise similarity checks for near-duplicates
- run a separate regex scan for snapshot-style entries that similarity checks will miss
- also manually review clusters like:
  - route policy
  - PR/worktree workflow
  - CMS limitations
  - localization preferences
  - repo-specific implementation snapshots

Important practical finding:
- similarity-based duplicate detection is not enough by itself
- many low-value memory entries are not textual duplicates, but historical snapshots such as:
  - specific branch names
  - specific PR numbers
  - specific commit hashes
  - `origin/main around <sha>` or `origin/main <sha>` point-in-time repo state notes
- these should be reviewed separately and either generalized into a reusable rule or removed if broader rules already cover them

Useful regex review queue examples:
```python
patterns = [
    r'PR #\\d+',
    r'\\bPR \\#?\\d+',
    r'origin/main \\([0-9a-f]{6,40}\\)',
    r'origin/main around [0-9a-f]{6,40}',
    r'commit [0-9a-f]{6,40}',
    r'branch `[^`]+`',
    r'remains the active',
    r'current .* work is being done',
]
```
Then inspect matching entries manually.

A practical Python pattern:
```python
import re, difflib
entries = [p.strip() for p in text.split('§') if p.strip()]
norm = lambda s: re.sub(r'\s+', ' ', s.strip().lower())
```

Good thresholds:
- exact duplicate: normalized strings equal
- near duplicate review queue: ratio >= 0.90 OR one normalized string contains the other

Important: similarity results are only a review queue, not an auto-delete rule.
Always inspect meaning before merging.

## Good edit patterns

### 1. Merge three repeated notes into one
Before:
- note A says pages.yaml is non-core
- note B says pages.yaml is straightforward
- note C says pages.yaml extra fields are testcase-only

After:
- one concise line preserving all three ideas

### 2. Merge repeated user preferences into one stronger preference
Before:
- fast acknowledgements
- immediate verbal response first
- no proposal-only pauses

After:
- one concise rule covering all three user expectations

### 3. Merge old route snapshots into one current canonical rule
Before:
- multiple historical AIP/use-case/webinar route notes
- old singular/plural snapshots
- legacy-path notes repeated separately

After:
- one current canonical-path rule plus one note that older paths are legacy/history

## What not to do

- Do not delete durable repo facts just because they are long.
- Do not keep multiple historical versions when one current rule is enough.
- Do not aggressively compress unrelated preferences into one vague sentence if it loses operational meaning.
- Do not work in a dirty unrelated branch if a fresh worktree can isolate the change.

## Verification

After editing, verify all of the following:

1. `MEMORY.md` and `USER.md` still parse cleanly as `§`-separated entries.
2. No exact duplicates remain.
3. No obvious near-duplicates remain in the main repeated clusters.
4. File size went down meaningfully.
5. The diff touches only the memory files unless the user explicitly asked for more.

Useful checks:
```bash
git diff --stat
wc -c .hermes/memories/MEMORY.md .hermes/memories/USER.md
```

And rerun the duplicate-detection script after edits.

## Commit/PR guidance

Use a commit message like:
```bash
chore: dedupe Hermes memory markdown
```

For follow-up rounds on the same PR, a good second commit pattern is:
```bash
chore: further compress Hermes memory markdown
```

PR body should explain:
- which duplicate clusters were merged
- whether stale snapshot notes were removed
- resulting duplicate counts (exact/near)
- resulting file-size reduction if measured

## Practical lessons from use

- Memory files often contain not only exact duplicates but also “superseded by a broader current rule” entries; these are the biggest compression wins.
- Repo-history or route-snapshot notes are often safe to collapse when a newer canonical rule already exists elsewhere in the file.
- User preference files tend to accumulate multiple phrasings of the same behavioral expectation; merge them into one stronger, clearer instruction.
- A fresh worktree is safer than reusing a dirty branch when the main workspace has unrelated local edits.

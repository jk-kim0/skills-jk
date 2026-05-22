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

In practice, a topic-cluster pass works better than pure pairwise similarity alone.
After the initial duplicate scan, group entries into broad clusters such as:
- repo workflow / latest-main / worktree / cwd
- corp-web-japan deployment / governance / rollout
- corp-web-v2 CMS / route-policy / legacy-scope restrictions
- Hermes runtime / HERMES_HOME / sessions
- querypie-docs reverse-sync

Then review each cluster as a set and ask:
1. which lines are the current durable rule?
2. which lines are just older phrasings of the same rule?
3. which lines are historical snapshots that can be replaced by one current general statement?

This cluster-first pass often finds better compression wins than string similarity alone.

Suggested script logic:
- split entries on `§`
- normalize whitespace and lowercase for exact-match detection
- run pairwise similarity checks for near-duplicates
- run a separate regex scan for snapshot-style entries that similarity checks will miss
- group entries into topic clusters and review each cluster together before editing
- also manually review clusters like:
  - route policy
  - PR/worktree workflow
  - CMS limitations
  - localization preferences
  - repo-specific implementation snapshots

A practical clustering approach that worked well in real use:
- assign coarse topic buckets such as `repo_workflow`, `corp_web_v2_demo`, `corp_web_v2_scope`, `corp_web_japan`, `querypie_docs_reverse_sync`, `hermes_runtime`
- print per-cluster counts and total character size
- sort entries inside each cluster by length so the longest, most repetitive rules are reviewed first
- use this to decide whether several entries should become one merged durable rule

This helps catch not just textual duplicates, but families of overlapping rules that should be rewritten as one current instruction.

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

## Bulk-edit safety rule

When applying large markdown replacements, do not patch an overly broad block unless you have re-read the surrounding entries carefully.

Practical lesson from use:
- a broad `replace` can accidentally remove neighboring non-duplicate rules that merely happen to sit between duplicated entries
- after any bulk merge/edit, immediately re-read the edited region and confirm that unrelated durable preferences were not dropped
- if a bulk replacement accidentally removes valid neighboring entries, restore them right away and continue with narrower, more targeted patches

Good pattern:
1. read the exact region around the duplicate cluster
2. patch only that cluster
3. re-read the region
4. rerun duplicate detection after each large merge pass

## Repo-specific extraction-to-skill pattern

When `MEMORY.md` or `USER.md` is dominated by facts for specific repositories, do not only dedupe wording. Move those entries into class-level repo-context skills and leave a short global pointer behind.

Recommended shape:
1. Cluster entries by durable repo/work area, for example `skills-jk`, `querypie-docs`, `corp-web-v2`, `corp-web-japan`, `corp-web-app`, runner ops, or Vercel ops.
2. Prefer updating an existing umbrella skill for that repo/workflow. If none exists, create one class-level repo-context skill, not one skill per memory entry.
3. Put the migrated raw entries in `references/migrated-memory-and-user-context.md`, separated by source section (`From MEMORY.md`, `From USER.md`).
4. Keep `SKILL.md` as a trigger/index with instructions to read the reference and verify live repo state before acting on potentially stale facts.
5. Rewrite global memory/user files to keep only broad user preferences plus a pointer such as: “repo-specific implementation facts and workflow constraints have been moved into repo-context skills; load the relevant skill before substantial work.”
6. Verify with a regex scan that repo-specific names/routes remain in global memory only as the pointer, while the detailed entries exist in the skill references.

Use this when the goal is to reduce global prompt pressure and make repo-specific facts load only when relevant. Do not use it for general user preferences that should apply across repos.

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
- Do not use overly broad replace ranges when merging cluster entries. Large block replacements can accidentally drop neighboring still-valid rules. Re-read the affected section after each large merge and restore any durable rule that disappeared unintentionally.

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

Useful reporting metrics that proved helpful:
- entry count before vs after for each file
- total character count before vs after for each file
- exact duplicate count after edit
- near-duplicate review queue count after edit

These make it easier to show that the dedupe was real compression rather than just rewriting text.

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

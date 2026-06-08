---
name: git-change-provenance-forensics
description: Trace who changed a file, why it changed, and whether the change belongs to historical main/PR history or only the current local dirty workspace. Combines git history, GitHub PR metadata, and optional Hermes session forensics.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [git, github, forensics, provenance, history, pr, audit]
---

# Git change provenance forensics

Use this when the user asks questions like:
- "이 파일 변경을 누가 했어?"
- "왜 이 스킬이 업데이트됐어?"
- "이 변경이 main 에 들어간 건지, 지금 로컬에만 있는 건지 조사해줘"
- "이 diff 가 어느 PR/세션에서 생긴 건지 찾아줘"

This is especially useful in repos like `skills-jk` where:
- a file may have historical changes already merged to `main`
- the current root worktree may also be dirty with a newer local follow-up patch
- PR creation may happen through GitHub Actions, so the merge commit author is a bot even though the real change author is a human

## Goal

Separate these clearly:
1. latest historical change already on `main`
2. real human author vs merge/bot committer
3. PR title/body/branch that explains the intent
4. current local dirty changes not yet on `main`
5. optional originating Hermes session evidence

## Core workflow

### 1. Start with file history, not blame alone

Use `git log --follow` on the exact file:

```bash
git log --follow --format='%H %ad | %an <%ae> | %s' --date=iso -- path/to/file
```

Why:
- this shows the sequence of commits that touched the file
- it immediately reveals whether the latest visible change on `main` is a bot merge commit or a human-authored commit

If the user asks about a cluster of related files, include them together:

```bash
git log --oneline --decorate -- path/a path/b path/c
```

### 2. Inspect the latest main-side commit in detail

For the latest commit from step 1:

```bash
git log -1 --stat --format=fuller -- path/to/file
```

This helps answer:
- what else changed in the same commit
- whether the file was part of a broader skill refresh / migration / cleanup

Important interpretation:
- if the latest commit author is `github-actions[bot]`, do not stop there
- treat that as the merge surface, not necessarily the real author of the content change

### 3. Find the real PR behind a bot-authored merge commit

Often the commit subject includes `(#123)`.
Use that PR number directly:

```bash
env -u GITHUB_TOKEN gh pr view 123 --json number,title,body,url,author,mergedAt,headRefName,baseRefName,commits,files
```

What to extract:
- PR title/body for the stated reason
- human-authored commits inside the PR
- head branch name
- whether the PR body explicitly mentions the subsystem/file family

Practical rule:
- when the merge commit on `main` is by GitHub Actions or another bot, report:
  - `main 반영 주체`: bot/merge mechanism
  - `실질 작성자`: PR commit author(s)

### 4. If the interesting PR head commit is not in local history, query GitHub directly

Sometimes the PR head commit was squashed/rebased and is not a local object anymore.
In that case:

```bash
env -u GITHUB_TOKEN gh api repos/<owner>/<repo>/commits/<sha>
```

This is the fastest way to recover:
- commit author/committer
- stats
- file list
- per-file patches

Very useful when `git show <sha>` fails locally but the PR API exposed the head commit SHA.

### 5. Pull the exact patch for the target file

If you need to explain what changed and why, get the patch for that file from the commit API:

```bash
env -u GITHUB_TOKEN gh api repos/<owner>/<repo>/commits/<sha> \
  --jq '.files[] | select(.filename=="path/to/file") | .patch'
```

Use this to summarize the actual intent, for example:
- generic local-inference docs changed into HF-Hub-first discovery workflow
- old CLI examples replaced with new tool names
- stale references deleted while core guide was kept

### 5.5 Use deployment/runtime history when the question is about a deployed regression

If the user asks which PR caused a live deployment failure, git diff alone can identify candidates but may miss the actual trigger.
Combine provenance with deployment evidence:

```bash
vercel list <project> --format json --status READY
```

Then probe recent deployment URLs in chronological order with representative paths such as `/`, `/login`, and a known app route.
Find the first transition from normal responses (`200`/`307`) to the failing status (`500`, etc.), then map that deployment's metadata back to `githubPrId`, `githubCommitSha`, `githubCommitRef`, and commit message.

Report latent and triggering causes separately.
For example, an older PR may have introduced a latent package setting such as `"type": "module"`, while a later PR is the first deployment where Vercel actually starts returning 500.
Do not blame the currently open preview PR until production/main and earlier deployments have been checked.

### 6. Distinguish historical main changes from current local dirty changes

Do not assume the user is asking only about what is on `main`.
Always check live repo state too:

```bash
git status --short --branch
```

Then inspect the current checked-out file content or diff:

```bash
sed -n '1,120p' path/to/file
git diff -- path/to/file
```

If the user specifically asks what local changes exist in the `main` workspace, keep the task focused on the live root checkout and avoid drifting into PR/history forensics unless provenance is requested. Use this compact local-dirty audit:

```bash
pwd
git rev-parse --show-toplevel
git branch --show-current
git status --short --branch
git diff --stat
git diff --name-status
git diff --cached --stat
git diff --cached --name-status
git ls-files --others --exclude-standard
git rev-list --left-right --count main...origin/main
git log --oneline --decorate --max-count=12 main..origin/main
```

Report:
- workspace path and current branch
- whether the branch is ahead/behind origin
- staged vs unstaged vs untracked changes
- file-by-file intent summary from `git diff`
- caution if local `main` is behind `origin/main`, because the dirty diff is relative to the stale local base

If there is also a current PR/worktree for local follow-up work, inspect that separately:

```bash
git -C <worktree> status --short --branch
git -C <worktree> diff -- path/to/file
```

Important interpretation:
- the file may have one explanation for the latest merged main-side change
- and a different explanation for the current local dirty change
- report these as separate layers, not as one blended story

Suggested summary labels:
- `latest main-side meaningful change`
- `current local dirty follow-up`

### 7. Use blame only as a supporting view

`git blame` is useful for answering “which commit last touched these exact lines in the current file?”

```bash
git blame -w --date=iso path/to/file
```

But do not rely on blame alone because:
- it does not tell the PR-level reason well
- current uncommitted edits can appear as `Not Committed Yet`
- it is line-oriented, not intent-oriented

Good use:
- confirm whether most of the current file still comes from an older foundational commit
- spot whether a few lines are currently modified but not committed yet

### 8. If needed, connect the change to a Hermes session

If the user wants to know which conversation likely produced the change, use Hermes session forensics after the git/PR facts are known.

Search by:
- PR number
- branch name
- head commit SHA
- exact commit subject
- notable phrases from the PR body

Typical pattern:

```bash
search_files \
  path=<HERMES_HOME>/sessions \
  pattern='<commit-sha>|<branch>|<commit subject>|<PR phrase>'
```

Practical rule:
- do not treat hits from the current investigation session as evidence of the original session
- use session hits only as supporting provenance after git/PR evidence is already established

## Recommended reporting structure

When answering the user, separate the layers explicitly:

1. `main 반영 최신 이력`
   - commit SHA
   - surface author/committer
   - subject
2. `실질 작성자`
   - PR number/title
   - human commit author(s)
3. `왜 업데이트됐는가`
   - quote/summarize PR body and exact file patch direction
4. `현재 로컬 변경이 별도로 있는가`
   - yes/no
   - if yes, explain that it is a newer local follow-up and not the same as the historical main-side change
5. `확신 수준`
   - direct git evidence
   - PR API evidence
   - optional session evidence

## skills-jk specific lessons

- In `skills-jk`, PR creation often uses GitHub Actions workflow dispatch, so `main` may show bot-authored merge commits even when JK authored the real content change.
- `gh pr view <number> --json commits,files,body` is usually the fastest explanation source for “why did this skill change?”
- If a PR head commit SHA is shown by the API but `git show` says the object is missing locally, use `gh api repos/<owner>/<repo>/commits/<sha>` instead of assuming the commit is gone.
- Always compare the historical merged state with the current root dirty state before answering. In `skills-jk`, a file can have:
  - an older merged Hub-first skill refresh on `main`
  - plus a newer local root-follow-up patch preparing a different PR
- When a file is under active local modification, blame may show `Not Committed Yet`; this is evidence of current local changes, not proof about original authorship.

## Done criteria

You are done when you can answer, with evidence:
- who last changed the file on `main`
- who actually authored that content change
- what PR/work branch carried it
- why it was changed
- whether the currently visible local diff is the same historical change or a separate newer local follow-up

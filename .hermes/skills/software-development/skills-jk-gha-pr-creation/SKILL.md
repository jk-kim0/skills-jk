---
name: skills-jk-gha-pr-creation
description: Create pull requests in the skills-jk repository via the repo's GitHub Actions workflow `.github/workflows/create-pr.yml` instead of direct `gh pr create`, to avoid local shell quoting issues and follow repo convention.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [github, pull-request, github-actions, workflow-dispatch, skills-jk]
---

# skills-jk GHA PR Creation

Use this skill when creating a PR in the `skills-jk` repository.

## Why this exists

`skills-jk` has a repository-standard PR creation workflow at `.github/workflows/create-pr.yml`.
It accepts `branch`, `title`, and `body` via `workflow_dispatch`, then creates the PR in GitHub Actions.
This is safer than local `gh pr create --body "..."` when the body contains backticks, paths, or multiline markdown that can be mangled by shell quoting.

## When to use

Trigger this skill when:
- working inside the `skills-jk` repository
- a new PR needs to be opened
- the branch is already committed and pushed
- the PR body is multiline markdown

## Procedure

1. Confirm you are in `skills-jk` and that the work branch is pushed.
   - Check current branch with `git branch --show-current`
   - Check remote tracking with `git status -sb`

2. Confirm whether a PR already exists for the branch.
   - Use `gh pr status`
   - If a PR already exists, edit that PR instead of creating a new one

3. Prepare the PR body in a file first.
   - Write the full markdown body to a temporary file
   - Avoid inline shell interpolation of multiline markdown

4. Trigger the repository workflow instead of calling `gh pr create` directly.
   - Use `gh workflow run .github/workflows/create-pr.yml`
   - Pass:
     - `-f branch=<branch>`
     - `-f title=<title>`
     - `--raw-field body="$(cat <body-file>)"`

5. Wait for the workflow run to appear and finish.
   - Use `gh run list --workflow create-pr.yml --limit 5`
   - In this repo, the dispatched `create-pr.yml` run may appear with `headBranch` shown as `main` in `gh run list`, even when it creates a PR for another branch. Do not try to identify the run by filtering on the feature branch name.
   - If you need to inspect the run, take the newest `create-pr.yml` run and use `gh run view <run-id>` or `gh run watch <run-id>`.

6. Verify the PR was created.
   - Prefer `gh pr status` to confirm the resulting PR.
   - If you need a branch-specific lookup, use `gh pr list --head <branch>` or `gh pr view <branch>`.
   - Do not use `gh pr view --head <branch>`; that flag is not supported by `gh pr view` and fails with `unknown flag: --head`.
   - Do not rely on `gh run list --branch <branch>` to prove the PR-creation workflow ran; that branch filter may show nothing for this workflow even when PR creation succeeded.
   - After the final push/update, verify the actual remote branch ref directly before trusting PR metadata:
     - `git rev-parse HEAD`
     - `git ls-remote origin refs/heads/<branch>`
   - Treat the remote ref match as the source of truth for whether the branch tip really reached GitHub. `gh pr view` / `gh pr status` can lag briefly after push or workflow-driven PR creation.
   - Report the PR number and URL

## If a PR already exists

Do not dispatch the create workflow again unless intentionally creating a replacement PR.
Instead:
- use `gh pr edit <number> --title ...`
- or `gh pr edit <number> --body-file <file>`

## Pitfalls

- Follow the active repository/global GitHub CLI safety policy when invoking `gh`. In this environment that means using `env -u GITHUB_TOKEN gh ...` rather than raw `gh ...`.
- In `skills-jk`, do not create PRs with direct local `gh pr create` when the intent is to open a normal review PR. The repository-standard path is the `create-pr.yml` workflow so the PR is created by `github-actions[bot]`, not by the local human GitHub identity.
- Practical user-specific rule: if you accidentally created the PR directly and it shows the user's account as author, treat that as incorrect for this repo. Create a bot-authored replacement PR via the workflow instead of pretending the existing PR is acceptable.
- Safe repair pattern for that mistake:
  1. verify the already-pushed branch tip/commit to preserve
  2. create and push a replacement branch name if needed (for example `<branch>-bot`) pointing at the same commit
  3. dispatch `.github/workflows/create-pr.yml` with the same title/body against that replacement branch
  4. verify the new PR author is `app/github-actions` or another bot identity via `gh pr view --json author`
  5. do not close the mistaken human-authored PR unless the user explicitly asks; report both PRs and let the user decide the cleanup action
- Do not pass complex markdown directly to `gh pr create --body` in this repo unless there is a strong reason
- `create-pr.yml` targets `main` as the base branch
- The workflow appends a GitHub Actions bot footer to the body
- If the branch has an existing open PR, the workflow may fail or create duplicate intent; check first
- After dispatching the PR-creation workflow, verify completion with `gh run watch` and then confirm the resulting PR with `gh pr view` or `gh pr status`
- `gh pr checks` may legitimately report no checks for the new PR branch; if so, also inspect `gh run list --branch <branch>` before concluding that no CI ran
- When the local workspace contains mixed changes, inspect `git status --short`, `git diff --stat`, and representative diffs before staging. In `skills-jk`, it is common to have meaningful tracked changes under `.hermes/` mixed with local-only artifacts such as `.claude/worktrees/`, scratch files like `test.txt`, and usage trackers such as `.hermes/skills/.curator_state`, `.hermes/skills/.usage.json`, and `.hermes/skills/.usage.json.lock`; exclude those temporary artifacts from the PR unless the user explicitly asks to include them.
- Do not treat a tracked repo config file as disposable just because it reflects local Hermes runtime behavior. In particular, `.hermes/config.yaml` is repo-managed and if it changed intentionally, it should be reviewed via git: either include it in the current PR when scope matches, or split it into its own dedicated PR when mixing it into a skill/memory PR would muddy scope.
- Conversely, do not over-exclude tracked `.hermes/` changes just because they look local. Durable repo-managed updates such as `.hermes/memories/MEMORY.md`, bundled skill content under `.hermes/skills/**`, derived `.hermes/skills/.bundled_manifest`, and intentional `.hermes/config.yaml` updates can all be legitimate PR payload when the user asks to turn the current local Hermes workspace sweep into a reviewable PR.
- Important user-specific default for `skills-jk`: when the user asks to make a PR from the current local workspace state, treat all tracked repo changes as PR candidates by default, and also treat meaningful untracked skill/reference/script files as PR candidates by default. Split them into separate PRs only for review-scope clarity; do not silently drop tracked files just because they are "local-looking". The normal exclusions are only clearly runtime-only residue such as `.hermes/skills/.curator_state`, `.hermes/skills/.usage.json`, and `.hermes/skills/.usage.json.lock`, unless the user explicitly asks to include those too.

## Local workspace sweep workflow

When the user asks to create a PR from the current local workspace state rather than from a single known change:

1. Review all current changes first:
   - `git status --short`
   - `git diff --stat`
   - `git diff --name-status`
   - `git ls-files --others --exclude-standard`
2. Read representative diffs or files to classify them:
   - meaningful tracked repo changes
   - new skill/reference content that should be committed
   - local runtime/worktree/scratch artifacts that should stay untracked
3. Refresh repository references before committing:
   - `git fetch origin --prune`
   - inspect whether the current branch tracks a deleted remote branch (`[gone]` in `git branch -vv`)
   - inspect whether local `main` is behind `origin/main`
4. If local `main` is behind and is not currently checked out, fast-forward it safely with:
   - `git branch -f main origin/main`
   - This updates local `main` without disturbing the dirty current branch.
5. If the current checkout is already `main`, `main` is aligned with `origin/main`, and `gh pr status` confirms there is no existing PR for the current branch, it is acceptable in `skills-jk` to create a fresh PR branch in place from that checkout instead of transplanting the whole dirty tree into a new worktree.
   - Safe pattern:
     - confirm `git rev-list --left-right --count main...origin/main` is `0 0`
     - confirm current branch is `main`
     - create a fresh branch directly: `git checkout -b <new-branch>`
     - then stage only the intended `.hermes/` skill/memory/manifest changes and leave runtime artifacts untracked
   - This is a practical shortcut for repo-local Hermes workspace sweeps when the user explicitly asked to update `main` and turn the current local changes into a PR.
6. If the current branch corresponds to an already merged/closed PR, do **not** keep committing on that branch even if it still has useful local changes.
   - Fast detection: run `env -u GITHUB_TOKEN gh pr status` first. In `skills-jk`, this often surfaces the problem immediately as `Current branch  #<N> ... Merged` even when the remote branch has already been deleted.
   - Confirm with `env -u GITHUB_TOKEN gh pr list --head <branch> --state all --json number,state,mergedAt,url,title` when needed.
   - Additional signals:
     - `git status -sb` shows the branch is diverged (`[ahead N, behind M]`)
     - the remote tracking branch may already be deleted or stale
   - Refresh repository refs and fast-forward local `main` before branching:
     - `git fetch origin --prune`
     - `git branch -f main origin/main`
   - Preferred safe pattern in this repo when the user wants the current dirty workspace turned into a new PR without disturbing the root checkout:
     - create a fresh worktree and fresh branch from latest `origin/main`
       - `git worktree add -b <new-branch> <new-worktree> origin/main`
     - enumerate the current meaningful local changes in the dirty root checkout
       - `git diff --name-only`
       - `git ls-files --others --exclude-standard`
     - copy only those changed/untracked files from the dirty root checkout into the fresh worktree
     - verify the fresh worktree now shows exactly that change set against `origin/main`
   - This avoids using `stash`, keeps the user's existing dirty root workspace intact, and still yields a clean latest-main PR branch.
  - Important repeat-request lesson: if the user asks for the same "update main + make a PR from current local changes" flow again later in the same dirty root checkout, do **not** assume the last follow-up branch/PR is still open or still matches the current root state.
    - Re-check both the current root branch and any most recently created follow-up branch/PR.
    - A previous PR you created from a fresh worktree may already be merged, while the root checkout still sits on an older merged branch with additional new local edits accumulated afterward.
    - In that case, repeat the same safe transplant flow again from the current root diff onto a brand-new latest-`origin/main` branch, rather than trying to reuse the earlier follow-up branch name or infer state from the last PR you created.
  - Additional overlap-vs-new-scope lesson: even if there is still an OPEN follow-up PR, do **not** assume the current root dirty state belongs on that PR.
    - First compare the current root changed/untracked file set against the open PR worktree or branch tip.
    - Practical checks:
      - list root tracked/untracked changes
      - inspect the open PR branch's committed file list vs `origin/main`
      - compare root files byte-for-byte against the open PR worktree for overlapping paths
    - Interpret the result in three buckets:
      1. identical to the open PR state -> update that PR branch
      2. root state is a strict superset of the open PR and the user clearly wants one cumulative PR -> consider updating the same PR after explicit scope confirmation
      3. root state only partially overlaps and also contains additional or divergent local changes -> create a new latest-main branch/PR for the current root state
    - In `skills-jk`, case (3) is common because the root checkout can stay dirty on an old merged branch while one or more fresh-worktree follow-up PRs are created and merged separately.
    - Do not blindly pile new local changes onto the still-open PR just because some files overlap; if the root diff is not materially the same as the open PR diff, split it into a new PR.
  - Safer fallback when a clean file-copy transplant is impractical:
    - create a preserve branch/worktree that captures the full current dirty file set first
    - refresh repository refs and update local `main` to latest `origin/main`
    - create a fresh branch/worktree from `origin/main`
    - if there is an unmerged local commit you still need, cherry-pick it onto the new branch
    - if the cherry-pick becomes empty because latest `main` already contains that change, use `git cherry-pick --skip`
    - copy only the still-intended preserved diff into the fresh branch/worktree
  - This preserves the still-local work while avoiding accidental reuse of a stale merged-PR branch.
   - If there is an unmerged local commit you still need, cherry-pick it onto the new branch.
   - If the cherry-pick becomes empty because latest `main` already contains that change, use `git cherry-pick --skip` and continue.
   - Only then continue with staging/committing. This preserves the current file state while ensuring the new PR is based on clean latest main rather than a previously merged PR branch.
6. Commit only the meaningful files on the current branch.
7. Before push/PR creation, verify the final file/tree state still differs from latest `origin/main`.
   - Do not rely only on commit history such as `git log origin/main..HEAD`; local commits can remain on a stale merged branch even when the final file tree is already identical to latest `origin/main`.
   - Check both:
     - tracked diff: `git diff --name-status origin/main -- .`
     - tree identity when helpful: `git rev-parse HEAD^{tree}` vs `git rev-parse origin/main^{tree}`
   - If the tracked diff is empty and the trees match, there is no real PR payload left. Do not manufacture a follow-up PR just because old local commits still exist.
   - In that case, report that `main` was updated, no tracked changes remain, and only any local scratch/untracked files are left for the user to keep or delete.
8. Before push/PR creation, rebase the current branch onto latest `origin/main`.
   - This is especially important when the branch was created from an older local `main` or its remote tracking branch is gone.
   - If rebase conflicts come from settings already present on latest `main`, keep the newer `main` values and continue so the PR diff stays focused on the still-local changes.
9. After any manual conflict resolution, explicitly scan the touched files for leftover merge markers before committing or pushing.
   - In `skills-jk`, append-only markdown files such as `.hermes/memories/*.md` and skill `SKILL.md` files often conflict when both latest `main` and the local work added new bullets near the end.
   - Do not blindly choose one side; read the conflict block and keep both sides' new entries unless they are true duplicates.
   - Preserve existing separators like `§` in memory files.
   - At minimum run a targeted search like `rg -n '^(<<<<<<<|=======|>>>>>>>)' <files...>`.
   - Do not rely only on `git status`; a file can be marked resolved while still containing conflict text.
   - For config files such as `.yaml`, also run a lightweight parse check (for example `python -c 'import yaml, pathlib; yaml.safe_load(pathlib.Path(...).read_text())'`).
   - When resolving against latest `main`, prefer the actual `origin/main` file content as the source of truth instead of guessing which side of the conflict to keep.
9. If `git rebase --continue` is blocked because you restored broader local workspace changes while the rebased commit itself only touches a smaller subset of files, temporarily move the unrelated non-index changes back out of the way.
   - Practical pattern:
     - stage the actual conflict-resolved file(s) that belong to the rebased commit
     - preserve the broader unrelated local changes in a separate worktree/branch or patch file first
     - `GIT_EDITOR=true git rebase --continue`
     - re-apply only the intended preserved changes after the rebase finishes
   - This is especially useful in `skills-jk` when a one-file commit is being rebased but the working tree also contains many restored local skill/memory edits from the user's current workspace.
   - Without this step, `git rebase --continue` can fail or become confusing because the rebase commit is ready, but unrelated restored changes are still sitting unstaged in the working tree.
10. Push the branch, then create or update the PR.
10. Leave local-only artifacts untracked unless the user explicitly wants them in the PR.
11. In the PR body, briefly note what was intentionally excluded if that helps reviewers understand the scope
12. Before you declare the PR done, do a root-vs-PR payload reconciliation when working from a dirty root checkout.
   - Practical pattern in `skills-jk`:
     - in the dirty root checkout, list the meaningful tracked changes you intended to carry, often by excluding known local-only files such as `.hermes/config.yaml`
       - example: `git diff --name-only -- . ':(exclude).hermes/config.yaml' | sort`
     - in the fresh PR worktree, list the actual branch diff versus `origin/main`
       - example: `git -C <worktree> diff --name-only origin/main...HEAD | sort`
     - compare the two lists before final reporting
   - If a meaningful tracked file is present in root but missing from the PR worktree diff, do not finalize yet:
     - first inspect whether the file was truly omitted from the transplant, or whether latest `origin/main` already contains that exact change so it no longer appears in the PR diff
     - practical check:
       - copy the root file into the fresh worktree if needed
       - then re-run `git -C <worktree> status --short` and `git -C <worktree> diff --name-only origin/main...HEAD`
     - if the file becomes modified in the worktree, it was omitted and should be committed/pushed onto the PR branch
     - if the file still does not appear as modified after copying, treat it as already absorbed by latest `main`, not as a missing PR payload
  - Important repeated-workspace-sweep lesson: after you transplant many root files onto a fresh latest-main worktree, the final PR scope can shrink dramatically because latest `origin/main` may already include most earlier local skill/memory edits.
    - In that case, do not force all root-changed files into the PR just to mirror the dirty root list.
    - Instead, report the branch diff that actually remains unique on top of latest `main`, and explain briefly that the other root-local changes were already absorbed upstream.
  - Practical no-op-collapse pattern from repeated `skills-jk` sweeps:
  - Practical no-op-collapse pattern from repeated `skills-jk` sweeps:
    - it is acceptable to copy a broader candidate set from the dirty root checkout into the fresh latest-main worktree first, especially when many `.hermes/skills/**` and memory files look plausibly relevant
    - immediately after copying, inspect the fresh worktree's real status:
      - `git -C <worktree> status --short --branch`
      - `git -C <worktree> diff --name-only | sort`
      - `git -C <worktree> ls-files --others --exclude-standard | sort`
    - expect many copied files to disappear from the worktree diff as no-ops because latest `origin/main` already contains them
    - stage and commit only the files that still appear as modified/untracked in the fresh worktree after that collapse
    - do not try to re-add already-absorbed files by hand just because they were part of the root candidate list
    - important pitfall: before the first commit in that fresh worktree, do not use only `git -C <worktree> diff --name-only origin/main...HEAD` to decide whether any payload survived
      - that triple-dot `origin/main...HEAD` comparison only reflects committed branch history and can stay empty while the fresh worktree still has real uncommitted transplanted changes
      - for the pre-commit collapse check, trust working-tree signals first: `git status --short`, `git diff --name-only`, and `git ls-files --others --exclude-standard`
      - use `origin/main...HEAD` as the authoritative payload view only after the surviving changes have been committed

      - that triple-dot `origin/main...HEAD` comparison only reflects committed branch history and can stay empty while the fresh worktree still has real uncommitted transplanted changes
      - for the pre-commit collapse check, trust working-tree signals first: `git status --short`, `git diff --name-only`, and `git ls-files --others --exclude-standard`
      - use `origin/main...HEAD` as the authoritative payload view only after the surviving changes have been committed
  - Additional sequential-follow-up lesson from repeated same-day `skills-jk` sweeps:
    - a freshly created follow-up PR can merge quickly, have its remote branch auto-deleted, and be incorporated into `origin/main` before the user asks again
    - meanwhile the dirty root checkout may still show a much larger old candidate set because it is sitting on a stale merged branch with additional untouched local edits
    - the root checkout may even still be parked on that old merged branch rather than on `main`; treat that as stale control-state, not as the branch that should receive the new PR work
    - when that happens, do **not** reuse the previous follow-up worktree or assume the previous PR is still the right target
    - re-check all four facts explicitly:
      - `env -u GITHUB_TOKEN gh pr status` to detect whether the current root branch itself is already merged/closed
      - `env -u GITHUB_TOKEN gh pr list --head <previous-branch> --state all --json number,state,mergedAt,url`
      - `git fetch origin --prune`
      - `git branch -f main origin/main`
    - if the current root branch or previous follow-up PR is already merged, leave the dirty root checkout untouched, update the local `main` ref to latest `origin/main`, and create one more brand-new latest-main worktree/branch for the new PR
    - if the previous PR is already merged or its remote branch is gone, start one more brand-new latest-main worktree and repeat the transplant/collapse process
    - expect the surviving payload to shrink again, sometimes to only a few files, because the earlier follow-up PR may already have absorbed most of the root-local changes
    - however, do not assume the surviving payload only shrinks monotonically: new tracked root edits can also appear between repeated user requests while `origin/main` advances, so the next surviving diff may be a different small set than the previous PR payload
    - practical rule: on each repeated request, rebuild the candidate list from the current dirty root checkout first, then transplant into a brand-new latest-main worktree and trust only the post-copy collapsed diff there
    - report the final PR scope from the fresh worktree diff against latest `origin/main`, not from the stale root candidate list
  - Additional open-PR separation rule from repeated local sweeps:
    - the previous follow-up PR may still be OPEN while the dirty root checkout has accumulated further tracked changes on top of it
    - do **not** automatically widen that open PR just because some files overlap
    - first compare the current root files against the open PR worktree/branch tip and split the root candidate set into:
      1. files identical to the open PR state
      2. files changed differently than the open PR state
      3. files not present on the open PR at all
    - if buckets (2) or (3) exist and the user did not explicitly ask for one cumulative PR, preserve the existing open PR as-is and open a new latest-main PR for only the additional surviving changes
    - practical pattern:
      - inspect the open PR branch with `gh pr list --head <branch> --state open --json number,url,title`
      - compare root files byte-for-byte against the fresh worktree for that PR branch when needed
      - when building the candidate file list for the new PR, exclude any file whose root-workspace content is byte-identical to the open PR worktree copy
      - only transplant files that are absent from the open PR worktree or differ from it byte-for-byte
      - after transplant, trust the fresh worktree's working-tree status/diff as the payload for the new PR
    - this avoids silently broadening an in-review PR after the user already has a reviewable URL for it
  - Multi-follow-up refinement from repeated same-root sweeps:
    - by the time the user asks again, one or more earlier follow-up PRs may already be `MERGED` while another follow-up PR is still open, and the dirty root checkout can contain a mixture of:
      1. files already absorbed by latest `origin/main`
      2. files still represented by an open PR worktree
      3. newly diverged files not present in either place
    - safe order:
      1. `git fetch origin --prune`
      2. re-check every recent follow-up branch with `gh pr list --head <branch> --state all --json number,state,mergedAt,url`
      3. fast-forward local `main` with `git branch -f main origin/main`
      4. create one brand-new latest-main worktree for the new PR candidate
      5. if some earlier follow-up PRs are still open, exclude root files that are byte-identical to those open-PR worktrees
      6. copy the remaining candidate files into the new worktree and trust the post-copy collapse there
    - practical rule:
      - if a previous follow-up PR is now `MERGED`, do not keep treating its old worktree as an active comparator; latest `origin/main` already represents that line
      - if a previous follow-up PR is still `OPEN`, use the open PR worktree as the comparator and exclude byte-identical files from the next PR candidate set
      - after this filtering, the new PR payload should represent only files that are still unique versus both latest `origin/main` and any still-open follow-up PRs
  - Final repeated-sweep reporting rule:
    - when you update local `main`, discover that earlier follow-up PRs have already merged, and then open one more PR from the current dirty root checkout, report those as three distinct facts rather than one blended success statement:
      1. local `main` is now aligned to latest `origin/main`
      2. earlier follow-up PRs/branches were checked and are already merged or obsolete
      3. the newly created PR contains only the surviving diff that still remains unique on top of latest `origin/main`
    - include the new PR number/URL, branch name, commit hash, and the final payload file list from the fresh worktree diff
    - do not describe the whole stale root candidate set as if it were the PR payload
  - Additional user-scoped-payload rule from `skills-jk` root cleanup + PR work:
    - sometimes the user asks for two things together:
      1. update root `main`
      2. make a PR only for a very specific tracked subset such as `.hermes/config.yaml`, `.hermes/memories/MEMORY.md`, and `.hermes/memories/USER.md`
    - in that case, do not widen the PR just because the dirty root checkout also contains many other tracked skill/reference edits
    - safe pattern:
      1. enumerate the full dirty root tracked/untracked set
      2. split it into `requested PR payload` vs `other meaningful local tracked work`
      3. preserve the broader non-requested tracked work onto a clearly named local-only branch/worktree first (for example `preserve/...`), preferably based on latest `origin/main`
      4. restore those non-requested paths from the root checkout so root `main` can be refreshed cleanly
      5. fast-forward root `main` to latest `origin/main`
      6. create the narrow PR branch/worktree containing only the requested surviving payload
    - important nuance:
      - a requested file can collapse to a no-op on latest `origin/main` while sibling requested files still produce a real diff
      - report the final PR payload from the fresh worktree diff, and separately report the preserved local-only branch/worktree that still holds the broader non-requested line
    - do not imply that the preserve branch has a GitHub URL unless you actually pushed it; in many cases the correct final state is `narrow bot PR + local-only preserve branch`
  - After the create-pr workflow finishes, verify the resulting PR object and the payload separately:
    - PR object lookup: `env -u GITHUB_TOKEN gh pr list --head <branch> --state all --json number,state,url,title,headRefName,baseRefName`
    - payload lookup: `git -C <worktree> diff --name-only origin/main...HEAD | sort`
   - Prefer the payload list above as the final source of truth for "what this PR contains".
     - Do not summarize the PR scope from the dirty root checkout alone.
     - Do not assume every locally changed file belongs in the final PR just because it was part of the user's current root workspace.
   - This catches two common failure modes in repeated local-workspace sweeps:
     1. a tracked skill/memory file was accidentally omitted from the fresh PR worktree
     2. a file looked "missing from the PR" but in reality latest `main` had already absorbed it, so no new diff remained to review

## Worktree location preference in `skills-jk`

When this workflow needs a fresh worktree in `skills-jk`, prefer a repo-root path under `.worktrees/<flat-topic>` rather than creating sibling worktrees directly under `~/workspace`.

Recommended pattern:

```bash
git fetch origin --prune
git worktree add .worktrees/<flat-topic> -b <branch-name> origin/main
```

Why:
- matches the repo's current guidance direction
- keeps repo-local cleanup and stale-worktree inspection simpler
- avoids scattering many sibling worktree directories across `~/workspace`
- still preserves the existing flat-name rule: keep the directory name short and flat even if the branch name contains slashes

## Evidence from use

Observed in `skills-jk`:
- direct local `gh pr create --body` caused shell quoting issues with markdown/backticks
- `.github/workflows/create-pr.yml` already exists and is the repo-preferred PR creation path

## Completion checklist

- branch pushed
- existing PR checked
- workflow dispatched
- workflow completed successfully
- resulting PR number and URL verified

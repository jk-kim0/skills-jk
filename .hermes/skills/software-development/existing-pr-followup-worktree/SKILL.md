---
name: existing-pr-followup-worktree
description: When a user asks for follow-up changes to work already under review, use a fresh worktree on the existing PR branch and update the same PR instead of creating a new one.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [git, github, pr, worktree, review-feedback]
---

# Existing PR Follow-up via Fresh Worktree

Use this when the user asks for additional fixes or refinements to a PR that already exists.

Core rule:
- Fresh worktree: yes
- Existing PR branch: yes
- New branch: no, unless the user explicitly asks
- New PR: no, unless the user explicitly asks

Important distinction learned from review follow-up work:
- "Every new task should start from a fresh worktree + fresh branch" applies to new independent work.
- "Please update PR #N" or any review/follow-up on work already under review means: use a fresh worktree, but attach it to the existing PR branch and push back to that same branch.
- Do not satisfy the fresh-worktree requirement by creating a second branch/PR for the same review cycle.
- If the referenced PR is already merged and its head branch has been deleted, you cannot continue on that original PR branch. In that case, verify the merge commit is now on `origin/main` (or the PR base branch), create a fresh worktree from that merged tip, and open a new follow-up branch/PR for the requested additional work.
- Important branch-reuse rule learned from post-merge follow-up work: even if you still have the old local branch or recreate the same branch name after the PR merged, do not use that same branch name for a new follow-up PR. Reusing the merged branch name can make the next PR carry the already-merged commit(s) together with the new follow-up commit(s), producing a misleading multi-commit diff. For post-merge follow-up, create a fresh branch name from latest `origin/main`.
- Exception: if the requested "follow-up" actually depends on code or route structure that already landed on latest `origin/main` but is missing from the old PR branch, do not force the change onto the stale PR branch. Treat it as a new independent task: branch from latest `origin/main`, open a separate PR, and mention explicitly why the old PR branch was no longer the right base.
- Practical heuristic for this exception: if you discover during inspection that the target route family, helper layer, sitemap shape, or canonical-path policy already changed on `origin/main` after the old PR branched, switching to a new main-based branch is usually safer than backporting those structural assumptions into the old PR.
- Additional split-PR case: if the user explicitly asks to take part of an open PR (for example an extract/refactor-only subset) and make it a separate PR, do not assume it belongs on the existing PR branch just because the work originated there.
- First inspect whether that subset is truly independent of the open PR's unmerged code.
- If the subset can stand on its own against latest `origin/main`, recreate or reapply only that subset on a fresh latest-main branch.
- If the requested separate PR depends on code that exists only on the still-open parent PR branch, create a stacked PR instead: start a fresh worktree from the parent PR head, create a new child branch from there, apply only the requested follow-up refactor, and open the child PR with the parent PR branch as its base.
- If the parent PR has already grown beyond the exact comparison target (for example a broader semantic-composition rewrite landed on the parent PR, but the user now wants to compare only one subsection experiment), do not blindly branch from the latest parent head. First inspect the parent PR commits and choose the most appropriate parent commit baseline that still contains the prerequisite code but not the later broadening changes. Then create the child comparison branch from that exact commit and open the stacked PR against the parent branch. This keeps the comparison PR narrowly focused and avoids smuggling unrelated follow-up refactors into the experiment.
- In the independent split-PR case, prefer reimplementation/cherry-picking only the minimal independent commit(s) rather than branching from the old PR head. The goal is a clean PR diff against `main`, not a PR that drags along the larger in-progress branch context.
- In the dependency-on-parent case, prefer the stacked PR over forcing a fake `main`-based branch, because that keeps the review diff small and avoids duplicating the parent PR's not-yet-merged code.

## When to use
- "PR 32에 수정사항 넣어줘"
- "리뷰 반영해줘"
- "기존 PR에 이어서 수정해줘"
- Any follow-up request where work is already under review

## Why
Reusing a stale local checkout or creating a second PR for review follow-up causes confusion:
- accidental divergence from the PR branch
- rebase conflicts from stacking unrelated follow-up work
- duplicate PRs for one logical review cycle
- stale CI status and hard-to-track branch history

## Workflow

### 1. Inspect the existing PR
Use GitHub CLI to confirm the PR number, head branch, and current status.

Example:
```bash
gh pr view <pr-number> --json number,headRefName,url,state,updatedAt
```

Record:
- PR number
- head branch name
- PR URL
- PR state (`OPEN`, `MERGED`, or `CLOSED`)

Important precondition check learned from real follow-up work:
- Before doing any worktree/rebase/update flow, confirm the PR is still open.
- Also confirm the remote head branch still exists.
- A PR can already be merged while `gh pr view` still shows the historical `headRefName` and `headRefOid`.
- In that case, `git fetch origin <head-branch>:...` or `git worktree add ... origin/<head-branch>` will fail because the remote branch has already been deleted.

Recommended check sequence:
```bash
env -u GITHUB_TOKEN gh pr view <pr-number> --json state,headRefName,headRefOid,baseRefName,url
git ls-remote origin refs/heads/<head-branch>
```

How to interpret it:
- If PR state is `OPEN` and the remote head branch exists: continue with the normal existing-PR follow-up workflow.
- If PR state is `MERGED` or `CLOSED`: do not treat it as an update-in-place target anymore.
- If PR state is merged/closed and the branch is deleted: stop treating it as a live PR branch task and switch to a new latest-main follow-up branch/PR workflow if further changes are still needed.
- If PR state says open but `ls-remote` returns nothing, re-check the PR metadata because the branch may have been deleted manually or the PR may have just been merged.
- Important closed-PR branch-name lesson from corp-web-japan PR 223 follow-up: if a PR has already become `CLOSED`, pushing new commits to a branch with the same historical name does **not** reliably resume or update that PR. GitHub can treat it as a newly created branch ref while the closed PR remains pinned to its old head SHA.
- Always verify both pieces separately after pushing to a historical PR branch name:
  ```bash
  git ls-remote origin refs/heads/<pr-branch>
  gh pr view <pr-number> --json state,headRefName,headRefOid,url
  ```
- If the remote branch tip advances but the PR stays `CLOSED` and its `headRefOid` does not move, do not claim the PR was updated. Report clearly that the branch was pushed but the PR is no longer attached, and ask whether to reopen the PR or open a new PR from that branch.

### 2. Create a fresh worktree from the PR branch
From the repo root:

```bash
git fetch origin --prune
git worktree add .worktrees/<topic> origin/<pr-branch>
cd .worktrees/<topic>
git checkout -b <pr-branch>-local --track origin/<pr-branch> 2>/dev/null || git checkout <pr-branch>
```

Important path rule learned from real PR follow-up work:
- Keep the worktree directory name flat even if the branch name contains slashes.
- Good: branch `feat/internal-mdx-list-demo-whitepaper-ux` with worktree path `.worktrees/internal-mdx-list-demo-whitepaper`
- Risky: deriving the worktree path mechanically from the branch name, such as `.worktrees/feat/internal-mdx-list-demo-whitepaper-ux`
- Why this matters:
  - Git will happily create nested directories for the worktree path
  - later file-tool calls can target the wrong nested path or fail because you mentally tracked the branch name instead of the actual directory path
  - this becomes especially confusing when mixing `terminal` commands with absolute file-tool paths during follow-up edits
- Prefer choosing a short flat `<topic>` path first, then attach it to the PR branch tip.

Practical note:
- If the branch is already checked out in another worktree, `git checkout <pr-branch>` in the fresh worktree will fail. In that case, staying on the detached `origin/<pr-branch>` checkout is acceptable for a small follow-up.
- You can make the fix, commit on detached HEAD, and push with `git push origin HEAD:<pr-branch>`.
- In this detached state, some `gh pr ...` commands that rely on the current branch can fail with errors like `could not determine current branch`. Prefer explicit branch/PR arguments, e.g. `gh pr view <pr-branch> --json ...` or `gh pr view <pr-number> --json ...` instead of assuming branch autodetection will work.
- This still satisfies the core requirement because the fresh worktree starts from the PR branch tip and updates the same remote PR branch.
- The important thing is: the new worktree must start from the PR's remote head, not from `main` and not from some old local branch.
- Important tool-path pitfall from real follow-up work: Hermes file-edit tools (`patch`, `write_file`, sometimes `read_file`) do not automatically follow a `terminal` command's `workdir`, and repo-root-relative file paths can silently hit the main checkout instead of the fresh PR worktree.
- Before editing with file tools, confirm which checkout the path resolves against.
- Safe patterns:
  - prefer absolute paths into the target worktree when the specific file tool supports them reliably
  - for follow-up terminal commands as well (`git -C`, push, status, rev-parse, diff), prefer an absolute worktree path over a repo-relative `.worktrees/<topic>` path; in practice the agent/session cwd can differ between calls, and a relative worktree path that worked earlier can later fail with `No such file or directory`
  - do not assume all file tools behave the same way: in practice, `write_file` and `read_file` may accept absolute worktree paths while `patch` can still resolve against the repo root or fail on the same path style
  - if a `patch` or similar edit behaves unexpectedly, stop and verify whether the change landed on the root checkout instead of the PR worktree before continuing
  - otherwise edit only after confirming your file-tool path base, then verify with `git -C <absolute-worktree-path> status --short`
  - important read/write pitfall learned from follow-up refactors: `read_file` output is a display format, not raw file bytes. It includes `LINE|content` prefixes, and repeated reads can sometimes return a dedup placeholder like `File unchanged since last read...` instead of the raw file body.
  - because of that, do **not** round-trip `read_file(...)["content"]` directly back into `write_file`/scripted rewrites unless you first strip the line-number prefixes and confirm you are holding real source text rather than a dedup message.
  - if you need lossless programmatic rewrites in a PR follow-up worktree, prefer shell/Python file I/O in `terminal` or use `write_file` only with content you constructed explicitly, not blindly copied from `read_file` display output.
  - after any file-tool edit during PR follow-up, immediately compare both the repo root and the target worktree so you do not accidentally leave changes on `main`
- Practical verification loop:
  ```bash
  git status --short
  git -C .worktrees/<topic> status --short
  ```
  If the root checkout changed but the PR worktree did not, stop and move the change onto the PR worktree before committing.
- Important diff-base pitfall learned from PR scope-reduction follow-up work: in a fresh detached-HEAD PR worktree, `git diff origin/main...HEAD` only compares committed history. It does **not** include your current uncommitted edits, so after you start rewriting the PR scope it can misleadingly keep showing the old PR file list/stat even though your worktree has already changed direction.
- When you are actively editing an open PR branch and want to understand the current in-progress result, use both views explicitly:
  ```bash
  # What is currently uncommitted in the worktree?
  git diff --stat
  git diff --name-only

  # What committed PR history currently differs from main?
  git diff --stat origin/main...HEAD

  # What would the final result look like if committed right now?
  git diff --stat origin/main
  git diff --name-only origin/main
  ```
- Heuristic:
  - use `origin/main...HEAD` to inspect the already-pushed/committed PR scope
  - use plain `git diff` to inspect your local follow-up edits
  - use `git diff origin/main` when reducing or rewriting the PR scope and you need to see the combined final tree-vs-main result before committing
- This matters especially when the user asks to narrow an existing PR (for example, revert public-route rollout and keep only an internal demo). If you rely only on `origin/main...HEAD`, you can think the unwanted old scope is still present even after you already removed it locally.

### 3. Verify you are on the PR line before editing
```bash
git branch --show-current
git status -sb
git rev-parse HEAD origin/<pr-branch>
```

If local `HEAD` and `origin/<pr-branch>` differ before you start, stop and understand why.

Additional worktree-path sanity check learned from PR follow-up maintenance:
- After `git worktree add ...`, do not assume the path you requested is the path you should keep using.
- Immediately verify the registered worktree list and the target top-level path before file edits:
  ```bash
  git worktree list --porcelain
  git -C <expected-worktree-path> rev-parse --show-toplevel
  ```
- If the expected path is missing from `git worktree list`, or `git -C <expected-worktree-path> ...` fails, stop and fix that first.
- In practice, this protects you from editing against an imagined path while the real PR branch checkout is still an older existing worktree such as `.worktrees/<old-topic>`.
- If the branch is already checked out elsewhere and you decide to reuse that existing worktree, explicitly verify that it is on the remote PR tip and not on stale divergent local history before editing.

Important practical finding:
- Do not trust an existing local worktree just because its directory name suggests it belongs to the target PR branch.
- A previously used PR worktree can sit on a local tracking branch that is now `ahead`/`behind` the remote PR branch, which makes it unsafe as the starting point for a new follow-up edit.
- If `git status -sb` shows divergence like `[ahead N, behind M]`, prefer creating a brand-new worktree directly from `origin/<pr-branch>` again, even if another PR-named worktree already exists.
- In that situation, a detached-HEAD worktree at `origin/<pr-branch>` is usually the safest follow-up base. Make the edit there, commit, and push with `git push origin HEAD:<pr-branch>`.
- This avoids accidentally stacking new follow-up commits on top of stale local-only history from an older attempt.
- Additional selection heuristic from PR 253 follow-up work: if the user specifically asks you to reuse an existing worktree, inspect the actual registered worktree names first and choose the cleanest worktree whose name is closest to the requested topic or route family.
- Do not opportunistically reuse a clearly unrelated worktree just because it is clean; for example, a typography/about-us worktree is a poor fit for a demo-route rollout follow-up.
- If the user objects that the chosen worktree is for another active task, stop using it immediately, restore it to its prior detached/branch state if you changed it, and switch to a better-named existing worktree before making further edits.
- In practice, this means the worktree-name audit itself can be a required step: compare all registered `.worktrees/*` names, identify the best topical match, and only then attach the PR follow-up branch there.
- Additional scope-correction lesson from the same PR 253 follow-up: if you widened the scope beyond the user's intent while updating an open PR branch, do not defend the broader interpretation or leave the extra removals in place.
- First identify the exact mistaken expansion, then restore only that wrongly touched scope on the same PR branch.
- Practical example: removing specific demo `/t/...` preview entrypoints did **not** imply removing the global Preview Toggle UI or its API route.
- In that situation, the correct recovery was to restore only:
  - `src/components/layout/preview-mode-toggle.tsx`
  - `src/app/api/preview-navigation/route.ts`
  - the header wiring that renders the toggle
  while keeping the originally requested demo-route rollout intact.
- Heuristic: when the user says your previous interpretation was too broad, treat that as an instruction to narrow the PR back to the exact intended scope immediately, then rerun the smallest relevant tests and push the correction to the same PR branch.

### 4. Make the requested fix
Edit only the files needed for the follow-up request.

### 5. Validate
Run the relevant checks before pushing.

Typical examples:
```bash
npm run test:run
npm run typecheck
```

Special case: the user asks you to remove forbidden-scope changes from an already-open PR branch
- Example: "PR #44에서 CMS 데이터 파일 건드린 건 모두 취소해줘"
- Use a fresh worktree on the existing PR branch, not a new branch/PR.
- Discover the exact file set from the PR diff against the base branch, then restore only that forbidden scope from the base branch.
- For a main-based PR, the safest pattern is:
  ```bash
  git fetch origin --prune
  gh pr view <pr-number> --json headRefName
  git worktree add .worktrees/<topic> origin/<pr-branch>
  cd .worktrees/<topic>

  git diff --name-only origin/main...HEAD -- 'forbidden/scope/**' > /tmp/forbidden-files.txt
  while IFS= read -r f; do
    git checkout origin/main -- "$f"
  done < /tmp/forbidden-files.txt
  ```
- Then verify twice:
  1. `git diff --name-only origin/main...HEAD -- 'forbidden/scope/**'` should become empty after the revert commit.
  2. `git diff --stat -- 'forbidden/scope/**'` should reflect only your local revert before commit, then become clean after commit.
- Why both checks matter:
  - `origin/main...HEAD` answers "does the PR still contain this forbidden scope?"
  - plain `git diff -- ...` answers "what is currently uncommitted in the worktree?"
- On macOS/BSD, do not rely on GNU-only `xargs -a`; prefer the portable `while IFS= read -r f; do ...; done` loop above.
- Commit and push back to the same PR branch:
  ```bash
  git add forbidden/scope
  git commit -m "fix: revert forbidden-scope changes"
  git push origin HEAD:<pr-branch>
  ```
- This pattern is especially important when the forbidden scope is CMS-managed data or routes that the user explicitly said must not be touched. Do not try to "partially keep" those edits unless the user explicitly names the exact file/subtree they still want changed.

When the follow-up request is a broad cleanup of repeated behavior on the existing PR branch (for example removing all `target="_blank"` / `rel="noreferrer"` patterns, or fully eliminating a wrapper component the user no longer wants), use an exhaustive search-and-verify loop instead of editing only the first example the user mentions:

1. search the fresh PR worktree for the exact pattern or wrapper usage across `src/` (and tests if relevant)
2. patch every matching implementation site, not just the originally discussed route/file
3. if the request is to eliminate a shared wrapper/abstraction entirely, confirm remaining usage count reaches zero and then delete the wrapper file itself
4. add or update a narrow structure test when useful so the undesired wrapper/pattern does not silently return
5. re-run the same search and confirm zero matches remain in the intended scope
6. run targeted tests that cover the affected surfaces
7. if the PR's title/body now understates or misstates the final broader scope, rewrite them to describe the actual end state before pushing or immediately after the push
8. then commit and push back to the same PR branch

Important follow-up nuance learned from wrapper-removal work:
- the user may first ask for a shared wrapper to disappear entirely, then immediately ask for a more concrete shared component to be re-extracted from the resulting duplicated code
- when that happens, do not treat it as a contradiction or a new PR; it usually means the previous abstraction level was too generic, but a narrower concrete component is still desired
- search for all current duplicates after the wrapper removal, then separate true variants before re-extracting:
  - keep the routes that share the exact same links/behavior together on one concrete component
  - leave variant routes alone if their destinations or semantics differ (for example preview `/t/...` sidebars versus public `/...` sidebars)
- after the re-extraction, rerun structure tests so they assert the new concrete component is used only by the intended subset and that the removed generic wrapper stays gone
- important route-authoring nuance from corp-web-japan resource-list follow-up work: if the user explicitly wants hero/title/description blocks or CTA sections to remain authored in each `page.tsx`, do not respond to wrapper-removal follow-up by extracting those authored sections into the new concrete component. Keep route-owned hero/CTA markup in `page.tsx`, and extract only the repeated structural body that the user actually wants centralized (for example the sidebar markup and its link set).
- related specialization pattern: when the remaining duplicates share the same visual/sidebar structure but differ only by link destinations (for example public `/...` resource links vs preview `/t/...` resource links), prefer a single concrete component with a small `links` prop or variant prop over recreating multiple near-identical concrete components. This preserves the narrower abstraction level the user asked for while still avoiding repeated sidebar markup across routes.

This is especially useful when the user phrases the request as "all links" or says a wrapper should disappear entirely. The cited example file is only a clue, not the full edit set.

### 6. Commit and push back to the same PR branch
```bash
git add <files>
git commit -m "fix: address PR feedback"
git push origin HEAD:<pr-branch>
```

Do not create a new PR here.

Important user-expectation nuance learned from active-review follow-up:
- When a PR is already open and you make additional requested changes, commit and push those changes promptly instead of letting local edits accumulate.
- Treat each meaningful follow-up adjustment as reviewable progress on the existing PR branch unless the user explicitly asks you to batch changes before pushing.
- After each push, re-check PR status and CI so the user can review the updated PR without waiting for a later "finalize" step.
- If `git push origin HEAD:<pr-branch>` is rejected as non-fast-forward during PR follow-up, do not open a new PR or force-push blindly. First fetch and compare against `origin/<pr-branch>` because another follow-up worktree/session may already have advanced the same PR branch.
  Recommended recovery flow:
  ```bash
  git fetch origin --prune
  git rev-parse HEAD origin/<pr-branch>
  git rebase origin/<pr-branch>
  ```
  Then resolve any conflicts and push again. This keeps the same PR branch linear while preserving already-pushed review follow-ups.
- Additional stale-followup-branch lesson from PR 273 maintenance: if the local follow-up worktree still carries the PR branch's pre-rewrite or pre-squash history, a normal `git rebase origin/<pr-branch>` after a non-fast-forward rejection can explode into add/add conflicts on files that were already rewritten on the remote PR branch.
  - Typical signal:
    - your local branch contains many old follow-up commits that no longer exist on the remote PR branch
    - `git log --oneline --left-right HEAD...origin/<pr-branch>` shows the remote side is a new squashed/rebuilt history while the local side still has the old stacked commits
    - rebasing starts replaying obsolete commits and immediately conflicts in renamed/rewritten files
  - In that case, stop using that stale local branch/worktree as the recovery base.
  - Safer recovery flow:
    1. `git rebase --abort` if a rebase is in progress
    2. create a brand-new detached worktree directly from `origin/<pr-branch>`
    3. reapply only the tiny intended follow-up delta there
    4. commit once and push with `git push origin HEAD:<pr-branch>`
  - This is especially useful right after a latest-main rewrite + squash force-push, where the correct recovery for a one-line follow-up is to start from the rewritten remote PR head, not to replay the stale local review history onto it.
- Important detached-HEAD follow-up case learned from PR maintenance work: if you created the fresh worktree directly from `origin/<pr-branch>` and then rebased that detached HEAD onto `origin/main` before pushing, your local history may accidentally rewrite the PR's existing head commit(s), not just add your new follow-up commit.
  - Typical signal:
    ```bash
    git log --oneline --left-right HEAD...origin/<pr-branch>
    ```
    shows your local side contains both your new follow-up commit and a rewritten copy of the old PR tip, while the remote side still has the original old PR tip.
  - In that case, do not force-push the rewritten stack for a normal review follow-up.
  - Instead, transplant only your new follow-up commit(s) onto the current remote PR head:
    ```bash
    git fetch origin --prune
    git rebase --onto origin/<pr-branch> <old-local-pr-tip> HEAD
    ```
    where `<old-local-pr-tip>` is the local commit that used to correspond to the original PR tip before your new follow-up commit(s).
  - After that, verify `git log --oneline --decorate -n 5` shows `origin/<pr-branch>` followed by only your intended new follow-up commit(s), rerun the targeted test, and push normally.
  - This preserves the existing open PR history while still letting you rebase your new work onto the remote PR head.- If the user later asks to clean up the PR title/body, rewrite them to describe only the final end state of the PR. Do not narrate intermediate implementation history unless the user explicitly wants that context.
- If the user asks to squash the branch history for an open PR, use a fresh worktree from the PR branch tip, `git reset --soft <base-branch>`, recommit once with the final conventional-commit message, then `git push --force-with-lease origin HEAD:<pr-branch>` and re-check PR/CI status.
- Important latest-main squash/rebase guardrail learned from PR #240 maintenance: before doing a mechanical squash or rebase, inspect `git diff --stat origin/main..HEAD` and `git diff --name-only origin/main..HEAD`. If the open PR branch is carrying unrelated old file diffs from previous branch history (for example an old content/test topic unrelated to the current PR scope), do not preserve that history with a raw rebase/reset flow.
  Safer recovery pattern:
  1. create or reuse a fresh worktree based on latest `origin/main`
  2. copy only the intended PR file set from `origin/<pr-branch>` with `git checkout origin/<pr-branch> -- <intended-paths...>`
  3. verify the resulting diff against latest main contains only the intended scope
  4. commit once
  5. `git push --force-with-lease origin HEAD:<pr-branch>`
  This is effectively a latest-main rewrite, not a historical replay, and is the right choice when the user asked for "rebase onto latest main + squash" but the existing branch ancestry would otherwise keep dragging unrelated stale diffs into the PR.
- Additional repetition guardrail from later PR #240 maintenance: do not assume a previous cleanup/rewrite remains valid on the next turn. If the user asks again to rebase/squash the same open PR after `origin/main` has advanced or after more follow-up pushes landed, re-run the full `origin/main..origin/<pr-branch>` diff audit from scratch. Unrelated scope can reappear in the remote PR branch even if you already cleaned it once.
  Practical pattern:
  1. fetch `origin --prune`
  2. inspect `git rev-list --left-right --count origin/main...origin/<pr-branch>`
  3. inspect `git diff --stat origin/main..origin/<pr-branch>`
  4. if unrelated files are present again, create a brand-new latest-main detached worktree and re-copy only the intended scoped files from `origin/<pr-branch>`
  5. recommit once and force-push again
  This avoids trusting stale assumptions such as "the branch was already squashed last time, so a plain rebase is safe now."
- Additional scope-isolation pattern from PR #103 maintenance: when the user asks to rebase/squash an old open PR but also says "revert all font changes" or "leave only the implementation related to <component/file>", do not start by replaying the old PR's original route/page wiring. First inspect latest `origin/main` to find the component's current real usage site(s).
  - The stale PR branch may reference the component from an older page shape that no longer exists on main.
  - Safer flow:
    1. inspect the remote PR file list and diff against latest main
    2. read the latest-main version of the target component and grep for its current usage sites on `origin/main`
    3. read the stale PR branch's version to understand the intended enhancement
    4. reconstruct the smallest latest-main diff by applying the enhancement to the component plus only the current caller(s) that still need to pass new props or assets
    5. include any required optimized asset file only if the latest-main caller truly needs it
    6. verify the final diff against `origin/main` contains only that minimal component-related scope before committing
  - This prevents preserving obsolete page rewrites or unrelated font/layout work just because that was how the old PR originally delivered the component change.
- Additional instance-specific follow-up pattern from later PR #103 work: if the user asks for behavior that should apply only to one current usage of a shared component on the open PR branch (for example making a single zoomable image open larger on one page), do not hard-code the broader behavior globally first.
  - Prefer adding a small configurable prop surface to the shared component, keeping defaults identical for all existing callers.
  - Then update only the intended current caller in the PR scope to pass the more aggressive values.
  - Practical example: `ZoomableFigure` gained `modalViewportWidth` / `modalViewportHeight` defaults that preserved the old `94vw` / `88vh` behavior, while the AI Dashi value-diagram caller alone opted into `98vw`, `94vh`, and a larger `modalScale`.
  - Verification heuristic:
    1. grep for all current callers in the fresh PR worktree
    2. confirm only the intended caller changed
    3. confirm the shared component defaults still match the pre-follow-up behavior
  - This keeps the follow-up diff small, avoids accidental UX shifts on unrelated pages, and matches user intent when they refer to a specific page/image rather than the component globally.
- For small PR follow-ups such as squash, title/body edits, route/path renames, or other narrow review-driven fixes, do not automatically run local build/test verification unless the user explicitly asks for it. Prefer the fast path: edit -> commit -> push -> confirm PR updated -> watch CI.
- Likewise, do not start a local dev server for visual/manual verification unless the user explicitly asks for that method. If you need confidence without a dev server, prefer scoped tests, code inspection, PR reviewability, and CI.
- Important visual-follow-up caveat learned from preview-UI work: if the user points to a specific Preview Deployment URL and says the rendered result still looks wrong, verify that exact deployed preview in the browser before trusting your local render. Small spacing/icon/asset differences can still show up differently on the deployed preview even when a local dev server looked acceptable.
- If the preview and local render disagree, treat the preview as the source of truth for that follow-up, adjust from the current PR branch, and then use local render only as a quick iteration loop before pushing another preview update.
- At the start of a follow-up task, give a short time estimate. If the work exceeds that estimate, stop and immediately report current status and next step instead of staying silent.

### 6a. If the user asks to rebase the existing PR branch onto the latest main
Use the same fresh-worktree principle, but rebase the PR branch tip onto `origin/main` instead of creating a merge commit.

Recommended flow:
```bash
git fetch origin --prune
git worktree add .worktrees/<topic> origin/<pr-branch>
cd .worktrees/<topic>
git rebase origin/main
```

Important practical findings:
- `git worktree add <path> origin/<pr-branch>` often leaves you on a detached HEAD at the remote branch tip. That is acceptable for a rebase-only maintenance task.
- After a detached-HEAD rebase succeeds, do not force-push immediately. First verify that the expected post-PR follow-up commit(s) still survived the rebase and that their key scoped changes are still present. A fast check is:
  ```bash
  git log --oneline --decorate -n 5
  git search-files-or-grep-for-the-target-pattern
  ```
  For example, if a later follow-up changed a path prefix or removed a repeated pattern, re-check that exact pattern before pushing.
- Then push with:
  ```bash
  git push --force-with-lease origin HEAD:<pr-branch>
  ```
- If conflicts occur, resolve them by preserving the existing PR's intended behavior unless the user explicitly asked to adopt the newer `main` behavior in that area. Rebase conflicts often happen because `main` has evolved policy/tests while the PR still represents a deliberate exception or targeted rollout.
- Important special case: if a separate test-only PR was intentionally merged into `origin/main` before rebasing the implementation PR, and the implementation PR branch still contains overlapping test updates, prefer the latest-main test files during conflict resolution and keep only the implementation commits that are still unique to the PR. In practice:
  - inspect `git rev-list --oneline origin/main..HEAD` after the rebase attempt
  - if the remaining value of the PR is now only the implementation commits, resolve test-file conflicts with `--ours` from the rebasing `origin/main` side (or otherwise restore the latest-main test version)
  - remove delete/modify conflicts for superseded old test files that were already replaced on `main`
  - continue the rebase so the final PR branch contains the implementation changes on top of the already-merged shared test baseline, instead of duplicating or re-fighting the test-only refactor
- Similar split-PR special case: if you previously split an extract/refactor subset out of the original PR and that new PR has already merged into `origin/main`, rebasing the original PR can hit add/add or modify/delete conflicts against those now-upstream files.
  - First identify whether the conflicting file from the original PR is now already present on `origin/main` under the final intended name/path.
  - If yes, prefer the latest-main version of that extracted file during conflict resolution, then keep only the original PR changes that still matter on top of it (for example updated imports/usages in `page.tsx` or removal of the old superseded file/path).
  - Expect duplicate cleanup/rename commits near the end of the rebase to become empty or be auto-dropped as `patch contents already upstream`; this is normal and usually desirable.
  - Practical heuristic: when the conflict is between an old pre-split file path from the original PR and the new extracted file already merged on `main`, do not resurrect the old path just to preserve history. Preserve the final main-side extracted file and continue the rebase with the original PR's remaining unique behavior changes only.
- Same-file neighboring-refactor case: the current PR may refactor one section of a large route file while latest `origin/main` has already merged a different route-local refactor in a nearby section of that same file.
  - Typical signal: rebase conflicts in one large `page.tsx` plus companion structure tests, even though the PR scope is still valid.
  - In that case, do not blindly take either side wholesale.
  - Keep the latest-main refactor that already landed for the neighboring section, then layer the current PR's still-unique section refactor on top of that updated file shape.
  - Also merge the structure tests so both route-local sections are asserted after the rebase, rather than restoring an older single-section test state.
  - After resolving the main conflict this way, a later small follow-up commit from the PR (for example a visual/icon restore fix) may be auto-dropped as `patch contents already upstream` because its effect was already incorporated into the resolved tree. Treat that as normal if the intended final file content is still present.
- Stronger rewrite-on-main case: if the user explicitly asks not just for a mechanical rebase but for the PR to reflect the latest `main` implementation and recent merged follow-ups, a literal `git rebase origin/main` may be the wrong tool.
  - Typical signs: the PR branched before one or more related refactor PRs merged, the old branch has stacked/split follow-up commits mixed in, or the user questions whether the current diff still matches the intended refactor goal.
  - In that case, create a fresh worktree from latest `origin/main`, inspect the current PR branch's intended final file set, and reconstruct that intended end state on top of latest `main` as a new commit sequence (often one clean commit is enough).
  - Then force-push that rewritten latest-main branch back to the same PR branch.
  - Verify with `git merge-base origin/main <pr-branch>` that the PR branch now sits directly on the latest remote main tip (or that tip's exact ancestor if main advanced during work), and rerun local validation before pushing.
  - This is not a normal-first choice; use it when preserving old commit ancestry would keep dragging stale pre-main structure into the PR or would obscure the user's desired final diff.
  - Practical stale-top-page pattern: if multiple sibling PRs were split from an older top-page refactor branch and newer `main` has already absorbed some intermediate sections (for example platform/security, then whitepapers), do not blindly preserve the old mixed diff. First identify which sections are already on `origin/main`, then rebuild each PR so it keeps only its still-unique intended scope (for example whitepapers only, or later final CTA only) on top of latest main.
  - Practical partially-absorbed PR pattern from AI Crew route-local follow-up work: a rebase request can target an open PR whose branch still contains several commits, but latest `origin/main` already includes part of that branch's intent from an earlier sibling PR. In that case, a literal `git rebase origin/main` often collides because the PR is half superseded rather than fully independent.
    Recommended recovery flow:
    1. inspect `git rev-list --oneline origin/main..origin/<pr-branch>` and `git diff --stat origin/main...origin/<pr-branch>` to see the branch's total residual scope
    2. create a fresh clean worktree directly from latest `origin/main`
    3. copy the PR's touched file set from `origin/<pr-branch>` into that clean worktree with `git checkout origin/<pr-branch> -- <paths...>`
    4. then explicitly restore files that should stay on latest-main shape because that part of the refactor already landed via another PR (for example the route file's why-section structure, shared section exports, or data formerly moved into `main`)
    5. keep only the still-unique remainder of the current PR, run the narrowest meaningful regression test, commit once, and `git push --force-with-lease origin HEAD:<pr-branch>`
    This is especially useful when the final desired result is not "replay every historical commit" but "same open PR branch, rewritten so only its surviving unique review scope remains on top of latest main."
  - Consecutive sibling route-local PR pattern from AI Crew follow-up work: when latest `origin/main` already contains earlier sibling PRs that localized adjacent sections (for example `why`, then `design-elements`), and the current PR localizes the next section in sequence (for example `process`), do not revive the old branch's transitional wrapper such as `HomePagePreProcessSections` or re-import older content-backed sections wholesale.
    Safer reconstruction pattern:
    1. start from clean latest `origin/main`
    2. copy the current PR's touched files from `origin/<pr-branch>`
    3. immediately restore the main-owned route file, shared sections file, shared content file, and related tests from `origin/main`
    4. reapply only the current PR's unique section-local pieces onto the latest-main route shape (for example insert the route-local `process` section between the already-main `design-elements` section and the remaining shared post-process sections)
    5. trim the shared sections file so it contains only the remaining sections after the newly localized one
    6. delete any now-redundant content-backed data block from shared content files
    7. update structure/helper tests so they assert the latest-main route-local sections plus the newly localized section together
    8. if launch-readiness or CTA tests previously matched only content-file frontmatter/data, widen them to also accept the equivalent route-local JSX action pattern
    9. rerun the narrow route structure test plus any CTA/launch-readiness regression that inspects the same source paths, then squash to one clean commit and force-push back to the PR branch
    Heuristic: if the current PR's true value is "one more section becomes route-local" and latest main already contains the previous section-local PRs, reconstruct that final latest-main composition directly instead of preserving the old branch's intermediate split points.
  - Practical PR-cleanup pattern for "this PR includes unrelated commits": create a fresh detached worktree directly from latest `origin/main`, create a temporary local branch there, and then copy only the PR's intended scoped files from `origin/<pr-branch>` into that clean worktree with `git checkout origin/<pr-branch> -- <paths...>`. Verify the resulting diff with `git diff --stat origin/main...HEAD` and `git diff --name-only origin/main...HEAD`, run validation, commit once, then `git push --force-with-lease origin HEAD:<pr-branch>`. This is safer than trying to interactively prune old mixed branch history when the desired result is a clean single-scope PR.
  - Additional narrow-PR reconstruction pattern from PR 255 maintenance: when an open PR is supposed to contain only a very small follow-up scope, first treat the PR's current GitHub file list as the authoritative intended scope before trusting the branch diff. In practice:
    1. inspect `gh pr view <pr-number> --json files,commits` and note the exact intended file set
    2. compare that to `git diff --stat origin/main..origin/<pr-branch>`
    3. if the branch diff is much larger than the PR's intended file set, do not attempt a mechanical rebase or soft-reset squash
    4. create a fresh detached worktree from latest `origin/main`
    5. copy only the intended PR files from `origin/<pr-branch>` into the clean worktree
    6. run the narrowest relevant regression tests for just that scope
    7. commit once and force-push back to the same PR branch
  - This is especially useful when the open PR only intends a few route/test files, but the branch has accumulated unrelated stale diffs from earlier work or older main history. The GitHub PR file list can be a better statement of intended scope than the raw branch-vs-main diff.
  - Follow-on test-file guardrail from the same PR 255 maintenance: if one of the intended copied files is a broad repository structure test (for example `tests/redirect-endpoints.test.mjs`), do not assume the PR-branch copy is still valid on latest `origin/main` just because that file belongs to the intended scope.
    - After copying the intended test file onto latest main, compare it against `origin/main` immediately and inspect whether it reintroduces stale expectations unrelated to the PR's real behavior (for example asserting old redirect route files that latest main intentionally removed).
    - Safe recovery pattern:
      1. read the latest-main version of the test file
      2. keep the latest-main baseline assertions for unrelated route families
      3. reapply only the PR-specific assertions that prove the intended new behavior
      4. rerun the targeted tests before pushing
    - Heuristic: for latest-main rewrites, test files should usually be merged, not blindly copied wholesale, unless the PR truly owns the full current baseline of that test.
  - Important terminal state: after enough sibling PRs merge, an older PR's remaining intended diff may become fully absorbed by `origin/main`.
  - Before force-pushing a rebased/reconstructed branch, always check whether any unique commits or diff still remain:
    ```bash
    git rev-list --oneline origin/main..HEAD
    git diff --stat origin/main...HEAD
    ```
  - If both become effectively empty, the PR is no longer a meaningful review target. Pushing that branch to the exact latest `origin/main` tip can leave GitHub showing `no commit found on the pull request`, and the PR may effectively become a closed/empty historical shell rather than an active reviewable PR.
  - Practical outcome from real maintenance work: after force-pushing an open PR branch so its head exactly matches the latest base-branch tip, GitHub can stop treating it as an open review diff and `gh pr view` may start reporting the PR as `CLOSED`, with `gh pr checks` returning `no commit found on the pull request`.
  - In that situation, do not present the result as a normal successful PR update. Explicitly tell the user that the branch's content has already been absorbed by latest `main`, and that rebasing to main removes the PR's independent diff.
  - If the user still wants the branch mechanically aligned for bookkeeping, you can push it to the latest main tip, but call out that the PR will no longer behave like a normal open diff review and may appear closed/empty afterward.
  - If an earlier sibling PR from the same split series has already merged and its remote branch was deleted, do not depend on diffing against that deleted sibling branch name. Instead:
    - inspect the current PR file list with `gh pr view <pr-number> --json files --jq '.files[].path'`
    - inspect `git diff --stat origin/main...origin/<pr-branch>`
    - compare the latest-main versions of the overlapping files directly (`git show origin/main:<path>`)
    - infer the surviving unique scope by subtracting what is now already present on `origin/main`
  - In practice, this often means preserving latest-main content for sections already merged from a sibling PR, while rewriting `src/app/page.tsx` and related helpers/tests so only the current PR's still-unique route-local section remains.
  - Useful checks before rewriting in this situation:
    - `gh pr view <pr-number> --json files --jq '.files[].path'`
    - `git diff --stat origin/main...origin/<pr-branch>`
    - if there is a still-existing suspected parent/sibling branch, `git diff --stat origin/<older-pr-branch>..origin/<current-pr-branch>`
  - Useful reconstruction pattern:
    - copy over whole files whose latest intended state is clearly owned by the PR and not already on `main`
    - keep `src/app/page.tsx` or similar route files on latest-main shape, then patch only the minimal imports/sections needed for the PR's surviving scope
    - if an old shared container like `TopPageSections` still exists on main but the PR intends to inline/remove only part of it, decide explicitly whether that PR should still depend on the container or should remove it as part of the rewritten final state
  - After rewriting, compare both against `origin/main` and against the old PR branch so you can confirm the new diff kept the intended scope while dropping already-merged stale pieces.
  - Important practical guardrail from stale route-authoring PR work: do NOT try to "cleanly rebase" by taking the old PR worktree, staging your intended edits there, and then doing `git reset --soft origin/main`. On an old PR branch this can stage a huge mixed diff containing unrelated pre-main history plus later main-side changes, which is exactly what you are trying to avoid.
  - Safer pattern when the open PR branch is stale but the user wants the same PR rewritten on latest main:
    1. create a completely clean detached worktree directly from latest `origin/main`
    2. reapply or copy only the final intended file set for the PR's surviving scope
    3. verify there are no unrelated file changes in `git diff --stat`
    4. commit once on top of latest main
    5. push with `git push --force-with-lease origin HEAD:<pr-branch>`
  - Practical PR-cleanup pattern for `PR contains unrelated commits` follow-up:
    - First inspect `git rev-list --oneline origin/main..origin/<pr-branch>` and `git diff --stat origin/main...origin/<pr-branch>` to identify which commits/files are actually unrelated to the PR's intended scope.
    - Then create a fresh worktree from latest `origin/main` and do **not** branch-checkout the PR branch there if that branch name is already occupied by another local worktree.
    - Instead, use a temporary local branch name in the clean worktree (for example `pr205-rewrite`) and selectively copy only the intended paths from `origin/<pr-branch>` with `git checkout origin/<pr-branch> -- <paths...>`.
    - This is often faster and safer than rebasing a stale branch that has picked up unrelated commits from other topics.
    - After copying, verify again with `git diff --stat origin/main...HEAD` that only the intended scope remains, run validation, and then force-push the clean rewrite back to the original PR branch with `git push --force-with-lease origin HEAD:<pr-branch>`.
  - Additional practical rebase conflict pattern from PR 219 CI follow-up: when a one-commit open PR is rebased onto a newer `origin/main` and several files stop with conflict markers, it can be faster and safer to restore those conflicted files fully from `origin/main` first, then reapply only the PR's surviving scope on top, rather than hand-merging each conflict block.
    - Good candidates for this reset-and-reapply flow:
      - route files where latest main already contains major neighboring refactors
      - shared content files where the PR is supposed to delete one old content block entirely
      - structure tests where latest main already changed the canonical baseline and the PR only needs extra assertions for its surviving section scope
    - Practical sequence:
      1. `git checkout origin/main -- <conflicted-files>`
      2. reapply the PR's intended latest-main diff manually with file edits
      3. rerun narrow regression tests before `git rebase --continue`
    - This avoids preserving stale conflict-marker decisions from an older branch shape and is especially useful when the user asked for the PR to reflect the latest canonical refactor pattern, not just to replay history mechanically.
  - Fresh-worktree CI note from the same case: after conflict resolution in a newly created worktree, repo scripts like `npm run test:ci` can fail immediately with environment/setup issues such as `sh: eslint: command not found` because that worktree has no local install.
    - If the user prefers avoiding repeated installs in fresh worktrees, do not default to `npm install` just to satisfy a local CI wrapper.
    - Instead, run the narrowest meaningful regression tests already available in that worktree, push the fix, and use the repository CI rerun as the full verification path.
    - Still report clearly that the local `test:ci` wrapper was not runnable in that fresh worktree due to missing tooling, so the remaining confidence comes from targeted tests plus GitHub CI.
  - Additional stale-open-PR pattern from AI Crew PR 219 follow-up:
    - Sometimes the open PR has only one commit and looks simple, but latest `origin/main` has since absorbed adjacent sibling refactors that change the correct page section order and shared-shell boundaries.
    - In that case, a normal rebase can preserve the wrong final composition even if it applies cleanly.
    - Safer flow:
      1. inspect the live/latest-main section order and the open PR's target section scope
      2. create a clean worktree from latest `origin/main`
      3. reconstruct only the target section's final intended latest-main placement there
      4. run the narrow structure/regression tests that prove both route-local ownership and preserved order/CTA semantics
      5. force-push that clean rewrite back to the existing PR branch
    - This is especially useful when the user explicitly says the PR should be rewritten to match the repository's canonical refactor pattern rather than merely rebased mechanically.

- After a rewrite-on-main like this, re-check repository tests that assert source structure, not just runtime behavior. Structure-oriented tests may need helper updates when the user intentionally changes `page.tsx` from inline JSX to semantic section composition.
- Additional practical rebase pattern from PR 214 maintenance: when rebasing a stacked follow-up PR branch onto latest `origin/main`, the first implementation commit can conflict in structure-test helpers (for example `tests/helpers/static-marketing-page-sources.mjs`) because `main` has gained new sibling-section coverage since the PR branched. Resolve that first conflict by keeping the latest-main helper/test baseline and merging in the rebased PR's newly introduced section files/assertions together.
- Shared primitive/component rebase pattern from PR 217 maintenance: if the conflict is in a shared list/page primitive that both `main` and the PR extended in different ways, do not choose one side wholesale. Inspect the latest-main file and the PR-head file side by side, keep the latest-main API additions that other routes now depend on (for example a new `sidebarBasePath` prop or normalized sidebar key handling), then layer the PR-only feature hook-up on top (for example `initialVisibleCount` plus the conditional `ResourceListLoadMore` branch). After resolving, verify the rebased tree still preserves both behaviors: the new main-side compatibility path for existing callers and the PR-side behavior for the targeted routes.
- Shared type-contract drift pattern from the same PR 217 maintenance: after rebasing a PR that changed a broadly reused type or interface (for example adding `id` to a shared `ResourceItem` type), do not stop at the files that originally belonged to the PR. Latest `main` may now contain new helper layers, preview-item registries, or abstract repositories that were added after the PR branched and that still construct the old shape. CI and Vercel type-check failures can therefore surface in files the original PR never touched.
  Recommended recovery flow:
  1. inspect failed CI/build logs first rather than guessing from the original PR diff
  2. search for every constructor/mapper of the changed shared type across the fresh rebased worktree
  3. patch both data-driven mappers and handwritten preview/manual item arrays so they emit the new required field
  4. rerun the same repo-level validation the CI uses (`npm run test:ci`, and `npm run build` if preview deploy failed)
  5. only after the shared contract is fully restored should you squash/force-push the PR branch
  Practical example: adding `id` to `ResourceItem` required not only publication list mappers but also latest-main `src/lib/resources/base-resource-publication.ts` and `src/lib/resources/resource-preview-items.ts` to be updated before Verify/Vercel would pass.
- Important follow-on nuance from the same case: later follow-up commits in the same rebase can then conflict again in the same test file, but only because the test should reflect the repository state at that specific historical commit.
  - Example shape: commit 1 adds a new `why` section and its initial assertions; commit 2 changes only the `Before` card API; commit 3 changes only the `After` card API.
  - During rebase, if commit 2 stops on the already hand-merged test file, do **not** keep commit 3's assertions prematurely just because you know they will be added later. Instead, reduce the conflict to the test state that matches commit 2 only, continue the rebase, and let commit 3 add its own assertions in the next step.
  - Practical heuristic: at each stopped rebase commit, inspect the implementation files first and make the conflicted test describe exactly the code that currently exists in the tree at that step — no less, but also no future-state assertions from later commits.
  - This avoids accidentally making a follow-up commit empty for the wrong reason or hiding whether a later API-shape commit still replays correctly.
- Additional practical rebase pattern learned from PR follow-up work: sometimes an open PR branch contains several early "intermediate" commits that introduced a temporary helper or transitional architecture, while a later final commit on the same PR fully supersedes that intermediate path.
  - Typical signs:
    - rebasing onto latest `origin/main` stops first on an old early commit, not on the final intended commit
    - conflict files are the same surfaces later rewritten again on the PR branch
    - the old commit tries to revive deleted helper files or older prop/component shapes that the final PR state no longer uses
    - after skipping or dropping some early commits, only the final intended PR diff remains meaningful
  - In that case, do not spend time perfectly replaying each intermediate commit.
  - Prefer this recovery flow instead:
    1. inspect `git rev-list --oneline origin/main..origin/<pr-branch>` to see the full branch commit stack
    2. identify whether the early commits are transitional steps that are superseded by the PR branch tip
    3. create or keep a fresh worktree from latest `origin/main`
    4. copy the final intended file set directly from `origin/<pr-branch>` onto the latest-main worktree with `git checkout origin/<pr-branch> -- <paths...>`
    5. run the relevant verification
    6. squash the result to one clean commit on top of latest `origin/main`
    7. `git push --force-with-lease origin HEAD:<pr-branch>`
  - This is especially useful when a rebase leaves you with conflict churn from outdated helper-based commits but the user only cares about the final PR behavior on latest main.
  - Example shape from real work: an old PR first added a simple `/t` path helper, then refactored environment detection, then later replaced that whole approach with a cookie-based preview-mode toggle and server/client wrapper split. Replaying the old helper commits onto latest main produced noisy conflicts, but copying the final branch tip file set onto latest main yielded a clean and correct result.
  - Important guardrail: when you use this pattern, verify that the latest-main calling sites still match the final copied component API. If latest `main` has moved a callsite or prop contract since the old PR branched, make the smallest backward-compatible adjustment needed before pushing.
- In route-local/static-marketing refactor PRs, also rerun tests that read source files via helpers such as `tests/helpers/static-marketing-page-sources.mjs`; these helper-based tests are often what break after a rewrite-on-main because the source-of-truth path moves from shared content/container files to route-local section files.
- Practical single-file test-conflict pattern from AI Crew PR follow-up work: when rebasing a small one-commit PR onto newer `origin/main`, the only conflict can be a structure-oriented test file that latest `main` already expanded for a sibling section while the PR adds assertions for its own still-unique section behavior. In that case:
  1. read the conflicted test file, the latest-main implementation, and the PR's unique touched component/route files together
  2. keep the latest-main test setup/assertions that reflect already-merged sibling work
  3. add back only the current PR's still-unique assertions (for example new route-authored labels/aria text and negative assertions against the extracted section file)
  4. avoid reverting the test to either side wholesale just because only one file conflicted
  5. rerun the narrowest targeted tests before `rebase --continue`
- Common docs/memory conflict case: append-only markdown files such as `.hermes/memories/*.md` or skill `SKILL.md` files often conflict during rebase when both `main` and the PR added new bullets near the end of the same section.
  - Do not blindly take one side.
  - Read the conflict block and keep both sides' new entries unless one is a true duplicate.
  - Remove conflict markers, preserve the existing separator style (for example `§` lines in memory files), then continue the rebase.
  - This is especially important in `skills-jk`, where concurrent memory/skill updates are common and dropping one side silently loses durable knowledge.
- In stacked PR chains, `origin/main` may already contain one or more earlier sibling PR commits from the same series. Sometimes Git prints a clean `skipped previously applied commit <sha>` warning, but do not rely on that. It can also stop with normal content or add/add conflicts even when the current patch is logically already upstream, especially if `main` contains a later follow-up commit that edited the same files after the sibling PR merged.
- Before hand-merging, inspect `git rebase --show-current-patch` and the conflicted files. If the current patch is an already-upstream sibling change rather than this PR's unique change, prefer `git rebase --skip` instead of resolving the conflict manually.
- A practical signal for this case: the conflict appears in files changed by a previously merged sibling PR, the patch title/message belongs to that older PR topic, and the conflict markers show `HEAD`/`origin/main` already contains the newer desired shape of that feature while the replayed patch is trying to reintroduce the older version. This commonly happens when a feature PR was branched from another open PR and later rebased after the parent PR merged.
- If an early conflicted commit is resolved by manually rebuilding the branch into the final intended architecture, inspect later commits in the old PR before blindly replaying them. A later commit may only re-introduce an obsolete intermediate abstraction (for example a temporary wrapper or page-sections registry) that is no longer desired after the manual resolution.
- In that case, prefer this sequence:
  1. inspect the pending commit with `git show --stat <commit>`
  2. compare it against the already-resolved working tree and the user's final preferred structure
  3. if the pending commit is redundant or moves the code away from the desired end state, keep the current resolved files, remove any obsolete files it tries to revive, and use `git rebase --skip`
- Typical signal that skipping is correct: the pending commit mainly adds a now-unwanted intermediate abstraction layer while your current resolved tree already passes the intended structure and verification checks.
- In non-interactive agent environments, `git rebase --continue` may try to open Vim and hang. Prefer:
  ```bash
  GIT_EDITOR=true git rebase --continue
  ```
  after staging the resolved files.
- After force-pushing, verify both the remote branch tip and the PR head SHA. `gh pr view` can lag briefly right after the push, so confirm with both:
  ```bash
  git ls-remote origin refs/heads/<pr-branch>
  gh pr view <pr-number> --json headRefOid,updatedAt,url
  ```
  If they differ momentarily, wait a few seconds and re-check before concluding the push failed.
- Important stale-worktree lesson from PR 190 follow-up work: after a force-push/rewrite of an open PR branch, any older local worktree that still has the same branch checked out can be left behind at the pre-push commit and become misleadingly stale.
  - Do not assume the branch-named worktree is now at the rewritten remote tip.
  - Re-check with:
    ```bash
    git -C <old-worktree> rev-parse HEAD
    git rev-parse origin/<pr-branch>
    ```
  - If they differ, do not continue CI/debug follow-up in that old worktree. Create a fresh detached worktree directly from `origin/<pr-branch>` and continue there.
  - This is especially important after squash+force-push maintenance tasks, where the old local branch/worktree can remain on an orphaned pre-rewrite commit even though the PR itself is healthy.
- Additional local-ref drift lesson from PR 223 follow-up: if you pushed updates to the PR branch from a detached-HEAD worktree (`git push origin HEAD:<pr-branch>`), the remote PR branch moves but your ordinary local branch ref `refs/heads/<pr-branch>` may stay behind on its old commit stack.
  - Typical signal:
    ```bash
    git branch -vv
    git log --oneline --left-right <pr-branch>...origin/<pr-branch>
    ```
    shows the local branch both ahead and behind, even though the PR itself is healthy and the remote head is correct.
  - In that case, do not treat the divergence as a remote problem first. It can be just a stale local branch ref left behind by detached-HEAD pushes.
  - Safe recovery flow:
    ```bash
    git fetch origin --prune
    git branch backup/<topic>-stale <pr-branch>   # optional safety snapshot
    git branch -f <pr-branch> origin/<pr-branch>
    git branch --set-upstream-to=origin/<pr-branch> <pr-branch>
    ```
  - Verify with:
    ```bash
    git rev-parse <pr-branch>
    git rev-parse origin/<pr-branch>
    ```
    They should match afterward.
  - This is especially useful before starting another PR maintenance step such as squash/rebase, because otherwise you may accidentally inspect or reuse an obsolete local branch history instead of the actual PR head.
- Additional fresh-worktree sanity check from PR 233 follow-up: if a newly created follow-up worktree path is not recognized by Git (`fatal: not a git repository`) or only contains a partial subtree such as `tests/`, treat it as broken immediately.
  - Do not try to edit or run tests there.
  - Recovery flow:
    ```bash
    rm -rf <bad-worktree>
    git worktree prune
    git fetch origin --prune
    git worktree add <new-clean-path> origin/<pr-branch>
    git -C <new-clean-path> rev-parse --show-toplevel
    git -C <new-clean-path> status -sb
    find <new-clean-path> -maxdepth 2 | sed -n '1,30p'
    ```
  - Only continue after those checks show a real checkout root with normal repo contents.
- Additional stale-path recovery lesson from PR 240 follow-up: a path that previously worked as the active PR worktree can later disappear or become unusable between turns (for example after earlier rewrite/squash maintenance), and a local branch with the same PR name may still exist but be stale/ahead-behind relative to the remote PR branch.
  - Typical signal:
    - `cd <old-worktree>` or any command using that absolute path fails with `No such file or directory`
    - `git worktree list` no longer contains the expected active path
    - an older local branch for the PR still exists, but `git branch -vv` shows it is diverged from `origin/<pr-branch>`
  - In that case, do not continue from the stale local branch or try to recreate history there.
  - First re-check the live environment:
    ```bash
    pwd
    git rev-parse --show-toplevel
    git worktree list --porcelain
    git branch -vv | sed -n '1,40p'
    ```
  - Then create a fresh detached worktree directly from the remote PR tip and reapply only the final intended local delta there:
    ```bash
    git fetch origin --prune
    git worktree add -f <new-clean-path> origin/<pr-branch>
    git -C <new-clean-path> status -sb
    ```
  - This is especially useful when the requested follow-up is a very small change (for example one typography or spacing adjustment): just reapply that tiny final diff, rerun the narrow validation, and push with `git push origin HEAD:<pr-branch>` from the fresh detached worktree.
  - Practical rule: when the active PR worktree path fails unexpectedly, re-discover the real current checkout before any commit/push step; do not assume the last successful worktree path is still valid.

### 7. Re-check the PR and CI
```bash
gh pr view <pr-number> --json number,headRefName,updatedAt,commits
gh pr checks <pr-number>
```

Important practical note:
- `gh pr checks <pr-number>` returns a non-zero exit code not only for hard failures, but also while checks are still pending.
- Immediately after a force-push/rebase update, it can also briefly print `no checks reported on the '<branch>' branch` before GitHub attaches the new workflow runs to the PR head.
- Do not treat either the non-zero exit or that temporary `no checks reported` message as proof that your branch update failed.
- First confirm the new head landed with `gh pr view <pr-number> --json headRefOid,updatedAt,url` and/or `git ls-remote origin refs/heads/<pr-branch>`.
- Then rerun `gh pr checks <pr-number>` after a short wait and classify the resulting checks as `pass`, `pending`, or `fail`.
- Additional practical recovery from corp-web-japan PR 259: sometimes the PR head SHA updates successfully, but GitHub never attaches fresh `pull_request` runs for the new head (`gh pr checks` keeps saying `no checks reported on the '<branch>' branch`, and querying check-runs/actions by the new head SHA returns zero results).
- In that case, do not assume the code fix failed. Treat it as a workflow-trigger problem first.
- Recovery flow:
  1. confirm the remote PR branch tip and PR `headRefOid` match your pushed SHA
  2. inspect the relevant workflow files for `workflow_dispatch` support (for example `ci.yml`, preview-deploy workflow)
  3. if dispatch is available, manually run the workflows on the PR branch head, e.g.
     ```bash
     gh workflow run ci.yml --ref <pr-branch>
     gh workflow run deploy-preview.yml --ref <pr-branch> -f BRANCH=<pr-branch>
     ```
  4. watch those dispatched runs and use them as the validation result for the current head
- This is especially useful when you already reproduced the original failure locally, fixed it, and local verification passes, but GitHub's automatic synchronize event appears to be dropped or delayed.

Confirm:
- the PR still points to the intended branch
- the latest commit on the PR matches your pushed commit
- CI has started for the new head

## Anti-patterns to avoid

### Wrong: create a new PR for review follow-up
This splits one review cycle across multiple PRs.

### Wrong: keep working in an old unrelated worktree
This risks mixing stale local history into the PR.

### Wrong: start from a fresh branch off main for a PR fix
Unless explicitly requested, this creates unnecessary cherry-picking or duplicate PRs.

## Success criteria
- A fresh worktree was used
- The existing PR branch was updated directly
- No extra PR was created
- The new commit is visible on the original PR
- CI re-ran on the original PR

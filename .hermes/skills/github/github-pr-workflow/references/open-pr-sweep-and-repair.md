# Open PR sweep and repair pattern

Use this when a user asks to check/fix open PRs, or when frustration indicates an earlier response only handled one or two PRs instead of the open PR set.

Core expectation:
- Treat it as a full open-PR sweep, not a single-PR follow-up.
- Inspect every open PR for both check failures and mergeability.
- Continue fixing/rebasing/pushing until every relevant PR is CLEAN/pass, or report explicit blockers.

Workflow:
1. List open PRs:
   `gh pr list --state open --json number,title,headRefName,baseRefName,mergeStateStatus,isDraft,url`
2. For each PR, inspect both:
   - `gh pr checks <number> --watch=false`
   - `gh pr view <number> --json mergeStateStatus,headRefOid,headRefName,isDraft,url`
3. Classify problems:
   - failing checks: read the failed job logs and fix root cause
   - pending checks: monitor new-head runs unless the user asked not to wait
   - `DIRTY`: rebase/merge-conflict repair is required even if checks are green
   - `BLOCKED`: often pending required checks; verify whether it becomes CLEAN after checks pass
4. Use repo-local worktrees for branch repair. Rebase onto latest `origin/main` and resolve conflicts by preserving latest-main changes plus the PR's intended net diff.
5. Push updates:
   - normal push for new commits on top
   - `git push --force-with-lease origin HEAD:<branch>` after rebase
6. After every push or force-push, verify the pushed branch tip and PR head SHA match:
   - `git rev-parse HEAD origin/<branch>`
   - `gh pr view <number> --json headRefOid,statusCheckRollup`
7. Monitor only checks for the new head SHA. Old runs may be cancelled or stale after force-push.
8. Final report should enumerate every open PR checked, its merge state, and pass/fail/pending status.

Source-based CI test pitfall seen in this class of work:
- If a source-based test intends to ban mutable Docker image tags like `outbound-front:latest`, do not assert that the whole workflow source lacks the string `latest`; GitHub runner labels such as `ubuntu-latest` are legitimate.
- Prefer targeted assertions such as `not.toMatch(/outbound-front:latest\b/)` and, if relevant, `not.toContain('image_tag="latest"')`.

Session example summary:
- Several PRs had checks passing except one `DIRTY` merge state; the correct completion condition was not just fixing failed checks, but rebasing that PR until mergeStateStatus became CLEAN and CI passed again.
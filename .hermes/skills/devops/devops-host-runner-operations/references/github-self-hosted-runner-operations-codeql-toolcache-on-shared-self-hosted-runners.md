# CodeQL toolcache on shared self-hosted runners

Use this reference when investigating whether `_work/_tool/CodeQL` can be deleted from self-hosted runners.

## Key lesson

A repository-local CodeQL workflow being disabled does not prove the runner-local CodeQL cache is unused. The same self-hosted runner pool may execute CodeQL workflows for other repositories that share labels such as `self-hosted, querypie`.

Treat `_work/_tool/CodeQL` as runner-local, reusable, and safe to regenerate, but not necessarily obsolete.

## Investigation pattern

1. Check the target repository workflow definition.
   - Search `.github/workflows/**` for `github/codeql-action/init`, `github/codeql-action/analyze`, `github/codeql-action/upload-sarif`, `CodeQL`, and `codeql`.
   - Confirm triggers, especially whether `schedule` is active or commented out and whether only `workflow_dispatch` remains.
2. Check the target repository run history.
   - `gh run list --repo OWNER/REPO --workflow codeql.yml --limit 30 --json databaseId,workflowName,event,status,conclusion,createdAt,url`
   - If the latest runs are old and `schedule` is disabled, the target repo itself is likely not refreshing the cache.
3. Inspect a recent CodeQL run's job runner metadata.
   - `gh api repos/OWNER/REPO/actions/runs/RUN_ID/jobs --jq '.jobs[] | [.name,.conclusion,.runner_name,([.labels[]?]|join(",")),.started_at,.completed_at] | @tsv'`
   - Distinguish GitHub-hosted runners (`ubuntu-latest`, runner name like `GitHub Actions ...`) from self-hosted runner names.
4. Search runner-local state.
   - On each runner, check for active processes: `ps -eo pid,ppid,lstart,etime,cmd | grep -Ei '[c]odeql|[g]ithub/codeql|[c]odeql-action'`.
   - List CodeQL toolcache versions: `du -sh "$RUNNER/_work/_tool/CodeQL"; find "$RUNNER/_work/_tool/CodeQL" -mindepth 1 -maxdepth 1 -type d -printf '%TY-%Tm-%Td %TH:%TM\t%p\n' | sort -r`.
   - Look for repo workspaces and failed SARIF artifacts: `find "$RUNNER/_work" -maxdepth 6 \( -iname '*codeql*' -o -iname '*.ql' -o -iname '*.qls' \) -printf '%TY-%Tm-%Td %TH:%TM\t%p\n' | sort -r | head`.
5. Check likely sibling repositories sharing the same runner label.
   - In the observed QueryPie case, `querypie-mono` CodeQL was no longer scheduled, but other repositories such as `querypie-common`, `commandpie-engine`, `querypie-engine-backend`, `querypie-aws-credentials`, and `PgQuery.Net` still had scheduled CodeQL workflows using `self-hosted, querypie` runners.

## Interpretation

- No active `codeql` process means it is not currently running, but does not mean the cache is obsolete.
- Recent `_work/_tool/CodeQL/<version>` mtimes can be caused by other repositories, not the repository currently being audited.
- `codeql-failed-run.sarif` under a runner workspace is evidence that some CodeQL workflow used that runner, but it may belong to a different repository.
- CodeQL cache is safe to delete from a correctness perspective because `github/codeql-action` can download it again. The trade-off is slower future CodeQL runs and repeated downloads.

## Recommended cleanup policy

Prefer version pruning over full deletion when any shared-runner CodeQL usage still exists:

- Keep latest 1-2 CodeQL versions per runner.
- Delete older `_work/_tool/CodeQL/<version>` directories only when the runner is idle.
- For very large runners, prioritize hosts with many historical CodeQL versions (for example a runner with 10+ CodeQL versions and tens of GB under `_work/_tool/CodeQL`).
- Full deletion of `_work/_tool/CodeQL` is acceptable only if the owner accepts the next-run download cost, or after confirming no repo using that runner label still schedules CodeQL.

## Safe cleanup sketch

```bash
TOOL="$RUNNER/_work/_tool/CodeQL"
keep=2
find "$TOOL" -mindepth 1 -maxdepth 1 -type d -printf '%T@ %p\n' |
  sort -nr |
  awk -v keep="$keep" 'NR > keep { sub(/^[^ ]+ /, ""); print }' |
  while IFS= read -r d; do
    echo "rm -rf $d"   # dry-run first
  done
```

Run deletion only after replacing `echo` with `rm -rf` intentionally and after checking runner idle state.

# Scheduled runner cleanup label bootstrap pattern

Use this when a scheduled self-hosted runner maintenance workflow needs exact-runner custom labels such as `runner:<runner-name>` to exist before the cleanup job can safely target or verify runners.

## Pattern

1. Keep the label provisioning workflow separate and manual-dispatchable.
   - Example file name: `.github/workflows/ensure-runner-name-labels.yaml`.
   - It should list org self-hosted runners and add `runner:<runner.name>` only when missing.
   - It needs a secret with org self-hosted runner write permission, e.g. `ORG_RUNNER_WRITABLE_TOKEN`.
2. In the scheduled cleanup workflow, add a schedule-only bootstrap job before cleanup.
   - Grant `actions: write` so the workflow can dispatch another workflow with `github.token`.
   - Use `gh workflow run <workflow-file> --ref "$GITHUB_REF_NAME"`.
   - Find the dispatched run created after the current UTC timestamp and watch it with `gh run watch --exit-status`.
3. Gate cleanup on the bootstrap job only for scheduled runs.
   - Manual `workflow_dispatch` should not be blocked by a skipped bootstrap job.
   - Use a cleanup `if` similar to:

```yaml
needs: [ensure-runner-name-labels]
if: ${{ always() && (github.event_name != 'schedule' || needs.ensure-runner-name-labels.result == 'success') }}
```

4. If a notify job should alert on bootstrap failure as well as cleanup failure, include both dependencies:

```yaml
needs: [ensure-runner-name-labels, cleanup]
if: failure()
```

## Implementation notes

- GitHub's default `GITHUB_TOKEN` cannot modify org runner labels directly, but it can dispatch another workflow when `permissions.actions: write` is granted.
- The dispatched label workflow must already exist on the selected ref. For default-branch schedules, merge the label workflow PR before the cleanup workflow PR or document that dependency clearly.
- For `gh api --jq` filters containing jq variables like `$runner`, avoid single-quoted embedded scripts if actionlint/shellcheck flags SC2016. A compact double-quoted jq filter with escaped `$` variables is actionlint-friendly:

```bash
gh api "/orgs/${ORG}/actions/runners?per_page=100" --paginate --jq \
  ".runners[] as \$runner | select([\$runner.labels[].name] | index(\"runner:\" + \$runner.name) | not) | [\$runner.id, \$runner.name] | @tsv"
```

## Verification

- Run the repository's actionlint-backed check, e.g. `MISE_TRUSTED_CONFIG_PATHS="$PWD" mise r check -o quiet -f`.
- Verify the PR has only the intended workflow/script files after squashing.
- Verify latest workflow runs are attached to the rewritten PR head SHA after force-push.

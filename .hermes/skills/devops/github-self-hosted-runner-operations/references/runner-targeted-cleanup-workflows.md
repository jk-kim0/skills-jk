# Runner-targeted cleanup workflows

Use this when implementing a GitHub Actions maintenance workflow that must clean self-hosted runner-local caches on one specific runner or across a runner fleet.

## Key GitHub Actions constraint

GitHub Actions does not automatically expose the runner name as a schedulable label. A workflow cannot reliably target `SVR-L2-RUNNER-1` by runner name alone.

To route a job to one exact runner, add a unique custom label to that runner, for example:

- `runner:SVR-L2-RUNNER-1`
- `runner:SVR-L3-RUNNER-2`

Then use `runs-on` with the normal platform labels plus that custom runner label.

Example:

```yaml
runs-on: [self-hosted, Linux, X64, os:ubuntu, arch:amd64, runner:SVR-L2-RUNNER-1]
```

For ARM64 Linux runners, include the GitHub default architecture label and the org's arch label:

```yaml
runs-on: [self-hosted, Linux, ARM64, os:ubuntu, arch:arm64, runner:SVR-MS-ARM-RUNNER-1]
```

## Recommended workflow shape

Keep the workflow as a thin wrapper and put cleanup logic in a sibling script under `.github/workflows/`.

Useful dispatch modes:

1. `single`
   - User selects a `target_runner` from a choice list.
   - A prepare job emits a 1-entry matrix with `runs_on` containing `runner:<target_runner>`.
2. `all`
   - A prepare job emits a matrix with every supported runner and its unique label.
   - Use `strategy.fail-fast: false` so one bad/offline runner does not hide other results.
3. `labels`
   - Backward-compatible/manual fallback: accept a JSON array of labels and run one job against that label pool.
   - Do not assert a specific runner name in this mode.

## Dynamic matrix builder rationale

For workflows that support `single`, `selected`, `all`, and fallback `labels` modes, use a small script step (Python is a good default) to emit the `strategy.matrix` JSON via `$GITHUB_OUTPUT`. This is not cleanup logic; it is routing glue that translates user-facing runner names into schedulable `runs-on` label arrays.

The builder should:

- Keep a canonical runner inventory of `(runner_name, github_arch, custom_labels)`.
- Include both GitHub default platform labels such as `self-hosted`, `Linux`, `X64`/`ARM64` and org-specific labels such as `os:ubuntu`, `arch:amd64`/`arch:arm64`, and `runner:<name>`.
- Parse `selected` mode from comma/newline text or a JSON array, reject unknown names, preserve user order, and deduplicate repeated names.
- Emit matrix rows with `runner_name`, `expected_runner_name`, and `runs_on`.
- Leave `expected_runner_name` empty for generic `labels` mode, because that mode intentionally does not pin a specific runner instance.

Important maintenance pitfall: if the workflow UI also has a `workflow_dispatch.inputs.target_runner.options` choice list, it duplicates the runner inventory. Update the UI options and the matrix builder inventory together; otherwise a runner can be selectable but rejected as unknown, or known to the script but impossible to select from the UI.

## Safety guard inside the script

When `single`, `selected`, or `all` targets a specific runner, pass the expected runner name to the script and verify it before deletion:

```bash
TARGET_RUNNER_NAME="${TARGET_RUNNER_NAME:-}"

if [[ -n "$TARGET_RUNNER_NAME" && "${RUNNER_NAME:-}" != "$TARGET_RUNNER_NAME" ]]; then
  echo "expected runner=$TARGET_RUNNER_NAME but actual runner=${RUNNER_NAME:-unknown}; refusing cleanup"
  exit 1
fi
```

This catches missing/misapplied custom labels before any destructive cache cleanup runs.

## Cache cleanup defaults that preserve runner function

For querypie-mono-style Linux self-hosted runners, safe cleanup defaults are:

- `_work/_temp`: delete entries older than a minimum age, e.g. 24h.
- `_diag`: delete old diagnostic logs, e.g. older than 14 days.
- `_work/_update`: remove stale runner update staging.
- inactive `bin.*` / `externals.*`: remove only directories that are not current symlink targets.
- `_work/_tool`: prune by tool family; keep the newest N versions for frequently used tools.
- CodeQL: prefer version pruning rather than full removal when the runner pool may be shared by other repos.
- Docker: prune only unused build cache/images/containers/networks with an age filter, e.g. `until=24h`.
- Old workspaces: keep off by default; enable only via explicit input because deleting workspaces is more disruptive.

## Ensuring runner-name labels from a repo workflow

If the repository has a secret containing an org-level runner-write token, a small manual workflow can keep `runner:<runner-name>` labels present without hand-editing every runner.

Recommended naming:

- Workflow file: `.github/workflows/ensure-runner-name-labels.yaml`
- Workflow display name: `Ensure Runner Name Labels`
- Secret name used in querypie-mono: `ORG_RUNNER_WRITABLE_TOKEN`

Keep the workflow read-only with respect to repository contents and avoid checkout. The default `GITHUB_TOKEN` does not need permissions; use the org runner token only for `gh api` calls:

```yaml
name: Ensure Runner Name Labels

on:
  workflow_dispatch:

permissions: {}

jobs:
  sync:
    name: Add runner:<name> labels
    runs-on: ubuntu-latest
    steps:
      - name: Add missing runner name labels
        env:
          GH_TOKEN: ${{ secrets.ORG_RUNNER_WRITABLE_TOKEN }}
          ORG: chequer-io
        run: |
          set -euo pipefail

          gh api "/orgs/${ORG}/actions/runners?per_page=100" --paginate --jq \
            ".runners[] as \$runner | select([\$runner.labels[].name] | index(\"runner:\" + \$runner.name) | not) | [\$runner.id, \$runner.name] | @tsv" |
            while IFS=$'\t' read -r runner_id runner_name; do
              label="runner:${runner_name}"
              echo "Adding ${label} to ${runner_name} (${runner_id})"
              gh api -X POST "/orgs/${ORG}/actions/runners/${runner_id}/labels" -f labels[]="${label}" >/dev/null
            done
```

Actionlint/shellcheck pitfall:

- A multi-line single-quoted jq filter containing jq variables such as `$runner` can trigger ShellCheck `SC2016` inside actionlint: “Expressions don't expand in single quotes”.
- Prefer a double-quoted one-line jq filter and escape jq variables as `\$runner`; this keeps actionlint green while preserving jq variable semantics.
- Verify with the repo's lint command when available, e.g. `MISE_TRUSTED_CONFIG_PATHS="$PWD" mise r check -o quiet -f`.

## PR/body wording pitfall

Be explicit that `single`/`all` modes require per-runner custom labels. Otherwise reviewers may assume runner names are directly targetable by GitHub Actions and merge a workflow whose jobs never get scheduled on the intended runner.

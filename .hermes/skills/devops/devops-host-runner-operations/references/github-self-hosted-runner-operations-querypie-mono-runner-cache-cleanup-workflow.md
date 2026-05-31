# querypie-mono self-hosted runner cache cleanup workflow

Use this reference when adding or maintaining repository-managed cleanup workflows for QueryPie self-hosted GitHub Actions runners.

## Current desired workflow shape

Repository facts:

- Default/base branch: `develop`.
- Workflow file: `.github/workflows/clean-up-self-hosted-runner-cache.yaml`.
- Cleanup script: `.github/workflows/cleanup-runner-cache.sh`.
- Workflow display name: `Clean Up Self-hosted Runner Cache`.
- Workflow run name: `🧹 Clean Up Self-hosted Runner Cache`.
- Schedule: Saturday 02:00 KST / Friday 17:00 UTC: `0 17 * * 5`.

Name convention:

- Prefer a verb-first operation name for maintenance workflows: `Clean Up ...`.
- Keep file name, `name`, and `run-name` semantically aligned.
- Put the broom emoji in `run-name` rather than `name` when the user wants the run list to sort lower while keeping workflow list text clean.

## Runner targeting model

Assumption:

- Every target self-hosted runner already has a custom label shaped `runner:<runner-name>`.
- The separate label sync workflow can provision these labels; this cleanup workflow should not try to mutate labels.

Manual dispatch:

- Use a single `runner_names` input as a JSON array.
- One runner example: `["SVR-L2-RUNNER-1"]`.
- Many runners example: `["SVR-L2-RUNNER-1","SVR-L2-RUNNER-2"]`.
- Default manual run should stay conservative, e.g. one runner and `dry_run=true`.

Schedule:

- Scheduled events do not have `github.event.inputs`; do not assume workflow_dispatch defaults apply to schedule.
- Use a `resolve-runners` job to explicitly select runner names by event type:
  - `workflow_dispatch` -> output the operator-provided `runner_names` input.
  - `schedule` -> output the full known Linux runner list.
- Keep the scheduled runner inventory legible: one runner name per line in a heredoc, then convert it to a JSON array with `jq -Rcn '[inputs | select(length > 0)]'`. Do not hide the whole schedule inventory in one long JSON string.
- Validate the resolved JSON with `jq -e 'type == "array" and length > 0 and all(.[]; type == "string" and length > 0)'` before exporting to `GITHUB_OUTPUT`.
- The cleanup job should consume `fromJSON(needs.resolve-runners.outputs.runner_names)` as its matrix.

Cleanup matrix:

```yaml
jobs:
  resolve-runners:
    outputs:
      runner_names: ${{ steps.resolve.outputs.runner_names }}
    steps:
      - id: resolve
        env:
          INPUT_RUNNER_NAMES: ${{ github.event.inputs.runner_names || '' }}
        run: |
          set -euo pipefail

          schedule_runner_names_json() {
            jq -Rcn '[inputs | select(length > 0)]' <<'EOF'
          SVR-L2-RUNNER-1
          SVR-L2-RUNNER-2
          SVR-L2-RUNNER-3
          EOF
          }

          if [[ -n "${INPUT_RUNNER_NAMES}" ]]; then
            runner_names="${INPUT_RUNNER_NAMES}"
          else
            runner_names="$(schedule_runner_names_json)"
          fi
          echo "${runner_names}" | jq -e 'type == "array" and length > 0 and all(.[]; type == "string" and length > 0)' >/dev/null
          echo "runner_names=${runner_names}" >>"${GITHUB_OUTPUT}"

  cleanup:
    needs: [resolve-runners]
    runs-on: ["self-hosted", "runner:${{ matrix.runner_name }}"]
    strategy:
      fail-fast: false
      matrix:
        runner_name: ${{ fromJSON(needs.resolve-runners.outputs.runner_names) }}
```

Important `jq` detail: use `-Rcn`, not `-Rcns`; `-s` slurps the heredoc into one newline-containing string instead of one array element per runner line.

Do not keep the older label-pool model in this workflow:

- No `runner_labels` input.
- No `runs-on: ${{ fromJSON(github.event.inputs.runner_labels || '["self-hosted","Linux"]') }}`.
- No in-script `TARGET_RUNNER_NAME` / `RUNNER_NAME` mismatch guard. With exact `runner:<name>` labels, GitHub's scheduler is the targeting mechanism.

## Cleanup behavior

Keep destructive knobs out of the manual UI:

- Default `workflow_dispatch` to dry-run.
- Do not expose Docker cleanup as an input.
- Do not expose retention/pruning knobs as workflow_dispatch options.
- Keep retention as script constants/env defaults:
  - `_work/_temp`: 8 days / 192 hours.
  - `_diag`: 14 days.
  - Docker prune: 72 hours / 3 days, only when auto-allowed.
  - non-CodeQL toolcache families (`go`, `node`, Java, Python, `uv`): keep latest 5 versions.
  - CodeQL: keep latest 1 version.
  - workspace checkout cleanup: off by default.

Docker cleanup rules:

- Docker prune is host-wide; skip it on containerized/shared-daemon runners.
- Auto-skip when container markers are detected (`/.dockerenv`, `/run/.containerenv`, cgroup markers such as docker/containerd/kubepods/libpod/podman).
- Auto-skip known shared/container fleets:
  - `SVR-L3-DOCKERIZED-RUNNER-*`
  - `SVR-L3-MINI-DOCKERIZED-RUNNER-*`
  - `SVR-MS-ARM-RUNNER-*`
- Allow only known native VM runners:
  - `SVR-L2-RUNNER-1..6`
  - `SVR-L3-RUNNER-1..2`

## Verification checklist

Run before pushing:

```bash
bash -n .github/workflows/cleanup-runner-cache.sh
python3 - <<'PY'
import yaml
with open('.github/workflows/clean-up-self-hosted-runner-cache.yaml') as f:
    data = yaml.safe_load(f)
assert data['name'] == 'Clean Up Self-hosted Runner Cache'
assert data['run-name'] == '🧹 Clean Up Self-hosted Runner Cache'
assert 'resolve-runners' in data['jobs']
print('workflow yaml ok')
PY
MISE_TRUSTED_CONFIG_PATHS="$PWD" mise r check -o quiet -f
```

Also grep touched workflow files and PR text for stale wording before reporting done:

- `24h` / `24시간`
- `runner_labels`
- `label pool`
- `TARGET_RUNNER_NAME`
- `runner mismatch`
- old filename `runner-cache-cleanup.yaml`
- old titles such as `Self-hosted Runner Cache Cleanup` if the agreed name is `Clean Up Self-hosted Runner Cache`

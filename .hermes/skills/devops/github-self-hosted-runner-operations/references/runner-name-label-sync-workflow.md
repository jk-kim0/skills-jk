# Runner name label sync workflow

Use this pattern when a repository needs GitHub Actions jobs to target a specific self-hosted runner by name.

## Why

GitHub Actions cannot schedule a job by runner name directly. To target one runner, the runner name must also exist as a custom label, commonly:

```text
runner:<RUNNER_NAME>
```

Then a workflow can use:

```yaml
runs-on: [self-hosted, runner:SVR-L2-RUNNER-1]
```

## Minimal repository workflow

When the repository has a secret containing a token with organization self-hosted runner write permission, add a small manual workflow like this:

```yaml
name: Sync Runner Name Labels

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

          gh api "/orgs/${ORG}/actions/runners?per_page=100" --paginate --jq '
            .runners[] as $runner
            | select([$runner.labels[].name] | index("runner:" + $runner.name) | not)
            | [$runner.id, $runner.name]
            | @tsv
          ' | while IFS=$'\t' read -r runner_id runner_name; do
            label="runner:${runner_name}"
            echo "Adding ${label} to ${runner_name} (${runner_id})"
            gh api -X POST "/orgs/${ORG}/actions/runners/${runner_id}/labels" -f labels[]="${label}" >/dev/null
          done
```

## Token permissions

`GITHUB_TOKEN` is not sufficient for organization runner label mutation. Use a fine-grained PAT or GitHub App installation token with organization permission:

- `Self-hosted runners`: `Read and write`

A classic PAT fallback generally needs `admin:org`, which is broader and less preferred.

Store it as a repository or organization Actions secret, for example:

```text
ORG_RUNNER_WRITABLE_TOKEN
```

## Verification

Before committing, verify the jq expression against the live runner API using a human/admin `gh` auth context:

```sh
gh api "/orgs/chequer-io/actions/runners?per_page=100" --paginate --jq '
  .runners[] as $runner
  | select([$runner.labels[].name] | index("runner:" + $runner.name) | not)
  | [$runner.id, $runner.name]
  | @tsv
' | sed -n '1,20p'
```

Also run a YAML parse if available.

## Pitfall: jq context inside `select`

Do not write this shape:

```jq
.runners[]
| select([.labels[].name] | index("runner:" + .name) | not)
```

Inside the `index(...)` expression, `.` is the label-name array, not the runner object, so `.name` is wrong and `gh --jq` can fail with an error such as `expected an object but got: array`. Bind the runner first:

```jq
.runners[] as $runner
| select([$runner.labels[].name] | index("runner:" + $runner.name) | not)
```

## Safety notes

- Use `POST /labels` to add missing custom labels without replacing existing custom labels.
- Avoid `PUT /labels` unless you intentionally want to replace the runner's custom-label set.
- Keep `permissions: {}` because the workflow uses only the secret token, not repository `GITHUB_TOKEN` permissions.

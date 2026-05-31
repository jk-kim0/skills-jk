# QueryPie org `gh-runners` CLI pattern

Use this when implementing or reviewing a repo-local CLI that mirrors a known-good runner inventory script for the QueryPie organization.

## Goal

Provide a local `gh-runners` command that:
- defaults to `querypie` as the org
- lists org self-hosted runners in summarized / extended / JSON forms
- optionally resolves which workflow job is currently occupying each busy runner
- works with standard Python only (`urllib`, `json`, `argparse`, `subprocess`)

## Proven implementation shape

Source inspiration: `querypie-mono/scripts/gh-runners`.

Recommended repo-local shape:
- executable CLI at `bin/gh-runners`
- parser flags:
  - `--summarized`
  - `--extended`
  - `--show-labels`
  - `--json`
  - `--org <org>`
  - `--busy-repo <owner/repo>` repeatable
  - `--no-busy-jobs`
- token resolution order:
  1. `GITHUB_TOKEN`
  2. `GH_TOKEN`
  3. `gh auth token`

## API calls

Runner inventory:
- `GET /orgs/<org>/actions/runners?per_page=100`
- handle pagination from the HTTP `Link` header

Automatic busy-job repo scan seed:
- `GET /orgs/<org>/repos?type=all&per_page=100`
- skip `archived=true`
- skip `disabled=true`
- use `full_name`

Busy-job lookup for each repo:
- `GET /repos/<owner>/<repo>/actions/runs?status=in_progress&per_page=100`
- `GET /repos/<owner>/<repo>/actions/runs?status=queued&per_page=100`
- for each run: `GET /repos/<owner>/<repo>/actions/runs/<run_id>/jobs?filter=latest&per_page=100`
- match `job.runner_name` to busy runner names
- only treat jobs with `job.status == "in_progress"` as the active occupant

Useful fields to emit for matched busy jobs:
- `workflow_name`
- `job_name`
- `repo` (short name is enough in tables)
- `branch`
- `pr_number`
- `display_title`
- `event`
- `actor`
- `elapsed`
- `job_url`
- `run_url`

## QueryPie-specific observed behavior

Observed against the live QueryPie org during implementation:
- `GET /orgs/querypie/actions/runners` returned 6 Linux ARM64 runners.
- A narrow scan of only `querypie/querypie-mono` and `querypie/querypie-docs` found 0 active jobs for 6 busy runners, so those repos alone were insufficient.
- Auto-scanning all non-archived QueryPie repos found 4 active jobs out of 6 busy runners, all in `corp-web-app`; 2 runners still remained unmatched.

Interpretation:
- defaulting to a small hard-coded repo list is too brittle for QueryPie org-wide status tools
- default behavior should prefer org repo auto-discovery
- unmatched busy runners are normal; report them as unmatched instead of treating the lookup as failed

Recommended stderr messaging:
- before scan: `Scanning <N> repo(s) for <M> busy runner job(s)...`
- partial match: `Found <X> job(s), <Y> runner(s) not matched (may be in workflows not covered by the repo scan)`

## Verification pattern

Static verification:
- targeted pytest for parser, repo normalization, table formatting, and JSON/main flow
- `python3 -m py_compile bin/gh-runners tests/test_gh_runners.py`

Live verification:
- `python3 bin/gh-runners --summarized`
- `python3 bin/gh-runners --json --no-busy-jobs`
- optional narrow scan sanity check:
  - `python3 bin/gh-runners --summarized --busy-repo querypie/querypie-mono --busy-repo querypie/querypie-docs`

## Pitfalls

- Do not assume a small historical busy-repo allowlist still covers current runner usage; QueryPie runner occupancy can shift to a different active repo family such as `corp-web-app`.
- When a narrow `--busy-repo` scan finds zero matches for clearly busy runners, treat that as a scope miss, not proof that the busy-job lookup logic is broken.
- For JSON validation commands, avoid piping producer output straight into an inline Python heredoc reader in a way that can trigger broken-pipe / empty-stdin confusion; writing JSON to a temp file first is more reliable for verification.

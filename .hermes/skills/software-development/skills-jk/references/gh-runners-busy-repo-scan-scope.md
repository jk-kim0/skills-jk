# gh-runners busy-job scan scope

Use this reference when maintaining `bin/gh-runners`, especially when the command becomes slow while resolving which workflow job is occupying busy self-hosted runners.

## Durable pattern

`bin/gh-runners` can list organization self-hosted runners quickly, but resolving busy runner jobs is expensive if it scans every repository in the organization. For routine use, keep the default scan bounded to the repositories most likely to consume the runners, and provide an explicit full-scan escape hatch.

Current `skills-jk` pattern:

- Default busy-job scan targets the top runner-usage repositories rather than all org repos.
- `--busy-repo` remains the precise override for a known target repository.
- `--scan-all-repos` remains the explicit fallback when the bounded default misses a job or a broad audit is needed.
- JSON output should include the actual `busy_job_scan_repos` list so callers can see what was covered.

## How to choose the default repo set

Use recent GitHub Actions run/job metadata, not intuition alone:

1. List active non-archived org repositories.
2. For each repo, sample recent workflow runs, then sample jobs for the most recent runs.
3. Rank repositories by recent self-hosted runner job volume first, with recent run count and latest activity as tie-breakers.
4. Keep the default list small enough for interactive use. In the 2026-06-10 scan, five repos reduced the default from 18 repo scans to 5 while still covering the normal busy-runner workload.
5. Document the sample date and ranking basis near the constant or in README so future maintainers know it is an operational default, not a universal truth.

## Output readability pitfall

GitHub job metadata can contain long PR titles or, for some workflow names, body-like strings. Table columns can become unreadably wide if those values are printed unbounded. Truncate display-only workflow/job/title fields while preserving full job/run URLs in the detail section.

## Verification checklist

- Unit tests prove that the default path does not call the full org repository listing.
- Unit tests cover the default repo list and `--scan-all-repos` behavior.
- `python3 -m py_compile bin/gh-runners` passes.
- `pytest -q tests/test_gh_runners.py` passes.
- A live `python3 bin/gh-runners --summarized` run prints `Scanning 5 repo(s)` or the expected bounded count.
- If a busy runner is still `(unknown)`, compare with `--scan-all-repos`; if the full scan also misses it, treat it as a GitHub API/job timing or metadata limitation rather than a default-scope regression.

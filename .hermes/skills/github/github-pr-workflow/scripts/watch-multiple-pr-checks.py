#!/usr/bin/env python3
import json
import subprocess
import sys
import time

USAGE = "watch-multiple-pr-checks.py <owner/repo> <pr-number> [<pr-number> ...]"
PENDING = {"PENDING", "QUEUED", "IN_PROGRESS", "WAITING", "REQUESTED"}
FAILED = {"FAILURE", "ERROR", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED", "STARTUP_FAILURE"}


def run_checks(repo: str, pr: str):
    cmd = [
        "bash",
        "-lc",
        f"env -u GITHUB_TOKEN gh pr checks {pr} --repo {repo} --json name,state",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None, f"PR {pr}: checks unavailable ({result.stderr.strip() or result.stdout.strip()})"
    data = json.loads(result.stdout)
    return data, f"PR {pr}: " + ", ".join(f"{item['name']}={item['state']}" for item in data)


def main():
    if len(sys.argv) < 3:
        print(USAGE, file=sys.stderr)
        return 2
    repo = sys.argv[1]
    prs = sys.argv[2:]
    start = time.time()
    timeout = 540
    interval = 15

    while True:
        all_done = True
        any_fail = False
        for pr in prs:
            data, line = run_checks(repo, pr)
            print(line, flush=True)
            if data is None:
                all_done = False
                continue
            states = [item["state"] for item in data]
            if any(state in FAILED for state in states):
                any_fail = True
            if any(state in PENDING for state in states):
                all_done = False
        print("---", flush=True)

        if any_fail:
            return 1
        if all_done:
            return 0
        if time.time() - start > timeout:
            print("timeout waiting for CI", flush=True)
            return 2
        time.sleep(interval)


if __name__ == "__main__":
    raise SystemExit(main())

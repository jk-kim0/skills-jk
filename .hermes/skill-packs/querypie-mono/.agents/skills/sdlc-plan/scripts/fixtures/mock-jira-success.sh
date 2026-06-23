#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -lt 4 || "$1" != "issue" || "$2" != "view" ]]; then
  echo "unexpected jira arguments: $*" >&2
  exit 2
fi

issue_key="$3"
mode="$4"

case "$mode" in
  --raw)
    printf '{"key":"%s","fields":{"summary":"Mock Jira issue"}}\n' "$issue_key"
    ;;
  --plain)
    if [[ "${5:-}" != "--comments" ]]; then
      echo "missing --comments argument" >&2
      exit 3
    fi
    printf '%s Mock Jira issue with %s comments\n' "$issue_key" "${6:-0}"
    ;;
  *)
    echo "unexpected jira mode: $mode" >&2
    exit 4
    ;;
esac

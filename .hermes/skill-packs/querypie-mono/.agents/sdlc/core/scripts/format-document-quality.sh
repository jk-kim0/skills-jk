#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: format-document-quality.sh <file>...

Format generated SDLC Markdown documents with the shared Prettier configuration.

This command intentionally writes files. Stage completion scripts use check-only
validation and never format documents implicitly.
EOF
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_dir="$(cd "${script_dir}/.." && pwd)"
prettier_config="${skill_dir}/config/prettier.config.json"
files=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h)
      usage
      exit 0
      ;;
    -*)
      echo "unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
    *)
      files+=("$1")
      shift
      ;;
  esac
done

if ((${#files[@]} == 0)); then
  echo "at least one file is required" >&2
  usage >&2
  exit 1
fi

if command -v prettier >/dev/null 2>&1; then
  prettier_bin="$(command -v prettier)"
elif command -v mise >/dev/null 2>&1 && mise which prettier >/dev/null 2>&1; then
  prettier_bin="$(mise which prettier)"
else
  echo "prettier is required. Run: mise install" >&2
  exit 1
fi

"$prettier_bin" --write --config "$prettier_config" "${files[@]}"

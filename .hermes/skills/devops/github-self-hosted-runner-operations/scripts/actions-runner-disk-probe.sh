#!/usr/bin/env bash
# Read-only GitHub Actions runner disk-usage probe.
# Usage on remote host:
#   RUNNER_PATH=/home/ubuntu/actions-runner bash actions-runner-disk-probe.sh
#   RUNNER_PATH=/home/deploy/actions-runner bash actions-runner-disk-probe.sh
set -u
RUNNER=${RUNNER_PATH:-$HOME/actions-runner}

printf '## identity\n'
date -Is || true
hostname || true
whoami || true
uname -a || true

printf '\n## runner-root\n'
if [ ! -d "$RUNNER" ]; then
  echo "MISSING $RUNNER"
  exit 0
fi
du -sh "$RUNNER" 2>/dev/null || true

printf '\n## runner-direct-children\n'
du -xh --max-depth=1 "$RUNNER" 2>/dev/null | sort -hr | sed -n '1,80p'

printf '\n## work-direct-children\n'
if [ -d "$RUNNER/_work" ]; then
  du -xh --max-depth=1 "$RUNNER/_work" 2>/dev/null | sort -hr | sed -n '1,80p'
fi

printf '\n## work-depth2-top\n'
if [ -d "$RUNNER/_work" ]; then
  du -xh --max-depth=2 "$RUNNER/_work" 2>/dev/null | sort -hr | sed -n '1,80p'
fi

printf '\n## symlinks-and-versioned-runner-dirs\n'
cd "$RUNNER" 2>/dev/null || exit 0
for p in bin externals; do
  [ -e "$p" ] && printf '%s -> %s\n' "$p" "$(readlink "$p" 2>/dev/null || echo '[not symlink]')"
done
ls -ld bin* externals* temp_* 2>/dev/null || true

printf '\n## key-cache-sizes\n'
for p in "$RUNNER/_diag" "$RUNNER/_temp" "$RUNNER/_tool" "$RUNNER/_work/_temp" "$RUNNER/_work/_tool" "$RUNNER/_work/_actions" "$RUNNER/_work/_tasks" "$RUNNER/_work/_update"; do
  [ -e "$p" ] && du -sh "$p" 2>/dev/null || true
done

printf '\n## toolcache-depth2\n'
if [ -d "$RUNNER/_work/_tool" ]; then
  du -xh --max-depth=2 "$RUNNER/_work/_tool" 2>/dev/null | sort -hr | sed -n '1,80p'
fi

printf '\n## git-dir-sizes\n'
if [ -d "$RUNNER/_work" ]; then
  find "$RUNNER/_work" -mindepth 3 -maxdepth 3 -type d -name .git -exec du -sh {} + 2>/dev/null | sort -hr | sed -n '1,80p'
fi

printf '\n## repo-subtree-top\n'
if [ -d "$RUNNER/_work" ]; then
  for top in "$RUNNER"/_work/*; do
    [ -d "$top" ] || continue
    name=$(basename "$top")
    d="$top/$name"
    [ -d "$d" ] || continue
    echo "### $name"
    du -xh --max-depth=2 "$d" 2>/dev/null | sort -hr | sed -n '1,25p'
  done
fi

printf '\n## largest-files-actions-runner\n'
find "$RUNNER" -xdev -type f -printf '%s\t%TY-%Tm-%Td %TH:%TM\t%p\n' 2>/dev/null |
  sort -nr | sed -n '1,80p' |
  awk -F'\t' '{cmd="numfmt --to=iec --suffix=B "$1; cmd|getline s; close(cmd); print s "\t" $2 "\t" $3}'

printf '\n## log-files-top\n'
find "$RUNNER" -xdev -type f \( -iname '*.log' -o -iname '*.diag' -o -iname '*.txt' \) -printf '%s\t%TY-%Tm-%Td %TH:%TM\t%p\n' 2>/dev/null |
  sort -nr | sed -n '1,80p' |
  awk -F'\t' '{cmd="numfmt --to=iec --suffix=B "$1; cmd|getline s; close(cmd); print s "\t" $2 "\t" $3}'

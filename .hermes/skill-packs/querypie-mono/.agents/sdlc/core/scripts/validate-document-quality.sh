#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: validate-document-quality.sh [--max-width <chars>] <file>...

Validate readability rules for generated SDLC Markdown documents.

Checks:
  - Prettier check with SDLC Markdown configuration
  - markdownlint check with SDLC Markdown configuration
  - file exists and is not empty
  - prose lines are at most 100 characters by default
  - empty bullets are replaced with `없음` or real content
  - empty field bullets such as `- 문제:` are filled
  - empty table cells and known empty plain fields such as `작성일:` are filled

Fenced code blocks and URL lines are excluded from custom line width checks.
EOF
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_dir="$(cd "${script_dir}/.." && pwd)"
prettier_config="${skill_dir}/config/prettier.config.json"
markdownlint_config="${skill_dir}/config/markdownlint.json"
max_width=100
files=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h)
      usage
      exit 0
      ;;
    --max-width)
      max_width="${2:-}"
      shift 2
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

if [[ -z "$max_width" || ! "$max_width" =~ ^[0-9]+$ ]]; then
  echo "--max-width must be a positive number" >&2
  exit 1
fi

if ((${#files[@]} == 0)); then
  echo "at least one file is required" >&2
  usage >&2
  exit 1
fi

markdown_files=()
for file in "${files[@]}"; do
  case "$file" in
    *.md|*.markdown)
      markdown_files+=("$file")
      ;;
  esac
done

standard_failed=0

run_standard_check() {
  local output_file
  output_file="$(mktemp)"

  if "$@" >"$output_file" 2>&1; then
    rm -f "$output_file"
    return 0
  fi

  cat "$output_file"
  rm -f "$output_file"
  return 1
}

if ((${#markdown_files[@]} > 0)); then
  if command -v prettier >/dev/null 2>&1; then
    prettier_bin="$(command -v prettier)"
  elif command -v mise >/dev/null 2>&1 && mise which prettier >/dev/null 2>&1; then
    prettier_bin="$(mise which prettier)"
  else
    echo "prettier is required. Run: mise install" >&2
    standard_failed=1
    prettier_bin=""
  fi

  if [[ -n "${prettier_bin:-}" ]] && ! run_standard_check \
    "$prettier_bin" --check --config "$prettier_config" "${markdown_files[@]}"; then
    standard_failed=1
  fi

  if command -v markdownlint-cli2 >/dev/null 2>&1; then
    markdownlint_cmd=("$(command -v markdownlint-cli2)")
  elif command -v mise >/dev/null 2>&1 && mise which markdownlint-cli2 >/dev/null 2>&1; then
    markdownlint_cmd=("$(mise which markdownlint-cli2)")
  elif command -v npx >/dev/null 2>&1; then
    markdownlint_cmd=(npx --yes markdownlint-cli2@0.22.1)
  else
    echo "markdownlint-cli2 or npx is required for Markdown linting" >&2
    standard_failed=1
    markdownlint_cmd=()
  fi

  if ((${#markdownlint_cmd[@]} > 0)) && ! run_standard_check \
    "${markdownlint_cmd[@]}" --config "$markdownlint_config" "${markdown_files[@]}"; then
    standard_failed=1
  fi
fi

perl -Mutf8 -CS -e '
  use strict;
  use warnings;

  my ($max_width, @files) = @ARGV;
  my $failed = 0;

  sub issue {
    my ($file, $line_no, $message) = @_;
    print "$file:$line_no: $message\n";
    $failed = 1;
  }

  my %plain_field_labels = map { $_ => 1 } (
    "작성일",
    "작성 시각",
    "Case ID",
    "Stage",
    "Group ID",
    "상태",
    "생성 시각",
    "원래 출처",
    "문제",
    "추천 방향",
    "기대효과",
    "제외 범위"
  );

  for my $file (@files) {
    if (!-s $file) {
      print "$file: missing or empty file\n";
      $failed = 1;
      next;
    }

    open my $fh, "<:encoding(UTF-8)", $file
      or do {
        print "$file: cannot read file: $!\n";
        $failed = 1;
        next;
      };

    my $in_code = 0;
    my $line_no = 0;

    while (my $line = <$fh>) {
      $line_no += 1;
      chomp $line;
      $line =~ s/\r$//;

      if ($line =~ /^```/) {
        $in_code = !$in_code;
        next;
      }

      next if $in_code;

      my $visible_line = $line;
      $visible_line =~ s/\t/    /g;

      if (length($visible_line) > $max_width && $line !~ m{https?://}) {
        issue($file, $line_no, "line exceeds ${max_width} characters");
      }

      if ($line =~ /^\s*[-*+]\s*$/) {
        issue($file, $line_no, "empty bullet; use `없음` or real content");
      }

      if ($line =~ /^\s*[-*+]\s+[^`][^:]{0,80}:\s*$/) {
        issue($file, $line_no, "empty field bullet; add content or `없음`");
      }

      if ($line =~ /^\s*([^#|`][^:]{0,80}):\s*$/) {
        my $label = $1;
        $label =~ s/^\s+|\s+$//g;
        if ($plain_field_labels{$label}) {
          issue($file, $line_no, "empty field; add content or `없음`");
        }
      }

      if ($line =~ /^\s*\|/ && $line =~ /\|\s*\|/) {
        issue($file, $line_no, "empty table cell; add content or remove the row");
      }
    }

    close $fh;
  }

  exit($failed ? 1 : 0);
' "$max_width" "${files[@]}"

custom_status=$?

if [[ "$standard_failed" -ne 0 || "$custom_status" -ne 0 ]]; then
  exit 1
fi

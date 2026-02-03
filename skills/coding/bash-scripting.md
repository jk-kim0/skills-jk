---
name: bash-scripting
description: Bash 스크립트 작성 시 스타일 가이드 - 외부 명령 실행의 가시성(observability) 확보
tags: [coding, bash, shell, automation]
---

# Bash Scripting Style Guide

## 목적

자동화 스크립트 작성 시 외부 명령 실행을 사용자가 관찰할 수 있도록 하는 것이 핵심.
`set -o xtrace` 또는 구조화된 로깅을 통해 실행 중인 명령을 실시간으로 보여준다.

## Google Style Guide와 차이점

| 항목 | Google Style | JK Style |
|------|--------------|----------|
| 함수 이름 | `lowercase_with_underscores` | `namespace::function_name` |
| Shell options | `set -o errexit -o nounset -o pipefail` | + `-o errtrace` 추가 |
| 들여쓰기 | 2 spaces | 2 spaces (동일) |
| 함수 키워드 | `function` 없이 `name() {}` | `function name() {}` 명시 |
| 명령 실행 | 직접 실행 | `log::do` 래퍼로 가시성 확보 |

## 적용 시점

- 외부 명령을 호출하는 자동화 스크립트
- CLI 도구 또는 인스톨러 작성
- 다단계 배치 처리
- 가시성이 중요한 모든 스크립트

## 핵심 원칙

### 1. Observability First

모든 외부 명령 실행은 사용자에게 보여야 한다.

```bash
# Option A: Global xtrace (간단한 스크립트)
set -o xtrace

# Option B: 구조화된 로깅 (복잡한 스크립트) - ERR trap으로 실패 위치 추적
function log::do() {
  local line_no
  line_no=$(caller | awk '{print $1}')
  # shellcheck disable=SC2064
  trap "log::error 'Failed to run at line $line_no: $*'" ERR
  printf "%b+ %s%b\n" "$BOLD_CYAN" "$*" "$RESET" 1>&2
  "$@"
}
```

### 2. Script Header

```bash
#!/usr/bin/env bash
# Brief description of what this script does
# Usage examples

SCRIPT_VERSION="25.01.1"  # YY.MM.PATCH

# Shell options - 항상 포함 (errtrace로 ERR trap이 함수 내에서도 동작)
[[ -n "${ZSH_VERSION:-}" ]] && emulate bash
set -o nounset -o errexit -o errtrace -o pipefail
```

### 3. Color Definitions

```bash
# readonly로 상수 선언
readonly BOLD_CYAN="\e[1;36m"
readonly BOLD_YELLOW="\e[1;33m"
readonly BOLD_RED="\e[1;91m"
readonly RESET="\e[0m"
```

### 4. 스크립트 디렉토리 경로

```bash
# 스크립트가 위치한 디렉토리의 절대 경로
SCRIPT_DIR=$(dirname "$(realpath "${BASH_SOURCE[0]}")")
```

## Quick Reference

| 패턴 | 예시 |
|------|------|
| Global 변수 | `UPPER_CASE_NAME` |
| Local 변수 | `lower_case_name` |
| 함수 네임스페이스 | `namespace::function_name()` |
| 명령 존재 확인 | `command -v cmd >/dev/null 2>&1` |
| 안전한 변수 참조 | `${var:-default}` |
| 문자열 비교 | `[[ "$a" == "$b" ]]` |

## 함수 패턴

### 네임스페이스 함수

```bash
function log::error() {
  printf "%bERROR: %s%b\n" "$BOLD_RED" "$*" "$RESET" 1>&2
}

function log::warning() {
  printf "%bWARNING: %s%b\n" "$BOLD_YELLOW" "$*" "$RESET" 1>&2
}

function log::do() {
  printf "%b+ %s%b\n" "$BOLD_CYAN" "$*" "$RESET" 1>&2
  "$@"
}

function log::sudo() {
  printf "%b+ sudo %s%b\n" "$BOLD_CYAN" "$*" "$RESET" 1>&2
  sudo "$@"
}
```

### 명령 존재 확인

```bash
function command_exists() {
  command -v "$@" >/dev/null 2>&1
}
```

### Local 변수 우선 선언

```bash
function example() {
  local var1 var2 var3
  var1=$1
  var2=$2
  var3="${3:-default}"

  # Function body
}
```

## 에러 처리

```bash
# Cleanup trap
tmp_file=$(mktemp /tmp/script.XXXXXX)
# shellcheck disable=SC2064
trap "rm -f ${tmp_file}" EXIT

# Exit with message
function die() {
  log::error "$@"
  exit 1
}
```

## 사용자 상호작용

```bash
function ask_yes() {
  echo "$@" >&2
  if [[ ! -t 0 ]]; then
    echo >&2 "# stdin is not a terminal"
    return 1
  fi

  printf 'Continue? [y/N] : '
  local answer
  read -r answer
  case "${answer}" in
    y|Y|yes|YES) return 0 ;;
    *) return 1 ;;
  esac
}
```

## 사용법 출력 함수

```bash
function print_usage_and_exit() {
  local code=${1:-0} out=2
  [[ code -eq 0 ]] && out=1  # 정상 종료는 stdout, 에러는 stderr
  cat >&"${out}" <<END_OF_USAGE
Usage: $0 <required_arg> [optional_arg]

EXAMPLES:
  $0 11.0.1 amazon-linux-2023
  $0 11.0.1 ubuntu-24.04 arm64

OPTIONS:
  -h, --help      Show this help message
  -x, --xtrace    Enable debug mode

END_OF_USAGE
  exit "$code"
}
```

## Main 함수 패턴

```bash
function main() {
  local -a arguments=()  # zsh 호환: argv 예약어 회피
  local cmd="default"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      -h|--help) print_usage_and_exit 0 ;;
      -V|--version) echo "$SCRIPT_VERSION"; exit 0 ;;
      -x|--xtrace) set -o xtrace; shift ;;
      --) shift; break ;;  # 옵션 종료
      -*)
        log::error "Unexpected option: $1"
        print_usage_and_exit 1
        ;;
      *) arguments+=("$1"); shift ;;
    esac
  done

  # 위치 인자 복원
  if [[ ${#arguments[@]} -gt 0 ]]; then
    set -- "${arguments[@]}"
  else
    set --
  fi

  # 필수 인자 검증
  local required_arg=${1:-}
  [[ -n "$required_arg" ]] || print_usage_and_exit 1

  cmd::default "$@"
}

main "$@"
```

## 디렉토리 이동 패턴

```bash
# pushd/popd로 안전한 디렉토리 이동
function archive_package() {
  local source_dir=$1
  pushd "$source_dir"
  log::do tar zcvf ../output/package.tar.gz .
  popd
}
```

## 출력 규칙

```bash
# 상태 메시지 → stderr
echo >&2 "# Processing..."

# 데이터 출력 → stdout
echo "${result}"

# 섹션 헤더
echo >&2 "#"
echo >&2 "## Section Name"
echo >&2 "#"
```

## 파일 작업

```bash
# Cleanup이 보장된 임시 파일
tmp=$(mktemp)
trap "rm -f $tmp" EXIT

# File descriptor로 안전하게 읽기
while IFS= read -r -u 9 line; do
  # process line
done 9<"${input_file}"

# 파일 권한
umask 0022  # 644 files, 755 directories
```

## 자주 하는 실수

| 실수 | 해결 |
|------|------|
| 에러 처리 없음 | `set -o errexit -o pipefail` 추가 |
| 조용한 외부 명령 | `log::do` 또는 `set -o xtrace` 사용 |
| 따옴표 없는 변수 | 항상 `"${var}"` 형태로 |
| `[ ]` 문자열 비교 | `[[ ]]` 사용 |
| 하드코딩 경로 | 변수와 parameter expansion 사용 |

## ShellCheck 통합

```bash
# 필요시 특정 경고 비활성화
# shellcheck disable=SC2064
trap "rm -f ${tmp_file}" EXIT

# shellcheck disable=SC1091
source ./config.env
```

## 템플릿

```bash
#!/usr/bin/env bash
# Description: Brief description
# Usage: script.sh [options] <args>

SCRIPT_VERSION="25.01.1"

[[ -n "${ZSH_VERSION:-}" ]] && emulate bash
set -o nounset -o errexit -o pipefail

BOLD_CYAN="\e[1;36m"
BOLD_RED="\e[1;91m"
RESET="\e[0m"

function log::error() {
  printf "%bERROR: %s%b\n" "$BOLD_RED" "$*" "$RESET" 1>&2
}

function log::do() {
  printf "%b+ %s%b\n" "$BOLD_CYAN" "$*" "$RESET" 1>&2
  "$@"
}

function main() {
  # Parse arguments
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --help|-h) echo "Usage: $0 [options]"; exit 0 ;;
      --verbose|-v) set -o xtrace; shift ;;
      *) break ;;
    esac
  done

  # Main logic with observable commands
  log::do echo "Starting..."
}

main "$@"
```

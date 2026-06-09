---
name: jk-bash-script-style-reference
description: Use when writing or editing bash scripts for jk. Apply this before implementing shell automation, CI helper scripts, docker/compose wrappers, or script refactors.
---

# JK Bash Script Style Reference

## Overview
JK bash script 작업에서는 일반적인 셸 습관보다 기존 레퍼런스 구현의 스타일을 우선한다.
새 스크립트는 아래 참조들의 구조, 출력 방식, 오류 처리 방식을 먼저 읽고 맞춘다.

## Required References
- `~/workspace/skills-jk/skills/coding/bash-scripting.md`
- `~/workspace/deck/scripts/ci-e2e`
- `~/workspace/tpm/compose/` 아래 스크립트들

## Required Behavior
1. bash 스크립트를 새로 쓰거나 수정하기 전에 위 3개 경로를 먼저 확인한다.
2. 가능하면 `ci-e2e` 와 `tpm/compose` 의 패턴을 직접 따른다.
3. 기본 골격은 `#!/usr/bin/env bash`, `[[ -n "${ZSH_VERSION:-}" ]] && emulate bash`, `set -o nounset -o errexit -o errtrace -o pipefail` 를 우선 검토한다.
4. 로그 함수, usage 출력, 인수 파싱, cleanup/trap 패턴은 참조 구현과 일관되게 유지한다.
5. 불필요한 방어 로직, 설명용 trace 출력, 과도한 추상화는 추가하지 않는다.

## Notes
- 저장소 규칙과 충돌하면 사용자/저장소 지침이 우선이다.
- 스크립트 스타일 판단이 애매하면 `ci-e2e` 와 `tpm/compose` 구현 쪽으로 맞춘다.

---
name: cc-codex-debate-review
description: CC와 Codex가 교대 lead agent로 반복 리뷰하며 토론 합의에 도달하는 PR 리뷰 오케스트레이션
---

> **Plugin mode:** bin, lib, config 등 에셋은 플러그인 루트에 위치합니다.
> 아래 절차의 `SKILL_ROOT`를 설정할 때 `${CLAUDE_PLUGIN_ROOT}`를 사용하세요.

!`awk 'BEGIN{n=0} /^---$/{n++; if(n<=2) next} n>=2' "${CLAUDE_SKILL_DIR}/../../SKILL.md"`

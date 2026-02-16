# Skills

AI Agent가 특정 작업을 수행하는 방법과 지침을 정의합니다.

## 구조

- `coding/` - 코드 작업 관련 (리뷰, 리팩토링, 테스트 등)
- `integrations/` - 외부 서비스 연동 (Jira, Confluence, Slack 등)
- `ops/` - 운영/배포 관련 (배포, 모니터링, 인프라 등)
- `research/` - 조사/분석 관련 (기술 조사, 의존성 분석 등)
- `superpowers/` - superpowers 패키지에서 옮겨온 Codex 워크플로우 스킬
- `writing/` - 문서 작성 관련 (마크다운 가이드, 스타일 등)

## Claude Code Skills (`.claude/skills/`)

Claude Code의 custom skill로 등록된 스킬입니다.

| 스킬 | 설명 | 설치 |
|------|------|------|
| [playwright-cli](../.claude/skills/playwright-cli/SKILL.md) | 브라우저 자동화 (웹 테스트, 폼 입력, 스크린샷, 데이터 추출) | `npm install -g @playwright/cli@latest` |

## 파일 포맷

```markdown
---
name: skill-name
description: 스킬 설명
tags: [tag1, tag2]
---

# Skill Title

## 목적
...

## 수행 절차
...

## 출력 형식
...
```

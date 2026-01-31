---
title: Self-hosted Runner 설정
description: GitHub Actions self-hosted runner에 Claude Code를 설치하는 방법
---

# Self-hosted Runner 설정

이 문서는 GitHub Actions self-hosted runner에서 AI Agent를 실행하기 위한 설정 방법을 설명합니다.

## 사전 요구사항

- macOS (Apple Silicon 또는 Intel)
- Node.js 18 이상
- npm 또는 yarn

## Claude Code 설치

### 1. npm으로 설치

```bash
npm install -g @anthropic-ai/claude-code
```

### 2. 설치 확인

```bash
claude --version
```

### 3. 인증 설정

Claude Code는 Anthropic API 키가 필요합니다.

```bash
# 환경 변수로 설정
export ANTHROPIC_API_KEY="your-api-key"

# 또는 ~/.claude/config.json에 설정
```

## Runner별 설정 상태

| Runner | 라벨 | Claude Code | 상태 |
|--------|------|-------------|------|
| home-A | `home` | - | 미확인 |
| home-B | `home` | - | 미확인 |
| office | `office` | - | 미확인 |

## GitHub Actions에서 사용

### 환경 변수 설정

Runner에서 Claude Code를 사용하려면 `ANTHROPIC_API_KEY`가 필요합니다.

**방법 1: Runner 환경에 직접 설정**

```bash
# ~/.bashrc 또는 ~/.zshrc에 추가
export ANTHROPIC_API_KEY="your-api-key"
```

**방법 2: GitHub Secrets 사용 (권장)**

1. Repository Settings > Secrets and variables > Actions
2. `ANTHROPIC_API_KEY` secret 추가
3. Workflow에서 사용:

```yaml
- name: Run Claude Code
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: |
    claude --print "your prompt"
```

## 설치 검증 Workflow

Runner에 Claude Code가 올바르게 설치되었는지 확인하는 workflow:

```yaml
name: Verify Claude Code

on:
  workflow_dispatch:

jobs:
  verify:
    runs-on: self-hosted
    steps:
      - name: Check Claude Code installation
        run: |
          if command -v claude &> /dev/null; then
            echo "Claude Code is installed"
            claude --version
          else
            echo "Claude Code is NOT installed"
            exit 1
          fi
```

## 문제 해결

### Claude Code 명령어를 찾을 수 없음

```
command not found: claude
```

**해결:**
1. Node.js global bin 경로 확인: `npm root -g`
2. PATH에 추가: `export PATH="$PATH:$(npm root -g)/../bin"`

### API 키 오류

```
Error: ANTHROPIC_API_KEY is not set
```

**해결:**
1. 환경 변수 설정 확인
2. GitHub Secrets에 키 추가

## 체크리스트

- [ ] Node.js 18+ 설치
- [ ] Claude Code 설치 (`npm install -g @anthropic-ai/claude-code`)
- [ ] 설치 확인 (`claude --version`)
- [ ] ANTHROPIC_API_KEY 설정
- [ ] 테스트 실행

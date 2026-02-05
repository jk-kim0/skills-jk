---
name: document-location
description: Use when creating project plans, design documents, task lists, reports, or any project-related documentation - determines the correct repository location
---

# Document Location Rules

## Overview

프로젝트 계획, 디자인 문서, 과제, 리포트 등을 작성할 때 적절한 저장소 위치를 결정합니다.

## Default Rule

**명시적으로 다른 위치를 지정하지 않으면, 모든 프로젝트 문서는 skills-jk 또는 skills-jk-private에 작성합니다.**

## Repository Selection

| 문서 유형 | 공개 여부 | 저장소 |
|----------|----------|--------|
| 일반 기술 문서 | 공개 가능 | `skills-jk` |
| 프로젝트 계획 | 비공개 | `skills-jk-private` |
| 디자인 문서 | 비공개 | `skills-jk-private` |
| 분석 리포트 | 비공개 | `skills-jk-private` |
| 과제/태스크 | 비공개 | `skills-jk-private` |

## Directory Structure

### skills-jk (공개)
```
skills-jk/
├── skills/           # 재사용 가능한 스킬 문서
└── docs/             # 일반 기술 문서
```

### skills-jk-private (비공개)
```
skills-jk-private/
├── projects/
│   ├── active/       # 진행 중인 프로젝트 문서
│   └── archive/      # 완료된 프로젝트 문서
├── reports/          # 분석 리포트
└── tasks/            # 과제/태스크
```

## When NOT to Use This Rule

다음 경우에는 해당 프로젝트 저장소에 직접 작성합니다:

1. **사용자가 명시적으로 위치를 지정한 경우**
2. **코드와 함께 커밋되어야 하는 문서** (예: README, API 문서)
3. **PR 설명이나 이슈 본문**

## Examples

| 요청 | 저장 위치 |
|------|----------|
| "이 기능의 디자인 문서를 작성해줘" | `skills-jk-private/projects/active/` |
| "querypie-mono에 디자인 문서를 작성해줘" | `querypie-mono/docs/` (명시적 지정) |
| "분석 결과를 정리해줘" | `skills-jk-private/reports/` |
| "bash 스크립팅 스킬을 작성해줘" | `skills-jk/skills/` |

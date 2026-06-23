---
name: jira-debug-identify-components
description: |
  신뢰도 기반 컴포넌트 식별 (하이브리드 방식)
  1. 라벨링 데이터에서 유사 티켓 검색
  2. AI 분석으로 컴포넌트 예측
  3. 신뢰도 < 70% → AskUserQuestion
  4. 결과를 라벨링 데이터에 저장
allowed-tools:
  - Read
  - Write
  - AskUserQuestion
---

# Identify Components Skill

티켓 내용을 분석하여 관련 코드 컴포넌트를 식별합니다.
**하이브리드 방식**: AI 분석 + 신뢰도 기반 사용자 확인

## 사용법

```
/jira-debug-identify-components
```

이전에 `/jira-debug-fetch-ticket`으로 조회한 티켓 정보가 컨텍스트에 있어야 합니다.

## 워크플로우

### Step 1: 라벨링 데이터 검색

`.Codex/memories/component-labels.json` 파일을 읽어서 유사한 과거 티켓을 검색합니다.

### Step 2: AI 분석

티켓 내용에서 키워드를 추출하고 컴포넌트 매핑 테이블을 참조하여 관련 컴포넌트를 예측합니다.

**컴포넌트 매핑 테이블**:

| 키워드 | 관련 컴포넌트 |
|--------|--------------|
| 대시보드, UI, 화면, 프론트 | `apps/front/` |
| API, 서버, 백엔드, REST | `apps/api/` |
| 쿼리 실행, SQL, 데이터베이스 | `apps/engine/`, `apps/api/dbam/` |
| 에이전트, 연결, 접속 | `apps/agent/` |
| 쿠버네티스, K8s, 컨테이너 | `apps/api/kac/` |
| 인증, 로그인, SSO, OAuth | `apps/api/iam/` |
| 권한, 정책, 역할 | `apps/api/sam/` |
| 엔진, 쿼리 처리 | `apps/commandpie-engine/` |
| 프록시, 엔진 연동 | `apps/arisa/` |
| 멀티 에이전트, Native App | `apps/multi-agent/` |

### Step 3: 신뢰도 계산

다음 기준으로 신뢰도 점수를 계산합니다:

**신뢰도 증가 요인:**
- 유사한 과거 티켓이 라벨링 데이터에 있음: +40%
- 스택 트레이스에 명확한 패키지명 포함: +30%
- 에러 메시지에 서비스/컴포넌트명 포함: +20%
- 예측된 컴포넌트가 1-2개: +10%

**신뢰도 감소 요인:**
- 유사 티켓이 없음: -20%
- 키워드가 모호함 (여러 컴포넌트에 해당): -20%
- 예측된 컴포넌트가 5개 이상: -30%

### Step 4: 신뢰도 분기

**신뢰도 >= 70%:**
- 자동으로 컴포넌트 결정
- `labeled_by: "ai"` 로 저장

**신뢰도 < 70%:**
- `AskUserQuestion` 도구를 호출하여 사용자에게 질문
- 질문 예시: "이 티켓은 어떤 컴포넌트와 관련이 있나요?"
- 옵션: front, api, api/dbam, api/iam, api/sam, api/kac, engine, commandpie-engine, arisa, agent, multi-agent
- `labeled_by: "human"` 으로 저장

### Step 5: 라벨링 데이터 저장

결과를 `.Codex/memories/component-labels.json`에 추가합니다:

```json
{
  "ticket": "QCP-4832",
  "keywords": ["쿼리 실행", "timeout", "30초"],
  "components": ["api/dbam", "engine"],
  "labeled_by": "ai",
  "confidence": 0.85,
  "created_at": "2025-01-08"
}
```

## 출력 형식

```json
{
  "components": ["apps/api/dbam/", "apps/engine/"],
  "keywords": ["쿼리 실행", "timeout"],
  "confidence": 0.85,
  "labeled_by": "ai",
  "reasoning": "스택 트레이스에 DbamQueryService 포함, 유사 티켓 QCP-2222 발견"
}
```

## 사용자 질문 형식 (신뢰도 < 70%)

```
header: "컴포넌트"
question: "이 티켓 [QCP-XXXX]는 어떤 컴포넌트와 관련이 있나요?"
options:
  - label: "Front (UI/대시보드)"
    description: "apps/front/ - React 웹 애플리케이션"
  - label: "API (백엔드 서버)"
    description: "apps/api/ - Kotlin/Spring 백엔드"
  - label: "Engine (쿼리 엔진)"
    description: "apps/engine/, apps/commandpie-engine/"
  - label: "Agent (연결 에이전트)"
    description: "apps/agent/ - Go 에이전트"
multiSelect: true
```

## 다음 단계

이 스킬의 출력은 다음 스킬들에서 사용됩니다:
- `/jira-debug-search-code` - 식별된 컴포넌트에서 코드 검색

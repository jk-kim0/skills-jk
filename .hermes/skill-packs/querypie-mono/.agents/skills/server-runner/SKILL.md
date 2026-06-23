---
name: server-runner
description: Use when QueryPie 로컬 서버를 실행해야 하고, bambi와 로컬 CLI 또는 IDE 실행 조합을 결정하거나, 실행 전 환경 점검과 early fail 가이드가 필요할 때.
---

# Server Runner

QueryPie 로컬 실행용 오케스트레이션 스킬.

이 문서는 QueryPie 로컬 실행에 이미 있는 여러 `make` 커맨드 사이에서 어떤 순서로 무엇을 해야 하는지 정리한 모범 실행 사례 문서다.
`bambi.yaml`을 기준으로 실행 대상을 읽고, 실패 시 어느 단계에서 무엇을 먼저 의심해야 하는지에 대한 LLM 컨텍스트를 제공한다.

1. 현재 `bambi.yaml` 기준 실행 상태 파악
2. 실행 전 환경 점검
3. migrate gate 통과 여부 확인
4. 이상하면 억지로 진행하지 않고 멈추기

모든 상대경로는 레포 루트 기준이다.
**현재 로컬 브랜치의 로컬 변경을 대상으로 실행한다.**
**특정 브랜치에 대한 지시가 있을 때는 워크트리를 생성해서 그 기준으로 실행한다.**
**실패 시 실패 단계 및 실패 사유를 분명하게 사용자에게 설명한다.**

## 실행 기준

기본 실행 상태는 **현재 `tools/bambi/bambi.yaml`** 이다.

- 필수 컴포넌트: `mysql`, `redis`, `nginx`, `api`, `front`, `engine`
- 이 중 `bambi.yaml`의 `services.excludes`에 들어 있는 항목: 로컬 CLI 또는 IDE 실행 대상
- 이 중 `services.excludes`에 없는 항목: bambi 실행 대상
- 나머지 선택 컴포넌트(`arisa`, `commandpie`, `gateway`, `novas` 등)는 요청이 있을 때만 추가 판단

## 서비스별 포트

| 서비스 | 포트 | 비고 |
|--------|------|------|
| front | 4001 | webpack-dev-server |
| api | 8080, 8090 | HTTP 8080, gRPC 8090 (health: `/actuator/health`) |
| engine | 8010, 8020 | gRPC |
| mysql | 3306 | |
| redis | 6379 | |
| nginx | 80 | 리버스 프록시 |

실행 전 포트 충돌을 반드시 확인한다. `lsof -i :<포트> -sTCP:LISTEN`으로 점검.

## 실행 전 점검

### 1. `bambi.yaml` 준비

```bash
# api, front, engine은 기본적으로 로컬 CLI 또는 IDE 실행 대상으로 둔다.
make -C tools/bambi init-bambi-yaml EXCLUDES="api front engine"
```

### 2. 실행 계획 확인

```bash
# 실행 계획 출력 + Docker 실행 여부 확인 + 포트 체크
make -C tools/bambi print-run-plan
```

사용자가 특정 서비스를 로컬 또는 Docker로 바꾸라고 명시했을 때만 `bambi.yaml`을 수정한다.

## 표준 실행 순서

### 1. branch 환경 준비

```bash
make -C tools/bambi setup-env
```

### 2. DB 시작

```bash
make -C tools/bambi up-db
```

### 3. migrate gate

표준 시작에서는 `migrate-db`를 기본으로 실행한다.

```bash
make -C tools/bambi migrate-db
```

`migrate-db`가 실패하면 여기서 즉시 중단한다.

- `up-service`로 넘어가지 않는다
- `api`를 로컬로도 띄우지 않는다
- 실패 원인과 다음 액션만 안내한다

안내 템플릿:

```text
migrate-db 실패. 서비스 시작을 중단합니다.

다음 확인:
- migrate 출력 로그 확인
- 현재 브랜치와 DB 상태 차이 확인
- 필요 시 develop 동기화 후 재시도

주의:
- `make purge-mysql`은 파괴적 작업이므로 사용자 승인 없이 실행하지 않음
```

### 4. bambi 서비스 시작

```bash
make -C tools/bambi up-service
```

### 5. 로컬 서비스 시작

`필수 컴포넌트` 중 현재 `bambi.yaml`에서 exclude된 항목만 로컬 CLI 또는 IDE로 실행한다.

#### 장시간 실행 프로세스 주의

`front`, `api`, `engine`처럼 계속 떠 있어야 하는 서버 프로세스는 Codex/Codex의 일반 셸 실행 세션에 그대로 매달아 두지 않는다.

금지:

- `exec_command` 또는 일반 Bash tool에서 `make ... backend`처럼 장시간 실행 커맨드를 foreground로 띄워 둔 뒤, 응답을 마치는 방식
- `nohup <command> &` 또는 `<command> > /tmp/log 2>&1 &`만으로 충분하다고 보고 방치하는 방식

이 방식은 앱이 크래시하지 않아도 도구 세션 정리, PTY 종료, SIGHUP/SIGTERM 전달로 Spring Boot/webpack-dev-server가 graceful shutdown될 수 있다. API 로그의 thread name에 `ionShutdownHook`가 보이거나, `Commencing graceful shutdown`, `Graceful shutdown complete`가 찍히면 애플리케이션 예외가 아니라 실행 세션 종료를 먼저 의심한다.

대신 아래 중 하나를 사용한다.

- 사용자가 IDE 실행을 선호하면 IDE 실행을 안내하고 health만 대기한다.
- unattended CLI 실행이 필요하면 `tmux`/`screen`/`launchctl`처럼 호출 세션과 분리되는 persistent runner를 사용한다.
- 실행 후에는 반드시 포트와 health를 별도 명령으로 확인한다.

`tmux`가 없으면 `screen`을 사용한다. macOS 기본 환경처럼 `screen`만 있는 경우에도 `start-frontend.sh`는 동작해야 한다. 둘 다 없을 때만 IDE 실행을 안내한다.

예시:

```bash
tmux has-session -t querypie-api 2>/dev/null || tmux new-session -d -s querypie-api 'make -C tools/playwright-tests oas backend > /tmp/querypie-api.log 2>&1'
tmux has-session -t querypie-front 2>/dev/null || tmux new-session -d -s querypie-front 'make -C tools/playwright-tests frontend > /tmp/querypie-front.log 2>&1'
screen -ls | grep -q '[.]querypie-api' || screen -dmS querypie-api bash -lc 'make -C tools/playwright-tests oas backend > /tmp/querypie-api.log 2>&1'
screen -ls | grep -q '[.]querypie-front' || screen -dmS querypie-front bash -lc 'make -C tools/playwright-tests frontend > /tmp/querypie-front.log 2>&1'
```

기존 세션이 있으면 새로 띄우기 전에 상태를 확인한다.

```bash
tmux ls | grep querypie
tail -n 100 /tmp/querypie-api.log
curl -s http://localhost:8080/actuator/health
```

`front` (포트 4001):

```bash
bash .Codex/skills/server-runner/scripts/start-frontend.sh
```

`api` (HTTP 8080, gRPC 8090):

- 현재 exclude된 경우에만 로컬 실행 대상이다
- IDE 실행 선호면 IDE 실행을 안내하고 대기
- unattended 실행이 필요하면 CLI fallback 허용

```bash
make -C tools/playwright-tests oas backend
```

`engine`:

- 현재 exclude되었거나 `apps/engine` 변경으로 로컬 검증이 필요하면 아래 둘 중 하나

```bash
make -C tools/playwright-tests engine-build engine
```

### 6. API health 이후 라이센스 등록

API가 bambi면:

```bash
bash .Codex/skills/server-runner/scripts/wait-api-health.sh
```

API가 로컬면:

```bash
curl -s http://localhost:8080/actuator/health | grep -q "UP"
```

그 다음:

```bash
make -C tools/bambi add-license
```

## early fail 조건

아래 중 하나면 진행하지 말고 가이드를 주고 멈춘다.

- `yq` 없음
- Docker 미실행
- Docker로 띄울 서비스 포트 충돌
- `migrate-db` 실패
- API health 실패
- `apps/engine`이 바뀌었는데 오래된 bambi 이미지로 실행하려는 경우
- API를 IDE로 띄워야 하는데 아직 안 띄운 경우

## 최소 트러블슈팅

- Frontend가 안 뜨면: `bash .Codex/skills/server-runner/scripts/start-frontend.sh`
- API가 스키마 오류로 죽으면: `make -C tools/bambi migrate-db`
- `Table doesn't exist`, `Unknown column`, `DEK가 등록되어 있지 않습니다`는 먼저 DB 스키마 불일치를 의심한다

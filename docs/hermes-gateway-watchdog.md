# Hermes Telegram Gateway Watchdog

repo-local Hermes (`HERMES_HOME="$PWD/.hermes"`) 환경에서 Telegram gateway 를 주기적으로 점검하고, 복구 가능한 상태일 때 자동으로 `start`/`restart` 하도록 돕는 watchdog 입니다.

파일:
- 실행 스크립트: `bin/hermes-gateway-watchdog`
- 상태 파일: `.hermes/gateway-watchdog-state.json`
- launchd 로그:
  - `.hermes/logs/gateway-watchdog.log`
  - `.hermes/logs/gateway-watchdog.error.log`
- launchd plist: `~/Library/LaunchAgents/ai.hermes.gateway-watchdog.plist`

## 무엇을 점검하나

`bin/hermes-gateway-watchdog check` 는 다음을 확인합니다.

1. Hermes gateway 서비스가 실제로 실행 중인지
2. `api.telegram.org` DNS 조회가 되는지
3. Telegram Bot API `getMe` 호출이 성공하는지
4. 최근 `gateway.error.log` 에 Telegram 연결 실패 흔적이 있는지

핵심 원칙:
- Telegram API 자체가 아직 닿지 않으면, 불필요한 restart 루프를 피하기 위해 gateway 를 계속 재시작하지 않습니다.
- Telegram API 가 다시 살아났는데 gateway 가 죽어 있으면 `start` 합니다.
- Telegram API 가 다시 살아났는데 gateway 가 살아 있기만 하고 예전 연결 실패 상태에 남아 있을 수 있으면 `restart` 를 1회 시도합니다.
- 최근 연결 실패 로그가 새로 생겼고 Telegram API 는 접근 가능한 상태면 `restart` 를 시도합니다.
- `recent_connect_failure` 로 인한 반복 복구는 exponential back-off 를 적용합니다: 5분 → 10분 → 20분 → 40분 → 최대 60분.

## 즉시 상태 확인

```bash
bin/hermes-gateway-watchdog check --json
```

자동 복구까지 포함:

```bash
bin/hermes-gateway-watchdog check --repair --json
```

## launchd 로 1분마다 모니터링

설치:

```bash
bin/hermes-gateway-watchdog install-launch-agent --interval 60
```

상태 확인:

```bash
bin/hermes-gateway-watchdog status
```

plist 미리보기:

```bash
bin/hermes-gateway-watchdog print-launch-agent --interval 60
```

제거:

```bash
bin/hermes-gateway-watchdog uninstall-launch-agent
```

## 기대 동작

- 노트북이 sleep 에서 깨어난 뒤 Telegram API 연결이 회복되면 다음 주기(기본 60초)에서 watchdog 이 이를 감지합니다.
- gateway 가 죽어 있으면 `hermes gateway start`
- gateway 가 살아 있지만 네트워크 단절 이후 polling 상태가 꼬였다고 판단되면 `hermes gateway restart`
- Telegram API 자체가 아직 닿지 않으면, 상태만 기록하고 다음 주기에 다시 점검합니다.

## 주의

- 이 watchdog 은 Wi‑Fi/VPN 을 재연결하지 않습니다.
- 이 watchdog 은 Telegram API 경로 기준으로 건강 상태를 판단합니다. 즉, 일반 인터넷이 살아 있어도 Telegram 경로가 막혀 있으면 unhealthy 로 봅니다.
- 실제 런타임 env 는 `.hermes/.env` 를 사용합니다.

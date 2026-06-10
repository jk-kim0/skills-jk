---
name: browser-ui-inspection
description: Use when inspecting or testing localhost, dev-server, preview, or deployed web pages with browser automation; defaults to headless and uses the user's visible Chrome only when explicitly requested.
tags: [browser, chrome, headless, playwright, ui-inspection, local-dev]
---

# Browser UI Inspection

## 목적

이 skill은 local PC에서 browser를 실행하거나 연결해 `localhost`, `127.0.0.1`, `::1`, dev server, preview deployment, deployed web page를 검사하거나 기능 테스트할 때 사용한다.

기본값은 **headless browser execution**이다.
이 기본값은 AI Agent의 browser 작업이 사람 사용자의 현재 업무, 열려 있는 Chrome tab, login session, keyboard focus를 방해하지 않게 하기 위한 규칙이다.

## 사용 시점

다음 작업에서는 이 skill을 먼저 적용한다.

- local dev server 또는 `localhost` 화면을 browser로 확인할 때
- dev server, preview, staging, deployed 화면을 screenshot, smoke, 기능 테스트로 확인할 때
- Playwright, `playwright-cli`, Browser MCP, Chrome DevTools MCP, 현재 실행 중인 Chrome browser 중 어떤 표면을 쓸지 결정해야 할 때
- 다른 skill이 웹페이지 검사, UI capture, browser smoke, visible Chrome 연결 절차를 위임할 때

사용하지 않는 경우:

- browser를 열지 않는 source-level review, lint, typecheck, unit test만 수행할 때
- production 데이터 변경, 실제 외부 발송, credential-gated 운영 작업처럼 별도 승인 경계가 필요한 작업

## 핵심 규칙

1. Browser 기반 검사와 테스트는 기본적으로 headless로 실행한다.
2. 현재 실행 중인 Chrome browser, 사용자의 Chrome profile, 이미 열려 있는 tab/window에는 사용자가 현재 대화에서 명시적으로 요청한 경우에만 연결한다.
3. 사용자가 "현재 Chrome에서 보여줘", "내 Chrome에 연결해서 보여줘", "브라우저에서 기능 테스트 과정을 보여줘"처럼 visible browser를 요구하면 Chrome/Chrome DevTools MCP 또는 동등한 visible browser 표면을 사용할 수 있다.
4. visible Chrome을 사용할 때도 기존 tab을 재사용하거나 사용자의 session을 변경하지 말고 새 tab 또는 새 window에서 대상 URL을 연다.
5. 명시 요청이 없는데 headless 실행이 불가능하면 visible browser로 우회하지 말고, headless로 가능한 대체 검증 또는 blocker를 보고한다.

## Headless 절차

1. Target을 고정한다.
   - URL 또는 path
   - base URL: local dev server, preview, staging, production 중 어느 것인지
   - auth 필요 여부
   - viewport와 screenshot 필요 여부
2. 대상 repository에 이미 있는 Playwright config, E2E test, smoke script를 우선 사용한다.
3. headless 실행을 명시적으로 유지한다.
   - Playwright는 별도 `headed` 설정이 없으면 headless로 실행한다.
   - command나 config가 visible browser를 여는 옵션을 포함하면 제거하거나 headless equivalent로 바꾼다.
   - `--headed`, `--ui`, `playwright show-report`, 자동 report viewer open 같은 visible UI 옵션을 사용하지 않는다.
4. artifact는 git에 포함하지 않는다.
   - screenshot, trace, video, report는 대상 repository가 ignore하는 runtime artifact 경로에 둔다.
   - artifact 경로가 불명확하면 `test-results/`, `playwright-report/`, `.tmp/`처럼 ignore 여부를 확인할 수 있는 경로를 사용한다.
5. 결과는 command, URL/path, viewport, auth mode, artifact path, 실패 원인을 함께 기록한다.

## `playwright-cli` 사용 기준

`playwright-cli`가 필요한 경우에도 기본은 headless 원칙이다.

- 단순 navigation, snapshot, form interaction은 가능하면 project test 또는 headless Playwright script로 실행한다.
- `playwright-cli open`, `playwright-cli open --browser=chrome`, `playwright-cli open --extension`, `playwright-cli open --persistent`처럼 visible browser나 persistent profile을 여는 명령은 사용자가 명시적으로 요청한 경우에만 사용한다.
- persistent profile, extension 연결, 사용자의 현재 Chrome session 연결은 모두 visible Chrome과 같은 승인 경계로 취급한다.

## Visible Chrome 절차

visible Chrome은 사용자가 현재 대화에서 명시적으로 요청한 경우에만 사용한다.

1. 요청 문구에 visible Chrome 의도가 있는지 먼저 확인한다.
   - 예: "현재 Chrome에 연결해줘", "내가 볼 수 있게 브라우저에서 테스트해줘", "기능 테스트 과정을 보여줘"
2. Chrome/Chrome DevTools MCP, `playwright-cli --extension`, 또는 환경에서 제공하는 visible browser 표면을 사용해 새 tab 또는 새 window를 연다.
3. 기존 tab, 현재 입력 focus, 사용자의 작업 중인 page를 건드리지 않는다.
4. 테스트 중에는 사용자가 볼 수 있도록 주요 navigation, click, form 입력, assertion 지점을 짧게 설명한다.
5. 테스트가 끝나면 확인한 상태, 실패 지점, 남긴 tab/window 상태를 보고한다.

## Fallbacks

- Browser MCP 또는 Chrome DevTools MCP가 이미 연결되어 있어도, 명시 요청이 없으면 현재 Chrome 연결보다 headless Playwright 또는 repository-local test를 우선한다.
- headless 실행이 dependency, auth, network 문제로 실패하면 command output과 artifact를 확인한 뒤 같은 headless 표면에서 복구를 시도한다.
- visible browser만 문제를 확인할 수 있다고 판단되면 바로 연결하지 말고, 왜 headless evidence가 부족한지 보고하고 사용자의 명시 요청을 기다린다.

## 완료 증거

완료 보고에는 다음을 포함한다.

- 사용한 mode: `headless` 또는 `visible Chrome`
- 대상 URL/path와 base URL
- 실행 command 또는 browser tool
- viewport와 auth 여부
- screenshot/trace/report artifact path
- 통과/실패 결과와 남은 risk

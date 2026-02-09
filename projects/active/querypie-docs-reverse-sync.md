# QueryPie Docs Reverse Sync

> **Status:** In Progress
> **Target Repo:** [querypie/querypie-docs/confluence-mdx][repo]

[repo]: https://github.com/querypie/querypie-docs/tree/main/confluence-mdx
> **Branch:** `refactor/reverse-sync-cli-simplify`

## 목표

AI Agent가 개선한 MDX 문서의 변경사항을 원본 Confluence 문서에 신뢰성 있게 역반영하는 파이프라인.

### 배경

현재 파이프라인은 Confluence → XHTML → MDX → Nextra 사이트로 단방향이다.
AI Agent가 MDX를 개선해도 원본 Confluence에는 반영되지 않는 문제가 있다.
내부 팀이 Confluence에서 직접 편집하므로, Confluence가 최신 상태를 유지해야 한다.

### 변경 범위 (Phase별)

| Phase | 범위 | 상태 |
|-------|------|------|
| Phase 1 | 텍스트 수준 변경 (오탈자 교정, 문장 다듬기, 용어 통일) | 구현 완료 |
| Phase 2 | 구조적 변경 (헤딩 재구성, 섹션 분리/통합, Callout 추가) | 미착수 |
| Phase 3 | 전면 재구성 (문서 구조, 위치, 이름 변경) | 미착수 |

---

## 아키텍처

### 파이프라인

```
① MDX 블록 파싱    (원본 MDX + 개선 MDX)
② 블록 Diff 추출   (변경된 블록 목록)
③ XHTML 블록 매핑  (원본 XHTML에서 블록 레벨 요소 추출)
④ XHTML 패치      (원본 XHTML + diff + 매핑 → 수정된 XHTML)
⑤ Forward 변환     (수정된 XHTML → 검증용 MDX)
⑥ Round-trip 검증  (검증 MDX == 개선 MDX, 문자 단위 완전 일치)
⑦ Confluence 반영  (검증 통과 시 API로 업데이트)
```

①~⑥은 로컬에서 반복 실행 가능하고, ⑦은 검증 통과 후에만 실행한다.

### 핵심 메커니즘: 블록 매핑 기반 역반영

XHTML 블록 요소(heading, paragraph, list 등)와 MDX 블록을 대응시키고, MDX에서 변경된 블록의 content를 XHTML inner HTML로 직접 변환하여 대상 요소의 innerHTML을 통째로 교체한다. 이를 통해 인라인 서식 변경(bold 추가/제거, code span, link 등)도 지원한다.

### 설계 원칙

1. **기존 forward converter 수정 최소화** — XHTML 입출력을 외부에서 분석하여 매핑
2. **로컬 우선** — 검증까지 모두 로컬, Confluence API 호출은 별도 단계
3. **엄격한 검증** — 문자 단위 완전 일치, 정규화 없음
4. **안전한 실패** — 검증 실패 시 해당 페이지를 건너뛰고 리포트만 남김

---

## 파일 구조

```
confluence-mdx/
  bin/
    reverse-sync                    ← CLI 실행파일 (entry point)
    reverse_sync_cli.py             ← CLI 오케스트레이터 + run_verify()
    reverse_sync_test_verify.py     ← run_verify() 직접 호출 wrapper (테스트용)
    reverse_sync/                   ← 패키지
      __init__.py
      mdx_block_parser.py           ← MDX → 블록 시퀀스 파싱
      block_diff.py                 ← 블록 시퀀스 1:1 순차 비교
      mapping_recorder.py           ← XHTML 블록 요소 추출 → 매핑 생성
      mdx_to_xhtml_inline.py        ← MDX 블록 content → XHTML inner HTML 변환
      xhtml_patcher.py              ← 매핑 + inner HTML → XHTML 패치 (innerHTML 교체)
      roundtrip_verifier.py         ← MDX 문자 단위 완전 일치 검증
      confluence_client.py          ← Confluence REST API 클라이언트
  tests/
    test_reverse_sync_mdx_block_parser.py
    test_reverse_sync_block_diff.py
    test_reverse_sync_mapping_recorder.py
    test_reverse_sync_mdx_to_xhtml_inline.py  ← 인라인 변환 + 블록 변환 단위 테스트
    test_reverse_sync_xhtml_patcher.py
    test_reverse_sync_roundtrip_verifier.py
    test_reverse_sync_cli.py        ← CLI + 헬퍼 함수 단위 테스트
    test_reverse_sync_e2e.py        ← run_verify() 직접 호출 통합 테스트
    run-tests.sh                    ← shell e2e 테스트 러너
    Makefile                        ← make test-reverse-sync 타겟
    testcases/<page_id>/            ← 14개 testcase (shell e2e용)
```

### 중간 산출물 (`var/<page_id>/`)

verify 실행 시 다음 파일들이 `var/<page_id>/`에 생성된다:

| 파일 | 용도 |
|------|------|
| `reverse-sync.diff.yaml` | 변경된 블록 목록 |
| `reverse-sync.mapping.original.yaml` | 원본 XHTML ↔ MDX 블록 매핑 |
| `reverse-sync.mapping.patched.yaml` | 패치된 XHTML 매핑 (디버깅용) |
| `reverse-sync.patched.xhtml` | 수정된 XHTML (push 대상) |
| `reverse-sync.result.yaml` | pass/fail + diff report |
| `verify.mdx` | 패치 XHTML → forward 변환 결과 (검증용) |

---

## 모듈 작동 방식

> 소스: [`confluence-mdx/bin/reverse_sync/`][pkg] · [`reverse_sync_cli.py`][cli]
>
> [pkg]: https://github.com/querypie/querypie-docs/tree/main/confluence-mdx/bin/reverse_sync
> [cli]: https://github.com/querypie/querypie-docs/blob/main/confluence-mdx/bin/reverse_sync_cli.py

### `mdx_block_parser`

MDX 텍스트를 블록 시퀀스(`MdxBlock` 리스트)로 파싱한다. 블록 유형: frontmatter, import_statement, heading, paragraph, code_block, list, html_block, empty. 파싱된 블록의 content를 합치면 원본과 완전 일치한다 (roundtrip 보장).

### `block_diff`

두 MDX 블록 시퀀스를 1:1 순차 비교하여 content가 달라진 블록을 `BlockChange` 리스트로 반환한다. Phase 1에서는 블록 수가 동일해야 하며, 다르면 에러를 발생시킨다.

### `mapping_recorder`

XHTML을 BeautifulSoup으로 파싱하여 블록 레벨 요소(h1~h6, p, ul/ol, table, macro 등)를 추출하고, 각 요소의 간이 XPath, 원본 텍스트(서식 포함), 평문 텍스트를 `BlockMapping` 리스트로 반환한다.

### `mdx_to_xhtml_inline`

MDX 블록 content를 XHTML inner HTML로 직접 변환한다. 블록 타입별 처리:
- **heading**: `#` 마커 제거, bold 마커 strip (forward converter가 heading 내 strong을 strip하므로), code/link 변환
- **paragraph**: 인라인 변환(`_convert_inline`) — code span(placeholder 보호), bold, link 순서로 처리
- **list**: indent 기반 중첩 파싱, `<li><p>...</p></li>` 구조 생성, figure/img 줄 skip
- **code_block**: 펜스 마커 제거, 코드 내용만 추출

### `xhtml_patcher`

`_replace_inner_html()`로 대상 요소의 innerHTML을 통째로 교체한다. `mdx_to_xhtml_inline`이 생성한 inner HTML을 BeautifulSoup으로 파싱하여 자식 노드로 삽입한다. legacy path(difflib 기반 text node 분배)도 호환성을 위해 유지한다.

### `roundtrip_verifier`

개선 MDX와 패치 XHTML의 forward 변환 결과를 문자 단위 완전 일치로 비교한다. 공백, 줄바꿈, 인라인 서식 모두 포함하며 어떤 정규화도 하지 않는다. 불일치 시 unified diff 리포트를 생성한다.

### `confluence_client`

`~/.config/atlassian/confluence.conf`에서 인증 정보를 읽고, Confluence REST API v1으로 페이지 버전 조회 및 본문 업데이트를 수행한다.

### `reverse_sync_cli` (오케스트레이터)

위 모듈들을 조합하여 verify/push 파이프라인을 실행한다. 주요 구성:

- [`MdxSource`][cli-L24] — MDX 내용 + 출처 표시 dataclass
- [`_resolve_mdx_source()`][cli-L50] — `ref:path` → 파일 경로 2단계 해석
- [`_extract_ko_mdx_path()`][cli-L66] — descriptor에서 `src/content/ko/...mdx` 경로 추출
- [`_get_changed_ko_mdx_files()`][cli-L76] — `git diff`로 브랜치의 변경된 ko MDX 파일 발견
- [`_resolve_page_id()`][cli-L90] — `var/pages.yaml`을 통해 page_id 자동 유도
- [`_forward_convert()`][cli-L104] — 패치된 XHTML을 forward converter로 MDX 변환
- [`run_verify()`][cli-L128] — 로컬 검증 파이프라인 (①~⑥ 전체 수행)
- [`_do_verify()`][cli-L385] — 공통 verify 로직 (MDX 소스 해석 → run_verify())
- [`_do_verify_batch()`][cli-L402] — 브랜치의 모든 변경 파일을 배치 verify 처리
- [`_do_push()`][cli-L425] — Confluence push 로직 (patched XHTML → API 업데이트)
- [`main()`][cli-L452] — CLI argparse + verify/push 분기 (단일/배치 모드)

[cli-L24]: https://github.com/querypie/querypie-docs/blob/main/confluence-mdx/bin/reverse_sync_cli.py#L24
[cli-L50]: https://github.com/querypie/querypie-docs/blob/main/confluence-mdx/bin/reverse_sync_cli.py#L50
[cli-L66]: https://github.com/querypie/querypie-docs/blob/main/confluence-mdx/bin/reverse_sync_cli.py#L66
[cli-L76]: https://github.com/querypie/querypie-docs/blob/main/confluence-mdx/bin/reverse_sync_cli.py#L76
[cli-L90]: https://github.com/querypie/querypie-docs/blob/main/confluence-mdx/bin/reverse_sync_cli.py#L90
[cli-L128]: https://github.com/querypie/querypie-docs/blob/main/confluence-mdx/bin/reverse_sync_cli.py#L128
[cli-L346]: https://github.com/querypie/querypie-docs/blob/main/confluence-mdx/bin/reverse_sync_cli.py#L346
[cli-L363]: https://github.com/querypie/querypie-docs/blob/main/confluence-mdx/bin/reverse_sync_cli.py#L363
[cli-L390]: https://github.com/querypie/querypie-docs/blob/main/confluence-mdx/bin/reverse_sync_cli.py#L390

---

## CLI 사용법

### 실행파일

[`bin/reverse-sync`][entry] — `sys.path`에 `bin/`을 추가하고 `reverse_sync_cli.main()`을 호출하는 entry point. `bin/reverse_sync/` 패키지와 이름 충돌을 피하기 위해 하이픈 사용.

[entry]: https://github.com/querypie/querypie-docs/blob/main/confluence-mdx/bin/reverse-sync

### 현재 구현

```bash
# 단일 파일 verify
reverse-sync verify "proofread/fix-typo:src/content/ko/user-manual/user-agent.mdx"

# 브랜치 전체 배치 verify
reverse-sync verify --branch proofread/fix-typo

# 단일 파일 push
reverse-sync push "proofread/fix-typo:src/content/ko/user-manual/user-agent.mdx"

# 브랜치 전체 배치 push
reverse-sync push --branch proofread/fix-typo

# push --dry-run = verify
reverse-sync push --dry-run "proofread/fix-typo:src/content/ko/user-manual/user-agent.mdx"

# original 명시
reverse-sync push "proofread/fix-typo:src/content/ko/user-manual/user-agent.mdx" \
  --original-mdx "main:src/content/ko/user-manual/user-agent.mdx"
```

### `<mdx>` 인자 형식

| 형식 | 예시 | 설명 |
|------|------|------|
| `ref:path` | `main:src/content/ko/overview.mdx` | git ref에서 파일 내용을 가져옴 |
| `path` | `src/content/ko/overview.mdx` | 로컬 파일 시스템 경로 |

page_id는 경로의 `src/content/ko/` 부분에서 `var/pages.yaml`을 통해 자동 유도된다.

### verify 커맨드

```
reverse-sync verify <mdx> [--original-mdx <mdx>] [--xhtml <path>]
reverse-sync verify --branch <branch>
```

- `<mdx>`: improved MDX (positional, optional)
- `--branch`: 브랜치의 모든 변경 ko MDX 파일을 자동 발견하여 배치 처리
- `--original-mdx`: 원본 MDX (optional, 기본: `main:<improved 경로>`)
- `--xhtml`: 원본 XHTML (optional, 기본: `var/<page-id>/page.xhtml`)

`<mdx>`와 `--branch`는 상호 배타. `--branch` 사용 시 `--original-mdx`/`--xhtml` 사용 불가.

### push 커맨드

```
reverse-sync push <mdx> [--original-mdx <mdx>] [--xhtml <path>] [--dry-run]
reverse-sync push --branch <branch> [--dry-run]
```

- `<mdx>`: improved MDX (positional, optional)
- `--branch`: 브랜치의 모든 변경 ko MDX 파일을 자동 발견하여 배치 처리
- `--original-mdx`: 원본 MDX (optional, 기본: `main:<improved 경로>`)
- `--xhtml`: 원본 XHTML (optional, 기본: `var/<page-id>/page.xhtml`)
- `--dry-run`: 검증만 수행, Confluence 반영 안 함 (= verify)

push는 내부적으로 verify 파이프라인을 먼저 실행하고, pass 시 자동으로 Confluence에 반영한다. `verify` 커맨드는 `push --dry-run`의 alias이다.

---

## 테스트

```bash
cd /Users/jk/workspace/querypie-docs/confluence-mdx

# pytest (unit + e2e) — 88 tests
PYTHONPATH=bin python3 -m pytest tests/test_reverse_sync_*.py tests/test_reverse_sync_e2e.py -v

# shell e2e — 14 testcases
cd tests && make test-reverse-sync
```

### 테스트 구조

- **pytest 단위 테스트**: [`test_reverse_sync_cli.py`][t-cli] — run_verify(), main(), 헬퍼 함수
- **pytest e2e**: [`test_reverse_sync_e2e.py`][t-e2e] — 실제 testcase 데이터로 run_verify() 호출
- **shell e2e**: [`run-tests.sh`][t-sh] `--type reverse-sync` — [`reverse_sync_test_verify.py`][t-wrapper]를 통해 run_verify() 직접 호출, expected 파일과 diff 비교
- **모듈별 pytest**: `test_reverse_sync_{module}.py` — 각 모듈 단위 테스트

[t-cli]: https://github.com/querypie/querypie-docs/blob/main/confluence-mdx/tests/test_reverse_sync_cli.py
[t-e2e]: https://github.com/querypie/querypie-docs/blob/main/confluence-mdx/tests/test_reverse_sync_e2e.py
[t-sh]: https://github.com/querypie/querypie-docs/blob/main/confluence-mdx/tests/run-tests.sh
[t-wrapper]: https://github.com/querypie/querypie-docs/blob/main/confluence-mdx/bin/reverse_sync_test_verify.py

---

---

## 향후 계획

### Phase 2 — 구조적 변경 역반영

- `block_diff` 확장: 블록 추가/삭제/이동을 위한 시퀀스 정렬 알고리즘
- MDX → XHTML 부분 역변환 모듈: 추가된 블록을 Confluence 매크로로 변환

### Phase 3 — 전면 재구성

- Confluence API 페이지 이동/이름 변경 연동
- 설계 추가 필요

---

## 진행 로그

| 날짜 | PR | 내용 |
|------|-----|------|
| 2026-02-09 | querypie-docs#632 | MDX→XHTML inner HTML 변환 모듈 추가 (difflib 제거) |
| 2026-02-09 | querypie-docs#624 | `--branch` 배치 verify/push 구현 |
| 2026-02-09 | querypie-docs#623 | forward converter 로깅 개선 |
| 2026-02-08 | querypie-docs#622 | push가 verify를 자동 수행하도록 리팩토링 |
| 2026-02-08 | querypie-docs#621 | `--page-id` 제거 및 CLI 간소화 |
| 2026-02-07 | querypie-docs#619 | verify 커맨드에 git ref 지원 추가 |

## 진행 상태

- [x] Phase 1 모듈 구현 (6개 모듈 + 오케스트레이터)
- [x] Forward converter 연동 (round-trip 검증)
- [x] Push 커맨드 Confluence API 연동
- [x] Testcase 14개 + Make 타겟
- [x] Git ref 지원 (`ref:path` 형식)
- [x] `--page-id` 제거, page_id 자동 유도
- [x] `--original-mdx` optional (기본: `main:<improved 경로>`)
- [x] Positional argument 전환 (`<mdx>`)
- [x] `bin/reverse-sync` 실행파일
- [x] 도움말 상세화 (예시 포함)
- [x] Push가 verify를 자동 수행
- [x] 브랜치 기반 배치 검증 (`--branch`)
- [x] MDX→XHTML inner HTML 변환 모듈 (`mdx_to_xhtml_inline`) — 인라인 서식 변경 지원
- [ ] Phase 2 설계 및 구현

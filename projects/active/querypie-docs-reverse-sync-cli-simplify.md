# reverse_sync_cli.py: CLI 간소화 및 실행파일 리팩토링

> **Status:** In Progress
> **Target Repo:** `/Users/jk/workspace/querypie-docs/confluence-mdx/`
> **Branch:** `refactor/reverse-sync-cli-simplify`
> **선행 작업:** git ref 지원 추가 완료 (querypie-docs-reverse-sync-verify-git-ref.md)

## 목표

1. `--page-id` 제거 — MDX 경로에서 `pages.yaml`을 통해 자동 유도
2. `--original-mdx` 기본값 처리 — 생략 시 `main:<improved 경로>` 자동
3. positional argument 전환 — `--improved-mdx`, `--mdx-path` → `<mdx>`
4. `bin/reverse-sync` 실행파일 생성
5. push가 verify를 자동 수행 — verify = push --dry-run

## 최종 CLI 사용법

```bash
# verify (--original-mdx 생략 시 main 자동)
reverse-sync verify "proofread/fix-typo:src/content/ko/user-manual/user-agent.mdx"

# verify (original 명시)
reverse-sync verify "proofread/fix-typo:src/content/ko/user-manual/user-agent.mdx" \
  --original-mdx "main:src/content/ko/user-manual/user-agent.mdx"

# push (verify를 자동 수행 후 Confluence 반영)
reverse-sync push "proofread/fix-typo:src/content/ko/user-manual/user-agent.mdx"

# push --dry-run (= verify)
reverse-sync push --dry-run "proofread/fix-typo:src/content/ko/user-manual/user-agent.mdx"
```

### `<mdx>` 인자 형식

| 형식 | 예시 |
|------|------|
| `ref:path` | `main:src/content/ko/user-manual/user-agent.mdx` |
| `path` | `src/content/ko/user-manual/user-agent.mdx` |

## 변경 파일

| 파일 | 변경 |
|------|------|
| `bin/reverse_sync_cli.py` | CLI 전면 리팩토링 (아래 상세) |
| `bin/reverse-sync` | 신규 — 실행파일 entry point |
| `bin/reverse_sync_test_verify.py` | 신규 — run_verify() 직접 호출 thin wrapper (run-tests.sh용) |
| `tests/test_reverse_sync_cli.py` | 테스트 업데이트 |
| `tests/run-tests.sh` | `reverse_sync_test_verify.py` 호출로 변경 |
| `tests/test_reverse_sync_e2e.py` | 변경 없음 |

## 구현 상세

### 1. 핵심 함수

#### `_resolve_mdx_source(arg)` — 2-tier MDX 소스 해석

bare ref 지원 제거, page_id 파라미터 제거. `ref:path` → 파일 경로 2단계 해석.

```python
def _resolve_mdx_source(arg: str) -> MdxSource:
    # 1. ref:path
    if ':' in arg:
        ref, path = arg.split(':', 1)
        if _is_valid_git_ref(ref):
            content = _get_file_from_git(ref, path)
            return MdxSource(content=content, descriptor=f'{ref}:{path}')
    # 2. 파일 경로
    if Path(arg).is_file():
        return MdxSource(content=Path(arg).read_text(), descriptor=arg)
    raise ValueError(...)
```

#### `_extract_ko_mdx_path(descriptor)` — ko MDX 경로 추출

descriptor에서 `src/content/ko/...mdx` 경로를 추출한다. `ref:path`와 plain path 모두 지원.

#### `_resolve_page_id(ko_mdx_path)` — page_id 자동 유도

`var/pages.yaml`에서 경로 부분(`user-manual/user-agent`)을 매칭하여 page_id를 반환.

### 2. verify 커맨드

```
reverse-sync verify <mdx> [--original-mdx <mdx>] [--xhtml <path>]
```

- `<mdx>`: improved MDX (positional, required)
- `--original-mdx`: 원본 MDX (optional, 기본: `main:<improved 경로>`)
- `--xhtml`: 원본 XHTML (optional, 기본: `var/<page-id>/page.xhtml`)
- page_id는 `<mdx>`에서 자동 유도

### 3. push 커맨드 — verify 자동 수행 (TODO)

```
reverse-sync push <mdx> [--original-mdx <mdx>] [--xhtml <path>] [--dry-run]
```

- verify와 동일한 인자를 수용
- 내부적으로 verify 파이프라인을 먼저 실행
- verify 통과 시 Confluence API로 push
- `--dry-run`: verify만 수행하고 push하지 않음 (= verify 커맨드와 동일)

**현재 구현:** push는 별도로 verify 결과(`result.yaml`)를 확인하는 방식
**목표 구현:** push가 verify를 내부적으로 자동 수행

### 4. `bin/reverse-sync` 실행파일

`sys.path` 방식으로 `bin/` 디렉토리를 Python path에 추가 후 `main()` 호출.
`bin/reverse_sync/` 패키지 디렉토리와 이름 충돌을 피하기 위해 하이픈(`-`) 사용.

### 5. `bin/reverse_sync_test_verify.py`

CLI가 `page_id`를 받지 않으므로, `run-tests.sh`에서 `run_verify()`를 직접 호출하는 wrapper.

### 6. 삭제된 코드

- `_resolve_mdx_path_from_page_id()`: bare ref 제거로 불필요

## 검증

```bash
cd /Users/jk/workspace/querypie-docs/confluence-mdx

# pytest (unit + e2e)
PYTHONPATH=bin python3 -m pytest tests/test_reverse_sync_cli.py tests/test_reverse_sync_e2e.py -v

# shell e2e
cd tests && make test-reverse-sync
```

## 진행 상태

- [x] `--page-id` 제거, page_id 자동 유도
- [x] `--original-mdx` optional (기본값: `main:<improved 경로>`)
- [x] positional argument 전환 (`<mdx>`)
- [x] `bin/reverse-sync` 실행파일 생성
- [x] 도움말 상세화 (예시 포함)
- [x] `bin/reverse_sync_test_verify.py` 생성
- [x] `tests/run-tests.sh` 변경
- [x] 테스트 통과 (pytest 19/19, shell e2e 14/14)
- [ ] push가 verify를 자동 수행하도록 리팩토링
- [ ] push에 `--dry-run` 플래그 추가

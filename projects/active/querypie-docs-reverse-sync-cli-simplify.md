# reverse_sync_cli.py: --page-id 제거 및 CLI 간소화

> **Status:** Done
> **Target Repo:** `/Users/jk/workspace/querypie-docs/confluence-mdx/`
> **선행 작업:** git ref 지원 추가 완료 (querypie-docs-reverse-sync-verify-git-ref.md)

## 목표

`reverse_sync_cli.py`의 verify/push 커맨드에서 `--page-id`를 제거한다.
page_id는 MDX 경로에서 `pages.yaml`을 통해 자동 유도 가능하므로 중복 인자이다.
또한 `--original-mdx`는 대부분 main 브랜치의 동일 경로 파일이므로 기본값으로 처리한다.

## 배경

현재 CLI 사용법:
```bash
# 현재 (중복이 많다)
reverse_sync_cli.py verify \
  --page-id 544112828 \
  --original-mdx "main:src/content/ko/user-manual/user-agent.mdx" \
  --improved-mdx "proofread/fix-typo:src/content/ko/user-manual/user-agent.mdx"
```

개선 후:
```bash
# verify (--original-mdx 생략 시 main:<improved 경로>)
reverse_sync_cli.py verify \
  --improved-mdx "proofread/fix-typo:src/content/ko/user-manual/user-agent.mdx"

# verify (명시적 original)
reverse_sync_cli.py verify \
  --original-mdx "main:src/content/ko/user-manual/user-agent.mdx" \
  --improved-mdx "proofread/fix-typo:src/content/ko/user-manual/user-agent.mdx"

# push (--page-id 대신 --mdx-path)
reverse_sync_cli.py push \
  --mdx-path src/content/ko/user-manual/user-agent.mdx
```

## 변경할 파일

| 파일 | 변경 |
|------|------|
| `bin/reverse_sync_cli.py` | `--page-id` 제거, `--original-mdx` optional, push에 `--mdx-path` 추가, page_id 자동 유도 |
| `bin/reverse_sync_test_verify.py` | 신규 — run_verify() 직접 호출하는 thin wrapper (run-tests.sh용) |
| `tests/test_reverse_sync_cli.py` | CLI main() 테스트 업데이트 + page_id 유도 테스트 추가 |
| `tests/test_reverse_sync_e2e.py` | 변경 없음 (run_verify() 직접 호출, page_id 유지) |
| `tests/run-tests.sh` | CLI 대신 `reverse_sync_test_verify.py` 호출로 변경 |

## 구현 상세

### 1. `_resolve_mdx_source()` 변경 — bare ref 제거

page_id 파라미터를 제거하고 2-tier 해석으로 단순화:

```python
def _resolve_mdx_source(arg: str) -> MdxSource:
    """2-tier MDX 소스 해석: ref:path → 파일 경로."""
    if ':' in arg:
        ref, path = arg.split(':', 1)
        if _is_valid_git_ref(ref):
            content = _get_file_from_git(ref, path)
            return MdxSource(content=content, descriptor=f'{ref}:{path}')
    if Path(arg).is_file():
        return MdxSource(content=Path(arg).read_text(), descriptor=arg)
    raise ValueError(f"Cannot resolve MDX source '{arg}': not a file path or ref:path")
```

### 2. `_extract_ko_mdx_path()` 추가

descriptor에서 `src/content/ko/...mdx` 경로를 추출:

```python
def _extract_ko_mdx_path(descriptor: str) -> str:
    path = descriptor.split(':', 1)[-1] if ':' in descriptor else descriptor
    prefix = 'src/content/ko/'
    if prefix in path and path.endswith('.mdx'):
        idx = path.index(prefix)
        return path[idx:]
    raise ValueError(f"Cannot extract ko MDX path from '{descriptor}'")
```

### 3. `_resolve_page_id()` 추가

```python
def _resolve_page_id(ko_mdx_path: str) -> str:
    rel = ko_mdx_path.removeprefix('src/content/ko/').removesuffix('.mdx')
    path_parts = rel.split('/')
    pages_path = Path('var/pages.yaml')
    if not pages_path.exists():
        raise ValueError("var/pages.yaml not found")
    pages = yaml.safe_load(pages_path.read_text())
    for page in pages:
        if page.get('path') == path_parts:
            return page['page_id']
    raise ValueError(f"MDX path '{ko_mdx_path}' not found in var/pages.yaml")
```

### 4. verify 커맨드 변경

- `--page-id` 제거
- `--original-mdx` optional (기본값: `main:<improved의 경로>`)
- `--improved-mdx` required

### 5. push 커맨드 변경

- `--page-id` → `--mdx-path` (src/content/ko/...mdx 경로)

### 6. `_resolve_mdx_path_from_page_id()` 제거

bare ref가 없으므로 더 이상 불필요.

### 7. run-tests.sh 변경

CLI가 page_id를 받지 않으므로, `reverse_sync_test_verify.py`를 통해 run_verify()를 직접 호출:

```bash
run_cmd env PYTHONPATH=bin python3 bin/reverse_sync_test_verify.py \
    "${test_id}" \
    "tests/${test_path}/original.mdx" \
    "tests/${test_path}/improved.mdx" \
    "tests/${test_path}/page.xhtml"
```

## 검증

```bash
cd /Users/jk/workspace/querypie-docs/confluence-mdx

# 1. pytest (unit + e2e)
PYTHONPATH=bin python3 -m pytest tests/test_reverse_sync_cli.py tests/test_reverse_sync_e2e.py -v

# 2. shell e2e
cd tests && make test-reverse-sync
```

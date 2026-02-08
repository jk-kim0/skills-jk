# reverse_sync_cli.py verify: git ref 지원 추가

> **Status:** Done
> **Target Repo:** `/Users/jk/workspace/querypie-docs/confluence-mdx/`
> **선행 작업:** Phase 1 구현 완료, testcase 및 Make 타겟 추가 완료

## 목표

`reverse_sync_cli.py verify`의 `--original-mdx`와 `--improved-mdx` 인자가 파일 경로뿐 아니라 git ref(`main`, `HEAD~1`, 커밋 해시 등)로도 MDX 소스를 지정할 수 있도록 개선한다.

## 배경

실제 워크플로우에서 original은 main 브랜치의 MDX 파일이고, improved는 현재 작업 브랜치의 파일인 경우가 대부분이다. 매번 파일을 별도로 추출하는 것이 번거로우므로, git ref를 직접 인자로 받아 처리할 수 있도록 한다.

## 설계: 3-tier MDX 소스 해석

`--original-mdx`와 `--improved-mdx` 인자를 다음 순서로 해석한다:

| 우선순위 | 형식 | 예시 | 판별 조건 |
|---------|------|------|----------|
| 1 | `ref:path` | `main:src/content/ko/user-manual/user-agent.mdx` | `:` 포함 & 좌측이 유효한 git ref |
| 2 | 파일 경로 | `var/544112828/original.mdx` | 파일이 존재 |
| 3 | bare ref | `main` | 유효한 git ref → `pages.yaml`로 경로 자동 유도 |

### 사용 예시

```bash
# ref:path (명시적)
--original-mdx "main:src/content/ko/user-manual/user-agent.mdx"

# bare ref (page-id로 경로 자동 유도)
--original-mdx main

# 파일 경로 (기존 방식, 하위 호환)
--original-mdx tests/testcases/544112828/original.mdx

# 혼합
--original-mdx main --improved-mdx tests/testcases/544112828/improved.mdx
```

## 구현 상세

### 변경 파일

| 파일 | 변경 |
|------|------|
| `bin/reverse_sync_cli.py` | `MdxSource` dataclass + 4개 헬퍼 함수 + `run_verify()` 시그니처 변경 + `main()` 변경 |
| `tests/test_reverse_sync_cli.py` | 기존 테스트 `MdxSource` 적용 + 4개 해석 테스트 추가 |
| `tests/test_reverse_sync_e2e.py` | `run_verify()` 호출부 `MdxSource` 적용 |

### 추가된 요소

1. **`MdxSource` dataclass** — `content` (MDX 내용) + `descriptor` (출처 표시)
2. **`_is_valid_git_ref(ref)`** — `git rev-parse --verify`로 유효성 확인
3. **`_get_file_from_git(ref, path)`** — `git show ref:path`로 파일 내용 반환
4. **`_resolve_mdx_path_from_page_id(page_id)`** — `var/pages.yaml`에서 경로 유도
5. **`_resolve_mdx_source(arg, page_id)`** — 3-tier 해석 로직

### `run_verify()` 시그니처 변경

```python
# Before
def run_verify(page_id, original_mdx_path, improved_mdx_path, xhtml_path=None)

# After
def run_verify(page_id, original_src: MdxSource, improved_src: MdxSource, xhtml_path=None)
```

`diff.yaml`의 `original_mdx`, `improved_mdx` 필드도 `descriptor`로 기록.

## 검증 결과

- pytest 15/15 passed (unit + e2e)
- shell e2e 14/14 passed (`make test-reverse-sync`)
- 기존 파일 경로 방식 하위 호환 확인

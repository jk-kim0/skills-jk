# Reverse Sync Testcase 및 Make 타겟 추가 계획

> **Status:** Plan Review
> **Target Repo:** `/Users/jk/workspace/querypie-docs/confluence-mdx/`
> **선행 작업:** Phase 1 구현 완료 (7개 모듈), 페이지 1911652402 reverse sync verify → push 성공

## 목표

페이지 1911652402에서 성공한 reverse sync 결과를 재현 가능한 testcase로 저장하고, 기존 `make` 기반 테스트 인프라에 `reverse-sync` 테스트 타입을 추가하여 회귀 검증을 자동화한다.

## 기존 테스트 인프라 분석

### 디렉토리 구조

```
tests/
├── run-tests.sh          ← 테스트 러너 (--type xhtml|skeleton)
├── Makefile              ← make 타겟 (test-xhtml, test-skeleton, test-render, clean, help)
└── testcases/
    ├── 544382364/         ← 기존 testcase 예시
    │   ├── page.xhtml     ← 입력
    │   ├── page.v1.yaml   ← 메타데이터
    │   ├── expected.mdx   ← 기대 결과
    │   └── output.mdx     ← 생성된 출력 (clean 대상)
    └── ...                ← 20개 testcase
```

### run-tests.sh 패턴

- `run_<type>_test()` — 단일 testcase 실행 함수
- `has_<type>_input()` — 입력 파일 존재 확인 함수
- `main()` case문 — `--type` 분기

### Makefile 패턴

- `test-<type>` — 전체 테스트
- `test-<type>-one TEST_ID=<id>` — 단일 테스트
- `clean` — `output.*` 파일 삭제
- `all` — 기본 테스트 모음 (xhtml + skeleton + render)

## 수정 파일

| 파일 | 변경 유형 | 설명 |
|------|----------|------|
| `tests/testcases/1911652402/` (11개 파일) | **신규** | reverse-sync testcase |
| `tests/run-tests.sh` | 수정 | reverse-sync 테스트 함수 + case 분기 |
| `tests/Makefile` | 수정 | 타겟 2개 + clean/help 업데이트 |

---

## 구현 상세

### 1. Testcase 디렉토리: `tests/testcases/1911652402/`

`var/1911652402/`에서 복사하여 생성.

#### 테스트 시나리오

페이지 1911652402 ("Reverse Sync Test Page")에서 `Kubenetes` → `Kubernetes` typo 수정을 reverse sync하는 시나리오.

- **original.mdx** 42행: `Kubenetes 환경에서 제품을 설치하는 경우...`
- **improved.mdx** 42행: `Kubernetes 환경에서 제품을 설치하는 경우...`
- **기대 결과**: status=pass, exact_match=true, changes_count=1

#### 디렉토리 구조

```
tests/testcases/1911652402/
├── page.xhtml                              ← 입력: 원본 XHTML
├── page.v1.yaml                            ← 메타데이터: forward converter title 추출
├── page.v2.yaml                            ← 메타데이터
├── ancestors.v1.yaml                       ← 메타데이터
├── attachments.v1.yaml                     ← 메타데이터
├── children.v2.yaml                        ← 메타데이터
├── original.mdx                            ← 입력: forward 변환 결과 (typo 포함)
├── improved.mdx                            ← 입력: 텍스트 수정본
├── expected.mdx                            ← 기대: forward 변환 (= original.mdx)
├── expected.reverse-sync.result.yaml       ← 기대: verify 결과
├── expected.reverse-sync.patched.xhtml     ← 기대: 패치된 XHTML
└── expected.reverse-sync.diff.yaml         ← 기대: 변경 블록 목록
```

#### 입력 파일 (8개)

| 파일 | 원본 | 용도 |
|------|------|------|
| `page.xhtml` | `var/.../page.xhtml` | 원본 XHTML (verify `--xhtml` 입력) |
| `page.v1.yaml` | `var/.../page.v1.yaml` | forward converter title 추출 |
| `page.v2.yaml` | `var/.../page.v2.yaml` | 메타데이터 |
| `ancestors.v1.yaml` | `var/.../ancestors.v1.yaml` | 메타데이터 |
| `attachments.v1.yaml` | `var/.../attachments.v1.yaml` | 메타데이터 |
| `children.v2.yaml` | `var/.../children.v2.yaml` | 메타데이터 |
| `original.mdx` | `var/.../original.mdx` | forward 변환 결과 ("Kubenetes" typo 포함) |
| `improved.mdx` | `var/.../improved.mdx` | 텍스트 수정본 ("Kubernetes" 교정) |

#### 기대 결과 파일 (4개)

| 파일 | 원본 | 용도 |
|------|------|------|
| `expected.mdx` | `original.mdx` 복사 | 기존 xhtml 테스트 호환 (forward 변환 기대값) |
| `expected.reverse-sync.result.yaml` | `var/.../reverse-sync.result.yaml` | verify 결과 |
| `expected.reverse-sync.patched.xhtml` | `var/.../reverse-sync.patched.xhtml` | 패치된 XHTML |
| `expected.reverse-sync.diff.yaml` | `var/.../reverse-sync.diff.yaml` | 변경 블록 목록 |

#### 기대 결과 파일 내용

**expected.reverse-sync.result.yaml** (timestamp 제외 비교):
```yaml
changes_count: 1
created_at: '2026-02-07T17:00:05.921664+00:00'   # ← diff 시 grep -v 제외
page_id: '1911652402'
status: pass
verification:
  diff_report: ''
  exact_match: true
```

**expected.reverse-sync.diff.yaml** (timestamp/경로 제외 비교):
```yaml
changes:
- block_id: paragraph-32
  change_type: modified
  index: 32
  new_content: 'Kubernetes 환경에서 제품을 설치하는 경우, ...'
  old_content: 'Kubenetes 환경에서 제품을 설치하는 경우, ...'
created_at: '2026-02-07T17:00:05.921664+00:00'    # ← diff 시 grep -v 제외
improved_mdx: var/1911652402/improved.mdx          # ← diff 시 grep -v 제외
original_mdx: var/1911652402/original.mdx          # ← diff 시 grep -v 제외
page_id: '1911652402'
```

**expected.reverse-sync.patched.xhtml** (정확히 일치 비교):
- 원본 page.xhtml과 동일 구조이나 `Kubenetes` → `Kubernetes`로 교정됨
- `<ac:link>` 태그가 self-closing `<ri:page ... />` → `<ri:page ...></ri:page>` 형식으로 정규화됨 (BeautifulSoup 특성)

#### 생성되는 출력 (clean 대상)

- `output.reverse-sync.result.yaml`
- `output.reverse-sync.patched.xhtml`
- `output.reverse-sync.diff.yaml`

#### 구현 순서

```bash
# 1. 디렉토리 생성
mkdir -p tests/testcases/1911652402

# 2. 입력 파일 복사 (var → testcases)
for f in page.xhtml page.v1.yaml page.v2.yaml ancestors.v1.yaml \
         attachments.v1.yaml children.v2.yaml original.mdx improved.mdx; do
    cp var/1911652402/$f tests/testcases/1911652402/
done

# 3. expected 파일 생성
cp tests/testcases/1911652402/original.mdx tests/testcases/1911652402/expected.mdx
cp var/1911652402/reverse-sync.result.yaml  tests/testcases/1911652402/expected.reverse-sync.result.yaml
cp var/1911652402/reverse-sync.patched.xhtml tests/testcases/1911652402/expected.reverse-sync.patched.xhtml
cp var/1911652402/reverse-sync.diff.yaml    tests/testcases/1911652402/expected.reverse-sync.diff.yaml
```

### 2. `tests/run-tests.sh` 확장

#### 새 함수: `run_reverse_sync_test()`

```bash
run_reverse_sync_test() {
    local test_id="$1"
    local test_path="${TEST_DIR}/${test_id}"

    # verify 실행 (cwd를 confluence-mdx root로 이동)
    # CLI가 var/<page_id>/에 중간 파일을 쓰기 때문
    pushd .. > /dev/null
    run_cmd env PYTHONPATH=bin python bin/reverse_sync_cli.py verify \
        --page-id "${test_id}" \
        --original-mdx "tests/${test_path}/original.mdx" \
        --improved-mdx "tests/${test_path}/improved.mdx" \
        --xhtml "tests/${test_path}/page.xhtml"
    popd > /dev/null

    # var/에 생성된 중간 파일을 output.*으로 복사
    local var_dir="../var/${test_id}"
    cp "${var_dir}/reverse-sync.result.yaml"  "${test_path}/output.reverse-sync.result.yaml"
    cp "${var_dir}/reverse-sync.patched.xhtml" "${test_path}/output.reverse-sync.patched.xhtml"
    cp "${var_dir}/reverse-sync.diff.yaml"    "${test_path}/output.reverse-sync.diff.yaml"

    # expected와 비교 (timestamp/경로 필드 제외)
    diff -u <(grep -v 'created_at' "${test_path}/expected.reverse-sync.result.yaml") \
            <(grep -v 'created_at' "${test_path}/output.reverse-sync.result.yaml")
    diff -u "${test_path}/expected.reverse-sync.patched.xhtml" \
            "${test_path}/output.reverse-sync.patched.xhtml"
    diff -u <(grep -v 'created_at\|original_mdx\|improved_mdx' "${test_path}/expected.reverse-sync.diff.yaml") \
            <(grep -v 'created_at\|original_mdx\|improved_mdx' "${test_path}/output.reverse-sync.diff.yaml")
}
```

**핵심 포인트:**
- `pushd ..` — CLI가 `var/<page_id>/`에 결과를 쓰므로 cwd를 repo root로 이동
- `grep -v 'created_at'` — 실행 시마다 달라지는 timestamp 필드 제외
- `grep -v 'original_mdx\|improved_mdx'` — 절대 경로가 달라질 수 있는 필드 제외

#### 새 함수: `has_reverse_sync_input()`

```bash
has_reverse_sync_input() {
    local test_id="$1"
    [[ -f "${TEST_DIR}/${test_id}/original.mdx" ]] && \
    [[ -f "${TEST_DIR}/${test_id}/improved.mdx" ]]
}
```

#### main() case문 분기 추가

```bash
reverse-sync)
    if [[ -n "${TEST_ID}" ]]; then
        run_single_test run_reverse_sync_test "Reverse-Sync" "${TEST_ID}"
    else
        run_all_tests run_reverse_sync_test "Reverse-Sync" has_reverse_sync_input
    fi
    ;;
```

### 3. `tests/Makefile` 확장

#### 새 타겟

```makefile
# Run reverse-sync tests
.PHONY: test-reverse-sync
test-reverse-sync:
	@$(TEST_SCRIPT) --type reverse-sync $(VERBOSE_FLAG)

# Run a specific reverse-sync test
.PHONY: test-reverse-sync-one
test-reverse-sync-one:
	@if [ -z "$(TEST_ID)" ]; then \
		echo "Usage: make test-reverse-sync-one TEST_ID=<test_id>"; \
		exit 1; \
	fi
	@$(TEST_SCRIPT) --type reverse-sync --test-id $(TEST_ID) $(VERBOSE_FLAG)
```

#### clean 업데이트

```makefile
# 기존 삭제 패턴에 추가
@find testcases -name "output.reverse-sync.*" -type f -delete
```

#### help 업데이트

```
  test-reverse-sync      - Run Reverse-Sync tests
  test-reverse-sync-one  - Run a specific Reverse-Sync test
```

#### all 타겟

`all`에는 **추가하지 않음**. reverse-sync는 별도 타겟으로 운영한다.
(이유: forward converter venv 활성화 + var/ 디렉토리 의존성이 기존 테스트와 다름)

---

## 검증 절차

```bash
cd /Users/jk/workspace/querypie-docs/confluence-mdx/tests

# 1. 단일 reverse-sync 테스트
make test-reverse-sync-one TEST_ID=1911652402 VERBOSE=1

# 2. 전체 reverse-sync 테스트
make test-reverse-sync

# 3. 기존 테스트 회귀 확인
make test-xhtml

# 4. pytest 회귀 확인
cd .. && PYTHONPATH=bin python3 -m pytest tests/ -v
```

## 결정 사항

- [ ] `expected.mdx` = `original.mdx` 복사 — xhtml 테스트와 겸용 가능하게 할 것인가?
- [ ] `all` 타겟에 reverse-sync 포함 여부 — 현재 계획은 제외

# Debate Review CLI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Python CLI `bin/debate-review` — CC-Codex Debate Review의 상태 관리 도구 구현

**Architecture:** subcommand 기반 CLI. 각 subcommand는 상태 파일을 읽고, 상태 전이 로직을 수행하고, 결과를 저장한다. CC(오케스트레이터)가 라운드 루프를 돌면서 이 CLI를 호출한다. CLI는 오케스트레이션 자체를 수행하지 않는다.

**Tech Stack:** Python 3.10+, argparse (외부 의존성 없음), pytest

**Spec:** `docs/superpowers/specs/2026-03-30-cc-codex-debate-review-cli-interface-design.md`
**Design:** `docs/superpowers/specs/2026-03-30-cc-codex-debate-review-design.md`

---

## File Structure

```
bin/debate-review                  # 실행 엔트리포인트 (shebang, lib/ import)
lib/debate_review/
├── __init__.py
├── cli.py                         # argparse 정의, subcommand dispatch
├── state.py                       # 상태 파일 CRUD, 스키마 생성/검증
├── issue_ops.py                   # issue upsert, issue_key 생성, consensus 계산
├── round_ops.py                   # verdict 기록, settle-round, clean pass 판정
├── cross_verification.py          # record-cross-verification, resolve-rebuttals
├── application.py                 # record-application 3-phase
├── sync.py                        # sync-head (git fetch, worktree, supersede)
├── comment.py                     # post-comment (템플릿, 중복 확인, 게시)
├── gh.py                          # GitHub CLI 래퍼 (env -u GITHUB_TOKEN)
└── config.py                      # YAML config 로드
tests/debate_review/
├── conftest.py                    # 공통 fixture (tmp state file, sample state)
├── test_state.py
├── test_issue_ops.py
├── test_round_ops.py
├── test_cross_verification.py
├── test_application.py
├── test_sync.py                   # git 조작 mock 테스트
├── test_comment.py
└── test_cli.py                    # CLI 통합 테스트
pyproject.toml                     # 프로젝트 루트에 신규 생성
```

---

## Task 1: 프로젝트 스캐폴딩 + 상태 파일 CRUD

**Files:**
- Create: `pyproject.toml`
- Create: `bin/debate-review`
- Create: `lib/debate_review/__init__.py`
- Create: `lib/debate_review/cli.py`
- Create: `lib/debate_review/state.py`
- Create: `lib/debate_review/config.py`
- Create: `tests/debate_review/__init__.py`
- Create: `tests/debate_review/conftest.py`
- Create: `tests/debate_review/test_state.py`

- [ ] **Step 1: pyproject.toml 생성**

```toml
[project]
name = "debate-review"
version = "0.1.0"
description = "State management CLI for CC-Codex Debate Review"
requires-python = ">=3.10"
dependencies = ["pyyaml>=6.0"]

[project.optional-dependencies]
dev = ["pytest>=7.0"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["lib"]
```

- [ ] **Step 2: 상태 파일 스키마 테스트 작성**

`tests/debate_review/test_state.py`:

```python
import json
import pytest
from debate_review.state import create_initial_state, load_state, save_state


def test_create_initial_state_has_required_fields():
    state = create_initial_state(
        repo="owner/repo",
        repo_root="/tmp/repo",
        pr_number=123,
        is_fork=False,
        head_sha="abc1234",
        pr_branch_name="feat/x",
        max_rounds=10,
    )
    assert state["repo"] == "owner/repo"
    assert state["pr_number"] == 123
    assert state["status"] == "in_progress"
    assert state["current_round"] == 1
    assert state["head"]["initial_sha"] == "abc1234"
    assert state["head"]["target_ref"] == "refs/debate-sync/pr-123/head"
    assert state["issues"] == {}
    assert state["rounds"] == []
    assert state["journal"]["step"] == "init"


def test_save_and_load_roundtrip(tmp_path):
    state = create_initial_state(
        repo="owner/repo",
        repo_root="/tmp/repo",
        pr_number=42,
        is_fork=True,
        head_sha="def5678",
        pr_branch_name="fix/y",
        max_rounds=5,
    )
    path = tmp_path / "test-state.json"
    save_state(state, str(path))
    loaded = load_state(str(path))
    assert loaded == state


def test_load_nonexistent_returns_none(tmp_path):
    path = tmp_path / "nonexistent.json"
    assert load_state(str(path)) is None
```

- [ ] **Step 3: 테스트 실행 — 실패 확인**

Run: `cd /Users/jk/workspace/skills-jk && python -m pytest tests/debate_review/test_state.py -v`
Expected: FAIL (모듈 없음)

- [ ] **Step 4: state.py 구현**

`lib/debate_review/state.py`:

```python
"""상태 파일 CRUD 및 스키마 생성."""

import json
import os
from datetime import datetime, timezone


def create_initial_state(
    *,
    repo: str,
    repo_root: str,
    pr_number: int,
    is_fork: bool,
    head_sha: str,
    pr_branch_name: str,
    max_rounds: int = 10,
    dry_run: bool = False,
) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "repo": repo,
        "repo_root": repo_root,
        "pr_number": pr_number,
        "is_fork": is_fork,
        "dry_run": dry_run,
        "max_rounds": max_rounds,
        "status": "in_progress",
        "current_round": 1,
        "head": {
            "initial_sha": head_sha,
            "last_observed_pr_sha": head_sha,
            "terminal_sha": None,
            "pr_branch_name": pr_branch_name,
            "target_ref": f"refs/debate-sync/pr-{pr_number}/head",
            "synced_worktree_sha": None,
        },
        "journal": {
            "round": 1,
            "step": "init",
            "pre_sync_head_sha": None,
            "post_sync_head_sha": None,
            "synced_worktree_sha": None,
            "applied_issue_ids": [],
            "failed_application_issue_ids": [],
            "commit_sha": None,
            "push_verified": False,
            "state_persisted": True,
        },
        "issues": {},
        "rounds": [],
        "final_comment_tag": None,
        "final_comment_id": None,
        "started_at": now,
        "finished_at": None,
        "final_outcome": None,
    }


def state_file_path(repo: str, pr_number: int, dry_run: bool = False) -> str:
    state_dir = os.path.expanduser("~/.claude/debate-state")
    os.makedirs(state_dir, exist_ok=True)
    key = repo.replace("/", "-")
    suffix = ".dry-run.json" if dry_run else ".json"
    return os.path.join(state_dir, f"{key}-{pr_number}{suffix}")


def load_state(path: str) -> dict | None:
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def save_state(state: dict, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)
```

- [ ] **Step 5: 테스트 실행 — 통과 확인**

Run: `cd /Users/jk/workspace/skills-jk && python -m pytest tests/debate_review/test_state.py -v`
Expected: PASS

- [ ] **Step 6: config.py 구현**

`lib/debate_review/config.py`:

```python
"""YAML config 로드."""

import yaml
import os


def load_config(path: str | None = None) -> dict:
    if path is None:
        path = os.path.expanduser(
            "~/workspace/skills-jk/config/cc-codex-debate-review.yml"
        )
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path) as f:
        return yaml.safe_load(f)
```

- [ ] **Step 7: gh.py 래퍼 구현**

`lib/debate_review/gh.py`:

```python
"""GitHub CLI 래퍼 — keyring 인증 사용."""

import json
import os
import subprocess


def gh(*args: str) -> str:
    env = {k: v for k, v in os.environ.items() if k not in ("GITHUB_TOKEN", "GH_TOKEN")}
    result = subprocess.run(
        ["gh", *args],
        capture_output=True,
        text=True,
        env=env,
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def gh_json(*args: str) -> dict | list:
    return json.loads(gh(*args))
```

- [ ] **Step 8: cli.py 기본 구조 + `init` subcommand + `show` subcommand**

`lib/debate_review/cli.py`:

```python
"""CLI 엔트리포인트 및 subcommand dispatch."""

import argparse
import json
import sys

from . import state as st
from . import config as cfg
from . import gh


def cmd_init(args):
    # PR 메타데이터 수집
    pr_meta = gh.gh_json(
        "pr", "view", str(args.pr), "--repo", args.repo,
        "--json", "headRefName,headRefOid,headRepositoryOwner",
    )
    head_sha = pr_meta["headRefOid"]
    pr_branch = pr_meta["headRefName"]
    head_owner = pr_meta["headRepositoryOwner"]["login"]
    repo_owner = args.repo.split("/")[0]
    is_fork = head_owner != repo_owner

    # repo_root 결정
    if args.repo_root:
        repo_root = args.repo_root
    else:
        import os
        workspace = os.environ.get("WORKSPACE_ROOT", os.path.expanduser("~/workspace"))
        repo_name = args.repo.split("/")[1]
        repo_root = os.path.join(workspace, repo_name)

    # config
    config = cfg.load_config(args.config)
    max_rounds = args.max_rounds or config.get("max_rounds", 10)

    # 상태 파일 경로
    dry_run = getattr(args, "dry_run", False)
    sf_path = st.state_file_path(args.repo, args.pr, dry_run=dry_run)

    # 기존 상태 확인
    existing = st.load_state(sf_path)
    if existing is not None:
        status = existing["status"]
        if status == "in_progress":
            result = {
                "state_file": sf_path,
                "status": "resumed",
                "current_round": existing["current_round"],
                "is_fork": existing["is_fork"],
            }
            print(json.dumps(result, indent=2))
            return
        # terminal
        if status in ("consensus_reached", "max_rounds_exceeded", "failed"):
            terminal_sha = existing["head"].get("terminal_sha")
            if terminal_sha == head_sha:
                result = {"state_file": sf_path, "status": "already_terminal"}
                print(json.dumps(result, indent=2))
                return
            # 다른 HEAD → 재초기화 (기존 아카이브)
            import shutil
            archive = sf_path + f".archive.{terminal_sha[:7]}"
            shutil.copy2(sf_path, archive)

    # 새 세션 생성
    new_state = st.create_initial_state(
        repo=args.repo,
        repo_root=repo_root,
        pr_number=args.pr,
        is_fork=is_fork,
        head_sha=head_sha,
        pr_branch_name=pr_branch,
        max_rounds=max_rounds,
        dry_run=dry_run,
    )
    st.save_state(new_state, sf_path)

    result = {
        "state_file": sf_path,
        "status": "created",
        "current_round": 1,
        "is_fork": is_fork,
        "dry_run": dry_run,
    }
    print(json.dumps(result, indent=2))


def cmd_show(args):
    state = st.load_state(args.state_file)
    if state is None:
        print(f"Error: state file not found: {args.state_file}", file=sys.stderr)
        sys.exit(1)
    if args.json:
        print(json.dumps(state, indent=2, ensure_ascii=False))
    else:
        s = state
        issues = s.get("issues", {})
        open_count = sum(1 for i in issues.values() if i["consensus_status"] == "open")
        print(f"Repo:    {s['repo']} PR #{s['pr_number']}")
        print(f"Status:  {s['status']}")
        print(f"Round:   {s['current_round']}")
        print(f"Issues:  {len(issues)} total, {open_count} open")
        print(f"Journal: round={s['journal']['round']} step={s['journal']['step']}")
        if s.get("dry_run"):
            print("Mode:    dry-run")


def build_parser():
    parser = argparse.ArgumentParser(prog="debate-review")
    sub = parser.add_subparsers(dest="command", required=True)

    # init
    p_init = sub.add_parser("init")
    p_init.add_argument("--repo", required=True)
    p_init.add_argument("--pr", type=int, required=True)
    p_init.add_argument("--repo-root", default=None)
    p_init.add_argument("--config", default=None)
    p_init.add_argument("--max-rounds", type=int, default=None)
    p_init.add_argument("--dry-run", action="store_true")

    # show
    p_show = sub.add_parser("show")
    p_show.add_argument("--state-file", required=True)
    p_show.add_argument("--json", action="store_true")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    commands = {
        "init": cmd_init,
        "show": cmd_show,
    }
    handler = commands.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()
        sys.exit(1)
```

- [ ] **Step 9: bin/debate-review 엔트리포인트**

`bin/debate-review`:

```python
#!/usr/bin/env python3
"""CC-Codex Debate Review State Management CLI."""

import sys
import os

# lib/ 디렉토리를 Python path에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

from debate_review.cli import main

if __name__ == "__main__":
    main()
```

`chmod +x bin/debate-review`

- [ ] **Step 10: __init__.py 파일 생성**

빈 파일: `lib/debate_review/__init__.py`, `tests/debate_review/__init__.py`

conftest: `tests/debate_review/conftest.py`:

```python
import pytest
from debate_review.state import create_initial_state


@pytest.fixture
def sample_state():
    return create_initial_state(
        repo="owner/repo",
        repo_root="/tmp/repo",
        pr_number=123,
        is_fork=False,
        head_sha="abc1234def5678",
        pr_branch_name="feat/test",
        max_rounds=10,
    )


@pytest.fixture
def state_file(tmp_path, sample_state):
    """상태 파일을 임시 경로에 저장하고 경로를 반환."""
    import json
    path = tmp_path / "test-state.json"
    with open(path, "w") as f:
        json.dump(sample_state, f)
    return str(path)
```

- [ ] **Step 11: 전체 테스트 실행**

Run: `cd /Users/jk/workspace/skills-jk && python -m pytest tests/debate_review/ -v`
Expected: PASS

- [ ] **Step 12: Commit**

```bash
git add pyproject.toml bin/debate-review lib/debate_review/ tests/debate_review/
git commit -m "feat: scaffold debate-review CLI with init, show, state CRUD"
```

---

## Task 2: issue_ops — issue upsert + issue_key 생성

**Files:**
- Create: `lib/debate_review/issue_ops.py`
- Create: `tests/debate_review/test_issue_ops.py`
- Modify: `lib/debate_review/cli.py` (upsert-issue subcommand 추가)

- [ ] **Step 1: issue_ops 테스트 작성**

`tests/debate_review/test_issue_ops.py`:

```python
import pytest
from debate_review.issue_ops import generate_issue_key, upsert_issue

# --- issue_key 생성 ---

def test_issue_key_canonical_kind():
    key = generate_issue_key(criterion=3, file="src/foo.ts", anchor="retry", message="x")
    assert key == "criterion:3|file:src/foo.ts|anchor:retry|kind:unbounded_loop"


def test_issue_key_fallback_sha1():
    key = generate_issue_key(criterion=99, file="src/bar.ts", anchor="line10", message="some issue")
    assert key.startswith("criterion:99|file:src/bar.ts|anchor:line10|msg:")
    assert len(key.split("|msg:")[1]) == 12  # sha1[:12]


# --- upsert: 새 issue 생성 ---

def test_upsert_creates_new_issue(sample_state):
    result = upsert_issue(
        sample_state,
        agent="codex", round_num=1, severity="warning",
        criterion=3, file="src/foo.ts", line=42,
        anchor="retry", message="unbounded retry",
    )
    assert result["action"] == "created"
    isu_id = result["issue_id"]
    assert isu_id in sample_state["issues"]
    issue = sample_state["issues"][isu_id]
    assert issue["opened_by"] == "codex"
    assert issue["consensus_status"] == "open"
    assert issue["accepted_by"] == ["codex"]
    assert issue["application_status"] == "pending"
    assert len(issue["reports"]) == 1


# --- upsert: 기존 issue에 report 추가 ---

def test_upsert_appends_report_to_existing(sample_state):
    upsert_issue(
        sample_state,
        agent="codex", round_num=1, severity="warning",
        criterion=3, file="src/foo.ts", line=42,
        anchor="retry", message="unbounded retry",
    )
    result = upsert_issue(
        sample_state,
        agent="cc", round_num=2, severity="warning",
        criterion=3, file="src/foo.ts", line=42,
        anchor="retry", message="still unbounded",
    )
    assert result["action"] == "appended"
    issue = sample_state["issues"][result["issue_id"]]
    assert len(issue["reports"]) == 2
    assert set(issue["accepted_by"]) == {"codex", "cc"}


# --- withdrawn issue reopen ---

def test_upsert_reopens_withdrawn_issue(sample_state):
    r1 = upsert_issue(
        sample_state,
        agent="codex", round_num=1, severity="warning",
        criterion=3, file="src/foo.ts", line=42,
        anchor="retry", message="unbounded retry",
    )
    isu_id = r1["issue_id"]
    # withdraw 시뮬레이션
    issue = sample_state["issues"][isu_id]
    issue["consensus_status"] = "withdrawn"
    issue["accepted_by"] = []
    issue["application_status"] = "not_applicable"
    issue["reports"][0]["status"] = "withdrawn"

    r2 = upsert_issue(
        sample_state,
        agent="cc", round_num=3, severity="warning",
        criterion=3, file="src/foo.ts", line=45,
        anchor="retry", message="still an issue",
    )
    assert r2["action"] == "appended"
    issue = sample_state["issues"][isu_id]
    assert issue["consensus_status"] == "open"
    assert issue["accepted_by"] == ["cc"]
    assert issue["application_status"] == "pending"


# --- applied issue re-discovery ---

def test_upsert_resets_applied_issue(sample_state):
    r1 = upsert_issue(
        sample_state,
        agent="codex", round_num=1, severity="warning",
        criterion=3, file="src/foo.ts", line=42,
        anchor="retry", message="unbounded retry",
    )
    isu_id = r1["issue_id"]
    issue = sample_state["issues"][isu_id]
    issue["consensus_status"] = "accepted"
    issue["accepted_by"] = ["codex", "cc"]
    issue["application_status"] = "applied"
    issue["applied_by"] = "codex"
    issue["application_commit_sha"] = "abc123"

    r2 = upsert_issue(
        sample_state,
        agent="cc", round_num=3, severity="warning",
        criterion=3, file="src/foo.ts", line=42,
        anchor="retry", message="fix was insufficient",
    )
    assert r2["action"] == "appended"
    issue = sample_state["issues"][isu_id]
    assert issue["consensus_status"] == "open"
    assert issue["accepted_by"] == ["cc"]
    assert issue["application_status"] == "pending"
    assert issue["applied_by"] is None
```

- [ ] **Step 2: 테스트 실행 — 실패 확인**

- [ ] **Step 3: issue_ops.py 구현**

`lib/debate_review/issue_ops.py`:

```python
"""Issue upsert, issue_key 생성, consensus 계산."""

import hashlib
import re

CANONICAL_KINDS = {
    1: "missing_validation",
    2: "missing_error_handling",
    3: "unbounded_loop",
    4: "wrong_target_ref",
    5: "stale_state_transition",
    6: "unused_variable",
    7: "hardcoded_value",
    8: "duplicate_logic",
    9: "security_injection",
    10: "race_condition",
    11: "resource_leak",
    12: "wrong_scope",
    13: "incorrect_algorithm",
    14: "missing_test",
    15: "doc_mismatch",
}


def normalize_message(msg: str) -> str:
    s = msg.lower()
    s = re.sub(r"[^\w\s]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    # 라인 번호, 파일 경로 패턴 제거
    s = re.sub(r"\b(line\s*)?\d+\b", "", s)
    s = re.sub(r"[\w/]+\.\w+", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def generate_issue_key(*, criterion: int, file: str, anchor: str, message: str) -> str:
    kind = CANONICAL_KINDS.get(criterion)
    if kind:
        return f"criterion:{criterion}|file:{file}|anchor:{anchor}|kind:{kind}"
    # fallback
    normalized = normalize_message(message)
    sha = hashlib.sha1(normalized.encode()).hexdigest()[:12]
    return f"criterion:{criterion}|file:{file}|anchor:{anchor}|msg:{sha}"


def _next_id(prefix: str, existing: dict) -> str:
    max_n = 0
    for key in existing:
        if key.startswith(prefix):
            try:
                n = int(key[len(prefix):])
                max_n = max(max_n, n)
            except ValueError:
                pass
    return f"{prefix}{max_n + 1:03d}"


def _next_report_id(state: dict) -> str:
    all_reports = []
    for issue in state.get("issues", {}).values():
        for r in issue.get("reports", []):
            all_reports.append(r["report_id"])
    return _next_id("rpt_", {r: True for r in all_reports})


def upsert_issue(
    state: dict,
    *,
    agent: str,
    round_num: int,
    severity: str,
    criterion: int,
    file: str,
    line: int,
    anchor: str,
    message: str,
) -> dict:
    issue_key = generate_issue_key(
        criterion=criterion, file=file, anchor=anchor, message=message,
    )

    # 기존 issue 탐색
    existing_id = None
    for isu_id, issue in state.get("issues", {}).items():
        if issue["issue_key"] == issue_key:
            existing_id = isu_id
            break

    report_id = _next_report_id(state)
    report = {
        "report_id": report_id,
        "agent": agent,
        "round": round_num,
        "file": file,
        "line": line,
        "message": message,
        "status": "open",
    }

    if existing_id:
        issue = state["issues"][existing_id]

        # withdrawn → reopen
        if issue["consensus_status"] == "withdrawn":
            issue["consensus_status"] = "open"
            issue["application_status"] = "pending"
            issue["consensus_reason"] = None
            issue["accepted_by"] = [agent]

        # applied → re-discovery
        elif issue["application_status"] == "applied":
            issue["consensus_status"] = "open"
            issue["accepted_by"] = [agent]
            issue["application_status"] = "pending"
            issue["applied_by"] = None
            issue["application_commit_sha"] = None

        else:
            # 일반 append
            if agent not in issue["accepted_by"]:
                issue["accepted_by"].append(agent)

        issue["reports"].append(report)
        return {
            "issue_id": existing_id,
            "report_id": report_id,
            "action": "appended",
            "issue_key": issue_key,
        }

    # 새 issue 생성
    isu_id = _next_id("isu_", state.get("issues", {}))
    state.setdefault("issues", {})[isu_id] = {
        "id": isu_id,
        "issue_key": issue_key,
        "opened_by": agent,
        "introduced_in_round": round_num,
        "severity": severity,
        "criterion": criterion,
        "file": file,
        "line": line,
        "message": message,
        "reports": [report],
        "consensus_status": "open",
        "consensus_reason": None,
        "accepted_by": [agent],
        "application_status": "pending",
        "applied_by": None,
        "application_commit_sha": None,
    }
    return {
        "issue_id": isu_id,
        "report_id": report_id,
        "action": "created",
        "issue_key": issue_key,
    }
```

- [ ] **Step 4: 테스트 통과 확인**

- [ ] **Step 5: cli.py에 upsert-issue subcommand 추가**

`build_parser()`에 추가:

```python
    # upsert-issue
    p_upsert = sub.add_parser("upsert-issue")
    p_upsert.add_argument("--state-file", required=True)
    p_upsert.add_argument("--agent", required=True, choices=["cc", "codex"])
    p_upsert.add_argument("--round", type=int, required=True)
    p_upsert.add_argument("--severity", required=True, choices=["critical", "warning", "suggestion"])
    p_upsert.add_argument("--criterion", type=int, required=True)
    p_upsert.add_argument("--file", required=True)
    p_upsert.add_argument("--line", type=int, required=True)
    p_upsert.add_argument("--anchor", required=True)
    p_upsert.add_argument("--message", required=True)
```

`cmd_upsert_issue(args)` 함수 + commands dict에 등록.

- [ ] **Step 6: Commit**

```bash
git add lib/debate_review/issue_ops.py tests/debate_review/test_issue_ops.py lib/debate_review/cli.py
git commit -m "feat: implement upsert-issue with issue_key generation and consensus rules"
```

---

## Task 3: round_ops — record-verdict + settle-round

**Files:**
- Create: `lib/debate_review/round_ops.py`
- Create: `tests/debate_review/test_round_ops.py`
- Modify: `lib/debate_review/cli.py`

- [ ] **Step 1: round_ops 테스트 작성**

`tests/debate_review/test_round_ops.py` — 핵심 테스트:

```python
from debate_review.round_ops import record_verdict, settle_round, init_round

def test_record_verdict_has_findings(sample_state):
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    result = record_verdict(sample_state, round_num=1, verdict="has_findings")
    assert result["clean_pass"] is False
    assert sample_state["rounds"][0]["step1"]["verdict"] == "has_findings"

def test_record_verdict_clean_pass(sample_state):
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    result = record_verdict(sample_state, round_num=1, verdict="no_findings_mergeable")
    assert result["clean_pass"] is True
    assert sample_state["rounds"][0]["clean_pass"] is True

def test_settle_round_continue(sample_state):
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    record_verdict(sample_state, round_num=1, verdict="has_findings")
    result = settle_round(sample_state, round_num=1)
    assert result["result"] == "continue"
    assert sample_state["current_round"] == 2

def test_settle_round_consensus(sample_state):
    # Round 1: clean pass (codex lead)
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    record_verdict(sample_state, round_num=1, verdict="no_findings_mergeable")
    settle_round(sample_state, round_num=1)
    # Round 2: clean pass (cc lead)
    init_round(sample_state, round_num=2, lead_agent="cc", synced_head_sha="abc")
    record_verdict(sample_state, round_num=2, verdict="no_findings_mergeable")
    result = settle_round(sample_state, round_num=2)
    assert result["result"] == "consensus_reached"
    assert sample_state["status"] == "consensus_reached"

def test_settle_round_max_rounds(sample_state):
    sample_state["max_rounds"] = 1
    init_round(sample_state, round_num=1, lead_agent="codex", synced_head_sha="abc")
    record_verdict(sample_state, round_num=1, verdict="has_findings")
    result = settle_round(sample_state, round_num=1)
    assert result["result"] == "max_rounds_exceeded"
```

- [ ] **Step 2: 테스트 실행 — 실패 확인**

- [ ] **Step 3: round_ops.py 구현**

`init_round()`, `record_verdict()`, `settle_round()` — clean pass 조건 검증, 연속 2-round clean pass 판정, max_rounds 체크.

- [ ] **Step 4: 테스트 통과 확인**

- [ ] **Step 5: cli.py에 record-verdict, settle-round 추가**

- [ ] **Step 6: Commit**

```bash
git commit -m "feat: implement record-verdict and settle-round with consensus logic"
```

---

## Task 4: cross_verification — record-cross-verification + resolve-rebuttals

**Files:**
- Create: `lib/debate_review/cross_verification.py`
- Create: `tests/debate_review/test_cross_verification.py`
- Modify: `lib/debate_review/cli.py`

- [ ] **Step 1: 테스트 작성**

핵심 케이스:
- `record_cross_verification`: accept → `accepted_by` 추가, consensus_status 갱신. rebut → `step2.rebuttals` 기록.
- `resolve_rebuttals` step=1a: withdraw → report withdrawn, accepted_by 재계산. maintain → 재보고 대상.
- `resolve_rebuttals` step=3: withdraw → 동일. accept (cross-findings용) → accepted_by 추가. rebut → step3.rebuttals 기록.

- [ ] **Step 2: 테스트 실행 — 실패 확인**

- [ ] **Step 3: cross_verification.py 구현**

`record_cross_verification()`, `resolve_rebuttals()` — `accepted_by` 재계산 로직 포함.

- [ ] **Step 4: 테스트 통과 확인**

- [ ] **Step 5: cli.py에 subcommand 추가**

- [ ] **Step 6: Commit**

```bash
git commit -m "feat: implement cross-verification and resolve-rebuttals"
```

---

## Task 5: application — record-application 3-phase

**Files:**
- Create: `lib/debate_review/application.py`
- Create: `tests/debate_review/test_application.py`
- Modify: `lib/debate_review/cli.py`

- [ ] **Step 1: 테스트 작성**

Phase 1 (applied/failed 기록), Phase 2 (commit-sha), Phase 3 (verify-push). 각 phase의 idempotency 테스트 포함.

- [ ] **Step 2: 테스트 실행 — 실패 확인**

- [ ] **Step 3: application.py 구현**

- [ ] **Step 4: 테스트 통과 확인**

- [ ] **Step 5: cli.py에 record-application 추가 (3가지 호출 형태 지원)**

- [ ] **Step 6: Commit**

```bash
git commit -m "feat: implement record-application with 3-phase checkpoint"
```

---

## Task 6: sync — sync-head

**Files:**
- Create: `lib/debate_review/sync.py`
- Create: `tests/debate_review/test_sync.py`
- Modify: `lib/debate_review/cli.py`

- [ ] **Step 1: 테스트 작성**

git 조작은 subprocess mock으로 테스트. 핵심: supersede 판정 로직 (pre != post이고 이전 commit_sha가 아닌 경우).

- [ ] **Step 2: 테스트 실행 — 실패 확인**

- [ ] **Step 3: sync.py 구현**

`sync_head()` — gh pr view, git fetch, worktree add/reset, supersede 판정.

- [ ] **Step 4: 테스트 통과 확인**

- [ ] **Step 5: cli.py에 sync-head 추가**

- [ ] **Step 6: Commit**

```bash
git commit -m "feat: implement sync-head with worktree management and supersede detection"
```

---

## Task 7: comment — post-comment

**Files:**
- Create: `lib/debate_review/comment.py`
- Create: `tests/debate_review/test_comment.py`
- Modify: `lib/debate_review/cli.py`

- [ ] **Step 1: 테스트 작성**

4개 코멘트 템플릿 생성, 중복 확인 로직, --no-comment 동작.

- [ ] **Step 2: 테스트 실행 — 실패 확인**

- [ ] **Step 3: comment.py 구현**

- [ ] **Step 4: 테스트 통과 확인**

- [ ] **Step 5: cli.py에 post-comment 추가**

- [ ] **Step 6: Commit**

```bash
git commit -m "feat: implement post-comment with templates and dedup"
```

---

## Task 8: CLI 통합 테스트

**Files:**
- Create: `tests/debate_review/test_cli.py`

- [ ] **Step 1: 통합 테스트 작성**

`subprocess.run`으로 `bin/debate-review` 실행, init → upsert-issue → record-verdict → settle-round 흐름 테스트. (gh 호출은 mock 필요하므로 상태 파일 기반 subcommand만 직접 테스트.)

- [ ] **Step 2: 테스트 통과 확인**

- [ ] **Step 3: 전체 테스트 스위트 실행**

Run: `python -m pytest tests/debate_review/ -v --tb=short`
Expected: 모든 테스트 PASS

- [ ] **Step 4: Commit**

```bash
git commit -m "test: add CLI integration tests for debate-review"
```

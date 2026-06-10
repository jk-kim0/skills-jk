from __future__ import annotations

import importlib.util
import io
import json
import sys
from contextlib import redirect_stderr, redirect_stdout
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "bin" / "gh-runners"


def load_module(module_name: str = "gh_runners_under_test"):
    loader = SourceFileLoader(module_name, str(SCRIPT_PATH))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_build_parser_defaults_to_querypie_and_supports_busy_repo_flags() -> None:
    gh_runners = load_module("gh_runners_parser_test")

    parser = gh_runners.build_parser()
    args = parser.parse_args([
        "--org",
        "querypie",
        "--summarized",
        "--show-labels",
        "--busy-repo",
        "querypie/querypie-mono",
        "--busy-repo",
        "corp-web-app",
    ])

    assert args.org == "querypie"
    assert args.summarized is True
    assert args.show_labels is True
    assert args.busy_repo == ["querypie/querypie-mono", "corp-web-app"]
    assert args.scan_all_repos is False
    assert args.no_busy_jobs is False


def test_normalize_busy_repos_prefixes_bare_repo_names() -> None:
    gh_runners = load_module("gh_runners_repo_normalize_test")

    repos = gh_runners._normalize_busy_repos(
        "querypie",
        ["querypie/querypie-docs", "corp-web-app", "  corp-web-japan  "],
    )

    assert repos == [
        "querypie/querypie-docs",
        "querypie/corp-web-app",
        "querypie/corp-web-japan",
    ]


def test_default_busy_repos_are_top_runner_usage_repos() -> None:
    gh_runners = load_module("gh_runners_default_busy_repos_test")

    assert gh_runners._default_busy_repos("querypie") == [
        "querypie/corp-web-app",
        "querypie/corp-web-japan",
        "querypie/outbound-agent",
        "querypie/corp-web-contents",
        "querypie/payroll",
    ]


def test_list_org_repositories_skips_archived_and_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    gh_runners = load_module("gh_runners_org_repo_test")

    client = gh_runners.GitHubRunnersClient(token="token", org_name="querypie")

    monkeypatch.setattr(
        client,
        "_paginate",
        lambda url, data_key=None: [
            {"full_name": "querypie/querypie-mono", "archived": False, "disabled": False},
            {"full_name": "querypie/old-repo", "archived": True, "disabled": False},
            {"full_name": "querypie/disabled-repo", "archived": False, "disabled": True},
            {"full_name": "querypie/corp-web-app", "archived": False, "disabled": False},
        ],
    )

    assert client.list_org_repositories() == [
        "querypie/querypie-mono",
        "querypie/corp-web-app",
    ]


def test_format_runner_table_summarized_uses_busy_job_details() -> None:
    gh_runners = load_module("gh_runners_table_test")

    runners = [
        {
            "id": 24,
            "name": "mac-studio-llm1-linux-arm64-2",
            "status": "online",
            "busy": True,
            "labels": [
                {"name": "self-hosted"},
                {"name": "Linux"},
                {"name": "purpose:ci"},
            ],
        },
        {
            "id": 21,
            "name": "mac-studio-llm1-linux-arm64-1",
            "status": "offline",
            "busy": False,
            "labels": [],
        },
    ]
    busy_jobs = {
        "mac-studio-llm1-linux-arm64-2": {
            "repo": "querypie-mono",
            "workflow_name": "CI",
            "job_name": "build",
            "elapsed": "3m 12s",
            "display_title": "Build main",
            "event": "push",
            "actor": "jk",
            "branch": "main",
            "job_url": "https://example.com/job",
            "run_url": "https://example.com/run",
            "pr_number": "#123",
        }
    }

    output, separator_len = gh_runners.format_runner_table_summarized(runners, busy_jobs, show_labels=True)

    assert separator_len > 0
    assert "querypie-mono" in output
    assert "CI" in output
    assert "purpose:ci" in output
    assert "Busy Runner Jobs" in output
    assert "#123 Build main" in output


def test_main_json_output_uses_default_top_busy_repos_when_busy_repo_not_given(monkeypatch: pytest.MonkeyPatch) -> None:
    gh_runners = load_module("gh_runners_main_json_test")

    class FakeClient:
        def __init__(self, token: str, org_name: str, base_url: str = gh_runners.GITHUB_API_BASE):
            self.token = token
            self.org_name = org_name
            self.base_url = base_url

        def list_runners(self):
            return [
                {"id": 1, "name": "runner-1", "status": "online", "busy": True, "labels": []}
            ]

        def list_org_repositories(self, include_archived: bool = False):
            raise AssertionError("default scan should not list every org repository")

        def get_busy_runner_jobs(self, busy_runner_names, repos_to_scan):
            assert busy_runner_names == ["runner-1"]
            assert repos_to_scan == [
                "querypie/corp-web-app",
                "querypie/corp-web-japan",
                "querypie/outbound-agent",
                "querypie/corp-web-contents",
                "querypie/payroll",
            ]
            return {
                "runner-1": {
                    "repo": "querypie-mono",
                    "workflow_name": "CI",
                    "job_name": "build",
                    "elapsed": "10s",
                    "display_title": "Build main",
                    "event": "push",
                    "actor": "jk",
                    "branch": "main",
                    "job_url": "https://example.com/job",
                    "run_url": "https://example.com/run",
                    "pr_number": "",
                }
            }

    monkeypatch.setattr(gh_runners, "GitHubRunnersClient", FakeClient)
    monkeypatch.setattr(gh_runners, "get_token", lambda: "token")

    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        exit_code = gh_runners.main(["--json"])

    payload = json.loads(stdout.getvalue())
    assert exit_code == 0
    assert payload["organization"] == "querypie"
    assert payload["busy_job_scan_repos"] == [
        "querypie/corp-web-app",
        "querypie/corp-web-japan",
        "querypie/outbound-agent",
        "querypie/corp-web-contents",
        "querypie/payroll",
    ]
    assert payload["busy_jobs"]["runner-1"]["workflow_name"] == "CI"
    assert "Scanning 5 repo(s)" in stderr.getvalue()

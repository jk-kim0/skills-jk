from __future__ import annotations

import importlib.util
import subprocess
import sys
import types
from importlib.machinery import SourceFileLoader
from pathlib import Path
from types import SimpleNamespace


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "bin" / "gsc"


def install_google_module_stubs() -> None:
    google = sys.modules.setdefault("google", types.ModuleType("google"))
    google.auth = sys.modules.setdefault("google.auth", types.ModuleType("google.auth"))
    google.auth.transport = sys.modules.setdefault("google.auth.transport", types.ModuleType("google.auth.transport"))
    google.auth.transport.requests = sys.modules.setdefault(
        "google.auth.transport.requests",
        types.ModuleType("google.auth.transport.requests"),
    )
    google.auth.transport.requests.Request = object

    google.oauth2 = sys.modules.setdefault("google.oauth2", types.ModuleType("google.oauth2"))
    google.oauth2.credentials = sys.modules.setdefault(
        "google.oauth2.credentials",
        types.ModuleType("google.oauth2.credentials"),
    )
    google.oauth2.credentials.Credentials = object

    oauthlib = sys.modules.setdefault("google_auth_oauthlib", types.ModuleType("google_auth_oauthlib"))
    oauthlib.flow = sys.modules.setdefault("google_auth_oauthlib.flow", types.ModuleType("google_auth_oauthlib.flow"))
    oauthlib.flow.InstalledAppFlow = object

    googleapiclient = sys.modules.setdefault("googleapiclient", types.ModuleType("googleapiclient"))
    googleapiclient.discovery = sys.modules.setdefault(
        "googleapiclient.discovery",
        types.ModuleType("googleapiclient.discovery"),
    )
    googleapiclient.discovery.build = lambda *args, **kwargs: object()


def load_gsc_module(module_name: str = "gsc_cli_under_test"):
    install_google_module_stubs()
    loader = SourceFileLoader(module_name, str(SCRIPT_PATH))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_select_validation_sites_skips_domain_properties_by_default() -> None:
    gsc = load_gsc_module("gsc_select_validation_sites_test")

    selected, skipped = gsc.select_validation_sites(
        [
            {"siteUrl": "sc-domain:querypie.com"},
            {"siteUrl": "https://www.querypie.com/"},
            {"siteUrl": "https://docs.querypie.com/"},
        ]
    )

    assert selected == ["https://www.querypie.com/", "https://docs.querypie.com/"]
    assert skipped == [("sc-domain:querypie.com", "domain property skipped by default")]


def test_validate_index_issues_alias_can_build_browser_command() -> None:
    gsc = load_gsc_module("gsc_validate_alias_browser_test")
    args = SimpleNamespace(
        submit=True,
        only_status="all",
        include_started=False,
        issue_limit=3,
        limit=None,
        delay_ms=250,
        connect_timeout_ms=120000,
        port=9222,
    )

    cmd = gsc.build_validate_index_issues_browser_cmd(args, "https://www.querypie.com/")

    assert cmd[0].endswith("gsc-browser-indexing")
    assert cmd[1:] == [
        "--site",
        "https://www.querypie.com/",
        "--index-issues",
        "--submit",
        "--only-status",
        "all",
        "--limit",
        "3",
        "--delay-ms",
        "250",
        "--port",
        "9222",
        "--connect-timeout-ms",
        "120000",
    ]


def test_validate_index_issues_browser_batch_reuses_one_helper_process() -> None:
    gsc = load_gsc_module("gsc_validate_browser_batch_test")
    args = SimpleNamespace(
        submit=True,
        only_status="Failed",
        include_started=False,
        output_json=False,
        issue_limit=1,
        limit=None,
        delay_ms=250,
        site_delay_ms=500,
        connect_timeout_ms=120000,
        port=9222,
    )

    cmd = gsc.build_validate_index_issues_browser_batch_cmd(
        args,
        ["https://docs.querypie.com/", "https://querypie.ai/"],
    )

    assert cmd.count("--site") == 2
    assert "https://docs.querypie.com/" in cmd
    assert "https://querypie.ai/" in cmd
    assert cmd[-2:] == ["--site-delay-ms", "500"]



def test_validate_index_issues_output_json_is_opt_in() -> None:
    gsc = load_gsc_module("gsc_validate_output_json_opt_in_test")
    args = SimpleNamespace(
        submit=False,
        session_file="/tmp/frontend-session.json",
        only_status="actionable",
        include_started=False,
        sitemap=None,
        all_sitemaps=False,
        output_json=False,
        issue_limit=2,
        limit=None,
        delay_ms=0,
    )

    default_cmd = gsc.build_validate_index_issues_frontend_cmd(args, "https://www.querypie.com/")
    assert "--output-json" not in default_cmd

    args.output_json = True
    json_cmd = gsc.build_validate_index_issues_frontend_cmd(args, "https://www.querypie.com/")
    assert "--output-json" in json_cmd


def test_validate_index_issues_sitemap_filter_arguments_are_forwarded() -> None:
    gsc = load_gsc_module("gsc_validate_sitemap_filter_args_test")
    args = SimpleNamespace(
        submit=False,
        session_file="/tmp/frontend-session.json",
        only_status="actionable",
        include_started=False,
        sitemap="/sitemap.xml",
        all_sitemaps=False,
        output_json=False,
        issue_limit=2,
        limit=None,
        delay_ms=0,
        port=9222,
        connect_timeout_ms=120000,
    )

    frontend_cmd = gsc.build_validate_index_issues_frontend_cmd(args, "https://www.querypie.com/")
    browser_cmd = gsc.build_validate_index_issues_browser_cmd(args, "https://www.querypie.com/")

    for cmd in (frontend_cmd, browser_cmd):
        assert "--sitemap" in cmd
        assert cmd[cmd.index("--sitemap") + 1] == "/sitemap.xml"
        assert "--all-sitemaps" not in cmd

    args.sitemap = None
    args.all_sitemaps = True
    frontend_all_cmd = gsc.build_validate_index_issues_frontend_cmd(args, "https://www.querypie.com/")
    browser_all_cmd = gsc.build_validate_index_issues_browser_cmd(args, "https://www.querypie.com/")
    assert "--all-sitemaps" in frontend_all_cmd
    assert "--all-sitemaps" in browser_all_cmd



def test_validation_helpers_default_to_table_report_and_gate_json_output() -> None:
    frontend_source = (SCRIPT_PATH.parent / "gsc-frontend-indexing").read_text()
    browser_source = (SCRIPT_PATH.parent / "gsc-browser-indexing").read_text()

    for source in (frontend_source, browser_source):
        assert "--output-json" in source
        assert "--sitemap" in source
        assert "--all-sitemaps" in source
        assert "sitemap=" in source
        assert "const ISSUE_COLUMNS = [" in source
        assert "['SITE', 34]" in source
        assert "['VALIDATION', 13]" in source
        assert "['PAGES', 7]" in source
        assert "['OUTCOME', 15]" in source
        assert "['ACTION', 12]" in source
        assert "['REASON', 56]" in source
        assert "function printIssueReportHeader" in source
        assert "function printIssueReportRow" in source
        assert "function printIssueReportSummary" in source
        assert "if (args.outputJson)" in source

    assert "mode: 'index-issues-frontend'" in frontend_source
    assert "mode: 'index-issues'" in browser_source



def test_validate_index_issues_site_timeout_returns_process_style_124(monkeypatch, capsys) -> None:
    gsc = load_gsc_module("gsc_validate_site_timeout_test")

    def fake_run(cmd, timeout=None):
        assert cmd == ["helper"]
        assert timeout == 1.5
        raise subprocess.TimeoutExpired(cmd, timeout)

    monkeypatch.setattr(gsc.subprocess, "run", fake_run)

    assert gsc.run_validate_index_issues_site(["helper"], timeout_ms=1500) == 124
    assert "timed out after 1500ms" in capsys.readouterr().out


def test_validate_all_frontend_submit_does_not_fallback_to_browser(monkeypatch, capsys) -> None:
    gsc = load_gsc_module("gsc_validate_all_no_browser_fallback_test")
    args = SimpleNamespace(
        submit=True,
        include_domain_properties=False,
        site=["https://www.querypie.com/"],
        limit_sites=None,
        only_status="actionable",
        include_started=False,
        issue_limit=1,
        limit=None,
        delay_ms=0,
        site_delay_ms=0,
        session_file="/tmp/frontend-session.json",
        site_timeout_ms=180000,
    )

    monkeypatch.setattr(gsc, "get_site_entries", lambda: [{"siteUrl": "https://www.querypie.com/"}])

    def fake_run(cmd, timeout_ms=None):
        assert cmd[0].endswith("gsc-frontend-indexing")
        assert "gsc-browser-indexing" not in " ".join(cmd)
        assert "--submit" in cmd
        return 7

    monkeypatch.setattr(gsc, "run_validate_index_issues_site", fake_run)

    def forbidden_browser_cmd(*_args, **_kwargs):
        raise AssertionError("browser fallback must not be built for validate-index-issues-all")

    monkeypatch.setattr(gsc, "build_validate_index_issues_browser_cmd", forbidden_browser_cmd)

    assert gsc.validate_all_index_issues(args, browser=False) == 1
    out = capsys.readouterr().out
    assert "FAIL(7) https://www.querypie.com/" in out
    assert "browser fallback" not in out


def test_browser_helper_reuses_drilldown_resource_id_for_validation_url() -> None:
    source = (SCRIPT_PATH.parent / "gsc-browser-indexing").read_text()

    assert "function validationUrlFromDrilldownHref(drilldownHref)" in source
    assert "function clickSeeDetailsOnDrilldown(input)" in source
    assert "accounts.google.com/" in source
    assert "Search Console login tab" in source
    assert "function getIssueRowRect(input)" in source
    assert "function getSeeDetailsRect(input)" in source
    assert "await client.clickPoint(rowTarget.x, rowTarget.y" in source
    assert "await client.clickPoint(detailsTarget.x, detailsTarget.y" in source
    assert "validationStatus: issue.validation" in source
    assert "could not locate validation SEE DETAILS or VALIDATE FIX on drilldown page" in source
    assert "Validation\\s+(Failed|Not started|Started|Passed)" in source
    assert "url.pathname = '/search-console/index/validation';" in source
    assert "const validationUrl = validationUrlFromDrilldownHref(drilldownHref);" not in source
    assert "gscValidationResourceId" not in source


def test_browser_helper_prefers_validation_failed_see_details_context() -> None:
    source = (SCRIPT_PATH.parent / "gsc-browser-indexing").read_text()

    assert "const desiredStatus = normalize(input && input.validationStatus).toLowerCase();" in source
    assert "const desiredReason = normalize(input && input.reason).toLowerCase();" in source
    assert "lower.includes('validation failed')" in source
    assert "if (desiredStatus && lower.includes(desiredStatus)) score += 10;" in source
    assert "if (lower.includes('validation failed')) score += 8;" in source
    assert "sort((a, b) => b.score - a.score)" in source

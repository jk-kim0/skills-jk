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



def test_validate_index_issues_site_timeout_returns_process_style_124(monkeypatch, capsys) -> None:
    gsc = load_gsc_module("gsc_validate_site_timeout_test")

    def fake_run(cmd, timeout=None):
        assert cmd == ["helper"]
        assert timeout == 1.5
        raise subprocess.TimeoutExpired(cmd, timeout)

    monkeypatch.setattr(gsc.subprocess, "run", fake_run)

    assert gsc.run_validate_index_issues_site(["helper"], timeout_ms=1500) == 124
    assert "timed out after 1500ms" in capsys.readouterr().out


def test_browser_helper_reuses_drilldown_resource_id_for_validation_url() -> None:
    source = (SCRIPT_PATH.parent / "gsc-browser-indexing").read_text()

    assert "function validationUrlFromDrilldownHref(drilldownHref)" in source
    assert "function clickSeeDetailsOnDrilldown(input)" in source
    assert "accounts.google.com/" in source
    assert "Search Console login tab" in source
    assert "url.pathname = '/search-console/index/validation';" in source
    assert "const detailsClicked = await client.evaluate(clickSeeDetailsOnDrilldown" in source
    assert "const validationUrl = validationUrlFromDrilldownHref(drilldownHref);" in source
    assert "gscValidationResourceId" not in source

from __future__ import annotations

import importlib.util
import io
import sys
from contextlib import redirect_stdout
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "bin" / "ga"


def load_ga_module(module_name: str = "ga_cli_under_test"):
    loader = SourceFileLoader(module_name, str(SCRIPT_PATH))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_build_parser_includes_hosts_subcommand() -> None:
    ga = load_ga_module("ga_cli_parser_test")

    parser = ga.build_parser()
    args = parser.parse_args(["hosts", "451236681", "--days", "30", "--limit", "25"])

    assert args.command == "hosts"
    assert args.property_id == "451236681"
    assert args.days == 30
    assert args.limit == 25


def test_run_hosts_report_uses_hostname_dimension(monkeypatch: pytest.MonkeyPatch) -> None:
    ga = load_ga_module("ga_cli_hosts_report_test")

    captured_request = None

    class FakeValue:
        def __init__(self, value: str):
            self.value = value

    class FakeRow:
        def __init__(self, dimension_values, metric_values):
            self.dimension_values = dimension_values
            self.metric_values = metric_values

    class FakeResponse:
        def __init__(self):
            self.rows = [
                FakeRow(
                    [FakeValue("customer1.example.com")],
                    [
                        FakeValue("120"),
                        FakeValue("80"),
                        FakeValue("640"),
                        FakeValue("0.125"),
                        FakeValue("300.0"),
                    ],
                )
            ]
            self.totals = []

    class FakeClient:
        def __init__(self, credentials=None):
            self.credentials = credentials

        def run_report(self, request):
            nonlocal captured_request
            captured_request = request
            return FakeResponse()

    monkeypatch.setattr(ga, "get_credentials", lambda: object())
    monkeypatch.setattr(ga, "BetaAnalyticsDataClient", FakeClient)

    stdout = io.StringIO()
    with redirect_stdout(stdout):
        ga.run_hosts_report("451236681", days=30, limit=25)

    output = stdout.getvalue()
    assert captured_request is not None
    assert [dimension.name for dimension in captured_request.dimensions] == ["hostName"]
    assert [metric.name for metric in captured_request.metrics] == [
        "sessions",
        "activeUsers",
        "screenPageViews",
        "bounceRate",
        "averageSessionDuration",
    ]
    assert captured_request.limit == 25
    assert "Host name" in output
    assert "customer1.example.com" in output

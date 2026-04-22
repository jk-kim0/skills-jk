from __future__ import annotations

import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest


def load_watchdog_module():
    script_path = Path(__file__).resolve().parents[1] / "bin" / "hermes-gateway-watchdog"
    loader = SourceFileLoader("hermes_gateway_watchdog", str(script_path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_restart_is_requested_when_telegram_api_recovers() -> None:
    watchdog = load_watchdog_module()

    probe = watchdog.ProbeResult(
        gateway_running=True,
        gateway_pid=1234,
        gateway_status_summary="running",
        telegram_api_ok=True,
        telegram_api_transport="direct",
        telegram_dns_ok=True,
        fallback_api_ok=False,
        recent_connect_failure=False,
        error_fingerprint=None,
    )
    state = watchdog.WatchdogState(last_api_ok=False)

    action = watchdog.decide_repair_action(probe, state)

    assert action == ("restart", "telegram_api_recovered")


def test_no_restart_is_requested_while_telegram_api_is_still_down() -> None:
    watchdog = load_watchdog_module()

    probe = watchdog.ProbeResult(
        gateway_running=True,
        gateway_pid=1234,
        gateway_status_summary="running",
        telegram_api_ok=False,
        telegram_api_transport="none",
        telegram_dns_ok=False,
        fallback_api_ok=False,
        recent_connect_failure=True,
        error_fingerprint="mtime:123",
    )
    state = watchdog.WatchdogState(last_api_ok=False)

    action = watchdog.decide_repair_action(probe, state)

    assert action == (None, "telegram_api_unreachable")


def test_plist_contains_interval_and_repo_local_hermes_home() -> None:
    watchdog = load_watchdog_module()

    plist = watchdog.build_launch_agent_plist(
        label="ai.hermes.gateway-watchdog",
        script_path=Path("/Users/jk/workspace/skills-jk/bin/hermes-gateway-watchdog"),
        repo_root=Path("/Users/jk/workspace/skills-jk"),
        hermes_home=Path("/Users/jk/workspace/skills-jk/.hermes"),
        interval_seconds=60,
        stdout_path=Path("/Users/jk/workspace/skills-jk/.hermes/logs/gateway-watchdog.log"),
        stderr_path=Path("/Users/jk/workspace/skills-jk/.hermes/logs/gateway-watchdog.error.log"),
    )

    assert "<key>StartInterval</key>" in plist
    assert "<integer>60</integer>" in plist
    assert "<key>HERMES_HOME</key>" in plist
    assert "/Users/jk/workspace/skills-jk/.hermes" in plist


def test_load_state_returns_defaults_for_non_dict_json(tmp_path: Path) -> None:
    watchdog = load_watchdog_module()

    state_path = tmp_path / "gateway-watchdog-state.json"
    state_path.write_text('["not", "a", "dict"]')

    state = watchdog.load_state(state_path)

    assert state == watchdog.WatchdogState()


def test_install_launch_agent_raises_when_bootstrap_fails(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    watchdog = load_watchdog_module()

    home_dir = tmp_path / "home"
    monkeypatch.setattr(watchdog.Path, "home", staticmethod(lambda: home_dir))

    def fake_run_command(command, **kwargs):
        if command[:2] == ["launchctl", "bootstrap"]:
            return 1, "", "bootstrap failed"
        return 0, "", ""

    monkeypatch.setattr(watchdog, "run_command", fake_run_command)

    with pytest.raises(RuntimeError, match="bootstrap failed"):
        watchdog.install_launch_agent(
            label="ai.hermes.gateway-watchdog",
            script_path=tmp_path / "bin" / "hermes-gateway-watchdog",
            repo_root=tmp_path,
            hermes_home=tmp_path / ".hermes",
            interval_seconds=60,
        )


def test_backoff_blocks_repeat_restart_until_deadline() -> None:
    watchdog = load_watchdog_module()

    probe = watchdog.ProbeResult(
        gateway_running=True,
        gateway_pid=1234,
        gateway_status_summary="running",
        telegram_api_ok=True,
        telegram_api_transport="direct",
        telegram_dns_ok=True,
        fallback_api_ok=False,
        recent_connect_failure=True,
        error_fingerprint="fp-2",
    )
    state = watchdog.WatchdogState(
        last_api_ok=True,
        last_action="restart",
        last_action_reason="recent_connect_failure",
        last_action_at=10_000,
        last_repair_error_fingerprint="fp-1",
        network_failure_backoff_step=3,
        next_network_retry_at=20_000,
    )

    action = watchdog.decide_repair_action(probe, state, now=15_000)

    assert action == (None, "network_backoff_active")


def test_backoff_allows_restart_after_deadline() -> None:
    watchdog = load_watchdog_module()

    probe = watchdog.ProbeResult(
        gateway_running=True,
        gateway_pid=1234,
        gateway_status_summary="running",
        telegram_api_ok=True,
        telegram_api_transport="direct",
        telegram_dns_ok=True,
        fallback_api_ok=False,
        recent_connect_failure=True,
        error_fingerprint="fp-2",
    )
    state = watchdog.WatchdogState(
        last_api_ok=True,
        last_action="restart",
        last_action_reason="recent_connect_failure",
        last_action_at=10_000,
        last_repair_error_fingerprint="fp-1",
        network_failure_backoff_step=3,
        next_network_retry_at=20_000,
    )

    action = watchdog.decide_repair_action(probe, state, now=20_001)

    assert action == ("restart", "recent_connect_failure")


def test_recording_network_repair_failure_increases_backoff() -> None:
    watchdog = load_watchdog_module()

    state = watchdog.WatchdogState()
    watchdog.record_network_failure_backoff(state, now=1_000)
    assert state.network_failure_backoff_step == 1
    assert state.next_network_retry_at == 1_300

    watchdog.record_network_failure_backoff(state, now=2_000)
    assert state.network_failure_backoff_step == 2
    assert state.next_network_retry_at == 2_600


def test_backoff_caps_at_one_hour() -> None:
    watchdog = load_watchdog_module()

    state = watchdog.WatchdogState(network_failure_backoff_step=10)
    watchdog.record_network_failure_backoff(state, now=5_000)

    assert state.next_network_retry_at == 8_600
    assert state.network_failure_backoff_step >= 11


def test_successful_probe_clears_backoff_state() -> None:
    watchdog = load_watchdog_module()

    state = watchdog.WatchdogState(
        network_failure_backoff_step=4,
        next_network_retry_at=99_999,
    )
    watchdog.reset_network_failure_backoff(state)

    assert state.network_failure_backoff_step == 0
    assert state.next_network_retry_at is None


def test_same_fingerprint_is_not_treated_as_recovery() -> None:
    watchdog = load_watchdog_module()

    probe = watchdog.ProbeResult(
        gateway_running=True,
        gateway_pid=1234,
        gateway_status_summary="running",
        telegram_api_ok=True,
        telegram_api_transport="direct",
        telegram_dns_ok=True,
        fallback_api_ok=False,
        recent_connect_failure=True,
        error_fingerprint="fp-1",
    )
    state = watchdog.WatchdogState(
        last_api_ok=True,
        last_repair_error_fingerprint="fp-1",
        network_failure_backoff_step=3,
        next_network_retry_at=20_000,
    )

    action = watchdog.decide_repair_action(probe, state, now=15_000)

    assert action == (None, "awaiting_new_failure_signal")


def test_failed_recent_connect_failure_repair_still_increases_backoff(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    watchdog = load_watchdog_module()
    hermes_home = tmp_path / ".hermes"
    hermes_home.mkdir()
    state_path = hermes_home / watchdog.DEFAULT_STATE_FILE_NAME

    probe = watchdog.ProbeResult(
        gateway_running=True,
        gateway_pid=1234,
        gateway_status_summary="running",
        telegram_api_ok=True,
        telegram_api_transport="direct",
        telegram_dns_ok=True,
        fallback_api_ok=False,
        recent_connect_failure=True,
        error_fingerprint="fp-2",
    )
    state = watchdog.WatchdogState(last_api_ok=True)
    watchdog.save_state(state_path, state)

    monkeypatch.setattr(watchdog, "probe", lambda _home: probe)
    monkeypatch.setattr(watchdog, "run_gateway_action", lambda action, home: (False, "restart failed"))
    monkeypatch.setattr(watchdog.time, "time", lambda: 1_000.0)

    parser = watchdog.build_parser()
    args = parser.parse_args(["check", "--repair", "--hermes-home", str(hermes_home)])
    result = watchdog.command_check(args)
    state = watchdog.load_state(state_path)

    assert result == 0
    assert state.network_failure_backoff_step == 1
    assert state.next_network_retry_at == 1_300.0

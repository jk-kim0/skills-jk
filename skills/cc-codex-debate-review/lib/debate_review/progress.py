"""Real-time progress reporting for debate review sessions.

Outputs human-readable debate content and agent status to stderr
so that stdout remains reserved for the final JSON result.
"""

from __future__ import annotations

import sys
import threading
import time


def _format_elapsed(seconds: float) -> str:
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    if minutes > 0:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


class ProgressReporter:
    """Writes debate progress and content to stderr."""

    TICK_INTERVAL = 30  # seconds

    def __init__(self, file=None):
        self._file = file or sys.stderr
        self._timer: threading.Timer | None = None
        self._step_label: str = ""
        self._step_start: float = 0.0
        self._lock = threading.Lock()
        self._running = False
        self._token = 0

    def _write(self, text: str) -> None:
        self._file.write(text + "\n")
        self._file.flush()

    def _write_indented(self, text: str) -> None:
        for line in text.splitlines():
            self._write(f"  {line}")

    # ── lifecycle ──

    def round_start(self, round_num: int, lead: str, cross: str) -> None:
        self._write(f"\n── Round {round_num} (lead: {lead}) " + "─" * 40)

    def step_start(self, step: str, agent: str, action: str) -> None:
        self._stop_timer()
        self._step_label = f"[{step}] {agent} {action}"
        self._step_start = time.monotonic()
        with self._lock:
            self._running = True
            self._token += 1
            token = self._token
        self._write(f"{self._step_label}...")
        self._start_timer(token)

    def step_done(self, step: str, agent: str, action: str, elapsed: float, summary: str = "") -> None:
        self._stop_timer()
        line = f"[{step}] {agent} {action} ✓ ({_format_elapsed(elapsed)})"
        if summary:
            line += f" — {summary}"
        self._write(line)

    def abort_step(self) -> None:
        self._stop_timer()

    def step_skip(self, step: str, reason: str = "clean pass") -> None:
        self._write(f"[{step}] skip ({reason})")

    def debate_content(self, lines: list[str]) -> None:
        for line in lines:
            self._write_indented(line)

    def settle(self, result: str, next_round: int | None = None,
               settled: list[str] | None = None, unresolved: list[str] | None = None) -> None:
        extra = ""
        if result == "continue" and next_round is not None:
            extra = f" → round {next_round}"
        self._write(f"[Step4] settle ✓ {result}{extra}")
        if settled:
            self._write(f"        settled: {', '.join(settled)}")
        if unresolved:
            self._write(f"        unresolved: {', '.join(unresolved)}")

    def final_result(self, outcome: str, rounds: int, duration: str,
                     applied: int, withdrawn: int, unresolved: int) -> None:
        self._write(f"\n── Result " + "─" * 50)
        self._write(f"{outcome} after {rounds} rounds ({duration})")
        self._write(f"applied: {applied} | withdrawn: {withdrawn} | unresolved: {unresolved}")

    # ── timer ──

    def _start_timer(self, token: int | None = None) -> None:
        with self._lock:
            active_token = self._token if token is None else token
            if not self._running or active_token != self._token:
                return
            timer = threading.Timer(self.TICK_INTERVAL, self._tick, args=(active_token,))
            timer.daemon = True
            self._timer = timer
        timer.start()

    def _tick(self, token: int | None = None) -> None:
        with self._lock:
            active_token = self._token if token is None else token
            if not self._running or active_token != self._token:
                return
            elapsed = time.monotonic() - self._step_start
            line = f"{self._step_label}... ({_format_elapsed(elapsed)})"
        self._write(line)
        self._start_timer(active_token)

    def _stop_timer(self) -> None:
        with self._lock:
            self._running = False
            timer = self._timer
            self._timer = None
        if timer is not None:
            timer.cancel()


# ── debate content formatters ──

def format_step1(response: dict) -> list[str]:
    """Format lead review findings and verdict."""
    lines: list[str] = []
    for f in response.get("findings", []):
        severity = f.get("severity", "?")
        file = f.get("file", "?")
        line_num = f.get("line", "?")
        anchor = f.get("anchor", "")
        anchor_str = f" ({anchor})" if anchor else ""
        lines.append(f"[{severity}] {file}:{line_num}{anchor_str}")
        msg = f.get("message", "")
        if msg:
            for msg_line in msg.splitlines():
                lines.append(f"  {msg_line}")
        lines.append("")

    for r in response.get("rebuttal_responses", []):
        issue_id = r.get("issue_id", r.get("report_id", "?"))
        decision = r.get("decision", "?").upper()
        reason = r.get("reason", "")
        lines.append(f"{issue_id} {decision}:")
        if reason:
            for reason_line in reason.splitlines():
                lines.append(f"  {reason_line}")
        lines.append("")

    for w in response.get("withdrawals", []):
        issue_id = w.get("issue_id", "?")
        reason = w.get("reason", "")
        lines.append(f"{issue_id} WITHDRAW:")
        if reason:
            for reason_line in reason.splitlines():
                lines.append(f"  {reason_line}")
        lines.append("")

    verdict = response.get("verdict", "?")
    lines.append(f"verdict: {verdict}")
    return lines


def format_step2(response: dict) -> list[str]:
    """Format cross-verification decisions and new findings."""
    lines: list[str] = []
    for v in response.get("cross_verifications", []):
        issue_id = v.get("issue_id", v.get("report_id", "?"))
        verdict = v.get("verdict", v.get("decision", "?")).upper()
        reason = v.get("reason", "")
        lines.append(f"{issue_id} {verdict}:")
        if reason:
            for reason_line in reason.splitlines():
                lines.append(f"  {reason_line}")
        lines.append("")

    for w in response.get("withdrawals", []):
        issue_id = w.get("issue_id", "?")
        reason = w.get("reason", "")
        lines.append(f"{issue_id} WITHDRAW:")
        if reason:
            for reason_line in reason.splitlines():
                lines.append(f"  {reason_line}")
        lines.append("")

    new_findings = response.get("findings", [])
    if new_findings:
        lines.append(f"{len(new_findings)} new finding(s):")
        for f in new_findings:
            severity = f.get("severity", "?")
            file = f.get("file", "?")
            line_num = f.get("line", "?")
            anchor = f.get("anchor", "")
            anchor_str = f" ({anchor})" if anchor else ""
            lines.append(f"  [{severity}] {file}:{line_num}{anchor_str}")
            msg = f.get("message", "")
            if msg:
                for msg_line in msg.splitlines():
                    lines.append(f"    {msg_line}")
            lines.append("")
    return lines


def format_step3(response: dict) -> list[str]:
    """Format lead response decisions and code application result."""
    lines: list[str] = []
    for d in response.get("rebuttal_decisions", []):
        report_id = d.get("report_id", "?")
        decision = d.get("decision", "?").upper()
        reason = d.get("reason", "")
        lines.append(f"{report_id} {decision}:")
        if reason:
            for reason_line in reason.splitlines():
                lines.append(f"  {reason_line}")
        lines.append("")

    for e in response.get("cross_finding_evaluations", []):
        report_id = e.get("report_id", "?")
        decision = e.get("decision", "?").upper()
        reason = e.get("reason", "")
        lines.append(f"{report_id} {decision}:")
        if reason:
            for reason_line in reason.splitlines():
                lines.append(f"  {reason_line}")
        lines.append("")

    for w in response.get("withdrawals", []):
        issue_id = w.get("issue_id", "?")
        reason = w.get("reason", "")
        lines.append(f"{issue_id} WITHDRAW:")
        if reason:
            for reason_line in reason.splitlines():
                lines.append(f"  {reason_line}")
        lines.append("")

    app = response.get("application_result", {})
    applied = app.get("applied_issues", [])
    failed = app.get("failed_issues", [])
    commit = app.get("commit_sha", "")
    if applied:
        commit_str = f" → commit {commit[:7]}" if commit else ""
        lines.append(f"CODE APPLIED: {', '.join(applied)}{commit_str}")
    if failed:
        failed_ids = [f.get("issue_id", str(f)) if isinstance(f, dict) else str(f) for f in failed]
        lines.append(f"CODE FAILED: {', '.join(failed_ids)}")
    return lines

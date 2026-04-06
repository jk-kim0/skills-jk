"""Streaming subprocess utilities for debate-review runtime supervision."""

from __future__ import annotations

import queue
import shlex
import subprocess
import threading
import time


def _reader_thread(stream, channel: str, out_queue: queue.Queue) -> None:
    try:
        for line in iter(stream.readline, ""):
            out_queue.put((channel, line.rstrip("\n")))
    finally:
        out_queue.put((channel, None))


def run_streaming_command(
    command: str,
    *,
    cwd: str | None = None,
    stdin_text: str | None = None,
    tick_interval: float = 5.0,
    on_started=None,
    on_stdout_line=None,
    on_stderr_line=None,
    on_tick=None,
    stdout_log_path: str | None = None,
    stderr_log_path: str | None = None,
    output_file_path=None,
) -> dict:
    process = subprocess.Popen(
        shlex.split(command),
        cwd=cwd,
        stdin=subprocess.PIPE if stdin_text is not None else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    if on_started is not None:
        on_started(process.pid)

    if stdin_text is not None and process.stdin is not None:
        process.stdin.write(stdin_text)
        process.stdin.close()

    events: queue.Queue = queue.Queue()
    threads = [
        threading.Thread(target=_reader_thread, args=(process.stdout, "stdout", events), daemon=True),
        threading.Thread(target=_reader_thread, args=(process.stderr, "stderr", events), daemon=True),
    ]
    for thread in threads:
        thread.start()

    completed_streams = {"stdout": False, "stderr": False}
    stdout_log = open(stdout_log_path, "w") if stdout_log_path else None
    stderr_log = open(stderr_log_path, "w") if stderr_log_path else None
    next_tick = time.monotonic() + tick_interval

    try:
        while True:
            timeout = max(0.0, next_tick - time.monotonic())
            try:
                channel, line = events.get(timeout=timeout)
            except queue.Empty:
                if process.poll() is None and on_tick is not None:
                    on_tick()
                next_tick = time.monotonic() + tick_interval
                continue

            if line is None:
                completed_streams[channel] = True
                if all(completed_streams.values()) and process.poll() is not None and events.empty():
                    break
                continue

            if channel == "stdout":
                if stdout_log is not None:
                    stdout_log.write(line + "\n")
                    stdout_log.flush()
                if on_stdout_line is not None:
                    on_stdout_line(line)
            else:
                if stderr_log is not None:
                    stderr_log.write(line + "\n")
                    stderr_log.flush()
                if on_stderr_line is not None:
                    on_stderr_line(line)

            if time.monotonic() >= next_tick:
                if process.poll() is None and on_tick is not None:
                    on_tick()
                next_tick = time.monotonic() + tick_interval
    except Exception:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                process.kill()
        raise
    finally:
        if stdout_log is not None:
            stdout_log.close()
        if stderr_log is not None:
            stderr_log.close()

    return {
        "returncode": process.wait(),
        "stdout_log_path": stdout_log_path,
        "stderr_log_path": stderr_log_path,
        "child_pid": process.pid,
        "output_file_path": str(output_file_path) if output_file_path is not None else None,
    }


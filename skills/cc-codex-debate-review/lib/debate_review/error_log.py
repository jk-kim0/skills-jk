"""Error log persistence for debate-review CLI failures."""

import json
import os
from datetime import datetime, timezone


ERROR_LOG_DIR = os.path.expanduser("~/.claude/debate-state/error-logs")


def save_error_log(*, command, error_message, state_file=None):
    """Save a structured error log to disk. Returns the log file path."""
    os.makedirs(ERROR_LOG_DIR, exist_ok=True)
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y%m%dT%H%M%SZ")

    entry = {
        "timestamp": now.isoformat(),
        "command": command,
        "error": error_message,
        "state_file": state_file,
    }

    filename = f"{timestamp}-{command}.json"
    path = os.path.join(ERROR_LOG_DIR, filename)
    with open(path, "w") as f:
        json.dump(entry, f, indent=2)
    return path

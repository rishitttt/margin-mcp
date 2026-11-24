"""Optional process-local sanitized tool observations; never hidden reasoning."""

import json
import os
from pathlib import Path

from margin.core.contracts import DomainError, now


class ToolRecorder:
    def __init__(self, path=None, *, maximum=64 * 1024 * 1024):
        self.path = Path(path) if path else None
        self.maximum, self.sequence, self.size = maximum, 0, 0
        self.stream = None
        if self.path:
            # Refuse overwrite, symlinks, special files and previous sessions.
            fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            self.stream = os.fdopen(fd, "w", encoding="utf-8")

    def append(self, event):
        if self.stream is None:
            return None
        try:
            payload = (
                json.dumps(
                    {
                        "log_contract": "margin.mcp.log.v1",
                        "sequence": self.sequence + 1,
                        "at": now(),
                        **event,
                    },
                    ensure_ascii=False,
                    allow_nan=False,
                )
                + "\n"
            )
            length = len(payload.encode())
            if self.size + length > self.maximum:
                raise OSError
            self.stream.write(payload)
            self.stream.flush()
            self.sequence += 1
            self.size += length
            return self.sequence
        except (OSError, ValueError, TypeError):
            raise DomainError(
                "recording",
                "The private tool log could not be written; do not assume a new action was dispatched.",
            ) from None

    def close(self):
        if self.stream is not None:
            self.stream.close()

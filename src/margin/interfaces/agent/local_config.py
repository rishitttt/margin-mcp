"""Read a local provider credential file as data, never as executable shell code."""

from pathlib import Path

from margin.interfaces.agent.client import BridgeError

PROVIDER_KEYS = frozenset({"BHARATSTOCK_API_KEY", "DRISHTI_API_KEY"})


def read_provider_env(path):
    try:
        with Path(path).open("r", encoding="utf-8") as stream:
            raw = stream.read(65537)
        if len(raw.encode()) > 65536:
            raise ValueError
        values = {}
        for line in raw.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            name, separator, value = line.removeprefix("export ").partition("=")
            if not separator:
                raise ValueError
            if name.strip() not in PROVIDER_KEYS:
                continue
            value = value.strip()
            if value[:1] in {"'", '"'}:
                if len(value) < 2 or value[-1] != value[0]:
                    raise ValueError
                value = value[1:-1]
            if not value or any(c in value for c in "\n\r\x00"):
                raise ValueError
            values[name.strip()] = value
        return values
    except (OSError, ValueError):
        raise BridgeError(
            "credential_file", "Cannot read a valid local provider credential file."
        ) from None

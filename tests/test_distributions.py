"""Guards for archive traversal, unwanted content and secret-bearing distributions."""

import runpy
from pathlib import Path

import pytest

CHECK = runpy.run_path(str(Path(__file__).parents[1] / "scripts/check_distributions.py"))


@pytest.mark.parametrize(
    "name",
    [
        "../leak",
        "/absolute",
        "research/task.json",
        "tests/repository/test_private.py",
        ".env",
        "margin/connection.json",
    ],
)
def test_public_archive_rejects_private_or_unsafe_paths(name):
    with pytest.raises(ValueError):
        CHECK["check_paths"]({name: b"ordinary content"})


def test_credential_detection_withholds_value():
    token = b"pypi-" + b"a" * 48
    with pytest.raises(ValueError) as error:
        CHECK["check_paths"]({"margin/example.py": token})
    assert token.decode() not in str(error.value)

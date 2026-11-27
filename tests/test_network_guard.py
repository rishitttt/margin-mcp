"""The cross-platform self-pipe exception must not allow ordinary network calls."""

import socket

import pytest


@pytest.mark.parametrize("method", ["connect", "connect_ex"])
def test_network_guard_blocks_external_and_ordinary_loopback(method):
    with socket.socket() as sock:
        for address in [("127.0.0.1", 9), ("192.0.2.1", 443)]:
            with pytest.raises(AssertionError, match="Unexpected socket"):
                getattr(sock, method)(address)


def test_stdlib_socketpair_still_supports_event_loop_self_pipe():
    left, right = socket.socketpair()
    with left, right:
        right.sendall(b"wake")
        assert left.recv(4) == b"wake"

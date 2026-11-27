"""Default tests block network connects; stdlib socketpair may create a local self-pipe."""

import contextvars
import socket

import pytest


@pytest.fixture(autouse=True)
def no_external_network(monkeypatch):
    original_connect = socket.socket.connect
    original_connect_ex = socket.socket.connect_ex
    original_pair = socket.socketpair
    creating_pair = contextvars.ContextVar("creating_stdlib_socketpair", default=False)

    def local_pair_connection(sock, address):
        # Windows implements stdlib socketpair using TCP loopback for asyncio's
        # self-pipe. Exempt only that synchronous stdlib operation, not ordinary
        # loopback connects, provider sockets or arbitrary code during a test.
        return (
            creating_pair.get()
            and sock.family in (socket.AF_INET, socket.AF_INET6)
            and isinstance(address, tuple)
            and address[0] in {"127.0.0.1", "::1"}
        )

    def connect(sock, address):
        if local_pair_connection(sock, address):
            return original_connect(sock, address)
        raise AssertionError("Unexpected socket connection: use a synthetic transport.")

    def connect_ex(sock, address):
        if local_pair_connection(sock, address):
            return original_connect_ex(sock, address)
        raise AssertionError("Unexpected socket connection: use a synthetic transport.")

    def pair(*args, **kwargs):
        token = creating_pair.set(True)
        try:
            return original_pair(*args, **kwargs)
        finally:
            creating_pair.reset(token)

    monkeypatch.setattr(socket.socket, "connect", connect)
    monkeypatch.setattr(socket.socket, "connect_ex", connect_ex)
    monkeypatch.setattr(socket, "socketpair", pair)

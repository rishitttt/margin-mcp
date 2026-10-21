"""The default suite may use in-process transports, never real provider sockets."""

import socket

import pytest


@pytest.fixture(autouse=True)
def no_external_network(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError("Unexpected socket connection: use a synthetic transport.")

    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(socket.socket, "connect_ex", blocked)

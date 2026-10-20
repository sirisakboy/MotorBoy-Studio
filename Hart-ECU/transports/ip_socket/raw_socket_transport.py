"""Generic TCP byte-stream and UDP datagram transports for IP-connected adapters.

These classes deliberately do not define ELM327, SLCAN, GVRET, WiCAN, MQTT, UDS, or
any other adapter/vehicle protocol. Transmit is disabled by default.
"""
from __future__ import annotations

import socket
from typing import Optional


def _port_number(value: int | str, *, minimum: int) -> int:
    if isinstance(value, bool):
        raise ValueError("port must be an integer")
    if isinstance(value, int):
        number = value
    elif isinstance(value, str) and value.isdecimal():
        number = int(value)
    else:
        raise ValueError("port must be an integer")
    if not minimum <= number <= 65535:
        raise ValueError(f"port must be between {minimum} and 65535")
    return number


def _timeout_seconds(value: float) -> float:
    if isinstance(value, bool):
        raise ValueError("timeout must be a number of seconds")
    seconds = float(value)
    if not 0.05 <= seconds <= 30.0:
        raise ValueError("timeout must be between 0.05 and 30 seconds")
    return seconds


class TcpByteStream:
    """Client-side TCP byte stream. It never starts a listener or guesses a port."""

    def __init__(self, host: str, port: int | str, *, timeout: float = 1.0,
                 tx_enabled: bool = False) -> None:
        if not host or not isinstance(host, str):
            raise ValueError("host must be a non-empty hostname or IP address")
        self.host = host
        self.port = _port_number(port, minimum=1)
        self.timeout = _timeout_seconds(timeout)
        if not isinstance(tx_enabled, bool):
            raise ValueError("tx_enabled must be an explicit boolean")
        self.tx_enabled = tx_enabled
        self._sock: Optional[socket.socket] = None

    def connect(self) -> None:
        if self._sock is not None:
            raise RuntimeError("TCP transport is already connected")
        sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
        sock.settimeout(self.timeout)
        self._sock = sock

    def recv(self, max_bytes: int = 4096) -> bytes:
        if self._sock is None:
            raise RuntimeError("TCP transport is not connected")
        if isinstance(max_bytes, bool) or not isinstance(max_bytes, int) or not 1 <= max_bytes <= 65536:
            raise ValueError("max_bytes must be an integer between 1 and 65536")
        return self._sock.recv(max_bytes)

    def send(self, payload: bytes) -> int:
        if not self.tx_enabled:
            raise PermissionError("TCP transmit is disabled; enable only for an authorized adapter")
        if self._sock is None:
            raise RuntimeError("TCP transport is not connected")
        if not isinstance(payload, (bytes, bytearray, memoryview)):
            raise TypeError("payload must be bytes-like")
        data = bytes(payload)
        self._sock.sendall(data)
        return len(data)

    def close(self) -> None:
        sock, self._sock = self._sock, None
        if sock is not None:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            sock.close()

    def __enter__(self) -> "TcpByteStream":
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


class UdpDatagramEndpoint:
    """Connected UDP peer. Each send/receive is a datagram; framing remains adapter-specific."""

    def __init__(self, host: str, port: int | str, *, timeout: float = 1.0,
                 tx_enabled: bool = False, local_host: str = "0.0.0.0",
                 local_port: int | str = 0) -> None:
        if not host or not isinstance(host, str):
            raise ValueError("host must be a non-empty hostname or IP address")
        if not local_host or not isinstance(local_host, str):
            raise ValueError("local_host must be a non-empty local interface address")
        self.host = host
        self.port = _port_number(port, minimum=1)
        self.timeout = _timeout_seconds(timeout)
        if not isinstance(tx_enabled, bool):
            raise ValueError("tx_enabled must be an explicit boolean")
        self.tx_enabled = tx_enabled
        self.local_host = local_host
        self.local_port = _port_number(local_port, minimum=0)
        self._sock: Optional[socket.socket] = None

    def connect(self) -> None:
        if self._sock is not None:
            raise RuntimeError("UDP transport is already open")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)
        sock.bind((self.local_host, self.local_port))
        sock.connect((self.host, self.port))
        self._sock = sock

    def recv(self, max_bytes: int = 65507) -> bytes:
        if self._sock is None:
            raise RuntimeError("UDP transport is not open")
        if isinstance(max_bytes, bool) or not isinstance(max_bytes, int) or not 1 <= max_bytes <= 65507:
            raise ValueError("max_bytes must be an integer between 1 and 65507")
        return self._sock.recv(max_bytes)

    def send(self, payload: bytes) -> int:
        if not self.tx_enabled:
            raise PermissionError("UDP transmit is disabled; enable only for an authorized adapter")
        if self._sock is None:
            raise RuntimeError("UDP transport is not open")
        if not isinstance(payload, (bytes, bytearray, memoryview)):
            raise TypeError("payload must be bytes-like")
        return self._sock.send(bytes(payload))

    def close(self) -> None:
        sock, self._sock = self._sock, None
        if sock is not None:
            sock.close()

    def __enter__(self) -> "UdpDatagramEndpoint":
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

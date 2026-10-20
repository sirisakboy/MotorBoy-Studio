"""Localhost-only tests; no adapter or ECU is contacted."""
from __future__ import annotations

import socket
import threading

from transports.ip_socket.raw_socket_transport import TcpByteStream, UdpDatagramEndpoint


def test_tcp_byte_stream_and_tx_gate() -> None:
    # Verify that a read-only transport rejects before attempting a connection.
    ro = TcpByteStream("127.0.0.1", 1, tx_enabled=False)
    try:
        ro.send(b"blocked")
    except PermissionError:
        pass
    else:
        raise AssertionError("TCP transmit gate did not block a send")
    ro.close()

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)
    host, port = listener.getsockname()
    result: list[bytes] = []

    def server() -> None:
        conn, _ = listener.accept()
        with conn:
            data = conn.recv(64)
            result.append(data)
            conn.sendall(b"reply:" + data)
        listener.close()

    thread = threading.Thread(target=server, daemon=True)
    thread.start()
    with TcpByteStream(host, port, tx_enabled=True) as stream:
        assert stream.send(b"ping") == len(b"ping")
        assert stream.recv(64) == b"reply:ping"
    thread.join(timeout=1)
    assert not thread.is_alive()
    assert result == [b"ping"]


def test_udp_datagram_and_tx_gate() -> None:
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(("127.0.0.1", 0))
    server.settimeout(1)
    host, port = server.getsockname()
    endpoint = UdpDatagramEndpoint(host, port, tx_enabled=True)
    with endpoint:
        assert endpoint.send(b"datagram") == len(b"datagram")
        data, addr = server.recvfrom(64)
        assert data == b"datagram"
        server.sendto(b"ack", addr)
        assert endpoint.recv(64) == b"ack"
    server.close()

    gated = UdpDatagramEndpoint("127.0.0.1", 9, tx_enabled=False)
    try:
        gated.send(b"no")
    except PermissionError:
        pass
    else:
        raise AssertionError("UDP transmit gate did not block a send")
    finally:
        gated.close()

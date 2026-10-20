#!/usr/bin/env python3
"""Local JSON-lines sidecar around python-can. Read-only until --allow-tx is explicit.

This transport bridge does not implement ISO-TP, UDS, KWP, OEM services, or ECU profiles.
It reads/writes CAN frames only; callers must supply separately verified protocol data.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

_PACK_ROOT = Path(__file__).resolve().parents[2]
_CAN_SOURCE = _PACK_ROOT / "dependencies" / "python-can-4.6.1"
if not _CAN_SOURCE.is_dir():  # Avoid silently importing a different system package/version.
    raise SystemExit(f"Curated python-can source not found: {_CAN_SOURCE}")
sys.path.insert(0, str(_CAN_SOURCE))

try:
    import can
except ImportError as exc:  # pragma: no cover - exercised only in a missing-dependency install
    raise SystemExit(
        "python-can is required. Install its declared runtime dependencies and add the "
        "pack's dependencies/python-can-4.6.1 directory to PYTHONPATH."
    ) from exc


class CanJsonlService:
    """Small stdin/stdout JSON-RPC-like service; never opens a network listener."""

    def __init__(self, *, tx_enabled: bool = False) -> None:
        if not isinstance(tx_enabled, bool):
            raise TypeError("tx_enabled must be an explicit boolean")
        self.tx_enabled = tx_enabled
        self.bus: can.BusABC | None = None
        self.interface: str | None = None
        self.channel: str | int | None = None
        self.fd_enabled = False

    @staticmethod
    def _integer(value: Any, name: str) -> int:
        if isinstance(value, bool):
            raise ValueError(f"{name} must be an integer, not a boolean")
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            return int(value, 0)
        raise ValueError(f"{name} must be an integer or a base-prefixed string")

    @staticmethod
    def _error(request_id: Any, code: int, message: str) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id,
                "error": {"code": code, "message": message}}

    def _result(self, request_id: Any, value: Any) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "result": value}

    def _dispatch(self, request: Any) -> dict[str, Any]:
        if not isinstance(request, dict) or request.get("jsonrpc") != "2.0":
            return self._error(None, -32600, "Invalid JSON-RPC request")
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})
        valid_id = (request_id is None or isinstance(request_id, str)
                    or (isinstance(request_id, int) and not isinstance(request_id, bool))
                    or (isinstance(request_id, float) and math.isfinite(request_id)))
        if "id" not in request or not valid_id or not isinstance(method, str) or not isinstance(params, dict):
            return self._error(None, -32600, "id must be string, number, or null; method must be text and params an object")

        try:
            if method in {"system.info", "can.interfaces.list", "can.close"} and params:
                return self._error(request_id, -32602, f"{method} takes no parameters")
            if method == "system.info":
                return self._result(request_id, {
                    "service": "ecu-tuner-can-sidecar",
                    "python_can_version": "4.6.1",
                    "tx_enabled": self.tx_enabled,
                    "network_listener": False,
                })
            if method == "can.interfaces.list":
                return self._result(request_id, sorted(can.VALID_INTERFACES))
            if method == "can.open":
                return self._open(request_id, params)
            if method == "can.receive":
                return self._receive(request_id, params)
            if method == "can.send":
                return self._send(request_id, params)
            if method == "can.close":
                return self._close(request_id)
            return self._error(request_id, -32601, f"Unknown method: {method}")
        except (ValueError, TypeError) as exc:
            return self._error(request_id, -32602, str(exc))
        except Exception as exc:  # Normalize backend/driver errors for language bindings.
            return self._error(request_id, -32000, f"{type(exc).__name__}: {exc}")

    def _open(self, request_id: Any, params: dict[str, Any]) -> dict[str, Any]:
        if self.bus is not None:
            return self._error(request_id, -32001, "A CAN bus is already open")
        interface = params.get("interface")
        if not isinstance(interface, str) or interface not in can.VALID_INTERFACES:
            return self._error(request_id, -32602, "interface must be a supported python-can interface")

        # Explicit allowlist prevents arbitrary backend config from crossing the sidecar API.
        allowed = {"interface", "channel", "bitrate", "fd", "data_bitrate", "receive_own_messages"}
        unknown = set(params) - allowed
        if unknown:
            return self._error(request_id, -32602, f"unsupported can.open parameter(s): {', '.join(sorted(unknown))}")
        options: dict[str, Any] = {}
        channel = params.get("channel")
        if channel is not None:
            if not isinstance(channel, (str, int)) or isinstance(channel, bool):
                return self._error(request_id, -32602, "channel must be text or an integer")
            options["channel"] = channel
        bitrate = params.get("bitrate")
        if bitrate is not None:
            value = self._integer(bitrate, "bitrate")
            if not 10_000 <= value <= 5_000_000:
                return self._error(request_id, -32602, "bitrate is outside the accepted range")
            options["bitrate"] = value
        fd = params.get("fd", False)
        if not isinstance(fd, bool):
            return self._error(request_id, -32602, "fd must be boolean")
        data_bitrate = params.get("data_bitrate")
        if data_bitrate is not None and not fd:
            return self._error(request_id, -32602, "data_bitrate requires fd=true")
        if fd:
            options["fd"] = True
            if data_bitrate is not None:
                value = self._integer(data_bitrate, "data_bitrate")
                if not 100_000 <= value <= 10_000_000:
                    return self._error(request_id, -32602, "data_bitrate is outside the accepted range")
                options["data_bitrate"] = value
        receive_own = params.get("receive_own_messages")
        if receive_own is not None:
            if not isinstance(receive_own, bool):
                return self._error(request_id, -32602, "receive_own_messages must be boolean")
            options["receive_own_messages"] = receive_own

        # No transmit is performed by open(). Backend API/driver may initialize hardware.
        self.bus = can.Bus(interface=interface, **options)
        self.interface = interface
        self.channel = channel
        self.fd_enabled = fd
        return self._result(request_id, {
            "opened": True,
            "interface": interface,
            "channel": channel,
            "fd": fd,
            "tx_enabled": self.tx_enabled,
        })

    def _receive(self, request_id: Any, params: dict[str, Any]) -> dict[str, Any]:
        unknown = set(params) - {"timeout"}
        if unknown:
            return self._error(request_id, -32602, f"unsupported can.receive parameter(s): {', '.join(sorted(unknown))}")
        if self.bus is None:
            return self._error(request_id, -32002, "No CAN bus is open")
        timeout = params.get("timeout", 0.0)
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
            return self._error(request_id, -32602, "timeout must be a number of seconds")
        if not 0 <= float(timeout) <= 5.0:
            return self._error(request_id, -32602, "timeout must be between 0 and 5 seconds")
        msg = self.bus.recv(timeout=float(timeout))
        if msg is None:
            return self._result(request_id, None)
        return self._result(request_id, {
            "arbitration_id": msg.arbitration_id,
            "is_extended_id": msg.is_extended_id,
            "is_remote_frame": msg.is_remote_frame,
            "is_error_frame": msg.is_error_frame,
            "is_fd": msg.is_fd,
            "bitrate_switch": msg.bitrate_switch,
            "error_state_indicator": msg.error_state_indicator,
            "dlc": msg.dlc,
            "data_hex": bytes(msg.data).hex(),
            "timestamp": msg.timestamp,
            "channel": None if msg.channel is None else str(msg.channel),
        })

    def _send(self, request_id: Any, params: dict[str, Any]) -> dict[str, Any]:
        unknown = set(params) - {"arbitration_id", "data", "is_extended_id", "is_fd", "timeout"}
        if unknown:
            return self._error(request_id, -32602, f"unsupported can.send parameter(s): {', '.join(sorted(unknown))}")
        if not self.tx_enabled:
            return self._error(request_id, -32003, "CAN transmit is disabled; restart with --allow-tx only when authorized")
        if self.bus is None:
            return self._error(request_id, -32002, "No CAN bus is open")
        try:
            arbitration_id = self._integer(params.get("arbitration_id"), "arbitration_id")
        except (ValueError, TypeError) as exc:
            return self._error(request_id, -32602, str(exc))
        extended = params.get("is_extended_id", False)
        is_fd = params.get("is_fd", False)
        if not isinstance(extended, bool) or not isinstance(is_fd, bool):
            return self._error(request_id, -32602, "is_extended_id and is_fd must be booleans")
        max_id = 0x1FFFFFFF if extended else 0x7FF
        if not 0 <= arbitration_id <= max_id:
            return self._error(request_id, -32602, "arbitration_id is outside the selected CAN ID range")
        if is_fd and not self.fd_enabled:
            return self._error(request_id, -32602, "CAN FD transmit requires opening the bus with fd=true")

        data = params.get("data", [])
        try:
            if isinstance(data, str):
                payload = bytes.fromhex(data)
            elif isinstance(data, list) and all(
                isinstance(v, int) and not isinstance(v, bool) and 0 <= v <= 255 for v in data
            ):
                payload = bytes(data)
            else:
                raise ValueError("data must be a hex string or an array of byte values")
        except ValueError as exc:
            return self._error(request_id, -32602, f"invalid data: {exc}")
        if len(payload) > (64 if is_fd else 8):
            return self._error(request_id, -32602, "data exceeds the selected CAN frame limit")

        msg = can.Message(
            arbitration_id=arbitration_id,
            data=payload,
            is_extended_id=extended,
            is_fd=is_fd,
        )
        send_timeout = params.get("timeout", 0.2)
        if isinstance(send_timeout, bool) or not isinstance(send_timeout, (int, float)):
            return self._error(request_id, -32602, "timeout must be a number of seconds")
        if not 0 <= float(send_timeout) <= 5.0:
            return self._error(request_id, -32602, "timeout must be between 0 and 5 seconds")
        self.bus.send(msg, timeout=float(send_timeout))
        return self._result(request_id, {"sent": True, "arbitration_id": arbitration_id,
                                         "data_hex": payload.hex(), "is_fd": is_fd})

    def _close(self, request_id: Any) -> dict[str, Any]:
        if self.bus is not None:
            self.bus.shutdown()
        self.bus = None
        self.interface = None
        self.channel = None
        self.fd_enabled = False
        return self._result(request_id, {"closed": True})

    def dispatch(self, request: Any) -> dict[str, Any]:
        """Public entry point, used by the line protocol and tests."""
        return self._dispatch(request)


def serve(tx_enabled: bool = False) -> None:
    service = CanJsonlService(tx_enabled=tx_enabled)
    for line in sys.stdin:
        try:
            request = json.loads(line)
            response = service.dispatch(request)
        except json.JSONDecodeError as exc:
            response = CanJsonlService._error(None, -32700, f"Parse error: {exc.msg}")
        except Exception as exc:  # Keep the process alive across individual bad lines.
            response = CanJsonlService._error(None, -32000, f"{type(exc).__name__}: {exc}")
        sys.stdout.write(json.dumps(response, separators=(",", ":"), allow_nan=False) + "\n")
        sys.stdout.flush()
    service.dispatch({"jsonrpc": "2.0", "id": None, "method": "can.close"})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-tx", action="store_true",
                        help="enable CAN frame transmit; default is receive-only")
    args = parser.parse_args()
    serve(tx_enabled=args.allow_tx)


if __name__ == "__main__":
    main()

"""Hardware-free smoke tests for the local python-can sidecar."""
from __future__ import annotations

import importlib.util
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PYTHON_CAN = ROOT / "dependencies" / "python-can-4.6.1"
import sys
sys.path.insert(0, str(PYTHON_CAN))

SPEC = importlib.util.spec_from_file_location(
    "can_jsonl_sidecar",
    Path(__file__).with_name("can_jsonl_sidecar.py"),
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def req(method: str, params: dict | None = None, request_id: int = 1) -> dict:
    return {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params or {}}


def test_virtual_bus_receive_and_read_only_default() -> None:
    import can

    channel = f"ecu-tuner-test-{uuid.uuid4()}"
    service = MODULE.CanJsonlService(tx_enabled=False)
    opened = service.dispatch(req("can.open", {"interface": "virtual", "channel": channel}))
    assert opened["result"]["opened"] is True
    with can.Bus(interface="virtual", channel=channel) as sender:
        sender.send(can.Message(arbitration_id=0x123, data=[0x11, 0x22], is_extended_id=False))
        received = service.dispatch(req("can.receive", {"timeout": 0.5}))
        assert received["result"]["arbitration_id"] == 0x123
        assert received["result"]["data_hex"] == "1122"
    denied = service.dispatch(req("can.send", {"arbitration_id": 0x123, "data": "01"}))
    assert denied["error"]["code"] == -32003
    service.dispatch(req("can.close"))


def test_explicit_tx_on_virtual_bus() -> None:
    import can

    channel = f"ecu-tuner-test-{uuid.uuid4()}"
    service = MODULE.CanJsonlService(tx_enabled=True)
    assert service.dispatch(req("can.open", {"interface": "virtual", "channel": channel}))["result"]["opened"]
    with can.Bus(interface="virtual", channel=channel) as receiver:
        sent = service.dispatch(req("can.send", {"arbitration_id": "0x456", "data": [0xAA, 0x55]}))
        assert sent["result"]["sent"] is True
        msg = receiver.recv(timeout=0.5)
        assert msg is not None and msg.arbitration_id == 0x456 and bytes(msg.data) == b"\xaa\x55"
    service.dispatch(req("can.close"))


def test_rejects_bad_ids_and_unverified_bus_params() -> None:
    service = MODULE.CanJsonlService(tx_enabled=True)
    bad_interface = service.dispatch(req("can.open", {"interface": "unknown", "config": {"unsafe": True}}))
    assert "error" in bad_interface
    bad_receive = service.dispatch(req("can.receive", {"timeout": 999}))
    assert "error" in bad_receive


def test_interface_list_has_virtual() -> None:
    service = MODULE.CanJsonlService()
    result = service.dispatch(req("can.interfaces.list"))
    assert "virtual" in result["result"]

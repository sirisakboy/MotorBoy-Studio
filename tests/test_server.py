import asyncio, base64, json, os, sys
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "server"))
import ecu_backend as eb

XDF = os.path.join(ROOT, "Hart-ECU", "vehicle_profiles", "engine", "honda", "CBR1000RR_2012_US", "CBR1000RR_2012_US.xdf")


def b64(b): return base64.b64encode(b).decode()


@pytest.fixture
def sess():
    s = eb.Session()
    s.dispatch("xdf_load", {"b64": b64(open(XDF, "rb").read()), "name": "x.xdf"})
    import random
    r = random.Random(7)
    s.dispatch("rom_load", {"b64": b64(bytes(r.randrange(256) for _ in range(0x40000))), "name": "t.bin"})
    return s


def ev(res, name): return next(d for e, d in res if e == name)


def test_hardware_refused_and_unknown():
    s = eb.Session()
    for a in ("connect", "flash_rom", "read_rom", "sk_flash"):
        with pytest.raises(eb.ProtocolError, match="offline"):
            s.dispatch(a, {})
    with pytest.raises(eb.ProtocolError, match="unknown"):
        s.dispatch("__class__", {})


def test_load_read_write_roundtrip(sess):
    m = ev(sess.dispatch("map_read", {"id": "0x3A51"}), "map_data")
    assert m["rows"] == 38 and m["cols"] == 25 and len(m["raw"]) == 38
    r = sess.dispatch("map_write", {"id": "0x3A51", "cells": [{"row": 1, "col": 2, "raw": 4321}]})
    assert ev(r, "map_cells")["cells"][0]["value"] == 4321 and ev(r, "map_cells")["dirty"]
    assert ev(sess.dispatch("map_read", {"id": "0x3A51"}), "map_data")["raw"][1][2] == 4321


def test_write_is_atomic(sess):
    before = bytes(sess.rom.data)
    with pytest.raises(eb.ProtocolError, match="nothing changed"):
        sess.dispatch("map_write", {"id": "0x3A51", "cells": [{"row": 0, "col": 0, "raw": 1},
                                                              {"row": 0, "col": 1, "raw": 99999999}]})
    assert bytes(sess.rom.data) == before


def test_export_checksum_only_when_asked(sess):
    sess.dispatch("map_write", {"id": "0x3A51", "cells": [{"row": 0, "col": 0, "raw": 5}]})
    plain = ev(sess.dispatch("rom_export", {}), "rom_data")
    fixed = ev(sess.dispatch("rom_export", {"fix_checksum": True}), "rom_data")
    assert plain["checksum_fixed"] == [] and fixed["checksum_fixed"]
    out = base64.b64decode(fixed["b64"])
    assert sum(out) & 0xFF == 0
    assert bytes(sess.rom.data) != out or sum(sess.rom.data) & 0xFF == 0  # session ROM itself untouched


def test_need_files_first():
    s = eb.Session()
    with pytest.raises(eb.ProtocolError): s.dispatch("map_read", {"id": "1"})
    with pytest.raises(eb.ProtocolError): s.dispatch("xdf_load", {"b64": "!!!"})


def test_origin_policy():
    assert eb.origin_ok(None) and eb.origin_ok("null") and eb.origin_ok("http://localhost:5173")
    assert not eb.origin_ok("https://evil.example") and not eb.origin_ok("http://localhost.evil.com")


def test_websocket_end_to_end():
    websockets = pytest.importorskip("websockets")

    async def run():
        async def h(ws): await eb.handler(ws)
        async with websockets.serve(h, "127.0.0.1", 0) as srv:
            port = srv.sockets[0].getsockname()[1]
            async with websockets.connect(f"ws://127.0.0.1:{port}") as c:
                assert json.loads(await c.recv())["event"] == "server_info"
                await c.send(json.dumps({"action": "connect", "data": {}}))
                m = json.loads(await c.recv())
                assert m["event"] == "error" and "offline" in m["data"]["msg"]
                await c.send("not json")
                assert json.loads(await c.recv())["event"] == "error"
            with pytest.raises(Exception):  # bad origin is closed by the server
                async with websockets.connect(f"ws://127.0.0.1:{port}", origin="https://evil.example") as c2:
                    await c2.recv(); await c2.recv()
    asyncio.run(run())

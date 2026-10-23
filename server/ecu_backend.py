#!/usr/bin/env python3
"""MotorBoy offline XDF/BIN WebSocket backend for web/ecu_real.html.

Protocol (same envelope as the frontend): client -> {"action", "data"},
server -> {"event", "data"}.  OFFLINE ONLY: every hardware action (connect, read/flash ROM,
live data, SmartKey ...) is refused.  Binds to 127.0.0.1 and only accepts local/file origins.

    python server/ecu_backend.py [--host 127.0.0.1] [--port 8765] [--allow-origin URL]
"""
import argparse
import asyncio
import base64
import binascii
import io
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from xdfengine import (Rom, XdfFormatError, checksum_status, diff_roms,  # noqa: E402
                       fix_checksum, parse_xdf, read_table, validate, write_cell)

VERSION = "1.0-offline"
MAX_BYTES = 8 * 1024 * 1024
MAX_CELLS = 4096
HARDWARE = {"connect", "disconnect", "read_rom", "flash_rom", "read_dtc", "clear_dtc", "start_live",
            "stop_live", "sk_request_seed", "sk_send_key", "sk_read_slots", "sk_register_key",
            "sk_reset", "sk_factory_reset", "sk_flash", "sk_verify", "calc_checksum",
            "sensor_read", "sensor_read_all", "sensor_test", "sensor_toggle",
            "sensor_enable_all", "sensor_disable_all"}


class ProtocolError(Exception):
    pass


def _clean(o):
    """JSON-safe: NaN/inf -> None."""
    if isinstance(o, float):
        return o if math.isfinite(o) else None
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    return o


def _b64(data, what):
    try:
        raw = base64.b64decode(data.get("b64", ""), validate=True)
    except (binascii.Error, ValueError, AttributeError) as e:
        raise ProtocolError(f"{what}: invalid base64") from e
    if not raw or len(raw) > MAX_BYTES:
        raise ProtocolError(f"{what}: empty or larger than {MAX_BYTES} bytes")
    return raw


class Session:
    def __init__(self):
        self.xdf = self.rom = None
        self.xdf_name = self.rom_name = ""

    # -- helpers ----------------------------------------------------------
    def table(self, ident):
        if not self.xdf:
            raise ProtocolError("load an XDF first")
        try:
            return self.xdf.get(ident)
        except KeyError as e:
            raise ProtocolError(e.args[0]) from e

    def need_rom(self):
        if not self.rom:
            raise ProtocolError("load a BIN first")
        return self.rom

    def ck(self):
        if not (self.xdf and self.rom):
            return []
        out = []
        for cs in self.xdf.checksums:
            ok, st, comp = checksum_status(self.rom, cs)
            out.append({"title": cs.title, "supported": ok, "stored": st, "computed": comp,
                        "ok": bool(ok and st == comp), "addr": cs.store_addr})
        return out

    def map_payload(self, t):
        d = read_table(self.xdf, self.need_rom(), t)
        num = lambda vs: [v if isinstance(v, (int, float)) else i for i, v in enumerate(vs)]  # noqa: E731
        z = t.z
        return {"id": t.uid, "title": t.title, "rows": z.rows, "cols": z.cols,
                "x": d.x, "y": d.y, "x_num": num(d.x) or list(range(z.cols)),
                "y_num": num(d.y) or list(range(z.rows)),
                "raw": d.raw, "values": d.values, "address": f"0x{z.address:X}",
                "bits": z.elem_bits, "signed": z.signed, "lsb": z.lsb, "equation": z.equation,
                "decimals": z.decimals, "categories": t.categories, "dirty": self.rom.dirty}

    # -- actions ----------------------------------------------------------
    def dispatch(self, action, data):
        """Return list of (event, data). Raises ProtocolError for client mistakes."""
        if action == "ping":
            return [("pong", {})]
        if action in HARDWARE:
            raise ProtocolError(f"'{action}' disabled: offline XDF/BIN server (no hardware access)")
        h = getattr(self, "do_" + action, None)
        if not h:
            raise ProtocolError(f"unknown action '{action}'")
        return h(data or {})

    def do_list_ports(self, d):
        return [("ports", {"ports": []}), ("log", {"msg": "Offline server: no serial ports", "level": "info"})]

    def do_xdf_load(self, d):
        raw = _b64(d, "xdf")
        self.xdf = parse_xdf(io.BytesIO(raw))
        self.xdf_name = str(d.get("name", ""))[:120]
        tabs = [{"id": t.uid, "title": t.title, "rows": t.z.rows, "cols": t.z.cols, "bits": t.z.elem_bits,
                 "categories": t.categories, "editable": not t.z.static} for t in self.xdf.tables]
        ev = [("xdf_loaded", {"title": self.xdf.title, "name": self.xdf_name, "tables": tabs,
                              "checksums": len(self.xdf.checksums)})]
        return ev + self._rom_checks()

    def do_rom_load(self, d):
        raw = _b64(d, "bin")
        self.rom, self.rom_name = Rom(raw), str(d.get("name", ""))[:120]
        return [("rom_loaded", {"name": self.rom_name, "size": len(self.rom),
                                "crc32": f"{self.rom.crc32():08X}",
                                "issues": validate(self.xdf, len(self.rom)) if self.xdf else [],
                                "checksum": self.ck()})]

    def _rom_checks(self):
        if self.xdf and self.rom:
            return [("log", {"level": "warning", "msg": m}) for m in validate(self.xdf, len(self.rom))[:5]]
        return []

    def do_map_read(self, d):
        return [("map_data", self.map_payload(self.table(d.get("id"))))]

    def do_map_write(self, d):
        t, rom = self.table(d.get("id")), self.need_rom()
        cells = d.get("cells")
        if not isinstance(cells, list) or not cells or len(cells) > MAX_CELLS:
            raise ProtocolError(f"cells: list of 1..{MAX_CELLS} required")
        snap, out = bytes(rom.data), []
        try:
            for c in cells:
                kw = {"clamp": bool(d.get("clamp", False))}
                if "raw" in c:
                    kw["raw"] = int(c["raw"])
                elif "value" in c:
                    kw["value"] = float(c["value"])
                else:
                    raise ProtocolError("each cell needs 'raw' or 'value'")
                r, col = int(c["row"]), int(c["col"])
                raw = write_cell(self.xdf, rom, t, r, col, **kw)
                out.append({"row": r, "col": col, "raw": raw})
        except (ValueError, IndexError, KeyError, TypeError) as e:
            rom.data[:] = snap  # atomic: all cells or none
            raise ProtocolError(f"write rejected, nothing changed: {e}") from e
        except ProtocolError:
            rom.data[:] = snap
            raise
        full = self.map_payload(t)
        for o in out:
            o["value"] = full["values"][o["row"]][o["col"]]
        return [("map_cells", {"id": t.uid, "cells": out, "dirty": rom.dirty}),
                ("log", {"level": "success", "msg": f"{t.title}: {len(out)} cell(s) written (checksum NOT updated)"})]

    def do_rom_revert(self, d):
        rom = self.need_rom()
        rom.data[:] = rom.original
        return [("rom_reverted", {"dirty": False}), ("log", {"level": "warning", "msg": "ROM reverted to loaded file"})]

    def do_checksum_status(self, d):
        self.need_rom()
        if not self.xdf:
            raise ProtocolError("load an XDF first")
        return [("checksum", {"items": self.ck()})]

    def do_rom_diff(self, d):
        rom = self.need_rom()
        if not self.xdf:
            raise ProtocolError("load an XDF first")
        return [("rom_diff", {"tables": [{"title": a, "cells": b} for a, b in diff_roms(self.xdf, Rom(rom.original), rom)]})]

    def do_rom_export(self, d):
        rom = self.need_rom()
        out = Rom(bytes(rom.data))
        fixed = []
        if d.get("fix_checksum"):
            if not self.xdf:
                raise ProtocolError("load an XDF to fix checksum")
            for cs in self.xdf.checksums:
                fixed.append(f"0x{fix_checksum(out, cs):02X}@0x{cs.store_addr:X}")
        name = (os.path.splitext(self.rom_name or "rom")[0] + "_mod.bin")
        return [("rom_data", {"name": name, "b64": base64.b64encode(bytes(out.data)).decode(),
                              "crc32": f"{out.crc32():08X}", "checksum_fixed": fixed}),
                ("log", {"level": "success" if fixed or not rom.dirty else "warning",
                         "msg": "exported " + name + (" · checksum fixed " + ",".join(fixed) if fixed
                                                      else " · checksum NOT updated")})]


# -- WebSocket plumbing -----------------------------------------------------
LOCAL_ORIGINS = {None, "null", "http://localhost", "http://127.0.0.1"}


def origin_ok(origin, extra=()):
    if origin in LOCAL_ORIGINS or origin in extra:
        return True
    return bool(origin) and origin.split(":")[0:2] in (["http", "//localhost"], ["http", "//127.0.0.1"])


async def handler(ws, extra=()):
    hdrs = getattr(getattr(ws, "request", None), "headers", None) or getattr(ws, "request_headers", {})
    if not origin_ok(hdrs.get("Origin"), extra):
        await ws.close(code=1008, reason="origin not allowed")
        return
    s = Session()

    async def send(ev, data):
        await ws.send(json.dumps({"event": ev, "data": _clean(data)}, allow_nan=False))

    await send("server_info", {"version": VERSION, "mode": "offline-xdf", "ecu_count": 0, "dtc_count": 0})
    async for msg in ws:
        try:
            m = json.loads(msg)
            if not isinstance(m, dict):
                raise ProtocolError("message must be an object")
            for ev, data in s.dispatch(m.get("action"), m.get("data")):
                await send(ev, data)
        except (json.JSONDecodeError, ProtocolError, XdfFormatError) as e:
            await send("error", {"msg": str(e)})
        except Exception as e:  # keep the socket alive on engine errors
            await send("error", {"msg": f"{type(e).__name__}: {e}"})


async def serve(host, port, extra=()):
    import websockets
    async with websockets.serve(lambda ws: handler(ws, extra), host, port, max_size=2 * MAX_BYTES) as srv:
        print(f"MotorBoy offline backend {VERSION} on ws://{host}:{port}  (hardware disabled)")
        await asyncio.Future()


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--allow-origin", action="append", default=[])
    a = ap.parse_args()
    try:
        asyncio.run(serve(a.host, a.port, tuple(a.allow_origin)))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

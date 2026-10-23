"""BIN access + table decode/encode driven by an Xdf definition (offline only)."""
import struct
import zlib
from dataclasses import dataclass
from typing import List, Optional

from .equation import Equation
from .model import Axis, ChecksumDef, Table, Xdf


class Rom:
    def __init__(self, data):
        self.data = bytearray(data)
        self.original = bytes(data)

    @classmethod
    def load(cls, path):
        with open(path, "rb") as f:
            return cls(f.read())

    def save(self, path):
        with open(path, "wb") as f:
            f.write(self.data)

    def __len__(self):
        return len(self.data)

    @property
    def dirty(self):
        return bytes(self.data) != self.original

    def crc32(self):
        return zlib.crc32(self.data) & 0xFFFFFFFF

    def _check(self, addr, n):
        if addr < 0 or addr + n > len(self.data):
            raise IndexError(f"0x{addr:X}+{n} outside ROM (size 0x{len(self.data):X})")

    def get(self, addr, bits, signed=False, lsb=False, is_float=False):
        n = bits // 8
        self._check(addr, n)
        b = bytes(self.data[addr:addr + n])
        if is_float:
            return struct.unpack(("<" if lsb else ">") + {4: "f", 8: "d"}[n], b)[0]
        return int.from_bytes(b, "little" if lsb else "big", signed=signed)

    def put(self, addr, bits, raw, signed=False, lsb=False, is_float=False):
        n = bits // 8
        self._check(addr, n)
        if is_float:
            b = struct.pack(("<" if lsb else ">") + {4: "f", 8: "d"}[n], raw)
        else:
            raw = int(raw)
            lo, hi = (-(1 << (bits - 1)), (1 << (bits - 1)) - 1) if signed else (0, (1 << bits) - 1)
            if not lo <= raw <= hi:
                raise ValueError(f"raw {raw} outside {bits}-bit {'signed' if signed else 'unsigned'} range [{lo}, {hi}]")
            b = raw.to_bytes(n, "little" if lsb else "big", signed=signed)
        self.data[addr:addr + n] = b


# ---- layout ---------------------------------------------------------------
def _eff(xdf: Xdf, addr):
    return addr - xdf.base_offset if xdf.base_subtract else addr + xdf.base_offset


def _layout(xdf: Xdf, a: Axis, kind):
    """Byte addresses as [rows][cols]. kind: 'x' (1 row), 'y' (1 col), 'z' (grid)."""
    if a.elem_bits % 8:
        raise ValueError("bit-packed elements are not supported")
    base, eb = _eff(xdf, a.address), a.elem_bits // 8
    if kind == "x":
        st = (a.major // 8) if a.major > 0 else eb
        return [[base + c * st for c in range(a.count)]]
    if kind == "y":
        st = (a.major // 8) if a.major > 0 else eb
        return [[base + r * st] for r in range(a.count)]
    col = (a.minor // 8) if a.minor > 0 else eb
    row = (a.major // 8) if a.major > 0 else a.cols * col
    return [[base + r * row + c * col for c in range(a.cols)] for r in range(a.rows)]


def _eq(a: Axis):
    return Equation(a.equation, "X", a.elem_bits, a.signed)


def _axis_values(xdf, rom, a: Optional[Axis], kind):
    if a is None:
        return []
    if a.static:
        out = []
        for i in range(a.count):
            s = a.labels.get(i, str(i))
            try:
                out.append(float(s))
            except ValueError:
                out.append(s)
        return out
    eq = _eq(a)
    cells = _layout(xdf, a, kind)
    flat = [c for r in cells for c in r]
    return [eq(rom.get(ad, a.elem_bits, a.signed, a.lsb, a.is_float)) for ad in flat]


@dataclass
class TableData:
    title: str
    x: list
    y: list
    raw: List[List[int]]
    values: List[List[float]]
    addresses: List[List[int]]


def read_table(xdf: Xdf, rom: Rom, t: Table) -> TableData:
    z = t.z
    if z.static:
        raise ValueError(f"{t.title}: z axis has no address")
    eq, cells = _eq(z), _layout(xdf, z, "z")
    raw = [[rom.get(ad, z.elem_bits, z.signed, z.lsb, z.is_float) for ad in row] for row in cells]
    vals = [[eq(v) for v in row] for row in raw]
    return TableData(t.title, _axis_values(xdf, rom, t.x, "x"), _axis_values(xdf, rom, t.y, "y"),
                     raw, vals, cells)


def write_cell(xdf: Xdf, rom: Rom, t: Table, row, col, value=None, raw=None, clamp=False):
    """Set one z cell by scaled `value` or by `raw`. Returns raw written."""
    z = t.z
    if not (0 <= row < z.rows and 0 <= col < z.cols):
        raise IndexError(f"cell ({row},{col}) outside {z.rows}x{z.cols}")
    if raw is None:
        if value is None:
            raise ValueError("value or raw required")
        raw = _eq(z).inverse(value, clamp=clamp)
    addr = _layout(xdf, z, "z")[row][col]
    rom.put(addr, z.elem_bits, raw, z.signed, z.lsb, z.is_float)
    return raw


def validate(xdf: Xdf, rom_size: int):
    """Return list of problems (tables whose cells fall outside the ROM)."""
    bad = []
    for t in xdf.tables:
        for name, a, kind in (("x", t.x, "x"), ("y", t.y, "y"), ("z", t.z, "z")):
            if a is None or a.static:
                continue
            try:
                cells = _layout(xdf, a, kind)
            except ValueError as e:
                bad.append(f"{t.title}/{name}: {e}")
                continue
            hi = max(c for r in cells for c in r) + a.elem_bits // 8
            lo = min(c for r in cells for c in r)
            if lo < 0 or hi > rom_size:
                bad.append(f"{t.title}/{name}: 0x{lo:X}..0x{hi:X} outside ROM 0x{rom_size:X}")
    return bad


# ---- checksum (Honda 8-bit, same as HondaECU/eculib) ------------------------
def honda8(data):
    return ((sum(bytearray(data)) ^ 0xFF) + 1) & 0xFF


def checksum_status(rom: Rom, cs: ChecksumDef):
    """(supported, stored, computed). Only 8-bit Honda sum (method 0) is supported."""
    if cs.method != 0 or cs.store_bits != 8 or cs.end >= len(rom) or not cs.start <= cs.store_addr <= cs.end:
        return False, None, None
    d = rom.data
    body = bytes(d[cs.start:cs.store_addr]) + bytes(d[cs.store_addr + 1:cs.end + 1])
    return True, d[cs.store_addr], honda8(body)


def fix_checksum(rom: Rom, cs: ChecksumDef):
    ok, _, comp = checksum_status(rom, cs)
    if not ok:
        raise ValueError("unsupported checksum definition")
    rom.data[cs.store_addr] = comp
    return comp


def diff_roms(xdf: Xdf, a: Rom, b: Rom):
    """Per-table count of changed cells between two ROMs."""
    out = []
    for t in xdf.tables:
        try:
            da, db = read_table(xdf, a, t), read_table(xdf, b, t)
        except (IndexError, ValueError):
            continue
        n = sum(1 for ra, rb in zip(da.raw, db.raw) for p, q in zip(ra, rb) if p != q)
        if n:
            out.append((t.title, n))
    return out

"""TunerPro XDF (XDFFORMAT 1.60) parser -> plain dataclasses."""
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Dict, List, Optional


def _i(v, default=None):
    if v is None or str(v).strip() == "":
        return default
    try:
        return int(str(v).strip(), 0)
    except ValueError:
        return default


@dataclass
class Defaults:
    bits: int = 8
    signed: bool = False
    lsb: bool = False
    is_float: bool = False


@dataclass
class Axis:
    id: str
    address: Optional[int] = None
    elem_bits: int = 8
    rows: int = 1
    cols: int = 1
    major: int = 0
    minor: int = 0
    signed: bool = False
    lsb: bool = False
    is_float: bool = False
    count: int = 1
    equation: str = "X"
    decimals: int = 2
    labels: Dict[int, str] = field(default_factory=dict)
    vmin: Optional[float] = None
    vmax: Optional[float] = None
    units: str = ""

    @property
    def static(self):
        return self.address is None


@dataclass
class Table:
    uid: str
    title: str
    categories: List[str]
    x: Optional[Axis]
    y: Optional[Axis]
    z: Axis
    flags: int = 0


@dataclass
class ChecksumDef:
    uid: str
    title: str
    start: int
    end: int
    store_addr: int
    store_bits: int
    method: int


@dataclass
class Xdf:
    title: str
    base_offset: int
    base_subtract: bool
    defaults: Defaults
    region_size: Optional[int]
    categories: Dict[int, str]
    tables: List[Table]
    checksums: List[ChecksumDef]

    def get(self, ident):
        """Exactly one table by uniqueid (e.g. 0x3A51) or by unique title; else KeyError."""
        ident = str(ident).strip()
        m = [t for t in self.tables if t.uid.lower() == ident.lower()] or \
            [t for t in self.tables if t.title == ident]
        if len(m) != 1:
            raise KeyError(f"{ident!r}: {len(m)} matches (use the uniqueid from `list`)")
        return m[0]

    def find(self, title):
        t = [t for t in self.tables if t.title == title]
        if not t:
            t = [t for t in self.tables if title.lower() in t.title.lower()]
        return t


def _parse_axis(el, d: Defaults):
    emb = el.find("EMBEDDEDDATA")
    a = Axis(id=el.get("id", "z"))
    a.elem_bits = d.bits
    a.signed, a.lsb, a.is_float = d.signed, d.lsb, d.is_float
    if emb is not None:
        a.address = _i(emb.get("mmedaddress"))
        a.elem_bits = _i(emb.get("mmedelementsizebits"), d.bits)
        a.rows = _i(emb.get("mmedrowcount"), 1)
        a.cols = _i(emb.get("mmedcolcount"), 1)
        a.major = _i(emb.get("mmedmajorstridebits"), 0)
        a.minor = _i(emb.get("mmedminorstridebits"), 0)
        # mmedtypeflags: 0x01 signed, 0x02 LSB first, 0x04 float. When absent the
        # element is unsigned big-endian: header <DEFAULTS> only seeds new items
        # in the editor (verified against real ROMs: MGZ vs MJW).
        tf = _i(emb.get("mmedtypeflags"), 0)
        a.signed, a.lsb, a.is_float = bool(tf & 1), bool(tf & 2), bool(tf & 4)
    a.count = _i(el.findtext("indexcount"), 0) or 0
    a.decimals = _i(el.findtext("decimalpl"), 2)
    m = el.find("MATH")
    if m is not None and m.get("equation"):
        a.equation = m.get("equation")
    for lab in el.findall("LABEL"):
        a.labels[_i(lab.get("index"), 0)] = lab.get("value", "")
    for k, attr in (("min", "vmin"), ("max", "vmax")):
        try:
            setattr(a, attr, float(el.findtext(k)))
        except (TypeError, ValueError):
            pass
    return a


class XdfFormatError(ValueError):
    """Unsupported/invalid XDF (e.g. legacy binary V4)."""


def parse_xdf(path) -> Xdf:
    """`path` may be a filename or a binary file-like object."""
    if hasattr(path, "read"):
        raw = path.read()
    else:
        with open(path, "rb") as f:
            raw = f.read()
    if raw[:3] == b"\x05\x22\x97":
        raise XdfFormatError("legacy binary XDF (TunerPro V4) is not supported; "
                             "open it in TunerPro and Save As to V5 XML")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        raise XdfFormatError(f"not a valid XML XDF: {e}") from e
    if root.tag != "XDFFORMAT":
        raise ValueError("not an XDF file")
    h = root.find("XDFHEADER")
    dm = h.find("DEFAULTS")
    d = Defaults()
    if dm is not None:
        d = Defaults(_i(dm.get("datasizeinbits"), 8), dm.get("signed") == "1",
                     dm.get("lsbfirst") == "1", dm.get("float") == "1")
    bo = h.find("BASEOFFSET")
    reg = h.find("REGION")
    cats = {_i(c.get("index"), 0): c.get("name", "") for c in h.findall("CATEGORY")}
    tables = []
    for t in root.findall("XDFTABLE"):
        axes = {a.get("id"): _parse_axis(a, d) for a in t.findall("XDFAXIS")}
        if "z" not in axes:
            continue
        z = axes["z"]
        x, y = axes.get("x"), axes.get("y")
        if x and x.count:
            z.cols = z.cols if z.cols > 1 else x.count
        if y and y.count:
            z.rows = z.rows if z.rows > 1 else y.count
        cm = [cats.get(_i(c.get("category"), -1), "") for c in t.findall("CATEGORYMEM")]
        tables.append(Table(t.get("uniqueid", ""), (t.findtext("title") or "").strip(),
                            [c for c in cm if c], x, y, z, _i(t.get("flags"), 0)))
    sums = []
    for c in root.findall("XDFCHECKSUM"):
        r = c.find("REGION")
        if r is None:
            continue
        sums.append(ChecksumDef(c.get("uniqueid", ""), (c.findtext("title") or "").strip(),
                                _i(r.findtext("datastart"), 0), _i(r.findtext("dataend"), 0),
                                _i(r.findtext("storeaddress"), 0), _i(r.findtext("storesizebits"), 8),
                                _i(r.findtext("calculationmethod"), 0)))
    return Xdf(
        title=(h.findtext("deftitle") or "").strip(),
        base_offset=_i(bo.get("offset"), 0) if bo is not None else 0,
        base_subtract=(bo.get("subtract") == "1") if bo is not None else False,
        defaults=d,
        region_size=(_i(reg.get("size")) if reg is not None else None),
        categories=cats, tables=tables, checksums=sums)

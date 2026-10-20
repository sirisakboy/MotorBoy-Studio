import os, sys, random
import pytest
ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
from xdfengine import (Equation, EquationError, Rom, parse_xdf, read_table, write_cell,
                       validate, checksum_status, fix_checksum, diff_roms)

PROF = os.path.join(ROOT, "Hart-ECU", "vehicle_profiles", "engine", "honda")
CBR = os.path.join(PROF, "CBR1000RR_2012_US", "CBR1000RR_2012_US.xdf")
CRF = os.path.join(PROF, "CRF110F_2019_KYK-D12_candidate", "38770-KYK-D12.xdf")


def test_equation_linear_and_inverse():
    e = Equation("(250*X/799)+10", raw_bits=16)
    assert e(0) == 10 and abs(e(799) - 260) < 1e-9
    assert e.inverse(e(400)) == 400


def test_equation_shift_nonlinear_inverse():
    e = Equation("X >> 4", raw_bits=8)
    assert e(0x50) == 5 and e.inverse(5) in range(0x50, 0x60)


def test_equation_rejects_unsafe():
    for bad in ("__import__('os')", "X.real", "open('x')", "[1]"):
        with pytest.raises(EquationError):
            Equation(bad)


def test_inverse_range_check():
    e = Equation("X", raw_bits=8)
    with pytest.raises(ValueError):
        e.inverse(300)
    assert e.inverse(300, clamp=True) == 255


@pytest.fixture(scope="module")
def xdf():
    return parse_xdf(CBR)


def test_parse_and_bounds(xdf):
    assert len(xdf.tables) == 39 and len(xdf.checksums) == 1
    assert validate(xdf, 0x40000) == []
    assert validate(xdf, 0x10000)  # too small ROM is reported


def test_crf_candidate_parses():
    x = parse_xdf(CRF)
    assert x.defaults.lsb and validate(x, 0x10000) == []


def _rom(seed=1):
    r = random.Random(seed)
    return Rom(bytes(r.randrange(256) for _ in range(0x40000)))


def test_table_roundtrip_and_isolation(xdf):
    rom, t = _rom(), xdf.find("Cyl1")[0]
    before = bytes(rom.data)
    raw = write_cell(xdf, rom, t, 3, 4, raw=1234)
    d = read_table(xdf, rom, t)
    assert raw == 1234 and d.raw[3][4] == 1234 and d.values[3][4] == 1234
    changed = [i for i in range(len(before)) if before[i] != rom.data[i]]
    assert set(changed) <= {d.addresses[3][4], d.addresses[3][4] + 1}  # only that cell (big-endian 16-bit)
    assert rom.data[d.addresses[3][4]:d.addresses[3][4] + 2] == (1234).to_bytes(2, "big")


def test_scaled_axis_values(xdf):
    t = xdf.find("Cyl1")[0]
    d = read_table(xdf, _rom(), t)
    assert len(d.x) == 25 and len(d.y) == 38 and len(d.values) == 38 and len(d.values[0]) == 25


def test_checksum_fix_makes_rom_sum_zero(xdf):
    rom, cs = _rom(), xdf.checksums[0]
    ok, stored, comp = checksum_status(rom, cs)
    assert ok
    fix_checksum(rom, cs)
    assert sum(rom.data[cs.start:cs.end + 1]) & 0xFF == 0
    assert checksum_status(rom, cs)[1] == checksum_status(rom, cs)[2]


def test_diff_and_dirty(xdf):
    a = _rom(); b = Rom(bytes(a.data))
    assert not b.dirty
    t = xdf.find("Cyl1")[0]
    write_cell(xdf, b, t, 0, 0, raw=(read_table(xdf, b, t).raw[0][0] ^ 1))
    assert b.dirty and diff_roms(xdf, a, b) == [("Cyl1", 1)]


def test_write_bounds(xdf):
    t = xdf.find("Cyl1")[0]
    with pytest.raises(IndexError):
        write_cell(xdf, _rom(), t, 99, 0, raw=1)


def test_get_by_uid_and_duplicate_titles(xdf):
    assert xdf.get("0x3A51").title == "Cyl1"
    with pytest.raises(KeyError):
        xdf.get("Cyl1")  # four tables share this title

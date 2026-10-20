import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from checksum import checksum8bitHonda, calculate_ecu_checksum, fix_checksum


def test_honda_checksum_makes_rom_sum_zero():
    rom = bytearray(range(256)) * 4
    pos = 100
    rom[pos] = checksum8bitHonda(rom[:pos] + rom[pos + 1:])
    assert sum(rom) & 0xFF == 0


def test_fix_checksum_in_place_and_bounds():
    data = bytearray(16)
    assert fix_checksum(data, 3, 0xAB)[3] == 0xAB
    assert fix_checksum(data, 99, 0xFF) == data  # out of range: untouched
    assert fix_checksum(data, -1, 0xFF) == data  # no negative wraparound


def test_unknown_method():
    with pytest.raises(ValueError):
        calculate_ecu_checksum(b"\x00", "nope")


def test_matches_eculib_reference():
    ref = os.path.join(os.path.dirname(__file__), "..", "Hart-ECU")
    sys.path.insert(0, ref)
    honda = pytest.importorskip("eculib.honda")  # needs pylibftdi
    ref_ck = honda.checksum8bitHonda
    blob = bytes(range(200))
    assert checksum8bitHonda(blob) == ref_ck(blob)

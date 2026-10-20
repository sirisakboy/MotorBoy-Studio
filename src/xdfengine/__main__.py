"""CLI: python -m xdfengine <cmd> ...   (offline file editing only; never touches hardware)"""
import argparse
import json
import sys

from . import (Rom, parse_xdf, read_table, write_cell, validate, checksum_status,
               fix_checksum, diff_roms)


def _table(xdf, name):
    try:
        return xdf.get(name)
    except KeyError as e:
        sys.exit(f"{e.args[0]}\n" + "\n".join(f"  {t.uid:8s} {t.title}" for t in xdf.find(name)[:10]))


def main(argv=None):
    p = argparse.ArgumentParser(prog="xdfengine")
    sp = p.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("list"); a.add_argument("xdf")
    a = sp.add_parser("validate"); a.add_argument("xdf"); a.add_argument("bin")
    a = sp.add_parser("dump"); a.add_argument("xdf"); a.add_argument("bin"); a.add_argument("table", help="uniqueid (e.g. 0x3A51) or unique title")
    a.add_argument("--json", action="store_true")
    a = sp.add_parser("set"); a.add_argument("xdf"); a.add_argument("bin"); a.add_argument("table", help="uniqueid (e.g. 0x3A51) or unique title")
    a.add_argument("row", type=int); a.add_argument("col", type=int); a.add_argument("value", type=float)
    a.add_argument("-o", "--out", required=True, help="output file (input is never overwritten)")
    a.add_argument("--raw", action="store_true", help="value is a raw integer")
    a.add_argument("--fix-checksum", action="store_true")
    a = sp.add_parser("checksum"); a.add_argument("xdf"); a.add_argument("bin")
    a.add_argument("--fix", metavar="OUT")
    a = sp.add_parser("diff"); a.add_argument("xdf"); a.add_argument("a"); a.add_argument("b")
    n = p.parse_args(argv)
    xdf = parse_xdf(n.xdf)

    if n.cmd == "list":
        for t in xdf.tables:
            z = t.z
            print(f"{t.uid:8s} {t.title:36s} {z.rows:>3}x{z.cols:<3} {z.elem_bits:>2}b @0x{z.address or 0:X}  {'/'.join(t.categories)}")
    elif n.cmd == "validate":
        bad = validate(xdf, len(Rom.load(n.bin)))
        print("\n".join(bad) if bad else "OK: all tables inside ROM")
        return 1 if bad else 0
    elif n.cmd == "dump":
        d = read_table(xdf, Rom.load(n.bin), _table(xdf, n.table))
        if n.json:
            print(json.dumps({"title": d.title, "x": d.x, "y": d.y, "raw": d.raw, "values": d.values}))
        else:
            print("x:", d.x); print("y:", d.y)
            for r, row in zip(d.y or [""] * len(d.values), d.values):
                print(f"{r!s:>8} | " + " ".join(f"{v:8.2f}" for v in row))
    elif n.cmd == "set":
        rom, t = Rom.load(n.bin), _table(xdf, n.table)
        raw = write_cell(xdf, rom, t, n.row, n.col, raw=int(n.value)) if n.raw else \
            write_cell(xdf, rom, t, n.row, n.col, value=n.value)
        print(f"wrote raw {raw} at cell ({n.row},{n.col})")
        if n.fix_checksum:
            for cs in xdf.checksums:
                print("checksum ->", hex(fix_checksum(rom, cs)))
        else:
            print("note: checksum NOT updated (use --fix-checksum)")
        rom.save(n.out)
    elif n.cmd == "checksum":
        rom = Rom.load(n.bin)
        for cs in xdf.checksums:
            ok, st, comp = checksum_status(rom, cs)
            print(f"{cs.title}: " + ("unsupported" if not ok else f"stored=0x{st:02X} computed=0x{comp:02X} {'OK' if st == comp else 'MISMATCH'}"))
            if n.fix and ok:
                fix_checksum(rom, cs)
        if n.fix:
            rom.save(n.fix); print("saved", n.fix)
    elif n.cmd == "diff":
        for title, c in diff_roms(xdf, Rom.load(n.a), Rom.load(n.b)):
            print(f"{title:40s} {c} cells")
    return 0


if __name__ == "__main__":
    sys.exit(main())

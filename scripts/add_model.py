#!/usr/bin/env python3
"""
Helper script to add new Honda ECU models to the database.

Usage:
    python add_model.py

This will prompt you for the model information and generate the 
appropriate entry for ecmids.py and an XDF file template.
"""

import json
import os

def get_model_info():
    """Prompt user for model information."""
    print("=== Honda ECU Model Registration ===\n")
    
    ecmid = input("ECM ID (5 bytes hex, e.g., 0100aa0102): ").strip()
    model = input("Model name: ").strip()
    year = input("Year(s) (e.g., 2020 or 2018-2020): ").strip()
    pn = input("Part number (Keihin code): ").strip()
    rom_size_kb = int(input("ROM size (KB): ").strip())
    has_ecmid = input("Has ECM ID address? (y/n): ").strip().lower() == 'y'
    has_keihin = input("Has Keihin address? (y/n): ").strip().lower() == 'y'
    
    entries = {
        "ecmid": ecmid,
        "model": model,
        "year": year,
        "pn": pn,
        "rom_size_kb": rom_size_kb,
    }
    
    # Auto-detect checksum location
    checksum_offsets = {
        48: "0x0",
        56: "0xDFEF",
        64: "0x0",
        92: "0x0",
        128: "0x0",
        256: "0x3FFF8",
        512: "0x7FFF8",
        1024: "0xFFFF8",
    }
    entries["checksum"] = checksum_offsets.get(rom_size_kb, "0x0")
    
    if has_ecmid:
        entries["ecmidaddr"] = input("ECM ID address (hex, e.g., 0x7FF5C): ").strip()
    
    if has_keihin:
        entries["keihinaddr"] = input("Keihin address (hex, e.g., 0x3FFDE): ").strip()
    
    return entries

def generate_ecmids_entry(entry):
    """Generate the Python dict entry for ecmids.py."""
    key = f'b"\\x{entry["ecmid"]}"'
    values = [
        f'"model": "{entry["model"]}"',
        f'"year": "{entry["year"]}"',
        f'"pn": "{entry["pn"]}", "checksum": {entry["checksum"]}'
    ]
    if "ecmidaddr" in entry:
        values.append(f'"ecmidaddr": {entry["ecmidaddr"]}')
    if "keihinaddr" in entry:
        values.append(f'"keihinaddr": {entry["keihinaddr"]}')
    
    return f'''    {key}:
        {{", ".join(values)}},'''

def main():
    entry = get_model_info()
    print("\n=== Generated Entry ===")
    print(generate_ecmids_entry(entry))
    
    print("\n=== XDF Template Information ===")
    print(f"Model: {entry['model']}")
    print(f"Part Number: {entry['pn']}")
    print(f"ROM Size: {entry['rom_size_kb']} KB")
    print(f"Checksum: {entry['checksum']}")
    if "ecmidaddr" in entry:
        print(f"ECM ID Address: {entry['ecmidaddr']}")
    if "keihinaddr" in entry:
        print(f"Keihin Address: {entry['keihinaddr']}")

if __name__ == "__main__":
    main()
# HondaECU Project Updates

## Recent Changes

### 1. Fixed Import Issues
- Added missing `tarfile` import in `src/frames/flash.py`
- Added missing `time` and `struct` imports in `src/threads/kline.py`
- Removed incorrect import `from .checksum import ...` which pointed to non-existent module

### 2. Fixed Code Issues
- Removed duplicate `Build()` method in `src/frames/flash.py`
- Fixed syntax warning `if t is not 0x13` to `if t != 0x13` in `src/frames/data.py`
- Properly using `do_validation` from `eculib.honda`

### 3. Added Auto Checksum Offset Detection
- New method `auto_detect_checksum_offset()` in `flash.py`
- Automatically detects checksum location based on ROM file size
- Supports common Honda ECU sizes: 48KB, 56KB, 64KB, 92KB, 128KB, 256KB, 512KB, 1024KB

### 4. Improved Installation Process
- Created `setup.py` and `pyproject.toml` for modern Python packaging
- Created `setup.sh` for easy environment setup
- Updated `requirements.txt` to use available packages

### 5. Added ECUSTATE Extension
- Created `src/ecustate.py` with extended ECUSTATE enum including SECURE state
- Updated `src/controlpanel.py` to use the extended ECUSTATE
- Updated `src/frames/flash.py` and `src/frames/eeprom.py` to use extended ECUSTATE

### 6. Added Documentation
- Created `MODELS.md` with model database documentation
- Created `scripts/add_model.py` helper script for adding new models
- Added checksums, ecmid, and keihin address references

### 7. Added New Models from PDF Sources
- Created `databases/ecu_data.json` with ECU information from PDF files
- Created `src/ecudata.py` module to access the database
- Imported data from Honda DLC codes, Suzuki ECU data, KTM fault codes

## New Features

### Auto Checksum Offset Detection
When writing a `.bin` file with the "Fix" checkbox checked, the tool will now:
1. Automatically detect the ROM file size
2. Determine the correct checksum offset based on the size
3. Set the checksum location automatically

### Model Database
New data structure for easily adding/racking new Honda models:
```python
ECM_IDs = {
    b"\x01\x00\xaa\x01\x02": {
        "model": "VFR 1200 F",
        "year": "2010-2011",
        "pn": "38770-MGE-D02",
        "checksum": "0x7FFF8",
        "ecmidaddr": "0x7FF5C"
    },
    ...
}
```

## ECU Models Added from PDF Sources

### Honda (2022-2023)
- ADV 160 KOWL-NB1
- ADV-150 KOWA-N01, KOWF-T01, KOWH-M11
- GENIO K0J-N01, K0J-N71, K0J-N61
- NEW VARIO 125 K2VG-N32, K2VG-N42
- VERZA 150
- SPACY 110
- SCOOPY 110, SCOOPY K2F-N01, K2F-N11, K2F-N91 (2023)
- PCX 160 variants
- CRF 250 RALLY
- CRF 150 L

### Fault Codes Database
- **Honda DTC**: 100+ codes (ECM power, sensors, injectors, ignition)
- **KTM DTC**: P0xxx series fault codes
- **Suzuki ECU**: Multiple model variants with part numbers

## How to Add New Models

1. Check the ECM ID by reading the ECU
2. Edit `src/ecmids.py` and add the new entry
3. Create or update XDF file in `xdfs/<model_path>/`
4. Test the connection and flashing

Or use the helper script:
```bash
python scripts/add_model.py
```

## Installation

### Quick Start
```bash
./setup.sh
```

Or manually:
```bash
# Install eculib from local source
pip install ./eculib.tar.gz  # or use extracted eculib/ directory

# Install other dependencies
pip install -r requirements.txt
pip install wxPython  # for GUI
```

## Dependencies

Required packages (install via pip):
- `eculib` (from local eculib.tar.gz)
- `pyusb`
- `pydispatcher`
- `wxPython`
- `requests`
- `lxml`
- `numpy>=1.20`
- `colour`
- `pyparsing`
- `gitpython`
- `appdirs`

## File Locations

- Source code: `src/`
- ECU model definitions: `src/ecmids.py`
- ECU database: `databases/ecu_data.json`, `src/ecudata.py`
- XDF/TunerPro files: `xdfs/`
- Support scripts: `scripts/`
- Documentation: `MODELS.md`, `CHANGES.md`

## License

See LICENSE file for details.
## Stabilize pass (2026-10-21)
- flash.py: added missing `HondaECUAppPanel` / `dispatcher` imports (panel crashed on load/write); dropped unused imports
- Replaced `from eculib.honda import *` with explicit imports in frames/* and threads/kline.py
- ecustate.py: `ExtendedECUSTATE` used setattr on a plain Enum (members were bare ints, comparisons never matched) -> now built with Enum functional API
- checksum.py: `checksum8bitHonda` was a plain sum; now two's complement, identical to eculib
- Untracked committed `__pycache__`, extended `.gitignore`
- Added `tests/` (checksum, ECUSTATE) and GitHub Actions CI

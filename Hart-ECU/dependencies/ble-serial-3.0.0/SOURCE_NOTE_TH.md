# ble-serial 3.0.0 — source/provenance note

- **Source:** PyPI `ble-serial==3.0.0` source distribution, retained at `../source_archives/ble_serial-3.0.0.tar.gz`.
- **Archive SHA-256:** `86bcc3742d82647c56222356500dac84fa73aeeb7a333564e31712973a5e9bce` (70,819 bytes).
- **License:** MIT; upstream `LICENSE` is retained.
- **Extracted subset:** 27 files: `ble_serial/` package runtime source plus `LICENSE`, `README.md`, `pyproject.toml`, and `requirements.txt`. CI, tests, sample logs, notebooks, test-result CSVs and helper autoconnect daemons were not expanded. The exact sdist is retained. `FILE_INDEX.csv` contains path/size/SHA-256/role for each selected file.
- **Declared direct runtime dependencies:** `bleak>=0.20.0`, `coloredlogs>=15.0`; Windows path also declares `pyserial>=3.5`. These are not vendored.
- **Intended role:** convenience bridge for adapters that expose a compatible BLE-UART GATT service; upstream can create a POSIX PTY or use a TCP output mode. It is not Bluetooth Classic and does not infer ECU protocol or arbitrary BLE characteristic UUIDs.
- **Important platform caveat:** upstream Windows virtual-COM flow uses `com0com`. Its PyPI instructions warn that Windows 10+ may require Secure Boot to be disabled. This bundle does **not** recommend disabling Secure Boot; treat the extracted source as POSIX/reference-only unless Windows operation is redesigned and tested through a secure supported driver. `btleplug` is the alternative BLE GATT source for a native Windows path.
- **Important mode caveat:** upstream CLI defaults to `--permit rw`. Review and explicitly choose permissions before any use. No BLE adapter or ECU was tested. Source is unmodified; the companion note is not an endorsement for live ECU access.

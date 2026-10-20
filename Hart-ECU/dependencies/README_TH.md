# Third-party source dependencies

Source trees are kept isolated by version/license; only selected runtime files plus required license/build metadata are extracted. Exact official archives are retained under `source_archives/` when available. See each `SOURCE_NOTE_TH.md` and `FILE_INDEX.csv` for provenance, hashes, file roles and limitations.

| Component | Local path | License / status |
|---|---|---|
| libserialport | `libserialport/` | LGPL-3.0-or-later; curated C source/build subset, Linux timing test only |
| python-can 4.6.1 | `python-can-4.6.1/` | LGPL-3.0-only; runtime package source, official PyPI sdist retained; virtual-bus smoke test passed |
| btleplug 0.13.5 | `btleplug-0.13.5/` | `MIT/Apache-2.0/BSD-3-Clause`; official Crates.io crate retained; source reviewed but not built |
| ble-serial 3.0.0 | `ble-serial-3.0.0/` | MIT; selected Python package source and metadata; no BLE device test; Windows virtual-COM path not recommended because upstream setup may require disabling Secure Boot |

Runtime/transitive package dependencies are not vendored except where their own curated source is separately listed. Review and satisfy each license before combining or redistributing the application. This is a source pack, not a prebuilt installer.

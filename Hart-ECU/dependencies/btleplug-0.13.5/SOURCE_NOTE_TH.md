# btleplug 0.13.5 — source/provenance note

- **Source:** Crates.io `btleplug` crate 0.13.5, retained at `../source_archives/btleplug-0.13.5.crate`.
- **Crate SHA-256:** `3d836502de731602ea87cbb307065e8feaed4fd10f0855a75b0b87944ee011dc` (203,988 bytes); checksum matched the Crates.io API metadata reviewed on 2026-10-14.
- **License metadata:** `MIT/Apache-2.0/BSD-3-Clause`; upstream `LICENSE.md`, `Cargo.toml`, `.cargo_vcs_info.json`, and lockfile are retained. Review the applicable license notices before redistribution.
- **Extracted source:** complete 100-file crate package (812,210 uncompressed bytes), including `src/`, upstream examples, license and build/lock metadata. `FILE_INDEX.csv` records each file hash and groups source by API/backend/example/build role.
- **Intended role:** Rust host-side Bluetooth Low Energy central/GATT library. Upstream source includes Linux BlueZ, Windows WinRT, Apple CoreBluetooth and Android-specific implementations. It does **not** implement Bluetooth Classic/RFCOMM/SPP, BLE-UART UUID assumptions, ELM/KDS/SDS, or any ECU protocol.
- **Verification limitation:** Rust/Cargo are not installed in the build environment; this crate was not compiled, and no BLE device was paired or tested. A compatible Rust 2024 toolchain, platform SDKs and Cargo dependency resolution will be needed. The upstream example `examples/discover_adapters_peripherals.rs` is a starting point, not a verified adapter driver.
- **Safety:** GATT services/characteristics and device identity must be selected from a documented, authorized adapter. Do not send arbitrary GATT writes or treat a successful connection as ECU support.

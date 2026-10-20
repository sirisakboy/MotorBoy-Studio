# Read-only BLE discovery sidecar (Rust/btleplug)

## Scope

`src/main.rs` is a local stdin/stdout JSON-lines process for cross-language clients. It supports:

- `ble.adapters.list` — enumerate local BLE adapters and report OS/backend info/state.
- `ble.scan` — platform BLE advertisement scan for 1–30 seconds per adapter and report peripheral metadata (identifier/address/name/RSSI/service UUIDs). The OS/backend may use active scanning; this sample does not initiate a GATT connection.

It does **not** connect to any peripheral, discover services, read GATT values, subscribe to notifications, write characteristics, or issue vehicle/ECU requests. No network listener is opened. A successful scan is not an adapter match or ECU support claim.

Example input lines:

```json
{"jsonrpc":"2.0","id":1,"method":"ble.adapters.list","params":{}}
{"jsonrpc":"2.0","id":2,"method":"ble.scan","params":{"seconds":5}}
```

Exact response fields and constraints are in `../../core_contracts/BLE_SIDECAR_PROTOCOL.md`.

## Build and limitation

The wrapper uses the local `dependencies/btleplug-0.13.5` crate source plus Cargo dependencies declared in `Cargo.toml`. From pack root, on a Rust 2024-capable toolchain with Cargo and platform BLE prerequisites:

```sh
cargo run --manifest-path adapters/btleplug_scan/Cargo.toml
```

**Not compiled in this workspace:** `rustc` and `cargo` are unavailable, and no BLE adapter/device was tested. Static source review checked the used `Manager`, `Central`, `Peripheral`, `ScanFilter`, `adapter_info`, `adapter_state`, `start_scan`, `peripherals`, `stop_scan`, `id`, `address`, `properties`, and `is_connected` APIs against the pinned btleplug 0.13.5 source. This is not a compile guarantee; build/test before integration.

BLE scanning may have OS permission/location requirements and can disclose nearby device identifiers. Use only on devices/environments where discovery is authorized. This sample deliberately omits connect/GATT read/write paths.

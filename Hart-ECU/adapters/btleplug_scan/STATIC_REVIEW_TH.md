# Static review checklist — BLE sidecar

- Source dependency pinned to local `btleplug-0.13.5` crate; Cargo metadata declares Rust edition 2024.
- Imported methods/types were found in the included btleplug API: `Manager::new`, `Manager::adapters`, `Central::adapter_info/adapter_state/start_scan/peripherals/stop_scan`, `Peripheral::properties/is_connected/id/address`, and `ScanFilter::default`.
- No call sites for `connect`, `discover_services`, `read`, `write`, `subscribe`, notification streams, characteristic enumeration, or ECU protocol functions appear in this wrapper.
- Scan duration is bounded to 1–30 seconds per adapter; no network bind, process spawn, or persistent background task is included. OS/backend scanning may use active BLE scan requests; the wrapper performs no GATT connection.
- Output includes only peripheral ID/address/local name/RSSI/advertised service UUIDs and connection-state observation; it does not include arbitrary manufacturer payloads.
- **Build not verified:** no Rust toolchain is installed in the environment. Static API/source inspection is not a compile/test result. No Bluetooth device was present or tested.
- **Operational caveat:** host OS may request Bluetooth/location permissions, and scans expose nearby device metadata. Use only where authorized.

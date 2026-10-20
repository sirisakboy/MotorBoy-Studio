# Portability / plugin contract (draft)

This is an integration boundary, not an ECU protocol implementation.

## Layers

1. **Transport backend** owns OS/device I/O only (serial, J2534, CAN, BLE, USB, future adapters).
2. **Protocol plugin** consumes and emits byte/message frames; it must not open OS ports directly.
3. **ECU profile** declares model/ECU applicability, IDs, timings, data decoding, map/checksum metadata and evidence.
4. **Application/API** consumes normalized events/operations. GUI code does not speak to hardware directly.

## Cross-language rule

Expose the same versioned operation model through (a) JSON-RPC 2.0 over a local IPC endpoint for broad language reach, and (b) an optional C ABI for native clients. Publish JSON Schemas and test vectors; generate clients rather than reimplementing data shapes by hand.

## Minimum backend contract

A backend reports `id`, `version`, `supported_platforms`, `connection_types`, and explicit `capabilities`; it implements `enumerate`, `open`, `configure`, `read`, `write`, and `close` only where supported. Unsupported capabilities must be reported, not silently simulated.

## Current transport samples in this pack

- `adapters/can_jsonl_sidecar/` implements a local stdin/stdout JSON-lines CAN-frame API around `python-can`; its contract/schema are in `CAN_SIDECAR_PROTOCOL.md` and `CAN_SIDECAR_SCHEMA.json`. It does not open a network listener, and transmit is disabled unless explicitly enabled at process launch. The API intentionally stops at CAN frames—no ISO-TP/UDS/KWP/OEM requests are assumed.
- `transports/ip_socket/` provides generic TCP byte-stream and UDP datagram primitives. It does not select adapter ports, infer framing, or claim WiCAN/ELM/SLCAN/GVRET compatibility; transmit is off unless explicitly enabled by the caller.
- `adapters/btleplug_scan/` is a local, uncompiled Rust sidecar for BLE adapter listing and advertisement scanning only; `btleplug` is the BLE GATT source dependency. `ble-serial` is a source/reference bridge for matching BLE-UART devices. None is a verified ECU protocol or tested hardware adapter. Bluetooth Classic/SPP normally appears as an OS serial endpoint and should use the serial transport layer.

## ECU modules and exact profile matching

A profile must identify a **module**, not just a motorcycle make: `engine_ecu`, `abs`, `traction_control`, `transmission_tcu`, `instrument_cluster`, `immobilizer`, `bms_motor_controller`, `body_gateway`, or an explicit vendor-defined module. Record exact make/model/year/region and ECU part number plus hardware/software/calibration IDs when available. Make/model alone is not enough for offset/checksum matching.

- Match status is one of `exact`, `ambiguous`, `unknown`. Only `exact` may unlock model-specific decoding; `ambiguous`/`unknown` stays read-only or offline inspection and may not auto-select a checksum.
- Every definition carries `source_url`, pinned revision, license, content SHA-256, expected binary length, address space, address origin/base offset, byte order, element size, dimensions and scaling expression. Parse expressions with a small allowlisted AST; never `eval()` arbitrary XDF/XML text.
- Keep `file_offset` separate from `ecu_address` and specify any bank/segment/base translation explicitly. Do not transfer offsets between ECU models or firmware revisions without evidence.
- A checksum profile must identify its exact ECU/software applicability, covered range(s), algorithm/provider/version, seed/finalization, stored address/width/byte order, and known-good before/after test vectors. `auto_checksum` is allowed only when one exact profile matches and all vectors pass; missing plugin/algorithm/vector means `unsupported`, not “checksum OK”.
- Store provenance and validation separately: `source_found`, `license_checked`, `profile_id_verified`, `offline_format_verified`, `checksum_tested`, `vehicle_tested`. A profile may be redistributed but still remain unverified for operation.

## Safety/capability defaults

Capabilities are explicit and granular: `identify`, `read_live_data`, `read_dtc`, `read_calibration`, `edit_offline`, `verify_checksum`, `write_calibration`, and `erase_or_security_operations`. Default to read-only. Offline map definitions do not grant write capability. In this project, immobilizer/anti-theft profiles are limited to authorized identification/read-only diagnostics; exclude keys, secrets, seed-key material, bypasses and disable maps. Unsupported or safety-critical operations must return a clear unsupported status, not silently fall through to raw sends.

## Support labels

Use `reference_only`, `experimental`, `offline_format_verified`, `read_only_verified`, and `write_verified` as distinct states. A generic protocol label (for example KWP2000) is not proof of a tested ECU profile. A successful XML parse is only `offline_format_verified`; it is not evidence of correct map labels, checksum behavior, vehicle compatibility or safe calibration.

# BLE discovery sidecar protocol (draft v1)

The sidecar is a local process that reads one JSON-RPC 2.0 object per stdin line and writes one response per stdout line. No network listener is opened. It is discovery-only and does not expose GATT reads/writes or vehicle diagnostics. The companion draft JSON Schema is `BLE_SIDECAR_SCHEMA.json`.

## Methods

| Method | Params | Result |
|---|---|---|
| `ble.adapters.list` | `{}` | `adapters`: array of `{index, info, state}` plus connect/GATT capability flags, all false |
| `ble.scan` | optional `seconds` integer, default 5, range 1–30 | scanned adapter summaries and discovered advertisement metadata; no connection attempt |

A peripheral's displayed address/identifier can be platform-specific and may be privacy-randomized. Names, RSSI and advertised services are optional and may be absent/stale. The host OS/backend may use active BLE scan requests even though this wrapper does not initiate a GATT connection. Do not infer adapter model or ECU protocol from the advertised name/service UUID.

Example:

```json
{"jsonrpc":"2.0","id":1,"method":"ble.scan","params":{"seconds":5}}
```

The wrapper's GATT connect/read/write methods are intentionally absent. Future GATT support must require exact adapter service/characteristic UUIDs, documented permissions, pairing/security review and device-level tests. Immobilizer or security-sensitive services remain out of scope.

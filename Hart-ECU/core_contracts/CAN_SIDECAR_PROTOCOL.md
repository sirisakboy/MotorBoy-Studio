# CAN sidecar JSON-lines protocol (draft v1)

This local process interface is a transport adapter, not a vehicle diagnostic service. It uses one UTF-8 JSON-RPC 2.0 request per line on stdin and one response per line on stdout. It has no network listener or ECU protocol implementation. The companion JSON Schema is `CAN_SIDECAR_SCHEMA.json`.

## Methods

| Method | Params | Result | Notes |
|---|---|---|---|
| `system.info` | `{}` | service/version/transmit/listener status | `network_listener` is always false. |
| `can.interfaces.list` | `{}` | array of `python-can` interface names | Availability still depends on OS/driver/hardware. |
| `can.open` | `interface` required; optional `channel`, `bitrate`, `fd`, `data_bitrate`, `receive_own_messages` | opened/interface/channel/fd/TX state | Opening hardware may initialize it, but does not send a CAN frame. |
| `can.receive` | optional `timeout` in seconds, 0–5 | frame object or `null` | Data is hex; timestamps are backend-provided. |
| `can.send` | `arbitration_id`, optional `data`, `is_extended_id`, `is_fd`, `timeout` | sent/id/hex/fd | Rejected unless process starts with `--allow-tx`; this only enables raw CAN frame transmission. |
| `can.close` | `{}` | `{ "closed": true }` | Shuts down the currently open bus. |

Example read-only session:

```json
{"jsonrpc":"2.0","id":1,"method":"can.interfaces.list","params":{}}
{"jsonrpc":"2.0","id":2,"method":"can.open","params":{"interface":"virtual","channel":"bench-1"}}
{"jsonrpc":"2.0","id":3,"method":"can.receive","params":{"timeout":0.2}}
{"jsonrpc":"2.0","id":4,"method":"can.close","params":{}}
```

Example send is intentionally denied unless transmit was explicitly enabled at process launch:

```json
{"jsonrpc":"2.0","id":5,"method":"can.send","params":{"arbitration_id":"0x123","data":"0102"}}
```

## Safety and compatibility

- Only the CAN frame layer is represented. ISO-TP segmentation, UDS/KWP services, OBD PIDs, OEM identifiers, addressing, flow control and model-specific ECU profiles are outside this protocol.
- CAN TX is off by default and is not equivalent to “safe”: enabling it permits arbitrary raw frames within CAN identifier/length bounds. Only enable on an authorized bench/vehicle after reviewing the exact protocol and hardware.
- Sidecar never binds a socket. For app clients, spawn it with a local process API; if a future deployment proxies it, add authentication, per-client capability controls, auditing and timeouts.
- Do not treat a successful bus open or valid frame as proof of support for any motorcycle module.

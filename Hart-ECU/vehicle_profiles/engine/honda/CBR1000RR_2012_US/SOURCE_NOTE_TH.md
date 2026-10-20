# Honda CBR1000RR 2012 US — filtered profile note

- Upstream: https://github.com/roccofz1/HondaECU
- Snapshot commit: `dbb8d37bfb5dfd6d5d2b001ec44d8774063b9109`
- Upstream file: `definitions/xdf/CBR1000RR_2012_US.xdf`
- License: GPL-3.0; see adjacent `LICENSE`. The local file is a filtered derivative under the same GPL license.
- Included: XDF definition only. No `.bin`, flashing executable, or HondaECU application source.

## Scope filter applied on 2026-10-15

The upstream XDF contained five `XDFPATCH` blocks and one `XDFFLAG` that exposed disable/bypass controls. All six blocks were removed from the packaged copy to keep immobilizer and disable data out of scope:

- `Disable Exhaust Valve Fault Codes`
- `Disable Stock 02 Sensor Fault Codes`
- `Disable Knock Sensor Fault Codes`
- `Disable HESD Fault Codes`
- `Decel Fuel Cut Disable`
- `Disable Immobilizer`

No other XDF tables or checksum metadata were intentionally changed. The XDF itself contains a comment marking this modification; the exact filter and hashes are recorded below.

## Provenance and validation

- Upstream file: 63,564 bytes; SHA-256 `c942ffc16e498985dba5592388e7cf6f2d23e2adde94fde825b52d1287141415`.
- Packaged filtered file: 59,216 bytes; SHA-256 `a00f3ee1bee5a6fcd34b18d352238ff85fec602142bd51d796f517f1cb5acb0d`.
- XML parse passed; XDF declares a `0x40000`-byte binary region and 39 tables. The filtered copy has zero `XDFPATCH`, zero `XDFFLAG`, one `XDFCHECKSUM`, and 105 address-bearing `EMBEDDEDDATA` elements; all address starts are within the declared region.
- Checksum note: XDF has `XDFCHECKSUM` title `Honda Checksum`, stores one byte at `0x3FFF8`, and refers to an external plugin (`pluginmoduleid` `49524f4e-504f-4e59-524b-000000000000`) with `calculationmethod` `0x0`. The algorithm/plugin implementation and known-good test vectors are not included or independently verified; this is **not an approved auto-checksum profile**.
- Coverage: exact XDF title says CBR1000RR 2012 US. It does not prove compatibility with other regions/ECU software, and it does not provide ABS/immobilizer maps.
- Status: `filtered_candidate / definition-only / XML-validated / not vehicle-tested / checksum-unverified`.

# Motorcycle ECU profile definitions — candidate set

**Scope selected:** all ECU modules across motorcycle makes, added model-by-model as evidence permits; definitions/profile data only, no stock BIN/firmware ROM. This is not universal coverage and not a ready-to-flash tool.

## Included now

| ID / reference | Module | Data | License | Validation status |
|---|---|---|---|---|
| `honda.cbr1000rr.2012.us` | Engine ECU | CBR1000RR 2012 US filtered XDF | GPL-3.0 | Filtered derivative; removed five XDFPATCH disable blocks and the `Disable Immobilizer` flag. XML parses; 39 tables; external checksum plugin not verified. Not vehicle-tested. |
| `honda.crf110f.2019.kyk-d12.candidate` | Engine ECU | CRF110F 2019 / `38770-KYK-D12` XDF | GPL-3.0 | XML parses; 11 tables; no flags/checksum. Candidate only: XDF region is `0x65536` while upstream README says 64 kb; start offset/address origin unresolved. Do not auto-match/use until resolved. |
| Honda CRF250L K-Line sample | Engine ECU diagnostics | Example table/response bytes and notes | MIT | Several fields unknown; exact year/ECU/software not pinned; offline reference only, not an XDF/map. |
| Kawasaki/Suzuki KDS/SDS sample | Engine ECU diagnostics | Filtered Z750/Z1000 PID/DTC workbook | GPL-3.0 | Four sheets retained; values not vehicle-verified; offline reference only. Reset/clear/configuration sheets and original workbook excluded. |

The exact upstream URLs, pinned revisions, file hashes, rights and limitations are recorded beside each included item in `SOURCE_NOTE_TH.md`, accompanying LICENSE files, and `SOURCES_AND_REVISIONS.md`. Excluded MotoXDF and Honda/Suzuki candidates are reviewed in `XDF_CANDIDATE_AUDIT_TH.md`. Diagnostic samples do not increase the number of verified engine map profiles.

## Module coverage status

`PROFILE_PICKER_TH.csv` is the quick chooser; entries marked `no_excluded` are audit-only and have no profile file in the pack. `PROFILE_COVERAGE.csv` is the fuller module/coverage index. There are currently **two engine ECU map-definition candidates** and two **unverified diagnostic references**. No verified, license-clear motorcycle definitions have been added for:

- ABS
- separate traction-control ECU (some engine ECU definitions contain ride-mode/throttle maps; that does not imply an independent TCS profile)
- transmission/TCU
- instrument cluster
- BMS or motor controller
- immobilizer

`no_verified_definition` means “not selected and verified in this pass,” not that such data cannot exist. Search results include community material, paid definitions, source collections with per-file or unclear licensing, and model-specific projects; each file needs its own provenance and compatibility review.

## Safety and data handling

1. XDF/map files describe bytes and conversions; they do not prove the map's semantic label or correctness. The engine profiles are quarantined as **candidates** and should be read-only until validated against matching hardware/software identifiers and known-good samples.
2. Never apply offsets from one ECU family/region/software version to another. `CRF110F_2019_KYK-D12_candidate` has an XDF region/start-offset discrepancy; do not correct it by guesswork. The Hayabusa XDF candidate was excluded because it contains password metadata and disable patches; no password fields were stripped or bypassed.
3. No stock BIN is included. No auto-checksum profile is approved: Honda CBR1000RR's XDF points to an external TunerPro plugin; the CRF110F XDF also has no checksum block and its README's address alone is insufficient. A later checksum profile needs an exact ECU/software fingerprint plus known-good validation vectors.
4. No flashing/write operations are enabled by these definitions. Changing engine maps may affect emissions, engine reliability and rider safety; any future editable workflow needs backup, verified checksum, legal-use checks and qualified bench/vehicle testing.
5. The two diagnostic samples are offline references; their request/response semantics and ECU fit have not been independently verified. Do not transmit recorded bytes solely because they appear in a table.
6. Immobilizer/anti-theft data is out of scope beyond authorized module identification and read-only diagnostic status. Do not add secrets, key material, seed-key algorithms, bypass data or disable maps.

## How to add a profile

Add one directory per exact ECU/profile ID. Keep its upstream LICENSE and attribution beside the data file. Record make/model/year, region, ECU part number, HW/SW/calibration IDs, file format, expected binary length, address origin/base offset, byte order, map/table count, checksum data (if any), source commit, validation state and test vectors in `PROFILE_COVERAGE.csv` or a future schema. If a value is unknown, leave it `unknown`; do not infer it from another model.

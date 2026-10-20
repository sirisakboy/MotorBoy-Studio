# XDF candidate audit — rights, provenance, and fit

**Review date:** 2026-10-15  
**Purpose:** decide whether additional motorcycle XDF definitions can enter the curated pack without treating an XDF as proof of support. Only definitions and license/provenance notes are considered; stock BIN/ROM files are excluded.

## Decision summary

- **Added as an offline candidate:** Honda CRF110F 2019 / Keihin `38770-KYK-D12`, from a GPL-3.0 HondaECU repository. It is quarantined as `candidate_metadata_mismatch` because the XDF region size conflicts with the repository README's 64 KiB claim, and the README start offset has not been reconciled. It is not a verified profile.
- **Scope correction to an existing profile:** the packaged Honda CBR1000RR 2012 US XDF is now a GPL-3.0 filtered derivative. A re-audit found five disable-related `XDFPATCH` blocks and one `Disable Immobilizer` flag in the upstream file; all six were removed. The filtered copy has no `XDFPATCH`/`XDFFLAG` blocks.
- **Not added:** Ducati Monster 620 5AMHW610 XDF from MotoXDF Wiki. The wiki's CC BY-SA page license is relevant, but the XDF's upstream lineage has a credible GuzziDiag/Pauldaytona non-commercial restriction risk. The page-level license alone does not clear that upstream chain for this pack.
- **Not added:** other Honda XDFs reviewed below, due to an immobilizer flag, model/ECU identity ambiguity, testing/unknown tables, or unexplained disable/bypass flags.
- **Withheld entirely:** the Suzuki Hayabusa Gen 3 candidate XDF. Although the repository claims MIT, the XDF carries `modifypassword` / `openpassword` fields and ten `XDFPATCH` blocks, including disable controls. We did not strip those fields or publish a modified copy; the XDF and its profile folder are absent from the pack.
- **No stock BIN/ROM was copied.** The Honda repository contains stock BIN paths, but none of those files are in this pack.

## 1. MotoXDF Wiki: what the page license does—and does not—clear

Fandom's licensing terms license text contributions on a CC BY-SA 3.0 basis and require attribution/share-alike. Fandom also warns that material imported from external sources may carry additional requirements; the page license is not a blanket replacement for upstream rights. See [Fandom's licensing policy](https://www.fandom.com/licensing). The XDF examined below is embedded in a `syntaxhighlight` text block, rather than being an attached binary, so the page-text license is relevant—but it cannot grant rights that the contributor did not hold.

### Ducati M620 5AMHW610 stock XDF

Source page: [`(MM 5AMHW610) Ducati M620 Stock`, revision 4298](https://motoxdf.fandom.com/wiki/(MM_5AMHW610)_Ducati_M620_Stock?oldid=4298). The page identifies 2004–2006 Monster 620 and ECU references `28640711B` / `1210A11DG`. The page was created by `Warwickh` in 2015; the XDF author field reads `Warwick Harris Impulsive_Duc Pauldaytona Beard`. The latest page revision is from 2023. The XDF syntaxhighlight payload at revision 4298 is 39,876 bytes (SHA-256 `ed5702426e0552d3a1c12484a3033aa98a19636d6305257624d836dc82d94169`); that research copy is not included in this pack.

Static XML review found 24 tables, zero flags, zero constants, no XDF checksum block, and a declared region of `0x50000`; table data starts are within that region. The content itself does not expose an immobilizer flag. Those facts make it a technically plausible offline candidate, but not a validated ECU profile.

The rights chain remains unresolved:

- The MotoXDF page [`(MM 5AMHW610) Moto Guzzi One Lambda`](https://motoxdf.fandom.com/wiki/(MM_5AMHW610)_Moto_Guzzi_One_Lambda) explicitly labels `5AM_GuzziDiag_One_Lambda_V1.28.xdf` as the GuzziDiag reference. Its embedded XDF is version 1.28 and names Beard/Pauldaytona as authors.
- The Ducati S2R 5AMHW610 page also contains a version-1.28, one-lambda XDF by Pauldaytona/Beard, and the M620 5AMHW610 file shares table identifiers/structure with this family. The M620 description also retains a speedometer note referring to Moto Guzzi models. This is evidence of lineage risk, not proof of the exact copy path.
- A public Ducati Monster Forum post by `Impulsive_Duc` says adaptations of GuzziDiag and Pauldaytona XDFs were made with attribution, **not for sale**, described as CC BY-NC, with ShareAlike added to the derivatives. The M620 XDF author field includes `Impulsive_Duc` and `Pauldaytona`. See the [forum post](https://ducatimonsterforum.org/index.php?topic=67714.10%3Bwap2).
- The separate `5AMHW103 Ducati M620 Stock` page explicitly says it was adapted from `5AM_Ducati_S2_800R_V1.28.xdf`; its XDF also contains `Possible Red+Black key data (?)` and an `Immobilizer (likely!)` flag. That profile is out of scope independently of licensing.

**Disposition:** the generic CC BY-SA notice is sufficient for original page-contributed text when the contributors had the rights to license it. It is not enough to remove an upstream BY-NC restriction or clear an unverified derivative chain. No Ducati XDF is redistributed in this pass. Reconsider only if the upstream owners provide a compatible redistribution/commercial grant, or the exact file's independent authorship and license chain are established. The 59MHW010 M620 page is also held back pending source/provenance confirmation.

## 2. Honda GPL-3.0 repository review

Reviewed the model-specific XDF paths in [`aeaphichart/HondaECU-1`](https://github.com/aeaphichart/HondaECU-1), pinned at commit `b59ae98baf092def23d7c34d5ef5f43bd6aba952`. The project is a fork in the `Adeen117` / `roccofz1/HondaECU` lineage; its root `LICENSE` is GPL-3.0. XDF file history and README metadata were checked separately. The repository also contains stock BINs; only the one selected XDF and the project license were copied.

A separate re-audit of the already-included `definitions/xdf/CBR1000RR_2012_US.xdf` found one immobilizer flag and five disable patches. These were removed from the local GPL-3.0 derivative and are not redistributed; exact names/hashes are in that profile's `SOURCE_NOTE_TH.md`.

| XDF path in source tree | Static review / identity evidence | Disposition |
|---|---|---|
| `xdfs/CBR1000RR_MEL_2006-2007/38770-MEL.xdf` | 66 tables; contains an `Immobilizer` flag. | Excluded: security/immobilizer control. |
| `xdfs/CBR500R_MGZ_2013-2016/38770-MGZ.xdf` | 17 tables; contains a `Fuel Cut` flag. Path calls it CBR500R 2013–2016, while README says `CB500R` 2014 / `38770-MGZ-B01`; exact model/part-number match is not independently reconciled. | Not selected: unresolved model/ECU identity. |
| `xdfs/CBR500R_MGZ_2013-2016/testing/38770-MGZ.xdf` | 84 tables; explicitly stored under `testing/`, with many unknown/table-code names. | Excluded: test definition and semantics not sufficiently established. |
| `xdfs/CBR500R_MJW_2017-2018/38770-MJW.xdf` | 35 tables and 56 opaque bit flags named `B0-*` through `B6-*`; no clear semantics in the XDF. | Excluded pending per-flag provenance and safety review. |
| `xdfs/CRF110F_KYK_2019/38770-KYK-D12.xdf` | 11 tables; no flags, immobilizer labels, or XDF checksum block. README states CRF110F 2019, `38770-KYK-D12`, 64 kb, start offset `8000`, M16C. The XML says `REGION size="0x65536"`, not the expected `0x10000` for 64 KiB; `BASEOFFSET` is zero and the offset interpretation is unresolved. | **Included as a quarantined research candidate** with the upstream file unchanged. Do not auto-match or use until metadata is resolved. Details: `vehicle_profiles/engine/honda/CRF110F_2019_KYK-D12_candidate/SOURCE_NOTE_TH.md`. |
| `xdfs/CRF450R_MKE_2017-2019/38770-MKE-DataSettings.xdf` | 14 tables with `DataSettings`/unit/header fields; README does not establish an exact matching ECU part number for this file. | Excluded: not a sufficiently identified map profile. |
| `xdfs/MSX125_K26_*/*.xdf`, `xdfs/Z125M_K0F_2019/*.xdf` | Flags include `LTFT Disabled`, `LTFT, Bypass`, feedback, tip-over, and related controls. | Not selected in this conservative pass; flag semantics and scope need separate review. |

### CRF110F candidate validation details

- Selected file SHA-256: `0849ebc1173d206dc55ca1ed6ec614e7eb8477cdb9c6b899aa4316c059ac384d` (18,666 bytes); file-level history shows Ryan Hope's `xdf fixes` commit `b592b5709f27310abed6634bbb4a5c1ac289b8ec` from 2019-05-15.
- XML 1.60 parses. There are 11 table definitions, no flags/constants/checksum blocks, and the computed data ranges lie below `0x1E97`, inside 64 KiB. This validates XML structure and rough bounds only—not table semantics or fit.
- The upstream README's `64 kb`, `Start Offset 8000`, and checksum-address `0` have not been reconciled with the XDF's `0x65536` region / zero base offset. The local XDF is unmodified rather than silently “fixed.”
- No matching BIN, ECU read, calibration/software ID, checksum vector, bench test, or vehicle test was used. The file remains read-only research material; it does not establish support for every 2019 CRF110F or any other Honda model.

## 3. Suzuki Hayabusa Gen 3 XDF — withheld, not redistributed

- Source: [`DanCycles/HayabusaGen3`](https://github.com/DanCycles/HayabusaGen3), commit `58de6d211b6f42b254a1f37de13f4802487b2ba5`; upstream file `Suzuki-GSXR1300-32910-10LX0.xdf`, SHA-256 `fd7f86dda17a04dde4262821cff7dfd97c9b2c3fa0d6b7514c6cc866c146113a`, 203,795 bytes. The repository states MIT, but the file's own password metadata requires separate scope/rights caution.
- Static review: XML version 1.70, 122 tables, no `XDFCHECKSUM`, and ten `XDFPATCH` blocks: four fan-temperature alternatives and six disable controls (stock O2 sensor, wheel-speed sensor, EVAP purge, PAIR valve, ISC valve, fan FI error). The XDF also contains `modifypassword` and `openpassword` elements.
- The source repository's `ECU.md` lists part IDs `32990-10L0`–`32990-10LB`, which remain unreconciled with the XDF filename ID `32910-10LX0`.

**Disposition:** the entire XDF/profile directory was removed rather than distributing password material or deleting password fields in a way that could bypass the author's protection. No password values are reproduced in this audit note. The root MIT license alone does not make it appropriate to publish credential/protection fields or disable patches in this scope. No Suzuki BIN was added.

## Next evidence required

1. For Ducati 5AM definitions: written permission or an explicit upstream license that covers redistribution and the intended commercial-use scope, plus complete author attribution. A Fandom CC BY-SA page footer alone does not satisfy this if the file incorporates BY-NC source material.
2. For CRF110F: reconcile the XDF region and the README start-offset semantics against authoritative format documentation or a matching, lawfully obtained binary reference; establish the software/calibration identifier; then test all tables and checksum behavior on a controlled bench. Do not add a checksum algorithm based on the README's address alone.
3. For each further profile: record exact model/ECU/HW/SW identifiers, per-file rights/provenance, definition hash, region/address origin, checksum evidence, and validation status. Keep stock BIN/ROM outside the pack.

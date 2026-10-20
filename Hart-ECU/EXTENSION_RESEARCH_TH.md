# ส่วนต่อยอด Phase 2 — CAN / Bluetooth / Wi‑Fi / TTL / Serial / maps

**วันที่สำรวจ:** 14 ตุลาคม 2026  
**จุดประสงค์:** คัดส่วนที่เป็น transport/library หรือ profile format เท่านั้น; ไม่คัดทุก repository/ทุก firmware dump เข้าชุด core.

## ข้อสรุปสำคัญ

การเชื่อมต่อเหล่านี้อยู่คนละชั้นกัน:

- **TTL/UART/Serial** = การส่ง byte ระหว่าง host กับ adapter/MCU; FTDI/CH340 มักทำให้เห็นเป็น COM/TTY. `libserialport` ในชุดหลักจัดการพอร์ตนี้ได้.
- **K-Line และ CAN** = physical/data-link bus ที่ต้องใช้อินเทอร์เฟซไฟฟ้าเหมาะสม. USB-UART TTL อย่างเดียวไม่ใช่ K-Line transceiver และไม่ใช่ CAN transceiver.
- **Bluetooth/Wi‑Fi** = ลิงก์จากแอปไปยัง adapter (เช่น BLE GATT, Bluetooth SPP, TCP/UDP/MQTT); ไม่ได้บอกว่า ECU ใช้ KWP, UDS หรือ CAN service แบบใด.
- **XDF/offset/map/checksum** = definition/profile ของ firmware ECU รุ่นเฉพาะ; ไม่ใช่คุณสมบัติของสาย CAN/Bluetooth.

## แหล่งที่มีประโยชน์ — คัดเป็น backend/reference ไม่ใช่ universal driver

| ประเภท | แหล่ง/ส่วนที่ควรยึดเป็นต้นแบบ | นำไปใช้ได้แค่ไหน |
|---|---|---|
| CAN | [python-can 4.6.1](https://pypi.org/project/python-can/4.6.1/); runtime package source + license/build metadata and exact sdist are now included in `dependencies/python-can-4.6.1/` and `dependencies/source_archives/`. Companion local JSON-lines sidecar is in `adapters/can_jsonl_sidecar/`. | Python host CAN abstraction with many vendor/socket/serial interfaces. Sidecar is tested only against the `virtual` interface; no physical adapter is tested. No ISO-TP/UDS/KWP/OEM services or motorcycle IDs are supplied. LGPL-3.0-only; runtime/transitive packages and vendor drivers are not bundled. |
| CAN — C# option | [CanKit](https://github.com/pkuyo/CanKit) | เป็น alternative สำหรับแอป C# ที่รวม PCAN/Kvaser/SocketCAN/ZLG และ virtual adapters. ยังเป็น backend ตาม vendor driver และไม่ใช่ language-neutral core. ไม่ควรดึงทั้งก้อนถ้ายังไม่เลือก stack. |
| Bluetooth BLE | [btleplug 0.13.5](https://crates.io/crates/btleplug) | Source crate + upstream examples are included; local `adapters/btleplug_scan/` implements list/advertisement-scan only. Metadata license `MIT/Apache-2.0/BSD-3-Clause`. BLE GATT only, not Bluetooth Classic/SPP or ECU protocol. Wrapper/source were not compiled because Rust/Cargo are absent; no peripheral was tested. |
| Bluetooth BLE หลายภาษา | [SimpleBLE](https://github.com/simpleble/simpleble) | README ระบุ binding หลายภาษาและหลายแพลตฟอร์ม แต่ license ปัจจุบันเป็น BUSL-1.1 และ commercial use อาจต้องมี license; จึงยังไม่เลือกเป็น dependency กลาง. |
| BLE UART bridge | [ble-serial 3.0.0](https://pypi.org/project/ble-serial/3.0.0/) | Selected MIT source subset and exact PyPI sdist are included. It bridges compatible BLE-UART GATT to a POSIX PTY/TCP, not arbitrary BLE or BT Classic. Upstream Windows virtual-COM setup may require disabling Secure Boot; we do not recommend that. Upstream CLI defaults to read/write. No BLE adapter/ECU was tested. |
| Wi‑Fi/BLE-to-CAN adapter | [WiCAN firmware](https://github.com/meatpiHQ/wican-fw) | ตัวอย่าง firmware ESP32 ที่ทำ CAN bridge และมี Wi‑Fi/BLE/network interface; เป็น hardware firmware เฉพาะอุปกรณ์, GPL-3.0, และแนว OBD-II ไม่ใช่ support map/protocol สำหรับรถมอเตอร์ไซค์ทุกค่าย. ควรอ่าน API/docs แทนการยก firmware ทั้ง repo เข้า desktop core. |
| Wi‑Fi/TCP/UDP | Added local `transports/ip_socket/raw_socket_transport.py`: client-side TCP byte stream and connected UDP datagram, no protocol guess and no default TX. | Adapter endpoint, port, framing, authentication and reconnect behavior must be documented for the exact model/firmware. Localhost-only tests passed. Does not claim WiCAN/ELM327/SLCAN/GVRET/MQTT compatibility; WiCAN firmware was not copied because no usable endpoint protocol was established. |
| TTL/USB-UART | `libserialport` ที่ดาวน์โหลดไว้แล้ว | ใช้กับ serial devices ที่ OS enumerate ได้. สัญญาณ logic-level TTL ห้ามต่อเข้าบัส K-Line/CAN โดยตรง; ต้องมี line transceiver ที่ตรงกับบัสและแรงดัน. |
| K-Line generic OBD2 | [OBD2_KLine_Library](https://github.com/muki01/OBD2_KLine_Library) | โปรเจกต์ Arduino/ESP32 ที่ระบุ ISO9141, ISO14230, KW1281, DS2, KW82; เหมาะอ่านเป็น reference สำหรับ generic OBD diagnostics เท่านั้น. ไม่ได้ยืนยัน Honda/Yamaha/Kawasaki/Suzuki manufacturer services ทุกโมเดล; GPL-3.0 จึงยังไม่คัดเข้า core. |

## Maps, offsets, XDF, BIN และ auto checksum

| แหล่ง | ขอบเขตที่ตรวจพบ | การตัดสิน |
|---|---|---|
| [CBR250RR ECU binary definition](https://github.com/kelvinvalencio/cbr250rr-ecu-binary-definition) | Honda CBR250RR MC51 มี XDF ระบุสำหรับ ECU `38770-K64-N04` และ `38770-K64-ND1`; `N01` และ `R01` ไม่มี XDF ในตาราง repo. README เตือนให้ทดสอบเอง และหลาย map conversion/offset ยังระบุ unknown/uncategorized. ใน repository มี `.bin` stock dumps ด้วย. | เป็น **profile ตัวอย่างเฉพาะ ECU** ไม่ใช่ universal Honda map. ไม่คัด raw BIN เข้า bundle เพราะ license/provenance ไม่ชัดและไม่จำเป็นต่อ parser; XDF ก็ต้องตรวจสิทธิ์ก่อน redistribute. ห้ามนำ address/offset ไปใช้กับ part number อื่น. |
| [sostisoft/ecu-definitions](https://github.com/sostisoft/ecu-definitions) | รายการรวมมี 352 XDF/671 XML แต่ Motos มี 4 entries; Suzuki Denso เป็นหนึ่งในนั้น. | ใช้เป็น index หา profile เฉพาะรุ่นได้ แต่ไม่ใช่ฐานข้อมูลทุกยี่ห้อ. License ของ definition แต่ละไฟล์อาจมาจากคนละ source; ต้องตรวจทีละไฟล์. |
| [ZedSuite](https://github.com/LeZed97/ZedSuite) | app ข้าม Windows/macOS/Linux; เปิด arbitrary BIN และนำเข้า XDF/JSON mappack ได้ แต่ auto-detection/checksum ที่ยืนยันจำกัด Bosch VAG EDC15/EDC16. GPL-3.0. | ใช้ดูแนวทาง profile matching, completeness/confidence, XDF/JSON import และ checksum test design เท่านั้น. ห้ามนำ detector/checksum algorithm ไปใช้กับ ECU มอเตอร์ไซค์โดยไม่มีหลักฐาน. |
| `xdf_merge.py` ในชุดหลัก | Parser/exporter XDF/BIN ที่เก็บไว้ reference-only; README เน้น Porsche 944 และไม่มี LICENSE file ใน snapshot แม้ README แสดง MIT badge. | ยังไม่อนุมัติให้รวม source จนยืนยัน license และทดสอบ XDF หลายแบบ. |
| `MX-KING-CHECKSUM-CORRECTOR` | Utility เฉพาะ Yamaha MX King V1 (2PV0), มีไฟล์เดี่ยว `Form1.vb`. | ไม่ใช่ checksum engine กลาง; ใช้เป็น reference เฉพาะ part/software fingerprint ที่ match และต้องแก้ safety issue เรื่องเขียนไฟล์เดิมก่อนใช้. |

### กฎที่ต้องบังคับในระบบ map/checksum

1. **ไม่เดา offset/checksum จากยี่ห้ออย่างเดียว.** เลือก profile จาก ECU part number + HW/SW ID + region/version + BIN size/signature; หากไม่ match ให้หยุดและรายงาน `unknown_profile`.
2. แยก **file offset** ออกจาก **ECU address**; profile ระบุ address origin, bank/base offset, byte order, element width, axis/scale formula และ checksum range.
3. เก็บ checksum เป็น `algorithm primitive + ECU-specific profile + known-good before/after test vectors`; auto checksum หมายถึง “เลือก profile ที่ match ได้อย่างชัดเจน” ไม่ใช่ลอง CRC หลายแบบแล้วเขียนไฟล์.
4. แยก **XDF/map definition** ออกจาก **BIN firmware content**. ไม่ bundle stock BIN/ROM จากอินเทอร์เน็ตโดยอัตโนมัติ; ต้องมีเจ้าของ/สิทธิ์และ source ที่ตรวจได้.
5. แสดงระดับข้อมูลแยกกัน: `source_found`, `license_checked`, `profile_id_verified`, `checksum_tested`, `vehicle_tested`. การมีไฟล์ XDF ไม่ได้แปลว่าค่า map/offset ถูกต้องหรือปลอดภัย.

## ขอบเขตหลังยืนยันกับผู้ใช้

- ผู้ใช้เลือกให้ครอบคลุม **ทุกโมดูล ECU** (engine, ABS, traction control, immobilizer, cluster, transmission/TCU, BMS/controller ฯลฯ) โดยทยอยเพิ่มตามหลักฐานที่ตรวจได้.
- ผู้ใช้เลือก **definitions only**: XDF/JSON/profile metadata และ checksum metadata ที่มี license/provenance; **ไม่รวม stock BIN/firmware ROM**.
- Immobilizer/anti-theft ครอบคลุมได้เฉพาะการระบุโมดูล/อ่านสถานะวินิจฉัยที่ได้รับอนุญาต; ไม่เก็บกุญแจ/secret/seed-key/bypass หรือ map ปิดระบบป้องกัน.

## Profile files added in this pass

| Profile | Files included | License | ผลตรวจ/ข้อจำกัด |
|---|---|---|---|
| Honda CBR1000RR 2012 US | Filtered XDF + GPL-3.0 LICENSE + source note | GPL-3.0 | XML parse ผ่าน; 39 tables; กรองออก 5 `XDFPATCH` disable blocks และ `Disable Immobilizer` flag. Checksum plugin/store address `0x3FFF8` ยังไม่มี implementation/vectors ที่ยืนยัน จึงไม่มี auto-checksum. ไม่รวม BIN. |
| Honda CRF110F 2019 / `38770-KYK-D12` | XDF + GPL-3.0 LICENSE + source note | GPL-3.0 | XML parse ผ่าน; 11 tables; ไม่มี flags/checksum. Candidate only: XDF region `0x65536` ไม่ตรง README ที่ระบุ 64 kb และ start offset `8000` ยังไม่ reconcile; เก็บ XDF ต้นฉบับโดยไม่แก้ metadata. ไม่รวม BIN. |
| Honda CRF250L diagnostics | table/response text + upstream README + MIT license | MIT | มี fields unknown; exact year/software/ECU ID ไม่ pinned; reference only, not an XDF/map. |
| KDS/SDS Z750/Z1000 diagnostics | filtered XLSX (4 sheets) + GPL-3.0 LICENSE + source note | GPL-3.0 | Formula outputs flattened to cached values, not recalculated. Unverified; excluded reset/clear/configuration sheets; original workbook not included. |

ไฟล์ทั้งหมดและสถานะ module-by-module อยู่ใน `vehicle_profiles/README_TH.md`, `vehicle_profiles/diagnostics/README_TH.md` และ `vehicle_profiles/PROFILE_COVERAGE.csv`. สิทธิ์/provenance และ XDF ที่ไม่ผ่านคัดเลือกตรวจไว้ใน `XDF_CANDIDATE_AUDIT_TH.md`.

## แหล่งอื่นที่ตรวจแล้วแต่ยังไม่คัดเข้า

- `sostisoft/ecu-definitions` แสดง motorcycle folder 4 definitions (Buell, Ducati, Moto Guzzi, Suzuki Denso) แต่ repo **ไม่มี LICENSE ที่ root** และระบุว่าแต่ละไฟล์อาจใช้ license เดิมต่างกัน; จึงยังไม่คัดไฟล์รายตัวจนตรวจ provenance/license ของแต่ละต้นทาง.
- `KDS2Bluetooth` เป็น K-Line/KWP example สำหรับ Kawasaki KDS และ Suzuki SDS, ใช้ Bluetooth Classic serial/Arduino และ GPL-3.0; เพิ่มเฉพาะ workbook derivative 4 sheets (`KDS PID`, supported PID Z1000/Z750, `Service Codes`) ใน `vehicle_profiles/diagnostics/kawasaki_kds_suzuki_sds/`. ไม่รวม source workbook, AT/BT commands, reset/clear functions, standards PDFs หรือ repository code. ค่าใน workbook ยังไม่ verified.
- `Honda-Motorcycle-ECU-Tools` เป็น MIT reference สำหรับ Honda CRF250L K-Line diagnostics; เพิ่มเฉพาะ table/response sample + README/license ใน `vehicle_profiles/diagnostics/honda_crf250l/`. ค่าที่ unknown ยังคง unknown; ไม่ใช่ ECU map/XDF หรือ module set ครบ.
- `aeaphichart/HondaECU-1` / `roccofz1/HondaECU` มีหลาย XDF และ stock BINs. คัดเพิ่มเฉพาะ `CRF110F 2019 / 38770-KYK-D12` เป็น GPL-3.0 research candidate; ไม่คัด BIN. ไฟล์ XDF มี `REGION size="0x65536"` แม้ README ระบุ 64 kb จึงคงต้นฉบับและ mark เป็น metadata mismatch. XDF อื่นที่มี immobilizer/opaque flags/testing labels หรือ identity mismatch ไม่เพิ่ม; ดู file-by-file ใน `XDF_CANDIDATE_AUDIT_TH.md`.
- `DanCycles/HayabusaGen3` XDF was removed from the pack: it contains `modifypassword`/`openpassword` fields and ten `XDFPATCH` blocks, including disable controls. Password fields were neither copied nor stripped to bypass protection; the XDF, LICENSE, and profile directory are not distributed. Details in `XDF_CANDIDATE_AUDIT_TH.md`.
- `SuSoDevs` แสดงการอ่าน RS485/CAN ของ S.S. CPX ภายในรถ รวม ECU/จอ/BMS แต่ไม่มี license ที่ยืนยันใน root snapshot จึงไม่คัด source.
- ดัชนี DTC แบบ generic OBD-II ไม่เท่ากับ DTC/profile สำหรับ ABS/TCU/cluster ของมอเตอร์ไซค์; manufacturer data ต้องตรวจสิทธิ์และรุ่นแยก.

## สถานะการดาวน์โหลดและ additions ใน Phase 2

- มี XDF เฉพาะรุ่น 2 รายการใน `vehicle_profiles/engine/` พร้อม license/provenance แยกตาม profile; CBR1000RR เป็น filtered derivative ที่ไม่มี disable/immobilizer blocks และ CRF110F ถูก quarantine เพราะ region/start-offset mismatch; **ไม่มี stock BIN/ROM**.
- เพิ่ม `python-can` 4.6.1 source + local JSON-lines sidecar; virtual-bus test ผ่าน. เพิ่ม `btleplug` 0.13.5 source crate + local scan/list-only Rust wrapper (ยังไม่ build/test เพราะไม่มี Rust/Cargo) และ `ble-serial` 3.0.0 selected source (no BLE device test; Windows Secure Boot caveat documented).
- เพิ่ม generic TCP/UDP socket transport และ localhost tests; ไม่มี WiCAN firmware, WiCAN port/framing guess, `muki01` source หรือ ECU OEM service implementation.
- เพิ่ม Honda CRF250L K-Line diagnostic sample และ KDS/SDS filtered Z750/Z1000 workbook เป็น **offline references only**; ข้อมูลและ request semantics ยังไม่ vehicle-verified.
- ABS, TCU, cluster, BMS/controller และ separate traction-control ยังไม่มี model-specific, license-clear definitions. Coverage ใช้ `no_verified_definition`, ไม่ได้แปลว่าไม่มีข้อมูลอยู่ที่อื่น.
- `libserialport`, J2534 adapters แยกแพลตฟอร์ม และ API/plugin draft ยังอยู่ในชุดหลัก. ยังคงแยก transport / protocol / ECU profile; ไม่มี universal motorcycle support claim.


## Scope audit correction: Honda CBR1000RR XDF (2026-10-15)

A second static pass found that the original CBR1000RR XDF contained one `Disable Immobilizer` flag plus five `XDFPATCH` blocks for disabling fault codes or decel fuel cut. The local GPL-3.0 derivative now removes those six blocks; 39 calibration tables and the unverified external checksum metadata remain. The upstream hash, filtered hash, exact removed labels, and validation counts are in `vehicle_profiles/engine/honda/CBR1000RR_2012_US/SOURCE_NOTE_TH.md`. No original disable/immobilizer controls are packaged.

## MotoXDF Wiki license/provenance decision (2026-10-15)

Fandom CC BY-SA 3.0 applies to page-contributed text, including an XDF code block, when the contributor had the rights to license it; it does not cancel upstream restrictions. The 5AMHW610 Ducati M620 page is technically parseable (24 tables, no flags/checksum), but its author list includes `Impulsive_Duc` and `Pauldaytona`, and the 5AM one-lambda definitions have a GuzziDiag lineage. A public `Impulsive_Duc` post describes GuzziDiag/Pauldaytona adaptations as non-commercial with ShareAlike. Therefore no Ducati XDF was added; the page footer alone is insufficient to clear the likely upstream BY-NC restriction for a pack intended for possible future clients. The 5AMHW103 M620 XDF also exposes immobilizer/key-data flags and is independently excluded. Detailed evidence and page/revision links are in `XDF_CANDIDATE_AUDIT_TH.md`.

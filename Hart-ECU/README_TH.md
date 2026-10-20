# ECU Tuner — curated source and profile pack

แพ็กนี้เป็น **ชุด source ที่คัดและจัดหมวดเพื่อ review/ต่อยอด** ไม่ใช่โปรแกรมพร้อมใช้กับ ECU จริง ไม่ใช่การรวม repository ทั้งก้อน และไม่ใช่การรับรอง support ทุกยี่ห้อ/ทุกรุ่น

> **เริ่มเลือกใช้งาน:** เปิด `START_HERE_TH.md` ก่อน; ถ้าต้องเลือก ECU profile ให้ใช้ `vehicle_profiles/PROFILE_PICKER_TH.csv`.

## ภายในแพ็ก

- `START_HERE_TH.md` — คู่มือเลือกตามงานและ profile พร้อมทางลัดไปยังไฟล์ที่เกี่ยวข้อง; เป็นจุดเริ่มต้นหลังแตก ZIP.

- `dependencies/libserialport/` — selected C serial-port source/build files; ใช้เป็น UART/COM/TTY backend เท่านั้น ไม่ใช่ K-Line transceiver, CAN, J2534 หรือ ECU protocol.
- `dependencies/python-can-4.6.1/` — runtime package source (LGPL-3.0-only), official PyPI sdist และ per-file index; virtual CAN smoke test ผ่าน. Hardware backends ยังขึ้นกับ OS/driver/optional packages.
- `dependencies/btleplug-0.13.5/` — complete BLE GATT source crate (MIT/Apache-2.0/BSD-3-Clause) + upstream examples; `adapters/btleplug_scan/` adds a read-only scan/list sidecar. ยังไม่ได้ build เพราะไม่มี Rust/Cargo และไม่ใช่ Bluetooth Classic/SPP.
- `dependencies/ble-serial-3.0.0/` — selected MIT BLE-UART bridge source. Windows virtual COM setup อาจต้องปิด Secure Boot ตามคำเตือน upstream; แพ็กนี้ **ไม่แนะนำให้ปิด Secure Boot**. Upstream default permission เป็น read/write; ใช้เป็น reference/POSIX-only จนทดสอบ.
- `adapters/can_jsonl_sidecar/` — local stdin/stdout JSON-lines sidecar สำหรับ CAN frames, transmit ปิดเป็นค่าเริ่มต้น; contract/schema อยู่ใน `core_contracts/`.
- `transports/ip_socket/` — generic TCP byte stream และ UDP datagram สำหรับ IP/Wi-Fi adapters; ไม่มีการเดา port/framing ของ WiCAN, ELM327 หรือ protocol อื่น.
- `adapters/windows_pyj2534/`, `adapters/openport2_j2534/` — J2534 backend references แยก OS/device; ยังไม่ทดสอบอะแดปเตอร์จริง.
- `references/kwp2000/`, `references/xdf_parser/` — reference only; license/build/vehicle limitations บันทึกแยก.
- `core_contracts/PORTABILITY_AND_PLUGIN_CONTRACT.md` — draft API/plugin contract หลายภาษา/หลาย OS รวม exact profile matching, checksum evidence และ read-only defaults.
- `vehicle_profiles/` — `PROFILE_PICKER_TH.csv` เลือก profile ได้เร็ว; มี 2 XDF engine-map candidates เฉพาะรุ่น + 2 unverified diagnostic references (Honda CRF250L K-Line; filtered KDS/SDS Z750/Z1000 workbook). ไม่มี stock BIN/ROM.
- `EXTENSION_RESEARCH_TH.md` — research และเหตุผลเลือก/ไม่เลือก source สำหรับ CAN/Bluetooth/Wi-Fi/TTL/Serial/maps/checksum.
- `XDF_CANDIDATE_AUDIT_TH.md` — rights/provenance และ exact-fit review ของ MotoXDF และ Honda GPL XDF candidates; บันทึกเหตุผลเพิ่ม/ไม่เพิ่มทีละไฟล์.
- `FILE_ANALYSIS_TH.md` — per-file analysis ของ source/profile/documentation ที่คัดเข้าชุด.
- `SOURCES_AND_REVISIONS.md` — upstream versions/commits/artifact hashes และ scope/exclusions.
- `tools/filter_kds_workbook.py` — สคริปต์ทำซ้ำการกรอง workbook เป็น 4 sheets ที่คัดเลือกด้วย `openpyxl`; ใช้ไฟล์ upstream แยกที่ดาวน์โหลดเอง (ไม่รวมในแพ็ก).
- `MANIFEST_SHA256.csv` — SHA-256/size manifest ของชุดที่อัปเดตล่าสุด.

## ข้อจำกัดและการตรวจ

1. แยก **transport**, **vehicle protocol** และ **ECU profile**. การเปิด CAN/serial/BLE/Wi-Fi ไม่ได้บอก protocol ของ ECU และไม่ได้เพิ่ม map coverage.
2. `libserialport` จัดการ serial port; TTL-UART ห้ามต่อเข้าบัส K-Line/CAN โดยตรง ต้องมี electrical transceiver ที่ถูกต้อง.
3. CAN sidecar ส่งได้เฉพาะเมื่อเริ่ม process ด้วย `--allow-tx`; Wi-Fi socket classes ต้องตั้ง `tx_enabled=True` เอง. การเปิด hardware ยังอาจ initialize adapter. ใช้ bench/hardware ที่ได้รับอนุญาต.
4. ทดสอบใน sandbox: `libserialport` Linux timing test 1/1 ผ่าน; new Python 3 sidecar/transport/filter code ผ่าน syntax/tests; CAN virtual + IP localhost tests 6/6 ผ่าน. Blanket Python 3 compileall พบ upstream `libserialport/config-header.py` ใช้ Python 2 syntax (build ที่ทดสอบไม่ได้เรียกไฟล์นี้). ไม่ได้ทดสอบ CAN/BLE/serial/J2534/Wi-Fi กับ adapter หรือ ECU จริง.
5. OpenPort J2534 build ไม่ผ่านใน environment นี้เพราะไม่มี `libusb-1.0` development package; `btleplug` build ไม่ได้เพราะไม่มี `rustc`/`cargo`; KWP Arduino target ยังไม่ build.
6. XDFs ที่รวมอยู่ 2 รายการเป็น offline candidates: CBR1000RR เป็น filtered derivative ที่ตัด disable/immobilizer blocks ออกแล้ว แต่ checksum plugin ไม่พร้อม; CRF110F มี region/start-offset metadata discrepancy. ไม่รวม Suzuki XDF ที่มี password metadata และ disable patches. ไม่มี auto-checksum ที่อนุมัติ.
7. `PROFILE_COVERAGE.csv` แสดง 2 engine map candidates และ 2 unverified diagnostic references; ยังไม่มี verified definitions สำหรับ ABS/TCU/cluster/BMS/separate TCS. Immobilizer จำกัดเฉพาะ authorized read-only identification/diagnostics; ไม่รวม key/secret/seed-key/bypass data.
8. ตรวจ license ก่อนคัดลอก/แก้ไข/แจกจ่าย โดยเฉพาะ GPL/AGPL/LGPL; แต่ละ dependency เก็บแยก พร้อม license/provenance.

## รัน hardware-free tests

จาก directory `ecu_tuner_core_pack/`:

```sh
PYTHONPATH="dependencies/python-can-4.6.1:." python -m pytest -q \
  adapters/can_jsonl_sidecar/test_can_jsonl_sidecar.py \
  transports/ip_socket/test_raw_socket_transport.py
```

ผลล่าสุด: 6 tests ผ่าน โดยใช้ virtual CAN และ localhost socket เท่านั้น.

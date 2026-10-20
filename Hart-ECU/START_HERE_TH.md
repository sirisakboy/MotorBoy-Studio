# เริ่มที่นี่ — วิธีเลือกส่วนที่ต้องใช้

แพ็กนี้รวม **source, contracts, diagnostics references และ ECU definition candidates ที่ผ่านการคัดกรอง** ไว้ใน ZIP เดียว ไม่ใช่โปรแกรมติดตั้งหรือชุดแฟลช ECU: แตก ZIP หนึ่งครั้ง แล้วเปิดไฟล์นี้ก่อนเลือกส่วนอื่น

## เลือกตามงาน

| ต้องการทำอะไร | เปิดไฟล์/โฟลเดอร์นี้ก่อน | ใช้เพื่ออะไร / ข้อจำกัด |
|---|---|---|
| เลือก ECU map definition ตามรุ่น | `vehicle_profiles/PROFILE_PICKER_TH.csv` | ตารางเลือกแบบเร็วพร้อม exact target, สถานะ, path และข้อห้าม จากนั้นอ่าน `SOURCE_NOTE_TH.md` กับ LICENSE ในโฟลเดอร์ของ profile นั้น |
| ดู coverage และช่องว่างของ ECU modules | `vehicle_profiles/PROFILE_COVERAGE.csv` | ดัชนีรวมทั้งรายการ candidate, reference, รายการที่ถูก exclude และ module ที่ยังไม่มี definition ที่ตรวจยืนยัน |
| ดูตัวอย่าง diagnostic data | `vehicle_profiles/diagnostics/README_TH.md` | มีเพียง reference แบบ offline; ไม่ใช่ protocol ที่ยืนยันแล้ว และห้ามส่ง bytes ตามตัวอย่างโดยไม่มีหลักฐาน |
| เลือก transport/adapter | `adapters/README_TH.md` | สรุป CAN, BLE, serial, IP socket และ J2534 พร้อมสถานะทดสอบ/ข้อจำกัดของแต่ละตัว |
| ต่อ API/schema สำหรับ client หลายภาษา | `core_contracts/PORTABILITY_AND_PLUGIN_CONTRACT.md` | สัญญา integration แบบ draft; ยังไม่ใช่ implementation สากลที่ครบทุก protocol หรือ ECU |
| ดู provenance และไฟล์ที่ไม่คัดเข้า | `SOURCES_AND_REVISIONS.md`, `XDF_CANDIDATE_AUDIT_TH.md` | upstream URLs/commits, license, hashes และเหตุผลคัดเข้า/คัดออก |
| รันทดสอบ hardware-free ที่มี | คำสั่งท้ายเอกสารนี้ | ทดสอบ virtual CAN และ localhost TCP/UDP เท่านั้น ไม่ได้ทดสอบรถหรือ adapter จริง |

## เลือก ECU profile แบบเร็ว

| เป้าหมาย | Profile file | สถานะและการใช้ที่อนุญาต |
|---|---|---|
| Honda CBR1000RR 2012 US — engine ECU | `vehicle_profiles/engine/honda/CBR1000RR_2012_US/CBR1000RR_2012_US.xdf` | XDF ที่กรอง disable/immobilizer blocks ออกแล้ว; XML ผ่านการ parse แต่ยังเป็น offline candidate. ECU/software match และ external checksum plugin ยังไม่ยืนยัน. ห้าม auto-match หรือ write/flash. |
| Honda CRF110F 2019 / `38770-KYK-D12` — engine ECU | `vehicle_profiles/engine/honda/CRF110F_2019_KYK-D12_candidate/38770-KYK-D12.xdf` | XDF ต้นฉบับแบบ research candidate; region/start-offset ยังไม่ตรงกับ README upstream. ห้าม auto-match, แก้ offset โดยเดา, หรือ write/flash. |
| Honda CRF250L — diagnostic reference | `vehicle_profiles/diagnostics/honda_crf250l/` | ปี/ECU identity และค่าบางส่วนยัง unknown; ดูแบบ offline เท่านั้น ไม่ใช่ XDF หรือ verified protocol. |
| Kawasaki/Suzuki KDS/SDS — Z750/Z1000 context | `vehicle_profiles/diagnostics/kawasaki_kds_suzuki_sds/` | Workbook ที่กรองเหลือ 4 sheets; ค่าไม่ได้ยืนยันกับรถ ใช้เป็น offline reference เท่านั้น ไม่ใช่ ECU map profile. |

**ไม่มี engine profile ใดที่ `write_verified` หรือผ่านการทดสอบกับรถจริงในแพ็กนี้.** รายการ Suzuki Hayabusa ถูก exclude ทั้งโฟลเดอร์ เพราะต้นฉบับมี password metadata และ patch controls; Ducati MotoXDF ถูกพักไว้เพราะ upstream rights ยังไม่ชัดเจน. ไม่ได้รวม stock BIN/ROM, key/secret, seed-key, bypass หรือ disable maps.

## เข้าใจโครงสร้างก่อนเชื่อมอุปกรณ์

แนวคิดการแยกชั้นคือ **Application/API → protocol plugin → transport backend → adapter/device**. ECU profile เป็นข้อมูลประกอบสำหรับ exact ECU/module matching และ decoding/checksum evidence; การมี transport ไม่ได้แปลว่ามี protocol หรือ profile สำหรับรถคันนั้น

- **CAN frames:** `adapters/can_jsonl_sidecar/` + `dependencies/python-can-4.6.1/`; sidecar ใช้ JSON Lines ผ่าน stdin/stdout, TX ปิดโดยค่าเริ่มต้น และทดสอบกับ virtual CAN เท่านั้น. ไม่รวม ISO-TP/UDS/KWP หรือ OEM service.
- **TCP/UDP:** `transports/ip_socket/`; เป็น raw generic transport ไม่ได้เดา port/framing หรืออ้างว่าเข้ากันได้กับ WiCAN/ELM327.
- **BLE GATT:** `adapters/btleplug_scan/`; scan/list only, ยังไม่ได้ build และไม่ connect/read/write GATT.
- **Serial/BLE-UART/J2534:** ดู `adapters/README_TH.md`; เป็น source/reference เฉพาะ backend/device และยังไม่มี adapter จริงทดสอบ.

`dependencies/source_archives/` เก็บ source archives ที่เกี่ยวกับ dependency เพื่อ provenance/rebuild; เป็นไฟล์ภายในแพ็ก ไม่ใช่ ZIP เพิ่มเติมที่ต้องดาวน์โหลดแยก.

## ก่อนนำไปใช้กับรถหรือ hardware

1. ยืนยัน make/model/year/region **และ** module, ECU part number, HW/SW/calibration IDs ให้ตรงกับ profile; ถ้าไม่ตรงหรือ unknown ให้หยุดและไม่ auto-select.
2. ตรวจ source note, upstream revision และ LICENSE ของ component ที่จะใช้.
3. คงการทำงานเป็น read-only/offline จนกว่าจะมี exact-match evidence, known-good validation vectors, checksum verification และ bench/vehicle tests ที่เหมาะสม. XML parse ผ่านอย่างเดียวไม่ยืนยันความหมายของ map.
4. ใช้ adapter ตามเอกสารของรุ่นนั้นเท่านั้น; ห้ามต่อ TTL-UART เข้าบัส K-Line/CAN โดยตรง.

## รันทดสอบตัวอย่าง

จากโฟลเดอร์ `ecu_tuner_core_pack/` หลังติดตั้ง Python/pytest ตามสภาพแวดล้อม:

```sh
PYTHONPATH="dependencies/python-can-4.6.1:." python -m pytest -q \
  adapters/can_jsonl_sidecar/test_can_jsonl_sidecar.py \
  transports/ip_socket/test_raw_socket_transport.py
```

ผลตรวจล่าสุด: **6 tests ผ่าน** (virtual CAN + localhost TCP/UDP). นี่ไม่ใช่การทดสอบ ECU, รถ, Bluetooth หรือ adapter จริง.

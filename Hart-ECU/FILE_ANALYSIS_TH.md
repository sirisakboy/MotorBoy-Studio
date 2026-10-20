# วิเคราะห์ไฟล์ที่คัดเข้าชุด ECU Tuner Core

**สถานะการตรวจ:** ตรวจ source, dependency/import, platform binding, repository license และขอบเขตการทำงานจาก snapshot ที่ระบุใน `SOURCES_AND_REVISIONS.md`. นี่เป็น static review ไม่ใช่ security audit และไม่ได้ทดสอบ ECU/อะแดปเตอร์จริง.

## ข้อสรุปที่ควรอ่านก่อน

- **transport code เพิ่มแล้ว:** `adapters/can_jsonl_sidecar/` + `python-can 4.6.1` ผ่าน virtual CAN tests; `transports/ip_socket/` ผ่าน localhost TCP/UDP tests. ทั้งคู่ไม่มี ECU protocol; transmit ปิดโดยค่าเริ่มต้นและไม่มีการทดสอบอุปกรณ์/รถจริง.
- **serial/BT dependencies:** `libserialport` ยัง build/timing-test บน Linux ผ่าน; เพิ่ม source ของ `btleplug` (ยังไม่ได้ compile) และ `ble-serial` (BLE-UART reference; Windows Secure Boot caveat). ไม่มี BLE/serial adapter จริงทดสอบ.
- **เก็บเป็น reference แยกไว้ก่อน:** `references/kwp2000/` — โค้ดผูก Arduino และข้อมูลยี่ห้อปนกับ protocol. ตัวไฟล์มี MIT notice แต่ repository มี GPL-3.0 `LICENSE`; ให้ถือว่า license ยังต้องตรวจ ก่อนนำไป integrate.
- **เก็บเป็น reference only:** `references/xdf_parser/` — README แสดง MIT badge แต่ snapshot ไม่มีไฟล์ LICENSE/COPYING. โค้ดและข้อมูลยังไม่ควรย้ายเข้า software ที่จะแจกจ่ายจนยืนยันสิทธิ์.
- **backend แบบมีขอบเขต:** `adapters/windows_pyj2534/` ใช้ Windows DLL ผ่าน Python; `adapters/openport2_j2534/` เป็น C backend สำหรับ OpenPort 2.0 บน Linux/macOS. ไม่ใช่ driver สากลและไม่ควรรวมเป็น protocol layer.
- New Python 3 sidecar/transport/filter code passes syntax/tests. A blanket Python 3 `compileall` over the pack intentionally fails on upstream `dependencies/libserialport/config-header.py`, which uses Python 2 `print` syntax; that generator was not used in the successful Linux build. OpenPort backend ยัง build ไม่ได้ในสภาพแวดล้อมนี้เพราะไม่มี `libusb-1.0` development package. ไม่มีการเชื่อมอุปกรณ์จริง.

## 1. ไฟล์เอกสารและ contract ในชุด

| ไฟล์ | วิเคราะห์/การใช้ |
|---|---|
| `START_HERE_TH.md` | คู่มือเริ่มต้นหลังแตก ZIP; routes by task, links to exact profile/adapter files, states readiness and safety limits. ใช้เป็น quick selector ไม่ใช่คำสั่งแฟลช. |
| `README_TH.md` | คู่มือเปิดชุดและข้อจำกัด; เป็นเอกสารของชุดนี้ ไม่ใช่ upstream source. |
| `vehicle_profiles/PROFILE_PICKER_TH.csv` | quick chooser ของ included candidates, offline diagnostic references และ explicit excluded rows; ช่วยหา path/license/status/ข้อห้ามก่อนเปิด profile. ไม่ใช่การเพิ่ม coverage หรือการยืนยัน fit. |
| `SOURCES_AND_REVISIONS.md` | URL และ commit pin ของทุก upstream; ใช้ทำ provenance/repeatable review. |
| `core_contracts/PORTABILITY_AND_PLUGIN_CONTRACT.md` | Draft contract transport/protocol/profile/API สำหรับทุก module; ระบุ exact ECU matching, address semantics, checksum vectors, read-only default และขอบเขต immobilizer. ยังไม่มี implementation/schema validator ครบ และต้อง version ก่อนให้ client หลายภาษาใช้จริง. |
| `EXTENSION_RESEARCH_TH.md` | ผลคัดกรองและสถานะ additions สำหรับ CAN/BLE/Wi-Fi/K-Line/serial/maps/checksum; แยก transport/protocol/profile พร้อม license/scope, exclusions และ gaps. เป็น research note; implementation แยกอยู่ใน adapter/transport directories. |
| `XDF_CANDIDATE_AUDIT_TH.md` | File-by-file review ของ MotoXDF และ Honda GPL XDF candidates; บันทึก rights/provenance, identity gaps, excluded files และเหตุผลที่ CRF110F ยังเป็น candidate เท่านั้น. |
| `vehicle_profiles/README_TH.md` | ขอบเขตและข้อจำกัดของ model-specific definition candidates ที่เพิ่มภายหลัง; ระบุชัดว่า no stock BIN, no universal coverage, no approved auto-checksum. |
| `vehicle_profiles/PROFILE_COVERAGE.csv` | index machine-readable ของ ECU/module profiles และสถานะ checksum/license/validation; ใช้บอก gap โดยไม่แสร้งว่ารองรับทุกยี่ห้อ. |

## 2. `dependencies/libserialport/` — selected cross-platform serial library

| ไฟล์ | หน้าที่/ข้อสังเกต |
|---|---|
| `AUTHORS` | attribution ของผู้พัฒนา upstream; คงไว้พร้อม source. |
| `COPYING` | เงื่อนไข LGPL-3.0+ ของ library; ต้องแจกควบคู่ตามข้อกำหนด license. |
| `Makefile.am` | Automake build list; เลือก source ตาม OS. ในชุดนี้ examples ถูกตัดออก จึงไม่ใช้ `make dist` โดยไม่เพิ่ม example files กลับ. |
| `NEWS` | changelog/release notes; ใช้ตรวจการเปลี่ยนแปลงและแหล่งที่มา. |
| `README` | เอกสาร API/build/support; ระบุ port enumeration บน Windows/macOS/FreeBSD/Linux และ serial operations; ไม่ใช่ K-Line/J2534. |
| `autogen.sh` | เรียก `autoreconf` เพื่อสร้าง build machinery; ต้องมี autotools/libtool. |
| `common.props` | Visual Studio property sheet ที่ใช้ร่วมกัน; build metadata สำหรับ Windows. |
| `config-fields` | รายการ configuration field สำหรับ generator; ไม่ใช่ protocol code. |
| `config-header.py` | สร้าง/configure header จาก template และ feature checks. Source ใช้ Python 2 print syntax จึง `py_compile` ด้วย Python 3 ไม่ผ่าน; ไม่ได้ถูกเรียกใน build ที่ทดสอบบน Linux. คง upstream source ไว้ ไม่แก้ไขโดยไม่มี build rationale. |
| `config-pattern` | template/pattern สำหรับ generate configuration header; build-time เท่านั้น. |
| `configure.ac` | Autoconf checks และเลือก backend Linux/Windows/macOS/FreeBSD; เป็นจุดสำคัญของ portability. |
| `debug.props` | Visual Studio Debug configuration; build metadata. |
| `freebsd.c` | implementation เฉพาะ FreeBSD สำหรับ port/device metadata. |
| `libserialport.h` | public C API; จุดเชื่อมต่อที่ภาษาอื่นเรียกผ่าน FFI/wrapper ได้. เป็นส่วนที่สำคัญที่สุดสำหรับ client integration. |
| `libserialport.pc.in` | template สำหรับ `pkg-config`; ช่วยให้ build system อื่นหา library/header ได้. |
| `libserialport.sln` | Visual Studio solution. |
| `libserialport.vcxproj` | Windows/MSVC build definition. |
| `libserialport.vcxproj.filters` | แสดง/จัดกลุ่มไฟล์ใน Visual Studio; ไม่ใช่ runtime logic. |
| `libserialport_internal.h` | private structs, OS abstraction และ internal declarations; ไม่ควรให้ app layer เรียกตรง. |
| `linux.c` | Linux serial backend; system/device enumeration และ port operations. |
| `linux_termios.c` | Linux termios helper สำหรับ serial settings/baud/line configuration. |
| `linux_termios.h` | declarations/macros สำหรับ helper ใน `linux_termios.c`. |
| `macosx.c` | macOS-specific backend และการค้นหา/เปิด serial port. |
| `release.props` | Visual Studio Release configuration; build metadata. |
| `serialport.c` | common implementation: port objects, list/open/close/config/read/write/flush; shared runtime core. |
| `test_timing.c` | unit test สำหรับ timing utilities; ไม่ได้ทดสอบ USB/UART/K-Line. |
| `timing.c` | shared timing helpers; ใช้โดย core/backend. |
| `windows.c` | Windows-specific serial backend/port enumeration; ต้องใช้ Windows build/toolchain ที่ถูกต้อง. |

**Verification:** สร้างจาก curated subset บน Linux ด้วย autotools และ `make check`; `test_timing` ผ่าน 1/1. Build แจ้ง version macro ซ้ำ: `libserialport.h` ระบุ `0.1.1` แต่ `configure.ac` ระบุ `0.1.2`; ต้องตรวจ/แก้เวอร์ชันก่อน pin เป็น dependency production. ผลนี้ไม่เท่ากับทดสอบ adapter, USB driver หรือการสื่อสารกับ ECU.

## 3. `references/kwp2000/` — reference, ยังไม่ใช่ core ที่นำเข้า

| ไฟล์ | วิเคราะห์/การใช้ |
|---|---|
| `ISO.h` | รวม ISO/KWP constants แต่ยังใส่ global variables และ byte indices เฉพาะ Suzuki/Kawasaki/Honda/Yamaha ไว้ใน header เดียว; Honda/Yamaha มีค่า `?`/placeholder. การ include หลาย translation units อาจเจอ multiple-definition. แยก standard constants ออกจาก per-ECU profile ก่อนใช้. |
| `KWP2000.h` | public class/API แต่ผูก `HardwareSerial`, pin, `brand/model`, sensor getters กับ Arduino. ไม่เป็น interface กลางสำหรับ desktop OS/ภาษาอื่น. |
| `KWP2000.cpp` | implementation/state/timing/checksum/diagnostic requests; เรียก `millis`, `delay`, `digitalWrite`, `HardwareSerial`, `F()` ของ Arduino. มี warning ว่า Yamaha/Honda ยังไม่พร้อม; ใช้เป็น logic reference สำหรับ scope ที่ทดสอบเท่านั้น. ไม่ใช่ vehicle flash writer. |
| `LICENSE` | repository-level GPL-3.0. ต้องตรวจความสัมพันธ์กับ MIT permission header ที่ปรากฏใน source ก่อน reuse/redistribute. |
| `README.md` | ระบุ scope และ test/support claims; ใช้เป็น provenance, ไม่ถือว่า KWP2000 รองรับทุก ECU. |

**การตัดสิน:** ไม่คัด source นี้เข้า `portable-core` โดยตรง. ถ้าต้องใช้ ให้ยืนยัน license, แยก transport API ออกจาก protocol และเพิ่ม tests จาก ECU/profile ที่ต้องการจริง.

## 4. `references/xdf_parser/` — offline format reference only

| ไฟล์ | วิเคราะห์/การใช้ |
|---|---|
| `xdf_merge.py` | Python monolithic parser/exporter/merger สำหรับ XDF/BIN; มี XML parsing, map extraction, Excel/JSON export, imports `pandas`. README ผูกกับ Porsche 944. มี `eval()` สำหรับ formula ที่ปิด builtins แต่ยังต้อง audit/แทนด้วย parser ที่ allowlist ก่อนเปิดรับ XDF ที่ไม่เชื่อถือ. ไม่ทำ ECU connection/checksum/flash. |
| `README.md` | อธิบาย workflow และ dependencies (`pandas`, `xlsxwriter`); มี MIT badge แต่ไม่มี LICENSE file ใน tracked snapshot. |
| `LICENSE_STATUS.md` | ข้อจำกัดที่เราเพิ่มไว้: รอ license ชัดเจนก่อนนำ code ไปใช้/แจกจ่าย. |

**การตัดสิน:** เก็บเพื่อดู format handling เท่านั้น; ยังไม่ถือเป็น dependency ที่อนุมัติแล้ว.

## 5. `adapters/windows_pyj2534/` — Windows/Python J2534 reference

| ไฟล์ | วิเคราะห์/การใช้ |
|---|---|
| `LICENSE` | AGPL-3.0; ตรวจผล license ก่อนเชื่อมกับ application หรือเปิดเป็น network service. |
| `README.rst` | upstream notes; ทดสอบกับ Python 3.8.7 32-bit บน Windows ตามข้อมูลที่พบ. |
| `PyJ2534/__init__.py` | re-export enums/constants/functions ให้ import package ได้สะดวก. |
| `PyJ2534/define.py` | J2534 protocol IDs, flags, structures และ constants; เป็น reference ที่มีประโยชน์ แต่ต้องเทียบรุ่น SAE J2534/driver และ architecture. |
| `PyJ2534/dll.py` | wrapper `ctypes` สำหรับโหลด vendor DLL, enumerate Windows registry และเรียก PassThru functions; `WinDLL`/registry ทำให้เป็น Windows backend ไม่ใช่ cross-platform code. |
| `PyJ2534/error.py` | J2534 error enums/messages/exceptions; แยก error normalization ได้ แต่คง license attribution. |

**Verification:** syntax compile ผ่าน; ยังไม่ได้โหลด vendor DLL/adapter จึงยังไม่ได้ทดสอบ runtime.

## 6. `adapters/openport2_j2534/` — C backend สำหรับ OpenPort 2.0

| ไฟล์ | วิเคราะห์/การใช้ |
|---|---|
| `LICENSE` | GPL-3.0-or-later; คงการแยก backend จาก core จนกว่าจะตัดสินเรื่อง license/distribution. |
| `NOTICE` | attribution และข้อจำกัดความเกี่ยวข้องกับ Tactrix; ต้องคงไว้. |
| `README.md` | setup, supported OS/device, safety/limitations; ระบุ adapter OpenPort 2.0 ไม่ใช่ J2534 ทุกยี่ห้อ. |
| `Makefile` | build/install/test targets; ต้องมี `libusb-1.0` และ pthread. ในชุดนี้มี runtime/build core แต่ test suite ถูกตัด จึงอย่ารัน test target จนเพิ่ม tests กลับ. |
| `openport-j2534.pc.in` | package metadata template สำหรับ pkg-config. |
| `include/j2534/j2534.h` | public C ABI/type definitions ที่ expose PassThru functions; API boundary ระหว่าง client กับ backend. |
| `src/op_device.c` | device/channel lifecycle, queues, reader thread, frame dispatch; stateful device runtime. |
| `src/op_device.h` | internal device/channel structs และ declarations; private implementation contract. |
| `src/op_error.c` | เก็บ/format error detail ภายใน driver. |
| `src/op_error.h` | error helper declarations. |
| `src/op_j2534.c` | implementation ของ J2534 PassThru exported functions; เป็น backend API—not ECU manufacturer protocol. |
| `src/op_log.c` | diagnostics/logging ของ driver; ไม่ควรให้ log raw secrets/vehicle data โดยไม่ตั้งค่า. |
| `src/op_log.h` | logging API ภายใน. |
| `src/op_proto.c` | encode/decode protocol ระหว่าง driver กับ OpenPort cable; ไม่ใช่ ISO 14230/KWP2000 ของ ECU. |
| `src/op_proto.h` | declarations/types ของ cable protocol parser. |
| `src/op_serial.c` | serial transport implementation สำหรับคุยกับ cable ตาม backend. |
| `src/op_transport.h` | internal transport vtable/abstraction; ตัวอย่างที่ดีของการแยก USB กับ serial implementation. |
| `src/op_usb.c` | USB transport ผ่าน libusb; ต้องมี libusb headers/library และ permissions ที่ OS ต้องการ. |
| `tools/probe/op_probe.c` | diagnostic probe เพื่อค้นหา/ตรวจ cable; ไม่ใช่ ECU protocol. |
| `docs/API.md` | อธิบาย J2534 API surface ของ driver. |
| `docs/PROTOCOL.md` | หลักฐาน/รายละเอียด cable wire protocol; ใช้เฉพาะ OpenPort backend. |
| `docs/TESTING.md` | test strategy/simulator/limitations; ชุดนี้ไม่รวม source tests จึงใช้เป็นเอกสาร ไม่ใช่การยืนยันว่า tests ถูก run แล้ว. |

**Verification:** ยังไม่ได้ compile เพราะ environment ไม่มี `libusb-1.0` development package; ไม่ได้ต่อ OpenPort จริง. README upstream ระบุ CAN tested; K-Line ยังไม่ถือว่า verified กับ ECU จริง.

## ไฟล์/ข้อมูลที่จงใจไม่ดาวน์โหลด

ไม่รวม stock binary BIN/ROM, XDF collections ทั้งหมด, dashboard/GUI ของโปรเจกต์บอร์ด, ECU-specific checksum corrector, unfiltered manufacturer DTC dumps, Arduino examples และ full test/example trees ที่ไม่ใช่ runtime core. มีเพียง KDS/SDS workbook 4 sheets ที่คัดเป็น offline reference และ Honda CRF250L diagnostic sample ที่ license/provenance ระบุแยก; ยังไม่ถือว่า verified.

## 7. `vehicle_profiles/` — model-specific definitions (definitions only)

ผู้ใช้เลือก scope ว่าจะครอบคลุมทุกโมดูล ECU แต่เก็บเฉพาะ definitions/profile data และไม่รวม stock BIN. ไฟล์ข้างล่างเป็น profile candidate 2 รุ่นในกลุ่ม engine ECU เท่านั้น; ยังไม่มี profile สำหรับ ABS/TCU/cluster/BMS.

| ไฟล์ | วิเคราะห์/การใช้ |
|---|---|
| `vehicle_profiles/README_TH.md` | อธิบาย scope, validation gates, immobilizer exclusion และแนวทางเพิ่ม profile. เป็นเอกสารของชุดนี้. |
| `vehicle_profiles/PROFILE_COVERAGE.csv` | index ระบุ module, make/model/ID, format, license, status, checksum state, test status และ coverage gaps. ค่าที่ไม่ยืนยันถูกทำเครื่องหมายเป็น candidate/no_profile. |
| `vehicle_profiles/engine/honda/CBR1000RR_2012_US/CBR1000RR_2012_US.xdf` | Filtered GPL-3.0 derivative from HondaECU; XML version 1.60, `REGION` size `0x3FFFF` inclusive (262,144 bytes), 39 tables, 105 address-bearing `EMBEDDEDDATA` elements all within region. Removed five `XDFPATCH` disable blocks and one `Disable Immobilizer` `XDFFLAG`; no patch/flag blocks remain. `XDFCHECKSUM` still references an external plugin/store address `0x3FFF8`, with no algorithm/vectors in pack. No BIN; not vehicle-tested. |
| `vehicle_profiles/engine/honda/CBR1000RR_2012_US/LICENSE` | Upstream GNU GPL-3.0 license ที่คงไว้กับ XDF; การแจกจ่าย/รวมต่ออยู่ภายใต้เงื่อนไข GPL. |
| `vehicle_profiles/engine/honda/CBR1000RR_2012_US/SOURCE_NOTE_TH.md` | Provenance, original/filtered hashes, GPL-3.0 modification list, static validation และ checksum limitation. เป็นสถานะ `filtered_candidate`, ไม่ใช่หลักฐานการทดสอบ ECU จริง. |
| `vehicle_profiles/engine/honda/CRF110F_2019_KYK-D12_candidate/38770-KYK-D12.xdf` | XDF version 1.60 จาก HondaECU; 11 tables, 0 flags/constants/checksum blocks. XML parse และ data-span check ผ่าน แต่ upstream header ระบุ `REGION size="0x65536"` ขณะที่ README ระบุ 64 kb; `Start Offset 8000` กับ `BASEOFFSET=0` ยังไม่ reconcile. คงไฟล์ต้นฉบับไม่แก้; quarantined candidate only, no auto-match. ไม่รวม BIN. |
| `vehicle_profiles/engine/honda/CRF110F_2019_KYK-D12_candidate/LICENSE` | Root GPL-3.0 license จาก source snapshot; เก็บไว้ข้าง XDF เพื่อ attribution/redistribution. |
| `vehicle_profiles/engine/honda/CRF110F_2019_KYK-D12_candidate/SOURCE_NOTE_TH.md` | Source commit/hash, upstream README identity, static checks และ metadata/compatibility gaps; ระบุชัดว่าไม่ใช่ ECU/vehicle-tested support. |

**การตัดสิน:** XDF ทั้งสองเป็น offline definition/reference เท่านั้น. XML parse และ address-start/span checks ผ่าน แต่ไม่มี profile matching จาก real ECU/HW/SW ID, known-good BIN, checksum vectors หรือ vehicle testing. CRF110F ยังมี region/start-offset metadata discrepancy ที่ต้องแก้ไขจากหลักฐานต้นทางก่อนใช้งาน. จึงยังไม่มี auto checksum และยังไม่อนุญาตให้ write/flash จาก profile เหล่านี้. Hayabusa XDF ที่ตรวจพบ password metadata และ patch controls ถูกตัดออกทั้งหมด; ดู `XDF_CANDIDATE_AUDIT_TH.md`.

## 8. `dependencies/python-can-4.6.1/` + `adapters/can_jsonl_sidecar/` — CAN frame transport

### `python-can` source

| File group/file | วิเคราะห์/การใช้ |
|---|---|
| `dependencies/python-can-4.6.1/can/` | Upstream `python-can` runtime package (97 extracted files). Shared `BusABC`/message/listener/notifier/util APIs sit in common modules; `can/interfaces/` provides hardware/socket/serial-specific backends; `can/io/` handles trace/log formats. A backend can still require optional Python packages, vendor SDKs/drivers, OS configuration and hardware. It is not a motorcycle OEM protocol library. |
| `LICENSE.txt` | Upstream LGPL-3.0-only; retain and review dynamic/static linking and redistribution obligations. |
| `README.rst`, `CHANGELOG.md` | Upstream usage/release notes; not a verification report for this pack. |
| `pyproject.toml`, `setup.cfg` | Upstream project metadata, supported Python/dependency requirements and packaging/lint configuration. Direct runtime dependencies include `wrapt`, `packaging`, and `typing_extensions`; not vendored. |
| `FILE_INDEX.csv` | Per-file upstream path, byte count, SHA-256 and reviewed role for all extracted source/metadata files; the source note and generated index itself are local additions, not upstream files. |
| `SOURCE_NOTE_TH.md` | Records artifact hash, license, extraction boundaries, direct dependencies, smoke test and no-hardware status. |
| `dependencies/source_archives/python_can-4.6.1.tar.gz` | Exact PyPI source archive retained for reproducibility; SHA-256 is recorded in `SOURCES_AND_REVISIONS.md`. It contains more upstream material than the curated extracted tree. |

**Verification:** import of the extracted package and a two-bus `virtual` send/receive smoke test passed. No physical CAN adapter or motorcycle was tested. Virtual interface success does not validate PCAN/Kvaser/SocketCAN/SLCAN/vendor backends.

### Local sidecar

| File | วิเคราะห์/การใช้ |
|---|---|
| `adapters/can_jsonl_sidecar/can_jsonl_sidecar.py` | In-house JSON-RPC-like JSON-lines process over stdin/stdout. Methods: list interfaces, open/close bus, receive and (opt-in) send CAN frames. Does not bind a network port. Restricts backend options to an allowlist; TX is disabled unless started with `--allow-tx`. CAN frames are not parsed into ISO-TP/UDS/KWP/OEM services. |
| `adapters/can_jsonl_sidecar/test_can_jsonl_sidecar.py` | Hardware-free tests for virtual CAN receive, explicit transmit opt-in, invalid interface/parameter handling. Test frame values are synthetic, not ECU requests. |
| `adapters/can_jsonl_sidecar/README_TH.md` | Start/use instructions, dependencies, safety and hardware test limitations. |
| `core_contracts/CAN_SIDECAR_PROTOCOL.md` | Method fields, examples, error behavior and safety boundaries for cross-language callers. |
| `core_contracts/CAN_SIDECAR_SCHEMA.json` | Draft JSON Schema for the request/response envelope and method parameters. Schema/API are draft v1 and should be versioned before stable client generation. |

## 9. `transports/ip_socket/` — generic IP/Wi-Fi byte transports

| File | วิเคราะห์/การใช้ |
|---|---|
| `transports/ip_socket/raw_socket_transport.py` | In-house `TcpByteStream` and connected `UdpDatagramEndpoint`. TX is explicit opt-in, timeout/size/port ranges are validated, and the code is client-only (no listener/port scan). TCP reads are byte chunks, not message frames; UDP datagrams are not automatically CAN or ECU frames. No protocol/port is guessed. |
| `transports/ip_socket/test_raw_socket_transport.py` | Localhost-only TCP echo and UDP request/reply tests, including default TX gate; no adapter/ECU traffic. |
| `transports/ip_socket/README_TH.md` | Documents exact-model endpoint/framing/authentication requirements and exclusions for WiCAN/ELM/SLCAN/GVRET. |
| `transports/ip_socket/__init__.py` | Package marker; no runtime behavior. |

**Verification:** CAN + IP hardware-free tests passed 6/6. Socket tests establish only generic localhost transport semantics; they do not verify WiCAN or another adapter protocol.

## 10. `dependencies/btleplug-0.13.5/` and `dependencies/ble-serial-3.0.0/` — Bluetooth source

### `btleplug`

| File group | วิเคราะห์/การใช้ |
|---|---|
| `dependencies/btleplug-0.13.5/src/` | Upstream Rust BLE GATT library. `src/lib.rs`, `api`/platform facade and shared types define the API; `src/bluez/` is Linux BlueZ, `src/winrtble/` Windows WinRT, Apple-specific modules use CoreBluetooth, and Android modules use platform JNI/OS bindings. This is BLE GATT, not Bluetooth Classic/RFCOMM/SPP. |
| `examples/*.rs` | Four upstream samples for peripheral discovery, event discovery, notifications and a demonstration peripheral. Examples are not vehicle/adapter profiles. |
| `Cargo.toml`, `Cargo.toml.orig`, `Cargo.lock`, `.cargo_vcs_info.json` | Crate/feature/dependency/build metadata, lockfile and embedded Git revision. Edition 2024 is declared. |
| `LICENSE.md`, `README.md`, `CHANGELOG.md` | Upstream license bundle and project context/release history. Metadata lists `MIT/Apache-2.0/BSD-3-Clause`. |
| `FILE_INDEX.csv` | Per-file SHA-256/size/role inventory for the 100-file upstream crate extraction. |
| `SOURCE_NOTE_TH.md`, `../source_archives/btleplug-0.13.5.crate` | Provenance and exact Crates.io artifact checksum. |

**Verification limitation:** `rustc`/`cargo` were unavailable; no compile/test or BLE peripheral connection occurred. GATT UUIDs, pairing/security and adapter characteristics remain unknown. It is source for a future BLE sidecar only.

### `ble-serial`

| File group | วิเคราะห์/การใช้ |
|---|---|
| `dependencies/ble-serial-3.0.0/ble_serial/bluetooth/` | Upstream BLE client/server and UUID helpers for a matching BLE-UART service; does not fit every BLE adapter automatically. |
| `ble_serial/ports/linux_pty.py`, `ports/tcp_socket.py`, `ports/interface.py` | POSIX PTY/TCP serial-like data bridge. TCP server behavior is part of upstream BLE bridge; inspect host binding and use only on trusted local networks. |
| `ble_serial/ports/windows_com0com.py`, `setup_com0com/` | Upstream Windows virtual COM setup. Upstream install instructions may require disabling Secure Boot to install its driver; this pack does not recommend doing so. Prefer a native, secure BLE GATT route on Windows. |
| `ble_serial/scan/`, `main.py`, `cli.py`, `log/` | Scan, CLI/orchestration and optional traffic logging. Upstream CLI defaults to `rw`; set/review direction explicitly and do not treat it as a safe ECU diagnostic mode. |
| `LICENSE`, `README.md`, `pyproject.toml`, `requirements.txt` | MIT license, upstream usage, direct runtime dependency metadata (Bleak/coloredlogs; pyserial on Windows). Dependencies not bundled. |
| `FILE_INDEX.csv`, `SOURCE_NOTE_TH.md`, source archive | File inventory and provenance/checksum; source extraction intentionally excludes tests/log data, helper daemons, CI and notebooks. |

No BLE device was tested. The package is a BLE-UART bridge source/reference only, not an ECU protocol or profile.

### Local BLE scan sidecar

| File | วิเคราะห์/การใช้ |
|---|---|
| `adapters/btleplug_scan/Cargo.toml` | Local Rust 2024 package manifest; depends on the pinned local btleplug crate, Tokio, and serde_json. Transitive crates are not vendored. |
| `adapters/btleplug_scan/src/main.rs` | Local stdin/stdout JSON-lines adapter with `ble.adapters.list` and bounded `ble.scan`. It calls adapter enumeration/state, start/stop scan, and advertisement metadata APIs only. It deliberately contains no connect, GATT discovery/read/write/subscribe, nor ECU protocol path. |
| `adapters/btleplug_scan/example_requests.jsonl` | Two example requests; output is environment-dependent. |
| `adapters/btleplug_scan/README_TH.md` | Build/use contract and explicit no-build/no-device limitation. |
| `adapters/btleplug_scan/STATIC_REVIEW_TH.md` | Source API review checklist against included `btleplug` 0.13.5 interfaces; static review is not compile verification. |
| `core_contracts/BLE_SIDECAR_PROTOCOL.md` | Draft v1 method boundaries and output interpretation for client bindings. |
| `core_contracts/BLE_SIDECAR_SCHEMA.json` | Draft JSON Schema for adapter-list/scan requests and generic JSON-RPC responses. |

**Build status:** source-level inspection only. Rust/Cargo are absent; this wrapper has not been compiled, and no BLE adapter/peripheral was tested. Do not present it as a verified platform adapter.

## 11. `vehicle_profiles/diagnostics/` — model-specific offline diagnostic references

| File | วิเคราะห์/การใช้ |
|---|---|
| `diagnostics/README_TH.md` | Clarifies these two narrow samples are diagnostic reference data, not map definitions or verified OEM service coverage. |
| `diagnostics/honda_crf250l/Tables-With-Data-CRF250L.txt` | Upstream text with table/request-response byte samples and author annotations. Contains explicit `??` fields; exact CRF250L year/software/ECU identity is not pinned. Do not transmit solely based on this file. |
| `diagnostics/honda_crf250l/UPSTREAM_README.md` | Upstream author's K-Line hardware/baud/protocol context; claims are not independently validated. |
| `diagnostics/honda_crf250l/LICENSE`, `SOURCE_NOTE_TH.md` | MIT notice, source snapshot, SHA-256 and candidate/reference-only status. No Arduino source or firmware included. |
| `diagnostics/kawasaki_kds_suzuki_sds/KDS_SDS_Z750_Z1000_PIDs_filtered.xlsx` | Curated derivative of an upstream workbook. Exactly four sheets: `KDS PID` (164 rows), `Supported PIDs Z1000` (165), `Supported PIDs Z750` (195), `Service Codes` (28). Cached formulas are flattened as literal values so they display consistently; cached values are not recalculated or vehicle-verified. |
| `diagnostics/kawasaki_kds_suzuki_sds/LICENSE`, `SOURCE_NOTE_TH.md` | GPL-3.0 upstream license, repo/workbook hashes, transformation/filter details and uncertainty. Original workbook/repository is not included. |
| `tools/filter_kds_workbook.py` | Local openpyxl script to repeat the four-sheet filter against the exact upstream workbook; outputs cached formula values as literals and verifies the selected sheet names/no formulas. It does not verify PID/DTC correctness. |

Excluded from KDS derivative: generic OBD/other sheets, `AT-Commands`, `SID`, `Raterei`, `Test`, Bluetooth/reset/clear/configuration commands, standards PDFs, code and generated artifacts. The included `Service Codes` data does not prove compatibility beyond its documented sheet context and does not add ABS/TCU/cluster profiles.

## 12. Pack-level integrity and safety status

`MANIFEST_SHA256.csv` is regenerated after all additions and contains 338 file records; `ecu_tuner_core_pack.zip` contains those files plus the manifest (339 entries). Every manifest path/hash/size was checked against disk, the ZIP central directory matches the expected entry count, and `zipfile.testzip()` passes. Direct files and retained source archives were checked for `.bin`/`.rom`; none are included. A valid XML/XLSX/CAN virtual test is not proof of ECU compatibility, semantic correctness, checksum validity, safe calibration or vehicle operation.

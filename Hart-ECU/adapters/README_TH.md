# Transport adapters ที่คัดเพิ่ม

เอกสารนี้จัดแยก **transport**, **vehicle protocol** และ **ECU profile** ตาม contract หลัก การมี adapter ไม่ได้หมายถึงมี protocol/ECU definition สำหรับรถทุกคัน

| Link/transport | ส่วนในแพ็ก | สถานะ/ขอบเขต |
|---|---|---|
| CAN | `can_jsonl_sidecar/` + source `dependencies/python-can-4.6.1/` | ใช้ `python-can` สร้าง Bus/รับส่ง CAN frame. Sidecar ทำงานผ่าน stdin/stdout JSON Lines, ไม่มี network listener และปิด TX เป็นค่าเริ่มต้น. ทดสอบผ่าน virtual CAN เท่านั้น; ยังไม่ทดสอบ adapter จริง/รถจริง. ไม่ได้รวม ISO-TP/UDS/KWP หรือ OEM service/ID. |
| BLE GATT | `dependencies/btleplug-0.13.5/` + `btleplug_scan/` | Rust host BLE library และ local JSON-lines discovery sidecar; scan/list only, no connect/GATT read/write. ยังไม่ได้ build (environment ไม่มี `rustc`/`cargo`) หรือเชื่อมอุปกรณ์. BLE เท่านั้น ไม่ใช่ Bluetooth Classic/SPP และไม่รู้ UUID/protocol ของ adapter โดยอัตโนมัติ. |
| BLE-UART → serial | `dependencies/ble-serial-3.0.0/` | source subset MIT สำหรับ bridge BLE-UART กับ PTY/TCP; upstream Windows virtual-COM path อาศัย com0com และคู่มือ upstream ระบุให้ปิด Secure Boot ในบางระบบ Windows 10+. **ไม่แนะนำให้ปิด Secure Boot**; ใช้ source นี้เป็น POSIX/reference เท่านั้นจนทดสอบ OS/อุปกรณ์. Upstream CLI default เป็น read/write (`rw`), จึงอย่าต่อกับ ECU โดยไม่ตรวจ UUID, permission และ mode ก่อน. |
| Bluetooth Classic/SPP | OS มัก expose เป็น COM/TTY; `dependencies/libserialport/` จัดการ serial port | ต้องจับคู่/เลือกอุปกรณ์โดย OS และยืนยัน port. ไม่ใช่ BLE GATT. |
| Wi‑Fi / IP socket | `transports/ip_socket/raw_socket_transport.py` | generic TCP byte stream / UDP datagram, TX ปิดโดยค่าเริ่มต้น. ต้องระบุ IP/port และ framing จากเอกสารอะแดปเตอร์จริง; **ไม่มีการเดา WiCAN/ELM327/SLCAN/GVRET port หรือ framing**. Test ใช้ localhost เท่านั้น. |
| USB-TTL / UART | `dependencies/libserialport/` | serial API; ต้องตรวจ logic level, baud, parity, pinout และ transceiver. TTL UART ต่อเข้าบัส K-Line/CAN โดยตรงไม่ได้. |
| J2534 | `openport2_j2534/`, `windows_pyj2534/` | แยก backend ตาม OS/device/driver. ยังไม่มี adapter จริงเชื่อมทดสอบ. |

## Test ที่ทำได้ในแพ็ก

จาก `ecu_tuner_core_pack/`:

```sh
PYTHONPATH="dependencies/python-can-4.6.1:." python -m pytest -q \
  adapters/can_jsonl_sidecar/test_can_jsonl_sidecar.py \
  transports/ip_socket/test_raw_socket_transport.py
```

ผลตรวจใน sandbox: 6 tests ผ่าน (virtual CAN + localhost TCP/UDP); ไม่ใช่การทดสอบกับรถจริง. รายละเอียด JSON methods อยู่ใน `../core_contracts/CAN_SIDECAR_PROTOCOL.md`.

# Python CAN JSON-lines sidecar

## ขอบเขต

Sidecar นี้เป็นตัวอย่าง local process adapter สำหรับพา CAN frame API ไปยัง client หลายภาษา ผ่าน newline-delimited JSON-RPC 2.0 บน stdin/stdout. ไม่มี TCP/HTTP listener. ใช้ source `dependencies/python-can-4.6.1/` ซึ่ง license LGPL-3.0-only; runtime dependencies ที่ระบุ upstream (`wrapt`, `packaging`, `typing_extensions`) ต้องติดตั้งแยก.

**ไม่ใช่** ISO-TP, UDS, KWP2000, manufacturer diagnostics, ECU profile, map reader/writer หรือ checksum tool. รับ/ส่งได้เพียง CAN frame.

## Default และความปลอดภัย

- `can.send` ถูกปฏิเสธเป็นค่าเริ่มต้น. เปิดส่งได้เฉพาะเมื่อเรียก process ด้วย `--allow-tx` อย่างชัดแจ้ง.
- ไม่ส่ง request อัตโนมัติเมื่อเปิด bus; ไม่มี ECU address/protocol ที่เดาไว้.
- `can.open` รับเฉพาะ interface, channel, bitrate, CAN-FD และ receive-own flag ที่ allowlist; ไม่ส่ง config dictionary เข้า vendor backend แบบอิสระ.
- sidecar ควรเปิดผ่าน process pipe ของ client ที่เชื่อถือได้ ไม่ควรครอบด้วย network listener โดยไม่มี auth/ACL.
- การเปิด interface จริงอาจ initialize adapter/driver แม้ไม่ส่ง CAN. ใช้ bench/adapter ที่เหมาะสมและยืนยัน bitrate/termination ก่อน.

## Run

ตัวอย่าง virtual bus สำหรับ test เท่านั้น:

```sh
PYTHONPATH="dependencies/python-can-4.6.1" \
  python adapters/can_jsonl_sidecar/can_jsonl_sidecar.py
```

ส่ง JSON object หนึ่งบรรทัดต่อ request, อ่าน response หนึ่งบรรทัด. Methods: `system.info`, `can.interfaces.list`, `can.open`, `can.receive`, `can.send`, `can.close`. รายละเอียด fields/error codes อยู่ใน `../../core_contracts/CAN_SIDECAR_PROTOCOL.md` และ schema companion.

สำหรับ CAN hardware ให้ระบุ interface/channel/bitrate จากคู่มือ vendor ที่แน่นอน; อย่าคาดเดา hardware ID/bitrate. Test แบบ hardware-free:

```sh
PYTHONPATH="dependencies/python-can-4.6.1:." python -m pytest -q \
  adapters/can_jsonl_sidecar/test_can_jsonl_sidecar.py
```

ผล smoke tests ผ่านด้วย `virtual` interface เท่านั้น. License/attribution ของ upstream source อยู่ใน dependency directory.

# Generic Wi-Fi / IP socket transport

`raw_socket_transport.py` ให้ host-side TCP byte stream และ UDP datagram แบบไม่เดา protocol. ใช้ได้เฉพาะเมื่อคู่มือ adapter ระบุ endpoint และ payload framing จริงแล้ว.

- TCP คือ stream; ขอบเขตการอ่าน (`recv`) ไม่เท่ากับขอบเขต message/frame.
- UDP รักษาขอบเขต datagram แต่ไม่ได้กำหนด CAN framing หรือ ECU semantics.
- TX ถูกปิดโดยค่าเริ่มต้น (`tx_enabled=False`).
- Code ไม่เปิด listener, ไม่ scan network, ไม่ตั้ง port เอง, ไม่ parse ELM327/SLCAN/GVRET/WiCAN/MQTT และไม่ส่ง ECU command.
- Test ทำกับ loopback `127.0.0.1` เท่านั้น.

ก่อนต่ออะแดปเตอร์ Wi-Fi ต้อง pin exact model/firmware, security/pairing, local/remote IP, port, byte framing, timeout/reconnect semantics, bus bitrate/filter configuration และ verified vehicle protocol. ห้ามอนุมาน WiCAN protocol หรือ port จากคำว่า Wi-Fi อย่างเดียว.

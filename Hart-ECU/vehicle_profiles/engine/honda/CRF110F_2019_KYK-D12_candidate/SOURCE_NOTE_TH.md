# Honda CRF110F 2019 / 38770-KYK-D12 — XDF source note

**สถานะ:** research candidate เท่านั้น; ยังไม่ใช่ support ที่ยืนยันแล้ว และยังไม่ eligible สำหรับ auto-match, checksum correction, write หรือ flash.

## แหล่งที่มาและสิทธิ์

- Repository snapshot: [`aeaphichart/HondaECU-1`](https://github.com/aeaphichart/HondaECU-1) at commit `b59ae98baf092def23d7c34d5ef5f43bd6aba952`; repository metadata ระบุว่าเป็น fork ในสาย `Adeen117/HondaECU` / `roccofz1/HondaECU`.
- ไฟล์: `xdfs/CRF110F_KYK_2019/38770-KYK-D12.xdf`.
- File history: commit `b592b5709f27310abed6634bbb4a5c1ac289b8ec` โดย Ryan Hope, 2019-05-15 (`xdf fixes`).
- Root license ของ repository เป็น GNU GPL version 3; สำเนา `LICENSE` อยู่ใน directory นี้. ไม่พบ per-file exception หรือ license คนละชุดใน XDF/commit ที่ตรวจ.
- `README.md` ใน snapshot ระบุ `CRF110F`, ปี 2019, ROM size 64 kb, Keihin code `38770-KYK-D12`, checksum address `0`, start offset `8000`, CPU M16C.
- คัดลอกเฉพาะ XDF และ LICENSE; **ไม่คัดลอก stock BIN** หรือ source tree อื่น.

## SHA-256 และ static review

- XDF bytes: 18,666; SHA-256 `0849ebc1173d206dc55ca1ed6ec614e7eb8477cdb9c6b899aa4316c059ac384d`.
- XDF version `1.60`; XML parse ผ่าน; 11 tables; 0 constants; 0 flags; 0 `XDFCHECKSUM` blocks.
- Tables: RPM/TPS/MAP breakpoints, fuel MAP/TPS vs RPM, ignition timing tables 1–4, ignition timing TPS-fail, rev limiter.
- ไม่พบ label ที่ระบุ immobilizer/key/seed/bypass/security; ไม่มีไฟล์ firmware ใน directory นี้.
- Static span check จาก `EMBEDDEDDATA`/จำนวน element ที่ระบุใน XDF พบ map data อยู่ประมาณ `0x0011–0x1E97`; ทั้งหมดอยู่ภายใน 64 KiB หากใช้ region `0x10000`. นี่เป็น bounds check ไม่ใช่การยืนยันว่า address semantics ถูกต้อง.

## Compatibility gaps — ห้ามแก้/เดาโดยไม่มีหลักฐาน

1. XDF ประกาศ `REGION size="0x65536"` ขณะที่ README ของ upstream ระบุ ROM 64 kb (ซึ่งปกติเท่ากับ `0x10000`). เมื่ออ่าน prefix `0x` เป็นเลขฐานสิบหก ขนาดใน XDF ไม่ตรงกับ README. คงไฟล์ upstream ไว้ไม่แก้ไขและทำเครื่องหมายเป็น `candidate_metadata_mismatch`.
2. README ระบุ `Start Offset 8000`, แต่ XDF มี `BASEOFFSET offset="0"` และ map addresses อยู่ช่วงต้นของ file. ยังไม่ทราบว่า offset ใน README เป็น CPU load address หรือ binary-file offset; ต้องยืนยันก่อนนำไป match.
3. README มี checksum address `0`, แต่ XDF ไม่มี checksum definition/algorithm/test vectors. ห้ามตีความว่า checksum ใช้ได้.
4. ไม่มี software/calibration fingerprint, known-good BIN ที่ได้รับอนุญาต, ECU bench test หรือ vehicle test. `CRF110F 2019 / 38770-KYK-D12` เป็น label จาก upstream README เท่านั้น.

หากจะยกระดับเป็น profile ที่ใช้ได้ ต้องหาหลักฐานที่ระบุ software/calibration ID และ region/address origin, แก้หรือยืนยัน region metadata จากต้นทาง/ไฟล์ตัวอย่างที่มีสิทธิ์, เพิ่ม checksum vectors ที่ตรวจสอบได้ และทดสอบบน bench ที่ได้รับอนุญาต. ห้ามนำค่าไปใช้กับ ECU รุ่นอื่นเพียงเพราะเป็น Honda/M16C.

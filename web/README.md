# MotorBoy web editor (offline XDF/BIN)

```
pip install -r requirements-server.txt
python server/ecu_backend.py          # ws://127.0.0.1:8765
# then open web/ecu_real.html in a browser → Remap → "XDF / BIN (OFFLINE)"
```

1. Pick a **V5 XML** `.xdf` and the matching `.bin` (e.g. `xdfs/CBR500R_MJW_2017-2018/38770-MJW.xdf` + `bins/CBR500R_MJW_2017-2018/*.bin`).
2. Choose a table, click a cell, type the **scaled** value (the server converts back to raw with the XDF equation) and APPLY.
3. `EXPORT` downloads the edited copy. Checksum is **not** touched unless you use `+ CK`.

Safety: the server is offline-only. Every hardware action (connect / read / flash / SmartKey / live data) is refused,
it binds to 127.0.0.1 and rejects non-local browser origins. Never flash an exported file without checking
the checksum and comparing against a known-good backup of the same ECU part number.

Limits: legacy binary XDF (TunerPro V4, 13 files in `xdfs/`) is rejected with a clear message — re-save as V5 XML in TunerPro.
The Dashboard / DTC / Flash / Sensor pages of `ecu_real.html` still need the hardware backend (not part of this server).

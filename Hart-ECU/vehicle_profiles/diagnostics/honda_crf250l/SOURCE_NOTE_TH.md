# Honda CRF250L K-Line diagnostic sample — provenance note

- **Upstream:** `https://github.com/sophienyaa/Honda-Motorcycle-ECU-Tools`, pinned repository snapshot `84c203736dcea4ef1b436bfc4d36eca73d897110` (file content from that snapshot).
- **License:** MIT; `LICENSE` copied beside the sample.
- **Included:** `Tables-With-Data-CRF250L.txt` (upstream table/response sample, 940 bytes; SHA-256 `5b2c68b5a5405068a7489c277410c924eaae33eee50e43f5e3f8bc9715269974`) and `UPSTREAM_README.md` (hardware/protocol context; SHA-256 `91af927f1e14c8d2e14de533f27bb083dc1fd66af9a6d3407706c9efeeb6634b`). No Arduino sketch/source or firmware image is included.
- **Content:** example request/response byte sequences and author annotations for a Honda CRF250L diagnostic session; upstream README describes a K-Line adapter and approximately 10,400 baud. Several values are explicitly `??`/unknown. These are community observations, not verified maps, scaling metadata, checksum data, or universal post-2005 Honda support.
- **Status:** read-only/offline reference candidate. The packet semantics and exact CRF250L year/ECU/software identity have not been independently validated; do not send the recorded bytes to a vehicle without matching hardware/protocol evidence.
- **Scope:** this is not an XDF or engine-map definition and does not cover ABS, traction control, cluster, immobilizer, TCU, or BMS. No BIN/ROM is included.

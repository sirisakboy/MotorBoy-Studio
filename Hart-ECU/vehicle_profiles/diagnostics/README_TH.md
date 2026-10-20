# Diagnostic reference samples (not ECU map definitions)

`honda_crf250l/` and `kawasaki_kds_suzuki_sds/` contain narrow, license-attributed offline samples. They complement—but do not expand the verified map-profile set. Every request/response and table is model/hardware-specific and remains unverified unless a note says otherwise.

- Honda CRF250L: community K-Line example data; several fields are unknown; exact year and ECU identity are not pinned.
- KDS/SDS: filtered PID/service-code workbook for Z750/Z1000 context. Four read/reference sheets retained; reset/clear/configuration sheets excluded; source workbook not redistributed.

Neither sample is an XDF/map definition or an ABS/TCU/cluster/BMS profile. Do not transmit its bytes based solely on this reference. No BIN/ROM or security/immobilizer material is included.

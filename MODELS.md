# Honda ECU Models Database

This document describes the supported Honda ECU models and how to add new ones.

## Data Structure

Each ECU model entry contains:
- `model`: Human-readable model name
- `year`: Model year(s) or year range
- `pn`: Part number (Keihin code)
- `checksum`: Checksum location in the ROM file
- `offset`: Start offset for flashing (when different from 0)
- `ecmidaddr`: Memory address where ECM ID is stored
- `keihinaddr`: Memory address where Keihin ID is stored

## Adding New Models

1. Find the ECM ID (first 5 bytes of the ECU response at address 0x71)
2. Add the new entry to `src/ecmids.py` with the correct ECM ID key
3. Update the XDF files in the `xdfs/` directory

## Checksum Offsets Reference

| ROM Size | Common Checksum Locations |
|----------|---------------------------|
| 48KB     | 0x0                       |
| 56KB     | 0xDFEF                    |
| 64KB     | 0x0, last byte            |
| 92KB     | 0x0                       |
| 128KB    | 0x0                       |
| 256KB    | 0x0, 0x3FFF8, 0x1FFFA     |
| 512KB    | 0x7FFF8                   |
| 1024KB   | 0xFFFF8, 0x7FFF8          |

## Supported Models (Partial List)

From README.md:
- Z125M (2019)
- CRF110F (2019)
- MSX125 (2017, 2014)
- CBR250R (2012, 2014 HRC)
- CBR250RR (2017 HRC)
- CRF250R (2011-2015)
- VTR250 (2015)
- CBR300R (2014 HRC, 2008-2012)
- SH300 (2009)
- XRE 300 (2009-2012)
- CRF450R (2009-2014)
- CB500R (2014)
- CBR600RR (2004-2016)
- CB600F (2010)
- CB650F (2015)
- Transalp700 (2013)
- Shadow 750 (2009)
- NC750X (2015)
- NC750S (2016)
- VFR800F (2015)
- CB1000R (2008-2016)
- CBR1000RR (2004-2017)
- VFR1200F (2010)
- GL1800 (2015)
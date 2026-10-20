# ECU Files Organization

This directory contains organized ECU files (BIN and XDF) for Honda and other motorcycle models.

## Directory Structure

Each ECU model has its own directory named: `{PART_NUMBER}_{MODEL_NAME}`

Example: `38770-K0F-A01_Z125`

## Contains
- `ecu.bin` - Standard ECU binary file (renamed from original)
- `{part_number}.bin` - Original bin file (if different from standard name)
- `*.xdf` - TunerPro definition file for the ECU

## Supported Models

### Honda
| Part Number | Model | Capacity |
|-------------|-------|----------|
| 38770-K0F-A01 | Z 125 | 48KB |
| 38770-K0F-T01 | Z 125 | 48KB |
| 38770-K16-B61 | Scoopy i | 64KB |
| 38770-K16-901 | Scoopy i | 48KB |
| 38770-K20-T01 | Zoomer X | 64KB |
| 38770-KZL-C03 | Spacy i | 48KB |
| 38770-K2E-T02 | CT125 | 64KB |
| 38770-K2J-T01 | Wave 110i | 64KB |
| 38770-K1M-T01 | Dream | 64KB |

### XDF Files
Located directly in `xdfs/` directory for quick access.

## Usage

1. Select ECU file from the appropriate directory
2. Open with ECU editing software that supports TunerPro XDF format
3. Make modifications
4. Write back to ECU using K-Line or USB interface

## Checksum Offsets

Auto-detection is supported for common sizes:
- 48KB: 0x0
- 56KB: 0xDFEF
- 64KB: 0x0
- 92KB: 0x0
- 128KB: 0x0
- 256KB: 0x0 or 0x3FFF8
- 512KB: 0x7FFF8
- 1024KB: 0xFFFF8
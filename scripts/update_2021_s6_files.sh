#!/bin/bash

# Update ECU files with 2021 S6 specific versions

BACKUP_DIR="/media/BACKUP-FAT/ECU-M/Files-ECU"
PROJECT_DIR="/home/xxx/HondaECU-1"

echo "=== Updating ECU Files with 2021 S6 Versions ==="
echo ""

# Update Z 125 (มั้งกี้) - S6 version
dir="$PROJECT_DIR/ecu_files/38770-K0F-T01_Z125"
if [ -d "$dir" ]; then
    cp -v "$BACKUP_DIR/2021 S6/38770-K0F-T01 มั้งกี้/38770-K0F-T01- BG.xdf" "$dir/" 2>/dev/null || true
    cp -v "$BACKUP_DIR/2021 S6/38770-K0F-T01 มั้งกี้/k0F-T01.bin" "$dir/" 2>/dev/null || true
    echo "Updated Z 125 (S6)"
fi

# Update Dream - S6 version
dir="$PROJECT_DIR/ecu_files/38770-K1M-T01_Dream"
if [ -d "$dir" ]; then
    cp -v "$BACKUP_DIR/2021 S6/38770-K1M-T01 ดรีม/38770-K1M-T01-S6-BG.xdf" "$dir/" 2>/dev/null || true
    cp -v "$BACKUP_DIR/2021 S6/38770-K1M-T01 ดรีม/38770-K1M-T01.bin" "$dir/" 2>/dev/null || true
    echo "Updated Dream (S6)"
fi

# Update CT125 - S6 version
dir="$PROJECT_DIR/ecu_files/38770-K2E-T02_CT125"
if [ -d "$dir" ]; then
    cp -v "$BACKUP_DIR/2021 S6/38770-K2E-T02 CT125/38770-K2E-T02 -BG.xdf" "$dir/" 2>/dev/null || true
    cp -v "$BACKUP_DIR/2021 S6/38770-K2E-T02 CT125/38770-K2E-T02.bin" "$dir/" 2>/dev/null || true
    echo "Updated CT125 (S6)"
fi

# Update Wave 110i - S6 version
dir="$PROJECT_DIR/ecu_files/38770-K2J-T01_Wave110i"
if [ -d "$dir" ]; then
    cp -v "$BACKUP_DIR/2021 S6/38770-k2J-T01 110i 2021/38770-K2J-T01.xdf" "$dir/" 2>/dev/null || true
    cp -v "$BACKUP_DIR/2021 S6/38770-k2J-T01 110i 2021/38770-K2J-T01-003.bin" "$dir/" 2>/dev/null || true
    echo "Updated Wave 110i (S6)"
fi

echo ""
echo "=== Update Complete ==="

echo ""
echo "Updated contents:"
find "$PROJECT_DIR/ecu_files" -name "*.xdf" -o -name "*.bin" | sort
#!/bin/bash

# Script to copy and organize all Honda ECU files into the project
# Organizes by part number (PN) with BIN and XDF files together

BACKUP_DIR="/media/BACKUP-FAT/ECU-M/Files-ECU"
PROJECT_DIR="/home/xxx/HondaECU-1"

echo "=== Organizing All Honda ECU Files ==="
echo ""

# Create ecu_files directory if not exists
mkdir -p "$PROJECT_DIR/ecu_files"

# Counter for organized files
count=0

# Function to organize ECU files
organize_ecu() {
    local pn=$1
    local model=$2
    local bin_file=$3
    local xdf_file=$4
    
    local dest_dir="$PROJECT_DIR/ecu_files/${pn}_${model}"
    
    if [ -z "$bin_file" ] && [ -z "$xdf_file" ]; then
        return
    fi
    
    mkdir -p "$dest_dir"
    
    local file_count=0
    
    if [ -n "$bin_file" ] && [ -f "$bin_file" ]; then
        cp -v "$bin_file" "$dest_dir/" 2>/dev/null
        ((file_count++))
    fi
    
    if [ -n "$xdf_file" ] && [ -f "$xdf_file" ]; then
        cp -v "$xdf_file" "$dest_dir/" 2>/dev/null
        ((file_count++))
    fi
    
    if [ $file_count -gt 0 ]; then
        ((count++))
        echo "  Organized: $(basename "$dest_dir")"
    fi
}

# Honda Auto ECU files (RemapKorat)
echo "Processing Honda Auto ECU files..."

# Click 110 / Z125
organize_ecu "38770-K0F-T01" "Z125" \
    "$BACKUP_DIR/Honda ออโต้/Click 110 KVB - S53  48 KB  RemapKorat/KVB-S53.bin" \
    "$PROJECT_DIR/xdfs/38770-K0F-A01.xdf"

# Scoopy i K16
organize_ecu "38770-K16-901" "Scoopy" \
    "$BACKUP_DIR/Honda ออโต้/Scoopy i  K16 - 901  48 KB   RemapKorat/k16-901 ori.bin" \
    "$PROJECT_DIR/xdfs/38770-K16-B01.xdf"

organize_ecu "38770-K16-B61" "Scoopy" \
    "$BACKUP_DIR/Honda ออโต้/Scoopy i K16 - B61 64 KB  RemapKorat/38770-K16-B61.bin" \
    "$PROJECT_DIR/xdfs/38770-K16-B01.xdf"

# Spacy i
organize_ecu "38770-KZL-C03" "Spacy" \
    "$BACKUP_DIR/Honda ออโต้/Spacy i  KZL - C03  48 KB  RemapKorat/Spacy-i  - KZL - C03  48KB.bin" \
    "$PROJECT_DIR/xdfs/38770-K26-B13.xdf"

# Zoomer X
organize_ecu "38770-K20-T01" "ZoomerX" \
    "$BACKUP_DIR/Honda ออโต้/Zoomer x K20 - T01 64 KB    RemapKorat/64K-Zoomer x K20-T01.bin" \
    "$PROJECT_DIR/xdfs/38770-K26-B13.xdf"

# 2021 S6 models
echo ""
echo "Processing 2021 S6 models..."
organize_ecu "38770-K0F-T01" "Z125" \
    "$BACKUP_DIR/2021 S6/38770-K0F-T01 มั้งกี้/k0F-T01.bin" \
    "$PROJECT_DIR/xdfs/38770-K0F-A01.xdf"

organize_ecu "38770-K1M-T01" "Dream" \
    "$BACKUP_DIR/2021 S6/38770-K1M-T01 ดรีม/38770-K1M-T01.bin" \
    "$PROJECT_DIR/xdfs/"  # No XDF for this

organize_ecu "38770-K2E-T02" "CT125" \
    "$BACKUP_DIR/2021 S6/38770-K2E-T02 CT125/38770-K2E-T02.bin" \
    "$PROJECT_DIR/xdfs/"

# Wave 110i / Beetle 110
organize_ecu "38770-K2J-T01" "Wave110i" \
    "$BACKUP_DIR/2021 S6/38770-k2J-T01 110i 2021/38770-K2J-T01-003.bin" \
    "$PROJECT_DIR/xdfs/"

echo ""
echo "=== ECU Files Organization Complete ==="
echo "Total organized directories: $count"

echo ""
echo "Showing organized ECU directories:"
ls -la "$PROJECT_DIR/ecu_files/"
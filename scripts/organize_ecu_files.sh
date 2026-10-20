#!/bin/bash

# Script to organize ECU files from backup into proper project structure
# Creates organized directories with BIN and XDF files together

BACKUP_DIR="/media/BACKUP-FAT/ECU-M/Files-ECU"
PROJECT_DIR="/home/xxx/HondaECU-1"

echo "=== Organizing ECU Files into Project ==="
echo ""

# Create organized structure
mkdir -p "$PROJECT_DIR/ecu_files"

# Function to copy ECU files
copy_ecu() {
    local pn=$1
    local model=$2
    local year=$3
    local src_bin=$4
    local src_xdf=$5
    local dest_dir="$PROJECT_DIR/ecu_files/${pn}_${model}"
    
    mkdir -p "$dest_dir"
    
    if [ -n "$src_bin" ] && [ -f "$src_bin" ]; then
        cp -v "$src_bin" "$dest_dir/"
        # Rename to match pattern
        basename_bin=$(basename "$src_bin")
        if [ "$basename_bin" != "ecu.bin" ]; then
            mv -v "$dest_dir/$basename_bin" "$dest_dir/ecu.bin" 2>/dev/null || true
        fi
    fi
    
    if [ -n "$src_xdf" ] && [ -f "$src_xdf" ]; then
        cp -v "$src_xdf" "$dest_dir/"
    fi
}

# Honda Auto ECU files (RemapKorat)
echo "Processing Honda Auto ECU files..."

for dir in "$BACKUP_DIR/Honda ออโต้"/*; do
    if [ -d "$dir" ]; then
        name=$(basename "$dir")
        # Extract info from directory name
        if [[ "$name" == *"KVB"* ]]; then
            copy_ecu "38770-K0F-T01" "Z125" "48KB" "$dir/KVB-S53.bin" "$PROJECT_DIR/xdfs/38770-K0F-A01.xdf"
        elif [[ "$name" == *"Scoopy i  K16 - 901"* ]]; then
            copy_ecu "38770-K16-901" "Scoopy" "48KB" "$dir/k16-901 ori.bin" "$PROJECT_DIR/xdfs/38770-K16-B01.xdf"
        elif [[ "$name" == *"Scoopy i K16 - B61"* ]]; then
            copy_ecu "38770-K16-B61" "Scoopy" "64KB" "$dir/38770-K16-B61.bin" "$PROJECT_DIR/xdfs/38770-K16-B01.xdf"
        elif [[ "$name" == *"Spacy i"* ]]; then
            copy_ecu "38770-KZL-C03" "Spacy" "48KB" "$dir/Spacy-i  - KZL - C03  48KB.bin" "$PROJECT_DIR/xdfs/38770-K26-B13.xdf"
        elif [[ "$name" == *"Zoomer x"* ]]; then
            copy_ecu "38770-K20-T01" "ZoomerX" "64KB" "$dir/64K-Zoomer x K20-T01.bin" "$PROJECT_DIR/xdfs/38770-K26-B13.xdf"
        fi
    fi
done

echo ""
echo "=== ECU Files Organized ==="
echo ""
echo "Directory structure:"
ls -la "$PROJECT_DIR/ecu_files/"

echo ""
echo "Files organized successfully!"
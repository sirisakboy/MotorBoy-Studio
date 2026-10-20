#!/bin/bash

# Script to organize the main ECU BIN files from "ไฟล์ โม" directory
# Copies original/representative BIN files for each model

BACKUP_DIR="/media/BACKUP-FAT/ECU-M/Files-ECU/ไฟล์ โม"
PROJECT_DIR="/home/xxx/HondaECU-1"

echo "=== Organizing ECU BIN files from 'ไฟล์ โม' ==="
echo ""

# Z 125 / Click - Original
if [ -f "$BACKUP_DIR/38770-K0F-A01 11500RPM.bin" ]; then
    mkdir -p "$PROJECT_DIR/ecu_files/38770-K0F-A01_Z125_Original"
    cp -v "$BACKUP_DIR/38770-K0F-A01 11500RPM.bin" "$PROJECT_DIR/ecu_files/38770-K0F-A01_Z125_Original/ecu.bin"
    echo "Z 125 original: 38770-K0F-A01"
fi

# MSX 125 Grom - K26-911 48KB
if [ -f "$BACKUP_DIR/38770-K26-911  10500RPM.bin" ]; then
    mkdir -p "$PROJECT_DIR/ecu_files/38770-K26-911_MSX48KB"
    cp -v "$BACKUP_DIR/38770-K26-911  10500RPM.bin" "$PROJECT_DIR/ecu_files/38770-K26-911_MSX48KB/ecu.bin"
    echo "MSX 125 Grom 48KB: 38770-K26-911"
fi

# MSX 125 Grom - K26-B02 64KB
if [ -f "$BACKUP_DIR/38770-K26-B02_64kb-10500 RPM.bin" ]; then
    mkdir -p "$PROJECT_DIR/ecu_files/38770-K26-B02_MSX64KB"
    cp -v "$BACKUP_DIR/38770-K26-B02_64kb-10500 RPM.bin" "$PROJECT_DIR/ecu_files/38770-K26-B02_MSX64KB/ecu.bin"
    echo "MSX 125 Grom 64KB: 38770-K26-B02"
fi

# Wave 110i / Click 150 - K58-T81
if [ -f "$BACKUP_DIR/38770-K58-T81.bin" ]; then
    mkdir -p "$PROJECT_DIR/ecu_files/38770-K58-T81_Wave110i"
    cp -v "$BACKUP_DIR/38770-K58-T81.bin" "$PROJECT_DIR/ecu_files/38770-K58-T81_Wave110i/ecu.bin"
    echo "Wave 110i: 38770-K58-T81"
fi

# Wave 110i / Click 150 - K58M TC1
if [ -f "$BACKUP_DIR/38770 K58M TC1 New Wave110i  11500RPM.bin" ]; then
    mkdir -p "$PROJECT_DIR/ecu_files/38770-K58M-TC1_Wave110i"
    cp -v "$BACKUP_DIR/38770 K58M TC1 New Wave110i  11500RPM.bin" "$PROJECT_DIR/ecu_files/38770-K58M-TC1_Wave110i/ecu.bin"
    echo "Wave 110i: 38770-K58M-TC1"
fi

# MSX SF - K26-B02
if [ -f "$BACKUP_DIR/MSX_SF-38770-K26-B02-เดิม รอบ11000.bin" ]; then
    mkdir -p "$PROJECT_DIR/ecu_files/38770-K26-B02_MSXSF"
    cp -v "$BACKUP_DIR/MSX_SF-38770-K26-B02-เดิม รอบ11000.bin" "$PROJECT_DIR/ecu_files/38770-K26-B02_MSXSF/ecu.bin"
    echo "MSX SF: 38770-K26-B02"
fi

# Wave 125i - K73-M62
if [ -f "$BACKUP_DIR/38770-K73-M62  New Wave125i ปลาวาฬ 11500RPM.bin" ]; then
    mkdir -p "$PROJECT_DIR/ecu_files/38770-K73-M62_Wave125i"
    cp -v "$BACKUP_DIR/38770-K73-M62  New Wave125i ปลาวาฬ 11500RPM.bin" "$PROJECT_DIR/ecu_files/38770-K73-M62_Wave125i/ecu.bin"
    echo "Wave 125i: 38770-K73-M62"
fi

# Wave 125i - K73-T32
if [ -f "$BACKUP_DIR/38770-K73-T32_เฟรม78.bin" ]; then
    mkdir -p "$PROJECT_DIR/ecu_files/38770-K73-T32_Wave125i"
    cp -v "$BACKUP_DIR/38770-K73-T32_เฟรม78.bin" "$PROJECT_DIR/ecu_files/38770-K73-T32_Wave125i/ecu.bin"
    echo "Wave 125i: 38770-K73-T32"
fi

# Dream - K1M-T01
if [ -f "$BACKUP_DIR/38770-K1M-T01.bin" ] || [ -f "$BACKUP_DIR/38770 K76 T62 New Dream supercub 11500RPM.bin" ]; then
    # Check if we already have Dream from 2021 S6
    if [ ! -f "$PROJECT_DIR/ecu_files/38770-K1M-T01_Dream/38770-K1M-T01.bin" ]; then
        echo "Dream already has S6 version, skipping"
    fi
fi

echo ""
echo "=== Organization Complete ==="
import struct

def checksum8bit(data):
    """Standard 8-bit checksum (Sum of all bytes % 256)"""
    return sum(data) & 0xFF

def checksum8bitHonda(data):
    """Honda specific 8-bit checksum implementation"""
    s = 0
    for b in data:
        s += b
    return s & 0xFF

def checksum16bit(data):
    """16-bit checksum for newer ECU models"""
    s = 0
    for b in data:
        s += b
    return s & 0xFFFF

def calculate_ecu_checksum(data, method="honda8"):
    """
    Main entry point for checksum calculation.
    Methods: 'standard8', 'honda8', 'standard16'
    """
    if method == "honda8":
        return checksum8bitHonda(data)
    elif method == "standard8":
        return checksum8bit(data)
    elif method == "standard16":
        return checksum16bit(data)
    else:
        raise ValueError("Unknown checksum method")

def fix_checksum(data, checksum_pos, computed_val):
    """Fix checksum at given position in bytearray"""
    if len(data) > checksum_pos:
        data[checksum_pos] = computed_val
    return data

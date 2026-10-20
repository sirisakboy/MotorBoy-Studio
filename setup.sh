#!/bin/bash
set -e

echo "=== HondaECU Setup Script ==="
echo ""

# Check if we're in the project directory
if [ ! -f "requirements.txt" ]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

# Install eculib from local source if available
if [ -f "eculib.tar.gz" ]; then
    echo "Installing eculib from local source..."
    pip install -q ./eculib.tar.gz
elif [ -d "eculib" ]; then
    echo "Installing eculib from extracted source..."
    pip install -q ./eculib
else
    echo "Warning: eculib not found locally. Please download or clone it."
    echo "Expected locations:"
    echo "  - eculib.tar.gz (in project root)"
    echo "  - eculib/ (extracted source directory)"
    read -p "Would you like to continue with PyPI packages? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -q -r requirements.txt

# Verify installation
echo ""
echo "Verifying installation..."
python3 -c "from eculib import KlineAdapter; from eculib.honda import ECUSTATE, checksum8bitHonda, do_validation; print('eculib: OK')"

# Check if wxPython installed
python3 -c "import wx; print(f'wxPython {wx.version()}: OK')" 2>/dev/null || echo "wxPython: Not installed (GUI will not work)"

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To run the application:"
echo "  python -m src"
echo ""
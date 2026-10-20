#!/bin/bash
set -e

echo "=== HondaECU Build Script ==="
echo ""

# Build for current platform
build_executable() {
    echo "Building executable..."
    
    source venv/bin/activate
    
    # Build single file executable
    python -m PyInstaller \
        --noconsole \
        --onefile \
        --clean \
        --add-binary src/images/honda.ico;src/images \
        --add-binary src/images/*;images \
        src/__main__.py \
        --name HondaECU \
        --icon=src/images/honda.ico
    
    echo "Executable built in dist/ directory"
}

build_deb() {
    echo "Building .deb package..."
    
    # Install build dependencies
    sudo apt-get update
    sudo apt-get install -y devscripts debhelper dh-python python3-all python3-setuptools
    
    # Create deb package
    if [ -f debian/control ]; then
        mkdir -p debian/hondaecu/usr/bin
        mkdir -p debian/hondaecu/usr/share/hondaecu
        
        # Copy files
        cp -r src debian/hondaecu/usr/share/hondaecu/
        cp -r xdfs debian/hondaecu/usr/share/hondaecu/
        cp debian/hondaecu/usr/share/hondaecu/__main__.py debian/hondaecu/usr/bin/HondaECU
        chmod +x debian/hondaecu/usr/bin/HondaECU
        
        # Build
        dpkg-deb --build debian/hondaecu hondaecu_$(date +%Y%m%d)-1_amd64.deb
        echo "Deb package built: hondaecu_$(date +%Y%m%d)-1_amd64.deb"
    else
        echo "debian/control not found, skipping .deb build"
    fi
}

case "${1:-exe}" in
    exe)
        build_executable
        ;;
    deb)
        build_deb
        ;;
    all)
        build_executable
        build_deb
        ;;
    *)
        echo "Usage: $0 {exe|deb|all}"
        echo "  exe  - Build executable (default)"
        echo "  deb  - Build .deb package"
        echo "  all  - Build both"
        exit 1
        ;;
esac
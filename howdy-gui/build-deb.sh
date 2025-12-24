#!/bin/bash
#
# Build script for Howdy GUI Manager Debian package
#

set -e

echo "======================================"
echo "Building Howdy GUI Manager .deb package"
echo "======================================"

# Variables
PACKAGE_NAME="howdy-gui-manager"
VERSION="1.0.0"
BUILD_DIR="debian-package"
OUTPUT_DIR="."

# Check if we're in the right directory
if [ ! -d "howdy-gui-manager" ]; then
    echo "Error: howdy-gui-manager directory not found!"
    echo "Please run this script from the howdy project root."
    exit 1
fi

# Clean previous build if exists
echo "Cleaning previous build..."
rm -f "${OUTPUT_DIR}/${PACKAGE_NAME}_${VERSION}_all.deb"

# Copy Python files to package directory
echo "Copying application files..."
mkdir -p "${BUILD_DIR}/usr/share/howdy-gui"
cp -r howdy-gui-manager/howdy_gui "${BUILD_DIR}/usr/share/howdy-gui/"
cp howdy-gui-manager/howdy_gui_manager.py "${BUILD_DIR}/usr/share/howdy-gui/"

# Copy icon if it exists
if [ -f "howdy-gui-manager-icon.png" ]; then
    echo "Copying application icon..."
    cp howdy-gui-manager-icon.png "${BUILD_DIR}/usr/share/icons/hicolor/256x256/apps/howdy-gui-manager.png"
else
    echo "Warning: Icon file not found, skipping..."
fi

# Set permissions for DEBIAN scripts
echo "Setting permissions..."
chmod 755 "${BUILD_DIR}/DEBIAN/postinst"
chmod 755 "${BUILD_DIR}/DEBIAN/prerm"
chmod 755 "${BUILD_DIR}/DEBIAN/postrm"
chmod 755 "${BUILD_DIR}/usr/bin/howdy-gui-manager"

# Build the package
echo "Building .deb package..."
dpkg-deb --build "${BUILD_DIR}" "${OUTPUT_DIR}/${PACKAGE_NAME}_${VERSION}_all.deb"

# Check the package
echo ""
echo "======================================"
echo "Package built successfully!"
echo "======================================"
echo ""
echo "Package info:"
dpkg-deb --info "${OUTPUT_DIR}/${PACKAGE_NAME}_${VERSION}_all.deb"
echo ""
echo "Package contents:"
dpkg-deb --contents "${OUTPUT_DIR}/${PACKAGE_NAME}_${VERSION}_all.deb"
echo ""
echo "======================================"
echo "To install the package, run:"
echo "  sudo dpkg -i ${PACKAGE_NAME}_${VERSION}_all.deb"
echo "  sudo apt-get install -f  # If dependencies are missing"
echo "======================================"

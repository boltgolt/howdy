#!/bin/bash
#
# Howdy GUI Manager - Automated Installer
# This script installs both Howdy and Howdy GUI Manager
#

set -e

echo "=============================================="
echo "  Howdy GUI Manager - Automated Installer"
echo "=============================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Error: This script must be run as root"
    echo "Please run: sudo $0"
    exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
else
    echo "Error: Cannot detect OS version"
    exit 1
fi

echo "Detected OS: $OS $VER"
echo ""

# Function to install Howdy
install_howdy() {
    echo "Step 1/3: Installing Howdy..."
    echo "-------------------------------------------"
    
    if command -v howdy &> /dev/null; then
        echo "✓ Howdy is already installed"
        howdy version 2>/dev/null || echo "  Version: $(dpkg -l | grep howdy | awk '{print $3}')"
    else
        echo "Installing Howdy from PPA..."
        
        # Add Howdy PPA
        if ! grep -q "boltgolt/howdy" /etc/apt/sources.list /etc/apt/sources.list.d/* 2>/dev/null; then
            echo "Adding Howdy PPA repository..."
            add-apt-repository -y ppa:boltgolt/howdy
        fi
        
        # Update and install
        apt-get update
        DEBIAN_FRONTEND=noninteractive apt-get install -y howdy
        
        echo "✓ Howdy installed successfully"
    fi
    echo ""
}

# Function to install dependencies
install_dependencies() {
    echo "Step 2/3: Installing GUI Manager dependencies..."
    echo "-------------------------------------------"
    
    apt-get update
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        python3 \
        python3-pyqt5 \
        python3-opencv
    
    echo "✓ Dependencies installed"
    echo ""
}

# Function to install GUI Manager
install_gui_manager() {
    echo "Step 3/3: Installing Howdy GUI Manager..."
    echo "-------------------------------------------"
    
    # Check if .deb package exists
    if [ -f "howdy-gui-manager_1.0.0_all.deb" ]; then
        dpkg -i howdy-gui-manager_1.0.0_all.deb || apt-get install -f -y
        echo "✓ Howdy GUI Manager installed"
    else
        echo "Error: howdy-gui-manager_1.0.0_all.deb not found"
        echo "Please run this script from the howdy-gui directory"
        exit 1
    fi
    echo ""
}

# Main installation
echo "This script will install:"
echo "  1. Howdy (facial authentication)"
echo "  2. Required dependencies (PyQt5, OpenCV)"
echo "  3. Howdy GUI Manager"
echo ""
read -p "Continue with installation? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled"
    exit 0
fi

echo ""
echo "Starting installation..."
echo ""

# Run installation steps
install_howdy
install_dependencies
install_gui_manager

echo "=============================================="
echo "  Installation Complete!"
echo "=============================================="
echo ""
echo "You can now launch Howdy GUI Manager:"
echo "  • From terminal: sudo howdy-gui-manager"
echo "  • From application menu: Search for 'Howdy GUI Manager'"
echo ""
echo "Next steps:"
echo "  1. Launch the GUI Manager"
echo "  2. Go to Camera Settings and select your camera"
echo "  3. Go to Face Models and add your face"
echo "  4. Test recognition!"
echo ""
echo "For support, visit: https://github.com/boltgolt/howdy"
echo "=============================================="

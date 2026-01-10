#!/bin/bash
set -e

# ----------------------------
# Helpers
# ----------------------------
pause() {
    read -rp "Press Enter to continue..."
}

error_exit() {
    echo
    echo "❌ ERROR: $1"
    exit 1
}

require_root() {
    if [[ $EUID -ne 0 ]]; then
        error_exit "Run this script with sudo"
    fi
}

# ----------------------------
# Detect OS
# ----------------------------
detect_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        DISTRO="$ID"
        VERSION="$VERSION_ID"
    else
        read -rp "Enter distro (ubuntu/fedora/debian/arch): " DISTRO
        read -rp "Enter version: " VERSION
    fi

    DISTRO="$(echo "$DISTRO" | tr 'A-Z' 'a-z')"
    echo "Installing dependencies..."
    sudo apt update
    sudo apt install -y \
        software-properties-common \
        v4l-utils \
        python3-opencv \
        python3-numpy \
        libpam-python \
        libinireader0
}

# ----------------------------
# Install Howdy
# ----------------------------
install_howdy() {
    detect_os

    echo
    echo "Detected: $DISTRO $VERSION"
    echo

    case "$DISTRO" in
        ubuntu|linuxmint)
            MAJOR="${VERSION%%.*}"

            if [[ "$MAJOR" -ge 24 ]]; then
                echo "⚠️ Ubuntu $VERSION detected"
                echo "Using UbuntuHandbook PPA (community-maintained)"
                pause

                apt update
                apt install -y software-properties-common v4l-utils
                add-apt-repository -y ppa:ubuntuhandbook1/howdy
                apt update
                apt install -y howdy
            else
                echo "Using official Howdy PPA"
                apt update
                apt install -y software-properties-common v4l-utils
                add-apt-repository -y ppa:boltgolt/howdy
                apt update
                apt install -y howdy
            fi
            ;;

        fedora)
            echo "Installing Howdy via Fedora COPR"
            dnf copr enable -y principis/howdy
            dnf --refresh install -y howdy v4l-utils
            ;;

        debian)
            echo
            echo "Debian detected."
            echo "Download .deb from:"
            echo "https://github.com/boltgolt/howdy/releases"
            echo
            echo "Then install with:"
            echo "sudo apt install gdebi"
            echo "sudo gdebi howdy_x.y.z_amd64.deb"
            pause
            return
            ;;

        arch)
            echo
            echo "Arch Linux detected."
            echo "Install Howdy from AUR:"
            echo "yay -S howdy"
            echo "or"
            echo "paru -S howdy"
            pause
            return
            ;;

        *)
            error_exit "Unsupported distro: $DISTRO"
            ;;
    esac

    command -v howdy >/dev/null || error_exit "Howdy installation failed"
    echo "✅ Howdy installed successfully"
    pause
}

# ----------------------------
# Camera configuration
# ----------------------------
configure_camera() {
    echo
    echo "Available cameras:"
    v4l2-ctl --list-devices || error_exit "v4l-utils not installed"

    echo
    read -rp "Enter camera device (example: /dev/video0): " DEVICE

    [[ ! -e "$DEVICE" ]] && error_exit "Device not found"

    sed -i "s|^device_path *=.*|device_path = $DEVICE|" /etc/howdy/config.ini

    echo "✅ Camera set to $DEVICE"
    pause
}

# ----------------------------
# Menu actions
# ----------------------------
add_face() {
    echo
    echo "📸 Adding face model"
    echo "Look at the camera. Press Ctrl+C to cancel."
    pause
    howdy add
}

test_face() {
    echo
    echo "🧪 Testing face recognition"
    pause
    howdy test
}

list_models() {
    echo
    howdy list
    pause
}

remove_model() {
    howdy list
    echo
    read -rp "Enter model ID (or 'all'): " ID

    if [[ "$ID" == "all" ]]; then
        howdy clear
    else
        howdy remove "$ID"
    fi
    pause
}

toggle_howdy() {
    echo
    echo "1) Disable Howdy completely"
    echo "2) Disable Howdy for login screen only"
    echo "3) Enable Howdy (restore defaults)"
    echo
    read -rp "Choose: " CHOICE

    case "$CHOICE" in
        1)
            howdy disable
            ;;
        2)
            howdy disable-login
            ;;
        3)
            echo
            echo "To enable Howdy again, edit the config:"
            echo "sudo howdy config"
            echo
            echo "Set:"
            echo "disabled = false"
            echo "disable_login = false"
            ;;
        *)
            echo "Invalid choice"
            ;;
    esac
    pause
}

config_menu() {
    echo
    echo "========== HOWDY CONFIG =========="
    echo "1) Set camera device"
    echo "2) Enable Howdy"
    echo "3) Disable Howdy"
    echo "4) Disable login screen only"
    echo "5) Set timeout"
    echo "6) Set certainty (security level)"
    echo "7) Show current config"
    echo "0) Back"
    echo
    read -rp "Choose option: " CFG

    case "$CFG" in
        1)
            v4l2-ctl --list-devices
            read -rp "Enter device path (e.g. /dev/video0): " DEV
            [[ -e "$DEV" ]] && set_config device_path "$DEV"
            ;;
        2)
            set_config disabled false
            set_config disable_login false
            echo "Howdy enabled"
            ;;
        3)
            set_config disabled true
            echo "Howdy disabled"
            ;;
        4)
            set_config disable_login true
            echo "Login screen disabled"
            ;;
        5)
            read -rp "Enter timeout (seconds): " T
            set_config timeout "$T"
            ;;
        6)
            read -rp "Enter certainty (higher = stricter, e.g. 4.5): " C
            set_config certainty "$C"
            ;;
        7)
            echo
            cat /etc/howdy/config.ini
            ;;
        0)
            return
            ;;
        *)
            echo "Invalid option"
            ;;
    esac
    pause
}

set_config() {
    KEY="$1"
    VALUE="$2"
    CONFIG="/etc/howdy/config.ini"

    if grep -q "^$KEY" "$CONFIG"; then
        sed -i "s|^$KEY *=.*|$KEY = $VALUE|" "$CONFIG"
    else
        echo "$KEY = $VALUE" >> "$CONFIG"
    fi
}



# ----------------------------
# Main Menu
# ----------------------------
main_menu() {
    clear
    echo "======================================"
    echo "     HOWDY FACE AUTH MANAGER (BASH)"
    echo "======================================"
    echo
    echo "1) Install Howdy"
    echo "2) Configure camera"
    echo "3) Add face model"
    echo "4) Test face recognition"
    echo "5) List face models"
    echo "6) Remove / clear models"
    echo "7) Enable / disable Howdy"
    echo "8) Configure Howdy"
    echo "0) Exit"
    echo
    read -rp "Choose an option: " CHOICE

    case "$CHOICE" in
        1) install_howdy ;;
        2) configure_camera ;;
        3) add_face ;;
        4) test_face ;;
        5) list_models ;;
        6) remove_model ;;
        7) toggle_howdy ;;
        8) config_menu ;;
        0) exit 0 ;;
        *) echo "Invalid choice"; pause ;;
    esac
}

# ----------------------------
# Entry point
# ----------------------------
require_root

while true; do
    main_menu
done


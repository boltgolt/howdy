# Howdy Face Authentication Manager

A comprehensive bash-based CLI tool for managing Howdy face authentication on Linux systems.

## Overview

This interactive bash script provides a user-friendly menu-driven interface to install, configure, and manage Howdy facial recognition for Linux authentication. It supports multiple distributions and handles all common Howdy operations through a simple terminal interface.

## Features

### 🎯 Multi-Distribution Support
- **Ubuntu/Linux Mint**
  - Ubuntu 22.04 and earlier: Official PPA (`ppa:boltgolt/howdy`)
  - **Ubuntu 24.04+**: Unofficial PPA (`ppa:ubuntuhandbook1/howdy`) with automatic dependency installation
- **Fedora/RHEL** family via COPR repository
- **Debian** with manual installation instructions
- **Arch Linux** with AUR installation guide
- Automatic OS detection and version-specific installation

### 📸 Face Model Management
- **Add** new face models with interactive camera capture
- **List** all registered face models
- **Remove** individual models by ID
- **Clear** all models at once
- Real-time camera testing

### ⚙️ Configuration Management
- **Camera device selection** with automatic device detection via `v4l2-ctl`
- **Certainty threshold** adjustment (security level)
- **Timeout** configuration
- **Enable/Disable** Howdy globally or for login screen only
- **View** current configuration
- Direct config file editing support

### 🧪 Face Recognition Testing
- Interactive face recognition testing
- Live camera feedback
- Verification of enrolled models

## Requirements

- **Operating System**: Linux (Ubuntu, Fedora, Debian, Arch, or derivatives)
- **Root privileges**: Script must be run with `sudo`
- **Dependencies** (auto-installed on Ubuntu/Debian):
  - `v4l-utils` - Camera device management
  - `python3-opencv` - Computer vision library
  - `python3-numpy` - Numerical processing
  - `libpam-python` - PAM integration
  - `libinireader0` - Configuration file parsing
  - `software-properties-common` - PPA management

## Installation

### 1. Download the Script
```bash
git clone <repository-url>
cd howdy-gui
chmod +x howdy-manager.sh
```

### 2. Run the Script
```bash
sudo ./howdy-manager.sh
```

The script **must** be run with `sudo` as it requires root privileges for Howdy installation and configuration.

## Usage

### Main Menu

When you run the script, you'll see an interactive menu:

```
======================================
     HOWDY FACE AUTH MANAGER (BASH)
======================================

1) Install Howdy
2) Configure camera
3) Add face model
4) Test face recognition
5) List face models
6) Remove / clear models
7) Enable / disable Howdy
8) Configure Howdy
0) Exit
```

### First-Time Setup

1. **Install Howdy** (Option 1)
   - The script will detect your distribution
   - Automatically select the appropriate installation method
   - Install all required dependencies
   - For Ubuntu 24.04+, it will use the community PPA

2. **Configure Camera** (Option 2)
   - View all available camera devices
   - Select your IR camera (e.g., `/dev/video0`)
   - Camera path is saved to Howdy config

3. **Add Face Model** (Option 3)
   - Look at the camera when prompted
   - Your face will be captured and enrolled
   - Model is saved for authentication

4. **Test Recognition** (Option 4)
   - Verify that Howdy can recognize your face
   - Get immediate feedback on recognition success

### Configuration Options

The **Configure Howdy** submenu (Option 8) provides:

1. **Set camera device** - Change the camera used for recognition
2. **Enable Howdy** - Activate face authentication
3. **Disable Howdy** - Turn off face authentication completely
4. **Disable login screen only** - Keep Howdy active but disable for login
5. **Set timeout** - Configure how long to wait for face detection
6. **Set certainty** - Adjust security level (higher = stricter, e.g., 4.5)
7. **Show current config** - View the entire configuration file

### Managing Face Models

- **List models** (Option 5): View all enrolled face models
- **Remove models** (Option 6): 
  - Enter a specific model ID to remove one model
  - Enter `all` to clear all models at once

### Enable/Disable Howdy

Option 7 provides three choices:
1. **Disable completely** - Turn off Howdy for all authentication
2. **Disable login screen only** - Keep Howdy active for sudo/apps but not login
3. **Enable Howdy** - Instructions to re-enable via config file

## Supported Distributions

### Ubuntu Family
- Ubuntu 22.04 and earlier (Official PPA)
- **Ubuntu 24.04, 24.10, 25.04+** (Unofficial PPA)
- Linux Mint
- Pop!_OS
- Elementary OS
- Zorin OS

### Fedora Family
- Fedora (via COPR: `principis/howdy`)
- RHEL
- CentOS
- Rocky Linux
- AlmaLinux

### Debian
- Manual installation via `.deb` package from [Howdy releases](https://github.com/boltgolt/howdy/releases)

### Arch Family
- Arch Linux (via AUR: `yay -S howdy` or `paru -S howdy`)
- Manjaro
- EndeavourOS
- Garuda Linux

## Technical Details

### Script Structure

The script is organized into logical sections:

- **Helpers**: Error handling, root privilege checking, pause functionality
- **OS Detection**: Automatic distribution and version detection
- **Installation**: Distribution-specific Howdy installation logic
- **Camera Configuration**: Device detection and configuration
- **Menu Actions**: Face model management, testing, configuration
- **Main Menu**: Interactive menu loop

### Configuration File

Howdy configuration is stored at `/etc/howdy/config.ini`. The script provides helper functions to safely modify configuration values without manual editing.

### Key Functions

- `detect_os()` - Identifies Linux distribution and version
- `install_howdy()` - Handles distribution-specific installation
- `configure_camera()` - Sets up camera device
- `add_face()` - Enrolls new face model
- `test_face()` - Tests face recognition
- `config_menu()` - Interactive configuration interface
- `set_config()` - Safely updates config file values

## Troubleshooting

### Script won't run
```bash
# Ensure script is executable
chmod +x howdy-manager.sh

# Run with sudo
sudo ./howdy-manager.sh
```

### Howdy installation fails
- **Ubuntu 24.04+**: The script uses an unofficial PPA. Review the warning and press Enter to continue.
- **Debian**: Download the `.deb` package manually from GitHub releases
- **Arch**: Install via AUR using `yay` or `paru`
- Ensure you have an active internet connection

### Camera not detected
```bash
# List available cameras manually
v4l2-ctl --list-devices

# Check if your IR camera is recognized
ls -l /dev/video*
```

### Face recognition not working
- Ensure IR camera is properly connected
- Verify camera device path in config (Option 8 → 7)
- Add multiple face models for different lighting conditions
- Adjust certainty threshold (lower = stricter)
- Test in good lighting conditions

### Permission errors
- Always run the script with `sudo`
- Ensure your user has sudo privileges
- Check that `/etc/howdy/config.ini` is writable

### Configuration not saving
```bash
# Verify config file exists
ls -l /etc/howdy/config.ini

# Check file permissions
sudo chmod 644 /etc/howdy/config.ini
```

## Known Limitations

- Requires root privileges for all operations
- IR camera required for face authentication
- Ubuntu 24.04+ uses unofficial community PPA
- Some distributions require manual Howdy installation
- Configuration changes require script restart to take effect

## Security Considerations

- **Certainty threshold**: Lower values (e.g., 3.5-4.5) provide stricter authentication
- **Multiple models**: Register your face in different conditions (glasses, no glasses, different lighting)
- **Timeout**: Shorter timeouts reduce the window for unauthorized access attempts
- **Disable for login**: Consider disabling Howdy for login screen and using it only for sudo/apps

## Advanced Usage

### Direct Config Editing
```bash
# Edit config file directly
sudo nano /etc/howdy/config.ini

# Or use Howdy's built-in editor
sudo howdy config
```

### Manual Howdy Commands
```bash
# Add face model
sudo howdy add

# List models
sudo howdy list

# Remove specific model
sudo howdy remove <id>

# Clear all models
sudo howdy clear

# Test recognition
sudo howdy test

# Disable Howdy
sudo howdy disable
```

## Project Structure

```
howdy-gui/
├── howdy-manager.sh    # Main bash script (this tool)
└── README.md           # This file
```

## Contributing

Contributions are welcome! Please ensure:
- Code follows bash best practices
- Error handling is comprehensive
- All distributions are properly supported
- Changes are tested on multiple distros

## License

This project is provided as-is for managing Howdy face authentication.

## Credits

- **Howdy**: [boltgolt/howdy](https://github.com/boltgolt/howdy) - The underlying face authentication system
- **Ubuntu 24.04+ PPA**: [UbuntuHandbook](https://ubuntuhandbook.org/) - Community-maintained PPA
- **v4l-utils**: Video4Linux utilities for camera management

## Resources

- [Howdy GitHub Repository](https://github.com/boltgolt/howdy)
- [Howdy Documentation](https://github.com/boltgolt/howdy/wiki)
- [Ubuntu PPA (Official)](https://launchpad.net/~boltgolt/+archive/ubuntu/howdy)
- [Ubuntu PPA (Unofficial 24.04+)](https://launchpad.net/~ubuntuhandbook1/+archive/ubuntu/howdy)
- [Fedora COPR](https://copr.fedorainfracloud.org/coprs/principis/howdy/)
- [AUR Package](https://aur.archlinux.org/packages/howdy)

## Changelog

### Current Version
- Interactive bash-based CLI tool
- Multi-distribution support with automatic detection
- Ubuntu 24.04+ support via unofficial PPA
- Comprehensive configuration management
- Face model management (add, list, remove, clear)
- Camera device configuration with auto-detection
- Enable/disable functionality
- Interactive testing interface

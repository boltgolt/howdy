# Howdy GUI Manager

A modern graphical user interface for managing [Howdy](https://github.com/boltgolt/howdy) facial authentication on Linux.

![Howdy GUI Manager Icon](howdy-gui-manager-icon.png)

## Features

### 📷 Camera Settings
- **Auto-detect** available camera devices
- **Live camera preview** to verify camera functionality
- Configure timeout, certainty threshold, and dark threshold
- Adjust frame resolution and rotation settings
- Test camera before use

### 👤 Face Model Management
- **Add new face models** with custom labels
- **View all registered models** with timestamps
- **Remove individual models** or clear all
- **Test face recognition** in real-time

### ⚙️ Advanced Configuration
- Enable/disable detection and timeout notices
- Configure SSH and lid-closed behavior
- Toggle CNN detector (more accurate, slower)
- Snapshot settings for failed/successful attempts
- Debug options

### 🎨 Modern Interface
- Clean, intuitive tabbed interface
- Real-time camera preview
- Color-coded buttons and status indicators
- Built with PyQt5 for a modern look

## Installation

### From .deb Package

1. Download the latest `.deb` package from releases
2. Install with:
```bash
sudo dpkg -i howdy-gui-manager_1.0.0_all.deb
sudo apt-get install -f  # Install dependencies if needed
```

### Build from Source

1. Clone this repository
2. Run the build script:
```bash
cd /path/to/howdy
chmod +x build-deb.sh
./build-deb.sh
```

3. Install the generated package:
```bash
sudo dpkg -i howdy-gui-manager_1.0.0_all.deb
```

## Dependencies

- Python 3.6 or higher
- PyQt5 (`python3-pyqt5`)
- OpenCV for Python (`python3-opencv`)
- Howdy (must be installed separately)

## Usage

### Launch from Application Menu
Search for "Howdy GUI Manager" in your application launcher.

### Launch from Terminal
```bash
sudo howdy-gui-manager
```

**Note:** The application requires root privileges to modify Howdy configuration files and manage face models.

## Screenshots

### Camera Settings Tab
Configure your camera device, preview the feed, and adjust video settings like timeout and certainty thresholds.

### Face Models Tab
Manage your face models - add new ones, remove old ones, and test recognition.

### Advanced Settings Tab
Fine-tune Howdy behavior with advanced options for SSH sessions, lid detection, CNN mode, and more.

## Configuration

All settings are saved to `/etc/howdy/config.ini`. The application automatically creates backups before making changes.

## Troubleshooting

### Permission Errors
Make sure you're running the application with sudo:
```bash
sudo howdy-gui-manager
```

### Camera Not Detected
- Check if your camera is recognized: `ls /dev/video*`
- Verify Howdy can access the camera: `sudo howdy test`
- Try refreshing the device list in the Camera Settings tab

### Face Model Not Working
- Ensure good lighting when adding face models
- Adjust the dark threshold if frames are being skipped
- Test recognition from the Face Models tab

## Development

### Project Structure
```
howdy-gui-manager/
├── howdy_gui/
│   ├── __init__.py
│   ├── camera_utils.py      # Camera detection and testing
│   ├── config_manager.py    # Configuration file management
│   └── model_manager.py     # Face model operations
└── howdy_gui_manager.py     # Main GUI application

debian-package/
├── DEBIAN/
│   ├── control              # Package metadata
│   ├── postinst            # Post-installation script
│   ├── prerm               # Pre-removal script
│   └── postrm              # Post-removal script
└── usr/
    ├── bin/
    │   └── howdy-gui-manager
    └── share/
        ├── applications/
        │   └── howdy-gui-manager.desktop
        └── icons/
```

## License

This project follows the same license as Howdy (MIT License).

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Credits

- Built for [Howdy](https://github.com/boltgolt/howdy) by boltgolt
- GUI developed with PyQt5
- Icons and design inspired by modern Linux desktop applications

## Support

For issues related to:
- **Howdy itself**: Visit the [Howdy GitHub repository](https://github.com/boltgolt/howdy)
- **GUI Manager**: Open an issue in this repository

---

**Note:** Howdy GUI Manager is a convenience tool and should not be considered a security enhancement. Always maintain password authentication as a backup method.

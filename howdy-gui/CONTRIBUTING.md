# Howdy GUI Manager - Contribution Package

A modern graphical user interface for managing [Howdy](https://github.com/boltgolt/howdy) facial authentication on Linux.

![Howdy GUI Manager](howdy-gui-manager-icon.png)

## 📋 Overview

This package contains a complete GUI manager for Howdy, providing an intuitive interface for:
- Camera device selection and configuration
- Face model management (add, remove, list, test)
- Live camera preview
- All Howdy configuration settings
- Real-time face recognition testing

## 🎯 Purpose

This contribution aims to make Howdy more accessible to users who prefer graphical interfaces over command-line tools. It complements the existing `howdy-gtk` authentication UI with a full configuration and management interface.

## 📦 Package Contents

```
howdy-gui-contribution/
├── howdy-gui-manager/              # Main application source
│   ├── howdy_gui/                  # Python package
│   │   ├── __init__.py
│   │   ├── camera_utils.py         # Camera detection & testing
│   │   ├── config_manager.py       # Config file management
│   │   └── model_manager.py        # Face model operations
│   ├── howdy_gui_manager.py        # Main GUI application
│   └── README.md                   # User documentation
├── debian-package/                 # Debian package structure
│   ├── DEBIAN/
│   │   ├── control                 # Package metadata
│   │   ├── postinst               # Post-install script
│   │   ├── prerm                  # Pre-removal script
│   │   └── postrm                 # Post-removal script
│   └── usr/
│       ├── bin/
│       │   └── howdy-gui-manager   # Launcher script
│       └── share/
│           ├── applications/
│           │   └── howdy-gui-manager.desktop
│           └── icons/
├── build-deb.sh                    # Build script for .deb package
├── howdy-gui-manager-icon.png      # Application icon (256x256)
├── howdy-gui-manager_1.0.0_all.deb # Pre-built package
├── CONTRIBUTING.md                 # This file
└── SCREENSHOTS.md                  # Screenshots (to be added)
```

## 🚀 Quick Start

### Installation

```bash
# Install the pre-built package
sudo dpkg -i howdy-gui-manager_1.0.0_all.deb
sudo apt-get install -f

# Or build from source
./build-deb.sh
sudo dpkg -i howdy-gui-manager_1.0.0_all.deb
```

### Usage

```bash
# Launch from terminal
sudo howdy-gui-manager

# Or search for "Howdy GUI Manager" in your application menu
```

## 🛠️ Technical Details

### Technology Stack
- **Language:** Python 3.6+
- **GUI Framework:** PyQt5
- **Camera:** OpenCV (cv2)
- **Configuration:** ConfigParser (compatible with Howdy's config.ini)

### Dependencies
- `python3` (>= 3.6)
- `python3-pyqt5`
- `python3-opencv`
- `howdy` (must be installed)

### Architecture

**Camera Utilities** (`camera_utils.py`)
- Auto-detects video devices from `/dev/video*` and `/dev/v4l/by-path/`
- Tests camera accessibility
- Retrieves camera capabilities (resolution, FPS)

**Configuration Manager** (`config_manager.py`)
- Safe read/write to `/etc/howdy/config.ini`
- Automatic backups before changes
- Type-safe getters (int, float, boolean)

**Model Manager** (`model_manager.py`)
- Interfaces with Howdy CLI commands
- Parses JSON model files
- Manages face model lifecycle

**Main GUI** (`howdy_gui_manager.py`)
- Tabbed interface with three sections
- Live camera preview widget
- Real-time configuration updates
- Progress dialogs for long operations

## 🎨 Features

### Camera Settings Tab
- ✅ Auto-detect all available cameras
- ✅ Live camera preview (30 FPS)
- ✅ Test camera functionality
- ✅ Configure timeout (1-30 seconds)
- ✅ Adjust certainty threshold (1.0-10.0)
- ✅ Set dark threshold (0-100%)
- ✅ Frame resolution settings
- ✅ Rotation mode selector

### Face Models Tab
- ✅ List all registered models with metadata
- ✅ Add new models with custom labels
- ✅ Remove individual models
- ✅ Clear all models
- ✅ Test face recognition
- ✅ Display test results

### Advanced Settings Tab
- ✅ Core settings (detection notice, timeout notice)
- ✅ SSH and lid-closed behavior
- ✅ CNN detector toggle
- ✅ Snapshot settings (save failed/successful)
- ✅ Debug options

## 🤝 Contributing to Howdy

### Integration Suggestions

This GUI manager could be integrated into the main Howdy project in several ways:

**Option 1: Separate Package**
- Keep as `howdy-gui-manager` package
- Listed as optional companion to Howdy
- Independent release cycle

**Option 2: Integrated Package**
- Include in main Howdy repository
- Build alongside existing `howdy-gtk`
- Shared release cycle

**Option 3: Meson Integration**
- Add to existing `meson.build` structure
- Install alongside Howdy core
- Use existing paths and configuration

### Proposed Changes for Integration

If integrating into main Howdy repository:

1. **Directory Structure:**
   ```
   howdy/
   ├── howdy-gtk/          # Existing auth UI
   ├── howdy-gui-manager/  # New config GUI
   └── meson.build         # Updated to include GUI manager
   ```

2. **Meson Build Integration:**
   - Add `subdir('howdy-gui-manager')` to main `meson.build`
   - Create `howdy-gui-manager/meson.build` for installation
   - Use existing `paths_factory.py` for path management

3. **Shared Resources:**
   - Use existing icon/branding if available
   - Share translation infrastructure
   - Reuse PolicyKit configuration

### Code Quality

- ✅ Type hints for function parameters
- ✅ Docstrings for all classes and methods
- ✅ Error handling with user-friendly messages
- ✅ Graceful degradation (works without camera)
- ✅ Resource cleanup (camera release on exit)
- ✅ PEP 8 compliant code style

### Testing Checklist

- ✅ Camera detection on multiple devices
- ✅ Configuration save/load
- ✅ Face model add/remove
- ✅ Recognition testing
- ✅ Package installation/removal
- ⬜ Multi-user support (needs testing)
- ⬜ Non-English locales (needs i18n)

## 📝 Future Enhancements

### Planned Features
- [ ] Internationalization (i18n) support
- [ ] Dark mode theme
- [ ] Keyboard shortcuts
- [ ] Configuration import/export
- [ ] Multiple camera profiles
- [ ] Recognition statistics/history

### Known Limitations
- Requires root/sudo for all operations
- No multi-user model management in single session
- Camera preview limited to 640x480
- No undo functionality for model deletion

## 📸 Screenshots

*To be added: Screenshots of each tab and key features*

## 📄 License

This project follows the same license as Howdy (MIT License).

## 🙏 Acknowledgments

- Built for [Howdy](https://github.com/boltgolt/howdy) by boltgolt
- Inspired by the existing `howdy-gtk` authentication UI
- Uses PyQt5 for modern desktop integration

## 📧 Contact

For questions or suggestions about this contribution:
- Open an issue in the Howdy repository
- Tag with `gui-manager` label

---

**Ready for Review:** This package is ready for review and potential integration into the main Howdy project. Feedback and suggestions are welcome!

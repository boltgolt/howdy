# Installation Guide

## Prerequisites

Before installing Howdy GUI Manager, ensure you have:

1. **Howdy installed and working**
   ```bash
   which howdy
   # Should return: /usr/bin/howdy or similar
   ```

2. **Required dependencies** (will be installed automatically):
   - Python 3.6 or higher
   - PyQt5
   - OpenCV for Python

## Installation Methods

### Method 1: Install Pre-built Package (Recommended)

```bash
cd howdy-gui-contribution
sudo dpkg -i howdy-gui-manager_1.0.0_all.deb
```

If you get dependency errors:
```bash
sudo apt-get install -f
```

### Method 2: Build and Install

```bash
cd howdy-gui-contribution
./build-deb.sh
sudo dpkg -i howdy-gui-manager_1.0.0_all.deb
```

## Verification

After installation, verify it works:

```bash
# Check if installed
dpkg -l | grep howdy-gui-manager

# Launch the application
sudo howdy-gui-manager
```

## Uninstallation

To remove Howdy GUI Manager:

```bash
sudo apt remove howdy-gui-manager
```

This will not affect your Howdy installation or existing face models.

## Troubleshooting

### "Command not found"
Make sure `/usr/bin` is in your PATH:
```bash
echo $PATH | grep /usr/bin
```

### "Permission denied"
Always run with sudo:
```bash
sudo howdy-gui-manager
```

### "Cannot open camera"
Check camera permissions and that Howdy can access it:
```bash
ls -l /dev/video*
sudo howdy test
```

### Missing dependencies
Manually install dependencies:
```bash
sudo apt-get install python3 python3-pyqt5 python3-opencv
```

## First Run

1. Launch: `sudo howdy-gui-manager`
2. Go to **Camera Settings** tab
3. Select your camera from the dropdown
4. Click **Test Camera** to verify it works
5. Go to **Face Models** tab
6. Click **Add New Model** to register your face
7. Test recognition with **Test Recognition** button

Enjoy using Howdy GUI Manager!

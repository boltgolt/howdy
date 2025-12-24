# Howdy GUI Manager

A graphical user interface for managing [Howdy](https://github.com/boltgolt/howdy) facial authentication on Linux.

![Howdy GUI Manager](howdy-gui-manager-icon.png)

## 🚀 One-Command Installation

This package includes an **automated installer** that installs both Howdy and the GUI Manager:

```bash
cd howdy-gui
sudo ./install.sh
```

**That's it!** The installer will:
1. ✅ Install Howdy from official PPA
2. ✅ Install all dependencies (PyQt5, OpenCV)
3. ✅ Install Howdy GUI Manager
4. ✅ Set up desktop integration

**No need to download two separate packages!**

---

## ✨ Features

### 📷 Camera Settings
- Auto-detect available cameras
- Live camera preview (30 FPS)
- Configure timeout, certainty, and dark threshold
- Test camera functionality

### 👤 Face Model Management
- Add new face models with custom labels
- View all registered models with timestamps
- Remove individual or all models
- Test face recognition in real-time

### ⚙️ Advanced Configuration
- All Howdy settings in one interface
- SSH and lid-closed behavior
- CNN detector toggle
- Snapshot settings
- Debug options

---

## 📖 Usage

### Launch the Application

**From Application Menu:**
Search for "Howdy GUI Manager"

**From Terminal:**
```bash
sudo howdy-gui-manager
```

### First Time Setup

1. **Camera Settings Tab**
   - Select your camera from dropdown
   - Click "Test Camera"
   - Adjust settings as needed

2. **Face Models Tab**
   - Click "Add New Model"
   - Look at the camera
   - Test recognition

3. **Advanced Tab**
   - Configure additional settings
   - Save changes

---

## 🛠️ Manual Installation (Advanced)

If you prefer manual installation:

### Step 1: Install Howdy
```bash
sudo add-apt-repository ppa:boltgolt/howdy
sudo apt update
sudo apt install howdy
```

### Step 2: Install Dependencies
```bash
sudo apt install python3-pyqt5 python3-opencv
```

### Step 3: Install GUI Manager
```bash
sudo dpkg -i howdy-gui-manager_1.0.0_all.deb
```

---

## 🔧 Building from Source

```bash
./build-deb.sh
```

This creates `howdy-gui-manager_1.0.0_all.deb`

---

## ❓ Troubleshooting

### "Cannot open camera"
1. Check: `ls -l /dev/video*`
2. Test: `sudo howdy test`
3. Try different camera in GUI

### "Permission denied"
Always run with sudo:
```bash
sudo howdy-gui-manager
```

### Dependencies missing
```bash
sudo apt-get install -f
```

---

## 📦 Package Contents

```
howdy-gui/
├── install.sh                      # Automated installer ⭐
├── howdy-gui-manager_1.0.0_all.deb # GUI package
├── howdy-gui-manager/              # Source code
├── debian-package/                 # Package structure
└── build-deb.sh                    # Build script
```

---

## 🗑️ Uninstallation

```bash
# Remove GUI Manager
sudo apt remove howdy-gui-manager

# Remove Howdy (optional)
sudo apt remove howdy
```

---

## 📋 System Requirements

- Ubuntu 18.04+ or Debian-based distro
- Python 3.6+
- IR camera (recommended) or webcam
- 50 MB disk space

---

## 📄 License

MIT License - Same as Howdy

---

## 🙏 Credits

- Built for [Howdy](https://github.com/boltgolt/howdy)
- GUI: PyQt5
- Camera: OpenCV

---

**Enjoy password-free authentication!** 🎉

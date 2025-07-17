### **`GSTREAMER_INTEGRATION.md`**

# Enabling Modern Camera Support (libcamera / IPU6) with GStreamer

This guide explains how to use Howdy's GStreamer integration feature. If you have a modern laptop (roughly 2020 or newer) and your built-in camera does not work with Howdy out of the box, you are in the right place.

## The Problem: Modern Cameras vs. Older Applications

Many new cameras, especially the Infrared (IR) cameras used for facial recognition (like those compatible with Windows Hello), no longer present themselves as simple webcams. They use a modern driver stack called `libcamera`.

Howdy, by default, uses a library (OpenCV) that expects a standard V4L2 video device (`/dev/videoX`). The `libcamera` stack does not provide a stable device in this format, causing Howdy to fail with "camera not found" or "failed to read frame" errors.

## The Solution: An On-Demand GStreamer Bridge

This feature solves the problem by using **GStreamer**, a powerful multimedia framework, to create a real-time "translator." Howdy will automatically start this translator only when it needs to scan your face, and shut it down immediately afterward.

**This means your camera light will only be on for the few seconds it takes to authenticate.**

This process works in three steps:
1.  **`v4l2loopback`**: A kernel module creates a "virtual" webcam device that Howdy can understand.
2.  **GStreamer Pipeline**: A command you define captures the real video from your modern `libcamera` device.
3.  **Howdy Integration**: Howdy launches the pipeline, which sends the video to the virtual webcam. Howdy reads from this virtual webcam, and then terminates the pipeline when finished.

---

## Step-by-Step Setup Guide

### Step 1: Install Prerequisites

You will need `GStreamer`, the `libcamera` plugin for it, and the `v4l2loopback` kernel module.

*   **Ubuntu / Debian:**
    ```bash
    sudo apt install gstreamer1.0-tools gstreamer1.0-libcamera v4l2loopback-dkms
    ```

*   **Fedora / openSUSE / RPM-based:**
    ```bash
    sudo dnf install gstreamer1.0 gstreamer1.0-plugins-good libcamera-gstreamer v4l2loopback-kmp-default
    # On openSUSE, you might need 'zypper' instead of 'dnf'
    ```

*   **Arch Linux:**
    ```bash
    sudo pacman -S gstreamer gst-plugins-good gst-plugin-libcamera v4l2loopback-dkms
    ```
*(Note: `v4l2loopback-dkms` is highly recommended as it will automatically rebuild the module when your kernel updates.)*

### Step 2: Create a Persistent Virtual Camera

We need to tell the system to create our virtual device (`/dev/video0`) every time it boots.

1.  **Load the module now for testing:**
    ```bash
    sudo modprobe v4l2loopback video_nr=0 card_label="Howdy Virtual Camera" exclusive_caps=1
    ```
2.  **Make it persistent across reboots:**
    ```bash
    echo "v4l2loopback" | sudo tee /etc/modules-load.d/v4l2loopback.conf
    echo "options v4l2loopback video_nr=0 card_label='Howdy Virtual Camera' exclusive_caps=1" | sudo tee /etc/modprobe.d/v4l2loopback.conf
    ```

### Step 3: Configure User Permissions

Your user account needs permission to access video devices.

```bash
sudo usermod -aG video $USER
```
**Important:** You must **log out and log back in** (or reboot) for this change to take effect. You can verify you are in the group by running the `groups` command.

### Step 4: Configure Howdy

Finally, tell Howdy to use your new on-demand bridge.

1.  Run `sudo howdy config` to open the configuration file.
2.  Find the `[video]` section and add/modify the following four lines:

    ```ini
    # --- GStreamer Integration Settings ---

    # Set to true to enable the GStreamer bridge feature.
    use_gstreamer = true

    # The full GStreamer pipeline command to run.
    gstreamer_pipeline = gst-launch-1.0 libcamerasrc ! video/x-raw,width=640,height=480 ! videoconvert ! video/x-raw,format=YUY2 ! v4l2sink device=/dev/video0

    # The number of seconds to wait for the pipeline to initialize. Increase if scans fail.
    gstreamer_startup_delay = 2

    # The virtual device path that Howdy should read from. Must match the device in the pipeline.
    device_path = /dev/video0
    ```

---

## Verification and Troubleshooting

1.  **Test the Pipeline Manually:** The best way to debug is to run your pipeline directly in the terminal. It should run without errors.
    ```bash
    gst-launch-1.0 libcamerasrc ! video/x-raw,width=640,height=480 ! videoconvert ! video/x-raw,format=YUY2 ! v4l2sink device=/dev/video0
    ```
    While that is running, open a second terminal and test the output with `ffplay /dev/video0`.

2.  **Test Howdy:** Run `howdy test`. The camera light should turn on, a test window should appear, and the light should turn off when you close it.

3.  **Authentication Fails:** If the light flashes but authentication doesn't work, try increasing `gstreamer_startup_delay` to `3` or `4` in the config file.

4.  **Find Your Camera:** If your camera isn't found, use `libcamera-hello --list-cameras` to see if the system detects it at all.

This feature was developed to address issues with modern camera stacks (#796). Community feedback on different hardware is welcome.
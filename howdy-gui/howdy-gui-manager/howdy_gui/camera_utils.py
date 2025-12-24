"""
Camera utilities for Howdy GUI Manager
Handles camera detection, testing, and device enumeration
"""

import os
import glob
import cv2
from typing import List, Tuple, Optional


class CameraUtils:
    """Utility class for camera operations"""
    
    @staticmethod
    def detect_video_devices() -> List[Tuple[str, str]]:
        """
        Detect all available video devices
        Returns: List of tuples (device_path, device_name)
        """
        devices = []
        
        # Check /dev/video* devices
        video_devices = glob.glob('/dev/video*')
        for device in sorted(video_devices):
            try:
                # Try to open the device to verify it works
                cap = cv2.VideoCapture(device)
                if cap.isOpened():
                    # Get device name from v4l2
                    device_name = CameraUtils._get_device_name(device)
                    devices.append((device, device_name))
                    cap.release()
            except Exception:
                pass
        
        # Check /dev/v4l/by-path/ for more descriptive paths
        by_path_devices = glob.glob('/dev/v4l/by-path/*')
        for device in by_path_devices:
            if os.path.islink(device):
                real_path = os.path.realpath(device)
                device_name = os.path.basename(device)
                # Only add if not already in list
                if not any(d[0] == real_path for d in devices):
                    devices.append((device, device_name))
        
        return devices
    
    @staticmethod
    def _get_device_name(device_path: str) -> str:
        """Get human-readable device name"""
        try:
            # Try to read from v4l2 sysfs
            video_num = device_path.replace('/dev/video', '')
            name_path = f'/sys/class/video4linux/video{video_num}/name'
            if os.path.exists(name_path):
                with open(name_path, 'r') as f:
                    return f.read().strip()
        except Exception:
            pass
        
        return os.path.basename(device_path)
    
    @staticmethod
    def test_camera(device_path: str) -> Tuple[bool, str]:
        """
        Test if a camera device is accessible
        Returns: (success, message)
        """
        try:
            cap = cv2.VideoCapture(device_path)
            if not cap.isOpened():
                return False, f"Cannot open camera at {device_path}"
            
            # Try to read a frame
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                return False, "Camera opened but cannot read frames"
            
            return True, "Camera is working correctly"
        except Exception as e:
            return False, f"Error testing camera: {str(e)}"
    
    @staticmethod
    def get_camera_capabilities(device_path: str) -> dict:
        """Get camera capabilities (resolution, FPS, etc.)"""
        capabilities = {}
        
        try:
            cap = cv2.VideoCapture(device_path)
            if cap.isOpened():
                capabilities['width'] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                capabilities['height'] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                capabilities['fps'] = int(cap.get(cv2.CAP_PROP_FPS))
                capabilities['backend'] = cap.getBackendName()
                cap.release()
        except Exception:
            pass
        
        return capabilities

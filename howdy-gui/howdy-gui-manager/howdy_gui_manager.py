#!/usr/bin/env python3
"""
Howdy GUI Manager - Main Application
A graphical interface for managing Howdy facial authentication
"""

import sys
import os
import getpass
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QComboBox, QSlider, QSpinBox,
    QDoubleSpinBox, QCheckBox, QLineEdit, QTextEdit, QListWidget,
    QGroupBox, QFormLayout, QMessageBox, QDialog, QDialogButtonBox,
    QListWidgetItem, QProgressDialog
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QFont
import cv2
import numpy as np

# Import our custom modules
from howdy_gui.camera_utils import CameraUtils
from howdy_gui.config_manager import ConfigManager
from howdy_gui.model_manager import ModelManager


class CameraPreviewWidget(QLabel):
    """Widget to display live camera preview"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(640, 480)
        self.setStyleSheet("border: 2px solid #ccc; background-color: #000;")
        self.setAlignment(Qt.AlignCenter)
        self.setText("No camera feed")
        
        self.camera = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
    
    def start_preview(self, device_path):
        """Start camera preview"""
        self.stop_preview()
        
        try:
            self.camera = cv2.VideoCapture(device_path)
            if self.camera.isOpened():
                self.timer.start(30)  # 30ms = ~33 FPS
                return True
        except Exception as e:
            print(f"Error starting preview: {e}")
        
        return False
    
    def stop_preview(self):
        """Stop camera preview"""
        self.timer.stop()
        if self.camera:
            self.camera.release()
            self.camera = None
        self.setText("No camera feed")
    
    def update_frame(self):
        """Update the displayed frame"""
        if self.camera and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                # Convert BGR to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Resize to fit widget
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                
                # Scale to fit
                scaled_frame = cv2.resize(frame, (640, 480))
                h, w, ch = scaled_frame.shape
                bytes_per_line = ch * w
                
                qt_image = QImage(scaled_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.setPixmap(QPixmap.fromImage(qt_image))


class CameraSettingsTab(QWidget):
    """Tab for camera and video settings"""
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.camera_utils = CameraUtils()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Camera selection group
        camera_group = QGroupBox("Camera Selection")
        camera_layout = QFormLayout()
        
        self.device_combo = QComboBox()
        self.refresh_devices()
        camera_layout.addRow("Camera Device:", self.device_combo)
        
        refresh_btn = QPushButton("Refresh Devices")
        refresh_btn.clicked.connect(self.refresh_devices)
        camera_layout.addRow("", refresh_btn)
        
        test_btn = QPushButton("Test Camera")
        test_btn.clicked.connect(self.test_camera)
        camera_layout.addRow("", test_btn)
        
        camera_group.setLayout(camera_layout)
        layout.addWidget(camera_group)
        
        # Preview
        preview_group = QGroupBox("Camera Preview")
        preview_layout = QVBoxLayout()
        
        self.preview_widget = CameraPreviewWidget()
        preview_layout.addWidget(self.preview_widget)
        
        preview_controls = QHBoxLayout()
        self.start_preview_btn = QPushButton("Start Preview")
        self.start_preview_btn.clicked.connect(self.toggle_preview)
        preview_controls.addWidget(self.start_preview_btn)
        preview_layout.addLayout(preview_controls)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Video settings group
        video_group = QGroupBox("Video Settings")
        video_layout = QFormLayout()
        
        # Timeout
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 30)
        self.timeout_spin.setValue(self.config.get_int('video', 'timeout', 4))
        self.timeout_spin.setSuffix(" seconds")
        video_layout.addRow("Timeout:", self.timeout_spin)
        
        # Certainty
        self.certainty_spin = QDoubleSpinBox()
        self.certainty_spin.setRange(1.0, 10.0)
        self.certainty_spin.setSingleStep(0.1)
        self.certainty_spin.setValue(self.config.get_float('video', 'certainty', 3.5))
        video_layout.addRow("Certainty (lower = stricter):", self.certainty_spin)
        
        # Dark threshold
        self.dark_threshold_spin = QSpinBox()
        self.dark_threshold_spin.setRange(0, 100)
        self.dark_threshold_spin.setValue(self.config.get_int('video', 'dark_threshold', 60))
        self.dark_threshold_spin.setSuffix(" %")
        video_layout.addRow("Dark Threshold:", self.dark_threshold_spin)
        
        # Max height
        self.max_height_spin = QSpinBox()
        self.max_height_spin.setRange(120, 1080)
        self.max_height_spin.setValue(self.config.get_int('video', 'max_height', 320))
        self.max_height_spin.setSuffix(" px")
        video_layout.addRow("Max Frame Height:", self.max_height_spin)
        
        # Rotation
        self.rotate_combo = QComboBox()
        self.rotate_combo.addItems(["Landscape only (0)", "Landscape + Portrait (1)", "Portrait only (2)"])
        self.rotate_combo.setCurrentIndex(self.config.get_int('video', 'rotate', 0))
        video_layout.addRow("Rotation Mode:", self.rotate_combo)
        
        video_group.setLayout(video_layout)
        layout.addWidget(video_group)
        
        # Save button
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-weight: bold;")
        layout.addWidget(save_btn)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def refresh_devices(self):
        """Refresh the list of available cameras"""
        self.device_combo.clear()
        devices = self.camera_utils.detect_video_devices()
        
        if not devices:
            self.device_combo.addItem("No cameras detected", "none")
        else:
            for device_path, device_name in devices:
                self.device_combo.addItem(f"{device_name} ({device_path})", device_path)
        
        # Set current device from config
        current_device = self.config.get('video', 'device_path', 'none')
        index = self.device_combo.findData(current_device)
        if index >= 0:
            self.device_combo.setCurrentIndex(index)
    
    def test_camera(self):
        """Test the selected camera"""
        device_path = self.device_combo.currentData()
        if device_path == "none":
            QMessageBox.warning(self, "No Camera", "Please select a camera device first.")
            return
        
        success, message = self.camera_utils.test_camera(device_path)
        if success:
            QMessageBox.information(self, "Camera Test", message)
        else:
            QMessageBox.warning(self, "Camera Test Failed", message)
    
    def toggle_preview(self):
        """Toggle camera preview on/off"""
        if self.preview_widget.camera is None:
            device_path = self.device_combo.currentData()
            if device_path == "none":
                QMessageBox.warning(self, "No Camera", "Please select a camera device first.")
                return
            
            if self.preview_widget.start_preview(device_path):
                self.start_preview_btn.setText("Stop Preview")
            else:
                QMessageBox.warning(self, "Preview Failed", "Could not start camera preview.")
        else:
            self.preview_widget.stop_preview()
            self.start_preview_btn.setText("Start Preview")
    
    def save_settings(self):
        """Save all settings to config file"""
        try:
            # Save device path
            device_path = self.device_combo.currentData()
            self.config.set('video', 'device_path', device_path)
            
            # Save video settings
            self.config.set('video', 'timeout', str(self.timeout_spin.value()))
            self.config.set('video', 'certainty', str(self.certainty_spin.value()))
            self.config.set('video', 'dark_threshold', str(self.dark_threshold_spin.value()))
            self.config.set('video', 'max_height', str(self.max_height_spin.value()))
            self.config.set('video', 'rotate', str(self.rotate_combo.currentIndex()))
            
            # Save to file
            if self.config.save():
                QMessageBox.information(self, "Success", "Settings saved successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to save settings. Check permissions.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving settings: {str(e)}")


class FaceModelsTab(QWidget):
    """Tab for managing face models"""
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.model_manager = ModelManager()
        self.username = getpass.getuser()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # User info
        user_label = QLabel(f"<b>Managing face models for user:</b> {self.username}")
        user_label.setStyleSheet("font-size: 14px; padding: 10px;")
        layout.addWidget(user_label)
        
        # Models list
        models_group = QGroupBox("Registered Face Models")
        models_layout = QVBoxLayout()
        
        self.models_list = QListWidget()
        self.refresh_models()
        models_layout.addWidget(self.models_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_models)
        btn_layout.addWidget(refresh_btn)
        
        add_btn = QPushButton("Add New Model")
        add_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        add_btn.clicked.connect(self.add_model)
        btn_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("Remove Selected")
        remove_btn.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        remove_btn.clicked.connect(self.remove_model)
        btn_layout.addWidget(remove_btn)
        
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear_models)
        btn_layout.addWidget(clear_btn)
        
        models_layout.addLayout(btn_layout)
        models_group.setLayout(models_layout)
        layout.addWidget(models_group)
        
        # Test section
        test_group = QGroupBox("Test Face Recognition")
        test_layout = QVBoxLayout()
        
        test_info = QLabel("Click the button below to test if your face is recognized correctly.")
        test_layout.addWidget(test_info)
        
        test_btn = QPushButton("Test Recognition")
        test_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 10px; font-weight: bold;")
        test_btn.clicked.connect(self.test_recognition)
        test_layout.addWidget(test_btn)
        
        self.test_output = QTextEdit()
        self.test_output.setReadOnly(True)
        self.test_output.setMaximumHeight(150)
        test_layout.addWidget(self.test_output)
        
        test_group.setLayout(test_layout)
        layout.addWidget(test_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def refresh_models(self):
        """Refresh the list of face models"""
        self.models_list.clear()
        models = self.model_manager.get_user_models(self.username)
        
        if not models:
            item = QListWidgetItem("No face models found. Click 'Add New Model' to create one.")
            item.setFlags(Qt.NoItemFlags)
            self.models_list.addItem(item)
        else:
            for model in models:
                info = self.model_manager.format_model_info(model)
                item = QListWidgetItem(info)
                item.setData(Qt.UserRole, model['id'])
                self.models_list.addItem(item)
    
    def add_model(self):
        """Add a new face model"""
        # Ask for label
        label, ok = QLineEdit.getText(self, "Add Face Model", "Enter a label for this model (optional):")
        
        if not ok:
            return
        
        # Show progress dialog
        progress = QProgressDialog("Adding face model...\nPlease look at the camera.", "Cancel", 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        QApplication.processEvents()
        
        # Add the model
        success, message = self.model_manager.add_model(self.username, label if label else None)
        
        progress.close()
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.refresh_models()
        else:
            QMessageBox.warning(self, "Error", message)
    
    def remove_model(self):
        """Remove the selected face model"""
        current_item = self.models_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a model to remove.")
            return
        
        model_id = current_item.data(Qt.UserRole)
        if model_id is None:
            return
        
        # Confirm
        reply = QMessageBox.question(
            self, "Confirm Removal",
            f"Are you sure you want to remove this face model?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self.model_manager.remove_model(self.username, model_id)
            if success:
                QMessageBox.information(self, "Success", message)
                self.refresh_models()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def clear_models(self):
        """Clear all face models"""
        reply = QMessageBox.question(
            self, "Confirm Clear All",
            "Are you sure you want to remove ALL face models? This cannot be undone!",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self.model_manager.clear_models(self.username)
            if success:
                QMessageBox.information(self, "Success", message)
                self.refresh_models()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def test_recognition(self):
        """Test face recognition"""
        self.test_output.clear()
        self.test_output.append("Testing face recognition...\nPlease look at the camera.\n")
        QApplication.processEvents()
        
        success, message, details = self.model_manager.test_recognition(self.username)
        
        self.test_output.append(f"Result: {message}\n")
        if details.get('stdout'):
            self.test_output.append("Output:\n" + details['stdout'])


class AdvancedSettingsTab(QWidget):
    """Tab for advanced Howdy settings"""
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Core settings
        core_group = QGroupBox("Core Settings")
        core_layout = QFormLayout()
        
        self.detection_notice_cb = QCheckBox()
        self.detection_notice_cb.setChecked(self.config.get_boolean('core', 'detection_notice', False))
        core_layout.addRow("Show detection notice:", self.detection_notice_cb)
        
        self.timeout_notice_cb = QCheckBox()
        self.timeout_notice_cb.setChecked(self.config.get_boolean('core', 'timeout_notice', True))
        core_layout.addRow("Show timeout notice:", self.timeout_notice_cb)
        
        self.no_confirmation_cb = QCheckBox()
        self.no_confirmation_cb.setChecked(self.config.get_boolean('core', 'no_confirmation', False))
        core_layout.addRow("No confirmation message:", self.no_confirmation_cb)
        
        self.abort_ssh_cb = QCheckBox()
        self.abort_ssh_cb.setChecked(self.config.get_boolean('core', 'abort_if_ssh', True))
        core_layout.addRow("Disable in SSH sessions:", self.abort_ssh_cb)
        
        self.abort_lid_cb = QCheckBox()
        self.abort_lid_cb.setChecked(self.config.get_boolean('core', 'abort_if_lid_closed', True))
        core_layout.addRow("Disable when lid closed:", self.abort_lid_cb)
        
        self.use_cnn_cb = QCheckBox()
        self.use_cnn_cb.setChecked(self.config.get_boolean('core', 'use_cnn', False))
        core_layout.addRow("Use CNN detector (slower, more accurate):", self.use_cnn_cb)
        
        core_group.setLayout(core_layout)
        layout.addWidget(core_group)
        
        # Snapshot settings
        snapshot_group = QGroupBox("Snapshot Settings")
        snapshot_layout = QFormLayout()
        
        self.save_failed_cb = QCheckBox()
        self.save_failed_cb.setChecked(self.config.get_boolean('snapshots', 'save_failed', False))
        snapshot_layout.addRow("Save failed attempts:", self.save_failed_cb)
        
        self.save_successful_cb = QCheckBox()
        self.save_successful_cb.setChecked(self.config.get_boolean('snapshots', 'save_successful', False))
        snapshot_layout.addRow("Save successful attempts:", self.save_successful_cb)
        
        snapshot_group.setLayout(snapshot_layout)
        layout.addWidget(snapshot_group)
        
        # Debug settings
        debug_group = QGroupBox("Debug Settings")
        debug_layout = QFormLayout()
        
        self.end_report_cb = QCheckBox()
        self.end_report_cb.setChecked(self.config.get_boolean('debug', 'end_report', False))
        debug_layout.addRow("Show diagnostic report:", self.end_report_cb)
        
        debug_group.setLayout(debug_layout)
        layout.addWidget(debug_group)
        
        # Save button
        save_btn = QPushButton("Save Advanced Settings")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-weight: bold;")
        layout.addWidget(save_btn)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def save_settings(self):
        """Save advanced settings"""
        try:
            # Core settings
            self.config.set('core', 'detection_notice', str(self.detection_notice_cb.isChecked()).lower())
            self.config.set('core', 'timeout_notice', str(self.timeout_notice_cb.isChecked()).lower())
            self.config.set('core', 'no_confirmation', str(self.no_confirmation_cb.isChecked()).lower())
            self.config.set('core', 'abort_if_ssh', str(self.abort_ssh_cb.isChecked()).lower())
            self.config.set('core', 'abort_if_lid_closed', str(self.abort_lid_cb.isChecked()).lower())
            self.config.set('core', 'use_cnn', str(self.use_cnn_cb.isChecked()).lower())
            
            # Snapshot settings
            self.config.set('snapshots', 'save_failed', str(self.save_failed_cb.isChecked()).lower())
            self.config.set('snapshots', 'save_successful', str(self.save_successful_cb.isChecked()).lower())
            
            # Debug settings
            self.config.set('debug', 'end_report', str(self.end_report_cb.isChecked()).lower())
            
            # Save to file
            if self.config.save():
                QMessageBox.information(self, "Success", "Advanced settings saved successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to save settings. Check permissions.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving settings: {str(e)}")


class HowdyGUIManager(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Howdy GUI Manager")
        self.setMinimumSize(900, 700)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Header
        header = QLabel("<h1>🔐 Howdy GUI Manager</h1>")
        header.setStyleSheet("background-color: #2196F3; color: white; padding: 15px;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Create tab widget
        tabs = QTabWidget()
        tabs.addTab(CameraSettingsTab(self.config), "📷 Camera Settings")
        tabs.addTab(FaceModelsTab(self.config), "👤 Face Models")
        tabs.addTab(AdvancedSettingsTab(self.config), "⚙️ Advanced")
        
        layout.addWidget(tabs)
        
        # Footer
        footer = QLabel("Howdy GUI Manager v1.0.0 | Manage your facial authentication settings")
        footer.setStyleSheet("padding: 10px; color: #666;")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Stop any camera previews
        for i in range(self.centralWidget().layout().itemAt(1).widget().count()):
            tab = self.centralWidget().layout().itemAt(1).widget().widget(i)
            if hasattr(tab, 'preview_widget'):
                tab.preview_widget.stop_preview()
        event.accept()


def main():
    """Main entry point"""
    # Check if running as root
    if os.geteuid() != 0:
        print("This application requires root privileges.")
        print("Please run with: sudo howdy-gui-manager")
        sys.exit(1)
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    window = HowdyGUIManager()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

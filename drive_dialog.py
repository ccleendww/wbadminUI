"""
Drive selection dialog
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QListWidget, QListWidgetItem, QLabel)
from PySide6.QtCore import Qt
from validation import DriveValidator
import psutil


class DriveSelectDialog(QDialog):
    """Drive selection dialog"""
    
    def __init__(self, parent=None, exclude_drive=None):
        super().__init__(parent)
        self.setWindowTitle("Select Drive")
        self.setGeometry(100, 100, 400, 300)
        self.selected_drive = None
        self.exclude_drive = exclude_drive
        
        layout = QVBoxLayout()
        
        # Title
        label = QLabel("Please select a drive:")
        layout.addWidget(label)
        
        # Drive list
        self.drive_list = QListWidget()
        self.populate_drives()
        layout.addWidget(self.drive_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def populate_drives(self):
        """Populate drive list"""
        drives = DriveValidator.get_all_drives()
        
        for drive in drives:
            # Skip excluded drives
            if self.exclude_drive and drive.upper() == self.exclude_drive.upper():
                continue
            
            try:
                total, used, free = DriveValidator.get_disk_usage(drive)
                fstype = DriveValidator.get_filesystem(drive)
                
                # Convert to GB
                total_gb = total / (1024**3)
                free_gb = free / (1024**3)
                
                # Get drive type
                drive_type = DriveValidator.get_drive_type(drive)
                
                # Create display text
                display_text = f"{drive}  ({fstype})  [{drive_type}]  Available: {free_gb:.1f} GB / {total_gb:.1f} GB"
                
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, drive)
                self.drive_list.addItem(item)
            except Exception as e:
                # If unable to get info, at least show the drive letter
                display_text = f"{drive}  (Failed to get info)"
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, drive)
                self.drive_list.addItem(item)
        
        # Default select first item
        if self.drive_list.count() > 0:
            self.drive_list.setCurrentRow(0)
    
    def get_selected_drive(self):
        """Get selected drive"""
        current_item = self.drive_list.currentItem()
        if current_item:
            return current_item.data(Qt.UserRole)
        return None
    
    def accept(self):
        """OK button"""
        self.selected_drive = self.get_selected_drive()
        if self.selected_drive:
            super().accept()

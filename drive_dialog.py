"""
驱动器选择对话框
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QListWidget, QListWidgetItem, QLabel)
from PySide6.QtCore import Qt
from validation import DriveValidator
import psutil


class DriveSelectDialog(QDialog):
    """驱动器选择对话框"""
    
    def __init__(self, parent=None, exclude_drive=None):
        super().__init__(parent)
        self.setWindowTitle("选择驱动器")
        self.setGeometry(100, 100, 400, 300)
        self.selected_drive = None
        self.exclude_drive = exclude_drive
        
        layout = QVBoxLayout()
        
        # 标题
        label = QLabel("请选择一个驱动器：")
        layout.addWidget(label)
        
        # 驱动器列表
        self.drive_list = QListWidget()
        self.populate_drives()
        layout.addWidget(self.drive_list)
        
        # 按钮
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def populate_drives(self):
        """填充驱动器列表"""
        drives = DriveValidator.get_all_drives()
        
        for drive in drives:
            # 跳过被排除的驱动器
            if self.exclude_drive and drive.upper() == self.exclude_drive.upper():
                continue
            
            try:
                total, used, free = DriveValidator.get_disk_usage(drive)
                fstype = DriveValidator.get_filesystem(drive)
                
                # 转换为 GB
                total_gb = total / (1024**3)
                free_gb = free / (1024**3)
                
                # 获取驱动器类型
                drive_type = DriveValidator.get_drive_type(drive)
                
                # 创建显示文本
                display_text = f"{drive}  ({fstype})  [{drive_type}]  可用: {free_gb:.1f} GB / {total_gb:.1f} GB"
                
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, drive)
                self.drive_list.addItem(item)
            except Exception as e:
                # 如果无法获取信息，至少显示驱动器盘符
                display_text = f"{drive}  (信息获取失败)"
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, drive)
                self.drive_list.addItem(item)
        
        # 默认选择第一个
        if self.drive_list.count() > 0:
            self.drive_list.setCurrentRow(0)
    
    def get_selected_drive(self):
        """获取选择的驱动器"""
        current_item = self.drive_list.currentItem()
        if current_item:
            return current_item.data(Qt.UserRole)
        return None
    
    def accept(self):
        """确定按钮"""
        self.selected_drive = self.get_selected_drive()
        if self.selected_drive:
            super().accept()

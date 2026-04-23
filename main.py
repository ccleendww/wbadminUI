import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from ui_main import BackupUI
from backup_engine import AdminUtils, BackupWorker, get_backup_versions
from validation import DriveValidator
from drive_dialog import DriveSelectDialog

class MainApp(BackupUI):
    def __init__(self):
        super().__init__()
        self.source_drive = None
        self.target_drive = None
        
        self.check_admin()
        
        # 绑定 UI 事件
        self.source_btn.clicked.connect(self.select_source_drive)
        self.target_btn.clicked.connect(self.select_target_drive)
        self.start_btn.clicked.connect(self.start_backup)
        
    def check_admin(self):
        if AdminUtils.is_admin():
            self.admin_label.setText("✅ 已获得管理员权限")
            self.admin_label.setStyleSheet("color: green")
        else:
            self.admin_label.setText("❌ 缺少管理员权限，功能可能受限")
            self.admin_label.setStyleSheet("color: red")

    def select_source_drive(self):
        """打开源盘选择对话框"""
        dialog = DriveSelectDialog(self, exclude_drive=self.target_drive)
        if dialog.exec():
            self.source_drive = dialog.selected_drive
            self.source_label.setText(f"源盘: {self.source_drive}")
            self.source_label.setStyleSheet("color: blue")
            # 刷新版本列表
            self.update_version_list()

    def select_target_drive(self):
        """打开目标盘选择对话框"""
        dialog = DriveSelectDialog(self, exclude_drive=self.source_drive)
        if dialog.exec():
            self.target_drive = dialog.selected_drive
            self.target_label.setText(f"目标盘: {self.target_drive}")
            self.target_label.setStyleSheet("color: blue")
            # 刷新版本列表
            self.update_version_list()

    def update_version_list(self):
        """刷新版本列表"""
        if self.target_drive:
            versions = get_backup_versions(self.target_drive)
            self.version_list.clear()
            self.version_list.addItems(versions)

    def start_backup(self):
        if not self.source_drive or not self.target_drive:
            QMessageBox.warning(self, "错误", "请先选择源盘和目标盘")
            return

        # 执行备份前验证
        self.log_area.clear()
        self.log_area.append(">>> 执行备份前检查...\n")
        
        all_passed, messages = DriveValidator.validate_backup(self.source_drive, self.target_drive)
        
        # 显示所有检查消息
        for msg in messages:
            self.log_area.append(msg)
        
        self.log_area.append("")
        
        if not all_passed:
            self.log_area.append("✗ 备份前检查失败，请解决上述问题后重试")
            QMessageBox.critical(self, "备份检查失败", 
                               "备份前检查发现以下问题：\n\n" + "\n".join(messages))
            return

        # 对于USB可移动介质的警告，需要特殊处理
        drive_type = DriveValidator.get_drive_type(self.target_drive)
        if drive_type == "Removable":
            reply = QMessageBox.warning(self, "高危警告", 
                                       "目标盘是 USB 可移动介质，wbadmin 对其支持极差。\n\n是否继续？",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                self.log_area.append("✗ 用户取消备份")
                return

        # 所有检查通过，开始备份
        self.start_btn.setEnabled(False)
        self.progress_bar.show()
        self.log_area.append("✓ 所有检查通过，准备启动 VSS 卷影复制备份...\n")

        # 创建并启动后台线程
        self.worker = BackupWorker(self.target_drive, self.source_drive)
        self.worker.output_signal.connect(self.update_log)
        self.worker.finished_signal.connect(self.on_finished)
        self.worker.start()

    def update_log(self, text):
        self.log_area.append(text)

    def on_finished(self, code):
        self.progress_bar.hide()
        self.start_btn.setEnabled(True)
        if code == 0:
            self.log_area.append("\n✓ 系统映像备份已完成")
            QMessageBox.information(self, "成功", "系统映像备份已完成")
        else:
            self.log_area.append(f"\n✗ 备份中止，错误代码: {code}")
            QMessageBox.critical(self, "失败", f"备份中止，错误代码: {code}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())

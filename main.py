import sys
from PySide6.QtWidgets import QApplication, QMessageBox, QFileDialog
from ui_main import BackupUI
from backup_engine import AdminUtils, BackupWorker, get_backup_versions

class MainApp(BackupUI):
    def __init__(self):
        super().__init__()
        self.check_admin()
        
        # 绑定 UI 事件
        self.path_btn.clicked.connect(self.select_path)
        self.start_btn.clicked.connect(self.start_backup)
        
    def check_admin(self):
        if AdminUtils.is_admin():
            self.admin_label.setText("✅ 已获得管理员权限")
            self.admin_label.setStyleSheet("color: green")
        else:
            self.admin_label.setText("❌ 缺少管理员权限，功能可能受限")
            self.admin_label.setStyleSheet("color: red")

    def select_path(self):
        path = QFileDialog.getExistingDirectory(self, "选择备份存放目录")
        if path:
            self.path_input.setText(path)
            # 自动刷新版本列表
            versions = get_backup_versions(path)
            self.version_list.clear()
            self.version_list.addItems(versions)

    def start_backup(self):
        target = self.path_input.text()
        if not target:
            QMessageBox.warning(self, "错误", "请先选择目标路径")
            return

        self.start_btn.setEnabled(False)
        self.progress_bar.show()
        self.log_area.append(">>> 准备启动 VSS 卷影复制备份...")

        # 创建并启动后台线程
        self.worker = BackupWorker(target)
        self.worker.output_signal.connect(self.update_log)
        self.worker.finished_signal.connect(self.on_finished)
        self.worker.start()

    def update_log(self, text):
        self.log_area.append(text)

    def on_finished(self, code):
        self.progress_bar.hide()
        self.start_btn.setEnabled(True)
        if code == 0:
            QMessageBox.information(self, "成功", "系统映像备份已完成")
        else:
            QMessageBox.critical(self, "失败", f"备份中止，错误代码: {code}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())
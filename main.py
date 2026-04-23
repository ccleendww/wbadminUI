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
        
        # Bind UI events
        self.source_btn.clicked.connect(self.select_source_drive)
        self.target_btn.clicked.connect(self.select_target_drive)
        self.start_btn.clicked.connect(self.start_backup)
        
    def check_admin(self):
        if AdminUtils.is_admin():
            self.admin_label.setText("✅ Admin privileges obtained")
            self.admin_label.setStyleSheet("color: green")
        else:
            self.admin_label.setText("❌ Admin privileges required")
            self.admin_label.setStyleSheet("color: red")

    def select_source_drive(self):
        """Open source drive selection dialog"""
        dialog = DriveSelectDialog(self, exclude_drive=self.target_drive)
        if dialog.exec():
            self.source_drive = dialog.selected_drive
            self.source_label.setText(f"Source Drive: {self.source_drive}")
            self.source_label.setStyleSheet("color: blue")
            # Refresh version list
            self.update_version_list()

    def select_target_drive(self):
        """Open target drive selection dialog"""
        dialog = DriveSelectDialog(self, exclude_drive=self.source_drive)
        if dialog.exec():
            self.target_drive = dialog.selected_drive
            self.target_label.setText(f"Target Drive: {self.target_drive}")
            self.target_label.setStyleSheet("color: blue")
            # Refresh version list
            self.update_version_list()

    def update_version_list(self):
        """Refresh version list"""
        if self.target_drive:
            versions = get_backup_versions(self.target_drive)
            self.version_list.clear()
            self.version_list.addItems(versions)

    def start_backup(self):
        if not self.source_drive or not self.target_drive:
            QMessageBox.warning(self, "Error", "Please select both source and target drives")
            return

        # Pre-backup validation
        self.log_area.clear()
        self.log_area.append(">>> Running pre-backup checks...\n")
        
        all_passed, messages = DriveValidator.validate_backup(self.source_drive, self.target_drive)
        
        # Display all check messages
        for msg in messages:
            self.log_area.append(msg)
        
        self.log_area.append("")
        
        if not all_passed:
            self.log_area.append("✗ Pre-backup checks failed. Please resolve the issues above and try again.")
            QMessageBox.critical(self, "Backup Check Failed", 
                               "Pre-backup checks found the following issues:\n\n" + "\n".join(messages))
            return

        # Special handling for USB removable media warning
        drive_type = DriveValidator.get_drive_type(self.target_drive)
        if drive_type == "Removable":
            reply = QMessageBox.warning(self, "High Risk Warning", 
                                       "Target drive is USB removable media. wbadmin has poor support for it.\n\nContinue?",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                self.log_area.append("✗ User cancelled backup")
                return

        # All checks passed, start backup
        self.start_btn.setEnabled(False)
        self.progress_bar.show()
        self.log_area.append("✓ All checks passed. Starting VSS snapshot backup...\n")

        # Create and start background thread
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
            self.log_area.append("\n✓ System image backup completed")
            QMessageBox.information(self, "Success", "System image backup completed")
        else:
            self.log_area.append(f"\n✗ Backup aborted. Error code: {code}")
            QMessageBox.critical(self, "Failed", f"Backup aborted. Error code: {code}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())

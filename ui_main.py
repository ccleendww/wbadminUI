from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QComboBox, QTextEdit, QLabel, QProgressBar, QListWidget)


class BackupUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("wbadminUI")
        self.resize(700, 600)
        
        layout = QVBoxLayout()

        # 1. Admin Status
        self.admin_label = QLabel("Checking admin privileges...")
        layout.addWidget(self.admin_label)

        # 2. Source Drive Selection
        source_layout = QHBoxLayout()
        self.source_label = QLabel("Source Drive: Not Selected")
        self.source_btn = QPushButton("Select Source Drive")
        source_layout.addWidget(self.source_label)
        source_layout.addStretch()
        source_layout.addWidget(self.source_btn)
        layout.addLayout(source_layout)

        # 3. Target Drive Selection
        target_layout = QHBoxLayout()
        self.target_label = QLabel("Target Drive: Not Selected")
        self.target_btn = QPushButton("Select Target Drive")
        target_layout.addWidget(self.target_label)
        target_layout.addStretch()
        target_layout.addWidget(self.target_btn)
        layout.addLayout(target_layout)

        # 4. Existing Backups
        layout.addWidget(QLabel("Existing Backups:"))
        self.version_list = QListWidget()
        layout.addWidget(self.version_list)

        # 5. Progress and Logs
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0) # Busy state
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        # 6. Action Buttons
        self.start_btn = QPushButton("Start Full Disk Backup")
        layout.addWidget(self.start_btn)

        self.setLayout(layout)
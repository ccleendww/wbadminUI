from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QComboBox, QTextEdit, QLabel, QProgressBar, QListWidget)


class BackupUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("wbadminUI")
        self.resize(700, 600)
        
        layout = QVBoxLayout()

        # 1. 管理员状态
        self.admin_label = QLabel("管理员权限检查中...")
        layout.addWidget(self.admin_label)

        # 2. 源盘选择
        source_layout = QHBoxLayout()
        self.source_label = QLabel("源盘: 未选择")
        self.source_btn = QPushButton("选择源盘")
        source_layout.addWidget(self.source_label)
        source_layout.addStretch()
        source_layout.addWidget(self.source_btn)
        layout.addLayout(source_layout)

        # 3. 目标盘选择
        target_layout = QHBoxLayout()
        self.target_label = QLabel("目标盘: 未选择")
        self.target_btn = QPushButton("选择目标盘")
        target_layout.addWidget(self.target_label)
        target_layout.addStretch()
        target_layout.addWidget(self.target_btn)
        layout.addLayout(target_layout)

        # 4. 历史版本
        layout.addWidget(QLabel("已有备份版本:"))
        self.version_list = QListWidget()
        layout.addWidget(self.version_list)

        # 5. 进度与日志
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0) # 忙碌状态
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        # 6. 操作按钮
        self.start_btn = QPushButton("开始全盘热备份")
        layout.addWidget(self.start_btn)

        self.setLayout(layout)
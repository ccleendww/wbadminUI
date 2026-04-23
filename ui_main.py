from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLineEdit, QTextEdit, QLabel, QProgressBar, QListWidget, QFileDialog)


class BackupUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("wbadminUI")
        self.resize(600, 500)
        
        layout = QVBoxLayout()

        # 1. 管理员状态
        self.admin_label = QLabel("管理员权限检查中...")
        layout.addWidget(self.admin_label)

        # 2. 路径选择
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_btn = QPushButton("选择目标路径")
        path_layout.addWidget(QLabel("目标:"))
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.path_btn)
        layout.addLayout(path_layout)

        # 3. 历史版本
        layout.addWidget(QLabel("已有备份版本:"))
        self.version_list = QListWidget()
        layout.addWidget(self.version_list)

        # 4. 进度与日志
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0) # 忙碌状态
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        # 5. 操作按钮
        self.start_btn = QPushButton("开始全盘热备份")
        layout.addWidget(self.start_btn)

        self.setLayout(layout)
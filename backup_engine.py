import subprocess
import ctypes
import os
from PySide6.QtCore import QThread, Signal

class AdminUtils:
    @staticmethod
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

class BackupWorker(QThread):
    """
    逻辑层：负责执行 wbadmin 备份，不涉及任何 UI 操作
    """
    output_signal = Signal(str)    # 传递实时日志
    finished_signal = Signal(int)  # 传递退出码

    def __init__(self, target_path, source_drive="C:"):
        super().__init__()
        self.target_path = target_path
        self.source_drive = source_drive

    def run(self):
        # 实际调用的指令
        cmd = [
            "wbadmin", "start", "backup",
            f"-backupTarget:{self.target_path}",
            f"-include:{self.source_drive}",
            "-allCritical", "-quiet"
        ]
        
        # 使用 Popen 实现非阻塞实时读取
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            shell=True, text=True, encoding='gbk'
        )

        for line in process.stdout:
            self.output_signal.emit(line.strip())
        
        process.wait()
        self.finished_signal.emit(process.returncode)

def get_backup_versions(parent_dir):
    """扫描目录下已有的备份版本"""
    if not os.path.exists(parent_dir):
        return []
    # 假设备份目录为 yyyyMMdd 格式
    return [d for d in os.listdir(parent_dir) if os.path.isdir(os.path.join(parent_dir, d))]
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

    def __init__(self, target_drive, source_drive):
        super().__init__()
        # 确保盘符格式正确（如 C: 或 C:\\）
        self.target_drive = target_drive.rstrip(':') + ':' if target_drive else None
        self.source_drive = source_drive.rstrip(':') + ':' if source_drive else None

    def run(self):
        # 实际调用的指令
        cmd = [
            "wbadmin", "start", "backup",
            f"-backupTarget:{self.target_drive}",
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
    """扫描目录下已有的备份版本，并严格校验文件结构特征"""
    if not os.path.exists(parent_dir):
        return []
        
    valid_versions = []
    
    try:
        # 获取父目录下的所有项目
        for d in os.listdir(parent_dir):
            dir_path = os.path.join(parent_dir, d)
            
            # 1. 基础过滤：必须是文件夹
            if not os.path.isdir(dir_path):
                continue
                
            try:
                # 校验特征 A (目录移动方案)：检查该目录下是否直接包含 WindowsImageBackup 文件夹
                has_wib_folder = os.path.isdir(os.path.join(dir_path, "WindowsImageBackup"))
                
                # 校验特征 B (容器方案)：检查该目录下是否存在 .vhdx 虚拟磁盘文件
                has_vhdx = any(f.lower().endswith('.vhdx') for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f)))
                
                # 只要满足任一特征，即认定为有效备份
                if has_wib_folder or has_vhdx:
                    valid_versions.append(d)
                    
            except PermissionError:
                # 静默拦截：如果遇到诸如 System Volume Information 这种连读取列表都没有权限的死锁文件夹，直接跳过
                continue
                
    except PermissionError:
        # 如果连父目录都没有读取权限，直接返回空列表
        return []

    # 降序排列：在 UI 列表中，通常希望最新的备份日期显示在最顶部
    return sorted(valid_versions, reverse=True)
"""
防呆机制库：确保备份操作的安全性和可靠性
"""
import os
import psutil
import ctypes
from typing import Tuple, List
import subprocess


class DriveValidator:
    """驱动器验证和检查类"""
    
    @staticmethod
    def get_all_drives() -> List[str]:
        """获取系统中所有的驱动器盘符"""
        drives = []
        seen = set()
        for drive in psutil.disk_partitions():
            # 提取盘符（如 C: 或 C:\）
            device = drive.device
            if len(device) >= 2 and device[1] == ':':
                # 格式化为 C: 的形式
                drive_letter = device[0:2]
                if drive_letter not in seen:
                    drives.append(drive_letter)
                    seen.add(drive_letter)
        return sorted(drives)
    
    @staticmethod
    def get_filesystem(drive: str) -> str:
        """获取驱动器的文件系统类型"""
        try:
            for partition in psutil.disk_partitions():
                if partition.device == drive or partition.device == f"{drive}\\":
                    return partition.fstype.upper()
        except Exception as e:
            raise RuntimeError(f"无法获取驱动器 {drive} 的文件系统: {e}")
        raise RuntimeError(f"未找到驱动器 {drive}")
    
    @staticmethod
    def check_filesystem(target_drive: str) -> Tuple[bool, str]:
        """
        检查目标驱动器是否为 NTFS 或 ReFS
        返回: (是否符合, 消息)
        """
        try:
            fstype = DriveValidator.get_filesystem(target_drive)
            if fstype in ["NTFS", "REFS"]:
                return True, f"✓ 目标盘 {target_drive} 文件系统为 {fstype}"
            else:
                return False, f"✗ 目标盘 {target_drive} 文件系统为 {fstype}，只支持 NTFS 或 ReFS"
        except Exception as e:
            return False, f"✗ 错误: {e}"
    
    @staticmethod
    def get_disk_usage(drive: str) -> Tuple[int, int, int]:
        """
        获取驱动器的使用情况
        返回: (总大小, 已用, 可用) 单位：字节
        """
        try:
            usage = psutil.disk_usage(drive)
            return usage.total, usage.used, usage.free
        except Exception as e:
            raise RuntimeError(f"无法获取驱动器 {drive} 的空间信息: {e}")
    
    @staticmethod
    def check_disk_space(source_drive: str, target_drive: str) -> Tuple[bool, str]:
        """
        检查目标盘的可用空间是否足够
        要求: 目标盘可用空间 > 源盘已用空间 * 1.1
        返回: (是否符合, 消息)
        """
        try:
            _, source_used, _ = DriveValidator.get_disk_usage(source_drive)
            _, _, target_free = DriveValidator.get_disk_usage(target_drive)
            
            required_space = int(source_used * 1.1)
            
            if target_free > required_space:
                source_used_gb = source_used / (1024**3)
                required_gb = required_space / (1024**3)
                target_free_gb = target_free / (1024**3)
                return True, f"✓ 目标盘可用空间充足 ({target_free_gb:.2f} GB > {required_gb:.2f} GB)"
            else:
                source_used_gb = source_used / (1024**3)
                required_gb = required_space / (1024**3)
                target_free_gb = target_free / (1024**3)
                return False, (f"✗ 目标盘可用空间不足\n"
                             f"  源盘已用: {source_used_gb:.2f} GB\n"
                             f"  需要空间: {required_gb:.2f} GB\n"
                             f"  可用空间: {target_free_gb:.2f} GB")
        except Exception as e:
            return False, f"✗ 错误: {e}"
    
    @staticmethod
    def check_same_drive(source_drive: str, target_drive: str) -> Tuple[bool, str]:
        """
        检查源盘和目标盘是否相同
        返回: (是否合法, 消息)
        """
        if source_drive.upper() == target_drive.upper():
            return False, "✗ 源盘和目标盘不能相同"
        return True, f"✓ 源盘 {source_drive} 和目标盘 {target_drive} 不同"
    
    @staticmethod
    def get_drive_type(drive: str) -> str:
        """
        通过系统 API 判断驱动器类型
        返回: "Fixed" (固定磁盘) 或 "Removable" (可移动介质) 或 "Unknown"
        """
        try:
            # 使用 Windows API 获取驱动器类型
            drive_letter = drive.rstrip(':')
            drive_path = f"{drive}\\"
            
            # GetDriveType 返回值：
            # 1 = DRIVE_NO_ROOT_DIR
            # 2 = DRIVE_REMOVABLE
            # 3 = DRIVE_FIXED
            # 4 = DRIVE_REMOTE
            # 5 = DRIVE_CDROM
            
            drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive_path)
            
            if drive_type == 3:
                return "Fixed"
            elif drive_type == 2:
                return "Removable"
            else:
                return "Unknown"
        except Exception as e:
            return "Unknown"
    
    @staticmethod
    def check_drive_type(target_drive: str) -> Tuple[bool, str]:
        """
        检查目标驱动器是否为 USB 等可移动介质
        返回: (是否安全, 消息)
        """
        drive_type = DriveValidator.get_drive_type(target_drive)
        
        if drive_type == "Removable":
            return False, (f"⚠ 【高危警告】目标盘 {target_drive} 是可移动介质\n"
                          f"wbadmin 对 USB 闪存盘支持极差，经常报错\n"
                          f"强烈建议使用固定磁盘作为备份目标")
        elif drive_type == "Fixed":
            return True, f"✓ 目标盘 {target_drive} 是固定磁盘"
        else:
            return True, f"◆ 目标盘 {target_drive} 类型未知，请谨慎操作"
    
    @staticmethod
    def check_ac_power() -> Tuple[bool, str]:
        """
        检查笔记本是否连接到交流电源
        返回: (是否连接电源, 消息)
        """
        try:
            # 获取电源状态
            battery = psutil.sensors_battery()
            
            if battery is None:
                # 没有电池，说明是台式机或已拔出电池
                return True, "✓ 未检测到电池（台式机或电池已拔出）"
            
            if battery.power_plugged:
                return True, "✓ 笔记本已连接交流电源"
            else:
                remaining = battery.secsleft
                if remaining != psutil.POWER_TIME_UNKNOWN:
                    remaining_min = remaining // 60
                    return False, (f"⚠ 【重要警告】笔记本处于电池供电状态\n"
                                 f"预计续航时间: {remaining_min} 分钟\n"
                                 f"块级备份会产生持续高强度 I/O，耗时可能长达几十分钟\n"
                                 f"中途断电会导致备份虚拟磁盘彻底损坏\n"
                                 f"请连接交流电源后重试")
                else:
                    return False, (f"⚠ 【重要警告】笔记本处于电池供电状态\n"
                                 f"块级备份会产生持续高强度 I/O，耗时可能长达几十分钟\n"
                                 f"中途断电会导致备份虚拟磁盘彻底损坏\n"
                                 f"请连接交流电源后重试")
        except Exception as e:
            # 如果无法获取电源状态，默认通过
            return True, "◆ 无法检测电源状态，请确保笔记本已连接电源"
    
    @staticmethod
    def validate_backup(source_drive: str, target_drive: str) -> Tuple[bool, List[str]]:
        """
        执行全面的备份前检查
        返回: (是否所有检查都通过, 检查消息列表)
        """
        messages = []
        all_passed = True
        
        # 1. 检查文件系统
        fs_ok, fs_msg = DriveValidator.check_filesystem(target_drive)
        messages.append(fs_msg)
        if not fs_ok:
            all_passed = False
        
        # 2. 检查盘符是否相同
        same_ok, same_msg = DriveValidator.check_same_drive(source_drive, target_drive)
        messages.append(same_msg)
        if not same_ok:
            all_passed = False
        
        # 3. 检查磁盘空间
        space_ok, space_msg = DriveValidator.check_disk_space(source_drive, target_drive)
        messages.append(space_msg)
        if not space_ok:
            all_passed = False
        
        # 4. 检查驱动器类型（USB 警告）
        drive_type_ok, drive_type_msg = DriveValidator.check_drive_type(target_drive)
        messages.append(drive_type_msg)
        # 不将此作为阻断条件，只是警告
        
        # 5. 检查电源状态
        power_ok, power_msg = DriveValidator.check_ac_power()
        messages.append(power_msg)
        if not power_ok:
            all_passed = False
        
        return all_passed, messages

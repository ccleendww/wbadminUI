# wbadminUI - Windows Backup Administration Interface

A user-friendly GUI wrapper for Windows `wbadmin` with comprehensive pre-backup validation and failsafe mechanisms.

## Features

- **Intuitive Drive Selection**: Easy-to-use dialogs for selecting source and target drives with detailed drive information
- **Comprehensive Pre-Backup Validation**: Multiple failsafe checks to prevent backup failures
- **Real-time Logging**: Live output from the backup process
- **Version History**: View existing backups on the target drive
- **Admin Privilege Check**: Ensures the application runs with required permissions

## Installation

1. Install Python 3.8+
2. Install dependencies:
   ```bash
   pip install pyside6 psutil
   ```

## Usage

```bash
python main.py
```

## Failsafe Mechanisms (Due to wbadmin Limitations)

The application includes multiple validation checks designed to prevent common backup failures caused by `wbadmin` limitations:

### 1. **File System Validation**
   - **Requirement**: Target drive must be formatted as NTFS or ReFS
   - **Reason**: `wbadmin` only supports NTFS and ReFS file systems. Other formats will fail silently
   - **Check**: Automatically detects and rejects incompatible file systems

### 2. **Disk Space Validation**
   - **Requirement**: Target drive available space > Source drive used space × 1.1
   - **Reason**: Block-level backup requires extra space for metadata and VSS snapshots
   - **Check**: Calculates both drives' space and enforces the 1.1× safety margin

### 3. **Same Drive Prevention**
   - **Requirement**: Source and target drives must be different
   - **Reason**: `wbadmin` fails if trying to backup a drive onto itself
   - **Check**: Blocks drive selection if source and target are identical

### 4. **Removable Media Detection**
   - **Warning Level**: HIGH RISK
   - **Issue**: `wbadmin` has extremely poor support for USB flash drives
   - **Common Errors**: "This storage device is not supported as a backup target"
   - **Detection**: Uses Windows API to identify drive type (Fixed vs Removable)
   - **Action**: Shows warning dialog and requires user confirmation to proceed

### 5. **AC Power Detection (Laptop Protection)**
   - **Target**: Protects laptop users during battery operation
   - **Risk**: Block-level backup performs continuous heavy I/O operations (may take 30+ minutes)
   - **Consequence**: Power loss during backup corrupts the VHDX virtual disk irreparably
   - **Detection**: Checks battery status and AC adapter connection
   - **Action**: Blocks backup if running on battery power; requires AC connection

## Validation Flow

When clicking "Start Full Disk Backup", the following checks are performed in order:

1. ✓ File system type validation (NTFS/ReFS)
2. ✓ Same drive check (source ≠ target)
3. ✓ Disk space calculation and validation
4. ⚠ Removable media detection (warning, user can override)
5. ⚠ AC power status check (blocking for battery operation)

All validation messages are displayed in the log area for transparency.

## System Requirements

- **OS**: Windows 7 or later (Vista+ for wbadmin support)
- **Privileges**: Administrator account required
- **Python**: 3.8 or higher
- **Dependencies**: PySide6, psutil

## File Structure

```
wbadminUI/
├── main.py              # Application entry point
├── ui_main.py           # Main UI window definition
├── drive_dialog.py      # Drive selection dialog
├── backup_engine.py     # Backup execution logic
├── validation.py        # Failsafe validation library
├── pyproject.toml       # Project configuration
└── README.md           # This file
```

## Known wbadmin Limitations (Why These Checks Exist)

1. **USB Support**: `wbadmin` frequently rejects USB drives as backup targets due to performance/reliability concerns
2. **Insufficient Space**: Silent failures if target space is too tight for VSS snapshots
3. **File System Restrictions**: Only NTFS and ReFS work reliably; other formats cause obscure errors
4. **Laptop Power Issues**: No built-in power loss protection; sudden shutdown during backup destroys the backup
5. **Quiet Failures**: Many errors occur silently without clear user feedback

## Troubleshooting

### "This storage device is not supported"
- Target drive is likely a USB device
- Solution: Use an internal hard drive or external USB drive reformatted as NTFS

### "Not enough space"
- Target drive doesn't have 1.1× the source drive's used space
- Solution: Free up space on target drive or use a larger drive

### Backup hangs on laptop
- Ensure AC adapter is connected
- Check Task Manager for wbadmin.exe CPU/Disk usage

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).
See the `LICENSE` file for the full license text.

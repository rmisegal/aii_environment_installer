# -*- coding: utf-8 -*-
"""
Drive Selector - Displays available drives and helps user select installation location
"""

import os
import sys
import shutil
import string
import ctypes
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional


class DriveSelector:
    """Helper class to select installation drive"""

    REQUIRED_SPACE_GB = 50

    # Windows drive type constants
    DRIVE_UNKNOWN = 0
    DRIVE_NO_ROOT_DIR = 1
    DRIVE_REMOVABLE = 2
    DRIVE_FIXED = 3
    DRIVE_REMOTE = 4
    DRIVE_CDROM = 5
    DRIVE_RAMDISK = 6

    def __init__(self):
        self.drives_info = []

    def is_usb_drive(self, drive_letter: str) -> bool:
        """
        Check if drive is connected via USB using PowerShell WMI query

        Args:
            drive_letter: Single letter drive identifier (e.g., 'C')

        Returns:
            True if USB drive, False otherwise
        """
        # Use PowerShell to specifically check THIS drive letter
        try:
            # More specific PowerShell query that actually checks the drive letter's physical disk
            cmd = f"""
            $result = $false
            try {{
                $disk = Get-WmiObject Win32_LogicalDisk -Filter "DeviceID='{drive_letter}:'"
                if ($disk) {{
                    $partition = Get-WmiObject -Query "ASSOCIATORS OF {{Win32_LogicalDisk.DeviceID='{drive_letter}:'}} WHERE AssocClass=Win32_LogicalDiskToPartition"
                    if ($partition) {{
                        $physicaldisk = Get-WmiObject -Query "ASSOCIATORS OF {{Win32_DiskPartition.DeviceID='$($partition.DeviceID)'}} WHERE AssocClass=Win32_DiskDriveToDiskPartition"
                        if ($physicaldisk) {{
                            # Check multiple USB indicators
                            if ($physicaldisk.InterfaceType -eq 'USB' -or
                                $physicaldisk.PNPDeviceID -match 'USBSTOR' -or
                                $physicaldisk.PNPDeviceID -match '^USB') {{
                                $result = $true
                            }}
                        }}
                    }}
                }}
            }} catch {{
                # Silently fail
            }}
            if ($result) {{ Write-Output 'USB_DETECTED' }}
            """

            result = subprocess.run(['powershell', '-NoProfile', '-Command', cmd],
                                   capture_output=True, text=True, timeout=5,
                                   creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)

            # Only return True if we specifically found USB_DETECTED
            return 'USB_DETECTED' in result.stdout

        except Exception:
            # If detection fails, assume not USB (safer default)
            return False

    def get_drive_type(self, drive_letter: str) -> str:
        """
        Determine if drive is internal or external using Windows API and USB detection

        Args:
            drive_letter: Single letter drive identifier (e.g., 'C')

        Returns:
            'Internal', 'External', or 'Other' (network, CD-ROM, etc.)
        """
        try:
            drive_path = f"{drive_letter}:\\"
            drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive_path)

            # Check for network and CD-ROM first
            if drive_type == self.DRIVE_REMOTE:
                return "Network"
            elif drive_type == self.DRIVE_CDROM:
                return "CD-ROM"

            # For fixed and removable drives, check if USB
            if drive_type == self.DRIVE_REMOVABLE:
                return "External"
            elif drive_type == self.DRIVE_FIXED:
                # Check if this is actually a USB drive
                if self.is_usb_drive(drive_letter):
                    return "External"
                else:
                    return "Internal"
            else:
                return "Other"
        except Exception:
            return "Unknown"

    def check_ailab_folder(self, drive_letter: str) -> Optional[str]:
        """
        Check if AI_Lab folder exists on the specified drive

        Args:
            drive_letter: Single letter drive identifier

        Returns:
            Full path to AI_Lab folder if found, None otherwise
        """
        drive_path = f"{drive_letter}:\\"
        ailab_path = os.path.join(drive_path, "AI_Lab")

        if os.path.exists(ailab_path) and os.path.isdir(ailab_path):
            return ailab_path

        # Also check for variations in case
        for item in os.listdir(drive_path) if os.path.exists(drive_path) else []:
            if item.lower() == "ai_lab":
                full_path = os.path.join(drive_path, item)
                if os.path.isdir(full_path):
                    return full_path

        return None

    def get_available_drives(self) -> List[Tuple[str, int, int, str, Optional[str]]]:
        """
        Get list of available drives with their space information.

        Returns:
            List of tuples: (drive_letter, free_space_gb, total_space_gb, drive_type, ailab_path)
        """
        drives = []

        # Check all possible drive letters
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"

            # Check if drive exists
            if os.path.exists(drive):
                try:
                    usage = shutil.disk_usage(drive)
                    free_gb = usage.free / (1024**3)
                    total_gb = usage.total / (1024**3)

                    # Only include drives with meaningful space (exclude CD/DVD, etc.)
                    if total_gb > 1:
                        drive_type = self.get_drive_type(letter)
                        # Check for AI_Lab folder on all drives, not just external
                        ailab_path = self.check_ailab_folder(letter)
                        drives.append((letter, free_gb, total_gb, drive_type, ailab_path))

                except (OSError, PermissionError):
                    # Skip drives that can't be accessed
                    continue

        return drives

    def display_drives(self, drives: List[Tuple[str, int, int, str, Optional[str]]], output=sys.stderr):
        """Display available drives with formatting"""
        print("\n" + "="*80, file=output)
        print("                    AVAILABLE DRIVES FOR INSTALLATION", file=output)
        print("="*80, file=output)
        print(file=output)
        print("IMPORTANT: Choose the right drive type for your needs!", file=output)
        print("  - Internal Drive: Your computer's built-in hard drive (usually C:)", file=output)
        print("  - External Drive: USB drive or external hard drive (portable)", file=output)
        print(file=output)
        print("="*80, file=output)

        for letter, free_gb, total_gb, drive_type, ailab_path in drives:
            used_gb = total_gb - free_gb
            percent_used = (used_gb / total_gb * 100) if total_gb > 0 else 0

            # Determine status
            if free_gb >= self.REQUIRED_SPACE_GB:
                status = "OK"
            elif free_gb >= 30:
                status = "WARNING"
            else:
                status = "INSUFFICIENT"

            # Format with bar chart
            bar_length = 20
            filled = int((percent_used / 100) * bar_length)
            bar = "#" * filled + "-" * (bar_length - filled)

            # Drive type indicator
            type_indicator = f"[{drive_type}]"

            print(f"Drive {letter}:\\ - {type_indicator:<12} Total: {total_gb:>6.1f} GB | Free: {free_gb:>6.1f} GB", file=output)
            print(f"         [{bar}] {percent_used:.0f}% used - Status: {status}", file=output)

            # Show AI_Lab folder if found on external drive
            if ailab_path:
                print(f"         *** AI_Lab folder found! Installation will use: {ailab_path}\\AI_Environment", file=output)

            print(file=output)

        print("="*80, file=output)
        print(f"Minimum required free space: {self.REQUIRED_SPACE_GB} GB", file=output)
        print("="*80, file=output)

    def get_recommended_drive(self, drives: List[Tuple[str, int, int, str, Optional[str]]]) -> Optional[str]:
        """
        Get the recommended drive (most free space that meets requirements)

        Returns:
            Drive letter or None if no suitable drive found
        """
        suitable_drives = [(letter, free_gb, total_gb, drive_type, ailab_path)
                          for letter, free_gb, total_gb, drive_type, ailab_path in drives
                          if free_gb >= self.REQUIRED_SPACE_GB]

        if not suitable_drives:
            return None

        # Return drive with most free space
        recommended = max(suitable_drives, key=lambda x: x[1])
        return recommended[0]

    def prompt_user_selection(self, drives: List[Tuple[str, int, int, str, Optional[str]]]) -> Optional[Tuple[str, Optional[str]]]:
        """
        Prompt user to select a drive with educational guidance

        Returns:
            Tuple of (selected drive letter, ailab_path) or None if cancelled
        """
        recommended = self.get_recommended_drive(drives)

        if not recommended:
            print("\nWARNING: No drives meet the recommended 50GB free space requirement.", file=sys.stderr)
            print("Installation may fail or run out of space during installation.", file=sys.stderr)
            print(file=sys.stderr)

        # Display guidance for students
        print("\n" + "="*80, file=sys.stderr)
        print("                      INSTALLATION GUIDE", file=sys.stderr)
        print("="*80, file=sys.stderr)
        print(file=sys.stderr)
        print("INTERNAL DRIVE (Built-in hard drive - usually C:, D:):", file=sys.stderr)
        print("  -> Best for: Personal computers", file=sys.stderr)
        print("  -> AI_Environment and AI_Lab will be installed side-by-side at root", file=sys.stderr)
        print(file=sys.stderr)
        print("EXTERNAL DRIVE (USB/External hard drive - usually E:, F:):", file=sys.stderr)
        print("  -> Best for: Portability between computers (school & home)", file=sys.stderr)
        print("  -> AI_Lab will be created automatically with AI_Environment nested inside", file=sys.stderr)
        print(file=sys.stderr)
        print("="*80, file=sys.stderr)

        while True:
            if recommended:
                prompt = f"\nEnter drive letter (recommended: {recommended}, or 'q' to quit): "
            else:
                prompt = "\nEnter drive letter (or 'q' to quit): "

            # Print prompt to stderr, read from stdin
            print(prompt, end='', file=sys.stderr)
            sys.stderr.flush()
            user_input = input().strip().upper()

            if user_input == 'Q':
                return None

            # Check if just letter or letter with colon
            if len(user_input) == 1:
                drive_letter = user_input
            elif len(user_input) == 2 and user_input[1] == ':':
                drive_letter = user_input[0]
            else:
                print("Invalid input. Please enter a single drive letter (e.g., 'D' or 'D:')", file=sys.stderr)
                continue

            # Validate drive exists in our list
            drive_exists = any(letter == drive_letter for letter, _, _, _, _ in drives)

            if not drive_exists:
                print(f"Drive {drive_letter}: not found or inaccessible. Please choose from the list above.", file=sys.stderr)
                continue

            # Get the drive info
            drive_info = next((info for info in drives if info[0] == drive_letter), None)
            if drive_info:
                _, free_gb, _, drive_type, ailab_path = drive_info

                # Space validation
                if free_gb < 30:
                    print(f"\nWARNING: Drive {drive_letter}: has only {free_gb:.1f}GB free.", file=sys.stderr)
                    print("This is likely insufficient for the AI Environment installation.", file=sys.stderr)
                    print("Continue anyway? (y/N): ", end='', file=sys.stderr)
                    sys.stderr.flush()
                    confirm = input().strip().lower()
                    if confirm not in ['y', 'yes']:
                        continue

                elif free_gb < self.REQUIRED_SPACE_GB:
                    print(f"\nWARNING: Drive {drive_letter}: has {free_gb:.1f}GB free (recommended: {self.REQUIRED_SPACE_GB}GB)", file=sys.stderr)
                    print("Continue anyway? (y/N): ", end='', file=sys.stderr)
                    sys.stderr.flush()
                    confirm = input().strip().lower()
                    if confirm not in ['y', 'yes']:
                        continue

                # Show drive selection confirmation (simplified - master_installer handles paths)
                print(file=sys.stderr)
                print("="*80, file=sys.stderr)
                print(f"Selected: Drive {drive_letter}:\\ [{drive_type}]", file=sys.stderr)
                print("="*80, file=sys.stderr)
                print(file=sys.stderr)
                print("Proceed with installation? (Y/n): ", end='', file=sys.stderr)
                sys.stderr.flush()
                confirm = input().strip().lower()

                if confirm in ['', 'y', 'yes']:
                    return (drive_letter, ailab_path)
                else:
                    print("Selection cancelled. Please choose a different drive.", file=sys.stderr)
                    continue

        return None

    def select_drive(self, auto_select: bool = False) -> Optional[Tuple[str, Optional[str]]]:
        """
        Main method to select installation drive

        Args:
            auto_select: If True, automatically select recommended drive

        Returns:
            Tuple of (drive_letter, ailab_path) or None if selection failed
        """
        drives = self.get_available_drives()

        if not drives:
            print("ERROR: No accessible drives found.", file=sys.stderr)
            return None

        self.display_drives(drives)

        if auto_select:
            recommended = self.get_recommended_drive(drives)
            if recommended:
                print(f"\nAuto-selecting recommended drive: {recommended}:", file=sys.stderr)
                # Get ailab_path for the recommended drive
                drive_info = next((info for info in drives if info[0] == recommended), None)
                ailab_path = drive_info[4] if drive_info else None
                return (recommended, ailab_path)
            else:
                print("\nERROR: No suitable drive found for auto-selection.", file=sys.stderr)
                print("At least 50GB free space is required.", file=sys.stderr)
                return None

        return self.prompt_user_selection(drives)


def main():
    """Main function for standalone testing"""
    import argparse

    parser = argparse.ArgumentParser(description='Drive Selector for AI Environment Installation')
    parser.add_argument('--auto', action='store_true',
                       help='Automatically select recommended drive')

    args = parser.parse_args()

    selector = DriveSelector()
    result = selector.select_drive(auto_select=args.auto)

    if result:
        drive_letter, ailab_path = result
        # Get drive type for this drive
        drive_type = selector.get_drive_type(drive_letter)

        # Output for master_installer.py (3 lines):
        # Line 1: drive_letter
        # Line 2: ailab_path (empty if None)
        # Line 3: drive_type (Internal/External/Other)
        print(drive_letter)
        print(ailab_path if ailab_path else "")
        print(drive_type)
        sys.exit(0)
    else:
        print("\nDrive selection cancelled or failed.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

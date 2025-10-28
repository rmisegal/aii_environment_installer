#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automated Uninstaller - Intelligent path detection and complete AI Environment removal
Version: 2.0 - Automated Path Detection
"""

import os
import sys
import json
import shutil
import logging
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

class AutomatedUninstaller:
    """Automated uninstaller with intelligent path detection"""

    def __init__(self, installer_dir: Path = None):
        """
        Initialize automated uninstaller

        Args:
            installer_dir: Path to installer directory (auto-detected if None)
        """
        self.installer_dir = installer_dir or Path(__file__).parent.parent
        self.logger = self._setup_logging()

        # Detection results
        self.detected_installations = []
        self.selected_installation = None

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for uninstaller"""
        log_dir = self.installer_dir / "logs"
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / f"uninstall_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )

        return logging.getLogger(__name__)

    # ========================================
    # PHASE 1.1: Primary Detection - installation_status.json
    # ========================================

    def detect_from_status_file(self) -> Optional[Tuple[Path, Optional[Path]]]:
        """
        Primary detection method: Read installation paths from master_installation_status.json

        Returns:
            Tuple of (AI_Environment path, AI_Lab path) if found, None otherwise
        """
        try:
            # Look for master status file first (new unified system)
            master_status_file = self.installer_dir / "master_installation_status.json"

            if master_status_file.exists():
                with open(master_status_file, 'r', encoding='utf-8') as f:
                    master_status = json.load(f)

                ai_env_path = None
                ai_lab_path = None

                # Get AI_Environment path
                ai_env_info = master_status.get("ai_environment", {})
                if ai_env_info.get("install_path"):
                    ai_env_path = Path(ai_env_info["install_path"])
                    if ai_env_path.exists():
                        self.logger.info(f"[OK] Found AI_Environment via master status: {ai_env_path}")
                    else:
                        self.logger.warning(f"Master status points to non-existent AI_Environment: {ai_env_path}")
                        ai_env_path = None

                # Get AI_Lab path
                ai_lab_info = master_status.get("ai_lab", {})
                if ai_lab_info.get("install_path"):
                    ai_lab_path = Path(ai_lab_info["install_path"])
                    if ai_lab_path.exists():
                        self.logger.info(f"[OK] Found AI_Lab via master status: {ai_lab_path}")
                    else:
                        self.logger.warning(f"Master status points to non-existent AI_Lab: {ai_lab_path}")
                        ai_lab_path = None

                if ai_env_path or ai_lab_path:
                    return (ai_env_path, ai_lab_path)

            # Fallback: Try legacy installation_status.json
            status_file = self.installer_dir / "installation_status.json"

            if not status_file.exists():
                self.logger.info("No status files found in installer directory")
                return None

            with open(status_file, 'r', encoding='utf-8') as f:
                status = json.load(f)

            install_path = status.get("installation_path")
            if install_path:
                # Normalize path - fix malformed paths like "D:AI_Environment" to "D:\AI_Environment"
                install_path_str = str(install_path)
                if len(install_path_str) > 2 and install_path_str[1] == ':' and install_path_str[2] != '\\':
                    install_path_str = install_path_str[:2] + '\\' + install_path_str[2:]

                install_path = Path(install_path_str)
                if install_path.exists():
                    self.logger.info(f"[OK] Found installation via legacy status file: {install_path}")
                    return (install_path, None)  # No AI_Lab in legacy
                else:
                    self.logger.warning(f"Status file points to non-existent path: {install_path}")

            return None

        except Exception as e:
            self.logger.warning(f"Error reading status files: {e}")
            return None

    def detect_from_ai_env_status(self, search_path: Path) -> Optional[Dict]:
        """
        Read installation_status.json from AI_Environment directory

        Args:
            search_path: Path to potential AI_Environment directory

        Returns:
            Dict with installation info or None
        """
        try:
            status_file = search_path / "installation_status.json"

            if not status_file.exists():
                return None

            with open(status_file, 'r', encoding='utf-8') as f:
                status = json.load(f)

            return {
                "path": search_path,
                "status": status,
                "installation_id": status.get("installation_id", "unknown"),
                "start_time": status.get("start_time", "unknown"),
                "completed_steps": status.get("completed_steps", []),
            }

        except Exception as e:
            self.logger.debug(f"Error reading status from {search_path}: {e}")
            return None

    # ========================================
    # PHASE 1.2: Fallback Detection - Drive Scanning
    # ========================================

    def scan_drives_for_installations(self) -> Tuple[List[Path], List[Path]]:
        """
        Fallback method: Scan all available drives for AI_Environment and AI_Lab installations
        Checks both external drive (nested) and internal drive (side-by-side) locations

        Returns:
            Tuple of (AI_Environment paths list, AI_Lab paths list)
        """
        self.logger.info("Scanning all available drives for installations...")
        found_ai_env = []
        found_ai_lab = []

        # Scan all possible drive letters
        import string
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"
            drive_path = Path(drive)

            if not drive_path.exists():
                continue

            self.logger.debug(f"Checking drive {letter}:...")

            # Check for AI_Lab at root (could be internal or external installation)
            ai_lab_root = drive_path / "AI_Lab"
            if ai_lab_root.exists() and ai_lab_root.is_dir():
                if self._verify_ai_lab(ai_lab_root):
                    self.logger.info(f"[OK] Found AI_Lab at: {ai_lab_root}")
                    found_ai_lab.append(ai_lab_root)

            # Check for AI_Lab\AI_Environment (external drive nested installation)
            ai_env_nested = drive_path / "AI_Lab" / "AI_Environment"
            if ai_env_nested.exists() and ai_env_nested.is_dir():
                if self._verify_ai_environment(ai_env_nested):
                    self.logger.info(f"[OK] Found AI_Environment at: {ai_env_nested} (nested in AI_Lab)")
                    found_ai_env.append(ai_env_nested)

            # Check for AI_Environment directory at root (internal drive side-by-side installation)
            ai_env_root = drive_path / "AI_Environment"
            if ai_env_root.exists() and ai_env_root.is_dir():
                # Verify it's actually our installation
                if self._verify_ai_environment(ai_env_root):
                    self.logger.info(f"[OK] Found AI_Environment at: {ai_env_root} (at root)")
                    found_ai_env.append(ai_env_root)

            # Also check for installations in common subdirectories (bug workaround)
            # This handles the case where installation happened in installer directory
            common_subdirs = [
                "AI_Environment_Installer-main",
                "AI_Installer",
                "Downloads"
            ]

            for subdir in common_subdirs:
                potential_env_path = drive_path / subdir / "AI_Environment"
                if potential_env_path.exists() and potential_env_path.is_dir():
                    if self._verify_ai_environment(potential_env_path):
                        # Only add if not already found
                        if potential_env_path not in found_ai_env:
                            self.logger.info(f"[OK] Found AI_Environment at: {potential_env_path} (non-standard location)")
                            found_ai_env.append(potential_env_path)

                potential_lab_path = drive_path / subdir / "AI_Lab"
                if potential_lab_path.exists() and potential_lab_path.is_dir():
                    if self._verify_ai_lab(potential_lab_path):
                        # Only add if not already found
                        if potential_lab_path not in found_ai_lab:
                            self.logger.info(f"[OK] Found AI_Lab at: {potential_lab_path} (non-standard location)")
                            found_ai_lab.append(potential_lab_path)

        return (found_ai_env, found_ai_lab)

    def _verify_ai_environment(self, path: Path) -> bool:
        """
        Verify that a directory is actually an AI_Environment installation

        Args:
            path: Path to verify

        Returns:
            True if it's a valid AI_Environment installation
        """
        # Check for signature files/directories
        signatures = [
            "activate_ai_env.bat",      # Activation script
            "installation_info.json",   # Installation metadata
            "installation_status.json", # Status file
        ]

        signature_dirs = [
            "Miniconda",
            "VSCode",
            "Ollama",
        ]

        # At least one signature file should exist
        has_signature_file = any((path / sig).exists() for sig in signatures)

        # At least one signature directory should exist
        has_signature_dir = any((path / sig_dir).exists() for sig_dir in signature_dirs)

        return has_signature_file or has_signature_dir

    def _verify_ai_lab(self, path: Path) -> bool:
        """
        Verify that a directory is actually an AI_Lab installation

        Args:
            path: Path to verify

        Returns:
            True if it's a valid AI_Lab installation
        """
        # Check for AI_Lab signature files
        signatures = [
            "activate_ai_env.py",       # Python activation script
            "run_ai_env.bat",           # Batch launcher
            ".git",                     # Git repository marker
        ]

        signature_dirs = [
            "src",                      # Source directory with Python modules
        ]

        # Check for signature files
        has_signature_file = any((path / sig).exists() for sig in signatures)

        # Check for signature directories
        has_signature_dir = any((path / sig_dir).exists() for sig_dir in signature_dirs)

        # AI_Lab should have Python files in src directory
        src_dir = path / "src"
        has_python_modules = False
        if src_dir.exists() and src_dir.is_dir():
            try:
                py_files = list(src_dir.glob("*.py"))
                has_python_modules = len(py_files) > 0
            except Exception:
                pass

        return (has_signature_file or has_signature_dir) and has_python_modules

    # ========================================
    # PHASE 1.3: Multi-Installation Detection
    # ========================================

    def detect_all_installations(self) -> List[Dict]:
        """
        Comprehensive detection: Find all AI_Environment and AI_Lab installations

        Returns:
            List of installation info dictionaries with both components
        """
        installations = []

        # Method 1: Check master status file in installer directory
        primary_result = self.detect_from_status_file()
        primary_env_path = None
        primary_lab_path = None

        if primary_result:
            primary_env_path, primary_lab_path = primary_result

        # Method 2: Scan drives for additional installations
        scanned_env_list, scanned_lab_list = self.scan_drives_for_installations()

        # Build a set of unique installation "groups" (matching AI_Environment with AI_Lab)
        installation_groups = {}

        # Helper function to normalize paths for comparison
        def normalize_path(p):
            return str(p).replace('\\', '/').lower() if p else None

        # Add primary installation first
        if primary_env_path or primary_lab_path:
            # Determine the installation key (drive letter)
            if primary_env_path:
                key = str(primary_env_path.drive)
            else:
                key = str(primary_lab_path.drive)

            installation_groups[key] = {
                "ai_environment_path": primary_env_path,
                "ai_lab_path": primary_lab_path,
                "detection_method": "status_file",
                "is_primary": True
            }

        # Add scanned AI_Environment installations
        for env_path in scanned_env_list:
            env_norm = normalize_path(env_path)

            # Skip if already in primary
            if primary_env_path and normalize_path(primary_env_path) == env_norm:
                continue

            # Determine drive key
            key = str(env_path.drive)

            if key not in installation_groups:
                installation_groups[key] = {
                    "ai_environment_path": env_path,
                    "ai_lab_path": None,
                    "detection_method": "drive_scan",
                    "is_primary": False
                }
            else:
                # Update existing group
                installation_groups[key]["ai_environment_path"] = env_path

        # Add scanned AI_Lab installations
        for lab_path in scanned_lab_list:
            lab_norm = normalize_path(lab_path)

            # Skip if already in primary
            if primary_lab_path and normalize_path(primary_lab_path) == lab_norm:
                continue

            # Determine drive key
            key = str(lab_path.drive)

            if key not in installation_groups:
                installation_groups[key] = {
                    "ai_environment_path": None,
                    "ai_lab_path": lab_path,
                    "detection_method": "drive_scan",
                    "is_primary": False
                }
            else:
                # Update existing group
                installation_groups[key]["ai_lab_path"] = lab_path

        # Convert groups to installation info list
        for key, group in installation_groups.items():
            env_path = group["ai_environment_path"]
            lab_path = group["ai_lab_path"]

            # Determine installation type (nested vs side-by-side)
            install_type = "unknown"
            if env_path and lab_path:
                # Check if nested (AI_Environment inside AI_Lab)
                try:
                    env_path.relative_to(lab_path)
                    install_type = "external_nested"
                except ValueError:
                    install_type = "internal_side_by_side"
            elif env_path:
                # Check if it's nested in an AI_Lab
                if "AI_Lab" in str(env_path):
                    install_type = "external_nested_partial"
                else:
                    install_type = "internal_env_only"
            elif lab_path:
                install_type = "lab_only"

            # Get status info if available
            env_status = None
            if env_path:
                env_status = self.detect_from_ai_env_status(env_path)

            install_info = {
                "ai_environment_path": env_path,
                "ai_lab_path": lab_path,
                "install_type": install_type,
                "status": env_status.get("status") if env_status else None,
                "installation_id": env_status.get("installation_id", "unknown") if env_status else "unknown",
                "detection_method": group["detection_method"],
                "is_primary": group["is_primary"]
            }

            installations.append(install_info)

        self.detected_installations = installations
        return installations

    def select_installation(self, installations: List[Dict], auto_select: bool = False) -> Optional[Dict]:
        """
        Select which installation to uninstall

        Args:
            installations: List of detected installations
            auto_select: If True, automatically select the first/primary installation

        Returns:
            Selected installation info or None
        """
        if not installations:
            self.logger.error("No installations found")
            return None

        if len(installations) == 1 or auto_select:
            # Only one installation or auto mode
            selected = installations[0]
            env_path = selected.get('ai_environment_path')
            lab_path = selected.get('ai_lab_path')
            self.logger.info(f"Selected installation - AI_Environment: {env_path}, AI_Lab: {lab_path}")
            return selected

        # Multiple installations found - present menu
        print("\n" + "="*60)
        print("Multiple installations detected:")
        print("="*60)

        for i, install in enumerate(installations, 1):
            env_path = install.get('ai_environment_path')
            lab_path = install.get('ai_lab_path')
            install_type = install.get('install_type', 'unknown')

            print(f"\n{i}. Installation on {env_path.drive if env_path else lab_path.drive}")

            if env_path:
                print(f"   AI_Environment: {env_path}")
            else:
                print(f"   AI_Environment: Not found")

            if lab_path:
                print(f"   AI_Lab: {lab_path}")
            else:
                print(f"   AI_Lab: Not found")

            print(f"   Type: {install_type}")
            print(f"   Installation ID: {install.get('installation_id', 'unknown')}")
            print(f"   Detection Method: {install.get('detection_method', 'unknown')}")

            if install.get('is_primary'):
                print(f"   [PRIMARY - matches installer status file]")

        print("\n" + "="*60)
        print("0. Cancel uninstall")
        print("A. Uninstall ALL detected installations")
        print("="*60)

        while True:
            choice = input("\nSelect installation to uninstall (0-{}/A): ".format(len(installations))).strip().upper()

            if choice == '0':
                self.logger.info("Uninstall cancelled by user")
                return None

            if choice == 'A':
                self.logger.info("User selected to uninstall ALL installations")
                return {"uninstall_all": True, "installations": installations}

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(installations):
                    selected = installations[idx]
                    env_path = selected.get('ai_environment_path')
                    lab_path = selected.get('ai_lab_path')
                    self.logger.info(f"User selected - AI_Environment: {env_path}, AI_Lab: {lab_path}")
                    return selected
            except ValueError:
                pass

            print("Invalid choice. Please try again.")

    # ========================================
    # Path Detection Main Entry Point
    # ========================================

    def detect_installation_path(self, auto_select: bool = False) -> Optional[Dict]:
        """
        Main entry point for path detection

        Args:
            auto_select: If True, automatically select first installation

        Returns:
            Selected installation info or None
        """
        self.logger.info("Starting installation detection...")

        # Detect all installations
        installations = self.detect_all_installations()

        if not installations:
            self.logger.info("No installations found")
            print("\n[INFO] No AI_Environment or AI_Lab installations detected")
            print("\nSearched locations:")
            print("  - Installer directory master status file")
            print("  - All available drives (A-Z)")
            print("    * AI_Lab: Drive:\\AI_Lab")
            print("    * External (nested): Drive:\\AI_Lab\\AI_Environment")
            print("    * Internal (side-by-side): Drive:\\AI_Environment")
            print("\n[OK] System is clean - no installations to remove")
            print("\nIf you know the installation location, use: uninstall.bat --path <path>")
            return None

        # Select installation to uninstall
        selected = self.select_installation(installations, auto_select)

        if selected:
            self.selected_installation = selected

        return selected

    # ========================================
    # PHASE 2: Uninstall Execution
    # ========================================

    def create_uninstall_plan(self, install_info: Dict, options: Dict) -> Dict:
        """
        Create detailed uninstall plan based on installation state
        Handles both AI_Environment and AI_Lab removal

        Args:
            install_info: Installation information from detection
            options: Uninstall options (keep_projects, backup, etc.)

        Returns:
            Uninstall plan dictionary
        """
        ai_env_path = install_info.get('ai_environment_path')
        ai_lab_path = install_info.get('ai_lab_path')
        install_type = install_info.get('install_type', 'unknown')
        status = install_info.get('status', {})
        pre_state = status.get('pre_install_state', {}) if status else {}

        plan = {
            "ai_environment_path": ai_env_path,
            "ai_lab_path": ai_lab_path,
            "install_type": install_type,
            "to_remove": [],
            "to_preserve": [],
            "backup_needed": [],
            "pre_existing": [],
            "warnings": [],
            "removal_order": []  # Order in which to remove components
        }

        # Determine removal order based on installation type
        # For nested: Remove AI_Environment first, then AI_Lab
        # For side-by-side: Remove both independently (order doesn't matter)
        if install_type == "external_nested":
            if ai_env_path:
                plan["removal_order"].append(("ai_environment", ai_env_path))
            if ai_lab_path:
                plan["removal_order"].append(("ai_lab", ai_lab_path))
        elif install_type == "external_nested_partial":
            # AI_Environment is nested in AI_Lab, but AI_Lab not detected
            # Remove AI_Environment only
            if ai_env_path:
                plan["removal_order"].append(("ai_environment", ai_env_path))
        else:
            # Internal side-by-side or single component
            # Order doesn't matter, but remove AI_Environment first by convention
            if ai_env_path:
                plan["removal_order"].append(("ai_environment", ai_env_path))
            if ai_lab_path:
                plan["removal_order"].append(("ai_lab", ai_lab_path))

        # ===== AI_Environment Removal Plan =====
        if ai_env_path:
            # Directories created by AI_Environment installer
            env_dirs = [
                "Miniconda",
                "VSCode",
                "Ollama",
                "Models",
                "Tools",
                "Scripts",
                "Logs",
                "Projects",
                "downloads"
            ]

            # Check each directory
            for dir_name in env_dirs:
                dir_path = ai_env_path / dir_name

                if not dir_path.exists():
                    continue

                # Check if this existed before installation
                existing_subdirs = pre_state.get('existing_subdirs', [])

                if dir_name in existing_subdirs:
                    plan["pre_existing"].append(str(dir_path))
                    plan["to_preserve"].append(str(dir_path))
                    plan["warnings"].append(f"Preserving pre-existing directory: {dir_name}")
                elif dir_name == "Projects" and options.get('keep_projects', False):
                    # Only preserve user projects if explicitly requested
                    plan["to_preserve"].append(str(dir_path))
                    plan["warnings"].append(f"Preserving user projects in: {dir_name}")
                    if options.get('backup', False):
                        plan["backup_needed"].append(str(dir_path))
                else:
                    plan["to_remove"].append(str(dir_path))

            # AI_Environment metadata files to remove
            env_metadata_files = [
                "installation_status.json",
                "installation_info.json",
                "activate_ai_env.bat",
                "README.md",
                "validation_report.json"  # Created by validate.bat
            ]

            for file_name in env_metadata_files:
                file_path = ai_env_path / file_name
                if file_path.exists():
                    plan["to_remove"].append(str(file_path))

            # Check for any remaining files in AI_Environment (catch-all)
            try:
                for item in ai_env_path.iterdir():
                    item_str = str(item)
                    # If it's not already in to_remove or to_preserve lists, add it
                    if item_str not in plan["to_remove"] and item_str not in plan["to_preserve"]:
                        if item.is_file():
                            plan["to_remove"].append(item_str)
                            self.logger.warning(f"Found unlisted AI_Environment file to remove: {item.name}")
            except Exception as e:
                self.logger.debug(f"Error scanning AI_Environment for remaining files: {e}")

        # Check for pre-existing Conda installation (AI_Environment only)
        conda_info = pre_state.get('conda_installations', {})

        if conda_info.get('allusers_exists'):
            # Conda was already installed - don't remove it
            allusers_path = Path(conda_info.get('allusers_path', 'C:/ProgramData/miniconda3'))
            plan["pre_existing"].append(str(allusers_path))
            plan["to_preserve"].append(str(allusers_path))
            plan["warnings"].append(f"Preserving pre-existing Conda at: {allusers_path}")

            # Mark AI2025 environment for conda-based removal
            ai2025_env = allusers_path / "envs" / "AI2025"
            if ai2025_env.exists():
                # Store this separately for conda command removal
                plan["conda_env_to_remove"] = "AI2025"
                plan["conda_path"] = str(allusers_path)
        else:
            plan["conda_env_to_remove"] = None
            plan["conda_path"] = None

        # ===== AI_Lab Removal Plan =====
        if ai_lab_path:
            # AI_Lab is a Git repository clone, so we can remove it entirely
            # But first, check if AI_Environment is nested inside (and not yet removed)
            is_nested = False
            if ai_env_path:
                try:
                    ai_env_path.relative_to(ai_lab_path)
                    is_nested = True
                    plan["warnings"].append(f"AI_Environment is nested inside AI_Lab - will remove in correct order")
                except ValueError:
                    is_nested = False

            # AI_Lab should be removed entirely
            if ai_lab_path.exists():
                try:
                    # Check if it's a git repository
                    git_dir = ai_lab_path / ".git"
                    is_git_repo = git_dir.exists()

                    if is_git_repo:
                        # It's a git repository - normal situation, no need to warn about files
                        self.logger.info(f"AI_Lab is a git repository, will remove entirely")
                        plan["to_remove"].append(str(ai_lab_path))
                    else:
                        # Not a git repo - unexpected, but still remove
                        self.logger.warning(f"AI_Lab is not a git repository")
                        plan["warnings"].append("AI_Lab is not a git repository (unexpected)")
                        plan["to_remove"].append(str(ai_lab_path))

                except Exception as e:
                    self.logger.debug(f"Error scanning AI_Lab directory: {e}")
                    # Still mark for removal
                    plan["to_remove"].append(str(ai_lab_path))

        return plan

    def backup_before_uninstall(self, install_path: Path, backup_items: List[str]) -> Optional[Path]:
        """
        Create backup of specified items before uninstall

        Args:
            install_path: Installation path
            backup_items: List of items to backup

        Returns:
            Path to backup directory or None
        """
        try:
            if not backup_items:
                self.logger.info("No items to backup")
                return None

            # Create backup directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = install_path.parent / f"AI_Environment_Backup_{timestamp}"
            backup_dir.mkdir(exist_ok=True)

            self.logger.info(f"Creating backup at: {backup_dir}")
            print(f"\n[BACKUP] Creating backup at: {backup_dir}")

            backed_up = 0
            for item_str in backup_items:
                item_path = Path(item_str)

                if not item_path.exists():
                    continue

                # Calculate relative path for backup structure
                rel_path = item_path.relative_to(install_path)
                backup_path = backup_dir / rel_path

                # Copy item to backup
                if item_path.is_file():
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item_path, backup_path)
                    backed_up += 1
                    print(f"  [OK] Backed up: {rel_path}")
                elif item_path.is_dir():
                    shutil.copytree(item_path, backup_path, dirs_exist_ok=True)
                    backed_up += 1
                    print(f"  [OK] Backed up: {rel_path}/")

            self.logger.info(f"Backup completed: {backed_up} items")
            print(f"\n[OK] Backup completed: {backed_up} items backed up")

            return backup_dir

        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            print(f"\n[ERROR] Backup failed: {e}")
            return None

    def remove_conda_environment(self, env_name: str, conda_path: str) -> bool:
        """
        Remove conda environment using conda command

        Args:
            env_name: Name of environment to remove
            conda_path: Path to conda installation

        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"\n[CLEANUP] Removing conda environment: {env_name}")
            self.logger.info(f"Removing conda environment: {env_name}")

            # Find conda executable
            conda_exe = Path(conda_path) / "Scripts" / "conda.exe"
            if not conda_exe.exists():
                conda_exe = Path(conda_path) / "condabin" / "conda.bat"

            if not conda_exe.exists():
                self.logger.warning(f"Could not find conda executable at {conda_path}")
                print(f"  [WARN] Could not find conda executable, will try direct removal")
                return False

            # Run conda env remove command
            result = subprocess.run(
                [str(conda_exe), "env", "remove", "-n", env_name, "-y"],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                print(f"  [OK] Successfully removed conda environment: {env_name}")
                self.logger.info(f"Successfully removed conda environment: {env_name}")
                return True
            else:
                self.logger.warning(f"Conda remove failed: {result.stderr}")
                print(f"  [WARN] Conda removal had issues, will try direct removal")
                return False

        except subprocess.TimeoutExpired:
            self.logger.error(f"Conda environment removal timed out")
            print(f"  [ERROR] Conda removal timed out")
            return False
        except Exception as e:
            self.logger.error(f"Error removing conda environment: {e}")
            print(f"  [WARN] Could not remove via conda: {e}")
            return False

    def stop_running_processes(self):
        """Stop all AI Environment related processes"""
        try:
            self.logger.info("Stopping AI Environment processes...")
            print("\n[CLEANUP] Stopping running processes...")

            # Get current process ID to avoid killing ourselves
            import os
            current_pid = os.getpid()

            processes = [
                "ollama.exe",
                "Code.exe",
                "jupyter.exe",
                "jupyter-lab.exe",
                "streamlit.exe"
            ]

            stopped = 0
            for process in processes:
                try:
                    result = subprocess.run(
                        ["taskkill", "/F", "/IM", process],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        stopped += 1
                        print(f"  [OK] Stopped: {process}")
                except Exception as e:
                    self.logger.debug(f"Could not stop {process}: {e}")

            if stopped > 0:
                self.logger.info(f"Stopped {stopped} processes")
                print(f"\n[OK] Stopped {stopped} running processes")
            else:
                print(f"  [INFO] No AI Environment processes running")

        except Exception as e:
            self.logger.warning(f"Error stopping processes: {e}")

    def _remove_directory_robust(self, dir_path: Path) -> bool:
        """
        Robustly remove a directory, handling Git repositories on Windows

        Args:
            dir_path: Path to directory to remove

        Returns:
            True if successfully removed, False otherwise
        """
        try:
            import platform

            # On Windows, use PowerShell for better handling of Git repositories
            if platform.system() == "Windows":
                self.logger.debug(f"Using PowerShell to remove: {dir_path}")
                result = subprocess.run(
                    [
                        "powershell", "-Command",
                        f"Remove-Item -Path '{dir_path}' -Recurse -Force -ErrorAction Stop"
                    ],
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if result.returncode == 0 and not dir_path.exists():
                    return True
                else:
                    self.logger.warning(f"PowerShell removal returned code {result.returncode}: {result.stderr}")
                    # Fall through to try shutil.rmtree

            # Fallback to shutil.rmtree (Unix or if PowerShell failed)
            shutil.rmtree(dir_path, ignore_errors=False)
            return not dir_path.exists()

        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout removing directory: {dir_path}")
            return False
        except Exception as e:
            self.logger.error(f"Error removing directory {dir_path}: {e}")
            # Last resort - try with ignore_errors
            try:
                shutil.rmtree(dir_path, ignore_errors=True)
                return not dir_path.exists()
            except:
                return False

    def execute_uninstall(self, install_info: Dict, plan: Dict, options: Dict) -> bool:
        """
        Execute uninstall based on plan
        Handles both AI_Environment and AI_Lab removal in correct order

        Args:
            install_info: Installation information
            plan: Uninstall plan from create_uninstall_plan()
            options: Uninstall options

        Returns:
            True if successful, False otherwise
        """
        try:
            ai_env_path = plan.get('ai_environment_path')
            ai_lab_path = plan.get('ai_lab_path')
            install_type = plan.get('install_type', 'unknown')

            print("\n" + "="*60)
            print("UNINSTALL EXECUTION")
            print("="*60)
            if ai_env_path:
                print(f"\nAI_Environment: {ai_env_path}")
            if ai_lab_path:
                print(f"AI_Lab: {ai_lab_path}")
            print(f"Installation Type: {install_type}")
            print(f"Items to remove: {len(plan['to_remove'])}")
            print(f"Items to preserve: {len(plan['to_preserve'])}")

            # Show warnings
            if plan['warnings']:
                print(f"\nWarnings:")
                for warning in plan['warnings']:
                    print(f"  [WARN] {warning}")

            # Confirmation unless auto mode
            if not options.get('auto', False):
                print("\n" + "="*60)
                print("The following will be PERMANENTLY DELETED:")
                for item in plan['to_remove'][:10]:  # Show first 10
                    print(f"  - {item}")
                if len(plan['to_remove']) > 10:
                    print(f"  ... and {len(plan['to_remove']) - 10} more items")

                print("\nThe following will be PRESERVED:")
                for item in plan['to_preserve'][:5]:  # Show first 5
                    print(f"  + {item}")
                if len(plan['to_preserve']) > 5:
                    print(f"  ... and {len(plan['to_preserve']) - 5} more items")

                print("\n" + "="*60)
                response = input("\nProceed with uninstall? (yes/no): ").strip().lower()
                if response not in ['yes', 'y']:
                    print("\n[CANCELLED] Uninstall cancelled by user")
                    return False

            # Step 1: Stop processes
            self.stop_running_processes()

            # Step 2: Remove conda environment if needed (before backup)
            if plan.get('conda_env_to_remove'):
                env_name = plan['conda_env_to_remove']
                conda_path = plan['conda_path']
                self.remove_conda_environment(env_name, conda_path)

            # Step 3: Backup if requested
            backup_dir = None
            if options.get('backup', False) and plan['backup_needed']:
                # Use AI_Environment path for backup location (if available)
                backup_base = ai_env_path if ai_env_path else (ai_lab_path.parent if ai_lab_path else Path.cwd())
                backup_dir = self.backup_before_uninstall(backup_base, plan['backup_needed'])
                if backup_dir:
                    print(f"\n[OK] Backup created at: {backup_dir}")

            # Step 4: Remove items in correct order
            print("\n[UNINSTALL] Removing installed components...")
            removed_count = 0
            failed_count = 0

            # Remove items from plan (subdirectories, files, but NOT the root directories yet)
            for item_str in plan['to_remove']:
                item_path = Path(item_str)

                # Skip root directories (AI_Environment and AI_Lab) - handle them later
                if ai_env_path and item_path == ai_env_path:
                    continue
                if ai_lab_path and item_path == ai_lab_path:
                    continue

                if not item_path.exists():
                    continue

                try:
                    if item_path.is_file():
                        item_path.unlink()
                        removed_count += 1
                        print(f"  [OK] Removed file: {item_path.name}")
                    elif item_path.is_dir():
                        shutil.rmtree(item_path, ignore_errors=True)
                        if not item_path.exists():
                            removed_count += 1
                            print(f"  [OK] Removed directory: {item_path.name}/")
                        else:
                            failed_count += 1
                            print(f"  [WARN] Could not fully remove: {item_path.name}/")
                except Exception as e:
                    failed_count += 1
                    self.logger.error(f"Failed to remove {item_path}: {e}")
                    print(f"  [ERROR] Failed to remove: {item_path.name}")

            # Step 5: Remove root directories in correct order
            # Follow the removal_order from plan
            for component_type, component_path in plan.get('removal_order', []):
                if not component_path or not component_path.exists():
                    continue

                try:
                    # Check for remaining items
                    remaining = list(component_path.iterdir())

                    if not remaining:
                        # Completely empty - remove it
                        print(f"\n[CLEANUP] Removing empty {component_type} directory: {component_path}")
                        component_path.rmdir()
                        print(f"[OK] Removed {component_type} directory")
                        self.logger.info(f"Removed {component_type} directory: {component_path}")
                        removed_count += 1
                    elif component_type == "ai_environment" and options.get('keep_projects', False):
                        # Check if only Projects folder remains
                        remaining_names = [item.name for item in remaining]
                        if remaining_names == ['Projects'] or set(remaining_names) <= {'Projects', 'README.md'}:
                            # Only Projects (and maybe README) remain
                            print(f"\n[INFO] AI_Environment directory contains only preserved items: {', '.join(remaining_names)}")
                            print(f"[INFO] Directory location: {component_path}")
                            print(f"\nNote: You can manually delete this folder or move Projects/ elsewhere if needed.")
                        else:
                            print(f"\n[INFO] AI_Environment directory kept (contains {len(remaining)} items: {', '.join(remaining_names)})")
                    elif component_type == "ai_lab":
                        # AI_Lab should be completely removed (it's just a git clone)
                        # But check if AI_Environment is still nested inside
                        if ai_env_path:
                            try:
                                ai_env_path.relative_to(component_path)
                                # AI_Environment is nested - check if it still exists
                                if ai_env_path.exists():
                                    print(f"\n[INFO] AI_Lab directory still contains AI_Environment - skipping AI_Lab removal")
                                    print(f"[INFO] Directory location: {component_path}")
                                    continue
                            except ValueError:
                                pass  # Not nested

                        # Remove AI_Lab completely
                        print(f"\n[CLEANUP] Removing {component_type} directory: {component_path}")
                        if self._remove_directory_robust(component_path):
                            print(f"[OK] Removed {component_type} directory")
                            self.logger.info(f"Removed {component_type} directory: {component_path}")
                            removed_count += 1
                        else:
                            failed_count += 1
                            print(f"[WARN] Could not fully remove {component_type} directory")
                    else:
                        # Some items remain
                        remaining_names = [item.name for item in remaining]
                        print(f"\n[WARN] {component_type} directory not empty (contains {len(remaining)} items):")
                        for name in remaining_names[:10]:
                            print(f"  - {name}")
                        if len(remaining_names) > 10:
                            print(f"  ... and {len(remaining_names) - 10} more")
                        print(f"\n[INFO] Directory location: {component_path}")
                        print(f"[INFO] You may need to manually remove this directory")

                except PermissionError as e:
                    failed_count += 1
                    self.logger.error(f"Permission denied removing {component_type} directory {component_path}: {e}")
                    print(f"\n[ERROR] Permission denied - cannot remove {component_type} directory: {component_path}")
                    print(f"[INFO] You may need to manually delete this folder as administrator")
                except Exception as e:
                    failed_count += 1
                    self.logger.warning(f"Could not remove {component_type} directory: {e}")
                    print(f"\n[WARN] Could not remove {component_type} directory {component_path}: {e}")

            # Step 6: Summary
            print("\n" + "="*60)
            print("UNINSTALL SUMMARY")
            print("="*60)
            print(f"Items removed: {removed_count}")
            print(f"Items failed: {failed_count}")
            print(f"Items preserved: {len(plan['to_preserve'])}")

            if backup_dir:
                print(f"Backup location: {backup_dir}")

            success = failed_count == 0
            if success:
                print("\n[OK] Uninstall completed successfully!")
            else:
                print("\n[WARN] Uninstall completed with some errors")

            self.logger.info(f"Uninstall completed: {removed_count} removed, {failed_count} failed")
            return success

        except Exception as e:
            self.logger.error(f"Uninstall execution failed: {e}")
            print(f"\n[ERROR] Uninstall failed: {e}")
            return False

    def verify_complete_removal(self, plan: Dict) -> bool:
        """
        Verify that uninstall was successful

        Args:
            plan: Uninstall plan that was executed

        Returns:
            True if verification passed
        """
        try:
            print("\n[VERIFY] Checking uninstall completeness...")

            issues = []

            # Check that removed items are actually gone
            for item_str in plan['to_remove']:
                item_path = Path(item_str)
                if item_path.exists():
                    issues.append(f"Still exists: {item_path}")

            # Check that preserved items are still there
            for item_str in plan['to_preserve']:
                item_path = Path(item_str)
                if not item_path.exists():
                    issues.append(f"Preserved item missing: {item_path}")

            # Check that root directories are removed
            ai_env_path = plan.get('ai_environment_path')
            ai_lab_path = plan.get('ai_lab_path')

            if ai_env_path and ai_env_path.exists():
                # Check if we're keeping projects
                if ai_env_path.exists():
                    remaining = list(ai_env_path.iterdir())
                    if remaining and not any('Projects' in item.name for item in remaining):
                        issues.append(f"AI_Environment directory still exists with unexpected content: {ai_env_path}")

            if ai_lab_path and ai_lab_path.exists():
                # AI_Lab should be completely gone unless AI_Environment is still nested
                if ai_env_path:
                    try:
                        ai_env_path.relative_to(ai_lab_path)
                        # Nested - AI_Lab might remain if AI_Environment wasn't fully removed
                    except ValueError:
                        # Not nested - AI_Lab should be gone
                        issues.append(f"AI_Lab directory still exists: {ai_lab_path}")
                else:
                    issues.append(f"AI_Lab directory still exists: {ai_lab_path}")

            if issues:
                print(f"\n[WARN] Verification found {len(issues)} issues:")
                for issue in issues[:5]:
                    print(f"  - {issue}")
                if len(issues) > 5:
                    print(f"  ... and {len(issues) - 5} more")
                return False
            else:
                print("[OK] Verification passed - uninstall complete")
                return True

        except Exception as e:
            self.logger.error(f"Verification failed: {e}")
            return False

    # ========================================
    # Utility Methods
    # ========================================

    def get_installation_summary(self, install_info: Dict) -> str:
        """Generate human-readable installation summary"""
        lines = ["\nInstallation Summary:"]

        ai_env_path = install_info.get('ai_environment_path')
        ai_lab_path = install_info.get('ai_lab_path')
        install_type = install_info.get('install_type', 'unknown')

        if ai_env_path:
            lines.append(f"  AI_Environment: {ai_env_path}")
        if ai_lab_path:
            lines.append(f"  AI_Lab: {ai_lab_path}")

        lines.append(f"  Installation Type: {install_type}")
        lines.append(f"  Installation ID: {install_info.get('installation_id', 'unknown')}")

        status = install_info.get('status', {})
        if status:
            completed = len(status.get('completed_steps', []))
            total = status.get('total_steps', 8)
            lines.append(f"  AI_Environment Progress: {completed}/{total} steps completed")

        return "\n".join(lines)


def main():
    """Main entry point for automated uninstaller"""
    parser = argparse.ArgumentParser(
        description="Automated AI Environment Uninstaller with Path Detection"
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Fully automated mode (no prompts)"
    )
    parser.add_argument(
        "--path",
        type=str,
        help="Specific installation path to uninstall"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be uninstalled without actually removing anything"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all detected installations and exit"
    )
    parser.add_argument(
        "--keep-projects",
        action="store_true",
        help="Keep user projects in Projects/ directory (default: delete everything)"
    )
    parser.add_argument(
        "--delete-projects",
        action="store_true",
        help="Delete user projects (deprecated - this is now the default behavior)"
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create backup before uninstall"
    )

    args = parser.parse_args()

    try:
        # Initialize uninstaller
        uninstaller = AutomatedUninstaller()

        # List mode - just show installations
        if args.list:
            print("\n" + "="*60)
            print("Detecting AI_Environment Installations...")
            print("="*60)

            installations = uninstaller.detect_all_installations()

            if not installations:
                print("\n[ERROR] No installations found")
                return 1

            print(f"\n[OK] Found {len(installations)} installation(s):\n")
            for i, install in enumerate(installations, 1):
                env_path = install.get('ai_environment_path')
                lab_path = install.get('ai_lab_path')
                print(f"{i}. Installation:")
                if env_path:
                    print(f"   AI_Environment: {env_path}")
                if lab_path:
                    print(f"   AI_Lab: {lab_path}")
                print(f"   ID: {install.get('installation_id', 'unknown')}")
                print(f"   Type: {install.get('install_type', 'unknown')}")
                if install.get('is_primary'):
                    print("   [PRIMARY]")
                print()

            return 0

        # Specific path provided
        if args.path:
            install_path = Path(args.path)
            if not install_path.exists():
                print(f"[ERROR] Path does not exist: {install_path}")
                return 1

            # Check if it's AI_Environment or AI_Lab
            is_ai_env = uninstaller._verify_ai_environment(install_path)
            is_ai_lab = uninstaller._verify_ai_lab(install_path)

            if not is_ai_env and not is_ai_lab:
                print(f"[ERROR] Path does not appear to be an AI_Environment or AI_Lab installation: {install_path}")
                return 1

            # Create installation info based on what we found
            env_status = uninstaller.detect_from_ai_env_status(install_path) if is_ai_env else None

            selected = {
                "ai_environment_path": install_path if is_ai_env else None,
                "ai_lab_path": install_path if is_ai_lab else None,
                "install_type": "user_specified",
                "status": env_status.get("status") if env_status else None,
                "installation_id": env_status.get("installation_id", "unknown") if env_status else "unknown",
                "detection_method": "user_specified",
                "is_primary": False
            }
        else:
            # Auto-detect installation
            selected = uninstaller.detect_installation_path(auto_select=args.auto)

        if not selected:
            return 1

        # Prepare options
        options = {
            'auto': args.auto,
            'keep_projects': args.keep_projects,  # Default to False - delete everything unless --keep-projects
            'backup': args.backup,
            'dry_run': args.dry_run
        }

        # Handle uninstall all
        if selected.get('uninstall_all'):
            print("\n[INFO] Uninstalling ALL detected installations...")
            all_success = True

            for install in selected['installations']:
                print(f"\n{'='*60}")
                print(f"Processing: {install['path']}")
                print(f"{'='*60}")

                # Create uninstall plan
                plan = uninstaller.create_uninstall_plan(install, options)

                if args.dry_run:
                    print("\n[DRY RUN] Would remove:")
                    for item in plan['to_remove'][:10]:
                        print(f"  - {item}")
                    if len(plan['to_remove']) > 10:
                        print(f"  ... and {len(plan['to_remove']) - 10} more")
                    continue

                # Execute uninstall
                success = uninstaller.execute_uninstall(install, plan, options)
                if success:
                    uninstaller.verify_complete_removal(plan)
                all_success = all_success and success

            return 0 if all_success else 1

        # Single installation uninstall
        # Show what we found
        print(uninstaller.get_installation_summary(selected))

        # Create uninstall plan
        print("\n[PLAN] Creating uninstall plan...")
        plan = uninstaller.create_uninstall_plan(selected, options)

        print(f"\nPlan created:")
        print(f"  Items to remove: {len(plan['to_remove'])}")
        print(f"  Items to preserve: {len(plan['to_preserve'])}")
        print(f"  Pre-existing items: {len(plan['pre_existing'])}")

        if args.dry_run:
            print("\n" + "="*60)
            print("[DRY RUN MODE - No files will be deleted]")
            print("="*60)

            print("\nWould REMOVE:")
            for item in plan['to_remove'][:15]:
                print(f"  - {item}")
            if len(plan['to_remove']) > 15:
                print(f"  ... and {len(plan['to_remove']) - 15} more items")

            print("\nWould PRESERVE:")
            for item in plan['to_preserve'][:10]:
                print(f"  + {item}")
            if len(plan['to_preserve']) > 10:
                print(f"  ... and {len(plan['to_preserve']) - 10} more items")

            if plan['warnings']:
                print("\nWARNINGS:")
                for warning in plan['warnings']:
                    print(f"  [WARN] {warning}")

            print("\n[INFO] Dry run complete - no changes made")
            return 0

        # Execute uninstall
        success = uninstaller.execute_uninstall(selected, plan, options)

        if success:
            # Verify uninstall
            verified = uninstaller.verify_complete_removal(plan)
            return 0 if verified else 1
        else:
            return 1

    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Uninstall cancelled by user")
        return 1
    except Exception as e:
        print(f"\n[ERROR] {e}")
        logging.error(f"Uninstall failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Master Installation Status Manager
Handles unified status tracking for both AI_Environment and AI_Lab installations
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Literal

# Status type definitions
AIEnvStatus = Literal["No Installation", "AI_Environment_Processing_Installation", "AI_Install_Completed", "Uninstall_Processing"]
AILabStatus = Literal["No Installation", "AI_Environment_Processing_Installation", "AI_Install_Completed", "Uninstall_Processing"]


class InstallationStatusManager:
    """Manages unified installation status for AI_Environment and AI_Lab"""

    # Status constants
    STATUS_NO_INSTALLATION = "No Installation"
    STATUS_PROCESSING = "AI_Environment_Processing_Installation"
    STATUS_COMPLETED = "AI_Install_Completed"
    STATUS_UNINSTALLING = "Uninstall_Processing"

    def __init__(self, status_file_path: Optional[Path] = None):
        """
        Initialize status manager

        Args:
            status_file_path: Path to master_installation_status.json
                            If None, will look for it in common locations
        """
        if status_file_path:
            self.status_file = Path(status_file_path)
        else:
            # Try to find existing status file in common locations
            self.status_file = self._find_status_file()

        self.status_data = self._load_status()

    def _find_status_file(self) -> Path:
        """Find existing status file or determine where to create it"""
        # Check current directory first
        current_dir_status = Path.cwd() / "master_installation_status.json"
        if current_dir_status.exists():
            return current_dir_status

        # Check installer directory
        installer_status = Path(__file__).parent.parent / "master_installation_status.json"
        if installer_status.exists():
            return installer_status

        # Default: create in installer directory
        return installer_status

    def _load_status(self) -> Dict:
        """Load status from file or create default structure"""
        if self.status_file.exists():
            try:
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[WARNING] Could not load status file: {e}")
                return self._create_default_status()
        else:
            return self._create_default_status()

    def _create_default_status(self) -> Dict:
        """Create default status structure"""
        return {
            "ai_environment": {
                "status": self.STATUS_NO_INSTALLATION,
                "install_path": None,
                "last_updated": None,
                "version": None,
                "last_step_completed": 0
            },
            "ai_lab": {
                "status": self.STATUS_NO_INSTALLATION,
                "install_path": None,
                "last_updated": None,
                "git_commit": None,
                "repository_url": "https://github.com/rmisegal/AILab.git"
            },
            "installation_context": {
                "drive_letter": None,
                "drive_type": None,
                "install_mode": None
            }
        }

    def _save_status(self):
        """Save current status to file"""
        try:
            # Ensure parent directory exists
            self.status_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(self.status_data, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Could not save status file: {e}")

    # AI_Environment status methods
    def get_ai_environment_status(self) -> str:
        """Get current AI_Environment installation status"""
        return self.status_data["ai_environment"]["status"]

    def set_ai_environment_status(self, status: str, install_path: Optional[str] = None,
                                  version: Optional[str] = None, last_step: Optional[int] = None):
        """
        Update AI_Environment status

        Args:
            status: New status value
            install_path: Installation path (optional)
            version: Version installed (optional)
            last_step: Last completed installation step (optional)
        """
        self.status_data["ai_environment"]["status"] = status
        self.status_data["ai_environment"]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if install_path is not None:
            self.status_data["ai_environment"]["install_path"] = str(install_path)

        if version is not None:
            self.status_data["ai_environment"]["version"] = version

        if last_step is not None:
            self.status_data["ai_environment"]["last_step_completed"] = last_step

        self._save_status()

    def get_ai_environment_last_step(self) -> int:
        """Get last completed installation step for AI_Environment"""
        return self.status_data["ai_environment"].get("last_step_completed", 0)

    def get_ai_environment_path(self) -> Optional[Path]:
        """Get AI_Environment installation path"""
        path_str = self.status_data["ai_environment"].get("install_path")
        return Path(path_str) if path_str else None

    # AI_Lab status methods
    def get_ai_lab_status(self) -> str:
        """Get current AI_Lab installation status"""
        return self.status_data["ai_lab"]["status"]

    def set_ai_lab_status(self, status: str, install_path: Optional[str] = None,
                          git_commit: Optional[str] = None):
        """
        Update AI_Lab status

        Args:
            status: New status value
            install_path: Installation path (optional)
            git_commit: Git commit hash (optional)
        """
        self.status_data["ai_lab"]["status"] = status
        self.status_data["ai_lab"]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if install_path is not None:
            self.status_data["ai_lab"]["install_path"] = str(install_path)

        if git_commit is not None:
            self.status_data["ai_lab"]["git_commit"] = git_commit

        self._save_status()

    def get_ai_lab_path(self) -> Optional[Path]:
        """Get AI_Lab installation path"""
        path_str = self.status_data["ai_lab"].get("install_path")
        return Path(path_str) if path_str else None

    # Installation context methods
    def set_installation_context(self, drive_letter: str, drive_type: str, install_mode: str):
        """
        Set installation context information

        Args:
            drive_letter: Target drive letter (e.g., "F")
            drive_type: "External" or "Internal"
            install_mode: "student" or "standalone"
        """
        self.status_data["installation_context"]["drive_letter"] = drive_letter
        self.status_data["installation_context"]["drive_type"] = drive_type
        self.status_data["installation_context"]["install_mode"] = install_mode
        self._save_status()

    def get_installation_context(self) -> Dict:
        """Get installation context information"""
        return self.status_data["installation_context"]

    # Status checking methods
    def is_ai_environment_installed(self) -> bool:
        """Check if AI_Environment is fully installed"""
        return self.get_ai_environment_status() == self.STATUS_COMPLETED

    def is_ai_lab_installed(self) -> bool:
        """Check if AI_Lab is fully installed"""
        return self.get_ai_lab_status() == self.STATUS_COMPLETED

    def is_ai_environment_installing(self) -> bool:
        """Check if AI_Environment installation is in progress"""
        return self.get_ai_environment_status() == self.STATUS_PROCESSING

    def is_ai_lab_installing(self) -> bool:
        """Check if AI_Lab installation is in progress"""
        return self.get_ai_lab_status() == self.STATUS_PROCESSING

    def has_incomplete_installation(self) -> bool:
        """Check if any component has an incomplete installation"""
        return (self.is_ai_environment_installing() or
                self.is_ai_lab_installing() or
                self.get_ai_environment_status() == self.STATUS_UNINSTALLING or
                self.get_ai_lab_status() == self.STATUS_UNINSTALLING)

    def get_resume_info(self) -> Dict:
        """Get information about what can be resumed"""
        info = {
            "can_resume": False,
            "ai_environment_resume": False,
            "ai_lab_resume": False,
            "ai_environment_last_step": 0,
            "must_complete_uninstall": False
        }

        ai_env_status = self.get_ai_environment_status()
        ai_lab_status = self.get_ai_lab_status()

        # Check for uninstall in progress (must complete)
        if ai_env_status == self.STATUS_UNINSTALLING or ai_lab_status == self.STATUS_UNINSTALLING:
            info["must_complete_uninstall"] = True
            info["can_resume"] = True
            return info

        # Check for installation in progress
        if ai_env_status == self.STATUS_PROCESSING:
            info["ai_environment_resume"] = True
            info["ai_environment_last_step"] = self.get_ai_environment_last_step()
            info["can_resume"] = True

        if ai_lab_status == self.STATUS_PROCESSING:
            info["ai_lab_resume"] = True
            info["can_resume"] = True

        return info

    # Display methods
    def print_status_summary(self):
        """Print formatted status summary"""
        print("\n" + "="*70)
        print("Current Installation Status:")
        print("="*70)

        # AI_Environment status
        ai_env_status = self.get_ai_environment_status()
        ai_env_path = self.get_ai_environment_path()
        print(f"\nAI_Environment:  [{ai_env_status}]")
        if ai_env_path:
            print(f"  Path: {ai_env_path}")
            version = self.status_data["ai_environment"].get("version")
            if version:
                print(f"  Version: {version}")

        # AI_Lab status
        ai_lab_status = self.get_ai_lab_status()
        ai_lab_path = self.get_ai_lab_path()
        print(f"\nAI_Lab:          [{ai_lab_status}]")
        if ai_lab_path:
            print(f"  Path: {ai_lab_path}")
            commit = self.status_data["ai_lab"].get("git_commit")
            if commit:
                print(f"  Git Commit: {commit[:8]}")

        # Installation context
        context = self.get_installation_context()
        if context.get("drive_letter"):
            print(f"\nInstallation Context:")
            print(f"  Drive: {context['drive_letter']}:\\ ({context.get('drive_type', 'Unknown')})")
            print(f"  Mode: {context.get('install_mode', 'Unknown')}")

        print("="*70 + "\n")

    def reset_status(self):
        """Reset all status to No Installation"""
        self.status_data = self._create_default_status()
        self._save_status()


def main():
    """Test the status manager"""
    manager = InstallationStatusManager()

    print("Testing Installation Status Manager")
    print("="*70)

    # Show current status
    manager.print_status_summary()

    # Test setting status
    print("\nTesting status updates...")
    manager.set_ai_lab_status(
        InstallationStatusManager.STATUS_PROCESSING,
        install_path="F:/AI_Lab"
    )
    manager.set_ai_environment_status(
        InstallationStatusManager.STATUS_PROCESSING,
        install_path="F:/AI_Lab/AI_Environment",
        version="3.0.28",
        last_step=3
    )
    manager.set_installation_context("F", "External", "student")

    # Show updated status
    manager.print_status_summary()

    # Test resume info
    resume_info = manager.get_resume_info()
    print("Resume Information:")
    print(json.dumps(resume_info, indent=2))


if __name__ == "__main__":
    main()

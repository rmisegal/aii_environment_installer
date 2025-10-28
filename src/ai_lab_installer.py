#!/usr/bin/env python3
"""
AI_Lab Installer
Handles cloning and validation of the AI_Lab repository from GitHub
"""

import subprocess
import shutil
from pathlib import Path
from typing import Optional, Tuple

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    class Fore:
        GREEN = RED = YELLOW = CYAN = ""
    class Style:
        RESET_ALL = ""


class AILabInstaller:
    """Manages AI_Lab repository installation"""

    REPOSITORY_URL = "https://github.com/rmisegal/AILab.git"

    def __init__(self, target_path: Path):
        """
        Initialize AI_Lab installer

        Args:
            target_path: Where to clone the repository
        """
        self.target_path = Path(target_path)
        self.git_available = False

    def print_info(self, message: str):
        """Print info message"""
        print(f"{Fore.YELLOW}[INFO] {message}{Style.RESET_ALL}")

    def print_success(self, message: str):
        """Print success message"""
        print(f"{Fore.GREEN}[OK] {message}{Style.RESET_ALL}")

    def print_error(self, message: str):
        """Print error message"""
        print(f"{Fore.RED}[ERROR] {message}{Style.RESET_ALL}")

    def print_warning(self, message: str):
        """Print warning message"""
        print(f"{Fore.YELLOW}[WARNING] {message}{Style.RESET_ALL}")

    def check_git_available(self) -> bool:
        """
        Check if git is installed and available

        Returns:
            True if git is available, False otherwise
        """
        try:
            result = subprocess.run(
                ['git', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                version = result.stdout.strip()
                self.print_success(f"Git detected: {version}")
                self.git_available = True
                return True
            else:
                self.git_available = False
                return False

        except FileNotFoundError:
            self.print_error("Git is not installed on your system")
            self.git_available = False
            return False
        except Exception as e:
            self.print_error(f"Error checking git: {e}")
            self.git_available = False
            return False

    def print_git_install_instructions(self):
        """Print instructions for installing Git"""
        print(f"\n{Fore.RED}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.RED}Git is required to install AI_Lab from GitHub{Style.RESET_ALL}")
        print(f"{Fore.RED}{'='*70}{Style.RESET_ALL}\n")
        print("Please follow these steps:\n")
        print("1. Visit: https://git-scm.com/download/win")
        print("2. Download 'Git for Windows'")
        print("3. Run the installer with default settings")
        print("4. Restart this MasterInstall program\n")
        print(f"{Fore.YELLOW}Note: Git is free and open-source{Style.RESET_ALL}\n")

    def check_target_directory(self) -> Tuple[bool, str]:
        """
        Check target directory status

        Returns:
            Tuple of (can_proceed, status_message)
        """
        if not self.target_path.exists():
            return True, "Directory does not exist (will be created)"

        # Check if it's a git repository
        git_dir = self.target_path / ".git"
        if git_dir.exists():
            return True, "Existing git repository found (can resume or overwrite)"

        # Check if directory is empty
        if not any(self.target_path.iterdir()):
            return True, "Directory is empty (ready to clone)"

        # Directory exists and has content
        return False, "Directory exists and contains files (must be cleaned first)"

    def clone_repository(self, force_reclone: bool = False) -> bool:
        """
        Clone AI_Lab repository from GitHub

        Args:
            force_reclone: If True, delete existing directory and reclone

        Returns:
            True if clone successful, False otherwise
        """
        if not self.git_available:
            self.print_error("Git is not available. Cannot clone repository.")
            return False

        # Handle existing directory
        if self.target_path.exists():
            if force_reclone:
                self.print_info(f"Removing existing directory: {self.target_path}")
                try:
                    shutil.rmtree(self.target_path)
                except Exception as e:
                    self.print_error(f"Failed to remove existing directory: {e}")
                    return False
            else:
                git_dir = self.target_path / ".git"
                if git_dir.exists():
                    self.print_info("Git repository already exists. Pulling latest changes...")
                    return self._git_pull()
                else:
                    self.print_error(f"Directory exists but is not a git repository: {self.target_path}")
                    self.print_info("Use force_reclone=True or manually remove the directory")
                    return False

        # Ensure parent directory exists
        self.target_path.parent.mkdir(parents=True, exist_ok=True)

        # Clone the repository
        self.print_info(f"Cloning AI_Lab repository to: {self.target_path}")
        self.print_info(f"Repository: {self.REPOSITORY_URL}")
        print(f"\n{Fore.CYAN}This may take a few minutes depending on your connection...{Style.RESET_ALL}\n")

        try:
            result = subprocess.run(
                ['git', 'clone', self.REPOSITORY_URL, str(self.target_path)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                self.print_success(f"Repository cloned successfully")
                return True
            else:
                self.print_error(f"Git clone failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.print_error("Git clone timed out (network issue or repository too large)")
            return False
        except Exception as e:
            self.print_error(f"Git clone error: {e}")
            return False

    def _git_pull(self) -> bool:
        """Pull latest changes from existing repository"""
        try:
            result = subprocess.run(
                ['git', 'pull'],
                cwd=str(self.target_path),
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                self.print_success("Repository updated successfully")
                return True
            else:
                self.print_warning(f"Git pull had issues: {result.stderr}")
                return True  # Still return True as repository exists
        except Exception as e:
            self.print_warning(f"Could not update repository: {e}")
            return True  # Still return True as repository exists

    def verify_repository(self) -> bool:
        """
        Verify that the cloned repository has the expected structure

        Returns:
            True if verification passes, False otherwise
        """
        self.print_info("Verifying repository structure...")

        if not self.target_path.exists():
            self.print_error(f"Repository directory does not exist: {self.target_path}")
            return False

        # Check for .git directory
        git_dir = self.target_path / ".git"
        if not git_dir.exists():
            self.print_error("Not a valid git repository (.git directory missing)")
            return False
        self.print_success("Git repository verified")

        # Check for critical files
        critical_files = [
            "activate_ai_env.py",
            "run_ai_env.bat",
            "src"
        ]

        all_present = True
        for file in critical_files:
            file_path = self.target_path / file
            if file_path.exists():
                self.print_success(f"Found: {file}")
            else:
                self.print_error(f"Missing: {file}")
                all_present = False

        # Check src directory has Python files
        src_dir = self.target_path / "src"
        if src_dir.exists() and src_dir.is_dir():
            py_files = list(src_dir.glob("*.py"))
            if py_files:
                self.print_success(f"src directory contains {len(py_files)} Python modules")
            else:
                self.print_warning("src directory is empty")
                all_present = False
        else:
            self.print_error("src directory not found or not a directory")
            all_present = False

        if all_present:
            self.print_success("Repository structure verified successfully")
            return True
        else:
            self.print_error("Repository verification failed")
            return False

    def get_git_commit(self) -> Optional[str]:
        """
        Get current git commit hash

        Returns:
            Commit hash or None if unavailable
        """
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=str(self.target_path),
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                commit = result.stdout.strip()
                return commit
            else:
                return None
        except Exception:
            return None

    def install(self, force_reclone: bool = False) -> bool:
        """
        Full installation process

        Args:
            force_reclone: If True, delete and reclone even if repository exists

        Returns:
            True if installation successful, False otherwise
        """
        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}AI_Lab Repository Installation{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

        # Step 1: Check git availability
        if not self.check_git_available():
            self.print_git_install_instructions()
            return False

        # Step 2: Check target directory
        can_proceed, status = self.check_target_directory()
        self.print_info(f"Target directory status: {status}")

        if not can_proceed and not force_reclone:
            self.print_error("Cannot proceed with installation")
            self.print_info("Use force_reclone=True or manually clean the directory")
            return False

        # Step 3: Clone repository
        if not self.clone_repository(force_reclone=force_reclone):
            return False

        # Step 4: Verify repository
        if not self.verify_repository():
            return False

        # Step 5: Get commit info
        commit = self.get_git_commit()
        if commit:
            self.print_info(f"Current commit: {commit[:8]}")

        print(f"\n{Fore.GREEN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}AI_Lab installation completed successfully{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*70}{Style.RESET_ALL}\n")

        return True


def main():
    """Test AI_Lab installer"""
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="AI_Lab Repository Installer")
    parser.add_argument("target_path", help="Target directory for AI_Lab")
    parser.add_argument("--force", action="store_true", help="Force reclone if directory exists")
    args = parser.parse_args()

    installer = AILabInstaller(Path(args.target_path))
    success = installer.install(force_reclone=args.force)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

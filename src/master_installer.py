#!/usr/bin/env python3
"""
Master Installer
Orchestrates installation of both AI_Environment and AI_Lab
"""

import sys
import subprocess
import argparse
from pathlib import Path
from typing import Optional, Tuple

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    class Fore:
        GREEN = RED = YELLOW = CYAN = BLUE = MAGENTA = ""
    class Style:
        RESET_ALL = BRIGHT = ""

# Import our custom modules
from installation_status_manager import InstallationStatusManager
from ai_lab_installer import AILabInstaller


class MasterInstaller:
    """Orchestrates installation of AI_Environment and AI_Lab"""

    VERSION = "3.0.28"

    def __init__(self):
        self.status_manager = InstallationStatusManager()
        self.installer_dir = Path(__file__).parent.parent
        self.selected_drive = None
        self.selected_drive_type = None
        self.ailab_base_path = None
        self.ai_environment_path = None
        self.ai_lab_path = None

    def print_banner(self):
        """Print installer banner"""
        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{Style.BRIGHT}    AI Environment & Lab Master Installer{Style.RESET_ALL}")
        print(f"{Fore.CYAN}    Version {self.VERSION}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

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

    def find_git(self) -> Optional[str]:
        """Find Git in PATH or common locations"""
        import os

        # Try PATH first
        try:
            result = subprocess.run(['git', '--version'], capture_output=True, timeout=10)
            if result.returncode == 0:
                return 'git'  # Found in PATH
        except:
            pass

        # Common Git installation locations
        common_locations = [
            Path(os.environ.get('LOCALAPPDATA', '')) / 'Programs' / 'Git' / 'cmd' / 'git.exe',
            Path(os.environ.get('PROGRAMFILES', '')) / 'Git' / 'cmd' / 'git.exe',
            Path(os.environ.get('PROGRAMFILES(X86)', '')) / 'Git' / 'cmd' / 'git.exe',
        ]

        for git_path in common_locations:
            if git_path.exists():
                return str(git_path)

        return None

    def check_system_requirements(self) -> bool:
        """Check basic system requirements"""
        self.print_info("Checking system requirements...")

        all_good = True

        # Check Git
        git_cmd = self.find_git()
        if git_cmd:
            try:
                result = subprocess.run([git_cmd, '--version'], capture_output=True, timeout=10)
                if result.returncode == 0:
                    git_version = result.stdout.decode().strip()
                    self.print_success(f"Git detected: {git_version}")
                    if git_cmd != 'git':
                        self.print_info(f"Git found at: {git_cmd}")
                else:
                    self.print_warning("Git not in PATH (will be needed for AI_Lab installation)")
            except:
                self.print_warning("Git not in PATH (will be needed for AI_Lab installation)")
        else:
            self.print_warning("Git not detected (will be needed for AI_Lab installation)")

        # Check Python (will be replaced with portable version, but check anyway)
        try:
            result = subprocess.run(['python', '--version'], capture_output=True, timeout=10)
            if result.returncode == 0:
                python_version = result.stdout.decode().strip()
                self.print_success(f"Python detected: {python_version} (will be replaced with portable version)")
        except:
            self.print_warning("Python not detected (portable version will be installed)")

        return all_good

    def show_main_menu(self) -> str:
        """Show main menu and get user choice"""
        print(f"\n{Fore.CYAN}What would you like to do?{Style.RESET_ALL}")
        print(f"[1] Fresh Installation (Install both AI_Environment and AI_Lab)")
        print(f"[2] Install AI_Lab only (requires AI_Environment already installed)")
        print(f"[3] Install AI_Environment only")
        print(f"[4] Resume incomplete installation")
        print(f"[5] Uninstall")
        print(f"[0] Exit\n")

        while True:
            choice = input("Enter choice: ").strip()
            if choice in ['0', '1', '2', '3', '4', '5']:
                return choice
            else:
                self.print_error("Invalid choice. Please enter 0-5.")

    def run_drive_selector(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Run drive selector to let user choose installation drive

        Returns:
            Tuple of (drive_letter, ailab_path, drive_type) or (None, None, None) on failure
        """
        self.print_info("Running drive selector...")

        try:
            drive_selector_script = self.installer_dir / "src" / "drive_selector.py"
            # Only capture stdout (the result), let stderr/stdin pass through for user interaction
            result = subprocess.run(
                ['python', str(drive_selector_script)],
                stdout=subprocess.PIPE,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                # Parse output: line 1 = drive_letter, line 2 = ailab_path, line 3 = drive_type
                lines = result.stdout.strip().split('\n')
                drive_letter = lines[0].strip() if len(lines) > 0 else None
                ailab_path = lines[1].strip() if len(lines) > 1 and lines[1].strip() else None
                drive_type = lines[2].strip() if len(lines) > 2 else "Internal"  # Default to Internal
                return drive_letter, ailab_path, drive_type
            else:
                self.print_error("Drive selector was cancelled or failed")
                return None, None, None

        except subprocess.TimeoutExpired:
            self.print_error("Drive selector timed out")
            return None, None, None
        except KeyboardInterrupt:
            self.print_info("Drive selection cancelled by user")
            return None, None, None
        except Exception as e:
            self.print_error(f"Error running drive selector: {e}")
            return None, None, None

    def determine_installation_paths(self, drive_letter: str, drive_type: str) -> bool:
        """
        Determine where to install based on drive selection

        Args:
            drive_letter: Selected drive letter (e.g., "F")
            drive_type: Drive type ("Internal" or "External")

        Returns:
            True if paths determined successfully
        """
        self.selected_drive = drive_letter
        self.selected_drive_type = drive_type
        drive_root = Path(f"{drive_letter}:/")

        if drive_type == "External":
            # External drive: AI_Lab at root, AI_Environment nested inside
            self.ai_lab_path = drive_root / "AI_Lab"
            self.ai_environment_path = self.ai_lab_path / "AI_Environment"
            self.ailab_base_path = self.ai_lab_path
            install_order = "1. AI_Lab (clone from GitHub)\n                              2. AI_Environment (inside AI_Lab)"
            self.print_info(f"Installation mode: Portable (External Drive)")
        else:
            # Internal drive: Both at root level, side by side
            self.ai_environment_path = drive_root / "AI_Environment"
            self.ai_lab_path = drive_root / "AI_Lab"
            self.ailab_base_path = None  # Not nested
            install_order = "1. AI_Environment (at root)\n                              2. AI_Lab (at root, clone from GitHub)"
            self.print_info(f"Installation mode: Standard (Internal Drive)")

        # Display installation plan
        print(f"\n{Fore.CYAN}Installation Plan:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─'*70}{Style.RESET_ALL}")
        print(f"Drive:                    {drive_letter}:\\ ({drive_type})")
        print(f"Installation Order:       {install_order}")
        print(f"\nFinal Locations:")
        print(f"  AI_Lab:                 {self.ai_lab_path}")
        print(f"  AI_Environment:         {self.ai_environment_path}")
        print(f"{Fore.CYAN}{'─'*70}{Style.RESET_ALL}\n")

        # Confirm with user
        confirm = input("Press Enter to continue or Ctrl+C to cancel...")

        return True

    def install_ai_lab(self, force_reclone: bool = False, phase_label: str = "") -> bool:
        """
        Install AI_Lab repository

        Args:
            force_reclone: Force re-clone even if exists
            phase_label: Optional phase label (e.g., "[Phase 2/3]")

        Returns:
            True if successful
        """
        phase_prefix = f"{phase_label} " if phase_label else ""
        print(f"\n{Fore.CYAN}{phase_prefix}Installing AI_Lab Repository{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

        # Update status to processing
        self.status_manager.set_ai_lab_status(
            InstallationStatusManager.STATUS_PROCESSING,
            install_path=str(self.ai_lab_path)
        )

        # Create installer and run
        installer = AILabInstaller(self.ai_lab_path)
        success = installer.install(force_reclone=force_reclone)

        if success:
            # Get git commit
            commit = installer.get_git_commit()

            # Update status to completed
            self.status_manager.set_ai_lab_status(
                InstallationStatusManager.STATUS_COMPLETED,
                install_path=str(self.ai_lab_path),
                git_commit=commit
            )
            self.print_success("AI_Lab installation completed")
            return True
        else:
            self.print_error("AI_Lab installation failed")
            return False

    def install_ai_environment(self, start_step: int = 1, phase_label: str = "") -> bool:
        """
        Install AI_Environment

        Args:
            start_step: Step to start from (for resume)
            phase_label: Optional phase label (e.g., "[Phase 2/3]")

        Returns:
            True if successful
        """
        phase_prefix = f"{phase_label} " if phase_label else ""
        print(f"\n{Fore.CYAN}{phase_prefix}Installing AI_Environment{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

        # Update status to processing
        self.status_manager.set_ai_environment_status(
            InstallationStatusManager.STATUS_PROCESSING,
            install_path=str(self.ai_environment_path),
            version=self.VERSION,
            last_step=start_step - 1
        )

        # Call existing install_manager.py
        try:
            install_manager_script = self.installer_dir / "src" / "install_manager.py"

            # Build command
            cmd = [
                'python',
                str(install_manager_script),
                '--drive', self.selected_drive,
                '--step', str(start_step)
            ]

            # Add --ailab parameter if installing to AI_Lab folder
            if self.ailab_base_path:
                cmd.extend(['--ailab', str(self.ailab_base_path)])

            self.print_info("Calling AI_Environment installer...")
            self.print_info(f"Command: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                timeout=3600  # 1 hour timeout
            )

            if result.returncode == 0:
                # Update status to completed
                self.status_manager.set_ai_environment_status(
                    InstallationStatusManager.STATUS_COMPLETED,
                    install_path=str(self.ai_environment_path),
                    version=self.VERSION,
                    last_step=8
                )
                self.print_success("AI_Environment installation completed")
                return True
            else:
                self.print_error(f"AI_Environment installation failed with code {result.returncode}")
                return False

        except Exception as e:
            self.print_error(f"Error installing AI_Environment: {e}")
            return False

    def do_fresh_installation(self) -> bool:
        """Perform fresh installation of both components"""
        # Phase 1: Drive Selection
        print(f"\n{Fore.CYAN}[Phase 1/3] Drive Selection{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

        drive_letter, ailab_path, drive_type = self.run_drive_selector()
        if not drive_letter:
            self.print_error("Drive selection failed")
            return False

        # Determine installation paths based on drive type
        if not self.determine_installation_paths(drive_letter, drive_type):
            return False

        # Update installation context
        install_mode = "student" if drive_type == "External" else "standalone"
        self.status_manager.set_installation_context(
            drive_letter,
            drive_type,
            install_mode
        )

        # Install components in correct order based on drive type
        if drive_type == "External":
            # External: AI_Lab first, then AI_Environment inside it
            # Phase 2: Install AI_Lab
            if not self.install_ai_lab(phase_label="[Phase 2/3]"):
                return False

            # Phase 3: Install AI_Environment
            if not self.install_ai_environment(phase_label="[Phase 3/3]"):
                return False
        else:
            # Internal: AI_Environment first, then AI_Lab (both at root)
            # Phase 2: Install AI_Environment
            if not self.install_ai_environment(phase_label="[Phase 2/3]"):
                return False

            # Phase 3: Install AI_Lab
            if not self.install_ai_lab(phase_label="[Phase 3/3]"):
                return False

        # Show completion summary
        self.show_completion_summary()
        return True

    def do_resume_installation(self) -> bool:
        """Resume incomplete installation"""
        resume_info = self.status_manager.get_resume_info()

        if not resume_info["can_resume"]:
            self.print_error("No incomplete installation found to resume")
            return False

        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Resuming Incomplete Installation{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

        # Get paths from status
        ai_env_path_str = self.status_manager.get_ai_environment_path()
        ai_lab_path_str = self.status_manager.get_ai_lab_path()

        if ai_env_path_str:
            self.ai_environment_path = Path(ai_env_path_str)
            # Extract drive letter from AI_Environment path
            self.selected_drive = self.ai_environment_path.drive[0]  # e.g., "F:\\" -> "F"

            # Determine if this is a nested installation (External)
            if "AI_Lab" in str(self.ai_environment_path.parent):
                self.selected_drive_type = "External"
                self.ai_lab_path = self.ai_environment_path.parent
                self.ailab_base_path = self.ai_lab_path
            else:
                self.selected_drive_type = "Internal"
                # AI_Lab would be at root level
                self.ai_lab_path = self.ai_environment_path.parent / "AI_Lab"
                self.ailab_base_path = None

        if ai_lab_path_str and not self.ai_lab_path:
            self.ai_lab_path = Path(ai_lab_path_str)
            if not self.selected_drive:
                self.selected_drive = self.ai_lab_path.drive[0]

        # Show what we're resuming
        if resume_info["ai_lab_resume"]:
            self.print_info(f"Resuming AI_Lab installation at: {self.ai_lab_path}")

        if resume_info["ai_environment_resume"]:
            last_step = resume_info["ai_environment_last_step"]
            self.print_info(f"Resuming AI_Environment installation at: {self.ai_environment_path}")
            self.print_info(f"Last completed step: {last_step}")

        print()
        confirm = input("Press Enter to continue or Ctrl+C to cancel...")

        # Resume AI_Lab first if needed
        if resume_info["ai_lab_resume"]:
            self.print_info("Resuming AI_Lab installation...")
            if not self.install_ai_lab(force_reclone=False):
                self.print_error("Failed to resume AI_Lab installation")
                return False

        # Resume AI_Environment if needed
        if resume_info["ai_environment_resume"]:
            last_step = resume_info["ai_environment_last_step"]
            start_step = last_step + 1
            self.print_info(f"Resuming AI_Environment installation from step {start_step}...")

            if not self.install_ai_environment(start_step=start_step):
                self.print_error("Failed to resume AI_Environment installation")
                return False

        # Show completion summary
        self.show_completion_summary()
        return True

    def do_ailab_only_installation(self) -> bool:
        """Install AI_Lab only (requires AI_Environment already installed)"""
        # Check if AI_Environment is installed
        ai_env_status = self.status_manager.get_ai_environment_status()
        ai_env_path = self.status_manager.get_ai_environment_path()

        if ai_env_status != InstallationStatusManager.STATUS_COMPLETED or not ai_env_path:
            self.print_error("AI_Environment is not installed")
            self.print_info("Please install AI_Environment first (option 1 or 3)")
            return False

        self.print_success(f"Found existing AI_Environment at: {ai_env_path}")

        # Get installation context
        context = self.status_manager.get_installation_context()
        drive_letter = context.get("drive_letter", "D")
        drive_type = context.get("drive_type", "Internal")

        # Set paths
        self.ai_environment_path = Path(ai_env_path)
        self.selected_drive = drive_letter
        self.selected_drive_type = drive_type

        # Determine AI_Lab path based on drive type
        if drive_type == "External":
            # External: AI_Lab is parent of AI_Environment
            self.ai_lab_path = self.ai_environment_path.parent
            self.ailab_base_path = self.ai_lab_path
        else:
            # Internal: AI_Lab is sibling of AI_Environment
            self.ai_lab_path = self.ai_environment_path.parent / "AI_Lab"
            self.ailab_base_path = None

        print(f"\n{Fore.CYAN}Installation Plan:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─'*70}{Style.RESET_ALL}")
        print(f"AI_Environment:           {self.ai_environment_path} (existing)")
        print(f"AI_Lab will be installed: {self.ai_lab_path}")
        print(f"{Fore.CYAN}{'─'*70}{Style.RESET_ALL}\n")

        confirm = input("Press Enter to continue or Ctrl+C to cancel...")

        # Install AI_Lab
        if not self.install_ai_lab():
            return False

        # Show completion summary
        self.show_completion_summary()
        return True

    def show_completion_summary(self):
        """Show installation completion summary"""
        # Check what was actually installed
        ai_env_status = self.status_manager.get_ai_environment_status()
        ai_lab_status = self.status_manager.get_ai_lab_status()

        ai_env_completed = ai_env_status == InstallationStatusManager.STATUS_COMPLETED
        ai_lab_completed = ai_lab_status == InstallationStatusManager.STATUS_COMPLETED

        print(f"\n{Fore.GREEN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{Style.BRIGHT}             Installation Complete!{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*70}{Style.RESET_ALL}\n")

        print(f"{Fore.CYAN}Installation Summary:{Style.RESET_ALL}")

        # Only show what was actually installed
        if ai_env_completed:
            print(f"[OK] AI_Environment installed to: {self.ai_environment_path}")
        if ai_lab_completed:
            print(f"[OK] AI_Lab cloned to: {self.ai_lab_path}")

        if ai_env_completed and ai_lab_completed:
            print(f"[OK] All components verified\n")
        elif ai_env_completed:
            print(f"\n[INFO] AI_Lab was not installed")
            print(f"[INFO] You can install AI_Lab later by running option 2 from the main menu\n")

        print(f"{Fore.CYAN}Next Steps:{Style.RESET_ALL}")

        if ai_lab_completed:
            run_script = self.ai_lab_path / "run_ai_env.bat"
            print(f"1. Run: {run_script}")
            print(f"2. Choose option 1 for full activation")
            print(f"3. Test Ollama server (option 6)")
        elif ai_env_completed:
            activate_script = self.ai_environment_path / "activate_ai_env.bat"
            print(f"1. Run: {activate_script}")
            print(f"2. Test Ollama: ollama serve")
            print(f"3. Optional: Install AI_Lab by running MasterInstall.bat again (option 2)")

        print(f"\n{Fore.YELLOW}Press Enter to exit...{Style.RESET_ALL}")
        input()

    def run(self):
        """Main execution flow"""
        import os  # Import for temp directory

        self.print_banner()

        # Check system requirements
        if not self.check_system_requirements():
            self.print_error("\nSystem requirements not met. Please install Git and try again.")
            return 1

        # Load and show current status
        self.print_info("Reading installation status...")
        self.status_manager.print_status_summary()

        # Check for incomplete installations
        resume_info = self.status_manager.get_resume_info()
        if resume_info["must_complete_uninstall"]:
            self.print_error("Previous uninstall was not completed.")
            self.print_info("Please run MasterUninstall.bat to complete the uninstallation.")
            return 1

        # Show main menu
        choice = self.show_main_menu()

        if choice == '0':
            self.print_info("Installation cancelled")
            return 0

        elif choice == '1':
            # Fresh installation
            self.print_info("Starting fresh installation...")
            success = self.do_fresh_installation()
            return 0 if success else 1

        elif choice == '2':
            # Install AI_Lab only
            self.print_info("Starting AI_Lab-only installation...")
            success = self.do_ailab_only_installation()
            return 0 if success else 1

        elif choice == '3':
            # Install AI_Environment only
            self.print_info("AI_Environment-only installation not yet implemented")
            return 1

        elif choice == '4':
            # Resume installation
            if not resume_info["can_resume"]:
                self.print_error("No incomplete installation found to resume")
                return 1

            self.print_info("Resuming installation...")
            success = self.do_resume_installation()
            return 0 if success else 1

        elif choice == '5':
            # Uninstall
            self.print_info("Please run MasterUninstall.bat to uninstall")
            return 0

        return 0


def main():
    """Main entry point"""
    # Parse command-line arguments for non-interactive mode
    parser = argparse.ArgumentParser(description="AI Environment & Lab Master Installer")
    parser.add_argument('--auto-install', action='store_true',
                       help='Run fresh installation non-interactively (for testing)')
    parser.add_argument('--drive', type=str,
                       help='Target drive letter (e.g., D) for auto-install')
    args = parser.parse_args()

    try:
        installer = MasterInstaller()

        # Non-interactive mode
        if args.auto_install:
            if not args.drive:
                print(f"{Fore.RED}[ERROR] --drive required with --auto-install{Style.RESET_ALL}")
                return 1

            installer.print_banner()
            if not installer.check_system_requirements():
                installer.print_error("\nSystem requirements not met. Please install Git and try again.")
                return 1

            installer.print_info("Running in auto-install mode...")
            installer.print_info(f"Target drive: {args.drive}")

            # Determine drive type
            drive_letter = args.drive.upper()
            drive_root = Path(f"{drive_letter}:/")

            # Check if drive exists
            if not drive_root.exists():
                installer.print_error(f"Drive {drive_letter}:\\ does not exist")
                return 1

            # Assume Internal for auto-mode (can be extended later)
            drive_type = "Internal"

            # Set installation paths
            installer.selected_drive = drive_letter
            installer.selected_drive_type = drive_type
            installer.ai_environment_path = drive_root / "AI_Environment"
            installer.ai_lab_path = drive_root / "AI_Lab"
            installer.ailab_base_path = None

            installer.print_info(f"AI_Environment will be installed to: {installer.ai_environment_path}")
            installer.print_info(f"AI_Lab will be installed to: {installer.ai_lab_path}")

            # Update installation context
            install_mode = "standalone"
            installer.status_manager.set_installation_context(
                drive_letter,
                drive_type,
                install_mode
            )

            # Install components
            if not installer.install_ai_environment(phase_label="[Phase 2/3]"):
                return 1

            if not installer.install_ai_lab(phase_label="[Phase 3/3]"):
                return 1

            installer.show_completion_summary()
            return 0

        # Interactive mode (original behavior)
        return installer.run()

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Installation cancelled by user{Style.RESET_ALL}")
        return 1
    except Exception as e:
        print(f"\n{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

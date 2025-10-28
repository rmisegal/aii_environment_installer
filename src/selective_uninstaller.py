#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Selective Uninstaller - Removes AI Environment components from specified step onwards
"""

import os
import sys
import shutil
import subprocess
import logging
import argparse
from pathlib import Path
from step_tracker import StepTracker

class SelectiveUninstaller:
    """Handles selective removal of AI Environment components"""
    
    def __init__(self, ai_env_path: Path):
        self.ai_env_path = ai_env_path
        self.logger = logging.getLogger(__name__)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(ai_env_path.parent / "logs" / "uninstall.log", encoding='utf-8')
            ]
        )
        
        # Initialize step tracker
        self.step_tracker = StepTracker(ai_env_path)
    
    def uninstall_from_step(self, from_step: int) -> bool:
        """Remove components from specified step onwards"""
        try:
            self.logger.info(f"Starting selective uninstall from step {from_step}")
            
            # Stop running processes first
            self._stop_processes()
            
            # Remove components based on step
            success = True
            
            if from_step <= 8:
                success &= self._remove_finalization()
            
            if from_step <= 7:
                success &= self._remove_ollama()
            
            if from_step <= 6:
                success &= self._remove_packages()
            
            if from_step <= 5:
                success &= self._remove_vscode()
            
            if from_step <= 4:
                success &= self._remove_ai_environment()
            
            if from_step <= 3:
                success &= self._remove_miniconda()
            
            if from_step <= 2:
                success &= self._remove_directories()
            
            # Update step tracker
            self.step_tracker.reset_from_step(from_step)
            
            self.logger.info(f"Selective uninstall completed from step {from_step}")
            return success
            
        except Exception as e:
            self.logger.error(f"Error during selective uninstall: {e}")
            return False
    
    def _stop_processes(self):
        """Stop all AI Environment related processes"""
        try:
            self.logger.info("Stopping AI Environment processes...")
            
            processes = [
                "ollama.exe",
                "Code.exe",
                "python.exe",
                "conda.exe",
                "jupyter.exe",
                "jupyter-lab.exe"
            ]
            
            for process in processes:
                try:
                    subprocess.run(
                        ["taskkill", "/f", "/im", process],
                        capture_output=True,
                        timeout=10
                    )
                except:
                    pass
            
            self.logger.info("Processes stopped")
            
        except Exception as e:
            self.logger.warning(f"Error stopping processes: {e}")
    
    def _remove_finalization(self) -> bool:
        """Remove finalization components (step 8)"""
        try:
            self.logger.info("Removing finalization components...")
            
            # Remove activation script
            activation_script = self.ai_env_path / "activate_ai_env.bat"
            if activation_script.exists():
                activation_script.unlink()
                self.logger.info("Removed activation script")
            
            # Remove project templates
            projects_dir = self.ai_env_path / "Projects"
            if projects_dir.exists():
                shutil.rmtree(projects_dir, ignore_errors=True)
                self.logger.info("Removed project templates")
            
            # Remove scripts
            scripts_dir = self.ai_env_path / "Scripts"
            if scripts_dir.exists():
                shutil.rmtree(scripts_dir, ignore_errors=True)
                self.logger.info("Removed scripts")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing finalization: {e}")
            return False
    
    def _remove_ollama(self) -> bool:
        """Remove Ollama and models (step 7)"""
        try:
            self.logger.info("Removing Ollama and models...")
            
            # Remove Ollama directory
            ollama_dir = self.ai_env_path / "Ollama"
            if ollama_dir.exists():
                shutil.rmtree(ollama_dir, ignore_errors=True)
                self.logger.info("Removed Ollama installation")
            
            # Remove models directory
            models_dir = self.ai_env_path / "Models"
            if models_dir.exists():
                shutil.rmtree(models_dir, ignore_errors=True)
                self.logger.info("Removed AI models")
            
            # Remove downloads directory (contains Ollama installer)
            downloads_dir = self.ai_env_path / "downloads"
            if downloads_dir.exists():
                shutil.rmtree(downloads_dir, ignore_errors=True)
                self.logger.info("Removed Ollama downloads")
            
            print("- Removed Ollama installation")
            print("- Removed AI models")
            print("- Removed Ollama downloads")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing Ollama: {e}")
            return False
    
    def _remove_packages(self) -> bool:
        """Remove Python packages (step 6)"""
        try:
            self.logger.info("Removing Python packages...")
            
            # For conda environment, we can't selectively remove packages easily
            # So we'll remove the entire environment and recreate it
            conda_exe = self.ai_env_path / "Miniconda" / "Scripts" / "conda.exe"
            
            if conda_exe.exists():
                try:
                    # Remove AI2025 environment
                    subprocess.run(
                        [str(conda_exe), "env", "remove", "--name", "AI2025", "--yes"],
                        capture_output=True,
                        timeout=60
                    )
                    self.logger.info("Removed AI2025 conda environment")
                    
                    # Recreate empty environment
                    subprocess.run(
                        [str(conda_exe), "create", "--name", "AI2025", "python=3.10", "--yes"],
                        capture_output=True,
                        timeout=300
                    )
                    self.logger.info("Recreated empty AI2025 environment")
                    
                except Exception as e:
                    self.logger.warning(f"Error managing conda environment: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing packages: {e}")
            return False
    
    def _remove_vscode(self) -> bool:
        """Remove VS Code (step 5)"""
        try:
            self.logger.info("Removing VS Code...")
            
            vscode_dir = self.ai_env_path / "VSCode"
            if vscode_dir.exists():
                shutil.rmtree(vscode_dir, ignore_errors=True)
                self.logger.info("Removed VS Code")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing VS Code: {e}")
            return False
    
    def _remove_ai_environment(self) -> bool:
        """Remove AI environment (step 4)"""
        try:
            self.logger.info("Removing AI2025 environment...")
            
            conda_exe = self.ai_env_path / "Miniconda" / "Scripts" / "conda.exe"
            
            if conda_exe.exists():
                try:
                    subprocess.run(
                        [str(conda_exe), "env", "remove", "--name", "AI2025", "--yes"],
                        capture_output=True,
                        timeout=60
                    )
                    self.logger.info("Removed AI2025 conda environment")
                except Exception as e:
                    self.logger.warning(f"Error removing conda environment: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing AI environment: {e}")
            return False
    
    def _remove_miniconda(self) -> bool:
        """Remove Miniconda (step 3)"""
        try:
            self.logger.info("Removing Miniconda...")
            
            miniconda_dir = self.ai_env_path / "Miniconda"
            if miniconda_dir.exists():
                shutil.rmtree(miniconda_dir, ignore_errors=True)
                self.logger.info("Removed Miniconda")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing Miniconda: {e}")
            return False
    
    def _remove_directories(self) -> bool:
        """Remove directory structure (step 2)"""
        try:
            self.logger.info("Removing directory structure...")
            
            # Remove all subdirectories but keep the main AI_Environment folder
            subdirs = ["Tools", "Logs"]
            
            for subdir in subdirs:
                dir_path = self.ai_env_path / subdir
                if dir_path.exists():
                    shutil.rmtree(dir_path, ignore_errors=True)
                    self.logger.info(f"Removed {subdir}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing directories: {e}")
            return False

def find_ai_environment():
    """Find AI_Environment installation on any drive"""
    import string

    # Check all possible drive letters
    for letter in string.ascii_uppercase:
        candidate = Path(f"{letter}:/AI_Environment")
        if candidate.exists() and candidate.is_dir():
            # Check if it looks like our installation
            if (candidate / "installation_status.json").exists() or \
               (candidate / "Miniconda").exists() or \
               (candidate / "activate_ai_env.bat").exists():
                return candidate

    return None


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Selective AI Environment Uninstaller")
    parser.add_argument("--from-step", type=int, required=True,
                       help="Remove from this step onwards (1-8)")
    parser.add_argument("--path", type=str,
                       help="Path to AI_Environment (auto-detected if not specified)")

    args = parser.parse_args()

    # Validate step number
    if args.from_step < 1 or args.from_step > 8:
        print("Error: Step number must be between 1 and 8")
        return 1

    # Find AI Environment
    if args.path:
        ai_env_path = Path(args.path)
    else:
        ai_env_path = find_ai_environment()

    if not ai_env_path or not ai_env_path.exists():
        print("Error: AI Environment not found on any drive")
        print("Use --path to specify the installation location manually")
        return 1

    print(f"Found AI Environment at: {ai_env_path}")

    # Create uninstaller and run
    uninstaller = SelectiveUninstaller(ai_env_path)

    print(f"Removing AI Environment components from step {args.from_step} onwards...")

    if uninstaller.uninstall_from_step(args.from_step):
        print(f"Successfully removed components from step {args.from_step}")
        return 0
    else:
        print(f"Failed to remove some components from step {args.from_step}")
        return 1

if __name__ == "__main__":
    sys.exit(main())


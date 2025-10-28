# -*- coding: utf-8 -*-
"""
Installation Manager - Main installation logic for AI Environment
Uses split Conda modules for better organization
Version 1.3 - Fixed StepTracker method calls
"""

import os
import sys
import json
import time
import logging
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Add core path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from download_manager import DownloadManager
from conda_installer import CondaInstaller
from conda_manager import CondaManager
from vscode_installer import VSCodeInstaller
from ollama_installer import OllamaInstaller
from step_tracker import StepTracker
from installation_status_manager import InstallationStatusManager

class InstallManager:
    """Main installation manager using split Conda modules"""
    
    def __init__(self, start_step: int = 1, target_drive: str = "D", ailab_base_path: str = None):
        self.installer_path = Path(__file__).parent.parent
        self.target_drive = Path(f"{target_drive}:\\")

        # If ailab_base_path is provided, install to AI_Lab/AI_Environment
        # Otherwise, install to Drive:\AI_Environment
        if ailab_base_path:
            self.ai_env_path = Path(ailab_base_path) / "AI_Environment"
        else:
            self.ai_env_path = self.target_drive / "AI_Environment"

        self.logs_path = self.installer_path / "logs"
        self.config_path = self.installer_path / "config"

        # Create required directories
        self.logs_path.mkdir(exist_ok=True)
        self.ai_env_path.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Load configuration
        self.config = self.load_config()
        
        # Initialize managers
        self.download_manager = DownloadManager(self.logs_path)
        
        # Initialize step tracker
        self.step_tracker = StepTracker(self.ai_env_path)

        # Initialize master status manager
        self.master_status = InstallationStatusManager()

        # Specialized installers
        self.conda_installer = CondaInstaller(self.ai_env_path, self.logs_path)
        self.conda_manager = None  # Will be initialized after conda installation
        self.vscode_installer = VSCodeInstaller(self.ai_env_path, self.logs_path)
        self.ollama_installer = OllamaInstaller(self.ai_env_path, self.logs_path)
        
        # Progress tracking
        self.total_steps = 8
        self.current_step = start_step - 1  # Will be incremented in print_progress
        self.start_step = start_step
        self.start_time = None

    def setup_logging(self):
        """Setup logging system"""
        log_file = self.logs_path / f"install_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Starting installation process")

    def load_config(self) -> Dict:
        """Load configuration file"""
        config_file = self.config_path / "install_config.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Error loading config file: {e}")
        
        # Default configuration
        return {
            "python_version": "3.10",
            "conda_channels": ["conda-forge", "defaults"],
            "vscode_extensions": [
                "ms-python.python",
                "ms-toolsai.jupyter", 
                "ms-python.vscode-pylance",
                "ms-python.black-formatter",
                "ms-vscode.vscode-json"
            ],
            "ollama_models": [
                "llama2:7b",
                "codellama:7b", 
                "mistral:7b",
                "phi:2.7b"
            ],
            "python_packages": [
                "langchain>=0.1.0",
                "langgraph>=0.1.0",
                "pyautogen>=0.2.0",
                "transformers",
                "torch",
                "sentence-transformers",
                "chromadb",
                "faiss-cpu",
                "streamlit",
                "fastapi",
                "uvicorn",
                "gradio",
                "pandas",
                "numpy",
                "matplotlib",
                "seaborn",
                "plotly",
                "scikit-learn",
                "jupyter",
                "jupyterlab",
                "ipykernel",
                "notebook",
                "requests",
                "python-dotenv",
                "pydantic",
                "httpx",
                "aiohttp",
                "beautifulsoup4",
                "lxml",
                "black",
                "pylint",
                "isort",
                "flake8"
            ]
        }

    def print_progress(self, message: str, step_name: str = ""):
        """Print progress with formatting and step tracking"""
        self.current_step += 1
        progress = (self.current_step / self.total_steps) * 100
        
        # Update step tracker - only pass step number
        self.step_tracker.start_step(self.current_step)
        
        print(f"\n{'='*60}")
        print(f"Step {self.current_step}/{self.total_steps} ({progress:.1f}%): {message}")
        if step_name:
            print(f"Action: {step_name}")
        print(f"{'='*60}")
        
        self.logger.info(f"Step {self.current_step}: {message}")

    def check_prerequisites(self) -> bool:
        """Check system prerequisites"""
        self.print_progress("Checking system prerequisites", "Verifying system and disk space")
        
        try:
            # Check disk space (Windows compatible)
            import shutil
            free_space_bytes = shutil.disk_usage(str(self.target_drive)).free
            free_space_gb = free_space_bytes / (1024**3)
            
            print(f"Available disk space: {free_space_gb:.0f}GB")
            
            if free_space_gb < 50:
                self.logger.error(f"Insufficient disk space: {free_space_gb:.1f}GB available, 50GB required")
                return False
            
            # Check internet connection
            try:
                import urllib.request
                urllib.request.urlopen('https://www.google.com', timeout=10)
                print("Internet connection available")
            except:
                self.logger.warning("Internet connection check failed")
                return False
            
            self.logger.info("Prerequisites check completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking prerequisites: {e}")
            return False

    def create_directory_structure(self) -> bool:
        """Create directory structure"""
        self.print_progress("Creating directory structure", "Creating base directories")
        
        try:
            directories = [
                self.ai_env_path / "Miniconda",
                self.ai_env_path / "VSCode",
                self.ai_env_path / "Ollama",
                self.ai_env_path / "Models",
                self.ai_env_path / "Tools",
                self.ai_env_path / "Projects",
                self.ai_env_path / "Scripts",
                self.ai_env_path / "Logs"
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                print(f"Created directory: {directory}")
            
            self.logger.info("Directory structure created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating directory structure: {e}")
            return False

    def install_conda(self) -> bool:
        """Install Miniconda"""
        self.print_progress("Installing Miniconda", "Downloading and installing Python environment manager")
        
        try:
            success = self.conda_installer.install()
            if success:
                # Initialize conda manager after successful installation
                conda_exe = self.conda_installer.get_conda_exe()
                self.conda_manager = CondaManager(conda_exe, self.ai_env_path)
            return success
        except Exception as e:
            self.logger.error(f"Error installing Miniconda: {e}")
            return False

    def create_conda_environment(self) -> bool:
        """Create AI2025 conda environment"""
        self.print_progress("Creating AI2025 environment", "Setting up conda environment with Python 3.10")
        
        try:
            if not self.conda_manager:
                self.logger.error("Conda manager not initialized")
                return False
            
            success = self.conda_manager.create_environment("AI2025", self.config["python_version"])
            return success
        except Exception as e:
            self.logger.error(f"Error creating conda environment: {e}")
            return False

    def install_vscode(self) -> bool:
        """Install VS Code"""
        self.print_progress("Installing VS Code", "Downloading and installing portable VS Code")
        
        try:
            success = self.vscode_installer.install("latest")
            return success
        except Exception as e:
            self.logger.error(f"Error installing VS Code: {e}")
            return False

    def install_python_packages(self) -> bool:
        """Install Python packages"""
        self.print_progress("Installing Python packages", "Installing AI and ML libraries using conda")
        
        try:
            if not self.conda_manager:
                self.logger.error("Conda manager not initialized")
                return False
            
            success = self.conda_manager.install_packages_batch(self.config["python_packages"], "AI2025")
            return success
        except Exception as e:
            self.logger.error(f"Error installing Python packages: {e}")
            return False

    def install_ollama(self) -> bool:
        """Install Ollama and models"""
        self.print_progress("Installing Ollama and LLM models", "Setting up local AI models")
        
        try:
            # Install Ollama server
            success = self.ollama_installer.install()
            if not success:
                return False
            
            # Ask user if they want to download models
            models = self.config["ollama_models"]
            if models:
                print(f"\n{'='*60}")
                print(f"AI Model Download")
                print(f"{'='*60}")
                print(f"The installer can download {len(models)} AI models:")
                for model in models:
                    print(f"  - {model}")
                print(f"\nTotal size: ~15-20 GB")
                print(f"Download time: 10-30 minutes (depending on connection)")
                print(f"\nYou can skip this and download models later with: ollama pull <model_name>")
                print(f"{'='*60}\n")

                response = input("Download AI models now? (y/n): ").strip().lower()

                if response in ['y', 'yes']:
                    print(f"\nDownloading {len(models)} AI models...")
                    print("This may take 10-30 minutes depending on your internet connection.")
                    success = self.ollama_installer.install_models(models)
                    if not success:
                        self.logger.warning("Some models failed to download, but Ollama is installed")
                        print("Warning: Some models failed to download. You can download them manually later.")
                else:
                    print("\nSkipping model downloads.")
                    print("You can download models later using: ollama pull <model_name>")
                    self.logger.info("User chose to skip model downloads")

            return True
        except Exception as e:
            self.logger.error(f"Error installing Ollama: {e}")
            return False

    def finalize_installation(self) -> bool:
        """Finalize installation"""
        self.print_progress("Finalizing installation", "Creating shortcuts and startup files")

        try:
            # Create activation script
            self.create_activation_script()

            # Create project templates
            self.create_project_templates()

            # Create README
            self.create_readme()

            # Save installation info
            self.save_installation_info()

            # Save final installation status to installer directory
            try:
                installer_status_copy = self.installer_path / "installation_status.json"
                with open(installer_status_copy, 'w', encoding='utf-8') as f:
                    json.dump(self.step_tracker.status, f, ensure_ascii=False, indent=2)
                self.logger.info("Final installation status saved to installer directory")
                print("[OK] Installation status saved for future uninstall")
            except Exception as e:
                self.logger.warning(f"Could not save final status to installer directory: {e}")

            self.logger.info("Installation finalization completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error finalizing installation: {e}")
            return False

    def create_activation_script(self):
        """Create activation script"""
        activation_script = self.ai_env_path / "activate_ai_env.bat"

        # Convert Path to string with proper Windows formatting
        # Use os.fspath to get proper Windows path representation
        ai_env_str = os.fspath(self.ai_env_path)
        # Ensure backslashes and proper drive letter format
        if not ai_env_str[1:3] == ':\\':
            # Fix missing backslash after drive letter (D: -> D:\)
            ai_env_str = ai_env_str[0] + ':\\' + ai_env_str[2:].lstrip(':\\/')

        script_content = f'''@echo off
title AI Environment - AI2025

echo.
echo ================================================================
echo                    AI Environment Activated
echo                         AI2025 (Conda)
echo ================================================================
echo.
echo Environment: AI2025
echo Python: 3.10 (Conda)
echo Location: {ai_env_str}
echo.
echo Available Commands:
echo   conda list          - Show installed packages
echo   jupyter lab         - Start Jupyter Lab
echo   code .              - Open VS Code
echo   ollama serve        - Start Ollama server
echo   ollama list         - Show available models
echo.
echo ================================================================

REM Activate conda environment - check both portable and AllUsers locations
if exist "{ai_env_str}\\Miniconda\\Scripts\\activate.bat" (
    call "{ai_env_str}\\Miniconda\\Scripts\\activate.bat" AI2025
) else if exist "C:\\ProgramData\\miniconda3\\Scripts\\activate.bat" (
    call "C:\\ProgramData\\miniconda3\\Scripts\\activate.bat" AI2025
) else (
    echo ERROR: Miniconda not found in either location
)

REM Add VS Code to PATH
set PATH={ai_env_str}\\VSCode;%PATH%

REM Add Ollama to PATH
set PATH={ai_env_str}\\Ollama;%PATH%

REM Change to projects directory
cd /d "{ai_env_str}\\Projects"

REM Keep command prompt open
cmd /k
'''

        with open(activation_script, 'w', encoding='utf-8') as f:
            f.write(script_content)

    def create_project_templates(self):
        """Create project templates"""
        projects_dir = self.ai_env_path / "Projects"
        projects_dir.mkdir(exist_ok=True)
        
        # Create basic LLM example
        basic_example = projects_dir / "01_Basic_LLM_Example"
        basic_example.mkdir(exist_ok=True)
        
        (basic_example / "main.py").write_text('''"""
Basic LLM Example with Ollama
Run: python main.py
"""
import requests

def query_ollama(prompt, model="llama2"):
    """Query Ollama API"""
    url = "http://127.0.0.1:11434/api/generate"
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=data, timeout=30)
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    print("Basic LLM Example")
    print("Make sure Ollama is running: ollama serve")
    print()
    
    prompt = "Explain artificial intelligence in simple terms"
    print(f"Question: {prompt}")
    print("Thinking...")
    
    response = query_ollama(prompt)
    print(f"AI Response: {response}")
''', encoding='utf-8')

    def create_readme(self):
        """Create README file"""
        readme_file = self.ai_env_path / "README.md"
        
        readme_content = f'''# AI Environment - Portable AI Development Setup

Welcome to your portable AI development environment!

## What's Included

### Development Tools
- **Miniconda**: Python environment manager
- **Python 3.10**: In conda environment AI2025
- **VS Code**: Portable code editor with AI extensions
- **Jupyter Lab**: Interactive development environment

### AI Environment
- **Ollama**: Local LLM engine
- **LLM Models**: Llama2, CodeLlama, Mistral, Phi
- **AI Libraries**: LangChain, LangGraph, AutoGen and more

## How to Start?

1. **Start Environment**: Run `activate_ai_env.bat`
2. **Start Ollama**: Run `ollama serve` (in separate terminal)
3. **Open VS Code**: Type `code .`
4. **Start Jupyter**: Type `jupyter lab`
5. **Check Models**: Type `ollama list`

## File Locations

- **Projects**: `Projects/` - Your AI projects
- **Scripts**: `Scripts/` - Utility scripts  
- **Logs**: `Logs/` - Installation and runtime logs
- **Models**: `Models/` - Ollama model files

## Conda Environment

The AI2025 environment includes:
- Python 3.10
- All AI/ML libraries
- Jupyter Lab
- Development tools

**Commands:**
- `conda list` - Show installed packages
- `conda install package` - Install new package
- `conda env list` - Show environments

## Support

For technical support, check log files in `Logs/` or refer to the complete manual.

---
Installed on: {datetime.now().strftime('%d/%m/%Y %H:%M')}
Environment: AI2025 (Conda)
'''
        
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)

    def save_installation_info(self):
        """Save installation information"""
        install_info = {
            "installation_date": datetime.now().isoformat(),
            "installer_version": "1.3",
            "environment_manager": "conda",
            "environment_name": "AI2025",
            "target_path": str(self.ai_env_path),
            "python_version": self.config["python_version"],
            "installed_packages": self.config["python_packages"],
            "ollama_models": self.config["ollama_models"],
            "installation_time_minutes": (time.time() - self.start_time) / 60 if self.start_time else 0,
            "conda_info": self.conda_manager.get_environment_info("AI2025") if self.conda_manager else {}
        }
        
        info_file = self.ai_env_path / "installation_info.json"
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(install_info, f, ensure_ascii=False, indent=2)

    def verify_pre_install_state(self):
        """Verify and display pre-install state capture"""
        try:
            pre_state = self.step_tracker.status.get('pre_install_state', {})

            if not pre_state:
                self.logger.warning("Pre-install state not captured - initializing now")
                # Force re-initialization to capture state
                self.step_tracker.status['pre_install_state'] = self.step_tracker._capture_pre_install_state()
                self.step_tracker._save_status()
                pre_state = self.step_tracker.status['pre_install_state']

            # Display pre-install state summary
            print("\n" + "="*60)
            print("PRE-INSTALL STATE CAPTURED")
            print("="*60)

            conda_info = pre_state.get('conda_installations', {})
            if conda_info.get('allusers_exists'):
                print(f"[OK] Existing Conda detected: {conda_info.get('allusers_path')}")
            if conda_info.get('portable_exists'):
                print(f"[OK] Portable Conda detected: {conda_info.get('portable_path')}")

            if pre_state.get('ai_env_existed'):
                existing_dirs = pre_state.get('existing_subdirs', [])
                if existing_dirs:
                    print(f"[OK] Existing AI_Environment directories: {', '.join(existing_dirs)}")
                else:
                    print(f"[OK] AI_Environment directory existed (empty)")
            else:
                print("[OK] Fresh installation (no existing AI_Environment)")

            if pre_state.get('python_in_path'):
                print("[OK] System Python detected in PATH")

            print(f"[OK] Installation timestamp: {pre_state.get('timestamp', 'N/A')}")
            print("="*60)

            # Save a copy of installation status to installer directory for uninstaller
            try:
                installer_status_copy = self.installer_path / "installation_status.json"
                with open(installer_status_copy, 'w', encoding='utf-8') as f:
                    json.dump(self.step_tracker.status, f, ensure_ascii=False, indent=2)
                self.logger.info(f"Installation status copied to installer directory")
            except Exception as e:
                self.logger.warning(f"Could not save status to installer directory: {e}")

            self.logger.info(f"Pre-install state verified and captured")
            return True

        except Exception as e:
            self.logger.error(f"Error verifying pre-install state: {e}")
            # Non-fatal - continue with installation
            return True

    def run_installation(self) -> bool:
        """Run complete installation process"""
        self.start_time = time.time()

        try:
            print("Starting AI Environment installation with Conda...")

            # Verify and display pre-install state (for clean uninstall later)
            if self.start_step == 1:
                self.verify_pre_install_state()

            # Initialize conda manager if starting from step 4 or later
            if self.start_step >= 4:
                conda_exe = self.ai_env_path / "Miniconda" / "Scripts" / "conda.exe"
                if conda_exe.exists():
                    self.conda_manager = CondaManager(conda_exe, self.ai_env_path)
                    print(f"Conda manager initialized for resume from step {self.start_step}")
            
            # Step 1: Check prerequisites
            if self.start_step <= 1:
                if not self.check_prerequisites():
                    self.step_tracker.fail_step(1, "Prerequisites check failed")
                    # Update master status
                    self.master_status.set_ai_environment_status(
                        InstallationStatusManager.STATUS_PROCESSING,
                        install_path=str(self.ai_env_path),
                        version="3.0.28",
                        last_step=0
                    )
                    return False
                self.step_tracker.complete_step(1)
                # Update master status after each step
                self.master_status.set_ai_environment_status(
                    InstallationStatusManager.STATUS_PROCESSING,
                    install_path=str(self.ai_env_path),
                    version="3.0.28",
                    last_step=1
                )
            else:
                print(f"Skipping step 1 (Prerequisites) - starting from step {self.start_step}")
            
            # Step 2: Create directory structure
            if self.start_step <= 2:
                if not self.create_directory_structure():
                    self.step_tracker.fail_step(2, "Directory creation failed")
                    return False
                self.step_tracker.complete_step(2)
            else:
                print(f"Skipping step 2 (Directory structure)")
            
            # Step 3: Install Miniconda
            if self.start_step <= 3:
                if not self.install_conda():
                    self.step_tracker.fail_step(3, "Miniconda installation failed")
                    return False
                self.step_tracker.complete_step(3)
                # Update master status
                self.master_status.set_ai_environment_status(
                    InstallationStatusManager.STATUS_PROCESSING,
                    install_path=str(self.ai_env_path),
                    version="3.0.28",
                    last_step=3
                )
            else:
                print(f"Skipping step 3 (Miniconda)")
            
            # Step 4: Create AI2025 conda environment
            if self.start_step <= 4:
                if not self.create_conda_environment():
                    self.step_tracker.fail_step(4, "Conda environment creation failed")
                    return False
                self.step_tracker.complete_step(4)
            else:
                print(f"Skipping step 4 (AI2025 environment)")
            
            # Step 5: Install VS Code
            if self.start_step <= 5:
                if not self.install_vscode():
                    self.step_tracker.fail_step(5, "VS Code installation failed")
                    return False
                self.step_tracker.complete_step(5)
            else:
                print(f"Skipping step 5 (VS Code)")
            
            # Step 6: Install Python packages
            if self.start_step <= 6:
                if not self.install_python_packages():
                    self.step_tracker.fail_step(6, "Python packages installation failed")
                    return False
                self.step_tracker.complete_step(6)
                # Update master status
                self.master_status.set_ai_environment_status(
                    InstallationStatusManager.STATUS_PROCESSING,
                    install_path=str(self.ai_env_path),
                    version="3.0.28",
                    last_step=6
                )
            else:
                print(f"Skipping step 6 (Python packages)")
            
            # Step 7: Install Ollama
            if self.start_step <= 7:
                if not self.install_ollama():
                    self.step_tracker.fail_step(7, "Ollama installation failed")
                    return False
                self.step_tracker.complete_step(7)
            else:
                print(f"Skipping step 7 (Ollama)")
            
            # Step 8: Finalize installation
            if self.start_step <= 8:
                if not self.finalize_installation():
                    self.step_tracker.fail_step(8, "Installation finalization failed")
                    return False
                self.step_tracker.complete_step(8)
            else:
                print(f"Skipping step 8 (Finalization)")
            
            # Mark installation as completed
            self.step_tracker.complete_installation()

            # Update master status to completed
            self.master_status.set_ai_environment_status(
                InstallationStatusManager.STATUS_COMPLETED,
                install_path=str(self.ai_env_path),
                version="3.0.28",
                last_step=8
            )

            # Summary
            total_time = (time.time() - self.start_time) / 60
            print(f"\n{'='*60}")
            print("INSTALLATION COMPLETED SUCCESSFULLY!")
            print(f"Installation time: {total_time:.1f} minutes")
            print(f"Location: {self.ai_env_path}")
            print(f"To start: {self.ai_env_path}/activate_ai_env.bat")
            print("Environment: AI2025 (Conda)")
            print(f"{'='*60}")
            
            # Ask user if they want to run verification
            print("\nWould you like to run the verification program to test the installation?")
            print("This will verify that all components are working correctly.")
            response = input("Run verification? (y/n): ").strip().lower()
            
            if response in ['y', 'yes']:
                print("\nStarting verification program...")
                try:
                    import subprocess
                    import sys
                    
                    # Get the path to validate.bat (in the installer directory)
                    # The installer is typically run from the AI_Installer directory
                    installer_dir = Path(__file__).parent.parent  # Go up from src/ to AI_Installer/
                    validate_script = installer_dir / "validate.bat"
                    
                    if validate_script.exists():
                        # Run validation without affecting main process exit code
                        result = subprocess.run([str(validate_script)], shell=True, cwd=str(installer_dir), capture_output=False)
                        # Don't check result.returncode - validation results shouldn't affect installation success
                        print("\nValidation completed. Check the validation report for details.")
                    else:
                        print("Warning: validate.bat not found. Please run it manually from the installer directory.")
                        print(f"Expected location: {validate_script}")
                        print("You can run validation manually by executing validate.bat from the AI_Installer folder.")
                except Exception as e:
                    print(f"Error running verification: {e}")
                    print("Please run validate.bat manually from the installer directory.")
                    # Don't let validation errors affect installation success
            else:
                print("\nYou can run the verification later by executing validate.bat")
                print("from the installer directory.")
            
            # Ensure we return success regardless of validation results
            self.logger.info(f"Installation completed successfully in {total_time:.1f} minutes")
            return True
            
        except Exception as e:
            current_actual_step = max(1, self.current_step)
            self.step_tracker.fail_step(current_actual_step, f"Critical error: {str(e)}")
            self.logger.error(f"General installation error: {e}")
            self.logger.error(traceback.format_exc())
            return False

def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='AI Environment Installer')
    parser.add_argument('--step', type=int, default=1,
                       help='Step to start installation from (1-8)')
    parser.add_argument('--drive', type=str, default='D',
                       help='Target drive letter (e.g., D, E, F)')
    parser.add_argument('--ailab', type=str, default=None,
                       help='Path to AI_Lab folder (if installing to external drive with AI_Lab)')

    args = parser.parse_args()

    # Validate step number
    if args.step < 1 or args.step > 8:
        print(f"Error: Step must be between 1 and 8, got {args.step}")
        sys.exit(1)

    # Validate and normalize drive letter
    drive_letter = args.drive.strip().upper()
    if len(drive_letter) == 2 and drive_letter[1] == ':':
        drive_letter = drive_letter[0]
    if len(drive_letter) != 1 or not drive_letter.isalpha():
        print(f"Error: Invalid drive letter '{args.drive}'. Must be a single letter (e.g., D, E, F)")
        sys.exit(1)

    try:
        print(f"Starting installation from step {args.step}")
        if args.ailab:
            print(f"Target installation: {args.ailab}\\AI_Environment")
        else:
            print(f"Target installation: {drive_letter}:\\AI_Environment")
        installer = InstallManager(start_step=args.step, target_drive=drive_letter, ailab_base_path=args.ailab)
        success = installer.run_installation()

        if success:
            sys.exit(0)
        else:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nCritical error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


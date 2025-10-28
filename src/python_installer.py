#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python Installer - Handles Python 3.10 portable installation
"""

import os
import sys
import zipfile
import logging
import subprocess
from pathlib import Path
from typing import Optional
from download_manager import DownloadManager

class PythonInstaller:
    """Handles Python 3.10 portable installation"""
    
    def __init__(self, ai_env_path: Path, logs_path: Path):
        self.ai_env_path = ai_env_path
        self.logs_path = logs_path
        self.logger = logging.getLogger(__name__)
        self.download_manager = DownloadManager(logs_path)
        
        # Installation paths
        self.python_path = ai_env_path / "Python"
        self.downloads_path = logs_path.parent / "downloads"
        
    def install(self, version: str = "3.10.11") -> bool:
        """Install Python portable"""
        try:
            self.logger.info(f"Installing Python {version}")
            
            # Download Python
            python_zip = self._download_python(version)
            if not python_zip:
                return False
            
            # Extract Python
            if not self._extract_python(python_zip):
                return False
            
            # Configure Python
            if not self._configure_python():
                return False
            
            # Install pip
            if not self._install_pip():
                return False
            
            # Verify installation
            if not self._verify_installation():
                return False
            
            self.logger.info("Python installation completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Python installation failed: {e}")
            return False
    
    def _download_python(self, version: str) -> Optional[Path]:
        """Download Python portable"""
        try:
            # Get download URL
            urls = self.download_manager.get_download_urls()
            if version not in urls["python"]:
                self.logger.error(f"Python version {version} not supported")
                return None
            
            python_info = urls["python"][version]
            url = python_info["url"]
            
            # Download
            filename = f"python-{version}-embed-amd64.zip"
            destination = self.downloads_path / filename
            
            success = self.download_manager.download_with_progress(
                url, destination, f"Downloading Python {version}"
            )
            
            if success:
                return destination
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to download Python: {e}")
            return None
    
    def _extract_python(self, python_zip: Path) -> bool:
        """Extract Python to installation directory"""
        try:
            self.logger.info("Extracting Python...")
            
            # Create Python directory
            self.python_path.mkdir(parents=True, exist_ok=True)
            
            # Extract zip file
            with zipfile.ZipFile(python_zip, 'r') as zip_ref:
                zip_ref.extractall(self.python_path)
            
            self.logger.info(f"Python extracted to: {self.python_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to extract Python: {e}")
            return False
    
    def _configure_python(self) -> bool:
        """Configure Python for portable use"""
        try:
            self.logger.info("Configuring Python...")
            
            # Create python._pth file for path configuration
            pth_content = f"""python310.zip
.
Lib
Lib/site-packages

# Enable site module for pip
import site
"""
            
            pth_file = self.python_path / "python310._pth"
            with open(pth_file, 'w', encoding='utf-8') as f:
                f.write(pth_content)
            
            # Create Scripts directory
            scripts_dir = self.python_path / "Scripts"
            scripts_dir.mkdir(exist_ok=True)
            
            # Create Lib/site-packages directory
            site_packages = self.python_path / "Lib" / "site-packages"
            site_packages.mkdir(parents=True, exist_ok=True)
            
            self.logger.info("Python configuration completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to configure Python: {e}")
            return False
    
    def _install_pip(self) -> bool:
        """Install pip in the portable Python"""
        try:
            self.logger.info("Installing pip...")
            
            python_exe = self.python_path / "python.exe"
            if not python_exe.exists():
                self.logger.error("Python executable not found")
                return False
            
            # Download get-pip.py
            get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
            get_pip_path = self.downloads_path / "get-pip.py"
            
            success = self.download_manager.download_with_progress(
                get_pip_url, get_pip_path, "Downloading pip installer"
            )
            
            if not success:
                return False
            
            # Install pip
            cmd = [str(python_exe), str(get_pip_path), "--no-warn-script-location"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.python_path))
            
            if result.returncode != 0:
                self.logger.error(f"Failed to install pip: {result.stderr}")
                return False
            
            # Verify pip installation
            pip_exe = self.python_path / "Scripts" / "pip.exe"
            if not pip_exe.exists():
                self.logger.error("Pip executable not found after installation")
                return False
            
            # Upgrade pip
            cmd = [str(python_exe), "-m", "pip", "install", "--upgrade", "pip"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.python_path))
            
            if result.returncode != 0:
                self.logger.warning(f"Failed to upgrade pip: {result.stderr}")
            
            self.logger.info("Pip installation completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install pip: {e}")
            return False
    
    def _verify_installation(self) -> bool:
        """Verify Python installation"""
        try:
            self.logger.info("Verifying Python installation...")
            
            python_exe = self.python_path / "python.exe"
            pip_exe = self.python_path / "Scripts" / "pip.exe"
            
            # Check executables exist
            if not python_exe.exists():
                self.logger.error("Python executable not found")
                return False
            
            if not pip_exe.exists():
                self.logger.error("Pip executable not found")
                return False
            
            # Test Python
            cmd = [str(python_exe), "--version"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"Python version check failed: {result.stderr}")
                return False
            
            python_version = result.stdout.strip()
            self.logger.info(f"Python version: {python_version}")
            
            # Test pip
            cmd = [str(pip_exe), "--version"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"Pip version check failed: {result.stderr}")
                return False
            
            pip_version = result.stdout.strip()
            self.logger.info(f"Pip version: {pip_version}")
            
            # Test basic import
            cmd = [str(python_exe), "-c", "import sys; print('Python path:', sys.executable)"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"Python import test failed: {result.stderr}")
                return False
            
            self.logger.info("Python installation verified successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Python verification failed: {e}")
            return False
    
    def get_python_executable(self) -> Path:
        """Get path to Python executable"""
        return self.python_path / "python.exe"
    
    def get_pip_executable(self) -> Path:
        """Get path to pip executable"""
        return self.python_path / "Scripts" / "pip.exe"


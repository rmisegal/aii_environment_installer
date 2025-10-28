#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VS Code Installer - Handles VS Code portable installation and configuration
"""

import os
import sys
import json
import zipfile
import logging
import subprocess
import time
from pathlib import Path
from typing import Optional, List, Dict
from download_manager import DownloadManager

class VSCodeInstaller:
    """Handles VS Code portable installation and configuration"""
    
    def __init__(self, ai_env_path: Path, logs_path: Path):
        self.ai_env_path = ai_env_path
        self.logs_path = logs_path
        self.logger = logging.getLogger(__name__)
        self.download_manager = DownloadManager(logs_path)
        
        # Installation paths
        self.vscode_path = ai_env_path / "VSCode"
        self.downloads_path = logs_path.parent / "downloads"
        
    def install(self, version: str = "latest") -> bool:
        """Install VS Code portable"""
        try:
            self.logger.info(f"Installing VS Code {version}")
            
            # Download VS Code
            vscode_zip = self._download_vscode(version)
            if not vscode_zip:
                return False
            
            # Extract VS Code
            if not self._extract_vscode(vscode_zip):
                return False
            
            # Configure VS Code for portable use
            if not self._configure_vscode():
                return False
            
            # Install essential extensions
            if not self._install_extensions():
                self.logger.warning("Some extensions failed to install, but continuing...")
            
            # Configure Python integration
            if not self._configure_python_integration():
                return False
            
            self.logger.info("VS Code installation completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error installing VS Code: {e}")
            return False
    
    def _download_vscode(self, version: str) -> Optional[Path]:
        """Download VS Code archive"""
        try:
            self.downloads_path.mkdir(exist_ok=True)
            
            # VS Code download URL for Windows 64-bit
            url = "https://code.visualstudio.com/sha/download?build=stable&os=win32-x64-archive"
            destination = self.downloads_path / f"vscode-{version}-win32-x64.zip"
            
            success = self.download_manager.download_file(url, destination)
            
            if success:
                return destination
            else:
                self.logger.error("Failed to download VS Code")
                return None
                
        except Exception as e:
            self.logger.error(f"Error downloading VS Code: {e}")
            return None
    
    def _extract_vscode(self, archive_path: Path) -> bool:
        """Extract VS Code archive"""
        try:
            self.logger.info("Extracting VS Code...")
            
            # Create VS Code directory
            self.vscode_path.mkdir(parents=True, exist_ok=True)
            
            # Extract archive
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(self.vscode_path)
            
            # VS Code extracts to a subdirectory, move contents up
            extracted_dirs = [d for d in self.vscode_path.iterdir() if d.is_dir()]
            if len(extracted_dirs) == 1:
                extracted_dir = extracted_dirs[0]
                
                # Move all contents from subdirectory to vscode_path
                for item in extracted_dir.iterdir():
                    item.rename(self.vscode_path / item.name)
                
                # Remove empty subdirectory
                extracted_dir.rmdir()
            
            # Verify VS Code executable exists
            vscode_exe = self.vscode_path / "Code.exe"
            if not vscode_exe.exists():
                self.logger.error("VS Code executable not found after extraction")
                return False
            
            self.logger.info(f"VS Code extracted to: {self.vscode_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error extracting VS Code: {e}")
            return False
    
    def _configure_vscode(self) -> bool:
        """Configure VS Code for portable use"""
        try:
            self.logger.info("Configuring VS Code...")
            
            # Create data directories for portable mode
            data_path = self.vscode_path / "data"
            user_data_path = data_path / "user-data"
            extensions_path = data_path / "extensions"
            
            data_path.mkdir(exist_ok=True)
            user_data_path.mkdir(exist_ok=True)
            extensions_path.mkdir(exist_ok=True)
            
            # Create User settings directory
            user_dir = user_data_path / "User"
            user_dir.mkdir(exist_ok=True)
            
            # Create settings.json with AI-friendly defaults
            settings = {
                "python.defaultInterpreterPath": f"{self.ai_env_path}\\Miniconda\\envs\\AI2025\\python.exe",
                "python.terminal.activateEnvironment": True,
                "jupyter.jupyterServerType": "local",
                "files.defaultLanguage": "python",
                "editor.fontSize": 14,
                "editor.tabSize": 4,
                "editor.insertSpaces": True,
                "editor.wordWrap": "on",
                "workbench.startupEditor": "none",
                "telemetry.telemetryLevel": "off",
                "update.mode": "none",
                "extensions.autoUpdate": False,
                "workbench.colorTheme": "Default Dark+",
                "files.autoSave": "afterDelay",
                "python.linting.enabled": True,
                "python.formatting.provider": "black"
            }
            
            settings_file = user_dir / "settings.json"
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            
            self.logger.info("VS Code configuration completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error configuring VS Code: {e}")
            return False
    
    def _install_extensions(self) -> bool:
        """Install essential VS Code extensions with better handling"""
        try:
            self.logger.info("Installing VS Code extensions...")
            
            extensions = [
                "ms-python.python",
                "ms-toolsai.jupyter", 
                "ms-python.vscode-pylance",
                "ms-python.black-formatter",
                "ms-vscode.vscode-json"
            ]
            
            vscode_exe = self.vscode_path / "Code.exe"
            data_path = self.vscode_path / "data"
            user_data_path = data_path / "user-data"
            extensions_path = data_path / "extensions"
            
            # Kill any running VS Code processes first
            self._kill_vscode_processes()
            
            success_count = 0
            failed_extensions = []
            
            for extension in extensions:
                print(f"Installing extension: {extension}")
                if self._install_single_extension(extension, vscode_exe, user_data_path, extensions_path):
                    success_count += 1
                    time.sleep(2)  # Brief pause between installations
                else:
                    failed_extensions.append(extension)
            
            self.logger.info(f"Extension installation completed: {success_count}/{len(extensions)} successful")
            
            if failed_extensions:
                self.logger.warning(f"Failed to install extensions: {failed_extensions}")
                print(f"Warning: Some extensions failed to install: {failed_extensions}")
            
            # Consider successful if at least 60% of extensions installed
            return success_count >= len(extensions) * 0.6
            
        except Exception as e:
            self.logger.error(f"Error installing VS Code extensions: {e}")
            return False
    
    def _install_single_extension(self, extension: str, vscode_exe: Path, user_data_path: Path, extensions_path: Path) -> bool:
        """Install a single VS Code extension"""
        try:
            self.logger.info(f"Installing extension: {extension}")
            
            # Use flags to prevent GUI issues
            cmd = [
                str(vscode_exe),
                "--install-extension", extension,
                "--force",
                "--no-sandbox",
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--user-data-dir", str(user_data_path),
                "--extensions-dir", str(extensions_path)
            ]
            
            # Set environment variables to prevent GUI
            env = os.environ.copy()
            env["DISPLAY"] = ""  # Prevent display issues
            env["VSCODE_CLI"] = "1"  # Indicate CLI usage
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=180,  # Increased timeout
                env=env
            )
            
            if result.returncode == 0:
                self.logger.info(f"Successfully installed extension: {extension}")
                return True
            else:
                self.logger.warning(f"Failed to install extension {extension}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"Extension installation timed out: {extension}")
            self._kill_vscode_processes()
            return False
        except Exception as e:
            self.logger.error(f"Error installing extension {extension}: {e}")
            return False
    
    def _kill_vscode_processes(self):
        """Kill any running VS Code processes"""
        try:
            # Kill VS Code processes on Windows
            subprocess.run(["taskkill", "/f", "/im", "Code.exe"], 
                         capture_output=True, text=True)
            subprocess.run(["taskkill", "/f", "/im", "code.exe"], 
                         capture_output=True, text=True)
            time.sleep(2)
        except:
            pass  # Ignore errors if no processes to kill
    
    def _configure_python_integration(self) -> bool:
        """Configure Python integration in VS Code"""
        try:
            # Create workspace settings for Projects directory
            projects_dir = self.ai_env_path / "Projects"
            projects_dir.mkdir(exist_ok=True)
            
            vscode_dir = projects_dir / ".vscode"
            vscode_dir.mkdir(exist_ok=True)
            
            # Workspace settings
            workspace_settings = {
                "python.defaultInterpreterPath": f"{self.ai_env_path}\\Miniconda\\envs\\AI2025\\python.exe",
                "python.terminal.activateEnvironment": True,
                "jupyter.jupyterServerType": "local",
                "files.associations": {
                    "*.py": "python",
                    "*.ipynb": "jupyter-notebook"
                }
            }
            
            settings_file = vscode_dir / "settings.json"
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(workspace_settings, f, indent=2)
            
            self.logger.info("Python integration configured")
            return True
            
        except Exception as e:
            self.logger.error(f"Error configuring Python integration: {e}")
            return False
    
    def verify_installation(self) -> bool:
        """Verify VS Code installation"""
        try:
            vscode_exe = self.vscode_path / "Code.exe"
            
            if not vscode_exe.exists():
                self.logger.error("VS Code executable not found")
                return False
            
            # Test VS Code version
            result = subprocess.run([str(vscode_exe), "--version"], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                self.logger.error(f"VS Code verification failed: {result.stderr}")
                return False
            
            version_info = result.stdout.strip().split('\n')[0]
            self.logger.info(f"VS Code verified: {version_info}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error verifying VS Code installation: {e}")
            return False


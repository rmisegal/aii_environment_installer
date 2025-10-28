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
            
            # Install essential extensions (with auto-close)
            if not self._install_extensions_with_autoclose():
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
                "python.formatting.provider": "black",
                "window.openWithoutArgumentsInNewWindow": "off",
                "extensions.ignoreRecommendations": True
            }
            
            settings_file = user_dir / "settings.json"
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            
            self.logger.info("VS Code configuration completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error configuring VS Code: {e}")
            return False
    
    def _install_extensions_with_autoclose(self) -> bool:
        """Install extensions with proper process handling"""
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

            # Kill any existing VS Code processes first - they might be blocking
            print("\nCleaning up any existing VS Code processes...")
            self._kill_vscode_processes(verbose=True)
            time.sleep(2)  # Give processes time to fully terminate

            # Test if VS Code can run basic commands
            print("Testing VS Code executable...")
            try:
                # Try version check with longer timeout and process killing
                test_result = subprocess.run(
                    [str(vscode_exe), "--version"],
                    capture_output=True,
                    text=True,
                    timeout=15,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )

                # Kill any windows that opened during test
                self._kill_vscode_processes()

                if test_result.returncode != 0:
                    self.logger.error("VS Code --version command failed")
                    print("⚠ VS Code may not be working correctly")
                    print("Skipping extension installation - you can install extensions manually later")
                    return True  # Don't fail the whole installation
                else:
                    version_line = test_result.stdout.strip().split('\n')[0] if test_result.stdout else "unknown"
                    print(f"[OK] VS Code version: {version_line}")

            except subprocess.TimeoutExpired:
                self.logger.error("VS Code --version timed out")
                print("⚠ VS Code --version command timed out")
                self._kill_vscode_processes()
                time.sleep(2)

                # Try one more time with a fresh slate
                print("Retrying VS Code test...")
                try:
                    test_result = subprocess.run(
                        [str(vscode_exe), "--version"],
                        capture_output=True,
                        text=True,
                        timeout=15,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                    )
                    self._kill_vscode_processes()

                    if test_result.returncode == 0:
                        print("[OK] VS Code working on retry")
                    else:
                        print("⚠ Skipping extension installation - install extensions manually later")
                        return True

                except Exception as e2:
                    self.logger.error(f"VS Code retry test failed: {e2}")
                    print("⚠ Cannot verify VS Code - skipping extension installation")
                    print("VS Code is installed but extensions must be added manually")
                    self._kill_vscode_processes()
                    return True

            except Exception as e:
                self.logger.error(f"VS Code test failed: {e}")
                print(f"⚠ Cannot test VS Code: {e}")
                print("Skipping extension installation - you can install extensions manually later")
                self._kill_vscode_processes()
                return True

            # Final cleanup before starting extension installation
            self._kill_vscode_processes()
            time.sleep(2)

            success_count = 0
            failed_extensions = []

            for i, extension in enumerate(extensions):
                print(f"\nInstalling extension {i+1}/{len(extensions)}: {extension}")

                try:
                    if self._install_single_extension_silent(extension, vscode_exe, user_data_path, extensions_path):
                        success_count += 1
                        print(f"[OK] Extension {extension} installed successfully")
                    else:
                        failed_extensions.append(extension)
                        print(f"[X] Extension {extension} failed to install")
                except Exception as e:
                    self.logger.error(f"Exception installing {extension}: {e}")
                    failed_extensions.append(extension)
                    print(f"[X] Extension {extension} failed with error")

                # Wait a bit between extensions
                time.sleep(2)

            # Clean up any VS Code processes after all installations complete
            self.logger.info("Cleaning up VS Code processes after extension installation")
            time.sleep(3)  # Give last extension time to finish
            self._kill_vscode_processes()

            self.logger.info(f"Extension installation completed: {success_count}/{len(extensions)} successful")

            if failed_extensions:
                self.logger.warning(f"Failed to install extensions: {failed_extensions}")
                print(f"\n⚠ Warning: Some extensions failed to install: {', '.join(failed_extensions)}")
                print("You can install them manually later by opening VS Code and searching for these extensions.")

            # Consider successful if at least 60% of extensions installed OR if none installed (might be network issue)
            if success_count == 0:
                print("\n⚠ No extensions installed automatically. This is not critical.")
                print("VS Code is installed and you can add extensions manually.")
                return True  # Don't fail installation

            return success_count >= len(extensions) * 0.6

        except Exception as e:
            self.logger.error(f"Error installing VS Code extensions: {e}")
            return False
    
    def _install_single_extension_silent(self, extension: str, vscode_exe: Path, user_data_path: Path, extensions_path: Path) -> bool:
        """Install a single VS Code extension silently with smart window closing"""
        try:
            self.logger.info(f"Installing extension: {extension}")

            # Check if extension is already installed
            if self._check_extension_installed(extension, extensions_path):
                self.logger.info(f"Extension {extension} is already installed")
                print(f"  [OK] Already installed, skipping")
                return True

            # Build command
            cmd = [
                str(vscode_exe),
                "--install-extension", extension,
                "--force",
                "--user-data-dir", str(user_data_path),
                "--extensions-dir", str(extensions_path)
            ]

            self.logger.info(f"Running: {' '.join(cmd)}")

            # Set environment variables
            env = os.environ.copy()
            env["VSCODE_CLI"] = "1"

            # Start the installation process without waiting
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            # Give extension time to download and start installing (increased from 3s)
            time.sleep(10)

            # Monitor and close VS Code windows that open during installation
            max_wait = 180  # 3 minutes max per extension
            start_time = time.time()
            closed_window = False
            window_close_time = None

            while process.poll() is None:  # While process is still running
                elapsed = time.time() - start_time

                if elapsed > max_wait:
                    self.logger.error(f"Extension installation timed out: {extension}")
                    process.kill()
                    return False

                # Check for VS Code windows every 3 seconds
                try:
                    result = subprocess.run(
                        ["tasklist", "/FI", "IMAGENAME eq Code.exe"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )

                    if "Code.exe" in result.stdout:
                        # Only close window if it's been open for at least 15 seconds
                        # This gives the extension time to download and install
                        if not closed_window:
                            if window_close_time is None:
                                window_close_time = time.time()
                                self.logger.info(f"VS Code window detected, waiting for installation to progress...")
                            elif time.time() - window_close_time > 15:
                                self.logger.info(f"Closing VS Code window to complete installation...")
                                print(f"  (Closing VS Code window to complete installation)")
                                closed_window = True

                                # Try multiple graceful close methods (mimics clicking X)
                                # Method 1: Send WM_CLOSE message via taskkill (graceful)
                                subprocess.run(
                                    ["taskkill", "/IM", "Code.exe"],
                                    capture_output=True,
                                    timeout=5
                                )
                                time.sleep(2)

                                # Check if still running
                                check = subprocess.run(
                                    ["tasklist", "/FI", "IMAGENAME eq Code.exe"],
                                    capture_output=True,
                                    text=True,
                                    timeout=5
                                )

                                # If still running, try PowerShell method (sends close message to window)
                                if "Code.exe" in check.stdout:
                                    self.logger.info("Trying alternative close method...")
                                    ps_cmd = '(Get-Process Code -ErrorAction SilentlyContinue).CloseMainWindow()'
                                    subprocess.run(
                                        ["powershell", "-Command", ps_cmd],
                                        capture_output=True,
                                        timeout=10
                                    )
                                    time.sleep(3)

                                    # Final check
                                    check = subprocess.run(
                                        ["tasklist", "/FI", "IMAGENAME eq Code.exe"],
                                        capture_output=True,
                                        text=True,
                                        timeout=5
                                    )

                                    # Only force kill as absolute last resort
                                    if "Code.exe" in check.stdout:
                                        self.logger.info("Graceful methods failed, force closing...")
                                        subprocess.run(
                                            ["taskkill", "/F", "/IM", "Code.exe"],
                                            capture_output=True,
                                            timeout=5
                                        )
                                        time.sleep(1)
                    else:
                        # Reset timer if window is not visible
                        window_close_time = None

                except:
                    pass

                time.sleep(3)

            # Get the result
            stdout, stderr = process.communicate(timeout=5)

            # Log output for debugging
            if stdout and stdout.strip():
                self.logger.info(f"Extension install stdout: {stdout.strip()}")
                print(f"  Output: {stdout.strip()}")
            if stderr and stderr.strip():
                self.logger.warning(f"Extension install stderr: {stderr.strip()}")
                print(f"  Error: {stderr.strip()}")

            if process.returncode == 0:
                self.logger.info(f"Successfully installed extension: {extension}")
                return True
            else:
                self.logger.warning(f"Failed to install extension {extension} (exit code {process.returncode})")
                # Check if extension is actually installed despite error code
                if self._check_extension_installed(extension, extensions_path):
                    self.logger.info(f"Extension {extension} appears to be installed despite error code")
                    print(f"  [OK] Extension found in extensions directory")
                    return True
                return False

        except subprocess.TimeoutExpired:
            self.logger.error(f"Extension installation timed out: {extension}")
            self._kill_vscode_processes()
            return False
        except Exception as e:
            self.logger.error(f"Error installing extension {extension}: {e}")
            self._kill_vscode_processes()
            return False
    
    def _check_extension_installed(self, extension: str, extensions_path: Path) -> bool:
        """Check if an extension is actually installed in the extensions directory"""
        try:
            if not extensions_path.exists():
                return False

            # Extension format: publisher.name-version
            # We need to check for folders starting with the extension ID
            extension_id = extension.lower()

            for item in extensions_path.iterdir():
                if item.is_dir() and item.name.lower().startswith(extension_id):
                    self.logger.info(f"Found extension directory: {item.name}")
                    return True

            return False
        except Exception as e:
            self.logger.error(f"Error checking extension installation: {e}")
            return False

    def _kill_vscode_processes(self, verbose: bool = False):
        """Kill any running VS Code processes"""
        try:
            # Kill all VS Code related processes
            processes = ["Code.exe", "code.exe", "CodeHelper.exe", "Electron.exe"]

            killed_any = False
            for process in processes:
                try:
                    # Check if process exists first
                    check_result = subprocess.run(
                        ["tasklist", "/FI", f"IMAGENAME eq {process}"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )

                    if process in check_result.stdout:
                        if verbose:
                            print(f"  Killing {process}...")
                        result = subprocess.run(
                            ["taskkill", "/F", "/IM", process],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        killed_any = True
                        if verbose and result.returncode == 0:
                            self.logger.info(f"Killed {process}")
                except Exception as e:
                    if verbose:
                        self.logger.debug(f"Could not kill {process}: {e}")

            if killed_any:
                time.sleep(2)  # Give more time if we actually killed something
            else:
                time.sleep(0.5)

        except Exception as e:
            self.logger.debug(f"Error in _kill_vscode_processes: {e}")
    
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


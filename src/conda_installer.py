#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conda Installer - Handles Miniconda installation and initial setup
"""

import os
import sys
import subprocess
import logging
import time
from pathlib import Path
from conda_downloader import CondaDownloader

class CondaInstaller:
    """Handles Miniconda installation operations"""

    def __init__(self, ai_env_path: Path, logs_path: Path):
        self.ai_env_path = ai_env_path
        self.logs_path = logs_path
        self.logger = logging.getLogger(__name__)

        # Paths - Check both AllUsers and JustMe locations
        self.all_users_path = Path("C:/ProgramData/miniconda3")
        self.just_me_path = ai_env_path / "Miniconda"

        # Determine installation path
        self.conda_path = self.just_me_path
        self.conda_exe = self.conda_path / "Scripts" / "conda.exe"

        # Downloader
        self.downloader = CondaDownloader(ai_env_path, logs_path)

    def check_existing_installation(self) -> dict:
        """
        Check if Miniconda is already installed in JustMe or AllUsers location
        Returns dict with 'found', 'location', 'type', and 'path'
        """
        result = {
            'found': False,
            'location': None,
            'type': None,
            'path': None
        }

        # Check AllUsers installation
        all_users_conda = self.all_users_path / "Scripts" / "conda.exe"
        if all_users_conda.exists():
            result['found'] = True
            result['location'] = str(self.all_users_path)
            result['type'] = 'AllUsers'
            result['path'] = str(all_users_conda)
            self.logger.info(f"Found AllUsers Miniconda at: {all_users_conda}")
            return result

        # Check JustMe installation (portable)
        just_me_conda = self.just_me_path / "Scripts" / "conda.exe"
        if just_me_conda.exists():
            result['found'] = True
            result['location'] = str(self.just_me_path)
            result['type'] = 'JustMe'
            result['path'] = str(just_me_conda)
            self.logger.info(f"Found JustMe Miniconda at: {just_me_conda}")
            return result

        self.logger.info("No existing Miniconda installation found")
        return result

    def install(self) -> bool:
        """Install Miniconda"""
        try:
            self.logger.info("Starting Miniconda installation")

            # Check for existing installation
            existing = self.check_existing_installation()
            if existing['found']:
                print(f"\nFound existing Miniconda installation:")
                print(f"  Type: {existing['type']}")
                print(f"  Location: {existing['location']}")
                print(f"  Path: {existing['path']}")

                # Update conda_path and conda_exe to point to existing installation
                if existing['type'] == 'AllUsers':
                    self.conda_path = self.all_users_path
                    self.conda_exe = self.all_users_path / "Scripts" / "conda.exe"
                else:
                    self.conda_path = self.just_me_path
                    self.conda_exe = self.just_me_path / "Scripts" / "conda.exe"

                print(f"\nUsing existing installation. Skipping download and installation.")

                # Verify existing installation
                if not self._verify_installation():
                    print("Existing installation verification failed. Installing fresh...")
                else:
                    # Initialize conda (update PATH for all terminals)
                    if not self._initialize_conda():
                        return False
                    return True

            # Download Miniconda installer
            installer_path = self.downloader.download_miniconda()
            if not installer_path:
                return False

            self.installer_path = installer_path

            # Install Miniconda
            if not self._install_miniconda():
                return False

            # Verify installation
            if not self._verify_installation():
                return False

            # Initialize conda and accept TOS
            if not self._initialize_conda():
                return False

            self.logger.info("Miniconda installation completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error installing Miniconda: {e}")
            return False
    
    def _install_miniconda(self) -> bool:
        """Install Miniconda using multiple methods"""
        try:
            self.logger.info(f"Installing Miniconda to: {self.conda_path}")
            print("Installing Miniconda (this may take a few minutes)...")
            
            # Create installation directory
            self.conda_path.mkdir(parents=True, exist_ok=True)
            
            # Try different installation methods
            success = False
            
            # Method 1: Standard silent installation
            print("Attempting standard silent installation...")
            if self._try_silent_install():
                success = True
            
            # Method 2: Interactive installation with timeout
            if not success:
                print("Silent installation failed, trying interactive mode...")
                if self._try_interactive_install():
                    success = True
            
            if not success:
                self.logger.error("All installation methods failed")
                return False
            
            self.logger.info("Miniconda installed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error installing Miniconda: {e}")
            return False
    
    def _try_silent_install(self) -> bool:
        """Try silent installation"""
        try:
            cmd = [
                str(self.installer_path),
                "/InstallationType=AllUsers",
                "/RegisterPython=0",
                "/AddToPath=1",
                "/S",  # Silent installation
                f"/D={self.all_users_path}"
            ]
            
            self.logger.info(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                self.logger.warning(f"Silent installation returned code {result.returncode}")
                return False
            
            return self._wait_for_installation()
            
        except subprocess.TimeoutExpired:
            self.logger.error("Silent installation timed out")
            return False
        except Exception as e:
            self.logger.error(f"Silent installation error: {e}")
            return False
    
    def _try_interactive_install(self) -> bool:
        """Try interactive installation"""
        try:
            cmd = [
                str(self.installer_path),
                "/InstallationType=AllUsers",
                "/RegisterPython=0",
                "/AddToPath=1",
                f"/D={self.all_users_path}"
            ]
            
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            try:
                stdout, stderr = process.communicate(timeout=300)
                
                if process.returncode != 0:
                    self.logger.warning(f"Interactive installation returned code {process.returncode}")
                    return False
                
                return self._wait_for_installation()
                
            except subprocess.TimeoutExpired:
                process.kill()
                self.logger.error("Interactive installation timed out")
                return False
                
        except Exception as e:
            self.logger.error(f"Interactive installation error: {e}")
            return False
    
    def _wait_for_installation(self) -> bool:
        """Wait for installation to complete"""
        try:
            max_wait = 300  # 5 minutes
            wait_time = 0

            # Check both possible locations
            all_users_exe = self.all_users_path / "Scripts" / "conda.exe"
            just_me_exe = self.just_me_path / "Scripts" / "conda.exe"

            while wait_time < max_wait:
                if all_users_exe.exists():
                    self.logger.info("Found conda.exe in AllUsers location")
                    self.conda_path = self.all_users_path
                    self.conda_exe = all_users_exe
                    return True

                if just_me_exe.exists():
                    self.logger.info("Found conda.exe in JustMe location")
                    self.conda_path = self.just_me_path
                    self.conda_exe = just_me_exe
                    return True

                time.sleep(5)
                wait_time += 5
                print(f"Waiting for installation to complete... ({wait_time}s)")

            self.logger.error("Conda executable not found after installation")
            return False

        except Exception as e:
            self.logger.error(f"Error waiting for installation: {e}")
            return False
    
    def _verify_installation(self) -> bool:
        """Verify conda installation comprehensively"""
        try:
            print("\nVerifying conda installation...")

            # Test 1: Check if conda.exe exists
            if not self.conda_exe.exists():
                self.logger.error("Conda executable not found")
                print("[X] Conda executable not found")
                return False
            print(f"[OK] Conda executable found at: {self.conda_exe}")

            # Test 2: Check conda version
            result = subprocess.run([str(self.conda_exe), "--version"],
                                  capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                self.logger.error(f"Conda version check failed: {result.stderr}")
                print("[X] Conda version check failed")
                return False

            conda_version = result.stdout.strip()
            self.logger.info(f"Conda verified: {conda_version}")
            print(f"[OK] Conda version: {conda_version}")

            # Test 3: Check if conda can be called via cmd.exe
            print("\nTesting conda accessibility from cmd...")
            test_cmd = f'"{self.conda_exe}" info --envs'
            result = subprocess.run(
                test_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                self.logger.warning(f"Conda info command failed: {result.stderr}")
                print("⚠ Warning: Conda info command failed, but continuing...")
            else:
                print("[OK] Conda can execute commands successfully")
                self.logger.info("Conda info command successful")

            # Test 4: Verify conda can list packages
            print("\nTesting conda package listing...")
            result = subprocess.run(
                [str(self.conda_exe), "list"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                self.logger.warning(f"Conda list failed: {result.stderr}")
                print("⚠ Warning: Conda package listing failed")
            else:
                print("[OK] Conda can list packages")

            # Test 5: Check conda configuration
            print("\nChecking conda configuration...")
            result = subprocess.run(
                [str(self.conda_exe), "config", "--show"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                print("[OK] Conda configuration accessible")
                self.logger.info("Conda configuration check passed")
            else:
                print("⚠ Warning: Could not read conda configuration")

            print("\n[OK] Conda installation verification completed")
            return True

        except subprocess.TimeoutExpired:
            self.logger.error("Conda verification timed out")
            print("[X] Conda verification timed out")
            return False
        except Exception as e:
            self.logger.error(f"Error verifying conda installation: {e}")
            print(f"[X] Error during verification: {e}")
            return False
    
    def _initialize_conda(self) -> bool:
        """Initialize conda and accept Terms of Service"""
        try:
            self.logger.info("Initializing conda and accepting Terms of Service")
            print("Configuring conda and accepting Terms of Service...")

            # Accept Terms of Service for default channels
            channels_to_accept = [
                "https://repo.anaconda.com/pkgs/main",
                "https://repo.anaconda.com/pkgs/r",
                "https://repo.anaconda.com/pkgs/msys2"
            ]

            for channel in channels_to_accept:
                self.logger.info(f"Accepting TOS for channel: {channel}")
                cmd = [str(self.conda_exe), "tos", "accept", "--override-channels", "--channel", channel]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

                if result.returncode != 0:
                    self.logger.warning(f"Failed to accept TOS for {channel}: {result.stderr}")
                else:
                    self.logger.info(f"TOS accepted for {channel}")

            # Add conda-forge channel (doesn't require TOS)
            self.logger.info("Adding conda-forge channel")
            cmd = [str(self.conda_exe), "config", "--add", "channels", "conda-forge"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                self.logger.warning(f"Failed to add conda-forge channel: {result.stderr}")
            else:
                self.logger.info("conda-forge channel added")

            # Set channel priority
            cmd = [str(self.conda_exe), "config", "--set", "channel_priority", "flexible"]
            subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            # Initialize conda for cmd (this updates PATH in registry for all terminals)
            self.logger.info("Initializing conda for command prompt (all terminals)")
            cmd = [str(self.conda_exe), "init", "cmd.exe"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                self.logger.warning(f"Conda init warning: {result.stderr}")
            else:
                print("Conda PATH configured for all cmd terminals")

            # Add conda to system PATH permanently (for AllUsers installation)
            if self.conda_path == self.all_users_path:
                self._add_to_system_path()

            return True

        except Exception as e:
            self.logger.error(f"Error initializing conda: {e}")
            return False

    def _add_to_system_path(self):
        """Add conda to system PATH for all users"""
        try:
            self.logger.info("Adding conda to system PATH for all users")
            print("Adding conda to system PATH for all cmd terminals...")

            conda_scripts = str(self.conda_path / "Scripts")
            conda_condabin = str(self.conda_path / "condabin")

            # Use setx to add to system PATH (requires admin)
            cmd = f'setx /M PATH "%PATH%;{conda_scripts};{conda_condabin}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                self.logger.warning(f"Failed to add to system PATH: {result.stderr}")
                print("Warning: Could not add conda to system PATH automatically.")
                print("You may need to add it manually or restart your terminal.")
            else:
                self.logger.info("Conda added to system PATH successfully")
                print("Conda added to system PATH - restart terminals to apply changes")

        except Exception as e:
            self.logger.warning(f"Error adding to system PATH: {e}")
            print("Warning: Could not update system PATH automatically.")
    
    def get_conda_exe(self) -> Path:
        """Get path to conda executable"""
        return self.conda_exe

    def test_conda_accessibility(self) -> dict:
        """
        Comprehensive test to verify conda can be called from cmd terminals
        Returns dict with test results
        """
        results = {
            'executable_exists': False,
            'version_check': False,
            'cmd_accessible': False,
            'can_list_envs': False,
            'can_list_packages': False,
            'path_configured': False,
            'details': {}
        }

        try:
            print("\n" + "="*60)
            print("CONDA ACCESSIBILITY TEST")
            print("="*60)

            # Test 1: Executable exists
            print("\n[Test 1] Checking conda executable...")
            if self.conda_exe.exists():
                results['executable_exists'] = True
                print(f"[OK] PASS: Conda found at {self.conda_exe}")
            else:
                print(f"[X] FAIL: Conda not found at {self.conda_exe}")
                return results

            # Test 2: Direct version check
            print("\n[Test 2] Testing direct conda execution...")
            try:
                result = subprocess.run(
                    [str(self.conda_exe), "--version"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    results['version_check'] = True
                    version = result.stdout.strip()
                    results['details']['version'] = version
                    print(f"[OK] PASS: {version}")
                else:
                    print(f"[X] FAIL: Return code {result.returncode}")
            except Exception as e:
                print(f"[X] FAIL: {e}")

            # Test 3: Accessibility from cmd.exe (simulating new terminal)
            print("\n[Test 3] Testing conda from cmd.exe (new terminal simulation)...")
            try:
                # Try calling conda without full path (as user would in terminal)
                result = subprocess.run(
                    "conda --version",
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    results['cmd_accessible'] = True
                    print(f"[OK] PASS: Conda accessible from cmd terminals")
                    print(f"  Output: {result.stdout.strip()}")
                else:
                    print(f"[X] FAIL: Conda not in PATH or not accessible")
                    print(f"  You may need to restart cmd terminals or add to PATH")
            except Exception as e:
                print(f"[X] FAIL: {e}")

            # Test 4: List environments
            print("\n[Test 4] Testing environment listing...")
            try:
                result = subprocess.run(
                    [str(self.conda_exe), "env", "list"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    results['can_list_envs'] = True
                    print(f"[OK] PASS: Can list conda environments")
                    # Parse environments
                    envs = [line.split()[0] for line in result.stdout.split('\n')
                           if line and not line.startswith('#') and line.strip()]
                    results['details']['environments'] = envs
                    if envs:
                        print(f"  Found {len(envs)} environment(s)")
                else:
                    print(f"[X] FAIL: Cannot list environments")
            except Exception as e:
                print(f"[X] FAIL: {e}")

            # Test 5: List packages in base
            print("\n[Test 5] Testing package listing...")
            try:
                result = subprocess.run(
                    [str(self.conda_exe), "list", "-n", "base"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    results['can_list_packages'] = True
                    print(f"[OK] PASS: Can list conda packages")
                else:
                    print(f"[X] FAIL: Cannot list packages")
            except Exception as e:
                print(f"[X] FAIL: {e}")

            # Test 6: Check if conda in PATH
            print("\n[Test 6] Checking PATH configuration...")
            try:
                # Check if conda Scripts directory is in PATH
                conda_scripts = str(self.conda_path / "Scripts")
                conda_condabin = str(self.conda_path / "condabin")

                result = subprocess.run(
                    "echo %PATH%",
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                path_env = result.stdout.lower()
                if conda_scripts.lower() in path_env or conda_condabin.lower() in path_env:
                    results['path_configured'] = True
                    print(f"[OK] PASS: Conda directories found in PATH")
                else:
                    print(f"⚠ WARNING: Conda directories not in current PATH")
                    print(f"  Expected: {conda_scripts}")
                    print(f"  or: {conda_condabin}")
                    print(f"  You may need to restart your terminal")
            except Exception as e:
                print(f"⚠ WARNING: Could not check PATH: {e}")

            # Summary
            print("\n" + "="*60)
            print("TEST SUMMARY")
            print("="*60)
            total_tests = 6
            passed_tests = sum([
                results['executable_exists'],
                results['version_check'],
                results['cmd_accessible'],
                results['can_list_envs'],
                results['can_list_packages'],
                results['path_configured']
            ])

            print(f"Passed: {passed_tests}/{total_tests} tests")

            if passed_tests == total_tests:
                print("\n[OK] ALL TESTS PASSED - Conda fully operational")
                results['overall'] = 'PASS'
            elif passed_tests >= 4:
                print("\n⚠ PARTIAL - Conda working but may need terminal restart")
                results['overall'] = 'PARTIAL'
            else:
                print("\n[X] FAILED - Conda not properly configured")
                results['overall'] = 'FAIL'

            print("="*60 + "\n")

        except Exception as e:
            self.logger.error(f"Error during conda accessibility test: {e}")
            print(f"\n[X] TEST ERROR: {e}")
            results['overall'] = 'ERROR'
            results['error'] = str(e)

        return results


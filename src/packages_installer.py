#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Packages Installer - Handles Python package installation in virtual environment
"""

import os
import sys
import json
import logging
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple

class PackagesInstaller:
    """Handles Python package installation in virtual environment"""
    
    def __init__(self, ai_env_path: Path, logs_path: Path):
        self.ai_env_path = ai_env_path
        self.logs_path = logs_path
        self.logger = logging.getLogger(__name__)
        
        # Paths
        self.venv_path = ai_env_path / "venv" / "AI2025"
        self.python_exe = self.venv_path / "Scripts" / "python.exe"
        self.pip_exe = self.venv_path / "Scripts" / "pip.exe"
        
    def install_packages(self, packages: List[str]) -> bool:
        """Install list of Python packages"""
        try:
            self.logger.info(f"Installing {len(packages)} Python packages")
            
            if not self._verify_environment():
                return False
            
            # Upgrade pip first
            if not self._upgrade_pip():
                self.logger.warning("Failed to upgrade pip, continuing anyway")
            
            # Install packages
            success_count = 0
            failed_packages = []
            
            for package in packages:
                if self._install_single_package(package):
                    success_count += 1
                else:
                    failed_packages.append(package)
            
            # Report results
            self.logger.info(f"Package installation completed: {success_count}/{len(packages)} successful")
            
            if failed_packages:
                self.logger.warning(f"Failed packages: {', '.join(failed_packages)}")
            
            # Create requirements.txt
            self._create_requirements_file(packages)
            
            # Verify critical packages
            if not self._verify_critical_packages():
                self.logger.warning("Some critical packages may not be working correctly")
            
            return len(failed_packages) == 0
            
        except Exception as e:
            self.logger.error(f"Package installation failed: {e}")
            return False
    
    def _verify_environment(self) -> bool:
        """Verify virtual environment is ready"""
        try:
            if not self.venv_path.exists():
                self.logger.error("Virtual environment not found")
                return False
            
            if not self.python_exe.exists():
                self.logger.error("Python executable not found in virtual environment")
                return False
            
            if not self.pip_exe.exists():
                self.logger.error("Pip executable not found in virtual environment")
                return False
            
            # Test Python
            result = subprocess.run([str(self.python_exe), "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                self.logger.error("Python test failed")
                return False
            
            self.logger.info(f"Environment verified: {result.stdout.strip()}")
            return True
            
        except Exception as e:
            self.logger.error(f"Environment verification failed: {e}")
            return False
    
    def _upgrade_pip(self) -> bool:
        """Upgrade pip to latest version"""
        try:
            self.logger.info("Upgrading pip...")
            
            cmd = [str(self.python_exe), "-m", "pip", "install", "--upgrade", "pip"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                self.logger.info("Pip upgraded successfully")
                return True
            else:
                self.logger.error(f"Pip upgrade failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error upgrading pip: {e}")
            return False
    
    def _install_single_package(self, package: str) -> bool:
        """Install a single package"""
        try:
            self.logger.info(f"Installing package: {package}")
            
            # Parse package specification (handle version constraints)
            package_name = package.split('>=')[0].split('==')[0].split('<=')[0].split('>')[0].split('<')[0].split('!=')[0]
            
            cmd = [str(self.pip_exe), "install", package, "--no-warn-script-location"]
            
            # Add timeout and show progress
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True
            )
            
            output_lines = []
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    line = output.strip()
                    output_lines.append(line)
                    
                    # Show progress for large packages
                    if any(keyword in line.lower() for keyword in ['downloading', 'installing', 'building']):
                        print(f"  {line}")
            
            return_code = process.poll()
            
            if return_code == 0:
                self.logger.info(f"Successfully installed: {package}")
                return True
            else:
                error_output = '\n'.join(output_lines[-10:])  # Last 10 lines
                self.logger.error(f"Failed to install {package}: {error_output}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error installing package {package}: {e}")
            return False
    
    def _create_requirements_file(self, packages: List[str]):
        """Create requirements.txt file"""
        try:
            requirements_file = self.ai_env_path / "requirements.txt"
            
            with open(requirements_file, 'w', encoding='utf-8') as f:
                f.write("# AI Environment Requirements\n")
                f.write("# Generated automatically during installation\n\n")
                
                for package in sorted(packages):
                    f.write(f"{package}\n")
            
            self.logger.info(f"Requirements file created: {requirements_file}")
            
        except Exception as e:
            self.logger.error(f"Error creating requirements file: {e}")
    
    def _verify_critical_packages(self) -> bool:
        """Verify critical packages are working"""
        try:
            self.logger.info("Verifying critical packages...")
            
            # Test critical imports
            test_imports = [
                ("langchain", "LangChain framework"),
                ("langraph", "LangGraph framework"),
                ("streamlit", "Streamlit web framework"),
                ("fastapi", "FastAPI framework"),
                ("jupyter", "Jupyter notebook"),
                ("pandas", "Pandas data analysis"),
                ("numpy", "NumPy numerical computing"),
                ("requests", "HTTP requests library")
            ]
            
            failed_imports = []
            
            for module, description in test_imports:
                if not self._test_import(module):
                    failed_imports.append((module, description))
            
            if failed_imports:
                self.logger.warning("Failed to import critical packages:")
                for module, description in failed_imports:
                    self.logger.warning(f"  - {module}: {description}")
                return False
            else:
                self.logger.info("All critical packages verified successfully")
                return True
                
        except Exception as e:
            self.logger.error(f"Error verifying critical packages: {e}")
            return False
    
    def _test_import(self, module_name: str) -> bool:
        """Test if a module can be imported"""
        try:
            cmd = [str(self.python_exe), "-c", f"import {module_name}; print(f'{module_name} imported successfully')"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return True
            else:
                self.logger.debug(f"Import test failed for {module_name}: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.debug(f"Error testing import for {module_name}: {e}")
            return False
    
    def install_ai_packages(self) -> bool:
        """Install AI-specific packages"""
        ai_packages = [
            # Core AI/ML packages
            "langchain>=0.1.0",
            "langgraph>=0.1.0",  # Fixed: was "langraph"
            "pyautogen>=0.2.0",
            
            # LLM and ML libraries
            "transformers",
            "torch",
            "sentence-transformers",
            "chromadb",
            "faiss-cpu",
            
            # Web frameworks
            "streamlit",
            "fastapi",
            "uvicorn",
            "gradio",
            
            # Data science
            "pandas",
            "numpy",
            "matplotlib",
            "seaborn",
            "plotly",
            "scikit-learn",

            # ML Monitoring & Tracking
            "tensorboard",
            "mlflow",

            # Development tools
            "jupyter",
            "jupyterlab",
            "ipykernel",
            "notebook",
            
            # Utilities
            "requests",
            "python-dotenv",
            "pydantic",
            "httpx",
            "aiohttp",
            "beautifulsoup4",
            "lxml",
            
            # Code quality
            "black",
            "pylint",
            "isort",
            "flake8"
        ]
        
        return self.install_packages(ai_packages)
    
    def install_jupyter_extensions(self) -> bool:
        """Install Jupyter extensions"""
        try:
            self.logger.info("Installing Jupyter extensions...")
            
            # Install JupyterLab extensions
            extensions = [
                "jupyterlab-git",
                "jupyterlab-lsp",
                "jupyter-ai"
            ]
            
            for extension in extensions:
                cmd = [str(self.pip_exe), "install", extension]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                
                if result.returncode == 0:
                    self.logger.info(f"Installed Jupyter extension: {extension}")
                else:
                    self.logger.warning(f"Failed to install Jupyter extension {extension}: {result.stderr}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error installing Jupyter extensions: {e}")
            return False
    
    def create_package_info(self) -> bool:
        """Create package information file"""
        try:
            # Get installed packages
            cmd = [str(self.pip_exe), "list", "--format=json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                self.logger.error("Failed to get package list")
                return False
            
            packages_data = json.loads(result.stdout)
            
            # Create package info
            package_info = {
                "installation_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "python_version": self._get_python_version(),
                "pip_version": self._get_pip_version(),
                "total_packages": len(packages_data),
                "packages": packages_data
            }
            
            info_file = self.ai_env_path / "package_info.json"
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(package_info, f, indent=2)
            
            self.logger.info(f"Package information saved: {info_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating package info: {e}")
            return False
    
    def _get_python_version(self) -> str:
        """Get Python version"""
        try:
            result = subprocess.run([str(self.python_exe), "--version"], 
                                  capture_output=True, text=True, timeout=10)
            return result.stdout.strip() if result.returncode == 0 else "Unknown"
        except:
            return "Unknown"
    
    def _get_pip_version(self) -> str:
        """Get pip version"""
        try:
            result = subprocess.run([str(self.pip_exe), "--version"], 
                                  capture_output=True, text=True, timeout=10)
            return result.stdout.strip() if result.returncode == 0 else "Unknown"
        except:
            return "Unknown"
    
    def get_package_status(self) -> Dict[str, bool]:
        """Get status of critical packages"""
        critical_packages = [
            "langchain", "langraph", "pyautogen", "streamlit", 
            "fastapi", "jupyter", "pandas", "numpy", "requests"
        ]
        
        status = {}
        for package in critical_packages:
            status[package] = self._test_import(package)
        
        return status


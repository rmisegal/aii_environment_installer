#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conda Manager - Handles conda environments and package management
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional

class CondaManager:
    """Manages conda environments and packages"""
    
    # Packages that should be installed directly via pip (not conda)
    PIP_ONLY_PACKAGES = {
        "torch", "torch>=", "torch==", "torch>", "torch<",
        "torchvision", "torchvision>=", "torchvision==", "torchvision>", "torchvision<",
        "torchaudio", "torchaudio>=", "torchaudio==", "torchaudio>", "torchaudio<",
        "sentence-transformers", "sentence-transformers>=", "sentence-transformers==",
        "openai", "openai>=", "openai==",
        "langchain-openai", "langchain-openai>=", "langchain-openai==",
        "transformers", "transformers>=", "transformers==",
        "accelerate", "accelerate>=", "accelerate==",
        "pandas", "pandas>=", "pandas==", "pandas>", "pandas<",
        "numpy", "numpy>=", "numpy==", "numpy>", "numpy<",
        "scikit-learn", "scikit-learn>=", "scikit-learn==",
        "matplotlib", "matplotlib>=", "matplotlib==",
        "seaborn", "seaborn>=", "seaborn==",
        "plotly", "plotly>=", "plotly=="
    }
    
    def __init__(self, conda_exe: Path, ai_env_path: Path):
        self.conda_exe = conda_exe
        self.ai_env_path = ai_env_path
        self.logger = logging.getLogger(__name__)
    
    def create_environment(self, env_name: str = "AI2025", python_version: str = "3.10") -> bool:
        """Create conda environment"""
        try:
            self.logger.info(f"Creating conda environment: {env_name}")
            print(f"Creating conda environment: {env_name} with Python {python_version}")
            
            # Create environment with specific Python version using conda-forge
            cmd = [
                str(self.conda_exe), 
                "create", 
                "--name", env_name,
                f"python={python_version}",
                "--channel", "conda-forge",
                "--yes"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode != 0:
                self.logger.error(f"Failed to create conda environment: {result.stderr}")
                
                # Try with default channels if conda-forge fails
                self.logger.info("Retrying with default channels...")
                cmd = [
                    str(self.conda_exe), 
                    "create", 
                    "--name", env_name,
                    f"python={python_version}",
                    "--yes"
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
                
                if result.returncode != 0:
                    self.logger.error(f"Failed to create conda environment with default channels: {result.stderr}")
                    return False
            
            # Verify environment was created
            if not self._verify_environment(env_name):
                return False
            
            self.logger.info(f"Conda environment '{env_name}' created successfully")
            print(f"Environment '{env_name}' created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating conda environment: {e}")
            return False
    
    def _verify_environment(self, env_name: str) -> bool:
        """Verify conda environment exists"""
        try:
            cmd = [str(self.conda_exe), "env", "list"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                self.logger.error("Failed to list conda environments")
                return False
            
            # Check if environment exists in the list
            if env_name in result.stdout:
                return True
            else:
                self.logger.error(f"Environment '{env_name}' not found in conda env list")
                return False
                
        except Exception as e:
            self.logger.error(f"Error verifying environment: {e}")
            return False
    
    def _should_use_pip(self, package: str) -> bool:
        """Check if package should be installed via pip only"""
        # Extract base package name (remove version specifiers)
        package_name = package.split('>=')[0].split('==')[0].split('>')[0].split('<')[0].split('!')[0].strip()
        
        # Check if base package name is in pip-only list
        if package_name in self.PIP_ONLY_PACKAGES:
            return True
            
        # Check if any pip-only package is a substring of the current package
        for pip_pkg in self.PIP_ONLY_PACKAGES:
            pip_base = pip_pkg.split('>=')[0].split('==')[0].split('>')[0].split('<')[0].strip()
            if pip_base == package_name:
                return True
                
        return False
    
    def install_package(self, package: str, env_name: str = "AI2025", use_pip: bool = False, timeout: int = 300) -> bool:
        """Install package in conda environment"""
        try:
            self.logger.info(f"Installing package '{package}' in environment '{env_name}'")
            
            # Fix common package name issues
            fixed_package = self._fix_package_name(package)
            if fixed_package != package:
                self.logger.info(f"Fixed package name: {package} -> {fixed_package}")
                package = fixed_package
            
            # Check if this package should use pip directly
            if self._should_use_pip(package) and not use_pip:
                self.logger.info(f"Package '{package}' is configured for pip-only installation")
                print(f"Using pip for {package} (pip-only package)")
                return self.install_package(package, env_name, use_pip=True, timeout=timeout)
            
            # Determine timeout based on package
            if "sentence-transformers" in package:
                timeout = 600  # 10 minutes for large packages
            elif "torch" in package or "transformers" in package:
                timeout = 500  # 8+ minutes for ML packages
            elif "streamlit" in package or "matplotlib" in package:
                timeout = 400  # 6+ minutes for visualization packages
            
            if use_pip:
                # Use pip within conda environment
                cmd = [
                    str(self.conda_exe), "run", 
                    "--name", env_name,
                    "pip", "install", package
                ]
            else:
                # Use conda to install with conda-forge first
                cmd = [
                    str(self.conda_exe), "install", 
                    "--name", env_name,
                    "--channel", "conda-forge",
                    package, "--yes"
                ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            
            if result.returncode != 0:
                self.logger.warning(f"Conda install failed for {package}, trying pip: {result.stderr}")
                
                # Fallback to pip if conda fails
                if not use_pip:
                    return self.install_package(package, env_name, use_pip=True, timeout=timeout)
                else:
                    self.logger.error(f"Failed to install {package}: {result.stderr}")
                    return False
            
            self.logger.info(f"Successfully installed: {package}")
            return True
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Error installing package {package}: Command timed out after {timeout} seconds")
            return False
        except Exception as e:
            self.logger.error(f"Error installing package {package}: {e}")
            return False
    
    def _fix_package_name(self, package: str) -> str:
        """Fix common package name issues"""
        # Fix langraph -> langgraph
        if package.startswith("langraph"):
            return package.replace("langraph", "langgraph", 1)
        return package
    
    def install_packages_batch(self, packages: List[str], env_name: str = "AI2025") -> bool:
        """Install multiple packages in conda environment"""
        try:
            self.logger.info(f"Installing {len(packages)} packages in environment '{env_name}'")
            
            success_count = 0
            failed_packages = []
            
            for package in packages:
                print(f"Installing: {package}")
                if self.install_package(package, env_name):
                    success_count += 1
                else:
                    failed_packages.append(package)
            
            self.logger.info(f"Package installation completed: {success_count}/{len(packages)} successful")
            
            if failed_packages:
                self.logger.warning(f"Failed to install packages: {failed_packages}")
                print(f"Warning: Failed to install some packages: {failed_packages}")
            
            # Consider successful if at least 80% of packages installed
            return success_count >= len(packages) * 0.8
            
        except Exception as e:
            self.logger.error(f"Error installing packages batch: {e}")
            return False
    
    def get_environment_info(self, env_name: str = "AI2025") -> Dict:
        """Get information about conda environment"""
        try:
            cmd = [str(self.conda_exe), "info", "--envs"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return {}
            
            # Parse environment info
            env_info = {
                "name": env_name,
                "conda_version": self._get_conda_version(),
                "python_version": self._get_python_version(env_name),
                "packages": self._get_installed_packages(env_name)
            }
            
            return env_info
            
        except Exception as e:
            self.logger.error(f"Error getting environment info: {e}")
            return {}
    
    def _get_conda_version(self) -> str:
        """Get conda version"""
        try:
            result = subprocess.run([str(self.conda_exe), "--version"], 
                                  capture_output=True, text=True, timeout=30)
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except:
            return "unknown"
    
    def _get_python_version(self, env_name: str) -> str:
        """Get Python version in environment"""
        try:
            cmd = [str(self.conda_exe), "run", "--name", env_name, "python", "--version"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except:
            return "unknown"
    
    def _get_installed_packages(self, env_name: str) -> List[str]:
        """Get list of installed packages"""
        try:
            cmd = [str(self.conda_exe), "list", "--name", env_name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return []
            
            packages = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('#'):
                    parts = line.split()
                    if len(parts) >= 2:
                        packages.append(f"{parts[0]}=={parts[1]}")
            
            return packages
            
        except:
            return []
    
    def create_activation_script(self, env_name: str = "AI2025") -> bool:
        """Create conda environment activation script"""
        try:
            script_path = self.ai_env_path / "activate_ai_env.bat"
            
            script_content = f"""@echo off
title AI Environment - {env_name} (Conda)

set "AI_ENV_PATH={self.ai_env_path}"
set "CONDA_PATH=%AI_ENV_PATH%\\Miniconda"
set "VSCODE_PATH=%AI_ENV_PATH%\\VSCode"
set "OLLAMA_PATH=%AI_ENV_PATH%\\Ollama"

:: Initialize conda
call "%CONDA_PATH%\\Scripts\\activate.bat"

:: Activate AI2025 environment
call conda activate {env_name}

:: Set additional paths
set "PATH=%VSCODE_PATH%;%OLLAMA_PATH%;%PATH%"

:: Set Ollama configuration
set "OLLAMA_HOST=127.0.0.1:11434"
set "OLLAMA_MODELS=%AI_ENV_PATH%\\Models"

echo.
echo ================================================================
echo                    AI Environment Activated                   
echo                    {env_name} (Conda Environment)             
echo ================================================================
echo.
echo Environment: {env_name}
echo Python: %CONDA_PREFIX%\\python.exe
echo Conda: %CONDA_PATH%\\Scripts\\conda.exe
echo.
echo Available commands:
echo   code .              - Open VS Code
echo   python              - Run Python
echo   jupyter lab         - Start Jupyter Lab
echo   conda list          - List installed packages
echo   conda install pkg   - Install new package
echo   ollama list         - List available models
echo   ollama run llama2   - Run Llama2 model
echo.

cmd /k
"""
            
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            self.logger.info(f"Activation script created: {script_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating activation script: {e}")
            return False


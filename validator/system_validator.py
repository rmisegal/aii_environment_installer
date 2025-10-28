#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Validator - Comprehensive testing of the AI Environment installation
Version: 2.1.0 - Fixed for Conda Environment (2025-08-11)
"""

import os
import sys
import json
import logging
import subprocess
import time
import requests
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# Version information
VALIDATOR_VERSION = "2.1.0"
VALIDATOR_DATE = "2025-08-11"
VALIDATOR_DESCRIPTION = "Fixed for Conda Environment"

def find_ai_environment():
    """
    Search for AI_Environment installation in common locations.
    This function is defined before SystemValidator class so it can be used in __init__.

    Returns:
        Path: Path to AI_Environment if found, None otherwise
    """
    # Common installation locations to search
    search_paths = [
        Path("D:/AI_Environment"),
        Path("E:/AI_Environment"),
        Path("F:/AI_Environment"),
        Path("F:/AI_Lab/AI_Environment"),
        Path("C:/AI_Environment"),
    ]

    # Also search in current drive
    for drive in ['C', 'D', 'E', 'F', 'G']:
        search_paths.append(Path(f"{drive}:/AI_Environment"))
        search_paths.append(Path(f"{drive}:/AI_Lab/AI_Environment"))

    # Check each path
    for path in search_paths:
        if path.exists() and (path / "activate_ai_env.bat").exists():
            return path

    return None

class SystemValidator:
    """Comprehensive system validation for AI Environment"""
    
    def __init__(self, ai_env_path: Path = None):
        """Initialize validator with AI environment path"""
        # If no path provided, try to find it automatically
        if ai_env_path is None:
            ai_env_path = find_ai_environment()
            if ai_env_path is None:
                # Fallback to D:/AI_Environment for backward compatibility
                ai_env_path = Path("D:/AI_Environment")

        self.ai_env_path = ai_env_path

        # Setup logging
        self.setup_logging()

        # Detect Miniconda installation location (portable or AllUsers)
        self.conda_path, self.conda_location_type = self._detect_conda_path()
        self.conda_env_path = self.conda_path / "envs" / "AI2025"

        # Other component paths
        self.vscode_path = self.ai_env_path / "VSCode"
        self.ollama_path = self.ai_env_path / "Ollama"
        self.models_path = self.ai_env_path / "Models"
        self.projects_path = self.ai_env_path / "Projects"

    def _detect_conda_path(self) -> tuple:
        """
        Detect Miniconda installation location dynamically
        Returns: (conda_path, location_type)
        """
        # Check portable location first
        portable_path = self.ai_env_path / "Miniconda"
        portable_conda = portable_path / "Scripts" / "conda.exe"

        if portable_conda.exists():
            return (portable_path, "Portable")

        # Check common AllUsers/system locations
        common_paths = [
            Path("C:/ProgramData/miniconda3"),
            Path("C:/ProgramData/anaconda3"),
            Path(os.path.expanduser("~/miniconda3")),
            Path(os.path.expanduser("~/anaconda3")),
            Path(os.environ.get("LOCALAPPDATA", "C:/Users/Default/AppData/Local")) / "miniconda3",
        ]

        for conda_path in common_paths:
            conda_exe = conda_path / "Scripts" / "conda.exe"
            if conda_exe.exists():
                return (conda_path, "System")

        # Try to find conda via PATH
        import shutil
        conda_executable = shutil.which("conda")
        if conda_executable:
            # Get base path from conda
            try:
                result = subprocess.run([conda_executable, "info", "--base"],
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    conda_base = Path(result.stdout.strip())
                    if conda_base.exists():
                        return (conda_base, "SystemPATH")
            except:
                pass

        # Default to portable path even if not found (for error messages)
        return (portable_path, "NotFound")

    def setup_logging(self):
        """Setup logging for validation"""
        logs_path = self.ai_env_path / "Logs"
        logs_path.mkdir(exist_ok=True)
        
        log_file = logs_path / f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def run_validation_suite(self) -> Dict:
        """Run complete validation suite"""
        try:
            self.start_time = time.time()
            
            # Display version information
            version_info = f"System Validator v{VALIDATOR_VERSION} ({VALIDATOR_DATE}) - {VALIDATOR_DESCRIPTION}"
            print(f"\n🔧 {version_info}")
            print("=" * 80)
            self.logger.info(f"Starting validation with {version_info}")
            
            print("\n" + "=" * 80)
            print("🧪 AI ENVIRONMENT VALIDATION SUITE")
            print("=" * 80)
            
            # Define test suite
            tests = [
                ("System Requirements", self.validate_system_requirements),
                ("Directory Structure", self.validate_directory_structure),
                ("Python Installation", self.validate_python_installation),
                ("Conda Environment", self.validate_conda_environment),
                ("Python Packages", self.validate_python_packages),
                ("VS Code Installation", self.validate_vscode_installation),
                ("Ollama Installation", self.validate_ollama_installation),
                ("LLM Models", self.validate_llm_models),
                ("Integration Tests", self.validate_integration_tests),
                ("Performance Tests", self.validate_performance_tests)
            ]
            
            # Initialize results
            self.validation_results = {}
            
            # Run each test
            for test_name, test_func in tests:
                print(f"\n📋 Running: {test_name}")
                print("-" * 60)
                
                try:
                    result = test_func()
                    self.validation_results[test_name] = result
                    
                    if result["status"] == "PASS":
                        print(f"✅ {test_name}: PASSED")
                    elif result["status"] == "WARN":
                        print(f"⚠️  {test_name}: WARNING")
                    else:
                        print(f"❌ {test_name}: FAILED")
                        
                    if result.get("details"):
                        for detail in result["details"]:
                            print(f"   • {detail}")
                            
                except Exception as e:
                    self.validation_results[test_name] = {
                        "status": "ERROR",
                        "message": str(e),
                        "details": []
                    }
                    print(f"💥 {test_name}: ERROR - {e}")
            
            # Generate summary report
            self.generate_validation_report()
            
            return self.validation_results
            
        except Exception as e:
            self.logger.error(f"Validation suite failed: {e}")
            return {"error": str(e)}
    
    def validate_system_requirements(self) -> Dict:
        """Validate system requirements"""
        details = []
        status = "PASS"
        
        try:
            # Check OS
            import platform
            os_info = platform.platform()
            details.append(f"Operating System: {os_info}")
            
            # Check disk space
            if self.ai_env_path.exists():
                import shutil
                total, used, free = shutil.disk_usage(self.ai_env_path)
                free_gb = free / (1024**3)
                details.append(f"Available disk space: {free_gb:.1f} GB")
                
                if free_gb < 10:
                    status = "WARN"
                    details.append("⚠️  Low disk space (< 10 GB)")
            
            # Check RAM
            try:
                import psutil
                ram_gb = psutil.virtual_memory().total / (1024**3)
                details.append(f"Total RAM: {ram_gb:.1f} GB")
                
                if ram_gb < 8:
                    status = "WARN"
                    details.append("⚠️  Low RAM (< 8 GB)")
            except ImportError:
                details.append("RAM check skipped (psutil not available)")
            
            return {
                "status": status,
                "message": "System requirements check completed",
                "details": details
            }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"System requirements check failed: {e}",
                "details": details
            }
    
    def validate_directory_structure(self) -> Dict:
        """Validate directory structure"""
        details = []
        status = "PASS"

        # Show detected Miniconda location
        if self.conda_location_type != "NotFound":
            details.append(f"ℹ️  Miniconda detected: {self.conda_location_type} installation at {self.conda_path}")

        required_dirs = [
            (self.ai_env_path, "AI_Environment"),
            (self.conda_path, f"Miniconda ({self.conda_location_type})"),
            (self.conda_env_path, "AI2025 Environment"),
            (self.vscode_path, "VSCode"),
            (self.ollama_path, "Ollama"),
            (self.models_path, "Models"),
            (self.projects_path, "Projects")
        ]

        for directory, name in required_dirs:
            if directory.exists():
                details.append(f"✅ {name}: Found")
            else:
                status = "FAIL"
                details.append(f"❌ {name}: Missing")

        return {
            "status": status,
            "message": "Directory structure validation completed",
            "details": details
        }
    
    def validate_python_installation(self) -> Dict:
        """Validate Python installation (conda-based)"""
        details = []
        status = "PASS"
        
        try:
            conda_python = self.conda_env_path / "python.exe"
            conda_pip = self.conda_env_path / "Scripts" / "pip.exe"
            conda_exe = self.conda_path / "Scripts" / "conda.exe"
            
            # Check conda installation
            if self.conda_path.exists():
                details.append("✅ Miniconda installation found")
            else:
                status = "FAIL"
                details.append("❌ Miniconda installation missing")
                return {"status": status, "message": "Miniconda not found", "details": details}
            
            # Check conda executable
            if conda_exe.exists():
                details.append("✅ Conda executable found")
            else:
                status = "FAIL"
                details.append("❌ Conda executable missing")
            
            # Check Python in conda environment
            if conda_python.exists():
                details.append(f"✅ Python executable found in conda environment ({self.conda_location_type})")
            else:
                status = "FAIL"
                details.append(f"❌ Python executable missing in conda environment")
                details.append(f"   Expected: {conda_python}")
                return {"status": status, "message": f"Python not found in conda environment\nExpected: {conda_python}", "details": details}
            
            # Check pip in conda environment
            if conda_pip.exists():
                details.append("✅ Pip executable found in conda environment")
            else:
                status = "WARN"
                details.append("⚠️  Pip executable missing in conda environment")
            
            # Test Python version
            result = subprocess.run([str(conda_python), "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip()
                details.append(f"Python version: {version}")
                
                if "3.10" not in version:
                    status = "WARN"
                    details.append("⚠️  Expected Python 3.10")
            else:
                status = "FAIL"
                details.append("❌ Python version check failed")
            
            # Test conda
            result = subprocess.run([str(conda_exe), "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                details.append(f"Conda version: {result.stdout.strip()}")
            else:
                status = "WARN"
                details.append("⚠️  Conda version check failed")
            
            return {
                "status": status,
                "message": "Python installation validation completed",
                "details": details
            }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Python validation failed: {e}",
                "details": details
            }
    
    def validate_conda_environment(self) -> Dict:
        """Validate conda virtual environment"""
        details = []
        status = "PASS"
        
        try:
            conda_python = self.conda_env_path / "python.exe"
            conda_exe = self.conda_path / "Scripts" / "conda.exe"
            
            # Check environment directory
            if self.conda_env_path.exists():
                details.append("✅ Conda environment directory found")
            else:
                status = "FAIL"
                details.append("❌ Conda environment directory missing")
                return {"status": status, "message": "Conda environment not found", "details": details}
            
            # Check Python in environment
            if conda_python.exists():
                details.append("✅ Conda environment Python found")
            else:
                status = "FAIL"
                details.append("❌ Conda environment Python missing")
            
            # Check conda executable
            if conda_exe.exists():
                details.append("✅ Conda executable found")
            else:
                status = "FAIL"
                details.append("❌ Conda executable missing")
            
            # Test Python in environment
            if conda_python.exists():
                result = subprocess.run([str(conda_python), "--version"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    details.append(f"Conda environment Python: {result.stdout.strip()}")
                else:
                    status = "WARN"
                    details.append("⚠️  Conda environment Python test failed")
            
            return {
                "status": status,
                "message": "Conda environment validation completed",
                "details": details
            }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Conda environment validation failed: {e}",
                "details": details
            }
    
    def validate_python_packages(self) -> Dict:
        """Validate Python packages"""
        details = []
        status = "PASS"
        
        try:
            conda_python = self.conda_env_path / "python.exe"
            
            if not conda_python.exists():
                return {
                    "status": "FAIL",
                    "message": "Conda environment Python not found",
                    "details": ["❌ Cannot test packages without Python"]
                }
            
            # Critical packages to test
            critical_packages = [
                "numpy", "pandas", "matplotlib", "requests", "flask",
                "streamlit", "langchain", "openai", "transformers"
            ]
            
            failed_packages = []
            
            for package in critical_packages:
                cmd = [str(conda_python), "-c", f"import {package}; print('{package} OK')"]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    details.append(f"✅ {package}: Available")
                else:
                    failed_packages.append(package)
                    details.append(f"❌ {package}: Missing or broken")
            
            if failed_packages:
                status = "FAIL" if len(failed_packages) > len(critical_packages) // 2 else "WARN"
                details.append(f"Failed packages: {', '.join(failed_packages)}")
            
            # Get package count
            cmd = [str(conda_python), "-m", "pip", "list", "--format=json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                try:
                    packages = json.loads(result.stdout)
                    details.append(f"Total packages installed: {len(packages)}")
                except:
                    details.append("Package count unavailable")
            
            return {
                "status": status,
                "message": "Python packages validation completed",
                "details": details
            }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Package validation failed: {e}",
                "details": details
            }
    
    def validate_vscode_installation(self) -> Dict:
        """Validate VS Code installation"""
        details = []
        status = "PASS"
        
        try:
            vscode_exe = self.vscode_path / "Code.exe"
            vscode_data = self.vscode_path / "data"
            
            # Check VS Code executable
            if vscode_exe.exists():
                details.append("✅ VS Code executable found")
            else:
                status = "FAIL"
                details.append("❌ VS Code executable missing")
                return {"status": status, "message": "VS Code not found", "details": details}
            
            # Check data directory (portable mode)
            if vscode_data.exists():
                details.append("✅ VS Code data directory found (portable mode)")
            else:
                status = "WARN"
                details.append("⚠️  VS Code data directory missing")
            
            # Test VS Code version
            try:
                result = subprocess.run([str(vscode_exe), "--version"], 
                                      capture_output=True, text=True, timeout=15)
                if result.returncode == 0:
                    version_lines = result.stdout.strip().split('\n')
                    if version_lines:
                        details.append(f"VS Code version: {version_lines[0]}")
                else:
                    details.append("VS Code version: Unable to determine")
            except:
                details.append("VS Code version: Check failed")
            
            # Check extensions
            extensions_path = vscode_data / "extensions"
            if extensions_path.exists():
                try:
                    extensions = list(extensions_path.glob("*"))
                    details.append(f"Extensions installed: {len(extensions)}")
                except:
                    details.append("Extensions: Unable to count")
            
            return {
                "status": status,
                "message": "VS Code validation completed",
                "details": details
            }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"VS Code validation failed: {e}",
                "details": details
            }
    
    def validate_ollama_installation(self) -> Dict:
        """Validate Ollama installation"""
        details = []
        status = "PASS"
        
        try:
            ollama_exe = self.ollama_path / "ollama.exe"
            
            # Check Ollama executable
            if ollama_exe.exists():
                details.append("✅ Ollama executable found")
            else:
                status = "FAIL"
                details.append("❌ Ollama executable missing")
                return {"status": status, "message": "Ollama not found", "details": details}
            
            # Test Ollama version
            try:
                result = subprocess.run([str(ollama_exe), "version"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    details.append(f"Ollama version: {result.stdout.strip()}")
                else:
                    details.append(f"Ollama version: {result.stderr.strip()}")
            except Exception as e:
                details.append(f"Ollama version check failed: {e}")
            
            # Check if Ollama service is running
            try:
                result = subprocess.run([str(ollama_exe), "list"], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    details.append("✅ Ollama service is running")
                else:
                    status = "WARN"
                    details.append("⚠️  Ollama service not running (this is normal)")
            except:
                status = "WARN"
                details.append("⚠️  Ollama service not running (this is normal)")
            
            return {
                "status": status,
                "message": "Ollama validation completed",
                "details": details
            }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Ollama validation failed: {e}",
                "details": details
            }
    
    def validate_llm_models(self) -> Dict:
        """Validate LLM models"""
        details = []
        status = "PASS"
        
        try:
            # Check models directory
            if self.models_path.exists():
                details.append("✅ Models directory found")
            else:
                status = "FAIL"
                details.append("❌ Models directory missing")
                return {"status": status, "message": "Models directory not found", "details": details}
            
            # Count model files
            model_files = []
            total_size = 0
            
            for ext in ['*.bin', '*.gguf', '*.safetensors', '*.pt', '*.pth']:
                model_files.extend(self.models_path.rglob(ext))
            
            for model_file in model_files:
                try:
                    total_size += model_file.stat().st_size
                except:
                    pass
            
            details.append(f"Model files found: {len(model_files)}")
            
            if len(model_files) == 0:
                status = "WARN"
                details.append("⚠️  No model files found")
            
            details.append(f"Total models size: {total_size / (1024**3):.1f} GB")
            
            # Try to check Ollama models
            ollama_exe = self.ollama_path / "ollama.exe"
            if ollama_exe.exists():
                try:
                    result = subprocess.run([str(ollama_exe), "list"], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        models = result.stdout.strip().split('\n')[1:]  # Skip header
                        details.append(f"Ollama registered models: {len(models)}")
                        for model in models[:5]:  # Show first 5 models
                            if model.strip():
                                details.append(f"  • {model.strip()}")
                    else:
                        details.append("ℹ️  Ollama service not running - cannot check registered models")
                except:
                    details.append("ℹ️  Ollama service not running - cannot check registered models")
            
            return {
                "status": status,
                "message": "LLM models validation completed",
                "details": details
            }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Models validation failed: {e}",
                "details": details
            }
    
    def validate_integration_tests(self) -> Dict:
        """Validate integration between components"""
        details = []
        status = "PASS"
        
        try:
            conda_python = self.conda_env_path / "python.exe"
            
            if conda_python.exists():
                # Test basic AI workflow
                test_script = '''
import sys
try:
    import langchain
    import streamlit
    import requests
    import pandas
    import numpy
    print("All critical packages imported successfully")
    print("Integration test completed successfully")
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

print("Integration test completed successfully")
'''
                
                result = subprocess.run([str(conda_python), "-c", test_script], 
                                      capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    details.append("✅ Python packages integration: OK")
                    for line in result.stdout.strip().split('\n'):
                        if line.strip():
                            details.append(f"  • {line.strip()}")
                else:
                    status = "FAIL"
                    details.append("❌ Python packages integration: FAILED")
                    details.append(f"Error: {result.stderr.strip()}")
            else:
                status = "FAIL"
                details.append("❌ Cannot test integration without Python")
            
            # Check project templates
            if self.projects_path.exists():
                templates = list(self.projects_path.glob("*"))
                details.append(f"Project templates found: {len(templates)}")
                
                for template in templates[:3]:  # Show first 3 templates
                    if template.is_dir():
                        main_files = list(template.glob("main.py")) + list(template.glob("*.py"))
                        if main_files:
                            details.append(f"  ✅ {template.name}: {main_files[0].name} found")
                        else:
                            details.append(f"  ⚠️  {template.name}: No Python files found")
            
            # Check activation script
            activate_script = self.ai_env_path / "activate_ai_env.bat"
            if activate_script.exists():
                details.append("✅ Environment activation script found")
            else:
                status = "WARN"
                details.append("⚠️  Environment activation script missing")
            
            return {
                "status": status,
                "message": "Integration tests completed",
                "details": details
            }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Integration test failed: {e}",
                "details": details
            }
    
    def validate_performance_tests(self) -> Dict:
        """Validate system performance"""
        details = []
        status = "PASS"
        
        try:
            conda_python = self.conda_env_path / "python.exe"
            
            if conda_python.exists():
                # Test Python startup time
                start_time = time.time()
                result = subprocess.run([str(conda_python), "-c", "print('Python started')"], 
                                      capture_output=True, text=True, timeout=10)
                startup_time = time.time() - start_time
                
                if result.returncode == 0:
                    details.append(f"Python startup time: {startup_time:.2f} seconds")
                    if startup_time > 5:
                        status = "WARN"
                        details.append("⚠️  Slow Python startup (> 5 seconds)")
                else:
                    status = "WARN"
                    details.append("⚠️  Python startup test failed")
            
            # Test package import time
            if conda_python.exists():
                start_time = time.time()
                result = subprocess.run([str(conda_python), "-c", "import langchain, streamlit, pandas"], 
                                      capture_output=True, text=True, timeout=30)
                import_time = time.time() - start_time
                
                if result.returncode == 0:
                    details.append(f"Package import time: {import_time:.2f} seconds")
                    if import_time > 10:
                        status = "WARN"
                        details.append("⚠️  Slow package imports (> 10 seconds)")
                else:
                    status = "WARN"
                    details.append("⚠️  Package import test failed")
            
            # Test disk performance
            try:
                test_file = self.ai_env_path / "test_performance.tmp"
                test_data = b"0" * (1024 * 1024)  # 1MB
                
                # Write test
                start_time = time.time()
                for i in range(10):
                    with open(test_file, "wb") as f:
                        f.write(test_data)
                write_time = time.time() - start_time
                write_speed = 10 / write_time  # MB/s
                
                # Read test
                start_time = time.time()
                for i in range(10):
                    with open(test_file, "rb") as f:
                        f.read()
                read_time = time.time() - start_time
                read_speed = 10 / read_time  # MB/s
                
                details.append(f"Disk write speed: {write_speed:.1f} MB/s")
                details.append(f"Disk read speed: {read_speed:.1f} MB/s")
                
                # Cleanup
                test_file.unlink(missing_ok=True)
                
                if write_speed < 10:
                    status = "WARN"
                    details.append("⚠️  Slow disk write speed (< 10 MB/s)")
                    
            except Exception as e:
                details.append(f"Disk performance test failed: {e}")
            
            return {
                "status": status,
                "message": "Performance tests completed",
                "details": details
            }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Performance test failed: {e}",
                "details": details
            }
    
    def generate_validation_report(self):
        """Generate comprehensive validation report"""
        try:
            total_time = time.time() - self.start_time
            
            # Count results
            passed = sum(1 for r in self.validation_results.values() if r.get("status") == "PASS")
            warnings = sum(1 for r in self.validation_results.values() if r.get("status") == "WARN")
            failed = sum(1 for r in self.validation_results.values() if r.get("status") == "FAIL")
            errors = sum(1 for r in self.validation_results.values() if r.get("status") == "ERROR")
            
            # Determine overall status
            if errors > 0 or failed > 0:
                overall_status = "FAILED"
            elif warnings > 0:
                overall_status = "WARNING"
            else:
                overall_status = "PASSED"
            
            # Print summary
            print("\n" + "=" * 80)
            print("📊 VALIDATION SUMMARY")
            print("=" * 80)
            print(f"Overall Status: {overall_status}")
            print(f"Total Tests: {len(self.validation_results)}")
            print(f"✅ Passed: {passed}")
            print(f"⚠️  Warnings: {warnings}")
            print(f"❌ Failed: {failed}")
            print(f"💥 Errors: {errors}")
            print(f"⏱️  Total Time: {total_time:.1f} seconds")
            
            # Save detailed report
            report_data = {
                "validation_info": {
                    "version": VALIDATOR_VERSION,
                    "date": VALIDATOR_DATE,
                    "description": VALIDATOR_DESCRIPTION,
                    "timestamp": datetime.now().isoformat(),
                    "total_time": total_time
                },
                "summary": {
                    "overall_status": overall_status,
                    "total_tests": len(self.validation_results),
                    "passed": passed,
                    "warnings": warnings,
                    "failed": failed,
                    "errors": errors
                },
                "results": self.validation_results
            }
            
            report_file = self.ai_env_path / "validation_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            print(f"📄 Report saved: {report_file}")
            print("=" * 80)
            
            # Log completion
            self.logger.info(f"Validation completed: {overall_status}")
            
        except Exception as e:
            print(f"Error generating report: {e}")
            self.logger.error(f"Report generation failed: {e}")

def main():
    """Main entry point"""
    try:
        # Check if path was provided as command-line argument
        ai_env_path = None

        if len(sys.argv) > 1:
            # Path provided as argument
            provided_path = sys.argv[1]
            ai_env_path = Path(provided_path)

            if not ai_env_path.exists():
                print(f"❌ Provided path does not exist: {provided_path}")
                return 1

            print(f"✅ Using provided path: {ai_env_path}\n")
        else:
            # No path provided, search for it
            print("🔍 Searching for AI_Environment installation...")
            ai_env_path = find_ai_environment()

            if not ai_env_path:
                print("❌ AI Environment not found")
                print("Searched locations:")
                print("  - D:/AI_Environment")
                print("  - E:/AI_Environment")
                print("  - F:/AI_Environment")
                print("  - F:/AI_Lab/AI_Environment")
                print("  - And other common locations")
                print("\nPlease run the installer first or specify the correct path.")
                print("\nUsage: python system_validator.py [AI_ENV_PATH]")
                return 1

            print(f"✅ Found AI_Environment at: {ai_env_path}\n")

        # Run validation
        validator = SystemValidator(ai_env_path)
        results = validator.run_validation_suite()

        # Return appropriate exit code
        if "error" in results:
            return 1

        # Check overall status
        failed = sum(1 for r in results.values() if r.get("status") in ["FAIL", "ERROR"])
        return 1 if failed > 0 else 0

    except KeyboardInterrupt:
        print("\n❌ Validation interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())


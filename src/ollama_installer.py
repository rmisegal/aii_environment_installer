#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama Installer - Handles Ollama installation and model management
"""

import os
import sys
import json
import zipfile
import logging
import subprocess
import time
import requests
from pathlib import Path
from typing import Optional, List, Dict
from download_manager import DownloadManager

class OllamaInstaller:
    """Handles Ollama installation and model management"""
    
    def __init__(self, ai_env_path: Path, logs_path: Path):
        self.ai_env_path = ai_env_path
        self.logs_path = logs_path
        self.logger = logging.getLogger(__name__)
        self.download_manager = DownloadManager(logs_path)
        
        # Installation paths
        self.ollama_path = ai_env_path / "Ollama"
        self.models_path = ai_env_path / "Models"
        self.downloads_path = ai_env_path / "downloads"  # Use D: drive for downloads
        
        # Ollama configuration
        self.ollama_host = "127.0.0.1"
        self.ollama_port = 11434
        self.ollama_url = f"http://{self.ollama_host}:{self.ollama_port}"
        
    def install(self) -> bool:
        """Install Ollama"""
        try:
            self.logger.info("Installing Ollama")
            
            # Download Ollama
            ollama_zip = self._download_ollama()
            if not ollama_zip:
                return False
            
            # Extract Ollama
            if not self._extract_ollama(ollama_zip):
                return False
            
            # Configure Ollama
            if not self._configure_ollama():
                return False
            
            # Start Ollama service
            if not self._start_ollama_service():
                return False
            
            # Verify installation
            if not self._verify_installation():
                return False
            
            self.logger.info("Ollama installation completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Ollama installation failed: {e}")
            return False
    
    def install_models(self, models: List[str]) -> bool:
        """Install configured models with retry logic"""
        try:
            self.logger.info(f"Installing {len(models)} models...")

            success_count = 0
            failed_models = []
            max_retries = 2

            for model in models:
                print(f"Downloading model: {model}")
                downloaded = False

                # Try downloading with retries
                for attempt in range(max_retries + 1):
                    if attempt > 0:
                        print(f"  Retry attempt {attempt}/{max_retries} for {model}...")
                        self.logger.info(f"Retrying download for {model} (attempt {attempt}/{max_retries})")
                        time.sleep(5)  # Brief pause before retry

                    if self.download_model(model):
                        success_count += 1
                        print(f"✅ Successfully downloaded: {model}")
                        downloaded = True
                        break

                if not downloaded:
                    failed_models.append(model)
                    print(f"❌ Failed to download: {model} (after {max_retries + 1} attempts)")

            self.logger.info(f"Model installation completed: {success_count}/{len(models)} successful")

            if failed_models:
                self.logger.warning(f"Failed to download models: {failed_models}")
                print(f"\nWarning: Some models failed to download: {failed_models}")
                print(f"You can retry failed models later using: ollama pull <model_name>")

            # Consider successful if at least 50% of models downloaded
            return success_count >= len(models) * 0.5

        except Exception as e:
            self.logger.error(f"Error installing models: {e}")
            return False
    
    def _download_ollama(self) -> Optional[Path]:
        """Download Ollama"""
        try:
            # Ollama download URL for Windows
            url = "https://github.com/ollama/ollama/releases/latest/download/ollama-windows-amd64.zip"
            
            filename = "ollama-windows-amd64.zip"
            destination = self.downloads_path / filename
            
            success = self.download_manager.download_with_progress(
                url, destination, "Downloading Ollama"
            )
            
            if success:
                return destination
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to download Ollama: {e}")
            return None
    
    def _extract_ollama(self, ollama_zip: Path) -> bool:
        """Extract Ollama to installation directory"""
        try:
            self.logger.info("Extracting Ollama...")
            
            # Create Ollama directory
            self.ollama_path.mkdir(parents=True, exist_ok=True)
            
            # Extract zip file
            with zipfile.ZipFile(ollama_zip, 'r') as zip_ref:
                zip_ref.extractall(self.ollama_path)
            
            # Create models directory
            self.models_path.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"Ollama extracted to: {self.ollama_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to extract Ollama: {e}")
            return False
    
    def _configure_ollama(self) -> bool:
        """Configure Ollama"""
        try:
            self.logger.info("Configuring Ollama...")
            
            # Create Ollama configuration
            config = {
                "host": self.ollama_host,
                "port": self.ollama_port,
                "models_path": str(self.models_path),
                "log_level": "info"
            }
            
            config_file = self.ollama_path / "config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            # Create startup script
            startup_script = self.ollama_path / "start_ollama.bat"
            script_content = f"""@echo off
title Ollama Server
echo Starting Ollama server...

set "OLLAMA_HOST={self.ollama_host}:{self.ollama_port}"
set "OLLAMA_MODELS={self.models_path}"
set "OLLAMA_LOGS={self.ollama_path}\\logs"

cd /d "{self.ollama_path}"
ollama.exe serve

pause
"""
            
            with open(startup_script, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # Create stop script
            stop_script = self.ollama_path / "stop_ollama.bat"
            stop_content = """@echo off
echo Stopping Ollama server...
taskkill /f /im ollama.exe 2>nul
echo Ollama server stopped.
pause
"""
            
            with open(stop_script, 'w', encoding='utf-8') as f:
                f.write(stop_content)
            
            self.logger.info("Ollama configuration completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to configure Ollama: {e}")
            return False
    
    def _start_ollama_service(self) -> bool:
        """Start Ollama service"""
        try:
            self.logger.info("Starting Ollama service...")
            
            ollama_exe = self.ollama_path / "ollama.exe"
            if not ollama_exe.exists():
                self.logger.error("Ollama executable not found")
                return False
            
            # Set environment variables
            env = os.environ.copy()
            env["OLLAMA_HOST"] = f"{self.ollama_host}:{self.ollama_port}"
            env["OLLAMA_MODELS"] = str(self.models_path)
            
            # Start Ollama server in background
            cmd = [str(ollama_exe), "serve"]
            process = subprocess.Popen(
                cmd,
                cwd=str(self.ollama_path),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            
            # Wait for service to start
            self.logger.info("Waiting for Ollama service to start...")
            for i in range(30):  # Wait up to 30 seconds
                try:
                    response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
                    if response.status_code == 200:
                        self.logger.info("Ollama service started successfully")
                        return True
                except:
                    pass
                time.sleep(1)
            
            self.logger.error("Ollama service failed to start within timeout")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to start Ollama service: {e}")
            return False
    
    def _verify_installation(self) -> bool:
        """Verify Ollama installation"""
        try:
            self.logger.info("Verifying Ollama installation...")
            
            ollama_exe = self.ollama_path / "ollama.exe"
            
            # Check executable exists
            if not ollama_exe.exists():
                self.logger.error("Ollama executable not found")
                return False
            
            # Test Ollama version
            cmd = [str(ollama_exe), "--version"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                self.logger.error(f"Ollama version check failed: {result.stderr}")
                return False
            
            version_info = result.stdout.strip()
            self.logger.info(f"Ollama version: {version_info}")
            
            # Test API connection
            try:
                response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    self.logger.info("Ollama API is accessible")
                else:
                    self.logger.warning(f"Ollama API returned status: {response.status_code}")
            except Exception as e:
                self.logger.warning(f"Ollama API test failed: {e}")
            
            self.logger.info("Ollama installation verified successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Ollama verification failed: {e}")
            return False
    
    def download_model(self, model_name: str) -> bool:
        """Download and install a model with proper encoding"""
        try:
            self.logger.info(f"Downloading model: {model_name}")
            
            ollama_exe = self.ollama_path / "ollama.exe"
            if not ollama_exe.exists():
                self.logger.error("Ollama executable not found")
                return False
            
            # Set environment variables
            env = os.environ.copy()
            env["OLLAMA_HOST"] = f"{self.ollama_host}:{self.ollama_port}"
            env["OLLAMA_MODELS"] = str(self.models_path)
            
            # Download model with proper encoding handling
            cmd = [str(ollama_exe), "pull", model_name]
            process = subprocess.Popen(
                cmd,
                cwd=str(self.ollama_path),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',  # Replace problematic characters
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Monitor download with timeout
            timeout = 5400  # 90 minutes (for large models on slower connections)
            start_time = time.time()
            
            while process.poll() is None:
                if time.time() - start_time > timeout:
                    self.logger.error(f"Model download timed out: {model_name}")
                    try:
                        process.terminate()
                        time.sleep(2)  # Wait for graceful termination
                        if process.poll() is None:
                            process.kill()  # Force kill if still running
                        time.sleep(1)  # Allow cleanup
                    except Exception as e:
                        self.logger.error(f"Error terminating process: {e}")
                    return False
                
                try:
                    # Read output with timeout
                    output = process.stdout.readline()
                    if output:
                        line = output.strip()
                        if line and not line.startswith('['):  # Skip ANSI escape sequences
                            print(f"  {line}")
                except UnicodeDecodeError:
                    # Skip problematic characters
                    continue
                
                time.sleep(0.1)
            
            return_code = process.poll()
            
            if return_code == 0:
                self.logger.info(f"Model {model_name} downloaded successfully")
                return True
            else:
                self.logger.error(f"Failed to download model {model_name}")
                return False
            
        except Exception as e:
            self.logger.error(f"Error downloading model {model_name}: {e}")
            return False
    
    def list_models(self) -> List[Dict]:
        """List installed models"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("models", [])
            else:
                self.logger.error(f"Failed to list models: {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error listing models: {e}")
            return []
    
    def test_model(self, model_name: str) -> bool:
        """Test a model with a simple query"""
        try:
            self.logger.info(f"Testing model: {model_name}")
            
            data = {
                "model": model_name,
                "prompt": "Hello! Please respond with 'Model test successful.'",
                "stream": False
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "").strip()
                self.logger.info(f"Model {model_name} test response: {response_text}")
                return True
            else:
                self.logger.error(f"Model test failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error testing model {model_name}: {e}")
            return False
    
    def get_recommended_models(self) -> List[str]:
        """Get list of recommended models for the AI environment"""
        return [
            "llama2:7b",
            "codellama:7b", 
            "mistral:7b",
            "phi:2.7b"
        ]
    
    def get_ollama_executable(self) -> Path:
        """Get path to Ollama executable"""
        return self.ollama_path / "ollama.exe"


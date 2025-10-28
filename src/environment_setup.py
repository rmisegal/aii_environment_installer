#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Environment Setup - Manages virtual environments and system configuration
"""

import os
import sys
import subprocess
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional

class EnvironmentSetup:
    """Manages Python virtual environments and system configuration"""
    
    def __init__(self, ai_env_path: Path, logs_path: Path):
        self.ai_env_path = ai_env_path
        self.logs_path = logs_path
        self.logger = logging.getLogger(__name__)
        
        # Paths
        self.python_path = ai_env_path / "Python"
        self.venv_path = ai_env_path / "venv"
        
    def create_virtual_environment(self, env_name: str = "AI2025") -> bool:
        """Create a Python virtual environment using virtualenv"""
        try:
            venv_dir = self.venv_path / env_name
            python_exe = self.python_path / "python.exe"
            pip_exe = self.python_path / "Scripts" / "pip.exe"
            
            if not python_exe.exists():
                self.logger.error(f"Python executable not found: {python_exe}")
                return False
            
            self.logger.info(f"Creating virtual environment: {env_name}")
            
            # First, install virtualenv using pip
            self.logger.info("Installing virtualenv package...")
            cmd = [str(pip_exe), "install", "virtualenv"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"Failed to install virtualenv: {result.stderr}")
                return False
            
            # Create virtual environment using virtualenv
            self.logger.info(f"Creating virtual environment directory: {venv_dir}")
            virtualenv_exe = self.python_path / "Scripts" / "virtualenv.exe"
            
            if not virtualenv_exe.exists():
                # Try using python -m virtualenv
                cmd = [str(python_exe), "-m", "virtualenv", str(venv_dir)]
            else:
                cmd = [str(virtualenv_exe), str(venv_dir)]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"Failed to create virtual environment: {result.stderr}")
                # Try alternative method - manual creation
                return self._create_manual_venv(venv_dir, python_exe)
            
            # Verify virtual environment was created
            venv_python = venv_dir / "Scripts" / "python.exe"
            venv_pip = venv_dir / "Scripts" / "pip.exe"
            
            if not venv_python.exists():
                self.logger.error("Virtual environment Python not found after creation")
                return self._create_manual_venv(venv_dir, python_exe)
            
            # Upgrade pip in the virtual environment
            if venv_pip.exists():
                self.logger.info("Upgrading pip in virtual environment")
                cmd = [str(venv_python), "-m", "pip", "install", "--upgrade", "pip"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    self.logger.warning(f"Failed to upgrade pip: {result.stderr}")
            
            self.logger.info(f"Virtual environment created successfully: {venv_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating virtual environment: {e}")
            return False
    
    def _create_manual_venv(self, venv_dir: Path, python_exe: Path) -> bool:
        """Manually create virtual environment structure"""
        try:
            self.logger.info("Attempting manual virtual environment creation...")
            
            # Create directory structure
            venv_dir.mkdir(parents=True, exist_ok=True)
            scripts_dir = venv_dir / "Scripts"
            lib_dir = venv_dir / "Lib" / "site-packages"
            scripts_dir.mkdir(parents=True, exist_ok=True)
            lib_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy Python executable
            venv_python = scripts_dir / "python.exe"
            shutil.copy2(python_exe, venv_python)
            
            # Copy pip if it exists
            pip_exe = self.python_path / "Scripts" / "pip.exe"
            if pip_exe.exists():
                venv_pip = scripts_dir / "pip.exe"
                shutil.copy2(pip_exe, venv_pip)
            
            # Create pyvenv.cfg
            pyvenv_cfg = venv_dir / "pyvenv.cfg"
            cfg_content = f"""home = {self.python_path}
include-system-site-packages = false
version = 3.10.11
"""
            with open(pyvenv_cfg, 'w') as f:
                f.write(cfg_content)
            
            # Create activation script
            activate_script = scripts_dir / "activate.bat"
            activate_content = f"""@echo off
set "VIRTUAL_ENV={venv_dir}"
set "PATH={scripts_dir};%PATH%"
set "_OLD_VIRTUAL_PROMPT=%PROMPT%"
set "PROMPT=(AI2025) %PROMPT%"
"""
            with open(activate_script, 'w') as f:
                f.write(activate_content)
            
            # Create deactivate script
            deactivate_script = scripts_dir / "deactivate.bat"
            deactivate_content = """@echo off
set "PATH=%_OLD_VIRTUAL_PATH%"
set "PROMPT=%_OLD_VIRTUAL_PROMPT%"
set "VIRTUAL_ENV="
set "_OLD_VIRTUAL_PATH="
set "_OLD_VIRTUAL_PROMPT="
"""
            with open(deactivate_script, 'w') as f:
                f.write(deactivate_content)
            
            # Test the manual environment
            if venv_python.exists():
                result = subprocess.run([str(venv_python), "--version"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    self.logger.info("Manual virtual environment created successfully")
                    return True
            
            self.logger.error("Manual virtual environment creation failed")
            return False
            
        except Exception as e:
            self.logger.error(f"Error in manual virtual environment creation: {e}")
            return False
    
    def activate_virtual_environment(self, env_name: str = "AI2025") -> Dict[str, str]:
        """Get environment variables for activating virtual environment"""
        venv_dir = self.venv_path / env_name
        venv_scripts = venv_dir / "Scripts"
        
        if not venv_scripts.exists():
            self.logger.error(f"Virtual environment not found: {venv_dir}")
            return {}
        
        # Prepare environment variables
        env_vars = os.environ.copy()
        env_vars["VIRTUAL_ENV"] = str(venv_dir)
        env_vars["PATH"] = f"{venv_scripts};{env_vars.get('PATH', '')}"
        
        # Remove PYTHONHOME if set (can interfere with venv)
        env_vars.pop("PYTHONHOME", None)
        
        return env_vars
    
    def install_package_in_venv(self, package: str, env_name: str = "AI2025") -> bool:
        """Install a package in the virtual environment"""
        try:
            venv_dir = self.venv_path / env_name
            venv_pip = venv_dir / "Scripts" / "pip.exe"
            venv_python = venv_dir / "Scripts" / "python.exe"
            
            if not venv_python.exists():
                self.logger.error(f"Virtual environment Python not found: {venv_dir}")
                return False
            
            self.logger.info(f"Installing package: {package}")
            
            # Use python -m pip to ensure we're using the right pip
            cmd = [str(venv_python), "-m", "pip", "install", package]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"Failed to install {package}: {result.stderr}")
                return False
            
            self.logger.info(f"Successfully installed: {package}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error installing package {package}: {e}")
            return False
    
    def create_environment_script(self, env_name: str = "AI2025") -> bool:
        """Create activation script for the environment"""
        try:
            venv_dir = self.venv_path / env_name
            script_path = self.ai_env_path / "activate_ai_env.bat"
            
            script_content = f"""@echo off
title AI Environment - {env_name}

set "AI_ENV_PATH={self.ai_env_path}"
set "PYTHON_PATH=%AI_ENV_PATH%\\Python"
set "VENV_PATH=%AI_ENV_PATH%\\venv\\{env_name}"
set "VSCODE_PATH=%AI_ENV_PATH%\\VSCode"
set "OLLAMA_PATH=%AI_ENV_PATH%\\Ollama"

:: Activate virtual environment
call "%VENV_PATH%\\Scripts\\activate.bat"

:: Set additional paths
set "PATH=%PYTHON_PATH%;%VSCODE_PATH%;%OLLAMA_PATH%;%PATH%"

:: Set Ollama configuration
set "OLLAMA_HOST=127.0.0.1:11434"
set "OLLAMA_MODELS=%AI_ENV_PATH%\\Models"

echo.
echo ================================================================
echo                    AI Environment Activated                   
echo                         {env_name}                            
echo ================================================================
echo.
echo Available commands:
echo   code .          - Open VS Code
echo   python          - Run Python
echo   jupyter lab     - Start Jupyter Lab
echo   ollama list     - List available models
echo   ollama run llama2 - Run Llama2 model
echo.

cmd /k
"""
            
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            self.logger.info(f"Environment script created: {script_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating environment script: {e}")
            return False
    
    def setup_jupyter_config(self, env_name: str = "AI2025") -> bool:
        """Setup Jupyter Lab configuration"""
        try:
            venv_dir = self.venv_path / env_name
            jupyter_dir = self.ai_env_path / "jupyter"
            jupyter_dir.mkdir(exist_ok=True)
            
            # Create Jupyter config
            config_content = f"""
c.ServerApp.ip = '127.0.0.1'
c.ServerApp.port = 8888
c.ServerApp.open_browser = True
c.ServerApp.root_dir = r'{self.ai_env_path / "Projects"}'
c.ServerApp.notebook_dir = r'{self.ai_env_path / "Projects"}'
"""
            
            config_file = jupyter_dir / "jupyter_lab_config.py"
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            self.logger.info("Jupyter configuration created")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting up Jupyter config: {e}")
            return False
    
    def create_project_templates(self) -> bool:
        """Create project templates and examples"""
        try:
            projects_dir = self.ai_env_path / "Projects"
            projects_dir.mkdir(exist_ok=True)
            
            # Create example projects
            examples = {
                "01_Basic_LLM": {
                    "main.py": '''"""
Basic LLM Example using Ollama
"""
import requests
import json

def query_ollama(prompt, model="llama2"):
    """Query Ollama API"""
    url = "http://127.0.0.1:11434/api/generate"
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()["response"]
    else:
        return f"Error: {response.status_code}"

if __name__ == "__main__":
    prompt = "Explain artificial intelligence in simple terms"
    response = query_ollama(prompt)
    print(f"AI Response: {response}")
''',
                    "requirements.txt": "requests\n"
                },
                
                "02_LangChain_Example": {
                    "main.py": '''"""
LangChain Example with Ollama
"""
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def main():
    # Initialize Ollama LLM
    llm = Ollama(model="llama2", base_url="http://127.0.0.1:11434")
    
    # Create a prompt template
    template = """
    You are a helpful AI assistant. Answer the following question:
    
    Question: {question}
    
    Answer:
    """
    
    prompt = PromptTemplate(template=template, input_variables=["question"])
    chain = LLMChain(llm=llm, prompt=prompt)
    
    # Ask a question
    question = "What are the benefits of using local LLMs?"
    response = chain.run(question=question)
    
    print(f"Question: {question}")
    print(f"Answer: {response}")

if __name__ == "__main__":
    main()
''',
                    "requirements.txt": "langchain\nollama\n"
                },
                
                "03_Streamlit_App": {
                    "app.py": '''"""
Streamlit AI Chat App
"""
import streamlit as st
import requests
import json

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

def main():
    st.title("🤖 Local AI Chat")
    st.write("Chat with your local AI models using Ollama")
    
    # Model selection
    model = st.selectbox("Select Model", ["llama2", "codellama", "mistral", "phi"])
    
    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("What would you like to know?"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = query_ollama(prompt, model)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
''',
                    "requirements.txt": "streamlit\nrequests\n",
                    "run.bat": '''@echo off
echo Starting Streamlit AI Chat App...
streamlit run app.py
pause
'''
                }
            }
            
            # Create example projects
            for project_name, files in examples.items():
                project_dir = projects_dir / project_name
                project_dir.mkdir(exist_ok=True)
                
                for filename, content in files.items():
                    file_path = project_dir / filename
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
            
            # Create README
            readme_content = """# AI Environment Projects

This directory contains example projects to get you started with the AI environment.

## Projects

### 01_Basic_LLM
Basic example of querying Ollama directly using HTTP requests.

### 02_LangChain_Example  
Example using LangChain framework with Ollama.

### 03_Streamlit_App
Interactive web app for chatting with AI models.

## Getting Started

1. Activate the AI environment: `activate_ai_env.bat`
2. Navigate to a project directory
3. Install requirements: `pip install -r requirements.txt`
4. Run the example: `python main.py`

## Creating New Projects

Feel free to create new directories here for your AI projects!
"""
            
            readme_file = projects_dir / "README.md"
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            self.logger.info("Project templates created")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating project templates: {e}")
            return False


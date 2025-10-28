# AI Environment User Manual
## Portable AI Development Environment

**Version:** 1.0  
**Date:** December 2024  
**Target:** Students and Educators  

---

## Table of Contents

1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [Installation Guide](#installation-guide)
4. [Getting Started](#getting-started)
5. [Using the AI Environment](#using-the-ai-environment)
6. [Project Examples](#project-examples)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Usage](#advanced-usage)
9. [Support](#support)

---

## 1. Introduction

### What is the AI Environment?

The AI Environment is a complete, portable artificial intelligence development platform that runs entirely from a USB drive. It includes everything you need to start developing AI applications:

- **Python 3.10** - Programming language for AI development
- **VS Code** - Professional code editor with AI extensions
- **Ollama** - Local AI model server for running LLMs
- **AI Libraries** - LangChain, LangGraph, AutoGen, and more
- **Data Science Tools** - Pandas, NumPy, Jupyter, Streamlit
- **Pre-trained Models** - Ready-to-use AI models

### Key Benefits

- ✅ **Portable** - Works on any Windows 11 computer
- ✅ **Complete** - Everything included, no additional setup
- ✅ **Offline Capable** - Core functions work without internet
- ✅ **Educational** - Perfect for learning AI development
- ✅ **Professional** - Suitable for real projects

---

## 2. System Requirements

### Minimum Requirements
- **Operating System:** Windows 11
- **RAM:** 8GB minimum
- **USB Drive:** 256GB+ (USB 3.0 recommended)
- **Free Space:** 50GB minimum
- **Internet:** Required for initial setup and model downloads

### Recommended Specifications
- **RAM:** 16GB or more
- **USB Drive:** 512GB+ SSD-based USB drive
- **Processor:** Intel i5/AMD Ryzen 5 or better
- **Internet:** High-speed connection for faster setup

---

## 3. Installation Guide

### Step 1: Prepare Your USB Drive

1. **Format the USB drive:**
   - Right-click on your USB drive in File Explorer
   - Select "Format"
   - Choose "NTFS" file system
   - Set allocation unit size to "Default"
   - Click "Start"

2. **Assign drive letter D:**
   - Open Disk Management (Windows + X, then K)
   - Right-click on your USB drive
   - Select "Change Drive Letter and Paths"
   - Click "Change" and select "D:"

### Step 2: Download the Installer

1. Download the `AI_Environment_Installer.zip` file
2. Extract the ZIP file to your Downloads folder
3. You should see a folder named `AI_Installer`

### Step 3: Run the Installation

1. **Run as Administrator:**
   - Navigate to the extracted `AI_Installer` folder
   - Right-click on `install.bat`
   - Select "Run as administrator"

2. **Follow the Installation:**
   - The installer will check your system
   - It will download and install all components
   - This process takes 30-60 minutes depending on your internet speed

3. **Wait for Completion:**
   - Do not disconnect the USB drive during installation
   - The installer will show progress for each component
   - A success message will appear when complete

### Step 4: Verify Installation

1. Run the validation tool:
   - Double-click `validate.bat` in the installer folder
   - This will test all components
   - Review the validation report

---

## 4. Getting Started

### Starting the AI Environment

1. **Connect your USB drive** to any Windows 11 computer
2. **Navigate to D:\AI_Environment**
3. **Double-click `activate_ai_env.bat`**
4. **Wait for the environment to load**

You'll see a command prompt with the AI2025 environment activated.

### First Steps

```bash
# Check Python version
python --version

# Check installed packages
pip list

# Start Jupyter Lab
jupyter lab

# Open VS Code
code .

# Check Ollama models
ollama list
```

### Directory Structure

```
D:\AI_Environment\
├── Python\           # Python 3.10 installation
├── venv\AI2025\      # Virtual environment
├── VSCode\           # VS Code portable
├── Ollama\           # Ollama AI server
├── Models\           # AI model files
├── Projects\         # Your projects go here
├── Scripts\          # Utility scripts
└── Logs\            # System logs
```

---

## 5. Using the AI Environment

### Working with Python

The environment includes Python 3.10 with all essential AI libraries:

```python
# Example: Basic AI chat
import requests
import json

def chat_with_ai(message):
    url = "http://127.0.0.1:11434/api/generate"
    data = {
        "model": "llama2",
        "prompt": message,
        "stream": False
    }
    response = requests.post(url, json=data)
    return response.json()["response"]

# Start Ollama first: ollama serve
response = chat_with_ai("Hello, how are you?")
print(response)
```

### Using VS Code

VS Code is pre-configured for AI development:

1. **Open VS Code:** Type `code .` in the terminal
2. **Python Integration:** Automatically uses the AI2025 environment
3. **Extensions Included:**
   - Python support with IntelliSense
   - Jupyter notebook integration
   - Code formatting and linting
   - Git integration

### Working with Ollama

Ollama provides local AI models:

```bash
# Start Ollama server
ollama serve

# In another terminal:
# List available models
ollama list

# Run a model
ollama run llama2

# Chat with the model
> Hello! Tell me about artificial intelligence.
```

### Using Jupyter Lab

Perfect for data science and AI experimentation:

```bash
# Start Jupyter Lab
jupyter lab

# This opens in your web browser
# Create new notebooks in the Projects folder
```

---

## 6. Project Examples

The environment includes several example projects:

### Example 1: Basic LLM Chat

```python
# File: Projects/01_Basic_LLM/main.py
import requests
import json

def query_ollama(prompt, model="llama2"):
    url = "http://127.0.0.1:11434/api/generate"
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(url, json=data)
    return response.json()["response"]

if __name__ == "__main__":
    prompt = "Explain machine learning in simple terms"
    response = query_ollama(prompt)
    print(f"AI Response: {response}")
```

### Example 2: LangChain Integration

```python
# File: Projects/02_LangChain_Example/main.py
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

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
print(f"Answer: {response}")
```

### Example 3: Streamlit Web App

```python
# File: Projects/03_Streamlit_App/app.py
import streamlit as st
import requests

def query_ollama(prompt, model="llama2"):
    url = "http://127.0.0.1:11434/api/generate"
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(url, json=data)
    return response.json()["response"]

st.title("🤖 Local AI Chat")
st.write("Chat with your local AI models")

# Model selection
model = st.selectbox("Select Model", ["llama2", "codellama", "mistral"])

# Chat interface
if prompt := st.chat_input("What would you like to know?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = query_ollama(prompt, model)
            st.markdown(response)

# Run with: streamlit run app.py
```

---

## 7. Troubleshooting

### Common Issues

**Issue: "Python not found"**
- Solution: Make sure you activated the environment with `activate_ai_env.bat`

**Issue: "Ollama connection failed"**
- Solution: Start Ollama server with `ollama serve` in a separate terminal

**Issue: "VS Code won't start"**
- Solution: Check if antivirus is blocking the executable

**Issue: "Slow performance"**
- Solution: Use a USB 3.0+ port and SSD-based USB drive

**Issue: "Package import errors"**
- Solution: Run the validation tool to check installation

### Getting Help

1. **Check the logs:** Look in `D:\AI_Environment\Logs\`
2. **Run validation:** Use `validate.bat` to diagnose issues
3. **Restart environment:** Close and reopen `activate_ai_env.bat`
4. **Check disk space:** Ensure sufficient free space on USB drive

### Performance Tips

- **Use USB 3.0+ ports** for better speed
- **Close unnecessary applications** to free up RAM
- **Use SSD-based USB drives** for optimal performance
- **Keep models on the USB drive** to avoid copying

---

## 8. Advanced Usage

### Adding New Packages

```bash
# Activate environment first
# Then install packages with pip
pip install new-package-name

# Example: Install additional AI tools
pip install transformers torch
```

### Custom Model Installation

```bash
# Download custom models
ollama pull custom-model-name

# List all models
ollama list

# Remove models you don't need
ollama rm model-name
```

### Environment Customization

Edit the configuration files:
- `D:\AI_Environment\venv\AI2025\pyvenv.cfg` - Python settings
- `D:\AI_Environment\VSCode\data\user-data\User\settings.json` - VS Code settings

### Backup and Restore

**Backup:**
1. Copy the entire `D:\AI_Environment` folder
2. Store on another drive or cloud storage

**Restore:**
1. Copy the backup to a new USB drive
2. Assign drive letter D:
3. Run `activate_ai_env.bat`

---

## 9. Support

### Documentation
- **ATP Document:** Complete testing procedures
- **Installation Logs:** Detailed installation records
- **Validation Reports:** System health checks

### Self-Help Resources
- Check the `Projects` folder for examples
- Review logs in the `Logs` folder
- Run the validation tool for diagnostics

### Best Practices
- Always safely eject the USB drive
- Keep the environment updated
- Backup important projects
- Use version control (Git) for your code

---

**Happy AI Development!** 🚀

This portable AI environment gives you everything needed to start your journey in artificial intelligence. Whether you're a student learning the basics or an educator teaching AI concepts, this environment provides a consistent, powerful platform for AI development.

Remember: The future of AI is in your hands! 🤖✨


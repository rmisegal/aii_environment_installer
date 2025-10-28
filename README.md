# AI Environment Installer
## Portable AI Development Environment for Windows

**Version:** 3.0
**Release Date:** January 2025
**Target Platform:** Windows 11
**Installation:** Any drive with 50GB+ free space

> **Note:** Version 3.0 introduces the unified MasterInstall.bat system that installs both AI_Environment (runtime) and AI_Lab (source code). Legacy install.bat files have been moved to `legacy_install_system/` folder.

---

## 🚀 Quick Start

1. **Extract** this ZIP file to your computer
2. **Right-click** `MasterInstall.bat` and select **"Run as administrator"**
3. **Choose installation type** - Fresh installation, AI_Lab only, or AI_Environment only
4. **Select drive** - Installer will show available drives and recommend the best option
5. **Wait** for installation to complete (30-60 minutes)
6. **Start** using your AI environment!

---

## 📦 What's Included

### Core Components
- **Miniconda** - Lightweight Python environment manager
- **Python 3.10** - In isolated conda environment (AI2025)
- **VS Code Portable** - Professional code editor with extensions
- **Ollama** - Local LLM server for running AI models

### AI & ML Libraries
- **LangChain** - Framework for LLM applications
- **LangGraph** - Graph-based AI workflows
- **AutoGen** - Multi-agent conversation framework
- **Transformers** - Hugging Face transformers library
- **Sentence Transformers** - Text embeddings
- **ChromaDB** - Vector database
- **FAISS** - Similarity search
- **Streamlit** - Web app framework for AI demos
- **FastAPI** - Modern API framework
- **Gradio** - Quick ML interfaces
- **Jupyter Lab** - Interactive development environment

### Data Science Tools
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computing
- **Matplotlib/Seaborn/Plotly** - Data visualization
- **Scikit-learn** - Machine learning library
- **PyTorch** - Deep learning framework

### Development Tools
- **Black, Pylint, isort, Flake8** - Code formatting and linting
- **Python-dotenv** - Environment variable management
- **Requests, HTTPX, AIOHTTP** - HTTP libraries
- **BeautifulSoup4, lxml** - Web scraping

### Pre-trained Models
- **Llama2 7B** - General purpose conversational AI
- **CodeLlama 7B** - Code generation and assistance
- **Mistral 7B** - Efficient general purpose model
- **Phi 2.7B** - Compact high-performance model

---

## 📋 System Requirements

### Minimum
- **OS:** Windows 11
- **RAM:** 8GB
- **Storage:** 50GB+ free space on any drive
- **Internet:** Required for initial setup

### Recommended
- **RAM:** 16GB+
- **Storage:** 100GB+ free space
- **Processor:** Intel i5/AMD Ryzen 5+
- **Internet:** High-speed for faster setup

---

## 📁 Installation Structure

After installation, your drive will contain:

```
<DRIVE>:\AI_Environment\
├── Miniconda\              # Python environment manager
│   ├── envs\AI2025\        # Isolated Python 3.10 environment
│   └── Scripts\            # Conda executables
├── VSCode\                 # Portable VS Code installation
├── Ollama\                 # Ollama AI server
├── Models\                 # Downloaded AI models
├── Projects\               # Your AI projects (preserved during uninstall)
├── Scripts\                # Utility scripts
├── Logs\                   # Runtime logs
├── Tools\                  # Additional tools
├── activate_ai_env.bat     # Quick activation script
├── installation_info.json  # Installation metadata
└── README.md               # Environment documentation
```

Installer Directory:
```
AI_Environment_Installer-main\
├── MasterInstall.bat        # Main unified installer (NEW)
├── MasterUninstall.bat      # Main unified uninstaller (NEW)
├── README.md                # This file
├── master_installation_status.json  # Unified status tracking
├── src\                     # Source code
│   ├── master_installer.py  # Main orchestration (NEW)
│   ├── installation_status_manager.py  # Status management (NEW)
│   ├── ai_lab_installer.py  # AI_Lab repository cloning (NEW)
│   ├── install_manager.py   # AI_Environment installation
│   ├── automated_uninstaller.py  # Smart uninstaller
│   ├── drive_selector.py    # Drive selection interface
│   ├── conda_installer.py   # Conda installation
│   ├── vscode_installer.py  # VS Code installation
│   ├── ollama_installer.py  # Ollama installation
│   └── [other modules...]   # Additional utilities
├── config\                  # Configuration files
│   └── install_config.json  # Installation settings
├── docs\                    # Documentation
├── logs\                    # Installation logs
└── legacy_install_system\   # Deprecated files from v1.x-2.x
    ├── batch_files\         # Old install.bat, uninstall.bat
    ├── status_files\        # Old status JSON files
    ├── documentation\       # Development phase docs
    └── README_LEGACY.md     # Legacy system documentation
```

---

## 🔧 Installation Guide

### Basic Installation

1. **Run as Administrator**
   ```
   Right-click MasterInstall.bat → "Run as administrator"
   ```

2. **Choose Installation Type**
   - [1] Fresh Installation (both AI_Environment and AI_Lab)
   - [2] Install AI_Lab only (requires AI_Environment)
   - [3] Install AI_Environment only
   - [4] Resume incomplete installation
   - [5] Uninstall

3. **Select Installation Drive**
   - Installer displays all available drives with free space
   - Drives with 50GB+ are marked as "Recommended"
   - Enter drive letter (e.g., `D` or `E`)
   - Confirm selection

4. **Wait for Installation**
   - Progress displayed in real-time
   - Logs saved to `logs/` folder

5. **Installation Complete!**
   - AI_Environment: `<DRIVE>:\AI_Environment\` or `<DRIVE>:\AI_Lab\AI_Environment\`
   - AI_Lab: `<DRIVE>:\AI_Lab\` (if installed)

### Advanced Options

**Non-interactive installation (for automation):**
```batch
MasterInstall.bat --auto-install --drive D
```

**Get help:**
```batch
MasterInstall.bat --help
```

Note: The master installer provides an interactive menu for most use cases. For AI_Environment step-by-step control, the underlying `install_manager.py` still supports the `--step` parameter.

---

## ✅ Using the Environment

### Starting the Environment

**Quick Start:**
```batch
<DRIVE>:\AI_Environment\activate_ai_env.bat
```

This will:
- Activate the AI2025 conda environment
- Add VS Code to PATH
- Add Ollama to PATH
- Change to the Projects directory
- Open a command prompt ready to use

### Available Commands

Once activated, you can use:

```batch
# Python and packages
python --version
pip list
conda list

# Jupyter Lab
jupyter lab

# VS Code
code .

# Ollama
ollama serve          # Start Ollama server
ollama list           # List downloaded models
ollama run llama2     # Chat with a model

# Package management
conda install package-name
pip install package-name
```

### Example Workflows

**Create a new AI project:**
```batch
# Activate environment
<DRIVE>:\AI_Environment\activate_ai_env.bat

# Create project directory
mkdir MyAIProject
cd MyAIProject

# Create Python script
code main.py

# Run your script
python main.py
```

**Start Jupyter Lab:**
```batch
# Activate environment
<DRIVE>:\AI_Environment\activate_ai_env.bat

# Launch Jupyter Lab
jupyter lab
```

**Chat with local AI:**
```batch
# Activate environment
<DRIVE>:\AI_Environment\activate_ai_env.bat

# Start Ollama (in one terminal)
ollama serve

# Chat with AI (in another terminal)
ollama run llama2
```

---

## 🗑️ Uninstallation

### Smart Uninstaller

The uninstaller automatically:
- **Detects** installations on all drives
- **Preserves** user projects by default
- **Removes** only installer-created files
- **Protects** pre-existing software

### Basic Uninstall

```batch
# Run as administrator
MasterUninstall.bat
```

The uninstaller will:
1. Search all drives for AI_Environment and AI_Lab
2. Display found installations
3. Ask which components to remove
4. Ask for confirmation
5. Remove selected installations
6. Preserve Projects/ folder by default

### Advanced Uninstall Options

**Fully automated (no prompts):**
```batch
MasterUninstall.bat --auto
```

**Preview what will be deleted:**
```batch
MasterUninstall.bat --dry-run
```

**Delete including projects:**
```batch
MasterUninstall.bat --delete-projects
```

**Create backup before uninstall:**
```batch
MasterUninstall.bat --backup
```

**List all installations:**
```batch
MasterUninstall.bat --list
```

**Uninstall specific path:**
```batch
MasterUninstall.bat --path "E:\AI_Environment"
```

**Combined options:**
```batch
MasterUninstall.bat --auto --backup --delete-projects
```

### What Gets Removed

**Always Removed:**
- Miniconda (if installed by this installer)
- VS Code portable installation
- Ollama and models
- Installation metadata files
- Scripts and logs folders

**Preserved by Default:**
- Projects/ folder (your work)
- Pre-existing Conda installations
- Pre-existing directories

---

## 📊 Status & Validation

### Check Installation Status

The master installer automatically detects and displays installation status when launched. You can also check by running `MasterInstall.bat` and selecting option 0 to exit after viewing the status.

The status display shows:
- AI_Environment installation status and location
- AI_Lab installation status and location
- Installation context (drive, type, mode)
- Last completed steps
- Resume options if installation is incomplete

---

## 🚨 Troubleshooting

### Common Issues

**"Administrator privileges required"**
- Right-click MasterInstall.bat → "Run as administrator"

**"No suitable drive found"**
- Ensure you have 50GB+ free space
- Free up space or use different drive
- Check disk with Windows Explorer

**"Drive selection cancelled"**
- Installer stopped, no changes made
- Run installer again to retry

**"AI Environment not found"**
- Installation may have failed
- Check logs in `logs/` folder
- Run `MasterInstall.bat` to view current status

**"Python not found"**
- Make sure to run `activate_ai_env.bat` first
- Check installation completed successfully
- Review installation logs in `logs/` folder

**"Ollama connection failed"**
- Start Ollama: `ollama serve`
- Check firewall settings
- Verify port 11434 available

**Installation to wrong location**
- Fixed in v2.0 - now installs to drive root
- Old issue: Drive without backslash caused relative path

### Log Files

Check these for troubleshooting:
- `logs/install_YYYYMMDD_HHMMSS.log` - Installation log
- `logs/uninstall_YYYYMMDD_HHMMSS.log` - Uninstall log
- `<DRIVE>:\AI_Environment\Logs\` - Runtime logs

### Getting Help

1. Run `MasterInstall.bat` to view installation status
2. Review logs in `logs/` folder
3. Check `master_installation_status.json` for detailed state
4. Check installation_info.json in AI_Environment (if installed)

---

## 🔄 Advanced Features

### Multiple Installations

You can install on multiple drives:
- Each drive gets independent installation
- Uninstaller can detect and manage all
- Use `--path` to target specific installation

### Portable Usage

The environment is fully portable:
- Move entire `AI_Environment` folder
- Update drive letter in `activate_ai_env.bat` if needed
- No registry dependencies
- No system-wide changes

### Customization

**Modify installed packages:**
Edit `config/install_config.json` before running installer:
```json
{
  "python_packages": [
    "your-package-here",
    "another-package"
  ],
  "ollama_models": [
    "llama2:7b",
    "your-model-here"
  ]
}
```

**Add packages after installation:**
```batch
activate_ai_env.bat
pip install your-package
```

**Add models after installation:**
```batch
activate_ai_env.bat
ollama pull model-name
```

---

## 📈 Performance Expectations

### Installation Time
- **Fast Internet (100+ Mbps):** 30-45 minutes
- **Medium Internet (25-100 Mbps):** 45-60 minutes
- **Slow Internet (<25 Mbps):** 60-90 minutes

### Storage Usage
- **Miniconda + AI2025:** ~5GB
- **VS Code:** ~500MB
- **Python Packages:** ~8GB
- **Ollama + Models:** ~25GB
- **Total:** ~40-50GB
- **Recommended Free Space:** 100GB+

### Runtime Performance
- **Environment Activation:** <5 seconds
- **Python Startup:** <3 seconds
- **VS Code Launch:** <10 seconds
- **Jupyter Lab Start:** <15 seconds
- **Ollama Service:** <15 seconds
- **Model Loading:** <60 seconds (7B models)

---

## 🆕 What's New in Version 3.0

### Unified Dual-Component Installer
- ✅ **New MasterInstall.bat** - Installs both AI_Environment AND AI_Lab
- ✅ **AI_Lab Integration** - Clone source code from GitHub repository
- ✅ **Interactive Menu** - Choose what to install
- ✅ **Resume Support** - Continue interrupted installations

### Installation Modes
- ✅ **External Drive Mode** - Nested structure: `F:\AI_Lab\AI_Environment\`
- ✅ **Internal Drive Mode** - Side-by-side: `D:\AI_Lab\` + `D:\AI_Environment\`
- ✅ **Flexible Options** - Install both, AI_Lab only, or AI_Environment only

### Unified Status Tracking
- ✅ **master_installation_status.json** - Tracks both components
- ✅ **Resume Detection** - Automatically detect incomplete installations
- ✅ **Git Integration** - Track AI_Lab commit versions

### Enhanced Uninstaller
- ✅ **MasterUninstall.bat** - Handles both components
- ✅ **Selective Removal** - Choose which components to uninstall
- ✅ **Auto-detection** - Finds installations across all drives
- ✅ **Smart Cleanup** - Preserves user data and projects

### Legacy System Archived
- ✅ Old `install.bat` and `uninstall.bat` moved to `legacy_install_system/`
- ✅ Full backward compatibility maintained
- ✅ Clean project structure with organized legacy files

---

## 📜 License & Credits

### Open Source Components
- **Python:** Python Software Foundation License
- **Miniconda:** BSD 3-Clause License
- **VS Code:** MIT License
- **Ollama:** MIT License
- **AI Libraries:** Various open source licenses

### Third-Party Models
- **Llama2:** Meta AI License
- **CodeLlama:** Meta AI License
- **Mistral:** Apache 2.0 License
- **Phi:** MIT License

---

## 🎉 Success Indicators

After successful installation, you should be able to:

✅ Run `activate_ai_env.bat` to start environment
✅ Execute `python --version` and see Python 3.10
✅ Run `conda list` to see installed packages
✅ Launch `jupyter lab` for interactive coding
✅ Open `code .` to use VS Code
✅ Start `ollama serve` for AI models
✅ Chat with AI using `ollama run llama2`
✅ Build complete AI applications end-to-end

---

## 🚀 Quick Reference

### Essential Commands
```batch
# Install
MasterInstall.bat

# Uninstall
MasterUninstall.bat

# Start environment
<DRIVE>:\AI_Environment\activate_ai_env.bat
# OR (if AI_Lab installed)
<DRIVE>:\AI_Lab\run_ai_env.bat

# Get help
MasterInstall.bat --help
MasterUninstall.bat --help
```

### File Locations
- **AI_Environment:** `<DRIVE>:\AI_Environment\` or `<DRIVE>:\AI_Lab\AI_Environment\`
- **AI_Lab:** `<DRIVE>:\AI_Lab\` (if installed)
- **Projects:** `<DRIVE>:\AI_Environment\Projects\`
- **Activation:** `<DRIVE>:\AI_Environment\activate_ai_env.bat` or `<DRIVE>:\AI_Lab\run_ai_env.bat`
- **Logs:** `AI_Environment_Installer-main\logs\`
- **Config:** `AI_Environment_Installer-main\config\`
- **Status:** `AI_Environment_Installer-main\master_installation_status.json`
- **Legacy Files:** `AI_Environment_Installer-main\legacy_install_system\`

---

**Ready to start your AI journey? Let's build the future together! 🚀🤖**

For more information, check the logs and status files generated during installation.

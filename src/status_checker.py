#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Status Checker - Shows current installation status
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

class StatusChecker:
    """Checks and displays installation status"""

    def __init__(self, custom_path=None):
        # Try to find AI_Environment installation
        if custom_path:
            self.ai_env_path = Path(custom_path)
        else:
            self.ai_env_path = self._find_installation()

        self.status_file = self.ai_env_path / "installation_status.json" if self.ai_env_path else None

        # Define all installation steps
        self.steps = {
            1: {"name": "Check prerequisites", "description": "System requirements validation"},
            2: {"name": "Create directory structure", "description": "Setup folder structure"},
            3: {"name": "Install Miniconda", "description": "Python environment manager"},
            4: {"name": "Create AI2025 environment", "description": "Conda environment setup"},
            5: {"name": "Install VS Code", "description": "Portable code editor"},
            6: {"name": "Install Python packages", "description": "AI/ML libraries"},
            7: {"name": "Install Ollama and LLM models", "description": "Local AI models"},
            8: {"name": "Finalize installation", "description": "Scripts and configuration"}
        }

    def _find_installation(self):
        """Find AI_Environment installation on any drive"""
        import string

        # Check all possible drive letters
        for letter in string.ascii_uppercase:
            candidate = Path(f"{letter}:/AI_Environment")
            if candidate.exists() and candidate.is_dir():
                # Check if it looks like our installation
                if (candidate / "installation_status.json").exists() or \
                   (candidate / "Miniconda").exists() or \
                   (candidate / "activate_ai_env.bat").exists():
                    return candidate

        # Default fallback
        return Path("D:/AI_Environment")

    def show_status(self):
        """Display current installation status"""
        print("=" * 64)
        print("                AI Environment Installation Status")
        print("=" * 64)
        print()

        # Check if AI Environment exists
        if not self.ai_env_path or not self.ai_env_path.exists():
            print("ERROR: AI Environment not found on any drive")
            print("   No installation detected.")
            print()
            print("To start installation: install.bat")
            return

        print(f"Installation Location: {self.ai_env_path}")
        print()
        
        # Load status file
        status_data = self._load_status()
        
        if not status_data:
            print("⚠️  Installation status file not found")
            print("   Installation may be incomplete or corrupted.")
            print()
            self._check_components()
            return
        
        # Display status information
        last_step = status_data.get("last_completed_step", 0)
        current_step = status_data.get("current_step", 1)
        status = status_data.get("status", "unknown")
        timestamp = status_data.get("timestamp", "unknown")
        
        print(f"Installation Status: {status.upper()}")
        print(f"Last Update: {timestamp}")
        print(f"Last Completed Step: {last_step}/8")
        print(f"Current Step: {current_step}/8")
        print()
        
        # Show step-by-step status
        print("Step-by-Step Status:")
        print("-" * 64)
        
        for step_num in range(1, 9):
            step_info = self.steps[step_num]
            
            if step_num <= last_step:
                status_icon = "✅"
                status_text = "COMPLETED"
            elif step_num == current_step:
                if status == "failed":
                    status_icon = "❌"
                    status_text = "FAILED"
                elif status == "in_progress":
                    status_icon = "🔄"
                    status_text = "IN PROGRESS"
                else:
                    status_icon = "⏳"
                    status_text = "PENDING"
            else:
                status_icon = "⏸️"
                status_text = "NOT STARTED"
            
            print(f"{status_icon} Step {step_num}: {step_info['name']}")
            print(f"   {step_info['description']} - {status_text}")
        
        print()
        
        # Show component status
        self._check_components()
        
        # Show next steps
        self._show_next_steps(last_step, current_step, status)
    
    def _load_status(self):
        """Load status from JSON file"""
        try:
            if self.status_file.exists():
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error reading status file: {e}")
        return None
    
    def _check_components(self):
        """Check which components are actually installed"""
        print("Component Status:")
        print("-" * 64)

        # Check Miniconda in multiple locations
        miniconda_found = False
        miniconda_location = ""

        miniconda_locations = [
            (self.ai_env_path / "Miniconda" / "Scripts" / "conda.exe", f"{self.ai_env_path}\\Miniconda (Portable)"),
            (Path("C:/ProgramData/miniconda3/Scripts/conda.exe"), "C:\\ProgramData\\miniconda3 (AllUsers)")
        ]

        for conda_path, location in miniconda_locations:
            if conda_path.exists():
                miniconda_found = True
                miniconda_location = location
                break

        if miniconda_found:
            print(f"✅ Miniconda: Installed at {miniconda_location}")
        else:
            print(f"❌ Miniconda: Not found")

        # Check AI2025 Environment in multiple locations
        ai2025_found = False
        ai2025_location = ""

        ai2025_locations = [
            (self.ai_env_path / "Miniconda" / "envs" / "AI2025", f"{self.ai_env_path}\\Miniconda\\envs"),
            (Path("C:/ProgramData/miniconda3/envs/AI2025"), "C:\\ProgramData\\miniconda3\\envs")
        ]

        for env_path, location in ai2025_locations:
            if env_path.exists():
                ai2025_found = True
                ai2025_location = location
                break

        if ai2025_found:
            print(f"✅ AI2025 Environment: Installed at {ai2025_location}")
        else:
            print(f"❌ AI2025 Environment: Not found")

        # Check other components
        other_components = [
            ("VS Code", self.ai_env_path / "VSCode" / "Code.exe"),
            ("Ollama", self.ai_env_path / "Ollama" / "ollama.exe"),
            ("Models Directory", self.ai_env_path / "Models"),
            ("Activation Script", self.ai_env_path / "activate_ai_env.bat"),
            ("Projects Directory", self.ai_env_path / "Projects")
        ]

        for name, path in other_components:
            if path.exists():
                print(f"✅ {name}: Installed")
            else:
                print(f"❌ {name}: Not found")

        print()
    
    def _show_next_steps(self, last_step, current_step, status):
        """Show recommended next steps"""
        print("Recommended Actions:")
        print("-" * 64)
        
        if status == "completed":
            print("Installation completed successfully!")
            print("   You can start using the AI Environment:")
            print(f"   • Run: {self.ai_env_path}\\activate_ai_env.bat")
            print("   • Or: install.bat --step 8 (to re-run finalization)")
        
        elif status == "failed":
            print(f"❌ Installation failed at step {current_step}")
            print("   Options to fix:")
            print(f"   • Retry failed step: install.bat --step {current_step}")
            print(f"   • Remove and retry: uninstall.bat --from-step {current_step}")
            print("   • Check logs in the logs folder for details")
        
        elif status == "in_progress":
            print(f"🔄 Installation in progress at step {current_step}")
            print("   Please wait for current step to complete")
        
        else:
            next_step = last_step + 1
            if next_step <= 8:
                print(f"⏭️  Ready to continue from step {next_step}")
                print(f"   Continue installation: install.bat --step {next_step}")
                print(f"   Or restart from beginning: install.bat")
            else:
                print("🤔 Installation status unclear")
                print("   Try: install.bat (will auto-detect next step)")
        
        print()
        print("Other options:")
        print("   • Complete removal: uninstall.bat")
        print("   • Selective removal: uninstall.bat --from-step N")
        print("   • Show help: install.bat --help")

def main():
    """Main function"""
    checker = StatusChecker()
    checker.show_status()

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Status Updater - Detects current installation state and creates/updates status file
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add core path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from step_tracker import StepTracker

class StatusUpdater:
    """Detects current installation state and updates status file"""

    def __init__(self, ai_env_path=None):
        if ai_env_path:
            self.ai_env_path = Path(ai_env_path)
        else:
            self.ai_env_path = self._find_ai_environment()
        self.step_tracker = StepTracker(self.ai_env_path) if self.ai_env_path else None

        # Define step detection criteria
        self.step_checks = {
            1: self._check_step1_prerequisites,
            2: self._check_step2_directories,
            3: self._check_step3_miniconda,
            4: self._check_step4_ai2025_env,
            5: self._check_step5_vscode,
            6: self._check_step6_packages,
            7: self._check_step7_ollama,
            8: self._check_step8_finalization
        }

        self.step_names = {
            1: "Check prerequisites",
            2: "Create directory structure",
            3: "Install Miniconda",
            4: "Create AI2025 environment",
            5: "Install VS Code",
            6: "Install Python packages",
            7: "Install Ollama and LLM models",
            8: "Finalize installation"
        }

    def _find_ai_environment(self):
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

        return None
    
    def _check_step1_prerequisites(self) -> bool:
        """Check if prerequisites step was completed"""
        # If we have the AI_Environment directory, prerequisites were checked
        return self.ai_env_path.exists()
    
    def _check_step2_directories(self) -> bool:
        """Check if directory structure was created"""
        # Check for key directories that should exist
        # Be more flexible - not all directories need to exist for step 2 to be considered complete
        key_dirs = ["Miniconda", "VSCode"]  # These are the most important ones
        
        existing_dirs = 0
        total_dirs = len(key_dirs)
        
        for dir_name in key_dirs:
            if (self.ai_env_path / dir_name).exists():
                existing_dirs += 1
        
        # If at least the key directories exist, consider step 2 complete
        return existing_dirs >= total_dirs
    
    def _check_step3_miniconda(self) -> bool:
        """Check if Miniconda is installed"""
        conda_exe = self.ai_env_path / "Miniconda" / "Scripts" / "conda.exe"
        return conda_exe.exists()
    
    def _check_step4_ai2025_env(self) -> bool:
        """Check if AI2025 environment exists"""
        ai2025_path = self.ai_env_path / "Miniconda" / "envs" / "AI2025"
        return ai2025_path.exists()
    
    def _check_step5_vscode(self) -> bool:
        """Check if VS Code is installed"""
        vscode_exe = self.ai_env_path / "VSCode" / "Code.exe"
        return vscode_exe.exists()
    
    def _check_step6_packages(self) -> bool:
        """Check if Python packages are installed in AI2025 environment"""
        # Check for key packages in the AI2025 environment
        ai2025_site_packages = self.ai_env_path / "Miniconda" / "envs" / "AI2025" / "Lib" / "site-packages"
        
        if not ai2025_site_packages.exists():
            return False
        
        # Check for some key AI packages - be more flexible
        key_packages = ["langchain", "torch", "transformers", "pandas", "numpy", "requests"]
        
        try:
            installed_packages = [d.name.lower() for d in ai2025_site_packages.iterdir() if d.is_dir()]
            
            # Check if at least 2 of the key packages are installed (more lenient)
            found_packages = sum(1 for pkg in key_packages if any(pkg in installed.lower() for installed in installed_packages))
            return found_packages >= 2
        except:
            # If we can't read the directory, assume packages not installed
            return False
    
    def _check_step7_ollama(self) -> bool:
        """Check if Ollama is installed"""
        ollama_exe = self.ai_env_path / "Ollama" / "ollama.exe"
        models_dir = self.ai_env_path / "Models"
        return ollama_exe.exists() and models_dir.exists()
    
    def _check_step8_finalization(self) -> bool:
        """Check if finalization is complete"""
        activation_script = self.ai_env_path / "activate_ai_env.bat"
        projects_dir = self.ai_env_path / "Projects"
        
        # Check if activation script exists OR projects directory has content
        # Be more flexible - either one indicates some finalization was done
        script_exists = activation_script.exists()
        projects_has_content = projects_dir.exists() and len(list(projects_dir.iterdir())) > 0
        
        return script_exists or projects_has_content
    
    def detect_installation_state(self) -> dict:
        """Detect current installation state"""
        print("Detecting current installation state...")
        print("=" * 50)
        
        state = {
            "last_completed_step": 0,
            "current_step": 1,
            "status": "not_started",
            "steps": {},
            "timestamp": datetime.now().isoformat(),
            "detection_method": "automatic_scan"
        }
        
        # Check each step
        for step_num in range(1, 9):
            step_name = self.step_names[step_num]
            is_completed = self.step_checks[step_num]()
            
            if is_completed:
                print(f"✅ Step {step_num}: {step_name} - COMPLETED")
                state["steps"][str(step_num)] = {
                    "status": "completed",
                    "name": step_name,
                    "completed_at": datetime.now().isoformat(),
                    "detected": True
                }
                state["last_completed_step"] = step_num
            else:
                print(f"❌ Step {step_num}: {step_name} - NOT COMPLETED")
                state["steps"][str(step_num)] = {
                    "status": "not_started",
                    "name": step_name,
                    "detected": True
                }
                if state["current_step"] == step_num - 1 or (step_num == 1 and state["current_step"] == 1):
                    state["current_step"] = step_num
                break
        
        # Determine overall status
        if state["last_completed_step"] == 0:
            state["status"] = "not_started"
        elif state["last_completed_step"] == 8:
            state["status"] = "completed"
        else:
            state["status"] = "partial"
            state["current_step"] = state["last_completed_step"] + 1
        
        print("=" * 50)
        print(f"Detection complete:")
        print(f"- Last completed step: {state['last_completed_step']}/8")
        print(f"- Current step: {state['current_step']}")
        print(f"- Status: {state['status'].upper()}")
        
        return state
    
    def update_status_file(self, force=False):
        """Update the installation status file"""
        status_file = self.ai_env_path / "installation_status.json"
        
        # Check if status file already exists
        if status_file.exists() and not force:
            print(f"\nStatus file already exists: {status_file}")
            response = input("Do you want to overwrite it? (y/N): ").strip().lower()
            if response != 'y':
                print("Status update cancelled.")
                return False
        
        # Detect current state
        state = self.detect_installation_state()
        
        # Create status file
        print(f"\nCreating status file: {status_file}")
        
        try:
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            
            print("✅ Status file created successfully!")
            print(f"📁 Location: {status_file}")
            
            # Show next steps
            if state["status"] == "partial":
                next_step = state["current_step"]
                print(f"\n🎯 Next step to run: install.bat --step {next_step}")
                print(f"   This will continue from: {self.step_names[next_step]}")
            elif state["status"] == "completed":
                print("\n🎉 Installation appears to be complete!")
                print("   Run: install.bat --status (to verify)")
            else:
                print("\n🚀 Ready to start installation:")
                print("   Run: install.bat")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating status file: {e}")
            return False
    
    def show_current_state(self):
        """Show current installation state without updating file"""
        state = self.detect_installation_state()
        
        print(f"\n📊 Current Installation State:")
        print(f"   Status: {state['status'].upper()}")
        print(f"   Progress: {state['last_completed_step']}/8 steps completed")
        
        if state["status"] == "partial":
            print(f"   Next step: {state['current_step']} - {self.step_names[state['current_step']]}")

def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Environment Status Updater")
    parser.add_argument("--path", type=str,
                       help="Path to AI_Environment (auto-detected if not specified)")

    args = parser.parse_args()

    print("AI Environment Status Updater")
    print("=" * 40)

    updater = StatusUpdater(ai_env_path=args.path if args.path else None)

    # Check if AI Environment exists
    if not updater.ai_env_path or not updater.ai_env_path.exists():
        print("ERROR: AI Environment not found on any drive")
        print("   No installation detected.")
        print("   Use --path to specify the installation location manually")
        return

    print(f"Found AI Environment at: {updater.ai_env_path}\n")
    
    # Show menu
    print("\nOptions:")
    print("1. Show current state (no changes)")
    print("2. Create/update status file")
    print("3. Force update status file")
    
    try:
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == "1":
            updater.show_current_state()
        elif choice == "2":
            updater.update_status_file(force=False)
        elif choice == "3":
            updater.update_status_file(force=True)
        else:
            print("Invalid choice. Showing current state...")
            updater.show_current_state()
            
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step Tracker - Tracks installation progress and enables resume functionality
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class StepTracker:
    """Tracks installation steps and enables resume functionality"""
    
    # Installation steps definition
    STEPS = {
        1: {
            "name": "Check prerequisites",
            "description": "Verifying system and disk space",
            "components": ["system_check", "disk_space", "internet"]
        },
        2: {
            "name": "Create directory structure", 
            "description": "Creating base directories",
            "components": ["directories"]
        },
        3: {
            "name": "Install Miniconda",
            "description": "Downloading and installing Python environment manager", 
            "components": ["miniconda_download", "miniconda_install", "conda_init"]
        },
        4: {
            "name": "Create AI2025 environment",
            "description": "Setting up conda environment with Python 3.10",
            "components": ["conda_env_create", "conda_env_verify"]
        },
        5: {
            "name": "Install VS Code",
            "description": "Downloading and installing portable VS Code",
            "components": ["vscode_download", "vscode_extract", "vscode_config", "vscode_extensions"]
        },
        6: {
            "name": "Install Python packages", 
            "description": "Installing AI and ML libraries using conda",
            "components": ["python_packages"]
        },
        7: {
            "name": "Install Ollama and LLM models",
            "description": "Downloading and installing local AI engine", 
            "components": ["ollama_install", "ollama_models"]
        },
        8: {
            "name": "Finalize installation",
            "description": "Creating shortcuts and startup files",
            "components": ["activation_script", "project_templates", "readme", "installation_info"]
        }
    }
    
    def __init__(self, ai_env_path: Path):
        self.ai_env_path = ai_env_path
        self.status_file = ai_env_path / "installation_status.json"
        self.logger = logging.getLogger(__name__)
        
        # Ensure directory exists
        ai_env_path.mkdir(exist_ok=True)
        
        # Load or create status
        self.status = self._load_status()
    
    def _load_status(self) -> Dict:
        """Load installation status from file"""
        try:
            if self.status_file.exists():
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    status = json.load(f)
                    # Ensure all required keys exist
                    return self._validate_status_structure(status)
            else:
                return self._create_initial_status()
        except Exception as e:
            self.logger.warning(f"Error loading status file: {e}")
            return self._create_initial_status()
    
    def _validate_status_structure(self, status: Dict) -> Dict:
        """Ensure status dictionary has all required keys"""
        required_keys = {
            "installation_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "start_time": datetime.now().isoformat(),
            "last_update": datetime.now().isoformat(),
            "current_step": 1,
            "completed_steps": [],
            "failed_steps": [],
            "step_details": {},
            "total_steps": len(self.STEPS),
            "installation_path": str(self.ai_env_path).replace(':', ':\\') if ':' in str(self.ai_env_path) and ':\\' not in str(self.ai_env_path) else str(self.ai_env_path),
            "installation_drive": str(self.ai_env_path.drive) if hasattr(self.ai_env_path, 'drive') else str(self.ai_env_path)[:2],
            "installer_location": str(Path(__file__).parent.parent),
            "pre_install_state": {},
            "resume_available": False
        }

        # Add missing keys with default values
        for key, default_value in required_keys.items():
            if key not in status:
                status[key] = default_value
                self.logger.info(f"Added missing status key: {key}")

        return status
    
    def _create_initial_status(self) -> Dict:
        """Create initial status structure"""
        return {
            "installation_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "start_time": datetime.now().isoformat(),
            "last_update": datetime.now().isoformat(),
            "current_step": 1,
            "completed_steps": [],
            "failed_steps": [],
            "step_details": {},
            "total_steps": len(self.STEPS),
            "installation_path": str(self.ai_env_path).replace(':', ':\\') if ':' in str(self.ai_env_path) and ':\\' not in str(self.ai_env_path) else str(self.ai_env_path),
            "installation_drive": str(self.ai_env_path.drive) if hasattr(self.ai_env_path, 'drive') else str(self.ai_env_path)[:2],
            "installer_location": str(Path(__file__).parent.parent),
            "pre_install_state": self._capture_pre_install_state(),
            "resume_available": False
        }
    
    def _save_status(self):
        """Save status to file"""
        try:
            self.status["last_update"] = datetime.now().isoformat()
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(self.status, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error saving status file: {e}")
    
    def start_step(self, step_number: int) -> bool:
        """Mark step as started"""
        try:
            if step_number not in self.STEPS:
                self.logger.error(f"Invalid step number: {step_number}")
                return False
            
            self.status["current_step"] = step_number
            self.status["step_details"][str(step_number)] = {
                "name": self.STEPS[step_number]["name"],
                "description": self.STEPS[step_number]["description"],
                "status": "in_progress",
                "start_time": datetime.now().isoformat(),
                "components": self.STEPS[step_number]["components"],
                "completed_components": []
            }
            
            self._save_status()
            self.logger.info(f"Started step {step_number}: {self.STEPS[step_number]['name']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting step {step_number}: {e}")
            return False
    
    def complete_step(self, step_number: int) -> bool:
        """Mark step as completed"""
        try:
            if step_number not in self.STEPS:
                return False
            
            if step_number not in self.status["completed_steps"]:
                self.status["completed_steps"].append(step_number)
            
            # Remove from failed steps if it was there
            if step_number in self.status["failed_steps"]:
                self.status["failed_steps"].remove(step_number)
            
            # Update step details
            if str(step_number) in self.status["step_details"]:
                self.status["step_details"][str(step_number)]["status"] = "completed"
                self.status["step_details"][str(step_number)]["end_time"] = datetime.now().isoformat()
            
            # Update current step to next
            if step_number < len(self.STEPS):
                self.status["current_step"] = step_number + 1
            
            self._save_status()
            self.logger.info(f"Completed step {step_number}: {self.STEPS[step_number]['name']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error completing step {step_number}: {e}")
            return False
    
    def fail_step(self, step_number: int, error_message: str = "") -> bool:
        """Mark step as failed"""
        try:
            if step_number not in self.STEPS:
                return False
            
            if step_number not in self.status["failed_steps"]:
                self.status["failed_steps"].append(step_number)
            
            # Update step details
            if str(step_number) in self.status["step_details"]:
                self.status["step_details"][str(step_number)]["status"] = "failed"
                self.status["step_details"][str(step_number)]["end_time"] = datetime.now().isoformat()
                self.status["step_details"][str(step_number)]["error"] = error_message
            
            self.status["resume_available"] = True
            self._save_status()
            self.logger.error(f"Failed step {step_number}: {self.STEPS[step_number]['name']} - {error_message}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error failing step {step_number}: {e}")
            return False
    
    def complete_component(self, step_number: int, component: str) -> bool:
        """Mark a component within a step as completed"""
        try:
            step_key = str(step_number)
            if step_key in self.status["step_details"]:
                if component not in self.status["step_details"][step_key]["completed_components"]:
                    self.status["step_details"][step_key]["completed_components"].append(component)
                    self._save_status()
                    self.logger.info(f"Completed component '{component}' in step {step_number}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error completing component {component} in step {step_number}: {e}")
            return False
    
    def get_resume_step(self) -> int:
        """Get the step number to resume from"""
        try:
            # If there are failed steps, resume from the first failed step
            if self.status["failed_steps"]:
                return min(self.status["failed_steps"])
            
            # If no failed steps, resume from current step
            return self.status["current_step"]
            
        except Exception as e:
            self.logger.error(f"Error getting resume step: {e}")
            return 1
    
    def get_completed_steps(self) -> List[int]:
        """Get list of completed steps"""
        return self.status.get("completed_steps", [])
    
    def get_failed_steps(self) -> List[int]:
        """Get list of failed steps"""
        return self.status.get("failed_steps", [])
    
    def is_step_completed(self, step_number: int) -> bool:
        """Check if a step is completed"""
        return step_number in self.status.get("completed_steps", [])
    
    def is_step_failed(self, step_number: int) -> bool:
        """Check if a step failed"""
        return step_number in self.status.get("failed_steps", [])
    
    def get_step_info(self, step_number: int) -> Optional[Dict]:
        """Get information about a specific step"""
        if step_number in self.STEPS:
            step_info = self.STEPS[step_number].copy()
            step_info["number"] = step_number
            step_info["completed"] = self.is_step_completed(step_number)
            step_info["failed"] = self.is_step_failed(step_number)
            
            # Add details if available
            step_key = str(step_number)
            if step_key in self.status["step_details"]:
                step_info.update(self.status["step_details"][step_key])
            
            return step_info
        return None
    
    def get_installation_summary(self) -> Dict:
        """Get summary of installation progress"""
        completed = len(self.status.get("completed_steps", []))
        failed = len(self.status.get("failed_steps", []))
        total = len(self.STEPS)
        current = self.status.get("current_step", 1)
        
        return {
            "total_steps": total,
            "completed_steps": completed,
            "failed_steps": failed,
            "current_step": current,
            "progress_percentage": (completed / total) * 100,
            "can_resume": self.status.get("resume_available", False),
            "resume_from_step": self.get_resume_step(),
            "installation_id": self.status.get("installation_id", "unknown"),
            "start_time": self.status.get("start_time", "unknown"),
            "last_update": self.status.get("last_update", "unknown")
        }
    
    def print_status(self):
        """Print current installation status"""
        summary = self.get_installation_summary()
        
        print(f"\n{'='*60}")
        print("INSTALLATION STATUS")
        print(f"{'='*60}")
        print(f"Progress: {summary['completed_steps']}/{summary['total_steps']} steps completed ({summary['progress_percentage']:.1f}%)")
        print(f"Current Step: {summary['current_step']}")
        print(f"Failed Steps: {summary['failed_steps']}")
        
        if summary['can_resume']:
            print(f"Resume Available: Yes (from step {summary['resume_from_step']})")
        else:
            print("Resume Available: No")
        
        print(f"\nStep Details:")
        for step_num in range(1, len(self.STEPS) + 1):
            step_info = self.get_step_info(step_num)
            if step_info:
                status = "[OK]" if step_info['completed'] else "[X]" if step_info['failed'] else "○"
                print(f"  {status} Step {step_num}: {step_info['name']}")
        
        print(f"{'='*60}")
    
    def reset_from_step(self, step_number: int):
        """Reset installation status from a specific step onwards"""
        try:
            # Remove completed steps from step_number onwards
            self.status["completed_steps"] = [s for s in self.status["completed_steps"] if s < step_number]
            
            # Remove failed steps from step_number onwards  
            self.status["failed_steps"] = [s for s in self.status["failed_steps"] if s < step_number]
            
            # Remove step details from step_number onwards
            steps_to_remove = [str(s) for s in range(step_number, len(self.STEPS) + 1)]
            for step_key in steps_to_remove:
                if step_key in self.status["step_details"]:
                    del self.status["step_details"][step_key]
            
            # Set current step
            self.status["current_step"] = step_number
            self.status["resume_available"] = step_number > 1
            
            self._save_status()
            self.logger.info(f"Reset installation status from step {step_number}")
            
        except Exception as e:
            self.logger.error(f"Error resetting from step {step_number}: {e}")
    
    def clear_status(self):
        """Clear all installation status"""
        try:
            if self.status_file.exists():
                self.status_file.unlink()
            self.status = self._create_initial_status()
            self.logger.info("Installation status cleared")
        except Exception as e:
            self.logger.error(f"Error clearing status: {e}")
    
    def complete_installation(self):
        """Mark the entire installation as completed"""
        try:
            # Mark all steps as completed if not already
            for step_num in range(1, len(self.STEPS) + 1):
                if step_num not in self.status["completed_steps"]:
                    self.status["completed_steps"].append(step_num)
            
            # Remove any failed steps
            self.status["failed_steps"] = []
            
            # Set final status
            self.status["current_step"] = len(self.STEPS)
            self.status["resume_available"] = False
            self.status["installation_complete"] = True
            self.status["completion_time"] = datetime.now().isoformat()
            
            self._save_status()
            self.logger.info("Installation marked as completed")
            
        except Exception as e:
            self.logger.error(f"Error marking installation complete: {e}")
    
    def _capture_pre_install_state(self) -> Dict:
        """Capture system state before installation for clean uninstall"""
        try:
            pre_state = {
                "timestamp": datetime.now().isoformat(),
                "target_drive": str(self.ai_env_path.drive) if hasattr(self.ai_env_path, 'drive') else str(self.ai_env_path)[:2],
                "ai_env_existed": self.ai_env_path.exists(),
                "existing_subdirs": [],
                "conda_installations": self._detect_conda_installations(),
                "python_in_path": self._check_python_in_path(),
            }

            # Capture existing subdirectories if AI_Environment already exists
            if self.ai_env_path.exists():
                pre_state["existing_subdirs"] = [
                    str(item.name) for item in self.ai_env_path.iterdir() if item.is_dir()
                ]

            return pre_state

        except Exception as e:
            self.logger.warning(f"Error capturing pre-install state: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    def _detect_conda_installations(self) -> Dict:
        """Detect existing Conda/Miniconda installations"""
        conda_info = {
            "portable_exists": False,
            "portable_path": None,
            "allusers_exists": False,
            "allusers_path": None,
        }

        try:
            # Check portable location
            portable_conda = self.ai_env_path / "Miniconda" / "Scripts" / "conda.exe"
            if portable_conda.exists():
                conda_info["portable_exists"] = True
                conda_info["portable_path"] = str(portable_conda.parent.parent)

            # Check AllUsers location
            allusers_conda = Path("C:/ProgramData/miniconda3/Scripts/conda.exe")
            if allusers_conda.exists():
                conda_info["allusers_exists"] = True
                conda_info["allusers_path"] = str(allusers_conda.parent.parent)

        except Exception as e:
            self.logger.warning(f"Error detecting conda installations: {e}")

        return conda_info

    def _check_python_in_path(self) -> bool:
        """Check if Python is already in system PATH"""
        try:
            import subprocess
            result = subprocess.run(
                ["python", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

    @classmethod
    def get_step_name(cls, step_number: int) -> str:
        """Get step name by number"""
        return cls.STEPS.get(step_number, {}).get("name", f"Unknown Step {step_number}")

    @classmethod
    def get_all_steps(cls) -> Dict:
        """Get all steps information"""
        return cls.STEPS


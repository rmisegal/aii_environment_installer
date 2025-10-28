#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Path Finder - Dynamically locates AI_Environment installation across all drives
"""

import os
import sys
import string
from pathlib import Path
from typing import Optional, List


class AIEnvironmentPathFinder:
    """Finds AI_Environment installation on any drive"""

    @staticmethod
    def find_ai_environment() -> Optional[Path]:
        """
        Search all drives for AI_Environment installation

        Priority:
        1. Check AI_Lab\AI_Environment (external drives)
        2. Check Drive:\AI_Environment (internal drives)

        Returns:
            Path to AI_Environment if found, None otherwise
        """
        # Check all drive letters
        for letter in string.ascii_uppercase:
            drive_path = Path(f"{letter}:\\")

            if not drive_path.exists():
                continue

            # Priority 1: Check AI_Lab\AI_Environment (external drive pattern)
            ai_lab_path = drive_path / "AI_Lab" / "AI_Environment"
            if ai_lab_path.exists() and ai_lab_path.is_dir():
                if AIEnvironmentPathFinder._verify_installation(ai_lab_path):
                    return ai_lab_path

            # Priority 2: Check root AI_Environment (internal drive pattern)
            ai_env_path = drive_path / "AI_Environment"
            if ai_env_path.exists() and ai_env_path.is_dir():
                if AIEnvironmentPathFinder._verify_installation(ai_env_path):
                    return ai_env_path

        return None

    @staticmethod
    def find_all_installations() -> List[Path]:
        """
        Find all AI_Environment installations across all drives

        Returns:
            List of paths to all found installations
        """
        installations = []

        for letter in string.ascii_uppercase:
            drive_path = Path(f"{letter}:\\")

            if not drive_path.exists():
                continue

            # Check AI_Lab\AI_Environment
            ai_lab_path = drive_path / "AI_Lab" / "AI_Environment"
            if ai_lab_path.exists() and ai_lab_path.is_dir():
                if AIEnvironmentPathFinder._verify_installation(ai_lab_path):
                    installations.append(ai_lab_path)

            # Check root AI_Environment
            ai_env_path = drive_path / "AI_Environment"
            if ai_env_path.exists() and ai_env_path.is_dir():
                if AIEnvironmentPathFinder._verify_installation(ai_env_path):
                    installations.append(ai_env_path)

        return installations

    @staticmethod
    def _verify_installation(path: Path) -> bool:
        """
        Verify that the path is actually an AI_Environment installation

        Args:
            path: Path to check

        Returns:
            True if valid installation, False otherwise
        """
        # Check for key signature files/directories
        signatures = [
            "activate_ai_env.bat",
            "installation_info.json",
        ]

        signature_dirs = [
            "Miniconda",
            "Ollama",
            "VSCode",
        ]

        # At least one signature file should exist
        has_file = any((path / sig).exists() for sig in signatures)

        # At least one signature directory should exist
        has_dir = any((path / dir_name).exists() for dir_name in signature_dirs)

        return has_file or has_dir

    @staticmethod
    def get_component_path(component_name: str, ai_env_path: Optional[Path] = None) -> Optional[Path]:
        """
        Get path to a specific component within AI_Environment

        Args:
            component_name: Name of component (e.g., "Ollama", "VSCode", "Miniconda")
            ai_env_path: Base path to AI_Environment (auto-detected if None)

        Returns:
            Path to component if found, None otherwise
        """
        if ai_env_path is None:
            ai_env_path = AIEnvironmentPathFinder.find_ai_environment()

        if ai_env_path is None:
            return None

        component_path = ai_env_path / component_name

        if component_path.exists() and component_path.is_dir():
            return component_path

        return None

    @staticmethod
    def get_ollama_path(ai_env_path: Optional[Path] = None) -> Optional[Path]:
        """
        Get path to Ollama executable

        Args:
            ai_env_path: Base path to AI_Environment (auto-detected if None)

        Returns:
            Path to ollama.exe if found, None otherwise
        """
        ollama_dir = AIEnvironmentPathFinder.get_component_path("Ollama", ai_env_path)

        if ollama_dir is None:
            return None

        ollama_exe = ollama_dir / "ollama.exe"

        if ollama_exe.exists():
            return ollama_exe

        return None

    @staticmethod
    def get_conda_path(ai_env_path: Optional[Path] = None) -> Optional[Path]:
        """
        Get path to Conda installation

        Args:
            ai_env_path: Base path to AI_Environment (auto-detected if None)

        Returns:
            Path to conda executable if found, None otherwise
        """
        # First check portable Miniconda in AI_Environment
        miniconda_dir = AIEnvironmentPathFinder.get_component_path("Miniconda", ai_env_path)

        if miniconda_dir:
            conda_exe = miniconda_dir / "Scripts" / "conda.exe"
            if conda_exe.exists():
                return conda_exe

        # Check system-wide Miniconda/Anaconda
        system_paths = [
            Path("C:\\ProgramData\\miniconda3\\Scripts\\conda.exe"),
            Path("C:\\ProgramData\\Anaconda3\\Scripts\\conda.exe"),
            Path(os.path.expanduser("~\\miniconda3\\Scripts\\conda.exe")),
            Path(os.path.expanduser("~\\Anaconda3\\Scripts\\conda.exe")),
        ]

        for path in system_paths:
            if path.exists():
                return path

        return None


def main():
    """Command-line interface for path finder"""
    import argparse

    parser = argparse.ArgumentParser(description="Find AI_Environment installation")
    parser.add_argument("--component", type=str, help="Find specific component (Ollama, VSCode, Miniconda)")
    parser.add_argument("--all", action="store_true", help="List all installations")
    parser.add_argument("--quiet", action="store_true", help="Only output path, no messages")

    args = parser.parse_args()

    finder = AIEnvironmentPathFinder()

    if args.all:
        installations = finder.find_all_installations()
        if installations:
            for install_path in installations:
                print(install_path)
            sys.exit(0)
        else:
            if not args.quiet:
                print("No AI_Environment installations found", file=sys.stderr)
            sys.exit(1)

    # Find single installation
    ai_env_path = finder.find_ai_environment()

    if ai_env_path is None:
        if not args.quiet:
            print("AI_Environment not found on any drive", file=sys.stderr)
            print("\nSearched locations:", file=sys.stderr)
            print("  - Drive:\\AI_Lab\\AI_Environment (external)", file=sys.stderr)
            print("  - Drive:\\AI_Environment (internal)", file=sys.stderr)
        sys.exit(1)

    if args.component:
        if args.component.lower() == "ollama":
            component_path = finder.get_ollama_path(ai_env_path)
        elif args.component.lower() == "conda":
            component_path = finder.get_conda_path(ai_env_path)
        else:
            component_path = finder.get_component_path(args.component, ai_env_path)

        if component_path:
            print(component_path)
            sys.exit(0)
        else:
            if not args.quiet:
                print(f"Component '{args.component}' not found in {ai_env_path}", file=sys.stderr)
            sys.exit(1)

    # Default: print AI_Environment path
    print(ai_env_path)
    sys.exit(0)


if __name__ == "__main__":
    main()

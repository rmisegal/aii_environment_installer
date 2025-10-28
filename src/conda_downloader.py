#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conda Downloader - Handles downloading Miniconda installer
"""

import os
import logging
from pathlib import Path
from download_manager import DownloadManager

class CondaDownloader:
    """Handles Miniconda download operations"""
    
    def __init__(self, ai_env_path: Path, logs_path: Path):
        self.ai_env_path = ai_env_path
        self.logs_path = logs_path
        self.logger = logging.getLogger(__name__)
        
        # Download manager
        self.download_manager = DownloadManager(logs_path)
        
        # Miniconda download URL (Windows 64-bit)
        self.miniconda_url = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
        
    def download_miniconda(self) -> Path:
        """Download Miniconda installer"""
        try:
            downloads_path = self.ai_env_path.parent / "downloads"
            downloads_path.mkdir(exist_ok=True)
            
            installer_path = downloads_path / "Miniconda3-latest-Windows-x86_64.exe"
            
            self.logger.info("Downloading Miniconda installer...")
            print("Downloading Miniconda (Python environment manager)...")
            
            # Use simple download without description parameter
            success = self.download_manager.download_file(
                url=self.miniconda_url,
                destination=installer_path
            )
            
            if not success:
                self.logger.error("Failed to download Miniconda installer")
                return None
            
            self.logger.info(f"Miniconda installer downloaded: {installer_path}")
            return installer_path
            
        except Exception as e:
            self.logger.error(f"Error downloading Miniconda: {e}")
            return None


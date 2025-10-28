#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Download Manager - Handles all file downloads for the AI Environment Installer
Supports resumable downloads, progress tracking, and integrity verification
"""

import os
import sys
import requests
import hashlib
import logging
from pathlib import Path
from typing import Optional, Callable, Dict, Any
from urllib.parse import urlparse
import time

class DownloadManager:
    """Manages file downloads with progress tracking and resume capability"""
    
    def __init__(self, logs_path: Path):
        self.logs_path = logs_path
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AI-Environment-Installer/1.0'
        })
        
    def download_file(self,
                     url: str,
                     destination: Path,
                     progress_callback: Optional[Callable[[int, int], None]] = None,
                     checksum: Optional[str] = None,
                     checksum_type: str = 'sha256',
                     max_retries: int = 3) -> bool:
        """
        Download a file with progress tracking and optional checksum verification

        Args:
            url: URL to download from
            destination: Local file path to save to
            progress_callback: Function to call with (downloaded, total) bytes
            checksum: Expected checksum for verification
            checksum_type: Type of checksum (sha256, md5, etc.)
            max_retries: Maximum number of retry attempts

        Returns:
            True if download successful, False otherwise
        """
        for attempt in range(max_retries):
            try:
                # Create destination directory
                destination.parent.mkdir(parents=True, exist_ok=True)

                # Check if file already exists and is complete
                if destination.exists() and checksum:
                    if self._verify_checksum(destination, checksum, checksum_type):
                        self.logger.info(f"File already exists and verified: {destination.name}")
                        return True
                    else:
                        self.logger.info(f"File exists but checksum mismatch, re-downloading: {destination.name}")
                        destination.unlink()

                if attempt == 0:
                    self.logger.info(f"Downloading: {url}")
                    self.logger.info(f"Destination: {destination}")
                else:
                    self.logger.info(f"Retry attempt {attempt + 1}/{max_retries}")

                # Get file size for progress tracking
                response = self.session.head(url, allow_redirects=True, timeout=30)
                total_size = int(response.headers.get('content-length', 0))

                # Check if server supports range requests for resume capability
                supports_resume = response.headers.get('accept-ranges') == 'bytes'

                # Determine starting position for resume
                resume_pos = 0
                if supports_resume and destination.exists():
                    resume_pos = destination.stat().st_size
                    if resume_pos >= total_size:
                        resume_pos = 0  # File is larger than expected, restart
                        destination.unlink()

                # Set up headers for resume
                headers = {}
                if resume_pos > 0:
                    headers['Range'] = f'bytes={resume_pos}-'
                    self.logger.info(f"Resuming download from byte {resume_pos} ({resume_pos/(1024*1024):.1f} MB)")
                    print(f"Resuming from {resume_pos/(1024*1024):.1f} MB / {total_size/(1024*1024):.1f} MB")

                # Start download with timeout
                response = self.session.get(url, headers=headers, stream=True, timeout=30)
                response.raise_for_status()

                # Open file for writing (append if resuming)
                mode = 'ab' if resume_pos > 0 else 'wb'
                downloaded = resume_pos

                with open(destination, mode) as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)

                            # Call progress callback
                            if progress_callback:
                                progress_callback(downloaded, total_size)

                # Verify download completed
                if total_size > 0 and downloaded < total_size:
                    raise Exception(f"Incomplete download: {downloaded}/{total_size} bytes")

                # Verify checksum if provided
                if checksum:
                    if not self._verify_checksum(destination, checksum, checksum_type):
                        self.logger.error(f"Checksum verification failed for {destination.name}")
                        destination.unlink()
                        return False

                self.logger.info(f"Download completed: {destination.name}")
                return True

            except Exception as e:
                self.logger.error(f"Download attempt {attempt + 1} failed for {url}: {e}")

                # On last attempt, clean up partial file if it's corrupted
                if attempt == max_retries - 1:
                    self.logger.error(f"All {max_retries} download attempts failed")
                    # Keep the partial file for manual resume
                    if destination.exists():
                        partial_size = destination.stat().st_size
                        self.logger.info(f"Partial file kept at {destination} ({partial_size/(1024*1024):.1f} MB)")
                        print(f"\nPartial file saved. You can retry installation to resume download.")
                    return False
                else:
                    # Wait before retry
                    wait_time = 5 * (attempt + 1)  # Exponential backoff
                    self.logger.info(f"Waiting {wait_time} seconds before retry...")
                    print(f"\nConnection interrupted. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)

        return False
    
    def _verify_checksum(self, file_path: Path, expected_checksum: str, checksum_type: str) -> bool:
        """Verify file checksum"""
        try:
            hash_func = getattr(hashlib, checksum_type.lower())()
            
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hash_func.update(chunk)
            
            actual_checksum = hash_func.hexdigest()
            return actual_checksum.lower() == expected_checksum.lower()
            
        except Exception as e:
            self.logger.error(f"Checksum verification error: {e}")
            return False
    
    def download_with_progress(self, url: str, destination: Path, description: str = "") -> bool:
        """Download with console progress bar"""
        
        def progress_callback(downloaded: int, total: int):
            if total > 0:
                percent = (downloaded / total) * 100
                bar_length = 50
                filled_length = int(bar_length * downloaded // total)
                bar = '█' * filled_length + '-' * (bar_length - filled_length)
                
                # Format sizes
                downloaded_mb = downloaded / (1024 * 1024)
                total_mb = total / (1024 * 1024)
                
                print(f'\r{description}: |{bar}| {percent:.1f}% ({downloaded_mb:.1f}/{total_mb:.1f} MB)', end='')
        
        result = self.download_file(url, destination, progress_callback)
        print()  # New line after progress bar
        return result
    
    def get_download_urls(self) -> Dict[str, Dict[str, Any]]:
        """Get download URLs and metadata for all required components"""
        return {
            "python": {
                "3.10.11": {
                    "url": "https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip",
                    "checksum": "608619f8619075629c9c69f361352a0da6ed7e62f83a0e19c63e0ea32eb7629d",
                    "size_mb": 9.2
                }
            },
            "vscode": {
                "latest": {
                    "url": "https://code.visualstudio.com/sha/download?build=stable&os=win32-x64-archive",
                    "size_mb": 150
                }
            },
            "ollama": {
                "latest": {
                    "url": "https://github.com/ollama/ollama/releases/latest/download/ollama-windows-amd64.zip",
                    "size_mb": 50
                }
            },
            "git": {
                "latest": {
                    "url": "https://github.com/git-for-windows/git/releases/latest/download/PortableGit-2.42.0.2-64-bit.7z.exe",
                    "size_mb": 45
                }
            }
        }
    
    def download_component(self, component: str, version: str = "latest", destination_dir: Path = None) -> Optional[Path]:
        """Download a specific component"""
        urls = self.get_download_urls()
        
        if component not in urls:
            self.logger.error(f"Unknown component: {component}")
            return None
        
        if version not in urls[component]:
            self.logger.error(f"Unknown version {version} for component {component}")
            return None
        
        component_info = urls[component][version]
        url = component_info["url"]
        
        # Determine filename from URL
        parsed_url = urlparse(url)
        filename = Path(parsed_url.path).name
        if not filename or filename == "download":
            filename = f"{component}-{version}.zip"
        
        # Set destination
        if destination_dir is None:
            destination_dir = self.logs_path.parent / "downloads"
        
        destination = destination_dir / filename
        
        # Download with progress
        description = f"Downloading {component} {version}"
        success = self.download_with_progress(url, destination, description)
        
        if success:
            return destination
        else:
            return None


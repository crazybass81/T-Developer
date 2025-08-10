"""
Project Packager Module - Production Implementation
Creates downloadable ZIP packages from assembled projects
"""

import os
import json
import zipfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ProjectPackager:
    """
    Production-ready project packager
    Creates ZIP files from assembled projects
    """
    
    def __init__(self):
        self.logger = logger
        self.input_dir = Path("/tmp/generated_projects")
        self.output_dir = Path("downloads")  # Main downloads directory
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
    async def initialize(self):
        """Initialize project packager"""
        self.logger.info("Project Packager initialized")
        return True
    
    async def package_project(
        self,
        project_id: str,
        project_path: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Package project into downloadable ZIP
        
        Args:
            project_id: Unique project identifier
            project_path: Path to assembled project
            metadata: Project metadata
            
        Returns:
            Package result with download info
        """
        
        try:
            self.logger.info(f"Packaging project {project_id}")
            
            # Validate project path
            source_path = Path(project_path)
            if not source_path.exists():
                raise FileNotFoundError(f"Project path not found: {project_path}")
            
            # Create ZIP file path
            zip_filename = f"{project_id}.zip"
            zip_path = self.output_dir / zip_filename
            
            # Create ZIP archive
            self.logger.info(f"Creating ZIP archive: {zip_path}")
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add all files from project directory
                for file_path in source_path.rglob('*'):
                    if file_path.is_file():
                        # Calculate relative path for archive
                        arcname = file_path.relative_to(source_path)
                        
                        # Skip certain files
                        if self._should_skip_file(str(arcname)):
                            continue
                        
                        # Add file to ZIP
                        zipf.write(file_path, arcname)
                        self.logger.debug(f"Added: {arcname}")
            
            # Get ZIP file info
            zip_size = zip_path.stat().st_size
            
            # Create download metadata
            download_metadata = {
                "project_id": project_id,
                "filename": zip_filename,
                "path": str(zip_path),
                "size_bytes": zip_size,
                "size_mb": round(zip_size / (1024 * 1024), 2),
                "created_at": datetime.now().isoformat(),
                "download_url": f"/api/v1/download/{project_id}",
                "project_info": metadata
            }
            
            # Save download metadata
            metadata_path = self.output_dir / f"{project_id}.json"
            metadata_path.write_text(json.dumps(download_metadata, indent=2))
            
            self.logger.info(f"Project packaged: {zip_filename} ({download_metadata['size_mb']} MB)")
            
            return {
                "success": True,
                "download_id": project_id,
                "filename": zip_filename,
                "download_url": download_metadata["download_url"],
                "size_bytes": zip_size,
                "size_mb": download_metadata["size_mb"],
                "metadata": download_metadata
            }
            
        except Exception as e:
            self.logger.error(f"Failed to package project: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _should_skip_file(self, filename: str) -> bool:
        """
        Check if file should be skipped in packaging
        
        Args:
            filename: File name to check
            
        Returns:
            True if file should be skipped
        """
        
        skip_patterns = [
            ".DS_Store",
            "Thumbs.db",
            "*.pyc",
            "__pycache__",
            ".git",
            ".svn",
            "node_modules",
            ".env.local",
            "*.log"
        ]
        
        for pattern in skip_patterns:
            if pattern in filename:
                return True
        
        return False
    
    async def get_package_info(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about packaged project
        
        Args:
            project_id: Project identifier
            
        Returns:
            Package information if exists
        """
        
        metadata_path = self.output_dir / f"{project_id}.json"
        
        if metadata_path.exists():
            return json.loads(metadata_path.read_text())
        
        return None
    
    async def cleanup_old_packages(self, max_age_hours: int = 24):
        """
        Clean up old package files
        
        Args:
            max_age_hours: Maximum age in hours
        """
        
        try:
            current_time = datetime.now()
            
            for zip_file in self.output_dir.glob("*.zip"):
                # Check file age
                file_time = datetime.fromtimestamp(zip_file.stat().st_mtime)
                age_hours = (current_time - file_time).total_seconds() / 3600
                
                if age_hours > max_age_hours:
                    self.logger.info(f"Removing old package: {zip_file.name}")
                    zip_file.unlink()
                    
                    # Remove metadata file
                    metadata_file = zip_file.with_suffix('.json')
                    if metadata_file.exists():
                        metadata_file.unlink()
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
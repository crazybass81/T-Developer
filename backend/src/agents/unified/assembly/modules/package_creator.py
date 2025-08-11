"""Package Creator Module for Assembly Agent
Creates deployable packages in various formats
"""

from typing import Dict, List, Any, Optional
import asyncio
import os
import zipfile
import tarfile
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

@dataclass
class PackageInfo:
    package_path: str
    package_size: int
    total_files: int
    compression_ratio: float
    package_format: str
    checksum: str

@dataclass
class PackageResult:
    success: bool
    package_path: str
    package_info: PackageInfo
    package_size: int
    total_files: int
    processing_time: float
    error: str = ""

class PackageCreator:
    """Advanced package creation system"""
    
    def __init__(self):
        self.version = "1.0.0"
        
        self.supported_formats = {
            'zip': self._create_zip_package,
            'tar.gz': self._create_tar_package,
            'tar.bz2': self._create_tar_package,
            'folder': self._create_folder_package
        }
    
    async def create_package(
        self,
        build_artifacts: Dict[str, str],
        context: Dict[str, Any],
        workspace_path: str
    ) -> PackageResult:
        """Create deployable package"""
        
        start_time = datetime.now()
        
        try:
            output_format = context.get('output_format', 'zip')
            project_name = context.get('project_name', 'generated-project')
            
            if output_format not in self.supported_formats:
                raise ValueError(f"Unsupported package format: {output_format}")
            
            # Create package using appropriate method
            package_result = await self.supported_formats[output_format](
                build_artifacts, context, workspace_path
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Calculate package info
            package_size = os.path.getsize(package_result['path'])
            
            package_info = PackageInfo(
                package_path=package_result['path'],
                package_size=package_size,
                total_files=len(build_artifacts),
                compression_ratio=package_result.get('compression_ratio', 1.0),
                package_format=output_format,
                checksum=self._calculate_checksum(package_result['path'])
            )
            
            return PackageResult(
                success=True,
                package_path=package_result['path'],
                package_info=package_info,
                package_size=package_size,
                total_files=len(build_artifacts),
                processing_time=processing_time
            )
            
        except Exception as e:
            return PackageResult(
                success=False,
                package_path="",
                package_info=PackageInfo("", 0, 0, 0, "", ""),
                package_size=0,
                total_files=0,
                processing_time=(datetime.now() - start_time).total_seconds(),
                error=str(e)
            )
    
    async def _create_zip_package(
        self,
        build_artifacts: Dict[str, str],
        context: Dict[str, Any],
        workspace_path: str
    ) -> Dict[str, Any]:
        """Create ZIP package"""
        
        project_name = context.get('project_name', 'generated-project')
        package_path = os.path.join(workspace_path, 'packages', f"{project_name}.zip")
        
        os.makedirs(os.path.dirname(package_path), exist_ok=True)
        
        original_size = 0
        compressed_size = 0
        
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path, content in build_artifacts.items():
                # Add file to zip
                zipf.writestr(file_path, content)
                original_size += len(content.encode('utf-8'))
        
        compressed_size = os.path.getsize(package_path)
        compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
        
        return {
            'path': package_path,
            'compression_ratio': compression_ratio
        }
    
    async def _create_tar_package(
        self,
        build_artifacts: Dict[str, str],
        context: Dict[str, Any],
        workspace_path: str
    ) -> Dict[str, Any]:
        """Create TAR package"""
        
        project_name = context.get('project_name', 'generated-project')
        output_format = context.get('output_format', 'tar.gz')
        
        if output_format == 'tar.gz':
            package_path = os.path.join(workspace_path, 'packages', f"{project_name}.tar.gz")
            mode = 'w:gz'
        else:  # tar.bz2
            package_path = os.path.join(workspace_path, 'packages', f"{project_name}.tar.bz2")
            mode = 'w:bz2'
        
        os.makedirs(os.path.dirname(package_path), exist_ok=True)
        
        # Create temporary directory with files
        temp_dir = os.path.join(workspace_path, 'temp', project_name)
        os.makedirs(temp_dir, exist_ok=True)
        
        original_size = 0
        
        for file_path, content in build_artifacts.items():
            full_path = os.path.join(temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            original_size += len(content.encode('utf-8'))
        
        # Create tar archive
        with tarfile.open(package_path, mode) as tarf:
            tarf.add(temp_dir, arcname=project_name)
        
        # Clean up temp directory
        shutil.rmtree(temp_dir)
        
        compressed_size = os.path.getsize(package_path)
        compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
        
        return {
            'path': package_path,
            'compression_ratio': compression_ratio
        }
    
    async def _create_folder_package(
        self,
        build_artifacts: Dict[str, str],
        context: Dict[str, Any],
        workspace_path: str
    ) -> Dict[str, Any]:
        """Create folder package (no compression)"""
        
        project_name = context.get('project_name', 'generated-project')
        package_path = os.path.join(workspace_path, 'packages', project_name)
        
        os.makedirs(package_path, exist_ok=True)
        
        for file_path, content in build_artifacts.items():
            full_path = os.path.join(package_path, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return {
            'path': package_path,
            'compression_ratio': 1.0  # No compression
        }
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate file checksum"""
        
        import hashlib
        
        hash_md5 = hashlib.md5()
        
        if os.path.isfile(file_path):
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
        else:
            # For directories, hash the structure
            for root, dirs, files in os.walk(file_path):
                for file in sorted(files):
                    file_path_full = os.path.join(root, file)
                    with open(file_path_full, "rb") as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            hash_md5.update(chunk)
        
        return hash_md5.hexdigest()[:16]
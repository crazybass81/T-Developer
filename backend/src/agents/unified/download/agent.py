"""
Download Agent - Final stage of the 9-agent pipeline
Provides secure download management and file delivery
"""

from typing import Dict, List, Any, Optional
import asyncio
import os
import shutil
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import json

@dataclass
class DownloadResult:
    success: bool
    download_url: str
    file_path: str
    file_size: int
    checksum: str
    expires_at: datetime
    download_token: str
    metadata: Dict[str, Any]
    processing_time: float
    error: str = ""

class DownloadAgent:
    """Advanced download management system"""
    
    def __init__(self):
        self.version = "1.0.0"
        self.agent_type = "download"
        
        # Download configuration
        self.download_config = {
            'base_download_path': '/tmp/downloads',
            'max_file_size': 100 * 1024 * 1024,  # 100MB
            'expiration_hours': 24,
            'allowed_formats': ['zip', 'tar.gz', 'tar.bz2'],
            'cleanup_interval': 3600,  # 1 hour
        }
        
        # Initialize download directory
        os.makedirs(self.download_config['base_download_path'], exist_ok=True)
    
    async def process(self, input_data: Dict[str, Any]) -> DownloadResult:
        """
        Main download processing method
        Prepares final package for secure download
        """
        
        start_time = datetime.now()
        
        try:
            # Extract assembly results
            assembly_result = input_data.get('assembly_result', {})
            context = input_data.get('context', {})
            
            # Validate assembly result
            if not assembly_result.get('success', False):
                raise ValueError("Assembly stage failed, cannot proceed with download")
            
            # Get package information
            package_path = assembly_result.get('package_path', '')
            if not package_path or not os.path.exists(package_path):
                raise ValueError("Package file not found")
            
            # Prepare download
            download_info = await self._prepare_download(
                package_path, context
            )
            
            # Generate download token
            download_token = self._generate_download_token(
                download_info['secure_path'], context
            )
            
            # Calculate expiration
            expires_at = datetime.now() + timedelta(
                hours=self.download_config['expiration_hours']
            )
            
            # Generate download URL
            download_url = self._generate_download_url(
                download_token, context
            )
            
            # Create download metadata
            metadata = await self._create_download_metadata(
                download_info, context, assembly_result
            )
            
            # Schedule cleanup
            await self._schedule_cleanup(
                download_info['secure_path'], expires_at
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return DownloadResult(
                success=True,
                download_url=download_url,
                file_path=download_info['secure_path'],
                file_size=download_info['file_size'],
                checksum=download_info['checksum'],
                expires_at=expires_at,
                download_token=download_token,
                metadata=metadata,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            return DownloadResult(
                success=False,
                download_url="",
                file_path="",
                file_size=0,
                checksum="",
                expires_at=datetime.now(),
                download_token="",
                metadata={},
                processing_time=processing_time,
                error=str(e)
            )
    
    async def _prepare_download(
        self,
        package_path: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare package for secure download"""
        
        # Validate file
        if not os.path.exists(package_path):
            raise ValueError(f"Package not found: {package_path}")
        
        file_size = os.path.getsize(package_path)
        if file_size > self.download_config['max_file_size']:
            raise ValueError(f"File too large: {file_size} bytes")
        
        # Generate secure filename
        project_name = context.get('project_name', 'generated-project')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        secure_filename = f"{project_name}_{timestamp}_{self._generate_secure_id()}"
        
        # Preserve original extension
        _, ext = os.path.splitext(package_path)
        if ext:
            secure_filename += ext
        
        # Create secure path
        secure_path = os.path.join(
            self.download_config['base_download_path'],
            secure_filename
        )
        
        # Copy file to secure location
        shutil.copy2(package_path, secure_path)
        
        # Calculate checksum
        checksum = self._calculate_file_checksum(secure_path)
        
        # Set secure permissions
        os.chmod(secure_path, 0o644)
        
        return {
            'secure_path': secure_path,
            'secure_filename': secure_filename,
            'file_size': file_size,
            'checksum': checksum,
            'original_path': package_path
        }
    
    def _generate_download_token(
        self,
        file_path: str,
        context: Dict[str, Any]
    ) -> str:
        """Generate secure download token"""
        
        # Create token data
        token_data = {
            'file_path': file_path,
            'timestamp': datetime.now().isoformat(),
            'project_name': context.get('project_name', ''),
            'user_session': context.get('session_id', ''),
            'random': self._generate_secure_id()
        }
        
        # Generate token hash
        token_string = json.dumps(token_data, sort_keys=True)
        token_hash = hashlib.sha256(token_string.encode()).hexdigest()
        
        return token_hash[:32]  # First 32 characters
    
    def _generate_download_url(
        self,
        token: str,
        context: Dict[str, Any]
    ) -> str:
        """Generate secure download URL"""
        
        base_url = context.get('base_url', 'http://localhost:8000')
        return f"{base_url}/api/v1/download/{token}"
    
    async def _create_download_metadata(
        self,
        download_info: Dict[str, Any],
        context: Dict[str, Any],
        assembly_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create comprehensive download metadata"""
        
        metadata = {
            'download_info': {
                'filename': download_info['secure_filename'],
                'size_bytes': download_info['file_size'],
                'size_formatted': self._format_file_size(download_info['file_size']),
                'checksum': download_info['checksum'],
                'format': self._detect_file_format(download_info['secure_path'])
            },
            'project_info': {
                'name': context.get('project_name', 'Generated Project'),
                'framework': context.get('framework', 'react'),
                'language': context.get('language', 'typescript'),
                'components': context.get('selected_components', []),
                'features': context.get('selected_features', [])
            },
            'generation_info': {
                'generated_at': datetime.now().isoformat(),
                'generator_version': self.version,
                'total_files': assembly_result.get('total_files', 0),
                'assembly_score': assembly_result.get('assembly_score', 0),
                'security_score': assembly_result.get('security_score', 0),
                'performance_score': assembly_result.get('performance_score', 0)
            },
            'download_instructions': {
                'steps': [
                    '1. Click the download link to start the download',
                    '2. Extract the downloaded archive to your desired location',
                    '3. Navigate to the project directory',
                    '4. Follow the README.md instructions to set up the project',
                    '5. Run the development server to start coding'
                ],
                'requirements': self._get_system_requirements(context),
                'next_steps': self._get_next_steps(context)
            }
        }
        
        return metadata
    
    async def _schedule_cleanup(
        self,
        file_path: str,
        expires_at: datetime
    ) -> None:
        """Schedule file cleanup after expiration"""
        
        # In production, this would use a proper job scheduler
        # For now, we'll create a simple cleanup record
        cleanup_record = {
            'file_path': file_path,
            'expires_at': expires_at.isoformat(),
            'created_at': datetime.now().isoformat()
        }
        
        cleanup_file = os.path.join(
            self.download_config['base_download_path'],
            '.cleanup_schedule.json'
        )
        
        # Load existing cleanup records
        cleanup_records = []
        if os.path.exists(cleanup_file):
            try:
                with open(cleanup_file, 'r') as f:
                    cleanup_records = json.load(f)
            except:
                cleanup_records = []
        
        # Add new record
        cleanup_records.append(cleanup_record)
        
        # Save updated records
        with open(cleanup_file, 'w') as f:
            json.dump(cleanup_records, f, indent=2)
    
    def _generate_secure_id(self) -> str:
        """Generate cryptographically secure random ID"""
        
        import secrets
        return secrets.token_hex(8)
    
    def _calculate_file_checksum(self, file_path: str) -> str:
        """Calculate SHA-256 checksum of file"""
        
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    def _detect_file_format(self, file_path: str) -> str:
        """Detect file format from extension"""
        
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        format_map = {
            '.zip': 'ZIP Archive',
            '.tar.gz': 'Compressed TAR Archive',
            '.tar.bz2': 'BZ2 Compressed TAR Archive',
            '.tar': 'TAR Archive'
        }
        
        return format_map.get(ext, 'Unknown Format')
    
    def _get_system_requirements(self, context: Dict[str, Any]) -> List[str]:
        """Get system requirements for the generated project"""
        
        framework = context.get('framework', 'react')
        
        requirements = {
            'react': [
                'Node.js 18.x or higher',
                'npm or yarn package manager',
                'Modern web browser'
            ],
            'vue': [
                'Node.js 16.x or higher',
                'npm or yarn package manager',
                'Modern web browser'
            ],
            'angular': [
                'Node.js 18.x or higher',
                'Angular CLI',
                'Modern web browser'
            ],
            'express': [
                'Node.js 18.x or higher',
                'npm or yarn package manager'
            ],
            'fastapi': [
                'Python 3.8 or higher',
                'pip package manager'
            ],
            'django': [
                'Python 3.8 or higher',
                'pip package manager',
                'Database (PostgreSQL recommended)'
            ],
            'flask': [
                'Python 3.7 or higher',
                'pip package manager'
            ]
        }
        
        return requirements.get(framework, ['Check project documentation'])
    
    def _get_next_steps(self, context: Dict[str, Any]) -> List[str]:
        """Get next steps after download"""
        
        framework = context.get('framework', 'react')
        
        steps = {
            'react': [
                'Install dependencies: npm install',
                'Start development server: npm run dev',
                'Open browser to http://localhost:3000',
                'Begin customizing your React application'
            ],
            'vue': [
                'Install dependencies: npm install',
                'Start development server: npm run serve',
                'Open browser to http://localhost:8080',
                'Begin customizing your Vue application'
            ],
            'angular': [
                'Install dependencies: npm install',
                'Start development server: ng serve',
                'Open browser to http://localhost:4200',
                'Begin customizing your Angular application'
            ],
            'express': [
                'Install dependencies: npm install',
                'Start server: npm start',
                'Test API endpoints',
                'Begin implementing your business logic'
            ],
            'fastapi': [
                'Install dependencies: pip install -r requirements.txt',
                'Start server: uvicorn main:app --reload',
                'View API docs at http://localhost:8000/docs',
                'Begin implementing your API endpoints'
            ],
            'django': [
                'Install dependencies: pip install -r requirements.txt',
                'Run migrations: python manage.py migrate',
                'Start server: python manage.py runserver',
                'Begin customizing your Django application'
            ],
            'flask': [
                'Install dependencies: pip install -r requirements.txt',
                'Start server: python app.py',
                'Test your endpoints',
                'Begin implementing your business logic'
            ]
        }
        
        return steps.get(framework, ['Follow project README for setup instructions'])
    
    async def cleanup_expired_files(self) -> Dict[str, Any]:
        """Clean up expired download files"""
        
        cleanup_file = os.path.join(
            self.download_config['base_download_path'],
            '.cleanup_schedule.json'
        )
        
        if not os.path.exists(cleanup_file):
            return {'cleaned': 0, 'errors': 0}
        
        try:
            with open(cleanup_file, 'r') as f:
                cleanup_records = json.load(f)
        except:
            return {'cleaned': 0, 'errors': 1}
        
        current_time = datetime.now()
        cleaned_count = 0
        error_count = 0
        remaining_records = []
        
        for record in cleanup_records:
            try:
                expires_at = datetime.fromisoformat(record['expires_at'])
                
                if current_time > expires_at:
                    # File expired, try to delete
                    file_path = record['file_path']
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        cleaned_count += 1
                else:
                    # File not expired yet, keep record
                    remaining_records.append(record)
            except Exception:
                error_count += 1
        
        # Update cleanup records
        try:
            with open(cleanup_file, 'w') as f:
                json.dump(remaining_records, f, indent=2)
        except:
            error_count += 1
        
        return {
            'cleaned': cleaned_count,
            'errors': error_count,
            'remaining': len(remaining_records)
        }
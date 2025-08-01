# backend/src/agents/implementations/download/download_agent.py
from agno.agent import Agent
from agno.models.aws import AwsBedrock
from agno.memory import ConversationSummaryMemory
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio
import json
import zipfile
import tarfile
import os

@dataclass
class PackageFormat:
    name: str
    extension: str
    compression: str
    includes: List[str]

@dataclass
class DownloadPackage:
    package_id: str
    formats: List[PackageFormat]
    download_urls: Dict[str, str]
    metadata: Dict[str, Any]
    installation_guide: str
    size_bytes: int

class ProjectPackager:
    """프로젝트 패키징 엔진"""
    
    def __init__(self):
        self.agent = Agent(
            name="Project-Packager",
            model=AwsBedrock(id="anthropic.claude-3-sonnet-v2:0"),
            role="Expert project packaging and distribution specialist",
            instructions=[
                "Create comprehensive project packages",
                "Generate installation documentation",
                "Optimize package structure",
                "Ensure cross-platform compatibility"
            ],
            memory=ConversationSummaryMemory(),
            temperature=0.2
        )
    
    async def create_package_structure(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """패키지 구조 생성"""
        prompt = f"""
        Create optimal package structure for project:
        
        Project: {project_data.get('name')}
        Type: {project_data.get('type')}
        Components: {list(project_data.get('components', {}).keys())}
        
        Design:
        1. Directory structure
        2. File organization
        3. Configuration placement
        4. Documentation structure
        """
        
        response = await self.agent.arun(prompt)
        return self._parse_package_structure(response)
    
    def _parse_package_structure(self, response: str) -> Dict[str, Any]:
        """패키지 구조 파싱"""
        return {
            "root_files": ["README.md", "package.json", ".env.example"],
            "directories": {
                "src/": "Source code",
                "tests/": "Test files", 
                "docs/": "Documentation",
                "config/": "Configuration files"
            },
            "structure": "standard"
        }

class MultiFormatGenerator:
    """다중 포맷 생성기"""
    
    def __init__(self):
        self.supported_formats = {
            "zip": self._create_zip_package,
            "tar.gz": self._create_tar_package,
            "docker": self._create_docker_package,
            "npm": self._create_npm_package,
            "pip": self._create_pip_package
        }
    
    async def generate_formats(self, 
                             project_data: Dict[str, Any],
                             requested_formats: List[str]) -> Dict[str, bytes]:
        """다중 포맷 생성"""
        packages = {}
        
        for format_name in requested_formats:
            if format_name in self.supported_formats:
                package_data = await self.supported_formats[format_name](project_data)
                packages[format_name] = package_data
        
        return packages
    
    async def _create_zip_package(self, project_data: Dict[str, Any]) -> bytes:
        """ZIP 패키지 생성"""
        import io
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # 소스 코드 추가
            for file_path, content in project_data.get('files', {}).items():
                zip_file.writestr(file_path, content)
            
            # 설정 파일 추가
            if 'configuration' in project_data:
                zip_file.writestr('config.json', 
                                json.dumps(project_data['configuration'], indent=2))
        
        return zip_buffer.getvalue()
    
    async def _create_tar_package(self, project_data: Dict[str, Any]) -> bytes:
        """TAR.GZ 패키지 생성"""
        import io
        
        tar_buffer = io.BytesIO()
        with tarfile.open(fileobj=tar_buffer, mode='w:gz') as tar_file:
            for file_path, content in project_data.get('files', {}).items():
                tarinfo = tarfile.TarInfo(name=file_path)
                tarinfo.size = len(content.encode())
                tar_file.addfile(tarinfo, io.BytesIO(content.encode()))
        
        return tar_buffer.getvalue()
    
    async def _create_docker_package(self, project_data: Dict[str, Any]) -> bytes:
        """Docker 패키지 생성"""
        dockerfile_content = f"""
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE {project_data.get('port', 3000)}
CMD ["npm", "start"]
"""
        
        docker_compose = f"""
version: '3.8'
services:
  app:
    build: .
    ports:
      - "{project_data.get('port', 3000)}:{project_data.get('port', 3000)}"
    environment:
      - NODE_ENV=production
"""
        
        # Docker 관련 파일들을 ZIP으로 패키징
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            zip_file.writestr('Dockerfile', dockerfile_content)
            zip_file.writestr('docker-compose.yml', docker_compose)
            
            # 프로젝트 파일들 추가
            for file_path, content in project_data.get('files', {}).items():
                zip_file.writestr(file_path, content)
        
        return zip_buffer.getvalue()
    
    async def _create_npm_package(self, project_data: Dict[str, Any]) -> bytes:
        """NPM 패키지 생성"""
        package_json = {
            "name": project_data.get('name', 'generated-project'),
            "version": "1.0.0",
            "description": project_data.get('description', ''),
            "main": "index.js",
            "scripts": {
                "start": "node index.js",
                "test": "npm test"
            },
            "dependencies": project_data.get('dependencies', {}),
            "author": "T-Developer AI",
            "license": "MIT"
        }
        
        return json.dumps(package_json, indent=2).encode()
    
    async def _create_pip_package(self, project_data: Dict[str, Any]) -> bytes:
        """PIP 패키지 생성"""
        setup_py = f"""
from setuptools import setup, find_packages

setup(
    name="{project_data.get('name', 'generated-project')}",
    version="1.0.0",
    description="{project_data.get('description', '')}",
    packages=find_packages(),
    install_requires={project_data.get('dependencies', [])},
    author="T-Developer AI",
    python_requires=">=3.8",
)
"""
        return setup_py.encode()

class InstallationGuideGenerator:
    """설치 가이드 생성기"""
    
    def __init__(self):
        self.agent = Agent(
            name="Installation-Guide-Generator",
            model=AwsBedrock(id="anthropic.claude-3-haiku-v1:0"),
            role="Technical documentation specialist",
            instructions=[
                "Create clear installation instructions",
                "Include troubleshooting steps",
                "Provide platform-specific guidance",
                "Add quick start examples"
            ]
        )
    
    async def generate_guide(self, 
                           project_data: Dict[str, Any],
                           package_formats: List[str]) -> str:
        """설치 가이드 생성"""
        prompt = f"""
        Generate installation guide for:
        
        Project: {project_data.get('name')}
        Type: {project_data.get('type')}
        Formats: {package_formats}
        Dependencies: {project_data.get('dependencies', [])}
        
        Include:
        1. Prerequisites
        2. Installation steps for each format
        3. Configuration setup
        4. Quick start guide
        5. Troubleshooting
        """
        
        return await self.agent.arun(prompt)

class DeliveryManager:
    """배포 관리자"""
    
    def __init__(self):
        self.agent = Agent(
            name="Delivery-Manager",
            model=AwsBedrock(id="amazon.nova-pro-v1:0"),
            role="Software delivery and distribution specialist",
            instructions=[
                "Manage software distribution",
                "Create download strategies",
                "Optimize delivery performance",
                "Ensure secure distribution"
            ]
        )
    
    async def create_delivery_strategy(self, 
                                     package_data: Dict[str, Any]) -> Dict[str, Any]:
        """배포 전략 생성"""
        prompt = f"""
        Create delivery strategy for:
        
        Package size: {package_data.get('size_mb', 0)}MB
        Formats: {list(package_data.get('formats', {}).keys())}
        Target audience: {package_data.get('audience', 'developers')}
        
        Design:
        1. Distribution channels
        2. Download optimization
        3. CDN strategy
        4. Version management
        """
        
        response = await self.agent.arun(prompt)
        return self._parse_delivery_strategy(response)
    
    def _parse_delivery_strategy(self, response: str) -> Dict[str, Any]:
        """배포 전략 파싱"""
        return {
            "channels": ["direct_download", "github_releases", "npm_registry"],
            "cdn_enabled": True,
            "compression": "gzip",
            "versioning": "semantic"
        }

class DownloadAgent:
    """통합 다운로드 에이전트"""
    
    def __init__(self):
        self.packager = ProjectPackager()
        self.format_generator = MultiFormatGenerator()
        self.guide_generator = InstallationGuideGenerator()
        self.delivery_manager = DeliveryManager()
    
    async def create_download_package(self, 
                                    project_data: Dict[str, Any],
                                    requested_formats: List[str] = None) -> DownloadPackage:
        """다운로드 패키지 생성"""
        
        if requested_formats is None:
            requested_formats = ["zip", "tar.gz"]
        
        # 1. 패키지 구조 설계
        package_structure = await self.packager.create_package_structure(project_data)
        
        # 2. 다중 포맷 생성
        format_packages = await self.format_generator.generate_formats(
            project_data, requested_formats
        )
        
        # 3. 설치 가이드 생성
        installation_guide = await self.guide_generator.generate_guide(
            project_data, requested_formats
        )
        
        # 4. 배포 전략 수립
        delivery_strategy = await self.delivery_manager.create_delivery_strategy({
            "size_mb": sum(len(data) for data in format_packages.values()) / (1024 * 1024),
            "formats": format_packages,
            "audience": project_data.get('target_audience', 'developers')
        })
        
        # 5. 다운로드 URL 생성 (시뮬레이션)
        download_urls = self._generate_download_urls(format_packages)
        
        # 6. 패키지 포맷 메타데이터
        package_formats = []
        for format_name, data in format_packages.items():
            package_formats.append(PackageFormat(
                name=format_name,
                extension=f".{format_name}",
                compression="gzip" if "tar" in format_name else "zip",
                includes=["source", "config", "docs"]
            ))
        
        return DownloadPackage(
            package_id=f"pkg_{project_data.get('name', 'project')}_{hash(str(project_data)) % 10000}",
            formats=package_formats,
            download_urls=download_urls,
            metadata={
                "project_name": project_data.get('name'),
                "version": "1.0.0",
                "created_at": "2024-01-01T00:00:00Z",
                "structure": package_structure,
                "delivery_strategy": delivery_strategy
            },
            installation_guide=installation_guide,
            size_bytes=sum(len(data) for data in format_packages.values())
        )
    
    def _generate_download_urls(self, format_packages: Dict[str, bytes]) -> Dict[str, str]:
        """다운로드 URL 생성"""
        base_url = "https://downloads.t-developer.ai/packages"
        urls = {}
        
        for format_name in format_packages.keys():
            urls[format_name] = f"{base_url}/{format_name}/package.{format_name}"
        
        return urls
    
    async def batch_create_packages(self, 
                                  projects: List[Dict[str, Any]]) -> List[DownloadPackage]:
        """배치 패키지 생성"""
        tasks = []
        for project in projects:
            task = self.create_download_package(project)
            tasks.append(task)
        
        return await asyncio.gather(*tasks)
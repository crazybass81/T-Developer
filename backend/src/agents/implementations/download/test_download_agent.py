# backend/src/agents/implementations/download/test_download_agent.py
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from download_agent import (
    DownloadAgent, ProjectPackager, MultiFormatGenerator,
    InstallationGuideGenerator, DeliveryManager,
    PackageFormat, DownloadPackage
)

@pytest.fixture
def sample_project_data():
    return {
        "name": "test-project",
        "type": "web_app",
        "description": "A test web application",
        "files": {
            "index.js": "console.log('Hello World');",
            "package.json": '{"name": "test-project", "version": "1.0.0"}',
            "README.md": "# Test Project\n\nA sample project."
        },
        "dependencies": {"express": "^4.18.0", "react": "^18.0.0"},
        "configuration": {"port": 3000, "env": "production"},
        "target_audience": "developers"
    }

@pytest.fixture
def mock_agent():
    agent = Mock()
    agent.arun = AsyncMock(return_value="Mock response")
    return agent

class TestProjectPackager:
    @pytest.mark.asyncio
    async def test_create_package_structure(self, sample_project_data, mock_agent):
        with patch('download_agent.Agent', return_value=mock_agent):
            packager = ProjectPackager()
            result = await packager.create_package_structure(sample_project_data)
            
            assert "root_files" in result
            assert "directories" in result
            assert "structure" in result
            mock_agent.arun.assert_called_once()

    def test_parse_package_structure(self):
        packager = ProjectPackager()
        response = "Directory structure with src/, tests/, docs/"
        result = packager._parse_package_structure(response)
        
        assert "root_files" in result
        assert "README.md" in result["root_files"]
        assert "src/" in result["directories"]

class TestMultiFormatGenerator:
    @pytest.mark.asyncio
    async def test_generate_formats(self, sample_project_data):
        generator = MultiFormatGenerator()
        formats = ["zip", "tar.gz"]
        
        result = await generator.generate_formats(sample_project_data, formats)
        
        assert "zip" in result
        assert "tar.gz" in result
        assert isinstance(result["zip"], bytes)
        assert isinstance(result["tar.gz"], bytes)

    @pytest.mark.asyncio
    async def test_create_zip_package(self, sample_project_data):
        generator = MultiFormatGenerator()
        result = await generator._create_zip_package(sample_project_data)
        
        assert isinstance(result, bytes)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_create_tar_package(self, sample_project_data):
        generator = MultiFormatGenerator()
        result = await generator._create_tar_package(sample_project_data)
        
        assert isinstance(result, bytes)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_create_docker_package(self, sample_project_data):
        generator = MultiFormatGenerator()
        result = await generator._create_docker_package(sample_project_data)
        
        assert isinstance(result, bytes)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_create_npm_package(self, sample_project_data):
        generator = MultiFormatGenerator()
        result = await generator._create_npm_package(sample_project_data)
        
        assert isinstance(result, bytes)
        package_json = result.decode()
        assert "test-project" in package_json
        assert "1.0.0" in package_json

    @pytest.mark.asyncio
    async def test_create_pip_package(self, sample_project_data):
        generator = MultiFormatGenerator()
        result = await generator._create_pip_package(sample_project_data)
        
        assert isinstance(result, bytes)
        setup_py = result.decode()
        assert "test-project" in setup_py
        assert "setuptools" in setup_py

class TestInstallationGuideGenerator:
    @pytest.mark.asyncio
    async def test_generate_guide(self, sample_project_data, mock_agent):
        with patch('download_agent.Agent', return_value=mock_agent):
            mock_agent.arun.return_value = """
            # Installation Guide
            
            ## Prerequisites
            - Node.js 18+
            - npm or yarn
            
            ## Installation
            1. Download the package
            2. Extract files
            3. Run npm install
            """
            
            generator = InstallationGuideGenerator()
            result = await generator.generate_guide(
                sample_project_data, 
                ["zip", "npm"]
            )
            
            assert "Installation Guide" in result
            assert "Prerequisites" in result
            mock_agent.arun.assert_called_once()

class TestDeliveryManager:
    @pytest.mark.asyncio
    async def test_create_delivery_strategy(self, mock_agent):
        with patch('download_agent.Agent', return_value=mock_agent):
            manager = DeliveryManager()
            package_data = {
                "size_mb": 5.2,
                "formats": {"zip": b"data", "tar.gz": b"data"},
                "audience": "developers"
            }
            
            result = await manager.create_delivery_strategy(package_data)
            
            assert "channels" in result
            assert "cdn_enabled" in result
            assert "compression" in result
            mock_agent.arun.assert_called_once()

    def test_parse_delivery_strategy(self):
        manager = DeliveryManager()
        response = "Use CDN with gzip compression"
        result = manager._parse_delivery_strategy(response)
        
        assert "channels" in result
        assert "direct_download" in result["channels"]
        assert result["cdn_enabled"] is True

class TestDownloadAgent:
    @pytest.mark.asyncio
    async def test_create_download_package_full_flow(self, sample_project_data):
        with patch('download_agent.Agent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.arun = AsyncMock(return_value="Mock response")
            mock_agent_class.return_value = mock_agent
            
            agent = DownloadAgent()
            result = await agent.create_download_package(
                sample_project_data,
                requested_formats=["zip", "tar.gz"]
            )
            
            assert isinstance(result, DownloadPackage)
            assert result.package_id
            assert len(result.formats) == 2
            assert "zip" in result.download_urls
            assert "tar.gz" in result.download_urls
            assert result.installation_guide
            assert result.size_bytes > 0

    @pytest.mark.asyncio
    async def test_create_download_package_default_formats(self, sample_project_data):
        with patch('download_agent.Agent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.arun = AsyncMock(return_value="Mock response")
            mock_agent_class.return_value = mock_agent
            
            agent = DownloadAgent()
            result = await agent.create_download_package(sample_project_data)
            
            # Should use default formats ["zip", "tar.gz"]
            assert len(result.formats) == 2
            format_names = [f.name for f in result.formats]
            assert "zip" in format_names
            assert "tar.gz" in format_names

    def test_generate_download_urls(self):
        agent = DownloadAgent()
        format_packages = {
            "zip": b"zip_data",
            "tar.gz": b"tar_data",
            "docker": b"docker_data"
        }
        
        urls = agent._generate_download_urls(format_packages)
        
        assert len(urls) == 3
        assert all(url.startswith("https://downloads.t-developer.ai") for url in urls.values())
        assert "zip" in urls
        assert "tar.gz" in urls
        assert "docker" in urls

    @pytest.mark.asyncio
    async def test_batch_create_packages(self, sample_project_data):
        with patch('download_agent.Agent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.arun = AsyncMock(return_value="Mock response")
            mock_agent_class.return_value = mock_agent
            
            agent = DownloadAgent()
            projects = [
                sample_project_data,
                {**sample_project_data, "name": "project-2"},
                {**sample_project_data, "name": "project-3"}
            ]
            
            results = await agent.batch_create_packages(projects)
            
            assert len(results) == 3
            assert all(isinstance(r, DownloadPackage) for r in results)
            assert results[0].metadata["project_name"] == "test-project"
            assert results[1].metadata["project_name"] == "project-2"

    @pytest.mark.asyncio
    async def test_package_metadata_structure(self, sample_project_data):
        with patch('download_agent.Agent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.arun = AsyncMock(return_value="Mock response")
            mock_agent_class.return_value = mock_agent
            
            agent = DownloadAgent()
            result = await agent.create_download_package(sample_project_data)
            
            metadata = result.metadata
            assert "project_name" in metadata
            assert "version" in metadata
            assert "created_at" in metadata
            assert "structure" in metadata
            assert "delivery_strategy" in metadata
            
            assert metadata["project_name"] == "test-project"
            assert metadata["version"] == "1.0.0"

    @pytest.mark.asyncio
    async def test_package_formats_structure(self, sample_project_data):
        with patch('download_agent.Agent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.arun = AsyncMock(return_value="Mock response")
            mock_agent_class.return_value = mock_agent
            
            agent = DownloadAgent()
            result = await agent.create_download_package(
                sample_project_data,
                requested_formats=["zip", "docker"]
            )
            
            assert len(result.formats) == 2
            
            zip_format = next(f for f in result.formats if f.name == "zip")
            assert zip_format.extension == ".zip"
            assert zip_format.compression == "zip"
            assert "source" in zip_format.includes
            
            docker_format = next(f for f in result.formats if f.name == "docker")
            assert docker_format.extension == ".docker"

if __name__ == "__main__":
    pytest.main([__file__])
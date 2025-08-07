# Download Agent Documentation

## Overview
The Download Agent is responsible for packaging completed projects into various downloadable formats and managing their distribution. It creates comprehensive packages with installation guides and deployment configurations.

## Architecture

### Core Components

1. **ProjectPackager**: Creates optimal project package structures
2. **MultiFormatGenerator**: Generates packages in multiple formats (ZIP, TAR, Docker, NPM, PIP)
3. **InstallationGuideGenerator**: Creates comprehensive installation documentation
4. **DeliveryManager**: Manages distribution strategies and delivery optimization

## Usage

### Basic Package Creation

```python
from download_agent import DownloadAgent

# Initialize agent
agent = DownloadAgent()

# Project data
project_data = {
    "name": "my-web-app",
    "type": "web_app",
    "description": "A modern web application",
    "files": {
        "index.js": "const express = require('express');",
        "package.json": '{"name": "my-web-app", "version": "1.0.0"}',
        "README.md": "# My Web App"
    },
    "dependencies": {"express": "^4.18.0", "react": "^18.0.0"},
    "configuration": {"port": 3000, "env": "production"}
}

# Create download package
package = await agent.create_download_package(
    project_data,
    requested_formats=["zip", "tar.gz", "docker", "npm"]
)

print(f"Package ID: {package.package_id}")
print(f"Available formats: {[f.name for f in package.formats]}")
print(f"Download URLs: {package.download_urls}")
print(f"Installation guide:\n{package.installation_guide}")
```

### Batch Package Creation

```python
# Create multiple packages
projects = [
    {"name": "frontend-app", "type": "react_app", ...},
    {"name": "backend-api", "type": "fastapi_app", ...},
    {"name": "mobile-app", "type": "react_native", ...}
]

packages = await agent.batch_create_packages(projects)

for package in packages:
    print(f"Created package: {package.metadata['project_name']}")
```

### Individual Component Usage

```python
from download_agent import MultiFormatGenerator, InstallationGuideGenerator

# Generate specific formats
generator = MultiFormatGenerator()
formats = await generator.generate_formats(
    project_data, 
    ["zip", "docker"]
)

# Generate installation guide
guide_generator = InstallationGuideGenerator()
guide = await guide_generator.generate_guide(
    project_data,
    ["zip", "npm"]
)
```

## Configuration

### Environment Variables

```bash
# AWS Bedrock Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Agno Configuration (Optional - Open Source)
AGNO_MONITORING_URL=https://agno.com

# Download Configuration
DOWNLOAD_BASE_URL=https://downloads.t-developer.ai
CDN_ENABLED=true
```

### Agent Configuration

```python
# Custom configuration
agent = DownloadAgent()

# Configure packaging options
agent.packager.agent.instructions.append(
    "Include comprehensive documentation"
)

# Configure delivery strategy
delivery_config = {
    "cdn_enabled": True,
    "compression": "gzip",
    "cache_duration": 3600
}
```

## Supported Formats

### Archive Formats
- **ZIP**: Cross-platform compressed archive
- **TAR.GZ**: Unix/Linux compressed archive
- **TAR.BZ2**: High compression archive

### Package Manager Formats
- **NPM**: Node.js package manager format
- **PIP**: Python package manager format
- **Maven**: Java package manager format

### Container Formats
- **Docker**: Container image with Dockerfile
- **Podman**: OCI-compliant container format

### Platform-Specific
- **Windows**: MSI installer package
- **macOS**: DMG disk image
- **Linux**: DEB/RPM packages

## Package Structure

### Standard Package Contents

```
project-package/
├── README.md                 # Project overview
├── INSTALL.md               # Installation instructions
├── LICENSE                  # License file
├── package.json            # Package metadata
├── src/                    # Source code
│   ├── components/         # Application components
│   ├── config/            # Configuration files
│   └── tests/             # Test files
├── docs/                   # Documentation
│   ├── api.md             # API documentation
│   ├── deployment.md      # Deployment guide
│   └── troubleshooting.md # Troubleshooting guide
├── scripts/               # Utility scripts
│   ├── setup.sh          # Setup script
│   ├── build.sh          # Build script
│   └── deploy.sh         # Deployment script
└── docker/               # Docker configurations
    ├── Dockerfile        # Container definition
    └── docker-compose.yml # Multi-container setup
```

### Package Metadata

```json
{
  "package_id": "pkg_my-web-app_1234",
  "metadata": {
    "project_name": "my-web-app",
    "version": "1.0.0",
    "created_at": "2024-01-01T00:00:00Z",
    "structure": {
      "root_files": ["README.md", "package.json"],
      "directories": {
        "src/": "Source code",
        "docs/": "Documentation"
      }
    },
    "delivery_strategy": {
      "channels": ["direct_download", "github_releases"],
      "cdn_enabled": true,
      "compression": "gzip"
    }
  }
}
```

## Installation Guide Generation

### Generated Guide Structure

```markdown
# Installation Guide

## Prerequisites
- Node.js 18+
- npm or yarn
- Git

## Quick Start
1. Download the package
2. Extract files: `unzip my-web-app.zip`
3. Install dependencies: `npm install`
4. Start application: `npm start`

## Installation Methods

### Method 1: ZIP Package
```bash
# Download and extract
wget https://downloads.t-developer.ai/packages/zip/my-web-app.zip
unzip my-web-app.zip
cd my-web-app
npm install
npm start
```

### Method 2: NPM Package
```bash
# Install via npm
npm install my-web-app
npx my-web-app
```

### Method 3: Docker
```bash
# Run with Docker
docker pull my-web-app:latest
docker run -p 3000:3000 my-web-app
```

## Configuration
- Copy `.env.example` to `.env`
- Update configuration values
- Set required environment variables

## Troubleshooting
- Check Node.js version compatibility
- Verify all dependencies are installed
- Review error logs in `logs/` directory
```

## Delivery Management

### Distribution Channels

```python
# Configure distribution channels
delivery_strategy = {
    "channels": [
        "direct_download",    # Direct HTTP download
        "github_releases",    # GitHub Releases
        "npm_registry",       # NPM Registry
        "docker_hub",         # Docker Hub
        "cdn_distribution"    # CDN Distribution
    ],
    "optimization": {
        "compression": "gzip",
        "caching": True,
        "cdn_enabled": True
    }
}
```

### Download URLs

```python
# Generated download URLs
download_urls = {
    "zip": "https://downloads.t-developer.ai/packages/zip/my-app.zip",
    "tar.gz": "https://downloads.t-developer.ai/packages/tar/my-app.tar.gz",
    "docker": "https://hub.docker.com/r/t-developer/my-app",
    "npm": "https://www.npmjs.com/package/my-app"
}
```

## Advanced Features

### Custom Package Structure

```python
# Define custom package structure
custom_structure = {
    "root_files": ["README.md", "LICENSE", "CHANGELOG.md"],
    "directories": {
        "app/": "Application code",
        "config/": "Configuration files",
        "docs/": "Documentation",
        "tests/": "Test suites",
        "scripts/": "Utility scripts"
    },
    "exclude_patterns": ["*.log", "node_modules/", ".git/"]
}

package = await agent.create_download_package(
    project_data,
    custom_structure=custom_structure
)
```

### Version Management

```python
# Version-specific packaging
versioned_data = {
    **project_data,
    "version": "2.1.0",
    "changelog": "Added new features and bug fixes",
    "breaking_changes": ["API endpoint changes", "Config format update"]
}

package = await agent.create_download_package(versioned_data)
```

### Platform-Specific Packages

```python
# Create platform-specific packages
platforms = ["windows", "macos", "linux"]

for platform in platforms:
    platform_data = {
        **project_data,
        "target_platform": platform,
        "platform_specific_files": get_platform_files(platform)
    }
    
    package = await agent.create_download_package(
        platform_data,
        requested_formats=[f"{platform}_installer"]
    )
```

## Integration Examples

### CI/CD Pipeline

```yaml
# GitHub Actions example
- name: Create Download Packages
  run: |
    python -c "
    import asyncio
    from download_agent import DownloadAgent
    
    async def create_packages():
        agent = DownloadAgent()
        project_data = load_project_data()
        
        package = await agent.create_download_package(
            project_data,
            requested_formats=['zip', 'tar.gz', 'docker']
        )
        
        # Upload to release
        upload_to_github_release(package)
        
        # Update download page
        update_download_page(package.download_urls)
    
    asyncio.run(create_packages())
    "
```

### API Integration

```python
from fastapi import FastAPI
from download_agent import DownloadAgent

app = FastAPI()
agent = DownloadAgent()

@app.post("/create-package")
async def create_package(project_data: dict, formats: list = None):
    package = await agent.create_download_package(
        project_data,
        requested_formats=formats or ["zip", "tar.gz"]
    )
    
    return {
        "package_id": package.package_id,
        "download_urls": package.download_urls,
        "installation_guide": package.installation_guide,
        "size_bytes": package.size_bytes
    }
```

## Best Practices

### 1. Package Optimization
- Minimize package size
- Exclude unnecessary files
- Use appropriate compression
- Include only required dependencies

### 2. Documentation
- Provide clear installation instructions
- Include troubleshooting guides
- Add platform-specific notes
- Include quick start examples

### 3. Version Management
- Use semantic versioning
- Maintain changelog
- Document breaking changes
- Provide migration guides

### 4. Security
- Scan packages for vulnerabilities
- Sign packages when possible
- Use secure distribution channels
- Validate package integrity

## Troubleshooting

### Package Creation Issues
- Check project data completeness
- Verify file permissions
- Review dependency specifications
- Validate configuration format

### Format Generation Problems
- Ensure format compatibility
- Check compression settings
- Verify platform requirements
- Review file size limits

### Distribution Failures
- Validate download URLs
- Check CDN configuration
- Verify access permissions
- Review network connectivity
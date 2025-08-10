"""
Project Assembler Module - Production Implementation
Assembles generated code into complete project structure
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ProjectAssembler:
    """
    Production-ready project assembler
    Takes generated code and creates complete project structure
    """
    
    def __init__(self):
        self.logger = logger
        self.output_dir = Path("/tmp/generated_projects")
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
    async def initialize(self):
        """Initialize project assembler"""
        self.logger.info("Project Assembler initialized")
        return True
    
    async def assemble_project(
        self,
        project_id: str,
        generated_code: Dict[str, Any],
        project_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assemble complete project from generated code
        
        Args:
            project_id: Unique project identifier
            generated_code: Generated code from previous agents
            project_metadata: Project configuration and metadata
            
        Returns:
            Assembly result with project path and statistics
        """
        
        try:
            self.logger.info(f"Assembling project {project_id}")
            
            # Create project directory
            project_path = self.output_dir / project_id
            project_path.mkdir(exist_ok=True, parents=True)
            
            # Extract project info
            project_name = project_metadata.get('project_name', 'untitled')
            project_type = project_metadata.get('project_type', 'react')
            features = project_metadata.get('features', [])
            
            # Process generated files
            files_created = 0
            total_size = 0
            
            # Check if we have actual generated code
            if generated_code and 'files' in generated_code:
                # Write generated files
                for file_path, content in generated_code['files'].items():
                    full_path = project_path / file_path
                    full_path.parent.mkdir(exist_ok=True, parents=True)
                    
                    # Write file content
                    if isinstance(content, dict):
                        # JSON configuration files
                        full_path.write_text(json.dumps(content, indent=2))
                    else:
                        # Regular text files
                        full_path.write_text(str(content))
                    
                    files_created += 1
                    total_size += len(str(content))
                    
            else:
                # No generated code, create basic structure
                self.logger.warning("No generated code provided, creating basic structure")
                await self._create_basic_structure(
                    project_path, 
                    project_name, 
                    project_type,
                    features
                )
                
                # Count created files
                for file in project_path.rglob('*'):
                    if file.is_file():
                        files_created += 1
                        total_size += file.stat().st_size
            
            # Add essential project files if missing
            await self._ensure_essential_files(
                project_path,
                project_name,
                project_type,
                project_metadata
            )
            
            # Create project manifest
            manifest = {
                "project_id": project_id,
                "project_name": project_name,
                "project_type": project_type,
                "features": features,
                "created_at": datetime.now().isoformat(),
                "files_count": files_created,
                "total_size": total_size,
                "structure": self._get_project_structure(project_path)
            }
            
            manifest_path = project_path / ".t-developer.json"
            manifest_path.write_text(json.dumps(manifest, indent=2))
            
            self.logger.info(f"Project assembled: {files_created} files, {total_size} bytes")
            
            return {
                "success": True,
                "project_path": str(project_path),
                "files_created": files_created,
                "total_size": total_size,
                "manifest": manifest,
                "structure": manifest["structure"]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to assemble project: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _create_basic_structure(
        self,
        project_path: Path,
        project_name: str,
        project_type: str,
        features: List[str]
    ):
        """Create basic project structure based on type"""
        
        if project_type == "react":
            await self._create_react_structure(project_path, project_name, features)
        elif project_type == "vue":
            await self._create_vue_structure(project_path, project_name, features)
        elif project_type == "nextjs":
            await self._create_nextjs_structure(project_path, project_name, features)
        else:
            await self._create_generic_structure(project_path, project_name)
    
    async def _create_react_structure(
        self,
        project_path: Path,
        project_name: str,
        features: List[str]
    ):
        """Create React project structure"""
        
        # Create directories
        (project_path / "src").mkdir(exist_ok=True)
        (project_path / "src" / "components").mkdir(exist_ok=True)
        (project_path / "src" / "styles").mkdir(exist_ok=True)
        (project_path / "public").mkdir(exist_ok=True)
        
        # package.json
        package_json = {
            "name": project_name.lower().replace(" ", "-"),
            "version": "0.1.0",
            "private": True,
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-scripts": "5.0.1"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test",
                "eject": "react-scripts eject"
            }
        }
        
        # Add feature dependencies
        if "routing" in features:
            package_json["dependencies"]["react-router-dom"] = "^6.8.0"
        if "state-management" in features:
            package_json["dependencies"]["redux"] = "^4.2.0"
            package_json["dependencies"]["react-redux"] = "^8.0.5"
        
        (project_path / "package.json").write_text(json.dumps(package_json, indent=2))
        
        # index.html
        index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{project_name}</title>
</head>
<body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
</body>
</html>"""
        (project_path / "public" / "index.html").write_text(index_html)
        
        # App.js
        app_js = f"""import React from 'react';
import './App.css';

function App() {{
  return (
    <div className="App">
      <header className="App-header">
        <h1>{project_name}</h1>
        <p>Welcome to your new React app!</p>
      </header>
    </div>
  );
}}

export default App;"""
        (project_path / "src" / "App.js").write_text(app_js)
        
        # index.js
        index_js = """import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);"""
        (project_path / "src" / "index.js").write_text(index_js)
        
        # CSS files
        (project_path / "src" / "App.css").write_text("""
.App {
  text-align: center;
  padding: 20px;
}

.App-header {
  background-color: #282c34;
  padding: 20px;
  color: white;
}""")
        
        (project_path / "src" / "index.css").write_text("""
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}""")
    
    async def _create_vue_structure(
        self,
        project_path: Path,
        project_name: str,
        features: List[str]
    ):
        """Create Vue project structure"""
        
        # Create directories
        (project_path / "src").mkdir(exist_ok=True)
        (project_path / "src" / "components").mkdir(exist_ok=True)
        (project_path / "src" / "assets").mkdir(exist_ok=True)
        (project_path / "public").mkdir(exist_ok=True)
        
        # package.json
        package_json = {
            "name": project_name.lower().replace(" ", "-"),
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "serve": "vue-cli-service serve",
                "build": "vue-cli-service build"
            },
            "dependencies": {
                "vue": "^3.2.13"
            },
            "devDependencies": {
                "@vue/cli-service": "~5.0.0"
            }
        }
        
        (project_path / "package.json").write_text(json.dumps(package_json, indent=2))
        
        # main.js
        main_js = """import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')"""
        (project_path / "src" / "main.js").write_text(main_js)
        
        # App.vue
        app_vue = f"""<template>
  <div id="app">
    <h1>{project_name}</h1>
    <p>Welcome to your new Vue app!</p>
  </div>
</template>

<script>
export default {{
  name: 'App'
}}
</script>

<style>
#app {{
  text-align: center;
  padding: 20px;
}}
</style>"""
        (project_path / "src" / "App.vue").write_text(app_vue)
    
    async def _create_nextjs_structure(
        self,
        project_path: Path,
        project_name: str,
        features: List[str]
    ):
        """Create Next.js project structure"""
        
        # Create directories
        (project_path / "pages").mkdir(exist_ok=True)
        (project_path / "styles").mkdir(exist_ok=True)
        (project_path / "public").mkdir(exist_ok=True)
        
        # package.json
        package_json = {
            "name": project_name.lower().replace(" ", "-"),
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start"
            },
            "dependencies": {
                "next": "13.4.0",
                "react": "18.2.0",
                "react-dom": "18.2.0"
            }
        }
        
        (project_path / "package.json").write_text(json.dumps(package_json, indent=2))
        
        # pages/index.js
        index_js = f"""export default function Home() {{
  return (
    <div>
      <h1>{project_name}</h1>
      <p>Welcome to your new Next.js app!</p>
    </div>
  )
}}"""
        (project_path / "pages" / "index.js").write_text(index_js)
    
    async def _create_generic_structure(
        self,
        project_path: Path,
        project_name: str
    ):
        """Create generic project structure"""
        
        # Create basic directories
        (project_path / "src").mkdir(exist_ok=True)
        (project_path / "docs").mkdir(exist_ok=True)
        (project_path / "tests").mkdir(exist_ok=True)
        
        # Create README
        readme = f"""# {project_name}

Generated by T-Developer AI Platform

## Getting Started

1. Install dependencies
2. Run the development server
3. Start building!

## Structure

- `src/` - Source code
- `docs/` - Documentation
- `tests/` - Test files
"""
        (project_path / "README.md").write_text(readme)
    
    async def _ensure_essential_files(
        self,
        project_path: Path,
        project_name: str,
        project_type: str,
        metadata: Dict[str, Any]
    ):
        """Ensure essential files exist"""
        
        # README.md
        if not (project_path / "README.md").exists():
            readme_content = f"""# {project_name}

{metadata.get('description', 'A project generated by T-Developer')}

## Project Type
{project_type}

## Features
{', '.join(metadata.get('features', []))}

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start development server:
   ```bash
   npm start
   ```

Generated by T-Developer AI Platform
"""
            (project_path / "README.md").write_text(readme_content)
        
        # .gitignore
        if not (project_path / ".gitignore").exists():
            gitignore = """node_modules/
.env
.env.local
.DS_Store
*.log
dist/
build/
.cache/
"""
            (project_path / ".gitignore").write_text(gitignore)
    
    def _get_project_structure(self, project_path: Path) -> Dict[str, Any]:
        """Get project directory structure"""
        
        structure = {}
        
        for item in project_path.iterdir():
            if item.name.startswith('.'):
                continue
                
            if item.is_dir():
                structure[item.name] = self._get_project_structure(item)
            else:
                structure[item.name] = {
                    "type": "file",
                    "size": item.stat().st_size
                }
        
        return structure
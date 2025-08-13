"""🧬 T-Developer Project Scaffolder <6.5KB"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional


class ProjectScaffolder:
    """Ultra-lightweight project scaffolder"""

    def __init__(self):
        self.templates = {
            "react": {"src": ["components", "pages", "utils"], "public": []},
            "vue": {"src": ["components", "views", "router"], "public": []},
            "express": {"src": ["routes", "models", "middleware"], "config": []},
            "fastapi": {"app": ["api", "models", "core"], "tests": []},
            "django": {"project": ["apps", "settings", "urls"], "static": []},
            "flask": {"app": ["routes", "models", "templates"], "config": []},
        }

    def create_structure(self, framework: str, project_name: str, base_path: str) -> Dict:
        """Create project structure"""
        if framework not in self.templates:
            return {"success": False, "error": "Unsupported framework"}

        project_path = Path(base_path) / project_name
        structure = self.templates[framework]
        created_dirs = []

        try:
            for root_dir, subdirs in structure.items():
                root_path = project_path / root_dir
                root_path.mkdir(parents=True, exist_ok=True)
                created_dirs.append(str(root_path))

                for subdir in subdirs:
                    sub_path = root_path / subdir
                    sub_path.mkdir(exist_ok=True)
                    created_dirs.append(str(sub_path))

            # Create basic files
            self._create_basic_files(project_path, framework)

            return {
                "success": True,
                "project_path": str(project_path),
                "directories": created_dirs,
                "framework": framework,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _create_basic_files(self, project_path: Path, framework: str):
        """Create essential files"""
        files = {
            "react": {
                "package.json": self._react_package(),
                "src/App.js": "export default function App() { return <div>Hello</div>; }",
                "public/index.html": "<!DOCTYPE html><html><head><title>App</title></head><body><div id='root'></div></body></html>",
            },
            "express": {
                "package.json": self._express_package(),
                "src/app.js": "const express = require('express');\nconst app = express();\napp.listen(3000);",
                "src/routes/index.js": "const express = require('express');\nmodule.exports = express.Router();",
            },
            "fastapi": {
                "requirements.txt": "fastapi\nuvicorn",
                "app/main.py": "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/')\ndef read_root(): return {'Hello': 'World'}",
                "app/__init__.py": "",
            },
        }

        if framework in files:
            for file_path, content in files[framework].items():
                full_path = project_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)

    def _react_package(self) -> str:
        return json.dumps(
            {
                "name": "react-app",
                "version": "1.0.0",
                "dependencies": {"react": "^18.0.0", "react-dom": "^18.0.0"},
                "scripts": {"start": "react-scripts start", "build": "react-scripts build"},
            },
            indent=2,
        )

    def _express_package(self) -> str:
        return json.dumps(
            {
                "name": "express-app",
                "version": "1.0.0",
                "dependencies": {"express": "^4.18.0"},
                "scripts": {"start": "node src/app.js", "dev": "nodemon src/app.js"},
            },
            indent=2,
        )

    def get_supported_frameworks(self) -> List[str]:
        """Get list of supported frameworks"""
        return list(self.templates.keys())

    def validate_framework(self, framework: str) -> bool:
        """Validate framework support"""
        return framework in self.templates

    def customize_structure(self, framework: str, custom_dirs: Dict) -> Dict:
        """Add custom directories to framework template"""
        if framework not in self.templates:
            return {"success": False, "error": "Unsupported framework"}

        template = self.templates[framework].copy()
        for root, dirs in custom_dirs.items():
            if root in template:
                template[root].extend(dirs)
            else:
                template[root] = dirs

        return {"success": True, "template": template}


def create_project(framework: str, name: str, path: str = ".") -> Dict:
    """Quick project creation"""
    scaffolder = ProjectScaffolder()
    return scaffolder.create_structure(framework, name, path)


def list_frameworks() -> List[str]:
    """List supported frameworks"""
    return ProjectScaffolder().get_supported_frameworks()

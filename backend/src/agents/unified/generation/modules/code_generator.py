"""🧬 T-Developer Code Generator <6.5KB"""
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


class CodeGenerator:
    """Ultra-lightweight code generator"""

    def __init__(self):
        self.templates = {
            "react": {
                "component": "function {name}() {{ return <div>{content}</div>; }}",
                "hook": "import {{ useState }} from 'react';\nfunction use{name}() {{ const [state, setState] = useState(null); return [state, setState]; }}",
            },
            "vue": {
                "component": "<template><div>{content}</div></template>\n<script>\nexport default {{ name: '{name}' }}\n</script>",
                "composable": "import {{ ref }} from 'vue';\nexport function use{name}() {{ const state = ref(null); return {{ state }}; }}",
            },
            "express": {
                "route": "app.{method}('/{path}', (req, res) => {{ res.json({{ message: '{message}' }}); }});",
                "middleware": "function {name}(req, res, next) {{ console.log('{name}'); next(); }}",
            },
            "fastapi": {
                "route": "@app.{method}('/{path}')\ndef {name}(): return {{'message': '{message}'}}",
                "model": "from pydantic import BaseModel\nclass {name}(BaseModel): {fields}",
            },
        }

        self.patterns = {
            "camelCase": lambda s: re.sub(r"_(.)", lambda m: m.group(1).upper(), s.lower()),
            "PascalCase": lambda s: "".join(
                word.capitalize() for word in s.replace("_", " ").replace("-", " ").split()
            ),
            "snake_case": lambda s: re.sub(r"([A-Z])", r"_\1", s).lower().lstrip("_"),
            "kebab-case": lambda s: re.sub(r"([A-Z])", r"-\1", s).lower().lstrip("-"),
        }

    def generate(self, framework: str, template_type: str, **params) -> str:
        """Generate code from template"""
        if framework not in self.templates:
            return f"// Unsupported framework: {framework}"

        if template_type not in self.templates[framework]:
            return f"// Unsupported template: {template_type}"

        template = self.templates[framework][template_type]

        # Apply naming conventions
        if "name" in params:
            params["Name"] = self.patterns["PascalCase"](params["name"])
            params["name_snake"] = self.patterns["snake_case"](params["name"])
            params["name_kebab"] = self.patterns["kebab-case"](params["name"])

        try:
            return template.format(**params)
        except KeyError as e:
            return f"// Missing parameter: {e}"

    def generate_file(self, framework: str, file_type: str, name: str, **opts) -> Dict:
        """Generate complete file"""
        content = self.generate(framework, file_type, name=name, **opts)

        extensions = {
            ("react", "component"): "jsx",
            ("react", "hook"): "js",
            ("vue", "component"): "vue",
            ("express", "route"): "js",
            ("fastapi", "route"): "py",
        }

        ext = extensions.get((framework, file_type), "txt")
        filename = (
            f"{self.patterns['PascalCase'](name) if 'component' in file_type else name}.{ext}"
        )

        return {"filename": filename, "content": content, "framework": framework, "type": file_type}

    def generate_project_structure(self, framework: str, project_name: str) -> List[Dict]:
        """Generate basic project structure"""
        files = []

        templates = {
            "react": [
                ("src/App.js", "function App() { return <div>React App</div>; }"),
                (
                    "src/index.js",
                    "import React from 'react';\nimport ReactDOM from 'react-dom';\nimport App from './App';",
                ),
                (
                    "package.json",
                    json.dumps({"name": project_name, "dependencies": {"react": "^18.0.0"}}),
                ),
            ],
            "express": [
                (
                    "app.js",
                    "const express = require('express');\nconst app = express();\napp.listen(3000);",
                ),
                (
                    "package.json",
                    json.dumps({"name": project_name, "dependencies": {"express": "^4.18.0"}}),
                ),
            ],
            "fastapi": [
                ("main.py", "from fastapi import FastAPI\napp = FastAPI()"),
                ("requirements.txt", "fastapi\nuvicorn"),
            ],
        }

        if framework in templates:
            files = [{"path": path, "content": content} for path, content in templates[framework]]

        return files

    def validate_code(self, code: str, lang: str) -> Dict:
        """Basic validation"""
        issues = []
        if lang == "javascript" and "var " in code:
            issues.append("Use const/let")
        elif lang == "python" and "import *" in code:
            issues.append("Avoid * imports")
        return {"valid": len(issues) == 0, "issues": issues}

    def get_supported_frameworks(self) -> List[str]:
        """Get supported frameworks"""
        return list(self.templates.keys())

    def get_template_types(self, framework: str) -> List[str]:
        """Get available template types for framework"""
        return list(self.templates.get(framework, {}).keys())


# Convenience functions
def generate_component(framework: str, name: str, **options) -> str:
    """Quick component generation"""
    gen = CodeGenerator()
    return gen.generate(framework, "component", name=name, **options)


def generate_route(framework: str, name: str, method: str = "get", **options) -> str:
    """Quick route generation"""
    gen = CodeGenerator()
    return gen.generate(framework, "route", name=name, method=method, **options)


def create_project_files(framework: str, project_name: str) -> List[Dict]:
    """Create basic project files"""
    gen = CodeGenerator()
    return gen.generate_project_structure(framework, project_name)

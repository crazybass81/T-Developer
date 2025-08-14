"""DocGenerator - Day 35
Documentation auto-generation - Size: ~6.5KB"""
import ast
import os
from typing import Any, Dict, List


class DocGenerator:
    """Generate documentation automatically - Size optimized to 6.5KB"""

    def __init__(self):
        self.templates = {
            "readme": "# {title}\n\n{desc}\n\n## Installation\n{install}\n\n## Usage\n{usage}",
            "api": "## {endpoint}\n\n**Method**: {method}\n\n**Params**: {params}\n\n**Response**: {response}",
            "class": "### {name}\n\n{docstring}\n\n**Methods**:\n{methods}",
            "function": "#### {name}\n\n{docstring}\n\n**Args**: {args}\n\n**Returns**: {returns}",
        }

    def generate_from_code(self, code: str, title: str = "Documentation") -> str:
        """Generate docs from Python code"""
        try:
            tree = ast.parse(code)
        except:
            return "# Parse Error\nCould not parse code"

        doc = f"# {title}\n\n"

        # Module docstring
        module_doc = ast.get_docstring(tree)
        if module_doc:
            doc += f"{module_doc}\n\n"

        # Classes
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                doc += self._document_class(node)
            elif isinstance(node, ast.FunctionDef):
                doc += self._document_function(node)

        return doc

    def generate_api_docs(self, endpoints: List[Dict[str, Any]]) -> str:
        """Generate API documentation"""
        doc = "# API Documentation\n\n"

        for ep in endpoints:
            doc += f"## {ep.get('path', '/')}\n\n"
            doc += f"**Method**: {ep.get('method', 'GET')}\n\n"

            if ep.get("params"):
                doc += "**Parameters**:\n"
                for p in ep["params"]:
                    doc += f"- `{p['name']}` ({p.get('type', 'str')}): {p.get('desc', '')}\n"
                doc += "\n"

            if ep.get("response"):
                doc += f"**Response**: `{ep['response']}`\n\n"

            if ep.get("example"):
                doc += "**Example**:\n```json\n{ep['example']}\n```\n\n"

        return doc

    def generate_readme(self, config: Dict[str, Any]) -> str:
        """Generate README.md"""
        readme = f"# {config.get('name', 'Project')}\n\n"
        readme += f"{config.get('description', 'Project description')}\n\n"

        if config.get("features"):
            readme += "## Features\n"
            for feat in config["features"]:
                readme += f"- {feat}\n"
            readme += "\n"

        if config.get("install"):
            readme += "## Installation\n```bash\n"
            readme += config["install"]
            readme += "\n```\n\n"

        if config.get("usage"):
            readme += "## Usage\n```python\n"
            readme += config["usage"]
            readme += "\n```\n\n"

        if config.get("api"):
            readme += "## API\n"
            readme += self.generate_api_docs(config["api"])

        return readme

    def generate_changelog(self, versions: List[Dict[str, Any]]) -> str:
        """Generate CHANGELOG.md"""
        changelog = "# Changelog\n\n"

        for v in versions:
            changelog += f"## [{v['version']}] - {v.get('date', 'TBD')}\n\n"

            if v.get("added"):
                changelog += "### Added\n"
                for item in v["added"]:
                    changelog += f"- {item}\n"
                changelog += "\n"

            if v.get("changed"):
                changelog += "### Changed\n"
                for item in v["changed"]:
                    changelog += f"- {item}\n"
                changelog += "\n"

            if v.get("fixed"):
                changelog += "### Fixed\n"
                for item in v["fixed"]:
                    changelog += f"- {item}\n"
                changelog += "\n"

        return changelog

    def _document_class(self, node: ast.ClassDef) -> str:
        """Document a class"""
        doc = f"## Class: {node.name}\n\n"

        docstring = ast.get_docstring(node)
        if docstring:
            doc += f"{docstring}\n\n"

        doc += "### Methods\n\n"
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                doc += self._document_method(item)

        return doc

    def _document_function(self, node: ast.FunctionDef) -> str:
        """Document a function"""
        doc = f"### {node.name}\n\n"

        docstring = ast.get_docstring(node)
        if docstring:
            doc += f"{docstring}\n\n"

        # Arguments
        args = []
        for arg in node.args.args:
            args.append(arg.arg)

        if args:
            doc += f"**Arguments**: {', '.join(args)}\n\n"

        return doc

    def _document_method(self, node: ast.FunctionDef) -> str:
        """Document a method"""
        if node.name.startswith("_") and node.name != "__init__":
            return ""  # Skip private methods

        doc = f"#### {node.name}\n"

        docstring = ast.get_docstring(node)
        if docstring:
            doc += f"{docstring}\n"

        return doc + "\n"

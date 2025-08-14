"""APIDocBuilder - Day 35
API documentation builder - Size: ~6.5KB"""
import json
from typing import Any, Dict, List


class APIDocBuilder:
    """Build API documentation - Size optimized to 6.5KB"""

    def __init__(self):
        self.openapi_version = "3.0.0"
        self.formats = ["openapi", "markdown", "html"]

    def build_openapi(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Build OpenAPI specification"""
        spec = {
            "openapi": self.openapi_version,
            "info": {
                "title": config.get("title", "API"),
                "version": config.get("version", "1.0.0"),
                "description": config.get("description", ""),
            },
            "servers": config.get("servers", [{"url": "http://localhost:8000"}]),
            "paths": {},
        }

        for endpoint in config.get("endpoints", []):
            path = endpoint.get("path", "/")
            method = endpoint.get("method", "get").lower()

            if path not in spec["paths"]:
                spec["paths"][path] = {}

            spec["paths"][path][method] = {
                "summary": endpoint.get("summary", ""),
                "description": endpoint.get("description", ""),
                "parameters": self._build_parameters(endpoint.get("params", [])),
                "responses": self._build_responses(endpoint.get("responses", {})),
            }

            if endpoint.get("requestBody"):
                spec["paths"][path][method]["requestBody"] = {
                    "content": {"application/json": {"schema": endpoint["requestBody"]}}
                }

        return spec

    def build_markdown(self, config: Dict[str, Any]) -> str:
        """Build Markdown documentation"""
        md = f"# {config.get('title', 'API Documentation')}\n\n"
        md += f"{config.get('description', '')}\n\n"
        md += f"**Version**: {config.get('version', '1.0.0')}\n\n"

        if config.get("servers"):
            md += "## Servers\n"
            for server in config["servers"]:
                md += f"- {server.get('url', '')}: {server.get('description', '')}\n"
            md += "\n"

        md += "## Endpoints\n\n"

        for endpoint in config.get("endpoints", []):
            md += f"### {endpoint.get('method', 'GET').upper()} {endpoint.get('path', '/')}\n\n"
            md += f"{endpoint.get('description', '')}\n\n"

            if endpoint.get("params"):
                md += "**Parameters**:\n"
                for param in endpoint["params"]:
                    md += f"- `{param['name']}` ({param.get('type', 'string')})"
                    if param.get("required"):
                        md += " *required*"
                    md += f": {param.get('description', '')}\n"
                md += "\n"

            if endpoint.get("requestBody"):
                md += "**Request Body**:\n```json\n"
                md += json.dumps(endpoint["requestBody"].get("example", {}), indent=2)
                md += "\n```\n\n"

            if endpoint.get("responses"):
                md += "**Responses**:\n"
                for code, resp in endpoint["responses"].items():
                    md += f"- `{code}`: {resp.get('description', '')}\n"
                md += "\n"

        return md

    def build_html(self, config: Dict[str, Any]) -> str:
        """Build HTML documentation"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{config.get("title", "API")}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; border-bottom: 1px solid #eee; }}
        h3 {{ color: #888; }}
        code {{ background: #f4f4f4; padding: 2px 5px; }}
        pre {{ background: #f4f4f4; padding: 10px; overflow-x: auto; }}
        .endpoint {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
        .method {{ font-weight: bold; }}
        .get {{ color: #61affe; }}
        .post {{ color: #49cc90; }}
        .put {{ color: #fca130; }}
        .delete {{ color: #f93e3e; }}
    </style>
</head>
<body>
    <h1>{config.get("title", "API Documentation")}</h1>
    <p>{config.get("description", "")}</p>
    <p><strong>Version</strong>: {config.get("version", "1.0.0")}</p>
"""

        for endpoint in config.get("endpoints", []):
            method = endpoint.get("method", "GET").upper()
            method_class = method.lower()

            html += f"""
    <div class="endpoint">
        <h3><span class="method {method_class}">{method}</span> {endpoint.get("path", "/")}</h3>
        <p>{endpoint.get("description", "")}</p>
"""

            if endpoint.get("params"):
                html += "<h4>Parameters</h4><ul>"
                for param in endpoint["params"]:
                    html += f"<li><code>{param['name']}</code> ({param.get('type', 'string')})"
                    if param.get("required"):
                        html += " <em>required</em>"
                    html += f": {param.get('description', '')}</li>"
                html += "</ul>"

            html += "</div>"

        html += "</body></html>"
        return html

    def _build_parameters(self, params: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build OpenAPI parameters"""
        parameters = []
        for param in params:
            parameters.append(
                {
                    "name": param.get("name", ""),
                    "in": param.get("in", "query"),
                    "required": param.get("required", False),
                    "schema": {"type": param.get("type", "string")},
                    "description": param.get("description", ""),
                }
            )
        return parameters

    def _build_responses(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Build OpenAPI responses"""
        resp = {}
        for code, data in responses.items():
            resp[code] = {
                "description": data.get("description", ""),
                "content": {"application/json": {"schema": data.get("schema", {"type": "object"})}},
            }
        if not resp:
            resp["200"] = {"description": "Success"}
        return resp

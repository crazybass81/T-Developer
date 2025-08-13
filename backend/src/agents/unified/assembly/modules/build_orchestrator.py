"""Build Orchestrator Module for Assembly Agent
Orchestrates build processes across different frameworks and environments
"""

import asyncio
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class BuildArtifact:
    name: str
    path: str
    size: int
    build_time: float
    checksum: str


@dataclass
class BuildResult:
    success: bool
    build_artifacts: Dict[str, str]
    build_time: float
    build_logs: List[str]
    artifacts: List[BuildArtifact]
    error: str = ""


class BuildOrchestrator:
    """Advanced build orchestration system"""

    def __init__(self):
        self.version = "1.0.0"

        self.build_commands = {
            "react": ["npm install", "npm run build"],
            "vue": ["npm install", "npm run build"],
            "angular": ["npm install", "ng build --prod"],
            "express": ["npm install", "npm run build"],
            "fastapi": ["pip install -r requirements.txt", "python -m build"],
            "django": [
                "pip install -r requirements.txt",
                "python manage.py collectstatic --noinput",
            ],
            "flask": ["pip install -r requirements.txt", "python -m build"],
        }

    async def orchestrate_build(
        self,
        validated_files: Dict[str, str],
        context: Dict[str, Any],
        workspace_path: str,
    ) -> BuildResult:
        """Orchestrate the build process"""

        start_time = datetime.now()
        build_logs = []

        try:
            framework = context.get("framework", "react")
            project_path = os.path.join(
                workspace_path, "source", context.get("project_name", "project")
            )

            # Write files to project directory
            for file_path, content in validated_files.items():
                full_path = os.path.join(project_path, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)

            # Execute build commands
            commands = self.build_commands.get(framework, ['echo "No build commands defined"'])

            for command in commands:
                build_logs.append(f"Executing: {command}")
                result = await self._execute_command(command, project_path)
                build_logs.extend(result["output"])

                if result["return_code"] != 0:
                    return BuildResult(
                        success=False,
                        build_artifacts={},
                        build_time=0,
                        build_logs=build_logs,
                        artifacts=[],
                        error=f"Build command failed: {command}",
                    )

            # Collect build artifacts
            artifacts = await self._collect_build_artifacts(project_path, framework)

            build_time = (datetime.now() - start_time).total_seconds()

            # Create artifact dictionary
            build_artifacts = {}
            for artifact in artifacts:
                with open(artifact.path, "r", encoding="utf-8", errors="ignore") as f:
                    build_artifacts[artifact.name] = f.read()

            return BuildResult(
                success=True,
                build_artifacts=build_artifacts,
                build_time=build_time,
                build_logs=build_logs,
                artifacts=artifacts,
            )

        except Exception as e:
            return BuildResult(
                success=False,
                build_artifacts={},
                build_time=0,
                build_logs=build_logs,
                artifacts=[],
                error=str(e),
            )

    async def _execute_command(self, command: str, cwd: str) -> Dict[str, Any]:
        """Execute a shell command"""

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
            )

            stdout, stderr = await process.communicate()

            output = []
            if stdout:
                output.extend(stdout.decode().split("\n"))
            if stderr:
                output.extend(stderr.decode().split("\n"))

            return {
                "return_code": process.returncode,
                "output": [line for line in output if line.strip()],
            }

        except Exception as e:
            return {"return_code": 1, "output": [f"Command execution failed: {str(e)}"]}

    async def _collect_build_artifacts(
        self, project_path: str, framework: str
    ) -> List[BuildArtifact]:
        """Collect build artifacts"""

        artifacts = []

        # Framework-specific artifact paths
        artifact_paths = {
            "react": ["build/", "dist/"],
            "vue": ["dist/"],
            "angular": ["dist/"],
            "express": ["dist/", "build/"],
            "fastapi": ["dist/"],
            "django": ["staticfiles/", "static/"],
            "flask": ["dist/", "static/"],
        }

        paths_to_check = artifact_paths.get(framework, ["dist/", "build/"])

        for artifact_dir in paths_to_check:
            full_path = os.path.join(project_path, artifact_dir)
            if os.path.exists(full_path):
                for root, dirs, files in os.walk(full_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if os.path.exists(file_path):
                            size = os.path.getsize(file_path)
                            rel_path = os.path.relpath(file_path, project_path)

                            artifacts.append(
                                BuildArtifact(
                                    name=rel_path,
                                    path=file_path,
                                    size=size,
                                    build_time=0,
                                    checksum="abc123",  # Simplified
                                )
                            )

        return artifacts

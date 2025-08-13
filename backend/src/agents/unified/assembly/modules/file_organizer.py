"""
File Organizer Module for Assembly Agent
Organizes and structures project files for optimal assembly
"""

from typing import Dict, List, Any, Optional, Tuple, Set
import asyncio
import os
import shutil
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import mimetypes
import json


class FileCategory(Enum):
    SOURCE_CODE = "source_code"
    CONFIGURATION = "configuration"
    DOCUMENTATION = "documentation"
    ASSETS = "assets"
    TESTS = "tests"
    BUILD_SCRIPTS = "build_scripts"
    DEPLOYMENT = "deployment"
    DEPENDENCIES = "dependencies"


@dataclass
class OrganizedFile:
    original_path: str
    organized_path: str
    category: FileCategory
    size: int
    checksum: str
    dependencies: List[str]
    metadata: Dict[str, Any]


@dataclass
class OrganizationResult:
    success: bool
    organized_files: Dict[str, OrganizedFile]
    directory_structure: Dict[str, List[str]]
    total_files: int
    total_size: int
    categories_distribution: Dict[str, int]
    processing_time: float
    error: str = ""


class FileOrganizer:
    """Advanced file organization system for project assembly"""

    def __init__(self):
        self.version = "1.0.0"

        # File organization patterns by framework
        self.framework_structures = {
            "react": {
                "src/": [
                    "components/",
                    "pages/",
                    "hooks/",
                    "utils/",
                    "services/",
                    "types/",
                    "assets/",
                ],
                "public/": ["index.html", "favicon.ico", "manifest.json"],
                "tests/": ["__tests__/", "unit/", "integration/", "e2e/"],
                "docs/": ["README.md", "API.md", "CONTRIBUTING.md"],
                "config/": ["webpack.config.js", "babel.config.js", "jest.config.js"],
                ".": ["package.json", ".gitignore", ".env.example", "tsconfig.json"],
            },
            "vue": {
                "src/": [
                    "components/",
                    "views/",
                    "composables/",
                    "utils/",
                    "services/",
                    "types/",
                    "assets/",
                ],
                "public/": ["index.html", "favicon.ico"],
                "tests/": ["unit/", "e2e/"],
                "docs/": ["README.md"],
                "config/": ["vite.config.ts", "vitest.config.ts"],
                ".": ["package.json", ".gitignore", ".env.example"],
            },
            "angular": {
                "src/": ["app/", "assets/", "environments/"],
                "src/app/": [
                    "components/",
                    "services/",
                    "models/",
                    "guards/",
                    "interceptors/",
                ],
                "tests/": ["unit/", "e2e/"],
                "docs/": ["README.md"],
                ".": ["package.json", "angular.json", "tsconfig.json", ".gitignore"],
            },
            "express": {
                "src/": [
                    "controllers/",
                    "services/",
                    "models/",
                    "middleware/",
                    "routes/",
                    "types/",
                    "utils/",
                ],
                "tests/": ["unit/", "integration/", "e2e/"],
                "docs/": ["README.md", "API.md"],
                "config/": ["database.js", "server.js"],
                ".": ["package.json", ".gitignore", ".env.example", "tsconfig.json"],
            },
            "fastapi": {
                "src/": [
                    "routers/",
                    "services/",
                    "models/",
                    "schemas/",
                    "core/",
                    "utils/",
                ],
                "tests/": ["unit/", "integration/", "e2e/"],
                "docs/": ["README.md", "API.md"],
                "config/": ["settings.py", "database.py"],
                ".": [
                    "requirements.txt",
                    ".gitignore",
                    ".env.example",
                    "pyproject.toml",
                ],
            },
            "django": {
                "src/": ["apps/", "core/", "templates/", "static/"],
                "tests/": ["unit/", "integration/"],
                "docs/": ["README.md"],
                "config/": ["settings/", "urls.py", "wsgi.py"],
                ".": ["requirements.txt", "manage.py", ".gitignore", ".env.example"],
            },
            "flask": {
                "src/": [
                    "views/",
                    "models/",
                    "services/",
                    "utils/",
                    "templates/",
                    "static/",
                ],
                "tests/": ["unit/", "integration/"],
                "docs/": ["README.md"],
                "config/": ["config.py", "wsgi.py"],
                ".": ["requirements.txt", "app.py", ".gitignore", ".env.example"],
            },
        }

        # File categorization rules
        self.categorization_rules = {
            FileCategory.SOURCE_CODE: {
                "extensions": [
                    ".js",
                    ".jsx",
                    ".ts",
                    ".tsx",
                    ".py",
                    ".java",
                    ".go",
                    ".rs",
                    ".php",
                    ".rb",
                ],
                "patterns": ["src/", "app/", "lib/"],
                "exclude_patterns": ["test", "spec", "__tests__"],
            },
            FileCategory.CONFIGURATION: {
                "extensions": [".json", ".yaml", ".yml", ".toml", ".ini", ".conf"],
                "patterns": [
                    "config/",
                    ".env",
                    "package.json",
                    "requirements.txt",
                    "Dockerfile",
                ],
                "filenames": [
                    "webpack.config.js",
                    "babel.config.js",
                    "jest.config.js",
                    "angular.json",
                ],
            },
            FileCategory.DOCUMENTATION: {
                "extensions": [".md", ".txt", ".rst", ".adoc"],
                "patterns": ["docs/", "README", "CHANGELOG", "LICENSE", "CONTRIBUTING"],
                "filenames": [
                    "README.md",
                    "CHANGELOG.md",
                    "LICENSE",
                    "CONTRIBUTING.md",
                ],
            },
            FileCategory.ASSETS: {
                "extensions": [
                    ".png",
                    ".jpg",
                    ".jpeg",
                    ".gif",
                    ".svg",
                    ".ico",
                    ".css",
                    ".scss",
                    ".less",
                ],
                "patterns": ["assets/", "static/", "public/", "images/", "styles/"],
            },
            FileCategory.TESTS: {
                "extensions": [
                    ".test.js",
                    ".test.ts",
                    ".spec.js",
                    ".spec.ts",
                    ".test.py",
                ],
                "patterns": [
                    "test/",
                    "tests/",
                    "__tests__/",
                    "spec/",
                    "cypress/",
                    "e2e/",
                ],
            },
            FileCategory.BUILD_SCRIPTS: {
                "extensions": [".sh", ".bat", ".ps1"],
                "patterns": ["scripts/", "build/"],
                "filenames": ["Makefile", "build.sh", "deploy.sh"],
            },
            FileCategory.DEPLOYMENT: {
                "patterns": [
                    "docker",
                    "k8s/",
                    "kubernetes/",
                    ".github/workflows/",
                    "deployment/",
                ],
                "filenames": [
                    "Dockerfile",
                    "docker-compose.yml",
                    "netlify.toml",
                    "vercel.json",
                ],
            },
            FileCategory.DEPENDENCIES: {
                "filenames": [
                    "package-lock.json",
                    "yarn.lock",
                    "requirements.txt",
                    "Pipfile",
                    "go.mod",
                    "Cargo.toml",
                ]
            },
        }

        # Directory priority for organization
        self.directory_priorities = {
            "src": 1,
            "app": 1,
            "lib": 2,
            "public": 3,
            "assets": 4,
            "static": 4,
            "tests": 5,
            "docs": 6,
            "config": 7,
            "scripts": 8,
            "build": 9,
            ".": 10,  # Root files
        }

    async def organize_project_files(
        self,
        generated_files: Dict[str, str],
        context: Dict[str, Any],
        workspace_path: str,
    ) -> OrganizationResult:
        """Organize project files according to framework conventions"""

        start_time = datetime.now()

        try:
            framework = context.get("framework", "react")
            project_name = context.get("project_name", "generated-project")

            # Create project directory structure
            project_path = os.path.join(workspace_path, "source", project_name)
            await self._create_directory_structure(project_path, framework)

            # Categorize files
            categorized_files = await self._categorize_files(generated_files)

            # Organize files by category and framework conventions
            organized_files = {}
            total_size = 0

            for file_path, file_content in generated_files.items():
                category = categorized_files.get(file_path, FileCategory.SOURCE_CODE)

                # Determine organized path
                organized_path = await self._determine_organized_path(
                    file_path, category, framework, project_path
                )

                # Calculate file metadata
                file_size = len(file_content.encode("utf-8"))
                file_checksum = self._calculate_checksum(file_content)
                dependencies = await self._extract_dependencies(file_content, file_path)

                # Create organized file entry
                organized_file = OrganizedFile(
                    original_path=file_path,
                    organized_path=organized_path,
                    category=category,
                    size=file_size,
                    checksum=file_checksum,
                    dependencies=dependencies,
                    metadata={
                        "mime_type": mimetypes.guess_type(file_path)[0] or "text/plain",
                        "framework": framework,
                        "last_modified": datetime.now().isoformat(),
                    },
                )

                organized_files[file_path] = organized_file
                total_size += file_size

                # Write file to organized location
                await self._write_organized_file(organized_path, file_content)

            # Generate directory structure map
            directory_structure = await self._generate_directory_structure(
                organized_files
            )

            # Calculate categories distribution
            categories_distribution = self._calculate_categories_distribution(
                organized_files
            )

            # Create organization summary
            await self._create_organization_summary(
                project_path, organized_files, context
            )

            processing_time = (datetime.now() - start_time).total_seconds()

            return OrganizationResult(
                success=True,
                organized_files=organized_files,
                directory_structure=directory_structure,
                total_files=len(organized_files),
                total_size=total_size,
                categories_distribution=categories_distribution,
                processing_time=processing_time,
            )

        except Exception as e:
            return OrganizationResult(
                success=False,
                organized_files={},
                directory_structure={},
                total_files=0,
                total_size=0,
                categories_distribution={},
                processing_time=(datetime.now() - start_time).total_seconds(),
                error=str(e),
            )

    async def _create_directory_structure(self, project_path: str, framework: str):
        """Create standard directory structure for framework"""

        structure = self.framework_structures.get(
            framework, self.framework_structures["react"]
        )

        for directory, subdirs in structure.items():
            dir_path = os.path.join(project_path, directory)
            os.makedirs(dir_path, exist_ok=True)

            if isinstance(subdirs, list):
                for subdir in subdirs:
                    if subdir.endswith("/"):  # Directory
                        subdir_path = os.path.join(dir_path, subdir.rstrip("/"))
                        os.makedirs(subdir_path, exist_ok=True)

    async def _categorize_files(
        self, generated_files: Dict[str, str]
    ) -> Dict[str, FileCategory]:
        """Categorize files based on patterns and extensions"""

        categorized = {}

        for file_path, content in generated_files.items():
            category = self._determine_file_category(file_path, content)
            categorized[file_path] = category

        return categorized

    def _determine_file_category(self, file_path: str, content: str) -> FileCategory:
        """Determine the category of a single file"""

        file_lower = file_path.lower()
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_path)[1]

        # Check each category's rules
        for category, rules in self.categorization_rules.items():
            # Check filenames
            if "filenames" in rules:
                for filename in rules["filenames"]:
                    if filename.lower() in file_name.lower():
                        return category

            # Check extensions
            if "extensions" in rules:
                for ext in rules["extensions"]:
                    if file_lower.endswith(ext.lower()):
                        # Check exclude patterns for source code
                        if (
                            category == FileCategory.SOURCE_CODE
                            and "exclude_patterns" in rules
                        ):
                            if any(
                                pattern in file_lower
                                for pattern in rules["exclude_patterns"]
                            ):
                                continue
                        return category

            # Check patterns
            if "patterns" in rules:
                for pattern in rules["patterns"]:
                    if pattern.lower() in file_lower:
                        return category

        # Default to source code
        return FileCategory.SOURCE_CODE

    async def _determine_organized_path(
        self,
        original_path: str,
        category: FileCategory,
        framework: str,
        project_path: str,
    ) -> str:
        """Determine the organized path for a file"""

        file_name = os.path.basename(original_path)

        # Category-based organization
        category_paths = {
            FileCategory.SOURCE_CODE: "src",
            FileCategory.CONFIGURATION: "",  # Root or config/
            FileCategory.DOCUMENTATION: "docs",
            FileCategory.ASSETS: "src/assets",
            FileCategory.TESTS: "tests",
            FileCategory.BUILD_SCRIPTS: "scripts",
            FileCategory.DEPLOYMENT: "",  # Root
            FileCategory.DEPENDENCIES: "",  # Root
        }

        base_path = category_paths.get(category, "src")

        # Framework-specific adjustments
        if framework == "angular" and category == FileCategory.ASSETS:
            base_path = "src/assets"
        elif (
            framework in ["fastapi", "django", "flask"]
            and category == FileCategory.ASSETS
        ):
            base_path = "static" if framework == "django" else "src/static"

        # Handle special files
        if file_name in [
            "package.json",
            "requirements.txt",
            ".gitignore",
            "Dockerfile",
        ]:
            base_path = ""  # Root
        elif file_name.startswith(".env"):
            base_path = ""  # Root
        elif (
            "config" in original_path.lower() and category == FileCategory.CONFIGURATION
        ):
            base_path = "config"

        # Construct full organized path
        if base_path:
            organized_path = os.path.join(project_path, base_path, file_name)
        else:
            organized_path = os.path.join(project_path, file_name)

        # Handle subdirectories from original path
        original_dir = os.path.dirname(original_path)
        if original_dir and original_dir != ".":
            # Preserve meaningful subdirectory structure
            subdirs = self._extract_meaningful_subdirs(original_dir, category)
            if subdirs:
                if base_path:
                    organized_path = os.path.join(
                        project_path, base_path, subdirs, file_name
                    )
                else:
                    organized_path = os.path.join(project_path, subdirs, file_name)

        return organized_path

    def _extract_meaningful_subdirs(
        self, original_dir: str, category: FileCategory
    ) -> str:
        """Extract meaningful subdirectory structure"""

        # Remove common prefixes that aren't meaningful in organized structure
        ignore_prefixes = ["src/", "app/", "lib/", "generated/"]

        meaningful_dir = original_dir
        for prefix in ignore_prefixes:
            if meaningful_dir.startswith(prefix):
                meaningful_dir = meaningful_dir[len(prefix) :]
                break

        # Keep only the last 2 levels of nesting to avoid overly deep structures
        parts = meaningful_dir.split("/")
        if len(parts) > 2:
            meaningful_dir = "/".join(parts[-2:])

        return meaningful_dir

    async def _write_organized_file(self, organized_path: str, content: str):
        """Write file to organized location"""

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(organized_path), exist_ok=True)

        # Write file content
        with open(organized_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _calculate_checksum(self, content: str) -> str:
        """Calculate file content checksum"""

        import hashlib

        return hashlib.md5(content.encode("utf-8")).hexdigest()

    async def _extract_dependencies(self, content: str, file_path: str) -> List[str]:
        """Extract dependencies from file content"""

        dependencies = []

        # JavaScript/TypeScript imports
        import_patterns = [
            r'import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'require\([\'"]([^\'"]+)[\'"]\)',
            r'import\([\'"]([^\'"]+)[\'"]\)',
        ]

        # Python imports
        python_import_patterns = [
            r"from\s+([^\s]+)\s+import",
            r"import\s+([^\s,]+)",
        ]

        import re

        # Extract JavaScript/TypeScript dependencies
        if file_path.endswith((".js", ".jsx", ".ts", ".tsx")):
            for pattern in import_patterns:
                matches = re.findall(pattern, content)
                dependencies.extend(matches)

        # Extract Python dependencies
        elif file_path.endswith(".py"):
            for pattern in python_import_patterns:
                matches = re.findall(pattern, content)
                dependencies.extend(matches)

        # Clean up dependencies (remove relative paths, keep only package names)
        cleaned_dependencies = []
        for dep in dependencies:
            if not dep.startswith(".") and not dep.startswith("/"):
                # Extract package name (first part before /)
                package_name = dep.split("/")[0]
                if package_name not in cleaned_dependencies:
                    cleaned_dependencies.append(package_name)

        return cleaned_dependencies

    async def _generate_directory_structure(
        self, organized_files: Dict[str, OrganizedFile]
    ) -> Dict[str, List[str]]:
        """Generate directory structure map"""

        structure = {}

        for file_path, organized_file in organized_files.items():
            directory = os.path.dirname(organized_file.organized_path)
            file_name = os.path.basename(organized_file.organized_path)

            if directory not in structure:
                structure[directory] = []

            structure[directory].append(file_name)

        # Sort files in each directory
        for directory in structure:
            structure[directory].sort()

        return structure

    def _calculate_categories_distribution(
        self, organized_files: Dict[str, OrganizedFile]
    ) -> Dict[str, int]:
        """Calculate distribution of files by category"""

        distribution = {}

        for organized_file in organized_files.values():
            category = organized_file.category.value
            distribution[category] = distribution.get(category, 0) + 1

        return distribution

    async def _create_organization_summary(
        self,
        project_path: str,
        organized_files: Dict[str, OrganizedFile],
        context: Dict[str, Any],
    ):
        """Create organization summary file"""

        summary = {
            "organization_info": {
                "project_name": context.get("project_name", "generated-project"),
                "framework": context.get("framework", "react"),
                "organized_at": datetime.now().isoformat(),
                "total_files": len(organized_files),
                "organizer_version": self.version,
            },
            "file_categories": {},
            "directory_structure": {},
            "file_details": [],
        }

        # Add category distribution
        for organized_file in organized_files.values():
            category = organized_file.category.value
            if category not in summary["file_categories"]:
                summary["file_categories"][category] = {"count": 0, "total_size": 0}

            summary["file_categories"][category]["count"] += 1
            summary["file_categories"][category]["total_size"] += organized_file.size

        # Add directory structure
        directories = set()
        for organized_file in organized_files.values():
            directories.add(os.path.dirname(organized_file.organized_path))

        for directory in sorted(directories):
            files_in_dir = [
                os.path.basename(f.organized_path)
                for f in organized_files.values()
                if os.path.dirname(f.organized_path) == directory
            ]
            summary["directory_structure"][directory] = sorted(files_in_dir)

        # Add file details (subset for large projects)
        file_details = [
            {
                "original_path": f.original_path,
                "organized_path": f.organized_path,
                "category": f.category.value,
                "size": f.size,
                "dependencies": f.dependencies,
            }
            for f in list(organized_files.values())[:100]  # Limit to first 100 files
        ]
        summary["file_details"] = file_details

        # Write summary file
        summary_path = os.path.join(project_path, ".organization-summary.json")
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

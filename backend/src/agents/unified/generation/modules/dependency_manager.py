"""
Dependency Manager Module for Generation Agent
Manages project dependencies, version resolution, and compatibility checking
"""

from typing import Dict, List, Any, Optional, Tuple, Set
import asyncio
import json
import re
import semver
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class DependencyType(Enum):
    PRODUCTION = "production"
    DEVELOPMENT = "development"
    PEER = "peer"
    OPTIONAL = "optional"


class PackageManager(Enum):
    NPM = "npm"
    YARN = "yarn"
    PNPM = "pnpm"
    PIP = "pip"
    PIPENV = "pipenv"
    POETRY = "poetry"
    MAVEN = "maven"
    GRADLE = "gradle"
    GO_MOD = "go_mod"
    CARGO = "cargo"


@dataclass
class Dependency:
    name: str
    version: str
    dependency_type: DependencyType
    description: str = ""
    repository: str = ""
    license: str = ""
    size: int = 0
    dependencies: List[str] = None
    dev_dependencies: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.dev_dependencies is None:
            self.dev_dependencies = []


@dataclass
class DependencyResult:
    success: bool
    dependencies: Dict[str, Dict[str, Any]]
    conflicts: List[Dict[str, Any]]
    vulnerabilities: List[Dict[str, Any]]
    recommendations: List[str]
    package_files: Dict[str, str]
    total_size: int
    processing_time: float
    error: str = ""


class DependencyManager:
    """Advanced dependency management system"""

    def __init__(self):
        self.version = "1.0.0"

        # Framework dependency templates
        self.framework_dependencies = {
            "react": {
                "production": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0",
                    "react-router-dom": "^6.8.0",
                },
                "development": {
                    "@vitejs/plugin-react": "^3.1.0",
                    "vite": "^4.1.0",
                    "@types/react": "^18.0.27",
                    "@types/react-dom": "^18.0.10",
                    "typescript": "^4.9.4",
                    "eslint": "^8.34.0",
                    "prettier": "^2.8.4",
                },
            },
            "vue": {
                "production": {
                    "vue": "^3.2.47",
                    "vue-router": "^4.1.6",
                    "pinia": "^2.0.32",
                },
                "development": {
                    "@vitejs/plugin-vue": "^4.0.0",
                    "vite": "^4.1.0",
                    "typescript": "^4.9.4",
                    "@vue/tsconfig": "^0.1.3",
                    "eslint": "^8.34.0",
                    "prettier": "^2.8.4",
                },
            },
            "angular": {
                "production": {
                    "@angular/animations": "^15.1.0",
                    "@angular/common": "^15.1.0",
                    "@angular/compiler": "^15.1.0",
                    "@angular/core": "^15.1.0",
                    "@angular/forms": "^15.1.0",
                    "@angular/platform-browser": "^15.1.0",
                    "@angular/platform-browser-dynamic": "^15.1.0",
                    "@angular/router": "^15.1.0",
                    "rxjs": "~7.8.0",
                    "tslib": "^2.3.0",
                    "zone.js": "~0.12.0",
                },
                "development": {
                    "@angular-devkit/build-angular": "^15.1.0",
                    "@angular/cli": "~15.1.0",
                    "@angular/compiler-cli": "^15.1.0",
                    "@types/jasmine": "~4.3.0",
                    "jasmine-core": "~4.5.0",
                    "karma": "~6.4.0",
                    "karma-chrome-launcher": "~3.1.0",
                    "karma-coverage": "~2.2.0",
                    "karma-jasmine": "~5.1.0",
                    "karma-jasmine-html-reporter": "~2.0.0",
                    "typescript": "~4.9.4",
                },
            },
            "express": {
                "production": {
                    "express": "^4.18.2",
                    "cors": "^2.8.5",
                    "helmet": "^6.0.1",
                    "morgan": "^1.10.0",
                    "dotenv": "^16.0.3",
                },
                "development": {
                    "@types/node": "^18.14.0",
                    "@types/express": "^4.17.17",
                    "@types/cors": "^2.8.13",
                    "@types/morgan": "^1.9.4",
                    "typescript": "^4.9.4",
                    "ts-node": "^10.9.1",
                    "nodemon": "^2.0.20",
                    "jest": "^29.4.3",
                    "supertest": "^6.3.3",
                },
            },
            "fastapi": {
                "production": [
                    "fastapi==0.95.0",
                    "uvicorn[standard]==0.20.0",
                    "pydantic==1.10.5",
                    "python-multipart==0.0.5",
                    "python-jose[cryptography]==3.3.0",
                ],
                "development": [
                    "pytest==7.2.1",
                    "pytest-asyncio==0.20.3",
                    "httpx==0.23.3",
                    "black==23.1.0",
                    "flake8==6.0.0",
                    "mypy==1.0.1",
                ],
            },
            "django": {
                "production": [
                    "Django==4.1.6",
                    "djangorestframework==3.14.0",
                    "django-cors-headers==3.13.0",
                    "celery==5.2.7",
                    "redis==4.5.1",
                    "psycopg2-binary==2.9.5",
                ],
                "development": [
                    "pytest-django==4.5.2",
                    "factory-boy==3.2.1",
                    "django-debug-toolbar==3.2.4",
                    "black==23.1.0",
                    "flake8==6.0.0",
                    "coverage==7.1.0",
                ],
            },
            "flask": {
                "production": [
                    "Flask==2.2.3",
                    "Flask-SQLAlchemy==3.0.3",
                    "Flask-Migrate==4.0.4",
                    "Flask-JWT-Extended==4.4.4",
                    "Flask-CORS==3.0.10",
                    "gunicorn==20.1.0",
                ],
                "development": [
                    "pytest==7.2.1",
                    "pytest-flask==1.2.0",
                    "black==23.1.0",
                    "flake8==6.0.0",
                    "coverage==7.1.0",
                ],
            },
        }

        # Component-specific dependencies
        self.component_dependencies = {
            "authentication": {
                "react": ["@auth0/auth0-react", "firebase"],
                "vue": ["@auth0/auth0-vue", "firebase"],
                "express": ["passport", "jsonwebtoken", "bcryptjs"],
                "fastapi": ["python-jose", "passlib", "bcrypt"],
                "django": ["django-allauth", "djangorestframework-simplejwt"],
            },
            "database": {
                "express": ["mongoose", "sequelize", "typeorm"],
                "fastapi": ["sqlalchemy", "databases", "asyncpg"],
                "django": ["psycopg2-binary", "pymongo"],
                "flask": ["Flask-SQLAlchemy", "pymongo"],
            },
            "ui_library": {
                "react": ["@mui/material", "antd", "chakra-ui", "react-bootstrap"],
                "vue": ["vuetify", "quasar", "ant-design-vue", "element-plus"],
                "angular": ["@angular/material", "ng-bootstrap", "primeng"],
            },
            "state_management": {
                "react": ["redux", "@reduxjs/toolkit", "zustand", "jotai"],
                "vue": ["pinia", "vuex"],
                "angular": ["@ngrx/store", "@ngrx/effects"],
            },
            "testing": {
                "react": ["@testing-library/react", "jest", "cypress"],
                "vue": ["@vue/test-utils", "jest", "cypress"],
                "angular": ["jasmine", "karma", "protractor"],
                "express": ["jest", "supertest", "mocha"],
                "fastapi": ["pytest", "pytest-asyncio", "httpx"],
                "django": ["pytest-django", "factory-boy"],
            },
        }

        # Vulnerability database (simplified)
        self.vulnerability_db = {
            "minimist": ["<1.2.6"],
            "lodash": ["<4.17.21"],
            "axios": ["<0.21.2"],
            "node-fetch": ["<2.6.7"],
            "tar": ["<6.1.9"],
        }

        # Popular package alternatives
        self.package_alternatives = {
            "moment": ["dayjs", "date-fns"],
            "request": ["axios", "node-fetch"],
            "underscore": ["lodash", "ramda"],
            "bower": ["npm", "yarn"],
        }

    async def resolve_dependencies(
        self, components: List[Dict[str, Any]], framework: str, language: str
    ) -> DependencyResult:
        """Main dependency resolution method"""

        start_time = datetime.now()

        try:
            # Get base dependencies for framework
            base_deps = self._get_base_dependencies(framework, language)

            # Add component-specific dependencies
            component_deps = await self._resolve_component_dependencies(
                components, framework, language
            )

            # Merge all dependencies
            all_dependencies = self._merge_dependencies(base_deps, component_deps)

            # Resolve version conflicts
            resolved_deps = await self._resolve_version_conflicts(all_dependencies)

            # Check for vulnerabilities
            vulnerabilities = await self._check_vulnerabilities(resolved_deps)

            # Generate package files
            package_files = await self._generate_package_files(
                resolved_deps, framework, language
            )

            # Calculate total size
            total_size = await self._calculate_total_size(resolved_deps)

            # Generate recommendations
            recommendations = await self._generate_recommendations(
                resolved_deps, components, framework
            )

            processing_time = (datetime.now() - start_time).total_seconds()

            return DependencyResult(
                success=True,
                dependencies=resolved_deps,
                conflicts=[],
                vulnerabilities=vulnerabilities,
                recommendations=recommendations,
                package_files=package_files,
                total_size=total_size,
                processing_time=processing_time,
            )

        except Exception as e:
            return DependencyResult(
                success=False,
                dependencies={},
                conflicts=[],
                vulnerabilities=[],
                recommendations=[],
                package_files={},
                total_size=0,
                processing_time=(datetime.now() - start_time).total_seconds(),
                error=str(e),
            )

    def _get_base_dependencies(
        self, framework: str, language: str
    ) -> Dict[str, Dict[str, Any]]:
        """Get base dependencies for framework and language"""

        if framework in self.framework_dependencies:
            framework_deps = self.framework_dependencies[framework]

            dependencies = {}

            # Add production dependencies
            if "production" in framework_deps:
                for name, version in framework_deps["production"].items():
                    dependencies[name] = {
                        "version": version,
                        "type": DependencyType.PRODUCTION.value,
                        "source": "framework_base",
                    }

            # Add development dependencies
            if "development" in framework_deps:
                for name, version in framework_deps["development"].items():
                    dependencies[name] = {
                        "version": version,
                        "type": DependencyType.DEVELOPMENT.value,
                        "source": "framework_base",
                    }

            return dependencies

        return {}

    async def _resolve_component_dependencies(
        self, components: List[Dict[str, Any]], framework: str, language: str
    ) -> Dict[str, Dict[str, Any]]:
        """Resolve dependencies for selected components"""

        component_deps = {}

        for component in components:
            component_type = component.get("type", "")
            component_category = component.get("category", "")
            component_tags = component.get("tags", [])

            # Map component to dependency categories
            dep_categories = self._map_component_to_dependencies(
                component_type, component_category, component_tags
            )

            # Add dependencies for each category
            for category in dep_categories:
                if category in self.component_dependencies:
                    category_deps = self.component_dependencies[category]

                    if framework in category_deps:
                        for dep_name in category_deps[framework]:
                            # Get latest version (simplified)
                            latest_version = await self._get_latest_version(
                                dep_name, language
                            )

                            component_deps[dep_name] = {
                                "version": latest_version,
                                "type": DependencyType.PRODUCTION.value,
                                "source": f"component_{category}",
                                "component": component.get("name", ""),
                            }

        return component_deps

    def _map_component_to_dependencies(
        self, component_type: str, category: str, tags: List[str]
    ) -> List[str]:
        """Map component characteristics to dependency categories"""

        dependency_categories = []

        # Map by type
        type_mapping = {
            "auth": ["authentication"],
            "database": ["database"],
            "ui": ["ui_library"],
            "state": ["state_management"],
            "test": ["testing"],
        }

        if component_type.lower() in type_mapping:
            dependency_categories.extend(type_mapping[component_type.lower()])

        # Map by category
        category_mapping = {
            "authentication": ["authentication"],
            "database": ["database"],
            "ui": ["ui_library"],
            "state management": ["state_management"],
            "testing": ["testing"],
        }

        if category.lower() in category_mapping:
            dependency_categories.extend(category_mapping[category.lower()])

        # Map by tags
        for tag in tags:
            tag_lower = tag.lower()
            if tag_lower in ["auth", "authentication"]:
                dependency_categories.append("authentication")
            elif tag_lower in ["db", "database"]:
                dependency_categories.append("database")
            elif tag_lower in ["ui", "component"]:
                dependency_categories.append("ui_library")
            elif tag_lower in ["state", "store"]:
                dependency_categories.append("state_management")
            elif tag_lower in ["test", "testing"]:
                dependency_categories.append("testing")

        return list(set(dependency_categories))  # Remove duplicates

    async def _get_latest_version(self, package_name: str, language: str) -> str:
        """Get latest version of a package (simplified implementation)"""

        # In production, this would query actual package registries
        # For now, return reasonable default versions

        default_versions = {
            # JavaScript/TypeScript packages
            "@auth0/auth0-react": "^2.0.1",
            "firebase": "^9.17.1",
            "@mui/material": "^5.11.10",
            "antd": "^5.2.1",
            "redux": "^4.2.1",
            "@reduxjs/toolkit": "^1.9.3",
            "zustand": "^4.3.6",
            "mongoose": "^6.9.1",
            "sequelize": "^6.28.0",
            "typeorm": "^0.3.12",
            "@testing-library/react": "^14.0.0",
            "cypress": "^12.6.0",
            # Python packages
            "sqlalchemy": "1.4.46",
            "databases": "0.7.0",
            "asyncpg": "0.27.0",
            "python-jose": "3.3.0",
            "passlib": "1.7.4",
            "bcrypt": "4.0.1",
            "pytest": "7.2.1",
            "httpx": "0.23.3",
        }

        return default_versions.get(package_name, "^1.0.0")

    def _merge_dependencies(
        self,
        base_deps: Dict[str, Dict[str, Any]],
        component_deps: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Dict[str, Any]]:
        """Merge base and component dependencies"""

        merged = base_deps.copy()

        for name, dep_info in component_deps.items():
            if name in merged:
                # Handle version conflicts
                existing_version = merged[name]["version"]
                new_version = dep_info["version"]

                # Use higher version (simplified)
                if self._compare_versions(new_version, existing_version) > 0:
                    merged[name].update(dep_info)
                    merged[name]["conflict_resolved"] = True
            else:
                merged[name] = dep_info

        return merged

    async def _resolve_version_conflicts(
        self, dependencies: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Resolve version conflicts between dependencies"""

        # Simplified conflict resolution
        # In production, this would use advanced conflict resolution algorithms

        resolved = dependencies.copy()

        # Group dependencies by package name
        package_groups = {}
        for name, dep_info in dependencies.items():
            base_name = name.split("@")[0] if "@" in name else name
            if base_name not in package_groups:
                package_groups[base_name] = []
            package_groups[base_name].append((name, dep_info))

        # Resolve conflicts within groups
        for base_name, deps in package_groups.items():
            if len(deps) > 1:
                # Use the highest version
                highest_version_dep = max(
                    deps, key=lambda x: self._version_to_number(x[1]["version"])
                )

                # Keep only the highest version
                for name, _ in deps:
                    if name != highest_version_dep[0]:
                        resolved.pop(name, None)

        return resolved

    async def _check_vulnerabilities(
        self, dependencies: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Check for known vulnerabilities"""

        vulnerabilities = []

        for name, dep_info in dependencies.items():
            if name in self.vulnerability_db:
                vulnerable_versions = self.vulnerability_db[name]
                current_version = self._clean_version(dep_info["version"])

                for vuln_version in vulnerable_versions:
                    if self._version_matches_range(current_version, vuln_version):
                        vulnerabilities.append(
                            {
                                "package": name,
                                "current_version": current_version,
                                "vulnerable_range": vuln_version,
                                "severity": "medium",  # Simplified
                                "description": f"Known vulnerability in {name} {vuln_version}",
                                "recommendation": "Update to latest version",
                            }
                        )

        return vulnerabilities

    async def _generate_package_files(
        self, dependencies: Dict[str, Dict[str, Any]], framework: str, language: str
    ) -> Dict[str, str]:
        """Generate package configuration files"""

        package_files = {}

        if language in ["javascript", "typescript"]:
            # Generate package.json
            package_json = await self._generate_package_json(dependencies, framework)
            package_files["package.json"] = package_json

            # Generate yarn.lock or package-lock.json (placeholder)
            package_files["yarn.lock"] = "# Yarn lockfile placeholder"

        elif language == "python":
            # Generate requirements.txt
            requirements_txt = await self._generate_requirements_txt(dependencies)
            package_files["requirements.txt"] = requirements_txt

            # Generate pyproject.toml (modern Python)
            pyproject_toml = await self._generate_pyproject_toml(
                dependencies, framework
            )
            package_files["pyproject.toml"] = pyproject_toml

        elif language == "java":
            # Generate pom.xml for Maven
            pom_xml = await self._generate_pom_xml(dependencies, framework)
            package_files["pom.xml"] = pom_xml

        elif language == "go":
            # Generate go.mod
            go_mod = await self._generate_go_mod(dependencies, framework)
            package_files["go.mod"] = go_mod

        return package_files

    async def _generate_package_json(
        self, dependencies: Dict[str, Dict[str, Any]], framework: str
    ) -> str:
        """Generate package.json content"""

        prod_deps = {}
        dev_deps = {}

        for name, dep_info in dependencies.items():
            if dep_info["type"] == DependencyType.PRODUCTION.value:
                prod_deps[name] = dep_info["version"]
            elif dep_info["type"] == DependencyType.DEVELOPMENT.value:
                dev_deps[name] = dep_info["version"]

        package_json = {
            "name": "generated-project",
            "version": "1.0.0",
            "private": True,
            "scripts": self._get_framework_scripts(framework),
            "dependencies": prod_deps,
            "devDependencies": dev_deps,
        }

        return json.dumps(package_json, indent=2)

    async def _generate_requirements_txt(
        self, dependencies: Dict[str, Dict[str, Any]]
    ) -> str:
        """Generate requirements.txt content"""

        requirements = []

        for name, dep_info in dependencies.items():
            if dep_info["type"] == DependencyType.PRODUCTION.value:
                version = dep_info["version"].replace("^", ">=").replace("~", ">=")
                requirements.append(f"{name}{version}")

        return "\n".join(sorted(requirements))

    async def _generate_pyproject_toml(
        self, dependencies: Dict[str, Dict[str, Any]], framework: str
    ) -> str:
        """Generate pyproject.toml content"""

        prod_deps = []
        dev_deps = []

        for name, dep_info in dependencies.items():
            version = dep_info["version"].replace("^", ">=").replace("~", ">=")
            dep_line = f'"{name}{version}"'

            if dep_info["type"] == DependencyType.PRODUCTION.value:
                prod_deps.append(dep_line)
            elif dep_info["type"] == DependencyType.DEVELOPMENT.value:
                dev_deps.append(dep_line)

        toml_content = f"""[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.2"]

[project]
name = "generated-project"
version = "1.0.0"
description = "Generated project with {framework}"
dependencies = [
{chr(10).join(f"    {dep}," for dep in sorted(prod_deps))}
]

[project.optional-dependencies]
dev = [
{chr(10).join(f"    {dep}," for dep in sorted(dev_deps))}
]

[tool.setuptools]
packages = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]

[tool.black]
line-length = 88
target-version = ['py38']

[tool.isort]
profile = "black"
"""

        return toml_content

    def _get_framework_scripts(self, framework: str) -> Dict[str, str]:
        """Get framework-specific npm scripts"""

        scripts = {
            "react": {
                "dev": "vite",
                "build": "tsc && vite build",
                "preview": "vite preview",
                "test": "jest",
                "lint": "eslint src --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
                "lint:fix": "eslint src --ext ts,tsx --fix",
            },
            "vue": {
                "dev": "vite",
                "build": "vue-tsc && vite build",
                "preview": "vite preview",
                "test": "jest",
                "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mts --fix --ignore-path .gitignore",
            },
            "angular": {
                "ng": "ng",
                "start": "ng serve",
                "build": "ng build",
                "test": "ng test",
                "lint": "ng lint",
                "e2e": "ng e2e",
            },
            "express": {
                "dev": "nodemon src/index.ts",
                "build": "tsc",
                "start": "node dist/index.js",
                "test": "jest",
                "lint": "eslint src --ext .ts --fix",
            },
        }

        return scripts.get(
            framework,
            {
                "start": "node index.js",
                "test": 'echo "Error: no test specified" && exit 1',
            },
        )

    async def _calculate_total_size(
        self, dependencies: Dict[str, Dict[str, Any]]
    ) -> int:
        """Calculate estimated total size of dependencies"""

        # Simplified size estimation
        # In production, this would query actual package sizes

        size_estimates = {
            "react": 2500000,  # 2.5MB
            "react-dom": 3000000,  # 3MB
            "vue": 1000000,  # 1MB
            "@angular/core": 5000000,  # 5MB
            "express": 500000,  # 500KB
            "fastapi": 1000000,  # 1MB (Python)
            "django": 8000000,  # 8MB (Python)
        }

        total_size = 0
        for name in dependencies:
            estimated_size = size_estimates.get(name, 100000)  # Default 100KB
            total_size += estimated_size

        return total_size

    async def _generate_recommendations(
        self,
        dependencies: Dict[str, Dict[str, Any]],
        components: List[Dict[str, Any]],
        framework: str,
    ) -> List[str]:
        """Generate dependency recommendations"""

        recommendations = []

        # Check for outdated packages
        outdated_count = 0
        for name, dep_info in dependencies.items():
            if self._is_version_outdated(dep_info["version"]):
                outdated_count += 1

        if outdated_count > 0:
            recommendations.append(
                f"Consider updating {outdated_count} outdated packages"
            )

        # Check for alternatives to heavy packages
        heavy_packages = [
            name
            for name, dep_info in dependencies.items()
            if self._is_package_heavy(name)
        ]

        if heavy_packages:
            for package in heavy_packages:
                if package in self.package_alternatives:
                    alternatives = ", ".join(self.package_alternatives[package])
                    recommendations.append(
                        f"Consider alternatives to {package}: {alternatives}"
                    )

        # Framework-specific recommendations
        if framework == "react" and "redux" in dependencies:
            if "@reduxjs/toolkit" not in dependencies:
                recommendations.append(
                    "Consider using Redux Toolkit for better Redux experience"
                )

        if framework == "vue" and "vuex" in dependencies:
            if "pinia" not in dependencies:
                recommendations.append(
                    "Consider migrating from Vuex to Pinia for better TypeScript support"
                )

        # Security recommendations
        vulnerable_count = len(
            [name for name in dependencies if name in self.vulnerability_db]
        )
        if vulnerable_count > 0:
            recommendations.append(
                f"Review {vulnerable_count} packages with known vulnerabilities"
            )

        # Bundle size recommendations
        total_size = await self._calculate_total_size(dependencies)
        if total_size > 50000000:  # 50MB
            recommendations.append(
                "Bundle size is large, consider code splitting or tree shaking"
            )

        return recommendations

    def _compare_versions(self, version1: str, version2: str) -> int:
        """Compare two version strings"""

        v1 = self._clean_version(version1)
        v2 = self._clean_version(version2)

        try:
            if semver.compare(v1, v2) > 0:
                return 1
            elif semver.compare(v1, v2) < 0:
                return -1
            else:
                return 0
        except:
            # Fallback to simple string comparison
            if v1 > v2:
                return 1
            elif v1 < v2:
                return -1
            else:
                return 0

    def _clean_version(self, version: str) -> str:
        """Clean version string for comparison"""

        # Remove prefixes like ^, ~, >=
        cleaned = re.sub(r"^[\^~>=<]+", "", version.strip())

        # Ensure valid semver format
        parts = cleaned.split(".")
        while len(parts) < 3:
            parts.append("0")

        return ".".join(parts[:3])

    def _version_to_number(self, version: str) -> float:
        """Convert version string to number for comparison"""

        cleaned = self._clean_version(version)
        parts = cleaned.split(".")

        try:
            major = int(parts[0]) if len(parts) > 0 else 0
            minor = int(parts[1]) if len(parts) > 1 else 0
            patch = int(parts[2]) if len(parts) > 2 else 0

            return major * 10000 + minor * 100 + patch
        except:
            return 0

    def _version_matches_range(self, version: str, range_pattern: str) -> bool:
        """Check if version matches vulnerability range"""

        if range_pattern.startswith("<"):
            threshold = self._clean_version(range_pattern[1:])
            return self._compare_versions(version, threshold) < 0
        elif range_pattern.startswith("<="):
            threshold = self._clean_version(range_pattern[2:])
            return self._compare_versions(version, threshold) <= 0
        elif range_pattern.startswith(">="):
            threshold = self._clean_version(range_pattern[2:])
            return self._compare_versions(version, threshold) >= 0
        elif range_pattern.startswith(">"):
            threshold = self._clean_version(range_pattern[1:])
            return self._compare_versions(version, threshold) > 0
        else:
            return version == self._clean_version(range_pattern)

    def _is_version_outdated(self, version: str) -> bool:
        """Check if version is outdated (simplified)"""

        # In production, this would check against latest versions from registries
        cleaned = self._clean_version(version)
        parts = cleaned.split(".")

        try:
            major = int(parts[0])
            # Consider major version < 2 as potentially outdated
            return major < 2
        except:
            return False

    def _is_package_heavy(self, package_name: str) -> bool:
        """Check if package is considered heavy"""

        heavy_packages = [
            "moment",
            "lodash",
            "jquery",
            "bootstrap",
            "@angular/core",
            "three",
            "d3",
        ]

        return package_name in heavy_packages

    async def _generate_pom_xml(
        self, dependencies: Dict[str, Dict[str, Any]], framework: str
    ) -> str:
        """Generate Maven pom.xml"""

        return """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.example</groupId>
    <artifactId>generated-project</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>

    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencies>
        <!-- Dependencies would be generated here -->
    </dependencies>
</project>"""

    async def _generate_go_mod(
        self, dependencies: Dict[str, Dict[str, Any]], framework: str
    ) -> str:
        """Generate go.mod file"""

        return """module generated-project

go 1.19

require (
    // Dependencies would be generated here
)"""

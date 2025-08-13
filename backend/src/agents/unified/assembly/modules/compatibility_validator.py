"""
Compatibility Validator Module for Assembly Agent
Validates cross-platform and framework compatibility
"""

from typing import Dict, List, Any, Optional
import asyncio
import re
import json
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CompatibilityIssue:
    severity: str  # critical, major, minor
    component: str
    issue: str
    recommendation: str
    platforms_affected: List[str]


@dataclass
class CompatibilityResult:
    success: bool
    compatible_platforms: List[str]
    compatibility_score: float
    issues: List[CompatibilityIssue]
    compatibility_report: Dict[str, Any]
    validations_run: int
    processing_time: float
    error: str = ""


class CompatibilityValidator:
    """Advanced compatibility validation system"""

    def __init__(self):
        self.version = "1.0.0"

        self.platform_requirements = {
            "web": {
                "browsers": ["chrome", "firefox", "safari", "edge"],
                "min_versions": {
                    "chrome": "90",
                    "firefox": "88",
                    "safari": "14",
                    "edge": "90",
                },
                "features": ["es2020", "modules", "fetch", "promises"],
            },
            "mobile": {
                "platforms": ["ios", "android"],
                "min_versions": {"ios": "14.0", "android": "7.0"},
                "features": ["touch", "responsive", "viewport"],
            },
            "desktop": {
                "platforms": ["windows", "macos", "linux"],
                "frameworks": ["electron", "tauri", "pwa"],
            },
            "server": {
                "platforms": ["nodejs", "python", "docker"],
                "min_versions": {"nodejs": "18.0", "python": "3.9", "docker": "20.0"},
            },
        }

        self.framework_compatibility = {
            "react": {
                "supported_versions": ["16.8+", "17.x", "18.x"],
                "peer_dependencies": ["react-dom"],
                "incompatible_features": ["class_components_only"],
                "browser_support": ["chrome>=90", "firefox>=88", "safari>=14"],
            },
            "vue": {
                "supported_versions": ["2.6+", "3.x"],
                "peer_dependencies": ["vue-router", "vuex"],
                "incompatible_features": ["options_api_only"],
                "browser_support": ["chrome>=87", "firefox>=78", "safari>=13"],
            },
            "angular": {
                "supported_versions": ["12+", "13.x", "14.x", "15.x"],
                "peer_dependencies": ["@angular/common", "@angular/core"],
                "incompatible_features": ["angularjs_syntax"],
                "browser_support": ["chrome>=84", "firefox>=70", "safari>=13"],
            },
            "express": {
                "supported_versions": ["4.x"],
                "peer_dependencies": [],
                "incompatible_features": ["express3_middleware"],
                "node_support": [">=14.0"],
            },
            "fastapi": {
                "supported_versions": ["0.68+"],
                "peer_dependencies": ["uvicorn", "pydantic"],
                "incompatible_features": ["sync_only"],
                "python_support": [">=3.7"],
            },
        }

    async def validate_compatibility(
        self, validated_files: Dict[str, str], context: Dict[str, Any]
    ) -> CompatibilityResult:
        """Validate cross-platform compatibility"""

        start_time = datetime.now()
        issues = []
        validations_run = 0

        try:
            framework = context.get("framework", "react")
            target_platforms = context.get("target_platforms", ["web"])

            # Framework compatibility validation
            framework_issues = await self._validate_framework_compatibility(
                validated_files, framework
            )
            issues.extend(framework_issues)
            validations_run += len(framework_issues)

            # Platform-specific validation
            for platform in target_platforms:
                platform_issues = await self._validate_platform_compatibility(
                    validated_files, platform, framework
                )
                issues.extend(platform_issues)
                validations_run += len(platform_issues)

            # Dependency compatibility validation
            dependency_issues = await self._validate_dependency_compatibility(
                validated_files, framework
            )
            issues.extend(dependency_issues)
            validations_run += len(dependency_issues)

            # Browser/runtime compatibility validation
            runtime_issues = await self._validate_runtime_compatibility(
                validated_files, target_platforms
            )
            issues.extend(runtime_issues)
            validations_run += len(runtime_issues)

            # Calculate compatibility score
            critical_issues = len([i for i in issues if i.severity == "critical"])
            major_issues = len([i for i in issues if i.severity == "major"])
            minor_issues = len([i for i in issues if i.severity == "minor"])

            compatibility_score = max(
                0, 100 - (critical_issues * 25 + major_issues * 10 + minor_issues * 2)
            )

            # Determine compatible platforms
            compatible_platforms = []
            for platform in target_platforms:
                platform_issues = [
                    i for i in issues if platform in i.platforms_affected
                ]
                critical_platform_issues = [
                    i for i in platform_issues if i.severity == "critical"
                ]
                if len(critical_platform_issues) == 0:
                    compatible_platforms.append(platform)

            # Generate compatibility report
            compatibility_report = {
                "framework": framework,
                "target_platforms": target_platforms,
                "compatible_platforms": compatible_platforms,
                "compatibility_score": compatibility_score,
                "issues_by_severity": {
                    "critical": critical_issues,
                    "major": major_issues,
                    "minor": minor_issues,
                },
                "total_validations": validations_run,
                "validation_timestamp": datetime.now().isoformat(),
            }

            processing_time = (datetime.now() - start_time).total_seconds()

            return CompatibilityResult(
                success=True,
                compatible_platforms=compatible_platforms,
                compatibility_score=compatibility_score,
                issues=issues,
                compatibility_report=compatibility_report,
                validations_run=validations_run,
                processing_time=processing_time,
            )

        except Exception as e:
            return CompatibilityResult(
                success=False,
                compatible_platforms=[],
                compatibility_score=0.0,
                issues=[],
                compatibility_report={},
                validations_run=0,
                processing_time=(datetime.now() - start_time).total_seconds(),
                error=str(e),
            )

    async def _validate_framework_compatibility(
        self, files: Dict[str, str], framework: str
    ) -> List[CompatibilityIssue]:
        """Validate framework-specific compatibility"""

        issues = []

        if framework not in self.framework_compatibility:
            issues.append(
                CompatibilityIssue(
                    severity="critical",
                    component="framework",
                    issue=f"Unsupported framework: {framework}",
                    recommendation=f"Use supported frameworks: {list(self.framework_compatibility.keys())}",
                    platforms_affected=["all"],
                )
            )
            return issues

        framework_config = self.framework_compatibility[framework]

        # Check for deprecated features
        for file_path, content in files.items():
            if file_path.endswith((".js", ".jsx", ".ts", ".tsx", ".vue", ".py")):
                for feature in framework_config.get("incompatible_features", []):
                    if self._check_feature_usage(content, feature, framework):
                        issues.append(
                            CompatibilityIssue(
                                severity="major",
                                component=file_path,
                                issue=f"Uses deprecated feature: {feature}",
                                recommendation=f"Update to modern {framework} patterns",
                                platforms_affected=["all"],
                            )
                        )

        # Check package.json for version compatibility
        if "package.json" in files:
            try:
                package_data = json.loads(files["package.json"])
                dependencies = {
                    **package_data.get("dependencies", {}),
                    **package_data.get("devDependencies", {}),
                }

                for dep, version in dependencies.items():
                    if dep == framework or dep.startswith(f"{framework}/"):
                        if not self._is_version_compatible(
                            version, framework_config["supported_versions"]
                        ):
                            issues.append(
                                CompatibilityIssue(
                                    severity="critical",
                                    component="package.json",
                                    issue=f"Incompatible {framework} version: {version}",
                                    recommendation=f"Use supported versions: {framework_config['supported_versions']}",
                                    platforms_affected=["all"],
                                )
                            )

            except json.JSONDecodeError:
                pass

        return issues

    async def _validate_platform_compatibility(
        self, files: Dict[str, str], platform: str, framework: str
    ) -> List[CompatibilityIssue]:
        """Validate platform-specific compatibility"""

        issues = []

        if platform not in self.platform_requirements:
            return issues

        platform_config = self.platform_requirements[platform]

        # Web platform specific checks
        if platform == "web":
            for file_path, content in files.items():
                if file_path.endswith((".js", ".jsx", ".ts", ".tsx")):
                    # Check for unsupported ES features
                    unsupported_features = [
                        (r"\?\?=", "Logical nullish assignment"),
                        (r"\|\|=", "Logical OR assignment"),
                        (r"\&\&=", "Logical AND assignment"),
                        (r"\btop-level await\b", "Top-level await"),
                    ]

                    for pattern, feature_name in unsupported_features:
                        if re.search(pattern, content):
                            issues.append(
                                CompatibilityIssue(
                                    severity="minor",
                                    component=file_path,
                                    issue=f"Uses {feature_name} - may not work in older browsers",
                                    recommendation="Consider using babel transforms or polyfills",
                                    platforms_affected=[platform],
                                )
                            )

        # Mobile platform specific checks
        elif platform == "mobile":
            # Check for touch event handling
            for file_path, content in files.items():
                if file_path.endswith(".css"):
                    if "hover:" in content and "touch:" not in content:
                        issues.append(
                            CompatibilityIssue(
                                severity="minor",
                                component=file_path,
                                issue="Uses hover effects without touch alternatives",
                                recommendation="Add touch-friendly interactions",
                                platforms_affected=[platform],
                            )
                        )

        # Server platform specific checks
        elif platform == "server":
            # Check for Node.js compatibility
            if framework in ["express", "fastapi"]:
                for file_path, content in files.items():
                    if file_path.endswith((".js", ".ts", ".py")):
                        if "process.env" in content and not re.search(
                            r"process\.env\.[A-Z_]+", content
                        ):
                            issues.append(
                                CompatibilityIssue(
                                    severity="minor",
                                    component=file_path,
                                    issue="Accesses process.env without proper error handling",
                                    recommendation="Add fallback values for environment variables",
                                    platforms_affected=[platform],
                                )
                            )

        return issues

    async def _validate_dependency_compatibility(
        self, files: Dict[str, str], framework: str
    ) -> List[CompatibilityIssue]:
        """Validate dependency compatibility"""

        issues = []

        if "package.json" in files:
            try:
                package_data = json.loads(files["package.json"])
                dependencies = package_data.get("dependencies", {})

                # Check for conflicting dependencies
                conflicting_pairs = [
                    (["react", "vue"], "Cannot use React and Vue together"),
                    (["angular", "react"], "Cannot use Angular and React together"),
                    (["express", "fastapi"], "Multiple backend frameworks detected"),
                ]

                for conflict_deps, message in conflicting_pairs:
                    found_deps = [dep for dep in conflict_deps if dep in dependencies]
                    if len(found_deps) > 1:
                        issues.append(
                            CompatibilityIssue(
                                severity="critical",
                                component="package.json",
                                issue=message,
                                recommendation=f"Choose one: {', '.join(found_deps)}",
                                platforms_affected=["all"],
                            )
                        )

            except json.JSONDecodeError:
                pass

        elif "requirements.txt" in files:
            requirements = files["requirements.txt"]

            # Check for Python dependency conflicts
            if "django" in requirements and "flask" in requirements:
                issues.append(
                    CompatibilityIssue(
                        severity="major",
                        component="requirements.txt",
                        issue="Multiple Python web frameworks detected",
                        recommendation="Choose either Django or Flask",
                        platforms_affected=["server"],
                    )
                )

        return issues

    async def _validate_runtime_compatibility(
        self, files: Dict[str, str], target_platforms: List[str]
    ) -> List[CompatibilityIssue]:
        """Validate runtime compatibility"""

        issues = []

        # Check for Node.js specific APIs in browser context
        if "web" in target_platforms:
            node_apis = ["fs", "path", "os", "child_process", "crypto"]

            for file_path, content in files.items():
                if file_path.endswith((".js", ".jsx", ".ts", ".tsx")):
                    for api in node_apis:
                        if re.search(
                            f"require\(['\"]?{api}['\"]?\)", content
                        ) or re.search(f"from ['\"]?{api}['\"]?", content):
                            issues.append(
                                CompatibilityIssue(
                                    severity="critical",
                                    component=file_path,
                                    issue=f"Uses Node.js API '{api}' in browser context",
                                    recommendation="Use browser-compatible alternatives or polyfills",
                                    platforms_affected=["web"],
                                )
                            )

        return issues

    def _check_feature_usage(self, content: str, feature: str, framework: str) -> bool:
        """Check if deprecated feature is used in code"""

        feature_patterns = {
            "class_components_only": r"class\s+\w+\s+extends\s+React\.Component",
            "options_api_only": r"export\s+default\s+\{\s*data\s*\(",
            "angularjs_syntax": r"\$scope\.|\$rootScope\.",
            "express3_middleware": r"app\.configure\(",
            "sync_only": r"def\s+\w+\([^)]*\)\s*:(?!.*async)",
        }

        pattern = feature_patterns.get(feature)
        if pattern:
            return bool(re.search(pattern, content, re.MULTILINE))

        return False

    def _is_version_compatible(
        self, version: str, supported_versions: List[str]
    ) -> bool:
        """Check if version is compatible with supported versions"""

        # Simple version compatibility check
        # In production, use proper semver parsing
        version_clean = re.sub(r"[^0-9.]", "", version.split(".")[0] if version else "")

        for supported in supported_versions:
            if "+" in supported:
                min_version = supported.replace("+", "")
                try:
                    if float(version_clean) >= float(min_version.split(".")[0]):
                        return True
                except (ValueError, IndexError):
                    continue
            elif "x" in supported:
                major_version = supported.split(".")[0]
                try:
                    if version_clean.startswith(major_version):
                        return True
                except (AttributeError, IndexError):
                    continue

        return False

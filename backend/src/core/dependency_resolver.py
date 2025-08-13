"""
🧬 T-Developer Dependency Resolver
Automatic dependency resolution for agents <6.5KB
"""
import ast
import importlib
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


@dataclass
class Dependency:
    """Dependency information"""

    name: str
    version: Optional[str] = None
    import_name: Optional[str] = None  # Different from package name (e.g., PIL -> pillow)
    optional: bool = False
    installed: bool = False


@dataclass
class ResolutionResult:
    """Dependency resolution result"""

    success: bool
    dependencies: List[Dependency]
    missing: List[str]
    conflicts: List[str]
    suggestions: List[str]
    total_size_estimate: int = 0


class DependencyResolver:
    """Ultra-lightweight dependency resolver for agents"""

    def __init__(self):
        # Common package mappings (import name -> package name)
        self.package_mappings = {
            "PIL": "pillow",
            "cv2": "opencv-python",
            "sklearn": "scikit-learn",
            "yaml": "pyyaml",
            "bs4": "beautifulsoup4",
            "requests": "requests",
            "numpy": "numpy",
            "pandas": "pandas",
            "matplotlib": "matplotlib",
            "sqlite3": None,  # Built-in
            "re": None,  # Built-in
            "json": None,  # Built-in
            "os": None,  # Built-in
            "sys": None,  # Built-in
            "pathlib": None,  # Built-in
            "typing": None,  # Built-in
            "asyncio": None,  # Built-in
            "dataclasses": None,  # Built-in
            "time": None,  # Built-in
            "datetime": None,  # Built-in
            "collections": None,  # Built-in
            "itertools": None,  # Built-in
        }

        # Size estimates (in KB) for common packages
        self.size_estimates = {
            "requests": 500,
            "pandas": 30000,
            "numpy": 15000,
            "pillow": 8000,
            "fastapi": 2000,
            "sqlalchemy": 3000,
            "pydantic": 1500,
        }

    def resolve_dependencies(self, code: str) -> ResolutionResult:
        """Resolve all dependencies for given code"""
        try:
            # Extract imports from code
            imports = self._extract_imports(code)

            # Convert to dependencies
            dependencies = []
            missing = []
            conflicts = []
            suggestions = []
            total_size = 0

            for import_name in imports:
                dep = self._create_dependency(import_name)
                dependencies.append(dep)

                if not dep.installed and dep.name:  # External package
                    missing.append(dep.name)
                    total_size += self.size_estimates.get(dep.name, 1000)  # Default 1MB

            # Check for conflicts and generate suggestions
            conflicts, suggestions = self._analyze_dependencies(dependencies)

            return ResolutionResult(
                success=len(missing) == 0,
                dependencies=dependencies,
                missing=missing,
                conflicts=conflicts,
                suggestions=suggestions,
                total_size_estimate=total_size,
            )

        except Exception as e:
            return ResolutionResult(
                success=False,
                dependencies=[],
                missing=[],
                conflicts=[],
                suggestions=[f"Resolution error: {str(e)}"],
            )

    def resolve_from_file(self, file_path: Path) -> ResolutionResult:
        """Resolve dependencies from Python file"""
        try:
            code = file_path.read_text()
            return self.resolve_dependencies(code)
        except Exception as e:
            return ResolutionResult(
                success=False,
                dependencies=[],
                missing=[],
                conflicts=[],
                suggestions=[f"File error: {str(e)}"],
            )

    def install_missing(self, result: ResolutionResult) -> bool:
        """Install missing dependencies (if possible)"""
        if not result.missing:
            return True

        try:
            # Use pip to install missing packages
            for package in result.missing:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", package], capture_output=True
                )

            return True
        except subprocess.CalledProcessError:
            return False

    def check_installed(self, package_name: str) -> bool:
        """Check if package is installed"""
        try:
            importlib.import_module(package_name)
            return True
        except ImportError:
            return False

    def suggest_alternatives(self, missing_package: str) -> List[str]:
        """Suggest alternative packages"""
        alternatives = {
            "requests": ["urllib3", "httpx"],
            "pandas": ["polars", "dask"],
            "numpy": ["array"],
            "pillow": ["opencv-python"],
            "matplotlib": ["seaborn", "plotly"],
        }
        return alternatives.get(missing_package, [])

    def _extract_imports(self, code: str) -> Set[str]:
        """Extract all import statements from code"""
        imports = set()

        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split(".")[0])
        except SyntaxError:
            # Fallback to regex if AST parsing fails
            import_patterns = [
                r"^import\s+(\w+)",
                r"^from\s+(\w+)\s+import",
            ]

            for line in code.split("\n"):
                line = line.strip()
                for pattern in import_patterns:
                    match = re.match(pattern, line)
                    if match:
                        imports.add(match.group(1))

        return imports

    def _create_dependency(self, import_name: str) -> Dependency:
        """Create dependency object from import name"""
        # Check if it's a built-in module
        if import_name in self.package_mappings and self.package_mappings[import_name] is None:
            return Dependency(name=import_name, import_name=import_name, installed=True)

        # Map import name to package name
        package_name = self.package_mappings.get(import_name, import_name)

        # Check if installed
        installed = self.check_installed(import_name)

        return Dependency(name=package_name, import_name=import_name, installed=installed)

    def _analyze_dependencies(self, dependencies: List[Dependency]) -> tuple[List[str], List[str]]:
        """Analyze dependencies for conflicts and generate suggestions"""
        conflicts = []
        suggestions = []

        # Calculate total estimated size
        total_size = sum(
            self.size_estimates.get(dep.name, 1000)
            for dep in dependencies
            if dep.name and not dep.installed
        )

        # Check for heavy dependencies
        heavy_deps = [
            dep.name
            for dep in dependencies
            if dep.name and self.size_estimates.get(dep.name, 0) > 10000
        ]

        if heavy_deps:
            suggestions.append(f"Heavy dependencies detected: {', '.join(heavy_deps)}")
            suggestions.append("Consider lighter alternatives for 6.5KB constraint")

        # Check for common conflicts
        dep_names = {dep.name for dep in dependencies if dep.name}

        if "tensorflow" in dep_names and "torch" in dep_names:
            conflicts.append("TensorFlow and PyTorch both detected - may cause conflicts")

        if total_size > 50000:  # 50MB
            suggestions.append(f"Total dependency size ~{total_size//1000}MB - consider minimizing")

        return conflicts, suggestions

    def get_builtin_modules(self) -> Set[str]:
        """Get list of built-in Python modules"""
        return {name for name, pkg in self.package_mappings.items() if pkg is None}

    def estimate_install_size(self, package_name: str) -> int:
        """Estimate package installation size in KB"""
        return self.size_estimates.get(package_name, 1000)

    def generate_requirements_txt(self, result: ResolutionResult) -> str:
        """Generate requirements.txt content"""
        lines = []
        for dep in result.dependencies:
            if dep.name and not dep.installed and dep.name not in self.get_builtin_modules():
                if dep.version:
                    lines.append(f"{dep.name}=={dep.version}")
                else:
                    lines.append(dep.name)

        return "\n".join(sorted(lines))


# Factory function
def create_resolver() -> DependencyResolver:
    """Create dependency resolver instance"""
    return DependencyResolver()


# Global resolver instance
_global_resolver = None


def get_global_resolver() -> DependencyResolver:
    """Get or create global resolver instance"""
    global _global_resolver
    if _global_resolver is None:
        _global_resolver = create_resolver()
    return _global_resolver


# Convenience functions
def resolve_code_dependencies(code: str) -> ResolutionResult:
    """Resolve dependencies for code using global resolver"""
    return get_global_resolver().resolve_dependencies(code)


def resolve_file_dependencies(file_path: Path) -> ResolutionResult:
    """Resolve dependencies for file using global resolver"""
    return get_global_resolver().resolve_from_file(file_path)


def quick_check(code: str) -> Dict[str, Any]:
    """Quick dependency check"""
    result = resolve_code_dependencies(code)
    return {
        "missing_count": len(result.missing),
        "missing_packages": result.missing,
        "total_size_mb": result.total_size_estimate // 1000,
        "has_conflicts": len(result.conflicts) > 0,
        "ready_to_run": result.success,
    }

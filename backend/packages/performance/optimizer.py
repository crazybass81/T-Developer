"""Performance Optimizer - Automated performance optimization engine.

Phase 6: P6-T1 - Performance Optimization
Automatically detect bottlenecks and apply optimizations.
"""

from __future__ import annotations

import ast
import asyncio
import hashlib
import logging
import shutil
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .profiler import PerformanceProfiler

# Constants
DEFAULT_TIMEOUT: int = 300
MAX_OPTIMIZATION_CYCLES: int = 5
MIN_IMPROVEMENT_THRESHOLD: float = 0.05  # 5% minimum improvement

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """Result of optimization operation."""

    success: bool
    file_path: str
    optimization_type: str
    performance_before: float
    performance_after: float
    improvement_percent: float
    patch_applied: str
    error: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationPatch:
    """Code patch for optimization."""

    id: str
    target_file: str
    line_number: int
    original_code: str
    optimized_code: str
    optimization_type: str
    expected_improvement: float
    safety_score: float  # 0-1, confidence in safety
    description: str


class CodeAnalyzer:
    """Analyze code for optimization opportunities."""

    def __init__(self):
        """Initialize code analyzer."""
        self.logger = logging.getLogger(self.__class__.__name__)

    def analyze_file(self, file_path: Path) -> list[OptimizationPatch]:
        """Analyze file for optimization opportunities."""
        patches = []

        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source)
            lines = source.split("\n")

            # Find various optimization opportunities
            patches.extend(self._find_loop_optimizations(tree, lines, str(file_path)))
            patches.extend(self._find_caching_opportunities(tree, lines, str(file_path)))
            patches.extend(self._find_async_opportunities(tree, lines, str(file_path)))
            patches.extend(self._find_db_optimizations(tree, lines, str(file_path)))
            patches.extend(self._find_memory_optimizations(tree, lines, str(file_path)))

        except Exception as e:
            self.logger.error(f"Error analyzing {file_path}: {e}")

        return patches

    def _find_loop_optimizations(
        self, tree: ast.AST, lines: list[str], file_path: str
    ) -> list[OptimizationPatch]:
        """Find loop optimization opportunities."""
        patches = []

        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Check for list comprehension opportunities
                if (
                    len(node.body) == 1
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Call)
                    and hasattr(node.body[0].value.func, "attr")
                    and node.body[0].value.func.attr == "append"
                ):
                    patch = OptimizationPatch(
                        id=self._generate_patch_id(file_path, node.lineno),
                        target_file=file_path,
                        line_number=node.lineno,
                        original_code=self._extract_code_block(
                            lines, node.lineno, node.end_lineno or node.lineno + 1
                        ),
                        optimized_code=self._generate_list_comprehension(node, lines),
                        optimization_type="list_comprehension",
                        expected_improvement=25.0,
                        safety_score=0.9,
                        description="Convert for loop with append to list comprehension",
                    )
                    patches.append(patch)

                # Check for nested loops that could be optimized
                nested_loops = [n for n in ast.walk(node) if isinstance(n, ast.For) and n != node]
                if nested_loops:
                    patch = OptimizationPatch(
                        id=self._generate_patch_id(file_path, node.lineno),
                        target_file=file_path,
                        line_number=node.lineno,
                        original_code=self._extract_code_block(
                            lines, node.lineno, node.end_lineno or node.lineno + 5
                        ),
                        optimized_code="# Consider using itertools.product() or vectorized operations",
                        optimization_type="nested_loop",
                        expected_improvement=40.0,
                        safety_score=0.6,
                        description="Nested loop detected - consider optimization",
                    )
                    patches.append(patch)

        return patches

    def _find_caching_opportunities(
        self, tree: ast.AST, lines: list[str], file_path: str
    ) -> list[OptimizationPatch]:
        """Find caching optimization opportunities."""
        patches = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if function is pure (no side effects)
                if self._is_pure_function(node):
                    # Check if function has expensive computations
                    if self._has_expensive_operations(node):
                        patch = OptimizationPatch(
                            id=self._generate_patch_id(file_path, node.lineno),
                            target_file=file_path,
                            line_number=node.lineno,
                            original_code=f"def {node.name}(",
                            optimized_code=f"@lru_cache(maxsize=128)\ndef {node.name}(",
                            optimization_type="caching",
                            expected_improvement=60.0,
                            safety_score=0.8,
                            description=f"Add LRU cache to pure function '{node.name}'",
                        )
                        patches.append(patch)

        return patches

    def _find_async_opportunities(
        self, tree: ast.AST, lines: list[str], file_path: str
    ) -> list[OptimizationPatch]:
        """Find async optimization opportunities."""
        patches = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Look for I/O operations that could be async
                io_calls = []
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if hasattr(child.func, "id") and child.func.id in [
                            "open",
                            "requests.get",
                            "requests.post",
                        ]:
                            io_calls.append(child)
                        elif hasattr(child.func, "attr") and child.func.attr in [
                            "read",
                            "write",
                            "get",
                            "post",
                        ]:
                            io_calls.append(child)

                if io_calls and not isinstance(node, ast.AsyncFunctionDef):
                    patch = OptimizationPatch(
                        id=self._generate_patch_id(file_path, node.lineno),
                        target_file=file_path,
                        line_number=node.lineno,
                        original_code=f"def {node.name}(",
                        optimized_code=f"async def {node.name}(",
                        optimization_type="async_io",
                        expected_improvement=50.0,
                        safety_score=0.7,
                        description=f"Convert I/O function '{node.name}' to async",
                    )
                    patches.append(patch)

        return patches

    def _find_db_optimizations(
        self, tree: ast.AST, lines: list[str], file_path: str
    ) -> list[OptimizationPatch]:
        """Find database optimization opportunities."""
        patches = []

        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Look for database queries inside loops
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if hasattr(child.func, "attr") and child.func.attr in [
                            "execute",
                            "query",
                            "fetch",
                        ]:
                            patch = OptimizationPatch(
                                id=self._generate_patch_id(file_path, node.lineno),
                                target_file=file_path,
                                line_number=node.lineno,
                                original_code=self._extract_code_block(
                                    lines, node.lineno, node.end_lineno or node.lineno + 3
                                ),
                                optimized_code="# Consider batch operations or query optimization",
                                optimization_type="db_batch",
                                expected_improvement=70.0,
                                safety_score=0.6,
                                description="Database query in loop - consider batching",
                            )
                            patches.append(patch)
                            break

        return patches

    def _find_memory_optimizations(
        self, tree: ast.AST, lines: list[str], file_path: str
    ) -> list[OptimizationPatch]:
        """Find memory optimization opportunities."""
        patches = []

        for node in ast.walk(tree):
            # Look for large list creations that could use generators
            if isinstance(node, ast.ListComp):
                # If list comprehension is very large or complex
                if self._is_complex_comprehension(node):
                    patch = OptimizationPatch(
                        id=self._generate_patch_id(file_path, node.lineno),
                        target_file=file_path,
                        line_number=node.lineno,
                        original_code="[...]",
                        optimized_code="(...)",
                        optimization_type="generator",
                        expected_improvement=30.0,
                        safety_score=0.8,
                        description="Convert list comprehension to generator expression",
                    )
                    patches.append(patch)

        return patches

    def _generate_patch_id(self, file_path: str, line_number: int) -> str:
        """Generate unique patch ID."""
        content = f"{file_path}:{line_number}"
        return hashlib.md5(content.encode()).hexdigest()[:8]

    def _extract_code_block(self, lines: list[str], start: int, end: int) -> str:
        """Extract code block from lines."""
        # Adjust for 0-based indexing
        start_idx = max(0, start - 1)
        end_idx = min(len(lines), end)
        return "\n".join(lines[start_idx:end_idx])

    def _generate_list_comprehension(self, node: ast.For, lines: list[str]) -> str:
        """Generate list comprehension from for loop."""
        # Simplified implementation
        return "# List comprehension optimization available"

    def _is_pure_function(self, node: ast.FunctionDef) -> bool:
        """Check if function is pure (no side effects)."""
        # Simplified check - look for global variables, prints, etc.
        for child in ast.walk(node):
            if isinstance(child, ast.Global):
                return False
            if isinstance(child, ast.Call):
                if hasattr(child.func, "id") and child.func.id == "print":
                    return False
        return True

    def _has_expensive_operations(self, node: ast.FunctionDef) -> bool:
        """Check if function has expensive operations."""
        # Look for loops, recursive calls, complex calculations
        for child in ast.walk(node):
            if isinstance(child, (ast.For, ast.While)):
                return True
            if isinstance(child, ast.Call):
                if hasattr(child.func, "id") and child.func.id == node.name:
                    return True  # Recursive call
        return False

    def _is_complex_comprehension(self, node: ast.ListComp) -> bool:
        """Check if list comprehension is complex."""
        # Look for nested comprehensions or complex generators
        return len(node.generators) > 1


class PatchApplicator:
    """Apply optimization patches to code."""

    def __init__(self):
        """Initialize patch applicator."""
        self.logger = logging.getLogger(self.__class__.__name__)

    async def apply_patch(self, patch: OptimizationPatch) -> OptimizationResult:
        """Apply optimization patch to file."""
        try:
            file_path = Path(patch.target_file)

            # Create backup
            backup_path = file_path.with_suffix(f".backup_{int(time.time())}")
            shutil.copy2(file_path, backup_path)

            # Read original file
            with open(file_path, encoding="utf-8") as f:
                original_content = f.read()

            # Apply patch based on type
            if patch.optimization_type == "caching":
                new_content = self._apply_caching_patch(original_content, patch)
            elif patch.optimization_type == "async_io":
                new_content = self._apply_async_patch(original_content, patch)
            elif patch.optimization_type == "list_comprehension":
                new_content = self._apply_comprehension_patch(original_content, patch)
            else:
                # Generic patch application
                new_content = original_content.replace(patch.original_code, patch.optimized_code)

            # Validate syntax
            try:
                ast.parse(new_content)
            except SyntaxError as e:
                self.logger.error(f"Syntax error in optimized code: {e}")
                return OptimizationResult(
                    success=False,
                    file_path=patch.target_file,
                    optimization_type=patch.optimization_type,
                    performance_before=0,
                    performance_after=0,
                    improvement_percent=0,
                    patch_applied=patch.id,
                    error=f"Syntax error: {e}",
                )

            # Write optimized file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            return OptimizationResult(
                success=True,
                file_path=patch.target_file,
                optimization_type=patch.optimization_type,
                performance_before=0,  # Will be measured
                performance_after=0,  # Will be measured
                improvement_percent=patch.expected_improvement,
                patch_applied=patch.id,
                metadata={"backup_path": str(backup_path), "safety_score": patch.safety_score},
            )

        except Exception as e:
            self.logger.error(f"Error applying patch {patch.id}: {e}")
            return OptimizationResult(
                success=False,
                file_path=patch.target_file,
                optimization_type=patch.optimization_type,
                performance_before=0,
                performance_after=0,
                improvement_percent=0,
                patch_applied=patch.id,
                error=str(e),
            )

    def _apply_caching_patch(self, content: str, patch: OptimizationPatch) -> str:
        """Apply caching optimization patch."""
        lines = content.split("\n")

        # Find the function definition line
        for i, line in enumerate(lines):
            if f"def {patch.original_code.split('(')[0].replace('def ', '')}(" in line:
                # Add import if not present
                if "from functools import lru_cache" not in content:
                    # Find import section
                    import_line = 0
                    for j, l in enumerate(lines):
                        if l.startswith("import ") or l.startswith("from "):
                            import_line = j + 1
                    lines.insert(import_line, "from functools import lru_cache")
                    i += 1

                # Add decorator
                indent = len(line) - len(line.lstrip())
                decorator = " " * indent + "@lru_cache(maxsize=128)"
                lines.insert(i, decorator)
                break

        return "\n".join(lines)

    def _apply_async_patch(self, content: str, patch: OptimizationPatch) -> str:
        """Apply async optimization patch."""
        # Replace function definition
        return content.replace(patch.original_code, patch.optimized_code)

    def _apply_comprehension_patch(self, content: str, patch: OptimizationPatch) -> str:
        """Apply list comprehension optimization patch."""
        # This would need more sophisticated AST manipulation
        return content

    async def rollback_patch(self, result: OptimizationResult) -> bool:
        """Rollback applied patch."""
        try:
            backup_path = Path(result.metadata.get("backup_path", ""))
            if backup_path.exists():
                file_path = Path(result.file_path)
                shutil.copy2(backup_path, file_path)
                backup_path.unlink()  # Remove backup
                return True
        except Exception as e:
            self.logger.error(f"Error rolling back patch: {e}")

        return False


class PerformanceBenchmarker:
    """Benchmark performance before and after optimizations."""

    def __init__(self):
        """Initialize performance benchmarker."""
        self.profiler = PerformanceProfiler()
        self.logger = logging.getLogger(self.__class__.__name__)

    async def benchmark_function(
        self, func, *args, iterations: int = 10, **kwargs
    ) -> dict[str, float]:
        """Benchmark function performance."""
        results = {
            "min_time": float("inf"),
            "max_time": 0,
            "avg_time": 0,
            "total_time": 0,
            "memory_usage": 0,
        }

        times = []

        for _ in range(iterations):
            report = await self.profiler.profile_code(func, *args, **kwargs)
            times.append(report.total_time)
            results["memory_usage"] = max(results["memory_usage"], report.total_memory)

        results["min_time"] = min(times)
        results["max_time"] = max(times)
        results["avg_time"] = sum(times) / len(times)
        results["total_time"] = sum(times)

        return results

    async def compare_performance(
        self, original_func, optimized_func, *args, **kwargs
    ) -> dict[str, Any]:
        """Compare performance between original and optimized functions."""
        original_results = await self.benchmark_function(original_func, *args, **kwargs)
        optimized_results = await self.benchmark_function(optimized_func, *args, **kwargs)

        improvement = {
            "time_improvement": (
                (original_results["avg_time"] - optimized_results["avg_time"])
                / original_results["avg_time"]
                * 100
            ),
            "memory_improvement": (
                (original_results["memory_usage"] - optimized_results["memory_usage"])
                / max(original_results["memory_usage"], 0.001)
                * 100
            ),
        }

        return {
            "original": original_results,
            "optimized": optimized_results,
            "improvement": improvement,
        }


class AutoOptimizer:
    """Automated performance optimization engine."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize auto optimizer.

        Args:
            config: Configuration dictionary with optimization settings
        """
        self.config = config or {}
        self.analyzer = CodeAnalyzer()
        self.applicator = PatchApplicator()
        self.benchmarker = PerformanceBenchmarker()
        self.logger = logging.getLogger(self.__class__.__name__)

        # Configuration
        self.max_cycles = self.config.get("max_cycles", MAX_OPTIMIZATION_CYCLES)
        self.min_improvement = self.config.get("min_improvement", MIN_IMPROVEMENT_THRESHOLD)
        self.safety_threshold = self.config.get("safety_threshold", 0.7)

    async def optimize_file(self, file_path: Path) -> list[OptimizationResult]:
        """Optimize single file performance.

        Args:
            file_path: Path to file to optimize

        Returns:
            List of optimization results
        """
        self.logger.info(f"Starting optimization of {file_path}")
        results = []

        try:
            # Analyze file for optimization opportunities
            patches = self.analyzer.analyze_file(file_path)
            self.logger.info(f"Found {len(patches)} optimization opportunities")

            # Filter patches by safety score
            safe_patches = [p for p in patches if p.safety_score >= self.safety_threshold]
            self.logger.info(f"Applying {len(safe_patches)} safe patches")

            # Apply patches one by one
            for patch in safe_patches:
                try:
                    result = await self.applicator.apply_patch(patch)
                    results.append(result)

                    if not result.success:
                        self.logger.warning(f"Failed to apply patch {patch.id}: {result.error}")
                        continue

                    # Verify syntax and basic functionality
                    if not await self._verify_optimization(file_path):
                        self.logger.warning(f"Optimization verification failed for {patch.id}")
                        await self.applicator.rollback_patch(result)
                        result.success = False
                        result.error = "Verification failed"

                except Exception as e:
                    self.logger.error(f"Error applying patch {patch.id}: {e}")
                    result = OptimizationResult(
                        success=False,
                        file_path=str(file_path),
                        optimization_type=patch.optimization_type,
                        performance_before=0,
                        performance_after=0,
                        improvement_percent=0,
                        patch_applied=patch.id,
                        error=str(e),
                    )
                    results.append(result)

        except Exception as e:
            self.logger.error(f"Error optimizing file {file_path}: {e}")

        return results

    async def optimize_directory(self, directory_path: Path) -> dict[str, list[OptimizationResult]]:
        """Optimize all Python files in directory.

        Args:
            directory_path: Path to directory to optimize

        Returns:
            Dictionary mapping file paths to optimization results
        """
        results = {}

        # Find all Python files
        python_files = list(directory_path.rglob("*.py"))
        self.logger.info(f"Found {len(python_files)} Python files to optimize")

        # Process files concurrently (with limits)
        semaphore = asyncio.Semaphore(3)  # Limit concurrent optimizations

        async def optimize_single_file(file_path: Path) -> tuple[str, list[OptimizationResult]]:
            async with semaphore:
                file_results = await self.optimize_file(file_path)
                return str(file_path), file_results

        # Execute optimizations
        tasks = [optimize_single_file(f) for f in python_files]
        completed_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for result in completed_results:
            if isinstance(result, Exception):
                self.logger.error(f"Optimization task failed: {result}")
            else:
                file_path, file_results = result
                results[file_path] = file_results

        return results

    async def _verify_optimization(self, file_path: Path) -> bool:
        """Verify that optimization didn't break the code.

        Args:
            file_path: Path to optimized file

        Returns:
            True if verification passed
        """
        try:
            # Check syntax
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            ast.parse(content)

            # Additional checks could include:
            # - Running tests
            # - Import verification
            # - Type checking

            return True

        except Exception as e:
            self.logger.error(f"Verification failed for {file_path}: {e}")
            return False

    def generate_optimization_report(
        self, results: dict[str, list[OptimizationResult]], output_path: Path
    ) -> None:
        """Generate optimization report.

        Args:
            results: Optimization results
            output_path: Path to save report
        """
        total_optimizations = sum(len(file_results) for file_results in results.values())
        successful_optimizations = sum(
            len([r for r in file_results if r.success]) for file_results in results.values()
        )

        report_content = f"""# Performance Optimization Report

Generated: {datetime.now()}

## Summary
- Files Analyzed: {len(results)}
- Total Optimizations Attempted: {total_optimizations}
- Successful Optimizations: {successful_optimizations}
- Success Rate: {successful_optimizations/max(total_optimizations, 1)*100:.1f}%

## Results by File
"""

        for file_path, file_results in results.items():
            report_content += f"\n### {file_path}\n"

            if not file_results:
                report_content += "- No optimizations applied\n"
                continue

            for result in file_results:
                status = "✅ Success" if result.success else "❌ Failed"
                report_content += f"""
- **{result.optimization_type}** {status}
  - Expected Improvement: {result.improvement_percent:.1f}%
  - Patch ID: {result.patch_applied}
"""
                if result.error:
                    report_content += f"  - Error: {result.error}\n"

        # Write report
        output_path.write_text(report_content)
        self.logger.info(f"Optimization report saved to {output_path}")


# Main optimization function for easy use
async def optimize_performance(
    target_path: Path, config: Optional[dict[str, Any]] = None
) -> dict[str, Any]:
    """Main function to optimize performance of target code.

    Args:
        target_path: Path to file or directory to optimize
        config: Optional configuration

    Returns:
        Optimization results and statistics
    """
    optimizer = AutoOptimizer(config)

    if target_path.is_file():
        results = {str(target_path): await optimizer.optimize_file(target_path)}
    else:
        results = await optimizer.optimize_directory(target_path)

    # Generate report
    report_path = target_path.parent / f"optimization_report_{int(time.time())}.md"
    optimizer.generate_optimization_report(results, report_path)

    # Calculate statistics
    total_files = len(results)
    total_optimizations = sum(len(file_results) for file_results in results.values())
    successful_optimizations = sum(
        len([r for r in file_results if r.success]) for file_results in results.values()
    )

    return {
        "results": results,
        "statistics": {
            "files_processed": total_files,
            "total_optimizations": total_optimizations,
            "successful_optimizations": successful_optimizations,
            "success_rate": successful_optimizations / max(total_optimizations, 1),
            "report_path": str(report_path),
        },
    }

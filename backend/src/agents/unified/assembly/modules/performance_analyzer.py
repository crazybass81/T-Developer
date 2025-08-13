"""
Performance Analyzer Module for Assembly Agent
Analyzes and optimizes project performance characteristics
"""

import ast
import asyncio
import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class PerformanceMetric:
    metric_name: str
    current_value: float
    target_value: float
    unit: str
    severity: str  # critical, warning, info
    recommendation: str


@dataclass
class PerformanceResult:
    success: bool
    performance_score: float
    metrics: List[PerformanceMetric]
    analysis_report: Dict[str, Any]
    optimizations_suggested: int
    processing_time: float
    error: str = ""


class PerformanceAnalyzer:
    """Advanced performance analysis system"""

    def __init__(self):
        self.version = "1.0.0"

        self.performance_thresholds = {
            "bundle_size_mb": {
                "react": {"target": 2.0, "warning": 5.0, "critical": 10.0},
                "vue": {"target": 1.5, "warning": 4.0, "critical": 8.0},
                "angular": {"target": 3.0, "warning": 6.0, "critical": 12.0},
            },
            "dependency_count": {"target": 20, "warning": 50, "critical": 100},
            "file_count": {"target": 50, "warning": 200, "critical": 500},
            "complexity_score": {"target": 5.0, "warning": 10.0, "critical": 20.0},
            "duplicate_code_percentage": {
                "target": 5.0,
                "warning": 15.0,
                "critical": 30.0,
            },
        }

        self.performance_patterns = {
            "inefficient_loops": [
                (r"for\s*\([^)]*\.length[^)]*\)", "Cache array length in loops"),
                (
                    r"while\s*\([^)]*\.length[^)]*\)",
                    "Cache array length in while loops",
                ),
                (
                    r"for\s*\([^)]*in\s+.*\)",
                    "Use for...of instead of for...in for arrays",
                ),
            ],
            "inefficient_dom": [
                (r"document\.getElementById", "Consider caching DOM elements"),
                (r"document\.querySelector", "Consider caching DOM selectors"),
                (
                    r"innerHTML\s*\+=",
                    "Use DocumentFragment for multiple DOM insertions",
                ),
            ],
            "memory_leaks": [
                (r"setInterval\s*\([^)]*\)", "Ensure intervals are cleared"),
                (r"addEventListener\s*\([^)]*\)", "Ensure event listeners are removed"),
                (r"new\s+\w+\s*\([^)]*\)", "Check for proper object cleanup"),
            ],
            "inefficient_css": [
                (r"\*\s*\{", "Avoid universal selector"),
                (r"\[id\^=", "Avoid complex attribute selectors"),
                (r"\w+\s+\w+\s+\w+\s+\w+", "Avoid deeply nested selectors"),
            ],
        }

    async def analyze_performance(
        self, validated_files: Dict[str, str], context: Dict[str, Any]
    ) -> PerformanceResult:
        """Analyze project performance characteristics"""

        start_time = datetime.now()
        metrics = []
        optimizations_suggested = 0

        try:
            framework = context.get("framework", "react")

            # Bundle size analysis
            bundle_metrics = await self._analyze_bundle_size(validated_files, framework)
            metrics.extend(bundle_metrics)

            # Code complexity analysis
            complexity_metrics = await self._analyze_code_complexity(validated_files)
            metrics.extend(complexity_metrics)

            # Dependency analysis
            dependency_metrics = await self._analyze_dependencies(validated_files)
            metrics.extend(dependency_metrics)

            # Performance patterns analysis
            pattern_metrics = await self._analyze_performance_patterns(validated_files)
            metrics.extend(pattern_metrics)

            # Resource optimization analysis
            resource_metrics = await self._analyze_resource_usage(validated_files)
            metrics.extend(resource_metrics)

            # Calculate overall performance score
            performance_score = self._calculate_performance_score(metrics)

            # Count optimization suggestions
            optimizations_suggested = len(
                [m for m in metrics if m.severity in ["critical", "warning"]]
            )

            # Generate analysis report
            analysis_report = {
                "framework": framework,
                "total_files_analyzed": len(validated_files),
                "performance_score": performance_score,
                "metrics_by_category": self._group_metrics_by_category(metrics),
                "top_recommendations": self._get_top_recommendations(metrics),
                "analysis_timestamp": datetime.now().isoformat(),
            }

            processing_time = (datetime.now() - start_time).total_seconds()

            return PerformanceResult(
                success=True,
                performance_score=performance_score,
                metrics=metrics,
                analysis_report=analysis_report,
                optimizations_suggested=optimizations_suggested,
                processing_time=processing_time,
            )

        except Exception as e:
            return PerformanceResult(
                success=False,
                performance_score=0.0,
                metrics=[],
                analysis_report={},
                optimizations_suggested=0,
                processing_time=(datetime.now() - start_time).total_seconds(),
                error=str(e),
            )

    async def _analyze_bundle_size(
        self, files: Dict[str, str], framework: str
    ) -> List[PerformanceMetric]:
        """Analyze bundle size and file structure"""

        metrics = []

        # Calculate total bundle size (estimated)
        total_size = sum(len(content.encode("utf-8")) for content in files.values())
        total_size_mb = total_size / (1024 * 1024)

        thresholds = self.performance_thresholds["bundle_size_mb"].get(
            framework, self.performance_thresholds["bundle_size_mb"]["react"]
        )

        severity = "info"
        if total_size_mb > thresholds["critical"]:
            severity = "critical"
        elif total_size_mb > thresholds["warning"]:
            severity = "warning"

        metrics.append(
            PerformanceMetric(
                metric_name="bundle_size",
                current_value=total_size_mb,
                target_value=thresholds["target"],
                unit="MB",
                severity=severity,
                recommendation=f"Optimize bundle size. Target: {thresholds['target']}MB",
            )
        )

        # Analyze file count
        file_count = len(files)
        file_thresholds = self.performance_thresholds["file_count"]

        file_severity = "info"
        if file_count > file_thresholds["critical"]:
            file_severity = "critical"
        elif file_count > file_thresholds["warning"]:
            file_severity = "warning"

        metrics.append(
            PerformanceMetric(
                metric_name="file_count",
                current_value=float(file_count),
                target_value=float(file_thresholds["target"]),
                unit="files",
                severity=file_severity,
                recommendation="Consider code splitting and modularization",
            )
        )

        # Analyze large files
        large_files = [
            (path, len(content)) for path, content in files.items() if len(content) > 10000
        ]  # Files > 10KB

        if large_files:
            largest_file_size = max(size for _, size in large_files) / 1024  # KB
            metrics.append(
                PerformanceMetric(
                    metric_name="largest_file_size",
                    current_value=largest_file_size,
                    target_value=50.0,  # 50KB target
                    unit="KB",
                    severity="warning" if largest_file_size > 100 else "info",
                    recommendation="Break down large files into smaller modules",
                )
            )

        return metrics

    async def _analyze_code_complexity(self, files: Dict[str, str]) -> List[PerformanceMetric]:
        """Analyze code complexity metrics"""

        metrics = []
        total_complexity = 0
        analyzed_files = 0

        for file_path, content in files.items():
            if file_path.endswith((".js", ".jsx", ".ts", ".tsx", ".py")):
                complexity = self._calculate_cyclomatic_complexity(content)
                total_complexity += complexity
                analyzed_files += 1

        if analyzed_files > 0:
            avg_complexity = total_complexity / analyzed_files
            complexity_thresholds = self.performance_thresholds["complexity_score"]

            severity = "info"
            if avg_complexity > complexity_thresholds["critical"]:
                severity = "critical"
            elif avg_complexity > complexity_thresholds["warning"]:
                severity = "warning"

            metrics.append(
                PerformanceMetric(
                    metric_name="average_complexity",
                    current_value=avg_complexity,
                    target_value=complexity_thresholds["target"],
                    unit="complexity score",
                    severity=severity,
                    recommendation="Refactor complex functions into smaller ones",
                )
            )

        return metrics

    async def _analyze_dependencies(self, files: Dict[str, str]) -> List[PerformanceMetric]:
        """Analyze dependency usage and optimization"""

        metrics = []

        if "package.json" in files:
            try:
                package_data = json.loads(files["package.json"])
                dependencies = package_data.get("dependencies", {})
                dev_dependencies = package_data.get("devDependencies", {})

                total_deps = len(dependencies) + len(dev_dependencies)
                dep_thresholds = self.performance_thresholds["dependency_count"]

                severity = "info"
                if total_deps > dep_thresholds["critical"]:
                    severity = "critical"
                elif total_deps > dep_thresholds["warning"]:
                    severity = "warning"

                metrics.append(
                    PerformanceMetric(
                        metric_name="dependency_count",
                        current_value=float(total_deps),
                        target_value=float(dep_thresholds["target"]),
                        unit="packages",
                        severity=severity,
                        recommendation="Review and remove unused dependencies",
                    )
                )

                # Check for heavy dependencies
                heavy_deps = ["moment", "lodash", "rxjs", "three"]
                found_heavy = [dep for dep in dependencies if dep in heavy_deps]

                if found_heavy:
                    metrics.append(
                        PerformanceMetric(
                            metric_name="heavy_dependencies",
                            current_value=float(len(found_heavy)),
                            target_value=0.0,
                            unit="packages",
                            severity="warning",
                            recommendation=f"Consider lighter alternatives for: {', '.join(found_heavy)}",
                        )
                    )

            except json.JSONDecodeError:
                pass

        return metrics

    async def _analyze_performance_patterns(self, files: Dict[str, str]) -> List[PerformanceMetric]:
        """Analyze code for performance anti-patterns"""

        metrics = []
        total_issues = 0

        for category, patterns in self.performance_patterns.items():
            category_issues = 0

            for file_path, content in files.items():
                for pattern, description in patterns:
                    matches = len(re.findall(pattern, content, re.MULTILINE))
                    category_issues += matches
                    total_issues += matches

            if category_issues > 0:
                severity = "warning" if category_issues > 5 else "info"
                metrics.append(
                    PerformanceMetric(
                        metric_name=f"{category}_issues",
                        current_value=float(category_issues),
                        target_value=0.0,
                        unit="issues",
                        severity=severity,
                        recommendation=f"Address {category.replace('_', ' ')} patterns",
                    )
                )

        return metrics

    async def _analyze_resource_usage(self, files: Dict[str, str]) -> List[PerformanceMetric]:
        """Analyze resource usage patterns"""

        metrics = []

        # Analyze CSS for unused rules (simplified)
        css_files = {k: v for k, v in files.items() if k.endswith(".css")}
        if css_files:
            total_css_rules = 0
            for content in css_files.values():
                # Count CSS rules (simplified)
                rules = len(re.findall(r"\{[^}]*\}", content))
                total_css_rules += rules

            if total_css_rules > 0:
                metrics.append(
                    PerformanceMetric(
                        metric_name="css_rules_count",
                        current_value=float(total_css_rules),
                        target_value=500.0,
                        unit="rules",
                        severity="warning" if total_css_rules > 1000 else "info",
                        recommendation="Consider CSS optimization and unused rule removal",
                    )
                )

        # Analyze image usage (if any referenced in code)
        image_references = 0
        for content in files.values():
            image_refs = len(re.findall(r"\.(jpg|jpeg|png|gif|webp|svg)", content, re.IGNORECASE))
            image_references += image_refs

        if image_references > 0:
            metrics.append(
                PerformanceMetric(
                    metric_name="image_references",
                    current_value=float(image_references),
                    target_value=20.0,
                    unit="images",
                    severity="info" if image_references < 50 else "warning",
                    recommendation="Optimize images and consider lazy loading",
                )
            )

        return metrics

    def _calculate_cyclomatic_complexity(self, code: str) -> float:
        """Calculate simplified cyclomatic complexity"""

        # Count decision points (simplified approach)
        decision_keywords = [
            "if",
            "elif",
            "else",
            "for",
            "while",
            "try",
            "except",
            "case",
            "switch",
        ]
        complexity = 1  # Base complexity

        for keyword in decision_keywords:
            pattern = rf"\b{keyword}\b"
            matches = len(re.findall(pattern, code, re.IGNORECASE))
            complexity += matches

        # Add complexity for logical operators
        logical_ops = ["&&", "||", "and", "or"]
        for op in logical_ops:
            matches = len(re.findall(re.escape(op), code))
            complexity += matches

        return float(complexity)

    def _calculate_performance_score(self, metrics: List[PerformanceMetric]) -> float:
        """Calculate overall performance score"""

        if not metrics:
            return 100.0

        total_penalty = 0
        for metric in metrics:
            if metric.severity == "critical":
                total_penalty += 20
            elif metric.severity == "warning":
                total_penalty += 10
            elif metric.severity == "info":
                total_penalty += 2

        score = max(0, 100 - total_penalty)
        return score

    def _group_metrics_by_category(self, metrics: List[PerformanceMetric]) -> Dict[str, List[Dict]]:
        """Group metrics by category"""

        categories = {}

        for metric in metrics:
            category = metric.metric_name.split("_")[0]
            if category not in categories:
                categories[category] = []

            categories[category].append(
                {
                    "name": metric.metric_name,
                    "current": metric.current_value,
                    "target": metric.target_value,
                    "unit": metric.unit,
                    "severity": metric.severity,
                }
            )

        return categories

    def _get_top_recommendations(
        self, metrics: List[PerformanceMetric], limit: int = 5
    ) -> List[str]:
        """Get top performance recommendations"""

        # Sort by severity and return top recommendations
        severity_order = {"critical": 0, "warning": 1, "info": 2}
        sorted_metrics = sorted(metrics, key=lambda m: severity_order.get(m.severity, 3))

        recommendations = []
        for metric in sorted_metrics[:limit]:
            recommendations.append(metric.recommendation)

        return recommendations

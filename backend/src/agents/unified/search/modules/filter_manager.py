"""
Filter Manager Module
Applies filters to search results with advanced filtering capabilities
"""

import re
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

from dateutil.parser import parse as parse_date


class FilterManager:
    """Advanced filtering system for search results"""

    def __init__(self):
        self.filter_types = {
            "category": self._apply_category_filter,
            "technology": self._apply_technology_filter,
            "tags": self._apply_tags_filter,
            "popularity": self._apply_popularity_filter,
            "quality": self._apply_quality_filter,
            "license": self._apply_license_filter,
            "date_range": self._apply_date_range_filter,
            "features": self._apply_features_filter,
            "size_range": self._apply_size_range_filter,
            "performance": self._apply_performance_filter,
            "maintenance": self._apply_maintenance_filter,
            "security": self._apply_security_filter,
            "compatibility": self._apply_compatibility_filter,
            "custom": self._apply_custom_filter,
        }

        # Predefined filter sets
        self.filter_presets = {
            "production_ready": {
                "quality": {"min": 7.0},
                "maintenance": {"status": "active"},
                "security": {"score": {"min": 6.0}},
            },
            "popular_only": {
                "popularity": {"min": 6.0},
                "tags": {"exclude": ["deprecated", "experimental"]},
            },
            "recent_only": {
                "date_range": {"after": "2023-01-01"},
                "maintenance": {"status": "active"},
            },
        }

    async def apply_filters(
        self, results: List[Dict[str, Any]], filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply all specified filters to results"""

        if not filters:
            return results

        filtered_results = results.copy()
        applied_filters = []
        filter_stats = {
            "initial_count": len(results),
            "filters_applied": [],
            "final_count": 0,
        }

        # Apply preset filters first
        if "preset" in filters:
            preset_name = filters["preset"]
            if preset_name in self.filter_presets:
                preset_filters = self.filter_presets[preset_name]
                for filter_name, filter_config in preset_filters.items():
                    if filter_name in self.filter_types:
                        before_count = len(filtered_results)
                        filtered_results = await self.filter_types[filter_name](
                            filtered_results, filter_config
                        )
                        after_count = len(filtered_results)

                        applied_filters.append(f"preset_{preset_name}_{filter_name}")
                        filter_stats["filters_applied"].append(
                            {
                                "name": f"preset_{filter_name}",
                                "before_count": before_count,
                                "after_count": after_count,
                                "filtered_out": before_count - after_count,
                            }
                        )

        # Apply individual filters
        for filter_name, filter_config in filters.items():
            if filter_name == "preset":
                continue

            if filter_name in self.filter_types:
                before_count = len(filtered_results)
                filtered_results = await self.filter_types[filter_name](
                    filtered_results, filter_config
                )
                after_count = len(filtered_results)

                applied_filters.append(filter_name)
                filter_stats["filters_applied"].append(
                    {
                        "name": filter_name,
                        "before_count": before_count,
                        "after_count": after_count,
                        "filtered_out": before_count - after_count,
                    }
                )

        filter_stats["final_count"] = len(filtered_results)

        # Add filter metadata to results
        for result in filtered_results:
            if "filter_metadata" not in result:
                result["filter_metadata"] = {}
            result["filter_metadata"]["applied_filters"] = applied_filters
            result["filter_metadata"]["stats"] = filter_stats

        return filtered_results

    async def _apply_category_filter(
        self, results: List[Dict[str, Any]], filter_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Filter by category"""

        if "include" in filter_config:
            included_categories = [cat.lower() for cat in filter_config["include"]]
            results = [r for r in results if r.get("category", "").lower() in included_categories]

        if "exclude" in filter_config:
            excluded_categories = [cat.lower() for cat in filter_config["exclude"]]
            results = [
                r for r in results if r.get("category", "").lower() not in excluded_categories
            ]

        if "pattern" in filter_config:
            pattern = re.compile(filter_config["pattern"], re.IGNORECASE)
            results = [r for r in results if pattern.search(r.get("category", ""))]

        return results

    async def _apply_technology_filter(
        self, results: List[Dict[str, Any]], filter_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Filter by technology/framework"""

        if "include" in filter_config:
            included_techs = [tech.lower() for tech in filter_config["include"]]
            results = [r for r in results if r.get("technology", "").lower() in included_techs]

        if "exclude" in filter_config:
            excluded_techs = [tech.lower() for tech in filter_config["exclude"]]
            results = [r for r in results if r.get("technology", "").lower() not in excluded_techs]

        if "version_range" in filter_config:
            # Filter by technology version if available
            version_filter = filter_config["version_range"]
            results = [r for r in results if self._check_version_compatibility(r, version_filter)]

        return results

    async def _apply_tags_filter(
        self, results: List[Dict[str, Any]], filter_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Filter by tags"""

        if "include_any" in filter_config:
            # Must have at least one of these tags
            required_tags = [tag.lower() for tag in filter_config["include_any"]]
            results = [
                r
                for r in results
                if any(
                    tag.lower() in [t.lower() for t in r.get("tags", [])] for tag in required_tags
                )
            ]

        if "include_all" in filter_config:
            # Must have all of these tags
            required_tags = [tag.lower() for tag in filter_config["include_all"]]
            results = [
                r
                for r in results
                if all(
                    tag.lower() in [t.lower() for t in r.get("tags", [])] for tag in required_tags
                )
            ]

        if "exclude" in filter_config:
            # Must not have any of these tags
            excluded_tags = [tag.lower() for tag in filter_config["exclude"]]
            results = [
                r
                for r in results
                if not any(
                    tag.lower() in [t.lower() for t in r.get("tags", [])] for tag in excluded_tags
                )
            ]

        return results

    async def _apply_popularity_filter(
        self, results: List[Dict[str, Any]], filter_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Filter by popularity metrics"""

        if "min" in filter_config:
            min_popularity = filter_config["min"]
            results = [r for r in results if r.get("popularity", 0) >= min_popularity]

        if "max" in filter_config:
            max_popularity = filter_config["max"]
            results = [r for r in results if r.get("popularity", 0) <= max_popularity]

        if "github_stars" in filter_config:
            stars_filter = filter_config["github_stars"]
            if "min" in stars_filter:
                min_stars = stars_filter["min"]
                results = [r for r in results if r.get("github_stars", 0) >= min_stars]

        if "downloads" in filter_config:
            downloads_filter = filter_config["downloads"]
            if "min" in downloads_filter:
                min_downloads = downloads_filter["min"]
                results = [
                    r
                    for r in results
                    if max(
                        r.get("npm_downloads", 0),
                        r.get("pypi_downloads", 0),
                        r.get("downloads", 0),
                    )
                    >= min_downloads
                ]

        return results

    async def _apply_quality_filter(
        self, results: List[Dict[str, Any]], filter_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Filter by quality metrics"""

        if "min" in filter_config:
            min_quality = filter_config["min"]
            results = [r for r in results if r.get("quality", 0) >= min_quality]

        if "max" in filter_config:
            max_quality = filter_config["max"]
            results = [r for r in results if r.get("quality", 0) <= max_quality]

        if "test_coverage" in filter_config:
            coverage_filter = filter_config["test_coverage"]
            if "min" in coverage_filter:
                min_coverage = coverage_filter["min"]
                results = [r for r in results if r.get("test_coverage", 0) >= min_coverage]

        if "documentation" in filter_config:
            doc_filter = filter_config["documentation"]
            if doc_filter.get("required", False):
                results = [
                    r
                    for r in results
                    if r.get("documentation") and len(str(r["documentation"])) > 0
                ]

        return results

    async def _apply_license_filter(
        self, results: List[Dict[str, Any]], filter_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Filter by license"""

        if "include" in filter_config:
            allowed_licenses = [lic.lower() for lic in filter_config["include"]]
            results = [r for r in results if r.get("license", "").lower() in allowed_licenses]

        if "exclude" in filter_config:
            excluded_licenses = [lic.lower() for lic in filter_config["exclude"]]
            results = [r for r in results if r.get("license", "").lower() not in excluded_licenses]

        if "commercial_use" in filter_config:
            # Filter by commercial use compatibility
            commercial_friendly = ["mit", "apache-2.0", "bsd-3-clause", "bsd-2-clause"]
            if filter_config["commercial_use"]:
                results = [
                    r for r in results if r.get("license", "").lower() in commercial_friendly
                ]

        return results

    async def _apply_date_range_filter(
        self, results: List[Dict[str, Any]], filter_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Filter by date range"""

        date_field = filter_config.get("field", "last_updated")

        if "after" in filter_config:
            after_date = self._parse_date(filter_config["after"])
            if after_date:
                results = [
                    r for r in results if self._get_component_date(r, date_field) >= after_date
                ]

        if "before" in filter_config:
            before_date = self._parse_date(filter_config["before"])
            if before_date:
                results = [
                    r for r in results if self._get_component_date(r, date_field) <= before_date
                ]

        if "last_n_days" in filter_config:
            cutoff_date = datetime.now() - timedelta(days=filter_config["last_n_days"])
            results = [r for r in results if self._get_component_date(r, date_field) >= cutoff_date]

        return results

    async def _apply_features_filter(
        self, results: List[Dict[str, Any]], filter_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Filter by features"""

        if "required" in filter_config:
            required_features = [feat.lower() for feat in filter_config["required"]]
            results = [
                r
                for r in results
                if all(
                    feat in [f.lower() for f in r.get("features", [])] for feat in required_features
                )
            ]

        if "preferred" in filter_config:
            # Score boost for preferred features (handled in ranking)
            preferred_features = [feat.lower() for feat in filter_config["preferred"]]
            for result in results:
                feature_matches = sum(
                    1
                    for feat in preferred_features
                    if feat in [f.lower() for f in result.get("features", [])]
                )
                result["feature_preference_score"] = feature_matches / len(preferred_features)

        if "exclude" in filter_config:
            excluded_features = [feat.lower() for feat in filter_config["exclude"]]
            results = [
                r
                for r in results
                if not any(
                    feat in [f.lower() for f in r.get("features", [])] for feat in excluded_features
                )
            ]

        return results

    async def _apply_size_range_filter(
        self, results: List[Dict[str, Any]], filter_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Filter by package size"""

        if "max_size_mb" in filter_config:
            max_size = filter_config["max_size_mb"] * 1024 * 1024  # Convert to bytes
            results = [r for r in results if r.get("package_size", 0) <= max_size]

        if "bundle_size" in filter_config:
            bundle_filter = filter_config["bundle_size"]
            if "max_kb" in bundle_filter:
                max_bundle = bundle_filter["max_kb"] * 1024
                results = [r for r in results if r.get("bundle_size", 0) <= max_bundle]

        return results

    async def _apply_performance_filter(
        self, results: List[Dict[str, Any]], filter_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Filter by performance metrics"""

        if "min_score" in filter_config:
            min_perf = filter_config["min_score"]
            results = [r for r in results if r.get("performance_score", 0) >= min_perf]

        if "benchmarks" in filter_config:
            benchmark_filter = filter_config["benchmarks"]
            for metric, threshold in benchmark_filter.items():
                results = [
                    r for r in results if r.get("benchmarks", {}).get(metric, 0) >= threshold
                ]

        return results

    async def _apply_maintenance_filter(
        self, results: List[Dict[str, Any]], filter_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Filter by maintenance status"""

        if "status" in filter_config:
            required_status = filter_config["status"].lower()
            results = [
                r for r in results if r.get("maintenance_status", "").lower() == required_status
            ]

        if "min_commit_frequency" in filter_config:
            # Filter by recent commit activity
            min_commits = filter_config["min_commit_frequency"]
            results = [r for r in results if r.get("recent_commits", 0) >= min_commits]

        if "active_maintainers" in filter_config:
            min_maintainers = filter_config["active_maintainers"]
            results = [r for r in results if r.get("active_maintainers", 0) >= min_maintainers]

        return results

    async def _apply_security_filter(
        self, results: List[Dict[str, Any]], filter_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Filter by security metrics"""

        if "score" in filter_config:
            score_filter = filter_config["score"]
            if "min" in score_filter:
                min_security = score_filter["min"]
                results = [r for r in results if r.get("security_score", 0) >= min_security]

        if "vulnerabilities" in filter_config:
            vuln_filter = filter_config["vulnerabilities"]
            if "max_critical" in vuln_filter:
                max_critical = vuln_filter["max_critical"]
                results = [
                    r for r in results if r.get("critical_vulnerabilities", 0) <= max_critical
                ]

        if "security_audit" in filter_config:
            if filter_config["security_audit"]:
                results = [r for r in results if r.get("security_audit_passed", False)]

        return results

    async def _apply_compatibility_filter(
        self, results: List[Dict[str, Any]], filter_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Filter by compatibility requirements"""

        if "node_version" in filter_config:
            node_version = filter_config["node_version"]
            results = [r for r in results if self._check_node_compatibility(r, node_version)]

        if "browser_support" in filter_config:
            browser_requirements = filter_config["browser_support"]
            results = [
                r for r in results if self._check_browser_compatibility(r, browser_requirements)
            ]

        if "python_version" in filter_config:
            python_version = filter_config["python_version"]
            results = [r for r in results if self._check_python_compatibility(r, python_version)]

        return results

    async def _apply_custom_filter(
        self, results: List[Dict[str, Any]], filter_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply custom filter function"""

        if "function" in filter_config:
            # Custom filter function provided
            filter_func = filter_config["function"]
            if callable(filter_func):
                results = [r for r in results if filter_func(r)]

        if "expression" in filter_config:
            # Custom filter expression
            expression = filter_config["expression"]
            results = [r for r in results if self._evaluate_filter_expression(r, expression)]

        return results

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object"""

        try:
            return parse_date(date_str)
        except (ValueError, TypeError):
            return None

    def _get_component_date(self, component: Dict[str, Any], field: str) -> datetime:
        """Get date from component field"""

        date_value = component.get(field)
        if not date_value:
            return datetime.min

        if isinstance(date_value, datetime):
            return date_value

        parsed_date = self._parse_date(str(date_value))
        return parsed_date if parsed_date else datetime.min

    def _check_version_compatibility(self, component: Dict[str, Any], version_range: str) -> bool:
        """Check if component version is compatible"""

        # Simplified version checking - in production use semantic versioning
        component_version = component.get("version", "1.0.0")

        # Basic range checking (e.g., ">=2.0.0", "<3.0.0")
        if version_range.startswith(">="):
            min_version = version_range[2:].strip()
            return component_version >= min_version
        elif version_range.startswith(">"):
            min_version = version_range[1:].strip()
            return component_version > min_version
        elif version_range.startswith("<="):
            max_version = version_range[2:].strip()
            return component_version <= max_version
        elif version_range.startswith("<"):
            max_version = version_range[1:].strip()
            return component_version < max_version
        else:
            return component_version == version_range

    def _check_node_compatibility(self, component: Dict[str, Any], node_version: str) -> bool:
        """Check Node.js compatibility"""

        supported_versions = component.get("node_versions", [])
        if not supported_versions:
            return True  # Assume compatible if not specified

        return node_version in supported_versions

    def _check_browser_compatibility(
        self, component: Dict[str, Any], browser_requirements: Dict[str, str]
    ) -> bool:
        """Check browser compatibility"""

        supported_browsers = component.get("browser_support", {})
        if not supported_browsers:
            return True  # Assume compatible if not specified

        for browser, min_version in browser_requirements.items():
            if browser not in supported_browsers:
                return False

            supported_version = supported_browsers[browser]
            if supported_version < min_version:
                return False

        return True

    def _check_python_compatibility(self, component: Dict[str, Any], python_version: str) -> bool:
        """Check Python compatibility"""

        supported_versions = component.get("python_versions", [])
        if not supported_versions:
            return True  # Assume compatible if not specified

        return any(python_version.startswith(v) for v in supported_versions)

    def _evaluate_filter_expression(self, component: Dict[str, Any], expression: str) -> bool:
        """Evaluate custom filter expression"""

        # Simple expression evaluator - in production use safe evaluation
        # For now, just check basic field conditions

        # Example: "popularity > 7 and quality >= 8"
        # This is a simplified implementation

        try:
            # Replace field references with actual values
            safe_expression = expression

            for field, value in component.items():
                if isinstance(value, (int, float)):
                    safe_expression = safe_expression.replace(field, str(value))
                elif isinstance(value, str):
                    safe_expression = safe_expression.replace(field, f"'{value}'")

            # Very basic evaluation - in production use ast.literal_eval or similar
            return eval(safe_expression)  # Note: Use safe evaluation in production

        except:
            return True  # Default to include if expression fails

    async def get_available_filter_options(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get available filter options based on current results"""

        if not results:
            return {}

        options = {
            "categories": list(set(r.get("category") for r in results if r.get("category"))),
            "technologies": list(set(r.get("technology") for r in results if r.get("technology"))),
            "licenses": list(set(r.get("license") for r in results if r.get("license"))),
            "tags": list(set(tag for r in results for tag in r.get("tags", []))),
            "popularity_range": {
                "min": min(r.get("popularity", 0) for r in results),
                "max": max(r.get("popularity", 0) for r in results),
            },
            "quality_range": {
                "min": min(r.get("quality", 0) for r in results),
                "max": max(r.get("quality", 0) for r in results),
            },
            "date_range": {
                "earliest": min(
                    self._get_component_date(r, "last_updated") for r in results
                ).isoformat(),
                "latest": max(
                    self._get_component_date(r, "last_updated") for r in results
                ).isoformat(),
            },
        }

        return options

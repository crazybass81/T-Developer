"""
Layout Optimizer Module
Optimizes layout structure for different screen sizes and use cases
"""

import math
from typing import Any, Dict, List, Tuple


class LayoutOptimizer:
    """Optimizes layout structures for optimal user experience"""

    def __init__(self):
        self.layout_patterns = {
            "holy_grail": {
                "structure": "header-sidebar-content-footer",
                "grid": "grid-template-areas",
                "suitable_for": ["dashboard", "admin", "application"],
                "responsive": True,
            },
            "two_column": {
                "structure": "sidebar-content",
                "grid": "grid-template-columns",
                "suitable_for": ["blog", "documentation", "news"],
                "responsive": True,
            },
            "single_column": {
                "structure": "header-content-footer",
                "grid": "flex-direction-column",
                "suitable_for": ["landing", "portfolio", "simple"],
                "responsive": True,
            },
            "masonry": {
                "structure": "dynamic-grid",
                "grid": "masonry",
                "suitable_for": ["gallery", "pinterest", "portfolio"],
                "responsive": True,
            },
            "split_screen": {
                "structure": "left-right",
                "grid": "grid-template-columns: 1fr 1fr",
                "suitable_for": ["comparison", "login", "showcase"],
                "responsive": False,
            },
            "card_based": {
                "structure": "grid-cards",
                "grid": "grid-auto-flow",
                "suitable_for": ["ecommerce", "catalog", "dashboard"],
                "responsive": True,
            },
            "timeline": {
                "structure": "vertical-timeline",
                "grid": "flex-direction-column",
                "suitable_for": ["history", "process", "roadmap"],
                "responsive": True,
            },
            "kanban": {
                "structure": "horizontal-columns",
                "grid": "grid-auto-columns",
                "suitable_for": ["project", "task", "workflow"],
                "responsive": False,
            },
        }

        self.grid_systems = {
            "12_column": {
                "columns": 12,
                "gutter": "24px",
                "margin": "24px",
                "breakpoints": {
                    "xs": {"width": 0, "columns": 4},
                    "sm": {"width": 600, "columns": 8},
                    "md": {"width": 960, "columns": 12},
                    "lg": {"width": 1280, "columns": 12},
                    "xl": {"width": 1920, "columns": 12},
                },
            },
            "16_column": {
                "columns": 16,
                "gutter": "16px",
                "margin": "16px",
                "breakpoints": {
                    "xs": {"width": 0, "columns": 4},
                    "sm": {"width": 600, "columns": 8},
                    "md": {"width": 960, "columns": 12},
                    "lg": {"width": 1280, "columns": 16},
                    "xl": {"width": 1920, "columns": 16},
                },
            },
            "fluid": {
                "columns": "auto",
                "gutter": "2%",
                "margin": "5%",
                "breakpoints": {
                    "mobile": {"width": 0, "columns": 1},
                    "tablet": {"width": 768, "columns": 2},
                    "desktop": {"width": 1024, "columns": 3},
                },
            },
        }

        self.spacing_systems = {
            "fibonacci": [0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89],
            "linear": [0, 4, 8, 12, 16, 20, 24, 32, 40, 48, 56, 64],
            "exponential": [0, 2, 4, 8, 16, 32, 64, 128],
            "material": [0, 4, 8, 16, 24, 32, 48, 64, 96],
        }

    def optimize(
        self, project_type: str, components: List[str], constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize layout for given requirements

        Args:
            project_type: Type of project
            components: List of components
            constraints: Layout constraints

        Returns:
            Optimized layout configuration
        """
        # Select base layout pattern
        layout_pattern = self._select_layout_pattern(project_type, components)

        # Select grid system
        grid_system = self._select_grid_system(layout_pattern, constraints)

        # Calculate optimal spacing
        spacing = self._calculate_spacing(components, grid_system)

        # Generate responsive behavior
        responsive_config = self._generate_responsive_config(
            layout_pattern, grid_system, constraints
        )

        # Optimize for performance
        performance_opts = self._optimize_performance(components, layout_pattern)

        # Calculate layout metrics
        metrics = self._calculate_metrics(layout_pattern, components)

        # Generate CSS Grid/Flexbox configuration
        css_config = self._generate_css_config(layout_pattern, grid_system)

        return {
            "pattern": layout_pattern,
            "grid": grid_system,
            "spacing": spacing,
            "responsive": responsive_config,
            "performance": performance_opts,
            "metrics": metrics,
            "css": css_config,
            "recommendations": self._generate_recommendations(
                layout_pattern, components, constraints
            ),
        }

    def _select_layout_pattern(self, project_type: str, components: List[str]) -> Dict[str, Any]:
        """Select optimal layout pattern"""
        # Map project types to layout patterns
        type_map = {
            "dashboard": "holy_grail",
            "blog": "two_column",
            "ecommerce": "card_based",
            "portfolio": "masonry",
            "landing": "single_column",
            "admin": "holy_grail",
            "todo": "two_column",
            "chat": "split_screen",
        }

        pattern_name = type_map.get(project_type, "single_column")

        # Check if components suggest different pattern
        if "Kanban" in components:
            pattern_name = "kanban"
        elif "Timeline" in components:
            pattern_name = "timeline"
        elif "Gallery" in components:
            pattern_name = "masonry"

        return self.layout_patterns[pattern_name]

    def _select_grid_system(
        self, layout: Dict[str, Any], constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Select appropriate grid system"""
        if constraints.get("mobile_first"):
            return self.grid_systems["fluid"]

        if layout["structure"] in ["holy_grail", "card_based"]:
            return self.grid_systems["12_column"]

        if layout["structure"] == "masonry":
            return self.grid_systems["fluid"]

        return self.grid_systems["12_column"]  # Default

    def _calculate_spacing(self, components: List[str], grid: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate optimal spacing"""
        # Determine density
        component_count = len(components)

        if component_count < 10:
            spacing_system = "material"  # Generous spacing
        elif component_count < 20:
            spacing_system = "linear"  # Moderate spacing
        else:
            spacing_system = "fibonacci"  # Compact spacing

        base_unit = 8  # Base spacing unit in pixels

        return {
            "system": spacing_system,
            "base_unit": base_unit,
            "scale": self.spacing_systems[spacing_system],
            "gutter": grid.get("gutter", "24px"),
            "margin": grid.get("margin", "24px"),
            "padding": {
                "small": f"{base_unit}px",
                "medium": f"{base_unit * 2}px",
                "large": f"{base_unit * 3}px",
            },
        }

    def _generate_responsive_config(
        self, layout: Dict[str, Any], grid: Dict[str, Any], constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate responsive configuration"""
        breakpoints = grid.get("breakpoints", {})

        responsive_config = {
            "breakpoints": breakpoints,
            "behavior": {},
            "visibility": {},
            "layout_changes": {},
        }

        # Define behavior at each breakpoint
        for bp_name, bp_config in breakpoints.items():
            width = bp_config.get("width", 0)

            # Mobile behavior
            if width < 768:
                responsive_config["behavior"][bp_name] = {
                    "navigation": "hamburger",
                    "sidebar": "hidden",
                    "columns": 1,
                    "stack_components": True,
                }
            # Tablet behavior
            elif width < 1024:
                responsive_config["behavior"][bp_name] = {
                    "navigation": "condensed",
                    "sidebar": "collapsible",
                    "columns": 2,
                    "stack_components": False,
                }
            # Desktop behavior
            else:
                responsive_config["behavior"][bp_name] = {
                    "navigation": "full",
                    "sidebar": "visible",
                    "columns": bp_config.get("columns", 3),
                    "stack_components": False,
                }

        return responsive_config

    def _optimize_performance(
        self, components: List[str], layout: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize layout for performance"""
        optimizations = {
            "lazy_loading": [],
            "virtualization": [],
            "code_splitting": [],
            "css_optimization": [],
        }

        # Determine what needs lazy loading
        if len(components) > 20:
            optimizations["lazy_loading"] = [
                "below-fold-content",
                "images",
                "heavy-components",
            ]

        # Check for virtualization needs
        if "Table" in components or "List" in components:
            optimizations["virtualization"] = ["long-lists", "data-tables"]

        # CSS optimizations
        optimizations["css_optimization"] = [
            "use-css-grid",
            "avoid-complex-selectors",
            "minimize-reflows",
            "use-transform-for-animations",
        ]

        return optimizations

    def _calculate_metrics(self, layout: Dict[str, Any], components: List[str]) -> Dict[str, Any]:
        """Calculate layout metrics"""
        # Calculate complexity score
        complexity = len(components) * 0.1

        if layout["structure"] in ["holy_grail", "masonry"]:
            complexity += 0.3

        # Calculate flexibility score
        flexibility = 0.5
        if layout.get("responsive", True):
            flexibility += 0.3
        if layout["grid"] in ["grid-template-areas", "grid-auto-flow"]:
            flexibility += 0.2

        return {
            "complexity_score": min(complexity, 1.0),
            "flexibility_score": flexibility,
            "maintainability_score": 1.0 - complexity,
            "estimated_css_lines": self._estimate_css_lines(layout, components),
            "render_cost": self._estimate_render_cost(components),
        }

    def _generate_css_config(self, layout: Dict[str, Any], grid: Dict[str, Any]) -> Dict[str, Any]:
        """Generate CSS configuration"""
        css_config = {
            "display": "grid" if "grid" in layout["grid"] else "flex",
            "container": {},
            "grid": {},
            "flex": {},
        }

        if css_config["display"] == "grid":
            css_config["grid"] = {
                "template_columns": self._generate_grid_columns(grid),
                "template_rows": "auto",
                "gap": grid.get("gutter", "24px"),
                "align_items": "start",
                "justify_content": "center",
            }

            if layout["structure"] == "holy_grail":
                css_config["grid"][
                    "template_areas"
                ] = """
                    "header header header"
                    "sidebar content aside"
                    "footer footer footer"
                """
        else:
            css_config["flex"] = {
                "direction": "row",
                "wrap": "wrap",
                "align_items": "stretch",
                "justify_content": "space-between",
            }

        return css_config

    def _generate_grid_columns(self, grid: Dict[str, Any]) -> str:
        """Generate CSS grid columns"""
        columns = grid.get("columns", 12)

        if columns == "auto":
            return "repeat(auto-fit, minmax(250px, 1fr))"
        else:
            return f"repeat({columns}, 1fr)"

    def _generate_recommendations(
        self, layout: Dict[str, Any], components: List[str], constraints: Dict[str, Any]
    ) -> List[str]:
        """Generate layout recommendations"""
        recommendations = []

        if len(components) > 30:
            recommendations.append("Consider breaking down into multiple pages")

        if not layout.get("responsive", True) and constraints.get("mobile_users"):
            recommendations.append("Consider using a responsive layout pattern")

        if "Table" in components:
            recommendations.append("Use horizontal scrolling for tables on mobile")

        if layout["structure"] == "holy_grail":
            recommendations.append("Implement collapsible sidebar for mobile")

        return recommendations

    def _estimate_css_lines(self, layout: Dict[str, Any], components: List[str]) -> int:
        """Estimate CSS lines needed"""
        base_css = 50  # Base layout CSS

        # Add for layout complexity
        if layout["structure"] in ["holy_grail", "masonry"]:
            base_css += 100
        else:
            base_css += 50

        # Add for components
        base_css += len(components) * 10

        # Add for responsive
        if layout.get("responsive", True):
            base_css += 150

        return base_css

    def _estimate_render_cost(self, components: List[str]) -> str:
        """Estimate render cost"""
        heavy_components = ["Chart", "Table", "Gallery", "Map", "Editor"]
        heavy_count = sum(1 for c in components if c in heavy_components)

        if heavy_count > 5:
            return "High"
        elif heavy_count > 2:
            return "Medium"
        else:
            return "Low"

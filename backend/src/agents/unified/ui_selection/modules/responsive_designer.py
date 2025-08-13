"""
Responsive Designer Module
Designs responsive layouts and breakpoints
"""

from typing import Dict, List, Any, Optional


class ResponsiveDesigner:
    """Designs responsive layouts for different screen sizes"""

    def __init__(self):
        self.breakpoints = {
            "mobile": {"min": 0, "max": 639, "columns": 4},
            "tablet": {"min": 640, "max": 1023, "columns": 8},
            "laptop": {"min": 1024, "max": 1279, "columns": 12},
            "desktop": {"min": 1280, "max": 1535, "columns": 12},
            "wide": {"min": 1536, "max": None, "columns": 12},
        }

        self.container_widths = {
            "mobile": "100%",
            "tablet": "640px",
            "laptop": "1024px",
            "desktop": "1280px",
            "wide": "1536px",
        }

        self.layout_strategies = {
            "mobile_first": {
                "approach": "min-width",
                "base": "mobile",
                "progressive": True,
            },
            "desktop_first": {
                "approach": "max-width",
                "base": "desktop",
                "progressive": False,
            },
            "adaptive": {"approach": "specific", "base": "all", "progressive": False},
        }

    def design(
        self, layout_type: str, components: List[str], strategy: str = "mobile_first"
    ) -> Dict[str, Any]:
        """Design responsive system"""

        # Select strategy
        responsive_strategy = self.layout_strategies.get(
            strategy, self.layout_strategies["mobile_first"]
        )

        # Configure breakpoints
        breakpoint_config = self._configure_breakpoints(layout_type, components)

        # Design grid system
        grid_system = self._design_grid_system(breakpoint_config)

        # Configure component behavior
        component_behavior = self._configure_component_behavior(
            components, breakpoint_config
        )

        # Generate media queries
        media_queries = self._generate_media_queries(
            breakpoint_config, responsive_strategy
        )

        # Create touch targets
        touch_targets = self._configure_touch_targets()

        # Generate CSS
        css = self._generate_responsive_css(
            breakpoint_config, grid_system, media_queries, component_behavior
        )

        return {
            "strategy": responsive_strategy,
            "breakpoints": breakpoint_config,
            "grid": grid_system,
            "component_behavior": component_behavior,
            "media_queries": media_queries,
            "touch_targets": touch_targets,
            "css": css,
            "guidelines": self._generate_guidelines(),
        }

    def _configure_breakpoints(self, layout_type: str, components: List[str]) -> Dict:
        """Configure breakpoints for project"""
        config = self.breakpoints.copy()

        # Adjust based on layout type
        if layout_type == "dashboard":
            # Dashboard needs more space
            config["tablet"]["min"] = 768
            config["laptop"]["min"] = 1280
        elif layout_type == "blog":
            # Blog can be narrower
            config["desktop"]["max"] = 1200

        return config

    def _design_grid_system(self, breakpoints: Dict) -> Dict:
        """Design responsive grid system"""
        return {
            "type": "flexbox-grid",
            "columns": {bp: config["columns"] for bp, config in breakpoints.items()},
            "gutters": {
                "mobile": "16px",
                "tablet": "24px",
                "laptop": "24px",
                "desktop": "32px",
                "wide": "32px",
            },
            "margins": {
                "mobile": "16px",
                "tablet": "32px",
                "laptop": "48px",
                "desktop": "64px",
                "wide": "auto",
            },
        }

    def _configure_component_behavior(
        self, components: List[str], breakpoints: Dict
    ) -> Dict:
        """Configure component responsive behavior"""
        behavior = {}

        for component in components:
            if component == "Navbar":
                behavior[component] = {
                    "mobile": "hamburger",
                    "tablet": "condensed",
                    "laptop": "full",
                    "desktop": "full",
                    "wide": "full",
                }
            elif component == "Sidebar":
                behavior[component] = {
                    "mobile": "hidden",
                    "tablet": "overlay",
                    "laptop": "collapsed",
                    "desktop": "expanded",
                    "wide": "expanded",
                }
            elif component == "Table":
                behavior[component] = {
                    "mobile": "cards",
                    "tablet": "horizontal-scroll",
                    "laptop": "full",
                    "desktop": "full",
                    "wide": "full",
                }
            elif component == "Grid":
                behavior[component] = {
                    "mobile": "1-column",
                    "tablet": "2-column",
                    "laptop": "3-column",
                    "desktop": "4-column",
                    "wide": "5-column",
                }
            else:
                behavior[component] = {
                    "mobile": "stacked",
                    "tablet": "responsive",
                    "laptop": "full",
                    "desktop": "full",
                    "wide": "full",
                }

        return behavior

    def _generate_media_queries(self, breakpoints: Dict, strategy: Dict) -> Dict:
        """Generate media query definitions"""
        queries = {}

        for name, config in breakpoints.items():
            if strategy["approach"] == "min-width":
                queries[name] = f"@media (min-width: {config['min']}px)"
            elif strategy["approach"] == "max-width":
                queries[name] = f"@media (max-width: {config['max']}px)"
            else:
                if config["max"]:
                    queries[
                        name
                    ] = f"@media (min-width: {config['min']}px) and (max-width: {config['max']}px)"
                else:
                    queries[name] = f"@media (min-width: {config['min']}px)"

        return queries

    def _configure_touch_targets(self) -> Dict:
        """Configure touch target sizes"""
        return {
            "minimum_size": "44px",
            "recommended_size": "48px",
            "spacing": "8px",
            "guidelines": [
                "Minimum 44x44px for touch targets",
                "Add padding to increase touch area",
                "Space targets at least 8px apart",
                "Consider thumb reach zones",
            ],
        }

    def _generate_responsive_css(
        self, breakpoints: Dict, grid: Dict, media_queries: Dict, behavior: Dict
    ) -> str:
        """Generate responsive CSS"""

        css = "/* Responsive Container */\n"
        css += ".container {\n"
        css += "  width: 100%;\n"
        css += "  margin: 0 auto;\n"
        css += "  padding: 0 16px;\n"
        css += "}\n\n"

        # Add breakpoint-specific styles
        for name, query in media_queries.items():
            css += f"{query} {{\n"
            css += f"  .container {{\n"
            css += f"    max-width: {self.container_widths.get(name, '100%')};\n"

            if name in grid["margins"]:
                css += f"    padding: 0 {grid['margins'][name]};\n"

            css += "  }\n"

            # Grid columns
            if name in grid["columns"]:
                css += f"  .grid {{\n"
                css += f"    grid-template-columns: repeat({grid['columns'][name]}, 1fr);\n"
                css += f"    gap: {grid['gutters'].get(name, '24px')};\n"
                css += "  }\n"

            # Component-specific
            for component, comp_behavior in behavior.items():
                if name in comp_behavior:
                    behavior_type = comp_behavior[name]

                    if component == "Navbar" and behavior_type == "hamburger":
                        css += "  .navbar-menu { display: none; }\n"
                        css += "  .navbar-hamburger { display: block; }\n"
                    elif component == "Sidebar" and behavior_type == "hidden":
                        css += "  .sidebar { display: none; }\n"
                    elif component == "Table" and behavior_type == "cards":
                        css += "  .table { display: block; }\n"
                        css += "  .table-row { display: block; margin-bottom: 16px; }\n"

            css += "}\n\n"

        # Utility classes
        css += self._generate_utility_classes(breakpoints)

        return css

    def _generate_utility_classes(self, breakpoints: Dict) -> str:
        """Generate responsive utility classes"""
        css = "/* Responsive Utilities */\n"

        for name in breakpoints.keys():
            css += f".{name}\\:hidden {{ display: none; }}\n"
            css += f".{name}\\:block {{ display: block; }}\n"
            css += f".{name}\\:inline-block {{ display: inline-block; }}\n"
            css += f".{name}\\:flex {{ display: flex; }}\n"
            css += f".{name}\\:grid {{ display: grid; }}\n"

        return css

    def _generate_guidelines(self) -> List[str]:
        """Generate responsive design guidelines"""
        return [
            "Design mobile-first for better performance",
            "Test on real devices, not just browser DevTools",
            "Consider thumb reach zones on mobile",
            "Ensure touch targets are at least 44x44px",
            "Use relative units (rem, %) for flexibility",
            "Test with different font sizes for accessibility",
            "Optimize images for different screen sizes",
            "Consider landscape orientation on mobile",
            "Test with slow network connections",
        ]

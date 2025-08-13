"""
Unified UI Selection Agent - Production Implementation
Selects appropriate UI components, layouts, and design patterns
"""

import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

# Unified base imports
from src.agents.unified.base import (
    UnifiedBaseAgent,
    AgentConfig,
    AgentContext,
    AgentResult,
)
from src.agents.unified.data_wrapper import (
    AgentInput,
    AgentContext,
    wrap_input,
    unwrap_result,
)


# Phase 2 imports - optional
try:
    from src.core.interfaces import AgentInput, ProcessingStatus
    from src.core.agent_models import UISelectionResult
    from src.core.event_bus import publish_agent_event, EventType

    CORE_IMPORTS_AVAILABLE = True
except ImportError:
    CORE_IMPORTS_AVAILABLE = False

    # Define dummy classes if needed
    class AgentInput:
        pass

    class ProcessingStatus:
        COMPLETED = "completed"
        FAILED = "failed"
        PROCESSING = "processing"

    @dataclass
    class UISelectionResult:
        components: List[str] = field(default_factory=list)
        styles: Dict[str, Any] = field(default_factory=dict)
        layout_structure: str = ""
        theme_config: Dict[str, Any] = field(default_factory=dict)
        responsive_config: Dict[str, Any] = field(default_factory=dict)
        accessibility_config: Dict[str, Any] = field(default_factory=dict)
        performance_considerations: List[str] = field(default_factory=list)
        confidence_score: float = 0.0

    class EventType:
        pass

    def publish_agent_event(*args, **kwargs):
        pass


import logging

logger = logging.getLogger(__name__)


@dataclass
class EnhancedUISelectionResult(UISelectionResult):
    """Extended UI Selection result with additional fields"""

    layout_type: str = "responsive"
    component_library: str = "custom"
    design_system: str = "modern"
    color_scheme: Dict[str, str] = field(default_factory=dict)
    typography: Dict[str, str] = field(default_factory=dict)
    animations: List[str] = field(default_factory=list)
    responsive_breakpoints: Dict[str, int] = field(default_factory=dict)
    accessibility_features: List[str] = field(default_factory=list)
    component_tree: Dict[str, Any] = field(default_factory=dict)
    interaction_patterns: List[str] = field(default_factory=list)
    navigation_type: str = "sidebar"
    form_validation: Dict[str, Any] = field(default_factory=dict)


class UnifiedUISelectionAgent(UnifiedBaseAgent):
    """
    Unified UI Selection Agent
    Analyzes requirements and selects appropriate UI components and patterns
    """

    def __init__(self, config: Optional[AgentConfig] = None, **kwargs):
        # Ignore extra kwargs that might come from pipeline
        if not config:
            config = AgentConfig(
                name="ui_selection",
                version="3.0.0",
                timeout=20,
                enable_monitoring=True,
                enable_caching=True,
            )

        super().__init__(config)

        # Component libraries
        self.component_libraries = {
            "material-ui": {
                "components": [
                    "Button",
                    "TextField",
                    "Card",
                    "AppBar",
                    "Drawer",
                    "Table",
                    "Dialog",
                ],
                "style": "material",
                "pros": ["comprehensive", "accessible", "theming"],
                "cons": ["large bundle", "opinionated"],
            },
            "ant-design": {
                "components": [
                    "Button",
                    "Input",
                    "Card",
                    "Layout",
                    "Menu",
                    "Table",
                    "Modal",
                ],
                "style": "enterprise",
                "pros": ["feature-rich", "form handling", "data components"],
                "cons": ["chinese defaults", "heavy"],
            },
            "chakra-ui": {
                "components": [
                    "Button",
                    "Input",
                    "Box",
                    "Stack",
                    "Grid",
                    "Modal",
                    "Toast",
                ],
                "style": "modern",
                "pros": ["modular", "accessible", "dark mode"],
                "cons": ["smaller ecosystem"],
            },
            "tailwind-ui": {
                "components": ["templates", "patterns"],
                "style": "utility",
                "pros": ["customizable", "small bundle", "fast"],
                "cons": ["no js components", "requires building"],
            },
            "custom": {
                "components": [],
                "style": "flexible",
                "pros": ["full control", "optimized"],
                "cons": ["time consuming", "maintenance"],
            },
        }

        # Layout patterns
        self.layout_patterns = {
            "dashboard": {
                "structure": "sidebar-content",
                "components": ["Sidebar", "Header", "MainContent", "Widgets"],
                "grid": "12-column",
                "suitable_for": ["admin", "analytics", "monitoring"],
            },
            "landing": {
                "structure": "sections",
                "components": ["Hero", "Features", "Testimonials", "CTA", "Footer"],
                "grid": "container",
                "suitable_for": ["marketing", "product", "company"],
            },
            "application": {
                "structure": "header-content-footer",
                "components": ["Navbar", "MainArea", "Footer"],
                "grid": "flexible",
                "suitable_for": ["saas", "tools", "platforms"],
            },
            "ecommerce": {
                "structure": "catalog-detail",
                "components": ["ProductGrid", "Filters", "Cart", "Checkout"],
                "grid": "responsive",
                "suitable_for": ["shop", "marketplace"],
            },
            "blog": {
                "structure": "content-sidebar",
                "components": ["PostList", "Article", "Sidebar", "Comments"],
                "grid": "2-column",
                "suitable_for": ["blog", "news", "magazine"],
            },
            "chat": {
                "structure": "three-panel",
                "components": ["UserList", "MessageArea", "InputArea"],
                "grid": "flex",
                "suitable_for": ["messaging", "support", "communication"],
            },
        }

        # Design systems
        self.design_systems = {
            "material": {
                "principles": ["depth", "motion", "bold"],
                "spacing": [4, 8, 16, 24, 32, 48],
                "shadows": True,
                "rounded": "medium",
            },
            "flat": {
                "principles": ["minimal", "clean", "simple"],
                "spacing": [8, 16, 24, 32, 48],
                "shadows": False,
                "rounded": "none",
            },
            "neumorphic": {
                "principles": ["soft", "extruded", "tactile"],
                "spacing": [12, 24, 36, 48],
                "shadows": "soft",
                "rounded": "large",
            },
            "glassmorphic": {
                "principles": ["transparent", "blur", "modern"],
                "spacing": [8, 16, 24, 32],
                "shadows": "colored",
                "rounded": "large",
            },
            "modern": {
                "principles": ["clean", "functional", "accessible"],
                "spacing": [8, 16, 24, 32, 48],
                "shadows": "subtle",
                "rounded": "small",
            },
        }

        # Color schemes
        self.color_schemes = {
            "blue": {
                "primary": "#3B82F6",
                "secondary": "#10B981",
                "accent": "#F59E0B",
                "neutral": "#6B7280",
                "base": "#FFFFFF",
            },
            "purple": {
                "primary": "#8B5CF6",
                "secondary": "#EC4899",
                "accent": "#F59E0B",
                "neutral": "#6B7280",
                "base": "#FFFFFF",
            },
            "dark": {
                "primary": "#3B82F6",
                "secondary": "#10B981",
                "accent": "#F59E0B",
                "neutral": "#9CA3AF",
                "base": "#111827",
            },
            "monochrome": {
                "primary": "#000000",
                "secondary": "#4B5563",
                "accent": "#000000",
                "neutral": "#9CA3AF",
                "base": "#FFFFFF",
            },
        }

    def log_info(self, message: str):
        """Log info message"""
        if hasattr(self, "logger"):
            self.logger.info(message)
        else:
            print(f"INFO: {message}")

    def log_error(self, message: str):
        """Log error message"""
        if hasattr(self, "logger"):
            self.logger.error(message)
        else:
            print(f"ERROR: {message}")

    def log_warning(self, message: str):
        """Log warning message"""
        if hasattr(self, "logger"):
            self.logger.warning(message)
        else:
            print(f"WARNING: {message}")

    async def _custom_initialize(self):
        """Initialize UI Selection specific resources"""
        self.logger.info("UI Selection Agent initialization complete")

    async def process(self, input_data) -> AgentResult[EnhancedUISelectionResult]:
        """Process UI selection - accepts dict or AgentInput"""

        try:
            # Handle both dict and AgentInput
            if isinstance(input_data, dict):
                data = input_data
            elif hasattr(input_data, "data"):
                data = input_data.data
            else:
                data = {"data": input_data}

            # Extract NL analysis result
            nl_result = data.get("nl_result", {})
            project_type = nl_result.get(
                "project_type", data.get("project_type", "web_application")
            )
            features = nl_result.get("features", data.get("features", []))
            preferences = nl_result.get("preferences", data.get("preferences", {}))
            constraints = nl_result.get("constraints", data.get("constraints", []))
            complexity = nl_result.get("complexity", data.get("complexity", "medium"))

            # Process UI selection
            result = await self._select_ui_components(
                project_type, features, preferences, constraints, complexity
            )

            # Publish event (optional - may not be available)
            try:
                if hasattr(input_data, "context") and input_data.context:
                    await publish_agent_event(
                        EventType.AGENT_COMPLETED,
                        self.config.name,
                        input_data.context.pipeline_id
                        if hasattr(input_data.context, "pipeline_id")
                        else "unknown",
                        {
                            "components_selected": len(result.components),
                            "layout_type": result.layout_type,
                            "design_system": result.design_system,
                        },
                    )
            except Exception as e:
                # Event publishing is optional, don't fail the agent
                logger.debug(f"Could not publish event: {e}")

            return AgentResult(
                success=True,
                data=result,
                status=ProcessingStatus.COMPLETED,
                agent_name=self.config.name,
                agent_version=self.config.version,
                confidence=result.confidence_score,
            )

        except Exception as e:
            logger.error(f"UI Selection Agent error: {e}")

            return AgentResult(
                success=False,
                error=str(e),
                status=ProcessingStatus.FAILED,
                agent_name=self.config.name,
                agent_version=self.config.version,
            )

    async def _process_internal(
        self, input_data: Dict[str, Any], context: AgentContext
    ) -> AgentResult:
        """Process for ECS mode"""
        nl_result = input_data.get("nl_result", {})

        result = await self._select_ui_components(
            nl_result.get("project_type", "web_application"),
            nl_result.get("features", []),
            nl_result.get("preferences", {}),
            nl_result.get("constraints", []),
            nl_result.get("complexity", "medium"),
        )

        return AgentResult(
            success=True,
            data=result,
            status=ProcessingStatus.COMPLETED,
            agent_name=self.config.name,
            confidence=result.confidence_score,
        )

    async def _select_ui_components(
        self,
        project_type: str,
        features: List[str],
        preferences: Dict[str, str],
        constraints: List[str],
        complexity: str,
    ) -> EnhancedUISelectionResult:
        """Core UI selection logic"""

        # Select layout pattern
        layout = self._select_layout(project_type)

        # Select component library
        library = self._select_component_library(features, constraints, complexity)

        # Select design system
        design_system = self._select_design_system(preferences)

        # Select color scheme
        color_scheme = self._select_color_scheme(preferences)

        # Generate component list
        components = self._generate_component_list(
            project_type, features, layout, library
        )

        # Generate styling approach
        styles = self._generate_styles(design_system, color_scheme)

        # Create component tree
        component_tree = self._create_component_tree(layout, components, project_type)

        # Select interaction patterns
        interactions = self._select_interaction_patterns(features, project_type)

        # Configure responsive design
        breakpoints = self._configure_breakpoints(preferences)

        # Configure accessibility
        accessibility = self._configure_accessibility(constraints)

        # Calculate confidence
        confidence = self._calculate_confidence(
            len(components), library != "custom", len(accessibility)
        )

        return EnhancedUISelectionResult(
            components=components,
            styles=styles,
            layout_structure=layout["structure"],
            theme_config={
                "design_system": design_system,
                "color_scheme": color_scheme,
                "library": library,
            },
            responsive_config=breakpoints,
            accessibility_config={"features": accessibility},
            performance_considerations=self._get_performance_considerations(
                library, len(components)
            ),
            confidence_score=confidence,
            layout_type=layout["structure"],
            component_library=library,
            design_system=design_system,
            color_scheme=color_scheme,
            typography=self._select_typography(design_system),
            animations=self._select_animations(preferences, complexity),
            responsive_breakpoints=breakpoints,
            accessibility_features=accessibility,
            component_tree=component_tree,
            interaction_patterns=interactions,
            navigation_type=self._select_navigation_type(project_type),
            form_validation=self._configure_form_validation(features),
        )

    def _select_layout(self, project_type: str) -> Dict[str, Any]:
        """Select appropriate layout pattern"""
        # Map project types to layouts
        layout_map = {
            "todo": "application",
            "blog": "blog",
            "ecommerce": "ecommerce",
            "dashboard": "dashboard",
            "chat": "chat",
            "portfolio": "landing",
            "social": "application",
            "saas": "application",
        }

        layout_name = layout_map.get(project_type, "application")
        return self.layout_patterns[layout_name]

    def _select_component_library(
        self, features: List[str], constraints: List[str], complexity: str
    ) -> str:
        """Select appropriate component library"""

        # Check constraints
        if "Budget conscious" in constraints:
            return "custom"  # Build custom to save on licensing

        if "No dependencies" in constraints:
            return "custom"

        # Based on complexity
        if complexity == "simple":
            return "tailwind-ui"  # Simple and fast
        elif complexity == "complex":
            if "enterprise" in str(features).lower():
                return "ant-design"
            else:
                return "material-ui"

        # Based on features
        if "chart" in features or "dashboard" in features:
            return "ant-design"  # Best for data-heavy apps

        if "accessibility" in features:
            return "chakra-ui"  # Best accessibility

        return "custom"  # Default to custom for flexibility

    def _select_design_system(self, preferences: Dict[str, str]) -> str:
        """Select design system based on preferences"""
        style = preferences.get("style", "modern")

        style_map = {
            "minimalist": "flat",
            "modern": "modern",
            "professional": "material",
            "colorful": "modern",
            "dark_mode": "modern",
        }

        return style_map.get(style, "modern")

    def _select_color_scheme(self, preferences: Dict[str, str]) -> Dict[str, str]:
        """Select color scheme"""
        theme = preferences.get("theme", "light_mode")

        if theme == "dark_mode":
            return self.color_schemes["dark"]

        # Select based on style preference
        style = preferences.get("style", "modern")
        if style == "professional":
            return self.color_schemes["blue"]
        elif style == "colorful":
            return self.color_schemes["purple"]
        elif style == "minimalist":
            return self.color_schemes["monochrome"]

        return self.color_schemes["blue"]  # Default

    def _generate_component_list(
        self, project_type: str, features: List[str], layout: Dict, library: str
    ) -> List[str]:
        """Generate list of UI components needed"""
        components = []

        # Add layout components
        components.extend(layout["components"])

        # Add feature-specific components
        component_map = {
            "auth": ["LoginForm", "RegisterForm", "ProfileCard"],
            "search": ["SearchBar", "FilterPanel", "ResultsList"],
            "payment": ["PaymentForm", "OrderSummary", "BillingAddress"],
            "chart": ["LineChart", "BarChart", "PieChart", "DataTable"],
            "upload": ["FileUploader", "ImagePreview", "ProgressBar"],
            "notification": ["NotificationBell", "Toast", "Alert"],
            "map": ["MapView", "LocationPicker", "MarkerList"],
            "realtime": ["StatusIndicator", "LiveFeed", "PresenceBadge"],
            "email": ["EmailComposer", "InboxList", "MessageView"],
            "calendar": ["Calendar", "DatePicker", "EventList"],
        }

        for feature in features:
            if feature in component_map:
                components.extend(component_map[feature])

        # Add common components
        common = ["Button", "Input", "Card", "Modal", "Dropdown", "Tabs"]
        components.extend(common)

        # Remove duplicates
        return list(dict.fromkeys(components))

    def _generate_styles(
        self, design_system: str, color_scheme: Dict[str, str]
    ) -> Dict[str, Any]:
        """Generate styling configuration"""
        system = self.design_systems[design_system]

        return {
            "colors": color_scheme,
            "spacing": system["spacing"],
            "borderRadius": {
                "none": "0",
                "small": "4px",
                "medium": "8px",
                "large": "16px",
            }.get(system["rounded"], "4px"),
            "shadows": self._generate_shadows(system["shadows"]),
            "transitions": {"fast": "150ms", "normal": "250ms", "slow": "350ms"},
        }

    def _generate_shadows(self, shadow_type) -> Dict[str, str]:
        """Generate shadow definitions"""
        if not shadow_type or shadow_type == False:
            return {}

        if shadow_type == "soft":
            return {
                "sm": "0 2px 4px rgba(0,0,0,0.05)",
                "md": "0 4px 8px rgba(0,0,0,0.08)",
                "lg": "0 8px 16px rgba(0,0,0,0.1)",
            }
        elif shadow_type == "colored":
            return {
                "sm": "0 2px 4px rgba(59,130,246,0.1)",
                "md": "0 4px 8px rgba(59,130,246,0.15)",
                "lg": "0 8px 16px rgba(59,130,246,0.2)",
            }
        else:  # subtle
            return {
                "sm": "0 1px 2px rgba(0,0,0,0.05)",
                "md": "0 2px 4px rgba(0,0,0,0.06)",
                "lg": "0 4px 6px rgba(0,0,0,0.07)",
            }

    def _create_component_tree(
        self, layout: Dict, components: List[str], project_type: str
    ) -> Dict[str, Any]:
        """Create hierarchical component structure"""
        tree = {"root": "App", "children": []}

        # Create layout structure
        if layout["structure"] == "sidebar-content":
            tree["children"] = [
                {
                    "name": "Layout",
                    "children": [
                        {"name": "Sidebar", "children": ["Navigation", "UserProfile"]},
                        {
                            "name": "MainContent",
                            "children": self._get_content_components(project_type),
                        },
                    ],
                }
            ]
        elif layout["structure"] == "header-content-footer":
            tree["children"] = [
                {"name": "Header", "children": ["Logo", "Navigation", "UserMenu"]},
                {
                    "name": "Main",
                    "children": self._get_content_components(project_type),
                },
                {"name": "Footer", "children": ["Links", "Copyright"]},
            ]

        return tree

    def _get_content_components(self, project_type: str) -> List[Dict]:
        """Get content area components for project type"""
        content_map = {
            "todo": [{"name": "TodoList"}, {"name": "TodoForm"}, {"name": "FilterBar"}],
            "blog": [
                {"name": "PostList"},
                {"name": "PostDetail"},
                {"name": "CommentSection"},
            ],
            "ecommerce": [
                {"name": "ProductGrid"},
                {"name": "ProductDetail"},
                {"name": "ShoppingCart"},
            ],
            "dashboard": [
                {"name": "StatsOverview"},
                {"name": "Charts"},
                {"name": "DataTable"},
            ],
        }

        return content_map.get(project_type, [{"name": "ContentArea"}])

    def _select_interaction_patterns(
        self, features: List[str], project_type: str
    ) -> List[str]:
        """Select interaction patterns"""
        patterns = []

        # Feature-based patterns
        if "realtime" in features:
            patterns.extend(["websocket", "polling", "server-sent-events"])

        if "drag" in str(features).lower() or project_type == "todo":
            patterns.append("drag-and-drop")

        if "search" in features:
            patterns.extend(["instant-search", "autocomplete", "filters"])

        if "upload" in features:
            patterns.extend(["file-drop", "progress-indication"])

        # Common patterns
        patterns.extend(["hover-effects", "loading-states", "error-handling"])

        return list(dict.fromkeys(patterns))

    def _configure_breakpoints(self, preferences: Dict) -> Dict[str, int]:
        """Configure responsive breakpoints"""
        return {
            "mobile": 640,
            "tablet": 768,
            "laptop": 1024,
            "desktop": 1280,
            "wide": 1536,
        }

    def _configure_accessibility(self, constraints: List[str]) -> List[str]:
        """Configure accessibility features"""
        features = ["semantic-html", "aria-labels", "keyboard-navigation"]

        # Check for specific requirements
        for constraint in constraints:
            if "accessibility" in constraint.lower() or "a11y" in constraint.lower():
                features.extend(
                    [
                        "screen-reader-support",
                        "high-contrast-mode",
                        "focus-indicators",
                        "skip-links",
                        "alt-text",
                    ]
                )
                break

        return features

    def _select_typography(self, design_system: str) -> Dict[str, str]:
        """Select typography settings"""
        typography_map = {
            "material": {"heading": "Roboto", "body": "Roboto", "mono": "Roboto Mono"},
            "modern": {"heading": "Inter", "body": "Inter", "mono": "JetBrains Mono"},
            "flat": {"heading": "system-ui", "body": "system-ui", "mono": "monospace"},
        }

        return typography_map.get(design_system, typography_map["modern"])

    def _select_animations(self, preferences: Dict, complexity: str) -> List[str]:
        """Select animation types"""
        if complexity == "simple":
            return ["fade", "slide"]

        animations = ["fade", "slide", "scale", "rotate"]

        if preferences.get("style") == "modern":
            animations.extend(["parallax", "stagger", "morph"])

        return animations

    def _select_navigation_type(self, project_type: str) -> str:
        """Select navigation pattern"""
        nav_map = {
            "dashboard": "sidebar",
            "ecommerce": "mega-menu",
            "blog": "header",
            "chat": "tabbed",
            "mobile": "bottom-tabs",
        }

        return nav_map.get(project_type, "header")

    def _configure_form_validation(self, features: List[str]) -> Dict[str, Any]:
        """Configure form validation rules"""
        if "auth" not in features and "form" not in str(features).lower():
            return {}

        return {
            "email": {
                "pattern": r"^[^\s@]+@[^\s@]+\.[^\s@]+$",
                "message": "Invalid email format",
            },
            "password": {
                "minLength": 8,
                "pattern": r"^(?=.*[A-Za-z])(?=.*\d)",
                "message": "Password must be 8+ chars with letters and numbers",
            },
            "required": {"rule": "notEmpty", "message": "This field is required"},
        }

    def _get_performance_considerations(
        self, library: str, component_count: int
    ) -> List[str]:
        """Get performance considerations"""
        considerations = []

        if library in ["material-ui", "ant-design"]:
            considerations.append("Use tree-shaking to reduce bundle size")

        if component_count > 20:
            considerations.append("Consider code splitting")
            considerations.append("Implement lazy loading")

        considerations.extend(
            [
                "Optimize images and assets",
                "Minimize re-renders",
                "Use production builds",
            ]
        )

        return considerations

    def _calculate_confidence(
        self, component_count: int, using_library: bool, accessibility_count: int
    ) -> float:
        """Calculate confidence score"""
        confidence = 0.6  # Base

        if component_count > 10:
            confidence += 0.1

        if using_library:
            confidence += 0.15

        if accessibility_count > 3:
            confidence += 0.1

        return min(confidence, 0.95)


# Export the agent
__all__ = ["UnifiedUISelectionAgent", "EnhancedUISelectionResult"]

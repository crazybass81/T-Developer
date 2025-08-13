"""
Design System Selector Module
Selects and configures appropriate design systems
"""

from typing import Dict, List, Any, Optional


class DesignSystemSelector:
    """Selects and configures design systems for projects"""

    def __init__(self):
        self.design_systems = {
            "material_design": {
                "name": "Material Design",
                "version": "3.0",
                "principles": [
                    "Material metaphor",
                    "Bold intentional",
                    "Motion meaning",
                ],
                "components": self._get_material_components(),
                "tokens": self._get_material_tokens(),
                "suitable_for": ["enterprise", "dashboard", "admin", "android"],
                "pros": ["Comprehensive", "Well-documented", "Accessible"],
                "cons": ["Can feel generic", "Heavy"],
                "libraries": ["@mui/material", "vuetify", "angular-material"],
            },
            "ant_design": {
                "name": "Ant Design",
                "version": "5.0",
                "principles": ["Natural", "Certain", "Meaningful", "Growing"],
                "components": self._get_ant_components(),
                "tokens": self._get_ant_tokens(),
                "suitable_for": ["enterprise", "dashboard", "data-heavy", "b2b"],
                "pros": ["Feature-rich", "Great for forms", "Data components"],
                "cons": ["Chinese-oriented", "Large bundle"],
                "libraries": ["antd", "@ant-design/pro-components"],
            },
            "carbon": {
                "name": "Carbon Design System",
                "version": "11.0",
                "principles": ["Productive", "Natural", "Lightweight"],
                "components": self._get_carbon_components(),
                "tokens": self._get_carbon_tokens(),
                "suitable_for": ["enterprise", "ibm", "data-viz", "professional"],
                "pros": ["Accessible", "Professional", "Consistent"],
                "cons": ["Corporate feel", "Limited customization"],
                "libraries": ["carbon-components-react", "@carbon/web-components"],
            },
            "fluent": {
                "name": "Fluent Design",
                "version": "2.0",
                "principles": ["Light", "Depth", "Motion", "Material", "Scale"],
                "components": self._get_fluent_components(),
                "tokens": self._get_fluent_tokens(),
                "suitable_for": ["microsoft", "windows", "office", "teams"],
                "pros": ["Modern", "Cross-platform", "Animated"],
                "cons": ["Microsoft-specific", "Complex"],
                "libraries": ["@fluentui/react", "@fluentui/web-components"],
            },
            "spectrum": {
                "name": "Spectrum Design",
                "version": "1.0",
                "principles": ["Rational", "Human", "Focused"],
                "components": self._get_spectrum_components(),
                "tokens": self._get_spectrum_tokens(),
                "suitable_for": ["creative", "adobe", "design-tools"],
                "pros": ["Creative-focused", "Flexible", "Modern"],
                "cons": ["Adobe-centric", "Less common"],
                "libraries": ["@adobe/react-spectrum"],
            },
            "custom": {
                "name": "Custom Design System",
                "version": "1.0",
                "principles": ["Brand-aligned", "Flexible", "Optimized"],
                "components": [],
                "tokens": {},
                "suitable_for": ["unique", "branded", "specific"],
                "pros": ["Full control", "Brand-specific", "Optimized"],
                "cons": ["Time-consuming", "Maintenance"],
                "libraries": [],
            },
        }

        self.evaluation_criteria = [
            "consistency",
            "accessibility",
            "performance",
            "documentation",
            "community",
            "customization",
            "learning_curve",
        ]

    def select(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Select appropriate design system

        Args:
            requirements: Project requirements

        Returns:
            Selected design system configuration
        """
        project_type = requirements.get("project_type", "")
        features = requirements.get("features", [])
        preferences = requirements.get("preferences", {})
        constraints = requirements.get("constraints", [])
        brand = requirements.get("brand", {})

        # Evaluate each design system
        scores = self._evaluate_systems(
            project_type, features, preferences, constraints
        )

        # Select best match
        selected_name = max(scores, key=scores.get)
        selected_system = self.design_systems[selected_name]

        # Customize for project
        customized = self._customize_system(selected_system, requirements, brand)

        # Generate implementation guide
        implementation = self._generate_implementation(customized, requirements)

        return {
            "system": customized,
            "score": scores[selected_name],
            "alternatives": self._get_alternatives(scores),
            "implementation": implementation,
            "tokens": self._generate_design_tokens(customized, brand),
            "components": self._map_components(customized, requirements),
        }

    def _evaluate_systems(
        self,
        project_type: str,
        features: List[str],
        preferences: Dict[str, Any],
        constraints: List[str],
    ) -> Dict[str, float]:
        """Evaluate design systems against requirements"""
        scores = {}

        for name, system in self.design_systems.items():
            score = 0.0

            # Check suitability
            if project_type in system["suitable_for"]:
                score += 0.3

            # Check feature support
            feature_support = self._check_feature_support(features, system)
            score += feature_support * 0.3

            # Check constraints
            if "Budget conscious" in constraints and name == "custom":
                score -= 0.2  # Custom is expensive

            if "Fast development" in constraints and name != "custom":
                score += 0.2  # Pre-built is faster

            # Check preferences
            if preferences.get("style") == "professional" and name in [
                "material_design",
                "carbon",
            ]:
                score += 0.1

            if preferences.get("style") == "modern" and name in ["fluent", "spectrum"]:
                score += 0.1

            scores[name] = min(score, 1.0)

        return scores

    def _check_feature_support(self, features: List[str], system: Dict) -> float:
        """Check how well system supports required features"""
        supported = 0
        total = len(features)

        if total == 0:
            return 0.5

        feature_map = {
            "chart": ["data-viz", "dashboard"],
            "form": ["enterprise", "admin"],
            "auth": ["enterprise", "admin"],
            "realtime": ["modern", "dashboard"],
        }

        for feature in features:
            if feature in feature_map:
                for suitable in feature_map[feature]:
                    if suitable in system["suitable_for"]:
                        supported += 1
                        break

        return supported / total

    def _customize_system(
        self, system: Dict, requirements: Dict, brand: Dict
    ) -> Dict[str, Any]:
        """Customize design system for project"""
        customized = system.copy()

        # Override with brand colors if provided
        if brand.get("colors"):
            if "tokens" not in customized:
                customized["tokens"] = {}
            customized["tokens"]["colors"] = brand["colors"]

        # Adjust for project type
        project_type = requirements.get("project_type")
        if project_type == "dashboard":
            customized["focus"] = "data-visualization"
        elif project_type == "ecommerce":
            customized["focus"] = "product-showcase"

        return customized

    def _generate_implementation(
        self, system: Dict, requirements: Dict
    ) -> Dict[str, Any]:
        """Generate implementation guide"""
        return {
            "setup": self._get_setup_steps(system),
            "configuration": self._get_configuration(system, requirements),
            "customization": self._get_customization_guide(system),
            "best_practices": self._get_best_practices(system),
            "migration_path": self._get_migration_path(system),
        }

    def _generate_design_tokens(self, system: Dict, brand: Dict) -> Dict[str, Any]:
        """Generate design tokens"""
        base_tokens = system.get("tokens", {})

        # Merge with brand tokens
        if brand:
            for key, value in brand.items():
                if key in base_tokens:
                    base_tokens[key].update(value)
                else:
                    base_tokens[key] = value

        return base_tokens

    def _map_components(self, system: Dict, requirements: Dict) -> List[Dict]:
        """Map required components to design system components"""
        mappings = []

        # Get required components from requirements
        required_components = requirements.get("components", [])
        system_components = system.get("components", [])

        for required in required_components:
            # Find matching system component
            match = self._find_component_match(required, system_components)
            mappings.append(
                {
                    "required": required,
                    "system": match,
                    "customization_needed": match is None,
                }
            )

        return mappings

    def _get_alternatives(self, scores: Dict[str, float]) -> List[Dict]:
        """Get alternative design systems"""
        sorted_systems = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        alternatives = []
        for name, score in sorted_systems[1:4]:  # Top 3 alternatives
            system = self.design_systems[name]
            alternatives.append(
                {
                    "name": name,
                    "score": score,
                    "pros": system["pros"],
                    "cons": system["cons"],
                }
            )

        return alternatives

    # Helper methods for component definitions
    def _get_material_components(self) -> List[str]:
        return [
            "Button",
            "TextField",
            "Card",
            "Dialog",
            "Drawer",
            "AppBar",
            "Table",
            "Tabs",
            "Stepper",
            "Chip",
            "Avatar",
            "Badge",
        ]

    def _get_ant_components(self) -> List[str]:
        return [
            "Button",
            "Input",
            "Card",
            "Modal",
            "Drawer",
            "Layout",
            "Table",
            "Form",
            "DatePicker",
            "Select",
            "Tree",
            "Upload",
        ]

    def _get_carbon_components(self) -> List[str]:
        return [
            "Button",
            "TextInput",
            "Tile",
            "Modal",
            "SideNav",
            "Header",
            "DataTable",
            "Form",
            "DatePicker",
            "Dropdown",
            "Accordion",
        ]

    def _get_fluent_components(self) -> List[str]:
        return [
            "Button",
            "TextField",
            "Card",
            "Dialog",
            "Nav",
            "CommandBar",
            "DetailsList",
            "Pivot",
            "Panel",
            "Persona",
            "MessageBar",
        ]

    def _get_spectrum_components(self) -> List[str]:
        return [
            "Button",
            "TextField",
            "Card",
            "Dialog",
            "SideBar",
            "Header",
            "Table",
            "Form",
            "DatePicker",
            "Picker",
            "ActionBar",
        ]

    # Token definitions
    def _get_material_tokens(self) -> Dict:
        return {
            "colors": {"primary": "#6200EE", "secondary": "#03DAC6"},
            "typography": {"scale": "material"},
            "spacing": {"unit": 8},
            "elevation": {"levels": 24},
        }

    def _get_ant_tokens(self) -> Dict:
        return {
            "colors": {"primary": "#1890ff", "success": "#52c41a"},
            "typography": {"scale": "ant"},
            "spacing": {"unit": 8},
            "borderRadius": {"base": 2},
        }

    def _get_carbon_tokens(self) -> Dict:
        return {
            "colors": {"blue": "#0f62fe", "gray": "#525252"},
            "typography": {"scale": "ibm"},
            "spacing": {"unit": 16},
            "grid": {"columns": 16},
        }

    def _get_fluent_tokens(self) -> Dict:
        return {
            "colors": {"themePrimary": "#0078d4", "themeSecondary": "#2b88d8"},
            "typography": {"scale": "segoe"},
            "spacing": {"unit": 4},
            "depth": {"levels": 5},
        }

    def _get_spectrum_tokens(self) -> Dict:
        return {
            "colors": {"blue": "#1473E6", "red": "#D7373F"},
            "typography": {"scale": "adobe"},
            "spacing": {"unit": 8},
            "animation": {"duration": "spectrum"},
        }

    # Implementation helpers
    def _get_setup_steps(self, system: Dict) -> List[str]:
        steps = []

        if system["libraries"]:
            steps.append(f"Install: npm install {' '.join(system['libraries'])}")

        steps.append("Import design system components")
        steps.append("Setup theme provider")
        steps.append("Configure design tokens")

        return steps

    def _get_configuration(self, system: Dict, requirements: Dict) -> Dict:
        return {
            "theme": system.get("tokens", {}),
            "components": system.get("components", []),
            "responsive": True,
            "rtl": requirements.get("rtl", False),
            "dark_mode": requirements.get("dark_mode", False),
        }

    def _get_customization_guide(self, system: Dict) -> List[str]:
        return [
            "Override design tokens",
            "Create custom components",
            "Extend existing components",
            "Apply brand colors",
            "Customize typography",
        ]

    def _get_best_practices(self, system: Dict) -> List[str]:
        return [
            f"Follow {system['name']} principles",
            "Use consistent spacing",
            "Maintain accessibility standards",
            "Optimize bundle size",
            "Test across devices",
        ]

    def _get_migration_path(self, system: Dict) -> List[str]:
        return [
            "Audit existing components",
            "Map to design system components",
            "Create migration plan",
            "Implement incrementally",
            "Test and validate",
        ]

    def _find_component_match(
        self, required: str, system_components: List[str]
    ) -> Optional[str]:
        """Find matching component in system"""
        # Direct match
        if required in system_components:
            return required

        # Fuzzy match
        required_lower = required.lower()
        for component in system_components:
            if (
                required_lower in component.lower()
                or component.lower() in required_lower
            ):
                return component

        return None

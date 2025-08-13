"""
Animation Designer Module
Designs and configures animations for UI components
"""

from typing import Any, Dict, List, Optional


class AnimationDesigner:
    """Designs animations and transitions for UI"""

    def __init__(self):
        self.animation_types = {
            "entrance": ["fadeIn", "slideIn", "zoomIn", "bounceIn", "flipIn"],
            "exit": ["fadeOut", "slideOut", "zoomOut", "bounceOut", "flipOut"],
            "attention": ["pulse", "shake", "swing", "tada", "wobble"],
            "transition": ["fade", "slide", "scale", "rotate", "morph"],
        }

        self.easing_functions = {
            "linear": "linear",
            "ease": "ease",
            "ease_in": "ease-in",
            "ease_out": "ease-out",
            "ease_in_out": "ease-in-out",
            "ease_in_quad": "cubic-bezier(0.55, 0.085, 0.68, 0.53)",
            "ease_out_quad": "cubic-bezier(0.25, 0.46, 0.45, 0.94)",
            "ease_in_out_quad": "cubic-bezier(0.455, 0.03, 0.515, 0.955)",
            "ease_in_cubic": "cubic-bezier(0.55, 0.055, 0.675, 0.19)",
            "ease_out_cubic": "cubic-bezier(0.215, 0.61, 0.355, 1)",
            "ease_in_out_cubic": "cubic-bezier(0.645, 0.045, 0.355, 1)",
            "ease_in_quart": "cubic-bezier(0.895, 0.03, 0.685, 0.22)",
            "ease_out_quart": "cubic-bezier(0.165, 0.84, 0.44, 1)",
            "ease_in_out_quart": "cubic-bezier(0.77, 0, 0.175, 1)",
            "ease_in_expo": "cubic-bezier(0.95, 0.05, 0.795, 0.035)",
            "ease_out_expo": "cubic-bezier(0.19, 1, 0.22, 1)",
            "ease_in_out_expo": "cubic-bezier(1, 0, 0, 1)",
            "ease_in_back": "cubic-bezier(0.6, -0.28, 0.735, 0.045)",
            "ease_out_back": "cubic-bezier(0.175, 0.885, 0.32, 1.275)",
            "ease_in_out_back": "cubic-bezier(0.68, -0.55, 0.265, 1.55)",
            "spring": "cubic-bezier(0.5, 1.5, 0.5, 1)",
            "bounce": "cubic-bezier(0.68, -0.55, 0.265, 1.55)",
        }

        self.duration_presets = {
            "instant": 100,
            "fast": 200,
            "normal": 300,
            "slow": 500,
            "very_slow": 1000,
        }

        self.micro_interactions = {
            "hover": {
                "button": {"scale": 1.05, "shadow": "elevated"},
                "card": {"translateY": -4, "shadow": "elevated"},
                "link": {"opacity": 0.8, "underline": True},
            },
            "active": {
                "button": {"scale": 0.95},
                "card": {"scale": 0.98},
                "input": {"borderColor": "primary"},
            },
            "focus": {
                "input": {"borderColor": "primary", "shadow": "focus"},
                "button": {"outline": "2px solid", "outlineOffset": 2},
            },
        }

    def design(
        self,
        project_type: str,
        components: List[str],
        preferences: Dict[str, Any],
        performance_level: str = "balanced",
    ) -> Dict[str, Any]:
        """
        Design animation system

        Args:
            project_type: Type of project
            components: List of UI components
            preferences: User preferences
            performance_level: Performance requirements

        Returns:
            Animation configuration
        """
        # Select animation style
        animation_style = self._select_animation_style(project_type, preferences, performance_level)

        # Configure component animations
        component_animations = self._configure_component_animations(components, animation_style)

        # Design page transitions
        page_transitions = self._design_page_transitions(project_type, animation_style)

        # Configure micro-interactions
        micro_interactions = self._configure_micro_interactions(components, animation_style)

        # Generate keyframes
        keyframes = self._generate_keyframes(component_animations)

        # Optimize for performance
        optimizations = self._optimize_animations(component_animations, performance_level)

        # Generate CSS
        css = self._generate_animation_css(component_animations, keyframes, micro_interactions)

        # Generate JavaScript hooks
        js_hooks = self._generate_js_hooks(component_animations)

        return {
            "style": animation_style,
            "component_animations": component_animations,
            "page_transitions": page_transitions,
            "micro_interactions": micro_interactions,
            "keyframes": keyframes,
            "optimizations": optimizations,
            "css": css,
            "js_hooks": js_hooks,
            "guidelines": self._generate_guidelines(animation_style),
        }

    def _select_animation_style(
        self, project_type: str, preferences: Dict, performance_level: str
    ) -> Dict[str, Any]:
        """Select animation style based on project"""

        style = {
            "intensity": "medium",
            "duration": "normal",
            "easing": "ease_out_cubic",
            "stagger": False,
            "parallax": False,
            "3d_transforms": False,
        }

        # Adjust based on project type
        if project_type in ["portfolio", "creative", "landing"]:
            style["intensity"] = "high"
            style["stagger"] = True
            style["parallax"] = True
        elif project_type in ["dashboard", "admin"]:
            style["intensity"] = "low"
            style["duration"] = "fast"
        elif project_type == "game":
            style["intensity"] = "high"
            style["3d_transforms"] = True

        # Adjust for performance
        if performance_level == "critical":
            style["intensity"] = "minimal"
            style["duration"] = "fast"
            style["parallax"] = False
            style["3d_transforms"] = False
        elif performance_level == "low":
            style["intensity"] = "low"
            style["stagger"] = False

        # Apply preferences
        if preferences.get("subtle_animations"):
            style["intensity"] = "low"
        elif preferences.get("no_animations"):
            style["intensity"] = "none"

        return style

    def _configure_component_animations(
        self, components: List[str], style: Dict
    ) -> Dict[str, Dict]:
        """Configure animations for each component"""

        animations = {}

        for component in components:
            if style["intensity"] == "none":
                animations[component] = {"enabled": False}
                continue

            # Default animation config
            config = {
                "enabled": True,
                "entrance": "fadeIn",
                "exit": "fadeOut",
                "duration": self.duration_presets[style["duration"]],
                "easing": style["easing"],
                "delay": 0,
            }

            # Component-specific adjustments
            if component in ["Modal", "Dialog"]:
                config["entrance"] = "zoomIn"
                config["exit"] = "zoomOut"
                config["backdrop"] = {"fade": True, "blur": True}
            elif component in ["Drawer", "Sidebar"]:
                config["entrance"] = "slideInLeft"
                config["exit"] = "slideOutLeft"
            elif component in ["Toast", "Notification"]:
                config["entrance"] = "slideInRight"
                config["exit"] = "slideOutRight"
                config["attention"] = "pulse"
            elif component == "Accordion":
                config["expand"] = "slideDown"
                config["collapse"] = "slideUp"
            elif component in ["Tab", "Tabs"]:
                config["switch"] = "fade"
                config["indicator"] = "slide"

            animations[component] = config

        return animations

    def _design_page_transitions(self, project_type: str, style: Dict) -> Dict[str, Any]:
        """Design page transition animations"""

        transitions = {
            "type": "fade",
            "duration": self.duration_presets[style["duration"]],
            "easing": style["easing"],
        }

        if project_type in ["portfolio", "creative"]:
            transitions["type"] = "creative"
            transitions["variants"] = ["fadeSlide", "reveal", "morph", "parallax"]
        elif project_type in ["dashboard", "admin"]:
            transitions["type"] = "simple"
            transitions["duration"] = self.duration_presets["fast"]
        elif project_type == "ecommerce":
            transitions["type"] = "smooth"
            transitions["preserveScroll"] = True

        return transitions

    def _configure_micro_interactions(self, components: List[str], style: Dict) -> Dict[str, Any]:
        """Configure micro-interactions"""

        if style["intensity"] == "none":
            return {"enabled": False}

        interactions = {"enabled": True, "hover": {}, "active": {}, "focus": {}}

        # Configure based on components
        if "Button" in components:
            interactions["hover"]["button"] = self.micro_interactions["hover"]["button"]
            interactions["active"]["button"] = self.micro_interactions["active"]["button"]

        if "Card" in components:
            interactions["hover"]["card"] = self.micro_interactions["hover"]["card"]
            interactions["active"]["card"] = self.micro_interactions["active"]["card"]

        if "Input" in components or "TextField" in components:
            interactions["focus"]["input"] = self.micro_interactions["focus"]["input"]
            interactions["active"]["input"] = self.micro_interactions["active"]["input"]

        # Adjust intensity
        if style["intensity"] == "low":
            # Reduce effects
            for state in interactions:
                if isinstance(interactions[state], dict):
                    for element in interactions[state]:
                        if "scale" in interactions[state][element]:
                            interactions[state][element]["scale"] *= 0.5

        return interactions

    def _generate_keyframes(self, animations: Dict) -> Dict[str, str]:
        """Generate CSS keyframes"""

        keyframes = {}

        # Common keyframes
        keyframes[
            "fadeIn"
        ] = """
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
        """

        keyframes[
            "fadeOut"
        ] = """
            @keyframes fadeOut {
                from { opacity: 1; }
                to { opacity: 0; }
            }
        """

        keyframes[
            "slideInLeft"
        ] = """
            @keyframes slideInLeft {
                from { transform: translateX(-100%); }
                to { transform: translateX(0); }
            }
        """

        keyframes[
            "slideOutLeft"
        ] = """
            @keyframes slideOutLeft {
                from { transform: translateX(0); }
                to { transform: translateX(-100%); }
            }
        """

        keyframes[
            "zoomIn"
        ] = """
            @keyframes zoomIn {
                from { transform: scale(0.8); opacity: 0; }
                to { transform: scale(1); opacity: 1; }
            }
        """

        keyframes[
            "pulse"
        ] = """
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); }
            }
        """

        return keyframes

    def _optimize_animations(self, animations: Dict, performance_level: str) -> Dict[str, Any]:
        """Optimize animations for performance"""

        optimizations = {
            "use_gpu": True,
            "will_change": [],
            "reduce_motion": False,
            "techniques": [],
        }

        if performance_level == "critical":
            optimizations["reduce_motion"] = True
            optimizations["techniques"] = [
                "Use transform instead of position",
                "Use opacity instead of display",
                "Avoid animating layout properties",
                "Use will-change sparingly",
            ]

        # Identify properties to optimize
        for component, config in animations.items():
            if config.get("enabled"):
                optimizations["will_change"].append(component)

        return optimizations

    def _generate_animation_css(
        self, animations: Dict, keyframes: Dict, micro_interactions: Dict
    ) -> str:
        """Generate CSS for animations"""

        css = "/* Animation Keyframes */\n"

        # Add keyframes
        for keyframe in keyframes.values():
            css += keyframe + "\n"

        css += "\n/* Animation Classes */\n"

        # Generate animation classes
        for component, config in animations.items():
            if config.get("enabled"):
                css += f".{component.lower()}-enter {{\n"
                css += f"  animation: {config.get('entrance', 'fadeIn')} "
                css += f"{config.get('duration', 300)}ms "
                css += f"{config.get('easing', 'ease-out')};\n"
                css += "}\n\n"

        # Micro-interactions
        if micro_interactions.get("enabled"):
            css += "/* Micro-interactions */\n"

            for state, elements in micro_interactions.items():
                if state == "enabled":
                    continue

                for element, props in elements.items():
                    css += f".{element}:{state} {{\n"

                    if "scale" in props:
                        css += f"  transform: scale({props['scale']});\n"
                    if "translateY" in props:
                        css += f"  transform: translateY({props['translateY']}px);\n"
                    if "opacity" in props:
                        css += f"  opacity: {props['opacity']};\n"

                    css += "  transition: all 200ms ease-out;\n"
                    css += "}\n\n"

        # Reduced motion support
        css += """
            @media (prefers-reduced-motion: reduce) {
                *, *::before, *::after {
                    animation-duration: 0.01ms !important;
                    animation-iteration-count: 1 !important;
                    transition-duration: 0.01ms !important;
                }
            }
        """

        return css

    def _generate_js_hooks(self, animations: Dict) -> Dict[str, str]:
        """Generate JavaScript hooks for animations"""

        hooks = {}

        for component, config in animations.items():
            if config.get("enabled"):
                hooks[component] = {
                    "onEnter": f"animate('{config.get('entrance', 'fadeIn')}')",
                    "onExit": f"animate('{config.get('exit', 'fadeOut')}')",
                    "duration": config.get("duration", 300),
                    "easing": config.get("easing", "ease-out"),
                }

        return hooks

    def _generate_guidelines(self, style: Dict) -> List[str]:
        """Generate animation guidelines"""

        guidelines = [
            f"Animation intensity: {style['intensity']}",
            f"Default duration: {style['duration']}",
            f"Easing function: {style['easing']}",
            "Use consistent animation timing across components",
            "Respect user's motion preferences",
            "Test animations on low-end devices",
            "Avoid animating during scroll for performance",
        ]

        if style.get("stagger"):
            guidelines.append("Use staggered animations for list items")

        if style.get("parallax"):
            guidelines.append("Implement parallax scrolling carefully")

        return guidelines

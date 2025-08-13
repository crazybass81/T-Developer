"""
Interaction Designer Module
Designs user interactions and gestures for UI components
"""

from typing import Dict, List, Any, Optional


class InteractionDesigner:
    """Designs interaction patterns and user gestures"""

    def __init__(self):
        self.interaction_patterns = {
            "click": {
                "description": "Single click/tap",
                "mobile": "tap",
                "desktop": "click",
                "feedback": "immediate",
            },
            "double_click": {
                "description": "Double click/tap",
                "mobile": "double_tap",
                "desktop": "dblclick",
                "feedback": "visual",
            },
            "long_press": {
                "description": "Press and hold",
                "mobile": "long_press",
                "desktop": "contextmenu",
                "feedback": "haptic",
            },
            "drag": {
                "description": "Drag to move",
                "mobile": "touch_drag",
                "desktop": "mouse_drag",
                "feedback": "continuous",
            },
            "swipe": {
                "description": "Swipe gesture",
                "mobile": "swipe",
                "desktop": "not_applicable",
                "feedback": "momentum",
            },
            "pinch": {
                "description": "Pinch to zoom",
                "mobile": "pinch",
                "desktop": "wheel_zoom",
                "feedback": "visual",
            },
            "hover": {
                "description": "Hover over element",
                "mobile": "not_applicable",
                "desktop": "mouseover",
                "feedback": "tooltip",
            },
            "scroll": {
                "description": "Scroll content",
                "mobile": "touch_scroll",
                "desktop": "wheel_scroll",
                "feedback": "smooth",
            },
        }

        self.gesture_recognizers = {
            "swipe_left": {
                "threshold": 50,  # pixels
                "velocity": 0.3,  # pixels/ms
                "action": "navigate_next",
            },
            "swipe_right": {
                "threshold": 50,
                "velocity": 0.3,
                "action": "navigate_previous",
            },
            "swipe_up": {"threshold": 50, "velocity": 0.3, "action": "dismiss"},
            "swipe_down": {"threshold": 50, "velocity": 0.3, "action": "refresh"},
            "pinch_in": {"scale": 0.8, "action": "zoom_out"},
            "pinch_out": {"scale": 1.2, "action": "zoom_in"},
            "rotate": {"angle": 15, "action": "rotate"},  # degrees
        }

        self.feedback_types = {
            "visual": {
                "ripple": "Material ripple effect",
                "highlight": "Color change",
                "scale": "Size change",
                "fade": "Opacity change",
                "glow": "Border glow",
            },
            "haptic": {
                "light": "Light vibration",
                "medium": "Medium vibration",
                "heavy": "Heavy vibration",
                "success": "Success pattern",
                "error": "Error pattern",
            },
            "audio": {
                "click": "Click sound",
                "success": "Success chime",
                "error": "Error tone",
                "notification": "Notification bell",
            },
        }

        self.state_machines = {
            "button": {
                "states": ["idle", "hover", "active", "disabled", "loading"],
                "transitions": {
                    "idle": ["hover", "disabled"],
                    "hover": ["idle", "active", "disabled"],
                    "active": ["idle", "loading"],
                    "loading": ["idle", "disabled"],
                    "disabled": ["idle"],
                },
            },
            "toggle": {
                "states": ["off", "turning_on", "on", "turning_off"],
                "transitions": {
                    "off": ["turning_on"],
                    "turning_on": ["on", "off"],
                    "on": ["turning_off"],
                    "turning_off": ["off", "on"],
                },
            },
            "drawer": {
                "states": ["closed", "opening", "open", "closing"],
                "transitions": {
                    "closed": ["opening"],
                    "opening": ["open", "closed"],
                    "open": ["closing"],
                    "closing": ["closed", "open"],
                },
            },
        }

        self.touch_zones = {
            "thumb_reach": {
                "easy": {"bottom": "0-40%", "sides": "20-80%"},
                "ok": {"bottom": "40-60%", "sides": "10-90%"},
                "hard": {"bottom": "60-100%", "sides": "0-100%"},
            },
            "two_handed": {"primary": "bottom_right", "secondary": "top_left"},
        }

    def design(
        self,
        components: List[str],
        platform: str = "web",
        interaction_level: str = "standard",
        accessibility: bool = True,
    ) -> Dict[str, Any]:
        """
        Design interaction patterns

        Args:
            components: List of UI components
            platform: Target platform (web, mobile, desktop)
            interaction_level: Complexity level
            accessibility: Include accessibility features

        Returns:
            Interaction design configuration
        """
        # Select interaction patterns
        patterns = self._select_patterns(components, platform, interaction_level)

        # Configure gestures
        gestures = self._configure_gestures(platform, interaction_level)

        # Design feedback
        feedback = self._design_feedback(components, interaction_level)

        # Configure state machines
        states = self._configure_states(components)

        # Design touch targets
        touch_targets = self._design_touch_targets(platform)

        # Configure drag and drop
        drag_drop = self._configure_drag_drop(components)

        # Design keyboard interactions
        keyboard = self._design_keyboard_interactions(components, accessibility)

        # Create interaction flow
        flow = self._create_interaction_flow(components, patterns)

        # Generate implementation code
        implementation = self._generate_implementation(
            patterns, gestures, feedback, states
        )

        return {
            "patterns": patterns,
            "gestures": gestures,
            "feedback": feedback,
            "states": states,
            "touch_targets": touch_targets,
            "drag_drop": drag_drop,
            "keyboard": keyboard,
            "flow": flow,
            "implementation": implementation,
            "guidelines": self._generate_guidelines(platform, interaction_level),
        }

    def _select_patterns(
        self, components: List[str], platform: str, level: str
    ) -> Dict[str, List[Dict]]:
        """Select interaction patterns for components"""
        patterns = {}

        for component in components:
            component_patterns = []

            if component == "Button":
                component_patterns.extend(
                    [
                        {"type": "click", "action": "primary"},
                        {"type": "hover", "action": "preview"},
                        {"type": "long_press", "action": "context_menu"},
                    ]
                )

            elif component == "Card":
                component_patterns.extend(
                    [
                        {"type": "click", "action": "expand"},
                        {"type": "hover", "action": "highlight"},
                        {"type": "drag", "action": "reorder"},
                    ]
                )

            elif component == "List":
                component_patterns.extend(
                    [
                        {"type": "click", "action": "select"},
                        {"type": "swipe", "action": "delete"},
                        {"type": "drag", "action": "reorder"},
                    ]
                )

            elif component == "Image":
                component_patterns.extend(
                    [
                        {"type": "click", "action": "lightbox"},
                        {"type": "pinch", "action": "zoom"},
                        {"type": "double_click", "action": "fullscreen"},
                    ]
                )

            elif component == "Carousel":
                component_patterns.extend(
                    [
                        {"type": "swipe", "action": "navigate"},
                        {"type": "click", "action": "select"},
                        {"type": "drag", "action": "scroll"},
                    ]
                )

            elif component in ["Modal", "Dialog"]:
                component_patterns.extend(
                    [
                        {"type": "click", "action": "close_backdrop"},
                        {"type": "swipe", "action": "dismiss"},
                    ]
                )

            elif component == "Form":
                component_patterns.extend(
                    [
                        {"type": "click", "action": "focus"},
                        {"type": "hover", "action": "tooltip"},
                    ]
                )

            # Platform-specific adjustments
            if platform == "mobile":
                # Remove hover patterns for mobile
                component_patterns = [
                    p for p in component_patterns if p["type"] != "hover"
                ]

            patterns[component] = component_patterns

        return patterns

    def _configure_gestures(self, platform: str, level: str) -> Dict[str, Any]:
        """Configure gesture recognition"""
        gestures = {
            "enabled": platform in ["mobile", "tablet"],
            "supported": [],
            "custom": [],
        }

        if gestures["enabled"]:
            if level == "advanced":
                gestures["supported"] = [
                    "swipe_left",
                    "swipe_right",
                    "swipe_up",
                    "swipe_down",
                    "pinch_in",
                    "pinch_out",
                    "rotate",
                    "three_finger_swipe",
                ]
                gestures["custom"] = [
                    {"name": "shake", "action": "undo", "threshold": "medium"},
                    {
                        "name": "double_tap_hold",
                        "action": "multi_select",
                        "duration": 500,
                    },
                ]
            elif level == "standard":
                gestures["supported"] = [
                    "swipe_left",
                    "swipe_right",
                    "pinch_in",
                    "pinch_out",
                ]
            else:  # minimal
                gestures["supported"] = ["swipe_left", "swipe_right"]

        return gestures

    def _design_feedback(self, components: List[str], level: str) -> Dict[str, Any]:
        """Design feedback mechanisms"""
        feedback = {"visual": {}, "haptic": {}, "audio": {}}

        # Visual feedback for all components
        for component in components:
            if component == "Button":
                feedback["visual"][component] = {
                    "hover": "scale(1.05)",
                    "active": "scale(0.95)",
                    "disabled": "opacity(0.5)",
                }
            elif component == "Card":
                feedback["visual"][component] = {
                    "hover": "shadow_elevation",
                    "active": "border_highlight",
                }
            elif component == "Input":
                feedback["visual"][component] = {
                    "focus": "border_color",
                    "error": "border_red",
                    "success": "border_green",
                }

        # Haptic feedback (mobile only)
        if level in ["standard", "advanced"]:
            feedback["haptic"] = {
                "button_press": "light",
                "toggle": "medium",
                "error": "heavy",
                "success": "pattern",
            }

        # Audio feedback (optional)
        if level == "advanced":
            feedback["audio"] = {
                "button_click": True,
                "success": True,
                "error": True,
                "notification": True,
            }

        return feedback

    def _configure_states(self, components: List[str]) -> Dict[str, Dict]:
        """Configure component state machines"""
        states = {}

        for component in components:
            if component == "Button":
                states[component] = self.state_machines["button"]
            elif component in ["Switch", "Checkbox"]:
                states[component] = self.state_machines["toggle"]
            elif component in ["Drawer", "Sidebar"]:
                states[component] = self.state_machines["drawer"]
            elif component == "Accordion":
                states[component] = {
                    "states": ["collapsed", "expanding", "expanded", "collapsing"],
                    "transitions": {
                        "collapsed": ["expanding"],
                        "expanding": ["expanded"],
                        "expanded": ["collapsing"],
                        "collapsing": ["collapsed"],
                    },
                }
            elif component == "Tab":
                states[component] = {
                    "states": ["inactive", "activating", "active"],
                    "transitions": {
                        "inactive": ["activating"],
                        "activating": ["active"],
                        "active": ["inactive"],
                    },
                }

        return states

    def _design_touch_targets(self, platform: str) -> Dict[str, Any]:
        """Design touch target areas"""
        targets = {"minimum_size": "44px", "recommended_size": "48px", "spacing": "8px"}

        if platform == "mobile":
            targets["zones"] = self.touch_zones["thumb_reach"]
            targets["optimization"] = {
                "primary_actions": "easy_zone",
                "secondary_actions": "ok_zone",
                "dangerous_actions": "hard_zone",
            }
        elif platform == "tablet":
            targets["zones"] = self.touch_zones["two_handed"]
            targets["minimum_size"] = "48px"
            targets["recommended_size"] = "56px"

        return targets

    def _configure_drag_drop(self, components: List[str]) -> Dict[str, Any]:
        """Configure drag and drop interactions"""
        drag_drop = {"enabled": False, "components": [], "zones": []}

        draggable_components = ["Card", "ListItem", "Image", "File"]
        droppable_components = ["List", "Grid", "Container", "Upload"]

        for component in components:
            if component in draggable_components:
                drag_drop["enabled"] = True
                drag_drop["components"].append(
                    {
                        "component": component,
                        "draggable": True,
                        "handle": "grip_icon",
                        "preview": "ghost",
                        "feedback": "elevation",
                    }
                )

            if component in droppable_components:
                drag_drop["zones"].append(
                    {
                        "component": component,
                        "accepts": draggable_components,
                        "indicator": "border_highlight",
                        "feedback": "visual",
                    }
                )

        return drag_drop

    def _design_keyboard_interactions(
        self, components: List[str], accessibility: bool
    ) -> Dict[str, Any]:
        """Design keyboard interaction patterns"""
        keyboard = {
            "navigation": {
                "Tab": "Next element",
                "Shift+Tab": "Previous element",
                "Arrow keys": "Navigate within component",
                "Home": "First item",
                "End": "Last item",
            },
            "actions": {
                "Enter": "Activate/Submit",
                "Space": "Toggle/Select",
                "Escape": "Cancel/Close",
                "Delete": "Remove item",
            },
            "shortcuts": {},
        }

        # Component-specific keyboard interactions
        for component in components:
            if component == "Modal":
                keyboard["shortcuts"]["Escape"] = "Close modal"
            elif component == "Form":
                keyboard["shortcuts"]["Ctrl+Enter"] = "Submit form"
            elif component == "Table":
                keyboard["shortcuts"]["Ctrl+A"] = "Select all"
            elif component == "Search":
                keyboard["shortcuts"]["Ctrl+K"] = "Focus search"

        if accessibility:
            keyboard["aria_keys"] = {
                "ArrowUp/Down": "Navigate menu items",
                "ArrowLeft/Right": "Navigate tabs",
                "PageUp/PageDown": "Navigate pages",
            }

        return keyboard

    def _create_interaction_flow(
        self, components: List[str], patterns: Dict
    ) -> Dict[str, List[str]]:
        """Create interaction flow diagram"""
        flow = {}

        for component in components:
            if component == "Form":
                flow[component] = [
                    "User focuses field",
                    "Show field hints",
                    "User enters data",
                    "Validate on blur",
                    "Show error/success",
                    "Enable submit when valid",
                ]
            elif component == "Modal":
                flow[component] = [
                    "Trigger opens modal",
                    "Focus trapped in modal",
                    "User interacts with content",
                    "Close via button/escape/backdrop",
                    "Return focus to trigger",
                ]
            elif component == "Wizard":
                flow[component] = [
                    "Show step 1",
                    "Validate step",
                    "Animate to next step",
                    "Allow back navigation",
                    "Submit on final step",
                    "Show confirmation",
                ]

        return flow

    def _generate_implementation(
        self, patterns: Dict, gestures: Dict, feedback: Dict, states: Dict
    ) -> Dict[str, str]:
        """Generate implementation code snippets"""
        implementation = {}

        # React implementation example
        implementation[
            "react"
        ] = """
// Button with interaction states
const InteractiveButton = ({ onClick, children }) => {
  const [state, setState] = useState('idle');

  const handleMouseEnter = () => setState('hover');
  const handleMouseLeave = () => setState('idle');
  const handleMouseDown = () => setState('active');
  const handleMouseUp = () => setState('hover');

  return (
    <button
      className={`btn btn-${state}`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onMouseDown={handleMouseDown}
      onMouseUp={handleMouseUp}
      onClick={onClick}
    >
      {children}
    </button>
  );
};

// Gesture handler
const SwipeableCard = ({ onSwipeLeft, onSwipeRight }) => {
  const handlers = useSwipeable({
    onSwipedLeft: onSwipeLeft,
    onSwipedRight: onSwipeRight,
    trackMouse: true
  });

  return <div {...handlers}>Swipe me!</div>;
};
"""

        # CSS for feedback
        implementation[
            "css"
        ] = """
/* Visual feedback */
.btn {
  transition: all 200ms ease-out;
}

.btn-hover {
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.btn-active {
  transform: scale(0.95);
}

/* Touch feedback */
@media (hover: none) {
  .btn:active {
    background: rgba(0,0,0,0.1);
  }
}
"""

        return implementation

    def _generate_guidelines(self, platform: str, level: str) -> List[str]:
        """Generate interaction design guidelines"""
        guidelines = [
            f"Platform: {platform}",
            f"Interaction level: {level}",
            "Ensure all interactions are predictable",
            "Provide immediate feedback for user actions",
            "Make touch targets at least 44x44px",
            "Support both touch and mouse inputs",
            "Include keyboard navigation",
            "Test with real devices",
        ]

        if platform == "mobile":
            guidelines.extend(
                [
                    "Optimize for one-handed use",
                    "Place primary actions in thumb-reach zone",
                    "Use gestures sparingly",
                    "Provide gesture hints",
                ]
            )

        if level == "advanced":
            guidelines.extend(
                [
                    "Implement custom gestures carefully",
                    "Add haptic feedback for key actions",
                    "Consider motion preferences",
                ]
            )

        return guidelines

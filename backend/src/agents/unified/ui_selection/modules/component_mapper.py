"""
Component Mapper Module
Maps abstract component requirements to concrete framework implementations
"""

from typing import Any, Dict, List, Optional


class ComponentMapper:
    """Maps abstract components to framework-specific implementations"""

    def __init__(self):
        self.framework_components = {
            "react": {
                "Button": {
                    "native": "button",
                    "mui": "@mui/material/Button",
                    "antd": "antd/Button",
                    "chakra": "@chakra-ui/react/Button",
                    "bootstrap": "react-bootstrap/Button",
                    "semantic": "semantic-ui-react/Button",
                },
                "Input": {
                    "native": "input",
                    "mui": "@mui/material/TextField",
                    "antd": "antd/Input",
                    "chakra": "@chakra-ui/react/Input",
                    "bootstrap": "react-bootstrap/Form.Control",
                    "semantic": "semantic-ui-react/Input",
                },
                "Card": {
                    "native": "div",
                    "mui": "@mui/material/Card",
                    "antd": "antd/Card",
                    "chakra": "@chakra-ui/react/Box",
                    "bootstrap": "react-bootstrap/Card",
                    "semantic": "semantic-ui-react/Card",
                },
                "Modal": {
                    "native": "dialog",
                    "mui": "@mui/material/Dialog",
                    "antd": "antd/Modal",
                    "chakra": "@chakra-ui/react/Modal",
                    "bootstrap": "react-bootstrap/Modal",
                    "semantic": "semantic-ui-react/Modal",
                },
                "Table": {
                    "native": "table",
                    "mui": "@mui/material/Table",
                    "antd": "antd/Table",
                    "chakra": "@chakra-ui/react/Table",
                    "bootstrap": "react-bootstrap/Table",
                    "semantic": "semantic-ui-react/Table",
                },
                "Form": {
                    "native": "form",
                    "mui": "@mui/material/Box",
                    "antd": "antd/Form",
                    "chakra": "@chakra-ui/react/FormControl",
                    "bootstrap": "react-bootstrap/Form",
                    "semantic": "semantic-ui-react/Form",
                },
                "Select": {
                    "native": "select",
                    "mui": "@mui/material/Select",
                    "antd": "antd/Select",
                    "chakra": "@chakra-ui/react/Select",
                    "bootstrap": "react-bootstrap/Form.Select",
                    "semantic": "semantic-ui-react/Dropdown",
                },
                "Checkbox": {
                    "native": 'input[type="checkbox"]',
                    "mui": "@mui/material/Checkbox",
                    "antd": "antd/Checkbox",
                    "chakra": "@chakra-ui/react/Checkbox",
                    "bootstrap": "react-bootstrap/Form.Check",
                    "semantic": "semantic-ui-react/Checkbox",
                },
                "Radio": {
                    "native": 'input[type="radio"]',
                    "mui": "@mui/material/Radio",
                    "antd": "antd/Radio",
                    "chakra": "@chakra-ui/react/Radio",
                    "bootstrap": "react-bootstrap/Form.Check",
                    "semantic": "semantic-ui-react/Radio",
                },
                "Switch": {
                    "native": 'input[type="checkbox"]',
                    "mui": "@mui/material/Switch",
                    "antd": "antd/Switch",
                    "chakra": "@chakra-ui/react/Switch",
                    "bootstrap": "react-bootstrap/Form.Switch",
                    "semantic": "semantic-ui-react/Checkbox",
                },
                "Tabs": {
                    "native": 'div[role="tablist"]',
                    "mui": "@mui/material/Tabs",
                    "antd": "antd/Tabs",
                    "chakra": "@chakra-ui/react/Tabs",
                    "bootstrap": "react-bootstrap/Tabs",
                    "semantic": "semantic-ui-react/Tab",
                },
                "Accordion": {
                    "native": "details",
                    "mui": "@mui/material/Accordion",
                    "antd": "antd/Collapse",
                    "chakra": "@chakra-ui/react/Accordion",
                    "bootstrap": "react-bootstrap/Accordion",
                    "semantic": "semantic-ui-react/Accordion",
                },
                "Menu": {
                    "native": "nav",
                    "mui": "@mui/material/Menu",
                    "antd": "antd/Menu",
                    "chakra": "@chakra-ui/react/Menu",
                    "bootstrap": "react-bootstrap/Dropdown",
                    "semantic": "semantic-ui-react/Menu",
                },
                "Tooltip": {
                    "native": 'div[role="tooltip"]',
                    "mui": "@mui/material/Tooltip",
                    "antd": "antd/Tooltip",
                    "chakra": "@chakra-ui/react/Tooltip",
                    "bootstrap": "react-bootstrap/Tooltip",
                    "semantic": "semantic-ui-react/Popup",
                },
                "Alert": {
                    "native": 'div[role="alert"]',
                    "mui": "@mui/material/Alert",
                    "antd": "antd/Alert",
                    "chakra": "@chakra-ui/react/Alert",
                    "bootstrap": "react-bootstrap/Alert",
                    "semantic": "semantic-ui-react/Message",
                },
                "Badge": {
                    "native": "span",
                    "mui": "@mui/material/Badge",
                    "antd": "antd/Badge",
                    "chakra": "@chakra-ui/react/Badge",
                    "bootstrap": "react-bootstrap/Badge",
                    "semantic": "semantic-ui-react/Label",
                },
                "Progress": {
                    "native": "progress",
                    "mui": "@mui/material/LinearProgress",
                    "antd": "antd/Progress",
                    "chakra": "@chakra-ui/react/Progress",
                    "bootstrap": "react-bootstrap/ProgressBar",
                    "semantic": "semantic-ui-react/Progress",
                },
                "Spinner": {
                    "native": "div",
                    "mui": "@mui/material/CircularProgress",
                    "antd": "antd/Spin",
                    "chakra": "@chakra-ui/react/Spinner",
                    "bootstrap": "react-bootstrap/Spinner",
                    "semantic": "semantic-ui-react/Loader",
                },
                "Avatar": {
                    "native": "img",
                    "mui": "@mui/material/Avatar",
                    "antd": "antd/Avatar",
                    "chakra": "@chakra-ui/react/Avatar",
                    "bootstrap": "react-bootstrap/Image",
                    "semantic": "semantic-ui-react/Image",
                },
                "Chip": {
                    "native": "span",
                    "mui": "@mui/material/Chip",
                    "antd": "antd/Tag",
                    "chakra": "@chakra-ui/react/Tag",
                    "bootstrap": "react-bootstrap/Badge",
                    "semantic": "semantic-ui-react/Label",
                },
            },
            "vue": {
                "Button": {
                    "native": "button",
                    "vuetify": "v-btn",
                    "element": "el-button",
                    "antdv": "a-button",
                    "quasar": "q-btn",
                    "naive": "n-button",
                },
                "Input": {
                    "native": "input",
                    "vuetify": "v-text-field",
                    "element": "el-input",
                    "antdv": "a-input",
                    "quasar": "q-input",
                    "naive": "n-input",
                },
                "Card": {
                    "native": "div",
                    "vuetify": "v-card",
                    "element": "el-card",
                    "antdv": "a-card",
                    "quasar": "q-card",
                    "naive": "n-card",
                },
            },
            "angular": {
                "Button": {
                    "native": "button",
                    "material": "mat-button",
                    "primeng": "p-button",
                    "ngbootstrap": "button",
                    "clarity": "clr-button",
                    "nebular": "nb-button",
                },
                "Input": {
                    "native": "input",
                    "material": "mat-form-field",
                    "primeng": "p-inputtext",
                    "ngbootstrap": "input",
                    "clarity": "clr-input",
                    "nebular": "nb-input",
                },
            },
            "svelte": {
                "Button": {
                    "native": "button",
                    "carbon": "Button",
                    "sveltestrap": "Button",
                    "smelte": "Button",
                    "svelte-mui": "Button",
                }
            },
        }

        self.component_properties = {
            "Button": {
                "required": ["onClick", "children"],
                "optional": ["variant", "color", "size", "disabled", "loading", "icon"],
                "events": ["onClick", "onFocus", "onBlur"],
                "aria": ["aria-label", "aria-pressed", "aria-expanded"],
            },
            "Input": {
                "required": ["value", "onChange"],
                "optional": ["placeholder", "type", "disabled", "error", "helperText"],
                "events": ["onChange", "onFocus", "onBlur", "onKeyPress"],
                "aria": ["aria-label", "aria-invalid", "aria-describedby"],
            },
            "Modal": {
                "required": ["open", "onClose"],
                "optional": ["title", "size", "backdrop", "keyboard", "animation"],
                "events": ["onClose", "onOpen", "onEscape"],
                "aria": ["aria-modal", "aria-labelledby", "aria-describedby"],
            },
            "Table": {
                "required": ["columns", "data"],
                "optional": [
                    "sortable",
                    "filterable",
                    "pagination",
                    "selectable",
                    "expandable",
                ],
                "events": ["onSort", "onFilter", "onSelect", "onExpand"],
                "aria": ["aria-label", "aria-rowcount", "aria-colcount"],
            },
        }

        self.styling_approaches = {
            "css_modules": {
                "description": "Component-scoped CSS",
                "pros": ["No conflicts", "Good performance"],
                "cons": ["Build setup required"],
                "example": "styles.module.css",
            },
            "styled_components": {
                "description": "CSS-in-JS with tagged templates",
                "pros": ["Dynamic styling", "Component coupling"],
                "cons": ["Runtime overhead", "Bundle size"],
                "example": "styled.button`...`",
            },
            "emotion": {
                "description": "Performant CSS-in-JS",
                "pros": ["Small bundle", "SSR support"],
                "cons": ["Learning curve"],
                "example": "css`...`",
            },
            "tailwind": {
                "description": "Utility-first CSS",
                "pros": ["Fast development", "Consistent"],
                "cons": ["HTML bloat", "Learning curve"],
                "example": 'className="px-4 py-2 bg-blue-500"',
            },
            "sass": {
                "description": "CSS preprocessor",
                "pros": ["Features", "Mature"],
                "cons": ["Build step", "Not component-scoped"],
                "example": "styles.scss",
            },
        }

    def map(
        self,
        components: List[str],
        framework: str = "react",
        ui_library: str = "native",
        styling: str = "css_modules",
        custom_mappings: Dict[str, str] = None,
    ) -> Dict[str, Any]:
        """
        Map abstract components to framework implementations

        Args:
            components: List of abstract component names
            framework: Target framework
            ui_library: UI library to use
            styling: Styling approach
            custom_mappings: Custom component mappings

        Returns:
            Component mapping configuration
        """
        # Get framework components
        framework_map = self.framework_components.get(framework, {})

        # Map each component
        mappings = self._create_mappings(components, framework_map, ui_library, custom_mappings)

        # Get component properties
        properties = self._get_component_properties(components)

        # Generate imports
        imports = self._generate_imports(mappings, ui_library)

        # Generate component templates
        templates = self._generate_templates(mappings, properties, framework)

        # Configure styling
        styling_config = self._configure_styling(styling, components)

        # Create composition patterns
        compositions = self._create_compositions(components)

        # Generate usage examples
        examples = self._generate_examples(mappings, framework)

        # Create integration guide
        integration = self._create_integration_guide(framework, ui_library, styling)

        return {
            "framework": framework,
            "ui_library": ui_library,
            "mappings": mappings,
            "properties": properties,
            "imports": imports,
            "templates": templates,
            "styling": styling_config,
            "compositions": compositions,
            "examples": examples,
            "integration": integration,
            "guidelines": self._generate_guidelines(framework, ui_library),
        }

    def _create_mappings(
        self,
        components: List[str],
        framework_map: Dict,
        ui_library: str,
        custom: Optional[Dict],
    ) -> Dict[str, Dict]:
        """Create component mappings"""
        mappings = {}

        for component in components:
            if custom and component in custom:
                # Use custom mapping
                mappings[component] = {
                    "implementation": custom[component],
                    "type": "custom",
                }
            elif component in framework_map:
                # Use framework mapping
                comp_map = framework_map[component]
                if ui_library in comp_map:
                    mappings[component] = {
                        "implementation": comp_map[ui_library],
                        "type": ui_library,
                        "fallback": comp_map.get("native", "div"),
                    }
                else:
                    # Fallback to native
                    mappings[component] = {
                        "implementation": comp_map.get("native", "div"),
                        "type": "native",
                    }
            else:
                # Unknown component - use div
                mappings[component] = {
                    "implementation": "div",
                    "type": "custom",
                    "note": "Custom implementation required",
                }

        return mappings

    def _get_component_properties(self, components: List[str]) -> Dict[str, Dict]:
        """Get properties for each component"""
        properties = {}

        for component in components:
            if component in self.component_properties:
                properties[component] = self.component_properties[component]
            else:
                # Default properties
                properties[component] = {
                    "required": ["children"],
                    "optional": ["className", "style"],
                    "events": ["onClick"],
                    "aria": [],
                }

        return properties

    def _generate_imports(self, mappings: Dict, ui_library: str) -> Dict[str, List[str]]:
        """Generate import statements"""
        imports = {"components": [], "styles": [], "utilities": []}

        if ui_library == "native":
            # No imports needed for native HTML
            pass
        elif ui_library == "mui":
            for component, mapping in mappings.items():
                if mapping["type"] == "mui":
                    imports["components"].append(
                        f"import {component} from '{mapping['implementation']}';"
                    )
            imports["styles"].append("import { ThemeProvider } from '@mui/material/styles';")
        elif ui_library == "antd":
            components_to_import = []
            for component, mapping in mappings.items():
                if mapping["type"] == "antd":
                    components_to_import.append(component)
            if components_to_import:
                imports["components"].append(
                    f"import {{ {', '.join(components_to_import)} }} from 'antd';"
                )
            imports["styles"].append("import 'antd/dist/reset.css';")

        return imports

    def _generate_templates(
        self, mappings: Dict, properties: Dict, framework: str
    ) -> Dict[str, str]:
        """Generate component templates"""
        templates = {}

        for component, mapping in mappings.items():
            props = properties.get(component, {})

            if framework == "react":
                templates[component] = self._generate_react_template(component, mapping, props)
            elif framework == "vue":
                templates[component] = self._generate_vue_template(component, mapping, props)
            elif framework == "angular":
                templates[component] = self._generate_angular_template(component, mapping, props)

        return templates

    def _generate_react_template(self, component: str, mapping: Dict, props: Dict) -> str:
        """Generate React component template"""
        impl = mapping["implementation"].split("/")[-1]

        template = f"""
const {component}Component = ({{ {', '.join(props.get('required', []))} }}) => {{
  return (
    <{impl}
      {' '.join([f'{p}={{{p}}}' for p in props.get('required', [])])}
    >
      {{children}}
    </{impl}>
  );
}};
"""
        return template

    def _generate_vue_template(self, component: str, mapping: Dict, props: Dict) -> str:
        """Generate Vue component template"""
        impl = mapping["implementation"]

        template = f"""
<template>
  <{impl}
    {' '.join([f':{p}="{p}"' for p in props.get('required', [])])}
  >
    <slot />
  </{impl}>
</template>

<script>
export default {{
  name: '{component}Component',
  props: {props.get('required', [])}
}}
</script>
"""
        return template

    def _generate_angular_template(self, component: str, mapping: Dict, props: Dict) -> str:
        """Generate Angular component template"""
        impl = mapping["implementation"]

        template = f"""
@Component({{
  selector: 'app-{component.lower()}',
  template: `
    <{impl}
      {' '.join([f'[{p}]="{p}"' for p in props.get('required', [])])}
    >
      <ng-content></ng-content>
    </{impl}>
  `
}})
export class {component}Component {{
  {'; '.join([f'@Input() {p}: any' for p in props.get('required', [])])};
}}
"""
        return template

    def _configure_styling(self, approach: str, components: List[str]) -> Dict[str, Any]:
        """Configure styling approach"""
        config = {
            "approach": approach,
            "details": self.styling_approaches.get(approach, {}),
            "setup": [],
            "examples": {},
        }

        if approach == "css_modules":
            config["setup"] = [
                "Configure webpack/build tool for CSS modules",
                "Create .module.css files for each component",
            ]
            config["examples"][
                "Button"
            ] = """
/* Button.module.css */
.button {
  padding: 8px 16px;
  border-radius: 4px;
}

/* Component */
import styles from './Button.module.css';
<button className={styles.button}>Click</button>
"""

        elif approach == "styled_components":
            config["setup"] = [
                "npm install styled-components",
                "Add babel plugin for better debugging",
            ]
            config["examples"][
                "Button"
            ] = """
import styled from 'styled-components';

const StyledButton = styled.button`
  padding: 8px 16px;
  border-radius: 4px;
  background: ${props => props.primary ? 'blue' : 'gray'};
`;
"""

        elif approach == "tailwind":
            config["setup"] = [
                "npm install tailwindcss",
                "npx tailwindcss init",
                "Configure postcss",
            ]
            config["examples"][
                "Button"
            ] = """
<button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
  Click
</button>
"""

        return config

    def _create_compositions(self, components: List[str]) -> List[Dict]:
        """Create component composition patterns"""
        compositions = []

        # Common patterns
        if "Card" in components and "Button" in components:
            compositions.append(
                {
                    "name": "Card with Actions",
                    "components": ["Card", "Button"],
                    "pattern": "Card containing content with action buttons",
                }
            )

        if "Form" in components and "Input" in components and "Button" in components:
            compositions.append(
                {
                    "name": "Form with Inputs",
                    "components": ["Form", "Input", "Button"],
                    "pattern": "Form containing multiple inputs and submit button",
                }
            )

        if "Modal" in components and "Form" in components:
            compositions.append(
                {
                    "name": "Modal Form",
                    "components": ["Modal", "Form"],
                    "pattern": "Form displayed in a modal dialog",
                }
            )

        if "Table" in components and "Button" in components:
            compositions.append(
                {
                    "name": "Table with Actions",
                    "components": ["Table", "Button"],
                    "pattern": "Table with action buttons in rows",
                }
            )

        return compositions

    def _generate_examples(self, mappings: Dict, framework: str) -> Dict[str, str]:
        """Generate usage examples"""
        examples = {}

        for component, mapping in mappings.items():
            if framework == "react":
                examples[
                    component
                ] = f"""
// Import
import {component} from './components/{component}';

// Usage
<{component}
  onClick={{() => console.log('Clicked')}}
  variant="primary"
  size="medium"
>
  Click Me
</{component}>
"""
            elif framework == "vue":
                examples[
                    component
                ] = f"""
<!-- Import -->
<script>
import {component} from './components/{component}.vue';
</script>

<!-- Usage -->
<{component}
  @click="handleClick"
  variant="primary"
  size="medium"
>
  Click Me
</{component}>
"""

        return examples

    def _create_integration_guide(
        self, framework: str, ui_library: str, styling: str
    ) -> Dict[str, List[str]]:
        """Create integration guide"""
        guide = {"setup": [], "configuration": [], "best_practices": []}

        # Setup steps
        if ui_library != "native":
            guide["setup"].append(f"Install {ui_library} package")
            guide["setup"].append(f"Import {ui_library} styles")
            guide["setup"].append(f"Configure theme provider")

        guide["setup"].append(f"Set up {styling} for styling")

        # Configuration
        guide["configuration"].append("Configure build tool")
        guide["configuration"].append("Set up linting rules")
        guide["configuration"].append("Configure testing utilities")

        # Best practices
        guide["best_practices"].append("Use semantic component names")
        guide["best_practices"].append("Implement proper prop validation")
        guide["best_practices"].append("Add accessibility attributes")
        guide["best_practices"].append("Write unit tests for components")
        guide["best_practices"].append("Document component APIs")

        return guide

    def _generate_guidelines(self, framework: str, ui_library: str) -> List[str]:
        """Generate component mapping guidelines"""
        return [
            f"Framework: {framework}",
            f"UI Library: {ui_library}",
            "Use consistent component naming",
            "Implement proper prop types/interfaces",
            "Handle all required props",
            "Add default props where appropriate",
            "Implement error boundaries",
            "Add loading states",
            "Handle edge cases",
            "Test with different data sets",
            "Ensure accessibility compliance",
            "Document component usage",
        ]

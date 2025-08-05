# backend/src/agents/implementations/generation_templates.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class TemplateType(Enum):
    REACT_COMPONENT = "react_component"
    NODE_API = "node_api"
    PYTHON_SERVICE = "python_service"
    DATABASE_SCHEMA = "database_schema"
    DOCKER_CONFIG = "docker_config"

@dataclass
class CodeTemplate:
    name: str
    type: TemplateType
    language: str
    framework: str
    template: str
    variables: List[str]
    dependencies: List[str]

class TemplateEngine:
    """Code template management and generation"""

    def __init__(self):
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, CodeTemplate]:
        """Load predefined code templates"""
        return {
            'react_component': CodeTemplate(
                name="React Component",
                type=TemplateType.REACT_COMPONENT,
                language="typescript",
                framework="react",
                template="""
import React, { useState, useEffect } from 'react';
import { {interfaces} } from './types';

interface {componentName}Props {
  {props}
}

export const {componentName}: React.FC<{componentName}Props> = ({
  {propNames}
}) => {
  {stateDeclarations}

  {useEffectHooks}

  {eventHandlers}

  return (
    <div className="{className}">
      {jsx}
    </div>
  );
};

export default {componentName};
""",
                variables=['componentName', 'interfaces', 'props', 'propNames', 'stateDeclarations', 'useEffectHooks', 'eventHandlers', 'className', 'jsx'],
                dependencies=['react', '@types/react']
            ),

            'node_api': CodeTemplate(
                name="Node.js API Endpoint",
                type=TemplateType.NODE_API,
                language="typescript",
                framework="express",
                template="""
import { Request, Response, NextFunction } from 'express';
import { {validators} } from '../validators';
import { {services} } from '../services';
import { {types} } from '../types';

export const {handlerName} = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    // Validate input
    {validation}

    // Process request
    {businessLogic}

    // Send response
    res.status({statusCode}).json({
      success: true,
      data: result,
      message: '{successMessage}'
    });
  } catch (error) {
    next(error);
  }
};
""",
                variables=['validators', 'services', 'types', 'handlerName', 'validation', 'businessLogic', 'statusCode', 'successMessage'],
                dependencies=['express', '@types/express']
            ),

            'python_service': CodeTemplate(
                name="Python Service Class",
                type=TemplateType.PYTHON_SERVICE,
                language="python",
                framework="fastapi",
                template="""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from {imports}

@dataclass
class {dataClass}:
    {dataFields}

class {serviceName}:
    \"\"\"
    {serviceDescription}
    \"\"\"

    def __init__(self{initParams}):
        {initialization}

    async def {mainMethod}(
        self,
        {methodParams}
    ) -> {returnType}:
        \"\"\"
        {methodDescription}
        \"\"\"
        try:
            {methodBody}
            return result
        except Exception as e:
            {errorHandling}
            raise

    {additionalMethods}
""",
                variables=['imports', 'dataClass', 'dataFields', 'serviceName', 'serviceDescription', 'initParams', 'initialization', 'mainMethod', 'methodParams', 'returnType', 'methodDescription', 'methodBody', 'errorHandling', 'additionalMethods'],
                dependencies=['fastapi', 'pydantic', 'typing']
            )
        }

    def generate_from_template(
        self,
        template_name: str,
        variables: Dict[str, Any]
    ) -> str:
        """Generate code from template with variables"""
        
        if template_name not in self.templates:
            raise ValueError(f"Template {template_name} not found")

        template = self.templates[template_name]
        code = template.template

        # Replace variables
        for var_name, var_value in variables.items():
            placeholder = f"{{{var_name}}}"
            code = code.replace(placeholder, str(var_value))

        return code.strip()

    def get_template_variables(self, template_name: str) -> List[str]:
        """Get required variables for a template"""
        if template_name not in self.templates:
            return []
        return self.templates[template_name].variables

    def get_template_dependencies(self, template_name: str) -> List[str]:
        """Get dependencies for a template"""
        if template_name not in self.templates:
            return []
        return self.templates[template_name].dependencies

class TemplateVariableExtractor:
    """Extract template variables from requirements"""

    async def extract_variables(
        self,
        requirements: Dict[str, Any],
        template_type: TemplateType
    ) -> Dict[str, Any]:
        """Extract template variables from requirements"""
        
        if template_type == TemplateType.REACT_COMPONENT:
            return await self._extract_react_variables(requirements)
        elif template_type == TemplateType.NODE_API:
            return await self._extract_api_variables(requirements)
        elif template_type == TemplateType.PYTHON_SERVICE:
            return await self._extract_service_variables(requirements)
        else:
            return {}

    async def _extract_react_variables(
        self,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract React component variables"""
        
        component_name = requirements.get('name', 'MyComponent')
        props = requirements.get('props', [])
        
        return {
            'componentName': component_name,
            'interfaces': ', '.join(requirements.get('interfaces', [])),
            'props': self._format_props(props),
            'propNames': ', '.join([prop['name'] for prop in props]),
            'stateDeclarations': self._generate_state_declarations(requirements.get('state', [])),
            'useEffectHooks': self._generate_use_effects(requirements.get('effects', [])),
            'eventHandlers': self._generate_event_handlers(requirements.get('events', [])),
            'className': requirements.get('className', component_name.lower()),
            'jsx': self._generate_jsx(requirements.get('ui', {}))
        }

    def _format_props(self, props: List[Dict[str, Any]]) -> str:
        """Format props for TypeScript interface"""
        if not props:
            return ""
        
        prop_lines = []
        for prop in props:
            optional = "?" if prop.get('optional', False) else ""
            prop_lines.append(f"  {prop['name']}{optional}: {prop['type']};")
        
        return "\n".join(prop_lines)

    def _generate_state_declarations(self, state_vars: List[Dict[str, Any]]) -> str:
        """Generate useState declarations"""
        if not state_vars:
            return ""
        
        declarations = []
        for var in state_vars:
            initial_value = var.get('initial', 'null')
            declarations.append(
                f"  const [{var['name']}, set{var['name'].capitalize()}] = useState<{var['type']}>({initial_value});"
            )
        
        return "\n".join(declarations)

    def _generate_jsx(self, ui_spec: Dict[str, Any]) -> str:
        """Generate JSX from UI specification"""
        if not ui_spec:
            return "<div>Content goes here</div>"
        
        # Simple JSX generation based on UI spec
        elements = ui_spec.get('elements', [])
        jsx_elements = []
        
        for element in elements:
            tag = element.get('tag', 'div')
            content = element.get('content', '')
            props = element.get('props', {})
            
            prop_str = ' '.join([f'{k}="{v}"' for k, v in props.items()])
            jsx_elements.append(f"      <{tag} {prop_str}>{content}</{tag}>")
        
        return "\n".join(jsx_elements) if jsx_elements else "<div>Generated content</div>"
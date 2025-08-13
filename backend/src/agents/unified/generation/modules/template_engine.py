"""
Template Engine Module for Generation Agent
Advanced template processing system with dynamic content generation
"""

from typing import Dict, List, Any, Optional, Callable, Union
import asyncio
import json
import re
import os
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from pathlib import Path
import yaml
from jinja2 import Environment, BaseLoader, meta, select_autoescape
from jinja2.exceptions import TemplateError, TemplateSyntaxError


class TemplateFormat(Enum):
    JINJA2 = "jinja2"
    MUSTACHE = "mustache"
    HANDLEBARS = "handlebars"
    EJS = "ejs"
    CUSTOM = "custom"


class ContentType(Enum):
    SOURCE_CODE = "source_code"
    CONFIG_FILE = "config_file"
    DOCUMENTATION = "documentation"
    TEST_FILE = "test_file"
    BUILD_SCRIPT = "build_script"
    DEPLOYMENT = "deployment"


@dataclass
class Template:
    name: str
    content: str
    format: TemplateFormat
    content_type: ContentType
    variables: List[str]
    description: str = ""
    category: str = ""
    framework: str = ""
    language: str = ""
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class TemplateResult:
    success: bool
    rendered_content: str
    template_name: str
    variables_used: Dict[str, Any]
    processing_time: float
    metadata: Dict[str, Any]
    error: str = ""


@dataclass
class TemplateEngineResult:
    success: bool
    rendered_templates: Dict[str, TemplateResult]
    total_processing_time: float
    templates_processed: int
    variables_context: Dict[str, Any]
    error: str = ""


class CustomTemplateLoader(BaseLoader):
    """Custom template loader for dynamic templates"""

    def __init__(self, templates: Dict[str, str]):
        self.templates = templates

    def get_source(self, environment, template):
        if template in self.templates:
            source = self.templates[template]
            return source, None, lambda: True
        raise TemplateError(f"Template {template} not found")


class TemplateEngine:
    """Advanced template processing engine"""

    def __init__(self):
        self.version = "1.0.0"

        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=CustomTemplateLoader({}),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Custom filters and functions
        self._register_custom_filters()
        self._register_custom_functions()

        # Template libraries
        self.template_libraries = {
            "react": self._get_react_templates(),
            "vue": self._get_vue_templates(),
            "angular": self._get_angular_templates(),
            "express": self._get_express_templates(),
            "fastapi": self._get_fastapi_templates(),
            "django": self._get_django_templates(),
            "flask": self._get_flask_templates(),
            "common": self._get_common_templates(),
        }

        # Variable processors
        self.variable_processors = {
            "camelCase": self._to_camel_case,
            "snake_case": self._to_snake_case,
            "PascalCase": self._to_pascal_case,
            "kebab-case": self._to_kebab_case,
            "UPPER_CASE": self._to_upper_case,
            "plural": self._to_plural,
            "singular": self._to_singular,
        }

        # Template cache
        self.template_cache = {}
        self.cache_enabled = True

        # Context processors
        self.context_processors = []

    async def process_templates(
        self,
        templates: List[str],
        context: Dict[str, Any],
        framework: str = "",
        output_path: str = "",
    ) -> TemplateEngineResult:
        """Process multiple templates with given context"""

        start_time = datetime.now()

        try:
            # Build complete context
            full_context = await self._build_context(context, framework)

            # Get templates to process
            template_objects = await self._get_template_objects(templates, framework)

            # Process templates concurrently
            processing_tasks = []
            for template in template_objects:
                task = self._process_single_template(template, full_context)
                processing_tasks.append(task)

            template_results = await asyncio.gather(*processing_tasks)

            # Build results dictionary
            rendered_templates = {}
            for i, template in enumerate(template_objects):
                rendered_templates[template.name] = template_results[i]

            processing_time = (datetime.now() - start_time).total_seconds()

            return TemplateEngineResult(
                success=True,
                rendered_templates=rendered_templates,
                total_processing_time=processing_time,
                templates_processed=len(template_objects),
                variables_context=full_context,
            )

        except Exception as e:
            return TemplateEngineResult(
                success=False,
                rendered_templates={},
                total_processing_time=(datetime.now() - start_time).total_seconds(),
                templates_processed=0,
                variables_context={},
                error=str(e),
            )

    async def render_template(
        self,
        template_name: str,
        context: Dict[str, Any],
        framework: str = "",
        template_format: TemplateFormat = TemplateFormat.JINJA2,
    ) -> TemplateResult:
        """Render a single template with context"""

        start_time = datetime.now()

        try:
            # Get template object
            template = await self._get_template(template_name, framework)

            if not template:
                return TemplateResult(
                    success=False,
                    rendered_content="",
                    template_name=template_name,
                    variables_used={},
                    processing_time=0,
                    metadata={},
                    error=f"Template {template_name} not found",
                )

            # Build complete context
            full_context = await self._build_context(context, framework)

            # Process template
            result = await self._process_single_template(template, full_context)

            return result

        except Exception as e:
            return TemplateResult(
                success=False,
                rendered_content="",
                template_name=template_name,
                variables_used={},
                processing_time=(datetime.now() - start_time).total_seconds(),
                metadata={},
                error=str(e),
            )

    async def _process_single_template(
        self, template: Template, context: Dict[str, Any]
    ) -> TemplateResult:
        """Process a single template"""

        start_time = datetime.now()

        try:
            # Update loader with current template
            self.jinja_env.loader.templates = {template.name: template.content}

            # Get template variables
            template_vars = self._extract_template_variables(template.content)

            # Filter context to only include relevant variables
            filtered_context = self._filter_context(context, template_vars)

            # Apply variable processors
            processed_context = await self._apply_variable_processors(
                filtered_context, template_vars
            )

            # Render template
            jinja_template = self.jinja_env.get_template(template.name)
            rendered_content = jinja_template.render(processed_context)

            # Post-process content
            final_content = await self._post_process_content(
                rendered_content, template, processed_context
            )

            processing_time = (datetime.now() - start_time).total_seconds()

            return TemplateResult(
                success=True,
                rendered_content=final_content,
                template_name=template.name,
                variables_used=processed_context,
                processing_time=processing_time,
                metadata={
                    "template_format": template.format.value,
                    "content_type": template.content_type.value,
                    "framework": template.framework,
                    "language": template.language,
                    "variables_count": len(template_vars),
                    "content_length": len(final_content),
                },
            )

        except Exception as e:
            return TemplateResult(
                success=False,
                rendered_content="",
                template_name=template.name,
                variables_used={},
                processing_time=(datetime.now() - start_time).total_seconds(),
                metadata={},
                error=str(e),
            )

    async def _build_context(
        self, base_context: Dict[str, Any], framework: str
    ) -> Dict[str, Any]:
        """Build complete template context"""

        # Start with base context
        full_context = base_context.copy()

        # Add framework-specific context
        framework_context = self._get_framework_context(framework)
        full_context.update(framework_context)

        # Add utility functions
        full_context["utils"] = {
            "camelCase": self._to_camel_case,
            "snake_case": self._to_snake_case,
            "PascalCase": self._to_pascal_case,
            "kebab_case": self._to_kebab_case,
            "upper_case": self._to_upper_case,
            "plural": self._to_plural,
            "singular": self._to_singular,
            "current_year": datetime.now().year,
            "current_date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().isoformat(),
        }

        # Add framework-specific utilities
        if framework == "react":
            full_context["utils"]["componentName"] = lambda name: self._to_pascal_case(
                name
            )
            full_context["utils"][
                "hookName"
            ] = lambda name: f"use{self._to_pascal_case(name)}"
        elif framework == "vue":
            full_context["utils"]["componentName"] = lambda name: self._to_pascal_case(
                name
            )
            full_context["utils"][
                "composableName"
            ] = lambda name: f"use{self._to_pascal_case(name)}"
        elif framework in ["fastapi", "django", "flask"]:
            full_context["utils"]["className"] = lambda name: self._to_pascal_case(name)
            full_context["utils"]["functionName"] = lambda name: self._to_snake_case(
                name
            )

        # Process context processors
        for processor in self.context_processors:
            full_context = await processor(full_context, framework)

        return full_context

    def _get_framework_context(self, framework: str) -> Dict[str, Any]:
        """Get framework-specific context variables"""

        framework_contexts = {
            "react": {
                "react_version": "18.2.0",
                "typescript": True,
                "jsx": True,
                "hooks": True,
                "router": "react-router-dom",
            },
            "vue": {
                "vue_version": "3.2.47",
                "composition_api": True,
                "typescript": True,
                "router": "vue-router",
                "store": "pinia",
            },
            "angular": {
                "angular_version": "15.1.0",
                "typescript": True,
                "cli": True,
                "material": True,
            },
            "express": {
                "express_version": "4.18.2",
                "middleware": ["cors", "helmet", "morgan"],
                "typescript": True,
            },
            "fastapi": {
                "fastapi_version": "0.95.0",
                "python_version": "3.9",
                "async": True,
                "pydantic": True,
            },
            "django": {
                "django_version": "4.1.6",
                "python_version": "3.9",
                "drf": True,
                "admin": True,
            },
            "flask": {
                "flask_version": "2.2.3",
                "python_version": "3.9",
                "sqlalchemy": True,
                "migrate": True,
            },
        }

        return framework_contexts.get(framework, {})

    async def _get_template_objects(
        self, template_names: List[str], framework: str
    ) -> List[Template]:
        """Get template objects from names"""

        template_objects = []

        for name in template_names:
            template = await self._get_template(name, framework)
            if template:
                template_objects.append(template)

        return template_objects

    async def _get_template(self, name: str, framework: str) -> Optional[Template]:
        """Get template by name and framework"""

        # Check cache first
        cache_key = f"{framework}:{name}"
        if self.cache_enabled and cache_key in self.template_cache:
            return self.template_cache[cache_key]

        # Search in framework-specific templates
        if framework in self.template_libraries:
            for template in self.template_libraries[framework]:
                if template.name == name:
                    if self.cache_enabled:
                        self.template_cache[cache_key] = template
                    return template

        # Search in common templates
        for template in self.template_libraries.get("common", []):
            if template.name == name:
                if self.cache_enabled:
                    self.template_cache[cache_key] = template
                return template

        return None

    def _extract_template_variables(self, template_content: str) -> List[str]:
        """Extract variables from template content"""

        try:
            ast = self.jinja_env.parse(template_content)
            variables = meta.find_undeclared_variables(ast)
            return list(variables)
        except:
            # Fallback to regex extraction
            pattern = r"\{\{\s*([^}]+)\s*\}\}"
            matches = re.findall(pattern, template_content)
            variables = []
            for match in matches:
                # Clean up variable names
                var_name = match.split("|")[0].split(".")[0].strip()
                if var_name not in variables:
                    variables.append(var_name)
            return variables

    def _filter_context(
        self, context: Dict[str, Any], template_vars: List[str]
    ) -> Dict[str, Any]:
        """Filter context to include only relevant variables"""

        filtered = {}

        for var_name in template_vars:
            if var_name in context:
                filtered[var_name] = context[var_name]

        # Always include utils
        if "utils" in context:
            filtered["utils"] = context["utils"]

        return filtered

    async def _apply_variable_processors(
        self, context: Dict[str, Any], template_vars: List[str]
    ) -> Dict[str, Any]:
        """Apply variable processors to context"""

        processed = context.copy()

        # Apply string transformations
        for var_name in template_vars:
            if var_name in processed:
                value = processed[var_name]

                if isinstance(value, str):
                    # Add transformed versions
                    processed[f"{var_name}_camel"] = self._to_camel_case(value)
                    processed[f"{var_name}_snake"] = self._to_snake_case(value)
                    processed[f"{var_name}_pascal"] = self._to_pascal_case(value)
                    processed[f"{var_name}_kebab"] = self._to_kebab_case(value)
                    processed[f"{var_name}_upper"] = self._to_upper_case(value)

        return processed

    async def _post_process_content(
        self, content: str, template: Template, context: Dict[str, Any]
    ) -> str:
        """Post-process rendered content"""

        processed_content = content

        # Remove excessive blank lines
        processed_content = re.sub(r"\n\s*\n\s*\n", "\n\n", processed_content)

        # Fix indentation for specific content types
        if template.content_type == ContentType.SOURCE_CODE:
            processed_content = self._fix_code_indentation(
                processed_content, template.language
            )

        # Add file headers if needed
        if template.content_type in [ContentType.SOURCE_CODE, ContentType.TEST_FILE]:
            processed_content = self._add_file_header(
                processed_content, template, context
            )

        # Format code if possible
        if template.language in ["javascript", "typescript"]:
            processed_content = self._format_js_code(processed_content)
        elif template.language == "python":
            processed_content = self._format_python_code(processed_content)

        return processed_content

    def _fix_code_indentation(self, content: str, language: str) -> str:
        """Fix code indentation"""

        lines = content.split("\n")
        if not lines:
            return content

        # Remove leading/trailing empty lines
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()

        if not lines:
            return ""

        # Find minimum indentation (excluding empty lines)
        min_indent = float("inf")
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                min_indent = min(min_indent, indent)

        # Remove common indentation
        if min_indent > 0 and min_indent != float("inf"):
            lines = [line[min_indent:] if line.strip() else line for line in lines]

        return "\n".join(lines)

    def _add_file_header(
        self, content: str, template: Template, context: Dict[str, Any]
    ) -> str:
        """Add file header comments"""

        if template.language in ["javascript", "typescript"]:
            header = f"""/**
 * Generated by T-Developer
 * Template: {template.name}
 * Framework: {template.framework}
 * Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 */

"""
        elif template.language == "python":
            header = f'''"""
Generated by T-Developer
Template: {template.name}
Framework: {template.framework}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

'''
        else:
            return content

        return header + content

    def _format_js_code(self, content: str) -> str:
        """Basic JavaScript/TypeScript formatting"""

        # Add missing semicolons (basic implementation)
        lines = content.split("\n")
        formatted_lines = []

        for line in lines:
            stripped = line.rstrip()
            if stripped and not stripped.endswith((";", "{", "}", ")", ",", ":", "//")):
                if any(
                    keyword in stripped
                    for keyword in ["const ", "let ", "var ", "return "]
                ):
                    if not stripped.endswith(","):
                        stripped += ";"
            formatted_lines.append(stripped)

        return "\n".join(formatted_lines)

    def _format_python_code(self, content: str) -> str:
        """Basic Python formatting"""

        lines = content.split("\n")
        formatted_lines = []

        for line in lines:
            # Remove trailing whitespace
            formatted_line = line.rstrip()
            formatted_lines.append(formatted_line)

        return "\n".join(formatted_lines)

    def _register_custom_filters(self):
        """Register custom Jinja2 filters"""

        self.jinja_env.filters["camelCase"] = self._to_camel_case
        self.jinja_env.filters["snake_case"] = self._to_snake_case
        self.jinja_env.filters["PascalCase"] = self._to_pascal_case
        self.jinja_env.filters["kebab_case"] = self._to_kebab_case
        self.jinja_env.filters["upper_case"] = self._to_upper_case
        self.jinja_env.filters["plural"] = self._to_plural
        self.jinja_env.filters["singular"] = self._to_singular
        self.jinja_env.filters["indent"] = self._indent_text
        self.jinja_env.filters["quote"] = self._quote_string

    def _register_custom_functions(self):
        """Register custom Jinja2 global functions"""

        self.jinja_env.globals["range"] = range
        self.jinja_env.globals["len"] = len
        self.jinja_env.globals["str"] = str
        self.jinja_env.globals["int"] = int
        self.jinja_env.globals["float"] = float
        self.jinja_env.globals["bool"] = bool
        self.jinja_env.globals["enumerate"] = enumerate
        self.jinja_env.globals["zip"] = zip

    # String transformation utilities
    def _to_camel_case(self, text: str) -> str:
        """Convert to camelCase"""
        if not text:
            return text

        components = re.split(r"[_\-\s]+", str(text))
        return components[0].lower() + "".join(
            word.capitalize() for word in components[1:]
        )

    def _to_snake_case(self, text: str) -> str:
        """Convert to snake_case"""
        if not text:
            return text

        # Insert underscore before uppercase letters
        s1 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", str(text))
        # Replace spaces and hyphens with underscores
        s2 = re.sub(r"[_\-\s]+", "_", s1)
        return s2.lower()

    def _to_pascal_case(self, text: str) -> str:
        """Convert to PascalCase"""
        if not text:
            return text

        components = re.split(r"[_\-\s]+", str(text))
        return "".join(word.capitalize() for word in components)

    def _to_kebab_case(self, text: str) -> str:
        """Convert to kebab-case"""
        if not text:
            return text

        # Insert hyphen before uppercase letters
        s1 = re.sub("([a-z0-9])([A-Z])", r"\1-\2", str(text))
        # Replace underscores and spaces with hyphens
        s2 = re.sub(r"[_\s]+", "-", s1)
        return s2.lower()

    def _to_upper_case(self, text: str) -> str:
        """Convert to UPPER_CASE"""
        return self._to_snake_case(text).upper()

    def _to_plural(self, text: str) -> str:
        """Convert to plural form (simplified)"""
        if not text:
            return text

        text = str(text)
        if text.endswith("y"):
            return text[:-1] + "ies"
        elif text.endswith(("s", "sh", "ch", "x", "z")):
            return text + "es"
        else:
            return text + "s"

    def _to_singular(self, text: str) -> str:
        """Convert to singular form (simplified)"""
        if not text:
            return text

        text = str(text)
        if text.endswith("ies"):
            return text[:-3] + "y"
        elif text.endswith("es"):
            return text[:-2]
        elif text.endswith("s"):
            return text[:-1]
        else:
            return text

    def _indent_text(self, text: str, spaces: int = 4) -> str:
        """Indent text by specified spaces"""
        if not text:
            return text

        indent = " " * spaces
        lines = str(text).split("\n")
        return "\n".join(indent + line if line.strip() else line for line in lines)

    def _quote_string(self, text: str, quote_char: str = '"') -> str:
        """Quote a string"""
        return f"{quote_char}{text}{quote_char}"

    # Template libraries (simplified - would be much larger in production)
    def _get_react_templates(self) -> List[Template]:
        """Get React-specific templates"""

        return [
            Template(
                name="react_component",
                content="""import React from 'react';
{% if typescript %}
interface {{ component_name }}Props {
  // Define props here
}
{% endif %}

const {{ component_name }}{% if typescript %}: React.FC<{{ component_name }}Props>{% endif %} = ({% if typescript %}props{% endif %}) => {
  return (
    <div className="{{ component_name | kebab_case }}">
      <h1>{{ component_name }} Component</h1>
    </div>
  );
};

export default {{ component_name }};""",
                format=TemplateFormat.JINJA2,
                content_type=ContentType.SOURCE_CODE,
                variables=["component_name", "typescript"],
                framework="react",
                language="typescript",
            ),
            Template(
                name="react_hook",
                content="""import { useState, useEffect } from 'react';

export const use{{ hook_name | PascalCase }} = () => {
  const [state, setState] = useState(null);

  useEffect(() => {
    // Hook logic here
  }, []);

  return {
    state,
    setState
  };
};""",
                format=TemplateFormat.JINJA2,
                content_type=ContentType.SOURCE_CODE,
                variables=["hook_name"],
                framework="react",
                language="typescript",
            ),
        ]

    def _get_vue_templates(self) -> List[Template]:
        """Get Vue-specific templates"""

        return [
            Template(
                name="vue_component",
                content="""<template>
  <div class="{{ component_name | kebab_case }}">
    <h1>{{ component_name }} Component</h1>
  </div>
</template>

<script{% if typescript %} lang="ts"{% endif %}>
import { defineComponent } from 'vue'

export default defineComponent({
  name: '{{ component_name }}',
  setup() {
    // Component logic here

    return {
      // Expose reactive data and methods
    }
  }
})
</script>

<style scoped>
.{{ component_name | kebab_case }} {
  /* Component styles here */
}
</style>""",
                format=TemplateFormat.JINJA2,
                content_type=ContentType.SOURCE_CODE,
                variables=["component_name", "typescript"],
                framework="vue",
                language="typescript",
            )
        ]

    def _get_angular_templates(self) -> List[Template]:
        """Get Angular-specific templates"""

        return [
            Template(
                name="angular_component",
                content="""import { Component } from '@angular/core';

@Component({
  selector: 'app-{{ component_name | kebab_case }}',
  templateUrl: './{{ component_name | kebab_case }}.component.html',
  styleUrls: ['./{{ component_name | kebab_case }}.component.css']
})
export class {{ component_name | PascalCase }}Component {
  constructor() { }

  ngOnInit(): void {
    // Component initialization logic
  }
}""",
                format=TemplateFormat.JINJA2,
                content_type=ContentType.SOURCE_CODE,
                variables=["component_name"],
                framework="angular",
                language="typescript",
            )
        ]

    def _get_express_templates(self) -> List[Template]:
        """Get Express-specific templates"""

        return [
            Template(
                name="express_controller",
                content="""import { Request, Response } from 'express';

export class {{ controller_name | PascalCase }}Controller {

  async getAll(req: Request, res: Response) {
    try {
      // Get all {{ entity_name | plural }}
      const {{ entity_name | plural }} = [];

      res.json({
        success: true,
        data: {{ entity_name | plural }}
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  }

  async getById(req: Request, res: Response) {
    try {
      const { id } = req.params;
      // Get {{ entity_name }} by id

      res.json({
        success: true,
        data: null
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  }

  async create(req: Request, res: Response) {
    try {
      const {{ entity_name }}Data = req.body;
      // Create new {{ entity_name }}

      res.status(201).json({
        success: true,
        data: null
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  }
}""",
                format=TemplateFormat.JINJA2,
                content_type=ContentType.SOURCE_CODE,
                variables=["controller_name", "entity_name"],
                framework="express",
                language="typescript",
            )
        ]

    def _get_fastapi_templates(self) -> List[Template]:
        """Get FastAPI-specific templates"""

        return [
            Template(
                name="fastapi_model",
                content="""from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class {{ model_name | PascalCase }}Base(BaseModel):
    \"\"\"Base {{ model_name }} model\"\"\"
    # Define base fields here
    pass

class {{ model_name | PascalCase }}Create({{ model_name | PascalCase }}Base):
    \"\"\"{{ model_name }} creation model\"\"\"
    pass

class {{ model_name | PascalCase }}Update({{ model_name | PascalCase }}Base):
    \"\"\"{{ model_name }} update model\"\"\"
    pass

class {{ model_name | PascalCase }}({{ model_name | PascalCase }}Base):
    \"\"\"{{ model_name }} response model\"\"\"
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True""",
                format=TemplateFormat.JINJA2,
                content_type=ContentType.SOURCE_CODE,
                variables=["model_name"],
                framework="fastapi",
                language="python",
            )
        ]

    def _get_django_templates(self) -> List[Template]:
        """Get Django-specific templates"""

        return [
            Template(
                name="django_model",
                content="""from django.db import models
from django.utils import timezone

class {{ model_name | PascalCase }}(models.Model):
    \"\"\"{{ model_name }} model\"\"\"

    # Define fields here
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = '{{ model_name | snake_case }}'
        ordering = ['-created_at']
        verbose_name = '{{ model_name | title }}'
        verbose_name_plural = '{{ model_name | plural | title }}'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)""",
                format=TemplateFormat.JINJA2,
                content_type=ContentType.SOURCE_CODE,
                variables=["model_name"],
                framework="django",
                language="python",
            )
        ]

    def _get_flask_templates(self) -> List[Template]:
        """Get Flask-specific templates"""

        return [
            Template(
                name="flask_model",
                content="""from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class {{ model_name | PascalCase }}(db.Model):
    \"\"\"{{ model_name }} model\"\"\"

    __tablename__ = '{{ model_name | snake_case }}'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<{{ model_name | PascalCase }} {self.name}>'""",
                format=TemplateFormat.JINJA2,
                content_type=ContentType.SOURCE_CODE,
                variables=["model_name"],
                framework="flask",
                language="python",
            )
        ]

    def _get_common_templates(self) -> List[Template]:
        """Get common templates for all frameworks"""

        return [
            Template(
                name="readme",
                content="""# {{ project_name | title }}

{{ project_description }}

## Installation

1. Clone the repository
2. Install dependencies
3. Run the project

## Usage

Describe how to use your project here.

## Contributing

1. Fork the project
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## License

MIT License""",
                format=TemplateFormat.JINJA2,
                content_type=ContentType.DOCUMENTATION,
                variables=["project_name", "project_description"],
                framework="common",
                language="markdown",
            ),
            Template(
                name="gitignore",
                content="""# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
pip-log.txt
pip-delete-this-directory.txt

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Build outputs
dist/
build/
*.tgz
*.tar.gz

# Environment variables
.env
.env.local
.env.production""",
                format=TemplateFormat.JINJA2,
                content_type=ContentType.CONFIG_FILE,
                variables=[],
                framework="common",
                language="text",
            ),
        ]

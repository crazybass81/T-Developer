"""
Code Generator Module
Core code generation functionality for different frameworks and languages
"""

from typing import Dict, List, Any, Optional, Tuple
import os
import json
from datetime import datetime
from pathlib import Path
import re


class CodeGenerator:
    """Advanced code generator with multi-framework support"""
    
    def __init__(self):
        # Framework-specific generators
        self.generators = {
            'react': ReactGenerator(),
            'vue': VueGenerator(),
            'angular': AngularGenerator(),
            'express': ExpressGenerator(),
            'fastapi': FastAPIGenerator(),
            'django': DjangoGenerator(),
            'flask': FlaskGenerator(),
            'svelte': SvelteGenerator(),
            'next.js': NextJSGenerator(),
            'nuxt.js': NuxtGenerator()
        }
        
        # Language-specific code formatters
        self.formatters = {
            'javascript': JavaScriptFormatter(),
            'typescript': TypeScriptFormatter(),
            'python': PythonFormatter(),
            'java': JavaFormatter(),
            'go': GoFormatter()
        }
        
        # Common code patterns
        self.patterns = {
            'component_structure': self._get_component_patterns(),
            'service_structure': self._get_service_patterns(),
            'utility_structure': self._get_utility_patterns(),
            'configuration_structure': self._get_config_patterns()
        }
        
        # Code generation statistics
        self.generation_stats = {
            'files_generated': 0,
            'lines_generated': 0,
            'components_integrated': 0,
            'errors_encountered': 0
        }
        
    async def generate_core_files(
        self, 
        context: Dict[str, Any], 
        output_path: str
    ) -> 'GenerationResult':
        """Generate core application files"""
        
        try:
            framework = context.get('target_framework', 'react')
            language = context.get('target_language', 'javascript')
            
            if framework not in self.generators:
                return GenerationResult(False, {}, f"Unsupported framework: {framework}")
            
            generator = self.generators[framework]
            formatter = self.formatters.get(language, self.formatters['javascript'])
            
            # Generate main application files
            core_files = {}
            
            # Entry point file
            entry_file = await generator.generate_entry_point(context)
            if entry_file:
                formatted_entry = formatter.format_code(entry_file['content'])
                core_files[entry_file['path']] = formatted_entry
                await self._write_file(output_path, entry_file['path'], formatted_entry)
            
            # Main app component/module
            main_app = await generator.generate_main_app(context)
            if main_app:
                formatted_app = formatter.format_code(main_app['content'])
                core_files[main_app['path']] = formatted_app
                await self._write_file(output_path, main_app['path'], formatted_app)
            
            # Configuration files
            config_files = await generator.generate_config_files(context)
            for config_file in config_files:
                # Config files might not need code formatting
                if config_file['type'] == 'json':
                    content = json.dumps(config_file['content'], indent=2)
                else:
                    content = formatter.format_code(config_file['content'])
                
                core_files[config_file['path']] = content
                await self._write_file(output_path, config_file['path'], content)
            
            # Routing/navigation setup
            routing_files = await generator.generate_routing(context)
            for routing_file in routing_files:
                formatted_routing = formatter.format_code(routing_file['content'])
                core_files[routing_file['path']] = formatted_routing
                await self._write_file(output_path, routing_file['path'], formatted_routing)
            
            # State management setup (if applicable)
            state_files = await generator.generate_state_management(context)
            for state_file in state_files:
                formatted_state = formatter.format_code(state_file['content'])
                core_files[state_file['path']] = formatted_state
                await self._write_file(output_path, state_file['path'], formatted_state)
            
            # Utility functions and helpers
            utility_files = await self.generate_utilities(context, language)
            for util_path, util_content in utility_files.items():
                formatted_util = formatter.format_code(util_content)
                core_files[util_path] = formatted_util
                await self._write_file(output_path, util_path, formatted_util)
            
            self.generation_stats['files_generated'] += len(core_files)
            self.generation_stats['lines_generated'] += sum(
                len(content.split('\n')) for content in core_files.values()
            )
            
            return GenerationResult(True, core_files)
            
        except Exception as e:
            self.generation_stats['errors_encountered'] += 1
            return GenerationResult(False, {}, str(e))
    
    async def generate_component_integration(
        self, 
        components: List[Dict[str, Any]], 
        output_path: str
    ) -> 'GenerationResult':
        """Generate code to integrate selected components"""
        
        try:
            integration_files = {}
            
            for component in components:
                # Generate component wrapper/integration
                integration = await self._generate_component_wrapper(component)
                
                if integration:
                    integration_files[integration['path']] = integration['content']
                    await self._write_file(output_path, integration['path'], integration['content'])
                
                # Generate component usage examples
                examples = await self._generate_component_examples(component)
                for example in examples:
                    integration_files[example['path']] = example['content']
                    await self._write_file(output_path, example['path'], example['content'])
                
                # Generate component configuration
                config = await self._generate_component_config(component)
                if config:
                    integration_files[config['path']] = config['content']
                    await self._write_file(output_path, config['path'], config['content'])
            
            # Generate master integration file
            master_integration = await self._generate_master_integration(components)
            if master_integration:
                integration_files[master_integration['path']] = master_integration['content']
                await self._write_file(
                    output_path, 
                    master_integration['path'], 
                    master_integration['content']
                )
            
            self.generation_stats['components_integrated'] += len(components)
            self.generation_stats['files_generated'] += len(integration_files)
            
            return GenerationResult(True, integration_files)
            
        except Exception as e:
            self.generation_stats['errors_encountered'] += 1
            return GenerationResult(False, {}, str(e))
    
    async def generate_utilities(self, context: Dict[str, Any], language: str) -> Dict[str, str]:
        """Generate common utility functions"""
        
        utilities = {}
        
        # API utilities
        api_util = self._generate_api_utilities(context, language)
        utilities['src/utils/api.js'] = api_util
        
        # Validation utilities
        validation_util = self._generate_validation_utilities(context, language)
        utilities['src/utils/validation.js'] = validation_util
        
        # String utilities
        string_util = self._generate_string_utilities(language)
        utilities['src/utils/strings.js'] = string_util
        
        # Date utilities
        date_util = self._generate_date_utilities(language)
        utilities['src/utils/dates.js'] = date_util
        
        # Storage utilities
        storage_util = self._generate_storage_utilities(language)
        utilities['src/utils/storage.js'] = storage_util
        
        # Error handling utilities
        error_util = self._generate_error_utilities(language)
        utilities['src/utils/errors.js'] = error_util
        
        return utilities
    
    async def _generate_component_wrapper(self, component: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Generate wrapper code for a component"""
        
        component_name = component.get('name', 'UnknownComponent')
        component_type = component.get('category', 'Component')
        technology = component.get('technology', 'react')
        
        # Sanitize component name for code
        safe_name = re.sub(r'[^a-zA-Z0-9]', '', component_name)
        
        if technology.lower() == 'react':
            content = f'''import React from 'react';
import {{ {safe_name} }} from '{component.get("import_path", safe_name.lower())}';

interface {safe_name}WrapperProps {{
  // Add props based on component requirements
  className?: string;
  children?: React.ReactNode;
}}

export const {safe_name}Wrapper: React.FC<{safe_name}WrapperProps> = ({{
  className,
  children,
  ...props
}}) => {{
  return (
    <div className={{`{safe_name.lower()}-wrapper ${{className || ''}}`}}>
      <{safe_name} {{...props}}>
        {{children}}
      </{safe_name}>
    </div>
  );
}};

export default {safe_name}Wrapper;
'''
        elif technology.lower() == 'vue':
            content = f'''<template>
  <div class="{safe_name.lower()}-wrapper">
    <{safe_name} v-bind="$attrs" v-on="$listeners">
      <slot></slot>
    </{safe_name}>
  </div>
</template>

<script>
import {safe_name} from '{component.get("import_path", safe_name.lower())}';

export default {{
  name: '{safe_name}Wrapper',
  components: {{
    {safe_name}
  }},
  props: {{
    // Add props based on component requirements
  }},
  data() {{
    return {{
      // Component state
    }};
  }},
  methods: {{
    // Component methods
  }}
}};
</script>

<style scoped>
.{safe_name.lower()}-wrapper {{
  /* Component-specific styles */
}}
</style>
'''
        else:
            return None
        
        return {
            'path': f'src/components/{safe_name}Wrapper.{self._get_file_extension(technology)}',
            'content': content
        }
    
    async def _generate_component_examples(self, component: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate usage examples for a component"""
        
        examples = []
        component_name = component.get('name', 'UnknownComponent')
        safe_name = re.sub(r'[^a-zA-Z0-9]', '', component_name)
        technology = component.get('technology', 'react')
        
        if technology.lower() == 'react':
            example_content = f'''import React from 'react';
import {safe_name}Wrapper from '../components/{safe_name}Wrapper';

export const {safe_name}Example = () => {{
  return (
    <div className="example-container">
      <h2>{component_name} Example</h2>
      
      <div className="example-basic">
        <h3>Basic Usage</h3>
        <{safe_name}Wrapper>
          Basic example content
        </{safe_name}Wrapper>
      </div>
      
      <div className="example-advanced">
        <h3>Advanced Usage</h3>
        <{safe_name}Wrapper className="custom-style">
          Advanced example with props
        </{safe_name}Wrapper>
      </div>
    </div>
  );
}};

export default {safe_name}Example;
'''
            
            examples.append({
                'path': f'src/examples/{safe_name}Example.{self._get_file_extension(technology)}',
                'content': example_content
            })
        
        return examples
    
    async def _generate_component_config(self, component: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Generate configuration for a component"""
        
        config = {
            'name': component.get('name'),
            'version': component.get('version', '1.0.0'),
            'description': component.get('description', ''),
            'category': component.get('category'),
            'technology': component.get('technology'),
            'features': component.get('features', []),
            'dependencies': component.get('dependencies', {}),
            'configuration': {
                'theme': 'default',
                'size': 'medium',
                'variant': 'primary'
            }
        }
        
        return {
            'path': f'src/config/components/{component.get("id", "unknown")}.json',
            'content': json.dumps(config, indent=2)
        }
    
    async def _generate_master_integration(self, components: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate master integration file"""
        
        imports = []
        exports = []
        
        for component in components:
            safe_name = re.sub(r'[^a-zA-Z0-9]', '', component.get('name', 'Component'))
            imports.append(f"import {safe_name}Wrapper from './components/{safe_name}Wrapper';")
            exports.append(f"  {safe_name}Wrapper,")
        
        content = f'''// Auto-generated component integrations
{chr(10).join(imports)}

export {{
{chr(10).join(exports)}
}};

// Component registry for dynamic imports
export const componentRegistry = {{
{chr(10).join([f'  "{re.sub(r"[^a-zA-Z0-9]", "", comp.get("name", ""))}"): {re.sub(r"[^a-zA-Z0-9]", "", comp.get("name", ""))}Wrapper,' for comp in components])}
}};

// Get component by name
export const getComponent = (name: string) => {{
  return componentRegistry[name] || null;
}};

// Get all available components
export const getAllComponents = () => {{
  return Object.keys(componentRegistry);
}};
'''
        
        return {
            'path': 'src/components/index.ts',
            'content': content
        }
    
    def _generate_api_utilities(self, context: Dict[str, Any], language: str) -> str:
        """Generate API utility functions"""
        
        if language == 'typescript':
            return '''interface ApiResponse<T = any> {
  data: T;
  status: number;
  message?: string;
}

interface ApiError {
  message: string;
  status: number;
  code?: string;
}

class ApiClient {
  private baseURL: string;
  private defaultHeaders: Record<string, string>;

  constructor(baseURL: string = '/api') {
    this.baseURL = baseURL;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`;
    const config: RequestInit = {
      headers: { ...this.defaultHeaders, ...options.headers },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || `HTTP error! status: ${response.status}`);
      }

      return {
        data,
        status: response.status,
        message: data.message,
      };
    } catch (error) {
      throw new Error(`API request failed: ${error.message}`);
    }
  }

  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint);
  }

  async post<T>(endpoint: string, data: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put<T>(endpoint: string, data: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'DELETE',
    });
  }
}

export const apiClient = new ApiClient();
export type { ApiResponse, ApiError };
'''
        else:  # JavaScript
            return '''class ApiClient {
  constructor(baseURL = '/api') {
    this.baseURL = baseURL;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: { ...this.defaultHeaders, ...options.headers },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || `HTTP error! status: ${response.status}`);
      }

      return {
        data,
        status: response.status,
        message: data.message,
      };
    } catch (error) {
      throw new Error(`API request failed: ${error.message}`);
    }
  }

  async get(endpoint) {
    return this.request(endpoint);
  }

  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async delete(endpoint) {
    return this.request(endpoint, {
      method: 'DELETE',
    });
  }
}

export const apiClient = new ApiClient();
'''
    
    def _generate_validation_utilities(self, context: Dict[str, Any], language: str) -> str:
        """Generate validation utility functions"""
        
        if language == 'typescript':
            return '''type ValidationRule = {
  rule: (value: any) => boolean;
  message: string;
};

type ValidationRules = {
  [key: string]: ValidationRule[];
};

class Validator {
  static email(value: string): boolean {
    const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
    return emailRegex.test(value);
  }

  static minLength(min: number) {
    return (value: string): boolean => value.length >= min;
  }

  static maxLength(max: number) {
    return (value: string): boolean => value.length <= max;
  }

  static required(value: any): boolean {
    return value !== null && value !== undefined && value !== '';
  }

  static numeric(value: any): boolean {
    return !isNaN(Number(value));
  }

  static validate(data: Record<string, any>, rules: ValidationRules): string[] {
    const errors: string[] = [];

    for (const field in rules) {
      const fieldRules = rules[field];
      const value = data[field];

      for (const { rule, message } of fieldRules) {
        if (!rule(value)) {
          errors.push(`${field}: ${message}`);
        }
      }
    }

    return errors;
  }
}

export { Validator, type ValidationRule, type ValidationRules };
'''
        else:  # JavaScript
            return '''class Validator {
  static email(value) {
    const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
    return emailRegex.test(value);
  }

  static minLength(min) {
    return (value) => value.length >= min;
  }

  static maxLength(max) {
    return (value) => value.length <= max;
  }

  static required(value) {
    return value !== null && value !== undefined && value !== '';
  }

  static numeric(value) {
    return !isNaN(Number(value));
  }

  static validate(data, rules) {
    const errors = [];

    for (const field in rules) {
      const fieldRules = rules[field];
      const value = data[field];

      for (const { rule, message } of fieldRules) {
        if (!rule(value)) {
          errors.push(`${field}: ${message}`);
        }
      }
    }

    return errors;
  }
}

export { Validator };
'''
    
    def _generate_string_utilities(self, language: str) -> str:
        """Generate string utility functions"""
        
        return '''export const StringUtils = {
  capitalize: (str) => str.charAt(0).toUpperCase() + str.slice(1),
  
  camelCase: (str) => {
    return str
      .replace(/(?:^\\w|[A-Z]|\\b\\w)/g, (word, index) => {
        return index === 0 ? word.toLowerCase() : word.toUpperCase();
      })
      .replace(/\\s+/g, '');
  },
  
  kebabCase: (str) => {
    return str
      .match(/[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+/g)
      .map(s => s.toLowerCase())
      .join('-');
  },
  
  truncate: (str, length, suffix = '...') => {
    return str.length > length ? str.substring(0, length) + suffix : str;
  },
  
  slugify: (str) => {
    return str
      .toLowerCase()
      .replace(/[^a-z0-9 -]/g, '')
      .replace(/\\s+/g, '-')
      .replace(/-+/g, '-')
      .trim();
  },
  
  randomString: (length = 8) => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  }
};
'''
    
    def _generate_date_utilities(self, language: str) -> str:
        """Generate date utility functions"""
        
        return '''export const DateUtils = {
  format: (date, format = 'YYYY-MM-DD') => {
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const hour = String(d.getHours()).padStart(2, '0');
    const minute = String(d.getMinutes()).padStart(2, '0');
    
    return format
      .replace('YYYY', year)
      .replace('MM', month)
      .replace('DD', day)
      .replace('HH', hour)
      .replace('mm', minute);
  },
  
  isValid: (date) => {
    return date instanceof Date && !isNaN(date);
  },
  
  addDays: (date, days) => {
    const result = new Date(date);
    result.setDate(result.getDate() + days);
    return result;
  },
  
  diffDays: (date1, date2) => {
    const diffTime = Math.abs(date2 - date1);
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  },
  
  isToday: (date) => {
    const today = new Date();
    const d = new Date(date);
    return d.toDateString() === today.toDateString();
  },
  
  isWeekend: (date) => {
    const day = new Date(date).getDay();
    return day === 0 || day === 6;
  }
};
'''
    
    def _generate_storage_utilities(self, language: str) -> str:
        """Generate storage utility functions"""
        
        return '''export const StorageUtils = {
  set: (key, value) => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (error) {
      console.error('Failed to save to localStorage:', error);
      return false;
    }
  },
  
  get: (key, defaultValue = null) => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
      console.error('Failed to read from localStorage:', error);
      return defaultValue;
    }
  },
  
  remove: (key) => {
    try {
      localStorage.removeItem(key);
      return true;
    } catch (error) {
      console.error('Failed to remove from localStorage:', error);
      return false;
    }
  },
  
  clear: () => {
    try {
      localStorage.clear();
      return true;
    } catch (error) {
      console.error('Failed to clear localStorage:', error);
      return false;
    }
  },
  
  exists: (key) => {
    return localStorage.getItem(key) !== null;
  },
  
  // Session storage methods
  sessionSet: (key, value) => {
    try {
      sessionStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (error) {
      console.error('Failed to save to sessionStorage:', error);
      return false;
    }
  },
  
  sessionGet: (key, defaultValue = null) => {
    try {
      const item = sessionStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
      console.error('Failed to read from sessionStorage:', error);
      return defaultValue;
    }
  }
};
'''
    
    def _generate_error_utilities(self, language: str) -> str:
        """Generate error handling utilities"""
        
        return '''export class AppError extends Error {
  constructor(message, code = 'UNKNOWN_ERROR', statusCode = 500) {
    super(message);
    this.name = 'AppError';
    this.code = code;
    this.statusCode = statusCode;
    this.timestamp = new Date().toISOString();
  }
}

export const ErrorHandler = {
  handle: (error, context = {}) => {
    const errorInfo = {
      message: error.message,
      code: error.code || 'UNKNOWN_ERROR',
      statusCode: error.statusCode || 500,
      timestamp: new Date().toISOString(),
      context,
      stack: error.stack
    };
    
    // Log error (in production, send to logging service)
    console.error('Error occurred:', errorInfo);
    
    return errorInfo;
  },
  
  createNotFound: (resource) => {
    return new AppError(`${resource} not found`, 'NOT_FOUND', 404);
  },
  
  createValidation: (message) => {
    return new AppError(message, 'VALIDATION_ERROR', 400);
  },
  
  createUnauthorized: (message = 'Unauthorized') => {
    return new AppError(message, 'UNAUTHORIZED', 401);
  },
  
  createForbidden: (message = 'Forbidden') => {
    return new AppError(message, 'FORBIDDEN', 403);
  },
  
  createInternal: (message = 'Internal server error') => {
    return new AppError(message, 'INTERNAL_ERROR', 500);
  }
};
'''
    
    async def _write_file(self, base_path: str, file_path: str, content: str):
        """Write generated file to disk"""
        
        full_path = os.path.join(base_path, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _get_file_extension(self, technology: str) -> str:
        """Get appropriate file extension for technology"""
        
        extensions = {
            'react': 'tsx',
            'vue': 'vue',
            'angular': 'ts',
            'svelte': 'svelte',
            'express': 'ts',
            'fastapi': 'py',
            'django': 'py',
            'flask': 'py'
        }
        
        return extensions.get(technology.lower(), 'js')
    
    def _get_component_patterns(self) -> Dict[str, str]:
        """Get component code patterns"""
        return {
            'react_component': '''import React from 'react';

interface {ComponentName}Props {
  // Props interface
}

export const {ComponentName}: React.FC<{ComponentName}Props> = (props) => {
  return (
    <div>
      {/* Component content */}
    </div>
  );
};

export default {ComponentName};''',
            
            'vue_component': '''<template>
  <div>
    <!-- Component content -->
  </div>
</template>

<script>
export default {
  name: '{ComponentName}',
  props: {
    // Component props
  },
  data() {
    return {
      // Component state
    };
  }
};
</script>

<style scoped>
/* Component styles */
</style>'''
        }
    
    def _get_service_patterns(self) -> Dict[str, str]:
        """Get service code patterns"""
        return {
            'api_service': '''export class {ServiceName}Service {
  private baseURL = '/api/{endpoint}';
  
  async getAll() {
    // Implementation
  }
  
  async getById(id: string) {
    // Implementation
  }
  
  async create(data: any) {
    // Implementation
  }
  
  async update(id: string, data: any) {
    // Implementation
  }
  
  async delete(id: string) {
    // Implementation
  }
}

export const {serviceName}Service = new {ServiceName}Service();'''
        }
    
    def _get_utility_patterns(self) -> Dict[str, str]:
        """Get utility code patterns"""
        return {}
    
    def _get_config_patterns(self) -> Dict[str, str]:
        """Get configuration code patterns"""
        return {}


class GenerationResult:
    """Result of code generation operation"""
    
    def __init__(self, success: bool, data: Dict[str, Any], error: str = ""):
        self.success = success
        self.data = data
        self.error = error


# Framework-specific generators
class ReactGenerator:
    """React-specific code generator"""
    
    async def generate_entry_point(self, context: Dict[str, Any]) -> Dict[str, str]:
        language = context.get('target_language', 'javascript')
        project_name = context.get('project_name', 'MyApp')
        
        if language == 'typescript':
            content = '''import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
'''
            return {'path': 'src/index.tsx', 'content': content}
        else:
            content = '''import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
'''
            return {'path': 'src/index.js', 'content': content}
    
    async def generate_main_app(self, context: Dict[str, Any]) -> Dict[str, str]:
        language = context.get('target_language', 'javascript')
        project_name = context.get('project_name', 'MyApp')
        
        if language == 'typescript':
            content = f'''import React from 'react';
import './App.css';

function App(): JSX.Element {{
  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to {project_name}</h1>
        <p>Your application is ready!</p>
      </header>
    </div>
  );
}}

export default App;
'''
            return {'path': 'src/App.tsx', 'content': content}
        else:
            content = f'''import React from 'react';
import './App.css';

function App() {{
  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to {project_name}</h1>
        <p>Your application is ready!</p>
      </header>
    </div>
  );
}}

export default App;
'''
            return {'path': 'src/App.js', 'content': content}
    
    async def generate_config_files(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        configs = []
        
        # Package.json
        package_json = {
            'name': context.get('project_name', 'my-app'),
            'version': '0.1.0',
            'private': True,
            'dependencies': {
                'react': '^18.2.0',
                'react-dom': '^18.2.0',
                'react-scripts': '5.0.1'
            },
            'scripts': {
                'start': 'react-scripts start',
                'build': 'react-scripts build',
                'test': 'react-scripts test',
                'eject': 'react-scripts eject'
            },
            'eslintConfig': {
                'extends': ['react-app', 'react-app/jest']
            },
            'browserslist': {
                'production': ['>0.2%', 'not dead', 'not op_mini all'],
                'development': ['last 1 chrome version', 'last 1 firefox version', 'last 1 safari version']
            }
        }
        
        configs.append({
            'path': 'package.json',
            'type': 'json',
            'content': package_json
        })
        
        return configs
    
    async def generate_routing(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        # Basic routing setup
        return []
    
    async def generate_state_management(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        # Basic state management setup
        return []


class VueGenerator:
    """Vue-specific code generator"""
    
    async def generate_entry_point(self, context: Dict[str, Any]) -> Dict[str, str]:
        content = '''import { createApp } from 'vue';
import App from './App.vue';
import './style.css';

createApp(App).mount('#app');
'''
        return {'path': 'src/main.js', 'content': content}
    
    async def generate_main_app(self, context: Dict[str, Any]) -> Dict[str, str]:
        project_name = context.get('project_name', 'MyApp')
        
        content = f'''<template>
  <div id="app">
    <header class="app-header">
      <h1>Welcome to {project_name}</h1>
      <p>Your Vue application is ready!</p>
    </header>
  </div>
</template>

<script>
export default {{
  name: 'App',
  data() {{
    return {{
      message: 'Hello Vue!'
    }};
  }}
}};
</script>

<style>
#app {{
  font-family: Avenir, Helvetica, Arial, sans-serif;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}}
</style>
'''
        return {'path': 'src/App.vue', 'content': content}
    
    async def generate_config_files(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        configs = []
        
        # Package.json
        package_json = {
            'name': context.get('project_name', 'my-vue-app'),
            'version': '0.0.0',
            'private': True,
            'scripts': {
                'dev': 'vite',
                'build': 'vite build',
                'preview': 'vite preview'
            },
            'dependencies': {
                'vue': '^3.3.4'
            },
            'devDependencies': {
                '@vitejs/plugin-vue': '^4.2.3',
                'vite': '^4.4.5'
            }
        }
        
        configs.append({
            'path': 'package.json',
            'type': 'json',
            'content': package_json
        })
        
        return configs
    
    async def generate_routing(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        return []
    
    async def generate_state_management(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        return []


# Additional generator classes would be implemented similarly
class AngularGenerator:
    async def generate_entry_point(self, context: Dict[str, Any]) -> Dict[str, str]:
        return {'path': 'src/main.ts', 'content': '// Angular main file'}
    
    async def generate_main_app(self, context: Dict[str, Any]) -> Dict[str, str]:
        return {'path': 'src/app/app.component.ts', 'content': '// Angular app component'}
    
    async def generate_config_files(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        return []
    
    async def generate_routing(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        return []
    
    async def generate_state_management(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        return []


class ExpressGenerator:
    async def generate_entry_point(self, context: Dict[str, Any]) -> Dict[str, str]:
        return {'path': 'src/server.ts', 'content': '// Express server'}
    
    async def generate_main_app(self, context: Dict[str, Any]) -> Dict[str, str]:
        return {'path': 'src/app.ts', 'content': '// Express app'}
    
    async def generate_config_files(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        return []
    
    async def generate_routing(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        return []
    
    async def generate_state_management(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        return []


class FastAPIGenerator:
    async def generate_entry_point(self, context: Dict[str, Any]) -> Dict[str, str]:
        return {'path': 'main.py', 'content': '# FastAPI main file'}
    
    async def generate_main_app(self, context: Dict[str, Any]) -> Dict[str, str]:
        return {'path': 'app/main.py', 'content': '# FastAPI app'}
    
    async def generate_config_files(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        return []
    
    async def generate_routing(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        return []
    
    async def generate_state_management(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        return []


class DjangoGenerator:
    async def generate_entry_point(self, context: Dict[str, Any]) -> Dict[str, str]:
        return {'path': 'manage.py', 'content': '# Django manage file'}
    
    async def generate_main_app(self, context: Dict[str, Any]) -> Dict[str, str]:
        return {'path': 'project/settings.py', 'content': '# Django settings'}
    
    async def generate_config_files(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        return []
    
    async def generate_routing(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        return []
    
    async def generate_state_management(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        return []


class FlaskGenerator:
    async def generate_entry_point(self, context: Dict[str, Any]) -> Dict[str, str]:
        return {'path': 'app.py', 'content': '# Flask app'}
    
    async def generate_main_app(self, context: Dict[str, Any]) -> Dict[str, str]:
        return {'path': 'app/main.py', 'content': '# Flask main'}
    
    async def generate_config_files(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        return []
    
    async def generate_routing(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        return []
    
    async def generate_state_management(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        return []


class SvelteGenerator:
    async def generate_entry_point(self, context: Dict[str, Any]) -> Dict[str, str]:
        return {'path': 'src/main.js', 'content': '// Svelte main'}
    
    async def generate_main_app(self, context: Dict[str, Any]) -> Dict[str, str]:
        return {'path': 'src/App.svelte', 'content': '<!-- Svelte app -->'}
    
    async def generate_config_files(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        return []
    
    async def generate_routing(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        return []
    
    async def generate_state_management(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        return []


class NextJSGenerator:
    async def generate_entry_point(self, context: Dict[str, Any]) -> Dict[str, str]:
        return {'path': 'pages/_app.js', 'content': '// Next.js app'}
    
    async def generate_main_app(self, context: Dict[str, Any]) -> Dict[str, str]:
        return {'path': 'pages/index.js', 'content': '// Next.js index'}
    
    async def generate_config_files(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        return []
    
    async def generate_routing(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        return []
    
    async def generate_state_management(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        return []


class NuxtGenerator:
    async def generate_entry_point(self, context: Dict[str, Any]) -> Dict[str, str]:
        return {'path': 'app.vue', 'content': '<!-- Nuxt app -->'}
    
    async def generate_main_app(self, context: Dict[str, Any]) -> Dict[str, str]:
        return {'path': 'pages/index.vue', 'content': '<!-- Nuxt index -->'}
    
    async def generate_config_files(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        return []
    
    async def generate_routing(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        return []
    
    async def generate_state_management(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        return []


# Code formatters
class JavaScriptFormatter:
    def format_code(self, code: str) -> str:
        # Basic JavaScript formatting
        return code

class TypeScriptFormatter:
    def format_code(self, code: str) -> str:
        # Basic TypeScript formatting
        return code

class PythonFormatter:
    def format_code(self, code: str) -> str:
        # Basic Python formatting
        return code

class JavaFormatter:
    def format_code(self, code: str) -> str:
        # Basic Java formatting
        return code

class GoFormatter:
    def format_code(self, code: str) -> str:
        # Basic Go formatting
        return code
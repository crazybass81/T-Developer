# backend/src/agents/implementations/generation_agent.py
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import json
from agno.agent import Agent
from agno.models.aws import AwsBedrock
from agno.models.openai import OpenAIChat
from agno.tools import CodeAnalyzer, FileHandler

@dataclass
class GenerationRequest:
    component_type: str
    requirements: List[str]
    framework: str
    language: str
    dependencies: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GeneratedCode:
    id: str
    component_name: str
    language: str
    framework: str
    source_code: str
    test_code: str
    documentation: str
    dependencies: List[str]
    file_structure: Dict[str, str]
    quality_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)

class CodeTemplate:
    def __init__(self, name: str, language: str, framework: str):
        self.name = name
        self.language = language
        self.framework = framework
        self.template_code = ""
        self.placeholders = {}
        self.dependencies = []

class GenerationAgent:
    """AI-powered code generation agent"""

    def __init__(self):
        # Primary code generator - Claude 3 Opus (best for code)
        self.code_generator = Agent(
            name="Code-Generator",
            model=AwsBedrock(
                id="anthropic.claude-3-opus-v1:0",
                region="us-east-1"
            ),
            role="Expert software engineer and code architect",
            instructions=[
                "Generate high-quality, production-ready code",
                "Follow best practices and design patterns",
                "Include comprehensive error handling",
                "Write clean, maintainable, and well-documented code",
                "Ensure code is secure and performant",
                "Generate appropriate tests for all code"
            ],
            temperature=0.1,  # Low temperature for consistent code
            max_retries=3
        )

        # Test generator - GPT-4 (good for test patterns)
        self.test_generator = Agent(
            name="Test-Generator",
            model=OpenAIChat(id="gpt-4-turbo-preview"),
            role="Senior QA engineer and test architect",
            instructions=[
                "Generate comprehensive test suites",
                "Include unit, integration, and edge case tests",
                "Follow testing best practices",
                "Ensure high code coverage",
                "Write clear test descriptions"
            ],
            temperature=0.2
        )

        # Documentation generator
        self.doc_generator = Agent(
            name="Doc-Generator",
            model=AwsBedrock(id="amazon.nova-pro-v1:0"),
            role="Technical writer and documentation specialist",
            instructions=[
                "Generate clear, comprehensive documentation",
                "Include API documentation and usage examples",
                "Write user-friendly guides",
                "Document all public interfaces"
            ],
            temperature=0.3
        )

        # Code quality analyzer
        self.quality_analyzer = CodeQualityAnalyzer()
        
        # Template manager
        self.template_manager = TemplateManager()
        
        # Code optimizer
        self.code_optimizer = CodeOptimizer()

    async def generate_component(
        self,
        request: GenerationRequest
    ) -> GeneratedCode:
        """Generate a complete component with code, tests, and documentation"""

        # 1. Analyze requirements and select template
        template = await self._select_template(request)
        
        # 2. Generate code in parallel
        generation_tasks = [
            self._generate_source_code(request, template),
            self._generate_test_code(request),
            self._generate_documentation(request)
        ]
        
        source_code, test_code, documentation = await asyncio.gather(*generation_tasks)
        
        # 3. Optimize generated code
        optimized_code = await self.code_optimizer.optimize(
            source_code,
            request.language,
            request.framework
        )
        
        # 4. Analyze quality
        quality_score = await self.quality_analyzer.analyze(
            optimized_code,
            test_code
        )
        
        # 5. Generate file structure
        file_structure = self._generate_file_structure(
            request,
            optimized_code,
            test_code
        )
        
        return GeneratedCode(
            id=self._generate_id(),
            component_name=request.component_type,
            language=request.language,
            framework=request.framework,
            source_code=optimized_code,
            test_code=test_code,
            documentation=documentation,
            dependencies=self._extract_dependencies(optimized_code, request.framework),
            file_structure=file_structure,
            quality_score=quality_score,
            metadata={
                'template_used': template.name if template else 'custom',
                'generation_time': asyncio.get_event_loop().time(),
                'requirements_count': len(request.requirements)
            }
        )

    async def _generate_source_code(
        self,
        request: GenerationRequest,
        template: Optional[CodeTemplate]
    ) -> str:
        """Generate source code"""

        context = self._build_generation_context(request, template)
        
        prompt = f"""
Generate {request.language} code for a {request.component_type} component using {request.framework}.

Requirements:
{chr(10).join(f"- {req}" for req in request.requirements)}

Framework: {request.framework}
Language: {request.language}

Constraints:
{json.dumps(request.constraints, indent=2)}

Context:
{json.dumps(context, indent=2)}

Generate production-ready code with:
1. Proper error handling
2. Input validation
3. Security best practices
4. Performance optimization
5. Clear documentation
6. Modular design

Return only the code without explanations.
"""

        result = await self.code_generator.arun(prompt)
        return self._clean_generated_code(result.content)

    async def _generate_test_code(self, request: GenerationRequest) -> str:
        """Generate comprehensive test code"""

        prompt = f"""
Generate comprehensive test suite for a {request.component_type} in {request.language}.

Requirements to test:
{chr(10).join(f"- {req}" for req in request.requirements)}

Framework: {request.framework}
Testing Framework: {self._get_test_framework(request.language, request.framework)}

Include:
1. Unit tests for all functions/methods
2. Integration tests for component interactions
3. Edge case tests
4. Error handling tests
5. Performance tests (if applicable)
6. Mock external dependencies

Generate tests with clear descriptions and good coverage.
"""

        result = await self.test_generator.arun(prompt)
        return self._clean_generated_code(result.content)

    async def _generate_documentation(self, request: GenerationRequest) -> str:
        """Generate component documentation"""

        prompt = f"""
Generate comprehensive documentation for a {request.component_type} component.

Component Details:
- Type: {request.component_type}
- Language: {request.language}
- Framework: {request.framework}

Requirements:
{chr(10).join(f"- {req}" for req in request.requirements)}

Include:
1. Component overview and purpose
2. Installation instructions
3. API documentation
4. Usage examples
5. Configuration options
6. Troubleshooting guide

Format as Markdown.
"""

        result = await self.doc_generator.arun(prompt)
        return result.content

    def _build_generation_context(
        self,
        request: GenerationRequest,
        template: Optional[CodeTemplate]
    ) -> Dict[str, Any]:
        """Build context for code generation"""

        context = {
            'project_type': request.context.get('project_type', 'web_application'),
            'architecture_pattern': request.context.get('architecture', 'mvc'),
            'database_type': request.context.get('database', 'postgresql'),
            'authentication': request.context.get('auth', 'jwt'),
            'deployment_target': request.context.get('deployment', 'cloud')
        }

        if template:
            context['template'] = {
                'name': template.name,
                'placeholders': template.placeholders,
                'base_dependencies': template.dependencies
            }

        return context

    async def _select_template(self, request: GenerationRequest) -> Optional[CodeTemplate]:
        """Select appropriate code template"""

        template_key = f"{request.language}_{request.framework}_{request.component_type}"
        
        # Check for exact match
        if template_key in self.template_manager.templates:
            return self.template_manager.templates[template_key]
        
        # Find similar template
        similar_templates = self.template_manager.find_similar(
            request.language,
            request.framework,
            request.component_type
        )
        
        if similar_templates:
            return similar_templates[0]
        
        return None

    def _generate_file_structure(
        self,
        request: GenerationRequest,
        source_code: str,
        test_code: str
    ) -> Dict[str, str]:
        """Generate appropriate file structure"""

        structure = {}
        
        # Main source file
        main_file = self._get_main_filename(request)
        structure[main_file] = source_code
        
        # Test file
        test_file = self._get_test_filename(request)
        structure[test_file] = test_code
        
        # Additional files based on framework
        additional_files = self._get_additional_files(request)
        structure.update(additional_files)
        
        return structure

    def _get_main_filename(self, request: GenerationRequest) -> str:
        """Get main source filename"""
        
        extensions = {
            'python': '.py',
            'javascript': '.js',
            'typescript': '.ts',
            'java': '.java',
            'go': '.go',
            'rust': '.rs'
        }
        
        ext = extensions.get(request.language.lower(), '.txt')
        component_name = request.component_type.lower().replace(' ', '_')
        
        return f"src/{component_name}{ext}"

    def _get_test_filename(self, request: GenerationRequest) -> str:
        """Get test filename"""
        
        test_patterns = {
            'python': 'test_{}.py',
            'javascript': '{}.test.js',
            'typescript': '{}.test.ts',
            'java': '{}Test.java',
            'go': '{}_test.go',
            'rust': '{}_test.rs'
        }
        
        pattern = test_patterns.get(request.language.lower(), 'test_{}.txt')
        component_name = request.component_type.lower().replace(' ', '_')
        
        return f"tests/{pattern.format(component_name)}"

    def _get_additional_files(self, request: GenerationRequest) -> Dict[str, str]:
        """Generate additional framework-specific files"""
        
        files = {}
        
        # Package/dependency files
        if request.language == 'python':
            files['requirements.txt'] = self._generate_python_requirements(request)
            files['setup.py'] = self._generate_python_setup(request)
        elif request.language in ['javascript', 'typescript']:
            files['package.json'] = self._generate_package_json(request)
        elif request.language == 'java':
            files['pom.xml'] = self._generate_maven_pom(request)
        
        # Configuration files
        if request.framework == 'react':
            files['.eslintrc.js'] = self._generate_eslint_config()
        elif request.framework == 'vue':
            files['vue.config.js'] = self._generate_vue_config()
        elif request.framework == 'django':
            files['settings.py'] = self._generate_django_settings()
        
        return files

    def _extract_dependencies(self, code: str, framework: str) -> List[str]:
        """Extract dependencies from generated code"""
        
        dependencies = []
        
        # Language-specific import patterns
        import_patterns = {
            'python': [r'import\s+(\w+)', r'from\s+(\w+)\s+import'],
            'javascript': [r'import.*from\s+[\'"]([^\'"]+)[\'"]', r'require\([\'"]([^\'"]+)[\'"]\)'],
            'java': [r'import\s+([\w\.]+)'],
            'go': [r'import\s+"([^"]+)"']
        }
        
        # Extract based on patterns
        # Implementation would use regex to find imports
        
        # Add framework-specific dependencies
        framework_deps = self._get_framework_dependencies(framework)
        dependencies.extend(framework_deps)
        
        return list(set(dependencies))

    def _get_framework_dependencies(self, framework: str) -> List[str]:
        """Get standard dependencies for framework"""
        
        deps = {
            'react': ['react', 'react-dom'],
            'vue': ['vue'],
            'angular': ['@angular/core', '@angular/common'],
            'django': ['django'],
            'flask': ['flask'],
            'express': ['express'],
            'spring': ['org.springframework:spring-core']
        }
        
        return deps.get(framework.lower(), [])

    def _clean_generated_code(self, code: str) -> str:
        """Clean and format generated code"""
        
        # Remove markdown code blocks
        if code.startswith('```'):
            lines = code.split('\n')
            if len(lines) > 2:
                code = '\n'.join(lines[1:-1])
        
        # Remove extra whitespace
        code = code.strip()
        
        return code

    def _generate_id(self) -> str:
        """Generate unique ID for generated code"""
        import uuid
        return f"gen_{uuid.uuid4().hex[:8]}"

    def _get_test_framework(self, language: str, framework: str) -> str:
        """Get appropriate test framework"""
        
        test_frameworks = {
            'python': 'pytest',
            'javascript': 'jest',
            'typescript': 'jest',
            'java': 'junit',
            'go': 'testing',
            'rust': 'cargo test'
        }
        
        return test_frameworks.get(language.lower(), 'unittest')

class CodeQualityAnalyzer:
    """Analyzes code quality and provides scores"""

    async def analyze(self, source_code: str, test_code: str) -> float:
        """Analyze code quality and return score (0-1)"""
        
        scores = []
        
        # Code complexity
        complexity_score = self._analyze_complexity(source_code)
        scores.append(complexity_score * 0.3)
        
        # Test coverage estimation
        coverage_score = self._estimate_coverage(source_code, test_code)
        scores.append(coverage_score * 0.3)
        
        # Code style
        style_score = self._analyze_style(source_code)
        scores.append(style_score * 0.2)
        
        # Security patterns
        security_score = self._analyze_security(source_code)
        scores.append(security_score * 0.2)
        
        return sum(scores)

    def _analyze_complexity(self, code: str) -> float:
        """Analyze code complexity"""
        # Simplified complexity analysis
        lines = code.split('\n')
        non_empty_lines = [l for l in lines if l.strip()]
        
        # Basic complexity indicators
        complexity_keywords = ['if', 'for', 'while', 'try', 'except', 'switch', 'case']
        complexity_count = sum(
            line.count(keyword) for line in non_empty_lines 
            for keyword in complexity_keywords
        )
        
        # Normalize score (lower complexity = higher score)
        if len(non_empty_lines) == 0:
            return 1.0
        
        complexity_ratio = complexity_count / len(non_empty_lines)
        return max(0.0, 1.0 - complexity_ratio)

    def _estimate_coverage(self, source_code: str, test_code: str) -> float:
        """Estimate test coverage"""
        if not test_code.strip():
            return 0.0
        
        # Simple heuristic: ratio of test lines to source lines
        source_lines = len([l for l in source_code.split('\n') if l.strip()])
        test_lines = len([l for l in test_code.split('\n') if l.strip()])
        
        if source_lines == 0:
            return 1.0
        
        coverage_ratio = test_lines / source_lines
        return min(1.0, coverage_ratio)

    def _analyze_style(self, code: str) -> float:
        """Analyze code style"""
        # Basic style checks
        lines = code.split('\n')
        
        # Check for comments
        comment_lines = sum(1 for line in lines if line.strip().startswith('#') or line.strip().startswith('//'))
        comment_ratio = comment_lines / max(1, len(lines))
        
        # Check for proper naming (simplified)
        has_proper_naming = any(
            word.islower() or word.isupper() or '_' in word
            for line in lines
            for word in line.split()
            if word.isalpha()
        )
        
        style_score = (comment_ratio * 0.5) + (0.5 if has_proper_naming else 0.0)
        return min(1.0, style_score)

    def _analyze_security(self, code: str) -> float:
        """Analyze security patterns"""
        # Check for security anti-patterns
        security_issues = [
            'eval(',
            'exec(',
            'system(',
            'shell_exec(',
            'password',  # hardcoded passwords
            'secret',    # hardcoded secrets
        ]
        
        code_lower = code.lower()
        issue_count = sum(1 for issue in security_issues if issue in code_lower)
        
        # Security patterns (good)
        security_patterns = [
            'validate',
            'sanitize',
            'escape',
            'hash',
            'encrypt'
        ]
        
        pattern_count = sum(1 for pattern in security_patterns if pattern in code_lower)
        
        # Calculate score
        if issue_count > 0:
            return max(0.0, 0.5 - (issue_count * 0.1))
        
        return min(1.0, 0.7 + (pattern_count * 0.1))

class TemplateManager:
    """Manages code templates"""

    def __init__(self):
        self.templates = {}
        self._load_default_templates()

    def _load_default_templates(self):
        """Load default code templates"""
        
        # React component template
        react_component = CodeTemplate(
            name="react_functional_component",
            language="javascript",
            framework="react"
        )
        react_component.template_code = """
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

const {{COMPONENT_NAME}} = ({ {{PROPS}} }) => {
  {{STATE_DECLARATIONS}}
  
  {{USE_EFFECT_HOOKS}}
  
  {{EVENT_HANDLERS}}
  
  return (
    <div className="{{CSS_CLASS}}">
      {{COMPONENT_CONTENT}}
    </div>
  );
};

{{COMPONENT_NAME}}.propTypes = {
  {{PROP_TYPES}}
};

{{COMPONENT_NAME}}.defaultProps = {
  {{DEFAULT_PROPS}}
};

export default {{COMPONENT_NAME}};
"""
        react_component.placeholders = {
            'COMPONENT_NAME': 'string',
            'PROPS': 'string',
            'STATE_DECLARATIONS': 'code',
            'USE_EFFECT_HOOKS': 'code',
            'EVENT_HANDLERS': 'code',
            'CSS_CLASS': 'string',
            'COMPONENT_CONTENT': 'jsx',
            'PROP_TYPES': 'object',
            'DEFAULT_PROPS': 'object'
        }
        react_component.dependencies = ['react', 'prop-types']
        
        self.templates['javascript_react_component'] = react_component

    def find_similar(self, language: str, framework: str, component_type: str) -> List[CodeTemplate]:
        """Find similar templates"""
        
        similar = []
        
        for template in self.templates.values():
            score = 0
            
            if template.language == language:
                score += 3
            if template.framework == framework:
                score += 2
            if component_type.lower() in template.name.lower():
                score += 1
            
            if score > 0:
                similar.append((template, score))
        
        # Sort by score and return templates
        similar.sort(key=lambda x: x[1], reverse=True)
        return [template for template, _ in similar]

class CodeOptimizer:
    """Optimizes generated code"""

    async def optimize(self, code: str, language: str, framework: str) -> str:
        """Optimize code for performance and best practices"""
        
        optimizations = []
        
        # Language-specific optimizations
        if language == 'python':
            optimizations.extend(self._python_optimizations(code))
        elif language in ['javascript', 'typescript']:
            optimizations.extend(self._javascript_optimizations(code))
        elif language == 'java':
            optimizations.extend(self._java_optimizations(code))
        
        # Framework-specific optimizations
        if framework == 'react':
            optimizations.extend(self._react_optimizations(code))
        elif framework == 'vue':
            optimizations.extend(self._vue_optimizations(code))
        
        # Apply optimizations
        optimized_code = code
        for optimization in optimizations:
            optimized_code = optimization(optimized_code)
        
        return optimized_code

    def _python_optimizations(self, code: str) -> List[callable]:
        """Python-specific optimizations"""
        
        def add_type_hints(code: str) -> str:
            # Add basic type hints where missing
            return code
        
        def optimize_imports(code: str) -> str:
            # Organize and optimize imports
            return code
        
        return [add_type_hints, optimize_imports]

    def _javascript_optimizations(self, code: str) -> List[callable]:
        """JavaScript-specific optimizations"""
        
        def add_strict_mode(code: str) -> str:
            if "'use strict';" not in code:
                return "'use strict';\n\n" + code
            return code
        
        def optimize_async_await(code: str) -> str:
            # Optimize async/await patterns
            return code
        
        return [add_strict_mode, optimize_async_await]

    def _react_optimizations(self, code: str) -> List[callable]:
        """React-specific optimizations"""
        
        def add_memo_optimization(code: str) -> str:
            # Add React.memo where appropriate
            return code
        
        def optimize_useeffect(code: str) -> str:
            # Optimize useEffect dependencies
            return code
        
        return [add_memo_optimization, optimize_useeffect]

    def _java_optimizations(self, code: str) -> List[callable]:
        """Java-specific optimizations"""
        return []

    def _vue_optimizations(self, code: str) -> List[callable]:
        """Vue-specific optimizations"""
        return []
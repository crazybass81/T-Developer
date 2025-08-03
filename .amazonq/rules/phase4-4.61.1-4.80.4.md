# Phase 4: 9개 핵심 에이전트 구현 - Generation Agent & Assembly Agent

## 7. Generation Agent (코드 생성 에이전트) - Tasks 4.61-4.70

### Task 4.61: 컴포넌트 기반 코드 생성

#### SubTask 4.61.1: 코드 생성 엔진 구현

**담당자**: 시니어 백엔드 개발자  
**예상 소요시간**: 16시간

**작업 내용**:

```python
# backend/src/agents/implementations/generation/code_generation_engine.py
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import ast
import jinja2
from abc import ABC, abstractmethod

@dataclass
class CodeGenerationRequest:
    component_id: str
    component_type: str
    framework: str
    language: str
    requirements: Dict[str, Any]
    templates: List[str]
    customization: Dict[str, Any]
    dependencies: List[str]

@dataclass
class GeneratedCode:
    file_name: str
    file_path: str
    content: str
    language: str
    dependencies: List[str]
    imports: List[str]
    exports: List[str]
    tests: Optional[str] = None
    documentation: Optional[str] = None

class CodeGenerationEngine:
    """코드 생성 엔진"""

    def __init__(self):
        self.template_engine = TemplateEngine()
        self.code_builder = CodeBuilder()
        self.dependency_resolver = DependencyResolver()
        self.code_formatter = CodeFormatter()
        self.validation_engine = CodeValidationEngine()

    async def generate_code(
        self,
        request: CodeGenerationRequest
    ) -> List[GeneratedCode]:
        """컴포넌트 기반 코드 생성"""

        generated_files = []

        # 1. 템플릿 로드
        templates = await self.template_engine.load_templates(
            request.framework,
            request.component_type,
            request.templates
        )

        # 2. 컨텍스트 준비
        context = await self._prepare_generation_context(request)

        # 3. 코드 생성
        for template in templates:
            # 템플릿 렌더링
            raw_code = await self.template_engine.render(
                template,
                context
            )

            # 코드 빌드 및 최적화
            built_code = await self.code_builder.build(
                raw_code,
                request.language,
                request.framework
            )

            # 의존성 해결
            resolved_code = await self.dependency_resolver.resolve(
                built_code,
                request.dependencies
            )

            # 포맷팅
            formatted_code = await self.code_formatter.format(
                resolved_code,
                request.language
            )

            # 검증
            validation_result = await self.validation_engine.validate(
                formatted_code,
                request.language
            )

            if validation_result.is_valid:
                generated_file = GeneratedCode(
                    file_name=self._generate_file_name(template, request),
                    file_path=self._generate_file_path(template, request),
                    content=formatted_code,
                    language=request.language,
                    dependencies=validation_result.dependencies,
                    imports=validation_result.imports,
                    exports=validation_result.exports
                )

                # 테스트 코드 생성
                if request.requirements.get('generate_tests', True):
                    generated_file.tests = await self._generate_tests(
                        generated_file,
                        request
                    )

                # 문서 생성
                if request.requirements.get('generate_docs', True):
                    generated_file.documentation = await self._generate_documentation(
                        generated_file,
                        request
                    )

                generated_files.append(generated_file)

        return generated_files

    async def _prepare_generation_context(
        self,
        request: CodeGenerationRequest
    ) -> Dict[str, Any]:
        """생성 컨텍스트 준비"""

        context = {
            'component_name': request.requirements.get('name'),
            'component_type': request.component_type,
            'framework': request.framework,
            'props': request.requirements.get('props', {}),
            'state': request.requirements.get('state', {}),
            'methods': request.requirements.get('methods', []),
            'events': request.requirements.get('events', []),
            'styles': request.customization.get('styles', {}),
            'config': request.customization.get('config', {}),
            'utils': self._generate_utility_functions(request),
            'helpers': self._generate_helper_functions(request)
        }

        # 프레임워크별 특수 컨텍스트
        framework_context = await self._get_framework_context(
            request.framework,
            request
        )
        context.update(framework_context)

        return context

    def _generate_file_name(
        self,
        template: Template,
        request: CodeGenerationRequest
    ) -> str:
        """파일명 생성"""

        naming_convention = self._get_naming_convention(
            request.framework,
            request.language
        )

        base_name = request.requirements.get('name', 'Component')

        if request.language == 'typescript':
            if template.type == 'component':
                return f"{base_name}.tsx"
            elif template.type == 'style':
                return f"{base_name}.module.css"
            elif template.type == 'test':
                return f"{base_name}.test.tsx"
        elif request.language == 'python':
            if template.type == 'component':
                return f"{self._to_snake_case(base_name)}.py"
            elif template.type == 'test':
                return f"test_{self._to_snake_case(base_name)}.py"

        return f"{base_name}.{self._get_file_extension(request.language)}"

class TemplateEngine:
    """템플릿 엔진"""

    def __init__(self):
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader('templates'),
            enable_async=True
        )
        self.custom_filters = self._register_custom_filters()
        self.template_cache = {}

    async def render(
        self,
        template: Template,
        context: Dict[str, Any]
    ) -> str:
        """템플릿 렌더링"""

        # 캐시 확인
        cache_key = f"{template.id}:{hash(frozenset(context.items()))}"
        if cache_key in self.template_cache:
            return self.template_cache[cache_key]

        # Jinja2 템플릿 로드
        jinja_template = self.jinja_env.get_template(template.path)

        # 렌더링
        rendered = await jinja_template.render_async(**context)

        # 후처리
        processed = await self._post_process(rendered, template.type)

        # 캐시 저장
        self.template_cache[cache_key] = processed

        return processed

    def _register_custom_filters(self):
        """커스텀 필터 등록"""

        filters = {
            'camelCase': self._to_camel_case,
            'PascalCase': self._to_pascal_case,
            'snake_case': self._to_snake_case,
            'kebab-case': self._to_kebab_case,
            'pluralize': self._pluralize,
            'singularize': self._singularize
        }

        for name, func in filters.items():
            self.jinja_env.filters[name] = func

        return filters
```

**검증 기준**:

- [ ] 다양한 프레임워크 지원
- [ ] 코드 품질 검증
- [ ] 의존성 자동 해결
- [ ] 템플릿 캐싱 구현

#### SubTask 4.61.2: 템플릿 시스템 구축

**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 14시간

**작업 내용**:

```typescript
// backend/src/agents/implementations/generation/template_system.ts
interface TemplateMetadata {
  id: string;
  name: string;
  type: TemplateType;
  framework: string;
  language: string;
  version: string;
  variables: TemplateVariable[];
  blocks: TemplateBlock[];
  dependencies: string[];
}

interface TemplateVariable {
  name: string;
  type: string;
  required: boolean;
  default?: any;
  validation?: (value: any) => boolean;
}

interface TemplateBlock {
  name: string;
  type: 'conditional' | 'loop' | 'include';
  condition?: string;
  content: string;
}

class TemplateSystem {
  private templates: Map<string, TemplateMetadata> = new Map();
  private parser: TemplateParser;
  private validator: TemplateValidator;
  private optimizer: TemplateOptimizer;

  constructor() {
    this.parser = new TemplateParser();
    this.validator = new TemplateValidator();
    this.optimizer = new TemplateOptimizer();
  }

  async loadTemplate(path: string): Promise<TemplateMetadata> {
    const content = await this.readTemplateFile(path);
    const parsed = await this.parser.parse(content);
    const validated = await this.validator.validate(parsed);
    const optimized = await this.optimizer.optimize(validated);

    this.templates.set(optimized.id, optimized);
    return optimized;
  }

  async renderTemplate(templateId: string, context: Record<string, any>): Promise<string> {
    const template = this.templates.get(templateId);
    if (!template) {
      throw new Error(`Template ${templateId} not found`);
    }

    // 변수 검증
    this.validateVariables(template, context);

    // 블록 처리
    let rendered = template.content;
    for (const block of template.blocks) {
      rendered = await this.processBlock(block, context, rendered);
    }

    // 변수 치환
    rendered = this.substituteVariables(rendered, context);

    // 최종 최적화
    return this.optimizer.optimizeOutput(rendered);
  }

  private validateVariables(template: TemplateMetadata, context: Record<string, any>): void {
    for (const variable of template.variables) {
      if (variable.required && !(variable.name in context)) {
        throw new Error(`Required variable '${variable.name}' not provided`);
      }

      if (variable.validation && variable.name in context) {
        if (!variable.validation(context[variable.name])) {
          throw new Error(`Invalid value for variable '${variable.name}'`);
        }
      }
    }
  }

  private async processBlock(
    block: TemplateBlock,
    context: Record<string, any>,
    content: string,
  ): Promise<string> {
    switch (block.type) {
      case 'conditional':
        return this.processConditionalBlock(block, context, content);
      case 'loop':
        return this.processLoopBlock(block, context, content);
      case 'include':
        return this.processIncludeBlock(block, context, content);
      default:
        return content;
    }
  }
}

// React 컴포넌트 템플릿 예시
const reactComponentTemplate = `
import React{{#if hasState}}, { useState{{#if hasEffects}}, useEffect{{/if}} }{{/if}} from 'react';
{{#each imports}}
import {{this.name}} from '{{this.path}}';
{{/each}}
{{#if hasStyles}}
import styles from './{{componentName}}.module.css';
{{/if}}

{{#if hasTypes}}
interface {{componentName}}Props {
  {{#each props}}
  {{this.name}}{{#unless this.required}}?{{/unless}}: {{this.type}};
  {{/each}}
}
{{/if}}

{{#if exportType === 'default'}}export default {{/if}}{{#if exportType === 'named'}}export {{/if}}const {{componentName}}{{#if hasTypes}}: React.FC<{{componentName}}Props>{{/if}} = ({{#if hasProps}}{ {{#each props}}{{this.name}}{{#unless @last}}, {{/unless}}{{/each}} }{{/if}}) => {
  {{#if hasState}}
  {{#each state}}
  const [{{this.name}}, set{{this.name | capitalize}}] = useState{{#if this.type}}<{{this.type}}>{{/if}}({{this.defaultValue}});
  {{/each}}
  {{/if}}

  {{#if hasEffects}}
  {{#each effects}}
  useEffect(() => {
    {{this.body}}
  }, [{{#each this.dependencies}}{{this}}{{#unless @last}}, {{/unless}}{{/each}}]);
  {{/each}}
  {{/if}}

  {{#each methods}}
  const {{this.name}} = {{this.async ? 'async ' : ''}}({{#each this.params}}{{this}}{{#unless @last}}, {{/unless}}{{/each}}) => {
    {{this.body}}
  };
  {{/each}}

  return (
    {{jsx}}
  );
};
{{#if exportType === 'none'}}

export { {{componentName}} };
{{/if}}
`;
```

**검증 기준**:

- [ ] 유연한 템플릿 시스템
- [ ] 다양한 프레임워크 템플릿
- [ ] 조건부/반복 블록 지원
- [ ] 템플릿 검증 기능

#### SubTask 4.61.3: 프레임워크별 생성기

**담당자**: 풀스택 개발자  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/generation/framework_generators.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class FrameworkGenerator(ABC):
    """프레임워크별 코드 생성기 기본 클래스"""

    @abstractmethod
    async def generate_component(
        self,
        spec: ComponentSpec
    ) -> GeneratedCode:
        pass

    @abstractmethod
    async def generate_service(
        self,
        spec: ServiceSpec
    ) -> GeneratedCode:
        pass

    @abstractmethod
    async def generate_config(
        self,
        spec: ConfigSpec
    ) -> GeneratedCode:
        pass

class ReactGenerator(FrameworkGenerator):
    """React 코드 생성기"""

    async def generate_component(
        self,
        spec: ComponentSpec
    ) -> GeneratedCode:
        """React 컴포넌트 생성"""

        # 컴포넌트 타입 결정
        component_type = self._determine_component_type(spec)

        if component_type == 'functional':
            return await self._generate_functional_component(spec)
        elif component_type == 'class':
            return await self._generate_class_component(spec)
        elif component_type == 'server':
            return await self._generate_server_component(spec)

    async def _generate_functional_component(
        self,
        spec: ComponentSpec
    ) -> GeneratedCode:
        """함수형 컴포넌트 생성"""

        code_parts = []

        # Imports
        imports = self._generate_imports(spec)
        code_parts.append(imports)

        # Type definitions
        if spec.props:
            types = self._generate_prop_types(spec.props)
            code_parts.append(types)

        # Component
        component = f"""
const {spec.name}: React.FC<{spec.name}Props> = ({
    ', '.join(prop.name for prop in spec.props)
}) => {{
    {self._generate_state_hooks(spec.state)}
    {self._generate_effect_hooks(spec.effects)}
    {self._generate_methods(spec.methods)}

    return (
        {self._generate_jsx(spec.template)}
    );
}};
"""
        code_parts.append(component)

        # Export
        code_parts.append(f"export default {spec.name};")

        return GeneratedCode(
            file_name=f"{spec.name}.tsx",
            file_path=f"src/components/{spec.name}",
            content='\n\n'.join(code_parts),
            language='typescript',
            dependencies=self._extract_dependencies(spec),
            imports=self._extract_imports(imports),
            exports=[spec.name]
        )

class VueGenerator(FrameworkGenerator):
    """Vue 코드 생성기"""

    async def generate_component(
        self,
        spec: ComponentSpec
    ) -> GeneratedCode:
        """Vue 컴포넌트 생성"""

        # Vue 3 Composition API 사용
        template = self._generate_template(spec)
        script = self._generate_script(spec)
        style = self._generate_style(spec)

        content = f"""
<template>
{template}
</template>

<script setup lang="ts">
{script}
</script>

{f'<style scoped>{style}</style>' if style else ''}
"""

        return GeneratedCode(
            file_name=f"{spec.name}.vue",
            file_path=f"src/components/{spec.name}",
            content=content,
            language='vue',
            dependencies=self._extract_dependencies(spec),
            imports=[],
            exports=[spec.name]
        )

class NextJSGenerator(FrameworkGenerator):
    """Next.js 코드 생성기"""

    async def generate_component(
        self,
        spec: ComponentSpec
    ) -> GeneratedCode:
        """Next.js 컴포넌트 생성"""

        # App Router 사용 여부 확인
        if spec.config.get('use_app_router', True):
            return await self._generate_app_router_component(spec)
        else:
            return await self._generate_pages_router_component(spec)

    async def _generate_app_router_component(
        self,
        spec: ComponentSpec
    ) -> GeneratedCode:
        """App Router 컴포넌트 생성"""

        is_server = spec.config.get('server_component', True)

        code = f"""
{'use client' if not is_server else ''}

import type {{ Metadata }} from 'next'
{self._generate_imports(spec)}

{self._generate_metadata(spec) if spec.page else ''}

{f'interface {spec.name}Props {{ {self._generate_prop_interface(spec.props)} }}' if spec.props else ''}

export default {'async ' if is_server else ''}function {spec.name}({{
    {', '.join(prop.name for prop in spec.props)}
}}: {spec.name}Props) {{
    {await self._generate_server_logic(spec) if is_server else ''}
    {self._generate_client_logic(spec) if not is_server else ''}

    return (
        {self._generate_jsx(spec.template)}
    )
}}
"""

        return GeneratedCode(
            file_name=f"{spec.name}.tsx",
            file_path=self._determine_app_path(spec),
            content=code,
            language='typescript',
            dependencies=self._extract_dependencies(spec),
            imports=self._extract_imports(code),
            exports=[spec.name]
        )

# 프레임워크 생성기 팩토리
class FrameworkGeneratorFactory:
    """프레임워크 생성기 팩토리"""

    _generators = {
        'react': ReactGenerator,
        'vue': VueGenerator,
        'nextjs': NextJSGenerator,
        'angular': AngularGenerator,
        'svelte': SvelteGenerator,
        'express': ExpressGenerator,
        'fastapi': FastAPIGenerator,
        'django': DjangoGenerator,
        'nestjs': NestJSGenerator,
        'spring': SpringBootGenerator
    }

    @classmethod
    def create(cls, framework: str) -> FrameworkGenerator:
        """프레임워크별 생성기 생성"""

        generator_class = cls._generators.get(framework.lower())
        if not generator_class:
            raise ValueError(f"Unsupported framework: {framework}")

        return generator_class()
```

**검증 기준**:

- [ ] 주요 프레임워크 지원
- [ ] 프레임워크 특성 반영
- [ ] 최신 버전 지원
- [ ] 확장 가능한 구조

#### SubTask 4.61.4: 코드 검증 시스템

**담당자**: QA 엔지니어  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/generation/code_validation.py
from typing import List, Dict, Any, Optional, Tuple
import ast
import re
from dataclasses import dataclass

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationWarning]
    dependencies: List[str]
    imports: List[str]
    exports: List[str]
    metrics: CodeMetrics

@dataclass
class ValidationError:
    line: int
    column: int
    message: str
    rule: str
    severity: str = 'error'

@dataclass
class CodeMetrics:
    lines_of_code: int
    cyclomatic_complexity: int
    maintainability_index: float
    test_coverage: float
    documentation_coverage: float

class CodeValidationEngine:
    """코드 검증 엔진"""

    def __init__(self):
        self.syntax_validator = SyntaxValidator()
        self.semantic_validator = SemanticValidator()
        self.style_validator = StyleValidator()
        self.security_validator = SecurityValidator()
        self.performance_validator = PerformanceValidator()
        self.metrics_calculator = MetricsCalculator()

    async def validate(
        self,
        code: str,
        language: str,
        config: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """코드 검증"""

        errors = []
        warnings = []

        # 1. 구문 검증
        syntax_result = await self.syntax_validator.validate(code, language)
        if not syntax_result.is_valid:
            errors.extend(syntax_result.errors)
            return ValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                dependencies=[],
                imports=[],
                exports=[],
                metrics=CodeMetrics(0, 0, 0.0, 0.0, 0.0)
            )

        # 2. 의미 검증
        semantic_result = await self.semantic_validator.validate(
            code,
            language,
            syntax_result.ast
        )
        errors.extend(semantic_result.errors)
        warnings.extend(semantic_result.warnings)

        # 3. 스타일 검증
        style_result = await self.style_validator.validate(
            code,
            language,
            config.get('style_rules', {})
        )
        warnings.extend(style_result.warnings)

        # 4. 보안 검증
        security_result = await self.security_validator.validate(
            code,
            language
        )
        errors.extend(security_result.errors)
        warnings.extend(security_result.warnings)

        # 5. 성능 검증
        performance_result = await self.performance_validator.validate(
            code,
            language
        )
        warnings.extend(performance_result.warnings)

        # 6. 메트릭 계산
        metrics = await self.metrics_calculator.calculate(
            code,
            language,
            syntax_result.ast
        )

        # 7. 의존성 추출
        dependencies = self._extract_dependencies(code, language)
        imports = self._extract_imports(code, language)
        exports = self._extract_exports(code, language)

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            dependencies=dependencies,
            imports=imports,
            exports=exports,
            metrics=metrics
        )

    def _extract_dependencies(
        self,
        code: str,
        language: str
    ) -> List[str]:
        """의존성 추출"""

        dependencies = []

        if language in ['javascript', 'typescript']:
            # import 문 파싱
            import_pattern = r"import\s+.*?\s+from\s+['\"]([^'\"]+)['\"]"
            matches = re.findall(import_pattern, code)
            dependencies.extend(matches)

            # require 문 파싱
            require_pattern = r"require\s*\(['\"]([^'\"]+)['\"]\)"
            matches = re.findall(require_pattern, code)
            dependencies.extend(matches)

        elif language == 'python':
            # import 문 파싱
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        dependencies.append(node.module)

        # 외부 패키지만 필터링
        external_deps = [
            dep for dep in dependencies
            if not dep.startswith('.') and not dep.startswith('@/')
        ]

        return list(set(external_deps))

class SyntaxValidator:
    """구문 검증기"""

    async def validate(
        self,
        code: str,
        language: str
    ) -> SyntaxValidationResult:
        """구문 검증"""

        if language == 'python':
            return await self._validate_python_syntax(code)
        elif language in ['javascript', 'typescript']:
            return await self._validate_js_syntax(code)
        elif language == 'java':
            return await self._validate_java_syntax(code)
        else:
            # 기본 검증
            return SyntaxValidationResult(
                is_valid=True,
                errors=[],
                ast=None
            )

    async def _validate_python_syntax(self, code: str) -> SyntaxValidationResult:
        """Python 구문 검증"""

        try:
            tree = ast.parse(code)
            return SyntaxValidationResult(
                is_valid=True,
                errors=[],
                ast=tree
            )
        except SyntaxError as e:
            return SyntaxValidationResult(
                is_valid=False,
                errors=[
                    ValidationError(
                        line=e.lineno or 0,
                        column=e.offset or 0,
                        message=str(e),
                        rule='syntax'
                    )
                ],
                ast=None
            )

class SecurityValidator:
    """보안 검증기"""

    def __init__(self):
        self.vulnerability_patterns = self._load_vulnerability_patterns()

    async def validate(
        self,
        code: str,
        language: str
    ) -> SecurityValidationResult:
        """보안 취약점 검증"""

        errors = []
        warnings = []

        # 패턴 매칭
        for pattern in self.vulnerability_patterns.get(language, []):
            matches = re.finditer(pattern['regex'], code, re.MULTILINE)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1

                if pattern['severity'] == 'error':
                    errors.append(
                        ValidationError(
                            line=line_num,
                            column=match.start() - code.rfind('\n', 0, match.start()),
                            message=pattern['message'],
                            rule=pattern['rule'],
                            severity='error'
                        )
                    )
                else:
                    warnings.append(
                        ValidationWarning(
                            line=line_num,
                            column=match.start() - code.rfind('\n', 0, match.start()),
                            message=pattern['message'],
                            rule=pattern['rule']
                        )
                    )

        return SecurityValidationResult(
            errors=errors,
            warnings=warnings
        )

    def _load_vulnerability_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """취약점 패턴 로드"""

        return {
            'javascript': [
                {
                    'rule': 'no-eval',
                    'regex': r'\beval\s*\(',
                    'message': 'Avoid using eval() as it poses security risks',
                    'severity': 'error'
                },
                {
                    'rule': 'no-innerhtml',
                    'regex': r'\.innerHTML\s*=',
                    'message': 'Use textContent or safe DOM methods instead of innerHTML',
                    'severity': 'warning'
                }
            ],
            'python': [
                {
                    'rule': 'no-exec',
                    'regex': r'\bexec\s*\(',
                    'message': 'Avoid using exec() as it poses security risks',
                    'severity': 'error'
                },
                {
                    'rule': 'no-pickle',
                    'regex': r'pickle\.loads?\s*\(',
                    'message': 'Pickle can execute arbitrary code, use JSON instead',
                    'severity': 'warning'
                }
            ]
        }
```

**검증 기준**:

- [ ] 구문 검증 구현
- [ ] 보안 취약점 검사
- [ ] 코드 품질 메트릭
- [ ] 다국어 지원

---

### Task 4.62: 템플릿 엔진 구현

#### SubTask 4.62.1: 템플릿 파서 개발

**담당자**: 컴파일러 엔지니어  
**예상 소요시간**: 14시간

**작업 내용**:

```python
# backend/src/agents/implementations/generation/template_parser.py
from typing import List, Dict, Any, Optional, Tuple
import re
from dataclasses import dataclass
from enum import Enum

class TokenType(Enum):
    TEXT = "TEXT"
    VARIABLE = "VARIABLE"
    BLOCK_START = "BLOCK_START"
    BLOCK_END = "BLOCK_END"
    COMMENT = "COMMENT"
    EXPRESSION = "EXPRESSION"
    FILTER = "FILTER"

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

@dataclass
class ASTNode:
    type: str
    children: List['ASTNode']
    attributes: Dict[str, Any]

class TemplateParser:
    """템플릿 파서"""

    def __init__(self):
        self.lexer = TemplateLexer()
        self.syntax_analyzer = SyntaxAnalyzer()
        self.ast_builder = ASTBuilder()

    async def parse(self, template: str) -> ParseResult:
        """템플릿 파싱"""

        # 1. 렉싱 (토큰화)
        tokens = await self.lexer.tokenize(template)

        # 2. 구문 분석
        syntax_tree = await self.syntax_analyzer.analyze(tokens)

        # 3. AST 구축
        ast = await self.ast_builder.build(syntax_tree)

        # 4. 검증
        validation_result = await self._validate_ast(ast)

        return ParseResult(
            ast=ast,
            tokens=tokens,
            is_valid=validation_result.is_valid,
            errors=validation_result.errors,
            metadata=self._extract_metadata(ast)
        )

    async def _validate_ast(self, ast: ASTNode) -> ValidationResult:
        """AST 검증"""

        errors = []

        # 블록 매칭 검증
        block_stack = []

        def validate_node(node: ASTNode):
            if node.type == 'block_start':
                block_stack.append(node)
            elif node.type == 'block_end':
                if not block_stack:
                    errors.append(
                        ParseError(
                            line=node.attributes.get('line', 0),
                            column=node.attributes.get('column', 0),
                            message=f"Unexpected closing block: {node.attributes.get('name')}"
                        )
                    )
                else:
                    start_block = block_stack.pop()
                    if start_block.attributes.get('name') != node.attributes.get('name'):
                        errors.append(
                            ParseError(
                                line=node.attributes.get('line', 0),
                                column=node.attributes.get('column', 0),
                                message=f"Mismatched block: expected {start_block.attributes.get('name')}, got {node.attributes.get('name')}"
                            )
                        )

            for child in node.children:
                validate_node(child)

        validate_node(ast)

        if block_stack:
            for block in block_stack:
                errors.append(
                    ParseError(
                        line=block.attributes.get('line', 0),
                        column=block.attributes.get('column', 0),
                        message=f"Unclosed block: {block.attributes.get('name')}"
                    )
                )

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )

class TemplateLexer:
    """템플릿 렉서"""

    def __init__(self):
        self.patterns = {
            TokenType.VARIABLE: re.compile(r'\{\{\s*([^}]+)\s*\}\}'),
            TokenType.BLOCK_START: re.compile(r'\{%\s*(\w+)\s+([^%]*)\s*%\}'),
            TokenType.BLOCK_END: re.compile(r'\{%\s*end(\w+)\s*%\}'),
            TokenType.COMMENT: re.compile(r'\{#\s*([^#]*)\s*#\}'),
            TokenType.EXPRESSION: re.compile(r'\{\(\s*([^)]+)\s*\)\}'),
            TokenType.FILTER: re.compile(r'\|\s*(\w+)(?:\s*:\s*([^|}\s]+))?')
        }

    async def tokenize(self, template: str) -> List[Token]:
        """템플릿 토큰화"""

        tokens = []
        position = 0
        line = 1
        column = 1

        while position < len(template):
            # 각 패턴 매칭 시도
            matched = False

            for token_type, pattern in self.patterns.items():
                match = pattern.match(template, position)
                if match:
                    # 매칭 전 텍스트 처리
                    if position < match.start():
                        text = template[position:match.start()]
                        tokens.append(
                            Token(
                                type=TokenType.TEXT,
                                value=text,
                                line=line,
                                column=column
                            )
                        )
                        # 위치 업데이트
                        lines = text.count('\n')
                        if lines:
                            line += lines
                            column = len(text.split('\n')[-1]) + 1
                        else:
                            column += len(text)

                    # 매칭된 토큰 추가
                    tokens.append(
                        Token(
                            type=token_type,
                            value=match.group(0),
                            line=line,
                            column=column
                        )
                    )

                    # 위치 업데이트
                    matched_text = match.group(0)
                    lines = matched_text.count('\n')
                    if lines:
                        line += lines
                        column = len(matched_text.split('\n')[-1]) + 1
                    else:
                        column += len(matched_text)

                    position = match.end()
                    matched = True
                    break

            if not matched:
                # 일반 텍스트로 처리
                tokens.append(
                    Token(
                        type=TokenType.TEXT,
                        value=template[position],
                        line=line,
                        column=column
                    )
                )
                if template[position] == '\n':
                    line += 1
                    column = 1
                else:
                    column += 1
                position += 1

        return tokens

class ASTBuilder:
    """AST 빌더"""

    async def build(self, syntax_tree: SyntaxTree) -> ASTNode:
        """AST 구축"""

        root = ASTNode(
            type='root',
            children=[],
            attributes={'version': '1.0'}
        )

        current_node = root
        node_stack = [root]

        for element in syntax_tree.elements:
            if element.type == 'block_start':
                # 새 블록 노드 생성
                block_node = ASTNode(
                    type='block',
                    children=[],
                    attributes={
                        'name': element.name,
                        'args': element.args,
                        'line': element.line,
                        'column': element.column
                    }
                )
                current_node.children.append(block_node)
                node_stack.append(block_node)
                current_node = block_node

            elif element.type == 'block_end':
                # 블록 종료
                if len(node_stack) > 1:
                    node_stack.pop()
                    current_node = node_stack[-1]

            elif element.type == 'variable':
                # 변수 노드
                var_node = ASTNode(
                    type='variable',
                    children=[],
                    attributes={
                        'name': element.name,
                        'filters': element.filters,
                        'line': element.line,
                        'column': element.column
                    }
                )
                current_node.children.append(var_node)

            elif element.type == 'text':
                # 텍스트 노드
                text_node = ASTNode(
                    type='text',
                    children=[],
                    attributes={
                        'content': element.content,
                        'line': element.line,
                        'column': element.column
                    }
                )
                current_node.children.append(text_node)

        return root
```

**검증 기준**:

- [ ] 완전한 템플릿 파싱
- [ ] 에러 복구 메커니즘
- [ ] AST 생성
- [ ] 성능 최적화

---

#### SubTask 4.62.2: 변수 바인딩 시스템

**담당자**: 백엔드 개발자  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/generation/variable_binding.py
from typing import Dict, List, Any, Optional, Union, Callable
import re
from dataclasses import dataclass
import ast

@dataclass
class BindingContext:
    variables: Dict[str, Any]
    filters: Dict[str, Callable]
    globals: Dict[str, Any]
    locals: Dict[str, Any]
    parent: Optional['BindingContext'] = None

@dataclass
class BoundVariable:
    name: str
    value: Any
    source: str  # 'local', 'global', 'parent'
    path: List[str]
    filters: List[Tuple[str, List[Any]]]

class VariableBindingSystem:
    """변수 바인딩 시스템"""

    def __init__(self):
        self.resolver = VariableResolver()
        self.filter_engine = FilterEngine()
        self.expression_evaluator = ExpressionEvaluator()
        self.type_converter = TypeConverter()

    async def bind_variables(
        self,
        template_ast: ASTNode,
        context: BindingContext
    ) -> BoundTemplate:
        """템플릿에 변수 바인딩"""

        bound_nodes = []

        for node in template_ast.children:
            if node.type == 'variable':
                bound_node = await self._bind_variable_node(node, context)
                bound_nodes.append(bound_node)
            elif node.type == 'expression':
                bound_node = await self._bind_expression_node(node, context)
                bound_nodes.append(bound_node)
            elif node.type == 'block':
                # 블록은 새로운 스코프 생성
                block_context = self._create_block_context(node, context)
                bound_block = await self._bind_block_node(node, block_context)
                bound_nodes.append(bound_block)
            else:
                bound_nodes.append(node)

        return BoundTemplate(
            nodes=bound_nodes,
            context=context,
            unbound_variables=self._find_unbound_variables(bound_nodes)
        )

    async def _bind_variable_node(
        self,
        node: ASTNode,
        context: BindingContext
    ) -> BoundNode:
        """변수 노드 바인딩"""

        var_name = node.attributes['name']
        var_path = self._parse_variable_path(var_name)

        # 변수 해결
        resolved = await self.resolver.resolve(var_path, context)

        if resolved is None:
            return UnboundNode(
                original=node,
                reason=f"Variable '{var_name}' not found in context"
            )

        # 필터 적용
        value = resolved.value
        if 'filters' in node.attributes:
            for filter_spec in node.attributes['filters']:
                value = await self.filter_engine.apply_filter(
                    value,
                    filter_spec,
                    context
                )

        return BoundVariableNode(
            type='bound_variable',
            value=value,
            original_name=var_name,
            resolved_path=resolved.path,
            source=resolved.source,
            filters_applied=node.attributes.get('filters', [])
        )

    def _parse_variable_path(self, var_name: str) -> List[str]:
        """변수 경로 파싱"""

        # dot notation 지원 (e.g., user.profile.name)
        parts = var_name.split('.')

        # array notation 지원 (e.g., items[0].name)
        parsed_parts = []
        for part in parts:
            if '[' in part and ']' in part:
                # array index 추출
                base = part[:part.index('[')]
                indices = re.findall(r'\[([^\]]+)\]', part)
                parsed_parts.append(base)
                parsed_parts.extend(indices)
            else:
                parsed_parts.append(part)

        return parsed_parts

    async def _bind_expression_node(
        self,
        node: ASTNode,
        context: BindingContext
    ) -> BoundNode:
        """표현식 노드 바인딩"""

        expression = node.attributes['expression']

        try:
            # 안전한 표현식 평가
            result = await self.expression_evaluator.evaluate(
                expression,
                context
            )

            return BoundExpressionNode(
                type='bound_expression',
                value=result,
                original_expression=expression,
                evaluated=True
            )
        except Exception as e:
            return UnboundNode(
                original=node,
                reason=f"Expression evaluation failed: {str(e)}"
            )

    def _create_block_context(
        self,
        block_node: ASTNode,
        parent_context: BindingContext
    ) -> BindingContext:
        """블록 컨텍스트 생성"""

        block_type = block_node.attributes['name']
        block_args = block_node.attributes.get('args', [])

        # 새 로컬 스코프
        local_vars = {}

        if block_type == 'for':
            # for 루프 변수 추가
            if len(block_args) >= 3:  # for item in items
                local_vars[block_args[0]] = None  # 실제 값은 반복 시 설정

        elif block_type == 'with':
            # with 블록 변수 추가
            if len(block_args) >= 3:  # with expr as var
                local_vars[block_args[2]] = None

        return BindingContext(
            variables={**parent_context.variables},
            filters=parent_context.filters,
            globals=parent_context.globals,
            locals=local_vars,
            parent=parent_context
        )

class VariableResolver:
    """변수 해결기"""

    async def resolve(
        self,
        path: List[str],
        context: BindingContext
    ) -> Optional[ResolvedVariable]:
        """변수 경로 해결"""

        # 검색 순서: locals -> variables -> globals -> parent
        scopes = [
            ('local', context.locals),
            ('variable', context.variables),
            ('global', context.globals)
        ]

        for source, scope in scopes:
            value = await self._resolve_in_scope(path, scope)
            if value is not None:
                return ResolvedVariable(
                    value=value,
                    source=source,
                    path=path
                )

        # 부모 컨텍스트 검색
        if context.parent:
            return await self.resolve(path, context.parent)

        return None

    async def _resolve_in_scope(
        self,
        path: List[str],
        scope: Dict[str, Any]
    ) -> Any:
        """특정 스코프에서 변수 해결"""

        current = scope

        for i, part in enumerate(path):
            if isinstance(current, dict):
                if part in current:
                    current = current[part]
                else:
                    return None
            elif isinstance(current, list):
                try:
                    index = int(part)
                    if 0 <= index < len(current):
                        current = current[index]
                    else:
                        return None
                except ValueError:
                    return None
            elif hasattr(current, part):
                current = getattr(current, part)
            else:
                return None

        return current

class FilterEngine:
    """필터 엔진"""

    def __init__(self):
        self.builtin_filters = self._load_builtin_filters()
        self.custom_filters = {}

    async def apply_filter(
        self,
        value: Any,
        filter_spec: Dict[str, Any],
        context: BindingContext
    ) -> Any:
        """필터 적용"""

        filter_name = filter_spec['name']
        filter_args = filter_spec.get('args', [])

        # 필터 찾기
        filter_func = None
        if filter_name in context.filters:
            filter_func = context.filters[filter_name]
        elif filter_name in self.custom_filters:
            filter_func = self.custom_filters[filter_name]
        elif filter_name in self.builtin_filters:
            filter_func = self.builtin_filters[filter_name]
        else:
            raise ValueError(f"Unknown filter: {filter_name}")

        # 필터 적용
        try:
            if asyncio.iscoroutinefunction(filter_func):
                return await filter_func(value, *filter_args)
            else:
                return filter_func(value, *filter_args)
        except Exception as e:
            raise FilterError(f"Filter '{filter_name}' failed: {str(e)}")

    def _load_builtin_filters(self) -> Dict[str, Callable]:
        """내장 필터 로드"""

        return {
            # 문자열 필터
            'upper': lambda s: str(s).upper(),
            'lower': lambda s: str(s).lower(),
            'capitalize': lambda s: str(s).capitalize(),
            'title': lambda s: str(s).title(),
            'strip': lambda s: str(s).strip(),
            'replace': lambda s, old, new: str(s).replace(old, new),
            'truncate': lambda s, length=50: str(s)[:length] + '...' if len(str(s)) > length else str(s),

            # 숫자 필터
            'int': lambda n: int(n),
            'float': lambda n: float(n),
            'round': lambda n, precision=0: round(float(n), precision),
            'abs': lambda n: abs(n),

            # 리스트 필터
            'length': lambda l: len(l) if hasattr(l, '__len__') else 0,
            'first': lambda l: l[0] if l else None,
            'last': lambda l: l[-1] if l else None,
            'join': lambda l, sep=', ': sep.join(str(i) for i in l),
            'sort': lambda l: sorted(l),
            'reverse': lambda l: list(reversed(l)),

            # 날짜 필터
            'date': lambda d, fmt='%Y-%m-%d': d.strftime(fmt) if hasattr(d, 'strftime') else str(d),

            # 조건 필터
            'default': lambda v, default='': v if v is not None else default,
            'bool': lambda v: bool(v),

            # JSON 필터
            'json': lambda v: json.dumps(v),
            'pretty_json': lambda v: json.dumps(v, indent=2)
        }

class ExpressionEvaluator:
    """표현식 평가기"""

    def __init__(self):
        self.safe_builtins = {
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,
            'range': range,
            'enumerate': enumerate,
            'zip': zip,
            'min': min,
            'max': max,
            'sum': sum,
            'abs': abs,
            'round': round,
            'sorted': sorted,
            'reversed': reversed
        }

    async def evaluate(
        self,
        expression: str,
        context: BindingContext
    ) -> Any:
        """안전한 표현식 평가"""

        # 표현식 파싱
        try:
            tree = ast.parse(expression, mode='eval')
        except SyntaxError as e:
            raise ExpressionError(f"Invalid expression syntax: {str(e)}")

        # AST 검증 (안전한 노드만 허용)
        self._validate_ast(tree)

        # 평가 환경 준비
        eval_env = {
            '__builtins__': self.safe_builtins,
            **context.globals,
            **context.variables,
            **context.locals
        }

        # 평가
        try:
            return eval(compile(tree, '<expression>', 'eval'), eval_env)
        except Exception as e:
            raise ExpressionError(f"Expression evaluation failed: {str(e)}")

    def _validate_ast(self, tree: ast.AST):
        """AST 안전성 검증"""

        unsafe_nodes = (
            ast.Import,
            ast.ImportFrom,
            ast.Exec,
            ast.FunctionDef,
            ast.ClassDef,
            ast.Delete,
            ast.Global,
            ast.Nonlocal
        )

        for node in ast.walk(tree):
            if isinstance(node, unsafe_nodes):
                raise ExpressionError(
                    f"Unsafe operation in expression: {type(node).__name__}"
                )
```

**검증 기준**:

- [ ] 복잡한 변수 경로 지원
- [ ] 안전한 표현식 평가
- [ ] 다양한 내장 필터
- [ ] 스코프 관리

#### SubTask 4.62.3: 조건부 렌더링

**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```typescript
// backend/src/agents/implementations/generation/conditional_rendering.ts
interface ConditionalBlock {
  type: 'if' | 'elif' | 'else';
  condition?: string;
  body: TemplateNode[];
  next?: ConditionalBlock;
}

interface LoopBlock {
  type: 'for' | 'while';
  iterator?: string;
  iterable?: string;
  condition?: string;
  body: TemplateNode[];
  else?: TemplateNode[];
}

class ConditionalRenderer {
  private expressionEvaluator: ExpressionEvaluator;
  private contextManager: ContextManager;

  constructor() {
    this.expressionEvaluator = new ExpressionEvaluator();
    this.contextManager = new ContextManager();
  }

  async renderConditional(block: ConditionalBlock, context: RenderContext): Promise<string> {
    // if 블록 평가
    if (block.condition) {
      const result = await this.expressionEvaluator.evaluate(block.condition, context);

      if (result) {
        return await this.renderBody(block.body, context);
      }
    }

    // elif/else 체인 평가
    let current = block.next;
    while (current) {
      if (current.type === 'else' || !current.condition) {
        return await this.renderBody(current.body, context);
      }

      const result = await this.expressionEvaluator.evaluate(current.condition, context);

      if (result) {
        return await this.renderBody(current.body, context);
      }

      current = current.next;
    }

    return '';
  }

  async renderLoop(block: LoopBlock, context: RenderContext): Promise<string> {
    const results: string[] = [];

    if (block.type === 'for') {
      // for 루프 처리
      const iterable = await this.expressionEvaluator.evaluate(block.iterable!, context);

      if (!this.isIterable(iterable)) {
        throw new Error(`Expression '${block.iterable}' is not iterable`);
      }

      // 루프 실행
      let index = 0;
      for (const item of iterable) {
        // 루프 컨텍스트 생성
        const loopContext = this.contextManager.createLoopContext(context, {
          [block.iterator!]: item,
          loop: {
            index,
            index0: index,
            index1: index + 1,
            first: index === 0,
            last: index === iterable.length - 1,
            length: iterable.length,
            parent: context.get('loop'),
          },
        });

        const rendered = await this.renderBody(block.body, loopContext);
        results.push(rendered);
        index++;
      }

      // else 블록 (루프가 비어있을 때)
      if (results.length === 0 && block.else) {
        return await this.renderBody(block.else, context);
      }
    } else if (block.type === 'while') {
      // while 루프 처리
      let iterations = 0;
      const maxIterations = 10000; // 무한 루프 방지

      while (iterations < maxIterations) {
        const condition = await this.expressionEvaluator.evaluate(block.condition!, context);

        if (!condition) break;

        const loopContext = this.contextManager.createLoopContext(context, {
          loop: {
            index: iterations,
            index0: iterations,
            index1: iterations + 1,
            first: iterations === 0,
          },
        });

        const rendered = await this.renderBody(block.body, loopContext);
        results.push(rendered);
        iterations++;
      }

      if (iterations >= maxIterations) {
        throw new Error('Maximum iteration count exceeded');
      }
    }

    return results.join('');
  }

  private async renderBody(nodes: TemplateNode[], context: RenderContext): Promise<string> {
    const results: string[] = [];

    for (const node of nodes) {
      const rendered = await this.renderNode(node, context);
      results.push(rendered);
    }

    return results.join('');
  }

  private isIterable(value: any): boolean {
    return (
      value != null &&
      (Array.isArray(value) ||
        typeof value === 'string' ||
        value instanceof Set ||
        value instanceof Map ||
        typeof value[Symbol.iterator] === 'function')
    );
  }
}

// 고급 조건부 렌더링 지원
class AdvancedConditionalRenderer extends ConditionalRenderer {
  async renderSwitch(switchBlock: SwitchBlock, context: RenderContext): Promise<string> {
    const value = await this.expressionEvaluator.evaluate(switchBlock.expression, context);

    for (const caseBlock of switchBlock.cases) {
      if (caseBlock.type === 'default') {
        return await this.renderBody(caseBlock.body, context);
      }

      const caseValue = await this.expressionEvaluator.evaluate(caseBlock.value, context);

      if (value === caseValue) {
        return await this.renderBody(caseBlock.body, context);
      }
    }

    return '';
  }

  async renderTernary(
    condition: string,
    trueValue: string,
    falseValue: string,
    context: RenderContext,
  ): Promise<string> {
    const result = await this.expressionEvaluator.evaluate(condition, context);

    if (result) {
      return await this.expressionEvaluator.evaluate(trueValue, context);
    } else {
      return await this.expressionEvaluator.evaluate(falseValue, context);
    }
  }

  async renderUnless(
    condition: string,
    body: TemplateNode[],
    context: RenderContext,
  ): Promise<string> {
    const result = await this.expressionEvaluator.evaluate(condition, context);

    if (!result) {
      return await this.renderBody(body, context);
    }

    return '';
  }
}

// 최적화된 조건부 렌더링
class OptimizedConditionalRenderer extends AdvancedConditionalRenderer {
  private conditionCache: Map<string, boolean> = new Map();
  private compiledConditions: Map<string, Function> = new Map();

  async renderConditional(block: ConditionalBlock, context: RenderContext): Promise<string> {
    // 조건 캐싱
    const cacheKey = `${block.condition}:${JSON.stringify(context.variables)}`;

    if (this.conditionCache.has(cacheKey)) {
      const cached = this.conditionCache.get(cacheKey)!;
      if (cached) {
        return await this.renderBody(block.body, context);
      }
    }

    // 컴파일된 조건 사용
    let evaluator = this.compiledConditions.get(block.condition!);
    if (!evaluator) {
      evaluator = this.compileCondition(block.condition!);
      this.compiledConditions.set(block.condition!, evaluator);
    }

    const result = evaluator(context);
    this.conditionCache.set(cacheKey, result);

    if (result) {
      return await this.renderBody(block.body, context);
    }

    // 나머지 로직은 부모 클래스와 동일
    return super.renderConditional(block, context);
  }

  private compileCondition(condition: string): Function {
    // 간단한 조건 컴파일러
    return new Function(
      'context',
      `
      with (context.variables) {
        return ${condition};
      }
    `,
    );
  }
}
```

**검증 기준**:

- [ ] if/elif/else 지원
- [ ] for/while 루프 지원
- [ ] 중첩 조건 지원
- [ ] 성능 최적화

#### SubTask 4.62.4: 템플릿 캐싱

**담당자**: 성능 엔지니어  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/generation/template_cache.py
from typing import Dict, List, Any, Optional, Tuple
import hashlib
import pickle
import asyncio
from datetime import datetime, timedelta
import aioredis

@dataclass
class CacheEntry:
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime]
    hit_count: int
    size_bytes: int
    dependencies: List[str]

class TemplateCache:
    """템플릿 캐싱 시스템"""

    def __init__(self, config: CacheConfig):
        self.config = config
        self.memory_cache = LRUCache(config.memory_cache_size)
        self.redis_cache = None
        self.stats = CacheStatistics()
        self.dependency_tracker = DependencyTracker()

    async def initialize(self):
        """캐시 초기화"""

        if self.config.use_redis:
            self.redis_cache = await aioredis.create_redis_pool(
                self.config.redis_url,
                minsize=5,
                maxsize=10
            )

    async def get(
        self,
        key: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Any]:
        """캐시에서 템플릿 가져오기"""

        # 컨텍스트 기반 키 생성
        cache_key = self._generate_cache_key(key, context)

        # 1. 메모리 캐시 확인
        cached = self.memory_cache.get(cache_key)
        if cached:
            self.stats.record_hit('memory')
            return cached.value

        # 2. Redis 캐시 확인
        if self.redis_cache:
            redis_value = await self.redis_cache.get(cache_key)
            if redis_value:
                # 역직렬화
                cached_entry = pickle.loads(redis_value)

                # 만료 확인
                if not self._is_expired(cached_entry):
                    # 메모리 캐시에 승격
                    self.memory_cache.put(cache_key, cached_entry)
                    self.stats.record_hit('redis')
                    return cached_entry.value

        self.stats.record_miss()
        return None

    async def put(
        self,
        key: str,
        value: Any,
        context: Optional[Dict[str, Any]] = None,
        ttl: Optional[int] = None,
        dependencies: Optional[List[str]] = None
    ):
        """캐시에 템플릿 저장"""

        cache_key = self._generate_cache_key(key, context)

        # 캐시 엔트리 생성
        entry = CacheEntry(
            key=cache_key,
            value=value,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=ttl) if ttl else None,
            hit_count=0,
            size_bytes=self._calculate_size(value),
            dependencies=dependencies or []
        )

        # 1. 메모리 캐시에 저장
        evicted = self.memory_cache.put(cache_key, entry)

        # 2. Redis에 저장
        if self.redis_cache:
            serialized = pickle.dumps(entry)
            await self.redis_cache.setex(
                cache_key,
                ttl or self.config.default_ttl,
                serialized
            )

        # 3. 의존성 추적
        if dependencies:
            await self.dependency_tracker.track(cache_key, dependencies)

        # 4. 퇴출된 항목 처리
        if evicted:
            await self._handle_eviction(evicted)

        self.stats.record_put(entry.size_bytes)

    async def invalidate(
        self,
        key: Optional[str] = None,
        pattern: Optional[str] = None,
        dependencies: Optional[List[str]] = None
    ):
        """캐시 무효화"""

        invalidated_keys = set()

        # 1. 키 기반 무효화
        if key:
            invalidated_keys.add(key)

        # 2. 패턴 기반 무효화
        if pattern:
            matching_keys = self._find_matching_keys(pattern)
            invalidated_keys.update(matching_keys)

        # 3. 의존성 기반 무효화
        if dependencies:
            dependent_keys = await self.dependency_tracker.find_dependents(
                dependencies
            )
            invalidated_keys.update(dependent_keys)

        # 실제 무효화 수행
        for cache_key in invalidated_keys:
            # 메모리에서 제거
            self.memory_cache.remove(cache_key)

            # Redis에서 제거
            if self.redis_cache:
                await self.redis_cache.delete(cache_key)

        self.stats.record_invalidation(len(invalidated_keys))

    def _generate_cache_key(
        self,
        key: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """캐시 키 생성"""

        if not context:
            return key

        # 컨텍스트를 정규화하여 일관된 키 생성
        normalized_context = self._normalize_context(context)
        context_hash = hashlib.md5(
            pickle.dumps(normalized_context, protocol=pickle.HIGHEST_PROTOCOL)
        ).hexdigest()

        return f"{key}:{context_hash}"

    def _normalize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """컨텍스트 정규화"""

        # 키 정렬
        normalized = {}
        for key in sorted(context.keys()):
            value = context[key]

            # 값 타입별 정규화
            if isinstance(value, dict):
                normalized[key] = self._normalize_context(value)
            elif isinstance(value, list):
                normalized[key] = sorted(value) if all(
                    isinstance(item, (str, int, float)) for item in value
                ) else value
            else:
                normalized[key] = value

        return normalized

class LRUCache:
    """LRU 메모리 캐시"""

    def __init__(self, max_size: int):
        self.max_size = max_size
        self.cache = OrderedDict()
        self.lock = asyncio.Lock()

    def get(self, key: str) -> Optional[CacheEntry]:
        """캐시에서 가져오기"""

        if key in self.cache:
            # LRU 업데이트
            self.cache.move_to_end(key)
            entry = self.cache[key]
            entry.hit_count += 1
            return entry
        return None

    def put(self, key: str, entry: CacheEntry) -> Optional[CacheEntry]:
        """캐시에 저장"""

        evicted = None

        # 기존 항목 제거
        if key in self.cache:
            del self.cache[key]

        # 크기 초과 시 퇴출
        while len(self.cache) >= self.max_size:
            evicted_key, evicted_entry = self.cache.popitem(last=False)
            evicted = evicted_entry

        # 새 항목 추가
        self.cache[key] = entry

        return evicted

class CacheWarmer:
    """캐시 워밍 시스템"""

    def __init__(self, cache: TemplateCache):
        self.cache = cache
        self.warming_queue = asyncio.Queue()
        self.is_warming = False

    async def warm_cache(self, templates: List[TemplateSpec]):
        """캐시 사전 로드"""

        self.is_warming = True

        # 우선순위별 정렬
        sorted_templates = sorted(
            templates,
            key=lambda t: t.priority,
            reverse=True
        )

        # 배치 처리
        batch_size = 10
        for i in range(0, len(sorted_templates), batch_size):
            batch = sorted_templates[i:i + batch_size]

            # 병렬 처리
            tasks = [
                self._warm_template(template)
                for template in batch
            ]

            await asyncio.gather(*tasks, return_exceptions=True)

        self.is_warming = False

    async def _warm_template(self, template: TemplateSpec):
        """개별 템플릿 워밍"""

        try:
            # 템플릿 컴파일
            compiled = await self._compile_template(template)

            # 다양한 컨텍스트로 캐싱
            for context_variant in template.context_variants:
                await self.cache.put(
                    template.id,
                    compiled,
                    context=context_variant,
                    dependencies=template.dependencies
                )
        except Exception as e:
            # 워밍 실패는 무시
            logger.warning(f"Failed to warm template {template.id}: {e}")

class CacheStatistics:
    """캐시 통계"""

    def __init__(self):
        self.hits = {'memory': 0, 'redis': 0}
        self.misses = 0
        self.puts = 0
        self.invalidations = 0
        self.total_size = 0

    def record_hit(self, cache_level: str):
        """히트 기록"""
        self.hits[cache_level] += 1

    def record_miss(self):
        """미스 기록"""
        self.misses += 1

    def record_put(self, size_bytes: int):
        """저장 기록"""
        self.puts += 1
        self.total_size += size_bytes

    def get_hit_rate(self) -> float:
        """히트율 계산"""
        total_hits = sum(self.hits.values())
        total_requests = total_hits + self.misses

        if total_requests == 0:
            return 0.0

        return total_hits / total_requests
```

**검증 기준**:

- [ ] 다단계 캐싱 (메모리 + Redis)
- [ ] 컨텍스트 기반 캐싱
- [ ] 의존성 추적 및 무효화
- [ ] 캐시 워밍 지원

---

### Task 4.63: 코드 품질 보장

#### SubTask 4.63.1: 코드 스타일 검증

**담당자**: 코드 품질 엔지니어  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/generation/code_style_validator.py
from typing import Dict, List, Any, Optional
import subprocess
import tempfile
import os
from dataclasses import dataclass

@dataclass
class StyleViolation:
    file: str
    line: int
    column: int
    rule: str
    message: str
    severity: str  # 'error', 'warning', 'info'
    fixable: bool

@dataclass
class StyleValidationResult:
    is_valid: bool
    violations: List[StyleViolation]
    fixed_code: Optional[str]
    metrics: Dict[str, Any]

class CodeStyleValidator:
    """코드 스타일 검증기"""

    def __init__(self):
        self.linters = {
            'javascript': JSLinter(),
            'typescript': TSLinter(),
            'python': PythonLinter(),
            'java': JavaLinter(),
            'go': GoLinter(),
            'rust': RustLinter()
        }
        self.formatters = {
            'javascript': JSFormatter(),
            'typescript': TSFormatter(),
            'python': PythonFormatter(),
            'java': JavaFormatter(),
            'go': GoFormatter(),
            'rust': RustFormatter()
        }

    async def validate_style(
        self,
        code: str,
        language: str,
        config: Optional[Dict[str, Any]] = None
    ) -> StyleValidationResult:
        """코드 스타일 검증"""

        linter = self.linters.get(language)
        if not linter:
            return StyleValidationResult(
                is_valid=True,
                violations=[],
                fixed_code=None,
                metrics={}
            )

        # 린팅 수행
        violations = await linter.lint(code, config)

        # 자동 수정 시도
        fixed_code = None
        if config and config.get('auto_fix', False):
            formatter = self.formatters.get(language)
            if formatter:
                fixed_code = await formatter.format(code, config)

                # 수정 후 재검증
                if fixed_code != code:
                    violations = await linter.lint(fixed_code, config)

        # 메트릭 계산
        metrics = await self._calculate_style_metrics(
            code,
            violations,
            language
        )

        return StyleValidationResult(
            is_valid=len([v for v in violations if v.severity == 'error']) == 0,
            violations=violations,
            fixed_code=fixed_code,
            metrics=metrics
        )

    async def _calculate_style_metrics(
        self,
        code: str,
        violations: List[StyleViolation],
        language: str
    ) -> Dict[str, Any]:
        """스타일 메트릭 계산"""

        lines = code.splitlines()

        return {
            'total_lines': len(lines),
            'violation_count': len(violations),
            'error_count': len([v for v in violations if v.severity == 'error']),
            'warning_count': len([v for v in violations if v.severity == 'warning']),
            'fixable_count': len([v for v in violations if v.fixable]),
            'consistency_score': self._calculate_consistency_score(code, language),
            'readability_score': self._calculate_readability_score(code, language)
        }

class JSLinter:
    """JavaScript/TypeScript 린터"""

    def __init__(self):
        self.eslint_path = self._find_eslint()
        self.default_config = {
            'extends': ['eslint:recommended'],
            'rules': {
                'indent': ['error', 2],
                'quotes': ['error', 'single'],
                'semi': ['error', 'always'],
                'no-unused-vars': 'error',
                'no-console': 'warn',
                'prefer-const': 'error',
                'arrow-spacing': 'error',
                'object-curly-spacing': ['error', 'always'],
                'comma-dangle': ['error', 'never']
            }
        }

    async def lint(
        self,
        code: str,
        config: Optional[Dict[str, Any]] = None
    ) -> List[StyleViolation]:
        """ESLint 실행"""

        if not self.eslint_path:
            return []

        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.js',
            delete=False
        ) as f:
            f.write(code)
            temp_file = f.name

        try:
            # ESLint 실행
            cmd = [
                self.eslint_path,
                '--format', 'json',
                '--no-color',
                temp_file
            ]

            if config:
                # 설정 파일 생성
                config_file = await self._create_config_file(config)
                cmd.extend(['--config', config_file])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )

            # 결과 파싱
            if result.stdout:
                import json
                lint_results = json.loads(result.stdout)

                violations = []
                for file_result in lint_results:
                    for message in file_result.get('messages', []):
                        violations.append(
                            StyleViolation(
                                file=file_result['filePath'],
                                line=message.get('line', 1),
                                column=message.get('column', 1),
                                rule=message.get('ruleId', 'unknown'),
                                message=message.get('message', ''),
                                severity=self._map_severity(message.get('severity', 1)),
                                fixable=message.get('fix') is not None
                            )
                        )

                return violations

        finally:
            # 임시 파일 정리
            if os.path.exists(temp_file):
                os.unlink(temp_file)

        return []

    def _find_eslint(self) -> Optional[str]:
        """ESLint 경로 찾기"""

        # npx eslint
        try:
            result = subprocess.run(
                ['npx', '--no-install', 'eslint', '--version'],
                capture_output=True
            )
            if result.returncode == 0:
                return 'npx eslint'
        except:
            pass

        # 전역 eslint
        try:
            result = subprocess.run(
                ['eslint', '--version'],
                capture_output=True
            )
            if result.returncode == 0:
                return 'eslint'
        except:
            pass

        return None

class PythonLinter:
    """Python 린터"""

    def __init__(self):
        self.tools = {
            'flake8': self._find_tool('flake8'),
            'pylint': self._find_tool('pylint'),
            'black': self._find_tool('black'),
            'mypy': self._find_tool('mypy')
        }

    async def lint(
        self,
        code: str,
        config: Optional[Dict[str, Any]] = None
    ) -> List[StyleViolation]:
        """Python 린팅"""

        violations = []

        # Flake8
        if self.tools['flake8']:
            flake8_violations = await self._run_flake8(code, config)
            violations.extend(flake8_violations)

        # Pylint (선택적)
        if config and config.get('use_pylint', False) and self.tools['pylint']:
            pylint_violations = await self._run_pylint(code, config)
            violations.extend(pylint_violations)

        # Type checking (선택적)
        if config and config.get('type_check', False) and self.tools['mypy']:
            mypy_violations = await self._run_mypy(code, config)
            violations.extend(mypy_violations)

        return violations

    async def _run_flake8(
        self,
        code: str,
        config: Optional[Dict[str, Any]]
    ) -> List[StyleViolation]:
        """Flake8 실행"""

        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False
        ) as f:
            f.write(code)
            temp_file = f.name

        try:
            cmd = [
                self.tools['flake8'],
                '--format', '%(path)s:%(row)d:%(col)d: %(code)s %(text)s',
                temp_file
            ]

            # 설정 적용
            if config:
                if 'max_line_length' in config:
                    cmd.extend(['--max-line-length', str(config['max_line_length'])])
                if 'ignore' in config:
                    cmd.extend(['--ignore', ','.join(config['ignore'])])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )

            violations = []
            for line in result.stdout.splitlines():
                # 파싱: filename:line:column: CODE message
                parts = line.split(':', 3)
                if len(parts) >= 4:
                    message_parts = parts[3].strip().split(' ', 1)
                    violations.append(
                        StyleViolation(
                            file=parts[0],
                            line=int(parts[1]),
                            column=int(parts[2]),
                            rule=message_parts[0] if message_parts else 'unknown',
                            message=message_parts[1] if len(message_parts) > 1 else '',
                            severity='error' if message_parts[0].startswith('E') else 'warning',
                            fixable=False
                        )
                    )

            return violations

        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

class CodeFormatter:
    """코드 포매터 기본 클래스"""

    async def format(
        self,
        code: str,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """코드 포맷팅"""
        raise NotImplementedError

class PythonFormatter(CodeFormatter):
    """Python 포매터"""

    def __init__(self):
        self.black_path = self._find_black()
        self.autopep8_path = self._find_autopep8()

    async def format(
        self,
        code: str,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Python 코드 포맷팅"""

        formatter = config.get('formatter', 'black') if config else 'black'

        if formatter == 'black' and self.black_path:
            return await self._format_with_black(code, config)
        elif formatter == 'autopep8' and self.autopep8_path:
            return await self._format_with_autopep8(code, config)

        return code

    async def _format_with_black(
        self,
        code: str,
        config: Optional[Dict[str, Any]]
    ) -> str:
        """Black으로 포맷팅"""

        cmd = [self.black_path, '-']

        if config:
            if 'line_length' in config:
                cmd.extend(['--line-length', str(config['line_length'])])

        result = subprocess.run(
            cmd,
            input=code,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return result.stdout

        return code
```

**검증 기준**:

- [ ] 다국어 린팅 지원
- [ ] 자동 포맷팅 기능
- [ ] 커스텀 규칙 지원
- [ ] 성능 최적화

#### SubTask 4.63.2: 보안 취약점 스캔

**담당자**: 보안 엔지니어  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/generation/security_scanner.py
from typing import Dict, List, Any, Optional, Set
import re
import ast
from dataclasses import dataclass
from enum import Enum

class VulnerabilityType(Enum):
    SQL_INJECTION = "sql_injection"
    XSS = "cross_site_scripting"
    COMMAND_INJECTION = "command_injection"
    PATH_TRAVERSAL = "path_traversal"
    INSECURE_DESERIALIZATION = "insecure_deserialization"
    HARDCODED_SECRETS = "hardcoded_secrets"
    WEAK_CRYPTO = "weak_cryptography"
    OPEN_REDIRECT = "open_redirect"
    XXE = "xml_external_entity"
    SSRF = "server_side_request_forgery"

@dataclass
class Vulnerability:
    type: VulnerabilityType
    severity: str  # 'critical', 'high', 'medium', 'low'
    file: str
    line: int
    column: int
    code_snippet: str
    description: str
    remediation: str
    cwe_id: Optional[str] = None
    owasp_category: Optional[str] = None

class SecurityScanner:
    """보안 취약점 스캐너"""

    def __init__(self):
        self.pattern_scanner = PatternBasedScanner()
        self.ast_scanner = ASTBasedScanner()
        self.dependency_scanner = DependencyScanner()
        self.secret_scanner = SecretScanner()
        self.crypto_scanner = CryptoScanner()

    async def scan_code(
        self,
        code: str,
        language: str,
        context: Optional[Dict[str, Any]] = None
    ) -> SecurityScanResult:
        """코드 보안 스캔"""

        vulnerabilities = []

        # 1. 패턴 기반 스캔
        pattern_vulns = await self.pattern_scanner.scan(code, language)
        vulnerabilities.extend(pattern_vulns)

        # 2. AST 기반 스캔 (지원되는 언어만)
        if language in ['python', 'javascript', 'typescript']:
            ast_vulns = await self.ast_scanner.scan(code, language)
            vulnerabilities.extend(ast_vulns)

        # 3. 하드코딩된 시크릿 스캔
        secret_vulns = await self.secret_scanner.scan(code)
        vulnerabilities.extend(secret_vulns)

        # 4. 암호화 관련 취약점 스캔
        crypto_vulns = await self.crypto_scanner.scan(code, language)
        vulnerabilities.extend(crypto_vulns)

        # 5. 의존성 취약점 스캔
        if context and 'dependencies' in context:
            dep_vulns = await self.dependency_scanner.scan(
                context['dependencies']
            )
            vulnerabilities.extend(dep_vulns)

        # 중복 제거 및 정렬
        unique_vulns = self._deduplicate_vulnerabilities(vulnerabilities)
        sorted_vulns = sorted(
            unique_vulns,
            key=lambda v: self._severity_score(v.severity),
            reverse=True
        )

        # 보안 점수 계산
        security_score = self._calculate_security_score(sorted_vulns)

        return SecurityScanResult(
            vulnerabilities=sorted_vulns,
            security_score=security_score,
            summary=self._generate_summary(sorted_vulns),
            recommendations=self._generate_recommendations(sorted_vulns)
        )

    def _severity_score(self, severity: str) -> int:
        """심각도 점수"""
        scores = {
            'critical': 4,
            'high': 3,
            'medium': 2,
            'low': 1
        }
        return scores.get(severity, 0)

class PatternBasedScanner:
    """패턴 기반 스캐너"""

    def __init__(self):
        self.patterns = self._load_vulnerability_patterns()

    async def scan(
        self,
        code: str,
        language: str
    ) -> List[Vulnerability]:
        """패턴 매칭 스캔"""

        vulnerabilities = []
        patterns = self.patterns.get(language, {})

        for vuln_type, pattern_list in patterns.items():
            for pattern_info in pattern_list:
                regex = pattern_info['regex']
                matches = re.finditer(regex, code, re.MULTILINE | re.IGNORECASE)

                for match in matches:
                    line_num = code[:match.start()].count('\n') + 1

                    vulnerabilities.append(
                        Vulnerability(
                            type=vuln_type,
                            severity=pattern_info['severity'],
                            file='generated_code',
                            line=line_num,
                            column=match.start() - code.rfind('\n', 0, match.start()),
                            code_snippet=self._extract_snippet(code, line_num),
                            description=pattern_info['description'],
                            remediation=pattern_info['remediation'],
                            cwe_id=pattern_info.get('cwe_id'),
                            owasp_category=pattern_info.get('owasp_category')
                        )
                    )

        return vulnerabilities

    def _load_vulnerability_patterns(self) -> Dict[str, Dict[VulnerabilityType, List[Dict]]]:
        """취약점 패턴 로드"""

        return {
            'javascript': {
                VulnerabilityType.XSS: [
                    {
                        'regex': r'\.innerHTML\s*=\s*[^`]',
                        'severity': 'high',
                        'description': 'Potential XSS vulnerability: innerHTML with non-sanitized content',
                        'remediation': 'Use textContent or sanitize HTML content before assignment',
                        'cwe_id': 'CWE-79',
                        'owasp_category': 'A03:2021'
                    },
                    {
                        'regex': r'document\.write\s*\(',
                        'severity': 'high',
                        'description': 'Potential XSS vulnerability: document.write usage',
                        'remediation': 'Use DOM manipulation methods instead of document.write',
                        'cwe_id': 'CWE-79',
                        'owasp_category': 'A03:2021'
                    }
                ],
                VulnerabilityType.SQL_INJECTION: [
                    {
                        'regex': r'query\s*\(\s*[\'"`]\s*SELECT.*\+.*[\'"`]\s*\)',
                        'severity': 'critical',
                        'description': 'Potential SQL injection: string concatenation in query',
                        'remediation': 'Use parameterized queries or prepared statements',
                        'cwe_id': 'CWE-89',
                        'owasp_category': 'A03:2021'
                    }
                ],
                VulnerabilityType.COMMAND_INJECTION: [
                    {
                        'regex': r'exec\s*\(\s*[^\'"`].*\$\{.*\}',
                        'severity': 'critical',
                        'description': 'Potential command injection vulnerability',
                        'remediation': 'Validate and sanitize all user inputs before executing commands',
                        'cwe_id': 'CWE-78',
                        'owasp_category': 'A03:2021'
                    }
                ]
            },
            'python': {
                VulnerabilityType.SQL_INJECTION: [
                    {
                        'regex': r'execute\s*\(\s*[\'"`].*%[s|d].*[\'"`]\s*%',
                        'severity': 'critical',
                        'description': 'Potential SQL injection: string formatting in query',
                        'remediation': 'Use parameterized queries with placeholders',
                        'cwe_id': 'CWE-89',
                        'owasp_category': 'A03:2021'
                    }
                ],
                VulnerabilityType.COMMAND_INJECTION: [
                    {
                        'regex': r'os\.system\s*\(',
                        'severity': 'high',
                        'description': 'Potential command injection: os.system usage',
                        'remediation': 'Use subprocess module with proper input validation',
                        'cwe_id': 'CWE-78',
                        'owasp_category': 'A03:2021'
                    }
                ],
                VulnerabilityType.INSECURE_DESERIALIZATION: [
                    {
                        'regex': r'pickle\.loads?\s*\(',
                        'severity': 'high',
                        'description': 'Insecure deserialization: pickle usage',
                        'remediation': 'Use JSON or other safe serialization formats',
                        'cwe_id': 'CWE-502',
                        'owasp_category': 'A08:2021'
                    }
                ]
            }
        }

class ASTBasedScanner:
    """AST 기반 스캐너"""

    async def scan(
        self,
        code: str,
        language: str
    ) -> List[Vulnerability]:
        """AST 분석 기반 스캔"""

        if language == 'python':
            return await self._scan_python_ast(code)
        elif language in ['javascript', 'typescript']:
            return await self._scan_js_ast(code)

        return []

    async def _scan_python_ast(self, code: str) -> List[Vulnerability]:
        """Python AST 스캔"""

        vulnerabilities = []

        try:
            tree = ast.parse(code)

            # 위험한 함수 호출 검사
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    vuln = self._check_dangerous_call(node)
                    if vuln:
                        vulnerabilities.append(vuln)

                # eval/exec 사용 검사
                elif isinstance(node, ast.Name):
                    if node.id in ['eval', 'exec']:
                        vulnerabilities.append(
                            Vulnerability(
                                type=VulnerabilityType.COMMAND_INJECTION,
                                severity='critical',
                                file='generated_code',
                                line=node.lineno,
                                column=node.col_offset,
                                code_snippet=ast.get_source_segment(code, node),
                                description=f'Dangerous function: {node.id}',
                                remediation='Avoid using eval/exec, find safer alternatives',
                                cwe_id='CWE-95'
                            )
                        )

        except SyntaxError:
            pass  # 구문 오류는 무시

        return vulnerabilities

class SecretScanner:
    """하드코딩된 시크릿 스캐너"""

    def __init__(self):
        self.patterns = {
            'api_key': re.compile(r'api[_\-]?key\s*[:=]\s*[\'"`]([a-zA-Z0-9_\-]{20,})[\'"`]', re.IGNORECASE),
            'aws_key': re.compile(r'AKIA[0-9A-Z]{16}'),
            'private_key': re.compile(r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----'),
            'password': re.compile(r'password\s*[:=]\s*[\'"`]([^\'"`]{8,})[\'"`]', re.IGNORECASE),
            'token': re.compile(r'token\s*[:=]\s*[\'"`]([a-zA-Z0-9_\-\.]{20,})[\'"`]', re.IGNORECASE),
            'jwt': re.compile(r'eyJ[a-zA-Z0-9_\-]*\.eyJ[a-zA-Z0-9_\-]*\.[a-zA-Z0-9_\-]*'),
            'github_token': re.compile(r'ghp_[a-zA-Z0-9]{36}'),
            'slack_token': re.compile(r'xox[baprs]-[0-9a-zA-Z\-]+')
        }

    async def scan(self, code: str) -> List[Vulnerability]:
        """시크릿 스캔"""

        vulnerabilities = []

        for secret_type, pattern in self.patterns.items():
            matches = pattern.finditer(code)

            for match in matches:
                line_num = code[:match.start()].count('\n') + 1

                # 테스트 코드나 예제 코드인지 확인
                if not self._is_test_or_example(code, match.start()):
                    vulnerabilities.append(
                        Vulnerability(
                            type=VulnerabilityType.HARDCODED_SECRETS,
                            severity='high',
                            file='generated_code',
                            line=line_num,
                            column=match.start() - code.rfind('\n', 0, match.start()),
                            code_snippet=self._mask_secret(match.group(0)),
                            description=f'Hardcoded {secret_type.replace("_", " ")} detected',
                            remediation='Use environment variables or secure credential storage',
                            cwe_id='CWE-798',
                            owasp_category='A07:2021'
                        )
                    )

        return vulnerabilities

    def _mask_secret(self, secret: str) -> str:
        """시크릿 마스킹"""
        if len(secret) <= 8:
            return '*' * len(secret)
        return secret[:4] + '*' * (len(secret) - 8) + secret[-4:]

class CryptoScanner:
    """암호화 취약점 스캐너"""

    def __init__(self):
        self.weak_algorithms = {
            'md5', 'sha1', 'des', 'rc4', 'rc2'
        }
        self.weak_key_sizes = {
            'rsa': 2048,  # 최소 2048 비트
            'aes': 128,   # 최소 128 비트
            'ecdsa': 256  # 최소 256 비트
        }

    async def scan(
        self,
        code: str,
        language: str
    ) -> List[Vulnerability]:
        """암호화 관련 취약점 스캔"""

        vulnerabilities = []

        # 약한 알고리즘 사용 검사
        for algo in self.weak_algorithms:
            pattern = re.compile(rf'\b{algo}\b', re.IGNORECASE)
            matches = pattern.finditer(code)

            for match in matches:
                line_num = code[:match.start()].count('\n') + 1

                vulnerabilities.append(
                    Vulnerability(
                        type=VulnerabilityType.WEAK_CRYPTO,
                        severity='medium',
                        file='generated_code',
                        line=line_num,
                        column=match.start() - code.rfind('\n', 0, match.start()),
                        code_snippet=self._extract_context(code, match),
                        description=f'Weak cryptographic algorithm: {algo.upper()}',
                        remediation='Use strong algorithms like AES-256, SHA-256, or better',
                        cwe_id='CWE-327',
                        owasp_category='A02:2021'
                    )
                )

        # 불안전한 난수 생성 검사
        insecure_random_patterns = {
            'javascript': r'Math\.random\s*\(',
            'python': r'random\.\w+\s*\('
        }

        if language in insecure_random_patterns:
            pattern = re.compile(insecure_random_patterns[language])
            matches = pattern.finditer(code)

            for match in matches:
                # 암호화 관련 컨텍스트인지 확인
                if self._is_crypto_context(code, match.start()):
                    line_num = code[:match.start()].count('\n') + 1

                    vulnerabilities.append(
                        Vulnerability(
                            type=VulnerabilityType.WEAK_CRYPTO,
                            severity='high',
                            file='generated_code',
                            line=line_num,
                            column=match.start() - code.rfind('\n', 0, match.start()),
                            code_snippet=self._extract_context(code, match),
                            description='Insecure random number generation for cryptographic use',
                            remediation='Use cryptographically secure random number generators',
                            cwe_id='CWE-338',
                            owasp_category='A02:2021'
                        )
                    )

        return vulnerabilities

    def _is_crypto_context(self, code: str, position: int) -> bool:
        """암호화 컨텍스트 확인"""

        # 주변 100자 확인
        start = max(0, position - 100)
        end = min(len(code), position + 100)
        context = code[start:end].lower()

        crypto_keywords = [
            'key', 'token', 'secret', 'password', 'salt',
            'hash', 'encrypt', 'decrypt', 'sign', 'verify'
        ]

        return any(keyword in context for keyword in crypto_keywords)

# 보안 스캔 결과 집계
@dataclass
class SecurityScanResult:
    vulnerabilities: List[Vulnerability]
    security_score: float  # 0-100
    summary: Dict[str, Any]
    recommendations: List[str]

    def to_report(self) -> str:
        """보안 리포트 생성"""

        report = []
        report.append("# Security Scan Report\n")
        report.append(f"**Security Score**: {self.security_score}/100\n")

        # 요약
        report.append("## Summary")
        report.append(f"- Total vulnerabilities: {len(self.vulnerabilities)}")
        report.append(f"- Critical: {self.summary['critical']}")
        report.append(f"- High: {self.summary['high']}")
        report.append(f"- Medium: {self.summary['medium']}")
        report.append(f"- Low: {self.summary['low']}\n")

        # 취약점 상세
        if self.vulnerabilities:
            report.append("## Vulnerabilities")

            for i, vuln in enumerate(self.vulnerabilities, 1):
                report.append(f"\n### {i}. {vuln.type.value}")
                report.append(f"- **Severity**: {vuln.severity}")
                report.append(f"- **Location**: Line {vuln.line}")
                report.append(f"- **Description**: {vuln.description}")
                report.append(f"- **Remediation**: {vuln.remediation}")
                if vuln.cwe_id:
                    report.append(f"- **CWE**: {vuln.cwe_id}")
                if vuln.owasp_category:
                    report.append(f"- **OWASP**: {vuln.owasp_category}")

        # 권장사항
        if self.recommendations:
            report.append("\n## Recommendations")
            for rec in self.recommendations:
                report.append(f"- {rec}")

        return '\n'.join(report)
```

**검증 기준**:

- [ ] 주요 취약점 패턴 검사
- [ ] AST 기반 심층 분석
- [ ] 하드코딩된 시크릿 탐지
- [ ] 보안 점수 및 리포트

#### SubTask 4.63.3: 성능 최적화

**담당자**: 성능 엔지니어  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/generation/performance_optimizer.py
from typing import Dict, List, Any, Optional, Tuple
import ast
import re
from dataclasses import dataclass

@dataclass
class PerformanceIssue:
    type: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    file: str
    line: int
    description: str
    impact: str
    suggestion: str
    estimated_improvement: Optional[str] = None

@dataclass
class OptimizationResult:
    original_code: str
    optimized_code: str
    issues_found: List[PerformanceIssue]
    improvements: List[str]
    performance_score: float
    metrics: Dict[str, Any]

class PerformanceOptimizer:
    """성능 최적화기"""

    def __init__(self):
        self.code_analyzer = CodeComplexityAnalyzer()
        self.loop_optimizer = LoopOptimizer()
        self.memory_optimizer = MemoryOptimizer()
        self.async_optimizer = AsyncOptimizer()
        self.cache_optimizer = CacheOptimizer()
        self.query_optimizer = QueryOptimizer()

    async def optimize_code(
        self,
        code: str,
        language: str,
        framework: Optional[str] = None,
        target_metrics: Optional[Dict[str, Any]] = None
    ) -> OptimizationResult:
        """코드 성능 최적화"""

        issues = []
        optimized_code = code

        # 1. 코드 복잡도 분석
        complexity_issues = await self.code_analyzer.analyze(code, language)
        issues.extend(complexity_issues)

        # 2. 루프 최적화
        loop_result = await self.loop_optimizer.optimize(optimized_code, language)
        optimized_code = loop_result.optimized_code
        issues.extend(loop_result.issues)

        # 3. 메모리 최적화
        memory_result = await self.memory_optimizer.optimize(optimized_code, language)
        optimized_code = memory_result.optimized_code
        issues.extend(memory_result.issues)

        # 4. 비동기 최적화
        if language in ['javascript', 'typescript', 'python']:
            async_result = await self.async_optimizer.optimize(optimized_code, language)
            optimized_code = async_result.optimized_code
            issues.extend(async_result.issues)

        # 5. 캐싱 기회 식별
        cache_opportunities = await self.cache_optimizer.analyze(optimized_code, language)
        issues.extend(cache_opportunities)

        # 6. 쿼리 최적화 (해당되는 경우)
        if self._contains_database_queries(optimized_code):
            query_issues = await self.query_optimizer.analyze(optimized_code, language)
            issues.extend(query_issues)

        # 성능 점수 계산
        performance_score = self._calculate_performance_score(
            code,
            optimized_code,
            issues
        )

        # 개선사항 목록
        improvements = self._extract_improvements(code, optimized_code)

        # 메트릭 수집
        metrics = await self._collect_metrics(code, optimized_code, language)

        return OptimizationResult(
            original_code=code,
            optimized_code=optimized_code,
            issues_found=issues,
            improvements=improvements,
            performance_score=performance_score,
            metrics=metrics
        )

    def _calculate_performance_score(
        self,
        original: str,
        optimized: str,
        issues: List[PerformanceIssue]
    ) -> float:
        """성능 점수 계산"""

        base_score = 100.0

        # 이슈별 감점
        severity_penalty = {
            'critical': 20,
            'high': 10,
            'medium': 5,
            'low': 2
        }

        for issue in issues:
            base_score -= severity_penalty.get(issue.severity, 0)

        # 코드 개선도 가산점
        if len(optimized) < len(original) * 0.9:  # 10% 이상 코드 감소
            base_score += 5

        return max(0, min(100, base_score))

class LoopOptimizer:
    """루프 최적화기"""

    async def optimize(
        self,
        code: str,
        language: str
    ) -> LoopOptimizationResult:
        """루프 최적화"""

        issues = []
        optimized_code = code

        if language == 'python':
            optimized_code, py_issues = await self._optimize_python_loops(code)
            issues.extend(py_issues)
        elif language in ['javascript', 'typescript']:
            optimized_code, js_issues = await self._optimize_js_loops(code)
            issues.extend(js_issues)

        return LoopOptimizationResult(
            optimized_code=optimized_code,
            issues=issues
        )

    async def _optimize_python_loops(
        self,
        code: str
    ) -> Tuple[str, List[PerformanceIssue]]:
        """Python 루프 최적화"""

        issues = []

        try:
            tree = ast.parse(code)
            optimizer = PythonLoopOptimizer()
            optimized_tree = optimizer.visit(tree)

            # 최적화 이슈 수집
            issues = optimizer.get_issues()

            # 코드 재생성
            optimized_code = ast.unparse(optimized_tree)

            return optimized_code, issues
        except:
            return code, issues

class PythonLoopOptimizer(ast.NodeTransformer):
    """Python AST 기반 루프 최적화"""

    def __init__(self):
        self.issues = []
        self.current_line = 0

    def visit_For(self, node: ast.For) -> ast.For:
        """For 루프 최적화"""

        # range(len(x)) 패턴 감지
        if (isinstance(node.iter, ast.Call) and
            isinstance(node.iter.func, ast.Name) and
            node.iter.func.id == 'range' and
            len(node.iter.args) == 1 and
            isinstance(node.iter.args[0], ast.Call) and
            isinstance(node.iter.args[0].func, ast.Name) and
            node.iter.args[0].func.id == 'len'):

            # enumerate 사용 제안
            self.issues.append(
                PerformanceIssue(
                    type='inefficient_loop',
                    severity='medium',
                    file='generated_code',
                    line=node.lineno,
                    description='Using range(len(x)) pattern',
                    impact='Slower iteration and less readable code',
                    suggestion='Use enumerate() for index and value access',
                    estimated_improvement='10-20% faster'
                )
            )

        # 루프 내 불필요한 함수 호출 감지
        self._check_loop_invariants(node)

        self.generic_visit(node)
        return node

    def _check_loop_invariants(self, node: ast.For):
        """루프 불변식 검사"""

        invariant_calls = []

        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                # 루프 변수를 사용하지 않는 함수 호출 찾기
                if not self._uses_loop_variable(child, node.target):
                    invariant_calls.append(child)

        if invariant_calls:
            self.issues.append(
                PerformanceIssue(
                    type='loop_invariant',
                    severity='high',
                    file='generated_code',
                    line=node.lineno,
                    description='Function calls inside loop that don\'t depend on loop variable',
                    impact='Unnecessary repeated computation',
                    suggestion='Move invariant computations outside the loop',
                    estimated_improvement='Depends on loop size, can be significant'
                )
            )

class MemoryOptimizer:
    """메모리 최적화기"""

    async def optimize(
        self,
        code: str,
        language: str
    ) -> MemoryOptimizationResult:
        """메모리 사용 최적화"""

        issues = []
        optimized_code = code

        # 대용량 데이터 구조 감지
        large_data_issues = self._detect_large_data_structures(code, language)
        issues.extend(large_data_issues)

        # 메모리 누수 가능성 감지
        leak_issues = self._detect_memory_leaks(code, language)
        issues.extend(leak_issues)

        # 불필요한 복사 감지
        copy_issues = self._detect_unnecessary_copies(code, language)
        issues.extend(copy_issues)

        return MemoryOptimizationResult(
            optimized_code=optimized_code,
            issues=issues
        )

    def _detect_large_data_structures(
        self,
        code: str,
        language: str
    ) -> List[PerformanceIssue]:
        """대용량 데이터 구조 감지"""

        issues = []

        # 전체 파일을 메모리에 로드하는 패턴
        file_load_patterns = {
            'python': r'\.read\(\s*\)|\.readlines\(\s*\)',
            'javascript': r'readFileSync|\.toString\(\s*\)'
        }

        if language in file_load_patterns:
            pattern = re.compile(file_load_patterns[language])
            matches = pattern.finditer(code)

            for match in matches:
                line_num = code[:match.start()].count('\n') + 1

                issues.append(
                    PerformanceIssue(
                        type='memory_inefficient',
                        severity='high',
                        file='generated_code',
                        line=line_num,
                        description='Loading entire file into memory',
                        impact='High memory usage for large files',
                        suggestion='Use streaming or chunked reading for large files',
                        estimated_improvement='90% memory reduction for large files'
                    )
                )

        return issues

class AsyncOptimizer:
    """비동기 최적화기"""

    async def optimize(
        self,
        code: str,
        language: str
    ) -> AsyncOptimizationResult:
        """비동기 코드 최적화"""

        issues = []
        optimized_code = code

        # 동기 I/O 감지
        sync_io_issues = self._detect_sync_io(code, language)
        issues.extend(sync_io_issues)

        # 비효율적인 await 사용 감지
        await_issues = self._detect_inefficient_awaits(code, language)
        issues.extend(await_issues)

        # 병렬화 기회 감지
        parallel_opportunities = self._detect_parallelization_opportunities(code, language)
        issues.extend(parallel_opportunities)

        return AsyncOptimizationResult(
            optimized_code=optimized_code,
            issues=issues
        )

    def _detect_sync_io(
        self,
        code: str,
        language: str
    ) -> List[PerformanceIssue]:
        """동기 I/O 작업 감지"""

        issues = []

        sync_io_patterns = {
            'javascript': {
                'fs.readFileSync': 'Use fs.readFile or fs.promises.readFile',
                'fs.writeFileSync': 'Use fs.writeFile or fs.promises.writeFile',
                'child_process.execSync': 'Use child_process.exec with promises'
            },
            'python': {
                'requests.get': 'Use aiohttp or httpx for async requests',
                'open(': 'Use aiofiles for async file operations',
                'time.sleep': 'Use asyncio.sleep in async functions'
            }
        }

        if language in sync_io_patterns:
            for pattern, suggestion in sync_io_patterns[language].items():
                regex = re.compile(re.escape(pattern))
                matches = regex.finditer(code)

                for match in matches:
                    line_num = code[:match.start()].count('\n') + 1

                    issues.append(
                        PerformanceIssue(
                            type='blocking_io',
                            severity='high',
                            file='generated_code',
                            line=line_num,
                            description=f'Synchronous I/O operation: {pattern}',
                            impact='Blocks event loop, reduces concurrency',
                            suggestion=suggestion,
                            estimated_improvement='10-100x throughput for I/O bound operations'
                        )
                    )

        return issues

class CacheOptimizer:
    """캐싱 최적화기"""

    async def analyze(
        self,
        code: str,
        language: str
    ) -> List[PerformanceIssue]:
        """캐싱 기회 분석"""

        issues = []

        # 반복적인 계산 감지
        repeated_calculations = self._detect_repeated_calculations(code, language)
        issues.extend(repeated_calculations)

        # 캐시 가능한 API 호출 감지
        cacheable_calls = self._detect_cacheable_api_calls(code, language)
        issues.extend(cacheable_calls)

        # 메모이제이션 기회 감지
        memoization_opportunities = self._detect_memoization_opportunities(code, language)
        issues.extend(memoization_opportunities)

        return issues

    def _detect_repeated_calculations(
        self,
        code: str,
        language: str
    ) -> List[PerformanceIssue]:
        """반복 계산 감지"""

        issues = []

        # 동일한 함수 호출 패턴 찾기
        function_calls = re.findall(r'(\w+)\s*\([^)]*\)', code)
        call_counts = {}

        for call in function_calls:
            call_counts[call] = call_counts.get(call, 0) + 1

        # 3번 이상 호출되는 함수
        for call, count in call_counts.items():
            if count >= 3:
                issues.append(
                    PerformanceIssue(
                        type='repeated_calculation',
                        severity='medium',
                        file='generated_code',
                        line=0,  # 전체 파일 레벨 이슈
                        description=f'Function {call} called {count} times',
                        impact='Redundant computation',
                        suggestion='Consider caching results if inputs are the same',
                        estimated_improvement=f'{(count-1)/count*100:.0f}% reduction in computation'
                    )
                )

        return issues
```

**검증 기준**:

- [ ] 루프 최적화
- [ ] 메모리 사용 최적화
- [ ] 비동기 코드 개선
- [ ] 캐싱 전략 제안

#### SubTask 4.63.4: 코드 리뷰 자동화

**담당자**: 시니어 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

````python
# backend/src/agents/implementations/generation/code_review_automation.py
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio

class ReviewCategory(Enum):
    CODE_QUALITY = "code_quality"
    BEST_PRACTICES = "best_practices"
    MAINTAINABILITY = "maintainability"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    SECURITY = "security"
    PERFORMANCE = "performance"
    DESIGN_PATTERNS = "design_patterns"

@dataclass
class ReviewComment:
    category: ReviewCategory
    severity: str  # 'blocker', 'critical', 'major', 'minor', 'info'
    file: str
    line: int
    end_line: Optional[int]
    comment: str
    suggestion: Optional[str]
    code_example: Optional[str]
    references: List[str]

@dataclass
class CodeReviewResult:
    passed: bool
    score: float
    comments: List[ReviewComment]
    summary: Dict[str, Any]
    metrics: Dict[str, float]
    action_items: List[str]

class AutomatedCodeReviewer:
    """자동화된 코드 리뷰어"""

    def __init__(self):
        self.quality_reviewer = CodeQualityReviewer()
        self.best_practices_reviewer = BestPracticesReviewer()
        self.maintainability_reviewer = MaintainabilityReviewer()
        self.documentation_reviewer = DocumentationReviewer()
        self.testing_reviewer = TestingReviewer()
        self.design_pattern_reviewer = DesignPatternReviewer()

    async def review_code(
        self,
        code: str,
        language: str,
        context: Optional[Dict[str, Any]] = None,
        review_config: Optional[Dict[str, Any]] = None
    ) -> CodeReviewResult:
        """코드 리뷰 수행"""

        all_comments = []

        # 1. 코드 품질 리뷰
        quality_comments = await self.quality_reviewer.review(code, language)
        all_comments.extend(quality_comments)

        # 2. 베스트 프랙티스 리뷰
        best_practices_comments = await self.best_practices_reviewer.review(
            code,
            language,
            context
        )
        all_comments.extend(best_practices_comments)

        # 3. 유지보수성 리뷰
        maintainability_comments = await self.maintainability_reviewer.review(
            code,
            language
        )
        all_comments.extend(maintainability_comments)

        # 4. 문서화 리뷰
        doc_comments = await self.documentation_reviewer.review(code, language)
        all_comments.extend(doc_comments)

        # 5. 테스트 관련 리뷰
        if context and context.get('has_tests'):
            test_comments = await self.testing_reviewer.review(
                code,
                language,
                context.get('test_code')
            )
            all_comments.extend(test_comments)

        # 6. 디자인 패턴 리뷰
        pattern_comments = await self.design_pattern_reviewer.review(
            code,
            language,
            context
        )
        all_comments.extend(pattern_comments)

        # 리뷰 결과 집계
        review_result = self._aggregate_review_results(
            all_comments,
            code,
            language
        )

        return review_result

    def _aggregate_review_results(
        self,
        comments: List[ReviewComment],
        code: str,
        language: str
    ) -> CodeReviewResult:
        """리뷰 결과 집계"""

        # 심각도별 분류
        severity_counts = {
            'blocker': 0,
            'critical': 0,
            'major': 0,
            'minor': 0,
            'info': 0
        }

        category_counts = {}

        for comment in comments:
            severity_counts[comment.severity] += 1
            category_counts[comment.category.value] = \
                category_counts.get(comment.category.value, 0) + 1

        # 점수 계산
        score = self._calculate_review_score(severity_counts)

        # 통과 여부
        passed = severity_counts['blocker'] == 0 and severity_counts['critical'] == 0

        # 요약 생성
        summary = {
            'total_comments': len(comments),
            'severity_breakdown': severity_counts,
            'category_breakdown': category_counts,
            'lines_of_code': len(code.splitlines()),
            'comment_density': len(comments) / max(len(code.splitlines()), 1)
        }

        # 메트릭 계산
        metrics = self._calculate_code_metrics(code, comments, language)

        # 액션 아이템 생성
        action_items = self._generate_action_items(comments)

        return CodeReviewResult(
            passed=passed,
            score=score,
            comments=sorted(comments, key=lambda c: self._severity_priority(c.severity)),
            summary=summary,
            metrics=metrics,
            action_items=action_items
        )

    def _calculate_review_score(self, severity_counts: Dict[str, int]) -> float:
        """리뷰 점수 계산"""

        # 100점에서 감점
        score = 100.0

        penalties = {
            'blocker': 25,
            'critical': 15,
            'major': 8,
            'minor': 3,
            'info': 0
        }

        for severity, count in severity_counts.items():
            score -= penalties[severity] * count

        return max(0, score)

    def _severity_priority(self, severity: str) -> int:
        """심각도 우선순위"""

        priorities = {
            'blocker': 0,
            'critical': 1,
            'major': 2,
            'minor': 3,
            'info': 4
        }
        return priorities.get(severity, 5)

class CodeQualityReviewer:
    """코드 품질 리뷰어"""

    async def review(
        self,
        code: str,
        language: str
    ) -> List[ReviewComment]:
        """코드 품질 리뷰"""

        comments = []

        # 함수 길이 검사
        function_length_comments = self._check_function_length(code, language)
        comments.extend(function_length_comments)

        # 변수명 검사
        naming_comments = self._check_naming_conventions(code, language)
        comments.extend(naming_comments)

        # 중복 코드 검사
        duplication_comments = self._check_code_duplication(code, language)
        comments.extend(duplication_comments)

        # 복잡도 검사
        complexity_comments = self._check_complexity(code, language)
        comments.extend(complexity_comments)

        return comments

    def _check_function_length(
        self,
        code: str,
        language: str
    ) -> List[ReviewComment]:
        """함수 길이 검사"""

        comments = []

        # 언어별 함수 패턴
        function_patterns = {
            'python': r'def\s+(\w+)\s*\([^)]*\):',
            'javascript': r'function\s+(\w+)\s*\([^)]*\)|(\w+)\s*=\s*\([^)]*\)\s*=>',
            'java': r'(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\([^)]*\)'
        }

        if language in function_patterns:
            pattern = re.compile(function_patterns[language], re.MULTILINE)

            # 함수 찾기 및 길이 계산
            for match in pattern.finditer(code):
                func_name = match.group(1) or match.group(2)
                start_line = code[:match.start()].count('\n') + 1

                # 함수 종료 지점 찾기 (간단한 휴리스틱)
                func_body = self._extract_function_body(code[match.end():], language)
                func_lines = func_body.count('\n')

                if func_lines > 50:
                    comments.append(
                        ReviewComment(
                            category=ReviewCategory.CODE_QUALITY,
                            severity='major',
                            file='generated_code',
                            line=start_line,
                            end_line=start_line + func_lines,
                            comment=f'Function {func_name} is too long ({func_lines} lines)',
                            suggestion='Consider breaking this function into smaller, focused functions',
                            code_example=None,
                            references=['Clean Code by Robert C. Martin']
                        )
                    )

        return comments

class BestPracticesReviewer:
    """베스트 프랙티스 리뷰어"""

    def __init__(self):
        self.practices_db = self._load_best_practices()

    async def review(
        self,
        code: str,
        language: str,
        context: Optional[Dict[str, Any]]
    ) -> List[ReviewComment]:
        """베스트 프랙티스 리뷰"""

        comments = []

        # 언어별 베스트 프랙티스 검사
        if language in self.practices_db:
            for practice in self.practices_db[language]:
                violations = self._check_practice(code, practice)
                comments.extend(violations)

        # 프레임워크별 검사
        if context and 'framework' in context:
            framework = context['framework']
            if framework in self.practices_db.get('frameworks', {}):
                for practice in self.practices_db['frameworks'][framework]:
                    violations = self._check_practice(code, practice)
                    comments.extend(violations)

        return comments

    def _load_best_practices(self) -> Dict[str, List[Dict]]:
        """베스트 프랙티스 규칙 로드"""

        return {
            'python': [
                {
                    'name': 'use_list_comprehension',
                    'pattern': r'for\s+\w+\s+in\s+.*:\s*\n\s*\w+\.append\(',
                    'severity': 'minor',
                    'comment': 'Consider using list comprehension for better readability and performance',
                    'example': '[item for item in items if condition]'
                },
                {
                    'name': 'avoid_mutable_defaults',
                    'pattern': r'def\s+\w+\s*\([^)]*=\s*(?:\[\]|\{\})',
                    'severity': 'major',
                    'comment': 'Avoid mutable default arguments',
                    'example': 'def func(items=None):\n    if items is None:\n        items = []'
                }
            ],
            'javascript': [
                {
                    'name': 'use_const_let',
                    'pattern': r'\bvar\s+',
                    'severity': 'minor',
                    'comment': 'Use const or let instead of var',
                    'example': 'const value = 42; // or let if reassignment needed'
                },
                {
                    'name': 'avoid_callback_hell',
                    'pattern': r'}\s*\)\s*}\s*\)\s*}\s*\)',  # Nested callbacks
                    'severity': 'major',
                    'comment': 'Deeply nested callbacks detected. Consider using async/await',
                    'example': 'async function doWork() {\n  const result = await asyncOperation();\n}'
                }
            ]
        }

class DocumentationReviewer:
    """문서화 리뷰어"""

    async def review(
        self,
        code: str,
        language: str
    ) -> List[ReviewComment]:
        """문서화 리뷰"""

        comments = []

        # 함수 문서화 검사
        undocumented_functions = self._find_undocumented_functions(code, language)
        for func in undocumented_functions:
            comments.append(
                ReviewComment(
                    category=ReviewCategory.DOCUMENTATION,
                    severity='major',
                    file='generated_code',
                    line=func['line'],
                    end_line=None,
                    comment=f'Function {func["name"]} lacks documentation',
                    suggestion='Add docstring/JSDoc comment describing purpose, parameters, and return value',
                    code_example=self._generate_doc_example(func['name'], language),
                    references=['PEP 257', 'JSDoc documentation']
                )
            )

        # 복잡한 로직 문서화 검사
        complex_logic_comments = self._check_complex_logic_documentation(code, language)
        comments.extend(complex_logic_comments)

        # TODO/FIXME 주석 검사
        todo_comments = self._check_todo_comments(code)
        comments.extend(todo_comments)

        return comments

    def _generate_doc_example(self, func_name: str, language: str) -> str:
        """문서화 예제 생성"""

        if language == 'python':
            return f'''"""
Brief description of {func_name}.

Args:
    param1: Description of first parameter
    param2: Description of second parameter

Returns:
    Description of return value

Raises:
    ExceptionType: Description of when this exception is raised
"""'''
        elif language in ['javascript', 'typescript']:
            return f'''/**
 * Brief description of {func_name}.
 *
 * @param {{type}} param1 - Description of first parameter
 * @param {{type}} param2 - Description of second parameter
 * @returns {{type}} Description of return value
 * @throws {{Error}} Description of when this error is thrown
 */'''

        return ''

# 리뷰 리포트 생성기
class ReviewReportGenerator:
    """리뷰 리포트 생성기"""

    def generate_report(
        self,
        review_result: CodeReviewResult,
        format: str = 'markdown'
    ) -> str:
        """리뷰 리포트 생성"""

        if format == 'markdown':
            return self._generate_markdown_report(review_result)
        elif format == 'html':
            return self._generate_html_report(review_result)
        elif format == 'json':
            return self._generate_json_report(review_result)

        raise ValueError(f"Unsupported format: {format}")

    def _generate_markdown_report(self, result: CodeReviewResult) -> str:
        """Markdown 리포트 생성"""

        report = []

        # 헤더
        report.append("# Code Review Report")
        report.append(f"\n**Score**: {result.score}/100")
        report.append(f"**Status**: {'✅ PASSED' if result.passed else '❌ FAILED'}")

        # 요약
        report.append("\n## Summary")
        report.append(f"- Total comments: {result.summary['total_comments']}")
        report.append(f"- Lines of code: {result.summary['lines_of_code']}")

        # 심각도별 분류
        report.append("\n### Severity Breakdown")
        for severity, count in result.summary['severity_breakdown'].items():
            if count > 0:
                emoji = {
                    'blocker': '🚫',
                    'critical': '🔴',
                    'major': '🟠',
                    'minor': '🟡',
                    'info': 'ℹ️'
                }.get(severity, '')
                report.append(f"- {emoji} **{severity.upper()}**: {count}")

        # 주요 액션 아이템
        if result.action_items:
            report.append("\n## Action Items")
            for i, item in enumerate(result.action_items[:5], 1):  # Top 5
                report.append(f"{i}. {item}")

        # 상세 코멘트
        if result.comments:
            report.append("\n## Detailed Comments")

            current_category = None
            for comment in result.comments:
                if comment.category != current_category:
                    current_category = comment.category
                    report.append(f"\n### {comment.category.value.replace('_', ' ').title()}")

                severity_badge = f"[{comment.severity.upper()}]"
                report.append(f"\n**{severity_badge}** Line {comment.line}: {comment.comment}")

                if comment.suggestion:
                    report.append(f"  \n  💡 **Suggestion**: {comment.suggestion}")

                if comment.code_example:
                    report.append(f"  \n  **Example**:")
                    report.append(f"  ```{self._get_language_for_highlight(comment.file)}")
                    report.append(f"  {comment.code_example}")
                    report.append("  ```")

        return '\n'.join(report)
````

**검증 기준**:

- [ ] 다차원 코드 리뷰
- [ ] 구체적인 개선 제안
- [ ] 우선순위 기반 액션 아이템
- [ ] 다양한 리포트 형식

---

### Task 4.64: 테스트 코드 생성

#### SubTask 4.64.1: 단위 테스트 생성기

**담당자**: 테스트 엔지니어  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/generation/unit_test_generator.py
from typing import Dict, List, Any, Optional, Tuple
import ast
import re
from dataclasses import dataclass

@dataclass
class TestCase:
    name: str
    description: str
    test_type: str  # 'positive', 'negative', 'edge_case', 'boundary'
    input_data: Dict[str, Any]
    expected_output: Any
    expected_exception: Optional[str] = None
    setup_code: Optional[str] = None
    teardown_code: Optional[str] = None
    assertions: List[str] = None

@dataclass
class TestSuite:
    target_file: str
    target_class: Optional[str]
    target_function: Optional[str]
    test_cases: List[TestCase]
    imports: List[str]
    fixtures: List[Dict[str, Any]]
    test_framework: str

class UnitTestGenerator:
    """단위 테스트 생성기"""

    def __init__(self):
        self.test_case_generator = TestCaseGenerator()
        self.assertion_builder = AssertionBuilder()
        self.fixture_generator = FixtureGenerator()
        self.mock_generator = MockGenerator()
        self.test_data_generator = TestDataGenerator()

    async def generate_unit_tests(
        self,
        code: str,
        language: str,
        test_framework: Optional[str] = None,
        coverage_target: float = 0.8
    ) -> List[TestSuite]:
        """단위 테스트 생성"""

        test_suites = []

        # 1. 코드 분석
        analysis_result = await self._analyze_code(code, language)

        # 2. 테스트 대상 식별
        test_targets = self._identify_test_targets(analysis_result)

        # 3. 각 대상에 대한 테스트 생성
        for target in test_targets:
            # 테스트 케이스 생성
            test_cases = await self.test_case_generator.generate_cases(
                target,
                coverage_target
            )

            # 픽스처 생성
            fixtures = await self.fixture_generator.generate_fixtures(
                target,
                test_cases
            )

            # 목 객체 생성
            mocks = await self.mock_generator.generate_mocks(target)

            # 테스트 스위트 구성
            test_suite = TestSuite(
                target_file=target.file,
                target_class=target.class_name,
                target_function=target.function_name,
                test_cases=test_cases,
                imports=self._generate_imports(language, test_framework),
                fixtures=fixtures,
                test_framework=test_framework or self._default_framework(language)
            )

            test_suites.append(test_suite)

        return test_suites

    async def _analyze_code(
        self,
        code: str,
        language: str
    ) -> CodeAnalysisResult:
        """코드 분석"""

        if language == 'python':
            return await self._analyze_python_code(code)
        elif language in ['javascript', 'typescript']:
            return await self._analyze_js_code(code)
        elif language == 'java':
            return await self._analyze_java_code(code)
        else:
            raise ValueError(f"Unsupported language: {language}")

    async def _analyze_python_code(self, code: str) -> CodeAnalysisResult:
        """Python 코드 분석"""

        tree = ast.parse(code)

        functions = []
        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = {
                    'name': node.name,
                    'args': self._extract_function_args(node),
                    'returns': self._extract_return_type(node),
                    'docstring': ast.get_docstring(node),
                    'complexity': self._calculate_complexity(node),
                    'dependencies': self._extract_dependencies(node)
                }
                functions.append(func_info)

            elif isinstance(node, ast.ClassDef):
                class_info = {
                    'name': node.name,
                    'methods': self._extract_class_methods(node),
                    'attributes': self._extract_class_attributes(node),
                    'docstring': ast.get_docstring(node),
                    'base_classes': [base.id for base in node.bases if isinstance(base, ast.Name)]
                }
                classes.append(class_info)

        return CodeAnalysisResult(
            functions=functions,
            classes=classes,
            imports=self._extract_imports(tree),
            global_vars=self._extract_global_vars(tree)
        )

class TestCaseGenerator:
    """테스트 케이스 생성기"""

    async def generate_cases(
        self,
        target: TestTarget,
        coverage_target: float
    ) -> List[TestCase]:
        """테스트 케이스 생성"""

        test_cases = []

        # 1. 정상 케이스 생성
        positive_cases = await self._generate_positive_cases(target)
        test_cases.extend(positive_cases)

        # 2. 엣지 케이스 생성
        edge_cases = await self._generate_edge_cases(target)
        test_cases.extend(edge_cases)

        # 3. 에러 케이스 생성
        error_cases = await self._generate_error_cases(target)
        test_cases.extend(error_cases)

        # 4. 경계값 테스트 생성
        boundary_cases = await self._generate_boundary_cases(target)
        test_cases.extend(boundary_cases)

        # 5. 커버리지 기반 추가 케이스
        if self._calculate_coverage(test_cases, target) < coverage_target:
            additional_cases = await self._generate_coverage_cases(
                target,
                test_cases,
                coverage_target
            )
            test_cases.extend(additional_cases)

        return test_cases

    async def _generate_positive_cases(
        self,
        target: TestTarget
    ) -> List[TestCase]:
        """정상 동작 테스트 케이스"""

        cases = []

        # 함수 시그니처 분석
        if target.function_info:
            func = target.function_info

            # 기본 정상 케이스
            basic_case = TestCase(
                name=f"test_{func['name']}_basic",
                description=f"Test {func['name']} with valid basic input",
                test_type='positive',
                input_data=self._generate_basic_input(func['args']),
                expected_output=self._infer_expected_output(func),
                assertions=self._generate_basic_assertions(func)
            )
            cases.append(basic_case)

            # 다양한 유효 입력 케이스
            for i, variant in enumerate(self._generate_input_variants(func['args'])):
                variant_case = TestCase(
                    name=f"test_{func['name']}_variant_{i+1}",
                    description=f"Test {func['name']} with valid variant input #{i+1}",
                    test_type='positive',
                    input_data=variant,
                    expected_output=self._infer_expected_output(func, variant),
                    assertions=self._generate_variant_assertions(func, variant)
                )
                cases.append(variant_case)

        return cases

    def _generate_basic_input(self, args: List[Dict]) -> Dict[str, Any]:
        """기본 입력값 생성"""

        input_data = {}

        for arg in args:
            arg_name = arg['name']
            arg_type = arg.get('type', 'Any')

            # 타입별 기본값 생성
            if arg_type == 'str':
                input_data[arg_name] = "test_string"
            elif arg_type == 'int':
                input_data[arg_name] = 42
            elif arg_type == 'float':
                input_data[arg_name] = 3.14
            elif arg_type == 'bool':
                input_data[arg_name] = True
            elif arg_type == 'list':
                input_data[arg_name] = [1, 2, 3]
            elif arg_type == 'dict':
                input_data[arg_name] = {"key": "value"}
            else:
                input_data[arg_name] = None

        return input_data

class TestCodeFormatter:
    """테스트 코드 포매터"""

    def format_test_suite(
        self,
        test_suite: TestSuite,
        language: str
    ) -> str:
        """테스트 스위트를 코드로 변환"""

        if language == 'python':
            return self._format_python_tests(test_suite)
        elif language in ['javascript', 'typescript']:
            return self._format_js_tests(test_suite)
        elif language == 'java':
            return self._format_java_tests(test_suite)

    def _format_python_tests(self, test_suite: TestSuite) -> str:
        """Python 테스트 코드 생성"""

        code_parts = []

        # 임포트
        imports = [
            "import unittest",
            "from unittest.mock import Mock, patch, MagicMock",
            f"from {test_suite.target_file} import {test_suite.target_class or test_suite.target_function}"
        ]
        code_parts.append('\n'.join(imports))

        # 픽스처
        if test_suite.fixtures:
            code_parts.append("\n# Test Fixtures")
            for fixture in test_suite.fixtures:
                code_parts.append(self._format_fixture(fixture))

        # 테스트 클래스
        class_name = f"Test{test_suite.target_class or test_suite.target_function}"
        code_parts.append(f"\n\nclass {class_name}(unittest.TestCase):")

        # setUp/tearDown
        code_parts.append("    def setUp(self):")
        code_parts.append("        # Test setup")
        code_parts.append("        pass")

        # 각 테스트 케이스
        for test_case in test_suite.test_cases:
            code_parts.append(f"\n    def {test_case.name}(self):")
            code_parts.append(f'        """')
            code_parts.append(f'        {test_case.description}')
            code_parts.append(f'        """')

            # Setup
            if test_case.setup_code:
                code_parts.append(f"        # Setup")
                code_parts.append(f"        {test_case.setup_code}")

            # Arrange
            code_parts.append(f"        # Arrange")
            for param, value in test_case.input_data.items():
                code_parts.append(f"        {param} = {repr(value)}")

            # Act
            code_parts.append(f"\n        # Act")
            if test_suite.target_class:
                code_parts.append(f"        instance = {test_suite.target_class}()")
                code_parts.append(f"        result = instance.{test_suite.target_function}({', '.join(test_case.input_data.keys())})")
            else:
                code_parts.append(f"        result = {test_suite.target_function}({', '.join(test_case.input_data.keys())})")

            # Assert
            code_parts.append(f"\n        # Assert")
            if test_case.expected_exception:
                code_parts.append(f"        with self.assertRaises({test_case.expected_exception}):")
                code_parts.append(f"            # Re-run the function call")
            else:
                for assertion in test_case.assertions:
                    code_parts.append(f"        {assertion}")

            # Teardown
            if test_case.teardown_code:
                code_parts.append(f"\n        # Teardown")
                code_parts.append(f"        {test_case.teardown_code}")

        # Main
        code_parts.append("\n\nif __name__ == '__main__':")
        code_parts.append("    unittest.main()")

        return '\n'.join(code_parts)

    def _format_js_tests(self, test_suite: TestSuite) -> str:
        """JavaScript/TypeScript 테스트 코드 생성"""

        framework = test_suite.test_framework

        if framework == 'jest':
            return self._format_jest_tests(test_suite)
        elif framework == 'mocha':
            return self._format_mocha_tests(test_suite)
        else:
            return self._format_jest_tests(test_suite)  # 기본값

    def _format_jest_tests(self, test_suite: TestSuite) -> str:
        """Jest 테스트 코드 생성"""

        code_parts = []

        # 임포트
        imports = []
        if test_suite.target_class:
            imports.append(f"import {{ {test_suite.target_class} }} from './{test_suite.target_file}';")
        else:
            imports.append(f"import {{ {test_suite.target_function} }} from './{test_suite.target_file}';")

        code_parts.append('\n'.join(imports))

        # 테스트 describe 블록
        describe_name = test_suite.target_class or test_suite.target_function
        code_parts.append(f"\ndescribe('{describe_name}', () => {{")

        # beforeEach/afterEach
        code_parts.append("  beforeEach(() => {")
        code_parts.append("    // Test setup")
        code_parts.append("  });")

        # 각 테스트 케이스
        for test_case in test_suite.test_cases:
            code_parts.append(f"\n  it('{test_case.description}', () => {{")

            # Arrange
            code_parts.append("    // Arrange")
            for param, value in test_case.input_data.items():
                code_parts.append(f"    const {param} = {self._js_value(value)};")

            # Act
            code_parts.append("\n    // Act")
            if test_suite.target_class:
                code_parts.append(f"    const instance = new {test_suite.target_class}();")
                code_parts.append(f"    const result = instance.{test_suite.target_function}({', '.join(test_case.input_data.keys())});")
            else:
                code_parts.append(f"    const result = {test_suite.target_function}({', '.join(test_case.input_data.keys())});")

            # Assert
            code_parts.append("\n    // Assert")
            if test_case.expected_exception:
                code_parts.append(f"    expect(() => {{")
                code_parts.append(f"      // Function call that should throw")
                code_parts.append(f"    }}).toThrow({test_case.expected_exception});")
            else:
                for assertion in test_case.assertions:
                    code_parts.append(f"    {self._convert_to_jest_assertion(assertion)}")

            code_parts.append("  });")

        code_parts.append("});")

        return '\n'.join(code_parts)
```

**검증 기준**:

- [ ] 다양한 테스트 케이스 생성
- [ ] 커버리지 목표 달성
- [ ] 다국어 테스트 프레임워크 지원
- [ ] 픽스처 및 목 객체 생성

---

#### SubTask 4.64.2: 통합 테스트 생성기

**담당자**: 통합 테스트 전문가  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/generation/integration_test_generator.py
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
import asyncio

@dataclass
class IntegrationTestCase:
    name: str
    description: str
    components: List[str]  # 통합할 컴포넌트들
    test_scenario: str
    setup_steps: List[Dict[str, Any]]
    test_steps: List[Dict[str, Any]]
    teardown_steps: List[Dict[str, Any]]
    expected_results: List[Dict[str, Any]]
    dependencies: List[str]
    environment_config: Dict[str, Any]

@dataclass
class IntegrationTestSuite:
    name: str
    description: str
    test_cases: List[IntegrationTestCase]
    shared_fixtures: Dict[str, Any]
    test_data: Dict[str, Any]
    environment_setup: Dict[str, Any]
    cleanup_strategy: str

class IntegrationTestGenerator:
    """통합 테스트 생성기"""

    def __init__(self):
        self.scenario_generator = ScenarioGenerator()
        self.fixture_builder = IntegrationFixtureBuilder()
        self.environment_manager = TestEnvironmentManager()
        self.data_generator = TestDataGenerator()
        self.assertion_generator = IntegrationAssertionGenerator()

    async def generate_integration_tests(
        self,
        components: List[ComponentInfo],
        architecture: SystemArchitecture,
        test_config: Optional[Dict[str, Any]] = None
    ) -> List[IntegrationTestSuite]:
        """통합 테스트 생성"""

        test_suites = []

        # 1. 통합 포인트 식별
        integration_points = await self._identify_integration_points(
            components,
            architecture
        )

        # 2. 각 통합 포인트에 대한 테스트 시나리오 생성
        for point in integration_points:
            # 시나리오 생성
            scenarios = await self.scenario_generator.generate_scenarios(
                point,
                test_config
            )

            # 각 시나리오에 대한 테스트 케이스 생성
            test_cases = []
            for scenario in scenarios:
                test_case = await self._create_integration_test_case(
                    scenario,
                    point,
                    components
                )
                test_cases.append(test_case)

            # 공유 픽스처 생성
            shared_fixtures = await self.fixture_builder.build_shared_fixtures(
                point,
                test_cases
            )

            # 테스트 데이터 생성
            test_data = await self.data_generator.generate_integration_data(
                test_cases,
                components
            )

            # 환경 설정
            env_setup = await self.environment_manager.create_environment_config(
                point,
                components
            )

            # 테스트 스위트 생성
            test_suite = IntegrationTestSuite(
                name=f"Integration_{point.name}",
                description=f"Integration tests for {point.description}",
                test_cases=test_cases,
                shared_fixtures=shared_fixtures,
                test_data=test_data,
                environment_setup=env_setup,
                cleanup_strategy=self._determine_cleanup_strategy(point)
            )

            test_suites.append(test_suite)

        return test_suites

    async def _identify_integration_points(
        self,
        components: List[ComponentInfo],
        architecture: SystemArchitecture
    ) -> List[IntegrationPoint]:
        """통합 포인트 식별"""

        integration_points = []

        # 1. API 통합 포인트
        api_points = self._find_api_integrations(components, architecture)
        integration_points.extend(api_points)

        # 2. 데이터베이스 통합 포인트
        db_points = self._find_database_integrations(components, architecture)
        integration_points.extend(db_points)

        # 3. 메시지 큐 통합 포인트
        mq_points = self._find_message_queue_integrations(components, architecture)
        integration_points.extend(mq_points)

        # 4. 외부 서비스 통합 포인트
        external_points = self._find_external_service_integrations(components, architecture)
        integration_points.extend(external_points)

        # 5. 마이크로서비스 간 통합
        service_points = self._find_microservice_integrations(components, architecture)
        integration_points.extend(service_points)

        return integration_points

    async def _create_integration_test_case(
        self,
        scenario: TestScenario,
        integration_point: IntegrationPoint,
        components: List[ComponentInfo]
    ) -> IntegrationTestCase:
        """통합 테스트 케이스 생성"""

        # Setup 단계 생성
        setup_steps = await self._generate_setup_steps(
            scenario,
            integration_point,
            components
        )

        # Test 단계 생성
        test_steps = await self._generate_test_steps(
            scenario,
            integration_point
        )

        # 예상 결과 생성
        expected_results = await self._generate_expected_results(
            scenario,
            integration_point
        )

        # Teardown 단계 생성
        teardown_steps = await self._generate_teardown_steps(
            scenario,
            integration_point
        )

        # 의존성 식별
        dependencies = self._identify_test_dependencies(
            integration_point,
            components
        )

        # 환경 설정
        env_config = self._generate_environment_config(
            scenario,
            integration_point
        )

        return IntegrationTestCase(
            name=f"test_{integration_point.name}_{scenario.name}",
            description=scenario.description,
            components=[c.name for c in integration_point.components],
            test_scenario=scenario.scenario_type,
            setup_steps=setup_steps,
            test_steps=test_steps,
            teardown_steps=teardown_steps,
            expected_results=expected_results,
            dependencies=dependencies,
            environment_config=env_config
        )

class ScenarioGenerator:
    """시나리오 생성기"""

    async def generate_scenarios(
        self,
        integration_point: IntegrationPoint,
        config: Optional[Dict[str, Any]]
    ) -> List[TestScenario]:
        """테스트 시나리오 생성"""

        scenarios = []

        # 1. Happy Path 시나리오
        happy_path = await self._generate_happy_path_scenario(integration_point)
        scenarios.append(happy_path)

        # 2. Error Handling 시나리오
        error_scenarios = await self._generate_error_scenarios(integration_point)
        scenarios.extend(error_scenarios)

        # 3. Performance 시나리오
        if config and config.get('include_performance_tests', False):
            perf_scenarios = await self._generate_performance_scenarios(integration_point)
            scenarios.extend(perf_scenarios)

        # 4. Concurrency 시나리오
        if config and config.get('include_concurrency_tests', False):
            concurrency_scenarios = await self._generate_concurrency_scenarios(integration_point)
            scenarios.extend(concurrency_scenarios)

        # 5. Data Integrity 시나리오
        data_scenarios = await self._generate_data_integrity_scenarios(integration_point)
        scenarios.extend(data_scenarios)

        return scenarios

    async def _generate_happy_path_scenario(
        self,
        integration_point: IntegrationPoint
    ) -> TestScenario:
        """정상 동작 시나리오"""

        if integration_point.type == 'api':
            return TestScenario(
                name='api_happy_path',
                description='Test successful API integration flow',
                scenario_type='happy_path',
                steps=[
                    {'action': 'send_request', 'data': self._generate_valid_request()},
                    {'action': 'verify_response', 'expected': 'success'},
                    {'action': 'check_side_effects', 'targets': ['database', 'cache']}
                ]
            )
        elif integration_point.type == 'database':
            return TestScenario(
                name='db_crud_operations',
                description='Test database CRUD operations',
                scenario_type='happy_path',
                steps=[
                    {'action': 'create_record', 'data': self._generate_test_record()},
                    {'action': 'read_record', 'verify': 'created_data'},
                    {'action': 'update_record', 'data': self._generate_update_data()},
                    {'action': 'delete_record', 'verify': 'soft_delete'}
                ]
            )
        # 다른 타입들...

class IntegrationTestFormatter:
    """통합 테스트 코드 포매터"""

    def format_test_suite(
        self,
        test_suite: IntegrationTestSuite,
        language: str,
        framework: str
    ) -> str:
        """통합 테스트 스위트 포맷팅"""

        if language == 'python':
            return self._format_python_integration_tests(test_suite, framework)
        elif language in ['javascript', 'typescript']:
            return self._format_js_integration_tests(test_suite, framework)
        elif language == 'java':
            return self._format_java_integration_tests(test_suite, framework)

    def _format_python_integration_tests(
        self,
        test_suite: IntegrationTestSuite,
        framework: str
    ) -> str:
        """Python 통합 테스트 코드 생성"""

        if framework == 'pytest':
            return self._format_pytest_integration(test_suite)
        else:
            return self._format_unittest_integration(test_suite)

    def _format_pytest_integration(
        self,
        test_suite: IntegrationTestSuite
    ) -> str:
        """pytest 통합 테스트 코드"""

        code_parts = []

        # 임포트
        imports = [
            "import pytest",
            "import asyncio",
            "from typing import Dict, Any",
            "import aiohttp",
            "from sqlalchemy.ext.asyncio import create_async_engine",
            "import redis.asyncio as redis",
            "from testcontainers.postgres import PostgresContainer",
            "from testcontainers.redis import RedisContainer"
        ]
        code_parts.append('\n'.join(imports))

        # 픽스처 정의
        code_parts.append("\n\n# Shared Fixtures")

        # 데이터베이스 픽스처
        code_parts.append("""
@pytest.fixture(scope='session')
async def database():
    \"\"\"Test database fixture\"\"\"
    with PostgresContainer('postgres:14') as postgres:
        engine = create_async_engine(postgres.get_connection_url())

        # Create schema
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        yield engine

        # Cleanup
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()
""")

        # Redis 픽스처
        code_parts.append("""
@pytest.fixture(scope='session')
async def cache():
    \"\"\"Test cache fixture\"\"\"
    with RedisContainer('redis:7') as redis_container:
        redis_client = await redis.from_url(
            redis_container.get_connection_url(),
            decode_responses=True
        )
        yield redis_client
        await redis_client.close()
""")

        # HTTP 클라이언트 픽스처
        code_parts.append("""
@pytest.fixture
async def client(app):
    \"\"\"Test HTTP client fixture\"\"\"
    async with aiohttp.ClientSession() as session:
        yield session
""")

        # 테스트 클래스
        code_parts.append(f"\n\nclass Test{test_suite.name}:")

        # 각 테스트 케이스
        for test_case in test_suite.test_cases:
            code_parts.append(f"""
    @pytest.mark.asyncio
    async def {test_case.name}(self, database, cache, client):
        \"\"\"
        {test_case.description}
        \"\"\"

        # Setup
        {self._format_setup_steps(test_case.setup_steps)}

        # Execute test steps
        {self._format_test_steps(test_case.test_steps)}

        # Verify results
        {self._format_assertions(test_case.expected_results)}

        # Cleanup
        {self._format_teardown_steps(test_case.teardown_steps)}
""")

        return '\n'.join(code_parts)

    def _format_setup_steps(self, steps: List[Dict[str, Any]]) -> str:
        """Setup 단계 포맷팅"""

        formatted_steps = []
        for step in steps:
            if step['type'] == 'create_data':
                formatted_steps.append(f"""
        # Create test data
        test_data = {step['data']}
        async with database.begin() as conn:
            await conn.execute(
                insert(TestModel).values(**test_data)
            )""")
            elif step['type'] == 'mock_service':
                formatted_steps.append(f"""
        # Mock external service
        with aioresponses() as mocked:
            mocked.{step['method']}(
                '{step['url']}',
                status={step['status']},
                payload={step['response']}
            )""")

        return '\n'.join(formatted_steps)
```

**검증 기준**:

- [ ] 다양한 통합 시나리오
- [ ] 환경 격리 및 설정
- [ ] 외부 의존성 모킹
- [ ] 동시성 및 성능 테스트

#### SubTask 4.64.3: E2E 테스트 생성기

**담당자**: E2E 테스트 전문가  
**예상 소요시간**: 14시간

**작업 내용**:

```typescript
// backend/src/agents/implementations/generation/e2e_test_generator.ts
interface E2ETestCase {
  name: string;
  description: string;
  userJourney: UserJourney;
  preconditions: Precondition[];
  steps: E2ETestStep[];
  validations: Validation[];
  postconditions: Postcondition[];
  tags: string[];
}

interface UserJourney {
  persona: string;
  goal: string;
  scenario: string;
  criticalPath: boolean;
}

interface E2ETestStep {
  action: string;
  target: string;
  data?: any;
  waitFor?: WaitCondition;
  screenshot?: boolean;
}

class E2ETestGenerator {
  private journeyAnalyzer: UserJourneyAnalyzer;
  private pageObjectGenerator: PageObjectGenerator;
  private testDataBuilder: E2ETestDataBuilder;
  private validationBuilder: ValidationBuilder;

  async generateE2ETests(
    application: ApplicationSpec,
    requirements: Requirements[],
    testConfig?: E2ETestConfig,
  ): Promise<E2ETestSuite[]> {
    const testSuites: E2ETestSuite[] = [];

    // 1. 사용자 여정 분석
    const userJourneys = await this.journeyAnalyzer.analyzeJourneys(application, requirements);

    // 2. 각 여정에 대한 E2E 테스트 생성
    for (const journey of userJourneys) {
      // 페이지 객체 생성
      const pageObjects = await this.pageObjectGenerator.generatePageObjects(journey, application);

      // 테스트 케이스 생성
      const testCases = await this.createE2ETestCases(journey, pageObjects, testConfig);

      // 테스트 데이터 생성
      const testData = await this.testDataBuilder.buildTestData(testCases, application);

      // 테스트 스위트 구성
      const testSuite = new E2ETestSuite({
        name: `E2E_${journey.name}`,
        description: journey.description,
        testCases,
        pageObjects,
        testData,
        configuration: this.generateE2EConfig(journey, testConfig),
      });

      testSuites.push(testSuite);
    }

    return testSuites;
  }

  private async createE2ETestCases(
    journey: UserJourney,
    pageObjects: PageObject[],
    config?: E2ETestConfig,
  ): Promise<E2ETestCase[]> {
    const testCases: E2ETestCase[] = [];

    // 1. Critical Path 테스트
    const criticalPathTest = await this.generateCriticalPathTest(journey, pageObjects);
    testCases.push(criticalPathTest);

    // 2. Alternative Path 테스트
    const alternativePaths = await this.generateAlternativePathTests(journey, pageObjects);
    testCases.push(...alternativePaths);

    // 3. Error Path 테스트
    const errorPaths = await this.generateErrorPathTests(journey, pageObjects);
    testCases.push(...errorPaths);

    // 4. Cross-browser 테스트
    if (config?.crossBrowser) {
      const crossBrowserTests = await this.generateCrossBrowserTests(
        criticalPathTest,
        config.browsers,
      );
      testCases.push(...crossBrowserTests);
    }

    // 5. Mobile 테스트
    if (config?.mobile) {
      const mobileTests = await this.generateMobileTests(journey, pageObjects, config.devices);
      testCases.push(...mobileTests);
    }

    return testCases;
  }

  private async generateCriticalPathTest(
    journey: UserJourney,
    pageObjects: PageObject[],
  ): Promise<E2ETestCase> {
    const steps: E2ETestStep[] = [];

    // 1. 초기 네비게이션
    steps.push({
      action: 'navigate',
      target: journey.startUrl,
      waitFor: { type: 'load', timeout: 10000 },
    });

    // 2. 인증 (필요한 경우)
    if (journey.requiresAuth) {
      steps.push(...this.generateAuthSteps(journey.persona));
    }

    // 3. 주요 플로우 단계
    for (const flowStep of journey.mainFlow) {
      const pageObject = pageObjects.find((po) => po.name === flowStep.page);

      if (flowStep.action === 'click') {
        steps.push({
          action: 'click',
          target: `${pageObject.name}.${flowStep.element}`,
          waitFor: { type: 'element', selector: flowStep.waitFor },
        });
      } else if (flowStep.action === 'input') {
        steps.push({
          action: 'type',
          target: `${pageObject.name}.${flowStep.element}`,
          data: flowStep.data,
          waitFor: { type: 'enabled' },
        });
      } else if (flowStep.action === 'select') {
        steps.push({
          action: 'select',
          target: `${pageObject.name}.${flowStep.element}`,
          data: flowStep.value,
          waitFor: { type: 'visible' },
        });
      }

      // 스크린샷 (주요 단계)
      if (flowStep.critical) {
        steps.push({
          action: 'screenshot',
          target: flowStep.name,
          screenshot: true,
        });
      }
    }

    // 4. 검증 단계
    const validations = await this.validationBuilder.buildValidations(
      journey.expectedOutcome,
      pageObjects,
    );

    return {
      name: `test_${journey.name}_critical_path`,
      description: `E2E test for ${journey.description} - Critical Path`,
      userJourney: journey,
      preconditions: this.generatePreconditions(journey),
      steps,
      validations,
      postconditions: this.generatePostconditions(journey),
      tags: ['critical', 'e2e', journey.feature],
    };
  }
}

// Playwright 테스트 생성기
class PlaywrightTestGenerator {
  formatE2ETests(testSuite: E2ETestSuite, config: PlaywrightConfig): string {
    const code: string[] = [];

    // 임포트
    code.push(`
import { test, expect, Page } from '@playwright/test';
import { ${testSuite.pageObjects.map((po) => po.name).join(', ')} } from './page-objects';
import { testData } from './test-data/${testSuite.name}.data';
`);

    // 테스트 설정
    code.push(`
test.describe('${testSuite.name}', () => {
  let page: Page;
  ${testSuite.pageObjects.map((po) => `let ${this.camelCase(po.name)}: ${po.name};`).join('\n  ')}

  test.beforeEach(async ({ page: testPage, context }) => {
    page = testPage;
    
    // Initialize page objects
    ${testSuite.pageObjects
      .map((po) => `${this.camelCase(po.name)} = new ${po.name}(page);`)
      .join('\n    ')}
    
    // Set viewport
    await page.setViewportSize({ width: 1920, height: 1080 });
    
    // Clear cookies and storage
    await context.clearCookies();
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
  });

  test.afterEach(async () => {
    // Capture screenshot on failure
    if (test.info().status !== test.info().expectedStatus) {
      await page.screenshot({ 
        path: \`screenshots/\${test.info().title}-failure.png\`,
        fullPage: true 
      });
    }
  });
`);

    // 각 테스트 케이스
    for (const testCase of testSuite.testCases) {
      code.push(this.formatTestCase(testCase));
    }

    code.push('});');

    return code.join('\n');
  }

  private formatTestCase(testCase: E2ETestCase): string {
    return `
  test('${testCase.description}', async () => {
    // Preconditions
    ${this.formatPreconditions(testCase.preconditions)}
    
    // Test steps
    ${this.formatTestSteps(testCase.steps)}
    
    // Validations
    ${this.formatValidations(testCase.validations)}
    
    // Postconditions
    ${this.formatPostconditions(testCase.postconditions)}
  });
`;
  }

  private formatTestSteps(steps: E2ETestStep[]): string {
    return steps
      .map((step) => {
        switch (step.action) {
          case 'navigate':
            return `await page.goto('${step.target}');`;

          case 'click':
            return `
    await ${step.target}.click();
    ${step.waitFor ? this.formatWaitCondition(step.waitFor) : ''}`;

          case 'type':
            return `
    await ${step.target}.fill('${step.data}');`;

          case 'select':
            return `
    await ${step.target}.selectOption('${step.data}');`;

          case 'screenshot':
            return `
    await page.screenshot({ 
      path: \`screenshots/\${test.info().title}-${step.target}.png\` 
    });`;

          default:
            return `// Unknown action: ${step.action}`;
        }
      })
      .join('\n    ');
  }

  private formatWaitCondition(condition: WaitCondition): string {
    switch (condition.type) {
      case 'load':
        return `await page.waitForLoadState('load', { timeout: ${condition.timeout} });`;

      case 'element':
        return `await page.waitForSelector('${condition.selector}', { 
          state: 'visible',
          timeout: ${condition.timeout || 5000}
        });`;

      case 'network':
        return `await page.waitForResponse(response => 
          response.url().includes('${condition.url}') && response.status() === 200
        );`;

      default:
        return '';
    }
  }
}

// Cypress 테스트 생성기
class CypressTestGenerator {
  formatE2ETests(testSuite: E2ETestSuite, config: CypressConfig): string {
    const code: string[] = [];

    // 테스트 스위트
    code.push(`
describe('${testSuite.name}', () => {
  beforeEach(() => {
    // Reset application state
    cy.task('db:seed');
    cy.clearCookies();
    cy.clearLocalStorage();
    
    // Set viewport
    cy.viewport(1920, 1080);
  });

  afterEach(() => {
    // Clean up test data
    cy.task('db:cleanup');
  });
`);

    // 각 테스트 케이스
    for (const testCase of testSuite.testCases) {
      code.push(this.formatCypressTestCase(testCase));
    }

    code.push('});');

    return code.join('\n');
  }

  private formatCypressTestCase(testCase: E2ETestCase): string {
    return `
  it('${testCase.description}', () => {
    // Setup test data
    const testData = ${JSON.stringify(testCase.testData, null, 4)};
    
    ${testCase.steps.map((step) => this.formatCypressStep(step)).join('\n    ')}
    
    // Assertions
    ${testCase.validations.map((v) => this.formatCypressAssertion(v)).join('\n    ')}
  });
`;
  }

  private formatCypressStep(step: E2ETestStep): string {
    switch (step.action) {
      case 'navigate':
        return `cy.visit('${step.target}');`;

      case 'click':
        return `cy.get('${step.target}').click();`;

      case 'type':
        return `cy.get('${step.target}').type('${step.data}');`;

      case 'select':
        return `cy.get('${step.target}').select('${step.data}');`;

      case 'screenshot':
        return `cy.screenshot('${step.target}');`;

      default:
        return `// ${step.action}`;
    }
  }

  private formatCypressAssertion(validation: Validation): string {
    switch (validation.type) {
      case 'visible':
        return `cy.get('${validation.target}').should('be.visible');`;

      case 'text':
        return `cy.get('${validation.target}').should('contain.text', '${validation.expected}');`;

      case 'value':
        return `cy.get('${validation.target}').should('have.value', '${validation.expected}');`;

      case 'url':
        return `cy.url().should('include', '${validation.expected}');`;

      default:
        return `// ${validation.type} assertion`;
    }
  }
}
```

**검증 기준**:

- [ ] 사용자 여정 기반 테스트
- [ ] 크로스 브라우저 테스트
- [ ] 모바일 테스트 지원
- [ ] 스크린샷 및 비디오 캡처

#### SubTask 4.64.4: 테스트 커버리지 분석

**담당자**: QA 리드  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/generation/test_coverage_analyzer.py
from typing import Dict, List, Any, Optional, Set, Tuple
import ast
from dataclasses import dataclass
from enum import Enum

class CoverageType(Enum):
    LINE = "line"
    BRANCH = "branch"
    FUNCTION = "function"
    STATEMENT = "statement"
    PATH = "path"

@dataclass
class CoverageMetrics:
    total_lines: int
    covered_lines: int
    line_coverage: float
    total_branches: int
    covered_branches: int
    branch_coverage: float
    total_functions: int
    covered_functions: int
    function_coverage: float
    uncovered_areas: List[UncoveredArea]

@dataclass
class UncoveredArea:
    file: str
    start_line: int
    end_line: int
    type: str  # 'function', 'branch', 'exception_handler'
    description: str
    complexity: int
    risk_level: str  # 'high', 'medium', 'low'

@dataclass
class CoverageReport:
    overall_coverage: float
    metrics: CoverageMetrics
    risk_analysis: RiskAnalysis
    recommendations: List[CoverageRecommendation]
    test_gaps: List[TestGap]
    coverage_trend: CoverageTrend

class TestCoverageAnalyzer:
    """테스트 커버리지 분석기"""

    def __init__(self):
        self.code_analyzer = CodeCoverageAnalyzer()
        self.branch_analyzer = BranchCoverageAnalyzer()
        self.path_analyzer = PathCoverageAnalyzer()
        self.risk_assessor = CoverageRiskAssessor()
        self.gap_detector = TestGapDetector()

    async def analyze_coverage(
        self,
        source_code: Dict[str, str],
        test_code: Dict[str, str],
        execution_data: Optional[ExecutionData] = None
    ) -> CoverageReport:
        """테스트 커버리지 분석"""

        # 1. 코드 구조 분석
        code_structure = await self._analyze_code_structure(source_code)

        # 2. 테스트 범위 분석
        test_coverage = await self._analyze_test_coverage(
            test_code,
            code_structure
        )

        # 3. 실행 데이터 분석 (있는 경우)
        if execution_data:
            runtime_coverage = await self._analyze_runtime_coverage(
                execution_data,
                code_structure
            )
            # 정적 + 동적 분석 병합
            coverage_data = self._merge_coverage_data(
                test_coverage,
                runtime_coverage
            )
        else:
            coverage_data = test_coverage

        # 4. 커버리지 메트릭 계산
        metrics = await self._calculate_coverage_metrics(
            code_structure,
            coverage_data
        )

        # 5. 위험 분석
        risk_analysis = await self.risk_assessor.assess_risks(
            metrics.uncovered_areas,
            code_structure
        )

        # 6. 테스트 갭 감지
        test_gaps = await self.gap_detector.detect_gaps(
            code_structure,
            coverage_data,
            metrics
        )

        # 7. 권장사항 생성
        recommendations = await self._generate_recommendations(
            metrics,
            risk_analysis,
            test_gaps
        )

        # 8. 커버리지 트렌드 분석
        coverage_trend = await self._analyze_coverage_trend(
            metrics,
            execution_data
        )

        # 전체 커버리지 계산
        overall_coverage = self._calculate_overall_coverage(metrics)

        return CoverageReport(
            overall_coverage=overall_coverage,
            metrics=metrics,
            risk_analysis=risk_analysis,
            recommendations=recommendations,
            test_gaps=test_gaps,
            coverage_trend=coverage_trend
        )

    async def _analyze_code_structure(
        self,
        source_code: Dict[str, str]
    ) -> CodeStructure:
        """코드 구조 분석"""

        structure = CodeStructure()

        for file_path, code in source_code.items():
            try:
                tree = ast.parse(code)

                # 함수 및 메서드 추출
                functions = self._extract_functions(tree)
                structure.functions[file_path] = functions

                # 분기점 추출
                branches = self._extract_branches(tree)
                structure.branches[file_path] = branches

                # 코드 라인 계산
                lines = self._calculate_code_lines(code)
                structure.lines[file_path] = lines

                # 복잡도 계산
                complexity = self._calculate_complexity(tree)
                structure.complexity[file_path] = complexity

            except SyntaxError:
                # 파싱 실패 처리
                continue

        return structure

    def _extract_functions(self, tree: ast.AST) -> List[FunctionInfo]:
        """함수 정보 추출"""

        functions = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_info = FunctionInfo(
                    name=node.name,
                    start_line=node.lineno,
                    end_line=node.end_lineno,
                    complexity=self._calculate_function_complexity(node),
                    has_docstring=ast.get_docstring(node) is not None,
                    parameters=len(node.args.args),
                    is_async=isinstance(node, ast.AsyncFunctionDef)
                )
                functions.append(func_info)

        return functions

    def _extract_branches(self, tree: ast.AST) -> List[BranchInfo]:
        """분기점 추출"""

        branches = []

        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                branches.append(BranchInfo(
                    type='if',
                    line=node.lineno,
                    condition=ast.unparse(node.test),
                    has_else=bool(node.orelse)
                ))
            elif isinstance(node, ast.For):
                branches.append(BranchInfo(
                    type='for',
                    line=node.lineno,
                    condition=f"for {ast.unparse(node.target)} in {ast.unparse(node.iter)}"
                ))
            elif isinstance(node, ast.While):
                branches.append(BranchInfo(
                    type='while',
                    line=node.lineno,
                    condition=ast.unparse(node.test)
                ))
            elif isinstance(node, ast.Try):
                branches.append(BranchInfo(
                    type='try',
                    line=node.lineno,
                    condition='exception handling',
                    exception_types=[
                        handler.type.id if handler.type and hasattr(handler.type, 'id') else 'Exception'
                        for handler in node.handlers
                    ]
                ))

        return branches

class BranchCoverageAnalyzer:
    """분기 커버리지 분석기"""

    async def analyze_branch_coverage(
        self,
        code_structure: CodeStructure,
        test_execution: TestExecution
    ) -> BranchCoverageData:
        """분기 커버리지 분석"""

        branch_coverage = BranchCoverageData()

        for file_path, branches in code_structure.branches.items():
            covered_branches = set()
            uncovered_branches = []

            for branch in branches:
                if self._is_branch_covered(branch, test_execution):
                    covered_branches.add(branch.line)
                else:
                    uncovered_branches.append(branch)

            branch_coverage.coverage_by_file[file_path] = {
                'total': len(branches),
                'covered': len(covered_branches),
                'percentage': len(covered_branches) / len(branches) * 100 if branches else 100
            }

            # 미커버 분기 상세 정보
            for uncovered in uncovered_branches:
                branch_coverage.uncovered_branches.append({
                    'file': file_path,
                    'line': uncovered.line,
                    'type': uncovered.type,
                    'condition': uncovered.condition,
                    'risk': self._assess_branch_risk(uncovered, code_structure)
                })

        return branch_coverage

    def _is_branch_covered(
        self,
        branch: BranchInfo,
        test_execution: TestExecution
    ) -> bool:
        """분기 커버 여부 확인"""

        # 실행 데이터에서 해당 라인이 실행되었는지 확인
        if branch.line in test_execution.executed_lines:
            # If문의 경우 else 분기도 확인
            if branch.type == 'if' and branch.has_else:
                # else 분기 라인도 실행되었는지 확인
                else_line = self._find_else_line(branch)
                return else_line in test_execution.executed_lines
            return True
        return False

class TestGapDetector:
    """테스트 갭 감지기"""

    async def detect_gaps(
        self,
        code_structure: CodeStructure,
        coverage_data: CoverageData,
        metrics: CoverageMetrics
    ) -> List[TestGap]:
        """테스트 갭 감지"""

        gaps = []

        # 1. 완전히 테스트되지 않은 함수
        untested_functions = self._find_untested_functions(
            code_structure,
            coverage_data
        )
        for func in untested_functions:
            gaps.append(TestGap(
                type='untested_function',
                location=f"{func.file}:{func.name}",
                severity='high' if func.complexity > 10 else 'medium',
                description=f"Function '{func.name}' has no test coverage",
                suggested_tests=self._suggest_function_tests(func)
            ))

        # 2. 에러 핸들링 갭
        error_handling_gaps = self._find_error_handling_gaps(
            code_structure,
            coverage_data
        )
        gaps.extend(error_handling_gaps)

        # 3. 경계값 테스트 갭
        boundary_gaps = self._find_boundary_test_gaps(
            code_structure,
            coverage_data
        )
        gaps.extend(boundary_gaps)

        # 4. 통합 테스트 갭
        integration_gaps = await self._find_integration_gaps(
            code_structure,
            coverage_data
        )
        gaps.extend(integration_gaps)

        return gaps

    def _suggest_function_tests(
        self,
        function: FunctionInfo
    ) -> List[str]:
        """함수 테스트 제안"""

        suggestions = []

        # 기본 테스트
        suggestions.append(f"Test {function.name} with valid inputs")

        # 파라미터가 있는 경우
        if function.parameters > 0:
            suggestions.append(f"Test {function.name} with null/undefined parameters")
            suggestions.append(f"Test {function.name} with edge case values")

        # 비동기 함수인 경우
        if function.is_async:
            suggestions.append(f"Test {function.name} error handling for async operations")
            suggestions.append(f"Test {function.name} timeout scenarios")

        # 복잡도가 높은 경우
        if function.complexity > 5:
            suggestions.append(f"Test all branches in {function.name}")
            suggestions.append(f"Test combinations of conditions in {function.name}")

        return suggestions

class CoverageReportGenerator:
    """커버리지 리포트 생성기"""

    def generate_html_report(
        self,
        coverage_report: CoverageReport,
        source_code: Dict[str, str]
    ) -> str:
        """HTML 커버리지 리포트 생성"""

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Coverage Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f0f0f0; padding: 15px; border-radius: 5px; }}
        .metric {{ display: inline-block; margin: 10px; }}
        .coverage-bar {{ width: 200px; height: 20px; background: #ddd; border-radius: 10px; }}
        .coverage-fill {{ height: 100%; background: #4CAF50; border-radius: 10px; }}
        .uncovered {{ background: #ffcccc; }}
        .covered {{ background: #ccffcc; }}
        .risk-high {{ color: #d32f2f; }}
        .risk-medium {{ color: #f57c00; }}
        .risk-low {{ color: #388e3c; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background: #f5f5f5; }}
    </style>
</head>
<body>
    <h1>Test Coverage Report</h1>

    <div class="summary">
        <h2>Overall Coverage: {coverage_report.overall_coverage:.1f}%</h2>

        <div class="metric">
            <strong>Line Coverage:</strong> {coverage_report.metrics.line_coverage:.1f}%
            <div class="coverage-bar">
                <div class="coverage-fill" style="width: {coverage_report.metrics.line_coverage}%"></div>
            </div>
        </div>

        <div class="metric">
            <strong>Branch Coverage:</strong> {coverage_report.metrics.branch_coverage:.1f}%
            <div class="coverage-bar">
                <div class="coverage-fill" style="width: {coverage_report.metrics.branch_coverage}%"></div>
            </div>
        </div>

        <div class="metric">
            <strong>Function Coverage:</strong> {coverage_report.metrics.function_coverage:.1f}%
            <div class="coverage-bar">
                <div class="coverage-fill" style="width: {coverage_report.metrics.function_coverage}%"></div>
            </div>
        </div>
    </div>

    <h2>Risk Analysis</h2>
    <table>
        <tr>
            <th>File</th>
            <th>Uncovered Area</th>
            <th>Risk Level</th>
            <th>Description</th>
        </tr>
        {self._generate_risk_rows(coverage_report.risk_analysis)}
    </table>

    <h2>Test Gaps</h2>
    <ul>
        {self._generate_gap_list(coverage_report.test_gaps)}
    </ul>

    <h2>Recommendations</h2>
    <ol>
        {self._generate_recommendations_list(coverage_report.recommendations)}
    </ol>

    <h2>File Coverage Details</h2>
    {self._generate_file_coverage_details(coverage_report, source_code)}

</body>
</html>
"""
        return html

    def generate_json_report(
        self,
        coverage_report: CoverageReport
    ) -> Dict[str, Any]:
        """JSON 커버리지 리포트 생성"""

        return {
            'summary': {
                'overall_coverage': coverage_report.overall_coverage,
                'line_coverage': coverage_report.metrics.line_coverage,
                'branch_coverage': coverage_report.metrics.branch_coverage,
                'function_coverage': coverage_report.metrics.function_coverage,
                'total_lines': coverage_report.metrics.total_lines,
                'covered_lines': coverage_report.metrics.covered_lines,
                'total_branches': coverage_report.metrics.total_branches,
                'covered_branches': coverage_report.metrics.covered_branches,
                'total_functions': coverage_report.metrics.total_functions,
                'covered_functions': coverage_report.metrics.covered_functions
            },
            'uncovered_areas': [
                {
                    'file': area.file,
                    'start_line': area.start_line,
                    'end_line': area.end_line,
                    'type': area.type,
                    'description': area.description,
                    'risk_level': area.risk_level
                }
                for area in coverage_report.metrics.uncovered_areas
            ],
            'test_gaps': [
                {
                    'type': gap.type,
                    'location': gap.location,
                    'severity': gap.severity,
                    'description': gap.description,
                    'suggested_tests': gap.suggested_tests
                }
                for gap in coverage_report.test_gaps
            ],
            'recommendations': [
                {
                    'priority': rec.priority,
                    'category': rec.category,
                    'description': rec.description,
                    'impact': rec.impact
                }
                for rec in coverage_report.recommendations
            ],
            'trend': {
                'direction': coverage_report.coverage_trend.direction,
                'change': coverage_report.coverage_trend.change,
                'history': coverage_report.coverage_trend.history
            }
        }
```

**검증 기준**:

- [ ] 다차원 커버리지 분석
- [ ] 위험 영역 식별
- [ ] 테스트 갭 감지
- [ ] 시각적 리포트 생성

---

### Task 4.65: 문서화 자동 생성

#### SubTask 4.65.1: API 문서 생성

**담당자**: 기술 문서 작성자  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/generation/api_doc_generator.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re
import json
import yaml

@dataclass
class APIEndpoint:
    method: str
    path: str
    summary: str
    description: str
    parameters: List[APIParameter]
    request_body: Optional[APIRequestBody]
    responses: Dict[str, APIResponse]
    tags: List[str]
    security: List[Dict[str, List[str]]]
    examples: List[APIExample]

@dataclass
class APIParameter:
    name: str
    in_: str  # 'path', 'query', 'header', 'cookie'
    description: str
    required: bool
    schema: Dict[str, Any]
    example: Any
    deprecated: bool = False

@dataclass
class APIDocumentation:
    title: str
    version: str
    description: str
    servers: List[Dict[str, str]]
    endpoints: List[APIEndpoint]
    components: APIComponents
    security_schemes: Dict[str, Any]
    tags: List[Dict[str, str]]

class APIDocumentationGenerator:
    """API 문서 생성기"""

    def __init__(self):
        self.endpoint_analyzer = EndpointAnalyzer()
        self.schema_generator = SchemaGenerator()
        self.example_generator = ExampleGenerator()
        self.openapi_builder = OpenAPIBuilder()

    async def generate_api_documentation(
        self,
        source_code: Dict[str, str],
        framework: str,
        config: Optional[APIDocConfig] = None
    ) -> APIDocumentation:
        """API 문서 생성"""

        # 1. 엔드포인트 추출
        endpoints = await self.endpoint_analyzer.extract_endpoints(
            source_code,
            framework
        )

        # 2. 각 엔드포인트 분석
        documented_endpoints = []
        for endpoint in endpoints:
            # 파라미터 분석
            parameters = await self._analyze_parameters(endpoint)

            # 요청 본문 분석
            request_body = await self._analyze_request_body(endpoint)

            # 응답 분석
            responses = await self._analyze_responses(endpoint)

            # 예제 생성
            examples = await self.example_generator.generate_examples(
                endpoint,
                parameters,
                request_body,
                responses
            )

            # 문서화된 엔드포인트 생성
            doc_endpoint = APIEndpoint(
                method=endpoint.method,
                path=endpoint.path,
                summary=self._generate_summary(endpoint),
                description=self._generate_description(endpoint),
                parameters=parameters,
                request_body=request_body,
                responses=responses,
                tags=self._extract_tags(endpoint),
                security=self._extract_security(endpoint),
                examples=examples
            )

            documented_endpoints.append(doc_endpoint)

        # 3. 컴포넌트 생성
        components = await self._generate_components(
            documented_endpoints,
            source_code
        )

        # 4. 보안 스키마 생성
        security_schemes = await self._generate_security_schemes(
            documented_endpoints
        )

        # 5. 전체 문서 구성
        api_doc = APIDocumentation(
            title=config.title if config else "API Documentation",
            version=config.version if config else "1.0.0",
            description=config.description if config else "",
            servers=self._generate_servers(config),
            endpoints=documented_endpoints,
            components=components,
            security_schemes=security_schemes,
            tags=self._generate_tags(documented_endpoints)
        )

        return api_doc

    async def _analyze_parameters(
        self,
        endpoint: EndpointInfo
    ) -> List[APIParameter]:
        """파라미터 분석"""

        parameters = []

        # 경로 파라미터
        path_params = re.findall(r'{(\w+)}', endpoint.path)
        for param in path_params:
            param_info = self._extract_param_info(
                param,
                endpoint.function_ast,
                'path'
            )
            parameters.append(APIParameter(
                name=param,
                in_='path',
                description=param_info.description,
                required=True,
                schema=param_info.schema,
                example=param_info.example
            ))

        # 쿼리 파라미터
        query_params = self._extract_query_params(endpoint.function_ast)
        for param in query_params:
            parameters.append(APIParameter(
                name=param.name,
                in_='query',
                description=param.description,
                required=param.required,
                schema=param.schema,
                example=param.example
            ))

        # 헤더 파라미터
        header_params = self._extract_header_params(endpoint.function_ast)
        for param in header_params:
            parameters.append(APIParameter(
                name=param.name,
                in_='header',
                description=param.description,
                required=param.required,
                schema=param.schema,
                example=param.example
            ))

        return parameters

    async def _analyze_request_body(
        self,
        endpoint: EndpointInfo
    ) -> Optional[APIRequestBody]:
        """요청 본문 분석"""

        if endpoint.method not in ['POST', 'PUT', 'PATCH']:
            return None

        # 함수 시그니처에서 body 파라미터 찾기
        body_param = self._find_body_parameter(endpoint.function_ast)
        if not body_param:
            return None

        # 스키마 생성
        schema = await self.schema_generator.generate_schema(
            body_param.annotation
        )

        # 예제 생성
        example = await self.example_generator.generate_request_example(
            schema
        )

        return APIRequestBody(
            description=body_param.description or "Request body",
            required=not body_param.has_default,
            content={
                'application/json': {
                    'schema': schema,
                    'example': example
                }
            }
        )

    async def _analyze_responses(
        self,
        endpoint: EndpointInfo
    ) -> Dict[str, APIResponse]:
        """응답 분석"""

        responses = {}

        # 성공 응답
        success_response = await self._analyze_success_response(endpoint)
        responses['200'] = success_response

        # 에러 응답
        error_responses = await self._analyze_error_responses(endpoint)
        responses.update(error_responses)

        # 공통 응답 (401, 403, 500)
        common_responses = self._generate_common_responses()
        for status, response in common_responses.items():
            if status not in responses:
                responses[status] = response

        return responses

    def _generate_summary(self, endpoint: EndpointInfo) -> str:
        """엔드포인트 요약 생성"""

        # 함수명을 기반으로 요약 생성
        func_name = endpoint.function_name

        # 일반적인 패턴 매칭
        if func_name.startswith('get_'):
            return f"Get {self._humanize(func_name[4:])}"
        elif func_name.startswith('create_'):
            return f"Create {self._humanize(func_name[7:])}"
        elif func_name.startswith('update_'):
            return f"Update {self._humanize(func_name[7:])}"
        elif func_name.startswith('delete_'):
            return f"Delete {self._humanize(func_name[7:])}"
        elif func_name.startswith('list_'):
            return f"List {self._humanize(func_name[5:])}"
        else:
            return self._humanize(func_name)

    def _humanize(self, text: str) -> str:
        """텍스트를 사람이 읽기 쉬운 형태로 변환"""

        # snake_case를 Title Case로
        words = text.split('_')
        return ' '.join(word.capitalize() for word in words)

class OpenAPIBuilder:
    """OpenAPI 스펙 빌더"""

    def build_openapi_spec(
        self,
        api_doc: APIDocumentation
    ) -> Dict[str, Any]:
        """OpenAPI 3.0 스펙 생성"""

        spec = {
            'openapi': '3.0.3',
            'info': {
                'title': api_doc.title,
                'version': api_doc.version,
                'description': api_doc.description
            },
            'servers': api_doc.servers,
            'paths': {},
            'components': {
                'schemas': api_doc.components.schemas,
                'securitySchemes': api_doc.security_schemes,
                'parameters': api_doc.components.parameters,
                'responses': api_doc.components.responses,
                'requestBodies': api_doc.components.request_bodies,
                'examples': api_doc.components.examples
            },
            'tags': api_doc.tags
        }

        # 엔드포인트 추가
        for endpoint in api_doc.endpoints:
            if endpoint.path not in spec['paths']:
                spec['paths'][endpoint.path] = {}

            spec['paths'][endpoint.path][endpoint.method.lower()] = {
                'summary': endpoint.summary,
                'description': endpoint.description,
                'operationId': self._generate_operation_id(endpoint),
                'tags': endpoint.tags,
                'parameters': self._format_parameters(endpoint.parameters),
                'responses': self._format_responses(endpoint.responses)
            }

            if endpoint.request_body:
                spec['paths'][endpoint.path][endpoint.method.lower()]['requestBody'] = \
                    self._format_request_body(endpoint.request_body)

            if endpoint.security:
                spec['paths'][endpoint.path][endpoint.method.lower()]['security'] = \
                    endpoint.security

        return spec

    def export_to_yaml(self, spec: Dict[str, Any]) -> str:
        """YAML 형식으로 내보내기"""

        return yaml.dump(spec, default_flow_style=False, sort_keys=False)

    def export_to_json(self, spec: Dict[str, Any]) -> str:
        """JSON 형식으로 내보내기"""

        return json.dumps(spec, indent=2)

class SwaggerUIGenerator:
    """Swagger UI 생성기"""

    def generate_swagger_ui(
        self,
        openapi_spec: Dict[str, Any],
        config: SwaggerUIConfig
    ) -> str:
        """Swagger UI HTML 생성"""

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{openapi_spec['info']['title']}</title>
    <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
    <style>
        html {{
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }}
        *, *:before, *:after {{
            box-sizing: inherit;
        }}
        body {{
            margin: 0;
            background: #fafafa;
        }}
        .swagger-ui .topbar {{
            display: none;
        }}
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {{
            const spec = {json.dumps(openapi_spec)};

            const ui = SwaggerUIBundle({{
                spec: spec,
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout",
                defaultModelsExpandDepth: {config.default_models_expand_depth},
                defaultModelExpandDepth: {config.default_model_expand_depth},
                docExpansion: "{config.doc_expansion}",
                filter: {str(config.filter).lower()},
                showExtensions: {str(config.show_extensions).lower()},
                showCommonExtensions: {str(config.show_common_extensions).lower()}
            }});

            window.ui = ui;
        }};
    </script>
</body>
</html>
"""
        return html

class PostmanCollectionGenerator:
    """Postman Collection 생성기"""

    def generate_postman_collection(
        self,
        api_doc: APIDocumentation
    ) -> Dict[str, Any]:
        """Postman Collection 생성"""

        collection = {
            'info': {
                'name': api_doc.title,
                'description': api_doc.description,
                'version': api_doc.version,
                'schema': 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json'
            },
            'item': [],
            'variable': [],
            'auth': self._generate_auth_config(api_doc.security_schemes)
        }

        # 서버 변수 추가
        for i, server in enumerate(api_doc.servers):
            collection['variable'].append({
                'key': f'baseUrl{i}',
                'value': server['url'],
                'type': 'string'
            })

        # 태그별로 폴더 구성
        folders = {}
        for tag in api_doc.tags:
            folders[tag['name']] = {
                'name': tag['name'],
                'description': tag.get('description', ''),
                'item': []
            }

        # 엔드포인트를 폴더에 추가
        for endpoint in api_doc.endpoints:
            request = self._create_postman_request(endpoint)

            # 태그가 있으면 해당 폴더에, 없으면 루트에 추가
            if endpoint.tags:
                for tag in endpoint.tags:
                    if tag in folders:
                        folders[tag]['item'].append(request)
            else:
                collection['item'].append(request)

        # 폴더를 컬렉션에 추가
        for folder in folders.values():
            if folder['item']:  # 비어있지 않은 폴더만
                collection['item'].append(folder)

        return collection
```

**검증 기준**:

- [ ] OpenAPI 3.0 스펙 생성
- [ ] Swagger UI 통합
- [ ] Postman Collection 내보내기
- [ ] 예제 자동 생성

---

#### SubTask 4.65.2: 코드 주석 생성

**담당자**: 시니어 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/generation/code_comment_generator.py
from typing import Dict, List, Any, Optional, Tuple
import ast
import re
from dataclasses import dataclass
from enum import Enum

class CommentType(Enum):
    DOCSTRING = "docstring"
    INLINE = "inline"
    BLOCK = "block"
    TODO = "todo"
    FIXME = "fixme"
    WARNING = "warning"
    NOTE = "note"

@dataclass
class CommentContext:
    code_element: str  # 'function', 'class', 'method', 'variable', 'module'
    name: str
    signature: Optional[str]
    complexity: int
    dependencies: List[str]
    side_effects: List[str]
    return_type: Optional[str]
    parameters: List[Dict[str, Any]]

@dataclass
class GeneratedComment:
    type: CommentType
    content: str
    line: int
    format: str  # 'google', 'numpy', 'sphinx', 'jsdoc', 'javadoc'
    metadata: Dict[str, Any]

class CodeCommentGenerator:
    """코드 주석 자동 생성기"""

    def __init__(self):
        self.context_analyzer = CodeContextAnalyzer()
        self.docstring_generator = DocstringGenerator()
        self.inline_comment_generator = InlineCommentGenerator()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.ai_commenter = AICommentGenerator()

    async def generate_comments(
        self,
        code: str,
        language: str,
        style: str = 'auto',
        verbosity: str = 'normal'
    ) -> Tuple[str, List[GeneratedComment]]:
        """코드에 주석 생성"""

        # 1. 코드 분석
        analysis = await self.context_analyzer.analyze(code, language)

        # 2. 주석 스타일 결정
        comment_style = self._determine_comment_style(language, style)

        # 3. 각 코드 요소에 대한 주석 생성
        comments = []

        # 모듈 레벨 문서
        if analysis.needs_module_doc:
            module_comment = await self._generate_module_comment(
                analysis.module_info,
                comment_style
            )
            comments.append(module_comment)

        # 클래스 문서
        for class_info in analysis.classes:
            class_comments = await self._generate_class_comments(
                class_info,
                comment_style,
                verbosity
            )
            comments.extend(class_comments)

        # 함수 문서
        for func_info in analysis.functions:
            func_comments = await self._generate_function_comments(
                func_info,
                comment_style,
                verbosity
            )
            comments.extend(func_comments)

        # 복잡한 로직에 대한 인라인 주석
        if verbosity in ['detailed', 'verbose']:
            inline_comments = await self._generate_inline_comments(
                analysis.complex_blocks,
                language
            )
            comments.extend(inline_comments)

        # 4. 주석을 코드에 삽입
        commented_code = await self._insert_comments(
            code,
            comments,
            language
        )

        return commented_code, comments

    async def _generate_function_comments(
        self,
        func_info: FunctionInfo,
        style: str,
        verbosity: str
    ) -> List[GeneratedComment]:
        """함수 주석 생성"""

        comments = []

        # Docstring 생성
        context = CommentContext(
            code_element='function',
            name=func_info.name,
            signature=func_info.signature,
            complexity=func_info.complexity,
            dependencies=func_info.dependencies,
            side_effects=func_info.side_effects,
            return_type=func_info.return_type,
            parameters=func_info.parameters
        )

        docstring = await self.docstring_generator.generate(
            context,
            style,
            verbosity
        )

        comments.append(GeneratedComment(
            type=CommentType.DOCSTRING,
            content=docstring,
            line=func_info.start_line,
            format=style,
            metadata={'function': func_info.name}
        ))

        # 복잡한 파라미터에 대한 추가 설명
        if verbosity == 'verbose' and func_info.complex_params:
            for param in func_info.complex_params:
                param_comment = await self._generate_parameter_comment(
                    param,
                    func_info
                )
                comments.append(param_comment)

        # TODO/FIXME 마커 추가 (필요한 경우)
        if func_info.needs_refactoring:
            todo_comment = GeneratedComment(
                type=CommentType.TODO,
                content=f"TODO: Refactor this function - complexity score: {func_info.complexity}",
                line=func_info.start_line - 1,
                format='inline',
                metadata={'reason': 'high_complexity'}
            )
            comments.append(todo_comment)

        return comments

class DocstringGenerator:
    """Docstring 생성기"""

    def __init__(self):
        self.templates = self._load_docstring_templates()
        self.example_generator = ExampleGenerator()

    async def generate(
        self,
        context: CommentContext,
        style: str,
        verbosity: str
    ) -> str:
        """Docstring 생성"""

        if style == 'google':
            return await self._generate_google_style(context, verbosity)
        elif style == 'numpy':
            return await self._generate_numpy_style(context, verbosity)
        elif style == 'sphinx':
            return await self._generate_sphinx_style(context, verbosity)
        elif style == 'jsdoc':
            return await self._generate_jsdoc_style(context, verbosity)
        else:
            return await self._generate_auto_style(context, verbosity)

    async def _generate_google_style(
        self,
        context: CommentContext,
        verbosity: str
    ) -> str:
        """Google 스타일 docstring"""

        lines = []

        # 요약
        summary = await self._generate_summary(context)
        lines.append(summary)

        # 상세 설명 (verbose 모드)
        if verbosity in ['detailed', 'verbose']:
            description = await self._generate_detailed_description(context)
            if description:
                lines.append("")
                lines.append(description)

        # Args 섹션
        if context.parameters:
            lines.append("")
            lines.append("Args:")
            for param in context.parameters:
                param_desc = await self._generate_parameter_description(param)
                lines.append(f"    {param['name']} ({param.get('type', 'Any')}): {param_desc}")

        # Returns 섹션
        if context.return_type and context.return_type != 'None':
            lines.append("")
            lines.append("Returns:")
            return_desc = await self._generate_return_description(context)
            lines.append(f"    {context.return_type}: {return_desc}")

        # Raises 섹션
        if context.code_element in ['function', 'method']:
            exceptions = await self._detect_exceptions(context)
            if exceptions:
                lines.append("")
                lines.append("Raises:")
                for exc in exceptions:
                    lines.append(f"    {exc['type']}: {exc['description']}")

        # Examples 섹션 (verbose 모드)
        if verbosity == 'verbose':
            examples = await self.example_generator.generate_docstring_examples(context)
            if examples:
                lines.append("")
                lines.append("Examples:")
                for example in examples:
                    lines.append(f"    >>> {example}")

        # Note 섹션 (부가 정보)
        if context.side_effects:
            lines.append("")
            lines.append("Note:")
            for effect in context.side_effects:
                lines.append(f"    {effect}")

        return '\n'.join(lines)

    async def _generate_numpy_style(
        self,
        context: CommentContext,
        verbosity: str
    ) -> str:
        """NumPy 스타일 docstring"""

        lines = []

        # 요약
        summary = await self._generate_summary(context)
        lines.append(summary)

        # 확장 요약
        if verbosity in ['detailed', 'verbose']:
            lines.append("")
            lines.append(await self._generate_detailed_description(context))

        # Parameters 섹션
        if context.parameters:
            lines.append("")
            lines.append("Parameters")
            lines.append("----------")
            for param in context.parameters:
                param_type = param.get('type', 'Any')
                param_desc = await self._generate_parameter_description(param)
                lines.append(f"{param['name']} : {param_type}")
                lines.append(f"    {param_desc}")

        # Returns 섹션
        if context.return_type and context.return_type != 'None':
            lines.append("")
            lines.append("Returns")
            lines.append("-------")
            lines.append(f"{context.return_type}")
            lines.append(f"    {await self._generate_return_description(context)}")

        # See Also 섹션
        if context.dependencies:
            lines.append("")
            lines.append("See Also")
            lines.append("--------")
            for dep in context.dependencies[:3]:  # 최대 3개
                lines.append(f"{dep} : Related functionality")

        return '\n'.join(lines)

    async def _generate_jsdoc_style(
        self,
        context: CommentContext,
        verbosity: str
    ) -> str:
        """JSDoc 스타일 주석"""

        lines = []

        # 설명
        lines.append(f" * {await self._generate_summary(context)}")

        if verbosity in ['detailed', 'verbose']:
            description = await self._generate_detailed_description(context)
            if description:
                lines.append(" * ")
                for line in description.split('\n'):
                    lines.append(f" * {line}")

        # @param 태그
        for param in context.parameters:
            param_type = param.get('type', '*')
            param_desc = await self._generate_parameter_description(param)
            lines.append(f" * @param {{{param_type}}} {param['name']} - {param_desc}")

        # @returns 태그
        if context.return_type and context.return_type != 'void':
            return_desc = await self._generate_return_description(context)
            lines.append(f" * @returns {{{context.return_type}}} {return_desc}")

        # @throws 태그
        exceptions = await self._detect_exceptions(context)
        for exc in exceptions:
            lines.append(f" * @throws {{{exc['type']}}} {exc['description']}")

        # @example 태그
        if verbosity == 'verbose':
            examples = await self.example_generator.generate_docstring_examples(context)
            if examples:
                lines.append(" * @example")
                for example in examples:
                    lines.append(f" * {example}")

        # @since, @deprecated 등 추가 태그
        if context.metadata.get('since'):
            lines.append(f" * @since {context.metadata['since']}")

        return '\n'.join(lines)

class InlineCommentGenerator:
    """인라인 주석 생성기"""

    async def generate_inline_comments(
        self,
        complex_blocks: List[ComplexBlock],
        language: str
    ) -> List[GeneratedComment]:
        """복잡한 코드 블록에 대한 인라인 주석 생성"""

        comments = []

        for block in complex_blocks:
            if block.type == 'algorithm':
                comment = await self._comment_algorithm(block)
            elif block.type == 'business_logic':
                comment = await self._comment_business_logic(block)
            elif block.type == 'optimization':
                comment = await self._comment_optimization(block)
            elif block.type == 'workaround':
                comment = await self._comment_workaround(block)
            else:
                comment = await self._comment_complex_logic(block)

            comments.append(comment)

        return comments

    async def _comment_algorithm(self, block: ComplexBlock) -> GeneratedComment:
        """알고리즘 주석"""

        # 알고리즘 분석
        algorithm_info = await self._analyze_algorithm(block.code)

        comment_lines = []
        comment_lines.append(f"Algorithm: {algorithm_info.name}")
        comment_lines.append(f"Time Complexity: {algorithm_info.time_complexity}")
        comment_lines.append(f"Space Complexity: {algorithm_info.space_complexity}")

        if algorithm_info.description:
            comment_lines.append("")
            comment_lines.append(algorithm_info.description)

        return GeneratedComment(
            type=CommentType.BLOCK,
            content='\n'.join(comment_lines),
            line=block.start_line - 1,
            format='block',
            metadata={'algorithm': algorithm_info.name}
        )

    async def _comment_business_logic(self, block: ComplexBlock) -> GeneratedComment:
        """비즈니스 로직 주석"""

        # 비즈니스 규칙 추출
        rules = await self._extract_business_rules(block.code)

        comment_lines = []
        comment_lines.append("Business Logic:")
        for rule in rules:
            comment_lines.append(f"- {rule}")

        return GeneratedComment(
            type=CommentType.BLOCK,
            content='\n'.join(comment_lines),
            line=block.start_line - 1,
            format='block',
            metadata={'business_rules': rules}
        )

class AICommentGenerator:
    """AI 기반 주석 생성기"""

    def __init__(self):
        self.code_understanding_model = CodeUnderstandingModel()
        self.comment_generation_model = CommentGenerationModel()

    async def generate_intelligent_comments(
        self,
        code: str,
        context: Dict[str, Any]
    ) -> List[GeneratedComment]:
        """AI를 활용한 지능적 주석 생성"""

        # 1. 코드 이해
        understanding = await self.code_understanding_model.understand(
            code,
            context
        )

        # 2. 주석이 필요한 부분 식별
        comment_points = await self._identify_comment_points(
            understanding,
            code
        )

        # 3. 각 포인트에 대한 주석 생성
        comments = []
        for point in comment_points:
            comment_content = await self.comment_generation_model.generate(
                point,
                understanding,
                context
            )

            comment = GeneratedComment(
                type=self._determine_comment_type(point),
                content=comment_content,
                line=point.line,
                format='auto',
                metadata={
                    'confidence': point.confidence,
                    'reason': point.reason
                }
            )
            comments.append(comment)

        return comments

    async def _identify_comment_points(
        self,
        understanding: CodeUnderstanding,
        code: str
    ) -> List[CommentPoint]:
        """주석이 필요한 지점 식별"""

        points = []

        # 1. 복잡한 알고리즘
        if understanding.has_complex_algorithm:
            points.extend(understanding.algorithm_points)

        # 2. 비직관적인 로직
        if understanding.has_non_intuitive_logic:
            points.extend(understanding.non_intuitive_points)

        # 3. 성능 최적화 코드
        if understanding.has_optimizations:
            points.extend(understanding.optimization_points)

        # 4. 외부 의존성
        if understanding.has_external_dependencies:
            points.extend(understanding.dependency_points)

        # 5. 에지 케이스 처리
        if understanding.has_edge_cases:
            points.extend(understanding.edge_case_points)

        return points

# 주석 삽입기
class CommentInserter:
    """주석을 코드에 삽입"""

    def insert_comments(
        self,
        code: str,
        comments: List[GeneratedComment],
        language: str
    ) -> str:
        """주석을 코드에 삽입"""

        # 라인별로 코드 분리
        lines = code.split('\n')

        # 주석을 라인 번호순으로 정렬 (역순)
        sorted_comments = sorted(
            comments,
            key=lambda c: c.line,
            reverse=True
        )

        # 각 주석 삽입
        for comment in sorted_comments:
            if comment.type == CommentType.DOCSTRING:
                lines = self._insert_docstring(
                    lines,
                    comment,
                    language
                )
            elif comment.type == CommentType.INLINE:
                lines = self._insert_inline_comment(
                    lines,
                    comment,
                    language
                )
            elif comment.type == CommentType.BLOCK:
                lines = self._insert_block_comment(
                    lines,
                    comment,
                    language
                )

        return '\n'.join(lines)

    def _insert_docstring(
        self,
        lines: List[str],
        comment: GeneratedComment,
        language: str
    ) -> List[str]:
        """Docstring 삽입"""

        if language == 'python':
            # 함수/클래스 정의 다음 라인에 삽입
            indent = self._get_indentation(lines[comment.line - 1])
            docstring_lines = [
                f'{indent}    """',
                *[f'{indent}    {line}' for line in comment.content.split('\n')],
                f'{indent}    """'
            ]

            # 삽입 위치 찾기 (콜론 다음 라인)
            insert_line = comment.line
            while insert_line < len(lines) and not lines[insert_line - 1].strip().endswith(':'):
                insert_line += 1

            lines[insert_line:insert_line] = docstring_lines

        elif language in ['javascript', 'typescript']:
            # 함수 정의 바로 위에 삽입
            indent = self._get_indentation(lines[comment.line - 1])
            jsdoc_lines = [
                f'{indent}/**',
                *[f'{indent}{line}' for line in comment.content.split('\n')],
                f'{indent} */'
            ]

            lines[comment.line - 1:comment.line - 1] = jsdoc_lines

        return lines
```

**검증 기준**:

- [ ] 다양한 주석 스타일 지원
- [ ] 컨텍스트 기반 주석 생성
- [ ] AI 활용 지능적 주석
- [ ] 복잡도 기반 주석 추가

#### SubTask 4.65.3: 사용자 매뉴얼 생성

**담당자**: 기술 문서 작성자  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/generation/user_manual_generator.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import markdown
from PIL import Image
import io

@dataclass
class ManualSection:
    title: str
    content: str
    level: int
    subsections: List['ManualSection']
    images: List[ManualImage]
    examples: List[ManualExample]
    tips: List[str]
    warnings: List[str]

@dataclass
class ManualImage:
    caption: str
    path: str
    alt_text: str
    width: Optional[int] = None
    height: Optional[int] = None

@dataclass
class UserManual:
    title: str
    version: str
    introduction: str
    table_of_contents: List[Dict[str, Any]]
    sections: List[ManualSection]
    glossary: Dict[str, str]
    faqs: List[Dict[str, str]]
    troubleshooting: List[Dict[str, Any]]
    appendices: List[ManualSection]

class UserManualGenerator:
    """사용자 매뉴얼 생성기"""

    def __init__(self):
        self.content_analyzer = ContentAnalyzer()
        self.section_generator = SectionGenerator()
        self.screenshot_generator = ScreenshotGenerator()
        self.example_generator = UserExampleGenerator()
        self.formatter = ManualFormatter()

    async def generate_user_manual(
        self,
        application: ApplicationSpec,
        features: List[Feature],
        user_personas: List[UserPersona],
        config: Optional[ManualConfig] = None
    ) -> UserManual:
        """사용자 매뉴얼 생성"""

        # 1. 콘텐츠 구조 분석
        content_structure = await self.content_analyzer.analyze_structure(
            application,
            features,
            user_personas
        )

        # 2. 소개 섹션 생성
        introduction = await self._generate_introduction(
            application,
            user_personas
        )

        # 3. 각 기능에 대한 섹션 생성
        sections = []

        # 시작하기 섹션
        getting_started = await self._generate_getting_started_section(
            application,
            user_personas[0] if user_personas else None
        )
        sections.append(getting_started)

        # 주요 기능 섹션들
        for feature in features:
            section = await self._generate_feature_section(
                feature,
                application,
                user_personas
            )
            sections.append(section)

        # 고급 기능 섹션
        if any(f.complexity == 'advanced' for f in features):
            advanced_section = await self._generate_advanced_section(
                [f for f in features if f.complexity == 'advanced'],
                application
            )
            sections.append(advanced_section)

        # 4. 부록 생성
        appendices = await self._generate_appendices(
            application,
            features
        )

        # 5. FAQ 생성
        faqs = await self._generate_faqs(features, user_personas)

        # 6. 문제 해결 가이드
        troubleshooting = await self._generate_troubleshooting_guide(
            features,
            application
        )

        # 7. 용어집 생성
        glossary = await self._generate_glossary(
            application,
            features
        )

        # 8. 목차 생성
        toc = self._generate_table_of_contents(sections)

        return UserManual(
            title=f"{application.name} 사용자 매뉴얼",
            version=application.version,
            introduction=introduction,
            table_of_contents=toc,
            sections=sections,
            glossary=glossary,
            faqs=faqs,
            troubleshooting=troubleshooting,
            appendices=appendices
        )

    async def _generate_getting_started_section(
        self,
        application: ApplicationSpec,
        primary_persona: Optional[UserPersona]
    ) -> ManualSection:
        """시작하기 섹션 생성"""

        subsections = []

        # 시스템 요구사항
        requirements = ManualSection(
            title="시스템 요구사항",
            content=self._format_system_requirements(application.requirements),
            level=2,
            subsections=[],
            images=[],
            examples=[],
            tips=[],
            warnings=[]
        )
        subsections.append(requirements)

        # 설치 가이드
        installation = await self._generate_installation_guide(
            application,
            primary_persona
        )
        subsections.append(installation)

        # 첫 실행
        first_run = await self._generate_first_run_guide(
            application,
            primary_persona
        )
        subsections.append(first_run)

        # 기본 설정
        basic_setup = await self._generate_basic_setup_guide(
            application,
            primary_persona
        )
        subsections.append(basic_setup)

        return ManualSection(
            title="시작하기",
            content="이 섹션에서는 애플리케이션을 처음 사용하는 방법을 안내합니다.",
            level=1,
            subsections=subsections,
            images=[],
            examples=[],
            tips=[
                "처음 사용하신다면 이 섹션을 순서대로 따라해 주세요.",
                "문제가 발생하면 문제 해결 섹션을 참조하세요."
            ],
            warnings=[]
        )

    async def _generate_feature_section(
        self,
        feature: Feature,
        application: ApplicationSpec,
        user_personas: List[UserPersona]
    ) -> ManualSection:
        """기능별 섹션 생성"""

        # 기능 설명
        description = await self._generate_feature_description(
            feature,
            user_personas
        )

        # 스크린샷 생성
        screenshots = await self.screenshot_generator.generate_feature_screenshots(
            feature,
            application
        )

        # 사용 예제 생성
        examples = await self.example_generator.generate_feature_examples(
            feature,
            user_personas
        )

        # 하위 섹션들
        subsections = []

        # 기본 사용법
        basic_usage = await self._generate_basic_usage_section(
            feature,
            screenshots[:2]  # 처음 2개 스크린샷
        )
        subsections.append(basic_usage)

        # 고급 옵션 (있는 경우)
        if feature.advanced_options:
            advanced_options = await self._generate_advanced_options_section(
                feature,
                screenshots[2:]  # 나머지 스크린샷
            )
            subsections.append(advanced_options)

        # 팁과 트릭
        tips = await self._generate_tips_section(feature, user_personas)
        warnings = await self._generate_warnings_section(feature)

        return ManualSection(
            title=feature.display_name,
            content=description,
            level=1,
            subsections=subsections,
            images=screenshots,
            examples=examples,
            tips=tips,
            warnings=warnings
        )

    async def _generate_basic_usage_section(
        self,
        feature: Feature,
        screenshots: List[ManualImage]
    ) -> ManualSection:
        """기본 사용법 섹션"""

        steps = []

        # 단계별 가이드 생성
        for i, step in enumerate(feature.basic_workflow):
            step_content = f"{i+1}. {step.description}\n"

            # 상세 설명 추가
            if step.details:
                step_content += f"   - {step.details}\n"

            # 스크린샷 참조
            if step.screenshot_index < len(screenshots):
                step_content += f"   (그림 {step.screenshot_index + 1} 참조)\n"

            steps.append(step_content)

        content = '\n'.join(steps)

        return ManualSection(
            title="기본 사용법",
            content=content,
            level=2,
            subsections=[],
            images=screenshots,
            examples=[],
            tips=feature.basic_tips,
            warnings=[]
        )

class ScreenshotGenerator:
    """스크린샷 생성기"""

    async def generate_feature_screenshots(
        self,
        feature: Feature,
        application: ApplicationSpec
    ) -> List[ManualImage]:
        """기능별 스크린샷 생성"""

        screenshots = []

        # 각 주요 UI 상태에 대한 스크린샷
        for ui_state in feature.ui_states:
            # 스크린샷 캡처 시뮬레이션
            screenshot_path = await self._capture_screenshot(
                application,
                feature,
                ui_state
            )

            # 주석 추가
            annotated_path = await self._annotate_screenshot(
                screenshot_path,
                ui_state.annotations
            )

            screenshot = ManualImage(
                caption=ui_state.caption,
                path=annotated_path,
                alt_text=ui_state.alt_text,
                width=1200,
                height=800
            )
            screenshots.append(screenshot)

        return screenshots

    async def _annotate_screenshot(
        self,
        screenshot_path: str,
        annotations: List[Annotation]
    ) -> str:
        """스크린샷에 주석 추가"""

        # 이미지 로드
        img = Image.open(screenshot_path)

        # 주석 추가 (화살표, 박스, 텍스트 등)
        annotated = self._add_annotations(img, annotations)

        # 저장
        output_path = screenshot_path.replace('.png', '_annotated.png')
        annotated.save(output_path)

        return output_path

class ManualFormatter:
    """매뉴얼 포맷터"""

    def format_to_html(self, manual: UserManual) -> str:
        """HTML 형식으로 변환"""

        html_parts = []

        # HTML 헤더
        html_parts.append(self._generate_html_header(manual))

        # 네비게이션
        html_parts.append(self._generate_navigation(manual))

        # 메인 콘텐츠
        html_parts.append('<main class="manual-content">')

        # 소개
        html_parts.append(f'<section class="introduction">')
        html_parts.append(f'<h1>{manual.title}</h1>')
        html_parts.append(f'<p class="version">버전 {manual.version}</p>')
        html_parts.append(markdown.markdown(manual.introduction))
        html_parts.append('</section>')

        # 목차
        html_parts.append(self._generate_toc_html(manual.table_of_contents))

        # 각 섹션
        for section in manual.sections:
            html_parts.append(self._format_section_html(section))

        # FAQ
        if manual.faqs:
            html_parts.append(self._format_faq_html(manual.faqs))

        # 문제 해결
        if manual.troubleshooting:
            html_parts.append(self._format_troubleshooting_html(manual.troubleshooting))

        # 용어집
        if manual.glossary:
            html_parts.append(self._format_glossary_html(manual.glossary))

        # 부록
        for appendix in manual.appendices:
            html_parts.append(self._format_section_html(appendix))

        html_parts.append('</main>')

        # HTML 푸터
        html_parts.append(self._generate_html_footer())

        return '\n'.join(html_parts)

    def format_to_pdf(self, manual: UserManual) -> bytes:
        """PDF 형식으로 변환"""

        # HTML 생성
        html_content = self.format_to_html(manual)

        # PDF 변환 (wkhtmltopdf 또는 weasyprint 사용)
        pdf_bytes = self._convert_html_to_pdf(html_content)

        return pdf_bytes

    def format_to_markdown(self, manual: UserManual) -> str:
        """Markdown 형식으로 변환"""

        md_parts = []

        # 제목과 버전
        md_parts.append(f"# {manual.title}")
        md_parts.append(f"\n**버전**: {manual.version}\n")

        # 소개
        md_parts.append("## 소개")
        md_parts.append(manual.introduction)

        # 목차
        md_parts.append("\n## 목차")
        for item in manual.table_of_contents:
            indent = "  " * (item['level'] - 1)
            md_parts.append(f"{indent}- [{item['title']}](#{item['anchor']})")

        # 각 섹션
        for section in manual.sections:
            md_parts.append(self._format_section_markdown(section))

        # FAQ
        if manual.faqs:
            md_parts.append("\n## 자주 묻는 질문")
            for faq in manual.faqs:
                md_parts.append(f"\n### Q: {faq['question']}")
                md_parts.append(f"A: {faq['answer']}")

        # 문제 해결
        if manual.troubleshooting:
            md_parts.append("\n## 문제 해결")
            for issue in manual.troubleshooting:
                md_parts.append(f"\n### 문제: {issue['problem']}")
                md_parts.append(f"**증상**: {issue['symptoms']}")
                md_parts.append(f"**해결 방법**:")
                for step in issue['solution_steps']:
                    md_parts.append(f"1. {step}")

        # 용어집
        if manual.glossary:
            md_parts.append("\n## 용어집")
            for term, definition in sorted(manual.glossary.items()):
                md_parts.append(f"\n**{term}**: {definition}")

        return '\n'.join(md_parts)

    def _generate_html_header(self, manual: UserManual) -> str:
        """HTML 헤더 생성"""

        return f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{manual.title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }}

        .manual-header {{
            background: #f8f9fa;
            padding: 2rem;
            border-radius: 8px;
            margin-bottom: 2rem;
        }}

        .toc {{
            background: #fff;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 1.5rem;
            margin: 2rem 0;
        }}

        .section {{
            margin: 3rem 0;
        }}

        .screenshot {{
            max-width: 100%;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            margin: 1rem 0;
        }}

        .tip {{
            background: #d4edda;
            border-left: 4px solid #28a745;
            padding: 1rem;
            margin: 1rem 0;
        }}

        .warning {{
            background: #f8d7da;
            border-left: 4px solid #dc3545;
            padding: 1rem;
            margin: 1rem 0;
        }}

        .example {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 1rem;
            margin: 1rem 0;
        }}

        code {{
            background: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
    </style>
</head>
<body>
"""
```

**검증 기준**:

- [ ] 사용자 친화적 콘텐츠
- [ ] 단계별 가이드 포함
- [ ] 스크린샷 자동 생성
- [ ] 다양한 출력 형식

#### SubTask 4.65.4: 기술 문서 템플릿

**담당자**: 문서화 전문가  
**예상 소요시간**: 8시간

**작업 내용**:

```python
# backend/src/agents/implementations/generation/tech_doc_templates.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class DocumentTemplate:
    name: str
    type: str  # 'architecture', 'api', 'database', 'deployment', 'security'
    sections: List[TemplateSection]
    metadata: Dict[str, Any]
    examples: Dict[str, str]
    guidelines: List[str]

@dataclass
class TemplateSection:
    title: str
    required: bool
    description: str
    content_template: str
    subsections: List['TemplateSection']
    placeholders: Dict[str, PlaceholderInfo]

class TechnicalDocumentTemplates:
    """기술 문서 템플릿 관리"""

    def __init__(self):
        self.templates = self._load_templates()
        self.placeholder_resolver = PlaceholderResolver()
        self.content_generator = ContentGenerator()

    def get_template(self, doc_type: str) -> DocumentTemplate:
        """문서 타입별 템플릿 반환"""

        return self.templates.get(doc_type)

    def _load_templates(self) -> Dict[str, DocumentTemplate]:
        """모든 템플릿 로드"""

        return {
            'architecture': self._create_architecture_template(),
            'api': self._create_api_template(),
            'database': self._create_database_template(),
            'deployment': self._create_deployment_template(),
            'security': self._create_security_template(),
            'testing': self._create_testing_template(),
            'maintenance': self._create_maintenance_template()
        }

    def _create_architecture_template(self) -> DocumentTemplate:
        """아키텍처 문서 템플릿"""

        sections = [
            TemplateSection(
                title="개요",
                required=True,
                description="시스템 아키텍처의 전반적인 개요",
                content_template="""
## 개요

### 목적
{purpose}

### 범위
{scope}

### 주요 이해관계자
{stakeholders}

### 문서 규약
{conventions}
""",
                subsections=[],
                placeholders={
                    'purpose': PlaceholderInfo('시스템의 목적과 비즈니스 목표'),
                    'scope': PlaceholderInfo('아키텍처 문서의 범위'),
                    'stakeholders': PlaceholderInfo('주요 이해관계자 목록'),
                    'conventions': PlaceholderInfo('문서에서 사용하는 규약')
                }
            ),
            TemplateSection(
                title="아키텍처 원칙",
                required=True,
                description="시스템 설계의 핵심 원칙",
                content_template="""
## 아키텍처 원칙

### 설계 원칙
{design_principles}

### 기술 표준
{tech_standards}

### 제약사항
{constraints}
""",
                subsections=[],
                placeholders={
                    'design_principles': PlaceholderInfo('핵심 설계 원칙 목록'),
                    'tech_standards': PlaceholderInfo('준수해야 할 기술 표준'),
                    'constraints': PlaceholderInfo('기술적/비즈니스적 제약사항')
                }
            ),
            TemplateSection(
                title="시스템 컨텍스트",
                required=True,
                description="시스템의 외부 환경과 상호작용",
                content_template="""
## 시스템 컨텍스트

### 비즈니스 컨텍스트
{business_context}

### 기술 컨텍스트
{technical_context}

### 외부 인터페이스
{external_interfaces}

### 시스템 경계
{system_boundaries}
""",
                subsections=[],
                placeholders={
                    'business_context': PlaceholderInfo('비즈니스 관점의 시스템 위치'),
                    'technical_context': PlaceholderInfo('기술적 환경과 통합 포인트'),
                    'external_interfaces': PlaceholderInfo('외부 시스템과의 인터페이스'),
                    'system_boundaries': PlaceholderInfo('시스템의 범위와 경계')
                }
            ),
            TemplateSection(
                title="컴포넌트 뷰",
                required=True,
                description="시스템의 주요 컴포넌트와 관계",
                content_template="""
## 컴포넌트 뷰

### 컴포넌트 다이어그램
{component_diagram}

### 주요 컴포넌트
{components}

### 컴포넌트 간 관계
{relationships}

### 데이터 흐름
{data_flow}
""",
                subsections=[
                    TemplateSection(
                        title="프론트엔드 컴포넌트",
                        required=False,
                        description="UI/UX 컴포넌트 상세",
                        content_template="{frontend_components}",
                        subsections=[],
                        placeholders={}
                    ),
                    TemplateSection(
                        title="백엔드 컴포넌트",
                        required=False,
                        description="서버 측 컴포넌트 상세",
                        content_template="{backend_components}",
                        subsections=[],
                        placeholders={}
                    )
                ],
                placeholders={
                    'component_diagram': PlaceholderInfo('컴포넌트 다이어그램 이미지/설명'),
                    'components': PlaceholderInfo('각 컴포넌트의 역할과 책임'),
                    'relationships': PlaceholderInfo('컴포넌트 간 의존성과 통신'),
                    'data_flow': PlaceholderInfo('시스템 내 데이터 흐름')
                }
            ),
            TemplateSection(
                title="배포 뷰",
                required=True,
                description="시스템의 물리적 배포 구조",
                content_template="""
## 배포 뷰

### 인프라 아키텍처
{infrastructure}

### 네트워크 토폴로지
{network_topology}

### 배포 환경
{deployment_environments}

### 확장성 전략
{scalability}
""",
                subsections=[],
                placeholders={
                    'infrastructure': PlaceholderInfo('인프라 구성 요소'),
                    'network_topology': PlaceholderInfo('네트워크 구성도'),
                    'deployment_environments': PlaceholderInfo('개발/스테이징/운영 환경'),
                    'scalability': PlaceholderInfo('수평/수직 확장 전략')
                }
            ),
            TemplateSection(
                title="품질 속성",
                required=True,
                description="비기능적 요구사항과 품질 목표",
                content_template="""
## 품질 속성

### 성능 요구사항
{performance}

### 보안 요구사항
{security}

### 가용성 요구사항
{availability}

### 유지보수성
{maintainability}
""",
                subsections=[],
                placeholders={
                    'performance': PlaceholderInfo('응답시간, 처리량 등'),
                    'security': PlaceholderInfo('보안 요구사항과 대책'),
                    'availability': PlaceholderInfo('가동시간 목표와 전략'),
                    'maintainability': PlaceholderInfo('유지보수 용이성 전략')
                }
            )
        ]

        return DocumentTemplate(
            name="Software Architecture Document",
            type="architecture",
            sections=sections,
            metadata={
                'version': '2.0',
                'based_on': 'ISO/IEC/IEEE 42010',
                'last_updated': '2024-01-01'
            },
            examples={
                'microservices': 'examples/microservices_architecture.md',
                'monolithic': 'examples/monolithic_architecture.md',
                'serverless': 'examples/serverless_architecture.md'
            },
            guidelines=[
                "다이어그램은 C4 모델 또는 UML을 사용하세요",
                "각 섹션은 독립적으로 이해 가능해야 합니다",
                "기술적 결정사항에는 근거를 포함하세요",
                "버전 관리를 통해 변경 이력을 추적하세요"
            ]
        )

    def _create_api_template(self) -> DocumentTemplate:
        """API 문서 템플릿"""

        sections = [
            TemplateSection(
                title="API 개요",
                required=True,
                description="API의 목적과 주요 기능",
                content_template="""
# {api_name} API Documentation

## 개요
{overview}

## 버전 정보
- 현재 버전: {version}
- 릴리즈 날짜: {release_date}
- 이전 버전: {previous_versions}

## 기본 URL
```

{base_url}

````

## 지원 형식
- Request: {request_formats}
- Response: {response_formats}
""",
                subsections=[],
                placeholders={
                    'api_name': PlaceholderInfo('API 이름'),
                    'overview': PlaceholderInfo('API의 목적과 주요 기능'),
                    'version': PlaceholderInfo('현재 API 버전'),
                    'release_date': PlaceholderInfo('릴리즈 날짜'),
                    'previous_versions': PlaceholderInfo('이전 버전 목록'),
                    'base_url': PlaceholderInfo('API 기본 URL'),
                    'request_formats': PlaceholderInfo('지원하는 요청 형식'),
                    'response_formats': PlaceholderInfo('지원하는 응답 형식')
                }
            ),
            TemplateSection(
                title="인증",
                required=True,
                description="API 인증 방법",
                content_template="""
## 인증

### 인증 방식
{auth_method}

### 인증 프로세스
{auth_process}

### 인증 예제
```{code_lang}
{auth_example}
````

### 에러 처리

{auth_errors}
""",
subsections=[],
placeholders={
'auth_method': PlaceholderInfo('사용하는 인증 방식 (OAuth, API Key 등)'),
'auth_process': PlaceholderInfo('인증 프로세스 설명'),
'code_lang': PlaceholderInfo('예제 코드 언어'),
'auth_example': PlaceholderInfo('인증 코드 예제'),
'auth_errors': PlaceholderInfo('인증 관련 에러 코드와 메시지')
}
),
TemplateSection(
title="엔드포인트",
required=True,
description="API 엔드포인트 상세",
content_template="""

## 엔드포인트

{endpoints}
""",
subsections=[
TemplateSection(
title="엔드포인트 상세",
required=False,
description="개별 엔드포인트 문서",
content_template="""

### {endpoint_name}

**{method}** `{path}`

#### 설명

{description}

#### 파라미터

{parameters}

#### 요청 예제

```{request_lang}
{request_example}
```

#### 응답 예제

```json
{response_example}
```

#### 에러 코드

{error_codes}
""",
subsections=[],
placeholders={
'endpoint_name': PlaceholderInfo('엔드포인트 이름'),
'method': PlaceholderInfo('HTTP 메서드'),
'path': PlaceholderInfo('엔드포인트 경로'),
'description': PlaceholderInfo('엔드포인트 설명'),
'parameters': PlaceholderInfo('파라미터 테이블'),
'request_lang': PlaceholderInfo('요청 예제 언어'),
'request_example': PlaceholderInfo('요청 예제 코드'),
'response_example': PlaceholderInfo('응답 예제 JSON'),
'error_codes': PlaceholderInfo('에러 코드 테이블')
}
)
],
placeholders={
'endpoints': PlaceholderInfo('엔드포인트 목록')
}
)
]

        return DocumentTemplate(
            name="API Documentation",
            type="api",
            sections=sections,
            metadata={
                'format': 'OpenAPI 3.0 compatible',
                'tools': ['Swagger', 'Postman', 'Insomnia']
            },
            examples={
                'rest': 'examples/rest_api.md',
                'graphql': 'examples/graphql_api.md',
                'grpc': 'examples/grpc_api.md'
            },
            guidelines=[
                "모든 엔드포인트에 대한 예제를 포함하세요",
                "에러 응답 형식을 명확히 문서화하세요",
                "Rate limiting 정보를 포함하세요",
                "변경 로그를 유지관리하세요"
            ]
        )

    def _create_database_template(self) -> DocumentTemplate:
        """데이터베이스 문서 템플릿"""

        sections = [
            TemplateSection(
                title="데이터베이스 개요",
                required=True,
                description="데이터베이스 시스템 개요",
                content_template="""

# 데이터베이스 설계 문서

## 개요

{overview}

## 데이터베이스 시스템

- DBMS: {dbms}
- 버전: {version}
- 호스팅: {hosting}

## 설계 원칙

{design_principles}

## 명명 규칙

{naming_conventions}
""",
subsections=[],
placeholders={
'overview': PlaceholderInfo('데이터베이스의 목적과 범위'),
'dbms': PlaceholderInfo('사용하는 DBMS'),
'version': PlaceholderInfo('DBMS 버전'),
'hosting': PlaceholderInfo('호스팅 환경'),
'design_principles': PlaceholderInfo('데이터베이스 설계 원칙'),
'naming_conventions': PlaceholderInfo('테이블, 컬럼 등의 명명 규칙')
}
),
TemplateSection(
title="데이터 모델",
required=True,
description="논리적/물리적 데이터 모델",
content_template="""

## 데이터 모델

### ER 다이어그램

{er_diagram}

### 주요 엔티티

{entities}

### 관계 정의

{relationships}

### 데이터 딕셔너리

{data_dictionary}
""",
subsections=[
TemplateSection(
title="테이블 상세",
required=False,
description="각 테이블의 상세 명세",
content_template="""

#### {table_name}

**설명**: {table_description}

**컬럼**:
{columns}

**인덱스**:
{indexes}

**제약조건**:
{constraints}

**트리거**:
{triggers}
""",
subsections=[],
placeholders={
'table_name': PlaceholderInfo('테이블 이름'),
'table_description': PlaceholderInfo('테이블 설명'),
'columns': PlaceholderInfo('컬럼 명세 테이블'),
'indexes': PlaceholderInfo('인덱스 정보'),
'constraints': PlaceholderInfo('제약조건 목록'),
'triggers': PlaceholderInfo('트리거 정보')
}
)
],
placeholders={
'er_diagram': PlaceholderInfo('ER 다이어그램 이미지/설명'),
'entities': PlaceholderInfo('주요 엔티티 목록과 설명'),
'relationships': PlaceholderInfo('엔티티 간 관계 설명'),
'data_dictionary': PlaceholderInfo('데이터 딕셔너리 링크/내용')
}
),
TemplateSection(
title="성능 고려사항",
required=True,
description="데이터베이스 성능 최적화",
content_template="""

## 성능 고려사항

### 인덱싱 전략

{indexing_strategy}

### 파티셔닝

{partitioning}

### 쿼리 최적화

{query_optimization}

### 캐싱 전략

{caching}
""",
subsections=[],
placeholders={
'indexing_strategy': PlaceholderInfo('인덱스 설계 전략'),
'partitioning': PlaceholderInfo('테이블 파티셔닝 전략'),
'query_optimization': PlaceholderInfo('쿼리 최적화 가이드'),
'caching': PlaceholderInfo('캐싱 전략과 구현')
}
)
]

        return DocumentTemplate(
            name="Database Design Document",
            type="database",
            sections=sections,
            metadata={
                'standards': ['SQL:2016', 'ISO/IEC 9075'],
                'modeling_tools': ['ERwin', 'MySQL Workbench', 'dbdiagram.io']
            },
            examples={
                'relational': 'examples/relational_db.md',
                'nosql': 'examples/nosql_db.md',
                'graph': 'examples/graph_db.md'
            },
            guidelines=[
                "정규화 수준을 명시하세요",
                "백업 및 복구 전략을 포함하세요",
                "데이터 보안 정책을 문서화하세요",
                "마이그레이션 계획을 포함하세요"
            ]
        )

# 문서 생성기

class DocumentGenerator:
"""템플릿 기반 문서 생성기"""

    def __init__(self):
        self.template_manager = TechnicalDocumentTemplates()
        self.content_filler = ContentFiller()
        self.validator = DocumentValidator()

    async def generate_document(
        self,
        doc_type: str,
        project_info: ProjectInfo,
        custom_content: Optional[Dict[str, Any]] = None
    ) -> GeneratedDocument:
        """문서 생성"""

        # 1. 템플릿 가져오기
        template = self.template_manager.get_template(doc_type)
        if not template:
            raise ValueError(f"Unknown document type: {doc_type}")

        # 2. 프로젝트 정보에서 콘텐츠 추출
        extracted_content = await self.content_filler.extract_content(
            project_info,
            template
        )

        # 3. 사용자 정의 콘텐츠 병합
        if custom_content:
            extracted_content.update(custom_content)

        # 4. 템플릿에 콘텐츠 채우기
        filled_document = await self.content_filler.fill_template(
            template,
            extracted_content
        )

        # 5. 문서 검증
        validation_result = await self.validator.validate(
            filled_document,
            template
        )

        if not validation_result.is_valid:
            # 누락된 콘텐츠 자동 생성 시도
            filled_document = await self._auto_fill_missing(
                filled_document,
                validation_result.missing_sections
            )

        return GeneratedDocument(
            title=filled_document.title,
            content=filled_document.content,
            format=filled_document.format,
            metadata=filled_document.metadata,
            validation=validation_result
        )

    async def _auto_fill_missing(
        self,
        document: Document,
        missing_sections: List[str]
    ) -> Document:
        """누락된 섹션 자동 채우기"""

        for section in missing_sections:
            # AI를 활용한 콘텐츠 생성
            generated_content = await self.content_filler.generate_section(
                section,
                document.context
            )

            document.add_section(section, generated_content)

        return document

````

**검증 기준**:

- [ ] 다양한 문서 타입 템플릿
- [ ] 자동 콘텐츠 채우기
- [ ] 문서 검증 기능
- [ ] 커스터마이징 가능

---

### Task 4.66: 프레임워크별 최적화

#### SubTask 4.66.1: React 최적화

**담당자**: React 전문가
**예상 소요시간**: 12시간

**작업 내용**:

```typescript
// backend/src/agents/implementations/generation/react_optimizer.ts
interface ReactOptimizationRule {
  name: string;
  description: string;
  detector: (code: string, ast: any) => OptimizationOpportunity[];
  optimizer: (code: string, opportunity: OptimizationOpportunity) => string;
  impact: 'high' | 'medium' | 'low';
}

interface OptimizationOpportunity {
  type: string;
  location: CodeLocation;
  description: string;
  suggestion: string;
  autoFixable: boolean;
}

class ReactOptimizer {
  private rules: ReactOptimizationRule[] = [];
  private performanceAnalyzer: PerformanceAnalyzer;
  private bundleAnalyzer: BundleAnalyzer;

  constructor() {
    this.initializeRules();
    this.performanceAnalyzer = new PerformanceAnalyzer();
    this.bundleAnalyzer = new BundleAnalyzer();
  }

  async optimizeReactCode(
    code: string,
    config?: ReactOptimizationConfig
  ): Promise<OptimizedReactCode> {
    // 1. AST 파싱
    const ast = this.parseReactCode(code);

    // 2. 최적화 기회 탐지
    const opportunities = await this.detectOptimizations(code, ast);

    // 3. 최적화 적용
    let optimizedCode = code;
    const appliedOptimizations: AppliedOptimization[] = [];

    for (const opportunity of opportunities) {
      if (config?.autoFix || opportunity.autoFixable) {
        const result = await this.applyOptimization(
          optimizedCode,
          opportunity
        );
        optimizedCode = result.code;
        appliedOptimizations.push(result.optimization);
      }
    }

    // 4. 번들 사이즈 분석
    const bundleAnalysis = await this.bundleAnalyzer.analyze(optimizedCode);

    // 5. 성능 영향 분석
    const performanceImpact = await this.performanceAnalyzer.estimateImpact(
      code,
      optimizedCode
    );

    return {
      originalCode: code,
      optimizedCode,
      opportunities,
      appliedOptimizations,
      bundleAnalysis,
      performanceImpact
    };
  }

  private initializeRules() {
    // React.memo 최적화
    this.rules.push({
      name: 'add-react-memo',
      description: 'Add React.memo to functional components without it',
      detector: this.detectMemoOpportunities.bind(this),
      optimizer: this.addReactMemo.bind(this),
      impact: 'high'
    });

    // useMemo 최적화
    this.rules.push({
      name: 'add-use-memo',
      description: 'Add useMemo for expensive computations',
      detector: this.detectUseMemoOpportunities.bind(this),
      optimizer: this.addUseMemo.bind(this),
      impact: 'medium'
    });

    // useCallback 최적화
    this.rules.push({
      name: 'add-use-callback',
      description: 'Add useCallback for function props',
      detector: this.detectUseCallbackOpportunities.bind(this),
      optimizer: this.addUseCallback.bind(this),
      impact: 'medium'
    });

    // 컴포넌트 분할
    this.rules.push({
      name: 'split-large-components',
      description: 'Split large components into smaller ones',
      detector: this.detectLargeComponents.bind(this),
      optimizer: this.splitComponent.bind(this),
      impact: 'high'
    });

    // Lazy Loading
    this.rules.push({
      name: 'add-lazy-loading',
      description: 'Add lazy loading for heavy components',
      detector: this.detectLazyLoadingOpportunities.bind(this),
      optimizer: this.addLazyLoading.bind(this),
      impact: 'high'
    });

    // 불필요한 re-render 방지
    this.rules.push({
      name: 'prevent-unnecessary-renders',
      description: 'Prevent unnecessary re-renders',
      detector: this.detectUnnecessaryRenders.bind(this),
      optimizer: this.preventUnnecessaryRenders.bind(this),
      impact: 'high'
    });
  }

  private detectMemoOpportunities(
    code: string,
    ast: any
  ): OptimizationOpportunity[] {
    const opportunities: OptimizationOpportunity[] = [];

    // 함수형 컴포넌트 찾기
    ast.traverse({
      FunctionDeclaration(path: any) {
        if (this.isFunctionalComponent(path.node)) {
          if (!this.hasReactMemo(path)) {
            opportunities.push({
              type: 'add-react-memo',
              location: {
                start: path.node.loc.start,
                end: path.node.loc.end
              },
              description: `Component ${path.node.id.name} can benefit from React.memo`,
              suggestion: 'Wrap component with React.memo to prevent unnecessary re-renders',
              autoFixable: true
            });
          }
        }
      }
    });

    return opportunities;
  }

  private addReactMemo(
    code: string,
    opportunity: OptimizationOpportunity
  ): string {
    // React.memo 추가 로직
    const componentName = this.extractComponentName(code, opportunity.location);

    // 컴포넌트 정의 찾기
    const componentRegex = new RegExp(
      `(function|const)\\s+${componentName}\\s*[=:]?\\s*\\([^)]*\\)\\s*=>\\s*{`,
      'g'
    );

    // React.memo로 감싸기
    return code.replace(componentRegex, (match) => {
      return `const ${componentName} = React.memo(${match.replace(componentName, '')}`;
    }) + ')';
  }

  private detectUseMemoOpportunities(
    code: string,
    ast: any
  ): OptimizationOpportunity[] {
    const opportunities: OptimizationOpportunity[] = [];

    ast.traverse({
      VariableDeclarator(path: any) {
        // 컴포넌트 내부의 복잡한 계산 찾기
        if (this.isInsideComponent(path) && this.isExpensiveComputation(path.node.init)) {
          opportunities.push({
            type: 'add-use-memo',
            location: {
              start: path.node.loc.start,
              end: path.node.loc.end
            },
            description: `Expensive computation can be memoized`,
            suggestion: 'Wrap computation with useMemo to avoid recalculation',
            autoFixable: true
          });
        }
      }
    });

    return opportunities;
  }

  private isExpensiveComputation(node: any): boolean {
    if (!node) return false;

    // 복잡도 계산
    const complexity = this.calculateComplexity(node);

    // 배열 메서드 체이닝
    if (this.hasArrayMethodChaining(node)) return true;

    // 깊은 객체 연산
    if (this.hasDeepObjectOperation(node)) return true;

    // 높은 복잡도
    if (complexity > 10) return true;

    return false;
  }
}

// React 성능 분석기
class ReactPerformanceAnalyzer {
  async analyzeComponentPerformance(
    component: ReactComponent
  ): Promise<ComponentPerformanceReport> {
    const report: ComponentPerformanceReport = {
      renderCount: 0,
      averageRenderTime: 0,
      unnecessaryRenders: 0,
      propsDrillDepth: 0,
      stateComplexity: 0,
      recommendations: []
    };

    // 렌더링 분석
    const renderAnalysis = await this.analyzeRenders(component);
    report.renderCount = renderAnalysis.count;
    report.averageRenderTime = renderAnalysis.averageTime;
    report.unnecessaryRenders = renderAnalysis.unnecessary;

    // Props drilling 분석
    report.propsDrillDepth = await this.analyzePropsDrilling(component);

    // State 복잡도 분석
    report.stateComplexity = await this.analyzeStateComplexity(component);

    // 권장사항 생성
    report.recommendations = this.generateRecommendations(report);

    return report;
  }

  private generateRecommendations(
    report: ComponentPerformanceReport
  ): string[] {
    const recommendations: string[] = [];

    if (report.unnecessaryRenders > 5) {
      recommendations.push('Consider using React.memo or PureComponent');
    }

    if (report.propsDrillDepth > 3) {
      recommendations.push('Consider using Context API or state management library');
    }

    if (report.stateComplexity > 10) {
      recommendations.push('Consider splitting state or using useReducer');
    }

    if (report.averageRenderTime > 16) {
      recommendations.push('Optimize expensive computations with useMemo');
    }

    return recommendations;
  }
}

// React 번들 최적화
class ReactBundleOptimizer {
  async optimizeBundle(
    projectPath: string,
    config: BundleOptimizationConfig
  ): Promise<BundleOptimizationResult> {
    // 1. 코드 스플리팅 분석
    const splitPoints = await this.analyzeSplitPoints(projectPath);

    // 2. Tree shaking 기회
    const treeShakingOpportunities = await this.analyzeTreeShaking(projectPath);

    // 3. 의존성 최적화
    const dependencyOptimizations = await this.optimizeDependencies(projectPath);

    // 4. 최적화 적용
    const optimizedConfig = await this.generateOptimizedConfig(
      splitPoints,
      treeShakingOpportunities,
      dependencyOptimizations
    );

    return {
      originalSize: await this.calculateBundleSize(projectPath),
      optimizedSize: await this.estimateOptimizedSize(optimizedConfig),
      splitPoints,
      treeShakingOpportunities,
      dependencyOptimizations,
      config: optimizedConfig
    };
  }

  private async analyzeSplitPoints(
    projectPath: string
  ): Promise<SplitPoint[]> {
    const splitPoints: SplitPoint[] = [];

    // 라우트 기반 스플리팅
    const routes = await this.findRoutes(projectPath);
    for (const route of routes) {
      splitPoints.push({
        type: 'route',
        path: route.path,
        component: route.component,
        estimatedSize: await this.estimateComponentSize(route.component)
      });
    }

    // 큰 컴포넌트 스플리팅
    const largeComponents = await this.findLargeComponents(projectPath);
    for (const component of largeComponents) {
      splitPoints.push({
        type: 'component',
        path: component.path,
        component: component.name,
        estimatedSize: component.size
      });
    }

    return splitPoints;
  }

  private async generateOptimizedConfig(
    splitPoints: SplitPoint[],
    treeShaking: TreeShakingOpportunity[],
    dependencies: DependencyOptimization[]
  ): Promise<WebpackConfig> {
    return {
      optimization: {
        splitChunks: {
          chunks: 'all',
          cacheGroups: this.generateCacheGroups(splitPoints, dependencies)
        },
        usedExports: true,
        sideEffects: false,
        minimizer: [
          {
            name: 'TerserPlugin',
            options: {
              terserOptions: {
                compress: {
                  drop_console: true,
                  drop_debugger: true,
                  pure_funcs: ['console.log']
                }
              }
            }
          }
        ]
      },
      plugins: [
        {
          name: 'BundleAnalyzerPlugin',
          options: {
            analyzerMode: 'static',
            openAnalyzer: false
          }
        }
      ]
    };
  }
}

// React 코드 생성 최적화
class OptimizedReactGenerator {
  generateOptimizedComponent(
    spec: ComponentSpec,
    optimizationLevel: 'none' | 'basic' | 'aggressive'
  ): string {
    let code = this.generateBaseComponent(spec);

    if (optimizationLevel === 'none') {
      return code;
    }

    // 기본 최적화
    if (optimizationLevel === 'basic' || optimizationLevel === 'aggressive') {
      // React.memo 추가 (순수 컴포넌트인 경우)
      if (spec.isPure) {
        code = this.wrapWithMemo(code, spec);
      }

      // useMemo 추가 (복잡한 계산이 있는 경우)
      code = this.addUseMemoOptimizations(code, spec);

      // useCallback 추가 (콜백 함수가 있는 경우)
      code = this.addUseCallbackOptimizations(code, spec);
    }

    // 공격적 최적화
    if (optimizationLevel === 'aggressive') {
      // 가상화 추가 (긴 리스트인 경우)
      if (spec.hasLongList) {
        code = this.addVirtualization(code, spec);
      }

      // 지연 로딩 추가
      code = this.addLazyLoading(code, spec);

      // 에러 바운더리 추가
      code = this.addErrorBoundary(code, spec);
    }

    return code;
  }

  private wrapWithMemo(code: string, spec: ComponentSpec): string {
    const memoComparison = spec.memoComparison
      ? `, ${spec.memoComparison}`
      : '';

    return `import React from 'react';

${code.replace(
  `export default ${spec.name};`,
  `export default React.memo(${spec.name}${memoComparison});`
)}`;
  }

  private addUseMemoOptimizations(code: string, spec: ComponentSpec): string {
    // 복잡한 계산 찾아서 useMemo로 감싸기
    for (const computation of spec.expensiveComputations || []) {
      const memoizedName = `memoized${computation.name}`;
      const dependencies = computation.dependencies.join(', ');

      const memoCode = `
  const ${memoizedName} = useMemo(() => {
    ${computation.code}
  }, [${dependencies}]);`;

      // 원래 계산을 memoized 버전으로 교체
      code = code.replace(computation.originalCode, memoCode);
    }

    return code;
  }
}
````

**검증 기준**:

- [ ] React 특화 최적화 규칙
- [ ] 번들 사이즈 최적화
- [ ] 렌더링 성능 개선
- [ ] 자동 최적화 적용

---

#### SubTask 4.66.2: Vue 최적화

**담당자**: Vue.js 전문가  
**예상 소요시간**: 12시간

**작업 내용**:

```typescript
// backend/src/agents/implementations/generation/vue_optimizer.ts
interface VueOptimizationRule {
  name: string;
  description: string;
  applies: (component: VueComponent) => boolean;
  optimize: (component: VueComponent) => VueComponent;
  impact: OptimizationImpact;
}

interface VueComponent {
  template: string;
  script: string;
  style: string;
  name: string;
  props?: any;
  computed?: any;
  methods?: any;
  setup?: string;
}

class VueOptimizer {
  private rules: VueOptimizationRule[] = [];
  private compositionApiConverter: CompositionApiConverter;
  private reactivityOptimizer: ReactivityOptimizer;

  constructor() {
    this.initializeRules();
    this.compositionApiConverter = new CompositionApiConverter();
    this.reactivityOptimizer = new ReactivityOptimizer();
  }

  async optimizeVueComponent(
    component: VueComponent,
    options: VueOptimizationOptions,
  ): Promise<OptimizedVueComponent> {
    let optimized = { ...component };
    const appliedOptimizations: string[] = [];

    // 1. Composition API 변환 (옵션)
    if (options.convertToCompositionApi && !this.isCompositionApi(component)) {
      optimized = await this.compositionApiConverter.convert(optimized);
      appliedOptimizations.push('Converted to Composition API');
    }

    // 2. 반응성 최적화
    const reactivityResult = await this.reactivityOptimizer.optimize(optimized);
    optimized = reactivityResult.component;
    appliedOptimizations.push(...reactivityResult.optimizations);

    // 3. 규칙 기반 최적화
    for (const rule of this.rules) {
      if (rule.applies(optimized)) {
        optimized = rule.optimize(optimized);
        appliedOptimizations.push(rule.description);
      }
    }

    // 4. 템플릿 최적화
    optimized.template = await this.optimizeTemplate(optimized.template);

    // 5. 번들 최적화
    const bundleOptimizations = await this.optimizeForBundling(optimized);

    return {
      original: component,
      optimized,
      appliedOptimizations,
      bundleOptimizations,
      performanceGains: await this.estimatePerformanceGains(component, optimized),
    };
  }

  private initializeRules() {
    // computed 속성 최적화
    this.rules.push({
      name: 'optimize-computed',
      description: 'Optimize computed properties',
      applies: (component) => !!component.computed,
      optimize: this.optimizeComputedProperties.bind(this),
      impact: { performance: 'high', complexity: 'low' },
    });

    // v-if vs v-show 최적화
    this.rules.push({
      name: 'optimize-conditional-rendering',
      description: 'Optimize v-if and v-show usage',
      applies: (component) => /v-if|v-show/.test(component.template),
      optimize: this.optimizeConditionalRendering.bind(this),
      impact: { performance: 'medium', complexity: 'low' },
    });

    // 리스트 렌더링 최적화
    this.rules.push({
      name: 'optimize-list-rendering',
      description: 'Optimize v-for with proper keys',
      applies: (component) => /v-for/.test(component.template),
      optimize: this.optimizeListRendering.bind(this),
      impact: { performance: 'high', complexity: 'medium' },
    });

    // 이벤트 핸들러 최적화
    this.rules.push({
      name: 'optimize-event-handlers',
      description: 'Optimize event handler performance',
      applies: (component) => /@\w+/.test(component.template),
      optimize: this.optimizeEventHandlers.bind(this),
      impact: { performance: 'medium', complexity: 'low' },
    });

    // Async Components
    this.rules.push({
      name: 'add-async-components',
      description: 'Convert heavy components to async',
      applies: (component) => this.shouldBeAsync(component),
      optimize: this.convertToAsyncComponent.bind(this),
      impact: { performance: 'high', complexity: 'medium' },
    });
  }

  private optimizeComputedProperties(component: VueComponent): VueComponent {
    const optimized = { ...component };

    if (component.computed) {
      const optimizedComputed: any = {};

      for (const [key, value] of Object.entries(component.computed)) {
        if (typeof value === 'function') {
          // 단순 getter를 최적화된 getter로 변환
          optimizedComputed[key] = {
            get: value,
            cache: true, // 캐싱 활성화
          };
        } else {
          optimizedComputed[key] = value;
        }
      }

      optimized.computed = optimizedComputed;
    }

    return optimized;
  }

  private optimizeTemplate(template: string): string {
    let optimized = template;

    // 1. 불필요한 wrapper 제거
    optimized = this.removeUnnecessaryWrappers(optimized);

    // 2. 정적 클래스 최적화
    optimized = this.optimizeStaticClasses(optimized);

    // 3. 인라인 스타일 최적화
    optimized = this.optimizeInlineStyles(optimized);

    // 4. 슬롯 최적화
    optimized = this.optimizeSlots(optimized);

    // 5. 템플릿 표현식 최적화
    optimized = this.optimizeTemplateExpressions(optimized);

    return optimized;
  }

  private optimizeListRendering(component: VueComponent): VueComponent {
    const optimized = { ...component };

    // v-for에 key 추가/최적화
    optimized.template = optimized.template.replace(
      /<(\w+)\s+v-for="([^"]+)"\s*(?!:key)/g,
      (match, tag, iterator) => {
        const keyExpression = this.generateOptimalKey(iterator);
        return `<${tag} v-for="${iterator}" :key="${keyExpression}"`;
      },
    );

    // track-by 최적화 (Vue 2)
    optimized.template = optimized.template.replace(/track-by="index"/g, 'track-by="$index"');

    // 큰 리스트에 가상 스크롤링 제안
    if (this.hasLargeList(optimized.template)) {
      // 가상 스크롤링 컴포넌트로 래핑
      optimized.template = this.wrapWithVirtualScroll(optimized.template);
    }

    return optimized;
  }
}

// Vue Composition API 변환기
class CompositionApiConverter {
  async convert(component: VueComponent): Promise<VueComponent> {
    const converted = { ...component };

    // Options API에서 Composition API로 변환
    const setupFunction = this.generateSetupFunction(component);

    converted.script = this.replaceScriptContent(component.script, setupFunction);

    return converted;
  }

  private generateSetupFunction(component: VueComponent): string {
    const imports: string[] = [];
    const setupBody: string[] = [];
    const returns: string[] = [];

    // reactive data 변환
    if (component.data) {
      imports.push('ref', 'reactive');
      const dataSetup = this.convertData(component.data);
      setupBody.push(dataSetup.code);
      returns.push(...dataSetup.returns);
    }

    // computed 변환
    if (component.computed) {
      imports.push('computed');
      const computedSetup = this.convertComputed(component.computed);
      setupBody.push(computedSetup.code);
      returns.push(...computedSetup.returns);
    }

    // methods 변환
    if (component.methods) {
      const methodsSetup = this.convertMethods(component.methods);
      setupBody.push(methodsSetup.code);
      returns.push(...methodsSetup.returns);
    }

    // watch 변환
    if (component.watch) {
      imports.push('watch', 'watchEffect');
      const watchSetup = this.convertWatch(component.watch);
      setupBody.push(watchSetup.code);
    }

    // lifecycle hooks 변환
    const lifecycleSetup = this.convertLifecycleHooks(component);
    if (lifecycleSetup.imports.length > 0) {
      imports.push(...lifecycleSetup.imports);
      setupBody.push(lifecycleSetup.code);
    }

    return `
import { ${[...new Set(imports)].join(', ')} } from 'vue';

export default {
  name: '${component.name}',
  ${component.props ? `props: ${JSON.stringify(component.props)},` : ''}
  setup(props, { emit, slots, attrs }) {
    ${setupBody.join('\n\n    ')}

    return {
      ${returns.join(',\n      ')}
    };
  }
};`;
  }
}

// Vue 반응성 최적화
class ReactivityOptimizer {
  async optimize(component: VueComponent): Promise<ReactivityOptimizationResult> {
    const optimizations: string[] = [];
    let optimized = { ...component };

    // 1. shallowRef/shallowReactive 사용 기회 찾기
    const shallowOpportunities = this.findShallowOpportunities(component);
    if (shallowOpportunities.length > 0) {
      optimized = this.applyShallowOptimizations(optimized, shallowOpportunities);
      optimizations.push('Applied shallow reactivity where appropriate');
    }

    // 2. computed vs methods 최적화
    const computedOpportunities = this.findComputedOpportunities(component);
    if (computedOpportunities.length > 0) {
      optimized = this.convertToComputed(optimized, computedOpportunities);
      optimizations.push('Converted methods to computed properties');
    }

    // 3. 불필요한 반응성 제거
    const nonReactiveData = this.findNonReactiveData(component);
    if (nonReactiveData.length > 0) {
      optimized = this.removeUnnecessaryReactivity(optimized, nonReactiveData);
      optimizations.push('Removed unnecessary reactivity');
    }

    // 4. watchEffect vs watch 최적화
    if (component.watch) {
      optimized = this.optimizeWatchers(optimized);
      optimizations.push('Optimized watchers');
    }

    return {
      component: optimized,
      optimizations,
    };
  }

  private findShallowOpportunities(component: VueComponent): ShallowOpportunity[] {
    const opportunities: ShallowOpportunity[] = [];

    // 큰 객체나 배열 찾기
    const dataAnalysis = this.analyzeDataStructure(component);

    for (const data of dataAnalysis) {
      if (data.depth === 1 && data.size > 100) {
        opportunities.push({
          name: data.name,
          type: 'shallow',
          reason: 'Large flat data structure',
        });
      }
    }

    return opportunities;
  }
}

// Vue 번들 최적화
class VueBundleOptimizer {
  async optimizeForProduction(
    project: VueProject,
    config: VueBundleConfig,
  ): Promise<OptimizedBundle> {
    const optimizations: BundleOptimization[] = [];

    // 1. Tree shaking 최적화
    const treeShaking = await this.optimizeTreeShaking(project);
    optimizations.push(treeShaking);

    // 2. 청크 분할 최적화
    const chunkSplitting = await this.optimizeChunkSplitting(project);
    optimizations.push(chunkSplitting);

    // 3. 의존성 최적화
    const dependencies = await this.optimizeDependencies(project);
    optimizations.push(dependencies);

    // 4. CSS 최적화
    const css = await this.optimizeCSS(project);
    optimizations.push(css);

    // 5. 이미지/에셋 최적화
    const assets = await this.optimizeAssets(project);
    optimizations.push(assets);

    // Vite 설정 생성
    const viteConfig = this.generateViteConfig(optimizations);

    return {
      optimizations,
      config: viteConfig,
      estimatedSizeReduction: this.calculateSizeReduction(optimizations),
    };
  }

  private generateViteConfig(optimizations: BundleOptimization[]): ViteConfig {
    return {
      build: {
        rollupOptions: {
          output: {
            manualChunks: this.generateManualChunks(optimizations),
            chunkFileNames: (chunkInfo) => {
              const facadeModuleId = chunkInfo.facadeModuleId
                ? chunkInfo.facadeModuleId.split('/').pop()
                : 'chunk';
              return `js/${facadeModuleId}-[hash].js`;
            },
          },
        },
        cssCodeSplit: true,
        minify: 'terser',
        terserOptions: {
          compress: {
            drop_console: true,
            drop_debugger: true,
          },
        },
      },
      optimizeDeps: {
        include: ['vue', 'vue-router', 'pinia'],
        exclude: ['@vueuse/core'],
      },
    };
  }
}

// Vue 3 특화 최적화
class Vue3Optimizer extends VueOptimizer {
  async optimizeVue3Features(component: VueComponent): Promise<OptimizedVueComponent> {
    let optimized = { ...component };

    // 1. <script setup> 최적화
    if (this.canUseScriptSetup(component)) {
      optimized = this.convertToScriptSetup(optimized);
    }

    // 2. Suspense 활용
    if (this.shouldUseSuspense(component)) {
      optimized = this.addSuspenseWrapper(optimized);
    }

    // 3. Teleport 최적화
    optimized = this.optimizeTeleport(optimized);

    // 4. Fragment 최적화
    optimized = this.optimizeFragments(optimized);

    // 5. v-memo 지시자 추가
    optimized = this.addVMemoDirective(optimized);

    return {
      ...optimized,
      vue3Specific: true,
    };
  }

  private convertToScriptSetup(component: VueComponent): VueComponent {
    const converted = { ...component };

    // <script setup> 구문으로 변환
    const setupScript = `
<script setup lang="ts">
${this.generateScriptSetupImports(component)}
${this.generateScriptSetupProps(component)}
${this.generateScriptSetupCode(component)}
</script>`;

    converted.script = setupScript;
    return converted;
  }

  private addVMemoDirective(component: VueComponent): VueComponent {
    const optimized = { ...component };

    // 큰 리스트의 아이템에 v-memo 추가
    optimized.template = optimized.template.replace(
      /(<\w+\s+v-for="[^"]+"\s+:key="[^"]+")(?![^>]*v-memo)/g,
      (match) => {
        const memoExpression = this.generateMemoExpression(match);
        return `${match} v-memo="${memoExpression}"`;
      },
    );

    return optimized;
  }
}
```

**검증 기준**:

- [ ] Vue 특화 최적화 규칙
- [ ] Composition API 변환
- [ ] 반응성 시스템 최적화
- [ ] Vue 3 기능 활용

#### SubTask 4.66.3: Angular 최적화

**담당자**: Angular 전문가  
**예상 소요시간**: 12시간

**작업 내용**:

```typescript
// backend/src/agents/implementations/generation/angular_optimizer.ts
interface AngularOptimizationStrategy {
  name: string;
  description: string;
  analyze: (component: AngularComponent) => OptimizationOpportunity[];
  apply: (component: AngularComponent, opportunity: OptimizationOpportunity) => AngularComponent;
  priority: 'critical' | 'high' | 'medium' | 'low';
}

interface AngularComponent {
  selector: string;
  template: string;
  styles: string[];
  typescript: string;
  module?: string;
  metadata: ComponentMetadata;
}

class AngularOptimizer {
  private strategies: AngularOptimizationStrategy[] = [];
  private changeDetectionOptimizer: ChangeDetectionOptimizer;
  private bundleOptimizer: AngularBundleOptimizer;
  private rxjsOptimizer: RxJSOptimizer;

  constructor() {
    this.initializeStrategies();
    this.changeDetectionOptimizer = new ChangeDetectionOptimizer();
    this.bundleOptimizer = new AngularBundleOptimizer();
    this.rxjsOptimizer = new RxJSOptimizer();
  }

  async optimizeAngularComponent(
    component: AngularComponent,
    config: AngularOptimizationConfig,
  ): Promise<OptimizedAngularComponent> {
    const opportunities: OptimizationOpportunity[] = [];
    let optimized = { ...component };

    // 1. Change Detection 최적화
    const cdResult = await this.changeDetectionOptimizer.optimize(optimized);
    optimized = cdResult.component;
    opportunities.push(...cdResult.opportunities);

    // 2. RxJS 최적화
    const rxjsResult = await this.rxjsOptimizer.optimize(optimized);
    optimized = rxjsResult.component;
    opportunities.push(...rxjsResult.opportunities);

    // 3. 전략 기반 최적화
    for (const strategy of this.strategies) {
      const strategyOpportunities = strategy.analyze(optimized);
      for (const opportunity of strategyOpportunities) {
        if (config.autoApply || opportunity.impact === 'critical') {
          optimized = strategy.apply(optimized, opportunity);
          opportunities.push(opportunity);
        }
      }
    }

    // 4. 템플릿 최적화
    optimized.template = await this.optimizeTemplate(optimized.template);

    // 5. 번들 최적화 분석
    const bundleAnalysis = await this.bundleOptimizer.analyze(optimized);

    return {
      original: component,
      optimized,
      opportunities,
      bundleAnalysis,
      performanceMetrics: await this.calculatePerformanceMetrics(component, optimized),
    };
  }

  private initializeStrategies() {
    // OnPush 전략
    this.strategies.push({
      name: 'change-detection-onpush',
      description: 'Use OnPush change detection strategy',
      analyze: this.analyzeOnPushOpportunity.bind(this),
      apply: this.applyOnPushStrategy.bind(this),
      priority: 'high',
    });

    // TrackBy 함수 추가
    this.strategies.push({
      name: 'add-trackby',
      description: 'Add trackBy functions to *ngFor',
      analyze: this.analyzeTrackByOpportunity.bind(this),
      apply: this.addTrackByFunction.bind(this),
      priority: 'high',
    });

    // Pipe 최적화
    this.strategies.push({
      name: 'optimize-pipes',
      description: 'Optimize pipe usage',
      analyze: this.analyzePipeOpportunity.bind(this),
      apply: this.optimizePipes.bind(this),
      priority: 'medium',
    });

    // Lazy Loading
    this.strategies.push({
      name: 'lazy-loading',
      description: 'Implement lazy loading for modules',
      analyze: this.analyzeLazyLoadingOpportunity.bind(this),
      apply: this.implementLazyLoading.bind(this),
      priority: 'high',
    });

    // Preloading 전략
    this.strategies.push({
      name: 'preloading-strategy',
      description: 'Implement preloading strategy',
      analyze: this.analyzePreloadingOpportunity.bind(this),
      apply: this.implementPreloading.bind(this),
      priority: 'medium',
    });
  }

  private analyzeOnPushOpportunity(component: AngularComponent): OptimizationOpportunity[] {
    const opportunities: OptimizationOpportunity[] = [];

    // 현재 Default 전략을 사용하고 있는지 확인
    if (!component.typescript.includes('ChangeDetectionStrategy.OnPush')) {
      // 컴포넌트가 OnPush에 적합한지 분석
      const suitability = this.analyzeOnPushSuitability(component);

      if (suitability.suitable) {
        opportunities.push({
          type: 'change-detection',
          description: 'Component can use OnPush change detection',
          impact: 'critical',
          location: { file: component.selector, line: 0 },
          autoFixable: true,
          reason: suitability.reason,
        });
      }
    }

    return opportunities;
  }

  private applyOnPushStrategy(
    component: AngularComponent,
    opportunity: OptimizationOpportunity,
  ): AngularComponent {
    const optimized = { ...component };

    // Import 추가
    if (!optimized.typescript.includes('ChangeDetectionStrategy')) {
      optimized.typescript = optimized.typescript.replace(
        /@Component\({/,
        `import { ChangeDetectionStrategy } from '@angular/core';\n\n@Component({`,
      );
    }

    // OnPush 전략 추가
    optimized.typescript = optimized.typescript.replace(
      /@Component\({([^}]*)\}/,
      (match, content) => {
        if (!content.includes('changeDetection')) {
          return `@Component({${content},\n  changeDetection: ChangeDetectionStrategy.OnPush\n}`;
        }
        return match;
      },
    );

    return optimized;
  }

  private optimizeTemplate(template: string): string {
    let optimized = template;

    // 1. 불필요한 바인딩 제거
    optimized = this.removeUnnecessaryBindings(optimized);

    // 2. 구조 지시자 최적화
    optimized = this.optimizeStructuralDirectives(optimized);

    // 3. 이벤트 바인딩 최적화
    optimized = this.optimizeEventBindings(optimized);

    // 4. 템플릿 표현식 최적화
    optimized = this.optimizeTemplateExpressions(optimized);

    // 5. ng-container 사용 최적화
    optimized = this.optimizeNgContainer(optimized);

    return optimized;
  }
}

// Change Detection 최적화
class ChangeDetectionOptimizer {
  async optimize(component: AngularComponent): Promise<ChangeDetectionResult> {
    const opportunities: OptimizationOpportunity[] = [];
    let optimized = { ...component };

    // 1. 불필요한 변경 감지 트리거 찾기
    const unnecessaryTriggers = this.findUnnecessaryTriggers(component);
    if (unnecessaryTriggers.length > 0) {
      optimized = this.removeUnnecessaryTriggers(optimized, unnecessaryTriggers);
      opportunities.push({
        type: 'change-detection',
        description: 'Removed unnecessary change detection triggers',
        impact: 'high',
        details: unnecessaryTriggers,
      });
    }

    // 2. Immutable 데이터 구조 사용 권장
    const mutableData = this.findMutableDataStructures(component);
    if (mutableData.length > 0) {
      opportunities.push({
        type: 'immutability',
        description: 'Use immutable data structures',
        impact: 'medium',
        details: mutableData,
      });
    }

    // 3. markForCheck() 최적화
    const markForCheckOpportunities = this.analyzeMarkForCheck(component);
    if (markForCheckOpportunities.length > 0) {
      optimized = this.optimizeMarkForCheck(optimized, markForCheckOpportunities);
      opportunities.push({
        type: 'mark-for-check',
        description: 'Optimized markForCheck usage',
        impact: 'medium',
      });
    }

    return {
      component: optimized,
      opportunities,
    };
  }

  private findUnnecessaryTriggers(component: AngularComponent): string[] {
    const triggers: string[] = [];

    // 템플릿에서 함수 호출 찾기
    const functionCalls = component.template.match(/\{\{[^}]*\([^}]*\)[^}]*\}\}/g) || [];
    triggers.push(...functionCalls.map((call) => `Template function call: ${call}`));

    // getter에서 복잡한 계산 찾기
    const getterRegex = /get\s+(\w+)\s*\(\s*\)\s*{([^}]+)}/g;
    let match;
    while ((match = getterRegex.exec(component.typescript)) !== null) {
      const complexity = this.calculateComplexity(match[2]);
      if (complexity > 5) {
        triggers.push(`Complex getter: ${match[1]}`);
      }
    }

    return triggers;
  }
}

// RxJS 최적화
class RxJSOptimizer {
  async optimize(component: AngularComponent): Promise<RxJSOptimizationResult> {
    const opportunities: OptimizationOpportunity[] = [];
    let optimized = { ...component };

    // 1. 메모리 누수 방지
    const leaks = this.findPotentialMemoryLeaks(component);
    if (leaks.length > 0) {
      optimized = this.addUnsubscribeLogic(optimized, leaks);
      opportunities.push({
        type: 'memory-leak',
        description: 'Added proper unsubscribe logic',
        impact: 'critical',
        details: leaks,
      });
    }

    // 2. 연산자 최적화
    const operatorOptimizations = this.optimizeOperators(component);
    if (operatorOptimizations.length > 0) {
      optimized = this.applyOperatorOptimizations(optimized, operatorOptimizations);
      opportunities.push(...operatorOptimizations);
    }

    // 3. shareReplay 사용
    const shareReplayOpportunities = this.findShareReplayOpportunities(component);
    if (shareReplayOpportunities.length > 0) {
      optimized = this.addShareReplay(optimized, shareReplayOpportunities);
      opportunities.push({
        type: 'share-replay',
        description: 'Added shareReplay for shared subscriptions',
        impact: 'high',
      });
    }

    // 4. async pipe 최적화
    const asyncPipeOptimizations = this.optimizeAsyncPipe(component);
    if (asyncPipeOptimizations.length > 0) {
      optimized = this.applyAsyncPipeOptimizations(optimized, asyncPipeOptimizations);
      opportunities.push(...asyncPipeOptimizations);
    }

    return {
      component: optimized,
      opportunities,
    };
  }

  private findPotentialMemoryLeaks(component: AngularComponent): MemoryLeak[] {
    const leaks: MemoryLeak[] = [];

    // subscribe() 호출 찾기
    const subscribeRegex = /\.subscribe\s*\(/g;
    const matches = [...component.typescript.matchAll(subscribeRegex)];

    for (const match of matches) {
      const hasUnsubscribe = this.checkUnsubscribePresence(component.typescript, match.index!);

      if (!hasUnsubscribe) {
        leaks.push({
          line: this.getLineNumber(component.typescript, match.index!),
          type: 'missing-unsubscribe',
          suggestion: 'Use takeUntil or async pipe',
        });
      }
    }

    return leaks;
  }

  private addUnsubscribeLogic(component: AngularComponent, leaks: MemoryLeak[]): AngularComponent {
    let optimized = { ...component };

    // destroy$ subject 추가
    const destroySubject = `
  private destroy$ = new Subject<void>();`;

    // ngOnDestroy 추가/업데이트
    const ngOnDestroy = `
  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }`;

    // takeUntil 추가
    optimized.typescript = optimized.typescript.replace(
      /\.subscribe\(/g,
      '.pipe(takeUntil(this.destroy$)).subscribe(',
    );

    // imports 추가
    if (!optimized.typescript.includes('takeUntil')) {
      optimized.typescript = optimized.typescript.replace(
        /import\s*{([^}]+)}\s*from\s*'rxjs\/operators'/,
        "import { $1, takeUntil } from 'rxjs/operators'",
      );
    }

    return optimized;
  }
}

// Angular 번들 최적화
class AngularBundleOptimizer {
  async optimizeBuild(
    project: AngularProject,
    config: BuildOptimizationConfig,
  ): Promise<OptimizedBuildConfig> {
    const optimizations: BuildOptimization[] = [];

    // 1. Differential Loading
    if (config.enableDifferentialLoading) {
      optimizations.push(await this.configureDifferentialLoading(project));
    }

    // 2. Build Optimizer
    optimizations.push(this.configureBuildOptimizer());

    // 3. Tree Shaking
    optimizations.push(this.configureTreeShaking());

    // 4. Code Splitting
    const codeSplitting = await this.analyzeCodeSplitting(project);
    optimizations.push(codeSplitting);

    // 5. Budgets 설정
    const budgets = this.generateBudgets(project);

    // angular.json 설정 생성
    const angularConfig = this.generateAngularConfig(optimizations, budgets);

    return {
      config: angularConfig,
      optimizations,
      estimatedBuildTime: this.estimateBuildTime(optimizations),
      estimatedBundleSize: this.estimateBundleSize(project, optimizations),
    };
  }

  private generateAngularConfig(optimizations: BuildOptimization[], budgets: Budget[]): any {
    return {
      projects: {
        app: {
          architect: {
            build: {
              options: {
                aot: true,
                buildOptimizer: true,
                optimization: true,
                outputHashing: 'all',
                sourceMap: false,
                namedChunks: false,
                extractLicenses: true,
                vendorChunk: false,
                budgets,
              },
              configurations: {
                production: {
                  fileReplacements: [
                    {
                      replace: 'src/environments/environment.ts',
                      with: 'src/environments/environment.prod.ts',
                    },
                  ],
                  optimization: {
                    scripts: true,
                    styles: {
                      minify: true,
                      inlineCritical: true,
                    },
                    fonts: true,
                  },
                },
              },
            },
          },
        },
      },
    };
  }
}

// Angular 컴포넌트 생성 최적화
class OptimizedAngularGenerator {
  generateOptimizedComponent(
    spec: ComponentSpec,
    features: AngularFeatures,
  ): GeneratedAngularComponent {
    const component: GeneratedAngularComponent = {
      selector: this.generateSelector(spec.name),
      template: '',
      styles: [],
      typescript: '',
      spec: '',
    };

    // 1. TypeScript 생성
    component.typescript = this.generateOptimizedTypeScript(spec, features);

    // 2. 템플릿 생성
    component.template = this.generateOptimizedTemplate(spec, features);

    // 3. 스타일 생성
    component.styles = this.generateOptimizedStyles(spec, features);

    // 4. 스펙 파일 생성
    component.spec = this.generateOptimizedSpec(spec, features);

    // 5. 모듈 설정
    if (features.standalone) {
      component.typescript = this.makeStandalone(component.typescript);
    }

    return component;
  }

  private generateOptimizedTypeScript(spec: ComponentSpec, features: AngularFeatures): string {
    const imports = this.generateImports(spec, features);
    const decorator = this.generateDecorator(spec, features);
    const classContent = this.generateClassContent(spec, features);

    return `${imports}

${decorator}
export class ${spec.name}Component implements OnInit${features.onPush ? ', OnDestroy' : ''} {
${classContent}
}`;
  }

  private generateDecorator(spec: ComponentSpec, features: AngularFeatures): string {
    const decoratorProps: string[] = [
      `selector: '${this.generateSelector(spec.name)}'`,
      `templateUrl: './${spec.name.toLowerCase()}.component.html'`,
      `styleUrls: ['./${spec.name.toLowerCase()}.component.scss']`,
    ];

    if (features.onPush) {
      decoratorProps.push('changeDetection: ChangeDetectionStrategy.OnPush');
    }

    if (features.standalone) {
      decoratorProps.push('standalone: true');
      decoratorProps.push(`imports: [${this.getStandaloneImports(spec)}]`);
    }

    if (features.encapsulation) {
      decoratorProps.push(`encapsulation: ViewEncapsulation.${features.encapsulation}`);
    }

    return `@Component({
  ${decoratorProps.join(',\n  ')}
})`;
  }
}
```

**검증 기준**:

- [ ] Angular 특화 최적화
- [ ] Change Detection 최적화
- [ ] RxJS 메모리 누수 방지
- [ ] 번들 사이즈 최적화

#### SubTask 4.66.4: Next.js 최적화

**담당자**: Next.js 전문가  
**예상 소요시간**: 10시간

**작업 내용**:

```typescript
// backend/src/agents/implementations/generation/nextjs_optimizer.ts
interface NextJSOptimizationRule {
  name: string;
  description: string;
  check: (page: NextJSPage) => boolean;
  optimize: (page: NextJSPage) => NextJSPage;
  category: 'performance' | 'seo' | 'ux' | 'bundle';
}

interface NextJSPage {
  path: string;
  component: string;
  hasGetStaticProps?: boolean;
  hasGetServerSideProps?: boolean;
  hasGetStaticPaths?: boolean;
  imports: string[];
  exports: string[];
}

class NextJSOptimizer {
  private rules: NextJSOptimizationRule[] = [];
  private imageOptimizer: NextImageOptimizer;
  private fontOptimizer: NextFontOptimizer;
  private routeOptimizer: RouteOptimizer;

  constructor() {
    this.initializeRules();
    this.imageOptimizer = new NextImageOptimizer();
    this.fontOptimizer = new NextFontOptimizer();
    this.routeOptimizer = new RouteOptimizer();
  }

  async optimizeNextJSApp(
    pages: NextJSPage[],
    config: NextJSOptimizationConfig,
  ): Promise<OptimizedNextJSApp> {
    const optimizations: AppliedOptimization[] = [];
    const optimizedPages: NextJSPage[] = [];

    // 1. 페이지별 최적화
    for (const page of pages) {
      let optimizedPage = { ...page };

      // 규칙 기반 최적화
      for (const rule of this.rules) {
        if (rule.check(optimizedPage)) {
          optimizedPage = rule.optimize(optimizedPage);
          optimizations.push({
            page: page.path,
            optimization: rule.name,
            category: rule.category,
          });
        }
      }

      optimizedPages.push(optimizedPage);
    }

    // 2. 이미지 최적화
    const imageOptimizations = await this.imageOptimizer.optimize(optimizedPages);
    optimizations.push(...imageOptimizations);

    // 3. 폰트 최적화
    const fontOptimizations = await this.fontOptimizer.optimize(optimizedPages);
    optimizations.push(...fontOptimizations);

    // 4. 라우팅 최적화
    const routeOptimizations = await this.routeOptimizer.optimize(optimizedPages);
    optimizations.push(...routeOptimizations);

    // 5. next.config.js 최적화
    const optimizedConfig = this.generateOptimizedConfig(optimizations);

    return {
      pages: optimizedPages,
      optimizations,
      config: optimizedConfig,
      performanceGains: await this.estimatePerformanceGains(pages, optimizedPages),
    };
  }

  private initializeRules() {
    // Static Generation 추천
    this.rules.push({
      name: 'prefer-static-generation',
      description: 'Use getStaticProps instead of getServerSideProps when possible',
      category: 'performance',
      check: (page) => page.hasGetServerSideProps && !this.requiresRealTimeData(page),
      optimize: this.convertToStaticGeneration.bind(this),
    });

    // ISR (Incremental Static Regeneration) 추가
    this.rules.push({
      name: 'add-isr',
      description: 'Add ISR for frequently updated static pages',
      category: 'performance',
      check: (page) => page.hasGetStaticProps && this.shouldUseISR(page),
      optimize: this.addISR.bind(this),
    });

    // Dynamic Imports
    this.rules.push({
      name: 'add-dynamic-imports',
      description: 'Use dynamic imports for heavy components',
      category: 'bundle',
      check: (page) => this.hasHeavyComponents(page),
      optimize: this.addDynamicImports.bind(this),
    });

    // API Routes 최적화
    this.rules.push({
      name: 'optimize-api-routes',
      description: 'Optimize API routes for performance',
      category: 'performance',
      check: (page) => page.path.startsWith('/api/'),
      optimize: this.optimizeAPIRoute.bind(this),
    });

    // SEO 최적화
    this.rules.push({
      name: 'add-seo-metadata',
      description: 'Add proper SEO metadata',
      category: 'seo',
      check: (page) => !this.hasProperSEO(page),
      optimize: this.addSEOMetadata.bind(this),
    });
  }

  private convertToStaticGeneration(page: NextJSPage): NextJSPage {
    const optimized = { ...page };

    // getServerSideProps를 getStaticProps로 변환
    optimized.component = optimized.component.replace(
      /export\s+async\s+function\s+getServerSideProps/,
      'export async function getStaticProps',
    );

    // revalidate 추가 (ISR)
    optimized.component = optimized.component.replace(
      /return\s*{\s*props:\s*{([^}]*)}\s*}/,
      'return {\n    props: {$1},\n    revalidate: 60 // ISR: revalidate every 60 seconds\n  }',
    );

    optimized.hasGetStaticProps = true;
    optimized.hasGetServerSideProps = false;

    return optimized;
  }

  private addDynamicImports(page: NextJSPage): NextJSPage {
    const optimized = { ...page };
    const heavyComponents = this.identifyHeavyComponents(page);

    for (const component of heavyComponents) {
      // 정적 import를 dynamic import로 변환
      optimized.component = optimized.component.replace(
        new RegExp(`import\\s+${component.name}\\s+from\\s+['"]${component.path}['"]`),
        `const ${component.name} = dynamic(() => import('${component.path}'), {
  loading: () => <LoadingSpinner />,
  ssr: ${component.needsSSR}
})`,
      );
    }

    // dynamic import 추가
    if (!optimized.imports.includes('dynamic')) {
      optimized.component = `import dynamic from 'next/dynamic';\n${optimized.component}`;
      optimized.imports.push('dynamic');
    }

    return optimized;
  }
}

// Next.js Image 최적화
class NextImageOptimizer {
  async optimize(pages: NextJSPage[]): Promise<AppliedOptimization[]> {
    const optimizations: AppliedOptimization[] = [];

    for (const page of pages) {
      // img 태그를 next/image로 변환
      if (this.hasUnoptimizedImages(page)) {
        this.convertToNextImage(page);
        optimizations.push({
          page: page.path,
          optimization: 'convert-to-next-image',
          category: 'performance',
        });
      }

      // 이미지 최적화 설정 추가
      if (this.needsImageOptimization(page)) {
        this.addImageOptimization(page);
        optimizations.push({
          page: page.path,
          optimization: 'add-image-optimization',
          category: 'performance',
        });
      }
    }

    return optimizations;
  }

  private convertToNextImage(page: NextJSPage): void {
    // <img> 태그를 <Image> 컴포넌트로 변환
    page.component = page.component.replace(
      /<img\s+([^>]*?)src=["']([^"']+)["']([^>]*?)>/g,
      (match, before, src, after) => {
        const alt = this.extractAlt(match) || 'Image';
        const width = this.extractDimension(match, 'width') || '800';
        const height = this.extractDimension(match, 'height') || '600';

        return `<Image 
          src="${src}"
          alt="${alt}"
          width={${width}}
          height={${height}}
          placeholder="blur"
          blurDataURL="${this.generateBlurDataURL()}"
          ${this.shouldBePriority(src) ? 'priority' : ''}
        />`;
      },
    );

    // Import 추가
    if (!page.imports.includes('Image')) {
      page.component = `import Image from 'next/image';\n${page.component}`;
      page.imports.push('Image');
    }
  }
}

// Next.js Font 최적화
class NextFontOptimizer {
  async optimize(pages: NextJSPage[]): Promise<AppliedOptimization[]> {
    const optimizations: AppliedOptimization[] = [];

    // 1. Google Fonts 최적화
    const googleFonts = this.detectGoogleFonts(pages);
    if (googleFonts.length > 0) {
      this.optimizeGoogleFonts(pages, googleFonts);
      optimizations.push({
        optimization: 'optimize-google-fonts',
        category: 'performance',
      });
    }

    // 2. 로컬 폰트 최적화
    const localFonts = this.detectLocalFonts(pages);
    if (localFonts.length > 0) {
      this.optimizeLocalFonts(pages, localFonts);
      optimizations.push({
        optimization: 'optimize-local-fonts',
        category: 'performance',
      });
    }

    return optimizations;
  }

  private optimizeGoogleFonts(pages: NextJSPage[], fonts: string[]): void {
    // _app.js에 next/font/google 추가
    const appPage = pages.find((p) => p.path === '/_app');
    if (appPage) {
      const fontImports = fonts
        .map((font) => {
          const varName = font.replace(/\s+/g, '_').toLowerCase();
          return `const ${varName} = ${font}({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-${varName}'
});`;
        })
        .join('\n');

      appPage.component = `import { ${fonts.join(', ')} } from 'next/font/google';\n${fontImports}\n${appPage.component}`;
    }
  }
}

// Next.js 라우팅 최적화
class RouteOptimizer {
  async optimize(pages: NextJSPage[]): Promise<AppliedOptimization[]> {
    const optimizations: AppliedOptimization[] = [];

    // 1. Prefetch 최적화
    const prefetchOptimizations = this.optimizePrefetching(pages);
    optimizations.push(...prefetchOptimizations);

    // 2. Route Groups 활용
    const routeGroups = this.suggestRouteGroups(pages);
    if (routeGroups.length > 0) {
      optimizations.push({
        optimization: 'add-route-groups',
        category: 'performance',
        details: routeGroups,
      });
    }

    // 3. Parallel Routes 제안
    const parallelRoutes = this.suggestParallelRoutes(pages);
    if (parallelRoutes.length > 0) {
      optimizations.push({
        optimization: 'add-parallel-routes',
        category: 'ux',
        details: parallelRoutes,
      });
    }

    return optimizations;
  }

  private optimizePrefetching(pages: NextJSPage[]): AppliedOptimization[] {
    const optimizations: AppliedOptimization[] = [];

    for (const page of pages) {
      // Link 컴포넌트에 prefetch 최적화
      page.component = page.component.replace(
        /<Link\s+href=["']([^"']+)["']([^>]*?)>/g,
        (match, href, rest) => {
          // 중요한 링크는 prefetch, 덜 중요한 링크는 prefetch={false}
          const shouldPrefetch = this.shouldPrefetchRoute(href);
          const prefetchAttr = shouldPrefetch ? '' : ' prefetch={false}';

          return `<Link href="${href}"${prefetchAttr}${rest}>`;
        },
      );
    }

    return optimizations;
  }
}

// Next.js Config 생성기
class NextConfigGenerator {
  generateOptimizedConfig(optimizations: AppliedOptimization[]): string {
    const config = {
      reactStrictMode: true,
      swcMinify: true,

      images: {
        domains: this.extractImageDomains(optimizations),
        formats: ['image/avif', 'image/webp'],
        deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
        imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
      },

      experimental: {
        optimizeCss: true,
        optimizePackageImports: ['lodash', 'date-fns', '@mui/material'],
      },

      compiler: {
        removeConsole: process.env.NODE_ENV === 'production',
      },

      headers: async () => [
        {
          source: '/:path*',
          headers: [
            {
              key: 'X-DNS-Prefetch-Control',
              value: 'on',
            },
            {
              key: 'X-XSS-Protection',
              value: '1; mode=block',
            },
            {
              key: 'X-Frame-Options',
              value: 'SAMEORIGIN',
            },
          ],
        },
      ],

      webpack: (config, { isServer }) => {
        // 번들 최적화
        if (!isServer) {
          config.optimization.splitChunks = {
            chunks: 'all',
            cacheGroups: {
              default: false,
              vendors: false,
              framework: {
                name: 'framework',
                chunks: 'all',
                test: /[\\/]node_modules[\\/](react|react-dom|scheduler|prop-types|use-subscription)[\\/]/,
                priority: 40,
                enforce: true,
              },
              lib: {
                test(module) {
                  return module.size() > 160000 && /node_modules[/\\]/.test(module.identifier());
                },
                name(module) {
                  const hash = crypto.createHash('sha1');
                  hash.update(module.identifier());
                  return hash.digest('hex').substring(0, 8);
                },
                priority: 30,
                minChunks: 1,
                reuseExistingChunk: true,
              },
            },
          };
        }

        return config;
      },
    };

    return `/** @type {import('next').NextConfig} */
const nextConfig = ${JSON.stringify(config, null, 2)};

module.exports = nextConfig;`;
  }
}

// Next.js App Router 최적화
class AppRouterOptimizer {
  optimizeAppRouter(route: AppRoute): OptimizedAppRoute {
    const optimized = { ...route };

    // 1. Loading UI 추가
    if (!route.hasLoading) {
      optimized.loading = this.generateLoadingUI(route);
    }

    // 2. Error Boundary 추가
    if (!route.hasError) {
      optimized.error = this.generateErrorBoundary(route);
    }

    // 3. Metadata 최적화
    optimized.metadata = this.optimizeMetadata(route);

    // 4. Route Segment Config
    optimized.routeConfig = this.generateRouteConfig(route);

    return optimized;
  }

  private generateLoadingUI(route: AppRoute): string {
    return `export default function Loading() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
    </div>
  );
}`;
  }

  private generateRouteConfig(route: AppRoute): string {
    const config: any = {};

    // Dynamic 설정
    if (route.isDynamic) {
      config.dynamic = 'force-dynamic';
    } else {
      config.dynamic = 'auto';
    }

    // Revalidate 설정
    if (route.revalidate !== undefined) {
      config.revalidate = route.revalidate;
    }

    // Runtime 설정
    config.runtime = route.needsNodeAPIs ? 'nodejs' : 'edge';

    return `export const ${Object.entries(config)
      .map(([key, value]) => `${key} = ${JSON.stringify(value)}`)
      .join(';\nexport const ')};`;
  }
}
```

**검증 기준**:

- [ ] Next.js 특화 최적화
- [ ] Image/Font 최적화
- [ ] App Router 최적화
- [ ] 빌드 설정 최적화

---

### Task 4.67: 보안 코드 생성

#### SubTask 4.67.1: 입력 검증 코드

**담당자**: 보안 엔지니어  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/generation/input_validation_generator.py
from typing import Dict, List, Any, Optional, Type
from dataclasses import dataclass
from enum import Enum
import re

class ValidationType(Enum):
    STRING = "string"
    NUMBER = "number"
    EMAIL = "email"
    URL = "url"
    DATE = "date"
    PHONE = "phone"
    CREDIT_CARD = "credit_card"
    IP_ADDRESS = "ip_address"
    FILE = "file"
    JSON = "json"
    CUSTOM = "custom"

@dataclass
class ValidationRule:
    type: ValidationType
    required: bool
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_values: Optional[List[Any]] = None
    custom_validator: Optional[str] = None
    error_messages: Dict[str, str] = None

@dataclass
class InputValidationSchema:
    name: str
    fields: Dict[str, ValidationRule]
    sanitization_rules: Dict[str, List[str]]
    security_checks: List[str]

class InputValidationGenerator:
    """입력 검증 코드 생성기"""

    def __init__(self):
        self.validator_templates = self._load_validator_templates()
        self.sanitizer = InputSanitizer()
        self.security_validator = SecurityValidator()

    async def generate_validation_code(
        self,
        schema: InputValidationSchema,
        language: str,
        framework: Optional[str] = None
    ) -> GeneratedValidationCode:
        """입력 검증 코드 생성"""

        # 1. 검증 함수 생성
        validation_functions = await self._generate_validation_functions(
            schema,
            language
        )

        # 2. 새니타이제이션 코드 생성
        sanitization_code = await self._generate_sanitization_code(
            schema,
            language
        )

        # 3. 보안 검사 코드 생성
        security_checks = await self._generate_security_checks(
            schema,
            language
        )

        # 4. 프레임워크별 통합 코드 생성
        if framework:
            integration_code = await self._generate_framework_integration(
                schema,
                language,
                framework
            )
        else:
            integration_code = None

        # 5. 테스트 코드 생성
        test_code = await self._generate_validation_tests(
            schema,
            language
        )

        return GeneratedValidationCode(
            validation_functions=validation_functions,
            sanitization_code=sanitization_code,
            security_checks=security_checks,
            integration_code=integration_code,
            test_code=test_code,
            usage_examples=self._generate_usage_examples(schema, language)
        )

    async def _generate_validation_functions(
        self,
        schema: InputValidationSchema,
        language: str
    ) -> Dict[str, str]:
        """검증 함수 생성"""

        functions = {}

        if language == 'python':
            # 메인 검증 클래스
            class_code = f"""
class {schema.name}Validator:
    \"\"\"입력 검증 클래스\"\"\"

    def __init__(self):
        self.errors = {{}}

    def validate(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, List[str]]]:
        \"\"\"전체 데이터 검증\"\"\"
        self.errors = {{}}

        # 각 필드 검증
        {self._generate_field_validations(schema, 'python')}

        # 보안 검사
        {self._generate_security_validations(schema, 'python')}

        return len(self.errors) == 0, self.errors
"""
            functions['main_validator'] = class_code

            # 개별 필드 검증 함수들
            for field_name, rule in schema.fields.items():
                field_func = self._generate_field_validator(
                    field_name,
                    rule,
                    'python'
                )
                functions[f'validate_{field_name}'] = field_func

        elif language in ['javascript', 'typescript']:
            # 메인 검증 함수
            main_func = f"""
{language === 'typescript' ? 'interface ValidationResult { isValid: boolean; errors: Record<string, string[]>; }' : ''}

class {schema.name}Validator {{
    constructor() {{
        this.errors = {{}};
    }}

    validate(data{language === 'typescript' ? ': any' : ''})${ language === 'typescript' ? ': ValidationResult' : ''} {{
        this.errors = {{}};

        // 각 필드 검증
        {self._generate_field_validations(schema, language)}

        // 보안 검사
        {self._generate_security_validations(schema, language)}

        return {{
            isValid: Object.keys(this.errors).length === 0,
            errors: this.errors
        }};
    }}
"""
            functions['main_validator'] = main_func

            # 개별 필드 검증 함수들
            for field_name, rule in schema.fields.items():
                field_func = self._generate_field_validator(
                    field_name,
                    rule,
                    language
                )
                functions[f'validate_{field_name}'] = field_func

        return functions

    def _generate_field_validator(
        self,
        field_name: str,
        rule: ValidationRule,
        language: str
    ) -> str:
        """개별 필드 검증 함수 생성"""

        if language == 'python':
            return self._generate_python_field_validator(field_name, rule)
        elif language in ['javascript', 'typescript']:
            return self._generate_js_field_validator(field_name, rule, language)

    def _generate_python_field_validator(
        self,
        field_name: str,
        rule: ValidationRule
    ) -> str:
        """Python 필드 검증 함수"""

        validations = []

        # 필수 값 검사
        if rule.required:
            validations.append(f"""
        if not value:
            errors.append("{rule.error_messages.get('required', f'{field_name} is required')}")
            return False, errors""")

        # 타입별 검증
        if rule.type == ValidationType.STRING:
            if rule.min_length:
                validations.append(f"""
        if len(value) < {rule.min_length}:
            errors.append("{rule.error_messages.get('min_length', f'{field_name} must be at least {rule.min_length} characters')}")""")

            if rule.max_length:
                validations.append(f"""
        if len(value) > {rule.max_length}:
            errors.append("{rule.error_messages.get('max_length', f'{field_name} must not exceed {rule.max_length} characters')}")""")

            if rule.pattern:
                validations.append(f"""
        if not re.match(r"{rule.pattern}", value):
            errors.append("{rule.error_messages.get('pattern', f'{field_name} format is invalid')}")""")

        elif rule.type == ValidationType.NUMBER:
            validations.append(f"""
        try:
            num_value = float(value)
        except (TypeError, ValueError):
            errors.append("{rule.error_messages.get('type', f'{field_name} must be a number')}")
            return False, errors""")

            if rule.min_value is not None:
                validations.append(f"""
        if num_value < {rule.min_value}:
            errors.append("{rule.error_messages.get('min_value', f'{field_name} must be at least {rule.min_value}')}")""")

            if rule.max_value is not None:
                validations.append(f"""
        if num_value > {rule.max_value}:
            errors.append("{rule.error_messages.get('max_value', f'{field_name} must not exceed {rule.max_value}')}")""")

        elif rule.type == ValidationType.EMAIL:
            validations.append(f"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{{2,}}$'
        if not re.match(email_pattern, value):
            errors.append("{rule.error_messages.get('email', f'{field_name} must be a valid email address')}")""")

        # 사용자 정의 검증
        if rule.custom_validator:
            validations.append(f"""
        # Custom validation
        {rule.custom_validator}""")

        return f"""
    def validate_{field_name}(self, value: Any) -> Tuple[bool, List[str]]:
        \"\"\"Validate {field_name} field\"\"\"
        errors = []

        {"".join(validations)}

        return len(errors) == 0, errors"""

    async def _generate_sanitization_code(
        self,
        schema: InputValidationSchema,
        language: str
    ) -> str:
        """새니타이제이션 코드 생성"""

        if language == 'python':
            sanitization_code = f"""
class {schema.name}Sanitizer:
    \"\"\"입력 새니타이제이션 클래스\"\"\"

    @staticmethod
    def sanitize(data: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"데이터 새니타이제이션\"\"\"
        sanitized = {{}}

        for field, value in data.items():
            if field in {list(schema.fields.keys())}:
                sanitized[field] = {schema.name}Sanitizer._sanitize_field(field, value)

        return sanitized

    @staticmethod
    def _sanitize_field(field_name: str, value: Any) -> Any:
        \"\"\"개별 필드 새니타이제이션\"\"\"

        # HTML 이스케이프
        if isinstance(value, str):
            value = html.escape(value, quote=True)

        # SQL 인젝션 방지
        if isinstance(value, str):
            value = value.replace("'", "''")
            value = value.replace('"', '""')

        # XSS 방지
        if isinstance(value, str):
            # 위험한 태그 제거
            dangerous_tags = ['<script', '<iframe', '<object', '<embed', '<link']
            for tag in dangerous_tags:
                value = re.sub(f'{tag}.*?>.*?</.*?>', '', value, flags=re.IGNORECASE | re.DOTALL)

        # 필드별 추가 새니타이제이션
        {self._generate_field_sanitization(schema, 'python')}

        return value
"""
        elif language in ['javascript', 'typescript']:
            sanitization_code = f"""
class {schema.name}Sanitizer {{
    static sanitize(data{': any' if language === 'typescript' else ''}) {{
        const sanitized = {{}};

        for (const [field, value] of Object.entries(data)) {{
            if ([{', '.join(f'"{field}"' for field in schema.fields.keys())}].includes(field)) {{
                sanitized[field] = this._sanitizeField(field, value);
            }}
        }}

        return sanitized;
    }}

    static _sanitizeField(fieldName{': string' if language === 'typescript' else ''}, value{': any' if language === 'typescript' else ''}) {{
        // HTML 이스케이프
        if (typeof value === 'string') {{
            value = value
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#x27;');
        }}

        // XSS 방지
        if (typeof value === 'string') {{
            const dangerousPatterns = [
                /<script[^>]*>.*?<\\/script>/gi,
                /<iframe[^>]*>.*?<\\/iframe>/gi,
                /javascript:/gi,
                /on\\w+\\s*=/gi
            ];

            for (const pattern of dangerousPatterns) {{
                value = value.replace(pattern, '');
            }}
        }}

        // 필드별 추가 새니타이제이션
        {self._generate_field_sanitization(schema, language)}

        return value;
    }}
}}
"""

        return sanitization_code

    def _generate_field_sanitization(
        self,
        schema: InputValidationSchema,
        language: str
    ) -> str:
        """필드별 새니타이제이션 규칙"""

        sanitization_rules = []

        for field, rules in schema.sanitization_rules.items():
            if language == 'python':
                field_rules = f"""
        if field_name == '{field}':"""
                for rule in rules:
                    if rule == 'trim':
                        field_rules += """
            value = value.strip() if isinstance(value, str) else value"""
                    elif rule == 'lowercase':
                        field_rules += """
            value = value.lower() if isinstance(value, str) else value"""
                    elif rule == 'uppercase':
                        field_rules += """
            value = value.upper() if isinstance(value, str) else value"""
                    elif rule == 'remove_spaces':
                        field_rules += """
            value = value.replace(' ', '') if isinstance(value, str) else value"""

                sanitization_rules.append(field_rules)

            elif language in ['javascript', 'typescript']:
                field_rules = f"""
        if (fieldName === '{field}') {{"""
                for rule in rules:
                    if rule == 'trim':
                        field_rules += """
            value = typeof value === 'string' ? value.trim() : value;"""
                    elif rule == 'lowercase':
                        field_rules += """
            value = typeof value === 'string' ? value.toLowerCase() : value;"""
                    elif rule == 'uppercase':
                        field_rules += """
            value = typeof value === 'string' ? value.toUpperCase() : value;"""
                    elif rule == 'remove_spaces':
                        field_rules += """
            value = typeof value === 'string' ? value.replace(/\\s/g, '') : value;"""

                field_rules += """
        }"""
                sanitization_rules.append(field_rules)

        return '\n'.join(sanitization_rules)

class SecurityValidator:
    """보안 검증 생성기"""

    def generate_security_checks(
        self,
        schema: InputValidationSchema,
        language: str
    ) -> str:
        """보안 검사 코드 생성"""

        security_checks = []

        for check in schema.security_checks:
            if check == 'sql_injection':
                security_checks.append(self._generate_sql_injection_check(language))
            elif check == 'xss':
                security_checks.append(self._generate_xss_check(language))
            elif check == 'command_injection':
                security_checks.append(self._generate_command_injection_check(language))
            elif check == 'path_traversal':
                security_checks.append(self._generate_path_traversal_check(language))
            elif check == 'xxe':
                security_checks.append(self._generate_xxe_check(language))

        return '\n'.join(security_checks)

    def _generate_sql_injection_check(self, language: str) -> str:
        """SQL 인젝션 검사"""

        if language == 'python':
            return """
    def check_sql_injection(self, value: str) -> bool:
        \"\"\"SQL 인젝션 패턴 검사\"\"\"
        sql_patterns = [
            r"(\'|\")\s*(OR|AND)\s*(\'|\")?\s*=\s*(\'|\")?",
            r"(\'|\")\s*;.*--",
            r"UNION\s+SELECT",
            r"INSERT\s+INTO",
            r"DELETE\s+FROM",
            r"DROP\s+TABLE",
            r"<script.*?>.*?</script>",
        ]

        for pattern in sql_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return False

        return True"""

        elif language in ['javascript', 'typescript']:
            return """
    checkSqlInjection(value${': string' if language === 'typescript' else ''}) {
        const sqlPatterns = [
            /('|")\\s*(OR|AND)\\s*('|")?\\s*=\\s*('|")?/i,
            /('|")\\s*;.*--/i,
            /UNION\\s+SELECT/i,
            /INSERT\\s+INTO/i,
            /DELETE\\s+FROM/i,
            /DROP\\s+TABLE/i,
        ];

        for (const pattern of sqlPatterns) {
            if (pattern.test(value)) {
                return false;
            }
        }

        return true;
    }"""
```

**검증 기준**:

- [ ] 다양한 입력 타입 지원
- [ ] 보안 취약점 검사
- [ ] 새니타이제이션 규칙
- [ ] 프레임워크 통합

---

#### SubTask 4.67.2: 인증/인가 코드

**담당자**: 보안 아키텍트  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/generation/auth_code_generator.py
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
import secrets
import hashlib
import jwt

class AuthType(Enum):
    JWT = "jwt"
    SESSION = "session"
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    BASIC = "basic"
    BEARER = "bearer"
    MULTI_FACTOR = "mfa"

@dataclass
class AuthenticationConfig:
    auth_type: AuthType
    secret_key: Optional[str]
    token_expiry: int  # seconds
    refresh_token_enabled: bool
    multi_factor_enabled: bool
    password_policy: PasswordPolicy
    session_config: Optional[SessionConfig]
    oauth_providers: List[OAuthProvider]

@dataclass
class AuthorizationConfig:
    role_based: bool
    permission_based: bool
    resource_based: bool
    hierarchical: bool
    default_role: str
    roles: Dict[str, Role]
    permissions: Dict[str, Permission]

class AuthCodeGenerator:
    """인증/인가 코드 생성기"""

    def __init__(self):
        self.jwt_generator = JWTAuthGenerator()
        self.session_generator = SessionAuthGenerator()
        self.oauth_generator = OAuthGenerator()
        self.rbac_generator = RBACGenerator()
        self.security_utils = SecurityUtilsGenerator()

    async def generate_auth_system(
        self,
        auth_config: AuthenticationConfig,
        authz_config: AuthorizationConfig,
        language: str,
        framework: Optional[str] = None
    ) -> GeneratedAuthSystem:
        """완전한 인증/인가 시스템 생성"""

        # 1. 인증 시스템 생성
        auth_code = await self._generate_authentication_code(
            auth_config,
            language,
            framework
        )

        # 2. 인가 시스템 생성
        authz_code = await self._generate_authorization_code(
            authz_config,
            language,
            framework
        )

        # 3. 미들웨어 생성
        middleware_code = await self._generate_auth_middleware(
            auth_config,
            authz_config,
            language,
            framework
        )

        # 4. 보안 유틸리티 생성
        security_utils = await self.security_utils.generate(
            auth_config,
            language
        )

        # 5. 데이터베이스 스키마 생성
        db_schema = await self._generate_auth_schema(
            auth_config,
            authz_config,
            language
        )

        # 6. API 엔드포인트 생성
        api_endpoints = await self._generate_auth_endpoints(
            auth_config,
            language,
            framework
        )

        return GeneratedAuthSystem(
            authentication=auth_code,
            authorization=authz_code,
            middleware=middleware_code,
            security_utils=security_utils,
            database_schema=db_schema,
            api_endpoints=api_endpoints,
            configuration=self._generate_config_file(auth_config, authz_config),
            tests=await self._generate_auth_tests(auth_config, authz_config, language)
        )

    async def _generate_authentication_code(
        self,
        config: AuthenticationConfig,
        language: str,
        framework: Optional[str]
    ) -> Dict[str, str]:
        """인증 코드 생성"""

        auth_code = {}

        if config.auth_type == AuthType.JWT:
            auth_code.update(await self.jwt_generator.generate(config, language, framework))
        elif config.auth_type == AuthType.SESSION:
            auth_code.update(await self.session_generator.generate(config, language, framework))
        elif config.auth_type == AuthType.OAUTH2:
            auth_code.update(await self.oauth_generator.generate(config, language, framework))

        # 공통 인증 컴포넌트
        auth_code['password_hasher'] = self._generate_password_hasher(config, language)
        auth_code['token_manager'] = self._generate_token_manager(config, language)

        if config.multi_factor_enabled:
            auth_code['mfa_handler'] = self._generate_mfa_handler(config, language)

        return auth_code

    def _generate_password_hasher(
        self,
        config: AuthenticationConfig,
        language: str
    ) -> str:
        """패스워드 해싱 코드 생성"""

        if language == 'python':
            return f"""
import bcrypt
import secrets
from typing import Tuple

class PasswordHasher:
    \"\"\"보안 패스워드 해싱\"\"\"

    def __init__(self, rounds: int = 12):
        self.rounds = rounds

    def hash_password(self, password: str) -> str:
        \"\"\"패스워드 해싱\"\"\"
        # 패스워드 정책 검증
        if not self._validate_password_policy(password):
            raise ValueError("Password does not meet security requirements")

        # Salt 생성 및 해싱
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)

        return hashed.decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        \"\"\"패스워드 검증\"\"\"
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed.encode('utf-8')
        )

    def _validate_password_policy(self, password: str) -> bool:
        \"\"\"패스워드 정책 검증\"\"\"
        # 최소 길이
        if len(password) < {config.password_policy.min_length}:
            return False

        # 복잡도 요구사항
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{{}}|;:,.<>?" for c in password)

        complexity_count = sum([has_upper, has_lower, has_digit, has_special])
        if complexity_count < {config.password_policy.min_complexity}:
            return False

        # 일반적인 패스워드 확인
        common_passwords = self._load_common_passwords()
        if password.lower() in common_passwords:
            return False

        return True

    def generate_secure_password(self, length: int = 16) -> str:
        \"\"\"안전한 패스워드 생성\"\"\"
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
"""

        elif language in ['javascript', 'typescript']:
            return f"""
import bcrypt from 'bcrypt';
import crypto from 'crypto';

class PasswordHasher {{
    private rounds: number;

    constructor(rounds: number = 12) {{
        this.rounds = rounds;
    }}

    async hashPassword(password: string): Promise<string> {{
        // 패스워드 정책 검증
        if (!this.validatePasswordPolicy(password)) {{
            throw new Error('Password does not meet security requirements');
        }}

        // Salt 생성 및 해싱
        const salt = await bcrypt.genSalt(this.rounds);
        const hashed = await bcrypt.hash(password, salt);

        return hashed;
    }}

    async verifyPassword(password: string, hashed: string): Promise<boolean> {{
        return await bcrypt.compare(password, hashed);
    }}

    private validatePasswordPolicy(password: string): boolean {{
        // 최소 길이
        if (password.length < {config.password_policy.min_length}) {{
            return false;
        }}

        // 복잡도 요구사항
        const hasUpper = /[A-Z]/.test(password);
        const hasLower = /[a-z]/.test(password);
        const hasDigit = /[0-9]/.test(password);
        const hasSpecial = /[!@#$%^&*()_+\\-=\\[\\]{{}}|;:,.<>?]/.test(password);

        const complexityCount = [hasUpper, hasLower, hasDigit, hasSpecial]
            .filter(Boolean).length;

        if (complexityCount < {config.password_policy.min_complexity}) {{
            return false;
        }}

        return true;
    }}

    generateSecurePassword(length: number = 16): string {{
        const charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*';
        let password = '';

        for (let i = 0; i < length; i++) {{
            const randomIndex = crypto.randomInt(0, charset.length);
            password += charset[randomIndex];
        }}

        return password;
    }}
}}
"""

class JWTAuthGenerator:
    """JWT 인증 코드 생성기"""

    async def generate(
        self,
        config: AuthenticationConfig,
        language: str,
        framework: Optional[str]
    ) -> Dict[str, str]:
        """JWT 인증 시스템 생성"""

        code_files = {}

        if language == 'python':
            # JWT 매니저
            code_files['jwt_manager.py'] = f"""
import jwt
import datetime
from typing import Dict, Any, Optional, Tuple
import redis
from functools import wraps

class JWTManager:
    \"\"\"JWT 토큰 관리\"\"\"

    def __init__(
        self,
        secret_key: str,
        algorithm: str = 'HS256',
        access_token_expire: int = {config.token_expiry},
        refresh_token_expire: int = {config.token_expiry * 7}
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_expire = access_token_expire
        self.refresh_expire = refresh_token_expire
        self.redis_client = redis.StrictRedis(decode_responses=True)

    def generate_tokens(
        self,
        user_id: str,
        claims: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, str]:
        \"\"\"액세스 토큰과 리프레시 토큰 생성\"\"\"

        # 액세스 토큰 생성
        access_payload = {{
            'user_id': user_id,
            'type': 'access',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=self.access_expire),
            'iat': datetime.datetime.utcnow(),
            'jti': self._generate_jti()
        }}

        if claims:
            access_payload.update(claims)

        access_token = jwt.encode(
            access_payload,
            self.secret_key,
            algorithm=self.algorithm
        )

        # 리프레시 토큰 생성
        refresh_payload = {{
            'user_id': user_id,
            'type': 'refresh',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=self.refresh_expire),
            'iat': datetime.datetime.utcnow(),
            'jti': self._generate_jti()
        }}

        refresh_token = jwt.encode(
            refresh_payload,
            self.secret_key,
            algorithm=self.algorithm
        )

        # 토큰 저장 (블랙리스트 관리용)
        self._store_token_metadata(access_payload['jti'], user_id, 'access')
        self._store_token_metadata(refresh_payload['jti'], user_id, 'refresh')

        return access_token, refresh_token

    def verify_token(self, token: str, token_type: str = 'access') -> Dict[str, Any]:
        \"\"\"토큰 검증\"\"\"
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )

            # 토큰 타입 확인
            if payload.get('type') != token_type:
                raise jwt.InvalidTokenError('Invalid token type')

            # 블랙리스트 확인
            if self._is_blacklisted(payload['jti']):
                raise jwt.InvalidTokenError('Token has been revoked')

            return payload

        except jwt.ExpiredSignatureError:
            raise ValueError('Token has expired')
        except jwt.InvalidTokenError as e:
            raise ValueError(f'Invalid token: {{str(e)}}')

    def refresh_access_token(self, refresh_token: str) -> str:
        \"\"\"리프레시 토큰으로 새 액세스 토큰 생성\"\"\"
        payload = self.verify_token(refresh_token, 'refresh')

        # 새 액세스 토큰 생성
        access_token, _ = self.generate_tokens(
            payload['user_id'],
            {{k: v for k, v in payload.items()
              if k not in ['exp', 'iat', 'jti', 'type']}}
        )

        return access_token

    def revoke_token(self, token: str):
        \"\"\"토큰 무효화 (블랙리스트에 추가)\"\"\"
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={{"verify_exp": False}}
            )

            # 블랙리스트에 추가
            ttl = payload['exp'] - datetime.datetime.utcnow().timestamp()
            if ttl > 0:
                self.redis_client.setex(
                    f"blacklist:{{payload['jti']}}",
                    int(ttl),
                    'revoked'
                )
        except:
            pass  # 이미 무효한 토큰

    def _generate_jti(self) -> str:
        \"\"\"고유 토큰 ID 생성\"\"\"
        import uuid
        return str(uuid.uuid4())

    def _store_token_metadata(self, jti: str, user_id: str, token_type: str):
        \"\"\"토큰 메타데이터 저장\"\"\"
        ttl = self.access_expire if token_type == 'access' else self.refresh_expire
        self.redis_client.setex(
            f"token:{{jti}}",
            ttl,
            f"{{user_id}}:{{token_type}}"
        )

    def _is_blacklisted(self, jti: str) -> bool:
        \"\"\"블랙리스트 확인\"\"\"
        return self.redis_client.exists(f"blacklist:{{jti}}") > 0

# 데코레이터
def jwt_required(f):
    \"\"\"JWT 인증 필수 데코레이터\"\"\"
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_request()  # 구현 필요

        if not token:
            return {{'error': 'No token provided'}}, 401

        try:
            jwt_manager = current_app.jwt_manager
            payload = jwt_manager.verify_token(token)
            request.jwt_payload = payload
            return f(*args, **kwargs)
        except ValueError as e:
            return {{'error': str(e)}}, 401

    return decorated_function
"""

            # 인증 서비스
            code_files['auth_service.py'] = f"""
from typing import Optional, Dict, Any
import asyncio
from datetime import datetime

class AuthenticationService:
    \"\"\"인증 서비스\"\"\"

    def __init__(self, jwt_manager: JWTManager, user_repository: UserRepository):
        self.jwt_manager = jwt_manager
        self.user_repo = user_repository
        self.login_attempts = {{}}  # 실제로는 Redis 사용

    async def login(
        self,
        username: str,
        password: str,
        ip_address: str,
        user_agent: str
    ) -> Dict[str, Any]:
        \"\"\"사용자 로그인\"\"\"

        # 브루트포스 공격 방지
        if self._is_locked_out(username, ip_address):
            raise SecurityError('Account temporarily locked due to multiple failed attempts')

        # 사용자 조회
        user = await self.user_repo.find_by_username(username)
        if not user:
            self._record_failed_attempt(username, ip_address)
            raise ValueError('Invalid credentials')

        # 패스워드 검증
        password_hasher = PasswordHasher()
        if not password_hasher.verify_password(password, user.password_hash):
            self._record_failed_attempt(username, ip_address)
            raise ValueError('Invalid credentials')

        # 계정 상태 확인
        if not user.is_active:
            raise ValueError('Account is not active')

        if user.is_locked:
            raise ValueError('Account is locked')

        # MFA 확인 (활성화된 경우)
        if user.mfa_enabled:
            # MFA 세션 생성
            mfa_token = self._create_mfa_session(user.id)
            return {{
                'requires_mfa': True,
                'mfa_token': mfa_token
            }}

        # 토큰 생성
        access_token, refresh_token = self.jwt_manager.generate_tokens(
            user.id,
            {{
                'username': user.username,
                'roles': [role.name for role in user.roles],
                'permissions': self._get_user_permissions(user)
            }}
        )

        # 로그인 기록
        await self._record_login(user.id, ip_address, user_agent)

        # 실패 시도 초기화
        self._reset_failed_attempts(username, ip_address)

        return {{
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {{
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'roles': [role.name for role in user.roles]
            }}
        }}

    async def logout(self, token: str, refresh_token: Optional[str] = None):
        \"\"\"로그아웃\"\"\"
        # 토큰 무효화
        self.jwt_manager.revoke_token(token)

        if refresh_token:
            self.jwt_manager.revoke_token(refresh_token)

        # 세션 정리
        payload = self.jwt_manager.verify_token(token, verify_exp=False)
        await self._cleanup_user_sessions(payload['user_id'])

    async def verify_mfa(
        self,
        mfa_token: str,
        code: str
    ) -> Dict[str, Any]:
        \"\"\"MFA 검증\"\"\"
        # MFA 세션 확인
        session = self._get_mfa_session(mfa_token)
        if not session:
            raise ValueError('Invalid MFA session')

        # 코드 검증
        user = await self.user_repo.find_by_id(session['user_id'])
        if not self._verify_mfa_code(user, code):
            raise ValueError('Invalid MFA code')

        # 정식 토큰 발급
        access_token, refresh_token = self.jwt_manager.generate_tokens(
            user.id,
            {{
                'username': user.username,
                'roles': [role.name for role in user.roles],
                'permissions': self._get_user_permissions(user),
                'mfa_verified': True
            }}
        )

        # MFA 세션 삭제
        self._delete_mfa_session(mfa_token)

        return {{
            'access_token': access_token,
            'refresh_token': refresh_token
        }}
"""

        elif language in ['javascript', 'typescript']:
            # JWT 매니저 (TypeScript)
            code_files['jwtManager.ts'] = f"""
import jwt from 'jsonwebtoken';
import {{ Redis }} from 'ioredis';
import {{ v4 as uuidv4 }} from 'uuid';

interface TokenPayload {{
    user_id: string;
    type: 'access' | 'refresh';
    exp: number;
    iat: number;
    jti: string;
    [key: string]: any;
}}

interface GeneratedTokens {{
    accessToken: string;
    refreshToken: string;
}}

export class JWTManager {{
    private redis: Redis;

    constructor(
        private readonly secretKey: string,
        private readonly algorithm: jwt.Algorithm = 'HS256',
        private readonly accessExpire: number = {config.token_expiry},
        private readonly refreshExpire: number = {config.token_expiry * 7}
    ) {{
        this.redis = new Redis();
    }}

    async generateTokens(
        userId: string,
        claims?: Record<string, any>
    ): Promise<GeneratedTokens> {{
        // 액세스 토큰 생성
        const accessPayload: TokenPayload = {{
            user_id: userId,
            type: 'access',
            exp: Math.floor(Date.now() / 1000) + this.accessExpire,
            iat: Math.floor(Date.now() / 1000),
            jti: uuidv4(),
            ...claims
        }};

        const accessToken = jwt.sign(
            accessPayload,
            this.secretKey,
            {{ algorithm: this.algorithm }}
        );

        // 리프레시 토큰 생성
        const refreshPayload: TokenPayload = {{
            user_id: userId,
            type: 'refresh',
            exp: Math.floor(Date.now() / 1000) + this.refreshExpire,
            iat: Math.floor(Date.now() / 1000),
            jti: uuidv4()
        }};

        const refreshToken = jwt.sign(
            refreshPayload,
            this.secretKey,
            {{ algorithm: this.algorithm }}
        );

        // 토큰 메타데이터 저장
        await this.storeTokenMetadata(accessPayload.jti, userId, 'access');
        await this.storeTokenMetadata(refreshPayload.jti, userId, 'refresh');

        return {{ accessToken, refreshToken }};
    }}

    async verifyToken(
        token: string,
        tokenType: 'access' | 'refresh' = 'access'
    ): Promise<TokenPayload> {{
        try {{
            const payload = jwt.verify(
                token,
                this.secretKey,
                {{ algorithms: [this.algorithm] }}
            ) as TokenPayload;

            // 토큰 타입 확인
            if (payload.type !== tokenType) {{
                throw new Error('Invalid token type');
            }}

            // 블랙리스트 확인
            const isBlacklisted = await this.isBlacklisted(payload.jti);
            if (isBlacklisted) {{
                throw new Error('Token has been revoked');
            }}

            return payload;

        }} catch (error) {{
            if (error instanceof jwt.TokenExpiredError) {{
                throw new Error('Token has expired');
            }} else if (error instanceof jwt.JsonWebTokenError) {{
                throw new Error('Invalid token');
            }}
            throw error;
        }}
    }}

    async revokeToken(token: string): Promise<void> {{
        try {{
            const payload = jwt.decode(token) as TokenPayload;
            if (!payload || !payload.jti) return;

            // 블랙리스트에 추가
            const ttl = payload.exp - Math.floor(Date.now() / 1000);
            if (ttl > 0) {{
                await this.redis.setex(
                    `blacklist:${{payload.jti}}`,
                    ttl,
                    'revoked'
                );
            }}
        }} catch {{
            // 이미 무효한 토큰
        }}
    }}

    private async storeTokenMetadata(
        jti: string,
        userId: string,
        tokenType: string
    ): Promise<void> {{
        const ttl = tokenType === 'access' ? this.accessExpire : this.refreshExpire;
        await this.redis.setex(
            `token:${{jti}}`,
            ttl,
            `${{userId}}:${{tokenType}}`
        );
    }}

    private async isBlacklisted(jti: string): Promise<boolean> {{
        const exists = await this.redis.exists(`blacklist:${{jti}}`);
        return exists === 1;
    }}
}}

// Express 미들웨어
export const jwtMiddleware = (jwtManager: JWTManager) => {{
    return async (req: any, res: any, next: any) => {{
        const token = extractTokenFromRequest(req);

        if (!token) {{
            return res.status(401).json({{ error: 'No token provided' }});
        }}

        try {{
            const payload = await jwtManager.verifyToken(token);
            req.user = payload;
            next();
        }} catch (error) {{
            return res.status(401).json({{ error: error.message }});
        }}
    }};
}};
"""

        return code_files

class RBACGenerator:
    """역할 기반 접근 제어 생성기"""

    async def generate(
        self,
        config: AuthorizationConfig,
        language: str,
        framework: Optional[str]
    ) -> Dict[str, str]:
        """RBAC 시스템 생성"""

        if language == 'python':
            return {
                'rbac_system.py': f"""
from typing import List, Dict, Set, Optional
from enum import Enum
from functools import wraps
import asyncio

class Permission:
    \"\"\"권한 클래스\"\"\"

    def __init__(self, name: str, resource: str, action: str):
        self.name = name
        self.resource = resource
        self.action = action

    def __str__(self):
        return f"{{self.resource}}:{{self.action}}"

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

class Role:
    \"\"\"역할 클래스\"\"\"

    def __init__(self, name: str, permissions: Set[Permission], parent: Optional['Role'] = None):
        self.name = name
        self.permissions = permissions
        self.parent = parent

    def has_permission(self, permission: Permission) -> bool:
        \"\"\"권한 확인\"\"\"
        # 직접 권한 확인
        if permission in self.permissions:
            return True

        # 상위 역할 권한 확인 (계층적 RBAC)
        if self.parent:
            return self.parent.has_permission(permission)

        return False

    def get_all_permissions(self) -> Set[Permission]:
        \"\"\"모든 권한 반환 (상속 포함)\"\"\"
        all_perms = self.permissions.copy()

        if self.parent:
            all_perms.update(self.parent.get_all_permissions())

        return all_perms

class RBACSystem:
    \"\"\"역할 기반 접근 제어 시스템\"\"\"

    def __init__(self):
        self.roles: Dict[str, Role] = {{}}
        self.permissions: Dict[str, Permission] = {{}}
        self._initialize_default_roles()

    def _initialize_default_roles(self):
        \"\"\"기본 역할 초기화\"\"\"
        # 권한 정의
        {self._generate_permission_definitions(config)}

        # 역할 정의
        {self._generate_role_definitions(config)}

    def check_permission(
        self,
        user_roles: List[str],
        resource: str,
        action: str
    ) -> bool:
        \"\"\"권한 확인\"\"\"
        required_permission = Permission('', resource, action)

        for role_name in user_roles:
            role = self.roles.get(role_name)
            if role and role.has_permission(required_permission):
                return True

        return False

    def get_user_permissions(self, user_roles: List[str]) -> Set[Permission]:
        \"\"\"사용자의 모든 권한 반환\"\"\"
        all_permissions = set()

        for role_name in user_roles:
            role = self.roles.get(role_name)
            if role:
                all_permissions.update(role.get_all_permissions())

        return all_permissions

# 데코레이터
def require_permission(resource: str, action: str):
    \"\"\"권한 확인 데코레이터\"\"\"
    def decorator(f):
        @wraps(f)
        async def decorated_function(*args, **kwargs):
            # JWT payload에서 사용자 정보 추출
            user = getattr(request, 'jwt_payload', None)
            if not user:
                return {{'error': 'Unauthorized'}}, 401

            # 권한 확인
            rbac = current_app.rbac_system
            if not rbac.check_permission(user.get('roles', []), resource, action):
                return {{'error': 'Forbidden'}}, 403

            return await f(*args, **kwargs)

        return decorated_function
    return decorator

def require_role(role: str):
    \"\"\"역할 확인 데코레이터\"\"\"
    def decorator(f):
        @wraps(f)
        async def decorated_function(*args, **kwargs):
            user = getattr(request, 'jwt_payload', None)
            if not user:
                return {{'error': 'Unauthorized'}}, 401

            if role not in user.get('roles', []):
                return {{'error': 'Forbidden'}}, 403

            return await f(*args, **kwargs)

        return decorated_function
    return decorator

# 리소스 기반 권한 확인
class ResourceBasedAuthorization:
    \"\"\"리소스 기반 권한 관리\"\"\"

    def __init__(self, rbac_system: RBACSystem):
        self.rbac = rbac_system

    async def can_access_resource(
        self,
        user_id: str,
        resource_id: str,
        action: str,
        resource_owner_id: Optional[str] = None
    ) -> bool:
        \"\"\"리소스 접근 권한 확인\"\"\"

        # 소유자 확인
        if resource_owner_id and user_id == resource_owner_id:
            return True

        # 역할 기반 권한 확인
        user = await self._get_user(user_id)
        return self.rbac.check_permission(
            user.roles,
            f"resource:{{resource_id}}",
            action
        )

    async def filter_accessible_resources(
        self,
        user_id: str,
        resources: List[Dict[str, Any]],
        action: str
    ) -> List[Dict[str, Any]]:
        \"\"\"접근 가능한 리소스만 필터링\"\"\"
        accessible = []

        for resource in resources:
            if await self.can_access_resource(
                user_id,
                resource['id'],
                action,
                resource.get('owner_id')
            ):
                accessible.append(resource)

        return accessible
""",
                'permission_definitions.py': self._generate_permission_file(config)
            }

    def _generate_permission_definitions(self, config: AuthorizationConfig) -> str:
        """권한 정의 생성"""

        permissions = []
        for perm_name, perm in config.permissions.items():
            permissions.append(
                f"self.permissions['{perm_name}'] = Permission('{perm_name}', '{perm.resource}', '{perm.action}')"
            )

        return '\n        '.join(permissions)

    def _generate_role_definitions(self, config: AuthorizationConfig) -> str:
        """역할 정의 생성"""

        roles = []
        for role_name, role in config.roles.items():
            perms = ', '.join(f"self.permissions['{p}']" for p in role.permissions)
            parent = f"self.roles['{role.parent}']" if role.parent else "None"

            roles.append(
                f"self.roles['{role_name}'] = Role('{role_name}', {{{perms}}}, {parent})"
            )

        return '\n        '.join(roles)

class SecurityUtilsGenerator:
    """보안 유틸리티 생성기"""

    async def generate(
        self,
        config: AuthenticationConfig,
        language: str
    ) -> Dict[str, str]:
        """보안 유틸리티 코드 생성"""

        if language == 'python':
            return {
                'security_utils.py': f"""
import secrets
import string
import hmac
import hashlib
from typing import Optional, Tuple
import pyotp
import qrcode
from io import BytesIO
import base64

class SecurityUtils:
    \"\"\"보안 유틸리티\"\"\"

    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        \"\"\"안전한 토큰 생성\"\"\"
        return secrets.token_urlsafe(length)

    @staticmethod
    def generate_otp_secret() -> str:
        \"\"\"OTP 시크릿 생성\"\"\"
        return pyotp.random_base32()

    @staticmethod
    def generate_qr_code(
        otp_uri: str
    ) -> str:
        \"\"\"OTP QR 코드 생성\"\"\"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(otp_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format='PNG')

        return base64.b64encode(buf.getvalue()).decode()

    @staticmethod
    def verify_otp(secret: str, token: str) -> bool:
        \"\"\"OTP 토큰 검증\"\"\"
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)

    @staticmethod
    def constant_time_compare(val1: str, val2: str) -> bool:
        \"\"\"상수 시간 문자열 비교\"\"\"
        return hmac.compare_digest(val1, val2)

    @staticmethod
    def generate_csrf_token() -> str:
        \"\"\"CSRF 토큰 생성\"\"\"
        return secrets.token_hex(16)

    @staticmethod
    def validate_csrf_token(
        token: str,
        session_token: str
    ) -> bool:
        \"\"\"CSRF 토큰 검증\"\"\"
        return SecurityUtils.constant_time_compare(token, session_token)

class RateLimiter:
    \"\"\"요청 제한\"\"\"

    def __init__(self, redis_client):
        self.redis = redis_client

    async def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> Tuple[bool, int]:
        \"\"\"요청 제한 확인\"\"\"
        current = await self.redis.incr(key)

        if current == 1:
            await self.redis.expire(key, window_seconds)

        if current > max_requests:
            ttl = await self.redis.ttl(key)
            return False, ttl

        return True, 0

    async def reset_limit(self, key: str):
        \"\"\"제한 초기화\"\"\"
        await self.redis.delete(key)

class IPWhitelist:
    \"\"\"IP 화이트리스트\"\"\"

    def __init__(self, allowed_ips: List[str]):
        self.allowed_ips = set(allowed_ips)
        self.allowed_networks = []

        # CIDR 표기법 파싱
        for ip in allowed_ips:
            if '/' in ip:
                import ipaddress
                self.allowed_networks.append(ipaddress.ip_network(ip))

    def is_allowed(self, ip: str) -> bool:
        \"\"\"IP 허용 여부 확인\"\"\"
        # 직접 매치
        if ip in self.allowed_ips:
            return True

        # 네트워크 매치
        import ipaddress
        ip_obj = ipaddress.ip_address(ip)

        for network in self.allowed_networks:
            if ip_obj in network:
                return True

        return False
"""
            }
```

**검증 기준**:

- [ ] JWT/Session 인증 구현
- [ ] RBAC 권한 시스템
- [ ] MFA 지원
- [ ] 보안 유틸리티 포함

#### SubTask 4.67.3: 암호화 구현

**담당자**: 암호화 전문가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/generation/encryption_generator.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class EncryptionType(Enum):
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    CHACHA20_POLY1305 = "chacha20_poly1305"
    HYBRID = "hybrid"

@dataclass
class EncryptionConfig:
    encryption_type: EncryptionType
    key_derivation: str  # 'pbkdf2', 'scrypt', 'argon2'
    key_rotation_enabled: bool
    key_rotation_period: int  # days
    data_classification: Dict[str, str]  # field -> classification
    compliance_requirements: List[str]  # 'PCI-DSS', 'HIPAA', 'GDPR'

class EncryptionCodeGenerator:
    """암호화 코드 생성기"""

    def __init__(self):
        self.symmetric_generator = SymmetricEncryptionGenerator()
        self.asymmetric_generator = AsymmetricEncryptionGenerator()
        self.key_management_generator = KeyManagementGenerator()
        self.field_encryption_generator = FieldEncryptionGenerator()

    async def generate_encryption_system(
        self,
        config: EncryptionConfig,
        language: str,
        framework: Optional[str] = None
    ) -> GeneratedEncryptionSystem:
        """완전한 암호화 시스템 생성"""

        # 1. 암호화 핵심 라이브러리
        core_encryption = await self._generate_core_encryption(
            config,
            language
        )

        # 2. 키 관리 시스템
        key_management = await self.key_management_generator.generate(
            config,
            language
        )

        # 3. 필드 레벨 암호화
        field_encryption = await self.field_encryption_generator.generate(
            config,
            language
        )

        # 4. 암호화 미들웨어
        middleware = await self._generate_encryption_middleware(
            config,
            language,
            framework
        )

        # 5. 유틸리티 함수들
        utilities = await self._generate_encryption_utilities(
            config,
            language
        )

        # 6. 테스트 코드
        tests = await self._generate_encryption_tests(
            config,
            language
        )

        return GeneratedEncryptionSystem(
            core=core_encryption,
            key_management=key_management,
            field_encryption=field_encryption,
            middleware=middleware,
            utilities=utilities,
            tests=tests,
            configuration=self._generate_config(config)
        )

    async def _generate_core_encryption(
        self,
        config: EncryptionConfig,
        language: str
    ) -> Dict[str, str]:
        """핵심 암호화 코드 생성"""

        if config.encryption_type in [EncryptionType.AES_256_GCM, EncryptionType.AES_256_CBC]:
            return await self.symmetric_generator.generate(config, language)
        elif config.encryption_type in [EncryptionType.RSA_2048, EncryptionType.RSA_4096]:
            return await self.asymmetric_generator.generate(config, language)
        elif config.encryption_type == EncryptionType.HYBRID:
            # 하이브리드 암호화 (RSA + AES)
            symmetric = await self.symmetric_generator.generate(config, language)
            asymmetric = await self.asymmetric_generator.generate(config, language)
            return {**symmetric, **asymmetric, **self._generate_hybrid_wrapper(config, language)}

        return {}

    def _generate_hybrid_wrapper(
        self,
        config: EncryptionConfig,
        language: str
    ) -> Dict[str, str]:
        """하이브리드 암호화 래퍼"""

        if language == 'python':
            return {
                'hybrid_encryption.py': f"""
from typing import Tuple, Dict, Any
import json
import base64

class HybridEncryption:
    \"\"\"하이브리드 암호화 (RSA + AES)\"\"\"

    def __init__(self):
        self.rsa_encryptor = RSAEncryption()
        self.aes_encryptor = AESEncryption()

    def encrypt(
        self,
        data: bytes,
        public_key: bytes
    ) -> Dict[str, str]:
        \"\"\"
        대용량 데이터를 위한 하이브리드 암호화
        1. AES 키로 데이터 암호화
        2. RSA로 AES 키 암호화
        \"\"\"

        # AES 키 생성
        aes_key = self.aes_encryptor.generate_key()

        # 데이터를 AES로 암호화
        encrypted_data, nonce, tag = self.aes_encryptor.encrypt(data, aes_key)

        # AES 키를 RSA로 암호화
        encrypted_key = self.rsa_encryptor.encrypt(aes_key, public_key)

        # 결과 패키징
        return {{
            'encrypted_data': base64.b64encode(encrypted_data).decode(),
            'encrypted_key': base64.b64encode(encrypted_key).decode(),
            'nonce': base64.b64encode(nonce).decode(),
            'tag': base64.b64encode(tag).decode() if tag else None,
            'algorithm': 'RSA-AES-HYBRID'
        }}

    def decrypt(
        self,
        encrypted_package: Dict[str, str],
        private_key: bytes
    ) -> bytes:
        \"\"\"하이브리드 복호화\"\"\"

        # Base64 디코딩
        encrypted_data = base64.b64decode(encrypted_package['encrypted_data'])
        encrypted_key = base64.b64decode(encrypted_package['encrypted_key'])
        nonce = base64.b64decode(encrypted_package['nonce'])
        tag = base64.b64decode(encrypted_package['tag']) if encrypted_package.get('tag') else None

        # RSA로 AES 키 복호화
        aes_key = self.rsa_encryptor.decrypt(encrypted_key, private_key)

        # AES로 데이터 복호화
        decrypted_data = self.aes_encryptor.decrypt(
            encrypted_data,
            aes_key,
            nonce,
            tag
        )

        return decrypted_data
"""
            }

class SymmetricEncryptionGenerator:
    """대칭키 암호화 생성기"""

    async def generate(
        self,
        config: EncryptionConfig,
        language: str
    ) -> Dict[str, str]:
        """대칭키 암호화 코드 생성"""

        if language == 'python':
            if config.encryption_type == EncryptionType.AES_256_GCM:
                return {
                    'aes_encryption.py': f"""
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import base64
from typing import Tuple, Optional

class AESEncryption:
    \"\"\"AES-256-GCM 암호화\"\"\"

    def __init__(self, key: Optional[bytes] = None):
        self.key = key
        self.backend = default_backend()

    def generate_key(self) -> bytes:
        \"\"\"256비트 키 생성\"\"\"
        return os.urandom(32)

    def derive_key(
        self,
        password: str,
        salt: bytes,
        iterations: int = 100000
    ) -> bytes:
        \"\"\"패스워드에서 키 유도\"\"\"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
            backend=self.backend
        )
        return kdf.derive(password.encode())

    def encrypt(
        self,
        plaintext: bytes,
        key: Optional[bytes] = None,
        associated_data: Optional[bytes] = None
    ) -> Tuple[bytes, bytes, bytes]:
        \"\"\"AES-GCM 암호화\"\"\"

        key = key or self.key
        if not key:
            raise ValueError("Encryption key not provided")

        # 96비트 nonce 생성 (GCM 권장)
        nonce = os.urandom(12)

        # 암호화
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce),
            backend=self.backend
        )
        encryptor = cipher.encryptor()

        # Associated data 추가 (선택적)
        if associated_data:
            encryptor.authenticate_additional_data(associated_data)

        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        return ciphertext, nonce, encryptor.tag

    def decrypt(
        self,
        ciphertext: bytes,
        key: Optional[bytes] = None,
        nonce: bytes = None,
        tag: bytes = None,
        associated_data: Optional[bytes] = None
    ) -> bytes:
        \"\"\"AES-GCM 복호화\"\"\"

        key = key or self.key
        if not key:
            raise ValueError("Decryption key not provided")

        # 복호화
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce, tag),
            backend=self.backend
        )
        decryptor = cipher.decryptor()

        # Associated data 검증 (선택적)
        if associated_data:
            decryptor.authenticate_additional_data(associated_data)

        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        return plaintext

    def encrypt_string(
        self,
        plaintext: str,
        key: Optional[bytes] = None
    ) -> Dict[str, str]:
        \"\"\"문자열 암호화 (Base64 인코딩)\"\"\"

        plaintext_bytes = plaintext.encode('utf-8')
        ciphertext, nonce, tag = self.encrypt(plaintext_bytes, key)

        return {{
            'ciphertext': base64.b64encode(ciphertext).decode(),
            'nonce': base64.b64encode(nonce).decode(),
            'tag': base64.b64encode(tag).decode()
        }}

    def decrypt_string(
        self,
        encrypted_data: Dict[str, str],
        key: Optional[bytes] = None
    ) -> str:
        \"\"\"문자열 복호화\"\"\"

        ciphertext = base64.b64decode(encrypted_data['ciphertext'])
        nonce = base64.b64decode(encrypted_data['nonce'])
        tag = base64.b64decode(encrypted_data['tag'])

        plaintext_bytes = self.decrypt(ciphertext, key, nonce, tag)

        return plaintext_bytes.decode('utf-8')
"""
                }
            elif config.encryption_type == EncryptionType.CHACHA20_POLY1305:
                return {
                    'chacha20_encryption.py': f"""
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
import os
import base64
from typing import Dict

class ChaCha20Encryption:
    \"\"\"ChaCha20-Poly1305 암호화\"\"\"

    def __init__(self, key: Optional[bytes] = None):
        if key:
            self.cipher = ChaCha20Poly1305(key)
        else:
            self.cipher = None

    def generate_key(self) -> bytes:
        \"\"\"256비트 키 생성\"\"\"
        key = ChaCha20Poly1305.generate_key()
        self.cipher = ChaCha20Poly1305(key)
        return key

    def encrypt(
        self,
        plaintext: bytes,
        associated_data: Optional[bytes] = None
    ) -> Tuple[bytes, bytes]:
        \"\"\"ChaCha20-Poly1305 암호화\"\"\"

        if not self.cipher:
            raise ValueError("Cipher not initialized")

        # 96비트 nonce
        nonce = os.urandom(12)

        # 암호화
        ciphertext = self.cipher.encrypt(
            nonce,
            plaintext,
            associated_data
        )

        return ciphertext, nonce

    def decrypt(
        self,
        ciphertext: bytes,
        nonce: bytes,
        associated_data: Optional[bytes] = None
    ) -> bytes:
        \"\"\"ChaCha20-Poly1305 복호화\"\"\"

        if not self.cipher:
            raise ValueError("Cipher not initialized")

        # 복호화
        plaintext = self.cipher.decrypt(
            nonce,
            ciphertext,
            associated_data
        )

        return plaintext
"""
                }

        elif language in ['javascript', 'typescript']:
            return {
                'aesEncryption.ts': f"""
import * as crypto from 'crypto';

interface EncryptedData {{
    ciphertext: string;
    iv: string;
    tag: string;
    algorithm: string;
}}

export class AESEncryption {{
    private algorithm = 'aes-256-gcm';
    private keyLength = 32; // 256 bits
    private ivLength = 16; // 128 bits
    private tagLength = 16; // 128 bits

    generateKey(): Buffer {{
        return crypto.randomBytes(this.keyLength);
    }}

    deriveKey(
        password: string,
        salt: Buffer,
        iterations: number = 100000
    ): Buffer {{
        return crypto.pbkdf2Sync(
            password,
            salt,
            iterations,
            this.keyLength,
            'sha256'
        );
    }}

    encrypt(
        plaintext: string,
        key: Buffer,
        associatedData?: Buffer
    ): EncryptedData {{
        // IV 생성
        const iv = crypto.randomBytes(this.ivLength);

        // 암호화
        const cipher = crypto.createCipheriv(this.algorithm, key, iv);

        if (associatedData) {{
            cipher.setAAD(associatedData);
        }}

        const encrypted = Buffer.concat([
            cipher.update(plaintext, 'utf8'),
            cipher.final()
        ]);

        const tag = cipher.getAuthTag();

        return {{
            ciphertext: encrypted.toString('base64'),
            iv: iv.toString('base64'),
            tag: tag.toString('base64'),
            algorithm: this.algorithm
        }};
    }}

    decrypt(
        encryptedData: EncryptedData,
        key: Buffer,
        associatedData?: Buffer
    ): string {{
        // Base64 디코딩
        const ciphertext = Buffer.from(encryptedData.ciphertext, 'base64');
        const iv = Buffer.from(encryptedData.iv, 'base64');
        const tag = Buffer.from(encryptedData.tag, 'base64');

        // 복호화
        const decipher = crypto.createDecipheriv(this.algorithm, key, iv);
        decipher.setAuthTag(tag);

        if (associatedData) {{
            decipher.setAAD(associatedData);
        }}

        const decrypted = Buffer.concat([
            decipher.update(ciphertext),
            decipher.final()
        ]);

        return decrypted.toString('utf8');
    }}

    // 파일 암호화를 위한 스트림 기반 메서드
    createEncryptStream(
        key: Buffer,
        outputStream: NodeJS.WritableStream
    ): {{ cipher: crypto.Cipher; iv: Buffer }} {{
        const iv = crypto.randomBytes(this.ivLength);
        const cipher = crypto.createCipheriv(this.algorithm, key, iv);

        // IV를 먼저 쓰기
        outputStream.write(iv);

        return {{ cipher, iv }};
    }}

    createDecryptStream(
        key: Buffer,
        iv: Buffer
    ): crypto.Decipher {{
        return crypto.createDecipheriv(this.algorithm, key, iv);
    }}
}}
"""
            }

class KeyManagementGenerator:
    """키 관리 시스템 생성기"""

    async def generate(
        self,
        config: EncryptionConfig,
        language: str
    ) -> Dict[str, str]:
        """키 관리 코드 생성"""

        if language == 'python':
            return {
                'key_management.py': f"""
import os
import json
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import boto3  # AWS KMS
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import redis

class KeyManagementSystem:
    \"\"\"암호화 키 관리 시스템\"\"\"

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.StrictRedis()
        self.kms_client = None

        if config.get('use_aws_kms'):
            self.kms_client = boto3.client('kms')
            self.master_key_id = config['kms_master_key_id']

    def generate_data_encryption_key(self) -> Tuple[bytes, str]:
        \"\"\"데이터 암호화 키 생성\"\"\"

        if self.kms_client:
            # AWS KMS 사용
            response = self.kms_client.generate_data_key(
                KeyId=self.master_key_id,
                KeySpec='AES_256'
            )

            plaintext_key = response['Plaintext']
            encrypted_key = base64.b64encode(response['CiphertextBlob']).decode()

            return plaintext_key, encrypted_key
        else:
            # 로컬 키 생성
            key = Fernet.generate_key()
            encrypted_key = self._encrypt_with_master_key(key)

            return key, encrypted_key

    def decrypt_data_encryption_key(self, encrypted_key: str) -> bytes:
        \"\"\"데이터 암호화 키 복호화\"\"\"

        if self.kms_client:
            # AWS KMS 사용
            ciphertext_blob = base64.b64decode(encrypted_key)
            response = self.kms_client.decrypt(CiphertextBlob=ciphertext_blob)

            return response['Plaintext']
        else:
            # 로컬 복호화
            return self._decrypt_with_master_key(encrypted_key)

    def rotate_encryption_keys(self):
        \"\"\"암호화 키 순환\"\"\"

        # 새 키 생성
        new_key, encrypted_new_key = self.generate_data_encryption_key()

        # 기존 데이터 재암호화 스케줄링
        self._schedule_reencryption(new_key)

        # 키 메타데이터 업데이트
        key_metadata = {{
            'key_id': self._generate_key_id(),
            'created_at': datetime.utcnow().isoformat(),
            'encrypted_key': encrypted_new_key,
            'status': 'active',
            'rotation_scheduled': (
                datetime.utcnow() + timedelta(days={config.key_rotation_period})
            ).isoformat()
        }}

        # 저장
        self._store_key_metadata(key_metadata)

        return key_metadata['key_id']

    def get_active_key(self) -> Tuple[bytes, str]:
        \"\"\"현재 활성 키 가져오기\"\"\"

        # Redis에서 활성 키 ID 가져오기
        active_key_id = self.redis_client.get('active_key_id')
        if not active_key_id:
            raise ValueError("No active encryption key found")

        # 키 메타데이터 가져오기
        key_metadata = self._get_key_metadata(active_key_id.decode())

        # 키 복호화
        plaintext_key = self.decrypt_data_encryption_key(
            key_metadata['encrypted_key']
        )

        return plaintext_key, key_metadata['key_id']

    def _encrypt_with_master_key(self, data: bytes) -> str:
        \"\"\"마스터 키로 암호화\"\"\"

        # 환경 변수에서 마스터 키 로드
        master_key = os.environ.get('MASTER_ENCRYPTION_KEY')
        if not master_key:
            raise ValueError("Master encryption key not found")

        f = Fernet(master_key.encode())
        encrypted = f.encrypt(data)

        return base64.b64encode(encrypted).decode()

    def _decrypt_with_master_key(self, encrypted_data: str) -> bytes:
        \"\"\"마스터 키로 복호화\"\"\"

        master_key = os.environ.get('MASTER_ENCRYPTION_KEY')
        if not master_key:
            raise ValueError("Master encryption key not found")

        f = Fernet(master_key.encode())
        encrypted_bytes = base64.b64decode(encrypted_data)

        return f.decrypt(encrypted_bytes)

class KeyRotationScheduler:
    \"\"\"키 순환 스케줄러\"\"\"

    def __init__(self, kms: KeyManagementSystem):
        self.kms = kms
        self.rotation_period = {config.key_rotation_period}  # days

    async def check_and_rotate_keys(self):
        \"\"\"키 순환 필요성 확인 및 실행\"\"\"

        active_key_metadata = self.kms._get_active_key_metadata()
        created_at = datetime.fromisoformat(active_key_metadata['created_at'])

        if datetime.utcnow() - created_at > timedelta(days=self.rotation_period):
            # 키 순환 실행
            new_key_id = self.kms.rotate_encryption_keys()

            # 알림 발송
            await self._notify_key_rotation(new_key_id)

            return new_key_id

        return None
"""
            }

class FieldEncryptionGenerator:
    """필드 레벨 암호화 생성기"""

    async def generate(
        self,
        config: EncryptionConfig,
        language: str
    ) -> Dict[str, str]:
        """필드 암호화 코드 생성"""

        if language == 'python':
            return {
                'field_encryption.py': f"""
from typing import Dict, List, Any, Optional, Type
from dataclasses import dataclass, field
import json
from functools import wraps

@dataclass
class FieldEncryptionPolicy:
    \"\"\"필드 암호화 정책\"\"\"

    field_name: str
    encryption_type: str  # 'deterministic' or 'randomized'
    data_type: str
    searchable: bool = False

class FieldLevelEncryption:
    \"\"\"필드 레벨 암호화\"\"\"

    def __init__(self, encryption_service: AESEncryption, kms: KeyManagementSystem):
        self.encryption = encryption_service
        self.kms = kms
        self.policies: Dict[str, FieldEncryptionPolicy] = {{}}
        self._load_encryption_policies()

    def _load_encryption_policies(self):
        \"\"\"암호화 정책 로드\"\"\"
        # 설정에서 정책 로드
        {self._generate_policy_definitions(config)}

    def encrypt_fields(
        self,
        data: Dict[str, Any],
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        \"\"\"선택적 필드 암호화\"\"\"

        encrypted_data = data.copy()
        key, key_id = self.kms.get_active_key()

        for field_name, value in data.items():
            if field_name in self.policies:
                policy = self.policies[field_name]

                if policy.encryption_type == 'deterministic':
                    # 결정적 암호화 (같은 입력 -> 같은 출력)
                    encrypted_value = self._deterministic_encrypt(
                        value,
                        key,
                        field_name
                    )
                else:
                    # 무작위 암호화
                    encrypted_value = self._randomized_encrypt(value, key)

                encrypted_data[field_name] = {{
                    'ciphertext': encrypted_value,
                    'key_id': key_id,
                    'algorithm': 'AES-256-GCM',
                    'encrypted': True
                }}

                # 검색 가능한 경우 인덱스 생성
                if policy.searchable:
                    encrypted_data[f'{{field_name}}_search'] = \
                        self._create_searchable_hash(value)

        return encrypted_data

    def decrypt_fields(
        self,
        encrypted_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        \"\"\"선택적 필드 복호화\"\"\"

        decrypted_data = {{}}

        for field_name, value in encrypted_data.items():
            if isinstance(value, dict) and value.get('encrypted'):
                # 암호화된 필드
                key = self.kms.decrypt_data_encryption_key(value['key_id'])

                if field_name in self.policies:
                    policy = self.policies[field_name]

                    if policy.encryption_type == 'deterministic':
                        decrypted_value = self._deterministic_decrypt(
                            value['ciphertext'],
                            key,
                            field_name
                        )
                    else:
                        decrypted_value = self._randomized_decrypt(
                            value['ciphertext'],
                            key
                        )

                    decrypted_data[field_name] = decrypted_value
            else:
                # 암호화되지 않은 필드
                decrypted_data[field_name] = value

        return decrypted_data

    def _deterministic_encrypt(
        self,
        value: Any,
        key: bytes,
        field_name: str
    ) -> str:
        \"\"\"결정적 암호화 (검색 가능)\"\"\"

        # 필드명을 salt로 사용하여 같은 값은 항상 같은 결과
        iv = self._derive_iv_from_value(str(value), field_name)

        # JSON 직렬화
        serialized = json.dumps(value)

        # 암호화 (IV 고정)
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(serialized.encode()) + encryptor.finalize()

        return base64.b64encode(ciphertext + encryptor.tag).decode()

    def _create_searchable_hash(self, value: Any) -> str:
        \"\"\"검색 가능한 해시 생성\"\"\"

        # HMAC을 사용한 안전한 해시
        import hmac
        import hashlib

        search_key = os.environ.get('SEARCH_HASH_KEY', 'default-search-key')

        h = hmac.new(
            search_key.encode(),
            str(value).encode(),
            hashlib.sha256
        )

        return h.hexdigest()

# 데코레이터
def encrypt_fields(*field_names):
    \"\"\"필드 암호화 데코레이터\"\"\"
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 함수 실행
            result = await func(*args, **kwargs)

            # 결과에서 지정된 필드 암호화
            if isinstance(result, dict):
                encryption = get_field_encryption()  # DI
                result = encryption.encrypt_fields(result)

            return result

        return wrapper
    return decorator

# ORM 통합 예시 (SQLAlchemy)
from sqlalchemy import TypeDecorator, String

class EncryptedType(TypeDecorator):
    \"\"\"암호화된 필드 타입\"\"\"

    impl = String

    def __init__(self, encryption_type='randomized', *args, **kwargs):
        self.encryption_type = encryption_type
        super().__init__(*args, **kwargs)

    def process_bind_param(self, value, dialect):
        \"\"\"DB 저장 시 암호화\"\"\"
        if value is None:
            return value

        encryption = get_field_encryption()
        encrypted = encryption.encrypt_single_value(
            value,
            self.encryption_type
        )

        return json.dumps(encrypted)

    def process_result_value(self, value, dialect):
        \"\"\"DB 조회 시 복호화\"\"\"
        if value is None:
            return value

        encryption = get_field_encryption()
        encrypted_data = json.loads(value)

        return encryption.decrypt_single_value(encrypted_data)
"""
            }

    def _generate_policy_definitions(self, config: EncryptionConfig) -> str:
        """암호화 정책 정의 생성"""

        policies = []
        for field, classification in config.data_classification.items():
            if classification in ['sensitive', 'pii', 'confidential']:
                policy_type = 'deterministic' if classification == 'pii' else 'randomized'
                searchable = classification == 'pii'

                policies.append(f"""
        self.policies['{field}'] = FieldEncryptionPolicy(
            field_name='{field}',
            encryption_type='{policy_type}',
            data_type='string',
            searchable={searchable}
        )""")

        return '\n'.join(policies)
```

**검증 기준**:

- [ ] AES-256-GCM 구현
- [ ] 키 관리 시스템
- [ ] 필드 레벨 암호화
- [ ] 규정 준수 지원

#### SubTask 4.67.4: 보안 헤더 설정

**담당자**: 웹 보안 전문가  
**예상 소요시간**: 8시간

**작업 내용**:

```python
# backend/src/agents/implementations/generation/security_headers_generator.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class SecurityLevel(Enum):
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    PARANOID = "paranoid"

@dataclass
class SecurityHeaderConfig:
    level: SecurityLevel
    enable_hsts: bool
    enable_csp: bool
    csp_report_uri: Optional[str]
    allowed_origins: List[str]
    feature_policy: Dict[str, List[str]]
    custom_headers: Dict[str, str]

class SecurityHeadersGenerator:
    """보안 헤더 코드 생성기"""

    def __init__(self):
        self.header_definitions = self._load_header_definitions()
        self.csp_generator = CSPGenerator()
        self.cors_generator = CORSGenerator()

    async def generate_security_headers(
        self,
        config: SecurityHeaderConfig,
        language: str,
        framework: str
    ) -> GeneratedSecurityHeaders:
        """보안 헤더 설정 코드 생성"""

        # 1. 기본 보안 헤더
        basic_headers = self._generate_basic_headers(config)

        # 2. CSP (Content Security Policy)
        csp_config = None
        if config.enable_csp:
            csp_config = await self.csp_generator.generate(config)

        # 3. CORS 설정
        cors_config = await self.cors_generator.generate(
            config.allowed_origins,
            config.level
        )

        # 4. 프레임워크별 구현
        implementation = await self._generate_framework_implementation(
            basic_headers,
            csp_config,
            cors_config,
            config,
            language,
            framework
        )

        # 5. 테스트 코드
        tests = await self._generate_security_tests(config, language)

        return GeneratedSecurityHeaders(
            headers=basic_headers,
            csp=csp_config,
            cors=cors_config,
            implementation=implementation,
            tests=tests,
            documentation=self._generate_documentation(config)
        )

    def _generate_basic_headers(
        self,
        config: SecurityHeaderConfig
    ) -> Dict[str, str]:
        """기본 보안 헤더 생성"""

        headers = {}

        # 레벨별 헤더 설정
        if config.level in [SecurityLevel.BASIC, SecurityLevel.STANDARD, SecurityLevel.STRICT, SecurityLevel.PARANOID]:
            # 모든 레벨에 포함
            headers.update({
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block',
                'Referrer-Policy': 'strict-origin-when-cross-origin'
            })

        if config.level in [SecurityLevel.STANDARD, SecurityLevel.STRICT, SecurityLevel.PARANOID]:
            # Standard 이상
            headers.update({
                'Permissions-Policy': self._generate_permissions_policy(config),
                'X-Permitted-Cross-Domain-Policies': 'none'
            })

        if config.level in [SecurityLevel.STRICT, SecurityLevel.PARANOID]:
            # Strict 이상
            headers.update({
                'Cross-Origin-Embedder-Policy': 'require-corp',
                'Cross-Origin-Opener-Policy': 'same-origin',
                'Cross-Origin-Resource-Policy': 'same-origin'
            })

        if config.level == SecurityLevel.PARANOID:
            # Paranoid 레벨
            headers.update({
                'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0',
                'X-DNS-Prefetch-Control': 'off'
            })

        # HSTS
        if config.enable_hsts:
            max_age = 31536000 if config.level == SecurityLevel.PARANOID else 15768000
            headers['Strict-Transport-Security'] = f'max-age={max_age}; includeSubDomains; preload'

        # 커스텀 헤더 추가
        headers.update(config.custom_headers)

        return headers

    def _generate_permissions_policy(
        self,
        config: SecurityHeaderConfig
    ) -> str:
        """Permissions Policy 생성"""

        default_policies = {
            'accelerometer': ['self'],
            'camera': ['self'],
            'geolocation': ['self'],
            'gyroscope': ['self'],
            'magnetometer': ['self'],
            'microphone': ['self'],
            'payment': ['self'],
            'usb': ['self']
        }

        # 설정된 정책 병합
        policies = {**default_policies, **config.feature_policy}

        # 문자열로 변환
        policy_strings = []
        for feature, allowlist in policies.items():
            if not allowlist:
                policy_strings.append(f'{feature}=()')
            else:
                allowed = ' '.join(f'"{origin}"' if origin != 'self' else origin for origin in allowlist)
                policy_strings.append(f'{feature}=({allowed})')

        return ', '.join(policy_strings)

    async def _generate_framework_implementation(
        self,
        headers: Dict[str, str],
        csp: Optional[str],
        cors: Dict[str, Any],
        config: SecurityHeaderConfig,
        language: str,
        framework: str
    ) -> Dict[str, str]:
        """프레임워크별 구현 코드"""

        implementations = {}

        if framework == 'express' and language in ['javascript', 'typescript']:
            implementations['security_headers.ts'] = f"""
import helmet from 'helmet';
import cors from 'cors';
import {{ Request, Response, NextFunction }} from 'express';

// 보안 헤더 미들웨어
export const securityHeaders = () => {{
    const helmetConfig = {{
        contentSecurityPolicy: {f'''{{
            directives: {{
                {self._format_csp_directives(csp)}
            }},
            reportOnly: false
        }}''' if config.enable_csp else 'false'},
        hsts: {f'''{{
            maxAge: {31536000 if config.level == SecurityLevel.PARANOID else 15768000},
            includeSubDomains: true,
            preload: true
        }}''' if config.enable_hsts else 'false'},
        frameguard: {{ action: 'deny' }},
        xssFilter: true,
        noSniff: true,
        referrerPolicy: {{ policy: 'strict-origin-when-cross-origin' }},
        permittedCrossDomainPolicies: {{ permittedPolicies: 'none' }}
    }};

    return helmet(helmetConfig);
}};

// CORS 설정
export const corsOptions: cors.CorsOptions = {{
    origin: {json.dumps(config.allowed_origins)},
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
    exposedHeaders: ['X-Total-Count', 'X-Page-Number'],
    maxAge: 86400 // 24 hours
}};

// 추가 보안 헤더
export const additionalSecurityHeaders = (
    req: Request,
    res: Response,
    next: NextFunction
) => {{
    // 추가 헤더 설정
    {self._generate_additional_headers(headers, language)}

    next();
}};

// Nonce 생성 (CSP용)
export const generateNonce = (): string => {{
    return crypto.randomBytes(16).toString('base64');
}};

// CSP Nonce 미들웨어
export const cspNonce = (
    req: Request,
    res: Response,
    next: NextFunction
) => {{
    res.locals.nonce = generateNonce();
    next();
}};
"""

        elif framework == 'fastapi' and language == 'python':
            implementations['security_headers.py'] = f"""
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from typing import Callable
import hashlib
import secrets

class SecurityHeadersMiddleware:
    \"\"\"보안 헤더 미들웨어\"\"\"

    def __init__(
        self,
        app: FastAPI,
        security_config: Dict[str, Any]
    ):
        self.app = app
        self.config = security_config
        self.headers = {json.dumps(headers, indent=8)}

        # CSP 설정
        self.csp_enabled = {config.enable_csp}
        self.csp_policy = {f'"{csp}"' if csp else 'None'}

        # Nonce 생성기
        self.generate_nonce = lambda: secrets.token_urlsafe(16)

    async def __call__(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        # 요청 처리
        response = await call_next(request)

        # 기본 보안 헤더 추가
        for header, value in self.headers.items():
            response.headers[header] = value

        # CSP 헤더 추가 (nonce 포함)
        if self.csp_enabled and self.csp_policy:
            nonce = self.generate_nonce()
            csp_with_nonce = self.csp_policy.replace(
                "'nonce-{{nonce}}'",
                f"'nonce-{{nonce}}'"
            )
            response.headers['Content-Security-Policy'] = csp_with_nonce

            # Nonce를 컨텍스트에 저장 (템플릿용)
            request.state.csp_nonce = nonce

        return response

def configure_security_headers(app: FastAPI):
    \"\"\"보안 헤더 설정\"\"\"

    # CORS 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins={config.allowed_origins},
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
        expose_headers=["X-Total-Count", "X-Page-Number"],
        max_age=86400
    )

    # Trusted Host 미들웨어
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*.yourdomain.com", "yourdomain.com"]
    )

    # 보안 헤더 미들웨어
    security_config = {{
        'level': '{config.level.value}',
        'enable_hsts': {config.enable_hsts},
        'enable_csp': {config.enable_csp}
    }}

    app.add_middleware(SecurityHeadersMiddleware, security_config=security_config)

# 보안 헤더 검증
async def validate_security_headers(response: Response) -> Dict[str, Any]:
    \"\"\"응답 헤더 검증\"\"\"

    required_headers = {list(headers.keys())}
    missing_headers = []
    invalid_headers = {{}}

    for header in required_headers:
        if header not in response.headers:
            missing_headers.append(header)
        else:
            # 헤더 값 검증
            expected = {json.dumps(headers)}[header]
            actual = response.headers[header]

            if actual != expected:
                invalid_headers[header] = {{
                    'expected': expected,
                    'actual': actual
                }}

    return {{
        'valid': len(missing_headers) == 0 and len(invalid_headers) == 0,
        'missing_headers': missing_headers,
        'invalid_headers': invalid_headers
    }}
"""

        elif framework == 'spring' and language == 'java':
            implementations['SecurityHeadersConfig.java'] = f"""
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter;
import org.springframework.security.web.header.writers.StaticHeadersWriter;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.Arrays;
import java.util.List;

@Configuration
@EnableWebSecurity
public class SecurityHeadersConfig extends WebSecurityConfigurerAdapter {{

    @Override
    protected void configure(HttpSecurity http) throws Exception {{
        http
            // CORS 설정
            .cors().configurationSource(corsConfigurationSource())
            .and()

            // 보안 헤더 설정
            .headers()
                .frameOptions().deny()
                .xssProtection().and()
                .contentTypeOptions().and()

                // HSTS
                {f'''.httpStrictTransportSecurity()
                    .maxAgeInSeconds({31536000 if config.level == SecurityLevel.PARANOID else 15768000})
                    .includeSubDomains(true)
                    .preload(true)
                .and()''' if config.enable_hsts else ''}

                // CSP
                {f'''.contentSecurityPolicy("{csp}")
                    .reportOnly(false)
                .and()''' if config.enable_csp else ''}

                // 추가 헤더
                {self._generate_spring_headers(headers)}

            .and()

            // 기타 보안 설정
            .requiresChannel()
                .anyRequest().requiresSecure(); // HTTPS 강제
    }}

    private CorsConfigurationSource corsConfigurationSource() {{
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOrigins(Arrays.asList({', '.join(f'"{origin}"' for origin in config.allowed_origins)}));
        configuration.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        configuration.setAllowedHeaders(Arrays.asList("Content-Type", "Authorization", "X-Requested-With"));
        configuration.setExposedHeaders(Arrays.asList("X-Total-Count", "X-Page-Number"));
        configuration.setAllowCredentials(true);
        configuration.setMaxAge(86400L);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);

        return source;
    }}
}}
"""

        return implementations

    def _generate_additional_headers(
        self,
        headers: Dict[str, str],
        language: str
    ) -> str:
        """추가 헤더 설정 코드"""

        if language in ['javascript', 'typescript']:
            header_lines = []
            for header, value in headers.items():
                if header not in ['Content-Security-Policy', 'Strict-Transport-Security']:
                    header_lines.append(f"    res.setHeader('{header}', '{value}');")
            return '\n'.join(header_lines)

        return ''

    def _generate_spring_headers(self, headers: Dict[str, str]) -> str:
        """Spring Security 추가 헤더"""

        header_lines = []
        for header, value in headers.items():
            if header not in ['X-Frame-Options', 'X-Content-Type-Options', 'X-XSS-Protection']:
                header_lines.append(
                    f'.addHeaderWriter(new StaticHeadersWriter("{header}", "{value}"))'
                )

        return '\n                '.join(header_lines)

class CSPGenerator:
    """Content Security Policy 생성기"""

    async def generate(self, config: SecurityHeaderConfig) -> str:
        """CSP 정책 생성"""

        directives = {}

        # 레벨별 기본 정책
        if config.level == SecurityLevel.BASIC:
            directives = {
                'default-src': ["'self'"],
                'script-src': ["'self'", "'unsafe-inline'"],
                'style-src': ["'self'", "'unsafe-inline'"],
                'img-src': ["'self'", 'data:', 'https:'],
                'font-src': ["'self'"],
                'connect-src': ["'self'"]
            }
        elif config.level == SecurityLevel.STANDARD:
            directives = {
                'default-src': ["'none'"],
                'script-src': ["'self'"],
                'style-src': ["'self'"],
                'img-src': ["'self'", 'data:'],
                'font-src': ["'self'"],
                'connect-src': ["'self'"],
                'frame-src': ["'none'"],
                'object-src': ["'none'"],
                'base-uri': ["'self'"],
                'form-action': ["'self'"]
            }
        elif config.level in [SecurityLevel.STRICT, SecurityLevel.PARANOID]:
            directives = {
                'default-src': ["'none'"],
                'script-src': ["'self'", "'nonce-{nonce}'"],
                'style-src': ["'self'", "'nonce-{nonce}'"],
                'img-src': ["'self'"],
                'font-src': ["'self'"],
                'connect-src': ["'self'"],
                'frame-src': ["'none'"],
                'object-src': ["'none'"],
                'base-uri': ["'none'"],
                'form-action': ["'self'"],
                'frame-ancestors': ["'none'"],
                'upgrade-insecure-requests': []
            }

        # Report URI 추가
        if config.csp_report_uri:
            directives['report-uri'] = [config.csp_report_uri]
            directives['report-to'] = ['csp-endpoint']

        # 정책 문자열 생성
        policy_parts = []
        for directive, sources in directives.items():
            if sources:
                policy_parts.append(f"{directive} {' '.join(sources)}")
            else:
                policy_parts.append(directive)

        return '; '.join(policy_parts)

# 보안 헤더 테스트 생성
class SecurityHeaderTestGenerator:
    """보안 헤더 테스트 코드 생성"""

    async def generate_tests(
        self,
        config: SecurityHeaderConfig,
        language: str
    ) -> str:
        """테스트 코드 생성"""

        if language in ['javascript', 'typescript']:
            return f"""
import {{ describe, it, expect }} from '@jest/globals';
import supertest from 'supertest';
import {{ app }} from '../app';

describe('Security Headers', () => {{
    const request = supertest(app);

    it('should set X-Content-Type-Options header', async () => {{
        const response = await request.get('/');
        expect(response.headers['x-content-type-options']).toBe('nosniff');
    }});

    it('should set X-Frame-Options header', async () => {{
        const response = await request.get('/');
        expect(response.headers['x-frame-options']).toBe('DENY');
    }});

    it('should set X-XSS-Protection header', async () => {{
        const response = await request.get('/');
        expect(response.headers['x-xss-protection']).toBe('1; mode=block');
    }});

    {f'''it('should set Strict-Transport-Security header', async () => {{
        const response = await request.get('/');
        expect(response.headers['strict-transport-security']).toMatch(/max-age=\\d+/);
        expect(response.headers['strict-transport-security']).toContain('includeSubDomains');
    }});''' if config.enable_hsts else ''}

    {f'''it('should set Content-Security-Policy header', async () => {{
        const response = await request.get('/');
        expect(response.headers['content-security-policy']).toBeDefined();
        expect(response.headers['content-security-policy']).toContain("default-src");
    }});''' if config.enable_csp else ''}

    it('should handle CORS preflight requests', async () => {{
        const response = await request
            .options('/')
            .set('Origin', '{config.allowed_origins[0] if config.allowed_origins else "http://localhost:3000"}')
            .set('Access-Control-Request-Method', 'POST');

        expect(response.status).toBe(204);
        expect(response.headers['access-control-allow-origin']).toBeDefined();
    }});
}});
"""
        elif language == 'python':
            return f"""
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

class TestSecurityHeaders:
    \"\"\"보안 헤더 테스트\"\"\"

    def test_basic_security_headers(self):
        \"\"\"기본 보안 헤더 확인\"\"\"
        response = client.get("/")

        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"
        assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"

    {f'''def test_hsts_header(self):
        \"\"\"HSTS 헤더 확인\"\"\"
        response = client.get("/")

        hsts = response.headers.get("Strict-Transport-Security")
        assert hsts is not None
        assert "max-age=" in hsts
        assert "includeSubDomains" in hsts
        assert "preload" in hsts
    ''' if config.enable_hsts else ''}

    {f'''def test_csp_header(self):
        \"\"\"CSP 헤더 확인\"\"\"
        response = client.get("/")

        csp = response.headers.get("Content-Security-Policy")
        assert csp is not None
        assert "default-src" in csp
        assert "script-src" in csp
    ''' if config.enable_csp else ''}

    def test_cors_headers(self):
        \"\"\"CORS 헤더 확인\"\"\"
        response = client.options(
            "/",
            headers={{
                "Origin": "{config.allowed_origins[0] if config.allowed_origins else 'http://localhost:3000'}",
                "Access-Control-Request-Method": "POST"
            }}
        )

        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response.headers
"""
```

**검증 기준**:

- [ ] 주요 보안 헤더 포함
- [ ] CSP 정책 생성
- [ ] CORS 설정
- [ ] 프레임워크별 구현

---

### Task 4.68: 에러 처리 및 로깅

#### SubTask 4.68.1: 에러 핸들링 시스템

**담당자**: 시니어 백엔드 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/generation/error_handling_generator.py
from typing import Dict, List, Any, Optional, Type
from dataclasses import dataclass
from enum import Enum

class ErrorHandlingStrategy(Enum):
    GRACEFUL_DEGRADATION = "graceful_degradation"
    FAIL_FAST = "fail_fast"
    RETRY_WITH_BACKOFF = "retry_with_backoff"
    CIRCUIT_BREAKER = "circuit_breaker"
    BULKHEAD = "bulkhead"

@dataclass
class ErrorHandlingConfig:
    strategy: ErrorHandlingStrategy
    retry_attempts: int
    retry_delay: int  # milliseconds
    circuit_breaker_threshold: int
    circuit_breaker_timeout: int  # seconds
    error_reporting_enabled: bool
    custom_error_pages: bool
    error_monitoring_service: Optional[str]  # 'sentry', 'rollbar', 'custom'

class ErrorHandlingGenerator:
    """에러 핸들링 시스템 생성기"""

    def __init__(self):
        self.error_class_generator = ErrorClassGenerator()
        self.exception_handler_generator = ExceptionHandlerGenerator()
        self.retry_mechanism_generator = RetryMechanismGenerator()
        self.circuit_breaker_generator = CircuitBreakerGenerator()

    async def generate_error_handling_system(
        self,
        config: ErrorHandlingConfig,
        language: str,
        framework: Optional[str] = None
    ) -> GeneratedErrorHandling:
        """완전한 에러 핸들링 시스템 생성"""

        # 1. 커스텀 에러 클래스
        error_classes = await self.error_class_generator.generate(
            language,
            framework
        )

        # 2. 예외 핸들러
        exception_handlers = await self.exception_handler_generator.generate(
            config,
            language,
            framework
        )

        # 3. 재시도 메커니즘
        retry_mechanism = None
        if config.strategy == ErrorHandlingStrategy.RETRY_WITH_BACKOFF:
            retry_mechanism = await self.retry_mechanism_generator.generate(
                config,
                language
            )

        # 4. Circuit Breaker
        circuit_breaker = None
        if config.strategy == ErrorHandlingStrategy.CIRCUIT_BREAKER:
            circuit_breaker = await self.circuit_breaker_generator.generate(
                config,
                language
            )

        # 5. 에러 모니터링
        error_monitoring = await self._generate_error_monitoring(
            config,
            language
        )

        # 6. 에러 응답 포맷터
        error_formatter = await self._generate_error_formatter(
            language,
            framework
        )

        # 7. 테스트 코드
        tests = await self._generate_error_handling_tests(
            config,
            language
        )

        return GeneratedErrorHandling(
            error_classes=error_classes,
            exception_handlers=exception_handlers,
            retry_mechanism=retry_mechanism,
            circuit_breaker=circuit_breaker,
            error_monitoring=error_monitoring,
            error_formatter=error_formatter,
            tests=tests
        )

    async def _generate_error_monitoring(
        self,
        config: ErrorHandlingConfig,
        language: str
    ) -> Dict[str, str]:
        """에러 모니터링 코드 생성"""

        if not config.error_monitoring_service:
            return {}

        if config.error_monitoring_service == 'sentry' and language == 'python':
            return {
                'error_monitoring.py': f"""
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from typing import Dict, Any, Optional
import logging

class ErrorMonitoring:
    \"\"\"에러 모니터링 시스템\"\"\"

    def __init__(self, dsn: str, environment: str):
        self.dsn = dsn
        self.environment = environment
        self._initialize_sentry()

    def _initialize_sentry(self):
        \"\"\"Sentry 초기화\"\"\"

        # 로깅 통합
        logging_integration = LoggingIntegration(
            level=logging.INFO,
            event_level=logging.ERROR
        )

        sentry_sdk.init(
            dsn=self.dsn,
            environment=self.environment,
            integrations=[
                logging_integration,
                SqlalchemyIntegration(),
            ],
            traces_sample_rate=0.1,
            profiles_sample_rate=0.1,
            attach_stacktrace=True,
            send_default_pii=False,
            before_send=self._before_send,
            before_send_transaction=self._before_send_transaction
        )

    def _before_send(
        self,
        event: Dict[str, Any],
        hint: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        \"\"\"이벤트 전송 전 처리\"\"\"

        # 민감한 데이터 제거
        if 'request' in event and 'data' in event['request']:
            event['request']['data'] = self._sanitize_data(
                event['request']['data']
            )

        # 특정 에러 필터링
        if 'exc_info' in hint:
            exc_type, exc_value, tb = hint['exc_info']

            # 404 에러는 보내지 않음
            if isinstance(exc_value, NotFoundError):
                return None

        return event

    def _sanitize_data(self, data: Any) -> Any:
        \"\"\"민감한 데이터 제거\"\"\"

        if isinstance(data, dict):
            sanitized = {{}}
            sensitive_keys = {{'password', 'token', 'secret', 'api_key', 'credit_card'}}

            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    sanitized[key] = '[REDACTED]'
                else:
                    sanitized[key] = self._sanitize_data(value)

            return sanitized
        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]
        else:
            return data

    def capture_exception(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None,
        user: Optional[Dict[str, Any]] = None
    ):
        \"\"\"예외 캡처\"\"\"

        with sentry_sdk.push_scope() as scope:
            # 컨텍스트 추가
            if context:
                for key, value in context.items():
                    scope.set_context(key, value)

            # 사용자 정보 추가
            if user:
                scope.set_user({{
                    'id': user.get('id'),
                    'email': user.get('email'),
                    'username': user.get('username')
                }})

            # 태그 추가
            scope.set_tag('handled', 'true')

            # 예외 캡처
            sentry_sdk.capture_exception(exception)

    def capture_message(
        self,
        message: str,
        level: str = 'info',
        context: Optional[Dict[str, Any]] = None
    ):
        \"\"\"메시지 캡처\"\"\"

        with sentry_sdk.push_scope() as scope:
            if context:
                for key, value in context.items():
                    scope.set_context(key, value)

            sentry_sdk.capture_message(message, level)

    def add_breadcrumb(
        self,
        message: str,
        category: str,
        level: str = 'info',
        data: Optional[Dict[str, Any]] = None
    ):
        \"\"\"브레드크럼 추가\"\"\"

        sentry_sdk.add_breadcrumb(
            message=message,
            category=category,
            level=level,
            data=data
        )
"""
            }

        return {}

class ErrorClassGenerator:
    """에러 클래스 생성기"""

    async def generate(
        self,
        language: str,
        framework: Optional[str]
    ) -> Dict[str, str]:
        """커스텀 에러 클래스 생성"""

        if language == 'python':
            return {
                'custom_errors.py': f"""
from typing import Optional, Dict, Any, List
from enum import Enum
import traceback

class ErrorCode(Enum):
    \"\"\"에러 코드 정의\"\"\"

    # 인증 관련 (1xxx)
    UNAUTHORIZED = 1001
    INVALID_TOKEN = 1002
    TOKEN_EXPIRED = 1003
    INSUFFICIENT_PERMISSIONS = 1004

    # 검증 관련 (2xxx)
    VALIDATION_ERROR = 2001
    INVALID_INPUT = 2002
    MISSING_REQUIRED_FIELD = 2003
    INVALID_FORMAT = 2004

    # 비즈니스 로직 (3xxx)
    BUSINESS_RULE_VIOLATION = 3001
    RESOURCE_NOT_FOUND = 3002
    DUPLICATE_RESOURCE = 3003
    OPERATION_NOT_ALLOWED = 3004

    # 시스템 에러 (4xxx)
    INTERNAL_SERVER_ERROR = 4001
    DATABASE_ERROR = 4002
    EXTERNAL_SERVICE_ERROR = 4003
    TIMEOUT_ERROR = 4004

    # 요청 제한 (5xxx)
    RATE_LIMIT_EXCEEDED = 5001
    QUOTA_EXCEEDED = 5002

class BaseCustomError(Exception):
    \"\"\"기본 커스텀 에러 클래스\"\"\"

    def __init__(
        self,
        message: str,
        code: ErrorCode,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        inner_exception: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {{}}
        self.inner_exception = inner_exception
        self.stack_trace = traceback.format_exc()

    def to_dict(self) -> Dict[str, Any]:
        \"\"\"에러를 딕셔너리로 변환\"\"\"

        error_dict = {{
            'error': {{
                'code': self.code.value,
                'message': self.message,
                'details': self.details
            }}
        }}

        # 개발 환경에서는 스택 트레이스 포함
        if self._is_development():
            error_dict['error']['stack_trace'] = self.stack_trace

        return error_dict

    def _is_development(self) -> bool:
        \"\"\"개발 환경 확인\"\"\"
        import os
        return os.getenv('ENVIRONMENT', 'production') == 'development'

# 구체적인 에러 클래스들
class ValidationError(BaseCustomError):
    \"\"\"검증 에러\"\"\"

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        constraints: Optional[Dict[str, Any]] = None
    ):
        details = {{
            'field': field,
            'value': value,
            'constraints': constraints
        }}

        super().__init__(
            message=message,
            code=ErrorCode.VALIDATION_ERROR,
            status_code=400,
            details=details
        )

class AuthenticationError(BaseCustomError):
    \"\"\"인증 에러\"\"\"

    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            code=ErrorCode.UNAUTHORIZED,
            status_code=401
        )

class AuthorizationError(BaseCustomError):
    \"\"\"인가 에러\"\"\"

    def __init__(
        self,
        message: str = "Insufficient permissions",
        required_permissions: Optional[List[str]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.INSUFFICIENT_PERMISSIONS,
            status_code=403,
            details={{'required_permissions': required_permissions}}
        )

class NotFoundError(BaseCustomError):
    \"\"\"리소스 없음 에러\"\"\"

    def __init__(
        self,
        resource_type: str,
        resource_id: Optional[str] = None
    ):
        message = f"{{resource_type}} not found"
        if resource_id:
            message += f": {{resource_id}}"

        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_NOT_FOUND,
            status_code=404,
            details={{
                'resource_type': resource_type,
                'resource_id': resource_id
            }}
        )

class BusinessLogicError(BaseCustomError):
    \"\"\"비즈니스 로직 에러\"\"\"

    def __init__(
        self,
        message: str,
        rule: str,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.BUSINESS_RULE_VIOLATION,
            status_code=422,
            details={{
                'rule': rule,
                'context': context
            }}
        )

class ExternalServiceError(BaseCustomError):
    \"\"\"외부 서비스 에러\"\"\"

    def __init__(
        self,
        service_name: str,
        operation: str,
        original_error: Optional[str] = None
    ):
        super().__init__(
            message=f"External service error: {{service_name}}",
            code=ErrorCode.EXTERNAL_SERVICE_ERROR,
            status_code=503,
            details={{
                'service': service_name,
                'operation': operation,
                'original_error': original_error
            }}
        )

class RateLimitError(BaseCustomError):
    \"\"\"요청 제한 에러\"\"\"

    def __init__(
        self,
        limit: int,
        window: str,
        retry_after: Optional[int] = None
    ):
        super().__init__(
            message=f"Rate limit exceeded: {{limit}} requests per {{window}}",
            code=ErrorCode.RATE_LIMIT_EXCEEDED,
            status_code=429,
            details={{
                'limit': limit,
                'window': window,
                'retry_after': retry_after
            }}
        )

# 에러 팩토리
class ErrorFactory:
    \"\"\"에러 생성 팩토리\"\"\"

    @staticmethod
    def create_validation_error(
        field: str,
        message: str,
        **kwargs
    ) -> ValidationError:
        \"\"\"검증 에러 생성\"\"\"
        return ValidationError(
            message=message,
            field=field,
            **kwargs
        )

    @staticmethod
    def create_from_exception(
        exception: Exception,
        default_message: str = "An error occurred"
    ) -> BaseCustomError:
        \"\"\"일반 예외로부터 커스텀 에러 생성\"\"\"

        # 이미 커스텀 에러인 경우
        if isinstance(exception, BaseCustomError):
            return exception

        # 기타 예외
        return BaseCustomError(
            message=str(exception) or default_message,
            code=ErrorCode.INTERNAL_SERVER_ERROR,
            status_code=500,
            inner_exception=exception
        )
"""
            }

        elif language in ['javascript', 'typescript']:
            return {
                'customErrors.ts': f"""
export enum ErrorCode {{
    // 인증 관련 (1xxx)
    UNAUTHORIZED = 1001,
    INVALID_TOKEN = 1002,
    TOKEN_EXPIRED = 1003,
    INSUFFICIENT_PERMISSIONS = 1004,

    // 검증 관련 (2xxx)
    VALIDATION_ERROR = 2001,
    INVALID_INPUT = 2002,
    MISSING_REQUIRED_FIELD = 2003,
    INVALID_FORMAT = 2004,

    // 비즈니스 로직 (3xxx)
    BUSINESS_RULE_VIOLATION = 3001,
    RESOURCE_NOT_FOUND = 3002,
    DUPLICATE_RESOURCE = 3003,
    OPERATION_NOT_ALLOWED = 3004,

    // 시스템 에러 (4xxx)
    INTERNAL_SERVER_ERROR = 4001,
    DATABASE_ERROR = 4002,
    EXTERNAL_SERVICE_ERROR = 4003,
    TIMEOUT_ERROR = 4004,

    // 요청 제한 (5xxx)
    RATE_LIMIT_EXCEEDED = 5001,
    QUOTA_EXCEEDED = 5002
}}

export interface ErrorDetails {{
    [key: string]: any;
}}

export class BaseCustomError extends Error {{
    public readonly code: ErrorCode;
    public readonly statusCode: number;
    public readonly details: ErrorDetails;
    public readonly timestamp: Date;
    public readonly stackTrace?: string;

    constructor(
        message: string,
        code: ErrorCode,
        statusCode: number = 500,
        details: ErrorDetails = {{}}
    ) {{
        super(message);
        this.name = this.constructor.name;
        this.code = code;
        this.statusCode = statusCode;
        this.details = details;
        this.timestamp = new Date();

        // 스택 트레이스 캡처
        if (Error.captureStackTrace) {{
            Error.captureStackTrace(this, this.constructor);
        }}

        this.stackTrace = this.stack;
    }}

    toJSON(): object {{
        const errorObject: any = {{
            error: {{
                code: this.code,
                message: this.message,
                details: this.details,
                timestamp: this.timestamp
            }}
        }};

        // 개발 환경에서는 스택 트레이스 포함
        if (process.env.NODE_ENV === 'development') {{
            errorObject.error.stackTrace = this.stackTrace;
        }}

        return errorObject;
    }}
}}

// 구체적인 에러 클래스들
export class ValidationError extends BaseCustomError {{
    constructor(
        message: string,
        field?: string,
        value?: any,
        constraints?: object
    ) {{
        super(
            message,
            ErrorCode.VALIDATION_ERROR,
            400,
            {{ field, value, constraints }}
        );
    }}
}}

export class AuthenticationError extends BaseCustomError {{
    constructor(message: string = 'Authentication required') {{
        super(message, ErrorCode.UNAUTHORIZED, 401);
    }}
}}

export class AuthorizationError extends BaseCustomError {{
    constructor(
        message: string = 'Insufficient permissions',
        requiredPermissions?: string[]
    ) {{
        super(
            message,
            ErrorCode.INSUFFICIENT_PERMISSIONS,
            403,
            {{ requiredPermissions }}
        );
    }}
}}

export class NotFoundError extends BaseCustomError {{
    constructor(resourceType: string, resourceId?: string) {{
        const message = resourceId
            ? `${{resourceType}} not found: ${{resourceId}}`
            : `${{resourceType}} not found`;

        super(
            message,
            ErrorCode.RESOURCE_NOT_FOUND,
            404,
            {{ resourceType, resourceId }}
        );
    }}
}}

export class BusinessLogicError extends BaseCustomError {{
    constructor(
        message: string,
        rule: string,
        context?: object
    ) {{
        super(
            message,
            ErrorCode.BUSINESS_RULE_VIOLATION,
            422,
            {{ rule, context }}
        );
    }}
}}

export class ExternalServiceError extends BaseCustomError {{
    constructor(
        serviceName: string,
        operation: string,
        originalError?: string
    ) {{
        super(
            `External service error: ${{serviceName}}`,
            ErrorCode.EXTERNAL_SERVICE_ERROR,
            503,
            {{ service: serviceName, operation, originalError }}
        );
    }}
}}

export class RateLimitError extends BaseCustomError {{
    constructor(
        limit: number,
        window: string,
        retryAfter?: number
    ) {{
        super(
            `Rate limit exceeded: ${{limit}} requests per ${{window}}`,
            ErrorCode.RATE_LIMIT_EXCEEDED,
            429,
            {{ limit, window, retryAfter }}
        );
    }}
}}

// 에러 타입 가드
export function isCustomError(error: any): error is BaseCustomError {{
    return error instanceof BaseCustomError;
}}

export function isValidationError(error: any): error is ValidationError {{
    return error instanceof ValidationError;
}}

export function isAuthError(error: any): error is AuthenticationError | AuthorizationError {{
    return error instanceof AuthenticationError || error instanceof AuthorizationError;
}}
"""
            }

        return {}

class ExceptionHandlerGenerator:
    """예외 핸들러 생성기"""

    async def generate(
        self,
        config: ErrorHandlingConfig,
        language: str,
        framework: Optional[str]
    ) -> Dict[str, str]:
        """예외 핸들러 생성"""

        if framework == 'fastapi' and language == 'python':
            return {
                'exception_handlers.py': f"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from typing import Union

logger = logging.getLogger(__name__)

def register_exception_handlers(app: FastAPI):
    \"\"\"예외 핸들러 등록\"\"\"

    @app.exception_handler(BaseCustomError)
    async def custom_error_handler(
        request: Request,
        exc: BaseCustomError
    ) -> JSONResponse:
        \"\"\"커스텀 에러 핸들러\"\"\"

        # 에러 로깅
        logger.error(
            f"Custom error: {{exc.code.name}} - {{exc.message}}",
            extra={{
                'error_code': exc.code.value,
                'status_code': exc.status_code,
                'details': exc.details,
                'url': str(request.url),
                'method': request.method
            }}
        )

        # 에러 모니터링 서비스로 전송
        if hasattr(app.state, 'error_monitoring'):
            app.state.error_monitoring.capture_exception(
                exc,
                context={{
                    'request': {{
                        'url': str(request.url),
                        'method': request.method,
                        'headers': dict(request.headers)
                    }}
                }}
            )

        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict()
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
    ) -> JSONResponse:
        \"\"\"검증 에러 핸들러\"\"\"

        # 에러 메시지 포맷팅
        errors = []
        for error in exc.errors():
            field = '.'.join(str(loc) for loc in error['loc'][1:])
            errors.append({{
                'field': field,
                'message': error['msg'],
                'type': error['type']
            }})

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={{
                'error': {{
                    'code': ErrorCode.VALIDATION_ERROR.value,
                    'message': 'Validation failed',
                    'details': {{'errors': errors}}
                }}
            }}
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException
    ) -> JSONResponse:
        \"\"\"HTTP 예외 핸들러\"\"\"

        # 404 에러 커스터마이징
        if exc.status_code == 404:
            return JSONResponse(
                status_code=404,
                content={{
                    'error': {{
                        'code': ErrorCode.RESOURCE_NOT_FOUND.value,
                        'message': 'The requested resource was not found',
                        'details': {{'path': str(request.url.path)}}
                    }}
                }}
            )

        # 기타 HTTP 에러
        return JSONResponse(
            status_code=exc.status_code,
            content={{
                'error': {{
                    'code': ErrorCode.INTERNAL_SERVER_ERROR.value,
                    'message': exc.detail or 'An error occurred',
                    'details': {{}}
                }}
            }}
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request,
        exc: Exception
    ) -> JSONResponse:
        \"\"\"일반 예외 핸들러\"\"\"

        # 심각한 에러 로깅
        logger.exception(
            "Unhandled exception",
            extra={{
                'url': str(request.url),
                'method': request.method,
                'exception_type': type(exc).__name__
            }}
        )

        # 에러 모니터링
        if hasattr(app.state, 'error_monitoring'):
            app.state.error_monitoring.capture_exception(exc)

        # 운영 환경에서는 상세 정보 숨김
        if os.getenv('ENVIRONMENT') == 'production':
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={{
                    'error': {{
                        'code': ErrorCode.INTERNAL_SERVER_ERROR.value,
                        'message': 'An internal server error occurred',
                        'details': {{}}
                    }}
                }}
            )
        else:
            # 개발 환경에서는 상세 정보 포함
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={{
                    'error': {{
                        'code': ErrorCode.INTERNAL_SERVER_ERROR.value,
                        'message': str(exc),
                        'details': {{
                            'type': type(exc).__name__,
                            'trace': traceback.format_exc()
                        }}
                    }}
                }}
            )

# 비동기 에러 핸들러
class AsyncErrorHandler:
    \"\"\"비동기 작업 에러 핸들러\"\"\"

    def __init__(self, error_monitoring=None):
        self.error_monitoring = error_monitoring

    async def handle_async_error(
        self,
        func,
        *args,
        **kwargs
    ):
        \"\"\"비동기 함수 에러 처리\"\"\"
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            # 에러 로깅
            logger.exception(f"Async error in {{func.__name__}}")

            # 모니터링
            if self.error_monitoring:
                self.error_monitoring.capture_exception(
                    e,
                    context={{
                        'function': func.__name__,
                        'args': str(args),
                        'kwargs': str(kwargs)
                    }}
                )

            # 에러 재발생 또는 기본값 반환
            if isinstance(e, BaseCustomError):
                raise
            else:
                raise BaseCustomError(
                    message=f"Async operation failed: {{str(e)}}",
                    code=ErrorCode.INTERNAL_SERVER_ERROR
                )
"""
            }

        elif framework == 'express' and language in ['javascript', 'typescript']:
            return {
                'errorHandlers.ts': f"""
import {{ Request, Response, NextFunction }} from 'express';
import {{ BaseCustomError, ErrorCode }} from './customErrors';
import logger from './logger';

// 에러 핸들링 미들웨어
export const errorHandler = (
    err: Error,
    req: Request,
    res: Response,
    next: NextFunction
): void => {{
    // 이미 응답이 전송된 경우
    if (res.headersSent) {{
        return next(err);
    }}

    // 커스텀 에러 처리
    if (err instanceof BaseCustomError) {{
        logger.error('Custom error', {{
            code: err.code,
            message: err.message,
            details: err.details,
            url: req.url,
            method: req.method
        }});

        res.status(err.statusCode).json(err.toJSON());
        return;
    }}

    // Validation 에러 처리 (express-validator)
    if (err.name === 'ValidationError') {{
        res.status(400).json({{
            error: {{
                code: ErrorCode.VALIDATION_ERROR,
                message: 'Validation failed',
                details: {{ errors: err.errors }}
            }}
        }});
        return;
    }}

    // MongoDB 에러 처리
    if (err.name === 'MongoError') {{
        if (err.code === 11000) {{
            res.status(409).json({{
                error: {{
                    code: ErrorCode.DUPLICATE_RESOURCE,
                    message: 'Resource already exists',
                    details: {{ }}
                }}
            }});
            return;
        }}
    }}

    // 일반 에러 처리
    logger.error('Unhandled error', {{
        error: err.message,
        stack: err.stack,
        url: req.url,
        method: req.method
    }});

    // 운영 환경에서는 상세 정보 숨김
    const isDevelopment = process.env.NODE_ENV === 'development';

    res.status(500).json({{
        error: {{
            code: ErrorCode.INTERNAL_SERVER_ERROR,
            message: isDevelopment ? err.message : 'Internal server error',
            details: isDevelopment ? {{ stack: err.stack }} : {{}}
        }}
    }});
}};

// 404 핸들러
export const notFoundHandler = (
    req: Request,
    res: Response,
    next: NextFunction
): void => {{
    res.status(404).json({{
        error: {{
            code: ErrorCode.RESOURCE_NOT_FOUND,
            message: 'Resource not found',
            details: {{ path: req.path }}
        }}
    }});
}};

// 비동기 에러 래퍼
export const asyncHandler = (
    fn: (req: Request, res: Response, next: NextFunction) => Promise<any>
) => {{
    return (req: Request, res: Response, next: NextFunction): void => {{
        Promise.resolve(fn(req, res, next)).catch(next);
    }};
}};

// 에러 로깅 미들웨어
export const errorLogger = (
    err: Error,
    req: Request,
    res: Response,
    next: NextFunction
): void => {{
    // 요청 정보 수집
    const requestInfo = {{
        url: req.url,
        method: req.method,
        headers: req.headers,
        body: req.body,
        params: req.params,
        query: req.query,
        ip: req.ip,
        userAgent: req.get('user-agent')
    }};

    // 에러 컨텍스트 로깅
    logger.error('Request failed', {{
        error: {{
            message: err.message,
            stack: err.stack,
            name: err.name
        }},
        request: requestInfo,
        timestamp: new Date().toISOString()
    }});

    next(err);
}};

// Express 앱에 에러 핸들러 등록
export const registerErrorHandlers = (app: any): void => {{
    // 404 핸들러 (라우트 끝에 등록)
    app.use(notFoundHandler);

    // 에러 로깅
    app.use(errorLogger);

    // 에러 핸들러 (마지막에 등록)
    app.use(errorHandler);
}};
"""
            }

        return {}

class RetryMechanismGenerator:
    """재시도 메커니즘 생성기"""

    async def generate(
        self,
        config: ErrorHandlingConfig,
        language: str
    ) -> Dict[str, str]:
        """재시도 메커니즘 코드 생성"""

        if language == 'python':
            return {
                'retry_mechanism.py': f"""
import asyncio
import functools
import random
from typing import TypeVar, Callable, Optional, Tuple, Type, Union, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

T = TypeVar('T')

class RetryConfig:
    \"\"\"재시도 설정\"\"\"

    def __init__(
        self,
        max_attempts: int = {config.retry_attempts},
        initial_delay: float = {config.retry_delay / 1000},  # seconds
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: Optional[List[Type[Exception]]] = None
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions or [Exception]

class RetryStrategy:
    \"\"\"재시도 전략 기본 클래스\"\"\"

    def calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        \"\"\"지연 시간 계산\"\"\"
        raise NotImplementedError

class ExponentialBackoff(RetryStrategy):
    \"\"\"지수 백오프 전략\"\"\"

    def calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        \"\"\"지수적으로 증가하는 지연 시간\"\"\"

        delay = config.initial_delay * (config.exponential_base ** (attempt - 1))

        # 최대 지연 시간 제한
        delay = min(delay, config.max_delay)

        # Jitter 추가 (충돌 회피)
        if config.jitter:
            delay = delay * (0.5 + random.random())

        return delay

class LinearBackoff(RetryStrategy):
    \"\"\"선형 백오프 전략\"\"\"

    def calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        \"\"\"선형적으로 증가하는 지연 시간\"\"\"

        delay = config.initial_delay * attempt
        delay = min(delay, config.max_delay)

        if config.jitter:
            delay = delay * (0.8 + random.random() * 0.4)

        return delay

def retry(
    config: Optional[RetryConfig] = None,
    strategy: Optional[RetryStrategy] = None,
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    \"\"\"재시도 데코레이터\"\"\"

    config = config or RetryConfig()
    strategy = strategy or ExponentialBackoff()

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(1, config.max_attempts + 1):
                try:
                    # 함수 실행
                    result = await func(*args, **kwargs)

                    # 성공 시 결과 반환
                    if attempt > 1:
                        logger.info(
                            f"{{func.__name__}} succeeded after {{attempt}} attempts"
                        )

                    return result

                except Exception as e:
                    last_exception = e

                    # 재시도 가능한 예외인지 확인
                    if not any(isinstance(e, exc_type) for exc_type in config.retryable_exceptions):
                        raise

                    # 마지막 시도였다면 예외 발생
                    if attempt == config.max_attempts:
                        logger.error(
                            f"{{func.__name__}} failed after {{attempt}} attempts",
                            exc_info=True
                        )
                        raise

                    # 지연 시간 계산
                    delay = strategy.calculate_delay(attempt, config)

                    # 재시도 콜백 실행
                    if on_retry:
                        on_retry(e, attempt)

                    logger.warning(
                        f"{{func.__name__}} failed (attempt {{attempt}}/{{config.max_attempts}}), "
                        f"retrying in {{delay:.2f}}s: {{str(e)}}"
                    )

                    # 지연
                    await asyncio.sleep(delay)

            # 이론적으로 도달하지 않는 코드
            raise last_exception

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(1, config.max_attempts + 1):
                try:
                    result = func(*args, **kwargs)

                    if attempt > 1:
                        logger.info(
                            f"{{func.__name__}} succeeded after {{attempt}} attempts"
                        )

                    return result

                except Exception as e:
                    last_exception = e

                    if not any(isinstance(e, exc_type) for exc_type in config.retryable_exceptions):
                        raise

                    if attempt == config.max_attempts:
                        logger.error(
                            f"{{func.__name__}} failed after {{attempt}} attempts",
                            exc_info=True
                        )
                        raise

                    delay = strategy.calculate_delay(attempt, config)

                    if on_retry:
                        on_retry(e, attempt)

                    logger.warning(
                        f"{{func.__name__}} failed (attempt {{attempt}}/{{config.max_attempts}}), "
                        f"retrying in {{delay:.2f}}s: {{str(e)}}"
                    )

                    import time
                    time.sleep(delay)

            raise last_exception

        # 비동기/동기 함수 구분
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator

# 조건부 재시도
class ConditionalRetry:
    \"\"\"조건부 재시도 로직\"\"\"

    def __init__(self, config: RetryConfig):
        self.config = config
        self.strategy = ExponentialBackoff()

    def should_retry(
        self,
        exception: Exception,
        attempt: int,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        \"\"\"재시도 여부 판단\"\"\"

        # 최대 시도 횟수 확인
        if attempt >= self.config.max_attempts:
            return False

        # HTTP 상태 코드 기반 판단
        if hasattr(exception, 'status_code'):
            # 5xx 에러는 재시도
            if 500 <= exception.status_code < 600:
                return True

            # 429 (Rate Limit)는 재시도
            if exception.status_code == 429:
                return True

            # 4xx 에러는 재시도하지 않음
            if 400 <= exception.status_code < 500:
                return False

        # 네트워크 관련 에러는 재시도
        network_errors = [
            'ConnectionError',
            'TimeoutError',
            'ConnectionResetError'
        ]

        if type(exception).__name__ in network_errors:
            return True

        # 기본: 설정된 예외 타입 확인
        return any(
            isinstance(exception, exc_type)
            for exc_type in self.config.retryable_exceptions
        )

# 사용 예시
@retry(
    config=RetryConfig(
        max_attempts=3,
        initial_delay=1.0,
        retryable_exceptions=[ConnectionError, TimeoutError]
    ),
    on_retry=lambda e, attempt: logger.info(f"Retry {{attempt}} due to: {{e}}")
)
async def fetch_data_with_retry(url: str):
    \"\"\"재시도가 적용된 데이터 페치\"\"\"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()
"""
            }

        elif language in ['javascript', 'typescript']:
            return {
                'retryMechanism.ts': f"""
interface RetryConfig {{
    maxAttempts: number;
    initialDelay: number; // milliseconds
    maxDelay: number;
    exponentialBase: number;
    jitter: boolean;
    retryableErrors?: Array<new (...args: any[]) => Error>;
}}

interface RetryStrategy {{
    calculateDelay(attempt: number, config: RetryConfig): number;
}}

class ExponentialBackoff implements RetryStrategy {{
    calculateDelay(attempt: number, config: RetryConfig): number {{
        let delay = config.initialDelay * Math.pow(config.exponentialBase, attempt - 1);

        // 최대 지연 시간 제한
        delay = Math.min(delay, config.maxDelay);

        // Jitter 추가
        if (config.jitter) {{
            delay = delay * (0.5 + Math.random());
        }}

        return delay;
    }}
}}

class LinearBackoff implements RetryStrategy {{
    calculateDelay(attempt: number, config: RetryConfig): number {{
        let delay = config.initialDelay * attempt;
        delay = Math.min(delay, config.maxDelay);

        if (config.jitter) {{
            delay = delay * (0.8 + Math.random() * 0.4);
        }}

        return delay;
    }}
}}

// 재시도 함수
export async function retry<T>(
    fn: () => Promise<T>,
    config: Partial<RetryConfig> = {{}},
    onRetry?: (error: Error, attempt: number) => void
): Promise<T> {{
    const defaultConfig: RetryConfig = {{
        maxAttempts: {config.retry_attempts},
        initialDelay: {config.retry_delay},
        maxDelay: 60000,
        exponentialBase: 2,
        jitter: true
    }};

    const finalConfig = {{ ...defaultConfig, ...config }};
    const strategy = new ExponentialBackoff();

    let lastError: Error | null = null;

    for (let attempt = 1; attempt <= finalConfig.maxAttempts; attempt++) {{
        try {{
            const result = await fn();

            if (attempt > 1) {{
                console.log(`Operation succeeded after ${{attempt}} attempts`);
            }}

            return result;
        }} catch (error) {{
            lastError = error as Error;

            // 재시도 가능한 에러인지 확인
            if (finalConfig.retryableErrors) {{
                const isRetryable = finalConfig.retryableErrors.some(
                    ErrorClass => error instanceof ErrorClass
                );

                if (!isRetryable) {{
                    throw error;
                }}
            }}

            // 마지막 시도였다면 에러 발생
            if (attempt === finalConfig.maxAttempts) {{
                console.error(`Operation failed after ${{attempt}} attempts`);
                throw error;
            }}

            // 지연 시간 계산
            const delay = strategy.calculateDelay(attempt, finalConfig);

            // 재시도 콜백
            if (onRetry) {{
                onRetry(error as Error, attempt);
            }}

            console.warn(
                `Operation failed (attempt ${{attempt}}/${{finalConfig.maxAttempts}}), ` +
                `retrying in ${{delay}}ms: ${{error}}`
            );

            // 지연
            await new Promise(resolve => setTimeout(resolve, delay));
        }}
    }}

    throw lastError;
}}

// 재시도 데코레이터
export function Retry(config: Partial<RetryConfig> = {{}}) {{
    return function (
        target: any,
        propertyKey: string,
        descriptor: PropertyDescriptor
    ) {{
        const originalMethod = descriptor.value;

        descriptor.value = async function (...args: any[]) {{
            return retry(
                () => originalMethod.apply(this, args),
                config
            );
        }};

        return descriptor;
    }};
}}

// 조건부 재시도
export class ConditionalRetry {{
    constructor(private config: RetryConfig) {{}}

    shouldRetry(error: Error, attempt: number): boolean {{
        // 최대 시도 횟수 확인
        if (attempt >= this.config.maxAttempts) {{
            return false;
        }}

        // HTTP 에러 처리
        if ('statusCode' in error) {{
            const statusCode = (error as any).statusCode;

            // 5xx 에러는 재시도
            if (statusCode >= 500 && statusCode < 600) {{
                return true;
            }}

            // 429 (Rate Limit)는 재시도
            if (statusCode === 429) {{
                return true;
            }}

            // 4xx 에러는 재시도하지 않음
            if (statusCode >= 400 && statusCode < 500) {{
                return false;
            }}
        }}

        // 네트워크 에러는 재시도
        const networkErrors = ['ECONNREFUSED', 'ETIMEDOUT', 'ENOTFOUND'];
        if ('code' in error && networkErrors.includes((error as any).code)) {{
            return true;
        }}

        return true; // 기본값
    }}
}}

// HTTP 클라이언트 재시도 래퍼
export class RetryableHttpClient {{
    private retryConfig: RetryConfig;

    constructor(config: Partial<RetryConfig> = {{}}) {{
        this.retryConfig = {{
            maxAttempts: 3,
            initialDelay: 1000,
            maxDelay: 10000,
            exponentialBase: 2,
            jitter: true,
            ...config
        }};
    }}

    async get<T>(url: string, options?: RequestInit): Promise<T> {{
        return retry(
            async () => {{
                const response = await fetch(url, options);

                if (!response.ok) {{
                    throw new HttpError(response.status, response.statusText);
                }}

                return response.json();
            }},
            this.retryConfig
        );
    }}

    async post<T>(url: string, data: any, options?: RequestInit): Promise<T> {{
        return retry(
            async () => {{
                const response = await fetch(url, {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        ...options?.headers
                    }},
                    body: JSON.stringify(data),
                    ...options
                }});

                if (!response.ok) {{
                    throw new HttpError(response.status, response.statusText);
                }}

                return response.json();
            }},
            this.retryConfig
        );
    }}
}}

class HttpError extends Error {{
    constructor(public statusCode: number, message: string) {{
        super(message);
        this.name = 'HttpError';
    }}
}}
"""
            }

        return {}

class CircuitBreakerGenerator:
    """Circuit Breaker 생성기"""

    async def generate(
        self,
        config: ErrorHandlingConfig,
        language: str
    ) -> Dict[str, str]:
        """Circuit Breaker 코드 생성"""

        if language == 'python':
            return {
                'circuit_breaker.py': f"""
import asyncio
from enum import Enum
from typing import TypeVar, Callable, Optional, Dict, Any
from datetime import datetime, timedelta
import functools
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')

class CircuitState(Enum):
    \"\"\"Circuit Breaker 상태\"\"\"
    CLOSED = "closed"  # 정상 작동
    OPEN = "open"      # 차단
    HALF_OPEN = "half_open"  # 테스트 중

class CircuitBreakerConfig:
    \"\"\"Circuit Breaker 설정\"\"\"

    def __init__(
        self,
        failure_threshold: int = {config.circuit_breaker_threshold},
        success_threshold: int = 2,
        timeout: int = {config.circuit_breaker_timeout},
        window_size: int = 60,  # seconds
        half_open_requests: int = 1
    ):
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        self.window_size = window_size
        self.half_open_requests = half_open_requests

class CircuitBreaker:
    \"\"\"Circuit Breaker 구현\"\"\"

    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.half_open_requests = 0
        self._lock = asyncio.Lock()

    async def call(
        self,
        func: Callable[..., T],
        *args,
        **kwargs
    ) -> T:
        \"\"\"Circuit Breaker를 통한 함수 호출\"\"\"

        async with self._lock:
            # 상태 확인 및 업데이트
            self._update_state()

            if self.state == CircuitState.OPEN:
                raise CircuitOpenError(
                    f"Circuit breaker '{{self.name}}' is OPEN"
                )

            if self.state == CircuitState.HALF_OPEN:
                if self.half_open_requests >= self.config.half_open_requests:
                    raise CircuitOpenError(
                        f"Circuit breaker '{{self.name}}' is HALF_OPEN with max requests reached"
                    )
                self.half_open_requests += 1

        try:
            # 함수 실행
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # 성공 처리
            await self._on_success()
            return result

        except Exception as e:
            # 실패 처리
            await self._on_failure()
            raise

    async def _on_success(self):
        \"\"\"성공 시 처리\"\"\"

        async with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1

                if self.success_count >= self.config.success_threshold:
                    # CLOSED 상태로 전환
                    logger.info(
                        f"Circuit breaker '{{self.name}}' transitioning from HALF_OPEN to CLOSED"
                    )
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    self.success_count = 0
                    self.half_open_requests = 0

            elif self.state == CircuitState.CLOSED:
                # 실패 카운트 리셋
                self.failure_count = 0

    async def _on_failure(self):
        \"\"\"실패 시 처리\"\"\"

        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            if self.state == CircuitState.HALF_OPEN:
                # 즉시 OPEN 상태로 전환
                logger.warning(
                    f"Circuit breaker '{{self.name}}' transitioning from HALF_OPEN to OPEN"
                )
                self.state = CircuitState.OPEN
                self.success_count = 0
                self.half_open_requests = 0

            elif self.state == CircuitState.CLOSED:
                if self.failure_count >= self.config.failure_threshold:
                    # OPEN 상태로 전환
                    logger.warning(
                        f"Circuit breaker '{{self.name}}' transitioning from CLOSED to OPEN "
                        f"after {{self.failure_count}} failures"
                    )
                    self.state = CircuitState.OPEN

    def _update_state(self):
        \"\"\"상태 업데이트\"\"\"

        if self.state == CircuitState.OPEN and self.last_failure_time:
            # 타임아웃 확인
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.config.timeout):
                logger.info(
                    f"Circuit breaker '{{self.name}}' transitioning from OPEN to HALF_OPEN"
                )
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                self.half_open_requests = 0

    def get_state(self) -> Dict[str, Any]:
        \"\"\"현재 상태 반환\"\"\"

        return {{
            'name': self.name,
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None
        }}

class CircuitOpenError(Exception):
    \"\"\"Circuit이 열려있을 때 발생하는 에러\"\"\"
    pass

# Circuit Breaker 데코레이터
def circuit_breaker(
    name: str,
    config: Optional[CircuitBreakerConfig] = None
):
    \"\"\"Circuit Breaker 데코레이터\"\"\"

    config = config or CircuitBreakerConfig()
    breaker = CircuitBreaker(name, config)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            return await breaker.call(func, *args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            # 동기 함수를 위한 래퍼
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(
                breaker.call(func, *args, **kwargs)
            )

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator

# Circuit Breaker 관리자
class CircuitBreakerManager:
    \"\"\"여러 Circuit Breaker 관리\"\"\"

    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {{}}

    def register(self, breaker: CircuitBreaker):
        \"\"\"Circuit Breaker 등록\"\"\"
        self.breakers[breaker.name] = breaker

    def get_breaker(self, name: str) -> Optional[CircuitBreaker]:
        \"\"\"Circuit Breaker 조회\"\"\"
        return self.breakers.get(name)

    def get_all_states(self) -> Dict[str, Dict[str, Any]]:
        \"\"\"모든 Circuit Breaker 상태 조회\"\"\"
        return {{
            name: breaker.get_state()
            for name, breaker in self.breakers.items()
        }}

    async def reset(self, name: str):
        \"\"\"Circuit Breaker 리셋\"\"\"

        breaker = self.breakers.get(name)
        if breaker:
            async with breaker._lock:
                breaker.state = CircuitState.CLOSED
                breaker.failure_count = 0
                breaker.success_count = 0
                breaker.last_failure_time = None
                breaker.half_open_requests = 0

                logger.info(f"Circuit breaker '{{name}}' has been reset")

# 사용 예시
@circuit_breaker(
    name="external_api",
    config=CircuitBreakerConfig(
        failure_threshold=5,
        timeout=60,
        success_threshold=3
    )
)
async def call_external_api(url: str):
    \"\"\"외부 API 호출 (Circuit Breaker 적용)\"\"\"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=5) as response:
            response.raise_for_status()
            return await response.json()
"""
            }

        return {}
```

**검증 기준**:

- [ ] 커스텀 에러 클래스 체계
- [ ] 프레임워크별 예외 핸들러
- [ ] 재시도 메커니즘 구현
- [ ] Circuit Breaker 패턴

#### SubTask 4.68.2: 구조화된 로깅

**담당자**: DevOps 엔지니어  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/generation/structured_logging_generator.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class LoggingConfig:
    log_level: LogLevel
    structured_format: bool
    log_destinations: List[str]  # 'console', 'file', 'elasticsearch', 'cloudwatch'
    rotation_policy: str  # 'size', 'time', 'both'
    retention_days: int
    sensitive_fields: List[str]
    correlation_id_enabled: bool
    performance_logging: bool

class StructuredLoggingGenerator:
    """구조화된 로깅 코드 생성기"""

    def __init__(self):
        self.logger_factory_generator = LoggerFactoryGenerator()
        self.formatter_generator = LogFormatterGenerator()
        self.handler_generator = LogHandlerGenerator()
        self.middleware_generator = LoggingMiddlewareGenerator()

    async def generate_logging_system(
        self,
        config: LoggingConfig,
        language: str,
        framework: Optional[str] = None
    ) -> GeneratedLoggingSystem:
        """완전한 로깅 시스템 생성"""

        # 1. 로거 팩토리
        logger_factory = await self.logger_factory_generator.generate(
            config,
            language
        )

        # 2. 로그 포맷터
        formatters = await self.formatter_generator.generate(
            config,
            language
        )

        # 3. 로그 핸들러
        handlers = await self.handler_generator.generate(
            config,
            language
        )

        # 4. 로깅 미들웨어
        middleware = await self.middleware_generator.generate(
            config,
            language,
            framework
        )

        # 5. 로그 유틸리티
        utilities = await self._generate_logging_utilities(
            config,
            language
        )

        # 6. 설정 파일
        configuration = await self._generate_logging_config(
            config,
            language
        )

        return GeneratedLoggingSystem(
            logger_factory=logger_factory,
            formatters=formatters,
            handlers=handlers,
            middleware=middleware,
            utilities=utilities,
            configuration=configuration
        )

    async def _generate_logging_utilities(
        self,
        config: LoggingConfig,
        language: str
    ) -> Dict[str, str]:
        """로깅 유틸리티 생성"""

        if language == 'python':
            return {
                'logging_utils.py': f"""
import functools
import time
import traceback
import json
from typing import Any, Dict, Optional, Callable
from contextvars import ContextVar
import uuid
import re

# 컨텍스트 변수
correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)
request_context_var: ContextVar[Optional[Dict[str, Any]]] = ContextVar('request_context', default=None)

class LogContext:
    \"\"\"로그 컨텍스트 관리\"\"\"

    @staticmethod
    def get_correlation_id() -> Optional[str]:
        \"\"\"현재 상관 ID 가져오기\"\"\"
        return correlation_id_var.get()

    @staticmethod
    def set_correlation_id(correlation_id: Optional[str] = None) -> str:
        \"\"\"상관 ID 설정\"\"\"
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())
        correlation_id_var.set(correlation_id)
        return correlation_id

    @staticmethod
    def get_request_context() -> Dict[str, Any]:
        \"\"\"요청 컨텍스트 가져오기\"\"\"
        return request_context_var.get() or {{}}

    @staticmethod
    def set_request_context(context: Dict[str, Any]):
        \"\"\"요청 컨텍스트 설정\"\"\"
        request_context_var.set(context)

    @staticmethod
    def clear():
        \"\"\"컨텍스트 초기화\"\"\"
        correlation_id_var.set(None)
        request_context_var.set(None)

class SensitiveDataFilter:
    \"\"\"민감한 데이터 필터링\"\"\"

    def __init__(self, sensitive_fields: List[str]):
        self.sensitive_fields = set(sensitive_fields)
        self.patterns = [
            (r'password["\']?\\s*[:=]\\s*["\']?([^"\'\\s]+)', 'password'),
            (r'token["\']?\\s*[:=]\\s*["\']?([^"\'\\s]+)', 'token'),
            (r'api_key["\']?\\s*[:=]\\s*["\']?([^"\'\\s]+)', 'api_key'),
            (r'\\b\\d{{4}}[\\s-]?\\d{{4}}[\\s-]?\\d{{4}}[\\s-]?\\d{{4}}\\b', 'credit_card'),
            (r'\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{{2,}}\\b', 'email')
        ]

    def filter(self, data: Any) -> Any:
        \"\"\"데이터 필터링\"\"\"

        if isinstance(data, dict):
            return self._filter_dict(data)
        elif isinstance(data, list):
            return [self.filter(item) for item in data]
        elif isinstance(data, str):
            return self._filter_string(data)
        else:
            return data

    def _filter_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"딕셔너리 필터링\"\"\"

        filtered = {{}}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in self.sensitive_fields):
                filtered[key] = '[REDACTED]'
            else:
                filtered[key] = self.filter(value)

        return filtered

    def _filter_string(self, text: str) -> str:
        \"\"\"문자열 필터링\"\"\"

        filtered_text = text
        for pattern, field_type in self.patterns:
            filtered_text = re.sub(
                pattern,
                f'[REDACTED_{field_type.upper()}]',
                filtered_text,
                flags=re.IGNORECASE
            )

        return filtered_text

def log_execution_time(logger=None):
    \"\"\"실행 시간 로깅 데코레이터\"\"\"

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time

                if logger:
                    logger.info(
                        f"Function executed",
                        extra={{
                            'function_name': func.__name__,
                            'execution_time': execution_time,
                            'status': 'success'
                        }}
                    )

                return result

            except Exception as e:
                execution_time = time.time() - start_time

                if logger:
                    logger.error(
                        f"Function failed",
                        extra={{
                            'function_name': func.__name__,
                            'execution_time': execution_time,
                            'status': 'error',
                            'error': str(e),
                            'traceback': traceback.format_exc()
                        }}
                    )

                raise

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time

                if logger:
                    logger.info(
                        f"Async function executed",
                        extra={{
                            'function_name': func.__name__,
                            'execution_time': execution_time,
                            'status': 'success'
                        }}
                    )

                return result

            except Exception as e:
                execution_time = time.time() - start_time

                if logger:
                    logger.error(
                        f"Async function failed",
                        extra={{
                            'function_name': func.__name__,
                            'execution_time': execution_time,
                            'status': 'error',
                            'error': str(e),
                            'traceback': traceback.format_exc()
                        }}
                    )

                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator

class LogAggregator:
    \"\"\"로그 집계\"\"\"

    def __init__(self):
        self.metrics = {{
            'request_count': 0,
            'error_count': 0,
            'warning_count': 0,
            'response_times': []
        }}

    def add_log_entry(self, log_entry: Dict[str, Any]):
        \"\"\"로그 엔트리 추가\"\"\"

        # 레벨별 카운트
        level = log_entry.get('level', '').lower()
        if level == 'error':
            self.metrics['error_count'] += 1
        elif level == 'warning':
            self.metrics['warning_count'] += 1

        # 응답 시간 추적
        if 'response_time' in log_entry:
            self.metrics['response_times'].append(log_entry['response_time'])

        # 요청 카운트
        if log_entry.get('event') == 'http_request':
            self.metrics['request_count'] += 1

    def get_summary(self) -> Dict[str, Any]:
        \"\"\"요약 통계\"\"\"

        response_times = self.metrics['response_times']

        return {{
            'total_requests': self.metrics['request_count'],
            'error_rate': self.metrics['error_count'] / max(self.metrics['request_count'], 1),
            'warning_count': self.metrics['warning_count'],
            'avg_response_time': sum(response_times) / len(response_times) if response_times else 0,
            'p95_response_time': self._calculate_percentile(response_times, 95),
            'p99_response_time': self._calculate_percentile(response_times, 99)
        }}

    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        \"\"\"백분위수 계산\"\"\"

        if not values:
            return 0

        sorted_values = sorted(values)
        index = int(len(sorted_values) * (percentile / 100))

        return sorted_values[min(index, len(sorted_values) - 1)]
"""
            }

        elif language in ['javascript', 'typescript']:
            return {
                'loggingUtils.ts': f"""
import {{ AsyncLocalStorage }} from 'async_hooks';
import {{ v4 as uuidv4 }} from 'uuid';

// 비동기 컨텍스트 스토리지
const asyncLocalStorage = new AsyncLocalStorage<Map<string, any>>();

export class LogContext {{
    static getCorrelationId(): string | undefined {{
        const store = asyncLocalStorage.getStore();
        return store?.get('correlationId');
    }}

    static setCorrelationId(correlationId?: string): string {{
        const store = asyncLocalStorage.getStore() || new Map();
        const id = correlationId || uuidv4();
        store.set('correlationId', id);
        return id;
    }}

    static getRequestContext(): Record<string, any> {{
        const store = asyncLocalStorage.getStore();
        return store?.get('requestContext') || {{}};
    }}

    static setRequestContext(context: Record<string, any>): void {{
        const store = asyncLocalStorage.getStore() || new Map();
        store.set('requestContext', context);
    }}

    static runWithContext<T>(
        fn: () => T,
        context?: Map<string, any>
    ): T {{
        return asyncLocalStorage.run(context || new Map(), fn);
    }}
}}

export class SensitiveDataFilter {{
    private sensitiveFields: Set<string>;
    private patterns: Array<{{ regex: RegExp; type: string }}>;

    constructor(sensitiveFields: string[]) {{
        this.sensitiveFields = new Set(sensitiveFields);
        this.patterns = [
            {{ regex: /password["']?\\s*[:=]\\s*["']?([^"'\\s]+)/gi, type: 'password' }},
            {{ regex: /token["']?\\s*[:=]\\s*["']?([^"'\\s]+)/gi, type: 'token' }},
            {{ regex: /api_key["']?\\s*[:=]\\s*["']?([^"'\\s]+)/gi, type: 'api_key' }},
            {{ regex: /\\b\\d{{4}}[\\s-]?\\d{{4}}[\\s-]?\\d{{4}}[\\s-]?\\d{{4}}\\b/g, type: 'credit_card' }},
            {{ regex: /\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{{2,}}\\b/g, type: 'email' }}
        ];
    }}

    filter(data: any): any {{
        if (typeof data === 'object' && data !== null) {{
            if (Array.isArray(data)) {{
                return data.map(item => this.filter(item));
            }}

            const filtered: Record<string, any> = {{}};
            for (const [key, value] of Object.entries(data)) {{
                if (this.isSensitiveField(key)) {{
                    filtered[key] = '[REDACTED]';
                }} else {{
                    filtered[key] = this.filter(value);
                }}
            }}
            return filtered;
        }}

        if (typeof data === 'string') {{
            return this.filterString(data);
        }}

        return data;
    }}

    private isSensitiveField(fieldName: string): boolean {{
        const lowerField = fieldName.toLowerCase();
        return Array.from(this.sensitiveFields).some(
            sensitive => lowerField.includes(sensitive.toLowerCase())
        );
    }}

    private filterString(text: string): string {{
        let filtered = text;

        for (const {{ regex, type }} of this.patterns) {{
            filtered = filtered.replace(regex, `[REDACTED_${{type.toUpperCase()}}]`);
        }}

        return filtered;
    }}
}}

// 실행 시간 측정 데코레이터
export function LogExecutionTime(logger?: any) {{
    return function (
        target: any,
        propertyKey: string,
        descriptor: PropertyDescriptor
    ) {{
        const originalMethod = descriptor.value;

        descriptor.value = async function (...args: any[]) {{
            const startTime = Date.now();
            const correlationId = LogContext.getCorrelationId();

            try {{
                const result = await originalMethod.apply(this, args);
                const executionTime = Date.now() - startTime;

                if (logger) {{
                    logger.info('Method executed', {{
                        method: propertyKey,
                        executionTime,
                        correlationId,
                        status: 'success'
                    }});
                }}

                return result;
            }} catch (error) {{
                const executionTime = Date.now() - startTime;

                if (logger) {{
                    logger.error('Method failed', {{
                        method: propertyKey,
                        executionTime,
                        correlationId,
                        status: 'error',
                        error: error.message,
                        stack: error.stack
                    }});
                }}

                throw error;
            }}
        }};

        return descriptor;
    }};
}}

export class LogAggregator {{
    private metrics = {{
        requestCount: 0,
        errorCount: 0,
        warningCount: 0,
        responseTimes: [] as number[]
    }};

    addLogEntry(logEntry: Record<string, any>): void {{
        const level = (logEntry.level || '').toLowerCase();

        if (level === 'error') {{
            this.metrics.errorCount++;
        }} else if (level === 'warning') {{
            this.metrics.warningCount++;
        }}

        if (logEntry.responseTime) {{
            this.metrics.responseTimes.push(logEntry.responseTime);
        }}

        if (logEntry.event === 'http_request') {{
            this.metrics.requestCount++;
        }}
    }}

    getSummary(): Record<string, any> {{
        const responseTimes = this.metrics.responseTimes;

        return {{
            totalRequests: this.metrics.requestCount,
            errorRate: this.metrics.requestCount > 0
                ? this.metrics.errorCount / this.metrics.requestCount
                : 0,
            warningCount: this.metrics.warningCount,
            avgResponseTime: responseTimes.length > 0
                ? responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length
                : 0,
            p95ResponseTime: this.calculatePercentile(responseTimes, 95),
            p99ResponseTime: this.calculatePercentile(responseTimes, 99)
        }};
    }}

    private calculatePercentile(values: number[], percentile: number): number {{
        if (values.length === 0) return 0;

        const sorted = [...values].sort((a, b) => a - b);
        const index = Math.floor(sorted.length * (percentile / 100));

        return sorted[Math.min(index, sorted.length - 1)];
    }}
}}
"""
            }

        return {}

class LoggerFactoryGenerator:
    """로거 팩토리 생성기"""

    async def generate(
        self,
        config: LoggingConfig,
        language: str
    ) -> Dict[str, str]:
        """로거 팩토리 코드 생성"""

        if language == 'python':
            return {
                'logger_factory.py': f"""
import logging
import logging.config
import json
import sys
from typing import Optional, Dict, Any
import structlog

class LoggerFactory:
    \"\"\"로거 팩토리\"\"\"

    _instance = None
    _loggers: Dict[str, logging.Logger] = {{}}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        \"\"\"로거 초기화\"\"\"

        # structlog 설정
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                self._add_context_processor,
                self._filter_sensitive_data,
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        # Python logging 설정
        logging_config = {{
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {{
                'json': {{
                    'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                    'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
                }},
                'standard': {{
                    'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
                }}
            }},
            'handlers': {{
                'console': {{
                    'class': 'logging.StreamHandler',
                    'level': '{config.log_level.value.upper()}',
                    'formatter': 'json' if {config.structured_format} else 'standard',
                    'stream': sys.stdout
                }},
                {'file': {{
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': '{config.log_level.value.upper()}',
                    'formatter': 'json',
                    'filename': 'logs/app.log',
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 5
                }},' if 'file' in config.log_destinations else ''}
            }},
            'root': {{
                'level': '{config.log_level.value.upper()}',
                'handlers': {config.log_destinations}
            }}
        }}

        logging.config.dictConfig(logging_config)

    def get_logger(self, name: str) -> structlog.BoundLogger:
        \"\"\"로거 인스턴스 가져오기\"\"\"

        if name not in self._loggers:
            self._loggers[name] = structlog.get_logger(name)

        return self._loggers[name]

    def _add_context_processor(self, logger, method_name, event_dict):
        \"\"\"컨텍스트 정보 추가\"\"\"

        # 상관 ID 추가
        correlation_id = LogContext.get_correlation_id()
        if correlation_id:
            event_dict['correlation_id'] = correlation_id

        # 요청 컨텍스트 추가
        request_context = LogContext.get_request_context()
        if request_context:
            event_dict.update(request_context)

        # 환경 정보
        event_dict['environment'] = os.getenv('ENVIRONMENT', 'development')
        event_dict['service'] = os.getenv('SERVICE_NAME', 'unknown')

        return event_dict

    def _filter_sensitive_data(self, logger, method_name, event_dict):
        \"\"\"민감한 데이터 필터링\"\"\"

        sensitive_filter = SensitiveDataFilter({config.sensitive_fields})

        # 메시지 필터링
        if 'msg' in event_dict:
            event_dict['msg'] = sensitive_filter.filter(event_dict['msg'])

        # 추가 데이터 필터링
        for key, value in list(event_dict.items()):
            if key not in ['timestamp', 'logger', 'level']:
                event_dict[key] = sensitive_filter.filter(value)

        return event_dict

# 싱글톤 인스턴스
logger_factory = LoggerFactory()

def get_logger(name: str) -> structlog.BoundLogger:
    \"\"\"로거 가져오기 헬퍼 함수\"\"\"
    return logger_factory.get_logger(name)

# 성능 로깅
class PerformanceLogger:
    \"\"\"성능 측정 로거\"\"\"

    def __init__(self, logger: structlog.BoundLogger):
        self.logger = logger

    def log_database_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]],
        execution_time: float,
        rows_affected: int
    ):
        \"\"\"데이터베이스 쿼리 로깅\"\"\"

        self.logger.info(
            "database_query",
            query=query,
            params=params,
            execution_time=execution_time,
            rows_affected=rows_affected,
            performance_category="database"
        )

    def log_http_request(
        self,
        method: str,
        url: str,
        status_code: int,
        response_time: float,
        request_size: int,
        response_size: int
    ):
        \"\"\"HTTP 요청 로깅\"\"\"

        self.logger.info(
            "http_request",
            method=method,
            url=url,
            status_code=status_code,
            response_time=response_time,
            request_size=request_size,
            response_size=response_size,
            performance_category="http"
        )

    def log_cache_operation(
        self,
        operation: str,
        key: str,
        hit: bool,
        execution_time: float
    ):
        \"\"\"캐시 작업 로깅\"\"\"

        self.logger.info(
            "cache_operation",
            operation=operation,
            key=key,
            cache_hit=hit,
            execution_time=execution_time,
            performance_category="cache"
        )
"""
            }

        elif language in ['javascript', 'typescript']:
            return {
                'loggerFactory.ts': f"""
import winston from 'winston';
import {{ LogContext, SensitiveDataFilter }} from './loggingUtils';

interface LoggerConfig {{
    level: string;
    format: winston.Logform.Format;
    transports: winston.transport[];
}}

export class LoggerFactory {{
    private static instance: LoggerFactory;
    private loggers: Map<string, winston.Logger> = new Map();
    private sensitiveFilter: SensitiveDataFilter;

    private constructor() {{
        this.sensitiveFilter = new SensitiveDataFilter({json.dumps(config.sensitive_fields)});
        this.initialize();
    }}

    static getInstance(): LoggerFactory {{
        if (!LoggerFactory.instance) {{
            LoggerFactory.instance = new LoggerFactory();
        }}
        return LoggerFactory.instance;
    }}

    private initialize(): void {{
        // 커스텀 포맷
        const customFormat = winston.format.combine(
            winston.format.timestamp({{ format: 'YYYY-MM-DD HH:mm:ss' }}),
            winston.format.errors({{ stack: true }}),
            winston.format.printf((info) => {{
                // 컨텍스트 추가
                const correlationId = LogContext.getCorrelationId();
                const requestContext = LogContext.getRequestContext();

                const logEntry = {{
                    timestamp: info.timestamp,
                    level: info.level,
                    message: info.message,
                    service: process.env.SERVICE_NAME || 'unknown',
                    environment: process.env.NODE_ENV || 'development',
                    correlationId,
                    ...requestContext,
                    ...info
                }};

                // 민감한 데이터 필터링
                const filtered = this.sensitiveFilter.filter(logEntry);

                return JSON.stringify(filtered);
            }})
        );

        // 기본 설정
        winston.configure({{
            level: '{config.log_level.value}',
            format: customFormat,
            transports: this.createTransports()
        }});
    }}

    private createTransports(): winston.transport[] {{
        const transports: winston.transport[] = [];

        // 콘솔 출력
        if ({json.dumps('console' in config.log_destinations)}) {{
            transports.push(new winston.transports.Console({{
                format: {f'winston.format.json()' if config.structured_format else 'winston.format.simple()'}
            }}));
        }}

        // 파일 출력
        if ({json.dumps('file' in config.log_destinations)}) {{
            transports.push(new winston.transports.File({{
                filename: 'logs/error.log',
                level: 'error',
                maxsize: 10485760, // 10MB
                maxFiles: 5,
                tailable: true
            }}));

            transports.push(new winston.transports.File({{
                filename: 'logs/combined.log',
                maxsize: 10485760,
                maxFiles: 5,
                tailable: true
            }}));
        }}

        return transports;
    }}

    getLogger(name: string): winston.Logger {{
        if (!this.loggers.has(name)) {{
            const logger = winston.createLogger({{
                defaultMeta: {{ component: name }},
                level: '{config.log_level.value}',
                format: winston.format.combine(
                    winston.format.label({{ label: name }}),
                    winston.format.timestamp(),
                    winston.format.json()
                ),
                transports: this.createTransports()
            }});

            this.loggers.set(name, logger);
        }}

        return this.loggers.get(name)!;
    }}
}}

// 싱글톤 인스턴스
export const loggerFactory = LoggerFactory.getInstance();

export function getLogger(name: string): winston.Logger {{
    return loggerFactory.getLogger(name);
}}

// 성능 로거
export class PerformanceLogger {{
    constructor(private logger: winston.Logger) {{}}

    logDatabaseQuery(
        query: string,
        params: any,
        executionTime: number,
        rowsAffected: number
    ): void {{
        this.logger.info('database_query', {{
            query,
            params,
            executionTime,
            rowsAffected,
            performanceCategory: 'database'
        }});
    }}

    logHttpRequest(
        method: string,
        url: string,
        statusCode: number,
        responseTime: number,
        requestSize: number,
        responseSize: number
    ): void {{
        this.logger.info('http_request', {{
            method,
            url,
            statusCode,
            responseTime,
            requestSize,
            responseSize,
            performanceCategory: 'http'
        }});
    }}

    logCacheOperation(
        operation: string,
        key: string,
        hit: boolean,
        executionTime: number
    ): void {{
        this.logger.info('cache_operation', {{
            operation,
            key,
            cacheHit: hit,
            executionTime,
            performanceCategory: 'cache'
        }});
    }}
}}
"""
            }

        return {}

class LoggingMiddlewareGenerator:
    """로깅 미들웨어 생성기"""

    async def generate(
        self,
        config: LoggingConfig,
        language: str,
        framework: Optional[str]
    ) -> Dict[str, str]:
        """로깅 미들웨어 생성"""

        if framework == 'express' and language in ['javascript', 'typescript']:
            return {
                'loggingMiddleware.ts': f"""
import {{ Request, Response, NextFunction }} from 'express';
import {{ getLogger }} from './loggerFactory';
import {{ LogContext }} from './loggingUtils';
import onFinished from 'on-finished';

const logger = getLogger('http');

export interface RequestLog {{
    method: string;
    url: string;
    headers: Record<string, any>;
    query: Record<string, any>;
    body: any;
    ip: string;
    userAgent: string;
}}

export interface ResponseLog {{
    statusCode: number;
    responseTime: number;
    contentLength: number;
}}

export const requestLoggingMiddleware = (
    req: Request,
    res: Response,
    next: NextFunction
): void => {{
    const startTime = Date.now();

    // 상관 ID 설정
    const correlationId = req.headers['x-correlation-id'] as string ||
                         LogContext.setCorrelationId();

    // 요청 컨텍스트 설정
    LogContext.setRequestContext({{
        method: req.method,
        path: req.path,
        ip: req.ip,
        userAgent: req.get('user-agent')
    }});

    // 요청 로깅
    const requestLog: RequestLog = {{
        method: req.method,
        url: req.originalUrl,
        headers: req.headers,
        query: req.query,
        body: req.body,
        ip: req.ip,
        userAgent: req.get('user-agent') || ''
    }};

    logger.info('Incoming request', {{
        event: 'http_request_start',
        request: requestLog,
        correlationId
    }});

    // 응답 완료 시 로깅
    onFinished(res, (err, res) => {{
        const responseTime = Date.now() - startTime;

        const responseLog: ResponseLog = {{
            statusCode: res.statusCode,
            responseTime,
            contentLength: parseInt(res.get('content-length') || '0', 10)
        }};

        const logLevel = res.statusCode >= 500 ? 'error' :
                        res.statusCode >= 400 ? 'warn' : 'info';

        logger.log(logLevel, 'Request completed', {{
            event: 'http_request_end',
            request: requestLog,
            response: responseLog,
            correlationId,
            error: err ? {{
                message: err.message,
                stack: err.stack
            }} : undefined
        }});
    }});

    // 상관 ID를 응답 헤더에 추가
    res.setHeader('X-Correlation-Id', correlationId);

    // 컨텍스트와 함께 다음 미들웨어 실행
    LogContext.runWithContext(next, new Map([
        ['correlationId', correlationId]
    ]));
}};

export const errorLoggingMiddleware = (
    err: Error,
    req: Request,
    res: Response,
    next: NextFunction
): void => {{
    const correlationId = LogContext.getCorrelationId();

    logger.error('Unhandled error in request', {{
        event: 'http_request_error',
        error: {{
            message: err.message,
            stack: err.stack,
            name: err.name
        }},
        request: {{
            method: req.method,
            url: req.originalUrl,
            headers: req.headers,
            body: req.body
        }},
        correlationId
    }});

    next(err);
}};

// 성능 모니터링 미들웨어
export const performanceLoggingMiddleware = (
    req: Request,
    res: Response,
    next: NextFunction
): void => {{
    const startTime = process.hrtime.bigint();
    const startMemory = process.memoryUsage();

    onFinished(res, () => {{
        const endTime = process.hrtime.bigint();
        const endMemory = process.memoryUsage();

        const responseTime = Number(endTime - startTime) / 1e6; // 나노초를 밀리초로

        if ({config.performance_logging}) {{
            logger.info('Request performance metrics', {{
                event: 'performance_metrics',
                path: req.path,
                method: req.method,
                responseTime,
                memoryDelta: {{
                    heapUsed: endMemory.heapUsed - startMemory.heapUsed,
                    external: endMemory.external - startMemory.external
                }},
                correlationId: LogContext.getCorrelationId()
            }});
        }}
    }});

    next();
}};
"""
            }

        elif framework == 'fastapi' and language == 'python':
            return {
                'logging_middleware.py': f"""
import time
import uuid
from typing import Callable
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import json

logger = get_logger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    \"\"\"로깅 미들웨어\"\"\"

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 상관 ID 설정
        correlation_id = request.headers.get('x-correlation-id', str(uuid.uuid4()))
        LogContext.set_correlation_id(correlation_id)

        # 요청 컨텍스트 설정
        request_context = {{
            'method': request.method,
            'path': request.url.path,
            'client_host': request.client.host if request.client else None,
            'user_agent': request.headers.get('user-agent')
        }}
        LogContext.set_request_context(request_context)

        # 시작 시간
        start_time = time.time()

        # 요청 로깅
        request_body = None
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                request_body = await request.json()
            except:
                request_body = await request.body()

        logger.info(
            "incoming_request",
            extra={{
                'event': 'http_request_start',
                'request': {{
                    'method': request.method,
                    'url': str(request.url),
                    'headers': dict(request.headers),
                    'query_params': dict(request.query_params),
                    'body': request_body
                }}
            }}
        )

        # 요청 처리
        response = await call_next(request)

        # 응답 시간 계산
        response_time = (time.time() - start_time) * 1000  # ms

        # 응답 로깅
        log_level = 'error' if response.status_code >= 500 else \
                   'warning' if response.status_code >= 400 else 'info'

        getattr(logger, log_level)(
            "request_completed",
            extra={{
                'event': 'http_request_end',
                'response': {{
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'headers': dict(response.headers)
                }}
            }}
        )

        # 응답 헤더에 상관 ID 추가
        response.headers['X-Correlation-Id'] = correlation_id

        # 컨텍스트 정리
        LogContext.clear()

        return response

class PerformanceLoggingMiddleware:
    \"\"\"성능 로깅 미들웨어\"\"\"

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            await self.app(scope, receive, send)
            return

        start_time = time.perf_counter()
        start_memory = self._get_memory_usage()

        async def send_wrapper(message):
            if message['type'] == 'http.response.start':
                # 응답 시작 시점에서 성능 메트릭 로깅
                end_time = time.perf_counter()
                end_memory = self._get_memory_usage()

                response_time = (end_time - start_time) * 1000  # ms
                memory_delta = end_memory - start_memory

                if {config.performance_logging}:
                    logger.info(
                        "performance_metrics",
                        extra={{
                            'event': 'performance_metrics',
                            'path': scope['path'],
                            'method': scope['method'],
                            'response_time': response_time,
                            'memory_delta': memory_delta,
                            'correlation_id': LogContext.get_correlation_id()
                        }}
                    )

            await send(message)

        await self.app(scope, receive, send_wrapper)

    def _get_memory_usage(self) -> int:
        \"\"\"현재 메모리 사용량 (bytes)\"\"\"
        import psutil
        import os

        process = psutil.Process(os.getpid())
        return process.memory_info().rss

def configure_logging_middleware(app: FastAPI):
    \"\"\"로깅 미들웨어 설정\"\"\"

    # 로깅 미들웨어 추가
    app.add_middleware(LoggingMiddleware)

    # 성능 로깅 미들웨어 추가
    if {config.performance_logging}:
        app.add_middleware(PerformanceLoggingMiddleware)

    # 요청/응답 로깅
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        # SQL 쿼리 로깅을 위한 핸들러 설정
        if hasattr(app.state, 'db'):
            # SQLAlchemy 이벤트 리스너
            from sqlalchemy import event

            @event.listens_for(app.state.db.sync_engine, "before_cursor_execute")
            def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
                conn.info.setdefault('query_start_time', []).append(time.time())
                logger.debug("executing_query", extra={{'query': statement, 'params': parameters}})

            @event.listens_for(app.state.db.sync_engine, "after_cursor_execute")
            def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
                total = time.time() - conn.info['query_start_time'].pop(-1)
                logger.info(
                    "query_executed",
                    extra={{
                        'query': statement,
                        'execution_time': total * 1000,  # ms
                        'rows_affected': cursor.rowcount
                    }}
                )

        response = await call_next(request)
        return response
"""
            }

        return {}
```

**검증 기준**:

- [ ] 구조화된 로그 포맷
- [ ] 민감 데이터 필터링
- [ ] 상관 ID 추적
- [ ] 성능 메트릭 로깅

#### SubTask 4.68.3: 모니터링 통합

**담당자**: DevOps 엔지니어  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/generation/monitoring_integration_generator.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class MonitoringService(Enum):
    PROMETHEUS = "prometheus"
    GRAFANA = "grafana"
    ELASTIC_APM = "elastic_apm"
    NEW_RELIC = "new_relic"
    DATADOG = "datadog"
    CUSTOM = "custom"

@dataclass
class MonitoringConfig:
    services: List[MonitoringService]
    metrics_port: int
    enable_tracing: bool
    enable_profiling: bool
    custom_metrics: List[Dict[str, Any]]
    alert_rules: List[Dict[str, Any]]
    sampling_rate: float

class MonitoringIntegrationGenerator:
    """모니터링 통합 코드 생성기"""

    def __init__(self):
        self.metrics_generator = MetricsGenerator()
        self.tracing_generator = TracingGenerator()
        self.alerting_generator = AlertingGenerator()
        self.dashboard_generator = DashboardGenerator()

    async def generate_monitoring_system(
        self,
        config: MonitoringConfig,
        language: str,
        framework: Optional[str] = None
    ) -> GeneratedMonitoringSystem:
        """완전한 모니터링 시스템 생성"""

        monitoring_code = {}

        # 1. 메트릭 수집
        metrics_code = await self.metrics_generator.generate(
            config,
            language,
            framework
        )
        monitoring_code.update(metrics_code)

        # 2. 분산 추적
        if config.enable_tracing:
            tracing_code = await self.tracing_generator.generate(
                config,
                language,
                framework
            )
            monitoring_code.update(tracing_code)

        # 3. 알림 규칙
        alert_rules = await self.alerting_generator.generate(
            config.alert_rules,
            config.services
        )

        # 4. 대시보드 설정
        dashboards = await self.dashboard_generator.generate(
            config.services,
            config.custom_metrics
        )

        # 5. 설정 파일
        configurations = await self._generate_configurations(
            config,
            language
        )

        return GeneratedMonitoringSystem(
            code=monitoring_code,
            alert_rules=alert_rules,
            dashboards=dashboards,
            configurations=configurations
        )

    async def _generate_configurations(
        self,
        config: MonitoringConfig,
        language: str
    ) -> Dict[str, str]:
        """모니터링 설정 파일 생성"""

        configs = {}

        # Prometheus 설정
        if MonitoringService.PROMETHEUS in config.services:
            configs['prometheus.yml'] = f"""
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'application'
    static_configs:
      - targets: ['localhost:{config.metrics_port}']
    metrics_path: '/metrics'

  - job_name: 'node_exporter'
    static_configs:
      - targets: ['localhost:9100']
"""

        # Docker Compose 설정
        configs['docker-compose.monitoring.yml'] = f"""
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./alert_rules.yml:/etc/prometheus/alert_rules.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    ports:
      - "9090:9090"
    networks:
      - monitoring

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    ports:
      - "3000:3000"
    networks:
      - monitoring

  alertmanager:
    image: prom/alertmanager:latest
    container_name: alertmanager
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
    ports:
      - "9093:9093"
    networks:
      - monitoring

volumes:
  prometheus_data:
  grafana_data:

networks:
  monitoring:
    driver: bridge
"""

        return configs

class MetricsGenerator:
    """메트릭 수집 코드 생성기"""

    async def generate(
        self,
        config: MonitoringConfig,
        language: str,
        framework: Optional[str]
    ) -> Dict[str, str]:
        """메트릭 수집 코드 생성"""

        if language == 'python' and MonitoringService.PROMETHEUS in config.services:
            return {
                'metrics.py': f"""
from prometheus_client import Counter, Histogram, Gauge, Summary
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import time
from functools import wraps
from typing import Callable, Any
import psutil
import asyncio

# 기본 메트릭 정의
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'HTTP requests in progress'
)

# 비즈니스 메트릭
business_operations_total = Counter(
    'business_operations_total',
    'Total business operations',
    ['operation', 'status']
)

active_users = Gauge(
    'active_users',
    'Number of active users'
)

# 시스템 메트릭
system_cpu_usage = Gauge(
    'system_cpu_usage_percent',
    'System CPU usage percentage'
)

system_memory_usage = Gauge(
    'system_memory_usage_bytes',
    'System memory usage in bytes'
)

database_connections_active = Gauge(
    'database_connections_active',
    'Active database connections'
)

# 커스텀 메트릭
{self._generate_custom_metrics(config.custom_metrics)}

class MetricsCollector:
    \"\"\"메트릭 수집기\"\"\"

    def __init__(self):
        self.start_system_metrics_collection()

    def track_request(self, method: str, endpoint: str, status: int, duration: float):
        \"\"\"HTTP 요청 추적\"\"\"
        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=str(status)
        ).inc()

        http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)

    def track_business_operation(self, operation: str, status: str):
        \"\"\"비즈니스 연산 추적\"\"\"
        business_operations_total.labels(
            operation=operation,
            status=status
        ).inc()

    def update_active_users(self, count: int):
        \"\"\"활성 사용자 수 업데이트\"\"\"
        active_users.set(count)

    def start_system_metrics_collection(self):
        \"\"\"시스템 메트릭 수집 시작\"\"\"

        async def collect_system_metrics():
            while True:
                # CPU 사용률
                cpu_percent = psutil.cpu_percent(interval=1)
                system_cpu_usage.set(cpu_percent)

                # 메모리 사용량
                memory = psutil.virtual_memory()
                system_memory_usage.set(memory.used)

                # 데이터베이스 연결 (예시)
                # db_connections = get_db_connection_count()
                # database_connections_active.set(db_connections)

                await asyncio.sleep(10)  # 10초마다 수집

        # 백그라운드 태스크로 실행
        asyncio.create_task(collect_system_metrics())

# 메트릭 데코레이터
def track_time(metric: Histogram):
    \"\"\"실행 시간 추적 데코레이터\"\"\"

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                metric.observe(duration)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                metric.observe(duration)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator

def track_in_progress(gauge: Gauge):
    \"\"\"진행 중인 작업 추적 데코레이터\"\"\"

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            gauge.inc()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                gauge.dec()

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            gauge.inc()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                gauge.dec()

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator

# FastAPI 통합
from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse
import time as time_module

def setup_metrics(app: FastAPI):
    \"\"\"FastAPI 앱에 메트릭 설정\"\"\"

    collector = MetricsCollector()

    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        start_time = time_module.time()

        # 진행 중인 요청 추적
        http_requests_in_progress.inc()

        try:
            response = await call_next(request)
            duration = time_module.time() - start_time

            # 메트릭 기록
            collector.track_request(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code,
                duration=duration
            )

            return response
        finally:
            http_requests_in_progress.dec()

    @app.get("/metrics", response_class=PlainTextResponse)
    async def metrics():
        \"\"\"Prometheus 메트릭 엔드포인트\"\"\"
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )
"""
            }

        elif language in ['javascript', 'typescript'] and MonitoringService.PROMETHEUS in config.services:
            return {
                'metrics.ts': f"""
import {{ Counter, Histogram, Gauge, register, collectDefaultMetrics }} from 'prom-client';
import {{ Request, Response, NextFunction }} from 'express';

// 기본 메트릭 수집
collectDefaultMetrics({{ register }});

// HTTP 메트릭
export const httpRequestsTotal = new Counter({{
    name: 'http_requests_total',
    help: 'Total HTTP requests',
    labelNames: ['method', 'route', 'status']
}});

export const httpRequestDuration = new Histogram({{
    name: 'http_request_duration_seconds',
    help: 'HTTP request latency',
    labelNames: ['method', 'route'],
    buckets: [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5]
}});

export const httpRequestsInProgress = new Gauge({{
    name: 'http_requests_in_progress',
    help: 'HTTP requests in progress'
}});

// 비즈니스 메트릭
export const businessOperationsTotal = new Counter({{
    name: 'business_operations_total',
    help: 'Total business operations',
    labelNames: ['operation', 'status']
}});

export const activeUsers = new Gauge({{
    name: 'active_users',
    help: 'Number of active users'
}});

// 시스템 메트릭
export const databaseConnectionsActive = new Gauge({{
    name: 'database_connections_active',
    help: 'Active database connections'
}});

// 커스텀 메트릭
{self._generate_custom_metrics_js(config.custom_metrics)}

export class MetricsCollector {{
    constructor() {{
        this.startSystemMetricsCollection();
    }}

    trackRequest(method: string, route: string, status: number, duration: number): void {{
        httpRequestsTotal.labels(method, route, status.toString()).inc();
        httpRequestDuration.labels(method, route).observe(duration);
    }}

    trackBusinessOperation(operation: string, status: string): void {{
        businessOperationsTotal.labels(operation, status).inc();
    }}

    updateActiveUsers(count: number): void {{
        activeUsers.set(count);
    }}

    private startSystemMetricsCollection(): void {{
        // 10초마다 시스템 메트릭 수집
        setInterval(() => {{
            // 예시: 데이터베이스 연결 수
            // const dbConnections = getDbConnectionCount();
            // databaseConnectionsActive.set(dbConnections);
        }}, 10000);
    }}
}}

// Express 미들웨어
export const metricsMiddleware = (
    req: Request,
    res: Response,
    next: NextFunction
): void => {{
    const start = Date.now();

    // 진행 중인 요청 추적
    httpRequestsInProgress.inc();

    // 응답 완료 시 메트릭 기록
    res.on('finish', () => {{
        const duration = (Date.now() - start) / 1000;
        const route = req.route?.path || req.path;

        httpRequestsTotal.labels(
            req.method,
            route,
            res.statusCode.toString()
        ).inc();

        httpRequestDuration.labels(
            req.method,
            route
        ).observe(duration);

        httpRequestsInProgress.dec();
    }});

    next();
}};

// 메트릭 엔드포인트
export const metricsEndpoint = async (
    req: Request,
    res: Response
): Promise<void> => {{
    res.set('Content-Type', register.contentType);
    const metrics = await register.metrics();
    res.end(metrics);
}};

// 데코레이터
export function TrackExecutionTime(
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor
): PropertyDescriptor {{
    const originalMethod = descriptor.value;
    const histogram = new Histogram({{
        name: `method_${{propertyKey}}_duration_seconds`,
        help: `Execution time of ${{propertyKey}}`,
        buckets: [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5]
    }});

    descriptor.value = async function (...args: any[]) {{
        const end = histogram.startTimer();
        try {{
            const result = await originalMethod.apply(this, args);
            end();
            return result;
        }} catch (error) {{
            end();
            throw error;
        }}
    }};

    return descriptor;
}}
"""
            }

        return {}

    def _generate_custom_metrics(self, custom_metrics: List[Dict[str, Any]]) -> str:
        """커스텀 메트릭 생성 (Python)"""

        metrics_code = []

        for metric in custom_metrics:
            if metric['type'] == 'counter':
                metrics_code.append(f"""
{metric['name']} = Counter(
    '{metric['name']}',
    '{metric['description']}',
    {metric.get('labels', [])}
)""")
            elif metric['type'] == 'gauge':
                metrics_code.append(f"""
{metric['name']} = Gauge(
    '{metric['name']}',
    '{metric['description']}',
    {metric.get('labels', [])}
)""")
            elif metric['type'] == 'histogram':
                metrics_code.append(f"""
{metric['name']} = Histogram(
    '{metric['name']}',
    '{metric['description']}',
    {metric.get('labels', [])},
    buckets={metric.get('buckets', [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10])}
)""")

        return '\n'.join(metrics_code)

class TracingGenerator:
    """분산 추적 코드 생성기"""

    async def generate(
        self,
        config: MonitoringConfig,
        language: str,
        framework: Optional[str]
    ) -> Dict[str, str]:
        """분산 추적 코드 생성"""

        if language == 'python':
            return {
                'tracing.py': f"""
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry import propagate
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class TracingConfig:
    \"\"\"추적 설정\"\"\"

    def __init__(
        self,
        service_name: str,
        otlp_endpoint: str = "http://localhost:4317",
        sampling_rate: float = {config.sampling_rate}
    ):
        self.service_name = service_name
        self.otlp_endpoint = otlp_endpoint
        self.sampling_rate = sampling_rate

class DistributedTracing:
    \"\"\"분산 추적 시스템\"\"\"

    def __init__(self, config: TracingConfig):
        self.config = config
        self.tracer = None
        self._setup_tracing()

    def _setup_tracing(self):
        \"\"\"추적 설정\"\"\"

        # 리소스 정의
        resource = Resource.create({{
            "service.name": self.config.service_name,
            "service.version": "1.0.0",
            "deployment.environment": os.getenv("ENVIRONMENT", "development")
        }})

        # TracerProvider 설정
        provider = TracerProvider(resource=resource)

        # OTLP 익스포터 설정
        otlp_exporter = OTLPSpanExporter(
            endpoint=self.config.otlp_endpoint,
            insecure=True
        )

        # 스팬 프로세서 추가
        span_processor = BatchSpanProcessor(otlp_exporter)
        provider.add_span_processor(span_processor)

        # 전역 TracerProvider 설정
        trace.set_tracer_provider(provider)

        # Tracer 가져오기
        self.tracer = trace.get_tracer(__name__)

        # 프로파게이터 설정
        propagate.set_global_textmap(TraceContextTextMapPropagator())

    def create_span(
        self,
        name: str,
        kind: trace.SpanKind = trace.SpanKind.INTERNAL,
        attributes: Optional[Dict[str, Any]] = None
    ):
        \"\"\"스팬 생성\"\"\"

        return self.tracer.start_as_current_span(
            name,
            kind=kind,
            attributes=attributes or {{}}
        )

    def add_span_attributes(self, attributes: Dict[str, Any]):
        \"\"\"현재 스팬에 속성 추가\"\"\"

        span = trace.get_current_span()
        if span and span.is_recording():
            for key, value in attributes.items():
                span.set_attribute(key, value)

    def add_span_event(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None
    ):
        \"\"\"스팬 이벤트 추가\"\"\"

        span = trace.get_current_span()
        if span and span.is_recording():
            span.add_event(name, attributes=attributes or {{}})

    def record_exception(self, exception: Exception):
        \"\"\"예외 기록\"\"\"

        span = trace.get_current_span()
        if span and span.is_recording():
            span.record_exception(exception)
            span.set_status(trace.Status(trace.StatusCode.ERROR))

# 자동 계측
def setup_automatic_instrumentation(app):
    \"\"\"자동 계측 설정\"\"\"

    # FastAPI 계측
    FastAPIInstrumentor.instrument_app(app)

    # HTTP 클라이언트 계측
    RequestsInstrumentor().instrument()

    # 데이터베이스 계측
    # SQLAlchemyInstrumentor().instrument(
    #     engine=db_engine,
    #     service="database"
    # )

# 수동 계측 예시
from functools import wraps

def trace_method(name: Optional[str] = None):
    \"\"\"메서드 추적 데코레이터\"\"\"

    def decorator(func):
        span_name = name or f"{{func.__module__}}.{{func.__name__}}"

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with tracer.start_as_current_span(span_name) as span:
                try:
                    # 함수 인자를 속성으로 추가
                    span.set_attribute("function.args", str(args))
                    span.set_attribute("function.kwargs", str(kwargs))

                    result = await func(*args, **kwargs)

                    # 성공 상태 설정
                    span.set_status(trace.Status(trace.StatusCode.OK))

                    return result
                except Exception as e:
                    # 예외 기록
                    span.record_exception(e)
                    span.set_status(
                        trace.Status(
                            trace.StatusCode.ERROR,
                            str(e)
                        )
                    )
                    raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            with tracer.start_as_current_span(span_name) as span:
                try:
                    span.set_attribute("function.args", str(args))
                    span.set_attribute("function.kwargs", str(kwargs))

                    result = func(*args, **kwargs)

                    span.set_status(trace.Status(trace.StatusCode.OK))

                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(
                        trace.Status(
                            trace.StatusCode.ERROR,
                            str(e)
                        )
                    )
                    raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator

# 사용 예시
tracing = DistributedTracing(
    TracingConfig(
        service_name=os.getenv("SERVICE_NAME", "my-service"),
        otlp_endpoint=os.getenv("OTLP_ENDPOINT", "http://localhost:4317")
    )
)

tracer = tracing.tracer
"""
            }

        return {}

class AlertingGenerator:
    """알림 규칙 생성기"""

    async def generate(
        self,
        alert_rules: List[Dict[str, Any]],
        services: List[MonitoringService]
    ) -> Dict[str, str]:
        """알림 규칙 생성"""

        rules_yaml = """groups:
  - name: application_alerts
    interval: 30s
    rules:"""

        # 기본 알림 규칙
        default_rules = [
            {
                'name': 'HighErrorRate',
                'expr': 'rate(http_requests_total{status=~"5.."}[5m]) > 0.05',
                'for': '5m',
                'labels': {'severity': 'critical'},
                'annotations': {
                    'summary': 'High error rate detected',
                    'description': 'Error rate is above 5% for 5 minutes'
                }
            },
            {
                'name': 'HighResponseTime',
                'expr': 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1',
                'for': '5m',
                'labels': {'severity': 'warning'},
                'annotations': {
                    'summary': 'High response time detected',
                    'description': '95th percentile response time is above 1 second'
                }
            },
            {
                'name': 'HighMemoryUsage',
                'expr': 'system_memory_usage_percent > 90',
                'for': '5m',
                'labels': {'severity': 'warning'},
                'annotations': {
                    'summary': 'High memory usage',
                    'description': 'Memory usage is above 90%'
                }
            }
        ]

        # 사용자 정의 규칙 추가
        all_rules = default_rules + alert_rules

        for rule in all_rules:
            rules_yaml += f"""
      - alert: {rule['name']}
        expr: {rule['expr']}
        for: {rule.get('for', '5m')}
        labels:
          severity: {rule.get('labels', {}).get('severity', 'warning')}
        annotations:
          summary: {rule.get('annotations', {}).get('summary', 'Alert triggered')}
          description: {rule.get('annotations', {}).get('description', 'Check the metric')}"""

        # Alertmanager 설정
        alertmanager_config = """global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'default'
  routes:
  - match:
      severity: critical
    receiver: critical_alerts
  - match:
      severity: warning
    receiver: warning_alerts

receivers:
- name: 'default'
  webhook_configs:
  - url: 'http://localhost:5001/webhooks/alerts'

- name: 'critical_alerts'
  email_configs:
  - to: 'critical-alerts@example.com'
    from: 'monitoring@example.com'
    smarthost: 'smtp.example.com:587'
    auth_username: 'monitoring@example.com'
    auth_password: 'password'

- name: 'warning_alerts'
  slack_configs:
  - api_url: 'YOUR_SLACK_WEBHOOK_URL'
    channel: '#alerts'
    title: 'Warning Alert'"""

        return {
            'alert_rules.yml': rules_yaml,
            'alertmanager.yml': alertmanager_config
        }

class DashboardGenerator:
    """대시보드 생성기"""

    async def generate(
        self,
        services: List[MonitoringService],
        custom_metrics: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """모니터링 대시보드 생성"""

        if MonitoringService.GRAFANA in services:
            # Grafana 대시보드 JSON
            dashboard = {
                "dashboard": {
                    "title": "Application Monitoring Dashboard",
                    "panels": [
                        {
                            "id": 1,
                            "title": "Request Rate",
                            "type": "graph",
                            "targets": [{
                                "expr": "rate(http_requests_total[5m])",
                                "legendFormat": "{{method}} {{status}}"
                            }],
                            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                        },
                        {
                            "id": 2,
                            "title": "Response Time (95th percentile)",
                            "type": "graph",
                            "targets": [{
                                "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
                                "legendFormat": "{{method}} {{route}}"
                            }],
                            "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                        },
                        {
                            "id": 3,
                            "title": "Error Rate",
                            "type": "graph",
                            "targets": [{
                                "expr": "rate(http_requests_total{status=~'5..'}[5m])",
                                "legendFormat": "{{method}} {{route}}"
                            }],
                            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
                        },
                        {
                            "id": 4,
                            "title": "Active Users",
                            "type": "singlestat",
                            "targets": [{
                                "expr": "active_users"
                            }],
                            "gridPos": {"h": 4, "w": 6, "x": 12, "y": 8}
                        }
                    ]
                }
            }

            # 커스텀 메트릭 패널 추가
            panel_id = 5
            for metric in custom_metrics:
                panel = {
                    "id": panel_id,
                    "title": metric.get('display_name', metric['name']),
                    "type": metric.get('panel_type', 'graph'),
                    "targets": [{
                        "expr": metric.get('query', metric['name'])
                    }],
                    "gridPos": {"h": 8, "w": 12, "x": (panel_id - 5) % 2 * 12, "y": 16 + ((panel_id - 5) // 2) * 8}
                }
                dashboard["dashboard"]["panels"].append(panel)
                panel_id += 1

            return {
                'grafana/dashboards/application.json': json.dumps(dashboard, indent=2),
                'grafana/provisioning/dashboards/dashboard.yml': """apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    options:
      path: /etc/grafana/provisioning/dashboards""",
                'grafana/provisioning/datasources/prometheus.yml': """apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true"""
            }

        return {}
```

**검증 기준**:

- [ ] Prometheus 메트릭 수집
- [ ] 분산 추적 구현
- [ ] 알림 규칙 설정
- [ ] Grafana 대시보드

#### SubTask 4.68.4: 디버깅 도구

**담당자**: 디버깅 전문가  
**예상 소요시간**: 8시간

**작업 내용**:

```python
# backend/src/agents/implementations/generation/debugging_tools_generator.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class DebuggingConfig:
    enable_debug_mode: bool
    enable_profiling: bool
    enable_memory_profiling: bool
    enable_request_debugging: bool
    debug_endpoints: bool
    log_sql_queries: bool
    stack_trace_depth: int

class DebuggingToolsGenerator:
    """디버깅 도구 코드 생성기"""

    def __init__(self):
        self.profiler_generator = ProfilerGenerator()
        self.debugger_generator = DebuggerGenerator()
        self.inspector_generator = InspectorGenerator()

    async def generate_debugging_tools(
        self,
        config: DebuggingConfig,
        language: str,
        framework: Optional[str] = None
    ) -> GeneratedDebuggingTools:
        """디버깅 도구 생성"""

        debugging_code = {}

        # 1. 프로파일러
        if config.enable_profiling:
            profiler_code = await self.profiler_generator.generate(
                config,
                language,
                framework
            )
            debugging_code.update(profiler_code)

        # 2. 디버거 헬퍼
        debugger_code = await self.debugger_generator.generate(
            config,
            language
        )
        debugging_code.update(debugger_code)

        # 3. 런타임 인스펙터
        inspector_code = await self.inspector_generator.generate(
            config,
            language,
            framework
        )
        debugging_code.update(inspector_code)

        # 4. 디버그 엔드포인트
        if config.debug_endpoints:
            endpoints_code = await self._generate_debug_endpoints(
                config,
                language,
                framework
            )
            debugging_code.update(endpoints_code)

        return GeneratedDebuggingTools(
            code=debugging_code,
            configuration=self._generate_debug_config(config)
        )

    async def _generate_debug_endpoints(
        self,
        config: DebuggingConfig,
        language: str,
        framework: Optional[str]
    ) -> Dict[str, str]:
        """디버그 엔드포인트 생성"""

        if framework == 'fastapi' and language == 'python':
            return {
                'debug_endpoints.py': f"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import psutil
import sys
import gc
import traceback
import threading
import asyncio
from typing import Dict, Any, List
import objgraph
import pympler.summary
import pympler.muppy
from datetime import datetime

router = APIRouter(prefix="/debug", tags=["debug"])

# 디버그 모드에서만 활성화
def debug_mode_only():
    if not {config.enable_debug_mode}:
        raise HTTPException(status_code=404, detail="Not Found")

@router.get("/health", dependencies=[Depends(debug_mode_only)])
async def debug_health():
    \"\"\"상세 헬스 체크\"\"\"

    process = psutil.Process()

    return {{
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "system": {{
            "cpu_percent": process.cpu_percent(interval=0.1),
            "memory_info": {{
                "rss": process.memory_info().rss,
                "vms": process.memory_info().vms,
                "percent": process.memory_percent()
            }},
            "open_files": len(process.open_files()),
            "num_threads": process.num_threads(),
            "connections": len(process.connections())
        }},
        "python": {{
            "version": sys.version,
            "gc_stats": gc.get_stats(),
            "gc_count": gc.get_count()
        }}
    }}

@router.get("/threads", dependencies=[Depends(debug_mode_only)])
async def debug_threads():
    \"\"\"활성 스레드 정보\"\"\"

    threads = []
    for thread in threading.enumerate():
        threads.append({{
            "name": thread.name,
            "ident": thread.ident,
            "daemon": thread.daemon,
            "is_alive": thread.is_alive()
        }})

    return {{
        "active_threads": threading.active_count(),
        "threads": threads
    }}

@router.get("/tasks", dependencies=[Depends(debug_mode_only)])
async def debug_async_tasks():
    \"\"\"비동기 태스크 정보\"\"\"

    tasks = []
    for task in asyncio.all_tasks():
        tasks.append({{
            "name": task.get_name(),
            "state": str(task._state),
            "stack": task.get_stack()
        }})

    return {{
        "total_tasks": len(tasks),
        "tasks": tasks
    }}

@router.get("/memory/objects", dependencies=[Depends(debug_mode_only)])
async def debug_memory_objects():
    \"\"\"메모리 객체 분석\"\"\"

    # 가장 많은 객체 타입
    most_common = objgraph.most_common_types(limit=20)

    # 메모리 사용량별 객체
    all_objects = pympler.muppy.get_objects()
    summary = pympler.summary.summarize(all_objects)

    return {{
        "most_common_types": [
            {{"type": type_name, "count": count}}
            for type_name, count in most_common
        ],
        "memory_summary": [
            {{
                "type": row[0],
                "count": row[1],
                "total_size": row[2]
            }}
            for row in summary[:20]
        ]
    }}

@router.get("/memory/growth", dependencies=[Depends(debug_mode_only)])
async def debug_memory_growth():
    \"\"\"메모리 증가 추적\"\"\"

    # 이전 스냅샷과 비교
    growth = objgraph.growth(limit=20)

    return {{
        "growth": [
            {{"type": type_name, "count": count, "change": change}}
            for type_name, count, change in growth
        ]
    }}

@router.get("/config", dependencies=[Depends(debug_mode_only)])
async def debug_config():
    \"\"\"현재 설정 정보\"\"\"

    import os

    # 민감한 정보 필터링
    safe_env = {{}}
    sensitive_keys = ['PASSWORD', 'SECRET', 'KEY', 'TOKEN']

    for key, value in os.environ.items():
        if any(sensitive in key.upper() for sensitive in sensitive_keys):
            safe_env[key] = '[REDACTED]'
        else:
            safe_env[key] = value

    return {{
        "environment": safe_env,
        "python_path": sys.path,
        "modules": list(sys.modules.keys())
    }}

@router.post("/gc", dependencies=[Depends(debug_mode_only)])
async def trigger_garbage_collection():
    \"\"\"가비지 컬렉션 실행\"\"\"

    before = gc.get_count()
    collected = gc.collect()
    after = gc.get_count()

    return {{
        "collected": collected,
        "before": before,
        "after": after
    }}

@router.get("/stack-traces", dependencies=[Depends(debug_mode_only)])
async def get_stack_traces():
    \"\"\"모든 스레드의 스택 트레이스\"\"\"

    traces = {{}}
    for thread_id, frame in sys._current_frames().items():
        traces[str(thread_id)] = {{
            "stack": traceback.format_stack(frame, limit={config.stack_trace_depth})
        }}

    return traces
"""
            }

        elif framework == 'express' and language in ['javascript', 'typescript']:
            return {
                'debugEndpoints.ts': f"""
import {{ Router, Request, Response }} from 'express';
import os from 'os';
import v8 from 'v8';
import {{ performance }} from 'perf_hooks';

const router = Router();

// 디버그 모드 체크 미들웨어
const debugModeOnly = (req: Request, res: Response, next: any) => {{
    if (!{str(config.enable_debug_mode).lower()}) {{
        return res.status(404).json({{ error: 'Not Found' }});
    }}
    next();
}};

router.use(debugModeOnly);

// 상세 헬스 체크
router.get('/health', (req: Request, res: Response) => {{
    const usage = process.memoryUsage();
    const cpuUsage = process.cpuUsage();

    res.json({{
        status: 'healthy',
        timestamp: new Date().toISOString(),
        system: {{
            platform: os.platform(),
            arch: os.arch(),
            nodeVersion: process.version,
            uptime: process.uptime(),
            pid: process.pid
        }},
        memory: {{
            rss: usage.rss,
            heapTotal: usage.heapTotal,
            heapUsed: usage.heapUsed,
            external: usage.external,
            arrayBuffers: usage.arrayBuffers
        }},
        cpu: {{
            user: cpuUsage.user,
            system: cpuUsage.system
        }},
        v8: {{
            heapStatistics: v8.getHeapStatistics(),
            heapSpaceStatistics: v8.getHeapSpaceStatistics()
        }}
    }});
}});

// V8 힙 스냅샷
router.get('/heap-snapshot', (req: Request, res: Response) => {{
    const snapshot = v8.writeHeapSnapshot();
    res.json({{
        message: 'Heap snapshot written',
        filename: snapshot
    }});
}});

// 성능 메트릭
router.get('/performance', (req: Request, res: Response) => {{
    const perfObserver = new PerformanceObserver((items) => {{
        const entries = items.getEntries();
        res.json({{
            entries: entries.map(entry => ({{
                name: entry.name,
                duration: entry.duration,
                startTime: entry.startTime,
                entryType: entry.entryType
            }}))
        }});
    }});

    perfObserver.observe({{ entryTypes: ['measure', 'function'] }});
}});

// 환경 변수 (민감한 정보 필터링)
router.get('/config', (req: Request, res: Response) => {{
    const sensitiveKeys = ['PASSWORD', 'SECRET', 'KEY', 'TOKEN'];
    const safeEnv: Record<string, string> = {{}};

    Object.entries(process.env).forEach(([key, value]) => {{
        if (sensitiveKeys.some(sensitive => key.toUpperCase().includes(sensitive))) {{
            safeEnv[key] = '[REDACTED]';
        }} else {{
            safeEnv[key] = value || '';
        }}
    }});
    res.json({
        environment: safeEnv,
        nodeModules: Object.keys(require.cache),
        processInfo: {
            execPath: process.execPath,
            cwd: process.cwd(),
            argv: process.argv
        }
    });
});

// 활성 핸들과 요청 추적
router.get('/active-handles', (req: Request, res: Response) => {
    const activeHandles = (process as any)._getActiveHandles();
    const activeRequests = (process as any)._getActiveRequests();

    res.json({
        activeHandles: activeHandles.length,
        activeRequests: activeRequests.length,
        handles: activeHandles.map((handle: any) => ({
            type: handle.constructor.name,
            fd: handle.fd || null
        }))
    });
});

// 가비지 컬렉션 트리거
router.post('/gc', (req: Request, res: Response) => {
    if (global.gc) {
        const before = process.memoryUsage();
        global.gc();
        const after = process.memoryUsage();

        res.json({
            message: 'Garbage collection triggered',
            before,
            after,
            freed: {
                rss: before.rss - after.rss,
                heapTotal: before.heapTotal - after.heapTotal,
                heapUsed: before.heapUsed - after.heapUsed
            }
        });
    } else {
        res.status(400).json({
            error: 'Garbage collection not exposed. Run node with --expose-gc flag'
        });
    }
});

export default router;
"""
            }

        return {}

class ProfilerGenerator:
    """프로파일러 코드 생성기"""

    async def generate(
        self,
        config: DebuggingConfig,
        language: str,
        framework: Optional[str]
    ) -> Dict[str, str]:
        """프로파일링 코드 생성"""

        if language == 'python':
            return {
                'profiler.py': f"""
import cProfile
import pstats
import io
import functools
import time
import tracemalloc
import linecache
from typing import Callable, Optional, Dict, Any, List
from datetime import datetime
import asyncio
from memory_profiler import profile as memory_profile

class PerformanceProfiler:
    \"\"\"성능 프로파일러\"\"\"

    def __init__(self):
        self.profiles: Dict[str, pstats.Stats] = {{}}
        self.execution_times: Dict[str, List[float]] = {{}}
        self.memory_snapshots: Dict[str, Any] = {{}}

        if {config.enable_memory_profiling}:
            tracemalloc.start()

    def profile_function(self, name: Optional[str] = None):
        \"\"\"함수 프로파일링 데코레이터\"\"\"

        def decorator(func: Callable) -> Callable:
            profile_name = name or f"{{func.__module__}}.{{func.__name__}}"

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                # CPU 프로파일링
                profiler = cProfile.Profile()
                profiler.enable()

                start_time = time.time()
                start_memory = tracemalloc.get_traced_memory() if tracemalloc.is_tracing() else (0, 0)

                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    profiler.disable()
                    execution_time = time.time() - start_time

                    # 프로파일 저장
                    self._save_profile(profile_name, profiler)

                    # 실행 시간 기록
                    if profile_name not in self.execution_times:
                        self.execution_times[profile_name] = []
                    self.execution_times[profile_name].append(execution_time)

                    # 메모리 사용량
                    if tracemalloc.is_tracing():
                        current, peak = tracemalloc.get_traced_memory()
                        memory_used = current - start_memory[0]

                        if {config.enable_debug_mode}:
                            print(f"[PROFILE] {{profile_name}}: "
                                  f"{{execution_time:.3f}}s, "
                                  f"Memory: {{memory_used / 1024 / 1024:.2f}}MB")

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                # 비동기 함수 프로파일링
                start_time = time.time()
                start_memory = tracemalloc.get_traced_memory() if tracemalloc.is_tracing() else (0, 0)

                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    execution_time = time.time() - start_time

                    if profile_name not in self.execution_times:
                        self.execution_times[profile_name] = []
                    self.execution_times[profile_name].append(execution_time)

                    if tracemalloc.is_tracing():
                        current, peak = tracemalloc.get_traced_memory()
                        memory_used = current - start_memory[0]

                        if {config.enable_debug_mode}:
                            print(f"[PROFILE] {{profile_name}} (async): "
                                  f"{{execution_time:.3f}}s, "
                                  f"Memory: {{memory_used / 1024 / 1024:.2f}}MB")

            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator

    def _save_profile(self, name: str, profiler: cProfile.Profile):
        \"\"\"프로파일 저장\"\"\"

        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s)
        ps.strip_dirs()
        ps.sort_stats('cumulative')

        self.profiles[name] = ps

    def get_profile_stats(self, name: str, top_n: int = 20) -> Dict[str, Any]:
        \"\"\"프로파일 통계 가져오기\"\"\"

        if name not in self.profiles:
            return {{"error": "Profile not found"}}

        s = io.StringIO()
        ps = self.profiles[name]
        ps.stream = s
        ps.print_stats(top_n)

        return {{
            "profile": s.getvalue(),
            "total_calls": ps.total_calls,
            "total_time": ps.total_tt,
            "execution_times": self.execution_times.get(name, [])
        }}

    def memory_profile(self, name: Optional[str] = None):
        \"\"\"메모리 프로파일링 데코레이터\"\"\"

        def decorator(func: Callable) -> Callable:
            profile_name = name or f"{{func.__module__}}.{{func.__name__}}"

            @functools.wraps(func)
            @memory_profile
            def wrapper(*args, **kwargs):
                # 메모리 스냅샷 시작
                if tracemalloc.is_tracing():
                    snapshot_start = tracemalloc.take_snapshot()

                result = func(*args, **kwargs)

                # 메모리 스냅샷 종료
                if tracemalloc.is_tracing():
                    snapshot_end = tracemalloc.take_snapshot()

                    # 상위 메모리 사용 통계
                    top_stats = snapshot_end.compare_to(snapshot_start, 'lineno')

                    self.memory_snapshots[profile_name] = {{
                        'timestamp': datetime.now().isoformat(),
                        'top_allocations': [
                            {{
                                'file': stat.traceback.format()[0] if stat.traceback else 'unknown',
                                'size_diff': stat.size_diff,
                                'count_diff': stat.count_diff
                            }}
                            for stat in top_stats[:10]
                        ]
                    }}

                return result

            return wrapper

        return decorator

    def get_memory_stats(self) -> Dict[str, Any]:
        \"\"\"메모리 통계 가져오기\"\"\"

        if not tracemalloc.is_tracing():
            return {{"error": "Memory tracing not enabled"}}

        current, peak = tracemalloc.get_traced_memory()
        snapshot = tracemalloc.take_snapshot()

        # 상위 10개 메모리 할당
        top_stats = snapshot.statistics('lineno')

        return {{
            "current_memory": current,
            "peak_memory": peak,
            "top_allocations": [
                {{
                    "file": stat.traceback.format()[0] if stat.traceback else 'unknown',
                    "size": stat.size,
                    "count": stat.count
                }}
                for stat in top_stats[:10]
            ],
            "memory_snapshots": self.memory_snapshots
        }}

# 전역 프로파일러 인스턴스
profiler = PerformanceProfiler()

# 라인 프로파일러
class LineProfiler:
    \"\"\"라인별 프로파일러\"\"\"

    def __init__(self):
        self.line_stats: Dict[str, Dict[int, Dict[str, float]]] = {{}}

    def profile_lines(self, func: Callable) -> Callable:
        \"\"\"라인별 실행 시간 측정\"\"\"

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import sys
            import inspect

            # 함수 소스 코드 가져오기
            source_lines = inspect.getsourcelines(func)[0]
            filename = inspect.getfile(func)
            func_name = func.__name__

            # 라인별 시간 측정을 위한 trace 함수
            line_times = {{}}

            def trace_lines(frame, event, arg):
                if event != 'line':
                    return

                line_no = frame.f_lineno
                if frame.f_code.co_filename == filename and frame.f_code.co_name == func_name:
                    if line_no not in line_times:
                        line_times[line_no] = {{'count': 0, 'total_time': 0}}

                    line_times[line_no]['count'] += 1
                    line_times[line_no]['start'] = time.time()

                return trace_lines

            # 트레이싱 활성화
            sys.settrace(trace_lines)

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                sys.settrace(None)

                # 결과 저장
                self.line_stats[func_name] = line_times

        return wrapper

    def get_line_stats(self, func_name: str) -> Dict[str, Any]:
        \"\"\"라인별 통계 가져오기\"\"\"

        if func_name not in self.line_stats:
            return {{"error": "No line profiling data for this function"}}

        return {{
            "function": func_name,
            "lines": self.line_stats[func_name]
        }}

# SQL 쿼리 프로파일러
class SQLQueryProfiler:
    \"\"\"SQL 쿼리 프로파일러\"\"\"

    def __init__(self):
        self.queries: List[Dict[str, Any]] = []
        self.slow_query_threshold = 1.0  # seconds

    def log_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]],
        execution_time: float,
        rows_affected: int
    ):
        \"\"\"쿼리 로깅\"\"\"

        query_info = {{
            'query': query,
            'params': params,
            'execution_time': execution_time,
            'rows_affected': rows_affected,
            'timestamp': datetime.now().isoformat(),
            'slow': execution_time > self.slow_query_threshold
        }}

        self.queries.append(query_info)

        if query_info['slow'] and {config.enable_debug_mode}:
            print(f"[SLOW QUERY] {{execution_time:.3f}}s: {{query[:100]}}...")

    def get_query_stats(self) -> Dict[str, Any]:
        \"\"\"쿼리 통계\"\"\"

        if not self.queries:
            return {{"total_queries": 0}}

        total_time = sum(q['execution_time'] for q in self.queries)
        slow_queries = [q for q in self.queries if q['slow']]

        return {{
            'total_queries': len(self.queries),
            'total_execution_time': total_time,
            'average_execution_time': total_time / len(self.queries),
            'slow_queries_count': len(slow_queries),
            'slow_queries': slow_queries[-10:],  # 최근 10개
            'top_queries': sorted(
                self.queries,
                key=lambda x: x['execution_time'],
                reverse=True
            )[:10]
        }}
"""
            }

        elif language in ['javascript', 'typescript']:
            return {
                'profiler.ts': f"""
import {{ performance, PerformanceObserver }} from 'perf_hooks';
import v8Profiler from 'v8-profiler-next';
import fs from 'fs';
import path from 'path';

interface ProfileData {{
    name: string;
    startTime: number;
    endTime?: number;
    duration?: number;
    memory?: {{
        before: NodeJS.MemoryUsage;
        after: NodeJS.MemoryUsage;
        diff: NodeJS.MemoryUsage;
    }};
}}

export class PerformanceProfiler {{
    private profiles: Map<string, ProfileData[]> = new Map();
    private cpuProfiles: Map<string, any> = new Map();
    private heapSnapshots: Map<string, any> = new Map();

    constructor(private config: {{ enableProfiling: boolean; enableMemoryProfiling: boolean }}) {{
        if (this.config.enableProfiling) {{
            v8Profiler.setGenerateType(1);
        }}
    }}

    // 함수 실행 시간 측정
    measurePerformance<T>(
        name: string,
        fn: () => T | Promise<T>
    ): T | Promise<T> {{
        const startTime = performance.now();
        const startMemory = process.memoryUsage();

        const profileData: ProfileData = {{
            name,
            startTime,
            memory: {{ before: startMemory, after: startMemory, diff: startMemory }}
        }};

        try {{
            const result = fn();

            if (result instanceof Promise) {{
                return result.finally(() => {{
                    this.recordProfile(profileData);
                }});
            }} else {{
                this.recordProfile(profileData);
                return result;
            }}
        }} catch (error) {{
            this.recordProfile(profileData);
            throw error;
        }}
    }}

    private recordProfile(profile: ProfileData): void {{
        profile.endTime = performance.now();
        profile.duration = profile.endTime - profile.startTime;

        const endMemory = process.memoryUsage();
        profile.memory!.after = endMemory;
        profile.memory!.diff = {{
            rss: endMemory.rss - profile.memory!.before.rss,
            heapTotal: endMemory.heapTotal - profile.memory!.before.heapTotal,
            heapUsed: endMemory.heapUsed - profile.memory!.before.heapUsed,
            external: endMemory.external - profile.memory!.before.external,
            arrayBuffers: endMemory.arrayBuffers - profile.memory!.before.arrayBuffers
        }};

        if (!this.profiles.has(profile.name)) {{
            this.profiles.set(profile.name, []);
        }}

        this.profiles.get(profile.name)!.push(profile);

        if ({config.enable_debug_mode}) {{
            console.log(
                `[PROFILE] ${{profile.name}}: ${{profile.duration.toFixed(3)}}ms, ` +
                `Memory: ${{(profile.memory!.diff.heapUsed / 1024 / 1024).toFixed(2)}}MB`
            );
        }}
    }}

    // CPU 프로파일링
    async startCPUProfile(name: string): Promise<void> {{
        if (!this.config.enableProfiling) return;

        v8Profiler.startProfiling(name, true);
    }}

    async stopCPUProfile(name: string): Promise<void> {{
        if (!this.config.enableProfiling) return;

        const profile = v8Profiler.stopProfiling(name);
        this.cpuProfiles.set(name, profile);

        // 프로파일을 파일로 저장
        return new Promise((resolve, reject) => {{
            profile.export((error: Error | null, result: string) => {{
                if (error) {{
                    reject(error);
                    return;
                }}

                const filename = path.join(
                    'profiles',
                    `cpu-${{name}}-${{Date.now()}}.cpuprofile`
                );

                fs.writeFile(filename, result, (err) => {{
                    profile.delete();
                    if (err) reject(err);
                    else resolve();
                }});
            }});
        }});
    }}

    // 힙 스냅샷
    async takeHeapSnapshot(name: string): Promise<void> {{
        if (!this.config.enableMemoryProfiling) return;

        const snapshot = v8Profiler.takeSnapshot(name);
        this.heapSnapshots.set(name, snapshot);

        return new Promise((resolve, reject) => {{
            snapshot.export((error: Error | null, result: string) => {{
                if (error) {{
                    reject(error);
                    return;
                }}

                const filename = path.join(
                    'profiles',
                    `heap-${{name}}-${{Date.now()}}.heapsnapshot`
                );

                fs.writeFile(filename, result, (err) => {{
                    snapshot.delete();
                    if (err) reject(err);
                    else resolve();
                }});
            }});
        }});
    }}

    // 프로파일 통계
    getProfileStats(name?: string): any {{
        if (name) {{
            const profiles = this.profiles.get(name) || [];
            const durations = profiles.map(p => p.duration || 0);

            return {{
                name,
                count: profiles.length,
                totalTime: durations.reduce((a, b) => a + b, 0),
                averageTime: durations.length > 0
                    ? durations.reduce((a, b) => a + b, 0) / durations.length
                    : 0,
                minTime: Math.min(...durations),
                maxTime: Math.max(...durations)
            }};
        }}

        // 모든 프로파일 통계
        const stats: any = {{}};
        this.profiles.forEach((profiles, name) => {{
            stats[name] = this.getProfileStats(name);
        }});

        return stats;
    }}
}}

// 데코레이터
export function Profile(name?: string) {{
    return function (
        target: any,
        propertyKey: string,
        descriptor: PropertyDescriptor
    ) {{
        const originalMethod = descriptor.value;
        const profileName = name || `${{target.constructor.name}}.${{propertyKey}}`;

        descriptor.value = async function (...args: any[]) {{
            const profiler = (global as any).profiler || new PerformanceProfiler({{
                enableProfiling: true,
                enableMemoryProfiling: true
            }});

            return profiler.measurePerformance(profileName, () =>
                originalMethod.apply(this, args)
            );
        }};

        return descriptor;
    }};
}}

// Express 미들웨어
export const profilingMiddleware = (profiler: PerformanceProfiler) => {{
    return (req: any, res: any, next: any) => {{
        const startTime = performance.now();
        const startMemory = process.memoryUsage();

        res.on('finish', () => {{
            const duration = performance.now() - startTime;
            const endMemory = process.memoryUsage();

            profiler.measurePerformance(
                `HTTP ${{req.method}} ${{req.path}}`,
                () => {{}}
            );
        }});

        next();
    }};
}};
"""
            }

        return {}

class DebuggerGenerator:
    """디버거 헬퍼 코드 생성기"""

    async def generate(
        self,
        config: DebuggingConfig,
        language: str
    ) -> Dict[str, str]:
        """디버거 헬퍼 코드 생성"""

        if language == 'python':
            return {
                'debugger_helpers.py': f"""
import inspect
import pprint
import sys
import os
from typing import Any, Dict, List, Optional, Callable
import functools
import logging

logger = logging.getLogger(__name__)

class DebugContext:
    \"\"\"디버그 컨텍스트\"\"\"

    def __init__(self, name: str):
        self.name = name
        self.enabled = {config.enable_debug_mode}
        self.variables: Dict[str, Any] = {{}}
        self.checkpoints: List[Dict[str, Any]] = []

    def __enter__(self):
        if self.enabled:
            print(f"[DEBUG] Entering context: {{self.name}}")
            self._capture_locals()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.enabled:
            print(f"[DEBUG] Exiting context: {{self.name}}")
            if exc_type:
                print(f"[DEBUG] Exception: {{exc_type.__name__}}: {{exc_val}}")
            self._print_summary()

    def _capture_locals(self):
        \"\"\"로컬 변수 캡처\"\"\"
        frame = inspect.currentframe()
        if frame and frame.f_back:
            self.variables = frame.f_back.f_locals.copy()

    def checkpoint(self, label: str, **kwargs):
        \"\"\"체크포인트 추가\"\"\"
        if self.enabled:
            checkpoint = {{
                'label': label,
                'timestamp': time.time(),
                'variables': kwargs,
                'stack': inspect.stack()[1:4]  # 상위 3개 프레임
            }}
            self.checkpoints.append(checkpoint)
            print(f"[DEBUG] Checkpoint: {{label}}")
            if kwargs:
                pprint.pprint(kwargs, indent=2)

    def _print_summary(self):
        \"\"\"디버그 요약 출력\"\"\"
        if self.checkpoints:
            print(f"[DEBUG] Summary for {{self.name}}:")
            for cp in self.checkpoints:
                print(f"  - {{cp['label']}}")

def debug_function(
    print_args: bool = True,
    print_result: bool = True,
    print_time: bool = True
):
    \"\"\"함수 디버깅 데코레이터\"\"\"

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not {config.enable_debug_mode}:
                return func(*args, **kwargs)

            func_name = f"{{func.__module__}}.{{func.__name__}}"

            # 함수 시작
            print(f"\\n[DEBUG] Calling: {{func_name}}")

            # 인자 출력
            if print_args:
                print(f"[DEBUG] Args: {{args}}")
                print(f"[DEBUG] Kwargs: {{kwargs}}")

            # 실행
            start_time = time.time() if print_time else None

            try:
                result = func(*args, **kwargs)

                # 결과 출력
                if print_result:
                    print(f"[DEBUG] Result: {{result}}")

                return result

            except Exception as e:
                print(f"[DEBUG] Exception in {{func_name}}: {{e}}")
                raise

            finally:
                if print_time and start_time:
                    duration = time.time() - start_time
                    print(f"[DEBUG] Execution time: {{duration:.3f}}s")
                print(f"[DEBUG] Finished: {{func_name}}\\n")

        return wrapper

    return decorator

class DebugInspector:
    \"\"\"런타임 객체 검사기\"\"\"

    @staticmethod
    def inspect_object(obj: Any, max_depth: int = 3) -> Dict[str, Any]:
        \"\"\"객체 상세 검사\"\"\"

        return {{
            'type': type(obj).__name__,
            'module': type(obj).__module__,
            'id': id(obj),
            'size': sys.getsizeof(obj),
            'attributes': DebugInspector._get_attributes(obj, max_depth),
            'methods': DebugInspector._get_methods(obj),
            'mro': [cls.__name__ for cls in type(obj).__mro__],
            'repr': repr(obj)
        }}

    @staticmethod
    def _get_attributes(obj: Any, max_depth: int, current_depth: int = 0) -> Dict[str, Any]:
        \"\"\"객체 속성 가져오기\"\"\"

        if current_depth >= max_depth:
            return {{'...': 'max depth reached'}}

        attributes = {{}}

        for name in dir(obj):
            if name.startswith('_'):
                continue

            try:
                value = getattr(obj, name)

                # 메서드는 제외
                if not callable(value):
                    if hasattr(value, '__dict__') and current_depth < max_depth - 1:
                        attributes[name] = DebugInspector._get_attributes(
                            value,
                            max_depth,
                            current_depth + 1
                        )
                    else:
                        attributes[name] = {{
                            'type': type(value).__name__,
                            'value': str(value)[:100]
                        }}
            except Exception as e:
                attributes[name] = f"Error: {{e}}"

        return attributes

    @staticmethod
    def _get_methods(obj: Any) -> List[str]:
        \"\"\"객체 메서드 목록\"\"\"

        methods = []
        for name in dir(obj):
            try:
                if callable(getattr(obj, name)) and not name.startswith('_'):
                    methods.append(name)
            except:
                pass

        return methods

# 조건부 브레이크포인트
def conditional_breakpoint(condition: Callable[[], bool], message: str = ""):
    \"\"\"조건부 브레이크포인트\"\"\"

    if {config.enable_debug_mode} and condition():
        import pdb

        frame = inspect.currentframe()
        if frame and frame.f_back:
            print(f"\\n[BREAKPOINT] {{message}}")
            print(f"Location: {{frame.f_back.f_code.co_filename}}:"
                  f"{{frame.f_back.f_lineno}}")

            # 로컬 변수 출력
            print("\\nLocal variables:")
            for name, value in frame.f_back.f_locals.items():
                print(f"  {{name}} = {{value}}")

        pdb.set_trace()

# 변수 워처
class VariableWatcher:
    \"\"\"변수 변경 감시\"\"\"

    def __init__(self):
        self.watches: Dict[str, Any] = {{}}

    def watch(self, name: str, value: Any):
        \"\"\"변수 감시 시작\"\"\"

        if name in self.watches:
            old_value = self.watches[name]
            if old_value != value:
                print(f"[WATCH] {{name}} changed: {{old_value}} -> {{value}}")

                # 스택 트레이스
                if {config.enable_debug_mode}:
                    import traceback
                    print("Stack trace:")
                    for line in traceback.format_stack()[:-1]:
                        print(line.strip())

        self.watches[name] = value

    def unwatch(self, name: str):
        \"\"\"변수 감시 중지\"\"\"

        if name in self.watches:
            del self.watches[name]

# 전역 워처
watcher = VariableWatcher()

# 디버그 출력 헬퍼
def debug_print(*args, **kwargs):
    \"\"\"조건부 디버그 출력\"\"\"

    if {config.enable_debug_mode}:
        frame = inspect.currentframe()
        if frame and frame.f_back:
            location = f"{{frame.f_back.f_code.co_filename}}:{{frame.f_back.f_lineno}}"
            print(f"[DEBUG @ {{location}}]", *args, **kwargs)
"""
            }

        return {}

class InspectorGenerator:
    """런타임 인스펙터 생성기"""

    async def generate(
        self,
        config: DebuggingConfig,
        language: str,
        framework: Optional[str]
    ) -> Dict[str, str]:
        """런타임 인스펙터 코드 생성"""

        if language == 'python':
            return {
                'runtime_inspector.py': f"""
import gc
import sys
import weakref
import threading
import asyncio
from typing import Dict, List, Any, Optional, Type
import psutil
import inspect
import dis

class RuntimeInspector:
    \"\"\"런타임 상태 검사기\"\"\"

    def __init__(self):
        self.object_registry: weakref.WeakValueDictionary = weakref.WeakValueDictionary()
        self.type_counts: Dict[str, int] = {{}}

    def register_object(self, name: str, obj: Any):
        \"\"\"객체 등록 (약한 참조)\"\"\"
        self.object_registry[name] = obj

    def inspect_runtime_state(self) -> Dict[str, Any]:
        \"\"\"전체 런타임 상태 검사\"\"\"

        return {{
            'python_version': sys.version,
            'platform': sys.platform,
            'memory': self._inspect_memory(),
            'threads': self._inspect_threads(),
            'async_tasks': self._inspect_async_tasks(),
            'modules': self._inspect_modules(),
            'gc_stats': self._inspect_gc(),
            'registered_objects': self._inspect_registered_objects()
        }}

    def _inspect_memory(self) -> Dict[str, Any]:
        \"\"\"메모리 상태 검사\"\"\"

        process = psutil.Process()
        memory_info = process.memory_info()

        # 객체 타입별 카운트
        type_counts = {{}}
        for obj in gc.get_objects():
            obj_type = type(obj).__name__
            type_counts[obj_type] = type_counts.get(obj_type, 0) + 1

        # 상위 10개 타입
        top_types = sorted(
            type_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return {{
            'rss': memory_info.rss,
            'vms': memory_info.vms,
            'percent': process.memory_percent(),
            'available': psutil.virtual_memory().available,
            'object_count': len(gc.get_objects()),
            'top_object_types': dict(top_types)
        }}

    def _inspect_threads(self) -> List[Dict[str, Any]]:
        \"\"\"스레드 상태 검사\"\"\"

        threads = []
        for thread in threading.enumerate():
            thread_info = {{
                'name': thread.name,
                'ident': thread.ident,
                'daemon': thread.daemon,
                'is_alive': thread.is_alive()
            }}

            # 스택 프레임 정보
            if thread.ident and {config.enable_debug_mode}:
                frame = sys._current_frames().get(thread.ident)
                if frame:
                    thread_info['current_function'] = frame.f_code.co_name
                    thread_info['current_file'] = frame.f_code.co_filename
                    thread_info['current_line'] = frame.f_lineno

            threads.append(thread_info)

        return threads

    def _inspect_async_tasks(self) -> Dict[str, Any]:
        \"\"\"비동기 태스크 검사\"\"\"

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return {{'error': 'No running event loop'}}

        tasks = asyncio.all_tasks(loop)

        task_info = []
        for task in tasks:
            info = {{
                'name': task.get_name(),
                'done': task.done(),
                'cancelled': task.cancelled()
            }}

            if not task.done():
                coro = task.get_coro()
                info['coroutine'] = {{
                    'name': coro.__name__ if hasattr(coro, '__name__') else str(coro),
                    'state': str(task._state)
                }}

            task_info.append(info)

        return {{
            'event_loop': str(loop),
            'task_count': len(tasks),
            'tasks': task_info
        }}

    def _inspect_modules(self) -> Dict[str, Any]:
        \"\"\"모듈 검사\"\"\"

        modules = {{
            'total_count': len(sys.modules),
            'stdlib_count': 0,
            'third_party_count': 0,
            'local_count': 0
        }}

        # 모듈 분류
        stdlib_path = sys.prefix
        for name, module in sys.modules.items():
            if module and hasattr(module, '__file__') and module.__file__:
                if module.__file__.startswith(stdlib_path):
                    modules['stdlib_count'] += 1
                elif 'site-packages' in module.__file__:
                    modules['third_party_count'] += 1
                else:
                    modules['local_count'] += 1

        return modules

    def _inspect_gc(self) -> Dict[str, Any]:
        \"\"\"가비지 컬렉터 검사\"\"\"

        return {{
            'enabled': gc.isenabled(),
            'count': gc.get_count(),
            'threshold': gc.get_threshold(),
            'stats': gc.get_stats() if hasattr(gc, 'get_stats') else None,
            'garbage_count': len(gc.garbage)
        }}

    def _inspect_registered_objects(self) -> Dict[str, Any]:
        \"\"\"등록된 객체 검사\"\"\"

        objects = {{}}
        for name, obj in self.object_registry.items():
            objects[name] = {{
                'type': type(obj).__name__,
                'id': id(obj),
                'size': sys.getsizeof(obj)
            }}

        return objects

    def find_references(self, obj: Any) -> List[Any]:
        \"\"\"객체 참조 찾기\"\"\"

        return gc.get_referents(obj)

    def find_referrers(self, obj: Any) -> List[Any]:
        \"\"\"객체를 참조하는 것들 찾기\"\"\"

        return gc.get_referrers(obj)

    def analyze_function(self, func: Callable) -> Dict[str, Any]:
        \"\"\"함수 분석\"\"\"

        if not callable(func):
            return {{'error': 'Not a callable'}}

        analysis = {{
            'name': func.__name__,
            'module': func.__module__,
            'file': inspect.getfile(func),
            'line': inspect.getsourcelines(func)[1],
            'args': str(inspect.signature(func)),
            'doc': inspect.getdoc(func)
        }}

        # 바이트코드 분석
        if {config.enable_debug_mode}:
            bytecode = []
            for instruction in dis.get_instructions(func):
                bytecode.append({{
                    'opname': instruction.opname,
                    'arg': instruction.arg,
                    'argval': str(instruction.argval),
                    'offset': instruction.offset
                }})

            analysis['bytecode'] = bytecode[:20]  # 처음 20개만

        return analysis

# 전역 인스펙터
inspector = RuntimeInspector()

# 메모리 누수 감지
class MemoryLeakDetector:
    \"\"\"메모리 누수 감지기\"\"\"

    def __init__(self):
        self.baseline: Optional[Dict[str, int]] = None
        self.growth_threshold = 1000  # 객체 수 증가 임계값

    def take_baseline(self):
        \"\"\"기준선 설정\"\"\"

        gc.collect()
        self.baseline = self._count_objects()

        return {{
            'total_objects': sum(self.baseline.values()),
            'types': len(self.baseline)
        }}

    def check_growth(self) -> Dict[str, Any]:
        \"\"\"메모리 증가 확인\"\"\"

        if not self.baseline:
            return {{'error': 'No baseline set'}}

        gc.collect()
        current = self._count_objects()

        growth = {{}}
        potential_leaks = []

        for type_name, count in current.items():
            baseline_count = self.baseline.get(type_name, 0)
            diff = count - baseline_count

            if diff > 0:
                growth[type_name] = {{
                    'baseline': baseline_count,
                    'current': count,
                    'growth': diff
                }}

                if diff > self.growth_threshold:
                    potential_leaks.append(type_name)

        return {{
            'growth': growth,
            'potential_leaks': potential_leaks,
            'total_growth': sum(g['growth'] for g in growth.values())
        }}

    def _count_objects(self) -> Dict[str, int]:
        \"\"\"객체 타입별 카운트\"\"\"

        counts = {{}}
        for obj in gc.get_objects():
            type_name = type(obj).__name__
            counts[type_name] = counts.get(type_name, 0) + 1

        return counts
"""
            }

        return {}

    def _generate_debug_config(self, config: DebuggingConfig) -> Dict[str, str]:
        """디버그 설정 파일 생성"""

        return {
            'debug_config.yaml': f"""
debug:
  enabled: {config.enable_debug_mode}
  profiling:
    enabled: {config.enable_profiling}
    memory_profiling: {config.enable_memory_profiling}
    sql_queries: {config.log_sql_queries}

  endpoints:
    enabled: {config.debug_endpoints}
    prefix: /debug
    auth_required: true

  logging:
    level: DEBUG
    format: detailed
    include_stack_trace: true
    stack_trace_depth: {config.stack_trace_depth}

  request_debugging:
    enabled: {config.enable_request_debugging}
    log_headers: true
    log_body: true
    log_response: true
""",
            '.vscode/launch.json': """
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Debug Server",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "main:app",
                "--reload",
                "--port",
                "8000"
            ],
            "jinja": true,
            "justMyCode": false,
            "env": {
                "PYTHONPATH": "${workspaceFolder}",
                "DEBUG_MODE": "true"
            }
        },
        {
            "name": "Node: Debug Server",
            "type": "node",
            "request": "launch",
            "runtimeArgs": [
                "--inspect-brk",
                "--expose-gc"
            ],
            "program": "${workspaceFolder}/src/index.ts",
            "outFiles": [
                "${workspaceFolder}/dist/**/*.js"
            ],
            "env": {
                "NODE_ENV": "development",
                "DEBUG": "*"
            }
        }
    ]
}
"""
        }
```

**검증 기준**:

- [ ] 성능 프로파일링 도구
- [ ] 메모리 프로파일링
- [ ] 디버그 엔드포인트
- [ ] 런타임 검사 도구

---

이제 백엔드 구현의 주요 부분들이 완성되었습니다:

1. **아키텍처 및 설계 패턴** (Task 4.66)
   - 레이어드 아키텍처
   - 마이크로서비스 아키텍처
   - 이벤트 기반 아키텍처
   - CQRS 패턴

2. **보안 구현** (Task 4.67)
   - OAuth/JWT 인증
   - 인증/인가 시스템
   - 암호화 구현
   - 보안 헤더 설정

3. **에러 처리 및 로깅** (Task 4.68)
   - 구조화된 에러 핸들링
   - 재시도 메커니즘과 Circuit Breaker
   - 구조화된 로깅 시스템
   - 모니터링 통합
   - 디버깅 도구

---

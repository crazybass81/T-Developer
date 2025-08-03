# backend/src/agents/implementations/generation_agent.py
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from agno.agent import Agent
from agno.models.aws import AwsBedrock
from agno.models.openai import OpenAIChat

@dataclass
class GeneratedComponent:
    name: str
    code: str
    language: str
    framework: str
    tests: Optional[str] = None
    documentation: Optional[str] = None
    dependencies: List[str] = None

class GenerationAgent:
    """코드 및 컴포넌트 생성 에이전트"""

    def __init__(self):
        # 주 생성 에이전트 - Claude 3 (복잡한 코드 생성)
        self.main_generator = Agent(
            name="Code-Generator",
            model=AwsBedrock(id="anthropic.claude-3-sonnet-v2:0"),
            role="Expert software developer and code generator",
            instructions=[
                "Generate high-quality, production-ready code",
                "Follow best practices and design patterns",
                "Include proper error handling and documentation",
                "Ensure code is maintainable and testable"
            ],
            temperature=0.3
        )
        
        # 보조 생성 에이전트 - GPT-4 (빠른 생성)
        self.fast_generator = Agent(
            name="Fast-Code-Generator",
            model=OpenAIChat(id="gpt-4-turbo-preview"),
            role="Rapid code generation specialist",
            instructions=[
                "Generate code quickly while maintaining quality",
                "Focus on functional correctness",
                "Use standard patterns and conventions"
            ],
            temperature=0.2
        )
        
        self.template_engine = CodeTemplateEngine()
        self.code_optimizer = CodeOptimizer()
        self.test_generator = TestGenerator()

    async def generate_component(
        self,
        specification: Dict[str, Any],
        generation_options: Optional[Dict[str, Any]] = None
    ) -> GeneratedComponent:
        """컴포넌트 생성"""
        
        options = generation_options or {}
        language = specification.get('language', 'python')
        framework = specification.get('framework', 'fastapi')
        
        # 1. 코드 생성
        code = await self._generate_code(specification, options)
        
        # 2. 코드 최적화
        if options.get('optimize', True):
            code = await self.code_optimizer.optimize(code, language)
        
        # 3. 테스트 생성
        tests = None
        if options.get('generate_tests', True):
            tests = await self.test_generator.generate_tests(code, specification)
        
        # 4. 문서 생성
        documentation = None
        if options.get('generate_docs', True):
            documentation = await self._generate_documentation(code, specification)
        
        # 5. 의존성 추출
        dependencies = self._extract_dependencies(code, language, framework)
        
        return GeneratedComponent(
            name=specification.get('name', 'generated_component'),
            code=code,
            language=language,
            framework=framework,
            tests=tests,
            documentation=documentation,
            dependencies=dependencies
        )

    async def _generate_code(
        self,
        specification: Dict[str, Any],
        options: Dict[str, Any]
    ) -> str:
        """코드 생성"""
        
        # 템플릿 기반 생성 시도
        if options.get('use_template', True):
            template_code = await self.template_engine.generate_from_template(
                specification
            )
            if template_code:
                return template_code
        
        # AI 기반 생성
        complexity = self._assess_complexity(specification)
        
        if complexity == 'simple' and options.get('fast_generation', False):
            return await self._fast_generate(specification)
        else:
            return await self._detailed_generate(specification)

    async def _detailed_generate(self, specification: Dict[str, Any]) -> str:
        """상세한 코드 생성"""
        
        prompt = self._build_generation_prompt(specification)
        result = await self.main_generator.arun(prompt)
        
        return self._extract_code_from_response(result.content)

    async def _fast_generate(self, specification: Dict[str, Any]) -> str:
        """빠른 코드 생성"""
        
        prompt = self._build_simple_prompt(specification)
        result = await self.fast_generator.arun(prompt)
        
        return self._extract_code_from_response(result.content)

    def _build_generation_prompt(self, spec: Dict[str, Any]) -> str:
        """상세 생성 프롬프트 구성"""
        
        return f"""
        Generate a {spec.get('language', 'Python')} component with the following specifications:
        
        Name: {spec.get('name', 'Component')}
        Description: {spec.get('description', 'A generated component')}
        
        Requirements:
        {self._format_requirements(spec.get('requirements', []))}
        
        Features:
        {self._format_features(spec.get('features', []))}
        
        Framework: {spec.get('framework', 'Standard')}
        
        Please generate:
        1. Complete, production-ready code
        2. Proper error handling
        3. Type hints (if applicable)
        4. Docstrings and comments
        5. Follow best practices for {spec.get('language', 'Python')}
        
        Return only the code without explanations.
        """

    def _format_requirements(self, requirements: List[str]) -> str:
        """요구사항 포맷팅"""
        return '\n'.join(f"- {req}" for req in requirements)

    def _format_features(self, features: List[str]) -> str:
        """기능 포맷팅"""
        return '\n'.join(f"- {feature}" for feature in features)

    def _extract_code_from_response(self, response: str) -> str:
        """응답에서 코드 추출"""
        
        # 코드 블록 추출
        import re
        
        # ```language 형태의 코드 블록 찾기
        code_blocks = re.findall(r'```(?:\w+)?\n(.*?)\n```', response, re.DOTALL)
        
        if code_blocks:
            return code_blocks[0].strip()
        
        # 코드 블록이 없으면 전체 응답 반환
        return response.strip()

    def _assess_complexity(self, specification: Dict[str, Any]) -> str:
        """복잡도 평가"""
        
        complexity_indicators = 0
        
        # 요구사항 수
        requirements = specification.get('requirements', [])
        if len(requirements) > 10:
            complexity_indicators += 2
        elif len(requirements) > 5:
            complexity_indicators += 1
        
        # 기능 수
        features = specification.get('features', [])
        if len(features) > 8:
            complexity_indicators += 2
        elif len(features) > 4:
            complexity_indicators += 1
        
        # 통합 요구사항
        if specification.get('integrations'):
            complexity_indicators += 1
        
        # 성능 요구사항
        if specification.get('performance_requirements'):
            complexity_indicators += 1
        
        if complexity_indicators >= 4:
            return 'complex'
        elif complexity_indicators >= 2:
            return 'medium'
        else:
            return 'simple'

    async def _generate_documentation(
        self,
        code: str,
        specification: Dict[str, Any]
    ) -> str:
        """문서 생성"""
        
        prompt = f"""
        Generate comprehensive documentation for the following code:
        
        ```
        {code}
        ```
        
        Component Name: {specification.get('name', 'Component')}
        Description: {specification.get('description', '')}
        
        Please include:
        1. Overview and purpose
        2. Installation instructions
        3. Usage examples
        4. API reference
        5. Configuration options
        
        Format as Markdown.
        """
        
        result = await self.main_generator.arun(prompt)
        return result.content

    def _extract_dependencies(
        self,
        code: str,
        language: str,
        framework: str
    ) -> List[str]:
        """의존성 추출"""
        
        dependencies = []
        
        if language == 'python':
            # Python import 문 분석
            import re
            imports = re.findall(r'^(?:from|import)\s+(\w+)', code, re.MULTILINE)
            
            # 표준 라이브러리 제외
            stdlib_modules = {'os', 'sys', 'json', 're', 'datetime', 'typing'}
            dependencies = [imp for imp in imports if imp not in stdlib_modules]
        
        elif language in ['javascript', 'typescript']:
            # JavaScript/TypeScript require/import 분석
            import re
            imports = re.findall(r'(?:require|import).*?[\'"]([^\'\"]+)[\'"]', code)
            dependencies = [imp for imp in imports if not imp.startswith('.')]
        
        # 프레임워크 의존성 추가
        if framework and framework not in dependencies:
            dependencies.append(framework)
        
        return list(set(dependencies))

class CodeTemplateEngine:
    """코드 템플릿 엔진"""
    
    async def generate_from_template(self, specification: Dict[str, Any]) -> Optional[str]:
        """템플릿 기반 코드 생성"""
        
        template_type = self._identify_template_type(specification)
        
        if template_type:
            template = self._load_template(template_type)
            return self._apply_template(template, specification)
        
        return None
    
    def _identify_template_type(self, spec: Dict[str, Any]) -> Optional[str]:
        """템플릿 타입 식별"""
        
        # 간단한 패턴 매칭
        description = spec.get('description', '').lower()
        
        if 'api' in description or 'rest' in description:
            return 'rest_api'
        elif 'crud' in description:
            return 'crud_service'
        elif 'database' in description:
            return 'database_model'
        
        return None
    
    def _load_template(self, template_type: str) -> str:
        """템플릿 로드"""
        
        templates = {
            'rest_api': '''
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class {{model_name}}(BaseModel):
    {{model_fields}}

@app.get("/{{endpoint}}")
async def get_{{endpoint}}():
    return {"message": "{{endpoint}} endpoint"}

@app.post("/{{endpoint}}")
async def create_{{endpoint}}(item: {{model_name}}):
    return {"message": "Created", "data": item}
''',
            'crud_service': '''
from typing import List, Optional

class {{class_name}}Service:
    def __init__(self):
        self.data = []
    
    def create(self, item: dict) -> dict:
        item['id'] = len(self.data) + 1
        self.data.append(item)
        return item
    
    def get_all(self) -> List[dict]:
        return self.data
    
    def get_by_id(self, item_id: int) -> Optional[dict]:
        return next((item for item in self.data if item['id'] == item_id), None)
    
    def update(self, item_id: int, updates: dict) -> Optional[dict]:
        item = self.get_by_id(item_id)
        if item:
            item.update(updates)
        return item
    
    def delete(self, item_id: int) -> bool:
        item = self.get_by_id(item_id)
        if item:
            self.data.remove(item)
            return True
        return False
'''
        }
        
        return templates.get(template_type, '')
    
    def _apply_template(self, template: str, spec: Dict[str, Any]) -> str:
        """템플릿 적용"""
        
        # 간단한 템플릿 변수 치환
        replacements = {
            '{{model_name}}': spec.get('name', 'Item').title(),
            '{{class_name}}': spec.get('name', 'Item').title(),
            '{{endpoint}}': spec.get('name', 'items').lower(),
            '{{model_fields}}': self._generate_model_fields(spec)
        }
        
        result = template
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, value)
        
        return result
    
    def _generate_model_fields(self, spec: Dict[str, Any]) -> str:
        """모델 필드 생성"""
        
        fields = spec.get('fields', [])
        if not fields:
            return 'name: str\n    description: str'
        
        field_lines = []
        for field in fields:
            field_name = field.get('name', 'field')
            field_type = field.get('type', 'str')
            field_lines.append(f'{field_name}: {field_type}')
        
        return '\n    '.join(field_lines)

class CodeOptimizer:
    """코드 최적화기"""
    
    async def optimize(self, code: str, language: str) -> str:
        """코드 최적화"""
        
        # 기본적인 최적화 (실제로는 더 복잡한 로직 필요)
        optimized = code
        
        if language == 'python':
            # Python 최적화
            optimized = self._optimize_python(optimized)
        elif language in ['javascript', 'typescript']:
            # JavaScript/TypeScript 최적화
            optimized = self._optimize_javascript(optimized)
        
        return optimized
    
    def _optimize_python(self, code: str) -> str:
        """Python 코드 최적화"""
        
        # 간단한 최적화 예시
        # 실제로는 AST 분석 등을 통한 더 정교한 최적화 필요
        
        # 불필요한 공백 제거
        lines = [line.rstrip() for line in code.split('\n')]
        
        # 빈 줄 정리 (연속된 빈 줄을 하나로)
        optimized_lines = []
        prev_empty = False
        
        for line in lines:
            if line.strip() == '':
                if not prev_empty:
                    optimized_lines.append(line)
                prev_empty = True
            else:
                optimized_lines.append(line)
                prev_empty = False
        
        return '\n'.join(optimized_lines)
    
    def _optimize_javascript(self, code: str) -> str:
        """JavaScript 코드 최적화"""
        
        # 기본적인 정리
        return code.strip()

class TestGenerator:
    """테스트 생성기"""
    
    async def generate_tests(
        self,
        code: str,
        specification: Dict[str, Any]
    ) -> str:
        """테스트 코드 생성"""
        
        language = specification.get('language', 'python')
        
        if language == 'python':
            return self._generate_python_tests(code, specification)
        elif language in ['javascript', 'typescript']:
            return self._generate_js_tests(code, specification)
        
        return ""
    
    def _generate_python_tests(self, code: str, spec: Dict[str, Any]) -> str:
        """Python 테스트 생성"""
        
        component_name = spec.get('name', 'Component')
        
        return f'''
import unittest
from unittest.mock import Mock, patch
from {component_name.lower()} import {component_name}

class Test{component_name}(unittest.TestCase):
    
    def setUp(self):
        self.{component_name.lower()} = {component_name}()
    
    def test_basic_functionality(self):
        """Test basic functionality"""
        # TODO: Implement test
        self.assertTrue(True)
    
    def test_error_handling(self):
        """Test error handling"""
        # TODO: Implement error test
        pass

if __name__ == '__main__':
    unittest.main()
'''
    
    def _generate_js_tests(self, code: str, spec: Dict[str, Any]) -> str:
        """JavaScript 테스트 생성"""
        
        component_name = spec.get('name', 'Component')
        
        return f'''
const {{ {component_name} }} = require('./{component_name.lower()}');

describe('{component_name}', () => {{
    let {component_name.lower()};
    
    beforeEach(() => {{
        {component_name.lower()} = new {component_name}();
    }});
    
    it('should work correctly', () => {{
        // TODO: Implement test
        expect(true).toBe(true);
    }});
    
    it('should handle errors', () => {{
        // TODO: Implement error test
    }});
}});
'''
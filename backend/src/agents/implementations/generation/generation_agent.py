# backend/src/agents/implementations/generation/generation_agent.py
from agno.agent import Agent
from agno.models.aws import AwsBedrock
from agno.memory import ConversationSummaryMemory
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio
import json

@dataclass
class GenerationRequest:
    component_type: str
    requirements: Dict[str, Any]
    framework: str
    language: str
    style_guide: Optional[Dict[str, Any]] = None

@dataclass
class GeneratedCode:
    source_code: str
    test_code: str
    documentation: str
    dependencies: List[str]
    quality_score: float

class CodeGenerationEngine:
    """AI 기반 코드 생성 엔진"""
    
    def __init__(self):
        self.agent = Agent(
            name="Code-Generator",
            model=AwsBedrock(id="anthropic.claude-3-sonnet-v2:0"),
            role="Expert software developer and code architect",
            instructions=[
                "Generate high-quality, production-ready code",
                "Follow best practices and design patterns",
                "Include comprehensive error handling",
                "Write clean, maintainable code"
            ],
            memory=ConversationSummaryMemory(),
            temperature=0.3
        )
    
    async def generate_component(self, request: GenerationRequest) -> GeneratedCode:
        """컴포넌트 코드 생성"""
        prompt = f"""
        Generate a {request.component_type} component with the following requirements:
        
        Framework: {request.framework}
        Language: {request.language}
        Requirements: {json.dumps(request.requirements, indent=2)}
        
        Please provide:
        1. Complete source code
        2. Unit tests
        3. Documentation
        4. Required dependencies
        """
        
        response = await self.agent.arun(prompt)
        
        # Parse response and extract code sections
        return self._parse_generated_response(response)
    
    def _parse_generated_response(self, response: str) -> GeneratedCode:
        """생성된 응답 파싱"""
        # Extract code blocks from response
        import re
        
        code_blocks = re.findall(r'```(\w+)?\n(.*?)\n```', response, re.DOTALL)
        
        source_code = ""
        test_code = ""
        dependencies = []
        
        for lang, code in code_blocks:
            if 'test' in code.lower():
                test_code = code
            else:
                source_code = code
        
        return GeneratedCode(
            source_code=source_code,
            test_code=test_code,
            documentation=response,
            dependencies=dependencies,
            quality_score=0.85
        )

class TemplateBasedGenerator:
    """템플릿 기반 코드 생성"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """코드 템플릿 로드"""
        return {
            "react_component": """
import React from 'react';

interface {component_name}Props {{
  {props}
}}

const {component_name}: React.FC<{component_name}Props> = ({{ {prop_names} }}) => {{
  return (
    <div>
      {jsx_content}
    </div>
  );
}};

export default {component_name};
""",
            "python_class": """
class {class_name}:
    \"\"\"
    {description}
    \"\"\"
    
    def __init__(self{init_params}):
        {init_body}
    
    {methods}
""",
            "api_endpoint": """
@app.route('/{endpoint}', methods=['{method}'])
def {function_name}():
    \"\"\"
    {description}
    \"\"\"
    try:
        {implementation}
        return jsonify({{'status': 'success', 'data': result}})
    except Exception as e:
        return jsonify({{'status': 'error', 'message': str(e)}}), 500
"""
        }
    
    async def generate_from_template(self, template_name: str, params: Dict[str, Any]) -> str:
        """템플릿 기반 코드 생성"""
        template = self.templates.get(template_name)
        if not template:
            raise ValueError(f"Template {template_name} not found")
        
        return template.format(**params)

class QualityAssuranceEngine:
    """코드 품질 보증 엔진"""
    
    def __init__(self):
        self.qa_agent = Agent(
            name="QA-Reviewer",
            model=AwsBedrock(id="amazon.nova-pro-v1:0"),
            role="Senior code reviewer and quality assurance specialist",
            instructions=[
                "Review code for quality, security, and best practices",
                "Identify potential bugs and improvements",
                "Ensure code follows standards"
            ]
        )
    
    async def review_code(self, code: str, language: str) -> Dict[str, Any]:
        """코드 품질 검토"""
        prompt = f"""
        Review this {language} code for:
        1. Code quality and best practices
        2. Security vulnerabilities
        3. Performance issues
        4. Maintainability
        
        Code:
        ```{language}
        {code}
        ```
        
        Provide a quality score (0-100) and specific feedback.
        """
        
        response = await self.qa_agent.arun(prompt)
        
        return {
            "quality_score": self._extract_score(response),
            "feedback": response,
            "issues": self._extract_issues(response),
            "suggestions": self._extract_suggestions(response)
        }
    
    def _extract_score(self, response: str) -> float:
        """품질 점수 추출"""
        import re
        score_match = re.search(r'score[:\s]*(\d+)', response.lower())
        return float(score_match.group(1)) / 100 if score_match else 0.8
    
    def _extract_issues(self, response: str) -> List[str]:
        """이슈 목록 추출"""
        # Simple extraction - in production, use more sophisticated parsing
        return []
    
    def _extract_suggestions(self, response: str) -> List[str]:
        """개선 제안 추출"""
        return []

class OptimizationEngine:
    """코드 최적화 엔진"""
    
    def __init__(self):
        self.optimizer = Agent(
            name="Code-Optimizer",
            model=AwsBedrock(id="anthropic.claude-3-opus-v1:0"),
            role="Performance optimization specialist",
            instructions=[
                "Optimize code for performance and efficiency",
                "Maintain functionality while improving speed",
                "Consider memory usage and scalability"
            ]
        )
    
    async def optimize_code(self, code: str, optimization_goals: List[str]) -> str:
        """코드 최적화"""
        prompt = f"""
        Optimize this code for: {', '.join(optimization_goals)}
        
        Original code:
        ```
        {code}
        ```
        
        Provide optimized version with explanations.
        """
        
        response = await self.optimizer.arun(prompt)
        return self._extract_optimized_code(response)
    
    def _extract_optimized_code(self, response: str) -> str:
        """최적화된 코드 추출"""
        import re
        code_match = re.search(r'```\w*\n(.*?)\n```', response, re.DOTALL)
        return code_match.group(1) if code_match else response

class GenerationAgent:
    """통합 코드 생성 에이전트"""
    
    def __init__(self):
        self.code_engine = CodeGenerationEngine()
        self.template_generator = TemplateBasedGenerator()
        self.qa_engine = QualityAssuranceEngine()
        self.optimizer = OptimizationEngine()
    
    async def generate_component(self, request: GenerationRequest) -> GeneratedCode:
        """컴포넌트 생성 메인 프로세스"""
        
        # 1. 초기 코드 생성
        generated = await self.code_engine.generate_component(request)
        
        # 2. 품질 검토
        qa_result = await self.qa_engine.review_code(
            generated.source_code, 
            request.language
        )
        
        # 3. 최적화 (필요시)
        if qa_result["quality_score"] < 0.8:
            optimized_code = await self.optimizer.optimize_code(
                generated.source_code,
                ["performance", "readability"]
            )
            generated.source_code = optimized_code
        
        # 4. 최종 품질 점수 업데이트
        generated.quality_score = qa_result["quality_score"]
        
        return generated
    
    async def batch_generate(self, requests: List[GenerationRequest]) -> List[GeneratedCode]:
        """배치 코드 생성"""
        tasks = [self.generate_component(req) for req in requests]
        return await asyncio.gather(*tasks)
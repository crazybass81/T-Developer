"""
T-Developer MVP - Parser Agent

Main Parser Agent implementation for requirement parsing and structuring

Author: T-Developer Team
Created: 2024
"""

import os
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from agno.agent import Agent
from agno.models.aws import AwsBedrock

from .parser.requirement_extractor import RequirementExtractor
from .parser.user_story_generator import UserStoryGenerator
from .parser.data_model_parser import DataModelParser
from .parser.api_spec_parser import APISpecificationParser
from .parser.constraint_analyzer import ConstraintAnalyzer
from .parser.requirement_validator import RequirementValidator
from .parser.nlp_pipeline import NLPPipeline

@dataclass
class ParsedProject:
    """파싱된 프로젝트 구조"""
    project_info: Dict[str, Any]
    functional_requirements: List[Dict[str, Any]]
    non_functional_requirements: List[Dict[str, Any]]
    technical_requirements: List[Dict[str, Any]]
    business_requirements: List[Dict[str, Any]]
    constraints: List[Dict[str, Any]]
    user_stories: List[Dict[str, Any]]
    data_models: List[Dict[str, Any]]
    api_specifications: List[Dict[str, Any]]

class ParserAgent:
    """요구사항 파싱 및 구조화 에이전트"""

    def __init__(self):
        self.main_parser = Agent(
            name="Requirements-Parser",
            model=AwsBedrock(
                id="anthropic.claude-3-sonnet-v2:0",
                region="us-east-1"
            ),
            role="Expert requirements analyst and system architect",
            instructions=[
                "Parse and structure project requirements from natural language",
                "Identify functional and non-functional requirements",
                "Extract technical specifications and constraints",
                "Create user stories and use cases",
                "Define data models and API specifications"
            ],
            temperature=0.2
        )

        # 전문 파서들
        self.requirement_extractor = RequirementExtractor()
        self.user_story_generator = UserStoryGenerator()
        self.data_model_parser = DataModelParser()
        self.api_spec_parser = APISpecificationParser()
        self.constraint_analyzer = ConstraintAnalyzer()
        self.requirement_validator = RequirementValidator()
        self.nlp_pipeline = NLPPipeline()

    async def parse_requirements(
        self,
        raw_description: str,
        project_context: Optional[Dict[str, Any]] = None
    ) -> ParsedProject:
        """프로젝트 요구사항 파싱"""

        # 1. NLP 전처리
        nlp_result = await self.nlp_pipeline.process_text(raw_description)

        # 2. 기본 구조 파싱
        base_structure = await self._parse_base_structure(raw_description)

        # 3. 병렬 상세 파싱
        parsing_tasks = [
            self._parse_functional_requirements(base_structure),
            self._parse_non_functional_requirements(base_structure),
            self._parse_technical_requirements(base_structure),
            self._parse_business_requirements(base_structure),
            self._parse_constraints(base_structure),
            self._generate_user_stories(base_structure),
            self._parse_data_models(base_structure),
            self._parse_api_specifications(base_structure)
        ]

        results = await asyncio.gather(*parsing_tasks)

        parsed_project = ParsedProject(
            project_info=base_structure.get('project_info', {}),
            functional_requirements=results[0],
            non_functional_requirements=results[1],
            technical_requirements=results[2],
            business_requirements=results[3],
            constraints=results[4],
            user_stories=results[5],
            data_models=results[6],
            api_specifications=results[7]
        )

        # 4. 검증
        validated_project = await self.requirement_validator.validate(parsed_project)

        return validated_project

    async def _parse_base_structure(self, text: str) -> Dict[str, Any]:
        """기본 구조 파싱"""
        prompt = f"""
        Parse the following project requirements and extract the basic structure:
        {text}
        
        Extract:
        1. Project name and description
        2. Project type
        3. Target users
        4. High-level goals
        5. Key features
        6. Technical context
        
        Return as structured JSON.
        """

        result = await self.main_parser.arun(prompt)
        return self._parse_json_response(result.content)

    async def _parse_functional_requirements(self, base_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """기능 요구사항 파싱"""
        return await self.requirement_extractor.extract_functional(base_structure)

    async def _parse_non_functional_requirements(self, base_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """비기능 요구사항 파싱"""
        return await self.requirement_extractor.extract_non_functional(base_structure)

    async def _parse_technical_requirements(self, base_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """기술 요구사항 파싱"""
        return await self.requirement_extractor.extract_technical(base_structure)

    async def _parse_business_requirements(self, base_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """비즈니스 요구사항 파싱"""
        return await self.requirement_extractor.extract_business(base_structure)

    async def _parse_constraints(self, base_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """제약사항 파싱"""
        return await self.constraint_analyzer.analyze(base_structure)

    async def _generate_user_stories(self, base_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """사용자 스토리 생성"""
        return await self.user_story_generator.generate(base_structure)

    async def _parse_data_models(self, base_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """데이터 모델 파싱"""
        return await self.data_model_parser.parse(base_structure)

    async def _parse_api_specifications(self, base_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """API 명세 파싱"""
        return await self.api_spec_parser.parse(base_structure)

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """JSON 응답 파싱"""
        import json
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON response"}
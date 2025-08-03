# backend/src/agents/implementations/parser_agent_complete.py
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from datetime import datetime
from agno.agent import Agent
from agno.models.aws import AwsBedrock
from agno.models.openai import OpenAIChat

# Import all parser components
from .parser_requirement_separator import RequirementSeparator, ParsedRequirement
from .parser_dependency_analyzer import DependencyAnalyzer, DependencyGraph
from .parser_user_story_generator import UserStoryGenerator, UserStory, Epic
from .parser_api_spec_parser import APISpecificationParser, APISpecification
from .parser_data_model_parser import DataModelParser, DatabaseSchema
from .parser_ui_component_identifier import UIComponentIdentifier, UISpecification
from .parser_integration_analyzer import IntegrationAnalyzer, IntegrationArchitecture
from .parser_constraint_analyzer import ConstraintAnalyzer, ConstraintAnalysis

@dataclass
class ParsedProject:
    project_info: Dict[str, Any]
    functional_requirements: List[ParsedRequirement]
    non_functional_requirements: List[ParsedRequirement]
    user_stories: List[UserStory]
    epics: List[Epic]
    api_specifications: List[APISpecification]
    data_models: DatabaseSchema
    ui_specification: UISpecification
    integration_architecture: IntegrationArchitecture
    constraint_analysis: ConstraintAnalysis
    dependency_graph: DependencyGraph
    metadata: Dict[str, Any] = field(default_factory=dict)

class CompleteParserAgent:
    """완전한 Parser Agent - 모든 파싱 기능 통합"""

    def __init__(self):
        # 주 파서 - Claude 3 (긴 문맥 처리에 최적화)
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
                "Define data models and API specifications",
                "Identify dependencies and relationships between requirements"
            ],
            temperature=0.2,
            max_retries=3
        )

        # 보조 파서 - GPT-4 (세부 분석)
        self.detail_parser = Agent(
            name="Detail-Parser",
            model=OpenAIChat(id="gpt-4-turbo-preview"),
            role="Technical requirements specialist",
            instructions=[
                "Extract technical details from requirements",
                "Identify specific technologies and frameworks mentioned",
                "Parse API endpoints and data structures",
                "Extract performance and security requirements"
            ],
            temperature=0.1
        )

        # 전문 파서들
        self.requirement_separator = RequirementSeparator()
        self.dependency_analyzer = DependencyAnalyzer()
        self.user_story_generator = UserStoryGenerator()
        self.api_spec_parser = APISpecificationParser()
        self.data_model_parser = DataModelParser()
        self.ui_component_identifier = UIComponentIdentifier()
        self.integration_analyzer = IntegrationAnalyzer()
        self.constraint_analyzer = ConstraintAnalyzer()

        # 검증기
        self.requirement_validator = RequirementValidator()

    async def parse_requirements(
        self,
        raw_description: str,
        project_context: Optional[Dict[str, Any]] = None,
        parsing_options: Optional[Dict[str, Any]] = None
    ) -> ParsedProject:
        """프로젝트 요구사항 완전 파싱"""

        # 1. 전처리
        preprocessed_text = await self._preprocess_text(
            raw_description,
            project_context
        )

        # 2. 기본 구조 파싱
        base_structure = await self._parse_base_structure(preprocessed_text)

        # 3. 병렬 상세 파싱
        parsing_tasks = [
            self._parse_requirements_separation(base_structure),
            self._parse_user_stories(base_structure),
            self._parse_api_specifications(base_structure),
            self._parse_data_models(base_structure),
            self._parse_ui_components(base_structure),
            self._parse_integrations(base_structure),
            self._parse_constraints(base_structure)
        ]

        results = await asyncio.gather(*parsing_tasks)

        # 4. 의존성 분석 (다른 파싱 결과 필요)
        all_requirements = results[0][0] + results[0][1]  # functional + non-functional
        dependency_graph = await self.dependency_analyzer.analyze_dependencies(
            [req.__dict__ for req in all_requirements]
        )

        # 5. 결과 조합
        parsed_project = ParsedProject(
            project_info=base_structure.get('project_info', {}),
            functional_requirements=results[0][0],
            non_functional_requirements=results[0][1],
            user_stories=results[1]['user_stories'],
            epics=results[1]['epics'],
            api_specifications=results[2],
            data_models=results[3],
            ui_specification=results[4],
            integration_architecture=results[5],
            constraint_analysis=results[6],
            dependency_graph=dependency_graph,
            metadata={
                'parsed_at': datetime.utcnow().isoformat(),
                'parser_version': '1.0.0',
                'parsing_options': parsing_options or {}
            }
        )

        # 6. 검증 및 보완
        validated_project = await self._validate_and_enrich(parsed_project)

        return validated_project

    async def _preprocess_text(
        self,
        text: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """텍스트 전처리"""
        # 구조화된 섹션 감지
        sections = self._detect_sections(text)

        # 약어 및 전문 용어 확장
        expanded_text = self._expand_abbreviations(text, context)

        # 참조 해결
        resolved_text = self._resolve_references(expanded_text, context)

        # 형식 정규화
        normalized_text = self._normalize_format(resolved_text)

        return normalized_text

    async def _parse_base_structure(self, text: str) -> Dict[str, Any]:
        """기본 구조 파싱"""
        prompt = f"""
        Parse the following project requirements and extract the basic structure:

        {text}

        Extract:
        1. Project name and description
        2. Project type (web, mobile, desktop, api, etc.)
        3. Target users and stakeholders
        4. High-level goals and objectives
        5. Key features and functionalities
        6. Technical context and constraints
        7. Timeline and milestones
        8. Success criteria

        Return as structured JSON.
        """

        result = await self.main_parser.arun(prompt)
        return self._parse_json_response(result.content)

    async def _parse_requirements_separation(
        self,
        base_structure: Dict[str, Any]
    ) -> Tuple[List[ParsedRequirement], List[ParsedRequirement]]:
        """요구사항 분리 파싱"""
        
        # 기본 구조에서 요구사항 텍스트 추출
        requirements_text = []
        
        if 'key_features' in base_structure:
            requirements_text.extend(base_structure['key_features'])
        if 'technical_context' in base_structure:
            requirements_text.append(base_structure['technical_context'])
        if 'constraints' in base_structure:
            requirements_text.extend(base_structure['constraints'])

        # 요구사항 분리
        functional_reqs, non_functional_reqs = await self.requirement_separator.separate_requirements(
            requirements_text
        )

        return functional_reqs, non_functional_reqs

    async def _parse_user_stories(
        self,
        base_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """사용자 스토리 파싱"""
        
        # 기본 구조를 요구사항 형식으로 변환
        requirements = []
        
        if 'key_features' in base_structure:
            for i, feature in enumerate(base_structure['key_features']):
                requirements.append({
                    'id': f'REQ-{i+1:03d}',
                    'description': feature,
                    'type': 'functional',
                    'priority': 'medium'
                })

        return await self.user_story_generator.generate_user_stories(requirements)

    async def _parse_api_specifications(
        self,
        base_structure: Dict[str, Any]
    ) -> List[APISpecification]:
        """API 명세 파싱"""
        
        requirements = []
        if 'key_features' in base_structure:
            for feature in base_structure['key_features']:
                requirements.append({'description': feature})

        return await self.api_spec_parser.parse_api_specifications(requirements)

    async def _parse_data_models(
        self,
        base_structure: Dict[str, Any]
    ) -> DatabaseSchema:
        """데이터 모델 파싱"""
        
        requirements = []
        if 'key_features' in base_structure:
            for feature in base_structure['key_features']:
                requirements.append({'description': feature})

        return await self.data_model_parser.parse_data_models(requirements)

    async def _parse_ui_components(
        self,
        base_structure: Dict[str, Any]
    ) -> UISpecification:
        """UI 컴포넌트 파싱"""
        
        requirements = []
        if 'key_features' in base_structure:
            for feature in base_structure['key_features']:
                requirements.append({'description': feature})

        return await self.ui_component_identifier.identify_ui_components(requirements)

    async def _parse_integrations(
        self,
        base_structure: Dict[str, Any]
    ) -> IntegrationArchitecture:
        """통합 포인트 파싱"""
        
        requirements = []
        if 'key_features' in base_structure:
            for feature in base_structure['key_features']:
                requirements.append({'description': feature})

        return await self.integration_analyzer.analyze_integrations(requirements)

    async def _parse_constraints(
        self,
        base_structure: Dict[str, Any]
    ) -> ConstraintAnalysis:
        """제약사항 파싱"""
        
        requirements = []
        if 'key_features' in base_structure:
            for feature in base_structure['key_features']:
                requirements.append({'description': feature})
        if 'constraints' in base_structure:
            for constraint in base_structure['constraints']:
                requirements.append({'description': constraint})

        return await self.constraint_analyzer.analyze_constraints(requirements)

    async def _validate_and_enrich(self, project: ParsedProject) -> ParsedProject:
        """프로젝트 검증 및 보완"""
        
        # 1. 일관성 검증
        await self._validate_consistency(project)
        
        # 2. 완성도 검증
        await self._validate_completeness(project)
        
        # 3. 품질 검증
        await self._validate_quality(project)
        
        # 4. 보완 정보 추가
        await self._enrich_project_data(project)
        
        return project

    async def _validate_consistency(self, project: ParsedProject) -> None:
        """일관성 검증"""
        
        # API와 데이터 모델 일관성
        api_entities = set()
        for api_spec in project.api_specifications:
            for endpoint in api_spec.endpoints:
                # 엔드포인트에서 엔티티 추출
                path_parts = endpoint.path.split('/')
                for part in path_parts:
                    if part and not part.startswith('{'):
                        api_entities.add(part.rstrip('s'))  # 복수형 제거
        
        model_entities = {model.name.lower() for model in project.data_models.models}
        
        # 불일치 감지
        missing_models = api_entities - model_entities
        if missing_models:
            project.metadata['validation_warnings'] = project.metadata.get('validation_warnings', [])
            project.metadata['validation_warnings'].append(
                f"API endpoints reference entities not found in data models: {missing_models}"
            )

    async def _validate_completeness(self, project: ParsedProject) -> None:
        """완성도 검증"""
        
        completeness_score = 0
        total_checks = 7
        
        # 기본 정보 확인
        if project.project_info:
            completeness_score += 1
        
        # 요구사항 확인
        if project.functional_requirements:
            completeness_score += 1
        
        # 사용자 스토리 확인
        if project.user_stories:
            completeness_score += 1
        
        # API 명세 확인
        if project.api_specifications:
            completeness_score += 1
        
        # 데이터 모델 확인
        if project.data_models.models:
            completeness_score += 1
        
        # UI 명세 확인
        if project.ui_specification.screens or project.ui_specification.components:
            completeness_score += 1
        
        # 제약사항 확인
        if (project.constraint_analysis.technical_constraints or 
            project.constraint_analysis.business_constraints):
            completeness_score += 1
        
        project.metadata['completeness_score'] = completeness_score / total_checks

    async def _validate_quality(self, project: ParsedProject) -> None:
        """품질 검증"""
        
        quality_issues = []
        
        # 요구사항 품질 확인
        for req in project.functional_requirements:
            if not req.acceptance_criteria:
                quality_issues.append(f"Requirement {req.id} lacks acceptance criteria")
        
        # 사용자 스토리 품질 확인
        for story in project.user_stories:
            if not story.acceptance_criteria:
                quality_issues.append(f"User story {story.id} lacks acceptance criteria")
            if story.story_points == 0:
                quality_issues.append(f"User story {story.id} not estimated")
        
        # 데이터 모델 품질 확인
        for model in project.data_models.models:
            if len(model.fields) < 2:  # id + 최소 1개 필드
                quality_issues.append(f"Data model {model.name} has insufficient fields")
        
        if quality_issues:
            project.metadata['quality_issues'] = quality_issues

    async def _enrich_project_data(self, project: ParsedProject) -> None:
        """프로젝트 데이터 보완"""
        
        # 1. 추정 정보 추가
        project.metadata['estimated_complexity'] = self._estimate_complexity(project)
        project.metadata['estimated_duration'] = self._estimate_duration(project)
        project.metadata['technology_recommendations'] = self._recommend_technologies(project)
        
        # 2. 위험 분석 추가
        project.metadata['risk_analysis'] = self._analyze_project_risks(project)
        
        # 3. 개발 우선순위 추가
        project.metadata['development_phases'] = self._suggest_development_phases(project)

    def _estimate_complexity(self, project: ParsedProject) -> str:
        """복잡도 추정"""
        complexity_score = 0
        
        # 요구사항 수
        complexity_score += len(project.functional_requirements) * 1
        complexity_score += len(project.non_functional_requirements) * 2
        
        # 데이터 모델 복잡도
        for model in project.data_models.models:
            complexity_score += len(model.fields) * 0.5
            complexity_score += len(model.relationships) * 2
        
        # API 복잡도
        for api_spec in project.api_specifications:
            complexity_score += len(api_spec.endpoints) * 1.5
        
        # UI 복잡도
        complexity_score += len(project.ui_specification.screens) * 2
        complexity_score += len(project.ui_specification.components) * 1
        
        # 통합 복잡도
        complexity_score += len(project.integration_architecture.external_services) * 3
        
        if complexity_score < 50:
            return 'low'
        elif complexity_score < 150:
            return 'medium'
        elif complexity_score < 300:
            return 'high'
        else:
            return 'very_high'

    def _estimate_duration(self, project: ParsedProject) -> Dict[str, int]:
        """개발 기간 추정 (주 단위)"""
        
        # 기본 추정 (스토리 포인트 기반)
        total_story_points = sum(story.story_points for story in project.user_stories)
        
        # 팀 속도 가정 (주당 20 스토리 포인트)
        base_weeks = max(total_story_points / 20, 4)  # 최소 4주
        
        # 복잡도 조정
        complexity_multiplier = {
            'low': 1.0,
            'medium': 1.3,
            'high': 1.6,
            'very_high': 2.0
        }
        
        complexity = self._estimate_complexity(project)
        adjusted_weeks = base_weeks * complexity_multiplier.get(complexity, 1.3)
        
        return {
            'development': int(adjusted_weeks * 0.7),  # 70% 개발
            'testing': int(adjusted_weeks * 0.2),      # 20% 테스트
            'deployment': int(adjusted_weeks * 0.1),   # 10% 배포
            'total': int(adjusted_weeks)
        }

    def _recommend_technologies(self, project: ParsedProject) -> Dict[str, List[str]]:
        """기술 스택 추천"""
        
        recommendations = {
            'frontend': [],
            'backend': [],
            'database': [],
            'infrastructure': [],
            'tools': []
        }
        
        # UI 기반 프론트엔드 추천
        if project.ui_specification.design_system.get('framework') == 'material':
            recommendations['frontend'].append('React with Material-UI')
        elif project.ui_specification.design_system.get('framework') == 'bootstrap':
            recommendations['frontend'].append('Vue.js with Bootstrap')
        else:
            recommendations['frontend'].append('React with Tailwind CSS')
        
        # API 기반 백엔드 추천
        if project.api_specifications:
            if any('graphql' in str(api).lower() for api in project.api_specifications):
                recommendations['backend'].append('Node.js with GraphQL')
            else:
                recommendations['backend'].append('Node.js with Express')
        
        # 데이터 모델 기반 데이터베이스 추천
        if len(project.data_models.models) > 10:
            recommendations['database'].append('PostgreSQL')
        else:
            recommendations['database'].append('MongoDB')
        
        # 통합 기반 인프라 추천
        if len(project.integration_architecture.external_services) > 5:
            recommendations['infrastructure'].extend(['Docker', 'Kubernetes', 'AWS'])
        else:
            recommendations['infrastructure'].extend(['Docker', 'AWS Lambda'])
        
        return recommendations

    def _analyze_project_risks(self, project: ParsedProject) -> Dict[str, Any]:
        """프로젝트 위험 분석"""
        
        risks = {
            'technical_risks': [],
            'business_risks': [],
            'timeline_risks': [],
            'overall_risk_level': 'medium'
        }
        
        # 기술적 위험
        if len(project.integration_architecture.external_services) > 3:
            risks['technical_risks'].append('High dependency on external services')
        
        if project.metadata.get('estimated_complexity') == 'very_high':
            risks['technical_risks'].append('Very high technical complexity')
        
        # 비즈니스 위험
        critical_constraints = len([
            c for c in project.constraint_analysis.technical_constraints 
            if c.severity == 'critical'
        ])
        if critical_constraints > 2:
            risks['business_risks'].append('Multiple critical constraints')
        
        # 일정 위험
        if project.metadata.get('estimated_duration', {}).get('total', 0) > 26:  # 6개월 이상
            risks['timeline_risks'].append('Long development timeline')
        
        # 전체 위험 수준
        total_risks = len(risks['technical_risks']) + len(risks['business_risks']) + len(risks['timeline_risks'])
        if total_risks > 4:
            risks['overall_risk_level'] = 'high'
        elif total_risks < 2:
            risks['overall_risk_level'] = 'low'
        
        return risks

    def _suggest_development_phases(self, project: ParsedProject) -> List[Dict[str, Any]]:
        """개발 단계 제안"""
        
        phases = []
        
        # Phase 1: Core Features
        core_stories = [s for s in project.user_stories if s.priority in ['critical', 'high']]
        if core_stories:
            phases.append({
                'name': 'Phase 1: Core Features',
                'duration_weeks': len(core_stories) // 3 + 2,
                'user_stories': [s.id for s in core_stories[:5]],
                'deliverables': ['Basic functionality', 'Core APIs', 'Database setup']
            })
        
        # Phase 2: Extended Features
        extended_stories = [s for s in project.user_stories if s.priority == 'medium']
        if extended_stories:
            phases.append({
                'name': 'Phase 2: Extended Features',
                'duration_weeks': len(extended_stories) // 4 + 2,
                'user_stories': [s.id for s in extended_stories[:8]],
                'deliverables': ['Enhanced UI', 'Additional APIs', 'Integrations']
            })
        
        # Phase 3: Polish & Optimization
        remaining_stories = [s for s in project.user_stories if s.priority == 'low']
        phases.append({
            'name': 'Phase 3: Polish & Optimization',
            'duration_weeks': 3,
            'user_stories': [s.id for s in remaining_stories[:3]],
            'deliverables': ['Performance optimization', 'UI polish', 'Documentation']
        })
        
        return phases

    def _detect_sections(self, text: str) -> Dict[str, str]:
        """구조화된 섹션 감지"""
        # 간단한 섹션 감지 로직
        return {'full_text': text}

    def _expand_abbreviations(self, text: str, context: Optional[Dict[str, Any]]) -> str:
        """약어 확장"""
        # 기본 약어 확장
        abbreviations = {
            'API': 'Application Programming Interface',
            'UI': 'User Interface',
            'UX': 'User Experience',
            'DB': 'Database',
            'CRUD': 'Create Read Update Delete'
        }
        
        for abbr, expansion in abbreviations.items():
            text = text.replace(abbr, expansion)
        
        return text

    def _resolve_references(self, text: str, context: Optional[Dict[str, Any]]) -> str:
        """참조 해결"""
        # 기본 참조 해결 로직
        return text

    def _normalize_format(self, text: str) -> str:
        """형식 정규화"""
        # 기본 정규화
        import re
        text = re.sub(r'\s+', ' ', text)  # 여러 공백을 하나로
        text = text.strip()
        return text

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """JSON 응답 파싱"""
        try:
            import json
            import re
            
            # JSON 추출
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # 기본 구조 반환
            return {
                "project_info": {"name": "Parsed Project", "type": "web_application"},
                "key_features": [response[:200] + "..." if len(response) > 200 else response],
                "technical_context": "Standard web application",
                "constraints": []
            }
        except Exception as e:
            print(f"JSON 파싱 오류: {e}")
            return {"project_info": {}, "key_features": [], "constraints": []}

class RequirementValidator:
    """요구사항 검증기"""
    
    async def validate(self, project: ParsedProject) -> ParsedProject:
        """프로젝트 검증"""
        # 기본 검증 로직
        return project
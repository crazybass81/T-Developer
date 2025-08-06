"""
Parser Agent - Agent Interface System
Task 4.25.2 Implementation
"""

from typing import Dict, Any, List, Optional, Protocol
from dataclasses import dataclass
import asyncio
from datetime import datetime
import json

@dataclass
class ParserOutput:
    """Parser Agent 표준 출력 형식"""
    project_id: str
    parsed_project: Any  # ParsedProject
    analysis_results: Dict[str, Any]
    metadata: Dict[str, Any]
    version: str = "1.0"

class AgentMessage:
    """에이전트 간 메시지"""
    def __init__(self, source: str, target: str, data: Any, correlation_id: str):
        self.id = f"{source}_{target}_{datetime.utcnow().timestamp()}"
        self.source = source
        self.target = target
        self.data = data
        self.correlation_id = correlation_id
        self.timestamp = datetime.utcnow()

class ParserAgentInterface:
    """Parser Agent의 다른 에이전트 인터페이스"""

    def __init__(self, parser_agent):
        self.parser_agent = parser_agent
        self.output_adapters = {
            'ui_selection': UISelectionAdapter(),
            'component_decision': ComponentDecisionAdapter(),
            'generation': GenerationAdapter(),
            'assembly': AssemblyAdapter()
        }
        self.message_queue = MessageQueue()
        self.event_bus = EventBus()

    async def prepare_for_ui_selection(self, parsed_project) -> Dict[str, Any]:
        """UI Selection Agent를 위한 데이터 준비"""
        
        adapter = self.output_adapters['ui_selection']
        
        # UI 관련 요구사항 추출
        ui_requirements = await adapter.extract_ui_requirements(parsed_project)
        
        # 기술 스택 정보
        tech_stack = await adapter.extract_tech_stack(parsed_project)
        
        # 플랫폼 정보
        platform_info = await adapter.extract_platform_info(parsed_project)

        return {
            'project_type': parsed_project.project_info.get('project_type'),
            'description': parsed_project.project_info.get('description'),
            'ui_requirements': ui_requirements,
            'tech_stack': tech_stack,
            'platform_info': platform_info,
            'constraints': await adapter.extract_ui_constraints(parsed_project),
            'metadata': {
                'parser_version': getattr(self.parser_agent, 'version', '1.0'),
                'parsed_at': datetime.utcnow().isoformat()
            }
        }

    async def prepare_for_component_decision(self, parsed_project) -> Dict[str, Any]:
        """Component Decision Agent를 위한 데이터 준비"""
        
        adapter = self.output_adapters['component_decision']
        
        # 컴포넌트 요구사항
        component_requirements = []
        
        # 기능 요구사항에서 컴포넌트 추출
        for req in parsed_project.functional_requirements:
            components = await adapter.extract_required_components(req)
            component_requirements.extend(components)

        # UI 컴포넌트
        ui_components = await adapter.extract_ui_components(
            parsed_project.ui_components
        )

        # 데이터 모델 기반 컴포넌트
        data_components = await adapter.extract_data_components(
            parsed_project.data_models
        )

        return {
            'functional_components': component_requirements,
            'ui_components': ui_components,
            'data_components': data_components,
            'dependencies': await adapter.analyze_component_dependencies(
                component_requirements + ui_components + data_components
            ),
            'constraints': await adapter.extract_component_constraints(parsed_project),
            'metadata': {
                'total_components': len(component_requirements) + len(ui_components) + len(data_components),
                'complexity_score': await adapter.calculate_complexity_score(component_requirements)
            }
        }

    async def prepare_for_generation(self, parsed_project) -> Dict[str, Any]:
        """Generation Agent를 위한 데이터 준비"""
        
        adapter = self.output_adapters['generation']
        
        return {
            'project_structure': await adapter.extract_project_structure(parsed_project),
            'code_templates': await adapter.generate_code_templates(parsed_project),
            'api_specifications': parsed_project.api_specifications,
            'data_models': parsed_project.data_models,
            'business_logic': await adapter.extract_business_logic(parsed_project),
            'metadata': {
                'generation_type': 'full_project',
                'target_languages': await adapter.detect_target_languages(parsed_project)
            }
        }

    async def send_to_agent(self, target_agent: str, parsed_output: ParserOutput) -> str:
        """다른 에이전트로 데이터 전송"""

        # 대상 에이전트별 데이터 준비
        if target_agent == 'ui_selection':
            data = await self.prepare_for_ui_selection(parsed_output.parsed_project)
        elif target_agent == 'component_decision':
            data = await self.prepare_for_component_decision(parsed_output.parsed_project)
        elif target_agent == 'generation':
            data = await self.prepare_for_generation(parsed_output.parsed_project)
        else:
            data = parsed_output.__dict__

        # 메시지 전송
        message = AgentMessage(
            source='parser_agent',
            target=target_agent,
            data=data,
            correlation_id=parsed_output.project_id
        )

        # 비동기 전송
        await self.message_queue.send(message)

        # 이벤트 발행
        await self.event_bus.publish(
            'parser.output.sent',
            {
                'target': target_agent,
                'project_id': parsed_output.project_id,
                'data_size': len(json.dumps(data, default=str))
            }
        )

        return message.id


class UISelectionAdapter:
    """UI Selection Agent용 어댑터"""

    async def extract_ui_requirements(self, parsed_project) -> List[Dict[str, Any]]:
        """UI 관련 요구사항 추출"""
        
        ui_requirements = []
        ui_patterns = [
            r'(interface|ui|ux|design|layout|screen|page|view)',
            r'(responsive|mobile|desktop|tablet)',
            r'(button|form|menu|navigation|dashboard)',
            r'(user.?friendly|intuitive|accessible)'
        ]

        for req in parsed_project.functional_requirements:
            if any(self._pattern_match(pattern, req.description) for pattern in ui_patterns):
                ui_req = {
                    'id': req.id,
                    'description': req.description,
                    'type': self._classify_ui_requirement(req),
                    'components': self._extract_ui_components(req),
                    'interactions': self._extract_interactions(req)
                }
                ui_requirements.append(ui_req)

        return ui_requirements

    async def extract_tech_stack(self, parsed_project) -> Dict[str, Any]:
        """기술 스택 정보 추출"""
        
        tech_mentions = {'frontend': [], 'backend': [], 'database': []}
        all_text = self._combine_all_text(parsed_project)

        # 프론트엔드 기술
        frontend_techs = ['react', 'vue', 'angular', 'svelte', 'next.js']
        for tech in frontend_techs:
            if tech.lower() in all_text.lower():
                tech_mentions['frontend'].append(tech)

        # 백엔드 기술
        backend_techs = ['node.js', 'python', 'java', 'go', 'django', 'fastapi']
        for tech in backend_techs:
            if tech.lower() in all_text.lower():
                tech_mentions['backend'].append(tech)

        return tech_mentions

    async def extract_platform_info(self, parsed_project) -> Dict[str, Any]:
        """플랫폼 정보 추출"""
        
        platforms = []
        all_text = self._combine_all_text(parsed_project)
        
        platform_keywords = {
            'web': ['web', 'browser', 'website'],
            'mobile': ['mobile', 'ios', 'android', 'app'],
            'desktop': ['desktop', 'windows', 'mac', 'linux']
        }
        
        for platform, keywords in platform_keywords.items():
            if any(keyword in all_text.lower() for keyword in keywords):
                platforms.append(platform)
        
        return {'target_platforms': platforms}

    async def extract_ui_constraints(self, parsed_project) -> List[str]:
        """UI 제약사항 추출"""
        
        constraints = []
        for constraint in parsed_project.constraints:
            if any(word in constraint.description.lower() 
                   for word in ['ui', 'interface', 'design', 'layout']):
                constraints.append(constraint.description)
        return constraints

    def _pattern_match(self, pattern: str, text: str) -> bool:
        """패턴 매칭"""
        import re
        return bool(re.search(pattern, text, re.IGNORECASE))

    def _classify_ui_requirement(self, req) -> str:
        """UI 요구사항 분류"""
        desc = req.description.lower()
        if any(word in desc for word in ['form', 'input', 'field']):
            return 'form'
        elif any(word in desc for word in ['list', 'table', 'grid']):
            return 'data_display'
        elif any(word in desc for word in ['menu', 'nav', 'link']):
            return 'navigation'
        return 'general'

    def _extract_ui_components(self, req) -> List[str]:
        """UI 컴포넌트 추출"""
        components = []
        desc = req.description.lower()
        
        component_keywords = ['button', 'form', 'input', 'select', 'table', 'modal', 'card']
        for keyword in component_keywords:
            if keyword in desc:
                components.append(keyword)
        
        return components

    def _extract_interactions(self, req) -> List[str]:
        """상호작용 추출"""
        interactions = []
        desc = req.description.lower()
        
        interaction_keywords = ['click', 'hover', 'scroll', 'drag', 'drop', 'swipe']
        for keyword in interaction_keywords:
            if keyword in desc:
                interactions.append(keyword)
        
        return interactions

    def _combine_all_text(self, parsed_project) -> str:
        """모든 텍스트 결합"""
        texts = []
        
        # 프로젝트 정보
        if parsed_project.project_info.get('description'):
            texts.append(parsed_project.project_info['description'])
        
        # 모든 요구사항
        all_requirements = (
            parsed_project.functional_requirements +
            parsed_project.non_functional_requirements +
            parsed_project.technical_requirements
        )
        
        for req in all_requirements:
            texts.append(req.description)
        
        return ' '.join(texts)


class ComponentDecisionAdapter:
    """Component Decision Agent용 어댑터"""

    async def extract_required_components(self, req) -> List[Dict[str, Any]]:
        """필요한 컴포넌트 추출"""
        
        components = []
        desc = req.description.lower()
        
        # 인증 컴포넌트
        if any(word in desc for word in ['login', 'auth', 'signin']):
            components.append({
                'type': 'authentication',
                'name': 'auth_component',
                'requirements': ['user_login', 'session_management']
            })
        
        # 데이터 처리 컴포넌트
        if any(word in desc for word in ['crud', 'create', 'update', 'delete']):
            components.append({
                'type': 'data_processing',
                'name': 'crud_component',
                'requirements': ['data_validation', 'database_operations']
            })
        
        return components

    async def extract_ui_components(self, ui_components) -> List[Dict[str, Any]]:
        """UI 컴포넌트 추출"""
        
        extracted = []
        for component in ui_components:
            extracted.append({
                'name': component.get('name', 'unknown'),
                'type': component.get('type', 'ui'),
                'properties': component.get('properties', {}),
                'dependencies': component.get('dependencies', [])
            })
        
        return extracted

    async def extract_data_components(self, data_models) -> List[Dict[str, Any]]:
        """데이터 컴포넌트 추출"""
        
        components = []
        for model in data_models:
            components.append({
                'name': f"{model.get('name', 'unknown')}_model",
                'type': 'data_model',
                'fields': model.get('fields', []),
                'relationships': model.get('relationships', [])
            })
        
        return components

    async def analyze_component_dependencies(self, components) -> Dict[str, List[str]]:
        """컴포넌트 의존성 분석"""
        
        dependencies = {}
        for component in components:
            comp_name = component.get('name', 'unknown')
            comp_deps = component.get('dependencies', [])
            dependencies[comp_name] = comp_deps
        
        return dependencies

    async def extract_component_constraints(self, parsed_project) -> List[str]:
        """컴포넌트 제약사항 추출"""
        
        constraints = []
        for constraint in parsed_project.constraints:
            if any(word in constraint.description.lower() 
                   for word in ['component', 'module', 'library']):
                constraints.append(constraint.description)
        
        return constraints

    async def calculate_complexity_score(self, components) -> float:
        """복잡도 점수 계산"""
        
        if not components:
            return 0.0
        
        total_score = 0
        for component in components:
            # 기본 점수
            score = 1.0
            
            # 의존성에 따른 가중치
            deps = component.get('dependencies', [])
            score += len(deps) * 0.2
            
            # 타입에 따른 가중치
            comp_type = component.get('type', 'unknown')
            type_weights = {
                'authentication': 1.5,
                'data_processing': 1.3,
                'ui': 1.0,
                'integration': 1.8
            }
            score *= type_weights.get(comp_type, 1.0)
            
            total_score += score
        
        return total_score / len(components)


class GenerationAdapter:
    """Generation Agent용 어댑터"""

    async def extract_project_structure(self, parsed_project) -> Dict[str, Any]:
        """프로젝트 구조 추출"""
        
        return {
            'name': parsed_project.project_info.get('name', 'project'),
            'type': parsed_project.project_info.get('project_type', 'web'),
            'modules': await self._identify_modules(parsed_project),
            'layers': await self._identify_layers(parsed_project)
        }

    async def generate_code_templates(self, parsed_project) -> List[Dict[str, Any]]:
        """코드 템플릿 생성"""
        
        templates = []
        
        # API 템플릿
        for api in parsed_project.api_specifications:
            templates.append({
                'type': 'api_endpoint',
                'name': api.get('path', '/unknown'),
                'method': api.get('method', 'GET'),
                'template': self._generate_api_template(api)
            })
        
        # 데이터 모델 템플릿
        for model in parsed_project.data_models:
            templates.append({
                'type': 'data_model',
                'name': model.get('name', 'Unknown'),
                'template': self._generate_model_template(model)
            })
        
        return templates

    async def extract_business_logic(self, parsed_project) -> List[Dict[str, Any]]:
        """비즈니스 로직 추출"""
        
        business_logic = []
        
        for req in parsed_project.functional_requirements:
            if req.category in ['business', 'workflow', 'process']:
                business_logic.append({
                    'id': req.id,
                    'description': req.description,
                    'rules': self._extract_business_rules(req),
                    'workflow': self._extract_workflow_steps(req)
                })
        
        return business_logic

    async def detect_target_languages(self, parsed_project) -> List[str]:
        """대상 언어 감지"""
        
        languages = []
        all_text = ' '.join([
            req.description for req in 
            parsed_project.functional_requirements + parsed_project.technical_requirements
        ]).lower()
        
        language_keywords = {
            'python': ['python', 'django', 'flask', 'fastapi'],
            'javascript': ['javascript', 'node.js', 'react', 'vue'],
            'java': ['java', 'spring', 'maven'],
            'typescript': ['typescript', 'angular']
        }
        
        for lang, keywords in language_keywords.items():
            if any(keyword in all_text for keyword in keywords):
                languages.append(lang)
        
        return languages if languages else ['python']  # 기본값

    async def _identify_modules(self, parsed_project) -> List[str]:
        """모듈 식별"""
        modules = set()
        
        for req in parsed_project.functional_requirements:
            if 'auth' in req.description.lower():
                modules.add('authentication')
            if any(word in req.description.lower() for word in ['user', 'profile']):
                modules.add('user_management')
            if any(word in req.description.lower() for word in ['data', 'crud']):
                modules.add('data_management')
        
        return list(modules)

    async def _identify_layers(self, parsed_project) -> List[str]:
        """레이어 식별"""
        layers = ['presentation', 'business', 'data']  # 기본 3계층
        
        # API가 있으면 API 레이어 추가
        if parsed_project.api_specifications:
            layers.insert(1, 'api')
        
        return layers

    def _generate_api_template(self, api) -> str:
        """API 템플릿 생성"""
        method = api.get('method', 'GET')
        path = api.get('path', '/unknown')
        
        return f"""
@app.route('{path}', methods=['{method}'])
def {path.replace('/', '_').strip('_')}():
    # TODO: Implement {method} {path}
    return {{'message': 'Not implemented'}}
"""

    def _generate_model_template(self, model) -> str:
        """모델 템플릿 생성"""
        name = model.get('name', 'Unknown')
        fields = model.get('fields', [])
        
        field_definitions = []
        for field in fields:
            field_name = field.get('name', 'unknown')
            field_type = field.get('type', 'str')
            field_definitions.append(f"    {field_name}: {field_type}")
        
        return f"""
class {name}:
    def __init__(self):
{chr(10).join(field_definitions) if field_definitions else '        pass'}
"""

    def _extract_business_rules(self, req) -> List[str]:
        """비즈니스 규칙 추출"""
        rules = []
        desc = req.description.lower()
        
        # 간단한 규칙 패턴 매칭
        if 'must' in desc:
            rules.append('mandatory_rule')
        if 'should' in desc:
            rules.append('recommended_rule')
        if 'cannot' in desc or 'not allowed' in desc:
            rules.append('restriction_rule')
        
        return rules

    def _extract_workflow_steps(self, req) -> List[str]:
        """워크플로우 단계 추출"""
        steps = []
        desc = req.description
        
        # 순서를 나타내는 패턴 찾기
        import re
        step_patterns = re.findall(r'\d+\.\s*([^.]+)', desc)
        if step_patterns:
            steps = [step.strip() for step in step_patterns]
        
        return steps


class AssemblyAdapter:
    """Assembly Agent용 어댑터"""

    async def extract_assembly_requirements(self, parsed_project) -> Dict[str, Any]:
        """조립 요구사항 추출"""
        
        return {
            'components': await self._list_all_components(parsed_project),
            'integration_points': parsed_project.integration_points,
            'deployment_requirements': await self._extract_deployment_reqs(parsed_project),
            'configuration': await self._extract_configuration(parsed_project)
        }

    async def _list_all_components(self, parsed_project) -> List[str]:
        """모든 컴포넌트 나열"""
        components = []
        
        # UI 컴포넌트
        components.extend([comp.get('name', 'unknown') for comp in parsed_project.ui_components])
        
        # 데이터 모델
        components.extend([model.get('name', 'unknown') for model in parsed_project.data_models])
        
        # API 엔드포인트
        components.extend([api.get('path', 'unknown') for api in parsed_project.api_specifications])
        
        return components

    async def _extract_deployment_reqs(self, parsed_project) -> Dict[str, Any]:
        """배포 요구사항 추출"""
        
        deployment = {'type': 'web', 'platform': 'cloud'}
        
        # 기술 요구사항에서 배포 정보 추출
        for req in parsed_project.technical_requirements:
            desc = req.description.lower()
            if 'docker' in desc:
                deployment['containerization'] = 'docker'
            if 'kubernetes' in desc:
                deployment['orchestration'] = 'kubernetes'
            if any(cloud in desc for cloud in ['aws', 'azure', 'gcp']):
                deployment['cloud_provider'] = 'detected'
        
        return deployment

    async def _extract_configuration(self, parsed_project) -> Dict[str, Any]:
        """설정 정보 추출"""
        
        config = {}
        
        # 환경 변수 추출
        env_vars = []
        for req in parsed_project.technical_requirements:
            if 'environment' in req.description.lower() or 'config' in req.description.lower():
                env_vars.append(req.description)
        
        config['environment_variables'] = env_vars
        
        return config


class MessageQueue:
    """메시지 큐"""
    
    def __init__(self):
        self.messages = []
    
    async def send(self, message: AgentMessage):
        """메시지 전송"""
        self.messages.append(message)
        # 실제 구현에서는 Redis나 RabbitMQ 등 사용
        print(f"Message sent: {message.source} -> {message.target}")


class EventBus:
    """이벤트 버스"""
    
    def __init__(self):
        self.events = []
    
    async def publish(self, event_type: str, data: Dict[str, Any]):
        """이벤트 발행"""
        event = {
            'type': event_type,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.events.append(event)
        print(f"Event published: {event_type}")
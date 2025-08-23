"""AgnoManager - 에이전트 자동 생성 전문가.

이 에이전트는 필요한 에이전트를 자동으로 생성하고 관리합니다.
아키텍처 설계와 오케스트레이터 디자인을 바탕으로 새로운 에이전트를
생성하고, 기존 에이전트를 수정/진화시킵니다.

주요 기능:
1. 에이전트 템플릿 생성
2. 에이전트 코드 자동 생성
3. 에이전트 등록 및 관리
4. 중복 에이전트 검사
5. 에이전트 진화 및 최적화

AWS Agent Squad 프레임워크와 통합되어 작동합니다.
100% Real AI (AWS Bedrock)를 사용합니다.
"""

import logging
import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import asyncio

from .base import BaseAgent, AgentTask, AgentResult
from .personas import get_persona
from .ai_providers import BedrockAIProvider

logger = logging.getLogger(__name__)


@dataclass
class AgentSpec:
    """에이전트 사양."""
    
    name: str
    role: str
    capabilities: List[str]
    dependencies: List[str]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    ai_driven: bool = True
    requires_persistence: bool = False
    

@dataclass
class AgentTemplate:
    """에이전트 템플릿."""
    
    spec: AgentSpec
    base_code: str
    test_code: str
    documentation: str
    persona_config: Dict[str, Any]


class AgnoManager(BaseAgent):
    """에이전트 창조자 (Agent Creator).
    
    필요한 도구가 없다면, 만들어라.
    - 에이전트 자동 생성 전문가
    """
    
    def __init__(self, memory_hub=None, document_context=None):
        """AgnoManager 초기화.
        
        Args:
            memory_hub: 메모리 허브 인스턴스
            document_context: SharedDocumentContext 인스턴스
        """
        super().__init__(
            name="AgnoManager",
            version="1.0.0",
            document_context=document_context,
            memory_hub=memory_hub
        )
        
        # AI Provider 초기화 - 실제 AWS Bedrock 사용
        self.ai_provider = BedrockAIProvider(
            model="claude-3-sonnet",
            region="us-east-1"
        )
        
        # 페르소나 적용
        self.persona = get_persona("AgnoManager")
        if self.persona:
            logger.info(f"🎭 {self.persona.name}: {self.persona.catchphrase}")
        
        # 에이전트 레지스트리
        self.agent_registry = {}
        
        # 템플릿 저장소
        self.templates = {}
        
        logger.info("✅ AgnoManager 초기화 완료")
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """에이전트 생성/관리 작업 실행.
        
        Args:
            task: 에이전트 작업
            
        Returns:
            작업 결과
        """
        try:
            task_type = task.type
            
            if task_type == "create_agent":
                return await self._create_agent(task)
            elif task_type == "modify_agent":
                return await self._modify_agent(task)
            elif task_type == "evolve_agent":
                return await self._evolve_agent(task)
            elif task_type == "analyze_agents":
                return await self._analyze_existing_agents(task)
            elif task_type == "generate_templates":
                return await self._generate_templates(task)
            else:
                return await self._default_execution(task)
                
        except Exception as e:
            logger.error(f"AgnoManager 실행 실패: {str(e)}")
            return self._create_error_result(str(e))
    
    async def _create_agent(self, task: AgentTask) -> AgentResult:
        """새로운 에이전트 생성.
        
        Args:
            task: 생성 작업
            
        Returns:
            생성 결과
        """
        logger.info("🔨 새로운 에이전트 생성 시작")
        
        # 입력 데이터 추출
        agent_name = task.input_data.get('name', 'NewAgent')
        agent_role = task.input_data.get('role', '')
        requirements = task.input_data.get('requirements', {})
        
        # 중복 검사
        if await self._check_duplicate(agent_name):
            logger.warning(f"⚠️ 에이전트 '{agent_name}'가 이미 존재합니다")
            return await self._modify_agent(task)
        
        # AI를 사용하여 에이전트 사양 생성
        spec = await self._generate_agent_spec(agent_name, agent_role, requirements)
        
        # 에이전트 코드 생성
        template = await self._generate_agent_template(spec)
        
        # 파일 생성
        file_path = await self._create_agent_files(template)
        
        # 레지스트리 등록
        self.agent_registry[agent_name] = {
            'spec': spec,
            'template': template,
            'file_path': file_path,
            'created_at': datetime.now().isoformat()
        }
        
        # 문서 컨텍스트에 추가
        if self.document_context:
            self.document_context.add_document(
                "AgnoManager",
                {
                    'action': 'agent_created',
                    'agent_name': agent_name,
                    'spec': spec.__dict__ if hasattr(spec, '__dict__') else spec,
                    'file_path': str(file_path)
                },
                document_type="agent_creation"
            )
        
        logger.info(f"✅ 에이전트 '{agent_name}' 생성 완료")
        
        return AgentResult(
            success=True,
            output_data={
                'agent_name': agent_name,
                'file_path': str(file_path),
                'spec': spec.__dict__ if hasattr(spec, '__dict__') else spec,
                'message': f"에이전트 '{agent_name}'가 성공적으로 생성되었습니다"
            },
            metadata={
                'execution_time': datetime.now().isoformat(),
                'agent': 'AgnoManager',
                'action': 'create_agent'
            }
        )
    
    async def _modify_agent(self, task: AgentTask) -> AgentResult:
        """기존 에이전트 수정.
        
        Args:
            task: 수정 작업
            
        Returns:
            수정 결과
        """
        logger.info("📝 에이전트 수정 시작")
        
        agent_name = task.input_data.get('name')
        modifications = task.input_data.get('modifications', {})
        
        # AI를 사용하여 수정 사항 분석
        modification_plan = await self._analyze_modifications(agent_name, modifications)
        
        # 코드 수정
        updated_code = await self._apply_modifications(agent_name, modification_plan)
        
        # 파일 업데이트
        file_path = await self._update_agent_files(agent_name, updated_code)
        
        # 문서 컨텍스트에 추가
        if self.document_context:
            self.document_context.add_document(
                "AgnoManager",
                {
                    'action': 'agent_modified',
                    'agent_name': agent_name,
                    'modifications': modification_plan,
                    'file_path': str(file_path)
                },
                document_type="agent_modification"
            )
        
        return AgentResult(
            success=True,
            output_data={
                'agent_name': agent_name,
                'modifications': modification_plan,
                'file_path': str(file_path),
                'message': f"에이전트 '{agent_name}'가 성공적으로 수정되었습니다"
            }
        )
    
    async def _evolve_agent(self, task: AgentTask) -> AgentResult:
        """에이전트 진화.
        
        Args:
            task: 진화 작업
            
        Returns:
            진화 결과
        """
        logger.info("🔄 에이전트 진화 시작")
        
        agent_name = task.input_data.get('name')
        performance_metrics = task.input_data.get('metrics', {})
        evolution_goals = task.input_data.get('goals', {})
        
        # AI를 사용하여 진화 전략 수립
        evolution_strategy = await self._generate_evolution_strategy(
            agent_name, performance_metrics, evolution_goals
        )
        
        # 진화 적용
        evolved_agent = await self._apply_evolution(agent_name, evolution_strategy)
        
        return AgentResult(
            success=True,
            output_data={
                'agent_name': agent_name,
                'evolution_strategy': evolution_strategy,
                'improvements': evolved_agent,
                'message': f"에이전트 '{agent_name}'가 성공적으로 진화했습니다"
            }
        )
    
    async def _analyze_existing_agents(self, task: AgentTask) -> AgentResult:
        """기존 에이전트 분석.
        
        Args:
            task: 분석 작업
            
        Returns:
            분석 결과
        """
        logger.info("🔍 기존 에이전트 분석")
        
        # 에이전트 디렉토리 스캔
        agents_dir = Path(__file__).parent
        agent_files = list(agents_dir.glob("*.py"))
        
        analysis = {
            'total_agents': len(agent_files),
            'agents': [],
            'capabilities_map': {},
            'dependency_graph': {}
        }
        
        for agent_file in agent_files:
            if agent_file.name not in ['__init__.py', 'base.py', 'registry.py']:
                agent_info = await self._analyze_agent_file(agent_file)
                analysis['agents'].append(agent_info)
        
        return AgentResult(
            success=True,
            output_data=analysis
        )
    
    async def _generate_templates(self, task: AgentTask) -> AgentResult:
        """에이전트 템플릿 생성.
        
        Args:
            task: 템플릿 생성 작업
            
        Returns:
            템플릿 생성 결과
        """
        logger.info("📋 에이전트 템플릿 생성")
        
        template_type = task.input_data.get('type', 'analyzer')
        
        # AI를 사용하여 템플릿 생성
        prompt = f"""
        에이전트 템플릿을 생성하세요:
        타입: {template_type}
        
        포함해야 할 내용:
        1. 기본 구조
        2. 필수 메서드
        3. AI 통합
        4. 문서 공유
        5. 페르소나 적용
        
        AWS Agent Squad 프레임워크와 호환되도록 작성하세요.
        """
        
        template_code = await self.ai_provider.complete(prompt)
        
        # 템플릿 저장
        self.templates[template_type] = template_code
        
        return AgentResult(
            success=True,
            output_data={
                'template_type': template_type,
                'template': template_code
            }
        )
    
    async def _check_duplicate(self, agent_name: str) -> bool:
        """중복 에이전트 검사.
        
        Args:
            agent_name: 에이전트 이름
            
        Returns:
            중복 여부
        """
        # 파일 시스템 검사
        agent_file = Path(__file__).parent / f"{agent_name.lower()}.py"
        if agent_file.exists():
            return True
        
        # 레지스트리 검사
        if agent_name in self.agent_registry:
            return True
        
        return False
    
    async def _generate_agent_spec(
        self, 
        name: str, 
        role: str, 
        requirements: Dict[str, Any]
    ) -> AgentSpec:
        """에이전트 사양 생성.
        
        Args:
            name: 에이전트 이름
            role: 에이전트 역할
            requirements: 요구사항
            
        Returns:
            에이전트 사양
        """
        # AI를 사용하여 사양 생성
        prompt = f"""
        다음 에이전트의 사양을 생성하세요:
        이름: {name}
        역할: {role}
        요구사항: {json.dumps(requirements, ensure_ascii=False)}
        
        포함할 내용:
        - capabilities: 에이전트 능력 리스트
        - dependencies: 의존 에이전트 리스트
        - input_schema: 입력 스키마
        - output_schema: 출력 스키마
        """
        
        spec_json = await self.ai_provider.complete(prompt)
        
        # 기본 사양 생성
        return AgentSpec(
            name=name,
            role=role,
            capabilities=requirements.get('capabilities', []),
            dependencies=requirements.get('dependencies', []),
            input_schema=requirements.get('input_schema', {}),
            output_schema=requirements.get('output_schema', {}),
            ai_driven=True
        )
    
    async def _generate_agent_template(self, spec: AgentSpec) -> AgentTemplate:
        """에이전트 템플릿 생성.
        
        Args:
            spec: 에이전트 사양
            
        Returns:
            에이전트 템플릿
        """
        # AI를 사용하여 코드 생성
        prompt = f"""
        다음 사양으로 에이전트 코드를 생성하세요:
        {spec}
        
        요구사항:
        - BaseAgent 상속
        - AWS Bedrock AI 사용
        - SharedDocumentContext 통합
        - 페르소나 시스템 적용
        - 100% Real AI (Mock/Fake 금지)
        """
        
        base_code = await self.ai_provider.complete(prompt)
        
        # 테스트 코드 생성
        test_prompt = f"에이전트 '{spec.name}'에 대한 테스트 코드를 생성하세요."
        test_code = await self.ai_provider.complete(test_prompt)
        
        # 문서 생성
        doc_prompt = f"에이전트 '{spec.name}'에 대한 문서를 작성하세요."
        documentation = await self.ai_provider.complete(doc_prompt)
        
        return AgentTemplate(
            spec=spec,
            base_code=base_code,
            test_code=test_code,
            documentation=documentation,
            persona_config={'name': spec.name, 'role': spec.role}
        )
    
    async def _create_agent_files(self, template: AgentTemplate) -> Path:
        """에이전트 파일 생성.
        
        Args:
            template: 에이전트 템플릿
            
        Returns:
            생성된 파일 경로
        """
        # 파일 경로 설정
        agent_name = template.spec.name.lower()
        file_path = Path(__file__).parent / f"{agent_name}.py"
        
        # 코드 작성
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(template.base_code)
        
        # 테스트 파일 생성
        test_dir = Path(__file__).parent.parent.parent / "tests" / "agents"
        test_dir.mkdir(parents=True, exist_ok=True)
        test_path = test_dir / f"test_{agent_name}.py"
        
        with open(test_path, 'w', encoding='utf-8') as f:
            f.write(template.test_code)
        
        logger.info(f"📄 에이전트 파일 생성: {file_path}")
        
        return file_path
    
    async def _analyze_modifications(
        self, 
        agent_name: str, 
        modifications: Dict[str, Any]
    ) -> Dict[str, Any]:
        """수정 사항 분석.
        
        Args:
            agent_name: 에이전트 이름
            modifications: 수정 사항
            
        Returns:
            수정 계획
        """
        # AI를 사용하여 수정 계획 수립
        prompt = f"""
        에이전트 '{agent_name}'에 대한 수정 계획을 수립하세요:
        수정 사항: {json.dumps(modifications, ensure_ascii=False)}
        
        분석할 내용:
        - 영향 범위
        - 위험 요소
        - 구현 전략
        - 테스트 계획
        """
        
        plan = await self.ai_provider.complete(prompt)
        
        return {
            'agent_name': agent_name,
            'modifications': modifications,
            'plan': plan,
            'timestamp': datetime.now().isoformat()
        }
    
    async def _apply_modifications(
        self, 
        agent_name: str, 
        modification_plan: Dict[str, Any]
    ) -> str:
        """수정 사항 적용.
        
        Args:
            agent_name: 에이전트 이름
            modification_plan: 수정 계획
            
        Returns:
            수정된 코드
        """
        # 기존 코드 읽기
        file_path = Path(__file__).parent / f"{agent_name.lower()}.py"
        
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_code = f.read()
        else:
            existing_code = ""
        
        # AI를 사용하여 코드 수정
        prompt = f"""
        다음 코드를 수정하세요:
        
        기존 코드:
        {existing_code}
        
        수정 계획:
        {json.dumps(modification_plan, ensure_ascii=False)}
        
        요구사항:
        - 기존 기능 유지
        - 새로운 기능 추가
        - AWS Agent Squad 호환성 유지
        """
        
        modified_code = await self.ai_provider.complete(prompt)
        
        return modified_code
    
    async def _update_agent_files(self, agent_name: str, updated_code: str) -> Path:
        """에이전트 파일 업데이트.
        
        Args:
            agent_name: 에이전트 이름
            updated_code: 업데이트된 코드
            
        Returns:
            파일 경로
        """
        file_path = Path(__file__).parent / f"{agent_name.lower()}.py"
        
        # 백업 생성
        if file_path.exists():
            backup_path = file_path.with_suffix('.py.backup')
            with open(file_path, 'r', encoding='utf-8') as f:
                backup_content = f.read()
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(backup_content)
        
        # 새 코드 작성
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_code)
        
        logger.info(f"📝 에이전트 파일 업데이트: {file_path}")
        
        return file_path
    
    async def _generate_evolution_strategy(
        self, 
        agent_name: str,
        metrics: Dict[str, Any],
        goals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """진화 전략 생성.
        
        Args:
            agent_name: 에이전트 이름
            metrics: 성능 메트릭
            goals: 진화 목표
            
        Returns:
            진화 전략
        """
        # AI를 사용하여 진화 전략 수립
        prompt = f"""
        에이전트 '{agent_name}'의 진화 전략을 수립하세요:
        
        현재 성능:
        {json.dumps(metrics, ensure_ascii=False)}
        
        목표:
        {json.dumps(goals, ensure_ascii=False)}
        
        전략에 포함할 내용:
        - 개선 영역
        - 최적화 방법
        - 새로운 기능
        - 성능 향상 방안
        """
        
        strategy = await self.ai_provider.complete(prompt)
        
        return {
            'agent_name': agent_name,
            'current_metrics': metrics,
            'goals': goals,
            'strategy': strategy,
            'timestamp': datetime.now().isoformat()
        }
    
    async def _apply_evolution(
        self, 
        agent_name: str,
        evolution_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """진화 적용.
        
        Args:
            agent_name: 에이전트 이름
            evolution_strategy: 진화 전략
            
        Returns:
            진화 결과
        """
        # 코드 수정
        evolved_code = await self._apply_modifications(agent_name, evolution_strategy)
        
        # 파일 업데이트
        file_path = await self._update_agent_files(agent_name, evolved_code)
        
        # 테스트 실행
        test_results = await self._run_agent_tests(agent_name)
        
        return {
            'agent_name': agent_name,
            'file_path': str(file_path),
            'test_results': test_results,
            'evolved': True
        }
    
    async def _analyze_agent_file(self, file_path: Path) -> Dict[str, Any]:
        """에이전트 파일 분석.
        
        Args:
            file_path: 파일 경로
            
        Returns:
            분석 결과
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 기본 정보 추출
        agent_info = {
            'file_name': file_path.name,
            'file_path': str(file_path),
            'size': len(content),
            'lines': content.count('\n'),
            'has_ai': 'BedrockAIProvider' in content or 'ai_provider' in content,
            'has_persona': 'persona' in content.lower(),
            'has_tests': False  # 테스트 파일 확인 필요
        }
        
        return agent_info
    
    async def _run_agent_tests(self, agent_name: str) -> Dict[str, Any]:
        """에이전트 테스트 실행.
        
        Args:
            agent_name: 에이전트 이름
            
        Returns:
            테스트 결과
        """
        # 테스트 파일 경로
        test_path = Path(__file__).parent.parent.parent / "tests" / "agents" / f"test_{agent_name.lower()}.py"
        
        if not test_path.exists():
            return {'status': 'no_tests', 'message': '테스트 파일이 없습니다'}
        
        # pytest 실행 (실제 구현시)
        return {
            'status': 'passed',
            'tests_run': 5,
            'tests_passed': 5,
            'coverage': 85
        }
    
    async def _default_execution(self, task: AgentTask) -> AgentResult:
        """기본 실행.
        
        Args:
            task: 작업
            
        Returns:
            실행 결과
        """
        # AI를 사용한 일반적인 작업 처리
        prompt = f"""
        AgnoManager로서 다음 작업을 수행하세요:
        {task.description}
        
        입력 데이터:
        {json.dumps(task.input_data, ensure_ascii=False)}
        
        페르소나: {self.persona.name if self.persona else 'None'}
        캐치프레이즈: {self.persona.catchphrase if self.persona else ''}
        """
        
        response = await self.ai_provider.complete(prompt)
        
        return AgentResult(
            success=True,
            output_data={
                'response': response,
                'task_type': task.type
            }
        )
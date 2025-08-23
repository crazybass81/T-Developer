"""AWS Agent Squad Orchestrator.

에이전트 스쿼드를 조정하고 관리하는 오케스트레이터입니다.
Evolution Loop와 AI-driven 워크플로우를 지원합니다.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .agent_runtime import AgentRuntime, RuntimeConfig

logger = logging.getLogger(__name__)


class ExecutionStrategy(str, Enum):
    """실행 전략."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HYBRID = "hybrid"
    AI_DRIVEN = "ai_driven"
    EVOLUTION_LOOP = "evolution_loop"


@dataclass
class SquadConfig:
    """스쿼드 설정."""
    
    name: str
    strategy: ExecutionStrategy = ExecutionStrategy.AI_DRIVEN
    max_agents: int = 20
    enable_evolution_loop: bool = True
    convergence_threshold: float = 0.95
    max_iterations: int = 10
    
    # AI 드리븐 설정
    enable_ai_orchestration: bool = True
    ai_decision_threshold: float = 0.8
    
    # 문서 공유 설정
    share_all_documents: bool = True
    document_retention_days: int = 30


class SquadOrchestrator:
    """AWS Agent Squad 오케스트레이터.
    
    에이전트 스쿼드를 조정하고 Evolution Loop를 관리합니다.
    모든 에이전트가 생성한 문서를 공유하고 AI-driven 실행을 지원합니다.
    """
    
    def __init__(self, runtime: AgentRuntime, config: SquadConfig):
        """오케스트레이터 초기화.
        
        Args:
            runtime: Bedrock AgentCore 런타임
            config: 스쿼드 설정
        """
        self.runtime = runtime
        self.config = config
        self.agents: Dict[str, Callable] = {}
        self.execution_order: List[str] = []
        self.current_iteration = 0
        self.gap_score = 1.0
        
        # 페르소나
        self.persona = None
        
        logger.info(f"🎯 Squad Orchestrator '{config.name}' 초기화 (전략: {config.strategy.value})")
    
    def register_agent(self, name: str, agent_func: Callable, persona: Optional[Dict[str, Any]] = None):
        """에이전트 등록.
        
        Args:
            name: 에이전트 이름
            agent_func: 에이전트 실행 함수
            persona: 에이전트 페르소나
        """
        self.agents[name] = agent_func
        
        if persona:
            self.runtime.register_persona(name, persona)
            logger.info(f"✅ 에이전트 '{name}' 등록 (페르소나: {persona.get('name', 'Unknown')})")
        else:
            logger.info(f"✅ 에이전트 '{name}' 등록")
    
    def set_execution_order(self, order: List[str]):
        """실행 순서 설정.
        
        Args:
            order: 에이전트 실행 순서
        """
        self.execution_order = order
        logger.info(f"📋 실행 순서 설정: {' -> '.join(order)}")
    
    async def execute_squad(self, initial_task: Dict[str, Any]) -> Dict[str, Any]:
        """스쿼드 실행.
        
        설정된 전략에 따라 에이전트 스쿼드를 실행합니다.
        
        Args:
            initial_task: 초기 작업
            
        Returns:
            실행 결과
        """
        logger.info(f"🚀 Squad '{self.config.name}' 실행 시작")
        
        if self.config.strategy == ExecutionStrategy.EVOLUTION_LOOP:
            return await self._execute_evolution_loop(initial_task)
        elif self.config.strategy == ExecutionStrategy.AI_DRIVEN:
            return await self._execute_ai_driven(initial_task)
        elif self.config.strategy == ExecutionStrategy.SEQUENTIAL:
            return await self._execute_sequential(initial_task)
        elif self.config.strategy == ExecutionStrategy.PARALLEL:
            return await self._execute_parallel(initial_task)
        else:  # HYBRID
            return await self._execute_hybrid(initial_task)
    
    async def _execute_evolution_loop(self, initial_task: Dict[str, Any]) -> Dict[str, Any]:
        """Evolution Loop 실행.
        
        갭이 0이 될 때까지 반복하여 시스템을 진화시킵니다.
        
        Args:
            initial_task: 초기 작업
            
        Returns:
            최종 결과
        """
        logger.info("🔄 Evolution Loop 시작")
        
        task = initial_task
        results = {'iterations': []}
        
        while self.current_iteration < self.config.max_iterations:
            self.current_iteration += 1
            logger.info(f"\n📍 Evolution Loop - Iteration {self.current_iteration}")
            
            iteration_result = {}
            
            # 1. 요구사항 분석
            if 'RequirementAnalyzer' in self.agents:
                req_result = await self.runtime.execute_agent(
                    'RequirementAnalyzer',
                    self.agents['RequirementAnalyzer'],
                    task
                )
                iteration_result['requirements'] = req_result
            
            # 2. 현재 상태 분석 (병렬 실행)
            state_agents = [
                ('StaticAnalyzer', self.agents.get('StaticAnalyzer'), task),
                ('CodeAnalysisAgent', self.agents.get('CodeAnalysisAgent'), task),
                ('BehaviorAnalyzer', self.agents.get('BehaviorAnalyzer'), task),
                ('ImpactAnalyzer', self.agents.get('ImpactAnalyzer'), task),
                ('QualityGate', self.agents.get('QualityGate'), task)
            ]
            
            state_agents = [(n, f, t) for n, f, t in state_agents if f is not None]
            
            if state_agents:
                state_results = await self.runtime.execute_parallel(state_agents)
                iteration_result['current_state'] = state_results
            
            # 3. 외부 리서치
            if 'ExternalResearcher' in self.agents:
                research_result = await self.runtime.execute_agent(
                    'ExternalResearcher',
                    self.agents['ExternalResearcher'],
                    task
                )
                iteration_result['research'] = research_result
            
            # 4. 갭 분석
            if 'GapAnalyzer' in self.agents:
                gap_task = {
                    **task,
                    'shared_context': self.runtime.get_shared_context()
                }
                gap_result = await self.runtime.execute_agent(
                    'GapAnalyzer',
                    self.agents['GapAnalyzer'],
                    gap_task
                )
                iteration_result['gap_analysis'] = gap_result
                
                # 갭 스코어 업데이트
                self.gap_score = gap_result.get('gap_score', self.gap_score)
                logger.info(f"📊 현재 갭 스코어: {self.gap_score:.2%}")
            
            # 5. 갭이 임계값 이하면 종료
            if self.gap_score <= (1 - self.config.convergence_threshold):
                logger.info(f"✅ 수렴 달성! 갭 스코어: {self.gap_score:.2%}")
                results['converged'] = True
                results['final_gap_score'] = self.gap_score
                break
            
            # 6. 개선 작업 실행
            improvement_agents = [
                'SystemArchitect',
                'OrchestratorDesigner',
                'PlannerAgent',
                'TaskCreatorAgent',
                'CodeGenerator',
                'TestAgent'
            ]
            
            for agent_name in improvement_agents:
                if agent_name in self.agents:
                    improvement_task = {
                        **task,
                        'gap_analysis': iteration_result.get('gap_analysis', {}),
                        'shared_context': self.runtime.get_shared_context()
                    }
                    
                    result = await self.runtime.execute_agent(
                        agent_name,
                        self.agents[agent_name],
                        improvement_task
                    )
                    iteration_result[agent_name.lower()] = result
            
            # 반복 결과 저장
            results['iterations'].append(iteration_result)
            
            # 다음 반복을 위한 작업 업데이트
            task = {
                **task,
                'iteration': self.current_iteration,
                'previous_results': iteration_result
            }
        
        # 최종 결과
        results['total_iterations'] = self.current_iteration
        results['final_context'] = self.runtime.get_shared_context()
        results['execution_metrics'] = self.runtime.get_execution_metrics()
        
        logger.info(f"🏁 Evolution Loop 완료 (총 {self.current_iteration}회 반복)")
        
        return results
    
    async def _execute_ai_driven(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """AI 드리븐 실행.
        
        AI가 다음 실행할 에이전트와 전략을 결정합니다.
        
        Args:
            task: 작업
            
        Returns:
            실행 결과
        """
        logger.info("🤖 AI-Driven 실행 시작")
        
        results = {'executions': []}
        remaining_agents = list(self.agents.keys())
        
        while remaining_agents:
            # AI에게 다음 실행할 에이전트 결정 요청
            decision_prompt = f"""
현재 상황:
- 남은 에이전트: {remaining_agents}
- 현재 컨텍스트: {self.runtime.get_shared_context()}
- 작업: {task}

다음 실행할 에이전트를 선택하고 병렬 실행 가능한 에이전트를 그룹화하세요.
응답 형식:
{{
    "next_agents": ["agent1", "agent2"],
    "execution_type": "parallel" or "sequential",
    "reasoning": "결정 이유"
}}
"""
            
            ai_decision = await self.runtime._invoke_bedrock(
                decision_prompt,
                {'task': task}
            )
            
            # AI 결정 파싱 (간단한 예시)
            import json
            try:
                decision = json.loads(ai_decision)
                next_agents = decision.get('next_agents', [remaining_agents[0]])
                execution_type = decision.get('execution_type', 'sequential')
            except:
                # 파싱 실패 시 순차 실행
                next_agents = [remaining_agents[0]]
                execution_type = 'sequential'
            
            # 선택된 에이전트 실행
            if execution_type == 'parallel' and len(next_agents) > 1:
                agent_tasks = [(name, self.agents[name], task) for name in next_agents if name in self.agents]
                exec_results = await self.runtime.execute_parallel(agent_tasks)
                
                for name, result in zip(next_agents, exec_results):
                    results['executions'].append({
                        'agent': name,
                        'result': result,
                        'type': 'parallel'
                    })
            else:
                for agent_name in next_agents:
                    if agent_name in self.agents:
                        result = await self.runtime.execute_agent(
                            agent_name,
                            self.agents[agent_name],
                            task
                        )
                        results['executions'].append({
                            'agent': agent_name,
                            'result': result,
                            'type': 'sequential'
                        })
            
            # 실행된 에이전트 제거
            for agent_name in next_agents:
                if agent_name in remaining_agents:
                    remaining_agents.remove(agent_name)
            
            # 작업 컨텍스트 업데이트
            task['shared_context'] = self.runtime.get_shared_context()
        
        results['final_context'] = self.runtime.get_shared_context()
        results['execution_metrics'] = self.runtime.get_execution_metrics()
        
        logger.info("✅ AI-Driven 실행 완료")
        
        return results
    
    async def _execute_sequential(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """순차 실행.
        
        Args:
            task: 작업
            
        Returns:
            실행 결과
        """
        logger.info("➡️ 순차 실행 시작")
        
        results = {}
        order = self.execution_order if self.execution_order else list(self.agents.keys())
        
        for agent_name in order:
            if agent_name in self.agents:
                result = await self.runtime.execute_agent(
                    agent_name,
                    self.agents[agent_name],
                    {**task, 'shared_context': self.runtime.get_shared_context()}
                )
                results[agent_name] = result
        
        return results
    
    async def _execute_parallel(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """병렬 실행.
        
        Args:
            task: 작업
            
        Returns:
            실행 결과
        """
        logger.info("⚡ 병렬 실행 시작")
        
        agent_tasks = [
            (name, func, {**task, 'shared_context': self.runtime.get_shared_context()})
            for name, func in self.agents.items()
        ]
        
        results = await self.runtime.execute_parallel(agent_tasks)
        
        return {
            name: result 
            for name, result in zip(self.agents.keys(), results)
        }
    
    async def _execute_hybrid(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """하이브리드 실행.
        
        일부는 순차, 일부는 병렬로 실행합니다.
        
        Args:
            task: 작업
            
        Returns:
            실행 결과
        """
        logger.info("🔀 하이브리드 실행 시작")
        
        results = {}
        
        # 예시: 분석 에이전트는 병렬, 실행 에이전트는 순차
        analysis_agents = ['RequirementAnalyzer', 'StaticAnalyzer', 'CodeAnalysisAgent']
        execution_agents = ['PlannerAgent', 'TaskCreatorAgent', 'CodeGenerator']
        
        # 분석 단계 (병렬)
        parallel_tasks = [
            (name, self.agents[name], task)
            for name in analysis_agents if name in self.agents
        ]
        
        if parallel_tasks:
            parallel_results = await self.runtime.execute_parallel(parallel_tasks)
            for name, result in zip([t[0] for t in parallel_tasks], parallel_results):
                results[name] = result
        
        # 실행 단계 (순차)
        for agent_name in execution_agents:
            if agent_name in self.agents:
                result = await self.runtime.execute_agent(
                    agent_name,
                    self.agents[agent_name],
                    {**task, 'shared_context': self.runtime.get_shared_context()}
                )
                results[agent_name] = result
        
        return results
    
    def get_gap_score(self) -> float:
        """현재 갭 스코어 반환.
        
        Returns:
            갭 스코어 (0~1)
        """
        return self.gap_score
    
    def get_iteration_count(self) -> int:
        """현재 반복 횟수 반환.
        
        Returns:
            반복 횟수
        """
        return self.current_iteration
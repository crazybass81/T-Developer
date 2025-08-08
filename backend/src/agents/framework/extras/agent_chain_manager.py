# backend/src/agents/framework/agent_chain_manager.py
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import asyncio
import uuid
from datetime import datetime

class ChainStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

@dataclass
class ChainStep:
    agent_id: str
    agent_type: str
    input_mapping: Dict[str, str]  # 이전 단계 출력 -> 현재 단계 입력
    output_keys: List[str]
    condition: Optional[str] = None
    timeout: int = 300
    retry_count: int = 3

@dataclass
class AgentChain:
    id: str
    name: str
    steps: List[ChainStep]
    status: ChainStatus = ChainStatus.PENDING
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    current_step: int = 0
    results: Dict[str, Any] = None
    error_message: Optional[str] = None

class AgentChainManager:
    """에이전트 체인 관리 시스템"""
    
    def __init__(self):
        self.chains: Dict[str, AgentChain] = {}
        self.running_chains: Dict[str, asyncio.Task] = {}
        self.step_handlers: Dict[str, Callable] = {}
        self.chain_templates: Dict[str, List[ChainStep]] = {}
        
    def register_step_handler(self, agent_type: str, handler: Callable):
        """스텝 핸들러 등록"""
        self.step_handlers[agent_type] = handler
    
    def register_chain_template(self, template_name: str, steps: List[ChainStep]):
        """체인 템플릿 등록"""
        self.chain_templates[template_name] = steps
    
    async def create_chain(
        self, 
        name: str, 
        steps: List[ChainStep],
        template_name: Optional[str] = None
    ) -> str:
        """에이전트 체인 생성"""
        
        chain_id = str(uuid.uuid4())
        
        # 템플릿 사용
        if template_name and template_name in self.chain_templates:
            steps = self.chain_templates[template_name].copy()
        
        chain = AgentChain(
            id=chain_id,
            name=name,
            steps=steps,
            created_at=datetime.utcnow(),
            results={}
        )
        
        self.chains[chain_id] = chain
        return chain_id
    
    async def execute_chain(self, chain_id: str, initial_input: Dict[str, Any]) -> Dict[str, Any]:
        """체인 실행"""
        
        chain = self.chains.get(chain_id)
        if not chain:
            raise ValueError(f"Chain {chain_id} not found")
        
        chain.status = ChainStatus.RUNNING
        chain.started_at = datetime.utcnow()
        
        task = asyncio.create_task(self._run_chain(chain, initial_input))
        self.running_chains[chain_id] = task
        
        try:
            results = await task
            chain.status = ChainStatus.COMPLETED
            chain.completed_at = datetime.utcnow()
            chain.results = results
            return results
        except Exception as e:
            chain.status = ChainStatus.FAILED
            chain.error_message = str(e)
            raise e
        finally:
            self.running_chains.pop(chain_id, None)
    
    async def _run_chain(self, chain: AgentChain, initial_input: Dict[str, Any]) -> Dict[str, Any]:
        """체인 실행 로직"""
        
        context = initial_input.copy()
        step_results = {}
        
        for i, step in enumerate(chain.steps):
            chain.current_step = i
            
            # 조건 확인
            if step.condition and not self._evaluate_condition(step.condition, context):
                continue
            
            # 입력 매핑
            step_input = self._map_input(step.input_mapping, context, step_results)
            
            # 스텝 실행
            handler = self.step_handlers.get(step.agent_type)
            if not handler:
                raise ValueError(f"No handler for agent type: {step.agent_type}")
            
            retry_count = 0
            while retry_count <= step.retry_count:
                try:
                    result = await asyncio.wait_for(
                        handler(step_input),
                        timeout=step.timeout
                    )
                    
                    # 결과 저장
                    step_results[f"step_{i}"] = result
                    
                    # 출력 키에 따라 컨텍스트 업데이트
                    for key in step.output_keys:
                        if key in result:
                            context[key] = result[key]
                    
                    break
                    
                except Exception as e:
                    retry_count += 1
                    if retry_count > step.retry_count:
                        raise e
                    await asyncio.sleep(2 ** retry_count)  # 지수 백오프
        
        return {
            'final_context': context,
            'step_results': step_results,
            'execution_summary': {
                'total_steps': len(chain.steps),
                'completed_steps': chain.current_step + 1,
                'execution_time': (datetime.utcnow() - chain.started_at).total_seconds()
            }
        }
    
    def _map_input(
        self, 
        input_mapping: Dict[str, str], 
        context: Dict[str, Any], 
        step_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """입력 매핑"""
        
        mapped_input = {}
        
        for target_key, source_key in input_mapping.items():
            # 컨텍스트에서 찾기
            if source_key in context:
                mapped_input[target_key] = context[source_key]
            # 이전 스텝 결과에서 찾기
            elif '.' in source_key:
                step_key, result_key = source_key.split('.', 1)
                if step_key in step_results and result_key in step_results[step_key]:
                    mapped_input[target_key] = step_results[step_key][result_key]
        
        return mapped_input
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """조건 평가"""
        try:
            return eval(condition, {"__builtins__": {}}, context)
        except:
            return False
    
    async def pause_chain(self, chain_id: str) -> bool:
        """체인 일시정지"""
        
        if chain_id in self.running_chains:
            task = self.running_chains[chain_id]
            task.cancel()
            
            chain = self.chains.get(chain_id)
            if chain:
                chain.status = ChainStatus.PAUSED
            
            return True
        
        return False
    
    async def resume_chain(self, chain_id: str) -> bool:
        """체인 재시작"""
        
        chain = self.chains.get(chain_id)
        if not chain or chain.status != ChainStatus.PAUSED:
            return False
        
        # 현재 스텝부터 재시작
        remaining_steps = chain.steps[chain.current_step:]
        
        # 새로운 체인으로 재시작
        new_chain_id = await self.create_chain(
            f"{chain.name}_resumed",
            remaining_steps
        )
        
        # 기존 컨텍스트로 실행
        await self.execute_chain(new_chain_id, chain.results.get('final_context', {}))
        
        return True
    
    def get_chain_status(self, chain_id: str) -> Optional[Dict[str, Any]]:
        """체인 상태 조회"""
        
        chain = self.chains.get(chain_id)
        if not chain:
            return None
        
        return {
            'id': chain.id,
            'name': chain.name,
            'status': chain.status.value,
            'current_step': chain.current_step,
            'total_steps': len(chain.steps),
            'created_at': chain.created_at.isoformat() if chain.created_at else None,
            'started_at': chain.started_at.isoformat() if chain.started_at else None,
            'completed_at': chain.completed_at.isoformat() if chain.completed_at else None,
            'error_message': chain.error_message
        }
    
    def list_chains(self, status_filter: Optional[ChainStatus] = None) -> List[Dict[str, Any]]:
        """체인 목록 조회"""
        
        chains = list(self.chains.values())
        
        if status_filter:
            chains = [c for c in chains if c.status == status_filter]
        
        return [
            {
                'id': chain.id,
                'name': chain.name,
                'status': chain.status.value,
                'created_at': chain.created_at.isoformat() if chain.created_at else None
            }
            for chain in chains
        ]
    
    def get_chain_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """체인 템플릿 목록"""
        
        templates = {}
        for name, steps in self.chain_templates.items():
            templates[name] = [
                {
                    'agent_type': step.agent_type,
                    'input_mapping': step.input_mapping,
                    'output_keys': step.output_keys,
                    'timeout': step.timeout
                }
                for step in steps
            ]
        
        return templates

# 미리 정의된 체인 템플릿들
PREDEFINED_TEMPLATES = {
    'full_development_chain': [
        ChainStep(
            agent_id='nl_input',
            agent_type='nl_input',
            input_mapping={'description': 'user_input'},
            output_keys=['requirements', 'project_type']
        ),
        ChainStep(
            agent_id='ui_selection',
            agent_type='ui_selection',
            input_mapping={'requirements': 'requirements', 'project_type': 'project_type'},
            output_keys=['ui_framework', 'design_system']
        ),
        ChainStep(
            agent_id='parser',
            agent_type='parser',
            input_mapping={'requirements': 'requirements'},
            output_keys=['parsed_requirements', 'user_stories']
        ),
        ChainStep(
            agent_id='component_decision',
            agent_type='component_decision',
            input_mapping={'requirements': 'parsed_requirements'},
            output_keys=['selected_components']
        ),
        ChainStep(
            agent_id='generation',
            agent_type='generation',
            input_mapping={
                'components': 'selected_components',
                'framework': 'ui_framework'
            },
            output_keys=['generated_code']
        ),
        ChainStep(
            agent_id='assembly',
            agent_type='assembly',
            input_mapping={'code': 'generated_code'},
            output_keys=['assembled_project']
        )
    ],
    
    'analysis_only_chain': [
        ChainStep(
            agent_id='nl_input',
            agent_type='nl_input',
            input_mapping={'description': 'user_input'},
            output_keys=['requirements']
        ),
        ChainStep(
            agent_id='parser',
            agent_type='parser',
            input_mapping={'requirements': 'requirements'},
            output_keys=['analysis_report']
        )
    ]
}
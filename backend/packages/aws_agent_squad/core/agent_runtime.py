"""AWS Bedrock AgentCore Runtime Implementation.

이 모듈은 AWS Bedrock AgentCore를 사용하여 에이전트를 실행하는 
런타임 환경을 제공합니다. 모든 에이전트는 이 런타임을 통해 실행됩니다.

주요 기능:
1. Bedrock AgentCore와의 통합
2. 에이전트 실행 관리
3. 리소스 제한 및 모니터링
4. 에러 처리 및 재시도 로직
5. 분산 실행 지원
"""

import asyncio
import logging
import os
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json
import boto3
from botocore.config import Config

logger = logging.getLogger(__name__)


@dataclass
class RuntimeConfig:
    """Bedrock AgentCore 런타임 설정.
    
    AWS Agent Squad 프레임워크에서 에이전트 실행을 위한
    런타임 환경 설정을 정의합니다.
    """
    
    # Bedrock 설정 (환경 변수에서 로드)
    region: str = os.getenv("BEDROCK_REGION", "us-east-1")
    model_id: str = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
    max_tokens: int = int(os.getenv("BEDROCK_MAX_TOKENS", "4096"))
    temperature: float = float(os.getenv("BEDROCK_TEMPERATURE", "0.7"))
    
    # 실행 설정
    max_parallel_agents: int = 5
    timeout_seconds: int = 300
    retry_count: int = 3
    retry_delay_seconds: int = 5
    
    # 리소스 제한
    max_memory_mb: int = 2000
    max_cpu_percent: int = 80
    
    # 모니터링
    enable_tracing: bool = True
    enable_metrics: bool = True
    log_level: str = "INFO"
    
    # Evolution Loop 설정
    max_evolution_iterations: int = 10
    convergence_threshold: float = 0.95
    gap_tolerance: float = 0.01


class AgentRuntime:
    """AWS Bedrock AgentCore 런타임.
    
    에이전트 실행을 위한 핵심 런타임 환경을 제공합니다.
    AWS Agent Squad 프레임워크의 모든 에이전트는 이 런타임을 통해 실행됩니다.
    """
    
    def __init__(self, config: RuntimeConfig):
        """런타임 초기화.
        
        Args:
            config: 런타임 설정
        """
        self.config = config
        self.bedrock_client = self._init_bedrock_client()
        self.bedrock_runtime = self._init_bedrock_runtime()
        self.active_agents: Dict[str, Any] = {}
        self.execution_history: List[Dict[str, Any]] = []
        
        # 페르소나 시스템
        self.personas: Dict[str, Any] = {}
        
        # 문서 컨텍스트 (모든 에이전트가 공유)
        self.shared_document_context: Dict[str, Any] = {}
        
        logger.info(f"🚀 Bedrock AgentCore Runtime 초기화 완료 (Region: {config.region})")
    
    def _init_bedrock_client(self):
        """Bedrock 클라이언트 초기화."""
        config = Config(
            region_name=self.config.region,
            retries={'max_attempts': self.config.retry_count}
        )
        return boto3.client('bedrock', config=config)
    
    def _init_bedrock_runtime(self):
        """Bedrock Runtime 클라이언트 초기화."""
        config = Config(
            region_name=self.config.region,
            retries={'max_attempts': self.config.retry_count}
        )
        return boto3.client('bedrock-runtime', config=config)
    
    async def execute_agent(
        self,
        agent_name: str,
        agent_callable: Callable,
        task: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """에이전트 실행.
        
        AWS Bedrock AgentCore를 통해 에이전트를 실행하고
        결과를 반환합니다.
        
        Args:
            agent_name: 에이전트 이름
            agent_callable: 실행할 에이전트 함수
            task: 에이전트 작업
            context: 추가 컨텍스트
            
        Returns:
            실행 결과
        """
        start_time = datetime.now()
        
        try:
            # AgentTask 객체 생성 (dict를 AgentTask로 변환)
            from backend.packages.agents.base import AgentTask
            
            if isinstance(task, dict):
                # dict를 AgentTask로 변환
                agent_task = AgentTask(
                    intent=task.get('type', 'default'),
                    inputs=task
                )
            else:
                agent_task = task
            
            # 페르소나 적용
            if agent_name in self.personas:
                persona = self.personas[agent_name]
                # 페르소나를 inputs에 적용
                if hasattr(agent_task, 'inputs'):
                    agent_task.inputs = self._apply_persona(agent_task.inputs, persona)
            
            # 공유 문서 컨텍스트 추가
            if context is None:
                context = {}
            context['shared_documents'] = self.shared_document_context
            
            # 에이전트 등록
            self.active_agents[agent_name] = {
                'status': 'running',
                'start_time': start_time.isoformat()
            }
            
            # Bedrock을 통한 AI 추론 (필요한 경우)
            if hasattr(agent_task, 'inputs') and agent_task.inputs.get('requires_ai', False):
                logger.info(f"🤖 Invoking Bedrock AI for {agent_name}")
                try:
                    ai_response = await self._invoke_bedrock(
                        prompt=agent_task.inputs.get('prompt', ''),
                        context=context
                    )
                    agent_task.inputs['ai_response'] = ai_response
                    logger.info(f"🤖 Bedrock AI response received for {agent_name}")
                except Exception as e:
                    logger.error(f"❌ Bedrock AI invocation failed for {agent_name}: {str(e)}")
                    raise
            
            # 에이전트 실행
            logger.info(f"🚀 Executing {agent_name} with task type: {agent_task.inputs.get('type', 'unknown') if hasattr(agent_task, 'inputs') else 'unknown'}")
            # agent_callable이 agent_execute 래퍼인 경우 context도 전달
            # agent_execute는 (task, context) 두 개의 인자를 받음
            import inspect
            sig = inspect.signature(agent_callable)
            if len(sig.parameters) > 1:
                # agent_execute 래퍼 (2개 인자)
                result = await agent_callable(agent_task, context)
            else:
                # 일반 execute 메서드 (1개 인자)
                result = await agent_callable(agent_task)
            logger.info(f"✅ {agent_name} completed execution")
            
            # 결과를 공유 문서 컨텍스트에 추가
            self.shared_document_context[agent_name] = {
                'result': result,
                'timestamp': datetime.now().isoformat()
            }
            
            # 실행 기록
            execution_time = (datetime.now() - start_time).total_seconds()
            task_type = agent_task.inputs.get('type', 'unknown') if hasattr(agent_task, 'inputs') else 'unknown'
            self.execution_history.append({
                'agent': agent_name,
                'task': task_type,
                'duration': execution_time,
                'status': 'success',
                'timestamp': start_time.isoformat()
            })
            
            # 에이전트 상태 업데이트
            self.active_agents[agent_name] = {
                'status': 'completed',
                'duration': execution_time
            }
            
            logger.info(f"✅ {agent_name} 실행 완료 ({execution_time:.2f}초)")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ {agent_name} 실행 실패: {str(e)}")
            
            # 에이전트 상태 업데이트
            self.active_agents[agent_name] = {
                'status': 'failed',
                'error': str(e)
            }
            
            # 재시도 로직
            retry_count = agent_task.inputs.get('retry_count', 0) if hasattr(agent_task, 'inputs') else 0
            if retry_count < self.config.retry_count:
                if hasattr(agent_task, 'inputs'):
                    agent_task.inputs['retry_count'] = retry_count + 1
                logger.info(f"🔄 {agent_name} 재시도 {retry_count + 1}/{self.config.retry_count}")
                await asyncio.sleep(self.config.retry_delay_seconds)
                # 원래 task dict를 다시 전달 (재변환을 위해)
                original_task = agent_task.inputs if hasattr(agent_task, 'inputs') else {}
                return await self.execute_agent(agent_name, agent_callable, original_task, context)
            
            raise
    
    async def execute_parallel(
        self,
        agents: List[tuple[str, Callable, Dict[str, Any]]],
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """병렬 에이전트 실행.
        
        여러 에이전트를 병렬로 실행합니다.
        
        Args:
            agents: (에이전트명, 함수, 작업) 튜플 리스트
            context: 공유 컨텍스트
            
        Returns:
            각 에이전트 실행 결과 리스트
        """
        # 병렬 실행 제한
        semaphore = asyncio.Semaphore(self.config.max_parallel_agents)
        
        async def run_with_semaphore(agent_info):
            name, func, task = agent_info
            async with semaphore:
                return await self.execute_agent(name, func, task, context)
        
        tasks = [run_with_semaphore(agent) for agent in agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 예외 처리
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"병렬 실행 중 에러 발생: {agents[i][0]} - {str(result)}")
                final_results.append({'error': str(result)})
            else:
                final_results.append(result)
        
        return final_results
    
    async def _invoke_bedrock(self, prompt: str, context: Dict[str, Any]) -> str:
        """Bedrock AI 모델 호출.
        
        Args:
            prompt: AI 프롬프트
            context: 추가 컨텍스트
            
        Returns:
            AI 응답
        """
        try:
            # 컨텍스트를 프롬프트에 추가
            full_prompt = self._build_prompt_with_context(prompt, context)
            
            # Bedrock Runtime 호출
            request_body = {
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': self.config.max_tokens,
                'temperature': self.config.temperature,
                'messages': [
                    {
                        'role': 'user',
                        'content': full_prompt
                    }
                ]
            }
            
            # JSON serialization with datetime handling
            import json
            from datetime import datetime
            
            def json_serial(obj):
                """JSON serializer for objects not serializable by default json code"""
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Type {type(obj)} not serializable")
            
            logger.info(f"🌐 Bedrock API 호출 중... (model: {self.config.model_id})")
            response = self.bedrock_runtime.invoke_model(
                modelId=self.config.model_id,
                contentType='application/json',
                accept='application/json',
                body=json.dumps(request_body, default=json_serial)
            )
            logger.info("🌐 Bedrock API 응답 수신")
            
            # 응답 파싱
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
            
        except Exception as e:
            logger.error(f"Bedrock 호출 실패: {str(e)}")
            raise
    
    def _build_prompt_with_context(self, prompt: str, context: Dict[str, Any]) -> str:
        """컨텍스트를 포함한 프롬프트 생성.
        
        Args:
            prompt: 기본 프롬프트
            context: 추가 컨텍스트
            
        Returns:
            완성된 프롬프트
        """
        context_str = ""
        
        # 공유 문서 컨텍스트 추가
        if 'shared_documents' in context:
            from datetime import datetime
            
            def json_serial(obj):
                """JSON serializer for objects not serializable by default json code"""
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return str(obj)
            
            context_str += "\n### 공유 문서 컨텍스트:\n"
            for agent, doc in context['shared_documents'].items():
                if isinstance(doc, dict) and 'result' in doc:
                    context_str += f"\n**{agent}:**\n{json.dumps(doc['result'], indent=2, ensure_ascii=False, default=json_serial)}\n"
        
        # 기타 컨텍스트 추가
        for key, value in context.items():
            if key != 'shared_documents':
                context_str += f"\n### {key}:\n{json.dumps(value, indent=2, ensure_ascii=False)}\n"
        
        return f"{context_str}\n\n### 작업:\n{prompt}"
    
    def _apply_persona(self, task: Dict[str, Any], persona: Dict[str, Any]) -> Dict[str, Any]:
        """페르소나를 작업에 적용.
        
        Args:
            task: 원본 작업
            persona: 적용할 페르소나
            
        Returns:
            페르소나가 적용된 작업
        """
        if 'prompt' in task:
            persona_prompt = f"""
당신은 {persona.get('name', '에이전트')}입니다.
역할: {persona.get('role', '')}
성격: {', '.join(persona.get('personality_traits', []))}
전문분야: {', '.join(persona.get('expertise', []))}
의사소통 스타일: {persona.get('communication_style', '')}
핵심 가치: {', '.join(persona.get('core_values', []))}
캐치프레이즈: "{persona.get('catchphrase', '')}"

이 페르소나를 유지하면서 다음 작업을 수행하세요:
"""
            task['prompt'] = persona_prompt + task['prompt']
        
        return task
    
    def register_persona(self, agent_name: str, persona: Dict[str, Any]):
        """에이전트 페르소나 등록.
        
        Args:
            agent_name: 에이전트 이름
            persona: 페르소나 정보
        """
        self.personas[agent_name] = persona
        logger.info(f"🎭 {agent_name} 페르소나 등록: {persona.get('name', 'Unknown')}")
    
    def get_shared_context(self) -> Dict[str, Any]:
        """공유 문서 컨텍스트 반환.
        
        Returns:
            모든 에이전트가 공유하는 문서 컨텍스트
        """
        return self.shared_document_context.copy()
    
    def update_shared_context(self, agent_name: str, document: Dict[str, Any]):
        """공유 문서 컨텍스트 업데이트.
        
        Args:
            agent_name: 에이전트 이름
            document: 추가할 문서
        """
        self.shared_document_context[agent_name] = {
            'document': document,
            'timestamp': datetime.now().isoformat()
        }
        logger.debug(f"📄 {agent_name} 문서가 공유 컨텍스트에 추가됨")
    
    def get_execution_metrics(self) -> Dict[str, Any]:
        """실행 메트릭 반환.
        
        Returns:
            런타임 실행 메트릭
        """
        total_executions = len(self.execution_history)
        successful = sum(1 for h in self.execution_history if h['status'] == 'success')
        failed = total_executions - successful
        
        avg_duration = 0
        if total_executions > 0:
            avg_duration = sum(h.get('duration', 0) for h in self.execution_history) / total_executions
        
        return {
            'total_executions': total_executions,
            'successful': successful,
            'failed': failed,
            'success_rate': successful / total_executions if total_executions > 0 else 0,
            'average_duration': avg_duration,
            'active_agents': len([a for a in self.active_agents.values() if a['status'] == 'running']),
            'history': self.execution_history[-10:]  # 최근 10개
        }
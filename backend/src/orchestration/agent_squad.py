"""
AWS Agent Squad Orchestration
9개 에이전트를 조율하는 중앙 오케스트레이터
"""

import json
import asyncio
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from pathlib import Path

import boto3
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit

# Production 에이전트 임포트
from agents.production.nl_input import NLInputAgent
from agents.production.ui_selection import UISelectionAgent
from agents.production.parser import ParserAgent
from agents.production.component_decision import ComponentDecisionAgent
from agents.production.match_rate import MatchRateAgent
from agents.production.search import SearchAgent
from agents.production.generation import GenerationAgent
from agents.production.assembly import AssemblyAgent
from agents.production.download import DownloadAgent

# AWS 클라이언트
stepfunctions = boto3.client('stepfunctions')
sns = boto3.client('sns')
sqs = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')

logger = Logger()
tracer = Tracer()
metrics = Metrics()


class PipelineStage(Enum):
    """파이프라인 단계"""
    NL_INPUT = "nl_input"
    UI_SELECTION = "ui_selection"
    PARSING = "parsing"
    COMPONENT_DECISION = "component_decision"
    MATCH_RATE = "match_rate"
    SEARCH = "search"
    GENERATION = "generation"
    ASSEMBLY = "assembly"
    DOWNLOAD = "download"
    COMPLETED = "completed"


@dataclass
class PipelineContext:
    """파이프라인 컨텍스트"""
    session_id: str
    user_id: str
    project_name: str
    current_stage: PipelineStage
    stages_completed: List[PipelineStage]
    intermediate_results: Dict[str, Any]
    errors: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리 변환"""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'project_name': self.project_name,
            'current_stage': self.current_stage.value,
            'stages_completed': [s.value for s in self.stages_completed],
            'intermediate_results': self.intermediate_results,
            'errors': self.errors,
            'metadata': self.metadata
        }


@dataclass
class SquadConfiguration:
    """Squad 설정"""
    parallel_execution: bool = False
    max_retries: int = 3
    timeout_seconds: int = 300
    save_intermediate: bool = True
    enable_monitoring: bool = True
    enable_notifications: bool = True


class AgentSquadOrchestrator:
    """AWS Agent Squad 오케스트레이터"""
    
    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.config = self._load_config()
        
        # 에이전트 초기화
        self._init_agents()
        
        # 스토리지 초기화
        self._init_storage()
        
        # 모니터링 초기화
        self._init_monitoring()
        
        logger.info(f"Agent Squad Orchestrator initialized for {environment}")
    
    def _load_config(self) -> Dict[str, Any]:
        """설정 로드"""
        ssm = boto3.client('ssm')
        try:
            response = ssm.get_parameters_by_path(
                Path=f'/t-developer/{self.environment}/squad/',
                Recursive=True,
                WithDecryption=True
            )
            
            config = {}
            for param in response['Parameters']:
                key = param['Name'].split('/')[-1]
                config[key] = param['Value']
            
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {
                'state_machine_arn': None,
                'notification_topic': None,
                'queue_url': None,
                'table_name': f't-dev-pipeline-{self.environment}'
            }
    
    def _init_agents(self):
        """에이전트 초기화"""
        self.agents = {
            PipelineStage.NL_INPUT: NLInputAgent(self.environment),
            PipelineStage.UI_SELECTION: UISelectionAgent(self.environment),
            PipelineStage.PARSING: ParserAgent(self.environment),
            PipelineStage.COMPONENT_DECISION: ComponentDecisionAgent(self.environment),
            PipelineStage.MATCH_RATE: MatchRateAgent(self.environment),
            PipelineStage.SEARCH: SearchAgent(self.environment),
            PipelineStage.GENERATION: GenerationAgent(self.environment),
            PipelineStage.ASSEMBLY: AssemblyAgent(self.environment),
            PipelineStage.DOWNLOAD: DownloadAgent(self.environment)
        }
    
    def _init_storage(self):
        """스토리지 초기화"""
        self.table = dynamodb.Table(self.config.get('table_name', 't-dev-pipeline'))
    
    def _init_monitoring(self):
        """모니터링 초기화"""
        self.metrics_namespace = 'TDeveloper/AgentSquad'
    
    @tracer.capture_method
    async def execute_pipeline(
        self,
        user_input: str,
        user_id: str,
        project_name: str,
        squad_config: Optional[SquadConfiguration] = None
    ) -> Dict[str, Any]:
        """
        전체 파이프라인 실행
        
        Args:
            user_input: 사용자의 자연어 입력
            user_id: 사용자 ID
            project_name: 프로젝트 이름
            squad_config: Squad 설정
            
        Returns:
            최종 결과
        """
        start_time = time.time()
        session_id = f"{user_id}_{int(time.time())}"
        
        # 파이프라인 컨텍스트 생성
        context = PipelineContext(
            session_id=session_id,
            user_id=user_id,
            project_name=project_name,
            current_stage=PipelineStage.NL_INPUT,
            stages_completed=[],
            intermediate_results={},
            errors=[],
            metadata={'start_time': start_time}
        )
        
        if not squad_config:
            squad_config = SquadConfiguration()
        
        try:
            # Step Functions 사용 가능한 경우
            if self.config.get('state_machine_arn'):
                return await self._execute_with_step_functions(
                    user_input, context, squad_config
                )
            else:
                # 직접 실행
                return await self._execute_direct(
                    user_input, context, squad_config
                )
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            context.errors.append({
                'stage': context.current_stage.value,
                'error': str(e),
                'timestamp': time.time()
            })
            
            # 실패 알림
            if squad_config.enable_notifications:
                await self._send_notification(context, 'failed')
            
            raise
    
    async def _execute_direct(
        self,
        user_input: str,
        context: PipelineContext,
        config: SquadConfiguration
    ) -> Dict[str, Any]:
        """직접 파이프라인 실행"""
        
        # 1. NL Input Processing
        context.current_stage = PipelineStage.NL_INPUT
        nl_result = await self._execute_stage(
            PipelineStage.NL_INPUT,
            {'query': user_input},
            context,
            config
        )
        context.intermediate_results['nl_input'] = nl_result
        
        # 2. UI Selection
        context.current_stage = PipelineStage.UI_SELECTION
        ui_result = await self._execute_stage(
            PipelineStage.UI_SELECTION,
            {'requirements': nl_result},
            context,
            config
        )
        context.intermediate_results['ui_selection'] = ui_result
        
        # 3. Parsing
        context.current_stage = PipelineStage.PARSING
        parsed_result = await self._execute_stage(
            PipelineStage.PARSING,
            {
                'input_data': nl_result,
                'ui_selection': ui_result
            },
            context,
            config
        )
        context.intermediate_results['parsed_project'] = parsed_result
        
        # 4. Component Decision
        context.current_stage = PipelineStage.COMPONENT_DECISION
        component_result = await self._execute_stage(
            PipelineStage.COMPONENT_DECISION,
            {
                'parsed_project': parsed_result,
                'ui_selection': ui_result
            },
            context,
            config
        )
        context.intermediate_results['technology_stack'] = component_result
        
        # 5. Match Rate Calculation
        context.current_stage = PipelineStage.MATCH_RATE
        match_result = await self._execute_stage(
            PipelineStage.MATCH_RATE,
            {
                'requirements': parsed_result,
                'component_library': {},  # 기본 라이브러리 사용
                'technology_stack': component_result
            },
            context,
            config
        )
        context.intermediate_results['matching_result'] = match_result
        
        # 6. Component Search
        context.current_stage = PipelineStage.SEARCH
        search_result = await self._execute_stage(
            PipelineStage.SEARCH,
            {
                'requirements': parsed_result,
                'technology_stack': component_result,
                'matching_result': match_result
            },
            context,
            config
        )
        context.intermediate_results['search_results'] = search_result
        
        # 7. Code Generation
        context.current_stage = PipelineStage.GENERATION
        generation_result = await self._execute_stage(
            PipelineStage.GENERATION,
            {
                'parsed_project': parsed_result,
                'technology_stack': component_result,
                'search_results': search_result
            },
            context,
            config
        )
        context.intermediate_results['generation_result'] = generation_result
        
        # 8. Project Assembly
        context.current_stage = PipelineStage.ASSEMBLY
        assembly_result = await self._execute_stage(
            PipelineStage.ASSEMBLY,
            {
                'generation_result': generation_result,
                'technology_stack': component_result
            },
            context,
            config
        )
        context.intermediate_results['assembly_result'] = assembly_result
        
        # 9. Download Preparation
        context.current_stage = PipelineStage.DOWNLOAD
        download_result = await self._execute_stage(
            PipelineStage.DOWNLOAD,
            {'assembly_result': assembly_result},
            context,
            config
        )
        context.intermediate_results['download_result'] = download_result
        
        # 완료
        context.current_stage = PipelineStage.COMPLETED
        context.metadata['end_time'] = time.time()
        context.metadata['total_duration'] = context.metadata['end_time'] - context.metadata['start_time']
        
        # 결과 저장
        if config.save_intermediate:
            await self._save_context(context)
        
        # 성공 알림
        if config.enable_notifications:
            await self._send_notification(context, 'completed')
        
        # 메트릭 기록
        metrics.add_metric(
            name="PipelineExecutionTime",
            unit=MetricUnit.Seconds,
            value=context.metadata['total_duration']
        )
        
        return {
            'success': True,
            'session_id': context.session_id,
            'download_links': download_result.get('download_links', []),
            'project_manifest': assembly_result.get('project_manifest', {}),
            'execution_time': context.metadata['total_duration'],
            'stages_completed': [s.value for s in context.stages_completed]
        }
    
    async def _execute_stage(
        self,
        stage: PipelineStage,
        input_data: Dict[str, Any],
        context: PipelineContext,
        config: SquadConfiguration
    ) -> Dict[str, Any]:
        """개별 스테이지 실행"""
        agent = self.agents.get(stage)
        if not agent:
            raise ValueError(f"Agent not found for stage: {stage}")
        
        start_time = time.time()
        retries = 0
        
        while retries < config.max_retries:
            try:
                # 에이전트별 메소드 호출
                if stage == PipelineStage.NL_INPUT:
                    result = await agent.process_description(
                        input_data['query']
                    )
                    result = result.to_dict() if hasattr(result, 'to_dict') else asdict(result)
                    
                elif stage == PipelineStage.UI_SELECTION:
                    result = await agent.select_ui_framework(
                        input_data['requirements']
                    )
                    result = result.to_dict() if hasattr(result, 'to_dict') else asdict(result)
                    
                elif stage == PipelineStage.PARSING:
                    result = await agent.parse_project(
                        input_data['input_data']
                    )
                    result = result.to_dict() if hasattr(result, 'to_dict') else asdict(result)
                    
                elif stage == PipelineStage.COMPONENT_DECISION:
                    result = await agent.make_decisions(
                        input_data['parsed_project'],
                        input_data['ui_selection']
                    )
                    result = result.to_dict() if hasattr(result, 'to_dict') else asdict(result)
                    
                elif stage == PipelineStage.MATCH_RATE:
                    result = await agent.calculate_match_rate(
                        input_data['requirements'],
                        input_data['component_library'],
                        input_data['technology_stack']
                    )
                    result = asdict(result)
                    
                elif stage == PipelineStage.SEARCH:
                    result = await agent.search_components(
                        input_data['requirements'],
                        input_data['technology_stack'],
                        input_data['matching_result']
                    )
                    
                elif stage == PipelineStage.GENERATION:
                    result = await agent.generate_code(
                        input_data['parsed_project'],
                        input_data['technology_stack'],
                        input_data['search_results']
                    )
                    result = asdict(result)
                    
                elif stage == PipelineStage.ASSEMBLY:
                    result = await agent.assemble_project(
                        input_data['generation_result'],
                        input_data['technology_stack']
                    )
                    result = asdict(result)
                    
                elif stage == PipelineStage.DOWNLOAD:
                    result = await agent.prepare_download(
                        input_data['assembly_result']
                    )
                    result = asdict(result)
                else:
                    raise ValueError(f"Unknown stage: {stage}")
                
                # 성공
                context.stages_completed.append(stage)
                
                # 메트릭 기록
                execution_time = time.time() - start_time
                metrics.add_metric(
                    name=f"Stage_{stage.value}_ExecutionTime",
                    unit=MetricUnit.Seconds,
                    value=execution_time
                )
                
                logger.info(f"Stage {stage.value} completed in {execution_time:.2f}s")
                
                return result
                
            except Exception as e:
                retries += 1
                logger.error(f"Stage {stage.value} failed (attempt {retries}): {e}")
                
                if retries >= config.max_retries:
                    context.errors.append({
                        'stage': stage.value,
                        'error': str(e),
                        'attempts': retries
                    })
                    raise
                
                # 재시도 대기
                await asyncio.sleep(2 ** retries)
    
    async def _execute_with_step_functions(
        self,
        user_input: str,
        context: PipelineContext,
        config: SquadConfiguration
    ) -> Dict[str, Any]:
        """Step Functions를 사용한 실행"""
        # Step Functions 입력 준비
        state_input = {
            'user_input': user_input,
            'context': context.to_dict(),
            'config': asdict(config)
        }
        
        # Step Functions 실행 시작
        response = stepfunctions.start_execution(
            stateMachineArn=self.config['state_machine_arn'],
            name=context.session_id,
            input=json.dumps(state_input)
        )
        
        execution_arn = response['executionArn']
        
        # 실행 상태 모니터링
        while True:
            status = stepfunctions.describe_execution(
                executionArn=execution_arn
            )
            
            if status['status'] == 'SUCCEEDED':
                output = json.loads(status['output'])
                return output
            elif status['status'] in ['FAILED', 'TIMED_OUT', 'ABORTED']:
                raise Exception(f"Step Functions execution failed: {status['status']}")
            
            await asyncio.sleep(5)
    
    async def _save_context(self, context: PipelineContext):
        """컨텍스트 저장"""
        try:
            self.table.put_item(
                Item={
                    'session_id': context.session_id,
                    'user_id': context.user_id,
                    'project_name': context.project_name,
                    'current_stage': context.current_stage.value,
                    'stages_completed': [s.value for s in context.stages_completed],
                    'intermediate_results': context.intermediate_results,
                    'errors': context.errors,
                    'metadata': context.metadata,
                    'timestamp': int(time.time())
                }
            )
        except Exception as e:
            logger.error(f"Failed to save context: {e}")
    
    async def _send_notification(self, context: PipelineContext, status: str):
        """알림 전송"""
        if not self.config.get('notification_topic'):
            return
        
        try:
            message = {
                'session_id': context.session_id,
                'user_id': context.user_id,
                'project_name': context.project_name,
                'status': status,
                'current_stage': context.current_stage.value,
                'stages_completed': [s.value for s in context.stages_completed],
                'errors': context.errors
            }
            
            sns.publish(
                TopicArn=self.config['notification_topic'],
                Subject=f"T-Developer Pipeline {status}: {context.project_name}",
                Message=json.dumps(message, indent=2)
            )
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda 핸들러 - 전체 파이프라인 실행
    
    Args:
        event: Lambda 이벤트
        context: Lambda 컨텍스트
        
    Returns:
        API Gateway 응답
    """
    import asyncio
    
    try:
        # 요청 파싱
        body = json.loads(event.get('body', '{}'))
        user_input = body.get('user_input', '')
        user_id = body.get('user_id', 'anonymous')
        project_name = body.get('project_name', 'untitled')
        
        # Squad 설정
        squad_config = SquadConfiguration(
            parallel_execution=body.get('parallel_execution', False),
            max_retries=body.get('max_retries', 3),
            timeout_seconds=body.get('timeout_seconds', 300),
            save_intermediate=body.get('save_intermediate', True),
            enable_monitoring=body.get('enable_monitoring', True),
            enable_notifications=body.get('enable_notifications', True)
        )
        
        # 오케스트레이터 실행
        orchestrator = AgentSquadOrchestrator()
        
        # 비동기 실행
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            orchestrator.execute_pipeline(
                user_input,
                user_id,
                project_name,
                squad_config
            )
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result, ensure_ascii=False, default=str)
        }
        
    except Exception as e:
        logger.error(f"Pipeline execution error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': {
                    'code': 'PIPELINE_ERROR',
                    'message': str(e)
                }
            }, ensure_ascii=False)
        }
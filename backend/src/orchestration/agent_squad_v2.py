"""
AWS Agent Squad Orchestration V2 - Critical Bug Fixes Applied
Fixes:
1. Unified result serialization
2. DynamoDB item size protection with S3 fallback
3. Improved Lambda event loop handling
4. SSM paginator for parameter loading
"""

import asyncio
import hashlib
import json
import logging
import time
import uuid
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import boto3
from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.metrics import MetricUnit

from agents.ecs_integrated.assembly.main import AssemblyAgent
from agents.ecs_integrated.component_decision.main import ComponentDecisionAgent
from agents.ecs_integrated.download.main import DownloadAgent
from agents.ecs_integrated.generation.main import GenerationAgent
from agents.ecs_integrated.match_rate.main import MatchRateAgent
from agents.ecs_integrated.nl_input.main import NLInputAgent
from agents.ecs_integrated.parser.main import ParserAgent
from agents.ecs_integrated.search.main import SearchAgent
from agents.ecs_integrated.ui_selection.main import UISelectionAgent

# AWS 클라이언트
stepfunctions = boto3.client("stepfunctions")
sns = boto3.client("sns")
sqs = boto3.client("sqs")
dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")
ssm = boto3.client("ssm")

logger = Logger()
tracer = Tracer()
metrics = Metrics()

# Configuration constants
MAX_DYNAMODB_ITEM_SIZE = 350 * 1024  # 350KB (safe margin from 400KB)
S3_BUCKET_NAME = "t-developer-large-results"
AGENT_VERSION = "2.0.0"  # Version token for cache keys


class PipelineStage(Enum):
    """파이프라인 단계"""
    NL_INPUT = "nl_input"
    UI_SELECTION = "ui_selection"
    PARSER = "parser"
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
            "session_id": self.session_id,
            "user_id": self.user_id,
            "project_name": self.project_name,
            "current_stage": self.current_stage.value,
            "stages_completed": [s.value for s in self.stages_completed],
            "intermediate_results": self.intermediate_results,
            "errors": self.errors,
            "metadata": self.metadata,
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


class AgentSquadOrchestratorV2:
    """AWS Agent Squad 오케스트레이터 V2"""

    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.config = self._load_config()
        self.agents = self._initialize_agents()
        self.table = dynamodb.Table(f"t-developer-pipeline-{environment}")

    def _initialize_agents(self) -> Dict[PipelineStage, Any]:
        """에이전트 초기화"""
        return {
            PipelineStage.NL_INPUT: NLInputAgent(),
            PipelineStage.UI_SELECTION: UISelectionAgent(),
            PipelineStage.PARSER: ParserAgent(),
            PipelineStage.COMPONENT_DECISION: ComponentDecisionAgent(),
            PipelineStage.MATCH_RATE: MatchRateAgent(),
            PipelineStage.SEARCH: SearchAgent(),
            PipelineStage.GENERATION: GenerationAgent(),
            PipelineStage.ASSEMBLY: AssemblyAgent(),
            PipelineStage.DOWNLOAD: DownloadAgent(),
        }

    def _load_config(self) -> Dict[str, Any]:
        """설정 로드 with SSM Paginator"""
        config = {}
        
        # Use paginator to handle many parameters
        paginator = ssm.get_paginator('get_parameters_by_path')
        page_iterator = paginator.paginate(
            Path=f"/t-developer/{self.environment}/squad/",
            Recursive=True,
            WithDecryption=True
        )
        
        for page in page_iterator:
            for param in page.get("Parameters", []):
                key = param["Name"].split("/")[-1]
                value = param["Value"]
                try:
                    config[key] = json.loads(value)
                except json.JSONDecodeError:
                    config[key] = value
                    
        return config

    def _normalize_result(self, result: Any, stage: PipelineStage) -> Dict[str, Any]:
        """
        Normalize all stage results to Dict[str, Any]
        Ensures consistent serialization across all stages
        """
        # Handle different result types uniformly
        if isinstance(result, dict):
            return result
        elif hasattr(result, "to_dict"):
            return result.to_dict()
        elif hasattr(result, "__dict__"):
            try:
                return asdict(result)
            except:
                return {"data": str(result)}
        else:
            # Fallback for primitive types
            return {"data": result}

    async def _execute_stage(
        self,
        stage: PipelineStage,
        input_data: Dict[str, Any],
        context: PipelineContext,
        config: SquadConfiguration,
    ) -> Dict[str, Any]:
        """개별 스테이지 실행 with unified serialization"""
        agent = self.agents.get(stage)
        if not agent:
            raise ValueError(f"Agent not found for stage: {stage}")
            
        start_time = time.time()
        retries = 0
        
        while retries < config.max_retries:
            try:
                # Execute agent method based on stage
                if stage == PipelineStage.NL_INPUT:
                    result = await agent.process_description(input_data["query"])
                elif stage == PipelineStage.UI_SELECTION:
                    result = await agent.select_ui_framework(input_data["requirements"])
                elif stage == PipelineStage.PARSER:
                    result = await agent.parse_project(input_data["input_data"])
                elif stage == PipelineStage.COMPONENT_DECISION:
                    result = await agent.make_decision(
                        input_data["parsed_structure"],
                        input_data["ui_framework"]
                    )
                elif stage == PipelineStage.MATCH_RATE:
                    result = await agent.calculate_match_rate(
                        input_data["requirements"],
                        input_data["component_specs"]
                    )
                elif stage == PipelineStage.SEARCH:
                    result = await agent.search_components(
                        input_data["requirements"],
                        input_data["technology_stack"],
                        input_data["matching_result"],
                    )
                elif stage == PipelineStage.GENERATION:
                    result = await agent.generate_code(
                        input_data["search_results"],
                        input_data["project_structure"]
                    )
                elif stage == PipelineStage.ASSEMBLY:
                    result = await agent.assemble_project(
                        input_data["generated_code"],
                        input_data["project_config"]
                    )
                elif stage == PipelineStage.DOWNLOAD:
                    result = await agent.prepare_download(
                        input_data["assembled_project"],
                        input_data["project_metadata"]
                    )
                else:
                    raise ValueError(f"Unknown stage: {stage}")
                
                # Normalize result to Dict[str, Any]
                normalized_result = self._normalize_result(result, stage)
                
                # Record metrics
                execution_time = time.time() - start_time
                metrics.add_metric(
                    name=f"stage_{stage.value}_duration",
                    unit=MetricUnit.Seconds,
                    value=execution_time
                )
                
                return normalized_result
                
            except Exception as e:
                retries += 1
                logger.error(f"Stage {stage} failed (attempt {retries}): {str(e)}")
                
                if retries >= config.max_retries:
                    raise
                    
                await asyncio.sleep(2 ** retries)  # Exponential backoff

    async def _save_context(self, context: PipelineContext):
        """컨텍스트 저장 with S3 fallback for large items"""
        try:
            context_dict = context.to_dict()
            
            # Calculate item size
            item_size = len(json.dumps(context_dict).encode('utf-8'))
            
            if item_size > MAX_DYNAMODB_ITEM_SIZE:
                # Save large intermediate results to S3
                s3_key = f"contexts/{context.session_id}/{int(time.time())}.json"
                
                s3.put_object(
                    Bucket=S3_BUCKET_NAME,
                    Key=s3_key,
                    Body=json.dumps(context.intermediate_results),
                    ContentType='application/json'
                )
                
                # Save reference to DynamoDB
                context_dict["intermediate_results"] = {
                    "type": "s3_reference",
                    "bucket": S3_BUCKET_NAME,
                    "key": s3_key,
                    "size": item_size
                }
            
            self.table.put_item(
                Item={
                    **context_dict,
                    "timestamp": int(time.time()),
                    "ttl": int(time.time()) + 86400 * 7  # 7 days TTL
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to save context: {str(e)}")
            # Continue execution even if save fails
    
    def _generate_cache_key(self, stage: str, input_data: Dict[str, Any]) -> str:
        """Generate cache key with version token"""
        # Normalize input data for consistent hashing
        normalized_input = json.dumps(input_data, sort_keys=True)
        
        # Include version token to prevent cross-version cache pollution
        cache_data = f"{stage}:{AGENT_VERSION}:{normalized_input}"
        
        # Generate hash
        return hashlib.sha256(cache_data.encode()).hexdigest()

    async def execute_pipeline(
        self,
        user_input: str,
        user_id: str = "anonymous",
        project_name: str = "untitled",
        config: Optional[SquadConfiguration] = None,
    ) -> Dict[str, Any]:
        """전체 파이프라인 실행"""
        config = config or SquadConfiguration()
        session_id = str(uuid.uuid4())
        
        # Initialize context
        context = PipelineContext(
            session_id=session_id,
            user_id=user_id,
            project_name=project_name,
            current_stage=PipelineStage.NL_INPUT,
            stages_completed=[],
            intermediate_results={},
            errors=[],
            metadata={"start_time": time.time()},
        )
        
        # Pipeline stages in order
        stages = [
            PipelineStage.NL_INPUT,
            PipelineStage.UI_SELECTION,
            PipelineStage.PARSER,
            PipelineStage.COMPONENT_DECISION,
            PipelineStage.MATCH_RATE,
            PipelineStage.SEARCH,
            PipelineStage.GENERATION,
            PipelineStage.ASSEMBLY,
            PipelineStage.DOWNLOAD,
        ]
        
        # Execute pipeline
        current_input = {"query": user_input}
        
        for stage in stages:
            try:
                context.current_stage = stage
                
                # Execute stage
                result = await self._execute_stage(
                    stage, current_input, context, config
                )
                
                # Store result
                context.intermediate_results[stage.value] = result
                context.stages_completed.append(stage)
                
                # Save intermediate state if configured
                if config.save_intermediate:
                    await self._save_context(context)
                
                # Prepare input for next stage
                current_input = self._prepare_next_input(
                    stage, result, context.intermediate_results
                )
                
            except Exception as e:
                logger.error(f"Pipeline failed at stage {stage}: {str(e)}")
                context.errors.append({
                    "stage": stage.value,
                    "error": str(e),
                    "timestamp": time.time()
                })
                
                if config.enable_notifications:
                    await self._send_error_notification(context, e)
                
                raise
        
        # Mark as completed
        context.current_stage = PipelineStage.COMPLETED
        context.metadata["end_time"] = time.time()
        context.metadata["duration"] = (
            context.metadata["end_time"] - context.metadata["start_time"]
        )
        
        # Final save
        await self._save_context(context)
        
        return {
            "session_id": session_id,
            "status": "completed",
            "result": context.intermediate_results.get(
                PipelineStage.DOWNLOAD.value, {}
            ),
            "duration": context.metadata["duration"],
        }

    def _prepare_next_input(
        self, 
        current_stage: PipelineStage, 
        current_result: Dict[str, Any],
        all_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare input for next stage based on current results"""
        # Map current stage results to next stage input
        stage_mapping = {
            PipelineStage.NL_INPUT: {
                "requirements": current_result
            },
            PipelineStage.UI_SELECTION: {
                "requirements": all_results.get(PipelineStage.NL_INPUT.value),
                "ui_framework": current_result,
                "input_data": all_results.get(PipelineStage.NL_INPUT.value)
            },
            PipelineStage.PARSER: {
                "parsed_structure": current_result,
                "ui_framework": all_results.get(PipelineStage.UI_SELECTION.value)
            },
            PipelineStage.COMPONENT_DECISION: {
                "requirements": all_results.get(PipelineStage.NL_INPUT.value),
                "component_specs": current_result
            },
            PipelineStage.MATCH_RATE: {
                "requirements": all_results.get(PipelineStage.NL_INPUT.value),
                "technology_stack": all_results.get(PipelineStage.UI_SELECTION.value),
                "matching_result": current_result
            },
            PipelineStage.SEARCH: {
                "search_results": current_result,
                "project_structure": all_results.get(PipelineStage.PARSER.value)
            },
            PipelineStage.GENERATION: {
                "generated_code": current_result,
                "project_config": all_results.get(PipelineStage.PARSER.value)
            },
            PipelineStage.ASSEMBLY: {
                "assembled_project": current_result,
                "project_metadata": {
                    "name": all_results.get(PipelineStage.NL_INPUT.value, {}).get("project_name"),
                    "framework": all_results.get(PipelineStage.UI_SELECTION.value, {}).get("framework")
                }
            }
        }
        
        return stage_mapping.get(current_stage, {})

    async def _send_error_notification(self, context: PipelineContext, error: Exception):
        """Send error notification via SNS"""
        try:
            message = {
                "session_id": context.session_id,
                "user_id": context.user_id,
                "project_name": context.project_name,
                "stage": context.current_stage.value,
                "error": str(error),
                "timestamp": time.time()
            }
            
            sns.publish(
                TopicArn=self.config.get("error_topic_arn"),
                Subject=f"Pipeline Error: {context.project_name}",
                Message=json.dumps(message)
            )
        except Exception as e:
            logger.error(f"Failed to send error notification: {str(e)}")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler V2 - Improved event loop handling
    Uses asyncio.run() for Python 3.7+ compatibility
    """
    try:
        # Parse request
        body = json.loads(event.get("body", "{}"))
        user_input = body.get("user_input", "")
        user_id = body.get("user_id", "anonymous")
        project_name = body.get("project_name", "untitled")
        
        # Squad configuration
        config = SquadConfiguration(
            parallel_execution=body.get("parallel", False),
            max_retries=body.get("max_retries", 3),
            timeout_seconds=body.get("timeout", 300),
        )
        
        # Initialize orchestrator
        orchestrator = AgentSquadOrchestratorV2(
            environment=event.get("environment", "production")
        )
        
        # Use asyncio.run() for better Lambda compatibility
        result = asyncio.run(
            orchestrator.execute_pipeline(
                user_input=user_input,
                user_id=user_id,
                project_name=project_name,
                config=config,
            )
        )
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(result),
        }
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({
                "error": str(e),
                "message": "Pipeline execution failed"
            }),
        }
#!/usr/bin/env python3
"""
AWS Agent Squad Integration
AWS Step Functions를 활용한 Agent 오케스트레이션
"""

import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import boto3

logger = logging.getLogger(__name__)


@dataclass
class AgentTask:
    """Agent 작업 정의"""

    agent_name: str
    task_type: str
    input_data: Dict[str, Any]
    dependencies: List[str] = None
    timeout_seconds: int = 30
    retry_count: int = 3
    priority: int = 1


@dataclass
class ExecutionResult:
    """실행 결과"""

    task_id: str
    agent_name: str
    success: bool
    result: Dict[str, Any] = None
    error: str = None
    execution_time: float = 0
    timestamp: str = None


class AWSAgentSquad:
    """AWS Agent Squad 오케스트레이션 매니저"""

    def __init__(self, region_name: str = "us-east-1"):
        self.region_name = region_name
        self.sfn_client = None
        self.lambda_client = None
        self.cloudwatch_client = None

        # Step Functions 상태 머신 ARN (환경변수에서 가져오기)
        import os

        self.state_machine_arn = os.getenv("T_DEVELOPER_STATE_MACHINE_ARN")

        self._initialize_aws_clients()

    def _initialize_aws_clients(self):
        """AWS 클라이언트 초기화"""
        try:
            # AWS 클라이언트 생성
            session = boto3.Session(region_name=self.region_name)
            self.sfn_client = session.client("stepfunctions")
            self.lambda_client = session.client("lambda")
            self.cloudwatch_client = session.client("cloudwatch")

            logger.info(f"AWS clients initialized for region: {self.region_name}")
        except Exception as e:
            logger.error(f"Failed to initialize AWS clients: {e}")

    def create_state_machine_definition(self) -> Dict[str, Any]:
        """Step Functions 상태 머신 정의 생성"""
        return {
            "Comment": "T-Developer 9-Agent Pipeline State Machine",
            "StartAt": "NLInputAgent",
            "States": {
                "NLInputAgent": {
                    "Type": "Task",
                    "Resource": "arn:aws:lambda:us-east-1:123456789012:function:t-developer-nl-input",
                    "TimeoutSeconds": 30,
                    "Retry": [
                        {
                            "ErrorEquals": ["States.TaskFailed"],
                            "IntervalSeconds": 2,
                            "MaxAttempts": 3,
                            "BackoffRate": 2.0,
                        }
                    ],
                    "Catch": [{"ErrorEquals": ["States.ALL"], "Next": "HandleError"}],
                    "Next": "UISelectionAgent",
                },
                "UISelectionAgent": {
                    "Type": "Task",
                    "Resource": "arn:aws:lambda:us-east-1:123456789012:function:t-developer-ui-selection",
                    "TimeoutSeconds": 30,
                    "Retry": [
                        {
                            "ErrorEquals": ["States.TaskFailed"],
                            "IntervalSeconds": 2,
                            "MaxAttempts": 3,
                            "BackoffRate": 2.0,
                        }
                    ],
                    "Catch": [{"ErrorEquals": ["States.ALL"], "Next": "HandleError"}],
                    "Next": "ParserAgent",
                },
                "ParserAgent": {
                    "Type": "Task",
                    "Resource": "arn:aws:lambda:us-east-1:123456789012:function:t-developer-parser",
                    "TimeoutSeconds": 30,
                    "Next": "ComponentDecisionAgent",
                },
                "ComponentDecisionAgent": {
                    "Type": "Task",
                    "Resource": "arn:aws:lambda:us-east-1:123456789012:function:t-developer-component-decision",
                    "TimeoutSeconds": 30,
                    "Next": "MatchRateAgent",
                },
                "MatchRateAgent": {
                    "Type": "Task",
                    "Resource": "arn:aws:lambda:us-east-1:123456789012:function:t-developer-match-rate",
                    "TimeoutSeconds": 30,
                    "Next": "SearchAgent",
                },
                "SearchAgent": {
                    "Type": "Task",
                    "Resource": "arn:aws:lambda:us-east-1:123456789012:function:t-developer-search",
                    "TimeoutSeconds": 30,
                    "Next": "GenerationAgent",
                },
                "GenerationAgent": {
                    "Type": "Task",
                    "Resource": "arn:aws:lambda:us-east-1:123456789012:function:t-developer-generation",
                    "TimeoutSeconds": 120,  # 생성 작업은 더 긴 시간 필요
                    "Next": "AssemblyAgent",
                },
                "AssemblyAgent": {
                    "Type": "Task",
                    "Resource": "arn:aws:lambda:us-east-1:123456789012:function:t-developer-assembly",
                    "TimeoutSeconds": 60,
                    "Next": "DownloadAgent",
                },
                "DownloadAgent": {
                    "Type": "Task",
                    "Resource": "arn:aws:lambda:us-east-1:123456789012:function:t-developer-download",
                    "TimeoutSeconds": 30,
                    "Next": "Success",
                },
                "Success": {"Type": "Succeed"},
                "HandleError": {
                    "Type": "Task",
                    "Resource": "arn:aws:lambda:us-east-1:123456789012:function:t-developer-error-handler",
                    "Next": "Fail",
                },
                "Fail": {"Type": "Fail", "Cause": "Pipeline execution failed"},
            },
        }

    async def execute_pipeline(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Agent Pipeline 실행"""
        try:
            if not self.state_machine_arn:
                logger.warning("State machine ARN not configured, using local execution")
                return await self._execute_local_pipeline(input_data)

            # Step Functions 실행 시작
            execution_name = f"t-developer-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

            response = self.sfn_client.start_execution(
                stateMachineArn=self.state_machine_arn,
                name=execution_name,
                input=json.dumps(input_data),
            )

            execution_arn = response["executionArn"]
            logger.info(f"Started pipeline execution: {execution_arn}")

            # 실행 완료까지 대기 (비동기)
            result = await self._wait_for_execution(execution_arn)
            return result

        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            return {"success": False, "error": str(e), "fallback_used": False}

    async def _wait_for_execution(self, execution_arn: str) -> Dict[str, Any]:
        """Step Functions 실행 완료 대기"""
        max_wait_time = 300  # 5분 최대 대기
        check_interval = 5  # 5초마다 확인
        elapsed_time = 0

        while elapsed_time < max_wait_time:
            try:
                response = self.sfn_client.describe_execution(executionArn=execution_arn)

                status = response["status"]

                if status == "SUCCEEDED":
                    output = json.loads(response.get("output", "{}"))
                    return {
                        "success": True,
                        "result": output,
                        "execution_arn": execution_arn,
                        "duration": elapsed_time,
                    }
                elif status in ["FAILED", "TIMED_OUT", "ABORTED"]:
                    error = response.get("error", "Unknown error")
                    return {
                        "success": False,
                        "error": error,
                        "execution_arn": execution_arn,
                        "status": status,
                    }

                # 아직 실행 중
                await asyncio.sleep(check_interval)
                elapsed_time += check_interval

            except Exception as e:
                logger.error(f"Error checking execution status: {e}")
                break

        # 타임아웃
        return {
            "success": False,
            "error": "Execution timeout",
            "execution_arn": execution_arn,
        }

    async def _execute_local_pipeline(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """로컬 파이프라인 실행 (AWS 없이)"""
        logger.info("Executing pipeline locally (fallback mode)")

        # 9-Agent 순서대로 실행
        agents = [
            "nl_input",
            "ui_selection",
            "parser",
            "component_decision",
            "match_rate",
            "search",
            "generation",
            "assembly",
            "download",
        ]

        pipeline_result = {
            "success": True,
            "steps": [],
            "final_result": input_data.copy(),
        }

        current_data = input_data.copy()

        for i, agent_name in enumerate(agents):
            try:
                start_time = datetime.now()

                # 에이전트 실행 시뮬레이션
                step_result = await self._execute_agent_locally(agent_name, current_data)

                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()

                step_info = {
                    "step": i + 1,
                    "agent": agent_name,
                    "success": step_result.get("success", True),
                    "execution_time": execution_time,
                    "timestamp": end_time.isoformat(),
                }

                if step_result.get("success", True):
                    # 결과를 다음 단계로 전달
                    current_data.update(step_result.get("result", {}))
                    step_info["result"] = step_result.get("result", {})
                else:
                    step_info["error"] = step_result.get("error", "Unknown error")
                    pipeline_result["success"] = False
                    break

                pipeline_result["steps"].append(step_info)

                # 진행률 로깅
                progress = ((i + 1) / len(agents)) * 100
                logger.info(f"Pipeline progress: {progress:.1f}% - {agent_name} completed")

            except Exception as e:
                logger.error(f"Error executing agent {agent_name}: {e}")
                pipeline_result["success"] = False
                pipeline_result["steps"].append(
                    {
                        "step": i + 1,
                        "agent": agent_name,
                        "success": False,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }
                )
                break

        pipeline_result["final_result"] = current_data
        return pipeline_result

    async def _execute_agent_locally(
        self, agent_name: str, input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """로컬 Agent 실행"""
        # 간단한 Agent 로직 시뮬레이션
        await asyncio.sleep(0.1)  # 작업 시간 시뮬레이션

        agent_results = {
            "nl_input": {
                "success": True,
                "result": {
                    "parsed_requirements": input_data.get("user_input", ""),
                    "project_type": "web_application",
                    "complexity_level": "medium",
                },
            },
            "ui_selection": {
                "success": True,
                "result": {
                    "framework": input_data.get("project_type", "react"),
                    "ui_library": "react",
                    "styling": "css",
                },
            },
            "parser": {
                "success": True,
                "result": {
                    "components": ["App", "TodoList", "TodoItem"],
                    "routes": ["/", "/todos"],
                    "state_structure": {"todos": "array"},
                },
            },
            "component_decision": {
                "success": True,
                "result": {
                    "selected_components": ["functional_components"],
                    "architecture": "single_page_app",
                },
            },
            "match_rate": {
                "success": True,
                "result": {"match_score": 0.85, "confidence": "high"},
            },
            "search": {
                "success": True,
                "result": {"templates_found": 3, "best_match": "react-todo-template"},
            },
            "generation": {
                "success": True,
                "result": {"generated_files": 12, "code_quality_score": 90},
            },
            "assembly": {
                "success": True,
                "result": {"bundle_size": "2.5MB", "optimization_applied": True},
            },
            "download": {
                "success": True,
                "result": {"download_ready": True, "package_size": "2.8MB"},
            },
        }

        return agent_results.get(
            agent_name, {"success": False, "error": f"Unknown agent: {agent_name}"}
        )

    async def get_execution_metrics(self, execution_arn: str = None) -> Dict[str, Any]:
        """실행 메트릭 조회"""
        if not execution_arn:
            return {"error": "Execution ARN required"}

        try:
            # Step Functions 실행 히스토리 조회
            response = self.sfn_client.get_execution_history(executionArn=execution_arn)

            events = response["events"]
            metrics = {
                "total_events": len(events),
                "execution_time": 0,
                "agent_metrics": {},
                "error_count": 0,
            }

            # 이벤트 분석
            for event in events:
                event_type = event["type"]

                if "Failed" in event_type:
                    metrics["error_count"] += 1

                # 개별 Agent 메트릭 수집
                if "Task" in event_type and "StateEntered" in event_type:
                    state_name = event.get("stateEnteredEventDetails", {}).get("name")
                    if state_name:
                        metrics["agent_metrics"][state_name] = {
                            "timestamp": event["timestamp"].isoformat()
                        }

            return metrics

        except Exception as e:
            logger.error(f"Failed to get execution metrics: {e}")
            return {"error": str(e)}

    async def stop_execution(self, execution_arn: str, reason: str = "User requested") -> bool:
        """실행 중단"""
        try:
            self.sfn_client.stop_execution(
                executionArn=execution_arn, error="ExecutionStopped", cause=reason
            )
            return True
        except Exception as e:
            logger.error(f"Failed to stop execution: {e}")
            return False

    def send_cloudwatch_metrics(self, metrics: Dict[str, Any]):
        """CloudWatch 메트릭 전송"""
        try:
            metric_data = []

            for metric_name, value in metrics.items():
                if isinstance(value, (int, float)):
                    metric_data.append(
                        {
                            "MetricName": metric_name,
                            "Value": value,
                            "Unit": "Count",
                            "Timestamp": datetime.now(),
                        }
                    )

            if metric_data:
                self.cloudwatch_client.put_metric_data(
                    Namespace="T-Developer/Pipeline", MetricData=metric_data
                )
                logger.info(f"Sent {len(metric_data)} metrics to CloudWatch")

        except Exception as e:
            logger.error(f"Failed to send CloudWatch metrics: {e}")


# 글로벌 인스턴스
aws_agent_squad = AWSAgentSquad()


async def initialize_aws_agent_squad() -> bool:
    """AWS Agent Squad 초기화"""
    try:
        # AWS 연결 테스트
        if aws_agent_squad.sfn_client:
            # Step Functions 서비스 가용성 확인
            try:
                aws_agent_squad.sfn_client.list_state_machines(maxResults=1)
                logger.info("AWS Agent Squad initialized successfully")
                return True
            except Exception as e:
                logger.warning(f"AWS Step Functions not available: {e}")
                return False
        else:
            logger.warning("AWS clients not initialized")
            return False

    except Exception as e:
        logger.error(f"Failed to initialize AWS Agent Squad: {e}")
        return False


if __name__ == "__main__":

    async def test_aws_agent_squad():
        """AWS Agent Squad 테스트"""
        # 초기화
        success = await initialize_aws_agent_squad()
        print(f"AWS Agent Squad initialized: {success}")

        # 테스트 파이프라인 실행
        test_input = {
            "user_input": "Create a todo app with React",
            "project_type": "react",
            "features": ["todo", "routing"],
        }

        result = await aws_agent_squad.execute_pipeline(test_input)
        print("Pipeline result:", result)

    asyncio.run(test_aws_agent_squad())

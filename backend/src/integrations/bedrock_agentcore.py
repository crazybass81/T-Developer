#!/usr/bin/env python3
"""
AWS Bedrock AgentCore Integration
T-Developer의 3대 핵심 프레임워크 중 하나인 AWS Bedrock AgentCore 통합
"""

import asyncio
import json
import logging
import os
import uuid
from contextlib import asynccontextmanager
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional

import boto3

logger = logging.getLogger(__name__)


@dataclass
class AgentCoreConfig:
    """Bedrock AgentCore 설정"""

    agent_id: str
    agent_alias_id: str
    region: str = "us-east-1"
    knowledge_base_id: Optional[str] = None
    session_timeout: int = 3600  # 1시간
    max_retries: int = 3

    @classmethod
    def from_env(cls) -> "AgentCoreConfig":
        """환경변수에서 설정 로드"""
        return cls(
            agent_id=os.getenv("BEDROCK_AGENT_ID", ""),
            agent_alias_id=os.getenv("BEDROCK_AGENT_ALIAS_ID", ""),
            region=os.getenv("AWS_REGION", "us-east-1"),
            knowledge_base_id=os.getenv("BEDROCK_KNOWLEDGE_BASE_ID"),
        )


@dataclass
class AgentSession:
    """Agent 세션"""

    session_id: str
    user_id: str
    created_at: datetime
    last_active: datetime
    session_attributes: Dict[str, str]
    conversation_history: List[Dict[str, Any]]


@dataclass
class AgentResponse:
    """Agent 응답"""

    session_id: str
    response_text: str
    completion_reason: str
    trace: List[Dict[str, Any]]
    citations: List[Dict[str, Any]]
    session_attributes: Dict[str, str]
    execution_time: float
    timestamp: datetime


class BedrockAgentCoreClient:
    """AWS Bedrock AgentCore 클라이언트"""

    def __init__(self, config: AgentCoreConfig):
        self.config = config
        self.sessions: Dict[str, AgentSession] = {}

        # Bedrock 클라이언트 초기화
        try:
            self.bedrock_agent_runtime = boto3.client(
                "bedrock-agent-runtime", region_name=config.region
            )

            self.bedrock_agent = boto3.client("bedrock-agent", region_name=config.region)

            logger.info(f"Bedrock AgentCore initialized: agent_id={config.agent_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock clients: {e}")
            self.bedrock_agent_runtime = None
            self.bedrock_agent = None

    def is_available(self) -> bool:
        """Bedrock AgentCore 사용 가능 여부"""
        return (
            self.bedrock_agent_runtime is not None
            and self.config.agent_id
            and self.config.agent_alias_id
        )

    async def create_session(self, user_id: str, context: Dict[str, Any] = None) -> str:
        """새 세션 생성"""
        session_id = f"t-developer-{user_id}-{uuid.uuid4().hex[:8]}"

        session = AgentSession(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.now(),
            last_active=datetime.now(),
            session_attributes=context or {},
            conversation_history=[],
        )

        self.sessions[session_id] = session
        logger.info(f"Created session: {session_id} for user: {user_id}")

        return session_id

    async def invoke_agent(
        self,
        session_id: str,
        input_text: str,
        enable_trace: bool = True,
        end_session: bool = False,
    ) -> AgentResponse:
        """Agent 호출"""
        if not self.is_available():
            raise RuntimeError("Bedrock AgentCore not available")

        if session_id not in self.sessions:
            raise ValueError(f"Session not found: {session_id}")

        session = self.sessions[session_id]
        start_time = datetime.now()

        try:
            # Bedrock Agent 호출
            response = self.bedrock_agent_runtime.invoke_agent(
                agentId=self.config.agent_id,
                agentAliasId=self.config.agent_alias_id,
                sessionId=session_id,
                inputText=input_text,
                enableTrace=enable_trace,
                endSession=end_session,
                sessionState={"sessionAttributes": session.session_attributes},
            )

            # 응답 스트림 처리
            response_text = ""
            completion_reason = ""
            trace_data = []
            citations = []

            if "completion" in response:
                async for chunk in self._process_response_stream(response["completion"]):
                    if chunk["type"] == "chunk":
                        if "bytes" in chunk["data"]:
                            response_text += chunk["data"]["bytes"].decode("utf-8")
                    elif chunk["type"] == "trace":
                        trace_data.append(chunk["data"])
                    elif chunk["type"] == "return_control":
                        completion_reason = chunk["data"].get("invocationId", "completed")

            execution_time = (datetime.now() - start_time).total_seconds()

            # 세션 업데이트
            session.last_active = datetime.now()
            session.conversation_history.append(
                {
                    "input": input_text,
                    "output": response_text,
                    "timestamp": datetime.now().isoformat(),
                    "execution_time": execution_time,
                }
            )

            agent_response = AgentResponse(
                session_id=session_id,
                response_text=response_text,
                completion_reason=completion_reason,
                trace=trace_data,
                citations=citations,
                session_attributes=session.session_attributes,
                execution_time=execution_time,
                timestamp=datetime.now(),
            )

            logger.info(f"Agent invocation completed: {session_id}, time: {execution_time:.2f}s")
            return agent_response

        except Exception as e:
            logger.error(f"Agent invocation failed: {session_id}, error: {e}")

            # 에러 응답 생성
            execution_time = (datetime.now() - start_time).total_seconds()
            return AgentResponse(
                session_id=session_id,
                response_text=f"에이전트 호출 중 오류가 발생했습니다: {str(e)}",
                completion_reason="error",
                trace=[],
                citations=[],
                session_attributes=session.session_attributes,
                execution_time=execution_time,
                timestamp=datetime.now(),
            )

    async def _process_response_stream(
        self, completion_stream
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """응답 스트림 처리"""
        try:
            for event in completion_stream:
                if "chunk" in event:
                    yield {"type": "chunk", "data": event["chunk"]}
                elif "trace" in event:
                    yield {"type": "trace", "data": event["trace"]}
                elif "returnControl" in event:
                    yield {"type": "return_control", "data": event["returnControl"]}
        except Exception as e:
            logger.error(f"Error processing response stream: {e}")
            yield {"type": "error", "data": {"error": str(e)}}

    async def retrieve_knowledge(
        self, query: str, knowledge_base_id: str = None, number_of_results: int = 5
    ) -> Dict[str, Any]:
        """지식베이스 검색"""
        kb_id = knowledge_base_id or self.config.knowledge_base_id

        if not kb_id:
            raise ValueError("Knowledge base ID not configured")

        try:
            response = self.bedrock_agent_runtime.retrieve(
                knowledgeBaseId=kb_id,
                retrievalQuery={"text": query},
                retrievalConfiguration={
                    "vectorSearchConfiguration": {"numberOfResults": number_of_results}
                },
            )

            results = []
            for result in response.get("retrievalResults", []):
                results.append(
                    {
                        "content": result.get("content", {}).get("text", ""),
                        "location": result.get("location", {}),
                        "score": result.get("score", 0.0),
                        "metadata": result.get("metadata", {}),
                    }
                )

            return {
                "query": query,
                "results": results,
                "knowledge_base_id": kb_id,
                "retrieved_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Knowledge retrieval failed: {e}")
            return {
                "query": query,
                "results": [],
                "error": str(e),
                "retrieved_at": datetime.now().isoformat(),
            }

    async def get_agent_info(self) -> Dict[str, Any]:
        """Agent 정보 조회"""
        if not self.is_available():
            return {"error": "Bedrock AgentCore not available"}

        try:
            response = self.bedrock_agent.get_agent(agentId=self.config.agent_id)

            agent_info = response.get("agent", {})

            return {
                "agent_id": agent_info.get("agentId"),
                "agent_name": agent_info.get("agentName"),
                "agent_arn": agent_info.get("agentArn"),
                "agent_status": agent_info.get("agentStatus"),
                "foundation_model": agent_info.get("foundationModel"),
                "description": agent_info.get("description"),
                "instruction": agent_info.get("instruction"),
                "created_at": agent_info.get("createdAt"),
                "updated_at": agent_info.get("updatedAt"),
                "prepared_at": agent_info.get("preparedAt"),
                "idle_session_ttl": agent_info.get("idleSessionTTLInSeconds"),
            }

        except Exception as e:
            logger.error(f"Failed to get agent info: {e}")
            return {"error": str(e)}

    async def close_session(self, session_id: str):
        """세션 종료"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Session closed: {session_id}")

    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """세션 정보 조회"""
        if session_id not in self.sessions:
            return {"error": "Session not found"}

        session = self.sessions[session_id]
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "created_at": session.created_at.isoformat(),
            "last_active": session.last_active.isoformat(),
            "conversation_count": len(session.conversation_history),
            "session_attributes": session.session_attributes,
        }

    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """모든 세션 정보 조회"""
        return [self.get_session_info(session_id) for session_id in self.sessions.keys()]


class BedrockAgentCoreIntegration:
    """Bedrock AgentCore T-Developer 통합"""

    def __init__(self):
        self.config = AgentCoreConfig.from_env()
        self.client = BedrockAgentCoreClient(self.config)
        self.agent_sessions = {}  # agent_name -> session_id 매핑

    async def initialize(self) -> bool:
        """통합 초기화"""
        try:
            if not self.client.is_available():
                logger.warning("Bedrock AgentCore not available, using fallback mode")
                return False

            # Agent 정보 확인
            agent_info = await self.client.get_agent_info()
            if "error" in agent_info:
                logger.error(f"Failed to verify agent: {agent_info['error']}")
                return False

            logger.info(f"Bedrock AgentCore integration initialized: {agent_info['agent_name']}")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Bedrock AgentCore: {e}")
            return False

    async def execute_agent_with_bedrock(
        self, agent_name: str, user_input: str, user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """Bedrock을 통한 Agent 실행"""
        try:
            # 세션 가져오기 또는 생성
            session_id = self.agent_sessions.get(agent_name)
            if not session_id:
                session_id = await self.client.create_session(
                    user_id, {"agent_name": agent_name, "framework": "t-developer"}
                )
                self.agent_sessions[agent_name] = session_id

            # Agent별 입력 포맷팅
            formatted_input = self._format_input_for_agent(agent_name, user_input)

            # Bedrock Agent 호출
            response = await self.client.invoke_agent(session_id, formatted_input)

            # 응답 처리
            processed_result = self._process_agent_response(agent_name, response)

            return {
                "success": True,
                "agent_name": agent_name,
                "result": processed_result,
                "session_id": session_id,
                "execution_time": response.execution_time,
                "timestamp": response.timestamp.isoformat(),
            }

        except Exception as e:
            logger.error(f"Bedrock agent execution failed: {agent_name}, error: {e}")
            return {
                "success": False,
                "agent_name": agent_name,
                "error": str(e),
                "fallback_used": True,
            }

    def _format_input_for_agent(self, agent_name: str, user_input: str) -> str:
        """Agent별 입력 포맷팅"""
        agent_prompts = {
            "nl_input": f"""
자연어 입력을 분석하여 프로젝트 요구사항을 추출해주세요.

입력: {user_input}

다음 정보를 JSON 형식으로 반환해주세요:
- project_type: 프로젝트 유형 (web_app, mobile_app, api, etc.)
- features: 요구된 기능들의 배열
- complexity: 복잡도 (simple, medium, complex)
- framework_preferences: 선호하는 프레임워크
- ui_requirements: UI/UX 요구사항
            """,
            "ui_selection": f"""
프로젝트 요구사항을 바탕으로 최적의 UI 프레임워크를 선택해주세요.

요구사항: {user_input}

다음 중에서 선택하고 이유를 설명해주세요:
- React: 컴포넌트 기반, 큰 생태계
- Vue.js: 쉬운 학습곡선, 점진적 적용
- Next.js: SSR, 성능 최적화
- Angular: 엔터프라이즈 급 기능

JSON 형식으로 반환:
{"framework": "선택된 프레임워크", "reason": "선택 이유", "additional_libraries": ["추가 라이브러리들"]}
            """,
            "generation": f"""
프로젝트 명세를 바탕으로 실제 코드를 생성해주세요.

요구사항: {user_input}

생성해야 할 항목:
- 프로젝트 구조
- 핵심 컴포넌트 코드
- 설정 파일들
- README 및 문서

결과를 다음 형식으로 반환:
{"files": [{"path": "파일경로", "content": "파일내용"}], "structure": "프로젝트구조", "instructions": "설치및실행방법"}
            """,
        }

        return agent_prompts.get(agent_name, f"다음 작업을 수행해주세요: {user_input}")

    def _process_agent_response(self, agent_name: str, response: AgentResponse) -> Dict[str, Any]:
        """Agent 응답 처리"""
        try:
            # JSON 응답 파싱 시도
            import re

            json_match = re.search(r"\{.*\}", response.response_text, re.DOTALL)
            if json_match:
                try:
                    parsed_json = json.loads(json_match.group())
                    return {
                        "parsed_response": parsed_json,
                        "raw_response": response.response_text,
                        "completion_reason": response.completion_reason,
                        "citations": response.citations,
                    }
                except json.JSONDecodeError:
                    pass

            # JSON 파싱 실패시 원본 응답 반환
            return {
                "raw_response": response.response_text,
                "completion_reason": response.completion_reason,
                "citations": response.citations,
                "trace": response.trace[:5] if response.trace else [],  # 처음 5개만
            }

        except Exception as e:
            logger.error(f"Error processing agent response: {e}")
            return {"raw_response": response.response_text, "error": str(e)}

    async def enhance_pipeline_with_bedrock(self, pipeline_input: Dict[str, Any]) -> Dict[str, Any]:
        """Bedrock으로 파이프라인 강화"""
        enhanced_steps = []
        user_input = pipeline_input.get("user_input", "")
        user_id = pipeline_input.get("user_id", "anonymous")

        # 주요 Agent들만 Bedrock으로 처리
        bedrock_agents = ["nl_input", "ui_selection", "generation"]

        for agent_name in bedrock_agents:
            try:
                result = await self.execute_agent_with_bedrock(agent_name, user_input, user_id)
                enhanced_steps.append(
                    {"agent": agent_name, "bedrock_enhanced": True, "result": result}
                )
            except Exception as e:
                logger.error(f"Bedrock enhancement failed for {agent_name}: {e}")
                enhanced_steps.append(
                    {"agent": agent_name, "bedrock_enhanced": False, "error": str(e)}
                )

        return {
            "enhanced_steps": enhanced_steps,
            "bedrock_integration": True,
            "timestamp": datetime.now().isoformat(),
        }

    async def cleanup_sessions(self):
        """세션 정리"""
        for session_id in list(self.agent_sessions.values()):
            await self.client.close_session(session_id)
        self.agent_sessions.clear()

    def get_integration_status(self) -> Dict[str, Any]:
        """통합 상태 조회"""
        return {
            "bedrock_available": self.client.is_available(),
            "agent_id": self.config.agent_id,
            "agent_alias_id": self.config.agent_alias_id,
            "region": self.config.region,
            "active_sessions": len(self.client.sessions),
            "agent_sessions": len(self.agent_sessions),
            "knowledge_base_configured": bool(self.config.knowledge_base_id),
        }


# 글로벌 인스턴스
bedrock_integration = BedrockAgentCoreIntegration()


async def initialize_bedrock_agentcore() -> bool:
    """Bedrock AgentCore 초기화"""
    try:
        return await bedrock_integration.initialize()
    except Exception as e:
        logger.error(f"Failed to initialize Bedrock AgentCore: {e}")
        return False


if __name__ == "__main__":

    async def test_bedrock_integration():
        """Bedrock 통합 테스트"""
        # 초기화
        success = await initialize_bedrock_agentcore()
        print(f"Bedrock AgentCore initialized: {success}")

        if success:
            # 상태 확인
            status = bedrock_integration.get_integration_status()
            print("Integration status:", json.dumps(status, indent=2))

            # Agent 테스트
            result = await bedrock_integration.execute_agent_with_bedrock(
                "nl_input", "Create a todo app with React and TypeScript", "test-user"
            )
            print("Agent result:", json.dumps(result, indent=2, default=str))

            # 정리
            await bedrock_integration.cleanup_sessions()

        print("Test completed")

    asyncio.run(test_bedrock_integration())

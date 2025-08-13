#!/usr/bin/env python3
"""
Agno Framework Integration Client
T-Developer에서 Agno 프레임워크를 사용하기 위한 클라이언트
"""

import os
import yaml
import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path
import httpx
import logging

logger = logging.getLogger(__name__)


class AgnoClient:
    """Agno Framework 통합 클라이언트"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = (
            config_path or Path(__file__).parent.parent.parent / "agno.config.yaml"
        )
        self.config = self._load_config()
        self.base_url = self.config.get("agno_api", {}).get(
            "base_url", "http://localhost:8080"
        )
        self.timeout = self.config.get("agno_api", {}).get("timeout", 30)
        self.client = httpx.AsyncClient(timeout=self.timeout)

    def _load_config(self) -> Dict[str, Any]:
        """Agno 설정 로드"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            else:
                logger.warning(f"Agno config not found: {self.config_path}")
                return self._get_default_config()
        except Exception as e:
            logger.error(f"Failed to load Agno config: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """기본 설정 반환"""
        return {
            "agno_api": {
                "base_url": "http://localhost:8080",
                "timeout": 30,
                "max_retries": 3,
            },
            "agents": {
                "nl_input": {
                    "enabled": True,
                    "model": "gpt-3.5-turbo",
                    "max_tokens": 1000,
                },
                "ui_selection": {
                    "enabled": True,
                    "frameworks": ["react", "vue", "nextjs"],
                    "default_framework": "react",
                },
                "generation": {
                    "enabled": True,
                    "template_path": "./templates",
                    "optimization_level": "standard",
                },
            },
            "performance": {
                "max_memory_mb": 100,
                "execution_timeout": 30,
                "parallel_agents": 3,
            },
        }

    async def health_check(self) -> bool:
        """Agno 서비스 헬스 체크"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Agno health check failed: {e}")
            return False

    async def create_agent(
        self, agent_type: str, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Agno에서 Agent 생성"""
        try:
            payload = {
                "type": agent_type,
                "config": config,
                "performance_settings": self.config.get("performance", {}),
            }

            response = await self.client.post(
                f"{self.base_url}/agents/create", json=payload
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to create agent: {response.text}")
                return {"success": False, "error": response.text}

        except Exception as e:
            logger.error(f"Agent creation failed: {e}")
            return {"success": False, "error": str(e)}

    async def execute_agent(
        self, agent_id: str, input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Agent 실행"""
        try:
            payload = {
                "agent_id": agent_id,
                "input": input_data,
                "timeout": self.timeout,
            }

            response = await self.client.post(
                f"{self.base_url}/agents/execute", json=payload
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Agent execution failed: {response.text}")
                return {"success": False, "error": response.text}

        except Exception as e:
            logger.error(f"Agent execution error: {e}")
            return {"success": False, "error": str(e)}

    async def get_agent_metrics(self, agent_id: str) -> Dict[str, Any]:
        """Agent 성능 메트릭 조회"""
        try:
            response = await self.client.get(
                f"{self.base_url}/agents/{agent_id}/metrics"
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": "Metrics not available"}

        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return {"success": False, "error": str(e)}

    async def optimize_agent(
        self, agent_id: str, optimization_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Agent 최적화"""
        try:
            payload = {"agent_id": agent_id, "optimization": optimization_config}

            response = await self.client.post(
                f"{self.base_url}/agents/optimize", json=payload
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": response.text}

        except Exception as e:
            logger.error(f"Agent optimization failed: {e}")
            return {"success": False, "error": str(e)}

    async def delete_agent(self, agent_id: str) -> bool:
        """Agent 삭제"""
        try:
            response = await self.client.delete(f"{self.base_url}/agents/{agent_id}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to delete agent: {e}")
            return False

    async def close(self):
        """클라이언트 연결 종료"""
        await self.client.aclose()


class AgnoAgentManager:
    """Agno Agent 관리자"""

    def __init__(self, agno_client: AgnoClient):
        self.client = agno_client
        self.agents = {}  # agent_type -> agent_id 매핑

    async def initialize_agents(self) -> Dict[str, str]:
        """9-Agent Pipeline용 Agent들 초기화"""
        agent_configs = {
            "nl_input": {
                "model": "gpt-3.5-turbo",
                "max_tokens": 500,
                "tasks": ["parse_natural_language", "extract_requirements"],
            },
            "ui_selection": {
                "frameworks": ["react", "vue", "nextjs"],
                "selection_criteria": ["complexity", "performance", "popularity"],
            },
            "parser": {
                "parsing_rules": ["components", "routing", "state"],
                "validation": True,
            },
            "component_decision": {
                "component_library": "standard",
                "reusability_threshold": 0.7,
            },
            "match_rate": {"similarity_algorithm": "cosine", "threshold": 0.8},
            "search": {"search_engines": ["github", "npm", "cdnjs"], "max_results": 10},
            "generation": {
                "template_engine": "jinja2",
                "code_style": "prettier",
                "optimization": True,
            },
            "assembly": {
                "bundler": "webpack",
                "minification": True,
                "tree_shaking": True,
            },
            "download": {
                "compression": "zip",
                "compression_level": 9,
                "include_docs": True,
            },
        }

        created_agents = {}

        for agent_type, config in agent_configs.items():
            try:
                result = await self.client.create_agent(agent_type, config)
                if result.get("success", False):
                    agent_id = result.get("agent_id")
                    self.agents[agent_type] = agent_id
                    created_agents[agent_type] = agent_id
                    logger.info(f"Created Agno agent: {agent_type} -> {agent_id}")
                else:
                    logger.error(
                        f"Failed to create agent {agent_type}: {result.get('error')}"
                    )
            except Exception as e:
                logger.error(f"Error creating agent {agent_type}: {e}")

        return created_agents

    async def execute_pipeline(
        self, user_input: str, project_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """9-Agent Pipeline 실행"""
        pipeline_result = {"steps": [], "final_result": None}

        # Agent 실행 순서
        pipeline_steps = [
            ("nl_input", {"query": user_input, "project_config": project_config}),
            ("ui_selection", {}),
            ("parser", {}),
            ("component_decision", {}),
            ("match_rate", {}),
            ("search", {}),
            ("generation", {}),
            ("assembly", {}),
            ("download", {}),
        ]

        current_data = {"user_input": user_input, "project_config": project_config}

        for step_name, step_input in pipeline_steps:
            if step_name not in self.agents:
                logger.warning(f"Agent {step_name} not initialized, skipping")
                continue

            try:
                agent_id = self.agents[step_name]

                # 이전 단계 결과를 현재 단계 입력에 포함
                combined_input = {**step_input, **current_data}

                logger.info(f"Executing agent: {step_name}")
                result = await self.client.execute_agent(agent_id, combined_input)

                if result.get("success", False):
                    step_result = {
                        "step": step_name,
                        "success": True,
                        "result": result.get("result", {}),
                        "metrics": result.get("metrics", {}),
                    }

                    # 다음 단계를 위해 결과 업데이트
                    current_data.update(result.get("result", {}))
                else:
                    step_result = {
                        "step": step_name,
                        "success": False,
                        "error": result.get("error", "Unknown error"),
                    }
                    logger.error(f"Agent {step_name} failed: {result.get('error')}")

                pipeline_result["steps"].append(step_result)

                # 실패 시 파이프라인 중단
                if not result.get("success", False):
                    break

            except Exception as e:
                logger.error(f"Pipeline step {step_name} error: {e}")
                pipeline_result["steps"].append(
                    {"step": step_name, "success": False, "error": str(e)}
                )
                break

        pipeline_result["final_result"] = current_data
        return pipeline_result

    async def get_pipeline_metrics(self) -> Dict[str, Any]:
        """파이프라인 전체 성능 메트릭"""
        metrics = {}

        for agent_type, agent_id in self.agents.items():
            try:
                agent_metrics = await self.client.get_agent_metrics(agent_id)
                metrics[agent_type] = agent_metrics
            except Exception as e:
                logger.error(f"Failed to get metrics for {agent_type}: {e}")
                metrics[agent_type] = {"error": str(e)}

        return metrics

    async def cleanup(self):
        """리소스 정리"""
        for agent_type, agent_id in self.agents.items():
            try:
                await self.client.delete_agent(agent_id)
                logger.info(f"Deleted agent: {agent_type}")
            except Exception as e:
                logger.error(f"Failed to delete agent {agent_type}: {e}")

        await self.client.close()


# 글로벌 인스턴스
agno_client = AgnoClient()
agno_manager = AgnoAgentManager(agno_client)


async def initialize_agno():
    """Agno 시스템 초기화"""
    try:
        # 헬스 체크
        if not await agno_client.health_check():
            logger.warning("Agno service not available, using fallback mode")
            return False

        # Agent 초기화
        created_agents = await agno_manager.initialize_agents()
        logger.info(f"Initialized {len(created_agents)} Agno agents")

        return len(created_agents) > 0

    except Exception as e:
        logger.error(f"Failed to initialize Agno: {e}")
        return False


if __name__ == "__main__":

    async def test_agno():
        """Agno 통합 테스트"""
        success = await initialize_agno()
        if success:
            print("Agno integration successful!")

            # 테스트 파이프라인 실행
            test_result = await agno_manager.execute_pipeline(
                "Create a todo app", {"framework": "react", "features": ["todo"]}
            )

            print("Pipeline result:", test_result)

        await agno_manager.cleanup()

    asyncio.run(test_agno())

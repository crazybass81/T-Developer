#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T-Developer Parameter Store Integration Example
실제 Evolution System에서 Parameter Store 클라이언트를 사용하는 예제

TDD REFACTOR Phase: 실제 사용 케이스 및 통합 패턴
이 파일은 다음을 보여줍니다:
1. Evolution Engine 설정 관리
2. Agent별 파라미터 관리
3. 환경별 설정 분리
4. 실시간 설정 업데이트
5. 계층적 설정 구조 활용
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass

try:
    from .parameter_store_client import (
        ParameterStoreClient,
        get_client,
        get_parameter_value,
    )
    from .config import get_config, initialize_security
except ImportError:
    from parameter_store_client import (
        ParameterStoreClient,
        get_client,
        get_parameter_value,
    )
    from config import get_config, initialize_security

logger = logging.getLogger(__name__)


@dataclass
class EvolutionConfig:
    """Evolution Engine 설정"""

    ai_autonomy_level: float = 0.85
    max_agent_memory_kb: float = 6.5
    instantiation_target_us: float = 3.0
    evolution_enabled: bool = True
    safety_threshold: float = 0.95

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvolutionConfig":
        """딕셔너리에서 설정 생성"""
        return cls(
            ai_autonomy_level=float(data.get("ai_autonomy_level", 0.85)),
            max_agent_memory_kb=float(data.get("max_agent_memory_kb", 6.5)),
            instantiation_target_us=float(data.get("instantiation_target_us", 3.0)),
            evolution_enabled=bool(data.get("evolution_enabled", True)),
            safety_threshold=float(data.get("safety_threshold", 0.95)),
        )


class EvolutionParameterManager:
    """Evolution Engine 파라미터 관리"""

    def __init__(self):
        self.config = get_config()
        self.parameter_client = get_client(self.config.to_parameter_client_config())
        self._cached_configs = {}

    def get_parameter_path(self, component: str, setting: str = "config") -> str:
        """파라미터 경로 생성"""
        return f"/{self.config.project_name}/{self.config.environment}/{component}/{setting}"

    async def get_evolution_config(self) -> EvolutionConfig:
        """Evolution Engine 설정 조회"""
        try:
            param_path = self.get_parameter_path("evolution/engine")
            parameter = await self.parameter_client.get_parameter_async(param_path)

            if "parsed_value" in parameter and isinstance(
                parameter["parsed_value"], dict
            ):
                return EvolutionConfig.from_dict(parameter["parsed_value"])
            else:
                logger.warning("Evolution config not in expected JSON format")
                return EvolutionConfig()  # 기본값 사용

        except Exception as e:
            logger.error(f"Failed to get evolution config: {e}")
            return self._get_fallback_evolution_config()

    async def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """특정 Agent 설정 조회"""
        try:
            param_path = self.get_parameter_path(f"agents/{agent_name}")
            parameter = await self.parameter_client.get_parameter_async(param_path)

            if "parsed_value" in parameter:
                return parameter["parsed_value"]
            else:
                logger.warning(f"Agent {agent_name} config not in expected format")
                return {}

        except Exception as e:
            logger.error(f"Failed to get agent {agent_name} config: {e}")
            return self._get_fallback_agent_config(agent_name)

    async def get_all_agent_configs(self) -> Dict[str, Dict[str, Any]]:
        """모든 Agent 설정 조회"""
        try:
            agents_path = self.get_parameter_path("agents")[:-7]  # '/config' 제거
            parameters = self.parameter_client.get_parameters_by_path(agents_path)

            agent_configs = {}
            for param in parameters:
                # '/project/env/agents/agent_name/config' -> 'agent_name' 추출
                path_parts = param["Name"].split("/")
                if len(path_parts) >= 5 and path_parts[-1] == "config":
                    agent_name = path_parts[-2]
                    if "parsed_value" in param:
                        agent_configs[agent_name] = param["parsed_value"]

            return agent_configs

        except Exception as e:
            logger.error(f"Failed to get all agent configs: {e}")
            return {}

    async def get_workflow_config(self, workflow_name: str) -> Dict[str, Any]:
        """워크플로우 설정 조회"""
        try:
            param_path = self.get_parameter_path(f"workflows/{workflow_name}")
            parameter = await self.parameter_client.get_parameter_async(param_path)

            if "parsed_value" in parameter:
                return parameter["parsed_value"]
            else:
                return {}

        except Exception as e:
            logger.error(f"Failed to get workflow {workflow_name} config: {e}")
            return {}

    async def get_environment_globals(self) -> Dict[str, Any]:
        """환경별 글로벌 설정 조회"""
        try:
            param_path = self.get_parameter_path("global")
            parameter = await self.parameter_client.get_parameter_async(param_path)

            if "parsed_value" in parameter:
                return parameter["parsed_value"]
            else:
                return {}

        except Exception as e:
            logger.error(f"Failed to get environment globals: {e}")
            return self._get_fallback_globals()

    def _get_fallback_evolution_config(self) -> EvolutionConfig:
        """Evolution 폴백 설정"""
        import os

        env = self.config.environment

        # 환경별 기본값
        defaults = {
            "development": EvolutionConfig(
                ai_autonomy_level=0.7, evolution_enabled=True
            ),
            "staging": EvolutionConfig(ai_autonomy_level=0.8, evolution_enabled=True),
            "production": EvolutionConfig(
                ai_autonomy_level=0.85, evolution_enabled=True
            ),
        }

        return defaults.get(env, EvolutionConfig())

    def _get_fallback_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Agent 폴백 설정"""
        base_config = {
            "max_memory_kb": 6.5,
            "timeout_seconds": 30,
            "retry_attempts": 3,
            "cache_enabled": True,
        }

        # Agent별 특화 설정
        agent_specific = {
            "nl_input": {"max_input_length": 10000, "processing_timeout": 60},
            "ui_selection": {"element_timeout": 5, "screenshot_enabled": True},
            "parser": {"max_parse_depth": 10, "strict_mode": False},
            "component_decision": {
                "confidence_threshold": 0.8,
                "fallback_enabled": True,
            },
            "generation": {"max_tokens": 4096, "temperature": 0.7},
        }

        config = base_config.copy()
        if agent_name in agent_specific:
            config.update(agent_specific[agent_name])

        return config

    def _get_fallback_globals(self) -> Dict[str, Any]:
        """글로벌 폴백 설정"""
        return {
            "logging_level": "INFO",
            "metrics_enabled": True,
            "health_check_interval": 30,
            "max_concurrent_operations": 10,
        }


class AgentConfigurationService:
    """Agent별 설정 서비스"""

    def __init__(self):
        self.param_manager = EvolutionParameterManager()
        self._agent_configs = {}

    async def initialize_agent(self, agent_name: str) -> Dict[str, Any]:
        """Agent 초기화 설정"""
        logger.info(f"Initializing agent: {agent_name}")

        try:
            # Agent별 설정 로드
            agent_config = await self.param_manager.get_agent_config(agent_name)

            # Evolution 글로벌 설정 로드
            evolution_config = await self.param_manager.get_evolution_config()

            # 환경 글로벌 설정 로드
            global_config = await self.param_manager.get_environment_globals()

            # 통합 설정 생성
            integrated_config = {
                "agent_name": agent_name,
                "agent_specific": agent_config,
                "evolution": {
                    "ai_autonomy_level": evolution_config.ai_autonomy_level,
                    "max_agent_memory_kb": evolution_config.max_agent_memory_kb,
                    "safety_threshold": evolution_config.safety_threshold,
                },
                "global": global_config,
                "initialized_at": datetime.utcnow().isoformat(),
            }

            # 캐시에 저장
            self._agent_configs[agent_name] = integrated_config

            logger.info(f"Agent {agent_name} initialized successfully")
            return integrated_config

        except Exception as e:
            logger.error(f"Failed to initialize agent {agent_name}: {e}")
            raise

    async def update_agent_config(
        self, agent_name: str, updates: Dict[str, Any]
    ) -> bool:
        """Agent 설정 업데이트 (런타임)"""
        try:
            if agent_name in self._agent_configs:
                # 기존 설정 업데이트
                self._agent_configs[agent_name]["agent_specific"].update(updates)
                self._agent_configs[agent_name][
                    "updated_at"
                ] = datetime.utcnow().isoformat()

                logger.info(
                    f"Agent {agent_name} config updated: {list(updates.keys())}"
                )
                return True
            else:
                logger.warning(f"Agent {agent_name} not initialized")
                return False

        except Exception as e:
            logger.error(f"Failed to update agent {agent_name} config: {e}")
            return False

    def get_agent_config(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Agent 설정 조회"""
        return self._agent_configs.get(agent_name)

    async def reload_all_configs(self):
        """모든 설정 재로드"""
        logger.info("Reloading all agent configurations")

        try:
            # Parameter Store 캐시 무효화
            self.param_manager.parameter_client.invalidate_cache()

            # 각 Agent 재초기화
            for agent_name in list(self._agent_configs.keys()):
                await self.initialize_agent(agent_name)

            logger.info("All configurations reloaded successfully")

        except Exception as e:
            logger.error(f"Failed to reload configurations: {e}")


class WorkflowParameterService:
    """워크플로우 파라미터 서비스"""

    def __init__(self):
        self.param_manager = EvolutionParameterManager()

    async def get_workflow_chain_config(
        self, workflow_type: str
    ) -> List[Dict[str, Any]]:
        """워크플로우 체인 설정"""
        workflow_configs = {
            "code_generation": [
                {"agent": "nl_input", "stage": "input_processing"},
                {"agent": "ui_selection", "stage": "element_identification"},
                {"agent": "parser", "stage": "code_parsing"},
                {"agent": "component_decision", "stage": "component_selection"},
                {"agent": "generation", "stage": "code_generation"},
                {"agent": "assembly", "stage": "code_assembly"},
            ],
            "bug_fixing": [
                {"agent": "nl_input", "stage": "problem_analysis"},
                {"agent": "parser", "stage": "code_analysis"},
                {"agent": "component_decision", "stage": "fix_strategy"},
                {"agent": "generation", "stage": "fix_generation"},
            ],
        }

        base_chain = workflow_configs.get(workflow_type, [])

        # 각 단계별 설정 로드
        enriched_chain = []
        for step in base_chain:
            agent_config = await self.param_manager.get_agent_config(step["agent"])
            enriched_step = {
                **step,
                "config": agent_config,
                "timeout": agent_config.get("timeout_seconds", 30),
            }
            enriched_chain.append(enriched_step)

        return enriched_chain


class SystemIntegrationExample:
    """통합 시스템 예제"""

    def __init__(self):
        self.param_manager = EvolutionParameterManager()
        self.agent_service = AgentConfigurationService()
        self.workflow_service = WorkflowParameterService()

    async def initialize_system(self) -> Dict[str, Any]:
        """전체 시스템 초기화"""
        logger.info("Initializing T-Developer Evolution System...")

        initialization_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "success": True,
            "initialized_components": [],
            "errors": [],
        }

        try:
            # Evolution Engine 설정 로드
            evolution_config = await self.param_manager.get_evolution_config()
            initialization_results["evolution_config"] = {
                "ai_autonomy_level": evolution_config.ai_autonomy_level,
                "max_agent_memory_kb": evolution_config.max_agent_memory_kb,
                "evolution_enabled": evolution_config.evolution_enabled,
            }
            initialization_results["initialized_components"].append("evolution_engine")

            # 모든 Agent 초기화
            agent_names = [
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

            for agent_name in agent_names:
                try:
                    await self.agent_service.initialize_agent(agent_name)
                    initialization_results["initialized_components"].append(
                        f"agent_{agent_name}"
                    )
                except Exception as e:
                    initialization_results["errors"].append(f"Agent {agent_name}: {e}")

            # 워크플로우 체인 준비
            workflow_chain = await self.workflow_service.get_workflow_chain_config(
                "code_generation"
            )
            initialization_results["workflow_chain_length"] = len(workflow_chain)
            initialization_results["initialized_components"].append("workflow_service")

            logger.info(
                f"System initialized: {len(initialization_results['initialized_components'])} components"
            )

        except Exception as e:
            initialization_results["success"] = False
            initialization_results["errors"].append(f"System initialization error: {e}")
            logger.error(f"System initialization failed: {e}")

        return initialization_results

    async def demonstrate_parameter_usage(self) -> Dict[str, Any]:
        """파라미터 사용 데모"""
        demo_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "demonstrations": {},
        }

        try:
            # 1. Evolution 설정 조회
            evolution_config = await self.param_manager.get_evolution_config()
            demo_results["demonstrations"]["evolution_config"] = {
                "ai_autonomy_level": evolution_config.ai_autonomy_level,
                "demonstration": "Evolution Engine autonomy level retrieved from Parameter Store",
            }

            # 2. 특정 Agent 설정 조회
            nl_config = await self.param_manager.get_agent_config("nl_input")
            demo_results["demonstrations"]["agent_config"] = {
                "agent": "nl_input",
                "config_keys": list(nl_config.keys()),
                "demonstration": "Individual agent configuration loaded",
            }

            # 3. 배치 설정 조회
            all_agents = await self.param_manager.get_all_agent_configs()
            demo_results["demonstrations"]["batch_config"] = {
                "agent_count": len(all_agents),
                "agents": list(all_agents.keys()),
                "demonstration": "All agent configurations loaded in batch",
            }

            # 4. 환경별 글로벌 설정
            globals_config = await self.param_manager.get_environment_globals()
            demo_results["demonstrations"]["environment_globals"] = {
                "logging_level": globals_config.get("logging_level", "INFO"),
                "demonstration": "Environment-specific global settings loaded",
            }

            # 5. 캐시 통계 확인
            cache_stats = self.param_manager.parameter_client.get_cache_stats()
            demo_results["demonstrations"]["cache_performance"] = {
                "cache_enabled": cache_stats["enabled"],
                "cache_size": cache_stats["size"],
                "demonstration": "Parameter caching performance metrics",
            }

        except Exception as e:
            demo_results["error"] = str(e)
            logger.error(f"Parameter usage demonstration failed: {e}")

        return demo_results


# 편의 함수들
async def quick_setup() -> SystemIntegrationExample:
    """빠른 설정 및 초기화"""
    initialize_security()
    integration = SystemIntegrationExample()
    await integration.initialize_system()
    return integration


async def health_check() -> Dict[str, Any]:
    """파라미터 시스템 상태 확인"""
    integration = SystemIntegrationExample()
    return await integration.demonstrate_parameter_usage()


# 실행 예제
async def main():
    """메인 실행 함수"""
    logging.basicConfig(level=logging.INFO)

    try:
        print("T-Developer Parameter Store Integration Test")
        print("=" * 60)

        # 시스템 초기화
        integration = await quick_setup()
        print("✓ System initialization completed")

        # 파라미터 사용 데모
        demo_results = await integration.demonstrate_parameter_usage()
        print("\n파라미터 사용 데모 결과:")
        print(json.dumps(demo_results, indent=2, default=str))

        # 실시간 설정 업데이트 테스트
        agent_service = integration.agent_service
        update_success = await agent_service.update_agent_config(
            "nl_input", {"max_input_length": 15000, "updated_by": "integration_test"}
        )
        print(f"\n✓ Runtime config update: {update_success}")

        # 설정 재로드 테스트
        await agent_service.reload_all_configs()
        print("✓ Configuration reload completed")

        print("\n🎉 Parameter Store integration test completed successfully!")

    except Exception as e:
        print(f"Integration test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

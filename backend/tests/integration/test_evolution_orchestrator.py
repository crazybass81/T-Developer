"""Evolution Orchestrator 통합 테스트.

오케스트레이터의 동적 에이전트 관리 기능을 테스트합니다.
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from backend.packages.orchestrator.evolution_orchestrator import (
    EvolutionOrchestrator,
    EvolutionConfig,
    EvolutionResult
)
from backend.packages.agents.base import BaseAgent
from backend.packages.agents.registry import AgentSpec


class MockAnalysisAgent(BaseAgent):
    """테스트용 분석 에이전트."""
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """모의 분석 실행."""
        return {
            "success": True,
            "analysis": "Mock analysis completed",
            "target": inputs.get("target")
        }


class MockQualityAgent(BaseAgent):
    """테스트용 품질 검사 에이전트."""
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """모의 품질 검사 실행."""
        return {
            "success": True,
            "quality_score": 95,
            "issues": []
        }


@pytest.mark.asyncio
class TestEvolutionOrchestrator:
    """Evolution Orchestrator 테스트."""
    
    async def test_initialization(self):
        """오케스트레이터 초기화 테스트."""
        config = EvolutionConfig(max_cycles=5)
        orchestrator = EvolutionOrchestrator(config)
        
        assert orchestrator.config.max_cycles == 5
        assert not orchestrator.is_initialized
        
        # 초기화
        with patch('backend.packages.memory.hub.MemoryHub') as MockMemoryHub:
            mock_hub = AsyncMock()
            MockMemoryHub.return_value = mock_hub
            
            await orchestrator.initialize()
            
            assert orchestrator.is_initialized
            assert orchestrator.memory_hub is not None
            assert orchestrator.agent_registry is not None
    
    async def test_dynamic_agent_loading(self):
        """동적 에이전트 로딩 테스트."""
        orchestrator = EvolutionOrchestrator()
        
        with patch('backend.packages.memory.hub.MemoryHub') as MockMemoryHub:
            mock_hub = AsyncMock()
            MockMemoryHub.return_value = mock_hub
            
            await orchestrator.initialize()
            
            # 테스트 에이전트 등록
            spec = AgentSpec(
                name="mock_analysis",
                version="1.0.0",
                purpose="Mock analysis for testing",
                tags=["analysis", "test"]
            )
            
            mock_agent = MockAnalysisAgent(memory_hub=mock_hub)
            orchestrator.agent_registry.register(MockAnalysisAgent, spec, mock_agent)
            
            # 에이전트 로드
            loaded_agent = await orchestrator.load_agent("mock_analysis")
            
            assert loaded_agent is not None
            assert loaded_agent == mock_agent
            assert "mock_analysis" in orchestrator.loaded_agents
    
    async def test_agent_execution(self):
        """에이전트 실행 테스트."""
        orchestrator = EvolutionOrchestrator()
        
        with patch('backend.packages.memory.hub.MemoryHub') as MockMemoryHub:
            mock_hub = AsyncMock()
            MockMemoryHub.return_value = mock_hub
            
            await orchestrator.initialize()
            
            # 테스트 에이전트 등록
            spec = AgentSpec(
                name="mock_quality",
                version="1.0.0",
                purpose="Mock quality check",
                tags=["quality", "test"]
            )
            
            mock_agent = MockQualityAgent(memory_hub=mock_hub)
            orchestrator.agent_registry.register(MockQualityAgent, spec, mock_agent)
            
            # 에이전트 실행
            result = await orchestrator.execute_agent(
                "mock_quality",
                {"codes": ["test_code.py"]}
            )
            
            assert result["success"] is True
            assert result["quality_score"] == 95
            assert result["issues"] == []
    
    async def test_agent_search(self):
        """에이전트 검색 테스트."""
        orchestrator = EvolutionOrchestrator()
        
        with patch('backend.packages.memory.hub.MemoryHub') as MockMemoryHub:
            mock_hub = AsyncMock()
            MockMemoryHub.return_value = mock_hub
            
            await orchestrator.initialize()
            
            # 여러 테스트 에이전트 등록
            specs = [
                AgentSpec(
                    name="analyzer1",
                    version="1.0.0",
                    purpose="Code analysis",
                    tags=["analysis", "code"]
                ),
                AgentSpec(
                    name="analyzer2",
                    version="1.0.0",
                    purpose="Security analysis",
                    tags=["analysis", "security"]
                ),
                AgentSpec(
                    name="generator1",
                    version="1.0.0",
                    purpose="Code generation",
                    tags=["generation", "code"]
                )
            ]
            
            for spec in specs:
                orchestrator.agent_registry.register(BaseAgent, spec)
            
            # 태그로 검색
            analysis_agents = orchestrator.search_agents(tags=["analysis"])
            assert len(analysis_agents) >= 2
            
            # 키워드로 검색
            security_agents = orchestrator.search_agents(purpose_keywords=["security"])
            assert len(security_agents) >= 1
            assert security_agents[0].name == "analyzer2"
    
    async def test_evolution_cycle(self):
        """진화 사이클 테스트."""
        config = EvolutionConfig(
            max_cycles=2,
            target_coverage=80.0,
            learning_enabled=True
        )
        orchestrator = EvolutionOrchestrator(config)
        
        with patch('backend.packages.memory.hub.MemoryHub') as MockMemoryHub:
            mock_hub = AsyncMock()
            MockMemoryHub.return_value = mock_hub
            
            # Mock the agent executions
            with patch.object(orchestrator, '_analyze_requirements') as mock_analyze:
                mock_analyze.return_value = {
                    "success": True,
                    "specification": {"type": "improvement"}
                }
                
                with patch.object(orchestrator, '_generate_improvements') as mock_generate:
                    mock_generate.return_value = {
                        "success": True,
                        "generated_codes": [{"file": "test.py", "code": "print('test')"}]
                    }
                    
                    with patch.object(orchestrator, '_check_quality') as mock_quality:
                        mock_quality.return_value = {
                            "success": True,
                            "results": [{"passed": True}]
                        }
                        
                        with patch.object(orchestrator, '_capture_metrics') as mock_metrics:
                            # 첫 번째 호출: 초기 메트릭
                            # 두 번째 호출: 사이클 1 후 메트릭
                            # 세 번째 호출: 사이클 2 후 메트릭
                            # 네 번째 호출: 최종 메트릭
                            mock_metrics.side_effect = [
                                {"test_coverage": 70.0, "docstring_coverage": 60.0},
                                {"test_coverage": 75.0, "docstring_coverage": 65.0},
                                {"test_coverage": 82.0, "docstring_coverage": 81.0},
                                {"test_coverage": 82.0, "docstring_coverage": 81.0}
                            ]
                            
                            # 진화 실행
                            result = await orchestrator.evolve(
                                target="test_module",
                                requirements="Improve test coverage",
                                focus_area="quality"
                            )
                            
                            assert isinstance(result, EvolutionResult)
                            assert result.success is True
                            assert result.completed_cycles == 2
                            assert result.final_metrics["test_coverage"] == 82.0
                            assert result.total_improvements > 0
    
    async def test_agent_not_found(self):
        """존재하지 않는 에이전트 실행 테스트."""
        orchestrator = EvolutionOrchestrator()
        
        with patch('backend.packages.memory.hub.MemoryHub') as MockMemoryHub:
            mock_hub = AsyncMock()
            MockMemoryHub.return_value = mock_hub
            
            await orchestrator.initialize()
            
            # 존재하지 않는 에이전트 실행
            result = await orchestrator.execute_agent(
                "non_existent_agent",
                {"test": "data"}
            )
            
            assert result["success"] is False
            assert "not found" in result["error"]
    
    async def test_shutdown(self):
        """오케스트레이터 종료 테스트."""
        orchestrator = EvolutionOrchestrator()
        
        with patch('backend.packages.memory.hub.MemoryHub') as MockMemoryHub:
            mock_hub = AsyncMock()
            MockMemoryHub.return_value = mock_hub
            
            await orchestrator.initialize()
            
            # 모의 에이전트 추가
            mock_agent = AsyncMock(spec=BaseAgent)
            mock_agent.shutdown = AsyncMock()
            orchestrator.loaded_agents["test_agent"] = mock_agent
            
            # 종료
            await orchestrator.shutdown()
            
            # 에이전트 종료 호출 확인
            mock_agent.shutdown.assert_called_once()
            # 메모리 허브 종료 호출 확인
            mock_hub.shutdown.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
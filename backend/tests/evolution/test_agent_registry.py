"""
Agent Registry 테스트 스위트
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# 테스트 경로 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.evolution.agent_registry import AgentMetadata, AgentRegistry


class TestAgentRegistry:
    """Agent Registry 단위 테스트"""

    @pytest.fixture
    def temp_registry(self):
        """임시 레지스트리 파일"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        yield temp_path

        # 정리
        Path(temp_path).unlink(missing_ok=True)

    @pytest.fixture
    def registry(self, temp_registry):
        """테스트용 레지스트리 인스턴스"""
        return AgentRegistry(temp_registry)

    @pytest.fixture
    def sample_agent_file(self):
        """테스트용 에이전트 파일"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
class TestAgent:
    def __init__(self):
        self.name = "test"

    def process(self, data):
        return data

    def analyze(self, input):
        return {"result": "analyzed"}
"""
            )
            temp_path = f.name

        yield temp_path

        Path(temp_path).unlink(missing_ok=True)

    def test_init_empty_registry(self, registry):
        """빈 레지스트리 초기화 테스트"""
        assert len(registry.agents) == 0
        assert len(registry.evolution_history) == 0
        assert registry.registry_path.exists()

    def test_register_agent_success(self, registry, sample_agent_file):
        """에이전트 등록 성공 테스트"""
        agent_id = registry.register_agent(sample_agent_file, "TestAgent")

        assert agent_id is not None
        assert agent_id in registry.agents
        assert registry.agents[agent_id].name == "TestAgent"
        assert registry.agents[agent_id].size_kb < 6.5

    def test_register_agent_size_violation(self, registry):
        """크기 제약 위반 테스트"""
        # 6.5KB 초과 파일 생성
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            # 7KB 이상의 내용 작성
            f.write("x" * 7000)
            large_file = f.name

        try:
            agent_id = registry.register_agent(large_file)
            assert agent_id is None  # 등록 실패해야 함
        finally:
            Path(large_file).unlink()

    def test_get_agent(self, registry, sample_agent_file):
        """에이전트 조회 테스트"""
        agent_id = registry.register_agent(sample_agent_file)

        agent = registry.get_agent(agent_id)
        assert agent is not None
        assert agent.id == agent_id

        # 존재하지 않는 에이전트
        assert registry.get_agent("nonexistent") is None

    def test_list_agents(self, registry, sample_agent_file):
        """에이전트 목록 조회 테스트"""
        # 여러 에이전트 등록
        id1 = registry.register_agent(sample_agent_file, "Agent1")
        id2 = registry.register_agent(sample_agent_file, "Agent2")

        agents = registry.list_agents()
        assert len(agents) == 2

        # 제약 조건 필터링
        agents_filtered = registry.list_agents(filter_constraints=True)
        assert len(agents_filtered) <= 2

    def test_update_fitness(self, registry, sample_agent_file):
        """적합도 업데이트 테스트"""
        agent_id = registry.register_agent(sample_agent_file)

        # 초기 적합도
        assert registry.agents[agent_id].fitness_score == 1.0

        # 적합도 업데이트
        registry.update_fitness(agent_id, 0.85)
        assert registry.agents[agent_id].fitness_score == 0.85

        # 성능 메트릭 기록 확인
        assert agent_id in registry.performance_metrics
        assert 0.85 in registry.performance_metrics[agent_id]

    def test_record_evolution(self, registry, sample_agent_file):
        """진화 기록 테스트"""
        parent_id = registry.register_agent(sample_agent_file, "Parent")
        child_id = registry.register_agent(sample_agent_file, "Child")

        # 진화 이벤트 기록
        registry.record_evolution(parent_id, child_id, "mutation")

        # 진화 이력 확인
        assert len(registry.evolution_history) == 1
        assert registry.evolution_history[0]["parent_id"] == parent_id
        assert registry.evolution_history[0]["child_id"] == child_id

        # 자식 에이전트 정보 확인
        child = registry.agents[child_id]
        assert child.parent_id == parent_id
        assert child.generation == 2
        assert child.evolution_count == 1

    def test_get_evolution_lineage(self, registry, sample_agent_file):
        """진화 계보 추적 테스트"""
        # 3세대 에이전트 생성
        gen1_id = registry.register_agent(sample_agent_file, "Gen1")
        gen2_id = registry.register_agent(sample_agent_file, "Gen2")
        gen3_id = registry.register_agent(sample_agent_file, "Gen3")

        # 진화 관계 설정
        registry.record_evolution(gen1_id, gen2_id, "mutation")
        registry.record_evolution(gen2_id, gen3_id, "crossover")

        # 계보 추적
        lineage = registry.get_evolution_lineage(gen3_id)
        assert len(lineage) == 3
        assert lineage == [gen3_id, gen2_id, gen1_id]

    def test_get_statistics(self, registry, sample_agent_file):
        """통계 조회 테스트"""
        # 에이전트 등록
        registry.register_agent(sample_agent_file, "Agent1")
        registry.register_agent(sample_agent_file, "Agent2")

        stats = registry.get_statistics()

        assert stats["total_agents"] == 2
        assert "average_size_kb" in stats
        assert "average_speed_us" in stats
        assert "average_fitness" in stats
        assert stats["total_evolutions"] == 0

    def test_validate_all_agents(self, registry, sample_agent_file):
        """전체 에이전트 검증 테스트"""
        agent_id = registry.register_agent(sample_agent_file)

        # 정상 에이전트
        violations = registry.validate_all_agents()
        assert len(violations["size"]) == 0
        assert len(violations["speed"]) == 0

        # 적합도가 낮은 에이전트 시뮬레이션
        registry.update_fitness(agent_id, 0.3)
        violations = registry.validate_all_agents()
        assert len(violations["fitness"]) == 1

    def test_extract_capabilities(self, registry, sample_agent_file):
        """능력 추출 테스트"""
        capabilities = registry._extract_capabilities(sample_agent_file)

        assert "processing" in capabilities  # process 메서드
        assert "analysis" in capabilities  # analyze 메서드

    def test_persistence(self, temp_registry, sample_agent_file):
        """레지스트리 영속성 테스트"""
        # 첫 번째 레지스트리에서 에이전트 등록
        registry1 = AgentRegistry(temp_registry)
        agent_id = registry1.register_agent(sample_agent_file, "PersistTest")
        registry1.update_fitness(agent_id, 0.9)

        # 두 번째 레지스트리에서 로드
        registry2 = AgentRegistry(temp_registry)

        assert agent_id in registry2.agents
        assert registry2.agents[agent_id].name == "PersistTest"
        assert registry2.agents[agent_id].fitness_score == 0.9

    @patch("src.evolution.agent_registry.time.perf_counter")
    def test_measure_instantiation_speed(self, mock_timer, registry, sample_agent_file):
        """인스턴스화 속도 측정 테스트"""
        # 2μs 시뮬레이션
        mock_timer.side_effect = [0, 0.000002]

        speed = registry._measure_instantiation_speed(sample_agent_file)
        assert speed == 2.0  # 2μs

    def test_agent_metadata_dataclass(self):
        """AgentMetadata 데이터클래스 테스트"""
        metadata = AgentMetadata(
            id="test123",
            name="TestAgent",
            version="1.0.0",
            size_kb=5.5,
            instantiation_us=2.5,
            fitness_score=0.95,
            generation=1,
        )

        assert metadata.id == "test123"
        assert metadata.size_kb == 5.5
        assert metadata.constraints_met == True
        assert metadata.created_at != ""
        assert metadata.capabilities == []


class TestAgentRegistryCLI:
    """CLI 인터페이스 테스트"""

    def test_cli_register_command(self, capsys, sample_agent_file):
        """CLI register 명령 테스트"""
        import sys

        sys.argv = [
            "agent_registry.py",
            "register",
            "--agent-path",
            sample_agent_file,
            "--name",
            "CLIAgent",
        ]

        # main 함수가 있다면 실행
        # 실제 구현에서는 argparse를 통한 CLI 테스트

    def test_cli_list_command(self, capsys):
        """CLI list 명령 테스트"""
        # CLI list 명령 테스트 구현
        pass

    def test_cli_stats_command(self, capsys):
        """CLI stats 명령 테스트"""
        # CLI stats 명령 테스트 구현
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

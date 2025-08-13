"""
Tests for Agent Registry

에이전트 레지스트리(Agent Registry)의 CRUD 기능을 테스트합니다.
"""

import asyncio
import os
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from evolution.registry import Agent, AgentMetrics, AgentRegistry, AgentStatus, AgentType


class TestAgentRegistry:
    """Agent Registry 테스트 클래스"""

    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        # 임시 디렉토리 생성
        self.temp_dir = Path(tempfile.mkdtemp())

        # Registry 객체 생성
        self.registry = AgentRegistry(self.temp_dir / "registry")

    def teardown_method(self):
        """각 테스트 메서드 실행 후 정리"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    @pytest.mark.asyncio
    async def test_registry_initialization(self):
        """레지스트리 초기화 테스트"""
        # When: 레지스트리 초기화
        result = await self.registry.initialize()

        # Then: 초기화 성공
        assert result is True
        assert self.registry.data_dir.exists()
        assert self.registry.agents_dir.exists()
        assert len(self.registry.agents) == 0

    @pytest.mark.asyncio
    async def test_agent_creation(self):
        """에이전트 생성 테스트"""
        await self.registry.initialize()

        # Given: 에이전트 정보
        agent_name = "테스트_NL_입력_에이전트"
        agent_type = AgentType.NL_INPUT
        agent_code = """
def process_natural_language(text):
    return {"intent": "create_todo", "entities": {"task": text}}
"""
        description = "자연어 입력을 처리하는 에이전트"
        tags = {"nlp", "input", "korean"}

        # When: 에이전트 생성
        agent = await self.registry.create_agent(
            name=agent_name,
            agent_type=agent_type,
            code=agent_code,
            description=description,
            tags=tags,
        )

        # Then: 에이전트가 올바르게 생성됨
        assert agent.name == agent_name
        assert agent.agent_type == agent_type
        assert agent.code == agent_code
        assert agent.description == description
        assert agent.tags == tags
        assert agent.status == AgentStatus.CREATED
        assert agent.version == "1.0.0"
        assert len(agent.versions) == 1

        # 레지스트리에 저장됨
        assert agent.id in self.registry.agents
        assert agent.id in self.registry.type_index[agent_type]
        assert agent.id in self.registry.status_index[AgentStatus.CREATED]

    @pytest.mark.asyncio
    async def test_agent_retrieval(self):
        """에이전트 조회 테스트"""
        await self.registry.initialize()

        # Given: 에이전트 생성
        agent = await self.registry.create_agent(
            name="검색_에이전트", agent_type=AgentType.SEARCH, code="def search(): pass"
        )

        # When: ID로 조회
        found_agent = await self.registry.get_agent(agent.id)

        # Then: 올바른 에이전트 반환
        assert found_agent is not None
        assert found_agent.id == agent.id
        assert found_agent.name == "검색_에이전트"

        # When: 이름으로 조회
        found_by_name = await self.registry.get_agent_by_name("검색_에이전트")

        # Then: 동일한 에이전트 반환
        assert found_by_name is not None
        assert found_by_name.id == agent.id

    @pytest.mark.asyncio
    async def test_agent_update(self):
        """에이전트 업데이트 테스트"""
        await self.registry.initialize()

        # Given: 에이전트 생성
        agent = await self.registry.create_agent(
            name="업데이트_테스트", agent_type=AgentType.PARSER, code="def parse(): pass"
        )

        # When: 상태 업데이트
        result = await self.registry.update_agent(
            agent.id, status=AgentStatus.DEPLOYED, description="업데이트된 설명"
        )

        # Then: 업데이트 성공
        assert result is True

        updated_agent = await self.registry.get_agent(agent.id)
        assert updated_agent.status == AgentStatus.DEPLOYED
        assert updated_agent.description == "업데이트된 설명"
        assert updated_agent.updated_at > agent.created_at

        # 인덱스도 업데이트됨
        assert agent.id not in self.registry.status_index[AgentStatus.CREATED]
        assert agent.id in self.registry.status_index[AgentStatus.DEPLOYED]

    @pytest.mark.asyncio
    async def test_agent_code_update(self):
        """에이전트 코드 업데이트 및 버전 관리 테스트"""
        await self.registry.initialize()

        # Given: 에이전트 생성
        agent = await self.registry.create_agent(
            name="버전_테스트",
            agent_type=AgentType.GENERATION,
            code="def generate_v1(): return 'v1'",
        )

        original_version = agent.version

        # When: 코드 업데이트
        new_version = await self.registry.update_agent_code(
            agent.id, "def generate_v2(): return 'v2'", "버그 수정 및 성능 개선"
        )

        # Then: 새 버전 생성
        assert new_version is not None
        assert new_version != original_version

        updated_agent = await self.registry.get_agent(agent.id)
        assert updated_agent.version == new_version
        assert updated_agent.code == "def generate_v2(): return 'v2'"
        assert len(updated_agent.versions) == 2

        # 버전 히스토리 확인
        latest_version = updated_agent.versions[-1]
        assert latest_version.version == new_version
        assert latest_version.changelog == "버그 수정 및 성능 개선"
        assert latest_version.parent_version == original_version

    @pytest.mark.asyncio
    async def test_agent_deletion(self):
        """에이전트 삭제 테스트"""
        await self.registry.initialize()

        # Given: 에이전트 생성
        agent = await self.registry.create_agent(
            name="삭제_테스트",
            agent_type=AgentType.ASSEMBLY,
            code="def assemble(): pass",
            tags={"test", "assembly"},
        )

        agent_id = agent.id

        # When: 에이전트 삭제
        result = await self.registry.delete_agent(agent_id)

        # Then: 삭제 성공
        assert result is True
        assert agent_id not in self.registry.agents
        assert agent_id not in self.registry.type_index[AgentType.ASSEMBLY]
        assert agent_id not in self.registry.status_index[AgentStatus.CREATED]

        # 태그 인덱스에서도 제거됨
        for tag in agent.tags:
            if tag in self.registry.tag_index:
                assert agent_id not in self.registry.tag_index[tag]

        # 조회시 None 반환
        deleted_agent = await self.registry.get_agent(agent_id)
        assert deleted_agent is None

    @pytest.mark.asyncio
    async def test_agent_listing_and_filtering(self):
        """에이전트 목록 조회 및 필터링 테스트"""
        await self.registry.initialize()

        # Given: 여러 에이전트 생성
        agents = []

        # NL Input 에이전트들
        for i in range(3):
            agent = await self.registry.create_agent(
                name=f"NL_입력_{i}",
                agent_type=AgentType.NL_INPUT,
                code=f"def process_{i}(): pass",
                tags={"nlp", "korean"},
            )
            agents.append(agent)

        # UI Selection 에이전트
        ui_agent = await self.registry.create_agent(
            name="UI_선택",
            agent_type=AgentType.UI_SELECTION,
            code="def select_ui(): pass",
            tags={"ui", "selection"},
        )
        agents.append(ui_agent)

        # 일부 에이전트 상태 변경
        await self.registry.update_agent(agents[0].id, status=AgentStatus.DEPLOYED)
        await self.registry.update_agent(agents[1].id, status=AgentStatus.DEPLOYED)

        # When: 전체 목록 조회
        all_agents = await self.registry.list_agents()

        # Then: 모든 에이전트 반환
        assert len(all_agents) == 4

        # When: 타입별 필터링
        nl_agents = await self.registry.list_agents(agent_type=AgentType.NL_INPUT)

        # Then: NL Input 에이전트만 반환
        assert len(nl_agents) == 3
        assert all(a.agent_type == AgentType.NL_INPUT for a in nl_agents)

        # When: 상태별 필터링
        deployed_agents = await self.registry.list_agents(status=AgentStatus.DEPLOYED)

        # Then: 배포된 에이전트만 반환
        assert len(deployed_agents) == 2
        assert all(a.status == AgentStatus.DEPLOYED for a in deployed_agents)

        # When: 태그별 필터링
        korean_agents = await self.registry.list_agents(tags={"korean"})

        # Then: 한국어 태그가 있는 에이전트만 반환
        assert len(korean_agents) == 3
        assert all("korean" in a.tags for a in korean_agents)

        # When: 제한된 수 조회
        limited_agents = await self.registry.list_agents(limit=2)

        # Then: 최대 2개만 반환
        assert len(limited_agents) <= 2

    @pytest.mark.asyncio
    async def test_agent_search(self):
        """에이전트 검색 테스트"""
        await self.registry.initialize()

        # Given: 검색용 에이전트들 생성
        await self.registry.create_agent(
            name="자연어_처리_에이전트",
            agent_type=AgentType.NL_INPUT,
            code="def process(): pass",
            description="한국어 자연어 처리를 담당하는 에이전트",
        )

        await self.registry.create_agent(
            name="컴포넌트_결정_에이전트",
            agent_type=AgentType.COMPONENT_DECISION,
            code="def decide(): pass",
            description="UI 컴포넌트 선택을 도와주는 에이전트",
            tags={"ui", "decision"},
        )

        await self.registry.create_agent(
            name="검색_엔진",
            agent_type=AgentType.SEARCH,
            code="def search(): pass",
            description="코드 검색 및 매칭",
        )

        # When: 이름으로 검색
        results = await self.registry.search_agents("자연어")

        # Then: 관련 에이전트 반환
        assert len(results) > 0
        assert any("자연어" in agent.name for agent in results)

        # When: 설명으로 검색
        ui_results = await self.registry.search_agents("컴포넌트")

        # Then: 설명에 포함된 에이전트 반환
        assert len(ui_results) > 0
        assert any("컴포넌트" in agent.description for agent in ui_results)

        # When: 태그로 검색
        tag_results = await self.registry.search_agents("decision")

        # Then: 태그가 일치하는 에이전트 반환
        assert len(tag_results) > 0
        assert any("decision" in agent.tags for agent in tag_results)

    @pytest.mark.asyncio
    async def test_agent_metrics_update(self):
        """에이전트 메트릭 업데이트 테스트"""
        await self.registry.initialize()

        # Given: 에이전트 생성
        agent = await self.registry.create_agent(
            name="메트릭_테스트",
            agent_type=AgentType.MATCH_RATE,
            code="def calculate_match(): pass",
        )

        # When: 메트릭 업데이트
        new_metrics = AgentMetrics(
            memory_usage_kb=5.2,
            instantiation_time_us=2.8,
            execution_time_ms=150.0,
            accuracy=0.95,
            throughput_ops_per_sec=1000.0,
            error_rate=0.01,
            fitness_score=0.92,
            safety_score=0.98,
        )

        result = await self.registry.update_agent_metrics(agent.id, new_metrics)

        # Then: 메트릭 업데이트 성공
        assert result is True

        updated_agent = await self.registry.get_agent(agent.id)
        assert updated_agent.metrics.memory_usage_kb == 5.2
        assert updated_agent.metrics.accuracy == 0.95
        assert updated_agent.metrics.fitness_score == 0.92

    @pytest.mark.asyncio
    async def test_registry_statistics(self):
        """레지스트리 통계 테스트"""
        await self.registry.initialize()

        # Given: 다양한 에이전트들 생성
        agent_configs = [
            ("NL_1", AgentType.NL_INPUT, {"nlp", "korean"}),
            ("NL_2", AgentType.NL_INPUT, {"nlp", "english"}),
            ("UI_1", AgentType.UI_SELECTION, {"ui", "web"}),
            ("Parser_1", AgentType.PARSER, {"parsing", "json"}),
            ("Search_1", AgentType.SEARCH, {"search", "elastic"}),
        ]

        for name, agent_type, tags in agent_configs:
            await self.registry.create_agent(
                name=name, agent_type=agent_type, code="def process(): pass", tags=tags
            )

        # When: 통계 조회
        stats = await self.registry.get_registry_stats()

        # Then: 올바른 통계 반환
        assert stats["total_agents"] == 5
        assert stats["by_type"]["nl_input"] == 2
        assert stats["by_type"]["ui_selection"] == 1
        assert stats["by_status"]["created"] == 5
        assert stats["total_tags"] > 0

        # 가장 많이 사용된 태그 확인
        most_common_tags = stats["most_common_tags"]
        assert len(most_common_tags) > 0
        assert all(
            isinstance(tag_info, tuple) and len(tag_info) == 2 for tag_info in most_common_tags
        )

    @pytest.mark.asyncio
    async def test_version_management(self):
        """버전 관리 테스트"""
        await self.registry.initialize()

        # Given: 에이전트 생성
        agent = await self.registry.create_agent(
            name="버전_관리_테스트",
            agent_type=AgentType.DOWNLOAD,
            code="def download_v1(): return 'v1'",
        )

        # When: 여러 버전 생성
        await self.registry.update_agent_code(agent.id, "def download_v2(): return 'v2'", "v2 업데이트")
        await self.registry.update_agent_code(agent.id, "def download_v3(): return 'v3'", "v3 업데이트")

        updated_agent = await self.registry.get_agent(agent.id)

        # Then: 버전 히스토리 관리
        assert len(updated_agent.versions) == 3
        assert updated_agent.version == "1.0.2"  # 패치 버전 증가

        # When: 특정 버전 조회
        v2 = updated_agent.get_version("1.0.1")

        # Then: 올바른 버전 반환
        assert v2 is not None
        assert v2.changelog == "v2 업데이트"
        assert v2.parent_version == "1.0.0"

        # When: 안정 버전 표시
        updated_agent.mark_version_stable("1.0.1")
        stable_version = updated_agent.get_latest_stable_version()

        # Then: 안정 버전 반환
        assert stable_version is not None
        assert stable_version.version == "1.0.1"
        assert stable_version.is_stable is True

    @pytest.mark.asyncio
    async def test_persistence(self):
        """데이터 영속성 테스트"""
        await self.registry.initialize()

        # Given: 에이전트 생성
        original_agent = await self.registry.create_agent(
            name="영속성_테스트",
            agent_type=AgentType.META_ORCHESTRATOR,
            code="def orchestrate(): pass",
            description="테스트용 오케스트레이터",
            tags={"test", "orchestrator"},
        )

        # When: 새 레지스트리 인스턴스로 로드
        new_registry = AgentRegistry(self.temp_dir / "registry")
        await new_registry.initialize()

        # Then: 데이터가 올바르게 로드됨
        loaded_agent = await new_registry.get_agent(original_agent.id)

        assert loaded_agent is not None
        assert loaded_agent.name == original_agent.name
        assert loaded_agent.agent_type == original_agent.agent_type
        assert loaded_agent.code == original_agent.code
        assert loaded_agent.description == original_agent.description
        assert loaded_agent.tags == original_agent.tags
        assert loaded_agent.version == original_agent.version

        # 인덱스도 올바르게 복원됨
        assert loaded_agent.id in new_registry.type_index[AgentType.META_ORCHESTRATOR]
        assert loaded_agent.id in new_registry.status_index[AgentStatus.CREATED]


if __name__ == "__main__":
    # 직접 실행시 테스트 수행
    pytest.main([__file__, "-v"])

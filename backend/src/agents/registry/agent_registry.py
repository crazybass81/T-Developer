"""Agent Registry System - Central management for all agents"""
import hashlib
import importlib
import inspect
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type

from src.agents.evolution.base_agent import BaseEvolutionAgent


class AgentRegistry:
    """
    중앙 에이전트 레지스트리
    - 모든 에이전트 등록/관리
    - 계층 구조 관리 (메타 → 최소 단위)
    - 버전 관리
    - 능력 기반 디스커버리
    """

    def __init__(self, db_path: str = "agents.db"):
        self.db_path = db_path
        self.agents: Dict[str, BaseEvolutionAgent] = {}
        self.metadata: Dict[str, Dict] = {}
        self.hierarchy: Dict[str, List[str]] = {}
        self._init_database()
        self._load_agents()

    def _init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Agents 테이블
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                version TEXT NOT NULL,
                type TEXT NOT NULL,
                capabilities TEXT,
                metadata TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                usage_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0,
                avg_execution_time REAL DEFAULT 0.0
            )
        """
        )

        # Agent Hierarchy 테이블
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS agent_hierarchy (
                parent_id TEXT,
                child_id TEXT,
                relationship_type TEXT,
                PRIMARY KEY (parent_id, child_id)
            )
        """
        )

        # Agent Versions 테이블
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS agent_versions (
                agent_id TEXT,
                version TEXT,
                changelog TEXT,
                created_at TIMESTAMP,
                performance_metrics TEXT,
                PRIMARY KEY (agent_id, version)
            )
        """
        )

        conn.commit()
        conn.close()

    def register_agent(
        self, agent_id: str, agent: BaseEvolutionAgent, agent_type: str = "minimal"
    ) -> bool:
        """최소 단위 에이전트 등록"""
        try:
            # 메모리에 저장
            self.agents[agent_id] = agent

            # 메타데이터 추출
            capabilities = agent.get_capabilities()
            metadata = {
                "class_name": agent.__class__.__name__,
                "module": agent.__class__.__module__,
                "source_file": inspect.getfile(agent.__class__),
                "methods": [m for m in dir(agent) if not m.startswith("_")],
                "doc": agent.__class__.__doc__,
                "signature": self._generate_signature(agent),
            }

            self.metadata[agent_id] = metadata

            # DB에 저장
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO agents
                (agent_id, name, version, type, capabilities, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    agent_id,
                    agent.name,
                    agent.version,
                    agent_type,
                    json.dumps(capabilities),
                    json.dumps(metadata),
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                ),
            )

            conn.commit()
            conn.close()

            return True

        except Exception as e:
            print(f"Failed to register agent {agent_id}: {e}")
            return False

    def register_composite_agent(
        self, meta_agent_id: str, component_ids: List[str], orchestrator: Optional[Callable] = None
    ) -> bool:
        """메타 에이전트 등록 (여러 최소 단위 에이전트 조합)"""
        try:
            # 모든 컴포넌트가 존재하는지 확인
            for comp_id in component_ids:
                if comp_id not in self.agents:
                    raise ValueError(f"Component agent {comp_id} not found")

            # 계층 구조 저장
            self.hierarchy[meta_agent_id] = component_ids

            # DB에 관계 저장
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            for child_id in component_ids:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO agent_hierarchy
                    (parent_id, child_id, relationship_type)
                    VALUES (?, ?, ?)
                """,
                    (meta_agent_id, child_id, "composite"),
                )

            # 메타 에이전트 정보 저장
            composite_metadata = {
                "type": "composite",
                "components": component_ids,
                "orchestrator": orchestrator.__name__ if orchestrator else None,
            }

            cursor.execute(
                """
                INSERT OR REPLACE INTO agents
                (agent_id, name, version, type, capabilities, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    meta_agent_id,
                    meta_agent_id,
                    "1.0.0",
                    "composite",
                    json.dumps(self._get_composite_capabilities(component_ids)),
                    json.dumps(composite_metadata),
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                ),
            )

            conn.commit()
            conn.close()

            return True

        except Exception as e:
            print(f"Failed to register composite agent {meta_agent_id}: {e}")
            return False

    def get_agent(self, agent_id: str) -> Optional[BaseEvolutionAgent]:
        """에이전트 인스턴스 반환"""
        if agent_id in self.agents:
            return self.agents[agent_id]

        # Composite agent인 경우
        if agent_id in self.hierarchy:
            return self._create_composite_agent(agent_id)

        return None

    def discover_agents(
        self, required_capabilities: List[str], agent_type: Optional[str] = None
    ) -> List[str]:
        """필요한 능력을 가진 에이전트 탐색"""
        matching_agents = []

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT agent_id, capabilities FROM agents WHERE 1=1"
        params = []

        if agent_type:
            query += " AND type = ?"
            params.append(agent_type)

        cursor.execute(query, params)

        for agent_id, capabilities_json in cursor.fetchall():
            capabilities = json.loads(capabilities_json) if capabilities_json else []
            if all(cap in capabilities for cap in required_capabilities):
                matching_agents.append(agent_id)

        conn.close()
        return matching_agents

    def get_agent_versions(self, agent_id: str) -> List[Dict]:
        """에이전트의 모든 버전 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT version, changelog, created_at, performance_metrics
            FROM agent_versions
            WHERE agent_id = ?
            ORDER BY created_at DESC
        """,
            (agent_id,),
        )

        versions = []
        for row in cursor.fetchall():
            versions.append(
                {
                    "version": row[0],
                    "changelog": row[1],
                    "created_at": row[2],
                    "metrics": json.loads(row[3]) if row[3] else {},
                }
            )

        conn.close()
        return versions

    def update_agent_metrics(self, agent_id: str, execution_time: float, success: bool):
        """에이전트 실행 메트릭 업데이트"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 현재 메트릭 조회
        cursor.execute(
            """
            SELECT usage_count, success_rate, avg_execution_time
            FROM agents
            WHERE agent_id = ?
        """,
            (agent_id,),
        )

        row = cursor.fetchone()
        if row:
            usage_count, success_rate, avg_time = row
            new_count = usage_count + 1
            new_success_rate = ((success_rate * usage_count) + (1 if success else 0)) / new_count
            new_avg_time = ((avg_time * usage_count) + execution_time) / new_count

            cursor.execute(
                """
                UPDATE agents
                SET usage_count = ?, success_rate = ?, avg_execution_time = ?, updated_at = ?
                WHERE agent_id = ?
            """,
                (new_count, new_success_rate, new_avg_time, datetime.now().isoformat(), agent_id),
            )

        conn.commit()
        conn.close()

    def export_agent(self, agent_id: str) -> Dict:
        """에이전트를 재사용 가능한 형태로 내보내기"""
        agent = self.get_agent(agent_id)
        if not agent:
            return {}

        metadata = self.metadata.get(agent_id, {})

        return {
            "agent_id": agent_id,
            "name": agent.name,
            "version": agent.version,
            "capabilities": agent.get_capabilities(),
            "metadata": metadata,
            "export_format": "t-developer-agent-v1",
            "exported_at": datetime.now().isoformat(),
        }

    def import_agent(self, agent_data: Dict) -> bool:
        """외부 에이전트 가져오기"""
        try:
            # 모듈 동적 임포트
            module_name = agent_data["metadata"]["module"]
            class_name = agent_data["metadata"]["class_name"]

            module = importlib.import_module(module_name)
            agent_class = getattr(module, class_name)

            # 인스턴스 생성 및 등록
            agent = agent_class()
            return self.register_agent(agent_data["agent_id"], agent)

        except Exception as e:
            print(f"Failed to import agent: {e}")
            return False

    def _generate_signature(self, agent: BaseEvolutionAgent) -> str:
        """에이전트 시그니처 생성 (버전 관리용)"""
        source = inspect.getsource(agent.__class__)
        return hashlib.sha256(source.encode()).hexdigest()[:16]

    def _get_composite_capabilities(self, component_ids: List[str]) -> List[str]:
        """컴포지트 에이전트의 통합 능력 계산"""
        all_capabilities = set()
        for comp_id in component_ids:
            if comp_id in self.agents:
                all_capabilities.update(self.agents[comp_id].get_capabilities())
        return list(all_capabilities)

    def _create_composite_agent(self, meta_agent_id: str):
        """컴포지트 에이전트 동적 생성"""
        component_ids = self.hierarchy.get(meta_agent_id, [])
        components = {cid: self.agents[cid] for cid in component_ids if cid in self.agents}

        # 동적 컴포지트 에이전트 클래스
        class CompositeAgent(BaseEvolutionAgent):
            def __init__(self):
                super().__init__(name=meta_agent_id, version="1.0.0")
                self.components = components

            async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
                results = {}
                for comp_id, comp_agent in self.components.items():
                    results[comp_id] = await comp_agent.execute(input_data)
                return results

            def get_capabilities(self) -> List[str]:
                caps = set()
                for comp in self.components.values():
                    caps.update(comp.get_capabilities())
                return list(caps)

        return CompositeAgent()

    def _load_agents(self):
        """시작시 등록된 에이전트 로드"""
        # 여기서 필요한 에이전트들을 자동으로 로드할 수 있음
        pass

    def get_statistics(self) -> Dict:
        """레지스트리 통계"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM agents WHERE type = 'minimal'")
        minimal_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM agents WHERE type = 'composite'")
        composite_count = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(success_rate) FROM agents")
        avg_success = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(usage_count) FROM agents")
        total_usage = cursor.fetchone()[0] or 0

        conn.close()

        return {
            "total_agents": minimal_count + composite_count,
            "minimal_agents": minimal_count,
            "composite_agents": composite_count,
            "average_success_rate": avg_success,
            "total_executions": total_usage,
            "hierarchy_depth": len(self.hierarchy),
        }


# Global Registry Instance
_global_registry = None


def get_global_registry() -> AgentRegistry:
    """전역 레지스트리 인스턴스 반환"""
    global _global_registry
    if _global_registry is None:
        _global_registry = AgentRegistry()
    return _global_registry

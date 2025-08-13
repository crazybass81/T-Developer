"""
T-Developer Evolution System - Agent Registry
에이전트 등록, 관리, 진화 추적을 위한 중앙 레지스트리

핵심 제약:
- 에이전트 크기: < 6.5KB
- 인스턴스화: < 3μs
- AI 자율성: 85%
"""

import hashlib
import importlib.util
import json
import os
import sys
import time
import traceback
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class AgentMetadata:
    """에이전트 메타데이터"""

    id: str
    name: str
    version: str
    size_kb: float
    instantiation_us: float
    fitness_score: float
    generation: int
    parent_id: Optional[str] = None
    created_at: str = ""
    last_evolved: str = ""
    capabilities: List[str] = None
    constraints_met: bool = True
    evolution_count: int = 0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.last_evolved:
            self.last_evolved = self.created_at
        if self.capabilities is None:
            self.capabilities = []


class AgentRegistry:
    """
    에이전트 중앙 레지스트리
    모든 에이전트의 생명주기를 관리하고 진화를 추적
    """

    # 제약 조건
    MAX_AGENT_SIZE_KB = 6.5
    MAX_INSTANTIATION_US = 3.0
    MIN_FITNESS_SCORE = 0.5

    def __init__(self, registry_path: str = None):
        """레지스트리 초기화"""
        self.registry_path = Path(registry_path or "backend/data/agents/registry.json")
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)

        self.agents: Dict[str, AgentMetadata] = {}
        self.evolution_history: List[Dict] = []
        self.performance_metrics: Dict[str, List[float]] = {}

        self._load_registry()

    def _load_registry(self):
        """레지스트리 데이터 로드"""
        if self.registry_path.exists():
            try:
                with open(self.registry_path, "r") as f:
                    data = json.load(f)

                # 에이전트 메타데이터 복원
                for agent_data in data.get("agents", []):
                    agent = AgentMetadata(**agent_data)
                    self.agents[agent.id] = agent

                self.evolution_history = data.get("evolution_history", [])
                self.performance_metrics = data.get("performance_metrics", {})

                print(f"✅ Loaded {len(self.agents)} agents from registry")
            except Exception as e:
                print(f"⚠️ Error loading registry: {e}")
                self._initialize_empty_registry()
        else:
            self._initialize_empty_registry()

    def _initialize_empty_registry(self):
        """빈 레지스트리 초기화"""
        self.agents = {}
        self.evolution_history = []
        self.performance_metrics = {}
        self._save_registry()
        print("📋 Initialized new agent registry")

    def _save_registry(self):
        """레지스트리 데이터 저장"""
        data = {
            "agents": [asdict(agent) for agent in self.agents.values()],
            "evolution_history": self.evolution_history,
            "performance_metrics": self.performance_metrics,
            "last_updated": datetime.now().isoformat(),
            "stats": {
                "total_agents": len(self.agents),
                "active_agents": sum(1 for a in self.agents.values() if a.constraints_met),
                "total_evolutions": sum(a.evolution_count for a in self.agents.values()),
                "average_fitness": sum(a.fitness_score for a in self.agents.values())
                / max(len(self.agents), 1),
            },
        }

        with open(self.registry_path, "w") as f:
            json.dump(data, f, indent=2)

    def register_agent(self, agent_path: str, name: str = None) -> Optional[str]:
        """
        새 에이전트 등록

        Args:
            agent_path: 에이전트 파일 경로
            name: 에이전트 이름 (옵션)

        Returns:
            등록된 에이전트 ID 또는 None
        """
        agent_file = Path(agent_path)

        if not agent_file.exists():
            print(f"❌ Agent file not found: {agent_path}")
            return None

        # 크기 검증
        size_bytes = agent_file.stat().st_size
        size_kb = size_bytes / 1024

        if size_kb > self.MAX_AGENT_SIZE_KB:
            print(f"❌ Agent exceeds size limit: {size_kb:.2f}KB > {self.MAX_AGENT_SIZE_KB}KB")
            return None

        # 인스턴스화 속도 측정
        instantiation_us = self._measure_instantiation_speed(agent_path)

        if instantiation_us > self.MAX_INSTANTIATION_US:
            print(
                f"⚠️ Agent instantiation slow: {instantiation_us:.2f}μs > {self.MAX_INSTANTIATION_US}μs"
            )

        # 에이전트 ID 생성
        agent_id = self._generate_agent_id(agent_path)

        # 메타데이터 생성
        metadata = AgentMetadata(
            id=agent_id,
            name=name or agent_file.stem,
            version="1.0.0",
            size_kb=round(size_kb, 2),
            instantiation_us=round(instantiation_us, 2),
            fitness_score=1.0,  # 초기 적합도
            generation=1,
            capabilities=self._extract_capabilities(agent_path),
            constraints_met=(
                size_kb <= self.MAX_AGENT_SIZE_KB and instantiation_us <= self.MAX_INSTANTIATION_US
            ),
        )

        # 레지스트리에 추가
        self.agents[agent_id] = metadata
        self._save_registry()

        print(f"✅ Registered agent: {metadata.name} (ID: {agent_id})")
        print(f"   Size: {metadata.size_kb}KB, Speed: {metadata.instantiation_us}μs")

        return agent_id

    def _generate_agent_id(self, agent_path: str) -> str:
        """에이전트 고유 ID 생성"""
        with open(agent_path, "rb") as f:
            content = f.read()

        hash_obj = hashlib.sha256(content)
        return hash_obj.hexdigest()[:16]

    def _measure_instantiation_speed(self, agent_path: str) -> float:
        """
        에이전트 인스턴스화 속도 측정

        Returns:
            인스턴스화 시간 (마이크로초)
        """
        try:
            # 모듈 동적 로드
            spec = importlib.util.spec_from_file_location("test_agent", agent_path)
            module = importlib.util.module_from_spec(spec)

            # 인스턴스화 시간 측정
            start = time.perf_counter()
            spec.loader.exec_module(module)

            # 에이전트 클래스 찾기 및 인스턴스화
            for name in dir(module):
                obj = getattr(module, name)
                if isinstance(obj, type) and name.endswith("Agent"):
                    instance = obj()
                    break

            end = time.perf_counter()

            return (end - start) * 1_000_000  # 마이크로초로 변환

        except Exception as e:
            print(f"⚠️ Error measuring instantiation speed: {e}")
            return 0.0

    def _extract_capabilities(self, agent_path: str) -> List[str]:
        """에이전트 능력 추출"""
        capabilities = []

        try:
            with open(agent_path, "r") as f:
                content = f.read()

            # 메서드 이름으로 능력 추론
            import re

            methods = re.findall(r"def\s+(\w+)\s*\(", content)

            capability_keywords = {
                "process": "processing",
                "analyze": "analysis",
                "generate": "generation",
                "validate": "validation",
                "transform": "transformation",
                "optimize": "optimization",
                "search": "searching",
                "match": "matching",
            }

            for method in methods:
                for keyword, capability in capability_keywords.items():
                    if keyword in method.lower():
                        if capability not in capabilities:
                            capabilities.append(capability)

        except Exception as e:
            print(f"⚠️ Error extracting capabilities: {e}")

        return capabilities

    def get_agent(self, agent_id: str) -> Optional[AgentMetadata]:
        """에이전트 메타데이터 조회"""
        return self.agents.get(agent_id)

    def list_agents(self, filter_constraints: bool = False) -> List[AgentMetadata]:
        """
        에이전트 목록 조회

        Args:
            filter_constraints: 제약 조건을 만족하는 에이전트만 필터링

        Returns:
            에이전트 메타데이터 목록
        """
        agents = list(self.agents.values())

        if filter_constraints:
            agents = [a for a in agents if a.constraints_met]

        return sorted(agents, key=lambda a: a.fitness_score, reverse=True)

    def update_fitness(self, agent_id: str, fitness_score: float):
        """에이전트 적합도 점수 업데이트"""
        if agent_id in self.agents:
            self.agents[agent_id].fitness_score = round(fitness_score, 3)
            self._save_registry()

            # 성능 메트릭 기록
            if agent_id not in self.performance_metrics:
                self.performance_metrics[agent_id] = []
            self.performance_metrics[agent_id].append(fitness_score)

    def record_evolution(self, parent_id: str, child_id: str, mutation_type: str):
        """진화 이벤트 기록"""
        evolution_event = {
            "parent_id": parent_id,
            "child_id": child_id,
            "mutation_type": mutation_type,
            "timestamp": datetime.now().isoformat(),
            "generation": self.agents[parent_id].generation + 1 if parent_id in self.agents else 1,
        }

        self.evolution_history.append(evolution_event)

        # 자식 에이전트 정보 업데이트
        if child_id in self.agents:
            self.agents[child_id].parent_id = parent_id
            self.agents[child_id].generation = evolution_event["generation"]
            self.agents[child_id].evolution_count += 1
            self.agents[child_id].last_evolved = evolution_event["timestamp"]

        self._save_registry()

    def get_evolution_lineage(self, agent_id: str) -> List[str]:
        """에이전트의 진화 계보 추적"""
        lineage = []
        current_id = agent_id

        while current_id and current_id in self.agents:
            lineage.append(current_id)
            current_id = self.agents[current_id].parent_id

        return lineage

    def get_statistics(self) -> Dict[str, Any]:
        """레지스트리 통계"""
        total = len(self.agents)
        if total == 0:
            return {"total_agents": 0, "message": "No agents registered"}

        active = sum(1 for a in self.agents.values() if a.constraints_met)
        avg_size = sum(a.size_kb for a in self.agents.values()) / total
        avg_speed = sum(a.instantiation_us for a in self.agents.values()) / total
        avg_fitness = sum(a.fitness_score for a in self.agents.values()) / total

        return {
            "total_agents": total,
            "active_agents": active,
            "compliance_rate": f"{(active/total)*100:.1f}%",
            "average_size_kb": round(avg_size, 2),
            "average_speed_us": round(avg_speed, 2),
            "average_fitness": round(avg_fitness, 3),
            "total_evolutions": len(self.evolution_history),
            "generations": max((a.generation for a in self.agents.values()), default=0),
        }

    def validate_all_agents(self) -> Dict[str, List[str]]:
        """모든 에이전트 제약 조건 검증"""
        violations = {"size": [], "speed": [], "fitness": []}

        for agent in self.agents.values():
            if agent.size_kb > self.MAX_AGENT_SIZE_KB:
                violations["size"].append(f"{agent.name}: {agent.size_kb}KB")

            if agent.instantiation_us > self.MAX_INSTANTIATION_US:
                violations["speed"].append(f"{agent.name}: {agent.instantiation_us}μs")

            if agent.fitness_score < self.MIN_FITNESS_SCORE:
                violations["fitness"].append(f"{agent.name}: {agent.fitness_score}")

        return violations


# CLI 인터페이스
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Agent Registry Management")
    parser.add_argument("command", choices=["register", "list", "stats", "validate"])
    parser.add_argument("--agent-path", help="Path to agent file")
    parser.add_argument("--name", help="Agent name")

    args = parser.parse_args()

    registry = AgentRegistry()

    if args.command == "register":
        if args.agent_path:
            registry.register_agent(args.agent_path, args.name)
        else:
            print("Error: --agent-path required for registration")

    elif args.command == "list":
        agents = registry.list_agents(filter_constraints=True)
        print(f"\n📋 Registered Agents ({len(agents)} active):")
        for agent in agents:
            status = "✅" if agent.constraints_met else "⚠️"
            print(f"{status} {agent.name} (v{agent.version})")
            print(f"   Size: {agent.size_kb}KB, Speed: {agent.instantiation_us}μs")
            print(f"   Fitness: {agent.fitness_score}, Generation: {agent.generation}")

    elif args.command == "stats":
        stats = registry.get_statistics()
        print("\n📊 Registry Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

    elif args.command == "validate":
        violations = registry.validate_all_agents()
        print("\n🔍 Validation Results:")
        for category, agents in violations.items():
            if agents:
                print(f"\n❌ {category.upper()} violations:")
                for agent in agents:
                    print(f"  - {agent}")

        if not any(violations.values()):
            print("✅ All agents meet constraints!")

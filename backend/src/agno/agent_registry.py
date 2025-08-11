"""
Agno Framework Agent Registry
동적으로 생성된 에이전트들을 등록하고 저장하는 시스템
"""

import json
import pickle
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import aiofiles
from dataclasses import dataclass, asdict
import sqlite3
import os

@dataclass
class AgentMetadata:
    """에이전트 메타데이터"""
    agent_id: str
    name: str
    type: str
    version: str
    created_at: str
    updated_at: str
    blueprint: Dict[str, Any]
    tags: List[str]
    usage_count: int = 0
    performance_metrics: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.performance_metrics is None:
            self.performance_metrics = {}


class AgentRegistry:
    """에이전트 레지스트리 - 생성된 모든 에이전트 관리"""
    
    def __init__(self, storage_path: str = None):
        self.storage_path = Path(storage_path or "/home/ec2-user/T-DeveloperMVP/backend/agent_storage")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 디렉토리 구조 생성
        self.blueprints_dir = self.storage_path / "blueprints"
        self.instances_dir = self.storage_path / "instances"
        self.metadata_dir = self.storage_path / "metadata"
        self.code_dir = self.storage_path / "generated_code"
        
        for dir_path in [self.blueprints_dir, self.instances_dir, self.metadata_dir, self.code_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # SQLite DB for metadata
        self.db_path = self.storage_path / "agent_registry.db"
        self._init_database()
        
        # In-memory cache
        self.agent_cache = {}
        self.blueprint_cache = {}
    
    def _init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 에이전트 메타데이터 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                version TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                blueprint TEXT NOT NULL,
                tags TEXT,
                usage_count INTEGER DEFAULT 0,
                performance_metrics TEXT,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # 에이전트 사용 이력 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                project_id TEXT,
                used_at TEXT NOT NULL,
                execution_time_ms REAL,
                success BOOLEAN,
                FOREIGN KEY (agent_id) REFERENCES agents (agent_id)
            )
        """)
        
        # 인덱스 생성
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_type ON agents(type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_name ON agents(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_usage_agent ON agent_usage(agent_id)")
        
        conn.commit()
        conn.close()
    
    def generate_agent_id(self, name: str, type: str, version: str) -> str:
        """고유 에이전트 ID 생성"""
        data = f"{name}:{type}:{version}:{datetime.now().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    async def register_agent(
        self,
        agent: Any,
        blueprint: Dict[str, Any],
        generated_code: str = None
    ) -> str:
        """
        새 에이전트 등록
        
        Args:
            agent: 에이전트 인스턴스
            blueprint: 에이전트 블루프린트
            generated_code: 생성된 코드 (선택)
            
        Returns:
            agent_id: 등록된 에이전트 ID
        """
        # 메타데이터 생성
        agent_id = self.generate_agent_id(
            blueprint['name'],
            blueprint['type'],
            blueprint.get('version', '1.0.0')
        )
        
        metadata = AgentMetadata(
            agent_id=agent_id,
            name=blueprint['name'],
            type=blueprint['type'],
            version=blueprint.get('version', '1.0.0'),
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            blueprint=blueprint,
            tags=blueprint.get('tags', [])
        )
        
        # 1. 블루프린트 저장
        blueprint_path = self.blueprints_dir / f"{agent_id}.json"
        async with aiofiles.open(blueprint_path, 'w') as f:
            await f.write(json.dumps(blueprint, indent=2))
        
        # 2. 에이전트 인스턴스 저장 (pickle 대신 blueprint만 저장)
        # Note: 동적으로 생성된 클래스는 pickle이 안되므로 blueprint로 재생성
        instance_path = self.instances_dir / f"{agent_id}.json"
        async with aiofiles.open(instance_path, 'w') as f:
            await f.write(json.dumps({
                'blueprint': blueprint,
                'type': 'dynamic_agent',
                'recreate_required': True
            }))
        
        # 3. 메타데이터 저장
        metadata_path = self.metadata_dir / f"{agent_id}.json"
        async with aiofiles.open(metadata_path, 'w') as f:
            await f.write(json.dumps(asdict(metadata), indent=2))
        
        # 4. 생성된 코드 저장 (있는 경우)
        if generated_code:
            code_path = self.code_dir / f"{agent_id}.js"
            async with aiofiles.open(code_path, 'w') as f:
                await f.write(generated_code)
        
        # 5. DB에 메타데이터 저장
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO agents 
            (agent_id, name, type, version, created_at, updated_at, blueprint, tags, usage_count, performance_metrics)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            agent_id,
            metadata.name,
            metadata.type,
            metadata.version,
            metadata.created_at,
            metadata.updated_at,
            json.dumps(metadata.blueprint),
            json.dumps(metadata.tags),
            0,
            json.dumps(metadata.performance_metrics)
        ))
        
        conn.commit()
        conn.close()
        
        # 6. 캐시 업데이트
        self.agent_cache[agent_id] = agent
        self.blueprint_cache[agent_id] = blueprint
        
        print(f"✅ Agent registered: {metadata.name} (ID: {agent_id})")
        
        return agent_id
    
    async def load_agent(self, agent_id: str) -> Optional[Any]:
        """
        저장된 에이전트 로드
        """
        # 캐시 확인
        if agent_id in self.agent_cache:
            return self.agent_cache[agent_id]
        
        # 파일에서 로드
        instance_path = self.instances_dir / f"{agent_id}.json"
        if not instance_path.exists():
            return None
        
        async with aiofiles.open(instance_path, 'r') as f:
            agent_data = json.loads(await f.read())
        
        # 동적으로 재생성이 필요한 경우
        if agent_data.get('recreate_required'):
            from src.agno.agent_generator import create_agent_from_blueprint
            agent = await create_agent_from_blueprint(agent_data['blueprint'])
        else:
            # 일반 에이전트 (추후 구현)
            agent = None
        
        # 캐시에 저장
        if agent:
            self.agent_cache[agent_id] = agent
        
        # 사용 횟수 증가
        self._update_usage_count(agent_id)
        
        return agent
    
    def _update_usage_count(self, agent_id: str):
        """사용 횟수 업데이트"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE agents SET usage_count = usage_count + 1
            WHERE agent_id = ?
        """, (agent_id,))
        
        conn.commit()
        conn.close()
    
    async def get_agent_metadata(self, agent_id: str) -> Optional[AgentMetadata]:
        """에이전트 메타데이터 조회"""
        metadata_path = self.metadata_dir / f"{agent_id}.json"
        
        if not metadata_path.exists():
            return None
        
        async with aiofiles.open(metadata_path, 'r') as f:
            data = json.loads(await f.read())
            return AgentMetadata(**data)
    
    def list_agents(
        self, 
        type: str = None, 
        tags: List[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        등록된 에이전트 목록 조회
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        query = "SELECT * FROM agents WHERE is_active = 1"
        params = []
        
        if type:
            query += " AND type = ?"
            params.append(type)
        
        if tags:
            # JSON 배열로 저장된 태그 검색
            tag_conditions = []
            for tag in tags:
                tag_conditions.append(f"tags LIKE '%\"{tag}\"%'")
            if tag_conditions:
                query += f" AND ({' OR '.join(tag_conditions)})"
        
        query += f" ORDER BY usage_count DESC LIMIT {limit}"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        agents = []
        for row in results:
            agents.append({
                'agent_id': row[0],
                'name': row[1],
                'type': row[2],
                'version': row[3],
                'created_at': row[4],
                'usage_count': row[8],
                'tags': json.loads(row[7]) if row[7] else []
            })
        
        conn.close()
        return agents
    
    async def record_usage(
        self,
        agent_id: str,
        project_id: str,
        execution_time_ms: float,
        success: bool
    ):
        """에이전트 사용 기록"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO agent_usage (agent_id, project_id, used_at, execution_time_ms, success)
            VALUES (?, ?, ?, ?, ?)
        """, (
            agent_id,
            project_id,
            datetime.now().isoformat(),
            execution_time_ms,
            success
        ))
        
        conn.commit()
        conn.close()
    
    def search_agents(self, query: str) -> List[Dict[str, Any]]:
        """에이전트 검색"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT agent_id, name, type, version, usage_count
            FROM agents
            WHERE is_active = 1
            AND (name LIKE ? OR type LIKE ? OR tags LIKE ?)
            ORDER BY usage_count DESC
            LIMIT 20
        """, (f"%{query}%", f"%{query}%", f"%{query}%"))
        
        results = cursor.fetchall()
        
        agents = []
        for row in results:
            agents.append({
                'agent_id': row[0],
                'name': row[1],
                'type': row[2],
                'version': row[3],
                'usage_count': row[4]
            })
        
        conn.close()
        return agents
    
    def get_popular_agents(self, limit: int = 10) -> List[Dict[str, Any]]:
        """인기 에이전트 조회"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT agent_id, name, type, usage_count
            FROM agents
            WHERE is_active = 1
            ORDER BY usage_count DESC
            LIMIT ?
        """, (limit,))
        
        results = cursor.fetchall()
        
        agents = []
        for row in results:
            agents.append({
                'agent_id': row[0],
                'name': row[1],
                'type': row[2],
                'usage_count': row[3]
            })
        
        conn.close()
        return agents
    
    async def export_agent(self, agent_id: str, export_path: str):
        """에이전트 내보내기 (이식 가능한 형태로)"""
        metadata = await self.get_agent_metadata(agent_id)
        if not metadata:
            raise ValueError(f"Agent {agent_id} not found")
        
        export_data = {
            'metadata': asdict(metadata),
            'blueprint': metadata.blueprint,
            'version': '1.0.0',
            'export_date': datetime.now().isoformat()
        }
        
        # 생성된 코드 포함
        code_path = self.code_dir / f"{agent_id}.js"
        if code_path.exists():
            async with aiofiles.open(code_path, 'r') as f:
                export_data['generated_code'] = await f.read()
        
        # 내보내기
        export_file = Path(export_path) / f"{metadata.name}_export.json"
        async with aiofiles.open(export_file, 'w') as f:
            await f.write(json.dumps(export_data, indent=2))
        
        return str(export_file)
    
    def get_statistics(self) -> Dict[str, Any]:
        """레지스트리 통계"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 전체 에이전트 수
        cursor.execute("SELECT COUNT(*) FROM agents WHERE is_active = 1")
        total_agents = cursor.fetchone()[0]
        
        # 타입별 분포
        cursor.execute("""
            SELECT type, COUNT(*) FROM agents
            WHERE is_active = 1
            GROUP BY type
        """)
        type_distribution = dict(cursor.fetchall())
        
        # 전체 사용 횟수
        cursor.execute("SELECT SUM(usage_count) FROM agents")
        total_usage = cursor.fetchone()[0] or 0
        
        # 평균 실행 시간
        cursor.execute("SELECT AVG(execution_time_ms) FROM agent_usage WHERE success = 1")
        avg_execution_time = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_agents': total_agents,
            'type_distribution': type_distribution,
            'total_usage': total_usage,
            'average_execution_time_ms': avg_execution_time,
            'storage_size_mb': self._get_storage_size() / (1024 * 1024)
        }
    
    def _get_storage_size(self) -> int:
        """저장소 크기 계산"""
        total_size = 0
        for path in self.storage_path.rglob('*'):
            if path.is_file():
                total_size += path.stat().st_size
        return total_size


# 글로벌 레지스트리 인스턴스
agent_registry = AgentRegistry()


async def test_registry():
    """레지스트리 테스트"""
    from src.agno.agent_generator import create_agent_from_blueprint
    
    # 테스트 블루프린트
    blueprint = {
        'name': 'TestCRUDAgent',
        'type': 'data_manager',
        'version': '1.0.0',
        'tags': ['test', 'crud', 'todo'],
        'config': {
            'entity': 'TestItem',
            'fields': {'id': 'string', 'name': 'string'}
        }
    }
    
    # 에이전트 생성
    agent = await create_agent_from_blueprint(blueprint)
    
    # 레지스트리에 등록
    agent_id = await agent_registry.register_agent(
        agent=agent,
        blueprint=blueprint,
        generated_code="// Test generated code"
    )
    
    print(f"Registered agent: {agent_id}")
    
    # 에이전트 조회
    loaded_agent = await agent_registry.load_agent(agent_id)
    print(f"Loaded agent: {loaded_agent}")
    
    # 목록 조회
    agents = agent_registry.list_agents(type='data_manager')
    print(f"Data manager agents: {agents}")
    
    # 통계
    stats = agent_registry.get_statistics()
    print(f"Registry statistics: {stats}")


if __name__ == "__main__":
    asyncio.run(test_registry())
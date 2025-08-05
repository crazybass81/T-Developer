# backend/src/agents/implementations/parser_dependency_analyzer.py
from typing import Dict, List, Any, Set, Tuple, Optional
from dataclasses import dataclass
import networkx as nx
import re

@dataclass
class Dependency:
    source_id: str
    target_id: str
    dependency_type: str  # 'requires', 'depends_on', 'blocks', 'enables'
    strength: float  # 0.0 ~ 1.0
    description: str

@dataclass
class DependencyGraph:
    nodes: List[Dict[str, Any]]
    edges: List[Dependency]
    cycles: List[List[str]]
    critical_path: List[str]
    levels: Dict[str, int]

class DependencyAnalyzer:
    """요구사항 간 의존성 분석"""

    def __init__(self):
        self.dependency_patterns = {
            'explicit': [
                r'depends\s+on\s+([^.]+)',
                r'requires\s+([^.]+)',
                r'needs\s+([^.]+)',
                r'after\s+([^.]+)',
                r'before\s+([^.]+)'
            ],
            'implicit': [
                r'(login|authentication).*?(user|profile)',
                r'(payment).*?(cart|order)',
                r'(search).*?(index|database)',
                r'(notification).*?(user|event)'
            ]
        }

    async def analyze_dependencies(
        self,
        requirements: List[Dict[str, Any]]
    ) -> DependencyGraph:
        """요구사항 간 의존성 분석"""

        # 의존성 추출
        dependencies = await self._extract_dependencies(requirements)

        # 그래프 생성
        graph = self._build_dependency_graph(requirements, dependencies)

        # 순환 의존성 검출
        cycles = self._detect_cycles(graph)

        # 임계 경로 계산
        critical_path = self._calculate_critical_path(graph)

        # 레벨 계산 (위상 정렬)
        levels = self._calculate_levels(graph)

        return DependencyGraph(
            nodes=requirements,
            edges=dependencies,
            cycles=cycles,
            critical_path=critical_path,
            levels=levels
        )

    async def _extract_dependencies(
        self,
        requirements: List[Dict[str, Any]]
    ) -> List[Dependency]:
        """의존성 추출"""
        dependencies = []

        # 명시적 의존성
        explicit_deps = await self._extract_explicit_dependencies(requirements)
        dependencies.extend(explicit_deps)

        # 암시적 의존성
        implicit_deps = await self._extract_implicit_dependencies(requirements)
        dependencies.extend(implicit_deps)

        # 의미적 의존성
        semantic_deps = await self._extract_semantic_dependencies(requirements)
        dependencies.extend(semantic_deps)

        return dependencies

    async def _extract_explicit_dependencies(
        self,
        requirements: List[Dict[str, Any]]
    ) -> List[Dependency]:
        """명시적 의존성 추출"""
        dependencies = []

        for req in requirements:
            description = req.get('description', '').lower()

            for pattern in self.dependency_patterns['explicit']:
                matches = re.findall(pattern, description, re.IGNORECASE)
                for match in matches:
                    # 매칭되는 요구사항 찾기
                    target_req = self._find_matching_requirement(match, requirements)
                    if target_req and target_req['id'] != req['id']:
                        dependencies.append(Dependency(
                            source_id=req['id'],
                            target_id=target_req['id'],
                            dependency_type='requires',
                            strength=0.9,
                            description=f"Explicitly requires: {match}"
                        ))

        return dependencies

    async def _extract_implicit_dependencies(
        self,
        requirements: List[Dict[str, Any]]
    ) -> List[Dependency]:
        """암시적 의존성 추출"""
        dependencies = []

        # 도메인 지식 기반 의존성
        domain_dependencies = {
            'authentication': ['user_management'],
            'authorization': ['authentication'],
            'payment': ['cart', 'user_account'],
            'order_processing': ['payment', 'inventory'],
            'notification': ['user_preferences', 'event_system'],
            'search': ['indexing', 'database'],
            'reporting': ['data_collection', 'analytics']
        }

        for req in requirements:
            req_keywords = self._extract_keywords(req.get('description', ''))

            for keyword in req_keywords:
                if keyword in domain_dependencies:
                    for dep_keyword in domain_dependencies[keyword]:
                        target_req = self._find_requirement_by_keyword(
                            dep_keyword,
                            requirements
                        )
                        if target_req and target_req['id'] != req['id']:
                            dependencies.append(Dependency(
                                source_id=req['id'],
                                target_id=target_req['id'],
                                dependency_type='depends_on',
                                strength=0.7,
                                description=f"Domain dependency: {keyword} -> {dep_keyword}"
                            ))

        return dependencies

    async def _extract_semantic_dependencies(
        self,
        requirements: List[Dict[str, Any]]
    ) -> List[Dependency]:
        """의미적 의존성 추출"""
        dependencies = []

        # 데이터 흐름 기반 의존성
        data_flow_deps = await self._analyze_data_flow_dependencies(requirements)
        dependencies.extend(data_flow_deps)

        # 시간적 의존성
        temporal_deps = await self._analyze_temporal_dependencies(requirements)
        dependencies.extend(temporal_deps)

        # 기능적 의존성
        functional_deps = await self._analyze_functional_dependencies(requirements)
        dependencies.extend(functional_deps)

        return dependencies

    def _build_dependency_graph(
        self,
        requirements: List[Dict[str, Any]],
        dependencies: List[Dependency]
    ) -> nx.DiGraph:
        """의존성 그래프 구축"""
        graph = nx.DiGraph()

        # 노드 추가
        for req in requirements:
            graph.add_node(req['id'], **req)

        # 엣지 추가
        for dep in dependencies:
            graph.add_edge(
                dep.source_id,
                dep.target_id,
                dependency_type=dep.dependency_type,
                strength=dep.strength,
                description=dep.description
            )

        return graph

    def _detect_cycles(self, graph: nx.DiGraph) -> List[List[str]]:
        """순환 의존성 검출"""
        try:
            cycles = list(nx.simple_cycles(graph))
            return cycles
        except nx.NetworkXError:
            return []

    def _calculate_critical_path(self, graph: nx.DiGraph) -> List[str]:
        """임계 경로 계산"""
        if not graph.nodes():
            return []

        # 가장 긴 경로 찾기
        longest_path = []
        max_length = 0

        # 모든 노드 쌍에 대해 경로 계산
        for source in graph.nodes():
            for target in graph.nodes():
                if source != target:
                    try:
                        path = nx.shortest_path(graph, source, target)
                        if len(path) > max_length:
                            max_length = len(path)
                            longest_path = path
                    except nx.NetworkXNoPath:
                        continue

        return longest_path

    def _calculate_levels(self, graph: nx.DiGraph) -> Dict[str, int]:
        """위상 정렬을 통한 레벨 계산"""
        levels = {}

        try:
            # 위상 정렬
            topo_order = list(nx.topological_sort(graph))

            # 각 노드의 레벨 계산
            for node in topo_order:
                predecessors = list(graph.predecessors(node))
                if not predecessors:
                    levels[node] = 0
                else:
                    max_pred_level = max(levels.get(pred, 0) for pred in predecessors)
                    levels[node] = max_pred_level + 1

        except nx.NetworkXError:
            # 순환이 있는 경우 기본 레벨 할당
            for i, node in enumerate(graph.nodes()):
                levels[node] = i

        return levels

    def _find_matching_requirement(
        self,
        keyword: str,
        requirements: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """키워드와 매칭되는 요구사항 찾기"""
        keyword_lower = keyword.lower().strip()

        for req in requirements:
            description = req.get('description', '').lower()
            name = req.get('name', '').lower()

            if keyword_lower in description or keyword_lower in name:
                return req

        return None

    def _find_requirement_by_keyword(
        self,
        keyword: str,
        requirements: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """키워드로 요구사항 찾기"""
        for req in requirements:
            req_keywords = self._extract_keywords(req.get('description', ''))
            if keyword in req_keywords:
                return req
        return None

    def _extract_keywords(self, text: str) -> List[str]:
        """텍스트에서 키워드 추출"""
        # 간단한 키워드 추출 (실제로는 더 정교한 NLP 사용)
        keywords = []
        
        # 도메인 키워드
        domain_keywords = [
            'authentication', 'authorization', 'login', 'user',
            'payment', 'cart', 'order', 'checkout',
            'search', 'filter', 'sort', 'index',
            'notification', 'email', 'sms', 'alert',
            'report', 'analytics', 'dashboard', 'chart'
        ]

        text_lower = text.lower()
        for keyword in domain_keywords:
            if keyword in text_lower:
                keywords.append(keyword)

        return keywords

    async def _analyze_data_flow_dependencies(
        self,
        requirements: List[Dict[str, Any]]
    ) -> List[Dependency]:
        """데이터 흐름 기반 의존성 분석"""
        dependencies = []

        # 데이터 엔티티 추출
        data_entities = {}
        for req in requirements:
            entities = self._extract_data_entities(req.get('description', ''))
            data_entities[req['id']] = entities

        # 공통 엔티티를 사용하는 요구사항 간 의존성
        for req1_id, entities1 in data_entities.items():
            for req2_id, entities2 in data_entities.items():
                if req1_id != req2_id:
                    common_entities = set(entities1) & set(entities2)
                    if common_entities:
                        # 데이터 생성자 -> 데이터 소비자 의존성
                        if self._is_data_producer(req1_id, requirements):
                            dependencies.append(Dependency(
                                source_id=req2_id,
                                target_id=req1_id,
                                dependency_type='depends_on',
                                strength=0.6,
                                description=f"Data dependency: {', '.join(common_entities)}"
                            ))

        return dependencies

    def _extract_data_entities(self, text: str) -> List[str]:
        """데이터 엔티티 추출"""
        entities = []
        
        # 일반적인 데이터 엔티티 패턴
        entity_patterns = [
            r'\b(user|customer|account|profile)\b',
            r'\b(product|item|inventory)\b',
            r'\b(order|transaction|payment)\b',
            r'\b(report|data|record)\b'
        ]

        text_lower = text.lower()
        for pattern in entity_patterns:
            matches = re.findall(pattern, text_lower)
            entities.extend(matches)

        return list(set(entities))

    def _is_data_producer(
        self,
        req_id: str,
        requirements: List[Dict[str, Any]]
    ) -> bool:
        """데이터 생성자인지 확인"""
        req = next((r for r in requirements if r['id'] == req_id), None)
        if not req:
            return False

        description = req.get('description', '').lower()
        producer_keywords = ['create', 'add', 'insert', 'register', 'generate']

        return any(keyword in description for keyword in producer_keywords)
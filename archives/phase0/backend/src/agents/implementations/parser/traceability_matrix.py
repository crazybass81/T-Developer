"""
Parser Agent - Traceability Matrix Generator
Task 4.24.3 Implementation
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import pandas as pd
from datetime import datetime
import json

@dataclass
class TraceabilityLink:
    source_id: str
    target_id: str
    link_type: str  # 'implements', 'tests', 'derives_from', 'satisfies'
    confidence: float
    metadata: Dict[str, Any]

class TraceabilityMatrixGenerator:
    """요구사항 추적성 매트릭스 생성기"""

    def __init__(self):
        self.coverage_analyzer = CoverageAnalyzer()

    async def generate_traceability_matrix(
        self,
        parsed_project,
        additional_artifacts: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """추적성 매트릭스 생성"""

        # 1. 추적 가능한 항목 수집
        traceable_items = await self._collect_traceable_items(
            parsed_project, additional_artifacts
        )

        # 2. 추적성 링크 생성
        links = await self._generate_traceability_links(traceable_items)

        # 3. 매트릭스 구성
        matrix = self._build_matrix(traceable_items, links)

        # 4. 커버리지 분석
        coverage = await self.coverage_analyzer.analyze(matrix, traceable_items)

        # 5. 갭 분석
        gaps = self._identify_gaps(matrix, traceable_items)

        return {
            'matrix': matrix.to_dict(),
            'links': [link.__dict__ for link in links],
            'coverage': coverage,
            'gaps': gaps,
            'report': await self._generate_report(matrix, coverage, gaps)
        }

    async def _collect_traceable_items(
        self, parsed_project, additional_artifacts
    ) -> Dict[str, List[Dict[str, Any]]]:
        """추적 가능한 항목 수집"""

        items = {
            'business_requirements': [],
            'functional_requirements': [],
            'technical_requirements': [],
            'user_stories': [],
            'test_cases': [],
            'design_elements': []
        }

        # 비즈니스 요구사항
        for req in parsed_project.business_requirements:
            items['business_requirements'].append({
                'id': req.id,
                'description': req.description,
                'priority': req.priority
            })

        # 기능 요구사항
        for req in parsed_project.functional_requirements:
            items['functional_requirements'].append({
                'id': req.id,
                'description': req.description,
                'category': req.category,
                'acceptance_criteria': req.acceptance_criteria
            })

        # 사용자 스토리
        for story in parsed_project.user_stories:
            items['user_stories'].append({
                'id': story.get('id'),
                'narrative': story.get('narrative'),
                'linked_requirements': story.get('linked_requirements', [])
            })

        return items

    async def _generate_traceability_links(
        self, traceable_items: Dict[str, List[Dict[str, Any]]]
    ) -> List[TraceabilityLink]:
        """추적성 링크 생성"""

        links = []

        # 비즈니스 → 기능 요구사항 링크
        links.extend(await self._link_business_to_functional(
            traceable_items['business_requirements'],
            traceable_items['functional_requirements']
        ))

        # 사용자 스토리 → 기능 요구사항 링크
        links.extend(await self._link_stories_to_requirements(
            traceable_items['user_stories'],
            traceable_items['functional_requirements']
        ))

        return links

    async def _link_business_to_functional(
        self, business_reqs, functional_reqs
    ) -> List[TraceabilityLink]:
        """비즈니스 요구사항과 기능 요구사항 연결"""

        links = []
        for br in business_reqs:
            for fr in functional_reqs:
                similarity = self._calculate_similarity(
                    br['description'], fr['description']
                )
                if similarity > 0.6:
                    links.append(TraceabilityLink(
                        source_id=br['id'],
                        target_id=fr['id'],
                        link_type='derives_from',
                        confidence=similarity,
                        metadata={'similarity_score': similarity}
                    ))
        return links

    async def _link_stories_to_requirements(
        self, user_stories, functional_reqs
    ) -> List[TraceabilityLink]:
        """사용자 스토리와 기능 요구사항 연결"""

        links = []
        for story in user_stories:
            if not story.get('id'):
                continue
                
            for req in functional_reqs:
                similarity = self._calculate_similarity(
                    story.get('narrative', ''), req['description']
                )
                if similarity > 0.5:
                    links.append(TraceabilityLink(
                        source_id=story['id'],
                        target_id=req['id'],
                        link_type='implements',
                        confidence=similarity,
                        metadata={'story_type': 'user_story'}
                    ))
        return links

    def _build_matrix(
        self, items: Dict[str, List[Dict[str, Any]]], links: List[TraceabilityLink]
    ) -> pd.DataFrame:
        """추적성 매트릭스 구축"""

        # 모든 항목 ID 수집
        all_ids = []
        for item_list in items.values():
            for item in item_list:
                if item.get('id'):
                    all_ids.append(item['id'])

        # 매트릭스 초기화
        matrix = pd.DataFrame(index=all_ids, columns=all_ids, data='')

        # 링크 정보로 매트릭스 채우기
        for link in links:
            if link.source_id in all_ids and link.target_id in all_ids:
                matrix.loc[link.source_id, link.target_id] = link.link_type

        return matrix

    def _identify_gaps(
        self, matrix: pd.DataFrame, items: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """갭 분석"""

        gaps = []
        
        # 연결되지 않은 요구사항 찾기
        for item_type, item_list in items.items():
            for item in item_list:
                item_id = item.get('id')
                if not item_id:
                    continue
                    
                # 해당 행과 열이 모두 비어있는지 확인
                if item_id in matrix.index:
                    row_empty = matrix.loc[item_id].eq('').all()
                    col_empty = matrix[item_id].eq('').all() if item_id in matrix.columns else True
                    
                    if row_empty and col_empty:
                        gaps.append({
                            'item_id': item_id,
                            'item_type': item_type,
                            'description': item.get('description', ''),
                            'gap_type': 'unlinked'
                        })

        return gaps

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """텍스트 유사도 계산"""
        if not text1 or not text2:
            return 0.0
            
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0

    async def _generate_report(
        self, matrix: pd.DataFrame, coverage: Dict[str, Any], gaps: List[Dict[str, Any]]
    ) -> str:
        """HTML 추적성 보고서 생성"""

        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Requirements Traceability Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ background: #f0f0f0; padding: 15px; border-radius: 5px; }}
                .matrix-table {{ border-collapse: collapse; font-size: 12px; }}
                .matrix-table td, .matrix-table th {{
                    border: 1px solid #ddd; padding: 5px; text-align: center;
                }}
                .matrix-table th {{ background-color: #f2f2f2; }}
                .linked {{ background-color: #90EE90; }}
                .gap-item {{ margin: 10px 0; padding: 10px; background: #f9f9f9; }}
            </style>
        </head>
        <body>
            <h1>Requirements Traceability Report</h1>
            
            <div class="summary">
                <h2>Coverage Summary</h2>
                <p>Overall Coverage: {coverage.get('overall_coverage', 0):.1%}</p>
                <p>Total Requirements: {len(matrix.index)}</p>
                <p>Linked Requirements: {coverage.get('linked_count', 0)}</p>
                <p>Gaps Found: {len(gaps)}</p>
            </div>

            <h2>Identified Gaps</h2>
            <div class="gaps-section">
                {''.join([f'<div class="gap-item"><strong>{gap["item_id"]}</strong>: {gap["description"]}</div>' for gap in gaps])}
            </div>

            <h2>Recommendations</h2>
            <ul>
                <li>Review unlinked requirements for missing connections</li>
                <li>Add test cases for uncovered functional requirements</li>
                <li>Create user stories for business requirements without implementation</li>
            </ul>
        </body>
        </html>
        """

        return html_template


class CoverageAnalyzer:
    """커버리지 분석기"""

    async def analyze(
        self, matrix: pd.DataFrame, items: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """커버리지 분석"""

        total_items = sum(len(item_list) for item_list in items.values())
        linked_items = 0

        # 연결된 항목 수 계산
        for item_list in items.values():
            for item in item_list:
                item_id = item.get('id')
                if item_id and item_id in matrix.index:
                    # 해당 행이나 열에 연결이 있는지 확인
                    has_links = not (matrix.loc[item_id].eq('').all() and 
                                   (matrix[item_id].eq('').all() if item_id in matrix.columns else True))
                    if has_links:
                        linked_items += 1

        overall_coverage = linked_items / total_items if total_items > 0 else 0

        return {
            'overall_coverage': overall_coverage,
            'total_items': total_items,
            'linked_count': linked_items,
            'unlinked_count': total_items - linked_items
        }
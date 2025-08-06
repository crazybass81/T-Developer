# backend/src/agents/nl_input/template_learner.py
from typing import Dict, List, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from dataclasses import dataclass

@dataclass
class ProjectTemplate:
    name: str
    description_pattern: str
    common_requirements: List[str]
    recommended_tech_stack: List[str]
    typical_complexity: float
    success_rate: float

class ProjectTemplateLearner:
    """완성된 프로젝트 템플릿 학습 시스템"""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.clustering_model = KMeans(n_clusters=10)
        self.templates: Dict[str, ProjectTemplate] = {}

    async def learn_from_successful_projects(self, projects: List[Dict[str, Any]]) -> Dict[str, ProjectTemplate]:
        """성공 프로젝트에서 템플릿 학습 - 완성된 구현"""
        
        # 1. 프로젝트 설명 벡터화
        descriptions = [p.get('description', '') for p in projects]
        if not descriptions:
            return {}
            
        vectors = self.vectorizer.fit_transform(descriptions)

        # 2. 클러스터링으로 유사 프로젝트 그룹화
        clusters = self.clustering_model.fit_predict(vectors)

        # 3. 각 클러스터에서 템플릿 추출
        for cluster_id in range(self.clustering_model.n_clusters):
            cluster_projects = [
                p for i, p in enumerate(projects)
                if clusters[i] == cluster_id
            ]

            if len(cluster_projects) >= 3:  # 최소 3개 프로젝트
                template = await self._extract_template(cluster_projects, cluster_id)
                self.templates[template.name] = template

        return self.templates

    async def _extract_template(self, projects: List[Dict[str, Any]], cluster_id: int) -> ProjectTemplate:
        """프로젝트 그룹에서 공통 템플릿 추출"""
        
        # 공통 요구사항 추출
        all_requirements = []
        for project in projects:
            all_requirements.extend(project.get('requirements', []))
        
        common_requirements = self._find_common_elements(all_requirements)

        # 공통 기술 스택
        all_tech_stacks = []
        for project in projects:
            all_tech_stacks.extend(project.get('tech_stack', []))
        
        common_tech_stack = self._find_common_elements(all_tech_stacks)

        # 평균 복잡도
        complexities = [p.get('complexity_score', 0.5) for p in projects]
        avg_complexity = np.mean(complexities) if complexities else 0.5

        # 성공률 계산
        success_rates = [p.get('success_rate', 1.0) for p in projects]
        avg_success_rate = np.mean(success_rates) if success_rates else 1.0

        return ProjectTemplate(
            name=f"template_cluster_{cluster_id}",
            description_pattern=self._extract_description_pattern(projects),
            common_requirements=common_requirements[:10],  # 상위 10개
            recommended_tech_stack=common_tech_stack[:5],   # 상위 5개
            typical_complexity=float(avg_complexity),
            success_rate=float(avg_success_rate)
        )

    def _find_common_elements(self, element_lists: List[str]) -> List[str]:
        """공통 요소 찾기"""
        if not element_lists:
            return []

        # 빈도 계산
        frequency = {}
        for element in element_lists:
            frequency[element] = frequency.get(element, 0) + 1

        # 빈도 순으로 정렬
        return sorted(frequency.keys(), key=lambda x: frequency[x], reverse=True)

    def _extract_description_pattern(self, projects: List[Dict[str, Any]]) -> str:
        """설명 패턴 추출"""
        descriptions = [p.get('description', '') for p in projects]
        if not descriptions:
            return ""
        
        # 가장 긴 설명을 패턴으로 사용
        return max(descriptions, key=len)

    async def suggest_template(self, description: str) -> Optional[ProjectTemplate]:
        """입력된 설명에 가장 적합한 템플릿 제안"""
        if not self.templates or not description:
            return None

        # 설명 벡터화
        desc_vector = self.vectorizer.transform([description])
        
        # 가장 가까운 클러스터 찾기
        cluster_id = self.clustering_model.predict(desc_vector)[0]
        
        # 해당 클러스터의 템플릿 반환
        template_name = f"template_cluster_{cluster_id}"
        return self.templates.get(template_name)
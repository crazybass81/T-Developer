from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
import json

@dataclass
class ProjectTemplate:
    name: str
    description_pattern: str
    common_requirements: List[str]
    recommended_tech_stack: Dict[str, List[str]]
    typical_complexity: float
    success_rate: float
    typical_timeline: str
    common_challenges: List[str]
    cluster_id: int = 0

@dataclass
class Project:
    original_description: str
    requirements: List[str]
    tech_stack: List[str]
    complexity_score: float
    success: bool
    timeline_days: int

class ProjectTemplateLearner:
    """성공적인 프로젝트에서 패턴을 학습하여 템플릿 생성"""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.clustering_model = KMeans(n_clusters=20, random_state=42)
        self.templates: Dict[str, ProjectTemplate] = {}

    async def learn_from_successful_projects(
        self,
        projects: List[Project]
    ) -> Dict[str, ProjectTemplate]:
        """성공 프로젝트에서 템플릿 학습"""

        # 1. 프로젝트 설명 벡터화
        descriptions = [p.original_description for p in projects]
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

    async def _extract_template(
        self,
        projects: List[Project],
        cluster_id: int
    ) -> ProjectTemplate:
        """프로젝트 그룹에서 공통 템플릿 추출"""

        # 공통 요구사항 추출
        common_requirements = self._find_common_elements(
            [p.requirements for p in projects]
        )

        # 공통 기술 스택
        common_tech_stack = self._find_common_elements(
            [p.tech_stack for p in projects]
        )

        # 평균 복잡도 및 규모
        avg_complexity = np.mean([p.complexity_score for p in projects])

        # 템플릿 이름 생성
        template_name = self._generate_template_name(
            common_requirements,
            common_tech_stack
        )

        return ProjectTemplate(
            name=template_name,
            description_pattern=self._extract_description_pattern(projects),
            common_requirements=common_requirements,
            recommended_tech_stack=self._group_tech_stack(common_tech_stack),
            typical_complexity=avg_complexity,
            success_rate=self._calculate_success_rate(projects),
            typical_timeline=self._calculate_typical_timeline(projects),
            common_challenges=self._extract_common_challenges(projects),
            cluster_id=cluster_id
        )

    async def suggest_template(
        self,
        description: str
    ) -> Optional[ProjectTemplate]:
        """입력된 설명에 가장 적합한 템플릿 제안"""

        if not self.templates:
            return None

        # 설명 벡터화
        desc_vector = self.vectorizer.transform([description])

        # 가장 가까운 클러스터 찾기
        cluster_id = self.clustering_model.predict(desc_vector)[0]

        # 해당 클러스터의 템플릿 반환
        for template in self.templates.values():
            if template.cluster_id == cluster_id:
                return template

        return None

    def _find_common_elements(
        self,
        element_lists: List[List[str]]
    ) -> List[str]:
        """여러 리스트에서 공통 요소 찾기"""

        if not element_lists:
            return []

        # 빈도 계산
        frequency = {}
        for elements in element_lists:
            for elem in elements:
                frequency[elem] = frequency.get(elem, 0) + 1

        # 50% 이상 나타나는 요소만 선택
        threshold = len(element_lists) * 0.5
        common = [elem for elem, freq in frequency.items() if freq >= threshold]

        return sorted(common, key=lambda x: frequency[x], reverse=True)

    def _generate_template_name(
        self,
        requirements: List[str],
        tech_stack: List[str]
    ) -> str:
        """템플릿 이름 생성"""
        
        # 주요 키워드 추출
        keywords = []
        
        # 요구사항에서 키워드
        for req in requirements[:2]:  # 상위 2개
            keywords.extend(req.split()[:2])
        
        # 기술 스택에서 키워드
        keywords.extend(tech_stack[:2])
        
        # 정리 및 조합
        clean_keywords = [k.lower().strip() for k in keywords if len(k) > 2]
        return "_".join(clean_keywords[:3]) + "_template"

    def _extract_description_pattern(self, projects: List[Project]) -> str:
        """설명 패턴 추출"""
        descriptions = [p.original_description for p in projects]
        
        # 간단한 패턴 추출 (실제로는 더 정교한 NLP 필요)
        common_words = []
        for desc in descriptions:
            words = desc.lower().split()
            common_words.extend(words)
        
        # 빈도 기반 패턴
        word_freq = {}
        for word in common_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        return " ".join([word for word, _ in top_words])

    def _group_tech_stack(self, tech_stack: List[str]) -> Dict[str, List[str]]:
        """기술 스택을 카테고리별로 그룹화"""
        
        categories = {
            'frontend': ['react', 'vue', 'angular', 'svelte'],
            'backend': ['node', 'python', 'java', 'go', 'django', 'fastapi'],
            'database': ['mysql', 'postgresql', 'mongodb', 'redis'],
            'cloud': ['aws', 'azure', 'gcp']
        }
        
        grouped = {}
        for tech in tech_stack:
            tech_lower = tech.lower()
            for category, techs in categories.items():
                if any(t in tech_lower for t in techs):
                    if category not in grouped:
                        grouped[category] = []
                    grouped[category].append(tech)
                    break
        
        return grouped

    def _calculate_success_rate(self, projects: List[Project]) -> float:
        """성공률 계산"""
        successful = sum(1 for p in projects if p.success)
        return successful / len(projects) if projects else 0.0

    def _calculate_typical_timeline(self, projects: List[Project]) -> str:
        """일반적인 타임라인 계산"""
        timelines = [p.timeline_days for p in projects]
        avg_days = np.mean(timelines)
        
        if avg_days < 30:
            return "1-4 weeks"
        elif avg_days < 90:
            return "1-3 months"
        elif avg_days < 180:
            return "3-6 months"
        else:
            return "6+ months"

    def _extract_common_challenges(self, projects: List[Project]) -> List[str]:
        """공통 도전과제 추출"""
        
        # 실제로는 프로젝트 메타데이터에서 추출해야 함
        # 여기서는 복잡도 기반으로 간단히 추정
        avg_complexity = np.mean([p.complexity_score for p in projects])
        
        challenges = []
        if avg_complexity > 0.7:
            challenges.extend(["High complexity", "Integration challenges"])
        if avg_complexity > 0.5:
            challenges.extend(["Scalability requirements", "Performance optimization"])
        
        challenges.append("Team coordination")
        return challenges[:3]
import pytest
from unittest.mock import Mock, patch
import numpy as np
from backend.src.agents.implementations.nl_template_learner import (
    ProjectTemplateLearner, 
    Project, 
    ProjectTemplate
)

class TestProjectTemplateLearner:
    """프로젝트 템플릿 학습기 테스트"""

    @pytest.fixture
    def template_learner(self):
        return ProjectTemplateLearner()

    @pytest.fixture
    def sample_projects(self):
        return [
            Project(
                original_description="Create a React web application with user authentication",
                requirements=["user authentication", "responsive design", "database integration"],
                tech_stack=["react", "node", "mysql"],
                complexity_score=0.6,
                success=True,
                timeline_days=45
            ),
            Project(
                original_description="Build a React dashboard with real-time data",
                requirements=["real-time updates", "data visualization", "user authentication"],
                tech_stack=["react", "node", "websocket"],
                complexity_score=0.7,
                success=True,
                timeline_days=60
            ),
            Project(
                original_description="Mobile app for iOS and Android",
                requirements=["cross-platform", "offline support", "push notifications"],
                tech_stack=["react-native", "firebase"],
                complexity_score=0.8,
                success=False,
                timeline_days=90
            )
        ]

    @pytest.mark.asyncio
    async def test_learn_from_successful_projects(self, template_learner, sample_projects):
        """성공 프로젝트에서 학습 테스트"""
        with patch.object(template_learner.vectorizer, 'fit_transform') as mock_vectorizer:
            with patch.object(template_learner.clustering_model, 'fit_predict') as mock_clustering:
                # Mock 설정
                mock_vectorizer.return_value = np.array([[1, 0], [1, 0], [0, 1]])
                mock_clustering.return_value = np.array([0, 0, 1])  # 첫 2개는 클러스터 0, 마지막은 클러스터 1
                
                templates = await template_learner.learn_from_successful_projects(sample_projects)
                
                # 클러스터 0에서 템플릿이 생성되었는지 확인 (2개 프로젝트)
                assert len(templates) >= 1
                
                # 템플릿 내용 확인
                template = list(templates.values())[0]
                assert isinstance(template, ProjectTemplate)
                assert template.cluster_id == 0

    def test_find_common_elements(self, template_learner):
        """공통 요소 찾기 테스트"""
        element_lists = [
            ["react", "node", "mysql"],
            ["react", "node", "redis"],
            ["vue", "node", "mysql"]
        ]
        
        common = template_learner._find_common_elements(element_lists)
        
        # node가 모든 리스트에 있으므로 포함되어야 함
        assert "node" in common
        # react는 2/3에만 있으므로 포함되지 않을 수 있음 (50% 임계값)

    def test_generate_template_name(self, template_learner):
        """템플릿 이름 생성 테스트"""
        requirements = ["user authentication", "data visualization"]
        tech_stack = ["react", "node"]
        
        name = template_learner._generate_template_name(requirements, tech_stack)
        
        assert isinstance(name, str)
        assert name.endswith("_template")
        assert len(name.split("_")) >= 2

    def test_group_tech_stack(self, template_learner):
        """기술 스택 그룹화 테스트"""
        tech_stack = ["react", "node.js", "mysql", "aws"]
        
        grouped = template_learner._group_tech_stack(tech_stack)
        
        assert "frontend" in grouped
        assert "react" in grouped["frontend"]
        assert "backend" in grouped
        assert "database" in grouped
        assert "cloud" in grouped

    def test_calculate_success_rate(self, template_learner, sample_projects):
        """성공률 계산 테스트"""
        success_rate = template_learner._calculate_success_rate(sample_projects)
        
        # 3개 중 2개 성공
        assert success_rate == 2/3

    def test_calculate_typical_timeline(self, template_learner, sample_projects):
        """일반적인 타임라인 계산 테스트"""
        timeline = template_learner._calculate_typical_timeline(sample_projects)
        
        # 평균이 65일 정도이므로 "1-3 months" 범위
        assert timeline == "1-3 months"

    @pytest.mark.asyncio
    async def test_suggest_template_no_templates(self, template_learner):
        """템플릿이 없을 때 제안 테스트"""
        template = await template_learner.suggest_template("Create a web app")
        
        assert template is None

    @pytest.mark.asyncio
    async def test_suggest_template_with_templates(self, template_learner):
        """템플릿이 있을 때 제안 테스트"""
        # Mock 템플릿 추가
        mock_template = ProjectTemplate(
            name="web_app_template",
            description_pattern="web application",
            common_requirements=["authentication"],
            recommended_tech_stack={"frontend": ["react"]},
            typical_complexity=0.6,
            success_rate=0.8,
            typical_timeline="1-3 months",
            common_challenges=["integration"],
            cluster_id=0
        )
        template_learner.templates["web_app"] = mock_template
        
        with patch.object(template_learner.vectorizer, 'transform') as mock_transform:
            with patch.object(template_learner.clustering_model, 'predict') as mock_predict:
                mock_transform.return_value = np.array([[1, 0]])
                mock_predict.return_value = np.array([0])
                
                suggested = await template_learner.suggest_template("Create a React web app")
                
                assert suggested is not None
                assert suggested.name == "web_app_template"
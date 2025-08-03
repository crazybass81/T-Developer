# backend/tests/agents/ui_selection/test_ui_selection_agent.py
import pytest
import asyncio
from unittest.mock import Mock, patch

@pytest.mark.integration
class TestUISelectionAgent:
    """UI Selection Agent 통합 테스트"""

    @pytest.fixture
    async def ui_agent(self):
        """UI Selection Agent 인스턴스"""
        from ui_selection_agent import UISelectionAgent
        
        agent = UISelectionAgent()
        yield agent

    @pytest.fixture
    def test_requirements(self):
        """다양한 테스트 요구사항"""
        return [
            {
                "name": "E-commerce Website",
                "requirements": {
                    "seo_critical": True,
                    "expected_users": 50000,
                    "target_platforms": ["web", "mobile"],
                    "team_expertise": {"react": "intermediate", "vue": "beginner"},
                    "timeline": "medium",
                    "performance_critical": True
                },
                "expected_framework": "nextjs"
            },
            {
                "name": "Admin Dashboard",
                "requirements": {
                    "seo_critical": False,
                    "expected_users": 1000,
                    "target_platforms": ["web"],
                    "team_expertise": {"react": "expert", "angular": "intermediate"},
                    "timeline": "short",
                    "real_time_features": True
                },
                "expected_framework": "react"
            }
        ]

    @pytest.mark.asyncio
    async def test_framework_selection(self, ui_agent, test_requirements):
        """프레임워크 선택 테스트"""
        
        for test_case in test_requirements:
            result = await ui_agent.select_ui_framework(
                test_case["requirements"]
            )
            
            # 기본 검증
            assert result.framework is not None
            assert result.confidence_score > 0.0
            assert len(result.reasons) > 0
            assert len(result.pros) > 0
            assert len(result.cons) > 0

    @pytest.mark.asyncio
    async def test_boilerplate_generation(self, ui_agent):
        """보일러플레이트 생성 테스트"""
        
        boilerplate = await ui_agent.boilerplate_generator.generate_boilerplate(
            framework="react",
            template_type="typescript",
            project_name="test-project"
        )
        
        # 기본 구조 검증
        assert boilerplate.framework == "react"
        assert boilerplate.template_name == "typescript"
        assert "package.json" in boilerplate.files
        assert "src/App.tsx" in boilerplate.files
        assert "tsconfig.json" in boilerplate.files

    @pytest.mark.performance
    async def test_selection_performance(self, ui_agent):
        """선택 성능 테스트"""
        
        requirements = {
            "seo_critical": True,
            "expected_users": 25000,
            "team_expertise": {"react": "intermediate"},
            "timeline": "medium"
        }
        
        import time
        start_time = time.time()
        
        result = await ui_agent.select_ui_framework(requirements)
        
        elapsed_time = time.time() - start_time
        
        # 성능 기준: 2초 이내
        assert elapsed_time < 2.0
        assert result is not None
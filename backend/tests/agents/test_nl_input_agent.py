import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
from backend.src.agents.implementations.nl_input_agent import NLInputAgent, ProjectRequirements

class TestNLInputAgent:
    """NL Input Agent 종합 테스트"""

    @pytest.fixture
    def nl_agent(self):
        with patch('backend.src.agents.implementations.nl_input_agent.Agent'):
            return NLInputAgent()

    @pytest.fixture
    def test_descriptions(self):
        return {
            "simple_web": "간단한 할일 관리 웹 애플리케이션을 만들어주세요",
            "complex_mobile": """
            iOS와 Android를 지원하는 소셜 미디어 앱을 개발해주세요.
            사용자는 사진과 동영상을 업로드하고, 친구들과 공유할 수 있어야 합니다.
            실시간 채팅 기능과 푸시 알림이 필요하고, 100만 명 이상의 사용자를 지원해야 합니다.
            """,
            "api_service": "RESTful API 서비스로 인증, 데이터 CRUD, 파일 업로드 기능 포함",
            "ambiguous": "좋은 앱 만들어주세요"
        }

    @pytest.mark.asyncio
    async def test_simple_project_extraction(self, nl_agent, test_descriptions):
        """간단한 프로젝트 설명 처리 테스트"""
        with patch.object(nl_agent.agent, 'arun', new_callable=AsyncMock) as mock_arun:
            mock_arun.return_value = '{"project_type": "web_application", "technical_requirements": ["todo management"]}'
            
            result = await nl_agent.process_description(test_descriptions["simple_web"])

            assert result.project_type == "web_application"
            assert len(result.technical_requirements) > 0

    @pytest.mark.asyncio
    async def test_complex_requirements_extraction(self, nl_agent, test_descriptions):
        """복잡한 요구사항 추출 테스트"""
        with patch.object(nl_agent.agent, 'arun', new_callable=AsyncMock) as mock_arun:
            mock_arun.return_value = '''
            {
                "project_type": "mobile_application",
                "technology_preferences": {"platforms": ["iOS", "Android"]},
                "technical_requirements": ["real-time chat", "photo upload"],
                "non_functional_requirements": ["1000000 users support"]
            }
            '''
            
            result = await nl_agent.process_description(test_descriptions["complex_mobile"])

            assert result.project_type == "mobile_application"
            assert "iOS" in str(result.technology_preferences.get("platforms", []))

    @pytest.mark.asyncio
    async def test_ambiguous_input_handling(self, nl_agent, test_descriptions):
        """모호한 입력 처리 테스트"""
        with patch.object(nl_agent, '_generate_clarification_questions', new_callable=AsyncMock) as mock_questions:
            mock_questions.return_value = [
                "어떤 종류의 앱을 원하시나요?",
                "선호하는 기술 스택이 있나요?"
            ]
            
            with patch.object(nl_agent.agent, 'arun', new_callable=AsyncMock) as mock_arun:
                mock_arun.return_value = '{"project_type": "general", "technical_requirements": []}'
                
                result = await nl_agent.process_description(test_descriptions["ambiguous"])
                
                # 모호한 입력에 대해 질문이 생성되는지 확인
                mock_questions.assert_called_once()

    @pytest.mark.benchmark
    async def test_performance_benchmark(self, nl_agent, test_descriptions):
        """성능 벤치마크 테스트"""
        import time
        
        with patch.object(nl_agent.agent, 'arun', new_callable=AsyncMock) as mock_arun:
            mock_arun.return_value = '{"project_type": "web_application", "technical_requirements": ["test"]}'
            
            start_time = time.time()
            
            tasks = [
                nl_agent.process_description(desc)
                for desc in test_descriptions.values()
            ]
            results = await asyncio.gather(*tasks)
            
            elapsed = time.time() - start_time
            
            assert len(results) == len(test_descriptions)
            assert elapsed < 2.0  # 2초 이하 목표

    def test_project_type_classifier(self):
        """프로젝트 유형 분류기 테스트"""
        from backend.src.agents.implementations.nl_input_agent import ProjectTypeClassifier
        
        classifier = ProjectTypeClassifier()
        
        assert classifier.classify("웹 애플리케이션") == "web_application"
        assert classifier.classify("mobile app for iOS") == "mobile_application"
        assert classifier.classify("REST API service") == "api_service"

    def test_tech_stack_analyzer(self):
        """기술 스택 분석기 테스트"""
        from backend.src.agents.implementations.nl_input_agent import TechStackAnalyzer
        
        analyzer = TechStackAnalyzer()
        result = analyzer.analyze("React frontend with Node.js backend and MySQL database")
        
        assert "react" in result.get("frontend", [])
        assert "node" in result.get("backend", [])
        assert "mysql" in result.get("database", [])

    def test_requirement_extractor(self):
        """요구사항 추출기 테스트"""
        from backend.src.agents.implementations.nl_input_agent import RequirementExtractor
        
        extractor = RequirementExtractor()
        text = "사용자는 로그인할 수 있어야 하고, 1000명의 사용자를 지원해야 합니다."
        result = extractor.extract(text)
        
        assert len(result["functional"]) > 0
        assert len(result["non_functional"]) > 0
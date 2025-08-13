"""
AI Capability Analyzer 테스트
"""

import os
import sys
import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock 모드 설정
os.environ["MOCK_MODE"] = "true"
os.environ["ENVIRONMENT"] = "test"

from src.core.registry.ai_capability_analyzer import (
    AICapabilityAnalyzer,
    CapabilityCategory,
    PerformanceProfile,
    CompatibilityInfo,
)


class TestAICapabilityAnalyzer:
    """AI Capability Analyzer 테스트"""

    @pytest.fixture
    def analyzer(self):
        """테스트용 Analyzer 인스턴스"""
        return AICapabilityAnalyzer()

    @pytest.fixture
    def sample_agent_code(self):
        """샘플 에이전트 코드"""
        return """
        class DataProcessingAgent:
            def __init__(self):
                self.model = self.load_model()
                self.cache = {}

            async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
                # 데이터 검증
                if not self.validate_input(data):
                    raise ValueError("Invalid input data")

                # 캐시 확인
                cache_key = self.get_cache_key(data)
                if cache_key in self.cache:
                    return self.cache[cache_key]

                # 데이터 처리
                cleaned = self.clean_data(data)
                analyzed = await self.analyze(cleaned)
                result = self.transform_output(analyzed)

                # 캐시 저장
                self.cache[cache_key] = result

                return result

            def validate_input(self, data: Dict) -> bool:
                return 'input' in data and data['input']

            async def analyze(self, data: Dict) -> Dict:
                # AI 모델로 분석
                return await self.model.predict(data)
        """

    @pytest.mark.asyncio
    async def test_analyze_agent_capabilities(self, analyzer, sample_agent_code):
        """에이전트 능력 분석 테스트"""
        result = await analyzer.analyze_agent_capabilities(sample_agent_code)

        # 결과 구조 확인
        assert "capabilities" in result
        assert "performance_profile" in result
        assert "compatibility_matrix" in result
        assert "suggested_improvements" in result
        assert "confidence_score" in result
        assert "analysis_metadata" in result

        # 능력 목록 확인
        assert isinstance(result["capabilities"], list)
        assert len(result["capabilities"]) > 0

        # 성능 프로파일 확인
        assert isinstance(result["performance_profile"], PerformanceProfile)
        assert result["performance_profile"].expected_latency_ms > 0
        assert result["performance_profile"].memory_footprint_mb > 0

        # 호환성 정보 확인
        assert isinstance(result["compatibility_matrix"], CompatibilityInfo)
        assert isinstance(result["compatibility_matrix"].supported_languages, list)

        # 신뢰도 점수 확인
        assert 0 <= result["confidence_score"] <= 1

    @pytest.mark.asyncio
    async def test_caching(self, analyzer, sample_agent_code):
        """캐싱 기능 테스트"""
        # 첫 번째 분석
        result1 = await analyzer.analyze_agent_capabilities(sample_agent_code)

        # 두 번째 분석 (캐시에서 반환되어야 함)
        result2 = await analyzer.analyze_agent_capabilities(sample_agent_code)

        # 동일한 결과 확인
        assert result1 == result2

        # 캐시 확인
        code_hash = analyzer._get_code_hash(sample_agent_code)
        assert code_hash in analyzer._cache

    @pytest.mark.asyncio
    async def test_batch_analyze(self, analyzer):
        """배치 분석 테스트"""
        codes = ["class Agent1: pass", "class Agent2: pass", "class Agent3: pass"]

        results = await analyzer.batch_analyze(codes)

        assert len(results) == 3
        for result in results:
            assert "capabilities" in result
            assert "confidence_score" in result

    def test_get_analysis_summary(self, analyzer):
        """분석 요약 테스트"""
        # 초기 상태
        summary = analyzer.get_analysis_summary()
        assert summary["total_analyses"] == 0

        # 분석 이력 추가
        analyzer._analysis_history.append(
            {"capabilities": ["NLP", "Code Generation"], "confidence_score": 0.85}
        )
        analyzer._analysis_history.append(
            {"capabilities": ["NLP", "Data Analysis"], "confidence_score": 0.90}
        )

        summary = analyzer.get_analysis_summary()
        assert summary["total_analyses"] == 2
        assert summary["average_confidence"] == 0.875
        assert "NLP" in summary["common_capabilities"]

    @pytest.mark.asyncio
    async def test_error_handling(self, analyzer):
        """에러 처리 테스트"""
        # 빈 코드는 Mock 모드에서 정상 처리될 수 있음
        result = await analyzer.analyze_agent_capabilities("")
        assert "confidence_score" in result
        assert "analysis_metadata" in result

    def test_performance_profile_generation(self, analyzer):
        """성능 프로파일 생성 테스트"""
        validation_data = {
            "performance": {
                "latency": 250,
                "memory": 256,
                "cpu_intensity": "high",
                "io_intensity": "medium",
                "scalability": "both",
                "concurrent": True,
            }
        }

        profile = analyzer._generate_performance_profile(validation_data)

        assert profile.expected_latency_ms == 250
        assert profile.memory_footprint_mb == 256
        assert profile.cpu_intensity == "high"
        assert profile.io_intensity == "medium"
        assert profile.scalability == "both"
        assert profile.concurrency_support == True

    def test_compatibility_matrix_generation(self, analyzer):
        """호환성 매트릭스 생성 테스트"""
        validation_data = {
            "compatible_agents": ["Agent1", "Agent2"],
            "required_services": ["Redis", "PostgreSQL"],
            "languages": ["python", "javascript"],
            "frameworks": ["django", "fastapi"],
        }

        matrix = analyzer._generate_compatibility_matrix(validation_data)

        assert "Agent1" in matrix.compatible_agents
        assert "Redis" in matrix.required_services
        assert "python" in matrix.supported_languages
        assert "django" in matrix.framework_requirements

    def test_confidence_calculation(self, analyzer):
        """신뢰도 계산 테스트"""
        structure = {}
        validation = {
            "confidence_ratings": {
                "capability1": 0.9,
                "capability2": 0.8,
                "capability3": 0.85,
            }
        }

        confidence = analyzer._calculate_confidence(structure, validation)
        assert confidence == pytest.approx(0.85, 0.01)

    @pytest.mark.asyncio
    async def test_mock_mode_behavior(self, analyzer, sample_agent_code):
        """Mock 모드 동작 테스트"""
        # Mock 모드 확인
        assert os.getenv("MOCK_MODE") == "true"

        # Mock 모드에서도 정상 동작
        result = await analyzer.analyze_agent_capabilities(sample_agent_code)

        assert result is not None
        assert "capabilities" in result
        assert len(result["capabilities"]) > 0


class TestAWSIntegration:
    """AWS 통합 테스트"""

    @pytest.mark.asyncio
    async def test_aws_config_loading(self):
        """AWS 설정 로딩 테스트"""
        with patch(
            "src.core.registry.ai_capability_analyzer.get_config_manager"
        ) as mock_get_config:
            # Mock 설정
            mock_manager = Mock()
            mock_manager.environment = "test"
            mock_manager.initialize_environment = Mock()
            mock_get_config.return_value = mock_manager

            # Analyzer 생성
            analyzer = AICapabilityAnalyzer()

            # 초기화 시 AWS 설정 로드 확인
            mock_manager.initialize_environment.assert_called()

    @pytest.mark.asyncio
    async def test_fallback_to_local_env(self):
        """AWS 실패 시 로컬 환경변수 폴백 테스트"""
        # AWS 연결 실패 시뮬레이션
        with patch(
            "src.core.config.aws_config_manager.AWSConfigManager"
        ) as mock_config:
            mock_config.side_effect = Exception("AWS connection failed")

            # 로컬 환경변수 설정
            os.environ["OPENAI_API_KEY"] = "test-key"
            os.environ["ANTHROPIC_API_KEY"] = "test-key"

            # Analyzer 생성 (에러 없이 생성되어야 함)
            analyzer = AICapabilityAnalyzer()
            assert analyzer is not None


if __name__ == "__main__":
    # 테스트 실행
    pytest.main([__file__, "-v", "--tb=short"])

"""
AI Capability Analyzer for Agent Registration
Analyzes agent code using multiple AI models to assess capabilities and quality
"""

import ast
import asyncio
import hashlib
import json
import logging
import re
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# AI Model imports
try:
    from openai import AsyncOpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from anthropic import AsyncAnthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
import hashlib
from dataclasses import dataclass
from enum import Enum

# AI 모델 인터페이스
from ..ai_models import Claude3Opus, GPT4Turbo

# AWS 설정 관리자
from ..config import get_config_manager


class CapabilityCategory(Enum):
    """에이전트 능력 카테고리"""

    DATA_PROCESSING = "data_processing"
    USER_INTERFACE = "user_interface"
    INTEGRATION = "integration"
    ANALYSIS = "analysis"
    GENERATION = "generation"
    OPTIMIZATION = "optimization"
    SECURITY = "security"
    TESTING = "testing"


@dataclass
class PerformanceProfile:
    """성능 프로파일"""

    expected_latency_ms: float
    memory_footprint_mb: float
    cpu_intensity: str  # low, medium, high
    io_intensity: str  # low, medium, high
    scalability: str  # vertical, horizontal, both
    concurrency_support: bool


@dataclass
class CompatibilityInfo:
    """호환성 정보"""

    compatible_agents: List[str]
    required_services: List[str]
    supported_languages: List[str]
    framework_requirements: List[str]
    minimum_resources: Dict[str, Any]


class AICapabilityAnalyzer:
    """AI가 에이전트 코드를 분석하여 능력을 자동 추론"""

    def __init__(self):
        """초기화"""
        # AWS 설정 매니저 초기화
        self.config_manager = get_config_manager()

        # AWS에서 환경변수 로드
        self._load_aws_config()

        # AI 모델 초기화
        self.claude = Claude3Opus()
        self.gpt4 = GPT4Turbo()

        # 캐시 초기화
        self._cache = {}
        self._analysis_history = []

    def _load_aws_config(self):
        """AWS에서 설정 로드"""
        try:
            # AWS에서 환경변수 초기화
            self.config_manager.initialize_environment()

            # API 키 확인
            required_keys = {
                "OPENAI_API_KEY": "GPT-4 모델 사용",
                "ANTHROPIC_API_KEY": "Claude-3-Opus 모델 사용",
            }

            missing = []
            for key, desc in required_keys.items():
                if not os.getenv(key):
                    missing.append(f"- {key}: {desc}")

            if missing:
                print("⚠️ AWS에서 API 키를 찾을 수 없습니다!")
                print("다음 키가 AWS Secrets Manager에 필요합니다:")
                print("\n".join(missing))
                print("\n설정 방법:")
                print(
                    f"1. AWS Secrets Manager에서 't-developer/{self.config_manager.environment}/openai-api-key' 생성"
                )
                print(
                    f"2. AWS Secrets Manager에서 't-developer/{self.config_manager.environment}/anthropic-api-key' 생성"
                )
                print("\nMOCK_MODE로 실행중...")
                os.environ["MOCK_MODE"] = "true"
            else:
                print("✅ AWS에서 모든 API 키 로드 완료")

        except Exception as e:
            print(f"AWS 설정 로드 실패: {e}")
            print("로컬 환경변수 확인중...")
            self._check_local_env_vars()

    def _check_local_env_vars(self):
        """로컬 환경변수 체크 (폴백)"""
        required_vars = {
            "OPENAI_API_KEY": "GPT-4 모델 사용",
            "ANTHROPIC_API_KEY": "Claude-3-Opus 모델 사용",
        }

        missing = []
        for var, desc in required_vars.items():
            if not os.getenv(var):
                missing.append(f"- {var}: {desc}")

        if missing and not os.getenv("MOCK_MODE"):
            print("⚠️ 환경변수 필요!")
            print("다음 환경변수가 설정되지 않았습니다:")
            print("\n".join(missing))
            print("\nMOCK_MODE로 실행중...")
            os.environ["MOCK_MODE"] = "true"

    async def analyze_agent_capabilities(self, agent_code: str) -> Dict:
        """에이전트 코드를 AI가 분석하여 능력 자동 도출"""

        # 캐시 확인
        code_hash = self._get_code_hash(agent_code)
        if code_hash in self._cache:
            return self._cache[code_hash]

        try:
            # 1. Claude로 전체 구조 이해
            structure_analysis = await self._analyze_structure(agent_code)

            # 2. GPT-4로 교차 검증 및 보완
            validation = await self._validate_and_enhance(structure_analysis)

            # 3. 자동으로 메타데이터 생성
            result = {
                "capabilities": validation.get("capabilities", []),
                "performance_profile": self._generate_performance_profile(validation),
                "compatibility_matrix": self._generate_compatibility_matrix(validation),
                "suggested_improvements": validation.get("improvements", []),
                "confidence_score": self._calculate_confidence(structure_analysis, validation),
                "analysis_metadata": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "models_used": ["claude-3-opus", "gpt-4-turbo"],
                    "code_hash": code_hash,
                },
            }

            # 캐시 저장
            self._cache[code_hash] = result
            self._analysis_history.append(result)

            return result

        except Exception as e:
            print(f"Error during analysis: {e}")
            return self._get_fallback_analysis(agent_code)

    async def _analyze_structure(self, agent_code: str) -> Dict:
        """Claude로 코드 구조 분석"""

        if os.getenv("MOCK_MODE"):
            # Mock 모드: 실제 API 호출 없이 예제 반환
            return self._get_mock_structure_analysis(agent_code)

        prompt = f"""
        Analyze this agent code and identify:
        1. Primary capabilities (what the agent can do)
        2. Input/output patterns (data flow)
        3. Dependencies and requirements
        4. Performance characteristics
        5. Potential use cases
        6. Code quality metrics
        7. Security considerations

        Code: {agent_code[:5000]}  # Limit for API

        Return as structured JSON with these exact keys:
        {{
            "capabilities": [...],
            "io_patterns": {{...}},
            "dependencies": [...],
            "performance": {{...}},
            "use_cases": [...],
            "quality_metrics": {{...}},
            "security": {{...}}
        }}
        """

        response = await self.claude.analyze(prompt=prompt, temperature=0.2, max_tokens=2000)

        return json.loads(response)

    async def _validate_and_enhance(self, structure_analysis: Dict) -> Dict:
        """GPT-4로 분석 결과 검증 및 보완"""

        if os.getenv("MOCK_MODE"):
            # Mock 모드: 실제 API 호출 없이 예제 반환
            return self._get_mock_validation(structure_analysis)

        prompt = f"""
        Validate and enhance this capability analysis:
        {json.dumps(structure_analysis, indent=2)}

        Tasks:
        1. Verify the identified capabilities are accurate
        2. Add any missing capabilities or patterns
        3. Correct any misidentifications
        4. Suggest specific improvements
        5. Rate confidence in each capability (0-1)

        Return enhanced analysis as JSON with:
        {{
            "capabilities": [...],
            "improvements": [...],
            "confidence_ratings": {{...}},
            "additional_insights": [...],
            "warnings": [...]
        }}
        """

        response = await self.gpt4.complete(prompt=prompt, temperature=0.3, max_tokens=2000)

        return json.loads(response)

    def _generate_performance_profile(self, validation: Dict) -> PerformanceProfile:
        """성능 프로파일 생성"""

        perf_data = validation.get("performance", {})

        return PerformanceProfile(
            expected_latency_ms=perf_data.get("latency", 100),
            memory_footprint_mb=perf_data.get("memory", 50),
            cpu_intensity=perf_data.get("cpu_intensity", "medium"),
            io_intensity=perf_data.get("io_intensity", "low"),
            scalability=perf_data.get("scalability", "horizontal"),
            concurrency_support=perf_data.get("concurrent", True),
        )

    def _generate_compatibility_matrix(self, validation: Dict) -> CompatibilityInfo:
        """호환성 매트릭스 생성"""

        return CompatibilityInfo(
            compatible_agents=validation.get("compatible_agents", []),
            required_services=validation.get("required_services", []),
            supported_languages=validation.get("languages", ["python"]),
            framework_requirements=validation.get("frameworks", ["agno"]),
            minimum_resources={"cpu": "1 core", "memory": "512MB", "storage": "1GB"},
        )

    def _calculate_confidence(self, structure: Dict, validation: Dict) -> float:
        """전체 신뢰도 계산"""

        confidence_ratings = validation.get("confidence_ratings", {})
        if not confidence_ratings:
            return 0.75  # 기본값

        scores = [v for v in confidence_ratings.values() if isinstance(v, (int, float))]
        return sum(scores) / len(scores) if scores else 0.75

    def _get_code_hash(self, code: str) -> str:
        """코드 해시 생성"""
        return hashlib.sha256(code.encode()).hexdigest()[:16]

    def _get_mock_structure_analysis(self, agent_code: str) -> Dict:
        """Mock 구조 분석 결과"""
        return {
            "capabilities": [
                "Natural language processing",
                "Code generation",
                "Pattern recognition",
                "Data transformation",
            ],
            "io_patterns": {
                "input": ["text", "json", "structured_data"],
                "output": ["code", "analysis", "recommendations"],
            },
            "dependencies": ["openai", "anthropic", "numpy", "pandas"],
            "performance": {"latency": 200, "memory": 128, "cpu_intensity": "medium"},
            "use_cases": [
                "Code review automation",
                "Requirements analysis",
                "Test generation",
            ],
            "quality_metrics": {
                "complexity": "medium",
                "maintainability": 0.85,
                "testability": 0.90,
            },
            "security": {"vulnerabilities": [], "best_practices": True},
        }

    def _get_mock_validation(self, structure: Dict) -> Dict:
        """Mock 검증 결과"""
        return {
            "capabilities": structure.get("capabilities", [])
            + ["Error handling", "Async operations"],
            "improvements": [
                "Add retry logic for API calls",
                "Implement caching for repeated analyses",
                "Add more comprehensive error handling",
            ],
            "confidence_ratings": {
                "Natural language processing": 0.95,
                "Code generation": 0.90,
                "Pattern recognition": 0.85,
                "Data transformation": 0.88,
            },
            "additional_insights": [
                "Agent shows strong NLP capabilities",
                "Could benefit from performance optimization",
                "Security practices are well-implemented",
            ],
            "warnings": [],
        }

    def _get_fallback_analysis(self, agent_code: str) -> Dict:
        """에러 시 폴백 분석"""
        return {
            "capabilities": ["Basic processing"],
            "performance_profile": self._generate_performance_profile({}),
            "compatibility_matrix": self._generate_compatibility_matrix({}),
            "suggested_improvements": ["Manual review required"],
            "confidence_score": 0.0,
            "analysis_metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "models_used": ["fallback"],
                "error": True,
            },
        }

    async def batch_analyze(self, agent_codes: List[str]) -> List[Dict]:
        """여러 에이전트를 배치로 분석"""
        tasks = [self.analyze_agent_capabilities(code) for code in agent_codes]
        return await asyncio.gather(*tasks)

    def get_analysis_summary(self) -> Dict:
        """분석 이력 요약"""
        if not self._analysis_history:
            return {"total_analyses": 0}

        return {
            "total_analyses": len(self._analysis_history),
            "average_confidence": sum(a["confidence_score"] for a in self._analysis_history)
            / len(self._analysis_history),
            "common_capabilities": self._get_common_capabilities(),
            "improvement_trends": self._get_improvement_trends(),
        }

    def _get_common_capabilities(self) -> List[str]:
        """공통 능력 추출"""
        if not self._analysis_history:
            return []

        capability_count = {}
        for analysis in self._analysis_history:
            for cap in analysis.get("capabilities", []):
                capability_count[cap] = capability_count.get(cap, 0) + 1

        # 상위 5개 반환
        sorted_caps = sorted(capability_count.items(), key=lambda x: x[1], reverse=True)
        return [cap for cap, _ in sorted_caps[:5]]

    def _get_improvement_trends(self) -> List[str]:
        """개선 트렌드 분석"""
        if not self._analysis_history:
            return []

        improvement_count = {}
        for analysis in self._analysis_history:
            for imp in analysis.get("suggested_improvements", []):
                improvement_count[imp] = improvement_count.get(imp, 0) + 1

        # 상위 3개 반환
        sorted_imps = sorted(improvement_count.items(), key=lambda x: x[1], reverse=True)
        return [imp for imp, _ in sorted_imps[:3]]


# 사용 예시
if __name__ == "__main__":

    async def main():
        analyzer = AICapabilityAnalyzer()

        # 예제 에이전트 코드
        sample_code = """
        class DataProcessingAgent:
            def __init__(self):
                self.model = load_model()

            async def process(self, data):
                # 데이터 전처리
                cleaned = self.clean_data(data)
                # 분석
                result = await self.analyze(cleaned)
                return result
        """

        # 분석 실행
        result = await analyzer.analyze_agent_capabilities(sample_code)
        print(json.dumps(result, indent=2))

    asyncio.run(main())

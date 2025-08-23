"""Integration test for RequirementAnalyzer to CodeGenerator flow.

요구사항 분석부터 코드 생성까지의 전체 플로우를 테스트합니다.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, patch

from backend.packages.agents.requirement_analyzer import RequirementAnalyzer
from backend.packages.agents.code_generator import CodeGenerator, GenerationConfig
from backend.packages.memory.hub import MemoryHub
from backend.packages.memory.contexts import ContextType


class TestRequirementToCodeIntegration:
    """요구사항에서 코드 생성까지 통합 테스트."""
    
    @pytest.fixture
    async def memory_hub(self):
        """공유 메모리 허브."""
        hub = MemoryHub()
        await hub.initialize()
        yield hub
        await hub.shutdown()
    
    @pytest.fixture
    def requirement_analyzer(self, memory_hub):
        """RequirementAnalyzer 인스턴스."""
        return RequirementAnalyzer(memory_hub=memory_hub)
    
    @pytest.fixture
    def code_generator(self, memory_hub):
        """CodeGenerator 인스턴스."""
        config = GenerationConfig(
            include_tests=True,
            include_docs=True
        )
        return CodeGenerator(memory_hub=memory_hub, config=config)
    
    @pytest.mark.asyncio
    async def test_full_flow(self, requirement_analyzer, code_generator, memory_hub):
        """전체 플로우 테스트: 요구사항 → 분석 → 코드 생성."""
        
        # 1. 자연어 요구사항
        requirements = """
        Build a simple calculator service with the following features:
        1. Add two numbers
        2. Subtract two numbers
        3. Multiply two numbers
        4. Divide two numbers with error handling for division by zero
        """
        
        # 2. 실제 AI를 사용한 요구사항 분석
        analysis_result = await requirement_analyzer.execute({
            "requirements": requirements,
            "context": "service"
        })
        
        assert analysis_result["success"], f"요구사항 분석 실패: {analysis_result.get('error')}"
        assert "specification" in analysis_result
        
        # 3. 메모리에서 분석 결과 확인
        stored_spec = await memory_hub.get(
            context_type=ContextType.S_CTX,
            key="requirements:latest"
        )
        assert stored_spec is not None
        
        # 4. 실제 AI를 사용한 코드 생성
        generation_result = await code_generator.execute({
            "read_from_memory": True,
            "memory_key": "requirements:latest"
        })
        
        assert generation_result["success"], f"코드 생성 실패: {generation_result.get('error')}"
        assert len(generation_result["generated_codes"]) > 0
        
        # 5. 생성된 코드 검증
        for code_info in generation_result["generated_codes"]:
            assert code_info["success"]
            assert len(code_info["code"]) > 0
            assert code_info["test_code"] is not None  # 테스트 포함
            assert code_info["documentation"] is not None  # 문서화 포함
            
            # 메모리에 저장되었는지 확인
            stored_code = await memory_hub.get(
                context_type=ContextType.A_CTX,
                key=f"generated:{code_info['component_name']}"
            )
            assert stored_code is not None
    
    @pytest.mark.asyncio
    async def test_error_handling_in_flow(self, requirement_analyzer, code_generator):
        """플로우 중 에러 처리 테스트."""
        
        # 잘못된 요구사항 (빈 문자열)
        invalid_requirements = ""
        
        # 요구사항 분석이 실패해야 함
        result = await requirement_analyzer.execute({
            "requirements": invalid_requirements
        })
        
        assert not result["success"]
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_partial_generation(self, code_generator, memory_hub):
        """일부 컴포넌트만 생성하는 경우."""
        
        # 하나의 컴포넌트만 있는 요구사항
        partial_requirements = {
            "components": [
                {
                    "name": "SimpleService",
                    "type": "service",
                    "responsibility": "Simple functionality"
                }
            ],
            "functional_requirements": ["Basic CRUD"],
            "dependencies": []
        }
        
        await memory_hub.put(
            context_type=ContextType.S_CTX,
            key="requirements:partial",
            value=partial_requirements
        )
        
        # 실제 AI로 코드 생성
        result = await code_generator.execute({
            "read_from_memory": True,
            "memory_key": "requirements:partial"
        })
        
        assert result["success"]
        assert len(result["generated_codes"]) == 1
        assert result["generated_codes"][0]["component_name"] == "SimpleService"
"""CodeGenerator 테스트.

TDD 방식으로 CodeGenerator의 모든 기능을 테스트합니다.
"""

import asyncio
import pytest
import json
from unittest.mock import AsyncMock, Mock, patch

from backend.packages.agents.code_generator import (
    CodeGenerator,
    GeneratedCode,
    CodeTemplate,
    GenerationConfig
)
from backend.packages.memory.hub import MemoryHub
from backend.packages.memory.contexts import ContextType


class TestCodeGenerator:
    """CodeGenerator 테스트."""
    
    @pytest.fixture
    async def memory_hub(self):
        """메모리 허브 픽스처."""
        hub = MemoryHub()
        await hub.initialize()
        yield hub
        await hub.shutdown()
    
    @pytest.fixture
    def generator(self, memory_hub):
        """테스트용 CodeGenerator."""
        return CodeGenerator(memory_hub=memory_hub)
    
    @pytest.fixture
    def sample_requirements(self):
        """샘플 요구사항 명세."""
        return {
            "functional_requirements": [
                "User authentication with JWT",
                "CRUD operations for tasks",
                "Task assignment to users"
            ],
            "non_functional_requirements": [
                "Response time < 100ms",
                "99.9% availability"
            ],
            "components": [
                {
                    "name": "AuthService",
                    "type": "service",
                    "responsibility": "Handle user authentication and JWT generation"
                },
                {
                    "name": "TaskService",
                    "type": "service",
                    "responsibility": "Manage task CRUD operations"
                },
                {
                    "name": "TaskController",
                    "type": "controller",
                    "responsibility": "REST API endpoints for tasks"
                }
            ],
            "dependencies": ["fastapi", "sqlalchemy", "pyjwt"],
            "complexity": "medium"
        }
    
    @pytest.mark.asyncio
    async def test_generate_single_component(self, generator, sample_requirements):
        """단일 컴포넌트 코드 생성."""
        component = sample_requirements["components"][0]  # AuthService
        
        # AI 호출을 모킹
        mock_code = """class AuthService:
    \"\"\"Authentication service.\"\"\"
    
    def __init__(self):
        self.name = "AuthService"
    
    async def authenticate(self, username: str, password: str) -> bool:
        # TODO: Implement authentication
        return True
"""
        
        async def mock_generate_ai(*args, **kwargs):
            return mock_code
        
        with patch.object(generator, '_generate_with_ai', side_effect=mock_generate_ai):
            result = await generator.generate_component(
                component=component,
                requirements=sample_requirements
            )
        
        assert isinstance(result, GeneratedCode)
        assert result.success
        assert result.component_name == "AuthService"
        assert result.file_path.endswith(".py")
        assert len(result.code) > 0
        assert "class AuthService" in result.code
        assert result.language == "python"
    
    @pytest.mark.asyncio
    async def test_generate_multiple_components(self, generator, sample_requirements):
        """여러 컴포넌트 동시 생성."""
        task = {
            "requirements": sample_requirements,
            "target_language": "python",
            "framework": "fastapi"
        }
        
        async def mock_generate_ai(component, *args, **kwargs):
            return f"class {component['name']}: pass"
        
        with patch.object(generator, '_generate_with_ai', side_effect=mock_generate_ai):
            result = await generator.execute(task)
        
        assert result["success"]
        assert "generated_codes" in result
        assert len(result["generated_codes"]) == len(sample_requirements["components"])
        
        # 각 컴포넌트가 생성되었는지 확인
        generated_names = [code["component_name"] for code in result["generated_codes"]]
        assert "AuthService" in generated_names
        assert "TaskService" in generated_names
        assert "TaskController" in generated_names
    
    @pytest.mark.asyncio
    async def test_apply_safety_mechanisms(self, generator):
        """Safety mechanisms 적용 확인."""
        # Circuit Breaker와 Resource Limiter가 적용되는지 확인
        assert generator.circuit_breaker is not None
        assert generator.resource_limiter is not None
        
        # Circuit Breaker 동작 테스트
        # 직접 circuit breaker의 실패를 트리거
        from backend.packages.safety import CircuitBreakerOpenError
        
        async def failing_func():
            raise ValueError("Test failure")
        
        # 3번 실패시켜 Circuit을 열기
        for _ in range(3):
            try:
                await generator.circuit_breaker.call(failing_func)
            except ValueError:
                pass
        
        # Circuit이 열렸는지 확인
        from backend.packages.safety import CircuitState
        assert generator.circuit_breaker.get_state() == CircuitState.OPEN
        
        # Circuit이 열린 상태에서 호출 시 CircuitBreakerOpenError 발생
        with pytest.raises(CircuitBreakerOpenError):
            await generator.circuit_breaker.call(failing_func)
    
    @pytest.mark.asyncio
    async def test_code_template_application(self, generator):
        """코드 템플릿 적용."""
        template = CodeTemplate(
            name="service_template",
            language="python",
            template_code='''
class {component_name}:
    """Generated service: {responsibility}"""
    
    def __init__(self):
        self.name = "{component_name}"
    
    async def execute(self, data):
        # TODO: Implement business logic
        pass
'''
        )
        
        generator.add_template(template)
        
        component = {
            "name": "UserService",
            "type": "service",
            "responsibility": "Manage user data"
        }
        
        result = await generator.generate_component(
            component=component,
            requirements={},
            use_template=True
        )
        
        assert result.success
        assert "class UserService" in result.code
        assert "Generated service: Manage user data" in result.code
    
    @pytest.mark.asyncio
    async def test_generation_config(self, generator):
        """생성 설정 적용."""
        config = GenerationConfig(
            max_tokens=1000,
            temperature=0.3,
            include_tests=True,
            include_docs=True,
            follow_conventions=True
        )
        
        generator.update_config(config)
        
        component = {
            "name": "TestComponent",
            "type": "service",
            "responsibility": "Test component"
        }
        
        async def mock_generate_ai(*args, **kwargs):
            return "class TestComponent: pass"
        
        async def mock_generate_tests(*args, **kwargs):
            return "def test_component(): assert True"
        
        with patch.object(generator, '_generate_with_ai', side_effect=mock_generate_ai):
            with patch.object(generator, '_generate_tests', side_effect=mock_generate_tests):
                result = await generator.generate_component(
                    component=component,
                    requirements={}
                )
        
        assert result.success
        # 설정이 적용되었는지 확인
        assert result.metadata.get("config") == config.__dict__
    
    @pytest.mark.asyncio
    async def test_error_handling(self, generator):
        """에러 처리."""
        # 잘못된 컴포넌트 정보
        invalid_component = {
            "name": "",  # 빈 이름
            "type": "unknown"
        }
        
        async def mock_generate_ai(*args, **kwargs):
            return "class Component: pass"
        
        with patch.object(generator, '_generate_with_ai', side_effect=mock_generate_ai):
            result = await generator.generate_component(
                component=invalid_component,
                requirements={}
            )
        
        assert not result.success
        assert result.error is not None
        assert "validation" in result.error.lower() or "invalid" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_memory_integration(self, generator, memory_hub, sample_requirements):
        """메모리 허브 통합."""
        # 요구사항을 메모리에 저장
        await memory_hub.put(
            context_type=ContextType.S_CTX,
            key="requirements:latest",
            value=sample_requirements
        )
        
        # 메모리에서 요구사항을 읽어 생성
        task = {
            "read_from_memory": True,
            "memory_key": "requirements:latest"
        }
        
        async def mock_generate_ai(comp, *args, **kwargs):
            return f"class {comp['name']}: pass"
        
        with patch.object(generator, '_generate_with_ai', side_effect=mock_generate_ai):
            result = await generator.execute(task)
        
        assert result["success"]
        assert len(result["generated_codes"]) > 0
        
        # 생성된 코드가 메모리에 저장되었는지 확인
        stored_code = await memory_hub.get(
            context_type=ContextType.A_CTX,
            key="generated:AuthService"
        )
        assert stored_code is not None
    
    @pytest.mark.asyncio
    async def test_language_support(self, generator):
        """다양한 언어 지원."""
        languages = ["python", "javascript", "typescript", "java"]
        
        component = {
            "name": "TestService",
            "type": "service",
            "responsibility": "Test service"
        }
        
        async def mock_generate_ai(comp, req, lang):
            if lang == "python":
                return "class TestService: pass"
            elif lang == "javascript":
                return "class TestService {}"
            elif lang == "typescript":
                return "class TestService {}"
            else:
                return "public class TestService {}"
        
        with patch.object(generator, '_generate_with_ai', side_effect=mock_generate_ai):
            for lang in languages:
                result = await generator.generate_component(
                    component=component,
                    requirements={},
                    target_language=lang
                )
                
                assert result.success
                assert result.language == lang
    
    @pytest.mark.asyncio
    async def test_dependency_injection(self, generator, sample_requirements):
        """의존성 주입 코드 생성."""
        component = {
            "name": "TaskService",
            "type": "service",
            "responsibility": "Manage tasks",
            "dependencies": ["DatabaseConnection", "CacheService"]
        }
        
        async def mock_generate_ai(*args, **kwargs):
            return """class TaskService:
    def __init__(self, database_connection: DatabaseConnection, cache_service: CacheService):
        self.db = database_connection
        self.cache = cache_service
"""
        
        with patch.object(generator, '_generate_with_ai', side_effect=mock_generate_ai):
            result = await generator.generate_component(
                component=component,
                requirements=sample_requirements
            )
        
        assert result.success
        # 의존성 주입 코드가 포함되었는지 확인
        assert "def __init__" in result.code
        assert any(dep.lower() in result.code.lower() 
                  for dep in component["dependencies"])
    
    @pytest.mark.asyncio
    async def test_test_generation(self, generator):
        """테스트 코드 생성."""
        component = {
            "name": "AuthService",
            "type": "service",
            "responsibility": "Authentication"
        }
        
        config = GenerationConfig(include_tests=True)
        generator.update_config(config)
        
        async def mock_generate_ai(*args, **kwargs):
            return "class AuthService: pass"
        
        async def mock_generate_tests(*args, **kwargs):
            return "def test_auth_service(): assert True"
        
        with patch.object(generator, '_generate_with_ai', side_effect=mock_generate_ai):
            with patch.object(generator, '_generate_tests', side_effect=mock_generate_tests):
                result = await generator.generate_component(
                    component=component,
                    requirements={}
                )
        
        assert result.success
        assert result.test_code is not None
        assert "test" in result.test_code.lower()
        assert "assert" in result.test_code or "expect" in result.test_code
    
    @pytest.mark.asyncio
    async def test_documentation_generation(self, generator):
        """문서화 생성."""
        component = {
            "name": "UserController",
            "type": "controller",
            "responsibility": "Handle user API requests"
        }
        
        config = GenerationConfig(include_docs=True)
        generator.update_config(config)
        
        async def mock_generate_ai(*args, **kwargs):
            return '''class UserController:
    """Controller for user API."""
    pass'''
        
        with patch.object(generator, '_generate_with_ai', side_effect=mock_generate_ai):
            result = await generator.generate_component(
                component=component,
                requirements={}
            )
        
        assert result.success
        # 문서화가 포함되었는지 확인
        assert '"""' in result.code or "'''" in result.code  # Docstring
        assert result.documentation is not None
        assert len(result.documentation) > 0
    
    @pytest.mark.asyncio
    async def test_parallel_generation(self, generator, sample_requirements):
        """병렬 코드 생성."""
        async def mock_generate_ai(comp, *args, **kwargs):
            await asyncio.sleep(0.01)  # 비동기 시뮬레이션
            return f"class {comp['name']}: pass"
        
        with patch.object(generator, '_generate_with_ai', side_effect=mock_generate_ai):
            # 여러 컴포넌트를 동시에 생성
            tasks = [
                generator.generate_component(comp, sample_requirements)
                for comp in sample_requirements["components"]
            ]
            
            results = await asyncio.gather(*tasks)
        
        assert len(results) == len(sample_requirements["components"])
        assert all(r.success for r in results)
        assert len(set(r.component_name for r in results)) == len(results)  # 모두 다른 컴포넌트
    
    @pytest.mark.asyncio
    async def test_incremental_generation(self, generator, memory_hub):
        """점진적 코드 생성."""
        # 첫 번째 생성
        component1 = {
            "name": "BaseService",
            "type": "service",
            "responsibility": "Base service functionality"
        }
        
        async def mock_generate_ai_1(*args, **kwargs):
            return "class BaseService: pass"
        
        with patch.object(generator, '_generate_with_ai', side_effect=mock_generate_ai_1):
            result1 = await generator.generate_component(component1, {})
        assert result1.success
        
        # 메모리에 저장
        await memory_hub.put(
            context_type=ContextType.S_CTX,
            key="existing:BaseService",
            value=result1.code
        )
        
        # 두 번째 생성 (기존 코드 참조)
        component2 = {
            "name": "ExtendedService",
            "type": "service",
            "responsibility": "Extended functionality",
            "extends": "BaseService"
        }
        
        async def mock_generate_ai_2(*args, **kwargs):
            return "from .base import BaseService\n\nclass ExtendedService(BaseService): pass"
        
        with patch.object(generator, '_generate_with_ai', side_effect=mock_generate_ai_2):
            result2 = await generator.generate_component(component2, {})
        assert result2.success
        assert "BaseService" in result2.code or "import" in result2.code
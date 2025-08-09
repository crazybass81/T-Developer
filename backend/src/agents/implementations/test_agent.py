"""
Test Agent
테스트 코드 생성 및 실행 에이전트
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import logging

from src.agents.base import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


@dataclass
class TestCase:
    """테스트 케이스"""
    name: str
    type: str  # unit, integration, e2e
    description: str
    code: str
    assertions: List[str]
    mocks: Optional[Dict[str, Any]] = None
    fixtures: Optional[Dict[str, Any]] = None


@dataclass
class TestSuite:
    """테스트 스위트"""
    name: str
    test_cases: List[TestCase] = field(default_factory=list)
    setup_code: Optional[str] = None
    teardown_code: Optional[str] = None
    coverage_target: float = 80.0


@dataclass
class TestGenerationResult:
    """테스트 생성 결과"""
    test_suites: List[TestSuite] = field(default_factory=list)
    total_tests: int = 0
    unit_tests: int = 0
    integration_tests: int = 0
    e2e_tests: int = 0
    estimated_coverage: float = 0.0
    test_files: Dict[str, str] = field(default_factory=dict)
    test_commands: Dict[str, str] = field(default_factory=dict)


class TestAgent(BaseAgent):
    """
    테스트 코드 생성 에이전트
    
    주요 기능:
    - 단위 테스트 생성
    - 통합 테스트 생성
    - E2E 테스트 생성
    - 테스트 커버리지 분석
    - 모킹 및 픽스처 생성
    """
    
    def __init__(self, environment: str = "production"):
        super().__init__(environment)
        self.name = "TestAgent"
        
        # 테스트 프레임워크 설정
        self.test_frameworks = {
            'javascript': 'jest',
            'typescript': 'jest',
            'python': 'pytest',
            'java': 'junit',
            'go': 'testing'
        }
        
        # 테스트 패턴
        self.test_patterns = self._init_test_patterns()
    
    def _init_test_patterns(self) -> Dict[str, Any]:
        """테스트 패턴 초기화"""
        return {
            'unit': {
                'focus': 'individual functions/methods',
                'isolation': 'high',
                'mocking': 'extensive',
                'speed': 'fast'
            },
            'integration': {
                'focus': 'component interactions',
                'isolation': 'medium',
                'mocking': 'selective',
                'speed': 'medium'
            },
            'e2e': {
                'focus': 'user workflows',
                'isolation': 'low',
                'mocking': 'minimal',
                'speed': 'slow'
            }
        }
    
    async def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        테스트 코드 생성
        
        Args:
            input_data: 생성된 코드 및 프로젝트 정보
            
        Returns:
            테스트 생성 결과
        """
        try:
            logger.info("Starting test generation...")
            
            code_files = input_data.get('code_files', {})
            project_type = input_data.get('project_type', 'web_app')
            framework = input_data.get('framework', 'react')
            language = input_data.get('language', 'javascript')
            
            result = TestGenerationResult()
            
            # 1. 코드 분석 및 테스트 대상 식별
            test_targets = await self._analyze_code_for_testing(code_files)
            
            # 2. 단위 테스트 생성
            unit_tests = await self._generate_unit_tests(test_targets, language)
            if unit_tests:
                result.test_suites.append(unit_tests)
                result.unit_tests = len(unit_tests.test_cases)
            
            # 3. 통합 테스트 생성
            integration_tests = await self._generate_integration_tests(test_targets, language)
            if integration_tests:
                result.test_suites.append(integration_tests)
                result.integration_tests = len(integration_tests.test_cases)
            
            # 4. E2E 테스트 생성
            e2e_tests = await self._generate_e2e_tests(project_type, framework)
            if e2e_tests:
                result.test_suites.append(e2e_tests)
                result.e2e_tests = len(e2e_tests.test_cases)
            
            # 5. 테스트 파일 생성
            result.test_files = await self._create_test_files(result.test_suites, language)
            
            # 6. 테스트 실행 명령어 생성
            result.test_commands = self._generate_test_commands(language, framework)
            
            # 통계 계산
            result.total_tests = result.unit_tests + result.integration_tests + result.e2e_tests
            result.estimated_coverage = await self._estimate_coverage(test_targets, result.test_suites)
            
            logger.info(f"Test generation completed. Total tests: {result.total_tests}")
            
            return AgentResult(
                success=True,
                data={
                    'test_result': result,
                    'total_tests': result.total_tests,
                    'estimated_coverage': result.estimated_coverage,
                    'test_files': result.test_files,
                    'test_commands': result.test_commands,
                    'summary': {
                        'unit_tests': result.unit_tests,
                        'integration_tests': result.integration_tests,
                        'e2e_tests': result.e2e_tests
                    }
                },
                metadata={
                    'agent': self.name,
                    'test_framework': self.test_frameworks.get(language),
                    'files_analyzed': len(code_files)
                }
            )
            
        except Exception as e:
            logger.error(f"Test generation failed: {e}")
            return AgentResult(
                success=False,
                error=str(e),
                data={}
            )
    
    async def _analyze_code_for_testing(self, code_files: Dict[str, str]) -> Dict[str, Any]:
        """테스트 대상 코드 분석"""
        test_targets = {
            'functions': [],
            'classes': [],
            'components': [],
            'api_endpoints': [],
            'pages': []
        }
        
        for file_path, content in code_files.items():
            # 함수 찾기
            if 'function' in content or 'def ' in content:
                functions = self._extract_functions(content)
                test_targets['functions'].extend([
                    {'file': file_path, 'name': f, 'content': content}
                    for f in functions
                ])
            
            # 클래스 찾기
            if 'class ' in content:
                classes = self._extract_classes(content)
                test_targets['classes'].extend([
                    {'file': file_path, 'name': c, 'content': content}
                    for c in classes
                ])
            
            # React 컴포넌트 찾기
            if '.jsx' in file_path or '.tsx' in file_path:
                components = self._extract_react_components(content)
                test_targets['components'].extend([
                    {'file': file_path, 'name': c, 'content': content}
                    for c in components
                ])
            
            # API 엔드포인트 찾기
            if 'route' in content.lower() or 'api' in file_path.lower():
                endpoints = self._extract_api_endpoints(content)
                test_targets['api_endpoints'].extend([
                    {'file': file_path, 'endpoint': e, 'content': content}
                    for e in endpoints
                ])
        
        return test_targets
    
    async def _generate_unit_tests(self, test_targets: Dict[str, Any], language: str) -> TestSuite:
        """단위 테스트 생성"""
        suite = TestSuite(
            name="Unit Tests",
            coverage_target=80.0
        )
        
        # 함수 테스트
        for func in test_targets.get('functions', [])[:10]:  # 상위 10개만
            test_case = await self._create_function_test(func, language)
            suite.test_cases.append(test_case)
        
        # 클래스 메서드 테스트
        for cls in test_targets.get('classes', [])[:5]:  # 상위 5개만
            test_case = await self._create_class_test(cls, language)
            suite.test_cases.append(test_case)
        
        # Setup/Teardown 코드
        suite.setup_code = self._generate_setup_code(language)
        suite.teardown_code = self._generate_teardown_code(language)
        
        return suite
    
    async def _generate_integration_tests(self, test_targets: Dict[str, Any], language: str) -> TestSuite:
        """통합 테스트 생성"""
        suite = TestSuite(
            name="Integration Tests",
            coverage_target=60.0
        )
        
        # API 엔드포인트 테스트
        for endpoint in test_targets.get('api_endpoints', [])[:5]:
            test_case = await self._create_api_test(endpoint, language)
            suite.test_cases.append(test_case)
        
        # 컴포넌트 상호작용 테스트
        components = test_targets.get('components', [])
        if len(components) >= 2:
            test_case = await self._create_component_interaction_test(
                components[:2], language
            )
            suite.test_cases.append(test_case)
        
        return suite
    
    async def _generate_e2e_tests(self, project_type: str, framework: str) -> TestSuite:
        """E2E 테스트 생성"""
        suite = TestSuite(
            name="E2E Tests",
            coverage_target=40.0
        )
        
        # 주요 사용자 플로우 테스트
        if project_type == 'e_commerce':
            test_cases = [
                self._create_e2e_test_case(
                    "User Registration and Login",
                    self._generate_auth_flow_test(framework)
                ),
                self._create_e2e_test_case(
                    "Product Search and Purchase",
                    self._generate_purchase_flow_test(framework)
                ),
                self._create_e2e_test_case(
                    "Cart Management",
                    self._generate_cart_flow_test(framework)
                )
            ]
        elif project_type == 'saas':
            test_cases = [
                self._create_e2e_test_case(
                    "User Onboarding",
                    self._generate_onboarding_flow_test(framework)
                ),
                self._create_e2e_test_case(
                    "Subscription Management",
                    self._generate_subscription_flow_test(framework)
                )
            ]
        else:
            test_cases = [
                self._create_e2e_test_case(
                    "Basic User Flow",
                    self._generate_basic_flow_test(framework)
                )
            ]
        
        suite.test_cases.extend(test_cases)
        return suite
    
    async def _create_function_test(self, func: Dict[str, Any], language: str) -> TestCase:
        """함수 단위 테스트 생성"""
        func_name = func['name']
        
        if language == 'javascript' or language == 'typescript':
            code = f"""
describe('{func_name}', () => {{
    it('should return expected result', () => {{
        const result = {func_name}(testInput);
        expect(result).toBe(expectedOutput);
    }});
    
    it('should handle edge cases', () => {{
        expect(() => {func_name}(null)).toThrow();
        expect({func_name}([])).toEqual([]);
    }});
    
    it('should validate input types', () => {{
        expect(() => {func_name}('invalid')).toThrow(TypeError);
    }});
}});
"""
        elif language == 'python':
            code = f"""
def test_{func_name}_normal():
    result = {func_name}(test_input)
    assert result == expected_output

def test_{func_name}_edge_cases():
    with pytest.raises(ValueError):
        {func_name}(None)
    assert {func_name}([]) == []

def test_{func_name}_type_validation():
    with pytest.raises(TypeError):
        {func_name}('invalid')
"""
        else:
            code = "// Test implementation needed"
        
        return TestCase(
            name=f"test_{func_name}",
            type="unit",
            description=f"Unit test for {func_name}",
            code=code,
            assertions=["returns correct value", "handles edge cases", "validates input"]
        )
    
    async def _create_class_test(self, cls: Dict[str, Any], language: str) -> TestCase:
        """클래스 테스트 생성"""
        class_name = cls['name']
        
        if language == 'javascript' or language == 'typescript':
            code = f"""
describe('{class_name}', () => {{
    let instance;
    
    beforeEach(() => {{
        instance = new {class_name}();
    }});
    
    it('should instantiate correctly', () => {{
        expect(instance).toBeInstanceOf({class_name});
    }});
    
    it('should have required methods', () => {{
        expect(instance.method1).toBeDefined();
        expect(instance.method2).toBeDefined();
    }});
    
    it('should maintain state correctly', () => {{
        instance.setState('test');
        expect(instance.getState()).toBe('test');
    }});
}});
"""
        elif language == 'python':
            code = f"""
class Test{class_name}:
    def setup_method(self):
        self.instance = {class_name}()
    
    def test_instantiation(self):
        assert isinstance(self.instance, {class_name})
    
    def test_required_methods(self):
        assert hasattr(self.instance, 'method1')
        assert hasattr(self.instance, 'method2')
    
    def test_state_management(self):
        self.instance.set_state('test')
        assert self.instance.get_state() == 'test'
"""
        else:
            code = "// Test implementation needed"
        
        return TestCase(
            name=f"test_{class_name}",
            type="unit",
            description=f"Unit test for {class_name} class",
            code=code,
            assertions=["instantiation", "method existence", "state management"]
        )
    
    async def _create_api_test(self, endpoint: Dict[str, Any], language: str) -> TestCase:
        """API 테스트 생성"""
        endpoint_path = endpoint['endpoint']
        
        if language == 'javascript' or language == 'typescript':
            code = f"""
describe('API: {endpoint_path}', () => {{
    it('should return 200 for valid request', async () => {{
        const response = await request(app)
            .get('{endpoint_path}')
            .expect(200);
        
        expect(response.body).toHaveProperty('data');
    }});
    
    it('should handle invalid parameters', async () => {{
        await request(app)
            .get('{endpoint_path}?invalid=true')
            .expect(400);
    }});
    
    it('should require authentication', async () => {{
        await request(app)
            .get('{endpoint_path}')
            .expect(401);
    }});
}});
"""
        elif language == 'python':
            code = f"""
def test_api_{endpoint_path.replace('/', '_')}(client):
    response = client.get('{endpoint_path}')
    assert response.status_code == 200
    assert 'data' in response.json()

def test_api_{endpoint_path.replace('/', '_')}_invalid_params(client):
    response = client.get('{endpoint_path}?invalid=true')
    assert response.status_code == 400

def test_api_{endpoint_path.replace('/', '_')}_auth_required(client):
    response = client.get('{endpoint_path}')
    assert response.status_code == 401
"""
        else:
            code = "// Test implementation needed"
        
        return TestCase(
            name=f"test_api_{endpoint_path.replace('/', '_')}",
            type="integration",
            description=f"API test for {endpoint_path}",
            code=code,
            assertions=["status codes", "response format", "authentication"]
        )
    
    async def _create_component_interaction_test(
        self,
        components: List[Dict[str, Any]],
        language: str
    ) -> TestCase:
        """컴포넌트 상호작용 테스트"""
        comp1 = components[0]['name']
        comp2 = components[1]['name']
        
        code = f"""
describe('Component Interaction: {comp1} and {comp2}', () => {{
    it('should communicate correctly', () => {{
        const wrapper1 = mount(<{comp1} />);
        const wrapper2 = mount(<{comp2} onReceive={{mockReceive}} />);
        
        wrapper1.find('button').simulate('click');
        expect(mockReceive).toHaveBeenCalled();
    }});
    
    it('should share state properly', () => {{
        const {{container}} = render(
            <Context.Provider>
                <{comp1} />
                <{comp2} />
            </Context.Provider>
        );
        
        // Test state sharing
        expect(container).toMatchSnapshot();
    }});
}});
"""
        
        return TestCase(
            name=f"test_interaction_{comp1}_{comp2}",
            type="integration",
            description=f"Interaction test between {comp1} and {comp2}",
            code=code,
            assertions=["communication", "state sharing"]
        )
    
    def _create_e2e_test_case(self, name: str, code: str) -> TestCase:
        """E2E 테스트 케이스 생성"""
        return TestCase(
            name=name.lower().replace(' ', '_'),
            type="e2e",
            description=name,
            code=code,
            assertions=["user flow completion", "data persistence", "UI responsiveness"]
        )
    
    def _generate_auth_flow_test(self, framework: str) -> str:
        """인증 플로우 테스트"""
        return """
describe('Authentication Flow', () => {
    it('should allow user registration and login', async () => {
        await page.goto('http://localhost:3000');
        await page.click('[data-testid="register-button"]');
        
        await page.type('[name="email"]', 'test@example.com');
        await page.type('[name="password"]', 'Test123!');
        await page.click('[type="submit"]');
        
        await page.waitForSelector('[data-testid="dashboard"]');
        expect(await page.title()).toContain('Dashboard');
    });
});
"""
    
    def _generate_purchase_flow_test(self, framework: str) -> str:
        """구매 플로우 테스트"""
        return """
describe('Purchase Flow', () => {
    it('should complete purchase workflow', async () => {
        await page.goto('http://localhost:3000/products');
        await page.click('[data-testid="product-1"]');
        await page.click('[data-testid="add-to-cart"]');
        
        await page.goto('http://localhost:3000/cart');
        await page.click('[data-testid="checkout"]');
        
        await page.type('[name="card-number"]', '4111111111111111');
        await page.click('[data-testid="place-order"]');
        
        await page.waitForSelector('[data-testid="order-confirmation"]');
        expect(await page.textContent('h1')).toContain('Order Confirmed');
    });
});
"""
    
    def _generate_cart_flow_test(self, framework: str) -> str:
        """장바구니 플로우 테스트"""
        return """
describe('Cart Management', () => {
    it('should manage cart items', async () => {
        await page.goto('http://localhost:3000/cart');
        
        const initialCount = await page.$$eval('.cart-item', items => items.length);
        
        await page.click('[data-testid="increase-quantity-1"]');
        await page.waitForTimeout(500);
        
        const quantity = await page.textContent('[data-testid="quantity-1"]');
        expect(parseInt(quantity)).toBeGreaterThan(1);
        
        await page.click('[data-testid="remove-item-1"]');
        await page.waitForTimeout(500);
        
        const finalCount = await page.$$eval('.cart-item', items => items.length);
        expect(finalCount).toBe(initialCount - 1);
    });
});
"""
    
    def _generate_onboarding_flow_test(self, framework: str) -> str:
        """온보딩 플로우 테스트"""
        return """
describe('User Onboarding', () => {
    it('should complete onboarding process', async () => {
        await page.goto('http://localhost:3000/onboarding');
        
        // Step 1: Profile
        await page.type('[name="company"]', 'Test Company');
        await page.click('[data-testid="next-step"]');
        
        // Step 2: Preferences
        await page.click('[value="option1"]');
        await page.click('[data-testid="next-step"]');
        
        // Step 3: Complete
        await page.click('[data-testid="complete-onboarding"]');
        
        await page.waitForNavigation();
        expect(page.url()).toContain('/dashboard');
    });
});
"""
    
    def _generate_subscription_flow_test(self, framework: str) -> str:
        """구독 플로우 테스트"""
        return """
describe('Subscription Management', () => {
    it('should manage subscription', async () => {
        await page.goto('http://localhost:3000/billing');
        
        await page.click('[data-testid="upgrade-plan"]');
        await page.click('[data-testid="plan-premium"]');
        
        await page.type('[name="card-number"]', '4111111111111111');
        await page.click('[data-testid="subscribe"]');
        
        await page.waitForSelector('[data-testid="subscription-active"]');
        expect(await page.textContent('.plan-name')).toBe('Premium');
    });
});
"""
    
    def _generate_basic_flow_test(self, framework: str) -> str:
        """기본 플로우 테스트"""
        return """
describe('Basic User Flow', () => {
    it('should navigate through main features', async () => {
        await page.goto('http://localhost:3000');
        
        // Navigate to main page
        await page.click('[data-testid="nav-home"]');
        expect(await page.title()).toContain('Home');
        
        // Test main functionality
        await page.click('[data-testid="main-action"]');
        await page.waitForSelector('[data-testid="result"]');
        
        // Verify result
        const result = await page.textContent('[data-testid="result"]');
        expect(result).toBeTruthy();
    });
});
"""
    
    async def _create_test_files(
        self,
        test_suites: List[TestSuite],
        language: str
    ) -> Dict[str, str]:
        """테스트 파일 생성"""
        test_files = {}
        
        for suite in test_suites:
            if suite.name == "Unit Tests":
                file_name = "unit.test.js" if language in ['javascript', 'typescript'] else "test_unit.py"
            elif suite.name == "Integration Tests":
                file_name = "integration.test.js" if language in ['javascript', 'typescript'] else "test_integration.py"
            else:
                file_name = "e2e.test.js" if language in ['javascript', 'typescript'] else "test_e2e.py"
            
            # 파일 내용 생성
            content = self._generate_test_file_content(suite, language)
            test_files[f"tests/{file_name}"] = content
        
        # 테스트 설정 파일
        if language in ['javascript', 'typescript']:
            test_files['jest.config.js'] = self._generate_jest_config()
        elif language == 'python':
            test_files['pytest.ini'] = self._generate_pytest_config()
        
        return test_files
    
    def _generate_test_file_content(self, suite: TestSuite, language: str) -> str:
        """테스트 파일 내용 생성"""
        if language in ['javascript', 'typescript']:
            content = f"// {suite.name}\n\n"
            if suite.setup_code:
                content += suite.setup_code + "\n\n"
            
            for test_case in suite.test_cases:
                content += test_case.code + "\n\n"
            
            if suite.teardown_code:
                content += suite.teardown_code
        else:
            content = f"# {suite.name}\n\n"
            content += "import pytest\n\n"
            
            if suite.setup_code:
                content += suite.setup_code + "\n\n"
            
            for test_case in suite.test_cases:
                content += test_case.code + "\n\n"
        
        return content
    
    def _generate_test_commands(self, language: str, framework: str) -> Dict[str, str]:
        """테스트 실행 명령어 생성"""
        if language in ['javascript', 'typescript']:
            return {
                'unit': 'npm test -- --testPathPattern=unit',
                'integration': 'npm test -- --testPathPattern=integration',
                'e2e': 'npm run test:e2e',
                'all': 'npm test',
                'coverage': 'npm test -- --coverage',
                'watch': 'npm test -- --watch'
            }
        elif language == 'python':
            return {
                'unit': 'pytest tests/test_unit.py',
                'integration': 'pytest tests/test_integration.py',
                'e2e': 'pytest tests/test_e2e.py',
                'all': 'pytest',
                'coverage': 'pytest --cov=src --cov-report=html',
                'watch': 'pytest-watch'
            }
        else:
            return {'all': 'test command not configured'}
    
    def _generate_setup_code(self, language: str) -> str:
        """Setup 코드 생성"""
        if language in ['javascript', 'typescript']:
            return """
// Test setup
beforeAll(() => {
    // Global setup
});

beforeEach(() => {
    // Reset state before each test
    jest.clearAllMocks();
});
"""
        elif language == 'python':
            return """
@pytest.fixture(scope='session')
def setup():
    # Global setup
    yield
    # Global teardown

@pytest.fixture
def reset_state():
    # Reset state before each test
    yield
    # Cleanup after test
"""
        return ""
    
    def _generate_teardown_code(self, language: str) -> str:
        """Teardown 코드 생성"""
        if language in ['javascript', 'typescript']:
            return """
afterEach(() => {
    // Cleanup after each test
});

afterAll(() => {
    // Global cleanup
});
"""
        elif language == 'python':
            return """
def teardown_module():
    # Module level teardown
    pass
"""
        return ""
    
    def _generate_jest_config(self) -> str:
        """Jest 설정 파일"""
        return """
module.exports = {
    testEnvironment: 'node',
    coverageDirectory: 'coverage',
    collectCoverageFrom: [
        'src/**/*.{js,jsx,ts,tsx}',
        '!src/index.js',
        '!src/**/*.test.{js,jsx,ts,tsx}'
    ],
    testMatch: [
        '**/__tests__/**/*.{js,jsx,ts,tsx}',
        '**/*.test.{js,jsx,ts,tsx}'
    ],
    transform: {
        '^.+\\.(js|jsx|ts|tsx)$': 'babel-jest'
    },
    moduleNameMapper: {
        '\\.(css|less|scss|sass)$': 'identity-obj-proxy'
    },
    setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
    coverageThreshold: {
        global: {
            branches: 70,
            functions: 70,
            lines: 70,
            statements: 70
        }
    }
};
"""
    
    def _generate_pytest_config(self) -> str:
        """Pytest 설정 파일"""
        return """
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow tests
"""
    
    async def _estimate_coverage(
        self,
        test_targets: Dict[str, Any],
        test_suites: List[TestSuite]
    ) -> float:
        """테스트 커버리지 추정"""
        total_targets = sum(len(v) for v in test_targets.values())
        total_tests = sum(len(suite.test_cases) for suite in test_suites)
        
        if total_targets == 0:
            return 0.0
        
        # 간단한 추정: 각 테스트가 대상의 일부를 커버한다고 가정
        coverage_ratio = min(1.0, total_tests / total_targets)
        return coverage_ratio * 100
    
    def _extract_functions(self, content: str) -> List[str]:
        """코드에서 함수 추출"""
        functions = []
        
        # JavaScript/TypeScript functions
        import re
        js_pattern = r'(?:function|const|let|var)\s+(\w+)\s*='
        functions.extend(re.findall(js_pattern, content))
        
        # Python functions
        py_pattern = r'def\s+(\w+)\s*\('
        functions.extend(re.findall(py_pattern, content))
        
        return functions[:10]  # 상위 10개만
    
    def _extract_classes(self, content: str) -> List[str]:
        """코드에서 클래스 추출"""
        import re
        pattern = r'class\s+(\w+)'
        return re.findall(pattern, content)[:5]  # 상위 5개만
    
    def _extract_react_components(self, content: str) -> List[str]:
        """React 컴포넌트 추출"""
        import re
        # Function components
        pattern1 = r'(?:export\s+)?(?:const|function)\s+([A-Z]\w+)\s*='
        # Class components
        pattern2 = r'class\s+([A-Z]\w+)\s+extends\s+(?:React\.)?Component'
        
        components = re.findall(pattern1, content) + re.findall(pattern2, content)
        return components[:5]  # 상위 5개만
    
    def _extract_api_endpoints(self, content: str) -> List[str]:
        """API 엔드포인트 추출"""
        import re
        patterns = [
            r'app\.(?:get|post|put|delete|patch)\([\'"]([^\'"]*)[\'""]',
            r'router\.(?:get|post|put|delete|patch)\([\'"]([^\'"]*)[\'""]',
            r'@app\.route\([\'"]([^\'"]*)[\'""]'
        ]
        
        endpoints = []
        for pattern in patterns:
            endpoints.extend(re.findall(pattern, content))
        
        return endpoints[:5]  # 상위 5개만
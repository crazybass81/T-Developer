"""
Testing Generator Module for Generation Agent
Generates comprehensive test suites for generated projects
"""

import asyncio
import json
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


class TestType(Enum):
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    API = "api"
    COMPONENT = "component"
    PERFORMANCE = "performance"
    SECURITY = "security"
    ACCESSIBILITY = "accessibility"


class TestFramework(Enum):
    JEST = "jest"
    VITEST = "vitest"
    CYPRESS = "cypress"
    PLAYWRIGHT = "playwright"
    PYTEST = "pytest"
    UNITTEST = "unittest"
    JASMINE = "jasmine"
    KARMA = "karma"


@dataclass
class TestFile:
    filename: str
    content: str
    test_type: TestType
    framework: TestFramework
    description: str = ""
    dependencies: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class TestSuite:
    name: str
    test_files: List[TestFile]
    configuration: Dict[str, Any]
    coverage_target: float
    test_commands: Dict[str, str]


@dataclass
class TestingResult:
    success: bool
    test_suites: Dict[str, TestSuite]
    configuration_files: Dict[str, str]
    total_tests: int
    coverage_config: Dict[str, Any]
    processing_time: float
    metadata: Dict[str, Any]
    error: str = ""


class TestingGenerator:
    """Advanced test suite generator"""

    def __init__(self):
        self.version = "1.0.0"

        # Framework test mappings
        self.framework_test_setups = {
            "react": {
                "unit": TestFramework.JEST,
                "component": TestFramework.JEST,
                "e2e": TestFramework.CYPRESS,
                "integration": TestFramework.JEST,
            },
            "vue": {
                "unit": TestFramework.VITEST,
                "component": TestFramework.VITEST,
                "e2e": TestFramework.CYPRESS,
                "integration": TestFramework.VITEST,
            },
            "angular": {
                "unit": TestFramework.JASMINE,
                "component": TestFramework.KARMA,
                "e2e": TestFramework.PLAYWRIGHT,
                "integration": TestFramework.JASMINE,
            },
            "express": {
                "unit": TestFramework.JEST,
                "api": TestFramework.JEST,
                "integration": TestFramework.JEST,
                "e2e": TestFramework.PLAYWRIGHT,
            },
            "fastapi": {
                "unit": TestFramework.PYTEST,
                "api": TestFramework.PYTEST,
                "integration": TestFramework.PYTEST,
                "e2e": TestFramework.PLAYWRIGHT,
            },
            "django": {
                "unit": TestFramework.UNITTEST,
                "api": TestFramework.UNITTEST,
                "integration": TestFramework.UNITTEST,
                "e2e": TestFramework.PLAYWRIGHT,
            },
            "flask": {
                "unit": TestFramework.PYTEST,
                "api": TestFramework.PYTEST,
                "integration": TestFramework.PYTEST,
                "e2e": TestFramework.PLAYWRIGHT,
            },
        }

        # Test templates
        self.test_templates = {
            TestType.UNIT: self._generate_unit_tests,
            TestType.INTEGRATION: self._generate_integration_tests,
            TestType.E2E: self._generate_e2e_tests,
            TestType.API: self._generate_api_tests,
            TestType.COMPONENT: self._generate_component_tests,
            TestType.PERFORMANCE: self._generate_performance_tests,
            TestType.SECURITY: self._generate_security_tests,
            TestType.ACCESSIBILITY: self._generate_accessibility_tests,
        }

        # Configuration templates
        self.config_templates = {
            TestFramework.JEST: self._generate_jest_config,
            TestFramework.VITEST: self._generate_vitest_config,
            TestFramework.CYPRESS: self._generate_cypress_config,
            TestFramework.PLAYWRIGHT: self._generate_playwright_config,
            TestFramework.PYTEST: self._generate_pytest_config,
            TestFramework.UNITTEST: self._generate_unittest_config,
        }

    async def generate_tests(self, context: Dict[str, Any], output_path: str) -> TestingResult:
        """Generate comprehensive test suite"""

        start_time = datetime.now()

        try:
            framework = context.get("target_framework", "react")
            components = context.get("selected_components", [])

            test_suites = {}
            configuration_files = {}
            total_tests = 0

            # Get framework test setup
            test_setup = self.framework_test_setups.get(framework, {})

            # Generate test suites for each test type
            for test_type, test_framework in test_setup.items():
                test_type_enum = TestType(test_type)
                test_framework_enum = TestFramework(test_framework)

                # Generate tests for this type
                test_files = await self._generate_tests_for_type(
                    test_type_enum, test_framework_enum, components, context
                )

                if test_files:
                    # Create test suite
                    suite = TestSuite(
                        name=f"{test_type}_tests",
                        test_files=test_files,
                        configuration=await self._get_test_configuration(
                            test_framework_enum, context
                        ),
                        coverage_target=self._get_coverage_target(test_type_enum),
                        test_commands=self._get_test_commands(test_framework_enum, test_type_enum),
                    )

                    test_suites[test_type] = suite
                    total_tests += len(test_files)

                # Generate configuration files
                config_files = await self.config_templates[test_framework_enum](context)
                configuration_files.update(config_files)

            # Generate coverage configuration
            coverage_config = await self._generate_coverage_config(framework, context)

            # Write test files
            if output_path:
                await self._write_test_files(test_suites, configuration_files, output_path)

            processing_time = (datetime.now() - start_time).total_seconds()

            return TestingResult(
                success=True,
                test_suites=test_suites,
                configuration_files=configuration_files,
                total_tests=total_tests,
                coverage_config=coverage_config,
                processing_time=processing_time,
                metadata={
                    "framework": framework,
                    "test_types": list(test_setup.keys()),
                    "test_frameworks": list(set(test_setup.values())),
                    "components_tested": len(components),
                },
            )

        except Exception as e:
            return TestingResult(
                success=False,
                test_suites={},
                configuration_files={},
                total_tests=0,
                coverage_config={},
                processing_time=(datetime.now() - start_time).total_seconds(),
                metadata={},
                error=str(e),
            )

    async def _generate_tests_for_type(
        self,
        test_type: TestType,
        test_framework: TestFramework,
        components: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> List[TestFile]:
        """Generate tests for specific test type"""

        if test_type in self.test_templates:
            return await self.test_templates[test_type](test_framework, components, context)

        return []

    # Test generators
    async def _generate_unit_tests(
        self,
        framework: TestFramework,
        components: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> List[TestFile]:
        """Generate unit tests"""

        test_files = []
        app_framework = context.get("target_framework", "react")

        for component in components:
            component_name = component.get("name", "Component")
            component_type = component.get("type", "component")

            if framework == TestFramework.JEST:
                if app_framework in ["react", "express"]:
                    test_content = self._generate_jest_unit_test(component, context)
                    test_files.append(
                        TestFile(
                            filename=f"tests/unit/{component_name.lower()}.test.ts",
                            content=test_content,
                            test_type=TestType.UNIT,
                            framework=framework,
                            description=f"Unit tests for {component_name}",
                            dependencies=["jest", "@types/jest"],
                        )
                    )

            elif framework == TestFramework.PYTEST:
                test_content = self._generate_pytest_unit_test(component, context)
                test_files.append(
                    TestFile(
                        filename=f"tests/unit/test_{component_name.lower()}.py",
                        content=test_content,
                        test_type=TestType.UNIT,
                        framework=framework,
                        description=f"Unit tests for {component_name}",
                        dependencies=["pytest", "pytest-asyncio"],
                    )
                )

        return test_files

    async def _generate_integration_tests(
        self,
        framework: TestFramework,
        components: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> List[TestFile]:
        """Generate integration tests"""

        test_files = []
        app_framework = context.get("target_framework", "react")

        # Generate integration test for main workflow
        if framework == TestFramework.JEST:
            if app_framework in ["react", "vue", "express"]:
                test_content = self._generate_jest_integration_test(components, context)
                test_files.append(
                    TestFile(
                        filename="tests/integration/app.integration.test.ts",
                        content=test_content,
                        test_type=TestType.INTEGRATION,
                        framework=framework,
                        description="Integration tests for main application workflow",
                    )
                )

        elif framework == TestFramework.PYTEST:
            test_content = self._generate_pytest_integration_test(components, context)
            test_files.append(
                TestFile(
                    filename="tests/integration/test_app_integration.py",
                    content=test_content,
                    test_type=TestType.INTEGRATION,
                    framework=framework,
                    description="Integration tests for main application workflow",
                )
            )

        return test_files

    async def _generate_e2e_tests(
        self,
        framework: TestFramework,
        components: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> List[TestFile]:
        """Generate end-to-end tests"""

        test_files = []

        if framework == TestFramework.CYPRESS:
            test_content = self._generate_cypress_e2e_test(components, context)
            test_files.append(
                TestFile(
                    filename="cypress/e2e/app.cy.ts",
                    content=test_content,
                    test_type=TestType.E2E,
                    framework=framework,
                    description="End-to-end tests for main user workflows",
                )
            )

        elif framework == TestFramework.PLAYWRIGHT:
            test_content = self._generate_playwright_e2e_test(components, context)
            test_files.append(
                TestFile(
                    filename="tests/e2e/app.spec.ts",
                    content=test_content,
                    test_type=TestType.E2E,
                    framework=framework,
                    description="End-to-end tests using Playwright",
                )
            )

        return test_files

    async def _generate_api_tests(
        self,
        framework: TestFramework,
        components: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> List[TestFile]:
        """Generate API tests"""

        test_files = []
        app_framework = context.get("target_framework", "express")

        # Only generate API tests for backend frameworks
        if app_framework not in ["express", "fastapi", "django", "flask"]:
            return test_files

        api_components = [
            c for c in components if c.get("category") == "api" or "api" in c.get("type", "")
        ]

        if framework == TestFramework.JEST:
            test_content = self._generate_jest_api_test(api_components, context)
            test_files.append(
                TestFile(
                    filename="tests/api/api.test.ts",
                    content=test_content,
                    test_type=TestType.API,
                    framework=framework,
                    description="API endpoint tests",
                )
            )

        elif framework == TestFramework.PYTEST:
            test_content = self._generate_pytest_api_test(api_components, context)
            test_files.append(
                TestFile(
                    filename="tests/api/test_api.py",
                    content=test_content,
                    test_type=TestType.API,
                    framework=framework,
                    description="API endpoint tests",
                )
            )

        return test_files

    async def _generate_component_tests(
        self,
        framework: TestFramework,
        components: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> List[TestFile]:
        """Generate component tests"""

        test_files = []
        app_framework = context.get("target_framework", "react")

        # Only generate component tests for frontend frameworks
        if app_framework not in ["react", "vue", "angular"]:
            return test_files

        ui_components = [c for c in components if c.get("category") in ["ui", "component", "form"]]

        for component in ui_components:
            component_name = component.get("name", "Component")

            if framework == TestFramework.JEST and app_framework == "react":
                test_content = self._generate_react_component_test(component, context)
                test_files.append(
                    TestFile(
                        filename=f"src/components/{component_name}/{component_name}.test.tsx",
                        content=test_content,
                        test_type=TestType.COMPONENT,
                        framework=framework,
                        description=f"Component tests for {component_name}",
                        dependencies=[
                            "@testing-library/react",
                            "@testing-library/jest-dom",
                        ],
                    )
                )

        return test_files

    async def _generate_performance_tests(
        self,
        framework: TestFramework,
        components: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> List[TestFile]:
        """Generate performance tests"""

        test_files = []

        # Generate basic performance test
        if framework == TestFramework.PLAYWRIGHT:
            test_content = self._generate_performance_test_playwright(context)
            test_files.append(
                TestFile(
                    filename="tests/performance/load.spec.ts",
                    content=test_content,
                    test_type=TestType.PERFORMANCE,
                    framework=framework,
                    description="Performance and load tests",
                )
            )

        return test_files

    async def _generate_security_tests(
        self,
        framework: TestFramework,
        components: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> List[TestFile]:
        """Generate security tests"""

        test_files = []

        # Generate basic security tests
        if framework == TestFramework.JEST:
            test_content = self._generate_security_test_jest(context)
            test_files.append(
                TestFile(
                    filename="tests/security/security.test.ts",
                    content=test_content,
                    test_type=TestType.SECURITY,
                    framework=framework,
                    description="Security vulnerability tests",
                )
            )

        return test_files

    async def _generate_accessibility_tests(
        self,
        framework: TestFramework,
        components: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> List[TestFile]:
        """Generate accessibility tests"""

        test_files = []
        app_framework = context.get("target_framework", "react")

        # Only for frontend frameworks
        if app_framework in ["react", "vue", "angular"]:
            if framework == TestFramework.JEST:
                test_content = self._generate_accessibility_test_jest(context)
                test_files.append(
                    TestFile(
                        filename="tests/accessibility/a11y.test.ts",
                        content=test_content,
                        test_type=TestType.ACCESSIBILITY,
                        framework=framework,
                        description="Accessibility tests",
                        dependencies=["@axe-core/playwright", "jest-axe"],
                    )
                )

        return test_files

    # Test content generators
    def _generate_jest_unit_test(self, component: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate Jest unit test content"""

        component_name = component.get("name", "Component")
        framework = context.get("target_framework", "react")

        if framework == "react":
            return f"""import React from 'react';
import {{ render, screen }} from '@testing-library/react';
import '@testing-library/jest-dom';
import {component_name} from './{component_name}';

describe('{component_name}', () => {{
  it('renders without crashing', () => {{
    render(<{component_name} />);
    expect(screen.getByRole('main')).toBeInTheDocument();
  }});

  it('displays correct content', () => {{
    render(<{component_name} />);
    expect(screen.getByText(/{component_name}/i)).toBeInTheDocument();
  }});

  it('handles user interactions', () => {{
    render(<{component_name} />);
    // Add interaction tests here
  }});

  it('handles edge cases', () => {{
    // Add edge case tests here
  }});
}});"""

        else:  # Express/Node.js
            return f"""import {{ {component_name}Service }} from '../src/services/{component_name}Service';

describe('{component_name}Service', () => {{
  beforeEach(() => {{
    jest.clearAllMocks();
  }});

  describe('getAll', () => {{
    it('should return all {component_name.lower()}s', async () => {{
      const result = await {component_name}Service.getAll();
      expect(result).toBeDefined();
      expect(Array.isArray(result)).toBe(true);
    }});
  }});

  describe('getById', () => {{
    it('should return {component_name.lower()} by id', async () => {{
      const id = 1;
      const result = await {component_name}Service.getById(id);
      expect(result).toBeDefined();
      expect(result.id).toBe(id);
    }});

    it('should handle non-existent id', async () => {{
      const id = 999;
      await expect({component_name}Service.getById(id)).rejects.toThrow();
    }});
  }});

  describe('create', () => {{
    it('should create new {component_name.lower()}', async () => {{
      const data = {{ name: 'Test {component_name}' }};
      const result = await {component_name}Service.create(data);
      expect(result).toBeDefined();
      expect(result.name).toBe(data.name);
    }});
  }});
}});"""

    def _generate_pytest_unit_test(self, component: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate pytest unit test content"""

        component_name = component.get("name", "Component")

        return f"""import pytest
from unittest.mock import Mock, patch
from src.services.{component_name.lower()}_service import {component_name}Service


class Test{component_name}Service:

    @pytest.fixture
    def service(self):
        return {component_name}Service()

    @pytest.mark.asyncio
    async def test_get_all(self, service):
        \"\"\"Test getting all {component_name.lower()}s\"\"\"
        result = await service.get_all()
        assert result is not None
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_get_by_id(self, service):
        \"\"\"Test getting {component_name.lower()} by ID\"\"\"
        test_id = 1
        result = await service.get_by_id(test_id)
        assert result is not None
        assert result.id == test_id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, service):
        \"\"\"Test handling non-existent ID\"\"\"
        with pytest.raises(ValueError):
            await service.get_by_id(999)

    @pytest.mark.asyncio
    async def test_create(self, service):
        \"\"\"Test creating new {component_name.lower()}\"\"\"
        data = {{"name": "Test {component_name}"}}
        result = await service.create(data)
        assert result is not None
        assert result.name == data["name"]

    @pytest.mark.asyncio
    async def test_update(self, service):
        \"\"\"Test updating {component_name.lower()}\"\"\"
        test_id = 1
        data = {{"name": "Updated {component_name}"}}
        result = await service.update(test_id, data)
        assert result is not None
        assert result.name == data["name"]

    @pytest.mark.asyncio
    async def test_delete(self, service):
        \"\"\"Test deleting {component_name.lower()}\"\"\"
        test_id = 1
        result = await service.delete(test_id)
        assert result is True"""

    def _generate_jest_integration_test(
        self, components: List[Dict[str, Any]], context: Dict[str, Any]
    ) -> str:
        """Generate Jest integration test content"""

        framework = context.get("target_framework", "react")

        if framework == "react":
            return """import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import App from '../src/App';

// Mock API calls
jest.mock('../src/services/api', () => ({
  fetchData: jest.fn(),
  postData: jest.fn(),
}));

describe('App Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const renderApp = () => {
    return render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
  };

  it('should render main application flow', async () => {
    renderApp();

    // Check if main components are rendered
    expect(screen.getByRole('navigation')).toBeInTheDocument();
    expect(screen.getByRole('main')).toBeInTheDocument();
  });

  it('should handle navigation between pages', async () => {
    renderApp();

    // Test navigation
    const navLink = screen.getByRole('link', { name: /home/i });
    fireEvent.click(navLink);

    await waitFor(() => {
      expect(screen.getByText(/welcome/i)).toBeInTheDocument();
    });
  });

  it('should handle form submission workflow', async () => {
    renderApp();

    // Navigate to form page
    const formLink = screen.getByRole('link', { name: /form/i });
    fireEvent.click(formLink);

    // Fill and submit form
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'test data' } });

    const submitButton = screen.getByRole('button', { name: /submit/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/success/i)).toBeInTheDocument();
    });
  });
});"""

        else:  # Express
            return """import request from 'supertest';
import app from '../src/app';

describe('API Integration Tests', () => {
  it('should handle complete API workflow', async () => {
    // Create item
    const createResponse = await request(app)
      .post('/api/items')
      .send({ name: 'Test Item' })
      .expect(201);

    const createdId = createResponse.body.data.id;

    // Get item
    await request(app)
      .get(`/api/items/${createdId}`)
      .expect(200)
      .expect(res => {
        expect(res.body.data.name).toBe('Test Item');
      });

    // Update item
    await request(app)
      .put(`/api/items/${createdId}`)
      .send({ name: 'Updated Item' })
      .expect(200);

    // Delete item
    await request(app)
      .delete(`/api/items/${createdId}`)
      .expect(200);

    // Verify deletion
    await request(app)
      .get(`/api/items/${createdId}`)
      .expect(404);
  });

  it('should handle authentication flow', async () => {
    // Register user
    const registerResponse = await request(app)
      .post('/api/auth/register')
      .send({
        email: 'test@example.com',
        password: 'password123'
      })
      .expect(201);

    // Login user
    const loginResponse = await request(app)
      .post('/api/auth/login')
      .send({
        email: 'test@example.com',
        password: 'password123'
      })
      .expect(200);

    const token = loginResponse.body.data.token;

    // Access protected route
    await request(app)
      .get('/api/protected')
      .set('Authorization', `Bearer ${token}`)
      .expect(200);
  });
});"""

    # Additional test content generators would be implemented here
    def _generate_cypress_e2e_test(
        self, components: List[Dict[str, Any]], context: Dict[str, Any]
    ) -> str:
        """Generate Cypress E2E test content"""

        return """describe('Application E2E Tests', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('should complete main user workflow', () => {
    // Navigate through the application
    cy.get('[data-testid="navigation"]').should('be.visible');

    // Interact with forms
    cy.get('[data-testid="form-input"]').type('Test User Input');
    cy.get('[data-testid="submit-button"]').click();

    // Verify results
    cy.get('[data-testid="success-message"]').should('be.visible');
    cy.get('[data-testid="success-message"]').should('contain', 'Success');
  });

  it('should handle error scenarios', () => {
    // Test error handling
    cy.get('[data-testid="form-input"]').type('invalid input');
    cy.get('[data-testid="submit-button"]').click();

    cy.get('[data-testid="error-message"]').should('be.visible');
  });

  it('should be responsive', () => {
    // Test responsive design
    cy.viewport('iphone-x');
    cy.get('[data-testid="mobile-menu"]').should('be.visible');

    cy.viewport('macbook-15');
    cy.get('[data-testid="desktop-menu"]').should('be.visible');
  });
});"""

    # Configuration generators
    async def _generate_jest_config(self, context: Dict[str, Any]) -> Dict[str, str]:
        """Generate Jest configuration"""

        jest_config = {
            "jest.config.js": """module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  roots: ['<rootDir>/src', '<rootDir>/tests'],
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.{js,jsx,ts,tsx}',
    '<rootDir>/src/**/*.{spec,test}.{js,jsx,ts,tsx}',
    '<rootDir>/tests/**/*.{spec,test}.{js,jsx,ts,tsx}'
  ],
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/index.tsx',
    '!src/serviceWorker.ts'
  ],
  coverageReporters: ['text', 'lcov', 'html'],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1'
  },
  transform: {
    '^.+\\.(ts|tsx)$': 'ts-jest',
    '^.+\\.css$': 'identity-obj-proxy'
  }
};""",
            "src/setupTests.ts": """import '@testing-library/jest-dom';

// Mock environment variables
process.env.REACT_APP_API_URL = 'http://localhost:8000';

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});""",
        }

        return jest_config

    async def _generate_pytest_config(self, context: Dict[str, Any]) -> Dict[str, str]:
        """Generate pytest configuration"""

        pytest_config = {
            "pytest.ini": """[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --disable-warnings
    --tb=short
    -v
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    api: API tests
    slow: Slow running tests
    asyncio_mode = auto""",
            "conftest.py": """import pytest
import asyncio
from unittest.mock import Mock
from src.config import get_settings

@pytest.fixture(scope="session")
def event_loop():
    \"\"\"Create an instance of the default event loop for the test session.\"\"\"
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_settings():
    \"\"\"Mock application settings\"\"\"
    settings = Mock()
    settings.database_url = "sqlite:///test.db"
    settings.secret_key = "test-secret-key"
    settings.environment = "testing"
    return settings

@pytest.fixture
async def client():
    \"\"\"Create test client\"\"\"
    from httpx import AsyncClient
    from src.main import app

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac""",
        }

        return pytest_config

    # Helper methods
    def _get_coverage_target(self, test_type: TestType) -> float:
        """Get coverage target for test type"""

        targets = {
            TestType.UNIT: 90.0,
            TestType.INTEGRATION: 80.0,
            TestType.E2E: 70.0,
            TestType.API: 85.0,
            TestType.COMPONENT: 85.0,
            TestType.PERFORMANCE: 0.0,
            TestType.SECURITY: 0.0,
            TestType.ACCESSIBILITY: 0.0,
        }

        return targets.get(test_type, 80.0)

    def _get_test_commands(self, framework: TestFramework, test_type: TestType) -> Dict[str, str]:
        """Get test commands for framework and type"""

        commands = {
            TestFramework.JEST: {
                "test": "jest",
                "test:watch": "jest --watch",
                "test:coverage": "jest --coverage",
            },
            TestFramework.PYTEST: {
                "test": "pytest",
                "test:watch": "pytest-watch",
                "test:coverage": "pytest --cov",
            },
            TestFramework.CYPRESS: {"test": "cypress run", "test:open": "cypress open"},
            TestFramework.PLAYWRIGHT: {
                "test": "playwright test",
                "test:debug": "playwright test --debug",
            },
        }

        return commands.get(framework, {})

    async def _get_test_configuration(
        self, framework: TestFramework, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get test configuration for framework"""

        return {
            "framework": framework.value,
            "parallel": True,
            "timeout": 30000,
            "retries": 2,
        }

    async def _generate_coverage_config(
        self, framework: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate coverage configuration"""

        return {
            "target": 80,
            "formats": ["text", "html", "lcov"],
            "exclude": ["node_modules/", "build/", "dist/", "**/*.d.ts", "coverage/"],
        }

    async def _write_test_files(
        self,
        test_suites: Dict[str, TestSuite],
        configuration_files: Dict[str, str],
        output_path: str,
    ):
        """Write test files to disk"""

        for suite_name, suite in test_suites.items():
            for test_file in suite.test_files:
                file_path = Path(output_path) / test_file.filename

                # Create directory if it doesn't exist
                file_path.parent.mkdir(parents=True, exist_ok=True)

                # Write test file
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(test_file.content)

        # Write configuration files
        for filename, content in configuration_files.items():
            file_path = Path(output_path) / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

    # Placeholder methods for additional test generators
    def _generate_pytest_integration_test(
        self, components: List[Dict[str, Any]], context: Dict[str, Any]
    ) -> str:
        return "# Pytest integration test content"

    def _generate_playwright_e2e_test(
        self, components: List[Dict[str, Any]], context: Dict[str, Any]
    ) -> str:
        return "// Playwright E2E test content"

    def _generate_jest_api_test(
        self, components: List[Dict[str, Any]], context: Dict[str, Any]
    ) -> str:
        return "// Jest API test content"

    def _generate_pytest_api_test(
        self, components: List[Dict[str, Any]], context: Dict[str, Any]
    ) -> str:
        return "# Pytest API test content"

    def _generate_react_component_test(
        self, component: Dict[str, Any], context: Dict[str, Any]
    ) -> str:
        return "// React component test content"

    def _generate_performance_test_playwright(self, context: Dict[str, Any]) -> str:
        return "// Playwright performance test content"

    def _generate_security_test_jest(self, context: Dict[str, Any]) -> str:
        return "// Jest security test content"

    def _generate_accessibility_test_jest(self, context: Dict[str, Any]) -> str:
        return "// Jest accessibility test content"

    # Additional config generators (simplified)
    async def _generate_vitest_config(self, context: Dict[str, Any]) -> Dict[str, str]:
        return {}

    async def _generate_cypress_config(self, context: Dict[str, Any]) -> Dict[str, str]:
        return {}

    async def _generate_playwright_config(self, context: Dict[str, Any]) -> Dict[str, str]:
        return {}

    async def _generate_unittest_config(self, context: Dict[str, Any]) -> Dict[str, str]:
        return {}

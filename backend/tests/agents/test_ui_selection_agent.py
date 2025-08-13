"""
UI Selection Agent 테스트 스위트
목표 커버리지: 80% 이상
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.unified.ui_selection.agent import (
    UISelectionAgent,
    FrameworkCategory,
    FrameworkInfo,
    UIStack,
    UISelectionResult,
)


class TestUISelectionAgent:
    """UI Selection Agent 단위 테스트"""

    @pytest.fixture
    def agent(self):
        """테스트용 에이전트 인스턴스"""
        with patch("src.lambda.agents.ui_selection_agent.ssm") as mock_ssm:
            mock_ssm.get_parameters_by_path.return_value = {
                "Parameters": [
                    {
                        "Name": "/t-developer/test/ui-selection-agent/max_alternatives",
                        "Value": "3",
                    },
                    {
                        "Name": "/t-developer/test/ui-selection-agent/min_confidence_score",
                        "Value": "0.5",
                    },
                ]
            }
            return UISelectionAgent("test")

    def test_init(self, agent):
        """초기화 테스트"""
        assert agent.environment == "test"
        assert agent.config["max_alternatives"] == "3"
        assert len(agent.frontend_frameworks) > 0
        assert len(agent.mobile_frameworks) > 0
        assert len(agent.backend_frameworks) > 0
        assert len(agent.project_type_mapping) > 0

    def test_validate_input_empty_project_type(self, agent):
        """빈 프로젝트 타입 검증"""
        with pytest.raises(ValueError, match="프로젝트 타입이 필요합니다"):
            agent._validate_input("", {})

    def test_validate_input_empty_requirements(self, agent):
        """빈 요구사항 검증"""
        with pytest.raises(ValueError, match="요구사항이 필요합니다"):
            agent._validate_input("web-application", None)

    def test_validate_input_invalid_project_type(self, agent):
        """잘못된 프로젝트 타입 검증"""
        with pytest.raises(ValueError, match="지원하지 않는 프로젝트 타입"):
            agent._validate_input("invalid-type", {})

    def test_get_framework_candidates_web(self, agent):
        """웹 프로젝트 프레임워크 후보"""
        candidates = agent._get_framework_candidates("web-application", {}, None)

        assert len(candidates) > 0
        assert any(fw in candidates for fw in ["react", "vue", "angular"])

    def test_get_framework_candidates_with_preference(self, agent):
        """선호 프레임워크가 있는 경우"""
        candidates = agent._get_framework_candidates(
            "web-application", {}, {"framework": "vue"}
        )

        # Vue가 첫 번째 후보여야 함
        assert candidates[0] == "vue"

    def test_select_best_framework_performance_critical(self, agent):
        """성능 중심 프레임워크 선택"""
        candidates = ["react", "vue", "angular"]
        requirements = {"performance_critical": True}

        best = agent._select_best_framework(candidates, requirements, None)

        assert best in candidates

    def test_select_best_framework_beginner_friendly(self, agent):
        """초보자 친화적 프레임워크 선택"""
        candidates = ["react", "vue", "angular"]
        requirements = {"experience_level": "beginner"}

        best = agent._select_best_framework(candidates, requirements, None)

        # Vue는 쉬운 학습 곡선을 가짐
        assert best in candidates

    def test_build_ui_stack_react(self, agent):
        """React UI 스택 구성"""
        stack = agent._build_ui_stack("react", {}, None)

        assert stack.framework == "react"
        assert stack.ui_library == "react"
        assert stack.routing == "react-router-dom"
        assert stack.build_tool == "vite"
        assert stack.css_framework == "tailwindcss"

    def test_build_ui_stack_react_with_typescript(self, agent):
        """React + TypeScript 스택"""
        stack = agent._build_ui_stack("react", {"type_safety": True}, None)

        assert stack.typescript is True
        assert stack.language == "typescript"

    def test_build_ui_stack_react_complex_state(self, agent):
        """복잡한 상태 관리가 필요한 React"""
        stack = agent._build_ui_stack("react", {"complex_state": True}, None)

        assert stack.state_management == "redux-toolkit"

    def test_build_ui_stack_vue(self, agent):
        """Vue UI 스택 구성"""
        stack = agent._build_ui_stack("vue", {}, None)

        assert stack.framework == "vue"
        assert stack.ui_library == "vue"
        assert stack.routing == "vue-router"
        assert stack.state_management == "pinia"
        assert stack.build_tool == "vite"

    def test_build_ui_stack_angular(self, agent):
        """Angular UI 스택 구성"""
        stack = agent._build_ui_stack("angular", {}, None)

        assert stack.framework == "angular"
        assert stack.ui_library == "@angular/core"
        assert stack.routing == "@angular/router"
        assert stack.typescript is True  # Angular는 항상 TypeScript
        assert stack.language == "typescript"

    def test_build_ui_stack_nextjs(self, agent):
        """Next.js UI 스택 구성"""
        stack = agent._build_ui_stack("nextjs", {}, None)

        assert stack.framework == "nextjs"
        assert stack.ui_library == "react"
        assert stack.routing == "file-based"
        assert stack.build_tool == "next"

    def test_build_ui_stack_react_native(self, agent):
        """React Native 스택 구성"""
        stack = agent._build_ui_stack("react-native", {}, None)

        assert stack.framework == "react-native"
        assert stack.ui_library == "react-native"
        assert stack.routing == "react-navigation"
        assert stack.build_tool == "metro"

    def test_build_ui_stack_fastapi(self, agent):
        """FastAPI 스택 구성"""
        stack = agent._build_ui_stack("fastapi", {}, None)

        assert stack.framework == "fastapi"
        assert stack.language == "python"
        assert stack.package_manager == "pip"
        assert stack.testing_framework == "pytest"
        assert stack.typescript is False

    def test_generate_alternatives(self, agent):
        """대안 스택 생성"""
        candidates = ["react", "vue", "angular", "svelte"]

        alternatives = agent._generate_alternatives(
            candidates, {}, None, "react"  # 선택된 프레임워크
        )

        assert len(alternatives) <= 3
        assert all(alt.framework != "react" for alt in alternatives)

    def test_generate_folder_structure_react(self, agent):
        """React 프로젝트 구조"""
        stack = UIStack(
            framework="react",
            ui_library="react",
            css_framework="tailwindcss",
            state_management="redux-toolkit",
            routing="react-router-dom",
            build_tool="vite",
            testing_framework="jest",
            package_manager="npm",
            language="javascript",
            typescript=False,
        )

        structure = agent._generate_folder_structure(stack)

        assert "src" in structure
        assert "components" in structure["src"]
        assert "hooks" in structure["src"]
        assert "stores" in structure["src"]
        assert "tests" in structure

    def test_generate_folder_structure_fastapi(self, agent):
        """FastAPI 프로젝트 구조"""
        stack = UIStack(
            framework="fastapi",
            ui_library=None,
            css_framework=None,
            state_management=None,
            routing="fastapi",
            build_tool="poetry",
            testing_framework="pytest",
            package_manager="pip",
            language="python",
            typescript=False,
        )

        structure = agent._generate_folder_structure(stack)

        assert "app" in structure
        assert "api" in structure["app"]
        assert "models" in structure["app"]
        assert "schemas" in structure["app"]
        assert "tests" in structure

    def test_analyze_dependencies_react(self, agent):
        """React 의존성 분석"""
        stack = UIStack(
            framework="react",
            ui_library="react",
            css_framework="tailwindcss",
            state_management="redux-toolkit",
            routing="react-router-dom",
            build_tool="vite",
            testing_framework="jest",
            package_manager="npm",
            language="javascript",
            typescript=False,
        )

        deps, dev_deps = agent._analyze_dependencies(stack)

        assert "react" in deps
        assert "react-dom" in deps
        assert "react-router-dom" in deps
        assert "@reduxjs/toolkit" in deps

        assert "vite" in dev_deps
        assert "tailwindcss" in dev_deps

    def test_analyze_dependencies_react_typescript(self, agent):
        """React + TypeScript 의존성"""
        stack = UIStack(
            framework="react",
            ui_library="react",
            css_framework="tailwindcss",
            state_management=None,
            routing=None,
            build_tool="vite",
            testing_framework="jest",
            package_manager="npm",
            language="typescript",
            typescript=True,
        )

        deps, dev_deps = agent._analyze_dependencies(stack)

        assert "typescript" in dev_deps
        assert "@types/react" in dev_deps
        assert "@types/react-dom" in dev_deps

    def test_get_configuration_files_react(self, agent):
        """React 설정 파일"""
        stack = UIStack(
            framework="react",
            ui_library="react",
            css_framework="tailwindcss",
            state_management=None,
            routing=None,
            build_tool="vite",
            testing_framework="jest",
            package_manager="npm",
            language="javascript",
            typescript=False,
        )

        files = agent._get_configuration_files(stack)

        assert "package.json" in files
        assert "vite.config.js" in files
        assert "tailwind.config.js" in files
        assert "jest.config.js" in files

    def test_get_configuration_files_typescript(self, agent):
        """TypeScript 프로젝트 설정 파일"""
        stack = UIStack(
            framework="react",
            ui_library="react",
            css_framework=None,
            state_management=None,
            routing=None,
            build_tool="vite",
            testing_framework=None,
            package_manager="npm",
            language="typescript",
            typescript=True,
        )

        files = agent._get_configuration_files(stack)

        assert "tsconfig.json" in files

    def test_generate_setup_commands_react(self, agent):
        """React 설치 명령어"""
        stack = UIStack(
            framework="react",
            ui_library="react",
            css_framework="tailwindcss",
            state_management=None,
            routing=None,
            build_tool="vite",
            testing_framework=None,
            package_manager="npm",
            language="javascript",
            typescript=False,
        )

        commands = agent._generate_setup_commands(stack)

        assert any("vite" in cmd for cmd in commands)
        assert any("npm install" in cmd for cmd in commands)
        assert any("tailwindcss" in cmd for cmd in commands)
        assert any("npm run dev" in cmd for cmd in commands)

    def test_generate_setup_commands_fastapi(self, agent):
        """FastAPI 설치 명령어"""
        stack = UIStack(
            framework="fastapi",
            ui_library=None,
            css_framework=None,
            state_management=None,
            routing="fastapi",
            build_tool="poetry",
            testing_framework="pytest",
            package_manager="pip",
            language="python",
            typescript=False,
        )

        commands = agent._generate_setup_commands(stack)

        assert any("venv" in cmd for cmd in commands)
        assert any("pip install fastapi" in cmd for cmd in commands)
        assert any("uvicorn" in cmd for cmd in commands)

    def test_calculate_confidence_high(self, agent):
        """높은 신뢰도 계산"""
        confidence = agent._calculate_confidence(
            "react", {"performance_critical": True}, {"framework": "react"}
        )

        assert confidence > 0.7

    def test_calculate_confidence_low(self, agent):
        """낮은 신뢰도 계산"""
        confidence = agent._calculate_confidence("unknown-framework", {}, None)

        assert confidence <= 0.5

    def test_select_ui_stack_success(self, agent):
        """전체 UI 스택 선택 성공"""
        result = agent.select_ui_stack(
            "web-application",
            {"performance_critical": True, "complex_state": True},
            {"framework": "react", "typescript": True},
        )

        assert isinstance(result, UISelectionResult)
        assert result.project_type == "web-application"
        assert result.recommended_stack.framework == "react"
        assert result.recommended_stack.typescript is True
        assert len(result.alternative_stacks) > 0
        assert result.confidence_score > 0
        assert len(result.setup_commands) > 0
        assert len(result.dependencies) > 0

    def test_select_ui_stack_mobile(self, agent):
        """모바일 앱 스택 선택"""
        result = agent.select_ui_stack(
            "mobile-application", {"cross_platform": True}, None
        )

        assert result.project_type == "mobile-application"
        assert result.recommended_stack.framework in [
            "react-native",
            "flutter",
            "ionic",
        ]

    def test_select_ui_stack_backend(self, agent):
        """백엔드 API 스택 선택"""
        result = agent.select_ui_stack(
            "backend-api", {"async_support": True}, {"framework": "fastapi"}
        )

        assert result.project_type == "backend-api"
        assert result.recommended_stack.framework == "fastapi"
        assert result.recommended_stack.language == "python"


class TestLambdaHandler:
    """Lambda 핸들러 테스트"""

    @patch("src.lambda.agents.ui_selection_agent.UISelectionAgent")
    def test_lambda_handler_success(self, mock_agent_class):
        """Lambda 핸들러 성공"""
        mock_agent = Mock()
        mock_result = UISelectionResult(
            project_type="web-application",
            recommended_stack=UIStack(
                framework="react",
                ui_library="react",
                css_framework="tailwindcss",
                state_management="redux-toolkit",
                routing="react-router-dom",
                build_tool="vite",
                testing_framework="jest",
                package_manager="npm",
                language="typescript",
                typescript=True,
            ),
            alternative_stacks=[],
            framework_details=FrameworkInfo(
                name="React",
                category="frontend",
                version="18.2.0",
                popularity=0.95,
                learning_curve="medium",
                performance="high",
                ecosystem="large",
                pros=[],
                cons=[],
                best_for=[],
                dependencies=[],
            ),
            rationale="React를 선택했습니다",
            setup_commands=["npm create vite@latest"],
            folder_structure={"src": {}},
            dependencies={"react": "^18.2.0"},
            dev_dependencies={"vite": "^5.0.0"},
            configuration_files=["package.json"],
            confidence_score=0.85,
            metadata={},
        )
        mock_agent.select_ui_stack.return_value = mock_result
        mock_agent_class.return_value = mock_agent

        event = {
            "body": json.dumps(
                {
                    "project_type": "web-application",
                    "requirements": {"performance_critical": True},
                    "preferences": {"framework": "react"},
                }
            )
        }

        response = lambda_handler(event, None)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["project_type"] == "web-application"
        assert body["recommended_stack"]["framework"] == "react"

    @patch("src.lambda.agents.ui_selection_agent.UISelectionAgent")
    def test_lambda_handler_validation_error(self, mock_agent_class):
        """Lambda 핸들러 검증 에러"""
        mock_agent = Mock()
        mock_agent.select_ui_stack.side_effect = ValueError("Invalid input")
        mock_agent_class.return_value = mock_agent

        event = {"body": json.dumps({"project_type": "", "requirements": {}})}

        response = lambda_handler(event, None)

        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert "error" in body
        assert body["error"]["code"] == "VALIDATION_ERROR"

    @patch("src.lambda.agents.ui_selection_agent.UISelectionAgent")
    def test_lambda_handler_internal_error(self, mock_agent_class):
        """Lambda 핸들러 내부 에러"""
        mock_agent = Mock()
        mock_agent.select_ui_stack.side_effect = Exception("Unexpected error")
        mock_agent_class.return_value = mock_agent

        event = {
            "body": json.dumps({"project_type": "web-application", "requirements": {}})
        }

        response = lambda_handler(event, None)

        assert response["statusCode"] == 500
        body = json.loads(response["body"])
        assert "error" in body
        assert body["error"]["code"] == "INTERNAL_ERROR"


if __name__ == "__main__":
    pytest.main(
        [
            __file__,
            "-v",
            "--cov=src.lambda.agents.ui_selection_agent",
            "--cov-report=term-missing",
        ]
    )

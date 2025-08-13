#!/usr/bin/env python3
"""
Project Quality Validator
생성된 프로젝트의 품질을 검증하는 시스템
"""

import ast
import asyncio
import json
import logging
import re
import subprocess
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class QualityMetrics:
    """품질 메트릭"""

    code_quality_score: float
    build_success: bool
    test_coverage: float
    eslint_score: float
    dependency_security: float
    file_structure_score: float
    documentation_score: float
    overall_score: float
    issues: List[str]
    recommendations: List[str]


class ProjectQualityValidator:
    """프로젝트 품질 검증기"""

    def __init__(self):
        self.temp_dir = None
        self.project_path = None

    async def validate_project_zip(self, zip_path: str) -> QualityMetrics:
        """ZIP 파일로부터 프로젝트 품질 검증"""

        with tempfile.TemporaryDirectory() as temp_dir:
            self.temp_dir = Path(temp_dir)

            # ZIP 압축 해제
            with zipfile.ZipFile(zip_path, "r") as zipf:
                zipf.extractall(temp_dir)

                # 프로젝트 루트 찾기
                extracted_items = list(Path(temp_dir).iterdir())
                if len(extracted_items) == 1 and extracted_items[0].is_dir():
                    self.project_path = extracted_items[0]
                else:
                    self.project_path = Path(temp_dir)

            return await self._run_quality_checks()

    async def _run_quality_checks(self) -> QualityMetrics:
        """품질 검사 실행"""
        issues = []
        recommendations = []

        # 각 검사 실행
        code_quality = await self._check_code_quality()
        build_success = await self._check_build_success()
        eslint_score = await self._check_eslint()
        dependency_security = await self._check_dependency_security()
        file_structure = await self._check_file_structure()
        documentation = await self._check_documentation()

        # 전체 점수 계산 (가중 평균)
        scores = {
            "code_quality": (code_quality["score"], 0.25),
            "build_success": (100.0 if build_success["success"] else 0.0, 0.30),
            "eslint": (eslint_score["score"], 0.15),
            "dependency_security": (dependency_security["score"], 0.10),
            "file_structure": (file_structure["score"], 0.10),
            "documentation": (documentation["score"], 0.10),
        }

        overall_score = sum(score * weight for score, weight in scores.values())

        # 이슈 및 추천사항 수집
        for check_name, check_result in [
            ("code_quality", code_quality),
            ("build_success", build_success),
            ("eslint", eslint_score),
            ("dependency_security", dependency_security),
            ("file_structure", file_structure),
            ("documentation", documentation),
        ]:
            issues.extend(check_result.get("issues", []))
            recommendations.extend(check_result.get("recommendations", []))

        return QualityMetrics(
            code_quality_score=code_quality["score"],
            build_success=build_success["success"],
            test_coverage=0.0,  # 현재 구현되지 않음
            eslint_score=eslint_score["score"],
            dependency_security=dependency_security["score"],
            file_structure_score=file_structure["score"],
            documentation_score=documentation["score"],
            overall_score=overall_score,
            issues=issues,
            recommendations=recommendations,
        )

    async def _check_code_quality(self) -> Dict[str, Any]:
        """코드 품질 검사"""
        issues = []
        recommendations = []
        score = 100.0

        # JavaScript/TypeScript 파일들 검사
        js_files = list(self.project_path.rglob("*.js")) + list(self.project_path.rglob("*.jsx"))
        ts_files = list(self.project_path.rglob("*.ts")) + list(self.project_path.rglob("*.tsx"))

        all_files = js_files + ts_files

        if not all_files:
            issues.append("No JavaScript/TypeScript files found")
            return {"score": 0.0, "issues": issues, "recommendations": recommendations}

        for file_path in all_files:
            try:
                content = file_path.read_text(encoding="utf-8")

                # 기본 품질 검사
                if len(content.strip()) == 0:
                    issues.append(f"Empty file: {file_path.name}")
                    score -= 5
                    continue

                # console.log 사용 검사
                if "console.log" in content:
                    issues.append(f"Debug console.log found in {file_path.name}")
                    score -= 2

                # TODO/FIXME 검사
                if re.search(r"(TODO|FIXME|XXX)", content, re.IGNORECASE):
                    issues.append(f"Unfinished code markers in {file_path.name}")
                    score -= 1

                # 기본 React 패턴 검사
                if file_path.suffix in [".jsx", ".tsx"]:
                    if "export default" not in content:
                        issues.append(f"No default export in React component: {file_path.name}")
                        score -= 3

                    if "import React" not in content and "import * as React" not in content:
                        # React 17+ 에서는 필요없을 수 있지만 권장
                        recommendations.append(
                            f"Consider explicit React import in {file_path.name}"
                        )

                # 함수 복잡도 간단 검사
                function_count = len(
                    re.findall(r"function\s+\w+|const\s+\w+\s*=\s*\([^)]*\)\s*=>", content)
                )
                if function_count > 10:
                    recommendations.append(
                        f"High function count in {file_path.name}, consider splitting"
                    )

            except Exception as e:
                issues.append(f"Error reading {file_path.name}: {str(e)}")
                score -= 5

        return {
            "score": max(0, score),
            "issues": issues,
            "recommendations": recommendations,
            "files_checked": len(all_files),
        }

    async def _check_build_success(self) -> Dict[str, Any]:
        """빌드 성공 검사"""
        issues = []
        recommendations = []

        package_json = self.project_path / "package.json"

        if not package_json.exists():
            return {
                "success": False,
                "issues": ["No package.json found"],
                "recommendations": ["Ensure package.json is properly generated"],
            }

        try:
            # package.json 구조 검증
            with open(package_json, "r") as f:
                package_data = json.load(f)

            required_fields = ["name", "version", "dependencies", "scripts"]
            for field in required_fields:
                if field not in package_data:
                    issues.append(f"Missing {field} in package.json")

            # npm install 시뮬레이션 (실제로는 실행하지 않음)
            dependencies = package_data.get("dependencies", {})
            dev_dependencies = package_data.get("devDependencies", {})

            if not dependencies:
                issues.append("No dependencies found")

            # React 관련 의존성 확인
            if package_data.get("dependencies", {}).get("react"):
                if not package_data.get("dependencies", {}).get("react-dom"):
                    issues.append("React found but react-dom missing")

                if not package_data.get("dependencies", {}).get("react-scripts"):
                    recommendations.append("Consider using react-scripts for easier build setup")

            # 스크립트 검증
            scripts = package_data.get("scripts", {})
            recommended_scripts = ["start", "build", "test"]

            for script in recommended_scripts:
                if script not in scripts:
                    issues.append(f"Missing '{script}' script in package.json")

            # 빌드 성공 가능성 추정
            build_success = len(issues) == 0

            return {
                "success": build_success,
                "issues": issues,
                "recommendations": recommendations,
                "package_valid": True,
                "dependency_count": len(dependencies) + len(dev_dependencies),
            }

        except json.JSONDecodeError:
            return {
                "success": False,
                "issues": ["Invalid package.json format"],
                "recommendations": ["Ensure package.json is valid JSON"],
            }
        except Exception as e:
            return {
                "success": False,
                "issues": [f"Error checking build: {str(e)}"],
                "recommendations": [],
            }

    async def _check_eslint(self) -> Dict[str, Any]:
        """ESLint 설정 및 코드 스타일 검사"""
        issues = []
        recommendations = []
        score = 100.0

        # ESLint 설정 파일 확인
        eslint_configs = [
            ".eslintrc",
            ".eslintrc.js",
            ".eslintrc.json",
            ".eslintrc.yaml",
            ".eslintrc.yml",
        ]

        eslint_config_found = any(
            (self.project_path / config).exists() for config in eslint_configs
        )

        # package.json에서 eslintConfig 확인
        package_json = self.project_path / "package.json"
        package_eslint_config = False

        if package_json.exists():
            try:
                with open(package_json, "r") as f:
                    package_data = json.load(f)
                    package_eslint_config = "eslintConfig" in package_data
            except:
                pass

        if not eslint_config_found and not package_eslint_config:
            issues.append("No ESLint configuration found")
            score -= 20
        else:
            recommendations.append("ESLint configuration detected - good practice")

        # 코드 스타일 간단 검사
        js_files = list(self.project_path.rglob("*.js")) + list(self.project_path.rglob("*.jsx"))

        for file_path in js_files:
            try:
                content = file_path.read_text()

                # 들여쓰기 일관성 검사 (간단한 버전)
                lines = content.split("\n")
                indent_types = set()

                for line in lines:
                    if line.strip():  # 빈 줄이 아닌 경우
                        leading_whitespace = len(line) - len(line.lstrip())
                        if leading_whitespace > 0:
                            if line.startswith("\t"):
                                indent_types.add("tab")
                            elif line.startswith(" "):
                                indent_types.add("space")

                if len(indent_types) > 1:
                    issues.append(f"Mixed indentation types in {file_path.name}")
                    score -= 5

                # 세미콜론 일관성 (간단 검사)
                semicolon_lines = [line for line in lines if line.strip().endswith(";")]
                no_semicolon_lines = [
                    line
                    for line in lines
                    if line.strip()
                    and not line.strip().endswith(";")
                    and not line.strip().endswith("{")
                    and not line.strip().endswith("}")
                    and not line.strip().startswith("//")
                    and not line.strip().startswith("*")
                    and "import" not in line
                    and "export" not in line
                ]

                if semicolon_lines and no_semicolon_lines:
                    issues.append(f"Inconsistent semicolon usage in {file_path.name}")
                    score -= 3

            except Exception as e:
                issues.append(f"Error checking style in {file_path.name}: {str(e)}")

        return {
            "score": max(0, score),
            "issues": issues,
            "recommendations": recommendations,
            "eslint_config_found": eslint_config_found or package_eslint_config,
        }

    async def _check_dependency_security(self) -> Dict[str, Any]:
        """의존성 보안 검사"""
        issues = []
        recommendations = []
        score = 100.0

        package_json = self.project_path / "package.json"

        if not package_json.exists():
            return {
                "score": 0,
                "issues": ["No package.json found"],
                "recommendations": [],
            }

        try:
            with open(package_json, "r") as f:
                package_data = json.load(f)

            dependencies = package_data.get("dependencies", {})
            dev_dependencies = package_data.get("devDependencies", {})

            all_deps = {**dependencies, **dev_dependencies}

            # 알려진 취약한 패키지 (예시)
            known_vulnerable = {
                "node-uuid": "Use uuid package instead",
                "request": "Package is deprecated, use axios or fetch",
                "bower": "Bower is deprecated",
            }

            for dep_name in all_deps:
                if dep_name in known_vulnerable:
                    issues.append(f"Vulnerable/deprecated dependency: {dep_name}")
                    recommendations.append(known_vulnerable[dep_name])
                    score -= 10

            # 버전 고정 검사
            for dep_name, version in all_deps.items():
                if version.startswith("^") or version.startswith("~"):
                    # 이것은 실제로는 좋은 관행이지만, 보안 관점에서는 고정 버전이 더 안전
                    recommendations.append(
                        f"Consider pinning version for {dep_name} for better security"
                    )
                elif version == "*" or version == "latest":
                    issues.append(f"Unsafe version specification for {dep_name}: {version}")
                    score -= 15

            # 의존성 개수 검사
            total_deps = len(all_deps)
            if total_deps > 50:
                recommendations.append(
                    f"High number of dependencies ({total_deps}), consider reducing"
                )
            elif total_deps == 0:
                issues.append("No dependencies found - project may be incomplete")
                score -= 20

            return {
                "score": max(0, score),
                "issues": issues,
                "recommendations": recommendations,
                "total_dependencies": total_deps,
                "vulnerable_dependencies": len(
                    [dep for dep in all_deps if dep in known_vulnerable]
                ),
            }

        except Exception as e:
            return {
                "score": 0,
                "issues": [f"Error checking dependencies: {str(e)}"],
                "recommendations": [],
            }

    async def _check_file_structure(self) -> Dict[str, Any]:
        """파일 구조 검사"""
        issues = []
        recommendations = []
        score = 100.0

        # React 프로젝트 표준 구조 확인
        expected_files = [
            "package.json",
            "README.md",
            "public/index.html",
            "src/index.js",
            "src/App.js",
        ]

        expected_dirs = ["src", "public"]

        # 필수 파일 확인
        for file_path in expected_files:
            full_path = self.project_path / file_path
            if not full_path.exists():
                issues.append(f"Missing expected file: {file_path}")
                score -= 10

        # 필수 디렉토리 확인
        for dir_path in expected_dirs:
            full_path = self.project_path / dir_path
            if not full_path.exists():
                issues.append(f"Missing expected directory: {dir_path}")
                score -= 15

        # .gitignore 확인
        gitignore = self.project_path / ".gitignore"
        if not gitignore.exists():
            recommendations.append("Add .gitignore file for better version control")
        else:
            try:
                gitignore_content = gitignore.read_text()
                if "node_modules" not in gitignore_content:
                    issues.append("node_modules not in .gitignore")
                    score -= 5
            except:
                pass

        # src 디렉토리 구조 확인
        src_dir = self.project_path / "src"
        if src_dir.exists():
            src_files = list(src_dir.rglob("*"))
            js_files = [f for f in src_files if f.suffix in [".js", ".jsx", ".ts", ".tsx"]]

            if len(js_files) < 2:
                issues.append("Very few source files - project may be incomplete")
                score -= 10

            # 컴포넌트 조직화 확인
            components_dir = src_dir / "components"
            if len(js_files) > 5 and not components_dir.exists():
                recommendations.append("Consider organizing components in a components/ directory")

        return {
            "score": max(0, score),
            "issues": issues,
            "recommendations": recommendations,
            "structure_valid": len(issues) == 0,
        }

    async def _check_documentation(self) -> Dict[str, Any]:
        """문서화 검사"""
        issues = []
        recommendations = []
        score = 100.0

        # README.md 확인
        readme = self.project_path / "README.md"
        if not readme.exists():
            issues.append("No README.md file found")
            score -= 30
            return {
                "score": max(0, score),
                "issues": issues,
                "recommendations": [
                    "Add README.md with project description and setup instructions"
                ],
            }

        try:
            readme_content = readme.read_text()

            if len(readme_content.strip()) < 100:
                issues.append("README.md is too brief")
                score -= 15

            # 필수 섹션 확인
            required_sections = ["install", "start", "run", "setup"]

            readme_lower = readme_content.lower()
            found_sections = sum(1 for section in required_sections if section in readme_lower)

            if found_sections == 0:
                issues.append("README.md lacks setup/installation instructions")
                score -= 20
            elif found_sections < 2:
                recommendations.append("Add more detailed setup instructions to README.md")

            # 코드 블록 확인
            if "```" not in readme_content and "`" not in readme_content:
                recommendations.append("Add code examples to README.md")

        except Exception as e:
            issues.append(f"Error reading README.md: {str(e)}")
            score -= 10

        # 기타 문서 확인
        other_docs = ["CHANGELOG.md", "CONTRIBUTING.md", "LICENSE"]

        for doc in other_docs:
            if (self.project_path / doc).exists():
                recommendations.append(f"Great! Found {doc}")
            elif doc == "LICENSE":
                recommendations.append("Consider adding a LICENSE file")

        return {
            "score": max(0, score),
            "issues": issues,
            "recommendations": recommendations,
            "readme_exists": readme.exists(),
        }


class QualityReportGenerator:
    """품질 보고서 생성기"""

    @staticmethod
    def generate_report(
        metrics: QualityMetrics, project_info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """품질 보고서 생성"""

        # 등급 계산
        def get_grade(score: float) -> str:
            if score >= 90:
                return "A"
            elif score >= 80:
                return "B"
            elif score >= 70:
                return "C"
            elif score >= 60:
                return "D"
            else:
                return "F"

        report = {
            "overall_assessment": {
                "score": metrics.overall_score,
                "grade": get_grade(metrics.overall_score),
                "production_ready": metrics.overall_score >= 80 and metrics.build_success,
            },
            "detailed_scores": {
                "code_quality": {
                    "score": metrics.code_quality_score,
                    "grade": get_grade(metrics.code_quality_score),
                },
                "build_success": {
                    "passed": metrics.build_success,
                    "score": 100.0 if metrics.build_success else 0.0,
                },
                "eslint": {
                    "score": metrics.eslint_score,
                    "grade": get_grade(metrics.eslint_score),
                },
                "dependency_security": {
                    "score": metrics.dependency_security,
                    "grade": get_grade(metrics.dependency_security),
                },
                "file_structure": {
                    "score": metrics.file_structure_score,
                    "grade": get_grade(metrics.file_structure_score),
                },
                "documentation": {
                    "score": metrics.documentation_score,
                    "grade": get_grade(metrics.documentation_score),
                },
            },
            "issues": {"total": len(metrics.issues), "details": metrics.issues},
            "recommendations": {
                "total": len(metrics.recommendations),
                "details": metrics.recommendations,
            },
            "project_info": project_info or {},
            "generated_at": datetime.now().isoformat(),
        }

        return report

    @staticmethod
    def print_report(report: Dict[str, Any]):
        """콘솔에 보고서 출력"""
        print("\n" + "=" * 60)
        print("🔍 PROJECT QUALITY ASSESSMENT REPORT")
        print("=" * 60)

        overall = report["overall_assessment"]
        print(f"Overall Score: {overall['score']:.1f}/100 (Grade: {overall['grade']})")
        print(f"Production Ready: {'✅ YES' if overall['production_ready'] else '❌ NO'}")

        print("\n📊 Detailed Scores:")
        for category, data in report["detailed_scores"].items():
            if "score" in data:
                print(
                    f"  {category.replace('_', ' ').title()}: {data['score']:.1f}/100 ({data.get('grade', 'N/A')})"
                )
            elif "passed" in data:
                print(
                    f"  {category.replace('_', ' ').title()}: {'✅ PASSED' if data['passed'] else '❌ FAILED'}"
                )

        if report["issues"]["total"] > 0:
            print(f"\n❌ Issues Found ({report['issues']['total']}):")
            for i, issue in enumerate(report["issues"]["details"], 1):
                print(f"  {i}. {issue}")

        if report["recommendations"]["total"] > 0:
            print(f"\n💡 Recommendations ({report['recommendations']['total']}):")
            for i, rec in enumerate(report["recommendations"]["details"], 1):
                print(f"  {i}. {rec}")

        print("\n" + "=" * 60)


async def validate_project_quality(zip_path: str) -> Dict[str, Any]:
    """프로젝트 품질 검증 메인 함수"""
    validator = ProjectQualityValidator()

    try:
        metrics = await validator.validate_project_zip(zip_path)
        report = QualityReportGenerator.generate_report(metrics)

        return {"success": True, "metrics": metrics, "report": report}

    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python project_quality_validator.py <path_to_project.zip>")
        sys.exit(1)

    zip_path = sys.argv[1]

    async def main():
        result = await validate_project_quality(zip_path)

        if result["success"]:
            QualityReportGenerator.print_report(result["report"])

            # 품질 점수에 따른 종료 코드
            overall_score = result["metrics"].overall_score
            if overall_score >= 80:
                print("\n🎉 Quality check passed!")
                return 0
            else:
                print(f"\n💥 Quality check failed (score: {overall_score:.1f}/100)")
                return 1
        else:
            print(f"❌ Quality validation failed: {result['error']}")
            return 1

    exit_code = asyncio.run(main())
    sys.exit(exit_code)
